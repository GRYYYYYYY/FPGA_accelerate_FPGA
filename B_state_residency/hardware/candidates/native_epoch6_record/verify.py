"""Verify package hashes; optionally run one standalone XSim regression."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--test',choices=['checkpoint','wrap']);ap.add_argument('--output',type=Path);ap.add_argument('--vivado-bin',type=Path);a=ap.parse_args()
 spec=json.loads((ROOT/'manifest.json').read_text())
 for name,digest in spec['artifacts'].items():assert sha(ROOT/name)==digest,name
 if not a.test:print('CANDIDATE_PACKAGE_HASH_PASS');return
 assert a.output,'--output must name a new directory';out=a.output.resolve();out.mkdir()
 binary=lambda n:str(a.vivado_bin/n) if a.vivado_bin else shutil.which(n)
 assert all(binary(n) for n in ['xvlog','xelab','xsim']),'Use --vivado-bin or put Vivado bin on PATH'
 top='tb_small_endpoint_epoch6' if a.test=='checkpoint' else 'tb_record_epoch6_wrap'
 tb=ROOT/'Sources/Simulation'/('tb_small_endpoint_epoch6.sv' if a.test=='checkpoint' else 'tb_record_epoch6_wrap.sv')
 (out/'run.tcl').write_text('run all\nquit\n')
 sources=[ROOT/name for name in spec['rtl']]+[tb]
 m={'status':'running','test':a.test,'commands':[],'package_sha256':sha(ROOT/'manifest.json')}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  commands=[('compile',[binary('xvlog'),'--sv',*[str(p) for p in sources]]),('elaborate',[binary('xelab'),top,'-s','candidate','--debug','typical','--mt','2']),('simulate',[binary('xsim'),'candidate','--tclbatch','run.tcl','--log','simulate.log'])]
  for stage,argv in commands:
   with (out/(stage+'.stdout.log')).open('w') as f:r=subprocess.run(argv,cwd=out,stdout=f,stderr=subprocess.STDOUT)
   m['commands'].append({'stage':stage,'argv':argv,'exit_code':r.returncode});save();assert r.returncode==0,stage
  log=(out/'simulate.log').read_text();assert 'Fatal:' not in log and '$finish' in log
  if a.test=='checkpoint':assert 'SMALL_STALLS_PASS cases=8 blocked_cycles=800' in log and 'SMALL_32SLOTS_PASS pages=32 fields=5 checkpoints=8 transfers=288 checks=1778 tag_wraps=4' in log
  else:assert 'COMPOSITE_WRAP_PASS queries=70 transfers=140 tag_wraps=17 epoch_wraps=1 clear_cycles=128 ' in log
  m.update(status='passed',log_sha256=sha(out/'simulate.log'));save();print('CANDIDATE_PACKAGE_SIM_PASS',a.test)
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
