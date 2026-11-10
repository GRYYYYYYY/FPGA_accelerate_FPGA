from pathlib import Path
import json,sys,shutil
from run_checkpoint_authority import sha
p=Path(sys.argv[1]).resolve();unit=Path(sys.argv[2]).resolve();base='--base'in sys.argv[3:];p.mkdir();s=p/'sources';s.mkdir();rtl=Path('/tmp/B_state_residency_offer_20261025/authority_query_v4/sources/query_lifecycle.sv')if base else unit/'sources/query_lifecycle.sv'
shutil.copyfile(rtl,s/'query_lifecycle.sv');shutil.copyfile(__file__,s/Path(__file__).name)
tcl='set_param general.maxThreads 2\nread_verilog -sv {'+str(s/'query_lifecycle.sv')+'}\nsynth_design -mode out_of_context -top query_lifecycle -part xcu280-fsvh2892-2L-e\nreport_utilization -file {'+str(p/'utilization.rpt')+'}\nwrite_checkpoint -force {'+str(p/'synth.dcp')+'}\nwrite_verilog -force {'+str(p/'synth.v')+'}\n'
tcl+='set fd [open {'+str(p/'facts.txt')+'} w]; puts $fd [list latches [llength [get_cells -hier -filter {REF_NAME =~ LD*}]] blackboxes [llength [get_cells -hier -filter {IS_BLACKBOX == 1}]] port_bits [llength [get_ports]]]; close $fd\nputs QUERY_CP_SYNTH_DONE\n'
(p/'synth.tcl').write_text(tcl);(p/'manifest.json').write_text(json.dumps({'status':'prepared','baseline':base,'reference':str(rtl),'rtl_sha256':sha(s/'query_lifecycle.sv'),'tcl_sha256':sha(p/'synth.tcl'),'scope':'Original query controller baseline OOC'if base else'Query sequence checkpoint native component only OOC; no full-query integration or timing/board claim'},indent=2)+'\n')
