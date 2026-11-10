catch {close $probe_out}
set probe_root /inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/A_graph_compression
close_design
open_checkpoint $probe_root/data/netlist/routeracc_cost_u280_20261022_v1/routed.dcp
source $probe_root/adapters/netlist_snapshot.tcl
set probe_out [open $probe_root/data/netlist/region_cap8_applied_20261023_v1/site_transition_v2.tsv {WRONLY CREAT EXCL}]
proc probe_site_state {stage} {
    global probe_out
    set bel [get_bels SLICE_X22Y411/G6LUT]
    set pin [get_bel_pins SLICE_X22Y411/OUTMUXG/D6]
    puts $probe_out [join [list state $stage [get_property CONFIG.EQN $bel] [get_property IS_USED $bel] [netlist_snapshot::names [get_nets -quiet -of_objects $pin]]] "\t"]
    flush $probe_out
}
set f [open $probe_root/data/derived/region_all_nets_cap8_20261022_v1/candidate_routes.tsv]
set probe_routes [dict create]
while {[gets $f line]>=0} {
    set fields [split $line "\t"]
    if {[lindex $fields 0] eq "net"} {dict set probe_routes [lindex $fields 1] [lindex $fields 2]}
}
close $f
probe_site_state baseline
set probe_nets {}
foreach name [dict keys $probe_routes] {lappend probe_nets [netlist_snapshot::exact_net $name]}
route_design -unroute -nets $probe_nets
probe_site_state after_unroute
foreach name [dict keys $probe_routes] {
    set n [netlist_snapshot::exact_net $name]
    set_property FIXED_ROUTE [dict get $probe_routes $name] $n
    probe_site_state $name
    puts $probe_out [join [list route_status $name [get_property ROUTE_STATUS $n]] "\t"]
    if {$name eq {cg_q[2]}} {break}
}
puts $probe_out complete
close $probe_out
puts SITE_TRANSITION_PROBE_COMPLETE
