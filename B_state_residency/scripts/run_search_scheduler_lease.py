from pathlib import Path
import json,hashlib,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();m=dict(status='running',sources={},commands=[],scope='Prepared query RTL search: seed/poll/label/expand/checkpoint; identities, failures, bound, drain and stalled request retirement.')
 for p in [ROOT/'hardware/variants/search_scheduler_v1/search_scheduler.sv',ROOT/'hardware/variants/search_scheduler_v1/search_host_fence.sv',ROOT/'hardware/variants/search_scheduler_v1/tb_search_lease.sv',Path(__file__)]:shutil.copyfile(p,src/p.name);m['sources'][p.name]=sha(src/p.name)
 (out/'run.tcl').write_text('run 2ms\nquit\n')
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  for stage,cmd in [('compile',[BIN/'xvlog','--sv',src/'search_scheduler.sv',src/'search_host_fence.sv',src/'tb_search_lease.sv']),('elaborate',[BIN/'xelab','tb_search_scheduler','-s','search_scheduler','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','search_scheduler','--tclbatch','run.tcl','--log','simulate.log','--testplusarg','events='+str(out/'events.txt')])]:
   cmd=list(map(str,cmd));t=time.monotonic()
   with(out/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(cmd,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=180)
   m['commands'].append(dict(stage=stage,argv=cmd,exit_code=r.returncode,elapsed_s=time.monotonic()-t));save();assert r.returncode==0,stage
  log=(out/'simulate.log').read_text();assert 'SEARCH_SCHEDULER_PASS checks='in log and 'Fatal:'not in log and '$finish called'in log;m['status']='passed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:m['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.name!='manifest.json'};save()
 print('SEARCH_SCHEDULER_SIM_PASSED')
if __name__=='__main__':main()
