# Vivado 2022.2: implement a copied, audited complete-system OOC checkpoint.
# Retain its research clock and all original constraints. No I/O budgets or waivers.
set state_out {/tmp/B_state_residency_offer_20261025/checkpoint_edit_physical_v1}
cd $state_out
set_param general.maxThreads 2
set state_flow [open [file join $state_out milestones.txt] w]
puts $state_flow "BEGIN version=[version -short]"
flush $state_flow
if {[version -short] ne "2022.2"} {error "Expected matched Vivado 2022.2"}
open_checkpoint [file join $state_out inputs synthesized.dcp]
if {[get_property PART [current_design]] ne "xcu280-fsvh2892-2L-e"} {error "Unexpected part"}
if {[llength [get_clocks]] != 1 || [llength [get_clocks core_clk]] != 1} {error "Expected only core_clk"}
if {[get_property PERIOD [get_clocks core_clk]] != 10.0} {error "Expected original 10ns clock"}

report_clocks -file [file join $state_out clocks_input.rpt]
report_utilization -file [file join $state_out utilization_input.rpt]
report_methodology -no_waivers -file [file join $state_out methodology_input.rpt]
check_timing -verbose -file [file join $state_out check_timing_input.rpt]
report_drc -no_waivers -checks [get_drc_checks LUTLP-1] -file [file join $state_out loops_input.rpt]
write_xdc -exclude_physical [file join $state_out constraints_input.xdc]
puts $state_flow "OPT [clock seconds]"; flush $state_flow
opt_design
write_checkpoint [file join $state_out optimized.dcp]
puts $state_flow "PLACE [clock seconds]"; flush $state_flow
place_design -directive Default
write_checkpoint [file join $state_out placed.dcp]
report_utilization -file [file join $state_out utilization_placed.rpt]
report_timing_summary -check_timing_verbose -report_unconstrained -max_paths 10 -file [file join $state_out timing_placed.rpt]
puts $state_flow "ROUTE [clock seconds]"; flush $state_flow
route_design -directive Default
write_checkpoint [file join $state_out routed.dcp]
report_route_status -file [file join $state_out route_status.rpt]
report_utilization -file [file join $state_out utilization_routed.rpt]
report_utilization -hierarchical -file [file join $state_out utilization_routed_hier.rpt]
report_methodology -no_waivers -file [file join $state_out methodology_routed.rpt]
report_drc -no_waivers -file [file join $state_out drc_routed.rpt]
report_drc -no_waivers -checks [get_drc_checks LUTLP-1] -file [file join $state_out loops_routed.rpt]
check_timing -verbose -file [file join $state_out check_timing_routed.rpt]
report_clocks -file [file join $state_out clocks_routed.rpt]
report_timing_summary -check_timing_verbose -report_unconstrained -max_paths 10 -file [file join $state_out timing_routed.rpt]
write_xdc -exclude_physical [file join $state_out constraints_routed.xdc]
set state_paths [open [file join $state_out internal_paths.tsv] w]
puts $state_paths [join {delay_type slack_ns startpoint endpoint datapath_delay_ns requirement_ns} "\t"]
foreach state_dtype {max min} {
    set state_found [get_timing_paths -from [get_clocks core_clk] -to [get_clocks core_clk] -delay_type $state_dtype -max_paths 10]
    if {[llength $state_found] == 0} {error "No constrained internal timing paths"}
    foreach state_path $state_found {
        puts $state_paths [join [list $state_dtype [get_property SLACK $state_path] [get_property STARTPOINT_PIN $state_path] [get_property ENDPOINT_PIN $state_path] [get_property DATAPATH_DELAY $state_path] [get_property REQUIREMENT $state_path]] "\t"]
    }
}
close $state_paths
set state_done [open [file join $state_out completed.txt] w]
puts $state_done "STATE_FULL_PHYSICAL_DONE version=[version -short] part=[get_property PART [current_design]] period=[get_property PERIOD [get_clocks core_clk]]"
close $state_done
puts $state_flow "STATE_FULL_PHYSICAL_DONE [clock seconds]"
close $state_flow
puts STATE_FULL_PHYSICAL_DONE
close_project
