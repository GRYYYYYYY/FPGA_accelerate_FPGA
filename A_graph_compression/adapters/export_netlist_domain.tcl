# Long read-only capture; use batch process so the caller can monitor progress.
set domain_root [file normalize [file join [file dirname [info script]] ..]]
source -notrace [file join $domain_root adapters export_traversal.tcl]
namespace eval netlist_domain {
    proc begin {path purpose} {
        foreach name {seen_nodes seen_tiles seen_pips roots} {set ::graph_export::$name [dict create]}
        set ::graph_export::out [open $path {WRONLY CREAT EXCL}]
        graph_export::row meta schema vivado_graph_tsv_v1
        graph_export::row meta part [get_property PART [current_design]]
        graph_export::row meta vivado_version [version -short]
        graph_export::row meta vivado_build [string map {\n { | } \r {}} [version]]
        graph_export::row meta timestamp_utc [clock format [clock seconds] -gmt 1 -format {%Y-%m-%dT%H:%M:%SZ}]
        graph_export::row meta scope complete_downhill_pips_and_nodes_for_selected_roots
        graph_export::row meta design routed_routeracc_cost_ooc_netlist
        graph_export::row meta purpose $purpose
    }
    proc reference {path source_file} {
        set input [open $source_file r]; set roots [split [string trim [read $input]] \n]; close $input
        begin $path reference_route_conditioned_integration_domain
        set code [catch {
            graph_export::row meta reference_source_count [llength $roots]
            set count 0
            foreach root $roots {
                set n [get_nodes [list $root]]
                if {[llength $n] != 1 || [get_property NAME $n] ne $root} {error "Missing canonical route node $root"}
                graph_export::select_root $n [lindex [split $root /] 0] reference_route_node
                graph_regions::expand $root
                incr count
                if {$count % 250 == 0} {puts "DOMAIN_PROGRESS $count/[llength $roots] nodes=[dict size $::graph_export::seen_nodes]"; flush $::graph_export::out}
            }
            graph_regions::finish
        } result options]
        close $::graph_export::out
        if {$code} {return -options $options $result}
    }
}
# Keep old exporter sources intact; replace only the metadata entrypoint here.
rename graph_regions::begin graph_regions::static_begin
proc graph_regions::begin {path purpose} {netlist_domain::begin $path $purpose}
open_checkpoint [file join $domain_root data netlist routeracc_cost_u280_20261022_v1 routed.dcp]
if {[get_property PART [current_design]] ne "xcu280-fsvh2892-2L-e"} {error "Wrong device"}
set directory [file join $domain_root data raw netlist_u280_20261022_v1]
traversal::export [file join $directory training.tsv] {INT_X2Y90/EE2_E_BEG0 INT_X3Y120/EE2_E_BEG0 INT_X2Y90/EE12_BEG0 INT_X3Y120/EE12_BEG0} 5 20000
netlist_domain::reference [file join $directory reference_domain.tsv] [file join $directory reference_sources.txt]
puts "NETLIST_DOMAIN_COMPLETE"
