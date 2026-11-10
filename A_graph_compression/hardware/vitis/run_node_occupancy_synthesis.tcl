# 2022.2 Tcl equivalent of the Ross HLS csim/csynth workflow.
set source_dir [file normalize $::env(A_NODE_OCCUPANCY_SOURCE)]
set project [file normalize $::env(A_NODE_OCCUPANCY_PROJECT)]
if {[file exists $project]} {error "Refusing existing occupancy HLS project"}
cd [file dirname $project]
open_project [file tail $project]
set_top search_node_occupancy_top
add_files $source_dir/search_node_occupancy_top.cpp -cflags "-std=c++14"
add_files -tb $source_dir/test_search_node_occupancy.cpp -cflags "-std=c++14"
open_solution solution -flow_target vitis
set_part {xcu280-fsvh2892-2L-e}
create_clock -period 5 -name default
set_clock_uncertainty 1.35
csim_design
puts NODE_OCCUPANCY_CSIM_COMPLETE
csynth_design
if {![file exists $project/solution/syn/report/search_node_occupancy_top_csynth.xml]} {error "Missing occupancy synthesis report"}
# Full C/RTL replay is a subsequent task; csim uses a CPU-only randomized
# oracle and includes a million-node update. No RTL success is implied here.
puts NODE_OCCUPANCY_SYNTHESIS_COMPLETE
exit
