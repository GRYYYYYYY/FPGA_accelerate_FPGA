# Recover only routing from the exact saved CP placement. Keep original constraints.
set state_out {/tmp/B_state_residency_offer_20261025/checkpoint_edit_route_recovery_v1}
cd $state_out
if {[version -short] ne "2022.2"} {error "Expected matched Vivado 2022.2"}
set_param general.maxThreads 2
config_webtalk -info
set state_maps [open /proc/[pid]/maps r]
set state_copy [open runtime_maps.txt w]
puts $state_copy [read $state_maps]
close $state_maps
close $state_copy
set state_flow [open milestones.txt w]
puts $state_flow "RESUME_PLACED version=[version -short]"
flush $state_flow
open_checkpoint inputs/resume_placed.dcp
if {[get_property PART [current_design]] ne "xcu280-fsvh2892-2L-e"} {error "Unexpected part"}
if {[llength [get_clocks]] != 1 || [llength [get_clocks core_clk]] != 1} {error "Expected only core_clk"}
if {[get_property PERIOD [get_clocks core_clk]] != 10.0} {error "Expected original 10ns clock"}
report_clocks -file clocks_resume.rpt
report_utilization -file utilization_resume.rpt
report_timing_summary -check_timing_verbose -report_unconstrained -max_paths 10 -file timing_resume.rpt
write_xdc -exclude_physical constraints_resume.xdc
puts $state_flow "ROUTE [clock seconds]"
flush $state_flow
route_design -directive Default
write_checkpoint routed.dcp
report_route_status -file route_status.rpt
report_utilization -file utilization_routed.rpt
report_utilization -hierarchical -file utilization_routed_hier.rpt
report_methodology -no_waivers -file methodology_routed.rpt
report_drc -no_waivers -file drc_routed.rpt
report_drc -no_waivers -checks [get_drc_checks LUTLP-1] -file loops_routed.rpt
check_timing -verbose -file check_timing_routed.rpt
report_clocks -file clocks_routed.rpt
report_timing_summary -check_timing_verbose -report_unconstrained -max_paths 10 -file timing_routed.rpt
write_xdc -exclude_physical constraints_routed.xdc
set state_paths [open internal_paths.tsv w]
puts $state_paths [join {delay_type slack_ns startpoint endpoint datapath_delay_ns requirement_ns} "\t"]
foreach state_dtype {max min} {
    set state_found [get_timing_paths -from [get_clocks core_clk] -to [get_clocks core_clk] -delay_type $state_dtype -max_paths 10]
    if {[llength $state_found] != 10} {error "Expected ten internal timing paths"}
    foreach state_path $state_found {
        puts $state_paths [join [list $state_dtype [get_property SLACK $state_path] [get_property STARTPOINT_PIN $state_path] [get_property ENDPOINT_PIN $state_path] [get_property DATAPATH_DELAY $state_path] [get_property REQUIREMENT $state_path]] "\t"]
    }
}
close $state_paths
set state_done [open completed.txt w]
puts $state_done "STATE_ROUTE_RECOVERY_DONE version=[version -short] part=[get_property PART [current_design]] period=[get_property PERIOD [get_clocks core_clk]]"
close $state_done
puts $state_flow "STATE_ROUTE_RECOVERY_DONE [clock seconds]"
close $state_flow
puts STATE_ROUTE_RECOVERY_DONE
close_project
