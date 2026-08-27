import json,time,uuid,hashlib
from urllib.request import Request,urlopen
RUN='/home/wzu/codex-run/statepool-k3s-gpu-pod-20260827'
MODEL='qwen2.5-0.5b-instruct-vllm'
REV='7ae557604adf67be50417f59c2c2f167def9a775'
TOK='sha256:'+hashlib.sha256(open('/home/data/wangyue/models/qwen/Qwen2.5-0.5B-Instruct-7ae5576/tokenizer.json','rb').read()).hexdigest()
def post(url,payload):
 req=Request(url,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'},method='POST')
 with urlopen(req,timeout=300) as r: return json.loads(r.read()),dict(r.headers)
plan,_=post('http://127.0.0.1:18130/plugin/v1/plan',{
 'contract_version':'statepool-plan-request.v1','request_id':'pre-'+uuid.uuid4().hex,
 'session_id':'k8s-recovery-session','owner_id':'evidence','model_ref':{'model_id':MODEL,'revision':REV,'tokenizer':TOK,'state_abi':'context-replay.v1'},
 'privacy':'cloud_allowed','latency_slo_ms':30000,'estimated_input_tokens':32,'estimated_output_tokens':16})
messages=[{'role':'user','content':'Memorize the codeword CLOUD-2719. Reply exactly: stored'}]
t=time.perf_counter(); completion,headers=post(plan['endpoint']+'/v1/chat/completions',{'model':MODEL,'messages':messages,'temperature':0,'max_tokens':16})
result={'plan':plan,'worker_id':headers.get('X-StatePool-Worker-Id'),'elapsed_ms':round((time.perf_counter()-t)*1000,3),'messages':messages,'completion':completion}
json.dump(result,open(RUN+'/before-failure.json','w'),ensure_ascii=False,indent=2)
print(json.dumps({'worker_id':result['worker_id'],'elapsed_ms':result['elapsed_ms'],'content':completion['choices'][0]['message']['content'],'usage':completion.get('usage')},ensure_ascii=False))
