from pathlib import Path
import sys,struct,json,shutil,subprocess
from run_checkpoint_authority import ROOT,BIN,sha
out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();bench=ROOT/'hardware/variants/label_frame_export_v1'
files=[bench/'expansion_20261024/pager/backend/backing_frame_directory_small.sv',bench/'label_snapshot_reader.sv',bench/'label_snapshot_checkpoint_adapter.sv',bench/'tb_label_snapshot_unit.sv',ROOT/'hardware/variants/iter2_runtime_owner_v1/axi_file_memory.sv',Path(__file__)]
for p in files:shutil.copyfile(p,src/p.name)
b=bytearray(1536)
for frame,page,slots in [(0,0,[0,2,7]),(1,1,[0]),(2,2,[1])]:
 for slot in slots:
  node=page*8+slot;b[frame*192]|=1<<slot;struct.pack_into('<5I',b,frame*192+1+slot*20,*[0x10000000+f*256+node for f in range(5)])
b[3*192+191]=1
(out/'labels.bin').write_bytes(b);(out/'run.tcl').write_text('run all\nquit\n')
m={'status':'running','sources':{p.name:sha(p)for p in src.iterdir()},'commands':[]}
try:
 for stage,args in [('compile',[BIN/'xvlog','--sv',*[src/p.name for p in files if p.suffix=='.sv']]),('elaborate',[BIN/'xelab','tb_label_snapshot_unit','-s','labelsnap','--debug','typical']),('simulate',[BIN/'xsim','labelsnap','--tclbatch','run.tcl','--testplusarg','labelsnap0='+str(out/'labels.bin'),'--testplusarg','labelsnaplog='+str(out/'labelsnap_axi.txt')])]:
  with(out/(stage+'.log')).open('w')as f:r=subprocess.run(list(map(str,args)),cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=120)
  m['commands'].append({'stage':stage,'exit_code':r.returncode});assert r.returncode==0,stage
 log=(out/'simulate.log').read_text();assert 'LABEL_SNAPSHOT_UNIT_PASS'in log and 'Fatal:'not in log;m['status']='observed'
finally:(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
print('LABEL_SNAPSHOT_UNIT_OBSERVED')
