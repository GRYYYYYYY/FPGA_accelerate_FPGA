"""Continue after v1 ambiguous mutation selector; preserve four completed controls.
Freeze codec inputs, run remaining mutations, and synthesize only the codec.
Successful run is build evidence; report_page_codec.py performs final audit.
"""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 evidence=Path(sys.argv[1]).resolve();out=evidence/'verified_build_v2';out.mkdir();path=out/'build_manifest.json'
 names=['hardware/rtl/scratch_page_codec.sv','hardware/tb/tb_scratch_page_codec.sv','hardware/tb/tb_codec_axi.sv','hardware/scripts/make_codec_axi_tb.py','hardware/scripts/verify_codec_artifacts.py','hardware/scripts/verify_codec_artifacts_v2.py','hardware/rtl/scratch_frame_store.xdc','hardware/rtl/scratch_page_axi.sv','hardware/rtl/backing_frame_directory.sv','hardware/rtl/backing_page_service.sv','hardware/tb/tb_backing_page_service.sv']
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
  variants={
   'bypass_commit':('else state<=D_COMMIT;','else begin node<=0;field<=0;record_word<=0;state<=D_READ;end','record exposed before successful commit'),
   'ignore_failed_commit':('if(!commit_ok)',"if(1'b0)",'record exposed before successful commit'),
   'ignore_bad_format':('if(bad_page)',"if(1'b0)",'malformed page accepted'),
   'ignore_cancel':('else if(cancel && state!=IDLE)',"else if(1'b0)",'abort did not terminate page'),
   'reverse_record_words':('state==E_STORE?record_buffer[field*32 +: 32]:unpack_word','state==E_STORE?record_buffer[(4-field)*32 +: 32]:unpack_word','encoded byte mismatch'),
   'drop_presence':('bitmap[node]<=record_in_present;','bitmap[node]<=0;','encoded byte mismatch'),
  }
  rtl=out/'sources/hardware/rtl';tb=out/'sources/hardware/tb/tb_scratch_page_codec.sv'
  pages=ROOT/'results/rtl_backing_axi_20261023/fixtures/pages.hex';records=evidence/'records.hex'
  original=(rtl/'scratch_page_codec.sv').read_text()
  prior_path=evidence/'verified_build/build_manifest.json';prior=json.loads(prior_path.read_text())
  if prior['status']!='failed' or prior['error']!="ValueError('Ambiguous mutation reverse_record_words')":raise ValueError('Unexpected prior flow')
  for name,digest in prior['files'].items():
   if sha(name)!=digest:raise ValueError('Inherited source changed '+name)
  record['prior_build']={'path':str(prior_path),'sha256':sha(prior_path)}

  for name,(old,new,expected) in variants.items():
   if name in ('bypass_commit','ignore_failed_commit','ignore_bad_format','ignore_cancel'):
    previous=prior['negative_controls'][name]
    if previous['status']!='expected_failure_observed' or previous['expected_failure']!=expected:raise ValueError('Invalid prior outcome')
    for artifact,digest in previous['artifacts'].items():
     if sha(artifact)!=digest:raise ValueError('Changed prior artifact '+artifact)
    record['negative_controls'][name]=dict(previous,inherited_from=str(prior_path));save();print(name+': verified inherited failure evidence',flush=True);continue
   d=out/'negative_controls'/name;d.mkdir(parents=True);row=dict(status='running',removed=old,replacement=new,expected_failure=expected);record['negative_controls'][name]=row
   if original.count(old)!=1:raise ValueError('Ambiguous mutation '+name)
   mutant=d/'scratch_page_codec.sv';mutant.write_text(original.replace(old,new));(d/'simulate.tcl').write_text('run 101ms\nquit\n')
   if run(d,row,'compile',[BIN/'xvlog','--sv','--work','xil_defaultlib',mutant,tb]):raise ValueError('Negative compile failure')
   if run(d,row,'elaborate',[BIN/'xelab','xil_defaultlib.tb_scratch_page_codec','--snapshot','negative_tb','--debug','typical','--mt','2']):raise ValueError('Negative elaboration failure')
   run(d,row,'simulate',[BIN/'xsim','negative_tb','--tclbatch','simulate.tcl','--testplusarg','PAGES='+str(pages),'--testplusarg','RECORDS='+str(records),'--log','simulate.log'])
   log=(d/'simulate.log').read_text();fatal=[x for x in log.splitlines() if x.startswith('Fatal:')]
   if len(fatal)!=1 or expected not in fatal[0] or 'TEST_PASS' in log:raise ValueError('Wrong negative outcome '+name)
   row.update(status='expected_failure_observed',causal_failure=fatal[0],artifacts={str(p):sha(p) for p in d.iterdir() if p.is_file() and p.suffix in ('.sv','.tcl','.log')});save();print(name+': '+fatal[0],flush=True)
  d=out/'synthesis';d.mkdir();row=record['synthesis'];row['status']='running'
  tcl=['set_param general.maxThreads 2',f'read_verilog -sv {{{rtl/"scratch_page_codec.sv"}}}',f'read_xdc {{{rtl/"scratch_frame_store.xdc"}}}',
   'synth_design -top scratch_page_codec -part xcu280-fsvh2892-2L-e -mode out_of_context',
   'report_utilization -file utilization.rpt','write_checkpoint scratch_page_codec.dcp',
   'set b_rams [get_cells -hier -filter {REF_NAME =~ RAMB*}]','set b_file [open ram_cells.txt w]',
   'foreach b_cell $b_rams {puts $b_file "$b_cell [get_property REF_NAME $b_cell]"}','close $b_file',
   'if {[llength $b_rams] == 0} {error "Codec BRAM was not inferred"}',
   'puts "B_CODEC_SYNTH_PASS ram_cells=[llength $b_rams]"','exit']
  (d/'synthesize.tcl').write_text('\n'.join(tcl)+'\n');print('Negative controls complete; synthesizing codec',flush=True)
  if run(d,row,'synthesize',[BIN/'vivado','-mode','batch','-source','synthesize.tcl','-log','synthesize.log','-journal','synthesize.jou']):raise ValueError('Synthesis failed')
  row.update(status='exited_zero',artifacts={str(p):sha(p) for p in d.iterdir() if p.is_file() and p.suffix in ('.tcl','.log','.rpt','.txt','.dcp')})
  for name,digest in files.items():
   if sha(name)!=digest:raise ValueError('Source changed during build')
  record['status']='completed';save();print('Build completed; independent audit still required',flush=True)
 except Exception as e:record.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
