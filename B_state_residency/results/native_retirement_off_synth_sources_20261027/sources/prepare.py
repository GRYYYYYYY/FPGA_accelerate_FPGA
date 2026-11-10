"""Prepare matched OOC roots from the audited restore seed candidate.

Preparation does not launch Vivado or imply synthesis/timing success.
Only the bypass generic differs between the two experiments. The baseline
provider and snapshot writers instantiated outside the query root in the TB
are outside this OOC boundary; all query root runtime ports remain external.
"""
from pathlib import Path
import json,shutil,sys
from run_checkpoint_authority import ROOT,sha

out=Path(sys.argv[1]).resolve();enabled=int(sys.argv[2]);assert enabled in [0,1]
base=out.parent/'restore_seed_on_full_v1'
bm=json.loads((base/'manifest.json').read_text());audit=json.loads((base/'source_bound_audit.json').read_text())
assert audit['status']=='passed'and audit['manifest_sha256']==sha(base/'manifest.json')
out.mkdir();src=out/'sources';src.mkdir();sources={}
for n,e in bm['sources'].items():
    if Path(n).suffix not in ['.sv','.v','.dat']or Path(n).name.startswith('tb_')or n=='axi_file_memory.sv':continue
    p=base/'sources'/n;assert sha(p)==e['sha256'];q=src/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);sources[n]=sha(q)
rtl=[n for n in bm['rtl']if n in sources and Path(n).suffix in ['.sv','.v']]
assert 'query_residency_system.sv'in rtl and 'residency_system.sv'in rtl
for p in src.rglob('*.dat'):shutil.copyfile(p,out/p.name)
parameters=dict(PATH_SLOTS=4,PATH_SLOT_BITS=2,SLOTS=32,FRAMES=16384,INDEX_BITS=14,HASH_BITS=15,
                RESTORE_RECORDS=1024,ENABLE_BASELINE=1,ENABLE_RESTORE_SEED_BYPASS=enabled,
                CHECK_LABEL_CRC=1,ENABLE_FRAME_SCAN=1,ENABLE_WARM_RECOVERY=1,ENABLE_TEST_INJECTION=0)
# A declared experimental target, not a claim that implementation meets 100 MHz.
(out/'clock.xdc').write_text('create_clock -name core_clk -period 10.000 [get_ports clk]\n')
tcl='set_param general.maxThreads 2\n'
tcl+='puts [list VIVADO_VERSION [version -short]]\n'
tcl+=''.join('read_verilog -sv {'+str(src/n)+'}\n'for n in rtl)
tcl+='read_xdc {'+str(out/'clock.xdc')+'}\n'
tcl+='synth_design -mode out_of_context -top query_residency_system -part xcu280-fsvh2892-2L-e -generic {'+' '.join(f'{k}={v}'for k,v in parameters.items())+'}\n'
tcl+='report_utilization -file {'+str(out/'utilization.rpt')+'}\n'
tcl+='report_timing_summary -delay_type min_max -report_unconstrained -max_paths 10 -file {'+str(out/'timing_synth.rpt')+'}\n'
tcl+='check_timing -verbose -file {'+str(out/'check_timing.rpt')+'}\n'
tcl+='write_checkpoint -force {'+str(out/'synth.dcp')+'}\nwrite_verilog -force {'+str(out/'synth.v')+'}\n'
tcl+='set fd [open {'+str(out/'facts.txt')+'} w]\n'
tcl+='puts $fd [list latches [llength [get_cells -hier -filter {REF_NAME =~ LD*}]] blackboxes [llength [get_cells -hier -filter {IS_BLACKBOX == 1}]] file_agents [llength [get_cells -hier -filter {REF_NAME =~ axi_file*}]] directory_observers [llength [get_cells -hier -filter {REF_NAME =~ tb_directory*}]] port_bits [llength [get_ports]]]\n'
tcl+='puts $fd [list bypass_port [llength [get_ports restore_seed_enable]] bypass_endpoints [llength [all_fanout -flat -endpoints_only -from [get_ports restore_seed_enable]]]]\n'
tcl+='close $fd\nreport_clocks -file {'+str(out/'clocks.rpt')+'}\nputs RESTORE_SEED_OOC_DONE\n'
(out/'synth.tcl').write_text(tcl)
shutil.copyfile(Path(__file__),src/'prepare.py');sources['prepare.py']=sha(src/'prepare.py')
manifest=dict(status='prepared',sources=sources,rtl=rtl,parameters=parameters,part='xcu280-fsvh2892-2L-e',
    reference=str(base),reference_audit_sha256=sha(base/'source_bound_audit.json'),
    tcl_sha256=sha(out/'synth.tcl'),xdc_sha256=sha(out/'clock.xdc'),clock_period_ns=10,
    scope='Matched query root OOC resource comparison,32 slots/16384 frames/4 paths/1024 restore records, all runtime inputs retained, test injection disabled. Only restore seed bypass generic differs. External baseline AXI provider and snapshot writers are outside this root boundary. Synthesis timing is a pre-placement estimate; no IO delays, placement/routing, timing closure or board measurement.')
(out/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
print('RESTORE_SEED_OOC_PREPARED',out,len(rtl),enabled)
