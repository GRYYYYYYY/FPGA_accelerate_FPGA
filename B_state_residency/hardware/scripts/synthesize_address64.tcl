set b_root [file normalize [file join [file dirname [info script]] ../..]]
set b_out [file join $b_root results address64_synthesis_20261024]
set_param general.maxThreads 2
puts "ADDRESS64_SYNTH_BEGIN version=[version -short]"
create_project -in_memory -part xcu280-fsvh2892-2L-e
foreach b_module {bounded_sync_fifo response_fallthrough_fifo scratch_frame_store_bram scratch_page_controller_small queued_scratch_endpoint_small scratch_page_axi_small backing_frame_directory_small backing_page_service_small scratch_page_codec_small_static record_backing_service_small_staticcodec memory_scratch_endpoint_small_staticcodec backing_base_config memory_scratch_endpoint_address64} {
    read_verilog -sv [file join $b_out sources ${b_module}.sv]
}
read_xdc [file join $b_out research_clock.xdc]
synth_design -top memory_scratch_endpoint_address64 -part xcu280-fsvh2892-2L-e -mode out_of_context -generic EPOCH_BITS=6
report_utilization -file [file join $b_out utilization.rpt]
report_utilization -hierarchical -file [file join $b_out utilization_hierarchical.rpt]
write_checkpoint -force [file join $b_out memory_scratch_endpoint_address64.dcp]
set b_file [open [file join $b_out ram_cells.txt] w]
foreach b_cell [get_cells -hier -filter {REF_NAME =~ RAMB*}] {puts $b_file "$b_cell [get_property REF_NAME $b_cell]"}
close $b_file
set b_file [open [file join $b_out completed.txt] w]
puts $b_file "ADDRESS64_SYNTH_DONE version=[version -short]"
close $b_file
close_project
puts "ADDRESS64_SYNTH_DONE"
