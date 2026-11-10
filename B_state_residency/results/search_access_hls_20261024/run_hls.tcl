set acc_out [file normalize [file dirname [info script]]]
set acc_src [file join $acc_out sources]
cd $acc_out
puts "ACCESS_HLS_BEGIN version=[version -short]"
open_project -reset access_step
set_top access_step
add_files [file join $acc_src kernel.cpp] -cflags "-std=c++14 -I$acc_src"
add_files -tb [file join $acc_src testbench.cpp] -cflags "-std=c++14 -I$acc_src"
add_files -tb [file join $acc_out vectors.txt]
open_solution -reset solution1 -flow_target vivado
set_part {xcu280-fsvh2892-2L-e}
create_clock -period 10.000 -name default
csim_design -clean
file copy [file join $acc_out access_step solution1 csim build observed.txt] [file join $acc_out csim_observed.txt]
csynth_design
if {![file isdirectory [file join $acc_out access_step solution1 syn]]} {error "Missing synthesis before cosim"}
cosim_design -rtl verilog -tool xsim -trace_level none
close_project
puts "ACCESS_HLS_DONE"
exit
