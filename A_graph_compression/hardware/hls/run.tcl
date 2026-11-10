# Vivado/Vitis HLS 2022.2 classic Tcl flow. Run with A_HLS_* environment.
foreach name {A_HLS_PROJECT A_HLS_FIXTURES A_HLS_STAGE} {
    if {![info exists ::env($name)]} {error "Missing $name"}
}
set here [file dirname [file normalize [info script]]]
set project [file normalize $::env(A_HLS_PROJECT)]
set fixtures [file normalize $::env(A_HLS_FIXTURES)]
set stage $::env(A_HLS_STAGE)
set cosim_manifest rtl.txt
if {[info exists ::env(A_HLS_COSIM_MANIFEST)]} {set cosim_manifest $::env(A_HLS_COSIM_MANIFEST)}
file mkdir [file dirname $project]
cd [file dirname $project]
set project_name [file tail $project]
if {$stage eq "synth"} {
    if {[file exists $project]} {error "Refusing to overwrite project $project"}
    open_project $project_name
    set_top graph_expand
    add_files [file join $here graph_expand.cpp] -cflags "-std=c++14"
    add_files -tb [file join $here test_graph_expand.cpp] -cflags "-std=c++14"
    open_solution solution -flow_target vitis
    set_part {xcu280-fsvh2892-2L-e}
    create_clock -period 5 -name default
    csim_design -argv [file join $fixtures full.txt]
    csynth_design
    puts GRAPH_EXPAND_SYNTH_COMPLETE
} elseif {$stage eq "cosim"} {
    if {![file exists [file join $project solution syn report graph_expand_csynth.xml]]} {error "Successful csynth required"}
    if {![file exists [file join $fixtures $cosim_manifest]]} {error "Missing explicit co-simulation arguments"}
    open_project $project_name
    open_solution solution
    cosim_design -rtl verilog -tool xsim -argv [file join $fixtures $cosim_manifest]
    puts GRAPH_EXPAND_COSIM_COMPLETE
} elseif {$stage eq "impl"} {
    set report [file join $project solution sim report graph_expand_cosim.rpt]
    if {![file exists $report]} {error "Co-simulation report required"}
    set f [open $report]; set content [read $f]; close $f
    if {![regexp {Verilog[ ]*\|[ ]*Pass} $content]} {error "Passing Verilog co-simulation required"}
    open_project $project_name
    open_solution solution
    export_design -flow impl -rtl verilog -format ip_catalog
    puts GRAPH_EXPAND_IMPL_COMPLETE
} else {error "Unknown stage $stage"}
exit
