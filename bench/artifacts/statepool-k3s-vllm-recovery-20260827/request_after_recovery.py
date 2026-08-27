import json,time,uuid,hashlib
from urllib.request import Request,urlopen
RUN='/home/wzu/codex-run/statepool-k3s-gpu-pod-20260827'
MODEL='qwen2.5-0.5b-instruct-vllm'; REV='7ae557604adf67be50417f59c2c2f167def9a775'
TOK='sha256:'+hashlib.sha256(open('/home/data/wangyue/models/qwen/Qwen2.5-0.5B-Instruct-7ae5576/tokenizer.json','rb').read()).hexdigest()
def post(url,payload):
 req=Request(url,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'},method='POST')
 with urlopen(req,timeout=300) as r: return json.loads(r.read()),dict(r.headers)
before=json.load(open(RUN+'/before-failure.json'))
assistant=before['completion']['choices'][0]['message']['content']
messages=before['messages']+[{'role':'assistant','content':assistant},{'role':'user','content':'What codeword did I ask you to memorize? Reply with only the codeword.'}]
plan,_=post('http://127.0.0.1:18130/plugin/v1/plan',{
 'contract_version':'statepool-plan-request.v1','request_id':'post-'+uuid.uuid4().hex,
 'session_id':'k8s-recovery-session','owner_id':'evidence','model_ref':{'model_id':MODEL,'revision':REV,'tokenizer':TOK,'state_abi':'context-replay.v1'},
 'privacy':'cloud_allowed','latency_slo_ms':30000,'estimated_input_tokens':64,'estimated_output_tokens':16,
 'affinity_worker_id':before['worker_id']})
t=time.perf_counter(); completion,headers=post(plan['endpoint']+'/v1/chat/completions',{'model':MODEL,'messages':messages,'temperature':0,'max_tokens':16})
content=completion['choices'][0]['message']['content']
result={'plan':plan,'worker_id':headers.get('X-StatePool-Worker-Id'),'elapsed_ms':round((time.perf_counter()-t)*1000,3),'messages':messages,'completion':completion,'old_worker_id':before['worker_id'],'worker_replaced':headers.get('X-StatePool-Worker-Id')!=before['worker_id'],'transcript_replay_verified':'CLOUD-2719' in content}
json.dump(result,open(RUN+'/after-recovery.json','w'),ensure_ascii=False,indent=2)
print(json.dumps({'old_worker_id':result['old_worker_id'],'new_worker_id':result['worker_id'],'worker_replaced':result['worker_replaced'],'transcript_replay_verified':result['transcript_replay_verified'],'elapsed_ms':result['elapsed_ms'],'content':content,'usage':completion.get('usage'),'plan_mode':plan.get('mode')},ensure_ascii=False))
if not result['worker_replaced'] or not result['transcript_replay_verified']: raise SystemExit(1)
