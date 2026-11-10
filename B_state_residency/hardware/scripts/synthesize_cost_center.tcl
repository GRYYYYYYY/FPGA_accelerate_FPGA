set center_root [file normalize [file join [file dirname [info script]] ../..]]
set center_sim [file join $center_root results cost_center_hls_20261025]
puts [exec /usr/bin/python3 -I [file join $center_root scripts audit_cost_center_hls.py] $center_sim 2>@1]
set center_out [file join $center_root results cost_center_synthesis_20261025]
if {[file exists $center_out]} {error "Preserve existing results"}
file mkdir $center_out
file copy [file join $center_sim cost_center_step solution1 syn verilog] [file join $center_out sources]
file copy [file join $center_sim source_bound_audit.json] [file join $center_out simulation_audit.json]
file copy [info script] [file join $center_out synthesize_cost_center.tcl]
puts "COST_CENTER_SYNTH_BEGIN version=[version -short]"
set_param general.maxThreads 2
create_project -in_memory -part xcu280-fsvh2892-2L-e
foreach center_file [glob [file join $center_out sources *.v]] {read_verilog $center_file}
set center_f [open [file join $center_out research_clock.xdc] w]
puts $center_f {create_clock -name research_clock -period 10.000 [get_ports ap_clk]}
close $center_f
read_xdc [file join $center_out research_clock.xdc]
synth_design -top cost_center_step -part xcu280-fsvh2892-2L-e -mode out_of_context
report_utilization -file [file join $center_out utilization.rpt]
report_drc -checks [get_drc_checks LUTLP-1] -file [file join $center_out combinational_loops.rpt]
check_timing -verbose -file [file join $center_out check_timing.rpt]
report_timing_summary -delay_type max -max_paths 10 -file [file join $center_out timing_summary.rpt]
write_checkpoint [file join $center_out cost_center_step.dcp]
close_project
puts "COST_CENTER_SYNTH_DONE"
