from pathlib import Path
import hashlib,json,subprocess,sys,os
ROOT=Path(__file__).resolve().parents[2]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir()
 paths=[ROOT/'hardware/rtl'/f'{n}.sv' for n in ['scratch_page_codec_small','scratch_page_axi_small','backing_frame_directory_small','backing_page_service_small','record_backing_service_small']]+[ROOT/'hardware/tb/tb_record_backing_service_small.sv',Path(__file__).resolve(),ROOT/'hardware/scripts/make_small_services.py',ROOT/'hardware/scripts/make_small_service_tb.py']
 m={'status':'running','pid':os.getpid(),'sources':{},'commands':[],'scope':'Small-page record/directory/AXI service with 32 leases and retained ID recycle; no closed endpoint drain or full default-capacity proof'}
 for p in paths:(src/p.name).write_bytes(p.read_bytes());m['sources'][str(p)]=sha(p)
 # Independent byte-oriented fixture construction, no DUT helper.
 pages=[];records=[]
 for page_id in range(64):
  raw=bytearray(192)
  for node in range(8):
   present=(page_id==0 or (page_id+node)%3!=0)
   word=bytes(((page_id*37+node*19+b*11)&255) for b in range(17)) if present else bytes(17)
   if page_id==0 and node==0:word=bytes(17)
   if page_id==0 and node==7:word=bytes([255])*17
   raw[0]|=int(present)<<node
   raw[1+node*20:1+node*20+17]=word
   records.append(format((int(present)<<160)|int.from_bytes(word,'little'),'041x'))
  pages.extend(raw[n:n+64][::-1].hex() for n in range(0,192,64))
 (out/'pages.hex').write_text('\n'.join(pages)+'\n');(out/'records.hex').write_text('\n'.join(records)+'\n')
 m['inputs']={p.name:sha(p) for p in [out/'pages.hex',out/'records.hex']}
 (out/'simulate.tcl').write_text('run 2ms\nquit\n')
 def save():
  p=out/'manifest.tmp';p.write_text(json.dumps(m,indent=2)+'\n');p.replace(out/'manifest.json')
 save()
 try:
  cmds=[('compile',[BIN/'xvlog','--sv',*[src/p.name for p in paths[:6]]]),('elaborate',[BIN/'xelab','tb_record_backing_service_small','-s','small_codec','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','small_codec','--tclbatch','simulate.tcl','--log','simulate.log','--testplusarg','PAGES='+str(out/'pages.hex'),'--testplusarg','RECORDS='+str(out/'records.hex')])]
  for stage,cmd in cmds:
   args=list(map(str,cmd))
   with (out/(stage+'.stdout.log')).open('w') as log:
    proc=subprocess.Popen(args,cwd=out,stdout=log,stderr=subprocess.STDOUT);row={'stage':stage,'argv':args,'pid':proc.pid,'exit_code':None};m['commands'].append(row);save();row['exit_code']=proc.wait();save()
   assert row['exit_code']==0,stage
  log=(out/'simulate.log').read_text();assert 'Fatal:' not in log and '$finish' in log
  lines=[s for s in log.splitlines() if s.startswith(('RETAINED_SERVICE_CONTENT_PASS','TEST_PASS record_adapter','TEST_PASS record_backing_service'))]
  assert len(lines)==3,lines
  assert lines[0]=='RETAINED_SERVICE_CONTENT_PASS pages=64 records=512',lines
  assert lines[1]=='TEST_PASS record_adapter records=1048 lookup_checks=259 bad_inputs=3 malformed_reads=3',lines
  assert lines[2].startswith('TEST_PASS record_backing_service checks=1511 '),lines
  assert 'error_cases=8 ' in lines[2],lines
  for name,h in m['sources'].items():assert sha(Path(name))==h
  m.update(status='passed',results=lines,artifacts={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.suffix in ('.log','.tcl')});save()
  (out/'completion_audit.json').write_text(json.dumps({'status':'passed','manifest_sha256':sha(out/'manifest.json')},indent=2)+'\n');print('\n'.join(lines))
 except Exception as exc:m.update(status='failed',error=repr(exc));save();raise
if __name__=='__main__':main()
