set center_out [file normalize [file dirname [info script]]]
set center_src [file join $center_out sources hls cost_center v1]
cd $center_out
puts "COST_CENTER_HLS_BEGIN version=[version -short]"
open_project -reset cost_center_step
set_top cost_center_step
add_files [file join $center_src kernel.cpp] -cflags "-std=c++14 -I$center_src"
add_files -tb [file join $center_src rtl_testbench.cpp] -cflags "-std=c++14 -I$center_src"
add_files -tb [file join $center_out vectors.txt]
open_solution -reset solution1 -flow_target vivado
set_part {xcu280-fsvh2892-2L-e}
create_clock -period 10.000 -name default
csim_design -clean
file copy [file join $center_out cost_center_step solution1 csim build observed.txt] [file join $center_out csim_observed.txt]
csynth_design
if {![file isdirectory [file join $center_out cost_center_step solution1 syn]]} {error "Missing synthesis before cosim"}
cosim_design -rtl verilog -tool xsim -trace_level none
close_project
puts "COST_CENTER_HLS_DONE"
exit
