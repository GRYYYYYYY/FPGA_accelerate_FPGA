set source_dir [file normalize $::env(A_SEARCH_KERNEL_SOURCE)]
set project [file normalize $::env(A_SEARCH_KERNEL_PROJECT)]
set mode $::env(A_SEARCH_KERNEL_MODE)
if {$mode ni {0 1}} {error "Invalid graph mode"}
if {[file exists $project]} {error "Refusing existing project"}
cd [file dirname $project]
open_project [file tail $project]
set_top search_kernel_top
set flags "-std=c++14 -DSEARCH_GRAPH_MODE=$mode"
add_files $source_dir/search_kernel_top.cpp -cflags $flags
add_files -tb $source_dir/test_search_kernel_top.cpp -cflags $flags
open_solution solution -flow_target vitis
set_part {xcu280-fsvh2892-2L-e}
create_clock -period 5 -name default
# Local 2022.2 help confirms the option. Keep the initial complete controller
# sequential; inspect synthesis logs for unexpected automatic pipelining.
config_compile -pipeline_loops 0
csim_design
puts SEARCH_KERNEL_CSIM_COMPLETE
csynth_design
if {![file exists $project/solution/syn/report/search_kernel_top_csynth.xml]} {error "Missing synthesis report"}
puts SEARCH_KERNEL_SYNTHESIS_COMPLETE
# No arguments for either simulation; identical full-capacity 2-call testbench.
cosim_design -rtl verilog
puts SEARCH_KERNEL_FLOW_COMPLETE
exit
