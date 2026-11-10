"""Continue after external COMPLETE is caught earlier by the ordering assertion.
Verify six existing failure traces; run the last control and whole-top synthesis.
"""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 variants={
  'complete_before_memory':('M_TRANSFER_SEND:if(m_ready)state<=kind?RF_GET:WB_EXPORT_SEND;','M_TRANSFER_SEND:if(m_ready)state<=Q_COMPLETE_SEND;','COMPLETE before memory and 64 record acknowledgements'),
  'retire_before_page_ack':('else state<=Q_COMPLETE_SEND;','else state<=M_RETIRE_SEND;','address RETIRE before page COMPLETE acknowledgement'),
  'skip_last_beat_ack':('RF_BEAT_SEND:if(q_ready)state<=RF_BEAT_WAIT;','RF_BEAT_SEND:if(q_ready)state<=position==63?M_STATUS:RF_BEAT_WAIT;','COMPLETE before memory and 64 record acknowledgements'),
  'skip_address_recycle':('if(op==11 && q_status==0)state<=M_RECYCLE_SEND;','if(op==11 && q_status==0)begin state<=IDLE;rsp_valid<=1;fence_open<=0;end','fence never reached address recycle'),
  'ignore_fault_guard':('if(fault)',"if(1'b0)",'host mismatch'),
  'allow_external_complete':('(cmd_op>=7 && cmd_op<=9) || cmd_op>=12','(cmd_op>=7 && cmd_op<=9 && cmd_op!=8) || cmd_op>=12','COMPLETE before memory and 64 record acknowledgements'),
  'accept_during_recycle':('assign cmd_ready=!rst && state==IDLE && !rsp_valid;','assign cmd_ready=!rst && !rsp_valid;','new host command before address recycle'),
 }
 original=(ROOT/'hardware/rtl/memory_scratch_endpoint.sv').read_text()
 for name,(old,new,expected) in variants.items():
  if original.count(old)!=1:raise ValueError('Nonunique mutation '+name)
 evidence=Path(sys.argv[1]).resolve();out=evidence/'verified_build_v2';out.mkdir();path=out/'build_manifest.json'
 rtl_names=['bounded_sync_fifo.sv','scratch_frame_store_bram.sv','scratch_page_controller.sv','queued_scratch_endpoint.sv','scratch_page_axi.sv','backing_frame_directory_lookup.sv','backing_page_service_lookup.sv','scratch_page_codec.sv','record_backing_service.sv','memory_scratch_endpoint.sv']
 names=['hardware/rtl/'+n for n in rtl_names]+['hardware/rtl/scratch_frame_store.xdc','hardware/tb/tb_memory_endpoint.sv','hardware/tb/memory_endpoint_stimulus.svh','hardware/tb/tb_backing_page_service.sv','hardware/scripts/make_memory_endpoint_tb.py','hardware/scripts/make_memory_endpoint_vectors.py','hardware/scripts/verify_memory_endpoint_artifacts.py','hardware/scripts/verify_memory_endpoint_artifacts_v2.py']
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
  rtl=out/'sources/hardware/rtl';tb=out/'sources/hardware/tb/tb_memory_endpoint.sv'
  prior_path=evidence/'verified_build/build_manifest.json';prior=json.loads(prior_path.read_text())
  if prior['status']!='failed' or prior['error']!="ValueError('Wrong negative outcome allow_external_complete')":raise ValueError('Unexpected prior classification')
  for p,h in prior['files'].items():
   if sha(p)!=h:raise ValueError('Changed prior source '+p)
  record['prior_build']={'path':str(prior_path),'sha256':sha(prior_path)}
  for name,(old,new,expected) in variants.items():
   if name!='accept_during_recycle':
    d=prior_path.parent/'negative_controls'/name;row=dict(prior['negative_controls'][name])
    if row['removed']!=old or row['replacement']!=new or (d/'memory_scratch_endpoint.sv').read_text()!=original.replace(old,new):raise ValueError('Inherited mutation differs')
    for p,h in row.get('artifacts',{}).items():
     if sha(p)!=h:raise ValueError('Changed prior artifact')
    log=(d/'simulate.log').read_text();fatal=[x for x in log.splitlines() if x.startswith('Fatal:')]
    if len(fatal)!=1 or expected not in fatal[0] or 'TEST_PASS' in log or any(c['exit_code'] for c in row['commands'][:2]):raise ValueError('Wrong inherited failure')
    row.update(status='expected_failure_observed',expected_failure=expected,causal_failure=fatal[0],inherited_from=str(prior_path),artifacts={str(p):sha(p) for p in d.iterdir() if p.is_file() and p.suffix in ('.sv','.tcl','.log')})
    record['negative_controls'][name]=row;save();print(name+': verified existing runtime failure',flush=True);continue
   d=out/'negative_controls'/name;d.mkdir(parents=True);row=dict(status='running',removed=old,replacement=new,expected_failure=expected);record['negative_controls'][name]=row
   mutant=d/'memory_scratch_endpoint.sv';mutant.write_text(original.replace(old,new));(d/'simulate.tcl').write_text('run 2s\nquit\n')
   src=[mutant if n=='memory_scratch_endpoint.sv' else rtl/n for n in rtl_names]
   if run(d,row,'compile',[BIN/'xvlog','--sv','--work','xil_defaultlib',*src,tb]):raise ValueError('Negative compile failure')
   if run(d,row,'elaborate',[BIN/'xelab','xil_defaultlib.tb_memory_endpoint_small','--snapshot','negative_tb','--debug','typical','--mt','2']):raise ValueError('Negative elaboration failure')
   run(d,row,'simulate',[BIN/'xsim','negative_tb','--tclbatch','simulate.tcl','--log','simulate.log'])
   log=(d/'simulate.log').read_text();fatal=[x for x in log.splitlines() if x.startswith('Fatal:')]
   if len(fatal)!=1 or expected not in fatal[0] or 'TEST_PASS' in log:raise ValueError('Wrong negative outcome '+name)
   row.update(status='expected_failure_observed',causal_failure=fatal[0],artifacts={str(p):sha(p) for p in d.iterdir() if p.is_file() and p.suffix in ('.sv','.tcl','.log')});save();print(name+': '+fatal[0],flush=True)
  d=out/'synthesis';d.mkdir();row=record['synthesis'];row['status']='running'
  tcl=['set_param general.maxThreads 2']+[f'read_verilog -sv {{{rtl/n}}}' for n in rtl_names]+[f'read_xdc {{{rtl/"scratch_frame_store.xdc"}}}',
   'synth_design -top memory_scratch_endpoint -part xcu280-fsvh2892-2L-e -mode out_of_context',
   'report_utilization -file utilization.rpt','report_utilization -hierarchical -file utilization_hierarchical.rpt','write_checkpoint memory_scratch_endpoint.dcp',
   'set b_rams [get_cells -hier -filter {REF_NAME =~ RAMB*}]','set b_file [open ram_cells.txt w]',
   'foreach b_cell $b_rams {puts $b_file "$b_cell [get_property REF_NAME $b_cell]"}','close $b_file',
   'if {[llength $b_rams] == 0} {error "Endpoint BRAM not inferred"}',
   'puts "B_MEMORY_ENDPOINT_SYNTH_PASS ram_cells=[llength $b_rams]"','exit']
  (d/'synthesize.tcl').write_text('\n'.join(tcl)+'\n');print('Seven negative controls complete; synthesizing closed memory endpoint',flush=True)
  if run(d,row,'synthesize',[BIN/'vivado','-mode','batch','-source','synthesize.tcl','-log','synthesize.log','-journal','synthesize.jou']):raise ValueError('Synthesis failed')
  row.update(status='exited_zero',artifacts={str(p):sha(p) for p in d.iterdir() if p.is_file() and p.suffix in ('.tcl','.log','.rpt','.txt','.dcp')})
  for name,digest in files.items():
   if sha(name)!=digest:raise ValueError('Source changed during build')
  record['status']='completed';save();print('Build complete; terminal audit required',flush=True)
 except Exception as e:record.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
