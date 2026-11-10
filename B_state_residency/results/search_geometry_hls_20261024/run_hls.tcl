set geo_out [file normalize [file dirname [info script]]]
set geo_src [file join $geo_out sources]
cd $geo_out
puts "GEOMETRY_HLS_BEGIN version=[version -short]"
open_project -reset geometry_step
set_top geometry_step
add_files [file join $geo_src kernel.cpp] -cflags "-std=c++14 -I$geo_src"
add_files -tb [file join $geo_src testbench.cpp] -cflags "-std=c++14 -I$geo_src"
add_files -tb [file join $geo_out vectors.txt]
open_solution -reset solution1 -flow_target vivado
set_part {xcu280-fsvh2892-2L-e}
create_clock -period 10.000 -name default
csim_design -clean
file copy [file join $geo_out geometry_step solution1 csim build observed.txt] [file join $geo_out csim_observed.txt]
csynth_design
if {![file isdirectory [file join $geo_out geometry_step solution1 syn]]} {error "Missing synthesis before cosim"}
cosim_design -rtl verilog -tool xsim -trace_level none
close_project
puts "GEOMETRY_HLS_DONE"
exit
