set b_root [file normalize [file join [file dirname [info script]] ../..]]
puts [exec /usr/bin/python3 -I [file join $b_root scripts/audit_expansion.py] 2>@1]
puts [exec /usr/bin/python3 -I [file join $b_root scripts/audit_expansion_boundaries.py] 2>@1]
set b_verified [file join $b_root results expansion_20261024]
set b_boundary [file join $b_root results expansion_boundaries_20261024]
set b_out [file join $b_root results expansion_synthesis_20261024]
if {[file exists $b_out]} {error "Preserve existing results"}
file mkdir $b_out
file copy [file join $b_verified sources] [file join $b_out sources]
file copy [file join $b_verified source_bound_audit.json] [file join $b_out simulation_audit.json]
file copy [file join $b_boundary source_bound_audit.json] [file join $b_out boundary_audit.json]
file copy [info script] [file join $b_out synthesize_expansion.tcl]
set b_files [exec /usr/bin/python3 -I -c {import json,sys,pathlib; m=json.load(open(sys.argv[1])); print("\n".join(n for n in m['rtl'] if not pathlib.Path(n).name.startswith('tb_') and pathlib.Path(n).name!='axi_file_memory.sv'))} [file join $b_verified manifest.json]]
puts "EXPANSION_SYNTH_BEGIN version=[version -short]"
set_param general.maxThreads 2
create_project -in_memory -part xcu280-fsvh2892-2L-e
foreach b_name [split $b_files \n] {read_verilog -sv [file join $b_out sources $b_name]}
set b_f [open [file join $b_out research_clock.xdc] w]
puts $b_f {create_clock -name research_clock -period 10.000 [get_ports clk]}
close $b_f
read_xdc [file join $b_out research_clock.xdc]
synth_design -top node_expansion_engine -part xcu280-fsvh2892-2L-e -mode out_of_context
report_utilization -file [file join $b_out utilization.rpt]
report_drc -checks [get_drc_checks LUTLP-1] -file [file join $b_out combinational_loops.rpt]
check_timing -verbose -file [file join $b_out check_timing.rpt]
write_checkpoint [file join $b_out node_expansion_engine.dcp]
close_project
puts "EXPANSION_SYNTH_DONE"
