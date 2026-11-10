# Diagnostic only: preserve failures, never invoke automatic route repair.
set diag_root /inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/A_graph_compression
set diag_dir $diag_root/data/netlist/region_all_diagnostic_20261023_v3
set_param general.maxThreads 1
if {[file exists $diag_dir]} {error "Refusing existing diagnostic output"}
file mkdir $diag_dir
if {[llength [get_designs -quiet]]} {close_design}
open_checkpoint $diag_root/data/netlist/routeracc_cost_u280_20261022_v1/routed.dcp
source $diag_root/adapters/netlist_snapshot.tcl
set f [open $diag_root/data/derived/region_all_nets_cap8_20261022_v1/candidate_routes.tsv]
set diag_routes [dict create];set diag_nodes [dict create];set diag_pips [dict create]
set diag_complete 0
while {[gets $f line]>=0} {
    set fields [split $line "\t"]
    switch -- [lindex $fields 0] {
        net {dict set diag_routes [lindex $fields 1] [lindex $fields 2]}
        node {dict lappend diag_nodes [lindex $fields 1] [lindex $fields 2]}
        pip {dict lappend diag_pips [lindex $fields 1] [lindex $fields 2]}
        complete {set diag_complete [lindex $fields 1]}
    }
}
close $f
if {$diag_complete!=1062 || [dict size $diag_routes]!=1062} {error "Incomplete candidate"}
set diag_nets {}
foreach name [dict keys $diag_routes] {lappend diag_nets [netlist_snapshot::exact_net $name]}
route_design -unroute -nets $diag_nets
set f [open $diag_dir/immediate_status.tsv {WRONLY CREAT EXCL}]
set diag_count 0
foreach name [dict keys $diag_routes] {
    puts $f [join [list begin $name] "\t"]
    flush $f
    set n [netlist_snapshot::exact_net $name]
    set code [catch {set_property FIXED_ROUTE [dict get $diag_routes $name] $n} message]
    set segments [get_nets -segments [list $name]]
    set nodes_equal [expr {[netlist_snapshot::names [get_nodes -quiet -of_objects $segments]] eq [lsort -unique [dict get $diag_nodes $name]]}]
    set pips_equal [expr {[netlist_snapshot::names [get_pips -quiet -of_objects $segments]] eq [lsort -unique [dict get $diag_pips $name]]}]
    puts $f [join [list net $name $code [get_property ROUTE_STATUS $n] $nodes_equal $pips_equal] "\t"]
    if {$code} {puts $f [join [list error $name [string map {\n { | } \t { }} $message]] "\t"]}
    flush $f
    incr diag_count
    if {$diag_count%100==0} {flush $f;puts "DIAGNOSTIC_PROGRESS $diag_count"}
}
puts $f "complete\t$diag_count"
close $f
report_route_status -file $diag_dir/route_status.rpt
report_drc -file $diag_dir/drc.rpt
write_checkpoint $diag_dir/diagnostic.dcp
netlist_snapshot::export $diag_dir/snapshot.tsv
puts REGION_ALL_DIAGNOSTIC_COMPLETE
