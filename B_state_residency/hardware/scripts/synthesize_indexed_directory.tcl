set b_root [file normalize [file join [file dirname [info script]] ../..]]
set b_evidence [file join $b_root results rtl_indexed_directory_20261023]
set_param general.maxThreads 2
puts "B_INDEXED_SYNTH_BEGIN version=[version -short]"
foreach b_variant {lookup indexed} {
    create_project -in_memory -part xcu280-fsvh2892-2L-e
    read_verilog -sv [file join $b_evidence sources backing_frame_directory_${b_variant}.sv]
    synth_design -top backing_frame_directory_${b_variant} -part xcu280-fsvh2892-2L-e -mode out_of_context
    create_clock -name core_clk -period 10.000 [get_ports clk]
    report_utilization -file [file join $b_evidence synthesis ${b_variant}_utilization.rpt]
    report_timing_summary -report_unconstrained -check_timing_verbose -file [file join $b_evidence synthesis ${b_variant}_timing.rpt]
    write_checkpoint -force [file join $b_evidence synthesis ${b_variant}.dcp]
    close_project
}
puts "B_INDEXED_SYNTH_DONE"
