"""Frozen record/AXI service regression including ID reuse with preserved bytes."""
from pathlib import Path
import hashlib,json,subprocess,sys
from make_retained_endpoint import generate
from make_retained_multipage_tb import generate as generate_tb
ROOT=Path(__file__).resolve().parents[2];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir()
 assert (ROOT/'hardware/rtl/memory_scratch_endpoint_retained.sv').read_text()==generate((ROOT/'hardware/rtl/memory_scratch_endpoint_indexed.sv').read_text())
 assert (ROOT/'hardware/tb/tb_retained_endpoint_multipage.sv').read_text()==generate_tb()
 names=['bounded_sync_fifo','scratch_frame_store_bram','scratch_page_controller','queued_scratch_endpoint','memory_scratch_endpoint_retained','scratch_page_axi','backing_frame_directory_retained','backing_page_service_retained','scratch_page_codec_wide','record_backing_service_retained']
 paths=[ROOT/'hardware/rtl'/f'{n}.sv' for n in names]+[ROOT/'hardware/tb/tb_retained_endpoint_multipage.sv',Path(__file__).resolve(),ROOT/'hardware/scripts/make_retained_endpoint.py',ROOT/'hardware/scripts/make_retained_multipage_tb.py',ROOT/'hardware/tb/tb_retained_checkpoint_profile.sv']
 parent=ROOT/'results/rtl_retained_services_20261023/manifest.json';assert json.loads(parent.read_text())['status']=='passed'
 m={'status':'running','sources':{},'inputs':{},'commands':[],'directory_regression_sha256':sha(parent),'checkpoint_endpoint_integrated':True,'scope':'Small directed pilot only; legacy and negative regressions pending'}
 for p in paths:(src/p.name).write_bytes(p.read_bytes());m['sources'][str(p)]=sha(p)
 pages=ROOT/'results/rtl_backing_axi_20261023/fixtures/pages.hex';records=ROOT/'results/rtl_page_codec_20261023/records.hex'
 for p in [pages,records]:m['inputs'][str(p)]=sha(p)
 (out/'simulate.tcl').write_text('run 2s\nquit\n')
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  cmds=[('compile',[BIN/'xvlog','--sv',*[src/f'{n}.sv' for n in names],src/'tb_retained_endpoint_multipage.sv',src/'tb_retained_checkpoint_profile.sv']),('elaborate',[BIN/'xelab','tb_retained_checkpoint_profile','-s','service_tb','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','service_tb','--tclbatch','simulate.tcl','--log','simulate.log','--testplusarg','PAGES='+str(pages),'--testplusarg','RECORDS='+str(records)])]
  for stage,cmd in cmds:
   args=list(map(str,cmd))
   with (out/(stage+'.stdout.log')).open('w') as log:
    proc=subprocess.Popen(args,cwd=out,stdout=log,stderr=subprocess.STDOUT);row={'stage':stage,'argv':args,'pid':proc.pid,'exit_code':None};m['commands'].append(row);save();row['exit_code']=proc.wait();save()
   assert row['exit_code']==0,stage
  s=(out/'simulate.log').read_text();assert 'Fatal:' not in s and '$finish' in s
  prefixes=['CHECKPOINT_PROFILE_PASS checkpoints=8 checks=221','RETAINED_MULTIPAGE_PASS pages=4 fields=5 checkpoints=8 transfers=36 checks=221 tag_wraps=4']
  m['results']=[]
  for prefix in prefixes:
   lines=[line for line in s.splitlines() if line.startswith(prefix)];assert len(lines)==1,prefix;m['results']+=lines
  for path,digest in {**m['sources'],**m['inputs']}.items():assert sha(Path(path))==digest
  assert '$finish called at time : 354420 ns' in s
  m['status']='passed';m['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.suffix in ('.log','.tcl','.csv')};save()
  (out/'completion_audit.json').write_text(json.dumps({'status':'passed','manifest_sha256':sha(out/'manifest.json')},indent=2)+'\n');print('\n'.join(m['results']))
 except Exception as exc:m.update(status='failed',error=repr(exc));save();raise
if __name__=='__main__':main()
