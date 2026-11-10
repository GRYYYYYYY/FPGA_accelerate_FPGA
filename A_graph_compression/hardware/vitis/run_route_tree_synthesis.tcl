# Local Vivado/Vitis HLS 2022.2 flow; no Unified-IDE/newer commands.
set source_dir [file normalize $::env(A_ROUTE_TREE_SOURCE)]
set project [file normalize $::env(A_ROUTE_TREE_PROJECT)]
if {[file exists $project]} {error "Refusing existing route tree project"}
cd [file dirname $project]
open_project [file tail $project]
set_top search_route_tree_top
add_files $source_dir/search_route_tree_top.cpp -cflags "-std=c++14"
add_files -tb $source_dir/test_search_route_tree.cpp -cflags "-std=c++14"
open_solution solution -flow_target vitis
set_part {xcu280-fsvh2892-2L-e}
create_clock -period 5 -name default
set_clock_uncertainty 1.35
csim_design
puts ROUTE_TREE_CSIM_COMPLETE
csynth_design
if {![file exists $project/solution/syn/report/search_route_tree_top_csynth.xml]} {error "Missing tree synthesis report"}
puts ROUTE_TREE_SYNTHESIS_COMPLETE
exit
