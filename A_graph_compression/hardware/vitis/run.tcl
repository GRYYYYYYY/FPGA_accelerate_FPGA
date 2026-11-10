# Classic Vitis HLS2022.2. Never modify the previous regional HLS projects.
foreach name {A_VITIS_SOURCE A_VITIS_PROJECT A_VITIS_STAGE} {
    if {![info exists ::env($name)]} {error "Missing $name"}
}
set source_dir [file normalize $::env(A_VITIS_SOURCE)]
set project [file normalize $::env(A_VITIS_PROJECT)]
set stage $::env(A_VITIS_STAGE)
file mkdir [file dirname $project]
cd [file dirname $project]
if {$stage eq "synth"} {
    if {[file exists $project]} {error "Refusing existing project"}
    open_project [file tail $project]
    set_top graph_accel
    add_files $source_dir/graph_body.cpp -cflags "-std=c++14"
    add_files $source_dir/graph_accel.cpp -cflags "-std=c++14"
    add_files -tb $source_dir/test_graph_expand.cpp -cflags "-std=c++14"
    open_solution solution -flow_target vitis
    set_part {xcu280-fsvh2892-2L-e}
    create_clock -period 5 -name default
    csim_design -argv $source_dir/full.txt
    csynth_design
    puts VITIS_GRAPH_SYNTH_COMPLETE
} elseif {$stage eq "cosim"} {
    if {![file exists $project/solution/syn/report/graph_accel_csynth.xml]} {error "Successful csynth required"}
    if {![file exists $source_dir/rtl.txt]} {error "Explicit co-simulation manifest required"}
    open_project [file tail $project]
    open_solution solution
    cosim_design -rtl verilog -tool xsim -argv $source_dir/rtl.txt
    puts VITIS_GRAPH_COSIM_COMPLETE
} elseif {$stage eq "export"} {
    set stream [open $project/solution/sim/report/graph_accel_cosim.rpt]
    set report [read $stream];close $stream
    if {![regexp {Verilog[ ]*\|[ ]*Pass} $report]} {error "Passing co-simulation required"}
    if {[file exists $source_dir/graph_accel.xo]} {error "Refusing existing kernel object"}
    open_project [file tail $project]
    open_solution solution
    export_design -format xo -rtl verilog -output $source_dir/graph_accel.xo
    puts VITIS_GRAPH_EXPORT_COMPLETE
} else {error "Unknown stage"}
exit
