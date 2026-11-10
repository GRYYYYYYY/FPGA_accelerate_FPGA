"""Freeze and simulate the center distance core with its actual ap_memory service."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();hls=ROOT/'results/cost_center_hls_20261025'
 gatepath=hls/'source_bound_audit.json';gate=json.loads(gatepath.read_text())
 hm=json.loads((hls/'manifest.json').read_text())
 assert gate['status']=='passed'
 assert gate['manifest_sha256']==sha(hls/'manifest.json')
 out.mkdir();src=out/'sources';src.mkdir()
 m={'status':'running','sources':{},'commands':[],'hls_gate':{'path':str(gatepath),'sha256':sha(gatepath)},'runner_sha256':sha(Path(__file__))}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 paths=[]
 for name,digest in hm['generated_rtl_artifacts'].items():
  p=hls/name;assert sha(p)==digest
  if p.suffix in ('.v','.dat') and '/syn/verilog/' in name:paths.append(p)
 paths+=sorted((ROOT/'hardware/variants/cost_center_service_v1').glob('*.sv'))
 assert len({p.name for p in paths})==len(paths)
 for p in paths:
  (src/p.name).write_bytes(p.read_bytes());m['sources'][p.name]={'path':str(p),'sha256':sha(p)}
  if p.suffix=='.dat':(out/p.name).write_bytes(p.read_bytes())
 (out/'vectors.txt').write_bytes((hls/'vectors.txt').read_bytes());m['vectors_sha256']=sha(out/'vectors.txt')
 assert m['vectors_sha256']==hm['vectors_sha256']
 (out/'runner.py').write_bytes(Path(__file__).read_bytes());(out/'run.tcl').write_text('run 300ms\nquit\n');save()
 cmds=[('compile',[BIN/'xvlog','--sv',*[src/p.name for p in paths if p.suffix in ('.v','.sv')]])]
 for name in ['cost_center_memory_call','cost_center_service']:
  cmds += [(name+'_elaborate',[BIN/'xelab','tb_'+name,'-s',name,'--debug','typical','--mt','2']),
   (name+'_simulate',[BIN/'xsim',name,'--tclbatch','run.tcl','--log',name+'.log'])]
 try:
  for stage,args in cmds:
   argv=list(map(str,args));start=time.monotonic()
   with (out/(stage+'.stdout.log')).open('w') as f:r=subprocess.run(argv,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=300)
   m['commands'].append({'stage':stage,'argv':argv,'exit_code':r.returncode,'elapsed_s':time.monotonic()-start});save();assert r.returncode==0,stage
   if stage.endswith('_simulate'):
    log=(out/(stage.replace('_simulate','')+'.log')).read_text()
    marker='COST_CENTER_MEMORY_CALL_PASS cases=16' if 'memory_call' in stage else 'COST_CENTER_SERVICE_PASS vectors=110397 reset_abort_offsets=120'
    assert marker in log and 'Fatal:' not in log and '$finish called' in log,stage
  m['status']='passed'
 except Exception as e:
  m.update(status='failed',error=repr(e));raise
 finally:
  m['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.suffix in ('.log','.tcl','.txt')};save()
 print(m['status'])
if __name__=='__main__':main()
