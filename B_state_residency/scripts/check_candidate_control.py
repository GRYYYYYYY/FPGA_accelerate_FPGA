from pathlib import Path
import hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();m={'status':'running','sources':{},'commands':[]}
 for n in ['candidate_controller.sv','tb_candidate_control.sv']:
  p=ROOT/'hardware/variants/candidate_pipeline_v1'/n;q=src/n;shutil.copyfile(p,q);m['sources'][n]={'path':str(p),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()}
 shutil.copyfile(__file__,src/'runner.py');(out/'run.tcl').write_text('run 1ms\nquit\n')
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 for stage,argv in [('compile',[BIN/'xvlog','--sv',src/'candidate_controller.sv',src/'tb_candidate_control.sv']),('elaborate',[BIN/'xelab','tb_candidate_control','-s','test']),('simulate',[BIN/'xsim','test','--tclbatch','run.tcl','--log','simulate.log'])]:
  with (out/(stage+'.log')).open('w')as f:code=subprocess.call(list(map(str,argv)),cwd=out,stdout=f,stderr=subprocess.STDOUT)
  m['commands'].append({'stage':stage,'exit_code':code});save()
  if code:m['status']='failed';save();raise RuntimeError(stage)
 lines=(out/'simulate.log').read_text();hits=[s for s in lines.splitlines()if s.startswith('CANDIDATE_CONTROL_PASS ')]
 if not(len(hits)==1 and 'Fatal:'not in lines and '$finish called'in lines):
  m.update(status='failed',error='Missing unique PASS or fatal XSim simulation');save();raise AssertionError(m['error'])
 m.update(status='passed',result=hits[0]);save();print(hits[0])
if __name__=='__main__':main()
