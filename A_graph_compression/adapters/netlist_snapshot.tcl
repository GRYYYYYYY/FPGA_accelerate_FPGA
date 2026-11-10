# Read-only snapshot of physical net groups and occupied inter-site resources.
namespace eval netlist_snapshot {
    proc row {stream args} {
        foreach v $args {if {[regexp {[\t\r\n]} $v]} {error "Control character in netlist TSV"}}
        puts $stream [join $args "\t"]
    }
    proc names {objects} {
        if {[llength $objects] == 0} {return {}}
        return [lsort -unique [get_property NAME $objects]]
    }
    proc exact_net {name} {
        set net [get_nets -quiet [list $name]]
        if {[llength $net] != 1 || [get_property NAME $net] ne $name} {error "Ambiguous/missing net: $name"}
        return $net
    }
    proc export {path} {
        if {[get_property PART [current_design]] ne "xcu280-fsvh2892-2L-e"} {error "Unexpected snapshot part"}
        set f [open $path {WRONLY CREAT EXCL}]
        set code [catch {
            row $f meta schema routed_netlist_tsv_v1
            row $f meta part [get_property PART [current_design]]
            row $f meta tool [version -short]
            row $f meta design [get_property NAME [current_design]]
            row $f meta scope physical_net_groups_all_inter_site_resources_ooc_external_io_unconstrained
            set nets [names [get_nets -hier -top_net_of_hierarchical_group]]
            set nc 0; set pc 0; set sc 0; set cc 0
            foreach name $nets {
                set net [exact_net $name]
                set segments [get_nets -segments [list $name]]
                row $f net $name [get_property TYPE $net] [get_property ROUTE_STATUS $net] [get_property IS_ROUTE_FIXED $net] [string trim [get_property ROUTE $net]] [string trim [get_property FIXED_ROUTE $net]]
                foreach seg [names $segments] {row $f segment $name $seg}
                foreach node [names [get_nodes -of_objects $segments]] {row $f node $name $node; incr nc}
                foreach pip [names [get_pips -of_objects $segments]] {row $f pip $name $pip; incr pc}
                foreach sp [get_site_pins -of_objects $segments] {
                    set node [get_nodes -of_objects $sp]
                    if {[llength $node] > 1} {error "Multiple nodes at site pin $sp"}
                    row $f site_pin $name [get_property NAME $sp] [get_property DIRECTION $sp] [get_property IS_USED $sp] [join [names $node] ""]
                    incr sc
                }
                foreach pin [get_pins -of_objects $segments -filter {IS_LEAF == 1}] {
                    row $f leaf_pin $name [get_property NAME $pin] [get_property DIRECTION $pin]
                }
            }
            foreach cell [get_cells -hier -filter {IS_PRIMITIVE}] {
                row $f cell [get_property NAME $cell] [get_property REF_NAME $cell] [get_property LOC $cell] [get_property BEL $cell]
                incr cc
            }
            row $f complete [llength $nets] $nc $pc $sc $cc
            puts "NETLIST_SNAPSHOT_COMPLETE nets=[llength $nets] nodes=$nc pips=$pc sitepins=$sc cells=$cc path=$path"
        } result options]
        close $f
        if {$code} {return -options $options $result}
    }
}
