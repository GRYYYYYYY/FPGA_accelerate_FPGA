set b_root [file normalize [file join [file dirname [info script]] ../..]]
set b_out [file join $b_root results cost_state_synthesis_20261025]
puts [exec /usr/bin/python3 -I [file join $b_root scripts prepare_cost_state_synthesis.py] $b_out 2>@1]
file copy [info script] [file join $b_out synthesize_cost_state.tcl]
set b_files [exec /usr/bin/python3 -I -c {import json,sys; print("\n".join(json.load(open(sys.argv[1]))['rtl']))} [file join $b_out manifest.json]]
puts "COST_STATE_SYNTH_BEGIN version=[version -short]"
set_param general.maxThreads 2
create_project -in_memory -part xcu280-fsvh2892-2L-e
foreach b_name [split $b_files \n] {read_verilog -sv [file join $b_out sources $b_name]}
set b_f [open [file join $b_out research_clock.xdc] w]
puts $b_f {create_clock -name research_clock -period 10.000 [get_ports clk]}
close $b_f
read_xdc [file join $b_out research_clock.xdc]
synth_design -top cost_state_store -part xcu280-fsvh2892-2L-e -mode out_of_context
report_utilization -file [file join $b_out utilization.rpt]
report_drc -checks [get_drc_checks LUTLP-1] -file [file join $b_out combinational_loops.rpt]
check_timing -verbose -file [file join $b_out check_timing.rpt]
report_timing_summary -delay_type max -max_paths 10 -file [file join $b_out timing_summary.rpt]
write_checkpoint [file join $b_out cost_state_store.dcp]
close_project
puts "COST_STATE_SYNTH_DONE"
