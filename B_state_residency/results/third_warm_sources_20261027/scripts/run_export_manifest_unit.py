from pathlib import Path
import json,shutil,subprocess,sys
from run_checkpoint_authority import ROOT,BIN,sha
out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();v=ROOT/'hardware/variants/owner_g3_publish_v1'
for p in [v/'export_manifest.sv',v/'tb_export_manifest.sv',Path(__file__)]:shutil.copyfile(p,src/p.name)
(out/'run.tcl').write_text('run all\nquit\n');m=dict(status='running',sources={p.name:sha(p)for p in src.iterdir()},commands=[],scope='Synthetic native-export handshake/parser/CRC unit; actual native controllers covered separately by full-system experiment.')
try:
 for name,args in [('compile',[BIN/'xvlog','--sv',src/'export_manifest.sv',src/'tb_export_manifest.sv']),('elaborate',[BIN/'xelab','tb_export_manifest','-s','manifest','--debug','typical']),('simulate',[BIN/'xsim','manifest','--tclbatch','run.tcl','--testplusarg','trace='+str(out/'events.txt')])]:
  with(out/(name+'.log')).open('w')as f:r=subprocess.run(list(map(str,args)),cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=120)
  m['commands'].append(dict(stage=name,exit_code=r.returncode));assert r.returncode==0,name
 log=(out/'simulate.log').read_text();assert 'EXPORT_MANIFEST_PASS checks='in log and 'Fatal:'not in log;m['status']='observed'
finally:(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
print('EXPORT_MANIFEST_OBSERVED')
