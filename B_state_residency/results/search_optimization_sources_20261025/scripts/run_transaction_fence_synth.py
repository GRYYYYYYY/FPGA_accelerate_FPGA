from pathlib import Path
import sys,subprocess,json,hashlib,shutil,time
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin/vivado')
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='prepared'
shutil.copyfile(__file__,p/'sources'/Path(__file__).name)
cmd=[str(BIN),'-mode','batch','-nojournal','-source',str(p/'synth.tcl'),'-log',str(p/'vivado.log')];t=time.monotonic()
with(p/'launch.stdout.log').open('w')as f:r=subprocess.run(cmd,cwd=p,stdout=f,stderr=subprocess.STDOUT,timeout=240)
m.update(status='passed'if r.returncode==0 else'failed',completion=dict(argv=cmd,exit_code=r.returncode,elapsed_s=time.monotonic()-t))
(p/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');assert r.returncode==0
print('TRANSACTION_FENCE_SYNTH_RETURNED',r.returncode)
