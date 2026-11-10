set b_root [file normalize [file join [file dirname [info script]] ../..]]
set b_out [file join $b_root results candidate_cost_synthesis_20261025]
puts [exec /usr/bin/python3 -I [file join $b_root scripts prepare_candidate_cost_synthesis.py] $b_out 2>@1]
file copy [info script] [file join $b_out synthesize_candidate_cost.tcl]
set b_files [exec /usr/bin/python3 -I -c {import json,sys; print("\n".join(json.load(open(sys.argv[1]))['rtl']))} [file join $b_out manifest.json]]
puts "CANDIDATE_COST_SYNTH_BEGIN version=[version -short]"
set_param general.maxThreads 2
create_project -in_memory -part xcu280-fsvh2892-2L-e
foreach b_name [split $b_files \n] {read_verilog -sv [file join $b_out sources $b_name]}
set b_f [open [file join $b_out research_clock.xdc] w]
puts $b_f {create_clock -name research_clock -period 10.000 [get_ports clk]}
close $b_f
read_xdc [file join $b_out research_clock.xdc]
synth_design -top candidate_cost_state_engine -part xcu280-fsvh2892-2L-e -mode out_of_context
report_utilization -file [file join $b_out utilization.rpt]
report_drc -checks [get_drc_checks LUTLP-1] -file [file join $b_out combinational_loops.rpt]
check_timing -verbose -file [file join $b_out check_timing.rpt]
report_timing_summary -delay_type max -max_paths 10 -file [file join $b_out timing_summary.rpt]
write_checkpoint [file join $b_out candidate_cost_state_engine.dcp]
close_project
puts "CANDIDATE_COST_SYNTH_DONE"
