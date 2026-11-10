"""Bounded standalone selector/identity protocol regression, Vivado 2022.2 XSim."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir()
 m={'status':'running','sources':{},'commands':[]}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 for name in ['children_frames.sv','tb_children_frames.sv']:
  p=ROOT/'hardware/variants/recursive_frames_v1'/name;shutil.copyfile(p,src/name);m['sources'][name]={'path':str(p),'sha256':sha(p)}
 shutil.copyfile(Path(__file__),out/'runner.py');m['runner_sha256']=sha(out/'runner.py');(out/'run.tcl').write_text('run 5ms\nquit\n');save()
 try:
  for stage,args in [('compile',[BIN/'xvlog','--sv',src/'children_frames.sv',src/'tb_children_frames.sv']),('elaborate',[BIN/'xelab','tb_children_frames','-s','prefetch','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','prefetch','--tclbatch','run.tcl','--log','simulate.log'])]:
   start=time.monotonic();argv=list(map(str,args))
   with (out/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(argv,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=180)
   m['commands'].append({'stage':stage,'argv':argv,'exit_code':r.returncode,'elapsed_s':time.monotonic()-start});save();assert r.returncode==0
  log=(out/'simulate.log').read_text();assert 'CHILDREN_FRAMES_PASS cases=9 items=4'in log and 'Fatal:'not in log and '$finish called'in log
  m['status']='passed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:m['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.suffix in ['.log','.tcl']};save()
 print(m['status'])
if __name__=='__main__':main()
