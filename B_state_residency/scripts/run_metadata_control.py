from pathlib import Path
import hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir()
 m={'status':'running','sources':{},'commands':[]}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 for p in list((ROOT/'hardware/variants/metadata_control_tests_v1').iterdir())+[ROOT/'hardware/variants/metadata_v1/metadata_controller.sv',Path(__file__)]:
  if p.is_file():shutil.copyfile(p,src/p.name);m['sources'][p.name]={'path':str(p),'sha256':sha(p)}
 (out/'run.tcl').write_text('run 1ms\nquit\n');save()
 try:
  for stage,args in [('compile',[BIN/'xvlog','--sv',src/'metadata_controller.sv',src/'tb_metadata_control.sv']),('elaborate',[BIN/'xelab','tb_metadata_control','-s','test','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','test','--tclbatch','run.tcl','--log','simulate.log'])]:
   c={'stage':stage,'argv':list(map(str,args))};m['commands'].append(c);save()
   with (out/(stage+'.stdout.log')).open('w')as f:c['exit_code']=subprocess.call(c['argv'],cwd=out,stdout=f,stderr=subprocess.STDOUT)
   save();assert c['exit_code']==0,stage
  log=(out/'simulate.log').read_text();hits=[s for s in log.splitlines()if s.startswith('METADATA_CONTROL_PASS ')];assert len(hits)==1 and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log,log[-1800:]
  m.update(status='passed',result=hits[0]);save();print(hits[0])
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
