set b_root [file normalize [file join [file dirname [info script]] ../..]]
puts [exec /usr/bin/python3 -I [file join $b_root scripts/audit_search_access_hls.py] 2>@1]
set b_verified [file join $b_root results search_access_hls_20261024]
set b_out [file join $b_root results search_access_synthesis_20261024]
if {[file exists $b_out]} {error "Preserve existing result directory"}
file mkdir $b_out
file copy [file join $b_verified access_step solution1 syn verilog] [file join $b_out sources]
file copy [file join $b_verified source_bound_audit.json] [file join $b_out simulation_audit.json]
file copy [info script] [file join $b_out synthesize_search_access.tcl]
puts "SEARCH_ACCESS_SYNTH_BEGIN version=[version -short]"
set_param general.maxThreads 2
create_project -in_memory -part xcu280-fsvh2892-2L-e
foreach b_file [glob [file join $b_out sources *.v]] {read_verilog $b_file}
set b_f [open [file join $b_out research_clock.xdc] w]
puts $b_f {create_clock -name research_clock -period 10.000 [get_ports ap_clk]}
close $b_f
read_xdc [file join $b_out research_clock.xdc]
synth_design -top access_step -part xcu280-fsvh2892-2L-e -mode out_of_context
report_utilization -file [file join $b_out utilization.rpt]
report_utilization -hierarchical -file [file join $b_out utilization_hierarchical.rpt]
report_drc -checks [get_drc_checks LUTLP-1] -file [file join $b_out combinational_loops.rpt]
check_timing -verbose -file [file join $b_out check_timing.rpt]
write_checkpoint [file join $b_out access_step.dcp]
close_project
puts "SEARCH_ACCESS_SYNTH_DONE"
