from pathlib import Path
import sys,json,shutil,subprocess
from run_checkpoint_authority import ROOT,BIN,sha
out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir()
for p in [ROOT/'hardware/variants/label_baseline_fence_v1/baseline_retirement_guard.sv',ROOT/'hardware/variants/label_baseline_fence_v1/tb_guard.sv',out.parent/'label_baseline_pair_full_v2/sources/axi_drain_watch.sv',Path(__file__)]:shutil.copyfile(p,src/p.name)
(out/'run.tcl').write_text('run all\nquit\n');m=dict(status='running',sources={p.name:sha(p)for p in src.iterdir()},commands=[])
try:
 for stage,args in [('compile',[BIN/'xvlog','--sv',src/'axi_drain_watch.sv',src/'baseline_retirement_guard.sv',src/'tb_guard.sv']),('elaborate',[BIN/'xelab','tb_guard','-s','guard','--debug','typical']),('simulate',[BIN/'xsim','guard','--tclbatch','run.tcl'])]:
  with(out/(stage+'.log')).open('w')as f:r=subprocess.run(list(map(str,args)),cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=90)
  m['commands'].append(dict(stage=stage,exit_code=r.returncode));assert r.returncode==0,stage
 log=(out/'simulate.log').read_text();assert 'BASELINE_GUARD_UNIT_PASS'in log and 'Fatal:'not in log;m['status']='observed'
finally:(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
print('BASELINE_GUARD_UNIT_OBSERVED')
