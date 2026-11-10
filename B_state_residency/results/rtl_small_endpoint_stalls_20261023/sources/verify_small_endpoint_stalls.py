from pathlib import Path
import hashlib,json,subprocess,sys,os
ROOT=Path(__file__).resolve().parents[2]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir()
 paths=[ROOT/'hardware/rtl'/f'{n}.sv' for n in ['bounded_sync_fifo','scratch_frame_store_bram','scratch_page_controller_small','queued_scratch_endpoint_small','memory_scratch_endpoint_small','scratch_page_codec_small','scratch_page_axi_small','backing_frame_directory_small','backing_page_service_small','record_backing_service_small']]+[ROOT/'hardware/tb/tb_small_endpoint_32slots_stalls.sv',Path(__file__).resolve(),ROOT/'hardware/scripts/make_small_endpoint.py']
 m={'status':'running','pid':os.getpid(),'sources':{},'commands':[],'scope':'Small-page closed endpoint multipage pilot; slots0/8/16/31 high page IDs, all fields, checkpoint tag wraps; not full trace or default capacity synthesis'}
 for p in paths:(src/p.name).write_bytes(p.read_bytes());m['sources'][str(p)]=sha(p)
 (out/'simulate.tcl').write_text('run 2ms\nquit\n')
 def save():
  p=out/'manifest.tmp';p.write_text(json.dumps(m,indent=2)+'\n');p.replace(out/'manifest.json')
 save()
 try:
  cmds=[('compile',[BIN/'xvlog','--sv',*[src/p.name for p in paths[:11]]]),('elaborate',[BIN/'xelab','tb_small_endpoint_32slots_stalls','-s','small_codec','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','small_codec','--tclbatch','simulate.tcl','--log','simulate.log'])]
  for stage,cmd in cmds:
   args=list(map(str,cmd))
   with (out/(stage+'.stdout.log')).open('w') as log:
    proc=subprocess.Popen(args,cwd=out,stdout=log,stderr=subprocess.STDOUT);row={'stage':stage,'argv':args,'pid':proc.pid,'exit_code':None};m['commands'].append(row);save();row['exit_code']=proc.wait();save()
   assert row['exit_code']==0,stage
  log=(out/'simulate.log').read_text();assert 'Fatal:' not in log and '$finish' in log
  assert 'SMALL_STALLS_PASS cases=8 blocked_cycles=800' in log
  lines=[s for s in log.splitlines() if s.startswith('SMALL_32SLOTS_PASS')]
  assert lines==['SMALL_32SLOTS_PASS pages=32 fields=5 checkpoints=8 transfers=288 checks=1778 tag_wraps=4'],lines
  for name,h in m['sources'].items():assert sha(Path(name))==h
  m.update(status='passed',results=lines,artifacts={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.suffix in ('.log','.tcl')});save()
  (out/'completion_audit.json').write_text(json.dumps({'status':'passed','manifest_sha256':sha(out/'manifest.json')},indent=2)+'\n');print('\n'.join(lines))
 except Exception as exc:m.update(status='failed',error=repr(exc));save();raise
if __name__=='__main__':main()
