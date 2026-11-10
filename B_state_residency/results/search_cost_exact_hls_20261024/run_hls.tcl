set cost_out [file normalize [file dirname [info script]]]
set cost_src [file join $cost_out sources]
cd $cost_out
puts "COST_HLS_BEGIN version=[version -short]"
open_project -reset cost_step
set_top cost_step
add_files [file join $cost_src kernel.cpp] -cflags "-std=c++14 -fno-fast-math -ffp-contract=off -I$cost_src"
add_files -tb [file join $cost_src testbench.cpp] -cflags "-std=c++14 -fno-fast-math -ffp-contract=off -I$cost_src"
add_files -tb [file join $cost_out vectors.txt]
open_solution -reset solution1 -flow_target vivado
set_part {xcu280-fsvh2892-2L-e}
create_clock -period 10.000 -name default
csim_design -clean
file copy [file join $cost_out cost_step solution1 csim build observed.txt] [file join $cost_out csim_observed.txt]
puts "COST_CSIM_DONE"
csynth_design
if {![file isdirectory [file join $cost_out cost_step solution1 syn]]} {error "Missing synthesis before cosim"}
puts "COST_CSYNTH_DONE"
cosim_design -rtl verilog -tool xsim -trace_level none
puts "COST_COSIM_DONE"
close_project
puts "COST_HLS_DONE"
exit
