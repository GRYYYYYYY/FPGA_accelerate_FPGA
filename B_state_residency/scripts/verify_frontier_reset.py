"""Characterize original HLS cold reset; stale heap is an expected negative result."""
from pathlib import Path
import hashlib,json,subprocess,sys
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
 paths.append(ROOT/'hardware/variants/frontier_reset_check/tb_frontier_reset.sv')
 for p in paths:
  (src/p.name).write_bytes(p.read_bytes());m['sources'][p.name]={'path':str(p),'sha256':sha(p)}
  if p.suffix=='.dat':(out/p.name).write_bytes(p.read_bytes())
 (out/'runner.py').write_bytes(Path(__file__).read_bytes());(out/'run.tcl').write_text('run 100us\nquit\n');save()
 cmds=[('compile',[BIN/'xvlog','--sv',*[src/p.name for p in paths if p.suffix in ('.v','.sv')]]),('elaborate',[BIN/'xelab','tb_frontier_reset','-s','reset_test','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','reset_test','--tclbatch','run.tcl','--log','simulate.log'])]
 for stage,args in cmds:
  argv=list(map(str,args))
  with (out/(stage+'.stdout.log')).open('w') as f:r=subprocess.run(argv,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=120)
  m['commands'].append({'stage':stage,'argv':argv,'exit_code':r.returncode});save();assert r.returncode==0
 log=(out/'simulate.log').read_text()
 assert 'RAW_RESET_RETAINS_OLD_HEAP size_after_reset=2 stale_id=deadbeef' in log
 assert 'FRONTIER_RESET_CHARACTERIZED calls=9 clear_hides_old_heap=1' in log and 'Fatal:' not in log and '$finish called' in log
 m.update(status='passed',raw_reset_safe=False,clear_hides_old_heap=True,artifacts={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.suffix in ('.log','.tcl')});save();print(m['status'])
if __name__=='__main__':main()
