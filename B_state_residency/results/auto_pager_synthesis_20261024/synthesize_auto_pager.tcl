set b_root [file normalize [file join [file dirname [info script]] ../..]]
puts [exec python3 [file join $b_root scripts/audit_auto_pager.py] 2>@1]
set b_verified [file join $b_root results auto_pager_20261024]
set b_out [file join $b_root results auto_pager_synthesis_20261024]
if {[file exists $b_out]} {error "Preserve existing result directory"}
file mkdir $b_out
file copy [file join $b_verified sources] [file join $b_out sources]
file copy [file join $b_verified source_bound_audit.json] [file join $b_out simulation_audit.json]
file copy [info script] [file join $b_out synthesize_auto_pager.tcl]
puts "AUTO_PAGER_SYNTH_BEGIN version=[version -short]"
set_param general.maxThreads 2
create_project -in_memory -part xcu280-fsvh2892-2L-e
foreach b_file [glob [file join $b_out sources hls32 *.v]] {read_verilog $b_file}
foreach b_file [glob [file join $b_out sources backend *.sv]] {read_verilog -sv $b_file}
read_verilog -sv [file join $b_out sources adapter exclusion_label_adapter.sv]
foreach b_name {exclusion_hls_call.sv exclusion_edge_controller.sv exclusion_edge_engine.sv} {
    read_verilog -sv [file join $b_out sources engine $b_name]
}
foreach b_name {resident_page_manager.sv paged_exclusion_engine.sv} {
    read_verilog -sv [file join $b_out sources pager $b_name]
}
set b_f [open [file join $b_out research_clock.xdc] w]
puts $b_f {create_clock -name research_clock -period 10.000 [get_ports clk]}
close $b_f
read_xdc [file join $b_out research_clock.xdc]
synth_design -top paged_exclusion_engine -part xcu280-fsvh2892-2L-e -mode out_of_context
report_utilization -file [file join $b_out utilization.rpt]
report_drc -checks [get_drc_checks LUTLP-1] -file [file join $b_out combinational_loops.rpt]
check_timing -verbose -file [file join $b_out check_timing.rpt]
write_checkpoint [file join $b_out paged_exclusion_engine.dcp]
set b_f [open [file join $b_out completed.txt] w]
puts $b_f "AUTO_PAGER_SYNTH_DONE version=[version -short]"
close $b_f
close_project
puts "AUTO_PAGER_SYNTH_DONE"
