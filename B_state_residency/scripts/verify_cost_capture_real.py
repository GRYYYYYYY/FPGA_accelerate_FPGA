"""Full real route with streaming first-touch children plus verified exclusion/frontier."""
from pathlib import Path
from itertools import zip_longest
import json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha
from profile_real import parse_log
from build_cost_capture_router import generate

def main():
 base=ROOT/'results/search_cost_real_20261024';bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
 audit=base/'source_bound_audit.json';assert json.loads(audit.read_text())['status']=='passed'
 original=ROOT/'results/real_trace_20261022T165136Z';om=json.loads((original/'manifest.json').read_text());assert om['status']=='passed'
 assert sha(ROOT/om['config']['input'])==om['config']['input_sha256']
 out=ROOT/'results/cost_capture_real_20261024';out.mkdir();src=out/'sources';src.mkdir();include=out/'include'
 m={'status':'preparing','pid':os.getpid(),'baseline_manifest_sha256':sha(base/'manifest.json'),'baseline_audit_sha256':sha(audit),'runner_sha256':sha(Path(__file__)),'sources':{},'commands':[],'scope':'Full CPU route with pure cost arithmetic, unchanged geometry/exclusion/children and bounded frontier; no cost RTL or speed claim.'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 unit=ROOT/'results/search_cost_unit_20261024/manifest.json'
 assert json.loads(unit.read_text())['status']=='passed' and json.loads(unit.read_text())['helper_sha256']==sha(ROOT/'hardware/search/search_cost.hpp')
 m['unit_gate_sha256']=sha(unit)
 save()
 try:
  for p in (base/'sources').iterdir():assert sha(p)==bm['sources'][str(p.relative_to(base))]
  source,header=generate((base/'sources/trace.cpp').read_text(),(base/'sources/real_trace.hpp').read_text())
  for p in (base/'sources').iterdir():(src/p.name).write_bytes(p.read_bytes())
  (src/'trace.cpp').write_text(source);(src/'real_trace.hpp').write_text(header)
  component=ROOT/'hardware/search'
  for name in ['cost_observe.hpp']:(src/name).write_bytes((component/name).read_bytes())
  for p in (base/'include').rglob('*'):
   if p.is_file():
    assert sha(p)==bm['sources'][str(p.relative_to(base))];q=include/p.relative_to(base/'include');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
  generator=ROOT/'adapters/build_cost_capture_router.py';(out/generator.name).write_bytes(generator.read_bytes());(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes());m['generator_sha256']=sha(generator)
  m['sources']={str(p.relative_to(out)):sha(p) for folder in [src,include] for p in folder.rglob('*') if p.is_file()}
  binary=out/'router_cost_capture';cmd=['g++','-std=c++17','-O3','-g','-fno-fast-math','-fno-omit-frame-pointer','-no-pie','-pthread','-I',str(include),'-I',str(src),str(src/'trace.cpp'),'-o',str(binary)]
  m['status']='building';m['commands'].append({'stage':'build','argv':cmd});save()
  with (out/'build.log').open('w') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
  m['commands'][-1]['exit_code']=0;m['binary_sha256']=sha(binary)
  cfg=om['config'];prefix=out/'trace';env={k:v for k,v in os.environ.items() if not k.startswith(('RW_','B_SAMPLE','B_TRACE','B_PROFILE'))}
  extra=dict(cfg['environment'],B_COST_VECTORS=str(out/'cost_packets.txt'),B_TRACE_PREFIX=str(prefix),B_TRACE_STRIDE=str(cfg['trace_stride']),B_PROFILE_PREFIX=str(prefix));env.update(extra);m['environment']=extra
  cmd=['/usr/bin/time','-v','-o',str(out/'trace.time'),'taskset','-c',str(cfg['cpu']),str(binary),str(ROOT/cfg['input']),str(out/'trace.result')]
  m['commands'].append({'stage':'route','argv':cmd});m['status']='running';save()
  with (out/'trace.log').open('w') as log:
   proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,env=env);m['commands'][-1]['pid']=proc.pid;save();code=proc.wait(timeout=600);m['commands'][-1]['exit_code']=code;save();assert code==0
  metrics=parse_log((out/'trace.log').read_text());assert metrics['convergence']==bm['metrics']['convergence'] and metrics['pushes']==bm['metrics']['pushes']
  assert sha(out/'trace.result')==bm['result_sha256'] and sha(out/'trace.accesses')==bm['accesses_sha256']
  count=0
  with (out/'trace.jsonl').open() as new,(base/'trace.jsonl').open() as old:
   for n,o in zip_longest(new,old):assert n is not None and o is not None and json.loads(n)==json.loads(o);count+=1
  assert count==570286
  m.update(cost_packets_sha256=sha(out/'cost_packets.txt'),status='passed',attempts=count,metrics=metrics,result_sha256=sha(out/'trace.result'),accesses_sha256=sha(out/'trace.accesses'),metadata_sha256=sha(out/'trace.jsonl'));save();print('COST_CAPTURE_REAL_PASS attempts=570286 all_metadata_equal=1 label_access_binary_equal=1 result_equal=1',flush=True)
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
