set source_dir [file normalize $::env(A_SEARCH_HEAP_SOURCE)]
set project [file normalize $::env(A_SEARCH_HEAP_PROJECT)]
if {[file exists $project]} {error "Refusing existing project"}
cd [file dirname $project]
open_project [file tail $project]
set_top search_heap_top
add_files $source_dir/search_heap_top.cpp -cflags "-std=c++14"
add_files -tb $source_dir/test_search_heap_top.cpp -cflags "-std=c++14"
open_solution solution -flow_target vitis
set_part {xcu280-fsvh2892-2L-e}
create_clock -period 5 -name default
csim_design
csynth_design
if {![file exists $project/solution/syn/report/search_heap_top_csynth.xml]} {error "Missing synthesis report"}
# Testbench has no command-line inputs; csim/cosim argv are both empty.
cosim_design -rtl verilog
puts SEARCH_HEAP_FLOW_COMPLETE
exit
