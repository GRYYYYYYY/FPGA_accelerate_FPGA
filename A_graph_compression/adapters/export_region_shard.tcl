# Read-only complete outgoing rows for one immutable regional source partition.
if {[llength $argv]!=5} {error "Expected roots output checkpoint config_sha shard_id"}
lassign $argv roots_file output checkpoint config_sha shard_id
set script_root [file normalize [file join [file dirname [info script]] ..]]
set region_export_library_only 1
source -notrace [file join $script_root adapters export_regions.tcl]
unset region_export_library_only
set_param general.maxThreads 1
open_checkpoint $checkpoint
if {[get_property PART [current_design]] ne "xcu280-fsvh2892-2L-e"} {error "Wrong device"}
set f [open $roots_file];set source_names [split [string trim [read $f]] \n];close $f
if {[llength $source_names]==0 || [lsort -unique $source_names] ne $source_names} {error "Empty/unsorted/duplicate source list"}
# Resolve roots together, then bind by NAME: never assume collection order.
set source_objects [get_nodes $source_names]
set object_by_name [dict create]
foreach node $source_objects {dict set object_by_name [get_property NAME $node] $node}
if {[lsort [dict keys $object_by_name]] ne $source_names} {error "Canonical source lookup differs"}
foreach name {seen_nodes seen_tiles seen_pips roots} {set ::graph_export::$name [dict create]}
set ::graph_export::out [open $output {WRONLY CREAT EXCL}]
set export_code [catch {
    graph_export::row meta schema vivado_graph_tsv_v1
    graph_export::row meta part [get_property PART [current_design]]
    graph_export::row meta vivado_version [version -short]
    graph_export::row meta vivado_build [string map {\n { | } \r {}} [version]]
    graph_export::row meta timestamp_utc [clock format [clock seconds] -gmt 1 -format {%Y-%m-%dT%H:%M:%SZ}]
    graph_export::row meta scope complete_downhill_pips_and_nodes_for_selected_roots
    graph_export::row meta design routed_routeracc_cost_ooc_netlist
    graph_export::row meta purpose independent_endpoint_region_complete_rows
    graph_export::row meta selection_config_sha256 $config_sha
    graph_export::row meta shard_id $shard_id
    set count 0
    foreach root $source_names {
        set n [dict get $object_by_name $root]
        graph_export::select_root $n [lindex [split $root /] 0] independent_endpoint_region_all_nodes
        graph_export::node $n
        set pips [get_pips -downhill -of_objects $n]
        set children [get_nodes -downhill -of_objects $n]
        graph_export::row root $root [llength $pips] [llength $children]
        foreach child $children {graph_export::row oracle_child $root [graph_export::node $child]}
        foreach p $pips {
            lassign [graph_export::pip $p] un vn uw vw directional
            set name [get_property NAME $p];set emitted 0
            if {$un eq $root} {graph_export::row edge $name forward $root $vn $uw $vw;incr emitted}
            if {!$directional && $vn eq $root} {graph_export::row edge $name reverse $root $un $vw $uw;incr emitted}
            if {!$emitted} {error "Downhill PIP endpoints incompatible: $root $p"}
        }
        incr count
        if {$count%250==0} {
            flush $::graph_export::out
            puts "REGION_SHARD_PROGRESS id=$shard_id roots=$count/[llength $source_names] nodes=[dict size $::graph_export::seen_nodes]"
        }
    }
    graph_regions::finish
    puts "REGION_SHARD_COMPLETE id=$shard_id roots=[llength $source_names]"
} result options]
close $::graph_export::out
if {$export_code} {return -options $options $result}
