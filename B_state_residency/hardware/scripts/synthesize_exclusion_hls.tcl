set b_root [file normalize [file join [file dirname [info script]] ../..]]
set b_gate [file join $b_root results exclusion_hls_20261024 source_bound_audit.json]
if {![file exists $b_gate]} {error "Exclusion RTL cosim independent audit required"}
set b_out [file join $b_root results exclusion_hls_vivado_synthesis_20261024]
if {[file exists $b_out]} {error "Result directory already exists; no overwrite or retry"}
file mkdir $b_out
set b_src [file join $b_root results exclusion_hls_20261024 gen32 exclusion_step solution1 syn verilog]
file copy $b_src [file join $b_out sources]
file copy $b_gate [file join $b_out hls_source_bound_audit.json]
file copy [info script] [file join $b_out synthesize_frontier_hls.tcl]
set b_previous_directory [pwd]
cd [file join $b_out sources]
set_param general.maxThreads 2
puts "EXCLUSION_VIVADO_SYNTH_BEGIN version=[version -short]"
create_project -in_memory -part xcu280-fsvh2892-2L-e
foreach b_file [glob [file join $b_out sources *.v]] {read_verilog $b_file}
set b_clock [open [file join $b_out research_clock.xdc] w]
puts $b_clock {create_clock -name research_clock -period 10.000 [get_ports ap_clk]}
close $b_clock
read_xdc [file join $b_out research_clock.xdc]
synth_design -top exclusion_step -part xcu280-fsvh2892-2L-e -mode out_of_context
report_utilization -file [file join $b_out utilization.rpt]
report_utilization -hierarchical -file [file join $b_out utilization_hierarchical.rpt]
write_checkpoint [file join $b_out exclusion_step.dcp]
set b_file [open [file join $b_out ram_cells.txt] w]
foreach b_cell [get_cells -hier -filter {REF_NAME =~ RAMB* || REF_NAME =~ URAM*}] {puts $b_file "$b_cell [get_property REF_NAME $b_cell]"}
close $b_file
set b_file [open [file join $b_out completed.txt] w]
puts $b_file "EXCLUSION_VIVADO_SYNTH_DONE version=[version -short]"
close $b_file
close_project
cd $b_previous_directory
puts "EXCLUSION_VIVADO_SYNTH_DONE"
