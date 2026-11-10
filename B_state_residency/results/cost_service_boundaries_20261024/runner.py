"""Freeze and simulate the exact cost core with its actual ap_memory service."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();hls=ROOT/'results/search_cost_exact_hls_20261024'
 gatepath=hls/'source_bound_audit.json';gate=json.loads(gatepath.read_text())
 hm=json.loads((hls/'manifest.json').read_text())
 assert gate['status']=='passed' and gate['rtl_bit_exact_on_all_vectors']
 assert gate['manifest_sha256']==sha(hls/'manifest.json')
 out.mkdir();src=out/'sources';src.mkdir()
 m={'status':'running','sources':{},'commands':[],'hls_gate':{'path':str(gatepath),'sha256':sha(gatepath)},'runner_sha256':sha(Path(__file__))}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 paths=[]
 for name,digest in hm['generated_rtl_artifacts'].items():
  p=hls/name;assert sha(p)==digest
  if p.suffix in ('.v','.dat') and '/syn/verilog/' in name:paths.append(p)
 paths+=[ROOT/'hardware/variants/cost_service_v2'/name for name in ['cost_memory_call.sv','cost_service.sv']]
 paths+=sorted((ROOT/'hardware/variants/cost_service_boundaries_v1').glob('*.sv'))
 assert len({p.name for p in paths})==len(paths)
 for p in paths:
  (src/p.name).write_bytes(p.read_bytes());m['sources'][p.name]={'path':str(p),'sha256':sha(p)}
  if p.suffix=='.dat':(out/p.name).write_bytes(p.read_bytes())
 (out/'vectors.txt').write_bytes((hls/'vectors.txt').read_bytes());m['vectors_sha256']=sha(out/'vectors.txt')
 assert m['vectors_sha256']==hm['vectors_sha256']
 (out/'runner.py').write_bytes(Path(__file__).read_bytes());(out/'run.tcl').write_text('run 200ms\nquit\n');save()
 cmds=[('compile',[BIN/'xvlog','--sv',*[src/p.name for p in paths if p.suffix in ('.v','.sv')]])]
 for name in ['cost_service_boundaries']:
  cmds += [(name+'_elaborate',[BIN/'xelab','tb_'+name,'-s',name,'--debug','typical','--mt','2']),
   (name+'_simulate',[BIN/'xsim',name,'--tclbatch','run.tcl','--log',name+'.log'])]
 try:
  for stage,args in cmds:
   argv=list(map(str,args));start=time.monotonic()
   with (out/(stage+'.stdout.log')).open('w') as f:r=subprocess.run(argv,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=300)
   m['commands'].append({'stage':stage,'argv':argv,'exit_code':r.returncode,'elapsed_s':time.monotonic()-start});save();assert r.returncode==0,stage
   if stage.endswith('_simulate'):
    log=(out/(stage.replace('_simulate','')+'.log')).read_text()
    marker='COST_SERVICE_BOUNDARIES_PASS fault_cases=45'
    assert marker in log and 'Fatal:' not in log and '$finish called' in log,stage
  m['status']='passed'
 except Exception as e:
  m.update(status='failed',error=repr(e));raise
 finally:
  m['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.suffix in ('.log','.tcl','.txt')};save()
 print(m['status'])
if __name__=='__main__':main()
