"""Run adversarial trusted RF-mask boundary contract on generated controller."""
from pathlib import Path
import hashlib,json,subprocess,os
from make_sparse_records import render as rtl_render
from make_sparse_records_boundaries_tb import render
ROOT=Path(__file__).resolve().parents[2]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/sparse_records_boundaries_20261024';out.mkdir();src=out/'sources';src.mkdir()
 tb=ROOT/'hardware/tb/tb_sparse_records_boundaries.sv';assert tb.read_text()==render()
 variants=rtl_render();paths=[ROOT/'hardware/variants/sparse_records'/name for name in ['scratch_frame_store_bram.sv','scratch_page_controller_small.sv']]+[tb]
 for p in paths[:-1]:assert p.read_text()==variants[p.name]
 m={'status':'running','pid':os.getpid(),'sources':{},'commands':[],'runner_sha256':sha(Path(__file__)),'tb_generator_sha256':sha(ROOT/'hardware/scripts/make_sparse_records_boundaries_tb.py')}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 for p in paths:(src/p.name).write_bytes(p.read_bytes());m['sources'][p.name]=sha(p)
 save()
 try:
  (out/'run.tcl').write_text('run all\nquit\n')
  cmds=[('compile',[str(BIN/'xvlog'),'--sv',*[str(src/p.name) for p in paths]]),('elaborate',[str(BIN/'xelab'),'tb_sparse_records_boundaries','-s','boundaries','--debug','typical','--mt','2']),('simulate',[str(BIN/'xsim'),'boundaries','--tclbatch','run.tcl','--log','simulate.log'])]
  for stage,argv in cmds:
   with (out/f'{stage}.stdout.log').open('w') as f:
    proc=subprocess.Popen(argv,cwd=out,stdout=f,stderr=subprocess.STDOUT);step={'stage':stage,'argv':argv,'pid':proc.pid};m['commands'].append(step);save();step['exit_code']=proc.wait();save();assert step['exit_code']==0,stage
  log=(out/'simulate.log').read_text();assert 'SPARSE_RF_BOUNDARIES_PASS checks=33' in log and 'Fatal:' not in log and '$finish' in log
  m.update(status='passed',log_sha256=sha(out/'simulate.log'));save();print(m['status'],flush=True)
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
