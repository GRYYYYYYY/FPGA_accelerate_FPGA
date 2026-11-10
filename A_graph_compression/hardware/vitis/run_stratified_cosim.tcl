# Classic Vitis HLS 2022.2: execute additional stimuli on private baseline copies.
foreach name {A_STRATIFIED_PROJECT A_STRATIFIED_MANIFEST} {
    if {![info exists ::env($name)]} {error "Missing $name"}
}
set project [file normalize $::env(A_STRATIFIED_PROJECT)]
set manifest [file normalize $::env(A_STRATIFIED_MANIFEST)]
if {![file exists $project/solution/syn/report/graph_accel_csynth.xml]} {error "Successful synthesis required"}
if {![file exists $manifest] || [file size $manifest] == 0} {error "Explicit nonempty cosim argv required"}
cd [file dirname $project]
open_project [file tail $project]
open_solution solution
cosim_design -rtl verilog -tool xsim -argv $manifest
puts VITIS_STRATIFIED_COSIM_COMPLETE
exit
