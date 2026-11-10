"""Bounded XSim gate-level protocol unit (callbacks/fence are testbench inputs)."""
from pathlib import Path
import json,hashlib,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir()
 m=dict(status='running',scope='Behavioral RTL unit of warm receipt join; fence/restore/completion inputs are modeled. No real DDR/coordinator retry proof.',sources={},commands=[])
 for p in [ROOT/'hardware/variants/warm_retry_v1/warm_restore_receipt_join.sv',ROOT/'hardware/variants/warm_retry_v1/tb_warm_retry.sv',ROOT/'hardware/variants/warm_retry_v1/build.py',Path(__file__)]:
  shutil.copyfile(p,src/p.name);m['sources'][p.name]=sha(src/p.name)
 (out/'run.tcl').write_text('run 10us\nquit\n')
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  for stage,cmd in [('compile',[BIN/'xvlog','--sv',src/'warm_restore_receipt_join.sv',src/'tb_warm_retry.sv']),('elaborate',[BIN/'xelab','tb_warm_retry','-s','retry','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','retry','--tclbatch','run.tcl','--log','simulate.log'])]:
   cmd=list(map(str,cmd));t=time.monotonic()
   with(out/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(cmd,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=180)
   m['commands'].append(dict(stage=stage,argv=cmd,exit_code=r.returncode,elapsed_s=time.monotonic()-t));save();assert r.returncode==0,stage
  log=(out/'simulate.log').read_text();assert 'WARM_RETRY_UNIT_PASS checks='in log and 'Fatal:'not in log and '$finish called'in log
  m['status']='passed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:
  m['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.name!='manifest.json'};save()
 print('WARM_RETRY_UNIT_PASSED')
if __name__=='__main__':main()
