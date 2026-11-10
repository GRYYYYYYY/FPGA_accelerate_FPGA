"""Measure exact original owner-slot mutations during the complete serial CPU route."""
from pathlib import Path
from itertools import zip_longest
import json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'));sys.path.insert(0,str(ROOT/'scripts'))
from prepare_real import sha
from profile_real import parse_log
from build_owner_profile_router import generate

def main():
 base=ROOT/'results/search_access_real_20261024';bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
 audit=base/'source_bound_audit.json';assert json.loads(audit.read_text())['status']=='passed'
 original=ROOT/'results/real_trace_20261022T165136Z';om=json.loads((original/'manifest.json').read_text());assert om['status']=='passed'
 assert sha(ROOT/om['config']['input'])==om['config']['input_sha256']
 out=ROOT/'results/owner_profile_real_20261024';out.mkdir();src=out/'sources';src.mkdir();include=out/'include'
 m={'status':'preparing','pid':os.getpid(),'baseline_manifest_sha256':sha(base/'manifest.json'),'baseline_audit_sha256':sha(audit),'runner_sha256':sha(Path(__file__)),'sources':{},'commands':[],'scope':'Original owner-slot mutations observed on complete serial CPU route, with every mutation recorded. Domain guards forbid uint16 reference/occupancy wrap. Not a hardware implementation or performance comparison.'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  for p in (base/'sources').iterdir():assert sha(p)==bm['sources'][str(p.relative_to(base))]
  source,header=generate((base/'sources/trace.cpp').read_text(),(base/'sources/real_trace.hpp').read_text())
  for p in (base/'sources').iterdir():(src/p.name).write_bytes(p.read_bytes())
  (src/'trace.cpp').write_text(source);(src/'real_trace.hpp').write_text(header)
  (src/'owner_profile.hpp').write_bytes((ROOT/'adapters/owner_profile.hpp').read_bytes())
  for p in (base/'include').rglob('*'):
   if p.is_file():
    assert sha(p)==bm['sources'][str(p.relative_to(base))];q=include/p.relative_to(base/'include');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
  generator=ROOT/'adapters/build_owner_profile_router.py';(out/generator.name).write_bytes(generator.read_bytes());(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes());m['generator_sha256']=sha(generator)
  m['sources']={str(p.relative_to(out)):sha(p) for folder in [src,include] for p in folder.rglob('*') if p.is_file()}
  binary=out/'router_owner_profile';cmd=['g++','-std=c++17','-O3','-g','-fno-fast-math','-fno-omit-frame-pointer','-no-pie','-pthread','-I',str(include),'-I',str(src),str(src/'trace.cpp'),'-o',str(binary)]
  m['status']='building';m['commands'].append({'stage':'build','argv':cmd});save()
  with (out/'build.log').open('w') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
  m['commands'][-1]['exit_code']=0;m['binary_sha256']=sha(binary)
  cfg=om['config'];prefix=out/'trace';env={k:v for k,v in os.environ.items() if not k.startswith(('RW_','B_SAMPLE','B_TRACE','B_PROFILE','B_OWNER'))}
  extra=dict(cfg['environment'],B_TRACE_PREFIX=str(prefix),B_TRACE_STRIDE=str(cfg['trace_stride']),B_PROFILE_PREFIX=str(prefix),B_OWNER_PREFIX=str(out/'owner'));env.update(extra);m['environment']=extra
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
  m.update(status='passed',owner_profile=json.loads((out/'owner.json').read_text()),owner_events_sha256=sha(out/'owner.events'),owner_profile_sha256=sha(out/'owner.json'),attempts=count,metrics=metrics,result_sha256=sha(out/'trace.result'),accesses_sha256=sha(out/'trace.accesses'),metadata_sha256=sha(out/'trace.jsonl'));save();print('OWNER_PROFILE_REAL_PASS attempts=570286 all_metadata_equal=1 label_access_binary_equal=1 result_equal=1',flush=True)
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
