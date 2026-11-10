from pathlib import Path
import json,shutil,subprocess,sys
from run_checkpoint_authority import ROOT,BIN,sha
out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir()
variant=ROOT/'hardware/variants/owner_cumulative_rearm_v1'
for p in [variant/'cumulative_owner_snapshot.sv',variant/'axi_file_memory.sv',variant/'tb_cumulative_owner.sv',Path(__file__)]:shutil.copyfile(p,src/p.name)
a=bytes((i*17+3)%256 for i in range(512));(out/'source.bin').write_bytes(a)
for n in ['bank0','bank1']:(out/(n+'.bin')).write_bytes(bytes(512))
(out/'run.tcl').write_text('run all\nquit\n')
m=dict(status='running',sources={p.name:sha(p) for p in src.iterdir()},commands=[],scope='Component-only cumulative dirty observer, two actual destination AXI windows, synthetic source AW/B observations and external lease/health/publication inputs. Not full G3 system proof.')
try:
 stages=[('compile',[BIN/'xvlog','--sv',src/'cumulative_owner_snapshot.sv',src/'axi_file_memory.sv',src/'tb_cumulative_owner.sv']),('elaborate',[BIN/'xelab','tb_cumulative_owner','-s','cumulative','--debug','typical']),('simulate',[BIN/'xsim','cumulative','--tclbatch','run.tcl'])]
 stages[-1][1].extend(sum((['--testplusarg',k+'='+str(out/v)] for k,v in [('copy0','source.bin'),('copy1','bank0.bin'),('copy2','bank1.bin'),('copylog','copy_axi.txt'),('trace','events.txt')]),[]))
 for name,args in stages:
  with(out/(name+'.log')).open('w')as f:r=subprocess.run(list(map(str,args)),cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=120)
  m['commands'].append(dict(stage=name,exit_code=r.returncode));assert r.returncode==0,name
 log=(out/'simulate.log').read_text();assert 'CUMULATIVE_OWNER_PASS checks='in log and 'Fatal:'not in log
 m['status']='observed'
finally:(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
print('CUMULATIVE_OWNER_OBSERVED')
