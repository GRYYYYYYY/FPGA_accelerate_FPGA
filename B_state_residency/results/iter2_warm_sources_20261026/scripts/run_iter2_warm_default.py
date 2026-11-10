"""Full proven commit/GET/q2 scenarios with rebase default-disabled."""
from pathlib import Path
import sys,json,shutil,subprocess,time
from run_checkpoint_authority import ROOT,BIN,sha
p=Path(sys.argv[1]).resolve();p.mkdir();src=p/'sources';src.mkdir();base=Path('/tmp/B_state_residency_offer_20261025/warm_shared_last_v1');bm=json.loads((base/'manifest.json').read_text());ba=json.loads((base/'source_bound_audit.json').read_text());assert ba['status']=='passed'and ba['manifest_sha256']==sha(base/'manifest.json')
m=dict(status='running',base=str(base),sources={},rtl=bm['rtl'],cases={},scope='Default512 restore capacity regression with parameterized three-level hierarchy, exact all outputs/cycles versus audited shared-last baseline.')
def copy(f,n):
 (src/n).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,src/n);m['sources'][n]=dict(path=str(f),sha256=sha(src/n))
for n,h in bm['sources'].items():
 assert sha(base/'sources'/n)==h['sha256'];copy(ROOT/'hardware/variants/iter2_warm_v1'/n if n in ['query_residency_system.sv','search_residency_system.sv','residency_system.sv']else ROOT/'hardware/variants/multi_owner_recovery_v1'/n if n=='recovery_coordinator.sv'else ROOT/'hardware/variants/warm_retry_v1'/n if n in ['query_residency_system.sv','warm_restore_receipt_join.sv']else Path('/tmp/B_state_residency_offer_20261025/warm_cancel_fixed_v2/sources')/n if n in ['residency_system.sv','search_residency_system.sv','recovery_coordinator.sv']else base/'sources'/n,n)
copy(Path(__file__),'regression_runner.py');copy(ROOT/'hardware/variants/iter2_warm_v1/build.py','restore_build.py');copy(ROOT/'hardware/variants/multi_owner_recovery_v1/build.py','capacity_build.py');copy(ROOT/'hardware/variants/warm_retry_v1/build.py','cancel_build.py');inp=Path(json.loads((Path(bm['base'])/'manifest.json').read_text())['input'])
def save():(p/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
def run(d,stage,args,c):
 t=time.monotonic()
 with(d/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(list(map(str,args)),cwd=d,stdout=f,stderr=subprocess.STDOUT,timeout=600)
 c['commands'].append(dict(stage=stage,exit_code=r.returncode,elapsed_s=time.monotonic()-t,argv=list(map(str,args))));save();assert r.returncode==0,stage
try:
 for name,define in [('full_5',None),('pressure_5','PRESSURE')]:
  if '--full-only'in sys.argv and name!='full_5':continue
  if '--pressure-only'in sys.argv and name!='pressure_5':continue
  d=p/name;d.mkdir();c=m['cases'][name]=dict(status='running',commands=[]);save()
  run(d,'compile',[BIN/'xvlog','--sv','--define','BUNDLE_TRACE','--define','QC_NO_LOSS']+(['--define',define]if define else[])+[src/n for n in m['rtl']],c)
  run(d,'elaborate',[BIN/'xelab','tb_candidate_offer','-s','normal','--debug','typical','--mt','2'],c)
  shutil.copyfile(base/name/'warm_imports.txt',d/'warm_imports.txt')
  for n in ['design.bin','owners.bin','cost.bin']:shutil.copyfile(inp/n,d/n)
  with(d/'owners.bin').open('ab')as f:f.write((inp/'owner_allocator.bin').read_bytes())
  shutil.copyfile(inp/'owners.bin',d/'primary.bin');shutil.copyfile(inp/'owner_allocator.bin',d/'allocator.bin');shutil.copyfile(base/name/'pool.bin',d/'pool.bin')
  with(d/'labels.bin').open('wb')as f:f.truncate(3145728)
  for f in src.rglob('*.dat'):shutil.copyfile(f,d/f.name)
  (d/'run.tcl').write_text('run 30ms\nquit\n');args=[BIN/'xsim','normal','--tclbatch','run.tcl','--log','simulate.log'];old=bm['cases'][name]['commands'][-1]['argv']
  for i,x in enumerate(old):
   if x!='--testplusarg':continue
   k,v=old[i+1].split('=',1)
   if k in ['design0','owners0','cost0','labels0','snapshot0','snapshot1','snapshot2','warmimports']or k.endswith('log'):v=str(d/Path(v).name)
   args+=['--testplusarg',k+'='+v]
  run(d,'simulate',args,c);log=(d/'simulate.log').read_text();assert 'JOINT_SYSTEM_COMMIT_PASS'in log and 'Fatal:'not in log;assert 'QUERY_FAULT_OBSERVED case=5 outcome=recovered_retry'in log;c['status']='observed';save();print(name,'observed',flush=True)
 m['status']='observed'
except Exception as e:m.update(status='failed',error=repr(e));raise
finally:save()
