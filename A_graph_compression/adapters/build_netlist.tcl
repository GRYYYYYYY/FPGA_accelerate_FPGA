# Invoke inside Vivado 2022.2. Existing source is read-only; all outputs stay in A.
set task_root [file normalize [file join [file dirname [info script]] ..]]
if {![info exists workload_part]} {set workload_part xcvu13p-fhgb2104-2-e}
if {![info exists workload_output]} {set workload_output [file join $task_root data netlist routeracc_cost_20261022_v1]}
if {[file exists $workload_output]} {error "Refusing to replace existing netlist output: $workload_output"}
file mkdir $workload_output
close_project
create_project -in_memory graph_netlist -part $workload_part
set_param general.maxThreads 4
set reference_root [file normalize [file join $task_root .. FPGA-Routing-main FPGA-Routing-hw src]]
read_verilog [list [file join $reference_root cost_calculator.v] [file join $reference_root dly_cell.v] [file join $task_root workloads routeracc_cost_registered.v]]
synth_design -top routeracc_cost_registered -part $workload_part -mode out_of_context
create_clock -name workload_clock -period 10.000 [get_ports clk]
opt_design
create_pblock workload_region
resize_pblock [get_pblocks workload_region] -add {SLICE_X10Y390:SLICE_X25Y430}
add_cells_to_pblock [get_pblocks workload_region] [get_cells -hier -filter {IS_PRIMITIVE && REF_NAME != BUFG}]
place_design
write_checkpoint [file join $workload_output placed.dcp]
report_utilization -file [file join $workload_output placed_utilization.rpt]
set route_start [clock milliseconds]
route_design
set baseline_route_ms [expr {[clock milliseconds]-$route_start}]
write_checkpoint [file join $workload_output routed.dcp]
report_route_status -file [file join $workload_output route_status.rpt]
report_timing_summary -file [file join $workload_output timing_summary.rpt]
set meta [open [file join $workload_output build.tsv] {WRONLY CREAT EXCL}]
puts $meta "tool\t[version -short]"
puts $meta "part\t[get_property PART [current_design]]"
puts $meta "baseline_route_ms\t$baseline_route_ms"
puts $meta "cells\t[llength [get_cells -hier -filter {IS_PRIMITIVE}]]"
puts $meta "nets\t[llength [get_nets -hier]]"
puts $meta "scope\tOOC registered wrapper of unchanged RouterAcc cost_calculator; external IO paths are unplaced/unconstrained"
close $meta
puts "NETLIST_BASELINE_COMPLETE $workload_output"
