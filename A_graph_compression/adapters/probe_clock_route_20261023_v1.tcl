set root /inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/A_graph_compression
set out $root/data/netlist/clock_route_probe_20261023_v1
if {[file exists $out]} {error "Refusing existing probe output"}
file mkdir $out
set_param general.maxThreads 1
open_checkpoint $root/data/netlist/routeracc_cost_u280_20261022_v1/routed.dcp
source $root/adapters/netlist_snapshot.tcl
set f [open $root/data/derived/region_all_nets_cap8_20261022_v1/candidate_routes.tsv]
set names {};set route {}
while {[gets $f line]>=0} {
    set x [split $line "\t"]
    if {[lindex $x 0] eq "net"} {
        lappend names [netlist_snapshot::exact_net [lindex $x 1]]
        if {[lindex $x 1] eq {cx_q[6]}} {set route [lindex $x 2]}
    }
}
close $f
if {$route eq "" || [llength $names]!=1062} {error "Incomplete input"}
set f [open $out/configuration.tsv {WRONLY CREAT EXCL}]
proc clock_probe_config {stage} {
    global f
    foreach name {BUFCE_LEAF_X115Y26 BUFCE_LEAF_X118Y26 BUFCE_LEAF_X114Y26} {
        foreach b [get_bels -of_objects [get_sites $name]] {
            foreach p [list_property $b] {
                if {[string match CONFIG.* $p] && ![string match *.DEFAULT $p] && ![string match *.VALUES $p]} {
                    puts $f [join [list config $stage [get_property NAME $b] $p [get_property $p $b]] "\t"]
                }
            }
        }
    }
    flush $f
}
clock_probe_config baseline
route_design -unroute -nets $names
clock_probe_config unrouted
set_property FIXED_ROUTE $route [netlist_snapshot::exact_net {cx_q[6]}]
clock_probe_config applied
puts $f "status\t[get_property ROUTE_STATUS [netlist_snapshot::exact_net {cx_q[6]}]]"
puts $f complete
close $f
report_route_status -of_objects [netlist_snapshot::exact_net {cx_q[6]}] -file $out/route_status.rpt
report_drc -file $out/drc.rpt
puts CLOCK_ROUTE_PROBE_COMPLETE
