# Compare already frozen OOC netlists; do not synthesize or alter constraints.
# Invoke with source from a Vivado 2022.2 Tcl session, with no project open.
set b_root [file normalize [file join [file dirname [info script]] ../..]]
set b_out [file join $b_root results rtl_small_codec_endpoint_timing_20261023]
set_param general.maxThreads 2
puts "B_SMALL_CODEC_TIMING_BEGIN version=[version -short]"
set b_help [open [file join $b_out help_2022_2.txt] w]
foreach b_cmd {report_methodology place_design route_design report_route_status get_timing_paths} {
    puts $b_help [help $b_cmd]
}
close $b_help
foreach {b_variant b_relative} {
    dynamic results/rtl_small_endpoint_synthesis_20261023/memory_scratch_endpoint_small.dcp
    static results/rtl_static_endpoint_synthesis_20261023/memory_scratch_endpoint_small_staticcodec.dcp
} {
    set b_dir [file join $b_out $b_variant]
    if {[file exists $b_dir]} {error "Refuse to overwrite timing evidence: $b_dir"}
    file mkdir $b_dir
    open_checkpoint [file join $b_root $b_relative]
    if {[get_property PART [current_design]] ne "xcu280-fsvh2892-2L-e"} {error "Wrong device"}
    if {[llength [get_clocks]] != 1 || [get_property PERIOD [get_clocks core_clk]] != 10.0} {error "Wrong clock"}
    write_xdc -exclude_physical [file join $b_dir constraints_before.xdc]
    report_methodology -file [file join $b_dir methodology_synth.rpt]
    report_timing_summary -check_timing_verbose -report_unconstrained -max_paths 5 -file [file join $b_dir timing_synth.rpt]
    puts "B_SMALL_CODEC_TIMING_OPT $b_variant"
    opt_design
    place_design -directive Default
    route_design -directive Default
    report_route_status -file [file join $b_dir route_status.rpt]
    report_timing_summary -check_timing_verbose -report_unconstrained -max_paths 10 -file [file join $b_dir timing_routed.rpt]
    report_methodology -file [file join $b_dir methodology_routed.rpt]
    report_drc -file [file join $b_dir drc_routed.rpt]
    report_utilization -file [file join $b_dir utilization_routed.rpt]
    report_utilization -hierarchical -file [file join $b_dir utilization_hierarchical.rpt]
    write_xdc -exclude_physical [file join $b_dir constraints_after.xdc]
    write_checkpoint [file join $b_dir routed.dcp]
    set b_metrics [open [file join $b_dir internal_paths.tsv] w]
    puts $b_metrics "delay_type\tslack_ns\tstartpoint\tendpoint\tdatapath_delay_ns\trequirement_ns"
    foreach b_delay {max min} {
        set b_paths [get_timing_paths -from [get_clocks core_clk] -to [get_clocks core_clk] -delay_type $b_delay -max_paths 10]
        if {[llength $b_paths] == 0} {error "No internal $b_delay timing paths"}
        foreach b_path $b_paths {
            puts $b_metrics "$b_delay\t[get_property SLACK $b_path]\t[get_property STARTPOINT_PIN $b_path]\t[get_property ENDPOINT_PIN $b_path]\t[get_property DATAPATH_DELAY $b_path]\t[get_property REQUIREMENT $b_path]"
        }
    }
    close $b_metrics
    set b_done [open [file join $b_dir completed.txt] w]
    puts $b_done "B_SMALL_CODEC_TIMING_VARIANT_DONE $b_variant version=[version -short] part=[get_property PART [current_design]] period=[get_property PERIOD [get_clocks core_clk]]"
    close $b_done
    puts "B_SMALL_CODEC_TIMING_VARIANT_DONE $b_variant"
    close_design
}
puts "B_SMALL_CODEC_TIMING_PAIR_DONE"
