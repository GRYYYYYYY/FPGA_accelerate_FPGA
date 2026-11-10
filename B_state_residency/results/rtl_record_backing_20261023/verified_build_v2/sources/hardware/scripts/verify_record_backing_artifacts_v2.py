"""Continue v1 after classifying the first observed runtime failure.
The bypassed encoder fails at the earlier write PIN-rejection input case.
Keep that evidence and run remaining six controls; do not weaken the TB.
"""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 variants={
  'start_before_validation':('record_backing_service.sv','state<=cookie[58]?SEND:ENCODE;','state<=SEND;','record input timeout'),
  'lookup_allocates_empty':('backing_frame_directory_lookup.sv','if(cmd_op==LOOKUP && allocated==0)',"if(1'b0)",'service mismatch'),
  'lookup_allocates_nonempty':('backing_frame_directory_lookup.sv','else if(lookup_only)',"else if(1'b0)",'service mismatch'),
  'respond_before_records':('record_backing_service.sv','FINISH:if(c_done)',"FINISH:if(1'b1)",'success before all decoded records consumed'),
  'ignore_bad_decoded_page':('record_backing_service.sv','if(c_error && rsp_status==0)',"if(1'b0)",'service mismatch'),
  'allow_commands_after_fault':('record_backing_service.sv','if(fault)',"if(1'b0)",'service mismatch'),
  'omit_codec_cancel':('record_backing_service.sv','.cancel(state==CANCEL)',".cancel(1'b0)",'response stuck'),
 }
 for name,(file,old,new,expected) in variants.items():
  if (ROOT/'hardware/rtl'/file).read_text().count(old)!=1:raise ValueError('Nonunique mutation '+name)
 evidence=Path(sys.argv[1]).resolve();out=evidence/'verified_build_v2';out.mkdir();path=out/'build_manifest.json'
 rtl_names=['scratch_page_axi.sv','backing_frame_directory_lookup.sv','backing_page_service_lookup.sv','scratch_page_codec.sv','record_backing_service.sv']
 names=['hardware/rtl/'+n for n in rtl_names]+['hardware/rtl/scratch_frame_store.xdc','hardware/rtl/backing_frame_directory.sv','hardware/rtl/backing_page_service.sv','hardware/tb/tb_record_backing_service.sv','hardware/tb/tb_backing_page_service.sv','hardware/scripts/make_lookup_service.py','hardware/scripts/make_record_backing_tb.py','hardware/scripts/verify_record_backing_artifacts.py','hardware/scripts/verify_record_backing_artifacts_v2.py']
 files={}
 for name in names:
  p=ROOT/name;files[str(p)]=sha(p);dst=out/'sources'/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(p.read_bytes())
 record=dict(status='running',files=files,negative_controls={},synthesis={})
 def save():path.write_text(json.dumps(record,indent=2)+'\n')
 def run(d,row,stage,cmd):
  row.setdefault('commands',[]).append(dict(stage=stage,argv=list(map(str,cmd))));save()
  with (d/(stage+'.console.log')).open('w') as log:r=subprocess.run(cmd,cwd=d,stdout=log,stderr=subprocess.STDOUT)
  row['commands'][-1]['exit_code']=r.returncode;save();return r.returncode
 save()
 try:
  rtl=out/'sources/hardware/rtl';tb=out/'sources/hardware/tb/tb_record_backing_service.sv'
  pages=ROOT/'results/rtl_backing_axi_20261023/fixtures/pages.hex';records=ROOT/'results/rtl_page_codec_20261023/records.hex'
  prior_path=evidence/'verified_build/build_manifest.json';prior=json.loads(prior_path.read_text())
  if prior['status']!='failed' or prior['error']!="ValueError('Wrong negative outcome start_before_validation')":raise ValueError('Unexpected prior failure')
  for p,h in prior['files'].items():
   if sha(p)!=h:raise ValueError('Prior source changed '+p)
  record['prior_build']={'path':str(prior_path),'sha256':sha(prior_path)}
  for name,(file,old,new,expected) in variants.items():
   if name=='start_before_validation':
    d=prior_path.parent/'negative_controls'/name;row=dict(prior['negative_controls'][name])
    if row['removed']!=old or row['replacement']!=new:raise ValueError('Changed inherited mutation')
    if (d/file).read_text()!=(rtl/file).read_text().replace(old,new):raise ValueError('Prior variant mismatch')
    log=(d/'simulate.log').read_text();fatal=[x for x in log.splitlines() if x.startswith('Fatal:')]
    if len(fatal)!=1 or expected not in fatal[0] or 'TEST_PASS' in log or any(c['exit_code'] for c in row['commands'][:2]):raise ValueError('Wrong inherited evidence')
    row.update(status='expected_failure_observed',expected_failure=expected,causal_failure=fatal[0],inherited_from=str(prior_path),artifacts={str(p):sha(p) for p in d.iterdir() if p.is_file() and p.suffix in ('.sv','.tcl','.log')})
    record['negative_controls'][name]=row;save();print(name+': verified prior runtime failure (early PIN rejection prevents record ingress)',flush=True);continue
   d=out/'negative_controls'/name;d.mkdir(parents=True);row=dict(status='running',file=file,removed=old,replacement=new,expected_failure=expected);record['negative_controls'][name]=row
   mutant=d/file;mutant.write_text((rtl/file).read_text().replace(old,new));(d/'simulate.tcl').write_text('run 101ms\nquit\n')
   src=[mutant if name==file else rtl/name for name in rtl_names]
   if run(d,row,'compile',[BIN/'xvlog','--sv','--work','xil_defaultlib',*src,tb]):raise ValueError('Negative compile failure')
   if run(d,row,'elaborate',[BIN/'xelab','xil_defaultlib.tb_record_backing_service','--snapshot','negative_tb','--debug','typical','--mt','2']):raise ValueError('Negative elaboration failure')
   run(d,row,'simulate',[BIN/'xsim','negative_tb','--tclbatch','simulate.tcl','--testplusarg','PAGES='+str(pages),'--testplusarg','RECORDS='+str(records),'--log','simulate.log'])
   log=(d/'simulate.log').read_text();fatal=[x for x in log.splitlines() if x.startswith('Fatal:')]
   if len(fatal)!=1 or expected not in fatal[0] or 'TEST_PASS' in log:raise ValueError('Wrong negative outcome '+name)
   row.update(status='expected_failure_observed',causal_failure=fatal[0],artifacts={str(p):sha(p) for p in d.iterdir() if p.is_file() and p.suffix in ('.sv','.tcl','.log')});save();print(name+': '+fatal[0],flush=True)
  d=out/'synthesis';d.mkdir();row=record['synthesis'];row['status']='running'
  tcl=['set_param general.maxThreads 2']+[f'read_verilog -sv {{{rtl/n}}}' for n in rtl_names]+[f'read_xdc {{{rtl/"scratch_frame_store.xdc"}}}',
   'synth_design -top record_backing_service -part xcu280-fsvh2892-2L-e -mode out_of_context',
   'report_utilization -file utilization.rpt','report_utilization -hierarchical -file utilization_hierarchical.rpt',
   'write_checkpoint record_backing_service.dcp',
   'set b_rams [get_cells -hier -filter {REF_NAME =~ RAMB*}]','set b_file [open ram_cells.txt w]',
   'foreach b_cell $b_rams {puts $b_file "$b_cell [get_property REF_NAME $b_cell]"}','close $b_file',
   'if {[llength $b_rams] == 0} {error "Adapter BRAM was not inferred"}',
   'puts "B_RECORD_BACKING_SYNTH_PASS ram_cells=[llength $b_rams]"','exit']
  (d/'synthesize.tcl').write_text('\n'.join(tcl)+'\n');print('Seven negative controls complete; synthesizing full record adapter at 23405 frames',flush=True)
  if run(d,row,'synthesize',[BIN/'vivado','-mode','batch','-source','synthesize.tcl','-log','synthesize.log','-journal','synthesize.jou']):raise ValueError('Synthesis failed')
  row.update(status='exited_zero',artifacts={str(p):sha(p) for p in d.iterdir() if p.is_file() and p.suffix in ('.tcl','.log','.rpt','.txt','.dcp')})
  for name,digest in files.items():
   if sha(name)!=digest:raise ValueError('Source changed during build')
  record['status']='completed';save();print('Build complete; terminal audit required',flush=True)
 except Exception as e:record.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
