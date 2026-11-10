set workload_part xcu280-fsvh2892-2L-e
set workload_output [file normalize [file join [file dirname [info script]] .. data netlist routeracc_cost_u280_20261022_v1]]
source [file normalize [file join [file dirname [info script]] .. adapters build_netlist.tcl]]
