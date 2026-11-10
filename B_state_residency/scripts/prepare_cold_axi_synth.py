from pathlib import Path
import json,sys,shutil
from run_checkpoint_authority import sha
p=Path(sys.argv[1]).resolve();base=Path(sys.argv[2]).resolve();p.mkdir();src=p/'sources';src.mkdir();bm=json.loads((base/'manifest.json').read_text());assert json.loads((base/'source_bound_audit.json').read_text())['status']=='passed';sources={}
for n,h in bm['sources'].items():
 if Path(n).suffix not in ['.sv','.v','.dat']or Path(n).name.startswith('tb_')or n=='axi_file_memory.sv':continue
 q=src/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(base/'sources'/n,q);assert sha(q)==h['sha256'];sources[n]=sha(q)
rtl=[n for n in bm['rtl']if n in sources and Path(n).suffix in ['.sv','.v']]
for f in src.rglob('*.dat'):shutil.copyfile(f,p/f.name)
tcl='set_param general.maxThreads 2\n'+''.join('read_verilog -sv {'+str(src/n)+'}\n'for n in rtl)
tcl+='synth_design -mode out_of_context -top query_residency_system -part xcu280-fsvh2892-2L-e\n'
tcl+='report_utilization -file {'+str(p/'utilization.rpt')+'}\nwrite_checkpoint -force {'+str(p/'synth.dcp')+'}\nwrite_verilog -force {'+str(p/'synth.v')+'}\nputs QUERY_LIFECYCLE_SYNTH_DONE\n'
tcl+='set fd [open {'+str(p/'facts.txt')+'} w]; puts $fd [list latches [llength [get_cells -hier -filter {REF_NAME =~ LD*}]] blackboxes [llength [get_cells -hier -filter {IS_BLACKBOX == 1}]] file_agents [llength [get_cells -hier -filter {REF_NAME =~ axi_file*}]] directory_observers [llength [get_cells -hier -filter {REF_NAME =~ tb_directory*}]] port_bits [llength [get_ports]]]; close $fd\n'
tcl+='set names {}; foreach pp [get_ports] {lappend names [regsub {\\[[0-9]+\\]$} [get_property NAME $pp] {}]}; set fd [open {'+str(p/'port_counts.txt')+'} w]; puts $fd [list logical_ports [llength [lsort -unique $names]] port_bits [llength [get_ports]]]; close $fd\n'
(p/'synth.tcl').write_text(tcl);(p/'manifest.json').write_text(json.dumps({'status':'prepared','sources':sources,'rtl':rtl,'part':'xcu280-fsvh2892-2L-e','tcl_sha256':sha(p/'synth.tcl'),'reference':str(base),'reference_audit_sha256':sha(base/'source_bound_audit.json'),'scope':'Full default32/16384 boot-gated production root with accepted-host-response ownership. All runtime descriptor/context inputs retained, no test injection/observer/AXI file agent. OOC only, no constrained timing/place/route/board result.'},indent=2)+'\n');print(p,len(rtl))
