from pathlib import Path
import json,shutil,subprocess,sys,hashlib
from run_checkpoint_authority import ROOT,BIN,sha
out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir()
paths=[ROOT/'hardware/variants/owner_snapshot_writer_v1/incremental_owner_snapshot.sv',ROOT/'hardware/variants/owner_snapshot_writer_v1/owner_snapshot_checkpoint_adapter.sv',ROOT/'hardware/variants/owner_snapshot_writer_v1/tb_snapshot.sv',ROOT/'hardware/variants/iter2_runtime_owner_v1/axi_file_memory.sv',Path(__file__)]
for p in paths:shutil.copyfile(p,src/p.name)
a=bytes((i*17+3)%256 for i in range(512));(out/'source.bin').write_bytes(a);(out/'target.bin').write_bytes(bytes(512));(out/'run.tcl').write_text('run all\nquit\n')
m={'status':'running','sources':{p.name:sha(p)for p in src.iterdir()},'commands':[],'scope':'Snapshot engine protocol/data unit with actual AXI memory and independently replayed bytes; not integrated runtime checkpoint proof.'}
try:
 for name,args in [('compile',[BIN/'xvlog','--sv',src/'incremental_owner_snapshot.sv',src/'owner_snapshot_checkpoint_adapter.sv',src/'axi_file_memory.sv',src/'tb_snapshot.sv']),('elaborate',[BIN/'xelab','tb_snapshot','-s','snapshot','--debug','typical']),('simulate',[BIN/'xsim','snapshot','--tclbatch','run.tcl','--testplusarg','copy0='+str(out/'source.bin'),'--testplusarg','copy1='+str(out/'target.bin'),'--testplusarg','copylog='+str(out/'copy_axi.txt')])]:
  with(out/(name+'.log')).open('w')as f:r=subprocess.run(list(map(str,args)),cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=120)
  m['commands'].append({'stage':name,'exit_code':r.returncode});assert r.returncode==0,name
 log=(out/'simulate.log').read_text();assert 'SNAPSHOT_UNIT_PASS checks=66'in log and 'Fatal:'not in log
 m['status']='observed'
finally:(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
print('SNAPSHOT_UNIT_OBSERVED')
