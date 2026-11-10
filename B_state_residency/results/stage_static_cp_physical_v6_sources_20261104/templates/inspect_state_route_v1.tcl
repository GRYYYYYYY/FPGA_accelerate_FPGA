# A separate Vivado process independently reopens the recovered routed DCP.
set state_out {@OUT@}
cd $state_out
if {[version -short] ne "2022.2"} {error "Expected matched Vivado 2022.2"}
set_param general.maxThreads 2
open_checkpoint routed.dcp
if {[get_property PART [current_design]] ne "xcu280-fsvh2892-2L-e"} {error "Unexpected part"}
if {[llength [get_clocks]]!=1 || [get_property PERIOD [get_clocks core_clk]]!=10.0} {error "Unexpected clock"}
report_route_status -file inspection/route_status.rpt
report_utilization -file inspection/utilization.rpt
report_timing_summary -check_timing_verbose -report_unconstrained -max_paths 10 -file inspection/timing.rpt
report_methodology -no_waivers -file inspection/methodology.rpt
report_drc -no_waivers -file inspection/drc.rpt
check_timing -verbose -file inspection/check_timing.rpt
write_xdc -exclude_physical inspection/constraints.xdc
puts STATE_ROUTE_RECOVERY_REOPENED
close_project
