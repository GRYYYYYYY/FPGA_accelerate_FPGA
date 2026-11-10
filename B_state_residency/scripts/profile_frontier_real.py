"""Measure every real search frontier without changing serial routing semantics."""
from pathlib import Path
from collections import Counter
from itertools import zip_longest
import json,os,subprocess,sys,re,shutil,time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha,UPSTREAM
from build_frontier_profile import generate
from profile_real import validate,parse_log

def main():
 base=ROOT/'results/real_trace_20261022T165136Z';bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed';validate(bm['config'],bm['build'])
 assert sha(ROOT/'build/real_trace/trace.cpp')==bm['build']['trace']['source_sha256']
 out=ROOT/'results/frontier_real_20261024';out.mkdir();src=out/'sources';src.mkdir();include=out/'include';include.mkdir()
 m={'status':'preparing','pid':os.getpid(),'baseline_manifest_sha256':sha(base/'manifest.json'),'runner_sha256':sha(Path(__file__)),'sources':{},'commands':[],'scope':'Every serial search attempt; instrumented work/capacity only, not a performance comparison.'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  inputs={'trace.cpp':ROOT/'build/real_trace/trace.cpp','real_trace.hpp':ROOT/'adapters/real_trace.hpp','real_router_hooks.inc':ROOT/'adapters/real_router_hooks.inc'}
  for name,p in inputs.items():(out/('original_'+name)).write_bytes(p.read_bytes())
  generated=generate(*(inputs[name].read_text() for name in ('trace.cpp','real_trace.hpp','real_router_hooks.inc')))
  for name,text in generated.items():(src/name).write_text(text)
  (src/'real_profile.hpp').write_bytes((ROOT/'adapters/real_profile.hpp').read_bytes())
  generator=ROOT/'adapters/build_frontier_profile.py';(out/generator.name).write_bytes(generator.read_bytes());m['generator_sha256']=sha(generator)
  (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
  files=subprocess.check_output(['rg','--files',str(UPSTREAM/'cpp_router/include'),'-g','*.h','-g','*.hpp','-g','*.inc','-g','*.tpp'],text=True).splitlines()
  for filename in files:
   p=Path(filename);target=include/p.relative_to(UPSTREAM/'cpp_router/include');target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
  m['sources']={str(p.relative_to(out)):sha(p) for folder in [src,include] for p in folder.rglob('*') if p.is_file()}
  binary=out/'router_frontier'
  cmd=['g++','-std=c++17','-O3','-g','-fno-fast-math','-fno-omit-frame-pointer','-no-pie','-pthread','-I',str(include),'-I',str(src),str(src/'trace.cpp'),'-o',str(binary)]
  m['status']='building';m['commands'].append({'stage':'build','argv':cmd});save()
  with (out/'build.log').open('w') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
  m['commands'][-1]['exit_code']=0;m['binary_sha256']=sha(binary)
  prefix=out/'trace';config=bm['config'];env={k:v for k,v in os.environ.items() if not k.startswith(('RW_','B_SAMPLE','B_TRACE','B_PROFILE'))}
  extra=dict(config['environment'],B_TRACE_PREFIX=str(prefix),B_TRACE_STRIDE=str(config['trace_stride']),B_PROFILE_PREFIX=str(prefix));env.update(extra);m['environment']=extra
  cmd=['/usr/bin/time','-v','-o',str(out/'trace.time'),'taskset','-c',str(config['cpu']),str(binary),str(ROOT/config['input']),str(out/'trace.result')]
  m['status']='running';m['commands'].append({'stage':'route','argv':cmd});save()
  with (out/'trace.log').open('w') as log:
   proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,env=env);m['commands'][-1]['pid']=proc.pid;save();code=proc.wait(timeout=600);m['commands'][-1]['exit_code']=code;save();assert code==0
  log=(out/'trace.log').read_text();metrics=parse_log(log);m['metrics']=metrics
  assert metrics['convergence']==bm['runs'][0]['metrics']['convergence'] and metrics['pushes']==bm['runs'][0]['metrics']['pushes']
  assert sha(out/'trace.result')==bm['runs'][0]['result_sha256']
  # Inline instrumentation preserves all original main-file line numbers.
  assert sha(out/'trace.accesses')==sha(base/'trace_0.accesses')
  peaks=[];top=[];total=Counter();hist=Counter();fields=('frontier_pushes','frontier_polls','frontier_peak','frontier_cleared')
  with (out/'trace.jsonl').open() as new,(base/'trace_0.jsonl').open() as old:
   for index,(n,o) in enumerate(zip_longest(new,old),1):
    assert n is not None and o is not None
    row,reference=json.loads(n),json.loads(o);counts={k:row.pop(k) for k in fields};assert row==reference
    assert counts['frontier_polls']==row['pops'] and counts['frontier_pushes']==counts['frontier_polls']+counts['frontier_cleared']
    assert 1<=counts['frontier_peak']<=counts['frontier_pushes']
    peaks.append(counts['frontier_peak']);hist[counts['frontier_peak']]+=1;total.update(counts)
    top.append({'attempt':row['attempt'],'iteration':row['iteration'],'connection_id':row['connection_id'],**counts})
  assert len(peaks)==570286 and total['frontier_pushes']==metrics['pushes'];peaks.sort();top=sorted(top,key=lambda x:x['frontier_peak'],reverse=True)[:20]
  graphs=[]
  for stage,entry,arity,nodes,edges,edge_sum,degree,lazy in re.findall(r'FRONTIER_GRAPH stage=(before|after) entry_bytes=(\d+) heap_arity=(\d+) nodes=(\d+) edges=(\d+) edge_sum=(\d+) max_degree=(\d+) lazy=(\d+)',log):
   graphs.append({'stage':stage,**dict(zip(['entry_bytes','heap_arity','nodes','edges','edge_sum','max_degree','lazy'],map(int,[entry,arity,nodes,edges,edge_sum,degree,lazy])))})
  assert len(graphs)==2 and graphs[0]['stage']=='before' and graphs[1]['stage']=='after'
  assert {k:v for k,v in graphs[0].items() if k!='stage'}=={k:v for k,v in graphs[1].items() if k!='stage'}
  assert graphs[0]['nodes']==config['nodes'] and graphs[0]['edges']==graphs[0]['edge_sum'] and graphs[0]['lazy']==0 and graphs[0]['heap_arity']==8 and graphs[0]['entry_bytes']==8
  result={'status':'passed','attempts':len(peaks),'totals':dict(total),'peak_quantiles':{str(p):peaks[max(0,(len(peaks)*p+99)//100-1)] for p in [50,90,99,100]},'peak_histogram':dict(sorted(hist.items())),'top20':top,'graph_layout':graphs,'capacity_coverage':[{'capacity_entries':cap,'payload_bytes':cap*8,'overflow_attempts':sum(v for k,v in hist.items() if k>cap)} for cap in [64,256,1024,4096,16384,65536,262144,1048576]],'scope':'Measured frontier entry demand over complete verified CPU route; no hardware latency, banking, graph upload, kernel, synthesis or speedup proof.'}
  (out/'frontier_analysis.json').write_text(json.dumps(result,indent=2)+'\n')
  m.update(status='passed',attempts=len(peaks),result_sha256=sha(out/'trace.result'),accesses_sha256=sha(out/'trace.accesses'),metadata_sha256=sha(out/'trace.jsonl'),analysis_sha256=sha(out/'frontier_analysis.json'));save();print(json.dumps({k:result[k] for k in ['status','attempts','peak_quantiles','graph_layout','capacity_coverage']},indent=2),flush=True)
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
