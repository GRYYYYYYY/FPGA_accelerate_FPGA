set b_root [file normalize [file join [file dirname [info script]] ../..]]
puts [exec /usr/bin/python3 -I [file join $b_root scripts/audit_frontier_service.py] 2>@1]
puts [exec /usr/bin/python3 -I [file join $b_root scripts/audit_frontier_service_boundaries.py] 2>@1]
set b_verified [file join $b_root results frontier_service_v2_20261024]
set b_out [file join $b_root results frontier_service_synthesis_20261024]
if {[file exists $b_out]} {error "Preserve existing result directory"}
file mkdir $b_out
file copy [file join $b_verified sources] [file join $b_out sources]
file copy [file join $b_verified source_bound_audit.json] [file join $b_out simulation_audit.json]
file copy [file join $b_root results frontier_service_boundaries_20261024 source_bound_audit.json] [file join $b_out boundaries_audit.json]
file copy [info script] [file join $b_out synthesize_frontier_service.tcl]
set b_previous_directory [pwd]
cd [file join $b_out sources]
puts "FRONTIER_SERVICE_SYNTH_BEGIN version=[version -short]"
set_param general.maxThreads 2
create_project -in_memory -part xcu280-fsvh2892-2L-e
foreach b_file [glob [file join $b_out sources *.v]] {read_verilog $b_file}
read_verilog -sv [file join $b_out sources frontier_hls_call.sv]
read_verilog -sv [file join $b_out sources frontier_service.sv]
set b_f [open [file join $b_out research_clock.xdc] w]
puts $b_f {create_clock -name research_clock -period 10.000 [get_ports clk]}
close $b_f
read_xdc [file join $b_out research_clock.xdc]
synth_design -top frontier_service -part xcu280-fsvh2892-2L-e -mode out_of_context
report_utilization -file [file join $b_out utilization.rpt]
report_utilization -hierarchical -file [file join $b_out utilization_hierarchical.rpt]
report_drc -checks [get_drc_checks LUTLP-1] -file [file join $b_out combinational_loops.rpt]
check_timing -verbose -file [file join $b_out check_timing.rpt]
write_checkpoint [file join $b_out frontier_service.dcp]
close_project
cd $b_previous_directory
puts "FRONTIER_SERVICE_SYNTH_DONE"
