# Read-only evidence from the currently loaded, physically validated site design.
set row_root /inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/A_graph_compression
set row_in [open $row_root/data/raw/region_u280_20261022_v1/pseudo_pips.tsv]
set row_endpoints [dict create]
while {[gets $row_in row_line]>=0} {
    set row_fields [split $row_line "\t"]
    if {[lindex $row_fields 0] eq "pip" && [string match *CLK_BUFCE_ROW_FSR* [lindex $row_fields 1]]} {
        dict set row_endpoints [lindex $row_fields 2] 1
        dict set row_endpoints [lindex $row_fields 3] 1
    }
}
close $row_in
set row_out [open $row_root/data/raw/region_u280_20261022_v1/clock_row_pins_20261023_v1.tsv {WRONLY CREAT EXCL}]
puts $row_out "meta\tschema\tclock_row_endpoint_pins_v1"
puts $row_out "meta\tpart\t[get_property PART [current_design]]"
puts $row_out "meta\tversion\t[version -short]"
set row_sites [dict create]
foreach row_name [lsort [dict keys $row_endpoints]] {
    set row_wire [get_wires $row_name]
    set row_node [get_nodes -of_objects $row_wire]
    if {[llength $row_wire]!=1 || [llength $row_node]!=1} {error "Ambiguous endpoint $row_name"}
    puts $row_out [join [list endpoint $row_name [get_property NAME $row_node]] "\t"]
    foreach row_pin [get_site_pins -quiet -of_objects $row_node] {
        puts $row_out [join [list pin $row_name [get_property NAME $row_pin] [get_property DIRECTION $row_pin] [get_property IS_USED $row_pin]] "\t"]
        foreach row_site [get_sites -of_objects $row_pin] {dict set row_sites [get_property NAME $row_site] 1}
    }
}
foreach row_site_name [lsort [dict keys $row_sites]] {
    set row_site [get_sites $row_site_name]
    puts $row_out [join [list site $row_site_name [get_property SITE_TYPE $row_site]] "\t"]
    foreach row_bel [get_bels -of_objects $row_site] {
        puts $row_out [join [list bel [get_property NAME $row_bel] [get_property TYPE $row_bel]] "\t"]
        foreach row_property [list_property $row_bel] {
            if {[string match CONFIG.* $row_property]} {
                puts $row_out [join [list config [get_property NAME $row_bel] $row_property [get_property $row_property $row_bel]] "\t"]
            }
        }
    }
}
puts $row_out "complete\t[dict size $row_endpoints]\t[dict size $row_sites]"
close $row_out
puts "CLOCK_ROW_ENDPOINTS_COMPLETE [dict size $row_endpoints] [dict size $row_sites]"
