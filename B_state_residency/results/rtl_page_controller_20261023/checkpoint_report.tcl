set_param general.maxThreads 2
open_checkpoint ./project/b_page_controller.runs/synth_1/scratch_page_controller.dcp
report_utilization -file utilization.rpt
set b_rams [get_cells -hier -filter {REF_NAME =~ RAMB*}]
set b_file [open ram_cells.txt w]
foreach b_cell $b_rams {puts $b_file "$b_cell [get_property REF_NAME $b_cell]"}
close $b_file
if {[llength $b_rams] != 2} {error "Expected exactly two block RAM primitives"}
puts "B_CONTROLLER_REPORT_PASS ram_cells=[llength $b_rams]"
exit
