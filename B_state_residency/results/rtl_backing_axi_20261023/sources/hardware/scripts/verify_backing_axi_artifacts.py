"""Freeze final source, run five negative controls, synthesize default 23405 frames."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();path=out/'build_manifest.json'
 if path.exists():raise ValueError('Do not restart existing flow')
 names=['hardware/rtl/scratch_page_axi.sv','hardware/rtl/backing_frame_directory.sv','hardware/rtl/backing_page_service.sv','hardware/rtl/scratch_frame_store.xdc','hardware/tb/tb_backing_page_service.sv','hardware/scripts/make_axi_pages.py','hardware/scripts/verify_backing_axi_artifacts.py']
 files={}
 for name in names:
  p=ROOT/name;b=p.read_bytes();files[str(p)]=sha(p);dst=out/'sources'/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(b)
 record=dict(status='running',files=files,negative_controls={},synthesis={})
 def save():path.write_text(json.dumps(record,indent=2)+'\n')
 def run(d,row,stage,cmd):
  row.setdefault('commands',[]).append(dict(stage=stage,argv=list(map(str,cmd))));save()
  with (d/(stage+'.console.log')).open('w') as log:r=subprocess.run(cmd,cwd=d,stdout=log,stderr=subprocess.STDOUT)
  row['commands'][-1]['exit_code']=r.returncode;save();return r.returncode
 save()
 try:
  variants={
   'complete_before_B':('scratch_page_axi.sv',"if(position==length-1'b1)state<=WRITE_RESPONSE;","if(position==length-1'b1)begin if(total==20)begin state<=IDLE;done_valid<=1;end else state<=WRITE_RESPONSE;end",'before final B response'),
   'ignore_B_error':('scratch_page_axi.sv','m_bid!=0 || m_bresp!=0',"1'b0",'service mismatch'),
   'release_before_consumer':('backing_frame_directory.sv','lease_phase[slot]<=memory_success?COMPLETE:FAILED;','lease_phase[slot]<=memory_success?FREE:FAILED;','lease released before consumer commit'),
   'recycle_without_fence':('backing_frame_directory.sv','if(leased!=0 || !fence_retired)','if(leased!=0)','service mismatch'),
   'old_read_error_stop':('scratch_page_axi.sv',None,None,'undrained read burst'),
  }
  tb=out/'sources/hardware/tb/tb_backing_page_service.sv';rtl=out/'sources/hardware/rtl';pages=out/'fixtures/pages.hex'
  for name,(file,old,new,expected) in variants.items():
   d=out/'negative_controls'/name;d.mkdir(parents=True);row=dict(status='running',file=file,removed=old,replacement=new,expected_failure=expected);record['negative_controls'][name]=row
   original=(rtl/file).read_text()
   if old is None:modified=(out/'protocol_gap'/file).read_text()
   else:
    if original.count(old)!=1:raise ValueError('Ambiguous mutation '+name)
    modified=original.replace(old,new)
   mutant=d/file;mutant.write_text(modified);(d/'simulate.tcl').write_text('run 101ms\nquit\n')
   src=[mutant if file==f else rtl/f for f in ('scratch_page_axi.sv','backing_frame_directory.sv','backing_page_service.sv')]
   if run(d,row,'compile',[BIN/'xvlog','--sv','--work','xil_defaultlib',*src,tb]):raise ValueError('Negative compile failure')
   if run(d,row,'elaborate',[BIN/'xelab','xil_defaultlib.tb_backing_page_service','--snapshot','negative_tb','--debug','typical','--mt','2']):raise ValueError('Negative elaboration failure')
   run(d,row,'simulate',[BIN/'xsim','negative_tb','--tclbatch','simulate.tcl','--testplusarg','PAGES='+str(pages),'--log','simulate.log'])
   log=(d/'simulate.log').read_text();fatal=[line for line in log.splitlines() if line.startswith('Fatal:')]
   if len(fatal)!=1 or expected not in fatal[0] or 'TEST_PASS' in log:raise ValueError('Wrong negative outcome '+name)
   row.update(status='expected_failure_observed',causal_failure=fatal[0],artifacts={str(p):sha(p) for p in d.iterdir() if p.is_file() and p.suffix in ('.sv','.tcl','.log')});save();print(name+': '+fatal[0],flush=True)
  d=out/'synthesis';d.mkdir();row=record['synthesis'];row['status']='running'
  tcl=['set_param general.maxThreads 2']+[f'read_verilog -sv {{{rtl/f}}}' for f in ('scratch_page_axi.sv','backing_frame_directory.sv','backing_page_service.sv')]
  tcl += [f'read_xdc {{{rtl/"scratch_frame_store.xdc"}}}',
   'synth_design -top backing_page_service -part xcu280-fsvh2892-2L-e -mode out_of_context',
   'report_utilization -file utilization.rpt','write_checkpoint backing_page_service.dcp',
   'set b_rams [get_cells -hier -filter {REF_NAME =~ RAMB*}]','set b_file [open ram_cells.txt w]',
   'foreach b_cell $b_rams {puts $b_file "$b_cell [get_property REF_NAME $b_cell]"}','close $b_file',
   'if {[llength $b_rams] == 0} {error "Directory BRAM was not inferred"}',
   'puts "B_BACKING_SYNTH_PASS ram_cells=[llength $b_rams]"','exit']
  (d/'synthesize.tcl').write_text('\n'.join(tcl)+'\n');print('Negative controls complete; synthesizing default 23405-frame service',flush=True)
  if run(d,row,'synthesize',[BIN/'vivado','-mode','batch','-source','synthesize.tcl','-log','synthesize.log','-journal','synthesize.jou']):raise ValueError('Synthesis failed')
  row.update(status='exited_zero',artifacts={str(p):sha(p) for p in d.iterdir() if p.is_file() and p.suffix in ('.tcl','.log','.rpt','.txt','.dcp')})
  for name,digest in files.items():
   if sha(name)!=digest:raise ValueError('Source changed during build')
  record['status']='completed';save();print('Build completed; independent audit still required',flush=True)
 except Exception as e:record.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
