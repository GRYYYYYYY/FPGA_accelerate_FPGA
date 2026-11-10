"""Export one audited native candidate; no dependency on an XPR or remote IP."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
SYNTH='''# Portable non-project OOC rebuild. No project, IP or prior DCP required.
set candidate_root [file normalize [file join [file dirname [info script]] ..]]
if {![info exists candidate_output]} {
    if {[llength $argv]!=1} {error "Usage: vivado -mode batch -source Scripts/synth.tcl -tclargs NEW_OUTPUT"}
    set candidate_output [file normalize [lindex $argv 0]]
}
if {[file exists $candidate_output]} {error "Refuse to overwrite candidate rebuild output"}
file mkdir $candidate_output
set_param general.maxThreads 2
puts "RESIDENCY_CANDIDATE_REBUILD_BEGIN version=[version -short]"
create_project -in_memory -part xcu280-fsvh2892-2L-e
foreach candidate_module {bounded_sync_fifo response_fallthrough_fifo scratch_frame_store_bram scratch_page_controller_small queued_scratch_endpoint_small scratch_page_axi_small backing_frame_directory_small backing_page_service_small scratch_page_codec_small_static record_backing_service_small_staticcodec memory_scratch_endpoint_small_staticcodec} {
    read_verilog -sv [file join $candidate_root Sources RTL ${candidate_module}.sv]
}
read_xdc [file join $candidate_root Sources Constraints research_clock.xdc]
synth_design -top memory_scratch_endpoint_small_staticcodec -part xcu280-fsvh2892-2L-e -mode out_of_context -generic EPOCH_BITS=6
report_utilization -file [file join $candidate_output utilization.rpt]
report_utilization -hierarchical -file [file join $candidate_output utilization_hierarchical.rpt]
write_checkpoint [file join $candidate_output candidate.dcp]
set candidate_done [open [file join $candidate_output completed.txt] w]
puts $candidate_done "RESIDENCY_CANDIDATE_REBUILD_DONE version=[version -short]"
close $candidate_done
close_project
puts "RESIDENCY_CANDIDATE_REBUILD_DONE"
'''
VERIFY='''"""Verify package hashes; optionally run one standalone XSim regression."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--test',choices=['checkpoint','wrap']);ap.add_argument('--output',type=Path);ap.add_argument('--vivado-bin',type=Path);a=ap.parse_args()
 spec=json.loads((ROOT/'manifest.json').read_text())
 for name,digest in spec['artifacts'].items():assert sha(ROOT/name)==digest,name
 if not a.test:print('CANDIDATE_PACKAGE_HASH_PASS');return
 assert a.output,'--output must name a new directory';out=a.output.resolve();out.mkdir()
 binary=lambda n:str(a.vivado_bin/n) if a.vivado_bin else shutil.which(n)
 assert all(binary(n) for n in ['xvlog','xelab','xsim']),'Use --vivado-bin or put Vivado bin on PATH'
 top='tb_small_endpoint_epoch6' if a.test=='checkpoint' else 'tb_record_epoch6_wrap'
 tb=ROOT/'Sources/Simulation'/('tb_small_endpoint_epoch6.sv' if a.test=='checkpoint' else 'tb_record_epoch6_wrap.sv')
 (out/'run.tcl').write_text('run all\\nquit\\n')
 sources=[ROOT/name for name in spec['rtl']]+[tb]
 m={'status':'running','test':a.test,'commands':[],'package_sha256':sha(ROOT/'manifest.json')}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\\n')
 save()
 try:
  commands=[('compile',[binary('xvlog'),'--sv',*[str(p) for p in sources]]),('elaborate',[binary('xelab'),top,'-s','candidate','--debug','typical','--mt','2']),('simulate',[binary('xsim'),'candidate','--tclbatch','run.tcl','--log','simulate.log'])]
  for stage,argv in commands:
   with (out/(stage+'.stdout.log')).open('w') as f:r=subprocess.run(argv,cwd=out,stdout=f,stderr=subprocess.STDOUT)
   m['commands'].append({'stage':stage,'argv':argv,'exit_code':r.returncode});save();assert r.returncode==0,stage
  log=(out/'simulate.log').read_text();assert 'Fatal:' not in log and '$finish' in log
  if a.test=='checkpoint':assert 'SMALL_STALLS_PASS cases=8 blocked_cycles=800' in log and 'SMALL_32SLOTS_PASS pages=32 fields=5 checkpoints=8 transfers=288 checks=1778 tag_wraps=4' in log
  else:assert 'COMPOSITE_WRAP_PASS queries=70 transfers=140 tag_wraps=17 epoch_wraps=1 clear_cycles=128 ' in log
  m.update(status='passed',log_sha256=sha(out/'simulate.log'));save();print('CANDIDATE_PACKAGE_SIM_PASS',a.test)
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
'''
def main():
 full=ROOT/'results/record_epoch6_full_20261024';m=json.loads((full/'manifest.json').read_text())
 wp=ROOT/'results/record_epoch6_full_workflow_20261024/manifest.json';w=json.loads(wp.read_text())
 if m['status']!='passed' or w['status']!='composite_replay_audited':
  print(json.dumps({'status':'waiting_for_completed_full_audit','replay':m['status'],'workflow':w['status']}));return
 fa=full/'source_bound_audit.json';a=json.loads(fa.read_text());assert a['status']=='passed' and a['manifest_sha256']==sha(full/'manifest.json')
 assert m['cycle_comparison']['equal'],'Cycle mismatch needs review before preferred native export'
 syn=ROOT/'results/record_epoch6_synthesis_20261024';sa=json.loads((syn/'final_audit.json').read_text());assert sa['status']=='synthesis_evidence_verified'
 phy=ROOT/'results/record_epoch6_timing_20261024';pa=json.loads((phy/'final_audit.json').read_text());assert pa['status']=='evidence_verified' and pa['internal_constraints_met_in_this_model']
 out=ROOT/'hardware/candidates/native_epoch6_record';out.mkdir(parents=True)
 for name in ['Sources/RTL','Sources/Constraints','Sources/Simulation','Scripts','Evidence']:(out/name).mkdir(parents=True)
 rtl=[]
 for p in (full/'pilot/sources').glob('*.sv'):
  if p.name.startswith('tb_'):continue
  assert sha(p)==next(h for n,h in m['cases']['pilot']['sources'].items() if Path(n).name==p.name)
  assert sha(p)==sha(syn/'sources'/p.name)
  dest=out/'Sources/RTL'/p.name;dest.write_bytes(p.read_bytes());rtl.append(str(dest.relative_to(out)))
 assert len(rtl)==11
 for name,case in [('tb_small_endpoint_epoch6.sv','record_epoch6_stalls_20261024'),('tb_record_epoch6_wrap.sv','record_epoch6_wrap_20261024')]:
  p=ROOT/'results'/case/'pilot/sources'/name;(out/'Sources/Simulation'/name).write_bytes(p.read_bytes())
  cm=json.loads((ROOT/'results'/case/'manifest.json').read_text());assert cm['status']=='passed'
  assert sha(p)==next(h for n,h in cm['cases']['pilot']['sources'].items() if Path(n).name==name)
 (out/'Sources/Constraints/research_clock.xdc').write_bytes((syn/'research_clock.xdc').read_bytes())
 for name,p in [('full_audit.json',fa),('query_comparison.json',full/'query_comparison.json'),('physical_audit.json',phy/'final_audit.json'),('synthesis_audit.json',syn/'final_audit.json'),('lifecycle_audit.json',ROOT/'results/record_epoch6_wrap_20261024/source_bound_audit.json')]:
  (out/'Evidence'/name).write_bytes(p.read_bytes())
 (out/'Scripts/synth.tcl').write_text(SYNTH);(out/'verify.py').write_text(VERIFY)
 (out/'README.md').write_text('''# Native epoch6 / static codec / record response bypass candidate

Self-contained RTL-only non-project OOC package. Requires Vivado 2022.2; default target xcu280-fsvh2892-2L-e. Top memory_scratch_endpoint_small_staticcodec, FRAMES163840, INDEX/HASH18, EPOCH_BITS6, TX/GEN16, TAG2, 32 slots, 192-byte pages.

Run `python3 verify.py` to verify hashes. Run `python3 verify.py --test checkpoint --output NEW_DIR --vivado-bin VIVADO_BIN` (or `--test wrap`) for a standalone regression. Rebuild synthesis with `vivado -mode batch -source Scripts/synth.tcl -tclargs NEW_OUTPUT`. Use a new output directory; generated results are not source inputs.

Evidence records retain original experiment provenance paths, but build and simulation require only this package. No XPR, IP, data fixture or prior DCP is needed. This is the native 32-bit relative-address endpoint; the separate address64 wrapper is not included.

Evidence covers 38-query actual-value replay, lifecycle/AXI checks, and internal 10ns OOC implementation. External IO delays and upstream physical-clock context remain incomplete. No complete FPGA router, XRT integration, board timing or board acceleration is claimed.
''')
 spec={'status':'source_exported','top':'memory_scratch_endpoint_small_staticcodec','part':'xcu280-fsvh2892-2L-e','parameters':{'FRAMES':163840,'INDEX_BITS':18,'HASH_BITS':18,'EPOCH_BITS':6,'TX_BITS':16,'GENERATION_BITS':16,'TAG_BITS':2},'rtl':sorted(rtl),'full_manifest_sha256':sha(full/'manifest.json'),'workflow_manifest_sha256':sha(wp),'exporter_sha256':sha(Path(__file__)),'artifacts':{str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}}
 (out/'manifest.json').write_text(json.dumps(spec,indent=2)+'\n');print(out)
if __name__=='__main__':main()
