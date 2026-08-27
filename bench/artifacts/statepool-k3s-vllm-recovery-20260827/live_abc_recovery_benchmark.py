import hashlib,json,subprocess,time,uuid
from urllib.request import Request,urlopen
RUN='/home/wzu/codex-run/statepool-k3s-gpu-pod-20260827'
MODEL='qwen2.5-0.5b-instruct-vllm'; REV='7ae557604adf67be50417f59c2c2f167def9a775'
TOK='sha256:'+hashlib.sha256(open('/home/data/wangyue/models/qwen/Qwen2.5-0.5B-Instruct-7ae5576/tokenizer.json','rb').read()).hexdigest()
K=['sudo','k3s','kubectl']
def cmd(*args): return subprocess.check_output(K+list(args),text=True).strip()
def pod():
 x=json.loads(cmd('get','pods','-l','app.kubernetes.io/name=statepool-vllm','-o','json'))
 if not x['items']: return ('','',False)
 p=x['items'][0]; ready=all(c.get('ready') for c in p.get('status',{}).get('containerStatuses',[])) and len(p.get('status',{}).get('containerStatuses',[]))==2
 return p['metadata']['name'],p['metadata']['uid'],ready
def wait_replacement(old_name,timeout=240):
 t0=time.perf_counter(); deadline=t0+timeout
 while time.perf_counter()<deadline:
  try:
   name,uid,ready=pod()
   if name and name!=old_name and ready: return name,uid,round((time.perf_counter()-t0)*1000,3)
  except Exception: pass
  time.sleep(.5)
 raise TimeoutError('replacement Pod did not become Ready')
def post(url,payload):
 req=Request(url,data=json.dumps(payload,separators=(',',':')).encode(),headers={'Content-Type':'application/json'},method='POST')
 with urlopen(req,timeout=300) as r: return json.loads(r.read()),dict(r.headers)
def choose(session,affinity=''):
 p={'contract_version':'statepool-plan-request.v1','request_id':'abc-'+uuid.uuid4().hex,'session_id':session,'owner_id':'evidence','model_ref':{'model_id':MODEL,'revision':REV,'tokenizer':TOK,'state_abi':'context-replay.v1'},'privacy':'cloud_allowed','latency_slo_ms':30000,'estimated_input_tokens':80,'estimated_output_tokens':16}
 if affinity: p['affinity_worker_id']=affinity
 t=time.perf_counter(); x,_=post('http://127.0.0.1:18130/plugin/v1/plan',p); return x,round((time.perf_counter()-t)*1000,3)
def chat(messages,use_plan=False,session='',affinity=''):
 plan_ms=0.0; route=None; endpoint='http://127.0.0.1:18138'
 if use_plan: route,plan_ms=choose(session,affinity); endpoint=route['endpoint']
 t=time.perf_counter(); out,h=post(endpoint+'/v1/chat/completions',{'model':MODEL,'messages':messages,'temperature':0,'max_tokens':16})
 return {'request_ms':round((time.perf_counter()-t)*1000,3),'plan_ms':plan_ms,'worker_id':h.get('X-StatePool-Worker-Id'),'content':out['choices'][0]['message']['content'],'usage':out.get('usage'),'plan':route}
def dialogue(codeword,use_plan=False,session=''):
 first_messages=[{'role':'user','content':f'Memorize codeword {codeword}. Reply exactly: stored'}]
 first=chat(first_messages,use_plan,session)
 transcript=first_messages+[{'role':'assistant','content':first['content']},{'role':'user','content':'What codeword did I ask you to memorize? Reply only with the codeword.'}]
 return first,transcript
results={}
# A: sticky Worker stays allocated during a 10-second idle window.
a_name,a_uid,_=pod(); a_first,a_transcript=dialogue('CLOUD-A2719')
t0=time.perf_counter(); time.sleep(10); a_second=chat(a_transcript); a_gap_ms=round((time.perf_counter()-t0)*1000,3)
results['A']={'policy':'sticky_warm_worker','first_pod':a_name,'first_pod_uid':a_uid,'replacement_pod':a_name,'replacement_pod_uid':a_uid,'worker_replaced':False,'idle_window_seconds':10,'recovery_ready_ms':0,'observed_allocated_gap_ms':a_gap_ms,'first':a_first,'second':a_second,'context_verified':'CLOUD-A2719' in a_second['content'] and a_first['worker_id']==a_second['worker_id']}
# B: external/direct stateless recycle; client replays full transcript to fixed endpoint.
b_name,b_uid,_=pod(); b_first,b_transcript=dialogue('CLOUD-B2719')
t0=time.perf_counter(); subprocess.run(K+['delete','pod',b_name,'--grace-period=0','--force'],check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
b_new,b_new_uid,b_ready_ms=wait_replacement(b_name)
b_second=chat(b_transcript)
results['B']={'policy':'stateless_direct_recycle','first_pod':b_name,'first_pod_uid':b_uid,'replacement_pod':b_new,'replacement_pod_uid':b_new_uid,'worker_replaced':b_first['worker_id']!=b_second['worker_id'],'idle_window_seconds':0,'recovery_ready_ms':b_ready_ms,'observed_allocated_gap_ms':round((time.perf_counter()-t0)*1000,3),'first':b_first,'second':b_second,'context_verified':'CLOUD-B2719' in b_second['content']}
# C: StatePool plans both calls, survives replacement, and client transcript replay preserves semantics.
c_name,c_uid,_=pod(); c_first,c_transcript=dialogue('CLOUD-C2719',True,'abc-c-session')
t0=time.perf_counter(); subprocess.run(K+['delete','pod',c_name,'--grace-period=0','--force'],check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
c_new,c_new_uid,c_ready_ms=wait_replacement(c_name)
c_second=chat(c_transcript,True,'abc-c-session',c_first['worker_id'])
results['C']={'policy':'statepool_managed_recycle','first_pod':c_name,'first_pod_uid':c_uid,'replacement_pod':c_new,'replacement_pod_uid':c_new_uid,'worker_replaced':c_first['worker_id']!=c_second['worker_id'],'idle_window_seconds':0,'recovery_ready_ms':c_ready_ms,'observed_allocated_gap_ms':round((time.perf_counter()-t0)*1000,3),'first':c_first,'second':c_second,'context_verified':'CLOUD-C2719' in c_second['content']}
valid=all(x['context_verified'] for x in results.values()) and results['B']['worker_replaced'] and results['C']['worker_replaced']
summary={'schema_version':'statepool-live-abc-recovery.v1','classification':'live_same_node_same_model_gpu_kubernetes_benchmark','environment':{'node':'wzu-SYS-4029GP-TRT','kubernetes':'k3s v1.36.3+k3s1','gpu_class':'Tesla V100-PCIE-32GB','gpu_resource_request':'nvidia.com/gpu=1','runtime':'vLLM 0.8.5.post1 / torch 2.6.0+cu124 / XFormers','model':'Qwen/Qwen2.5-0.5B-Instruct','model_revision':REV},'workload':{'two_turn_dialogue':True,'full_transcript_on_second_turn':True,'max_output_tokens':16,'A_idle_seconds':10},'results':results,'all_context_checks_passed':valid,'measured_break_even_idle_seconds':round(max(results['B']['recovery_ready_ms'],results['C']['recovery_ready_ms'])/1000,3),'interpretation':['A measures a warm, allocated Worker across the explicit 10-second idle gap.','B and C force-delete and recreate the same Deployment; recovery_ready_ms includes Kubernetes scheduling and vLLM cold start.','For OpenAI/vLLM, B and C preserve dialogue by full transcript replay; neither exports portable KV cache.','The measured cold-start duration is a break-even input: scale-to-zero saves allocated GPU time only when avoided idle exceeds shutdown/startup overhead.','C adds compatibility-aware planning and stale-affinity failover; it does not claim lower model compute than B.']}
json.dump(summary,open(RUN+'/live-abc-recovery-summary.json','w'),ensure_ascii=False,indent=2)
print(json.dumps({s:{'policy':x['policy'],'recovery_ready_ms':x['recovery_ready_ms'],'second_request_ms':x['second']['request_ms'],'second_plan_ms':x['second']['plan_ms'],'worker_replaced':x['worker_replaced'],'context_verified':x['context_verified'],'content':x['second']['content']} for s,x in results.items()},ensure_ascii=False,indent=2))
if not valid: raise SystemExit(1)
