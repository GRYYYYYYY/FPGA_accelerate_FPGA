# Caller selects a verified checkpoint and stage. Read-only capture, no property changes.
if {![info exists clock_semantics_stage] || $clock_semantics_stage ni {baseline probe}} {error "Set baseline/probe stage"}
set clock_semantics_root /inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/A_graph_compression
set clock_semantics_out [open $clock_semantics_root/data/netlist/clock_semantics_capture_20261023_v2/$clock_semantics_stage.tsv {WRONLY CREAT EXCL}]
proc clock_semantics_row {args} {
    global clock_semantics_out
    foreach value $args {if {[regexp {[\t\r\n]} $value]} {error "Unescaped TSV value"}}
    puts $clock_semantics_out [join $args "\t"]
}
proc clock_semantics_links {kind object} {
    set name [get_property NAME $object]
    foreach net [get_nets -quiet -of_objects $object] {
        clock_semantics_row net_link $kind $name [get_property NAME $net] [get_property TYPE $net]
    }
    foreach node [get_nodes -quiet -of_objects $object] {
        clock_semantics_row node_link $kind $name [get_property NAME $node]
    }
}
clock_semantics_row meta schema clock_semantics_capture_v2
clock_semantics_row meta stage $clock_semantics_stage
clock_semantics_row meta tool [version -short]
clock_semantics_row meta part [get_property PART [current_project]]
set clock_semantics_counts [dict create site 0 bel 0 bel_pin 0 site_pin 0 site_pip 0 config 0]
foreach site_name {BUFCE_ROW_FSR_X21Y6 BUFCE_LEAF_X110Y26} {
    set site [get_sites $site_name]
    if {[llength $site] != 1} {error "Missing clock site"}
    clock_semantics_row site $site_name [get_property SITE_TYPE $site]
    dict incr clock_semantics_counts site
    foreach bel [get_bels -of_objects $site -include_routing_bels -include_routethru_bels] {
        clock_semantics_row bel [get_property NAME $bel] [get_property TYPE $bel] [get_property IS_USED $bel]
        dict incr clock_semantics_counts bel
        foreach cell [get_cells -quiet -of_objects $bel] {
            clock_semantics_row cell_link [get_property NAME $bel] [get_property NAME $cell] [get_property REF_NAME $cell]
        }
        foreach prop [list_property $bel] {
            if {[string match CONFIG.* $prop]} {
                clock_semantics_row config [get_property NAME $bel] $prop [get_property $prop $bel]
                dict incr clock_semantics_counts config
            }
        }
    }
    foreach pin [get_bel_pins -of_objects $site] {
        clock_semantics_row bel_pin [get_property NAME $pin] [get_property DIRECTION $pin] [get_property IS_USED $pin] [get_property IS_OPTIONALLY_INVERTIBLE $pin]
        dict incr clock_semantics_counts bel_pin
        clock_semantics_links bel_pin $pin
    }
    foreach pin [get_site_pins -of_objects $site] {
        clock_semantics_row site_pin [get_property NAME $pin] [get_property DIRECTION $pin] [get_property IS_USED $pin]
        dict incr clock_semantics_counts site_pin
        clock_semantics_links site_pin $pin
    }
    foreach pip [get_site_pips -of_objects $site] {
        clock_semantics_row site_pip [get_property NAME $pip] [get_property IS_USED $pip] [get_property IS_FIXED $pip] [get_property FROM_PIN $pip] [get_property TO_PIN $pip]
        dict incr clock_semantics_counts site_pip
    }
}
dict for {kind count} $clock_semantics_counts {clock_semantics_row count $kind $count}
clock_semantics_row complete $clock_semantics_stage
close $clock_semantics_out
puts CLOCK_SEMANTICS_CAPTURE_COMPLETE
