from pathlib import Path
import hashlib,json,subprocess,sys,os
ROOT=Path(__file__).resolve().parents[2]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir()
 paths=[ROOT/'hardware/rtl/scratch_page_codec_small_static.sv',ROOT/'hardware/tb/tb_scratch_page_codec_small_static.sv',Path(__file__).resolve()]
 m={'status':'running','pid':os.getpid(),'sources':{},'commands':[],'scope':'8-node codec directed behavioral simulation, not AXI integration or timing'}
 for p in paths:(src/p.name).write_bytes(p.read_bytes());m['sources'][str(p)]=sha(p)
 (out/'simulate.tcl').write_text('run 2ms\nquit\n')
 def save():
  p=out/'manifest.tmp';p.write_text(json.dumps(m,indent=2)+'\n');p.replace(out/'manifest.json')
 save()
 try:
  cmds=[('compile',[BIN/'xvlog','--sv',src/paths[0].name,src/paths[1].name]),('elaborate',[BIN/'xelab','tb_scratch_page_codec_small_static','-s','small_codec','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','small_codec','--tclbatch','simulate.tcl','--log','simulate.log'])]
  for stage,cmd in cmds:
   args=list(map(str,cmd))
   with (out/(stage+'.stdout.log')).open('w') as log:
    proc=subprocess.Popen(args,cwd=out,stdout=log,stderr=subprocess.STDOUT);row={'stage':stage,'argv':args,'pid':proc.pid,'exit_code':None};m['commands'].append(row);save();row['exit_code']=proc.wait();save()
   assert row['exit_code']==0,stage
  log=(out/'simulate.log').read_text();assert 'Fatal:' not in log and '$finish' in log
  lines=[s for s in log.splitlines() if s.startswith('SMALL_CODEC_EDGES_PASS ')];assert len(lines)==1
  assert lines[0]=='SMALL_CODEC_EDGES_PASS cases=99 checks=286',lines
  for name,h in m['sources'].items():assert sha(Path(name))==h
  m.update(status='passed',results=lines,artifacts={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.suffix in ('.log','.tcl')});save()
  (out/'completion_audit.json').write_text(json.dumps({'status':'passed','manifest_sha256':sha(out/'manifest.json')},indent=2)+'\n');print(lines[0])
 except Exception as exc:m.update(status='failed',error=repr(exc));save();raise
if __name__=='__main__':main()
