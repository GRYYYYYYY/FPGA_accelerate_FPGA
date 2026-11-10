from pathlib import Path
import json,hashlib,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();m={'status':'running','sources':{},'commands':[]};rtl=[]
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 for p in [ROOT/'hardware/variants/cost_state_v1/cost_state_store.sv',ROOT/'hardware/variants/cost_state_v1/tb_cost_state_boundaries.sv',ROOT/'results/access_owner_v3_20261024/sources/coordinate/axi_file_memory.sv']:
  q=src/p.name;shutil.copyfile(p,q);m['sources'][p.name]={'path':str(p),'sha256':sha(q)};rtl.append(q)
 initial=ROOT/'results/cost_state_inputs_20261025/synthetic/initial.bin';shutil.copyfile(initial,out/'state.bin');m['initial_sha256']=sha(initial);shutil.copyfile(__file__,src/'runner.py');(out/'run.tcl').write_text('run 1ms\nquit\n');save()
 args=[BIN/'xsim','state','--tclbatch','run.tcl','--log','simulate.log']
 for k,v in {'state0':out/'state.bin','statelog':out/'axi.txt','initial':initial}.items():args+=['--testplusarg',k+'='+str(v)]
 try:
  for stage,argv in [('compile',[BIN/'xvlog','--sv']+rtl),('elaborate',[BIN/'xelab','tb_cost_state_boundaries','-s','state','--debug','typical','--mt','2']),('simulate',args)]:
   row={'stage':stage,'argv':list(map(str,argv))};m['commands'].append(row);save()
   with (out/(stage+'.stdout.log')).open('w')as f:row['exit_code']=subprocess.call(row['argv'],cwd=out,stdout=f,stderr=subprocess.STDOUT)
   save();assert row['exit_code']==0,stage
  log=(out/'simulate.log').read_text();hits=[s for s in log.splitlines()if s.startswith('COST_STATE_BOUNDARY_PASS ')];assert len(hits)==1 and 'Fatal:'not in log and '$finish called'in log,log[-2500:]
  assert sha(out/'state.bin')==sha(initial);m.update(status='passed',result=hits[0],artifacts={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.name!='manifest.json'});save();print(hits[0])
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
