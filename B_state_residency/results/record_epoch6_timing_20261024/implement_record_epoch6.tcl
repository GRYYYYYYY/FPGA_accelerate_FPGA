# Frozen default-capacity candidate; paired against existing static-codec epoch6 OOC route.
set b_root [file normalize [file join [file dirname [info script]] ../..]]
set b_out [file join $b_root results record_epoch6_timing_20261024]
set_param general.maxThreads 2
puts "RECORD_EPOCH6_TIMING_BEGIN version=[version -short]"
open_checkpoint [file join $b_root results record_epoch6_synthesis_20261024 memory_scratch_endpoint_small_staticcodec.dcp]
if {[get_property PART [current_design]] ne "xcu280-fsvh2892-2L-e"} {error "Wrong part"}
if {[llength [get_clocks]] != 1 || [get_property PERIOD [get_clocks core_clk]] != 10.0} {error "Wrong clock"}
write_xdc -exclude_physical [file join $b_out constraints_before.xdc]
report_methodology -file [file join $b_out methodology_synth.rpt]
report_timing_summary -check_timing_verbose -report_unconstrained -max_paths 5 -file [file join $b_out timing_synth.rpt]
opt_design
place_design -directive Default
write_checkpoint [file join $b_out placed.dcp]
route_design -directive Default
report_route_status -file [file join $b_out route_status.rpt]
report_timing_summary -check_timing_verbose -report_unconstrained -max_paths 10 -file [file join $b_out timing_routed.rpt]
report_methodology -file [file join $b_out methodology_routed.rpt]
report_drc -file [file join $b_out drc_routed.rpt]
report_utilization -file [file join $b_out utilization_routed.rpt]
report_utilization -hierarchical -file [file join $b_out utilization_hierarchical.rpt]
write_xdc -exclude_physical [file join $b_out constraints_after.xdc]
write_checkpoint [file join $b_out routed.dcp]
set b_metrics [open [file join $b_out internal_paths.tsv] w]
puts $b_metrics "delay_type\tslack_ns\tstartpoint\tendpoint\tdatapath_delay_ns\trequirement_ns"
foreach b_delay {max min} {
 set b_paths [get_timing_paths -from [get_clocks core_clk] -to [get_clocks core_clk] -delay_type $b_delay -max_paths 10]
 if {[llength $b_paths]==0} {error "No internal timing paths"}
 foreach b_path $b_paths {puts $b_metrics "$b_delay\t[get_property SLACK $b_path]\t[get_property STARTPOINT_PIN $b_path]\t[get_property ENDPOINT_PIN $b_path]\t[get_property DATAPATH_DELAY $b_path]\t[get_property REQUIREMENT $b_path]"}
}
close $b_metrics
set b_done [open [file join $b_out completed.txt] w]
puts $b_done "RECORD_EPOCH6_TIMING_DONE version=[version -short] part=[get_property PART [current_design]] period=[get_property PERIOD [get_clocks core_clk]]"
close $b_done
close_design
puts "RECORD_EPOCH6_TIMING_DONE"
