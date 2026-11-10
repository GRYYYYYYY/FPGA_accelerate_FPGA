# Vivado 2022.2. source this file after setting region_export_dir to a NEW directory.
# Batch: vivado -mode batch -source adapters/export_regions.tcl -tclargs <new-directory>
set graph_export_library_only 1
source -notrace [file join [file dirname [info script]] export_vivado.tcl]
unset graph_export_library_only
namespace eval graph_regions {
    variable part xcvu13p-fhgb2104-2-e
    proc begin {path purpose} {
        variable part
        foreach name {seen_nodes seen_tiles seen_pips roots} {set ::graph_export::$name [dict create]}
        set ::graph_export::out [open $path {WRONLY CREAT EXCL}]
        graph_export::row meta schema vivado_graph_tsv_v1
        graph_export::row meta part $part
        graph_export::row meta vivado_version [version -short]
        graph_export::row meta vivado_build [string map {\n { | } \r {}} [version]]
        graph_export::row meta timestamp_utc [clock format [clock seconds] -gmt 1 -format {%Y-%m-%dT%H:%M:%SZ}]
        graph_export::row meta scope complete_downhill_pips_and_nodes_for_selected_roots
        graph_export::row meta design empty_linked_device_no_netlist_occupancy
        graph_export::row meta purpose $purpose
    }
    proc finish {} {
        graph_export::row complete [dict size $::graph_export::roots] [dict size $::graph_export::seen_nodes] [dict size $::graph_export::seen_pips]
        flush $::graph_export::out
        puts "COMPLETE sources=[dict size $::graph_export::roots] nodes=[dict size $::graph_export::seen_nodes] pips=[dict size $::graph_export::seen_pips]"
    }
    proc expand {root} {
        set n [get_nodes $root]
        graph_export::node $n
        set pips [get_pips -downhill -of_objects $n]
        set children [get_nodes -downhill -of_objects $n]
        graph_export::row root $root [llength $pips] [llength $children]
        foreach child $children {graph_export::row oracle_child $root [graph_export::node $child]}
        foreach p $pips {
            lassign [graph_export::pip $p] un vn uw vw directional
            set name [get_property NAME $p]
            set emitted 0
            if {$un eq $root} {graph_export::row edge $name forward $root $vn $uw $vw; incr emitted}
            if {!$directional && $vn eq $root} {graph_export::row edge $name reverse $root $un $vw $uw; incr emitted}
            if {!$emitted} {error "Downhill PIP has incompatible endpoints: $root $p"}
        }
        if {[llength $children] == 0} {return {}}
        return [lsort -unique [get_property NAME $children]]
    }
    proc sample_tile {seed} {
        set t [get_tiles $seed]
        graph_export::tile $seed
        graph_export::row seed_tile $seed
        set groups [dict create]
        foreach n [get_nodes -of_objects $t] {
            set name [get_property NAME $n]
            set intent [get_property INTENT_CODE_NAME $n]
            if {[lindex [split $name /] 0] ne $seed && $intent ne "NODE_LAGUNA_DATA"} {continue}
            dict lappend groups $intent $name
        }
        foreach intent [lsort [dict keys $groups]] {
            set names [lsort -unique [dict get $groups $intent]]
            foreach name [lsort -unique [concat [lrange $names 0 2] [lrange $names end end]]] {
                graph_export::select_root [get_nodes $name] $seed "region_intent:$intent"
            }
        }
        set allpips [get_pips -of_objects $t]
        set excluded [get_pips -of_objects $t -filter {IS_EXCLUDED_PIP == 1}]
        graph_export::row meta "excluded_scan:$seed" "[llength $excluded]/[llength $allpips]"
        foreach flag {IS_DIRECTIONAL IS_PSEUDO IS_EXCLUDED_PIP} value {0 1 1} {
            foreach p [lrange [get_pips -of_objects $t -filter "$flag == $value"] 0 1] {
                foreach n [get_nodes -of_objects $p] {graph_export::select_root $n $seed "pip:$flag=$value"}
            }
        }
    }
    proc heldout {path} {
        begin $path slr1_2_3_heldout
        set code [catch {
            set seeds {INT_X0Y240 INT_X0Y360 INT_X0Y479 INT_X0Y480 INT_X0Y600 INT_X0Y719 INT_X0Y720 INT_X0Y840 INT_X0Y959 INT_X1Y360 INT_X1Y600 INT_X1Y840}
            # Select physical top/bottom rows from actual SLR membership, not lexical midpoint.
            foreach slr {1 2 3} {
                foreach ty {LAG_LAG BRAM DSP RCLK_INT_L} {
                    set filter [format {TYPE == %s && SLR_REGION_ID == %d} $ty $slr]
                    set candidates [get_tiles -filter $filter]
                    set rows [lsort -integer -unique [get_property ROW $candidates]]
                    foreach row [list [lindex $rows 0] [lindex $rows end]] {
                        set filter [format {TYPE == %s && SLR_REGION_ID == %d && ROW == %d} $ty $slr $row]
                        set names [lsort [get_property NAME [get_tiles -filter $filter]]]
                        lappend seeds [lindex $names 0]
                    }
                }
            }
            foreach seed [lsort -unique $seeds] {sample_tile $seed}
            set count 0
            foreach root [lsort [dict keys $::graph_export::roots]] {
                expand $root
                incr count
                if {$count % 100 == 0} {puts "heldout expanded=$count/[dict size $::graph_export::roots]"; flush $::graph_export::out}
            }
            finish
        } result options]
        close $::graph_export::out
        if {$code} {return -options $options $result}
    }
    proc closure {path} {
        begin $path bounded_bfs_query_domain
        set code [catch {
            set seeds {INT_X0Y360/EE2_E_BEG0 INT_X0Y600/EE2_E_BEG0 LAG_LAG_X4Y539/UBUMP0}
            set max_depth 4
            set max_sources 4000
            graph_export::row meta bfs_seeds [join $seeds ,]
            graph_export::row meta bfs_max_depth $max_depth
            graph_export::row meta bfs_max_sources $max_sources
            set seen [dict create]
            set queue {}
            foreach seed $seeds {
                set n [get_nodes $seed]
                if {[llength $n] != 1 || [get_property NAME $n] ne $seed} {error "Invalid canonical seed $seed"}
                dict set seen $seed 0
                lappend queue $seed
                graph_export::row seed_tile [lindex [split $seed /] 0]
            }
            set expanded 0
            set budget_hit 0
            for {set i 0} {$i < [llength $queue]} {incr i} {
                set root [lindex $queue $i]
                set depth [dict get $seen $root]
                if {$depth >= $max_depth} {continue}
                if {$expanded >= $max_sources} {set budget_hit 1; break}
                graph_export::select_root [get_nodes $root] [lindex [split $root /] 0] "bfs_depth:$depth"
                foreach child [expand $root] {
                    if {![dict exists $seen $child]} {
                        dict set seen $child [expr {$depth+1}]
                        lappend queue $child
                    }
                }
                incr expanded
                if {$expanded % 100 == 0} {puts "closure expanded=$expanded discovered=[dict size $seen]"; flush $::graph_export::out}
            }
            graph_export::row meta bfs_budget_hit $budget_hit
            graph_export::row meta bfs_discovered [dict size $seen]
            finish
        } result options]
        close $::graph_export::out
        if {$code} {return -options $options $result}
    }
    proc run {dir} {
        variable part
        if {[file exists $dir]} {error "Export directory already exists: $dir"}
        file mkdir $dir
        if {[current_project -quiet] eq ""} {
            create_project -in_memory graph_regions -part $part
            link_design -part $part -top graph_regions
        }
        if {[get_property PART [current_design]] ne $part} {error "Unexpected part"}
        heldout [file join $dir heldout.tsv]
        closure [file join $dir closure.tsv]
    }
}
if {[info exists region_export_library_only] && $region_export_library_only} {
    # Reuse the complete-row writer in preregistered experiments.
} elseif {[info exists region_export_dir]} {
    graph_regions::run $region_export_dir
} elseif {[info exists argv] && [llength $argv] == 1} {
    graph_regions::run [lindex $argv 0]
} else {error "Set region_export_dir or pass one new output directory"}
