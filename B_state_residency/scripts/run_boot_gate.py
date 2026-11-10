"""Run self-checking boot receipt component tests in an immutable run folder."""
from pathlib import Path
import sys,json,shutil,subprocess
from run_checkpoint_authority import ROOT,BIN,sha
out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();bench=ROOT/'hardware/variants/cold_boot_v1';sources={}
for n in ['boot_restore_gate.sv','tb_boot.sv']:
 shutil.copyfile(bench/n,src/n);sources[n]=sha(src/n)
m={'status':'running','sources':sources,'commands':[]};mf=out/'manifest.json'
try:
 for stage,args in [('compile',[BIN/'xvlog','--sv',src/'boot_restore_gate.sv',src/'tb_boot.sv']),('elaborate',[BIN/'xelab','tb_boot','-s','boot','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','boot','-runall'])]:
  with(out/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(list(map(str,args)),cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=120)
  m['commands'].append({'stage':stage,'exit_code':r.returncode,'argv':list(map(str,args))});assert r.returncode==0
 log=(out/'simulate.stdout.log').read_text();assert 'BOOT_GATE_PASS checks=31'in log and 'Fatal:'not in log;m['status']='passed'
except Exception as e:m.update(status='failed',error=repr(e));raise
finally:mf.write_text(json.dumps(m,indent=2)+'\n')
print(m['status'])
