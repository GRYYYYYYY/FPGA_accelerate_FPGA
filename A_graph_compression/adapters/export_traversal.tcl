# Library invoked by a preregistered, generated driver; Vivado Tcl 8.5 compatible.
set region_export_library_only 1
source -notrace [file join [file dirname [info script]] export_regions.tcl]
unset region_export_library_only
namespace eval traversal {
    proc export {path seeds max_depth max_sources} {
        foreach seed $seeds {
            set n [get_nodes $seed]
            if {[llength $n] != 1 || [get_property NAME $n] ne $seed} {error "Invalid seed $seed"}
        }
        graph_regions::begin $path preregistered_traversal
        set code [catch {
            graph_export::row meta bfs_seeds [join $seeds ,]
            graph_export::row meta bfs_max_depth $max_depth
            graph_export::row meta bfs_max_sources $max_sources
            set seen [dict create]
            set queue {}
            foreach seed $seeds {
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
                foreach child [graph_regions::expand $root] {
                    if {![dict exists $seen $child]} {
                        dict set seen $child [expr {$depth+1}]
                        lappend queue $child
                    }
                }
                incr expanded
                if {$expanded % 250 == 0} {puts "[file tail $path] sources=$expanded discovered=[dict size $seen]"; flush $::graph_export::out}
            }
            graph_export::row meta bfs_budget_hit $budget_hit
            graph_export::row meta bfs_discovered [dict size $seen]
            graph_regions::finish
        } result options]
        close $::graph_export::out
        if {$code} {return -options $options $result}
    }
    proc run {directory groups depth budget} {
        if {[file exists $directory]} {error "Directory already exists: $directory"}
        file mkdir $directory
        set part xcvu13p-fhgb2104-2-e
        if {[current_project -quiet] eq ""} {
            create_project -in_memory graph_traversal -part $part
            link_design -part $part -top graph_traversal
        }
        if {[get_property PART [current_design]] ne $part} {error "Unexpected part"}
        foreach group $groups {lassign $group name seeds; export [file join $directory "$name.tsv"] $seeds $depth $budget}
    }
}
