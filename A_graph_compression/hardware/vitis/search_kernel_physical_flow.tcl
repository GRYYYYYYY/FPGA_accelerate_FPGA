# Vivado2022.2 non-project OOC characterization of unchanged production RTL.
# Source only in the dedicated, otherwise idle MCP session for this mode.
set a_root [file dirname [file normalize [info script]]]
set a_mode [file tail $a_root]
if {$a_mode ni {csr compact}} {error "Unexpected mode directory"}
if {[file exists $a_root/state.json]} {error "Refusing to repeat an existing physical flow"}
set a_stage prepare
proc a_publish {status} {
    global a_root a_mode a_stage
    set f [open $a_root/state.tmp w]
    puts $f [format {{"owner_pid":%d,"status":"%s","stage":"%s","mode":"%s","updated_utc":"%s"}} [pid] $status $a_stage $a_mode [clock format [clock seconds] -gmt 1 -format {%Y-%m-%dT%H:%M:%SZ}]]
    close $f
    file rename -force $a_root/state.tmp $a_root/state.json
    puts [list SEARCH_PHYSICAL_STAGE $a_mode $status $a_stage]
    flush stdout
}
proc a_reports {stage} {
    global a_root
    report_utilization -hierarchical -file $a_root/reports/${stage}_utilization.rpt
    report_timing_summary -delay_type min_max -report_unconstrained -check_timing_verbose -max_paths 10 -file $a_root/reports/${stage}_timing.rpt
    check_timing -file $a_root/reports/${stage}_check_timing.rpt
    report_methodology -file $a_root/reports/${stage}_methodology.rpt
    report_drc -file $a_root/reports/${stage}_drc.rpt
    write_xdc -exclude_physical $a_root/reports/${stage}_timing.xdc
    set f [open $a_root/reports/${stage}_methodology_properties.tcllist w]
    foreach violation [get_methodology_violations -quiet] {
        foreach property [list_property $violation] {
            puts $f [list $violation $property [get_property $property $violation]]
        }
    }
    close $f
    set setup [get_timing_paths -delay_type max -max_paths 1]
    set hold [get_timing_paths -delay_type min -max_paths 1]
    if {[llength $setup] != 1 || [llength $hold] != 1} {error "No meaningful internal timing paths"}
    set f [open $a_root/reports/${stage}_summary.tcllist w]
    puts $f [list version [version -short] part [get_property PART [current_design]] clock_period [get_property PERIOD [get_clocks ap_clk]] setup_slack [get_property SLACK $setup] hold_slack [get_property SLACK $hold] cells [llength [get_cells -hierarchical]]]
    close $f
}
a_publish running
set a_code [catch {
    if {[version -short] ne "2022.2"} {error "This flow is pinned to validated Vivado2022.2 commands"}
    if {[current_design -quiet] ne "" || [current_project -quiet] ne ""} {error "Dedicated empty session required"}
    set_param general.maxThreads 2
    file mkdir $a_root/reports
    cd $a_root/source
    create_project -in_memory search_physical_$a_mode -part xcu280-fsvh2892-2L-e
    read_verilog [lsort [glob $a_root/source/*.v]]
    read_xdc $a_root/clock.xdc
    set a_stage synthesis
    a_publish running
    synth_design -top search_kernel_top -part xcu280-fsvh2892-2L-e -mode out_of_context
    write_checkpoint $a_root/synthesized.dcp
    set a_stage synthesis_reports
    a_publish running
    a_reports synthesis
    set a_stage optimization
    a_publish running
    opt_design
    set a_stage placement
    a_publish running
    place_design
    phys_opt_design
    write_checkpoint $a_root/placed.dcp
    set a_stage routing
    a_publish running
    route_design
    write_checkpoint $a_root/routed.dcp
    set a_stage routed_reports
    a_publish running
    report_route_status -file $a_root/reports/route_status.rpt
    a_reports routed
    set a_stage ooc_complete_pending_independent_audit
    a_publish complete
    puts SEARCH_PHYSICAL_FLOW_COMPLETE
} a_error a_options]
if {$a_code} {
    a_publish failed
    set f [open $a_root/error.txt w]
    puts $f $a_error
    puts $f [dict get $a_options -errorinfo]
    close $f
    return -options $a_options $a_error
}
