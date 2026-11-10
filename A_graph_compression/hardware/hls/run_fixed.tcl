# Separate 2022.2 projects from frozen per-mode sources and workload manifests.
foreach name {A_FIXED_SOURCE A_FIXED_PROJECT A_FIXED_STAGE} {
    if {![info exists ::env($name)]} {error "Missing $name"}
}
set source_dir [file normalize $::env(A_FIXED_SOURCE)]
set project [file normalize $::env(A_FIXED_PROJECT)]
set stage $::env(A_FIXED_STAGE)
file mkdir [file dirname $project]
cd [file dirname $project]
set project_name [file tail $project]
if {$stage eq "synth"} {
    if {[file exists $project]} {error "Refusing existing project"}
    open_project $project_name
    set_top graph_expand
    add_files [file join $source_dir graph_expand.cpp] -cflags "-std=c++14"
    add_files -tb [file join $source_dir test_graph_expand.cpp] -cflags "-std=c++14"
    open_solution solution -flow_target vitis
    set_part {xcu280-fsvh2892-2L-e}
    create_clock -period 5 -name default
    csim_design -argv [file join $source_dir full.txt]
    csynth_design
    puts FIXED_SYNTH_COMPLETE
} elseif {$stage eq "cosim"} {
    if {![file exists [file join $project solution syn report graph_expand_csynth.xml]]} {error "Successful csynth required"}
    if {![file exists [file join $source_dir rtl.txt]]} {error "Explicit cosim argv required"}
    open_project $project_name
    open_solution solution
    cosim_design -rtl verilog -tool xsim -argv [file join $source_dir rtl.txt]
    puts FIXED_COSIM_COMPLETE
} elseif {$stage eq "impl"} {
    set f [open [file join $project solution sim report graph_expand_cosim.rpt]]
    set content [read $f];close $f
    if {![regexp {Verilog[ ]*\|[ ]*Pass} $content]} {error "Passing co-simulation required"}
    open_project $project_name
    open_solution solution
    export_design -flow impl -rtl verilog -format ip_catalog
    puts FIXED_IMPL_COMPLETE
} else {error "Unknown stage"}
exit
