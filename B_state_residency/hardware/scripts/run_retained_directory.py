"""Standalone XSim fallback after the project launcher crashed before runtime."""
from pathlib import Path
import hashlib,json,subprocess,os
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/rtl_retained_directory_20261023'
RUN=OUT/'standalone';RUN.mkdir()
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parent=json.loads((OUT/'manifest.json').read_text())
for path,digest in parent['sources'].items():
 assert sha(Path(path))==digest
 assert sha(OUT/Path(path).name)==digest
(RUN/'run.tcl').write_text('run 10ms\nquit\n')
m={'status':'running','sources':parent['sources'],'commands':[], 'parent_launcher':'SIGABRT in tcmalloc / SimBridge::BoostProcessTransport::launch before runtime', 'source_sha256':sha(Path(__file__))}
def save():(RUN/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
save()
commands=[('compile',['xvlog','--sv',str(OUT/'backing_frame_directory_retained.sv'),str(OUT/'tb_retained_directory.sv')]),('elaborate',['xelab','tb_retained_directory','-s','retained_tb','--debug','typical','--mt','2']),('simulate',['xsim','retained_tb','--tclbatch','run.tcl','--log','simulate.log'])]
for name,args in commands:
 args[0]=str(BIN/args[0]);log=RUN/(name+'_stdout.log')
 with log.open('w') as f:
  proc=subprocess.Popen(args,cwd=RUN,stdout=f,stderr=subprocess.STDOUT)
  receipt={'stage':name,'argv':args,'pid':proc.pid,'exit_code':None};m['commands'].append(receipt);save()
  receipt['exit_code']=proc.wait();save()
 if receipt['exit_code']:
  m['status']='failed';save();raise SystemExit(name+' failed')
s=(RUN/'simulate.log').read_text()
assert s.count('RETAINED_DIRECTORY_PASS checks=1007 checkpoints=40 full_recycles=6')==1,s[-2000:]
assert 'Fatal:' not in s and 'Error:' not in s
for path,digest in parent['sources'].items():assert sha(Path(path))==digest
m['status']='passed';m['checks']=1007;m['rtl_checkpoint_integrated']=False
m['artifacts']={p.name:sha(p) for p in RUN.iterdir() if p.is_file() and p.suffix in ('.log','.tcl')}
save();(RUN/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
print(json.dumps(m,indent=2))
