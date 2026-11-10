"""Freeze and run actual Frontier RTL lifecycle and independent collector checks."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();hls=ROOT/'results/frontier_hls_relative_project_20261024'
 gatepath=hls/'source_bound_audit.json';gate=json.loads(gatepath.read_text());assert gate['status']=='passed'
 out.mkdir();src=out/'sources';src.mkdir()
 m={'status':'running','sources':{},'commands':[],'hls_gate':{'path':str(gatepath),'sha256':sha(gatepath)},'runner_sha256':sha(Path(__file__))}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 paths=[]
 for name,digest in gate['generated_rtl_artifacts'].items():
  p=hls/'frontier_step/solution1/syn/verilog'/name;assert sha(p)==digest
  if p.suffix in ('.v','.dat'):paths.append(p)
 paths+=sorted((ROOT/'hardware/variants/frontier_service_v1').glob('*.sv'))
 for p in paths:
  (src/p.name).write_bytes(p.read_bytes());m['sources'][p.name]={'path':str(p),'sha256':sha(p)}
  if p.suffix=='.dat':(out/p.name).write_bytes(p.read_bytes())
 (out/'runner.py').write_bytes(Path(__file__).read_bytes());(out/'run.tcl').write_text('run 200ms\nquit\n');save()
 cmds=[('compile',[BIN/'xvlog','--sv',*[src/p.name for p in paths if p.suffix in ('.v','.sv')]])]
 for name in ['frontier_hls_call','frontier_service']:
  cmds += [(name+'_elaborate',[BIN/'xelab','tb_'+name,'-s',name,'--debug','typical','--mt','2']),
   (name+'_simulate',[BIN/'xsim',name,'--tclbatch','run.tcl','--log',name+'.log'])]
 for stage,args in cmds:
  argv=list(map(str,args));start=time.monotonic()
  with (out/(stage+'.stdout.log')).open('w') as f:r=subprocess.run(argv,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=300)
  m['commands'].append({'stage':stage,'argv':argv,'exit_code':r.returncode,'elapsed_s':time.monotonic()-start});save();assert r.returncode==0,stage
  if stage.endswith('_simulate'):
   log=(out/(stage.replace('_simulate','')+'.log')).read_text()
   marker='FRONTIER_CALL_PASS permutations=120 coherent_calls=121 fault_cases=12' if 'hls_call' in stage else 'FRONTIER_SERVICE_PASS'
   assert marker in log and 'Fatal:' not in log and '$finish called' in log,stage
 m.update(status='passed',artifacts={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.suffix in ('.log','.tcl','.txt')});save();print(m['status'])
if __name__=='__main__':main()
