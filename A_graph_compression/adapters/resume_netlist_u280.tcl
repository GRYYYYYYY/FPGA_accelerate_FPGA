# Recovery from saved placement after an interrupted MCP session.
set task_root [file normalize [file join [file dirname [info script]] ..]]
set workload_output [file join $task_root data netlist routeracc_cost_u280_20261022_v1]
if {[file exists [file join $workload_output routed.dcp]]} {error "Routed checkpoint already exists"}
set_param general.maxThreads 4
open_checkpoint [file join $workload_output placed.dcp]
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
puts $meta "recovery\tresumed from placed.dcp after MCP process disappearance"
close $meta
puts "NETLIST_BASELINE_COMPLETE $workload_output"
