"""Bounded standalone selector/identity protocol regression, Vivado 2022.2 XSim."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir()
 inp=ROOT/'results/connection_state_inputs_20261025';gate=json.loads((inp/'source_bound_audit.json').read_text());assert gate['status']=='passed' and gate['manifest_sha256']==sha(inp/'manifest.json')
 m={'status':'running','sources':{},'commands':[],'input_sha256':sha(inp/'connections.bin'),'input_gate_sha256':sha(inp/'source_bound_audit.json')}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 for name in ['connection_state_reader.sv','tb_connection_state.sv']:
  p=ROOT/'hardware/variants/connection_state_v1'/name;shutil.copyfile(p,src/name);m['sources'][name]={'path':str(p),'sha256':sha(p)}
 shutil.copyfile(Path(__file__),out/'runner.py');m['runner_sha256']=sha(out/'runner.py');(out/'run.tcl').write_text('run 5ms\nquit\n');save()
 try:
  for stage,args in [('compile',[BIN/'xvlog','--sv',src/'connection_state_reader.sv',src/'tb_connection_state.sv']),('elaborate',[BIN/'xelab','tb_connection_state','-s','prefetch','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','prefetch','--tclbatch','run.tcl','--log','simulate.log','--testplusarg','input='+str(ROOT/'results/connection_state_inputs_20261025/connections.bin')])]:
   start=time.monotonic();argv=list(map(str,args))
   with (out/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(argv,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=180)
   m['commands'].append({'stage':stage,'argv':argv,'exit_code':r.returncode,'elapsed_s':time.monotonic()-start});save();assert r.returncode==0
  log=(out/'simulate.log').read_text();assert 'CONNECTION_STATE_PASS real_rows=182 errors=7'in log and 'Fatal:'not in log and '$finish called'in log
  assert sha(inp/'connections.bin')==m['input_sha256']
  m['status']='passed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:m['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.suffix in ['.log','.tcl']};save()
 print(m['status'])
if __name__=='__main__':main()
