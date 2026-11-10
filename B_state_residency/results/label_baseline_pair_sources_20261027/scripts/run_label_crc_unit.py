from pathlib import Path
import sys,struct,zlib,json,shutil,subprocess
from run_checkpoint_authority import ROOT,BIN,sha
out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();disabled='--disabled'in sys.argv
for p in [ROOT/'hardware/variants/label_source_crc_v1/label_restore_controller.sv',ROOT/'hardware/variants/label_source_crc_v1/tb_crc_unit.sv',Path(__file__)]:shutil.copyfile(p,src/p.name)
b=b''.join(struct.pack('<6I',n,*[base+f for f in range(5)])for n,base in [(10,0x1000),(20,0x2000)]);(out/'crc.txt').write_text(f'{zlib.crc32(b):08x}\n');(out/'run.tcl').write_text('run all\nquit\n')
m={'status':'running','disabled':disabled,'sources':{p.name:sha(p)for p in src.iterdir()},'commands':[]}
try:
 for stage,args in [('compile',[BIN/'xvlog','--sv']+(['--define','CRC_DISABLED']if disabled else[])+[src/'label_restore_controller.sv',src/'tb_crc_unit.sv']),('elaborate',[BIN/'xelab','tb_crc_unit','-s','crc','--debug','typical']),('simulate',[BIN/'xsim','crc','--tclbatch','run.tcl','--testplusarg','crcfile='+str(out/'crc.txt')])]:
  with(out/(stage+'.log')).open('w')as f:r=subprocess.run(list(map(str,args)),cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=120)
  m['commands'].append({'stage':stage,'exit_code':r.returncode});assert r.returncode==0,stage
 log=(out/'simulate.log').read_text();assert 'LABEL_CRC_UNIT_PASS'in log and 'Fatal:'not in log;m['status']='observed'
finally:(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
print('LABEL_CRC_UNIT_OBSERVED')
