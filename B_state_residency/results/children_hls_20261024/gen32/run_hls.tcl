set children_out [file normalize [file dirname [info script]]]
cd $children_out
puts "CHILDREN_HLS_BEGIN generation_bits=32 version=[version -short]"
open_project -reset children_step
set_top children_step
add_files {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/children_hls_20261024/rearchitect/v1/src/kernel_hls.cpp} -cflags {-std=c++14 -fno-fast-math -DCHILDREN_GENERATION_BITS=32 -I/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/children_hls_20261024/rearchitect/v1/src -I/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/children_hls_20261024/rearchitect/v1/tb}
add_files -tb {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/children_hls_20261024/rearchitect/v1/tb/testbench.cpp} -cflags {-std=c++14 -fno-fast-math -DCHILDREN_GENERATION_BITS=32 -I/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/children_hls_20261024/rearchitect/v1/src -I/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/children_hls_20261024/rearchitect/v1/tb}
open_solution -reset solution1 -flow_target vivado
set_part {xcu280-fsvh2892-2L-e}
create_clock -period 10.000 -name default
config_rtl -reset state
csim_design -clean
set f [open [file join $children_out csim_completed.txt] w]; puts $f CSIM_DONE; close $f
csynth_design
set f [open [file join $children_out csynth_completed.txt] w]; puts $f CSYNTH_DONE; close $f
if {![file isdirectory [file join $children_out children_step solution1 syn]]} {error "Missing synthesis before cosim"}
cosim_design -rtl verilog -tool xsim -trace_level none
set f [open [file join $children_out cosim_completed.txt] w]; puts $f COSIM_DONE; close $f
close_project
puts "CHILDREN_HLS_DONE generation_bits=32"
exit
