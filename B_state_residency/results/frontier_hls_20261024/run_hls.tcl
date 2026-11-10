set frontier_out [file normalize [file dirname [info script]]]
set frontier_src [file join $frontier_out rearchitect v1 src]
set frontier_tb [file join $frontier_out rearchitect v1 tb]
puts "FRONTIER_HLS_BEGIN version=[version -short]"
open_project -reset [file join $frontier_out frontier_step]
set_top frontier_step
add_files [file join $frontier_src kernel_hls.cpp] -cflags "-std=c++14 -fno-fast-math -I$frontier_src"
add_files -tb [file join $frontier_tb testbench.cpp] -cflags "-std=c++14 -fno-fast-math -I$frontier_src -I$frontier_tb"
open_solution -reset solution1 -flow_target vivado
set_part {xcu280-fsvh2892-2L-e}
create_clock -period 10.000 -name default
puts "FRONTIER_CSIM_BEGIN"
csim_design -clean
set frontier_fd [open [file join $frontier_out csim_completed.txt] w]
puts $frontier_fd "FRONTIER_CSIM_DONE"
close $frontier_fd
puts "FRONTIER_CSYNTH_BEGIN"
csynth_design
set frontier_fd [open [file join $frontier_out csynth_completed.txt] w]
puts $frontier_fd "FRONTIER_CSYNTH_DONE"
close $frontier_fd
if {![file isdirectory [file join $frontier_out frontier_step solution1 syn]]} {error "Missing synthesis output before cosim"}
puts "FRONTIER_COSIM_BEGIN argv_empty_allowed=1"
cosim_design -rtl verilog -tool xsim -trace_level none
set frontier_fd [open [file join $frontier_out cosim_completed.txt] w]
puts $frontier_fd "FRONTIER_COSIM_DONE"
close $frontier_fd
close_project
puts "FRONTIER_HLS_DONE"
exit
