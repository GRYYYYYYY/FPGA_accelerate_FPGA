"""Reproduce original two-module interface overlap in bounded XSim 2022.2."""
from pathlib import Path
import hashlib,json,subprocess,os,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from shadow_terminal_receipt_v1 import record_child_exit,record_exception
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025');p=B/'ka_publication_release_overlap_xsim_v1';V=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ident(pid):return Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()[19]
m=json.loads((p/'manifest.json').read_text());assert m['status']=='prepared'
for n,h in m['sources'].items():assert sha(p/n)==h
helper=R/'scripts/shadow_terminal_receipt_v1.py';cal=R/'results/shadow_terminal_receipt_v1_calibration_20261031.json';assert json.loads(cal.read_text())['helper_sha256']==sha(helper)
m.update(status='running',runner_pid=os.getpid(),runner_start_ticks=ident(os.getpid()),runner_sha256=sha(Path(__file__)),helper_sha256=sha(helper))
def save():(p/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
jobs=[('compile',[str(V/'xvlog'),'-sv','checkpoint_lease_guard.sv','checkpoint_publish_barrier.sv','tb.sv','-log','xvlog.log']),('elaborate',[str(V/'xelab'),'tb','-debug','typical','-s','overlap_snapshot','-log','xelab.log']),('simulate',[str(V/'xsim'),'overlap_snapshot','-tclbatch','run.tcl','-onfinish','stop','-log','simulate.log'])];child=None;save()
try:
 for stage,argv in jobs:
  m['stage']=stage;start=time.monotonic()
  with (p/(stage+'.stdout.log')).open('w') as log:
   child=subprocess.Popen(argv,cwd=p,stdout=log,stderr=subprocess.STDOUT);m['active_process']={'pid':child.pid,'start_ticks':ident(child.pid),'argv':argv};save();code=child.wait()
  record_child_exit(m,code);m['commands'].append({'stage':stage,'exit_code':code,'argv':argv,'elapsed_s':time.monotonic()-start,'stdout_sha256':sha(p/(stage+'.stdout.log'))});save();assert code==0
  print(stage,'observed',flush=True)
 text=(p/'simulate.log').read_text();assert all(text.count(s)==1 for s in m['expected_markers']);assert 'Fatal:' not in text and 'ERROR:' not in text
 m.update(status='reproduction_observed',stage='complete')
except BaseException as e:record_exception(m,e,child);raise
finally:save()
