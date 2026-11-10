# Portable non-project OOC rebuild. No project, IP or prior DCP required.
set candidate_root [file normalize [file join [file dirname [info script]] ..]]
if {![info exists candidate_output]} {
    if {[llength $argv]!=1} {error "Usage: vivado -mode batch -source Scripts/synth.tcl -tclargs NEW_OUTPUT"}
    set candidate_output [file normalize [lindex $argv 0]]
}
if {[file exists $candidate_output]} {error "Refuse to overwrite candidate rebuild output"}
file mkdir $candidate_output
set_param general.maxThreads 2
puts "RESIDENCY_CANDIDATE_REBUILD_BEGIN version=[version -short]"
create_project -in_memory -part xcu280-fsvh2892-2L-e
foreach candidate_module {bounded_sync_fifo response_fallthrough_fifo scratch_frame_store_bram scratch_page_controller_small queued_scratch_endpoint_small scratch_page_axi_small backing_frame_directory_small backing_page_service_small scratch_page_codec_small_static record_backing_service_small_staticcodec memory_scratch_endpoint_small_staticcodec} {
    read_verilog -sv [file join $candidate_root Sources RTL ${candidate_module}.sv]
}
read_xdc [file join $candidate_root Sources Constraints research_clock.xdc]
synth_design -top memory_scratch_endpoint_small_staticcodec -part xcu280-fsvh2892-2L-e -mode out_of_context -generic EPOCH_BITS=6
report_utilization -file [file join $candidate_output utilization.rpt]
report_utilization -hierarchical -file [file join $candidate_output utilization_hierarchical.rpt]
write_checkpoint [file join $candidate_output candidate.dcp]
set candidate_done [open [file join $candidate_output completed.txt] w]
puts $candidate_done "RESIDENCY_CANDIDATE_REBUILD_DONE version=[version -short]"
close $candidate_done
close_project
puts "RESIDENCY_CANDIDATE_REBUILD_DONE"
