# Classic2022.2 OOC implementation of an independently copied, audited project.
if {![info exists ::env(A_VITIS_IMPL_PROJECT)]} {error "Missing independent project"}
set project [file normalize $::env(A_VITIS_IMPL_PROJECT)]
set f [open $project/solution/sim/report/graph_accel_cosim.rpt]
set content [read $f];close $f
if {![regexp {Verilog[ ]*\|[ ]*Pass} $content]} {error "Passing co-simulation required"}
cd [file dirname $project]
open_project [file tail $project]
open_solution solution
export_design -flow impl -rtl verilog -format ip_catalog
puts VITIS_GRAPH_OOC_IMPL_COMPLETE
exit
