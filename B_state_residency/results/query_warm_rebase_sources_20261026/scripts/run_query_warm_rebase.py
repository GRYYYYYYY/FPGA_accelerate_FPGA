from pathlib import Path
import sys,json,shutil,subprocess,time,struct
from run_checkpoint_authority import ROOT,BIN,sha
from verify_rtl_bundle import verify
p=Path(sys.argv[1]).resolve();p.mkdir();src=p/'sources';src.mkdir();v=ROOT/'hardware/variants/query_warm_rebase_v1';bundle=Path('/tmp/B_state_residency_offer_20261025/bundle_capture_v3/full_5/bundle');verify(bundle)
m=dict(status='running',sources={},commands=[],bundle=str(bundle),bundle_manifest_sha256=sha(bundle/'manifest.json'))
for f,n in [(v/n,n)for n in ['build.py','query_lifecycle.sv','tb_rebase.sv']]+[(Path(__file__),'runner.py')]:shutil.copyfile(f,src/n);m['sources'][n]=dict(path=str(f),sha256=sha(src/n))
(p/'query.hex').write_text(''.join(f'{w:08x}\n'for w, in struct.iter_unpack('<I',(bundle/'query.bin').read_bytes())));(p/'run.tcl').write_text('run 100us\nquit\n')
def save():(p/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
try:
 for stage,args in [('compile',[BIN/'xvlog','--sv',src/'query_lifecycle.sv',src/'tb_rebase.sv']),('elaborate',[BIN/'xelab','tb_rebase','-s','rebase','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','rebase','--tclbatch','run.tcl','--log','simulate.log'])]:
  t=time.monotonic()
  with(p/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(list(map(str,args)),cwd=p,stdout=f,stderr=subprocess.STDOUT,timeout=180)
  m['commands'].append(dict(stage=stage,exit_code=r.returncode,elapsed_s=time.monotonic()-t));save();assert r.returncode==0,stage
 log=(p/'simulate.log').read_text();assert 'QUERY_REBASE_PASS'in log and 'Fatal:'not in log,log[-1800:];m['status']='observed';print(next(x for x in log.splitlines()if x.startswith('QUERY_REBASE_PASS')))
except Exception as e:m.update(status='failed',error=repr(e));raise
finally:save()
