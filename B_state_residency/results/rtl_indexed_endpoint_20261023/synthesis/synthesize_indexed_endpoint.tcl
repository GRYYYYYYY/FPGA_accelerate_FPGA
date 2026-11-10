set b_root [file normalize [file join [file dirname [info script]] ../..]]
set b_evidence [file join $b_root results rtl_indexed_endpoint_20261023]
set_param general.maxThreads 2
puts "B_INDEXED_ENDPOINT_SYNTH_BEGIN version=[version -short]"
create_project -in_memory -part xcu280-fsvh2892-2L-e
foreach b_module {bounded_sync_fifo scratch_frame_store_bram scratch_page_controller queued_scratch_endpoint scratch_page_axi backing_frame_directory_indexed backing_page_service_indexed scratch_page_codec_wide record_backing_service_indexed memory_scratch_endpoint_indexed} {
    read_verilog -sv [file join $b_evidence sources hardware rtl ${b_module}.sv]
}
set b_xdc [file join $b_evidence synthesis research_clock.xdc]
set b_file [open $b_xdc w]
puts $b_file {create_clock -name core_clk -period 10.000 [get_ports clk]}
close $b_file
read_xdc $b_xdc
synth_design -top memory_scratch_endpoint_indexed -part xcu280-fsvh2892-2L-e -mode out_of_context
report_utilization -file [file join $b_evidence synthesis utilization.rpt]
report_utilization -hierarchical -file [file join $b_evidence synthesis utilization_hierarchical.rpt]
write_checkpoint -force [file join $b_evidence synthesis memory_scratch_endpoint_indexed.dcp]
set b_rams [get_cells -hier -filter {REF_NAME =~ RAMB*}]
set b_file [open [file join $b_evidence synthesis ram_cells.txt] w]
foreach b_cell $b_rams {puts $b_file "$b_cell [get_property REF_NAME $b_cell]"}
close $b_file
close_project
puts "B_INDEXED_ENDPOINT_SYNTH_DONE"
