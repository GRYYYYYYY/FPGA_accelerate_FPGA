from pathlib import Path
import json,hashlib,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=Path(sys.argv[1]).resolve();p.mkdir();src=p/'sources';src.mkdir();m={'status':'running','sources':{},'commands':[]}
for q in [ROOT/'hardware/variants/route_checkpoint_join_v1/checkpoint_lease_guard.sv',ROOT/'hardware/variants/route_checkpoint_join_v1/tb_checkpoint_lease_guard.sv',ROOT/'hardware/variants/route_checkpoint_join_v1/build.py',Path(__file__)]:shutil.copyfile(q,src/q.name);m['sources'][q.name]=sha(src/q.name)
(p/'run.tcl').write_text('run 10us\nquit\n')
def save():(p/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
save()
try:
 for name,cmd in [('compile',[BIN/'xvlog','--sv',src/'checkpoint_lease_guard.sv',src/'tb_checkpoint_lease_guard.sv']),('elaborate',[BIN/'xelab','tb_checkpoint_lease_guard','-s','guard','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','guard','--tclbatch','run.tcl','--log','simulate.log','--testplusarg','events='+str(p/'events.txt')])]:
  start=time.monotonic();cmd=list(map(str,cmd))
  with(p/(name+'.stdout.log')).open('w')as f:r=subprocess.run(cmd,cwd=p,stdout=f,stderr=subprocess.STDOUT,timeout=180)
  m['commands'].append({'stage':name,'argv':cmd,'exit_code':r.returncode,'elapsed_s':time.monotonic()-start});save();assert r.returncode==0
 log=(p/'simulate.log').read_text();assert 'CHECKPOINT_LEASE_GUARD_PASS checks=25'in log and 'Fatal:'not in log and '$finish called'in log;m['status']='passed'
except Exception as e:m.update(status='failed',error=repr(e));raise
finally:m['artifacts']={q.name:sha(q)for q in p.iterdir()if q.is_file()and q.name!='manifest.json'};save()
print('CHECKPOINT_LEASE_GUARD_PASSED')
