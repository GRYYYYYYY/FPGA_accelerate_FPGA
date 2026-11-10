"""Freeze wide-record codec composition, seven negative controls and whole-top OOC."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 variants={
  'bypass_commit':('else state<=D_COMMIT;','else begin node<=0;state<=D_READ;end','record exposed before successful commit'),
  'ignore_failed_commit':('if(!commit_ok)',"if(1'b0)",'record exposed before successful commit'),
  'ignore_bad_format':('if(bad_page)',"if(1'b0)",'malformed page accepted'),
  'ignore_cancel':('else if(cancel && state!=IDLE)',"else if(1'b0)",'abort did not terminate page'),
  'wrong_first_word':('<=read_label[31:0];','<=read_label[63:32];','encoded byte mismatch'),
  'drop_presence':('bitmap[node]<=record_in_present;','bitmap[node]<=0;','encoded byte mismatch'),
  'truncate_without_padding_check':('unpack_word[31:8]!=0',"1'b0",'malformed page accepted')}
 original=(ROOT/'hardware/rtl/scratch_page_codec_wide.sv').read_text()
 for name,(old,new,expected) in variants.items():
  if original.count(old)!=1:raise ValueError('Nonunique mutation '+name)
 evidence=Path(sys.argv[1]).resolve();out=evidence/'verified_build';out.mkdir();path=out/'build_manifest.json'
 rtl_names=['bounded_sync_fifo.sv','scratch_frame_store_bram.sv','scratch_page_controller.sv','queued_scratch_endpoint.sv','scratch_page_axi.sv','backing_frame_directory_lookup.sv','backing_page_service_lookup.sv','scratch_page_codec_wide.sv','record_backing_service_wide.sv','memory_scratch_endpoint_wide.sv']
 extras=['hardware/rtl/scratch_frame_store.xdc','hardware/rtl/scratch_page_codec.sv','hardware/rtl/record_backing_service.sv','hardware/rtl/memory_scratch_endpoint.sv','hardware/tb/tb_scratch_page_codec.sv','hardware/tb/tb_scratch_page_codec_wide.sv','hardware/tb/tb_memory_endpoint.sv','hardware/tb/tb_memory_endpoint_profile.sv','hardware/tb/tb_memory_endpoint_wide.sv','hardware/tb/tb_memory_endpoint_wide_profile.sv','hardware/scripts/make_wide_codec_composition.py','hardware/scripts/verify_wide_codec_artifacts.py']
 files={}
 for name in ['hardware/rtl/'+n for n in rtl_names]+extras:
  p=ROOT/name;files[str(p)]=sha(p);dst=out/'sources'/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(p.read_bytes())
 record=dict(status='running',files=files,negative_controls={},synthesis={})
 def save():path.write_text(json.dumps(record,indent=2)+'\n')
 def run(d,row,stage,cmd):
  row.setdefault('commands',[]).append(dict(stage=stage,argv=list(map(str,cmd))));save()
  with (d/(stage+'.console.log')).open('w') as log:r=subprocess.run(cmd,cwd=d,stdout=log,stderr=subprocess.STDOUT)
  row['commands'][-1]['exit_code']=r.returncode;save();return r.returncode
 save()
 try:
  rtl=out/'sources/hardware/rtl';tb=out/'sources/hardware/tb/tb_scratch_page_codec_wide.sv'
  pages=ROOT/'results/rtl_backing_axi_20261023/fixtures/pages.hex';records=ROOT/'results/rtl_page_codec_20261023/records.hex'
  for name,(old,new,expected) in variants.items():
   d=out/'negative_controls'/name;d.mkdir(parents=True);row=dict(status='running',removed=old,replacement=new,expected_failure=expected);record['negative_controls'][name]=row
   mutant=d/'scratch_page_codec_wide.sv';mutant.write_text(original.replace(old,new));(d/'simulate.tcl').write_text('run 2s\nquit\n')
   if run(d,row,'compile',[BIN/'xvlog','--sv','--work','xil_defaultlib',mutant,tb]):raise ValueError('Negative compile failure')
   if run(d,row,'elaborate',[BIN/'xelab','xil_defaultlib.tb_scratch_page_codec_wide','--snapshot','negative_tb','--debug','typical','--mt','2']):raise ValueError('Negative elaboration failure')
   run(d,row,'simulate',[BIN/'xsim','negative_tb','--tclbatch','simulate.tcl','--testplusarg','PAGES='+str(pages),'--testplusarg','RECORDS='+str(records),'--log','simulate.log'])
   log=(d/'simulate.log').read_text();fatal=[x for x in log.splitlines() if x.startswith('Fatal:')]
   if len(fatal)!=1 or expected not in fatal[0] or 'TEST_PASS' in log:raise ValueError('Wrong negative outcome '+name)
   row.update(status='expected_failure_observed',causal_failure=fatal[0],artifacts={str(p):sha(p) for p in d.iterdir() if p.is_file() and p.suffix in ('.sv','.tcl','.log')});save();print(name+': '+fatal[0],flush=True)
  d=out/'synthesis';d.mkdir();row=record['synthesis'];row['status']='running'
  tcl=['set_param general.maxThreads 2']+[f'read_verilog -sv {{{rtl/n}}}' for n in rtl_names]+[f'read_xdc {{{rtl/"scratch_frame_store.xdc"}}}',
   'synth_design -top memory_scratch_endpoint_wide -part xcu280-fsvh2892-2L-e -mode out_of_context',
   'report_utilization -file utilization.rpt','report_utilization -hierarchical -file utilization_hierarchical.rpt','write_checkpoint memory_scratch_endpoint_wide.dcp',
   'set b_rams [get_cells -hier -filter {REF_NAME =~ RAMB*}]','set b_file [open ram_cells.txt w]',
   'foreach b_cell $b_rams {puts $b_file "$b_cell [get_property REF_NAME $b_cell]"}','close $b_file',
   'if {[llength $b_rams] == 0} {error "Wide codec RAM not inferred"}',
   'puts "B_WIDE_CODEC_SYNTH_PASS ram_cells=[llength $b_rams]"','exit']
  (d/'synthesize.tcl').write_text('\n'.join(tcl)+'\n');print('Seven negative controls complete; synthesizing wide-codec endpoint',flush=True)
  if run(d,row,'synthesize',[BIN/'vivado','-mode','batch','-source','synthesize.tcl','-log','synthesize.log','-journal','synthesize.jou']):raise ValueError('Synthesis failed')
  row.update(status='exited_zero',artifacts={str(p):sha(p) for p in d.iterdir() if p.is_file() and p.suffix in ('.tcl','.log','.rpt','.txt','.dcp')})
  for name,digest in files.items():
   if sha(name)!=digest:raise ValueError('Source changed during build')
  record['status']='completed';save();print('Build complete; terminal audit required',flush=True)
 except Exception as e:record.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
