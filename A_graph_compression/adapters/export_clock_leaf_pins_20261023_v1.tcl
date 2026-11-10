set root /inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/A_graph_compression
set_param general.maxThreads 1
open_checkpoint $root/data/netlist/routeracc_cost_u280_20261022_v1/routed.dcp
set f [open $root/data/raw/region_u280_20261022_v1/pseudo_pips.tsv]
set endpoints [dict create]
while {[gets $f line]>=0} {
    set fields [split $line "\t"]
    if {[lindex $fields 0] eq "pip" && [string match RCLK_INT* [lindex $fields 4]]} {
        dict set endpoints [lindex $fields 2] 1
        dict set endpoints [lindex $fields 3] 1
    }
}
close $f
set f [open $root/data/raw/region_u280_20261022_v1/clock_leaf_pins.tsv {WRONLY CREAT EXCL}]
puts $f "meta\tschema\tclock_leaf_endpoint_pins_v1"
set count 0
foreach wire_name [lsort [dict keys $endpoints]] {
    set wire [get_wires $wire_name]
    set nodes [get_nodes -of_objects $wire]
    if {[llength $wire]!=1 || [llength $nodes]!=1} {error "Ambiguous endpoint $wire_name"}
    puts $f [join [list endpoint $wire_name [get_property NAME $nodes]] "\t"]
    foreach pin [get_site_pins -quiet -of_objects $nodes] {
        puts $f [join [list pin $wire_name [get_property NAME $pin] [get_property DIRECTION $pin] [get_property IS_USED $pin]] "\t"]
    }
    incr count
    if {$count%100==0} {flush $f;puts "CLOCK_PIN_PROGRESS $count"}
}
puts $f "complete\t$count"
close $f
puts "CLOCK_LEAF_PINS_COMPLETE endpoints=$count"
