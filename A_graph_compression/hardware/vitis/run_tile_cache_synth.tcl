# Classic 2022.2: same baseline settings; one algorithmic tile-cache change.
foreach name {A_TILE_CACHE_SOURCE A_TILE_CACHE_PROJECT} {
    if {![info exists ::env($name)]} {error "Missing $name"}
}
set source_dir [file normalize $::env(A_TILE_CACHE_SOURCE)]
set project [file normalize $::env(A_TILE_CACHE_PROJECT)]
if {[file exists $project]} {error "Refusing existing project"}
cd [file dirname $project]
open_project [file tail $project]
set_top graph_accel
add_files $source_dir/graph_body.cpp -cflags "-std=c++14"
add_files $source_dir/graph_accel.cpp -cflags "-std=c++14"
add_files -tb $source_dir/test_graph_expand.cpp -cflags "-std=c++14"
open_solution solution -flow_target vitis
set_part {xcu280-fsvh2892-2L-e}
create_clock -period 5 -name default
csim_design -argv $source_dir/validation.txt
csynth_design
puts VITIS_TILE_CACHE_SYNTH_COMPLETE
exit
