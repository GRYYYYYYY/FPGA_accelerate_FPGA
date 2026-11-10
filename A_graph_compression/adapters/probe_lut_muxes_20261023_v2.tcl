set root /inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/A_graph_compression
set output $root/data/netlist/lut_route_probes_20261023_v2
if {[file exists $output]} {error "Refusing existing output"}
file mkdir $output
set_param general.maxThreads 1
source $root/adapters/netlist_snapshot.tcl
set f [open $root/data/derived/region_all_nets_cap8_20261022_v1/candidate_routes.tsv]
set routes [dict create]
while {[gets $f line]>=0} {
    set x [split $line "\t"]
    if {[lindex $x 0] eq "net"} {dict set routes [lindex $x 1] [lindex $x 2]}
}
close $f
set f [open $root/data/derived/region_all_nets_cap8_20261022_v1/lut_probe_bels.tsv]
set probes [dict create]
while {[gets $f line]>=0} {
    lassign [split $line "\t"] n b
    dict lappend probes $n $b
}
close $f
set f [open $output/equations.tsv {WRONLY CREAT EXCL}]
set count 0
foreach name [dict keys $probes] {
    if {[llength [get_designs -quiet]]} {close_design}
    open_checkpoint $root/data/netlist/routeracc_cost_u280_20261022_v1/routed.dcp
    foreach bel [dict get $probes $name] {
        puts $f [join [list baseline $name $bel [get_property CONFIG.EQN [get_bels $bel]]] "\t"]
    }
    set selected {}
    foreach n [dict keys $routes] {lappend selected [netlist_snapshot::exact_net $n]}
    route_design -unroute -nets $selected
    set_property FIXED_ROUTE [dict get $routes $name] [netlist_snapshot::exact_net $name]
    foreach bel [dict get $probes $name] {
        puts $f [join [list applied $name $bel [get_property CONFIG.EQN [get_bels $bel]]] "\t"]
    }
    set probe_sites [dict create]
    foreach bel [dict get $probes $name] {dict set probe_sites [lindex [split $bel /] 0] 1}
    foreach site [dict keys $probe_sites] {
        foreach pip [get_site_pips -of_objects [get_sites $site]] {
            if {[get_property IS_USED $pip]} {
                puts $f [join [list active_site_pip $name [get_property NAME $pip] [get_property FROM_PIN $pip] [get_property TO_PIN $pip]] "\t"]
            }
        }
    }
    puts $f [join [list status $name [get_property ROUTE_STATUS [netlist_snapshot::exact_net $name]]] "\t"]
    flush $f
    report_drc -file $output/drc_$count.rpt
    incr count
    puts "LUT_PROBE_PROGRESS $count"
}
puts $f "complete\t$count"
close $f
puts LUT_ROUTE_PROBES_COMPLETE
