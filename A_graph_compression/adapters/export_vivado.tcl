# Vivado 2022.2 device-only, complete one-hop adjacency for deterministic roots.
# In a fresh batch process: vivado -mode batch -source adapters/export_vivado.tcl \
#   -tclargs data/raw/xcvu13p_sample.tsv
# In an existing linked session: set graph_export_path <new.tsv>; source <this file>
namespace eval graph_export {
    variable out
    variable seen_nodes [dict create]
    variable seen_tiles [dict create]
    variable seen_pips [dict create]
    variable roots [dict create]
    proc row {args} {
        variable out
        foreach value $args {
            if {[regexp {[\t\r\n]} $value]} {error "TSV control character in field"}
        }
        puts $out [join $args "\t"]
    }
    proc props {obj} {
        set result {}
        foreach key [lsort [list_property $obj]] {
            if {$key ni {NAME CLASS}} {lappend result $key [get_property $key $obj]}
        }
        return $result
    }
    proc tile {name} {
        variable seen_tiles
        if {[dict exists $seen_tiles $name]} {return}
        set obj [get_tiles $name]
        if {[llength $obj] != 1} {error "Ambiguous tile $name"}
        dict set seen_tiles $name 1
        row tile $name {*}[props $obj]
    }
    proc node {obj} {
        variable seen_nodes
        if {[llength $obj] != 1} {error "Expected one canonical node, got $obj"}
        set name [get_property NAME $obj]
        if {[dict exists $seen_nodes $name]} {return $name}
        dict set seen_nodes $name 1
        row node $name {*}[props $obj]
        foreach w [get_wires -of_objects $obj] {
            set wn [get_property NAME $w]
            set actual [get_nodes -of_objects $w]
            if {[llength $actual] != 1 || [get_property NAME $actual] ne $name} {
                error "Alias does not resolve to canonical node: $wn -> $name"
            }
            row alias $wn $name
            tile [lindex [split $wn /] 0]
        }
        return $name
    }
    proc pip {obj} {
        variable seen_pips
        set name [get_property NAME $obj]
        if {[dict exists $seen_pips $name]} {return [dict get $seen_pips $name]}
        set u [get_wires -uphill -of_objects $obj]
        set v [get_wires -downhill -of_objects $obj]
        if {[llength $u] != 1 || [llength $v] != 1} {error "Unsupported PIP endpoints $name: $u $v"}
        set un [node [get_nodes -of_objects $u]]
        set vn [node [get_nodes -of_objects $v]]
        set uw [get_property NAME $u]
        set vw [get_property NAME $v]
        set directional [get_property IS_DIRECTIONAL $obj]
        row pip $name $uw $vw {*}[props $obj]
        tile [get_property TILE $obj]
        set info [list $un $vn $uw $vw $directional]
        dict set seen_pips $name $info
        return $info
    }
    proc select_root {obj seed reason} {
        variable roots
        set name [get_property NAME $obj]
        dict set roots $name 1
        row selection $name $seed $reason
    }
    proc run {path} {
        variable out
        variable roots
        variable seen_nodes
        variable seen_pips
        set part xcvu13p-fhgb2104-2-e
        if {[current_project -quiet] eq ""} {
            create_project -in_memory graph_sample -part $part
            link_design -part $part -top graph_sample
        }
        if {[get_property PART [current_design]] ne $part} {error "Unexpected part"}
        # All output files are exclusive-create. A missing 'complete' row marks interrupted export.
        set out [open $path {WRONLY CREAT EXCL}]
        set code [catch {
            row meta schema vivado_graph_tsv_v1
            row meta part $part
            row meta vivado_version [version -short]
            row meta vivado_build [string map {\n { | } \r {}} [version]]
            row meta timestamp_utc [clock format [clock seconds] -gmt 1 -format {%Y-%m-%dT%H:%M:%SZ}]
            row meta scope complete_downhill_pips_and_nodes_for_selected_roots
            row meta design empty_linked_device_no_netlist_occupancy
            set seeds {INT_X0Y0 INT_X0Y1 INT_X0Y30 INT_X0Y239 INT_X0Y240 INT_X0Y959 INT_X1Y1 INT_X1Y30}
            foreach ty {LAG_LAG BRAM DSP RCLK_INT_L} {
                set candidates [lsort [get_property NAME [get_tiles -filter "TYPE == $ty"]]]
                foreach idx [lsort -integer -unique [list 0 [expr {[llength $candidates]/2}] [expr {[llength $candidates]-1}]]] {
                    lappend seeds [lindex $candidates $idx]
                }
            }
            foreach seed $seeds {
                set t [get_tiles $seed]
                tile $seed
                row seed_tile $seed
                set groups [dict create]
                foreach n [get_nodes -of_objects $t] {
                    set name [get_property NAME $n]
                    # Prefer canonical base wires within the seed tile, but include aliases below.
                    if {[lindex [split $name /] 0] ne $seed} {continue}
                    dict lappend groups [get_property INTENT_CODE_NAME $n] $name
                }
                foreach intent [lsort [dict keys $groups]] {
                    set names [lsort -unique [dict get $groups $intent]]
                    set choices [concat [lrange $names 0 2] [lrange $names end end]]
                    foreach name [lsort -unique $choices] {select_root [get_nodes $name] $seed "intent:$intent"}
                }
                # Ensure two directions of real bidirectional PIPs and special flags are sampled.
                foreach flag {IS_DIRECTIONAL IS_PSEUDO IS_EXCLUDED_PIP} value {0 1 1} {
                    set matches [get_pips -of_objects $t -filter "$flag == $value"]
                    foreach p [lrange $matches 0 1] {
                        foreach n [get_nodes -of_objects $p] {select_root $n $seed "pip:$flag=$value"}
                    }
                }
                # Include non-local canonical nodes reached through this tile's wires.
                set aliases {}
                foreach n [get_nodes -of_objects $t] {
                    if {[lindex [split [get_property NAME $n] /] 0] ne $seed} {lappend aliases [get_property NAME $n]}
                }
                foreach name [lrange [lsort -unique $aliases] 0 1] {select_root [get_nodes $name] $seed alias}
            }
            set count 0
            foreach root [lsort [dict keys $roots]] {
                set n [get_nodes $root]
                node $n
                set pips [get_pips -downhill -of_objects $n]
                set children [get_nodes -downhill -of_objects $n]
                row root $root [llength $pips] [llength $children]
                foreach child $children {row oracle_child $root [node $child]}
                foreach p $pips {
                    lassign [pip $p] un vn uw vw directional
                    set name [get_property NAME $p]
                    set emitted 0
                    if {$un eq $root} {row edge $name forward $root $vn $uw $vw; incr emitted}
                    if {!$directional && $vn eq $root} {row edge $name reverse $root $un $vw $uw; incr emitted}
                    if {!$emitted} {error "Downhill PIP has incompatible endpoints: $root $p"}
                }
                incr count
                if {$count % 50 == 0} {puts "graph_export roots=$count/[dict size $roots] nodes=[dict size $seen_nodes] pips=[dict size $seen_pips]"; flush $out}
            }
            row complete [dict size $roots] [dict size $seen_nodes] [dict size $seen_pips]
            puts "graph_export COMPLETE roots=[dict size $roots] nodes=[dict size $seen_nodes] pips=[dict size $seen_pips] path=$path"
        } result options]
        close $out
        if {$code} {return -options $options $result}
    }
}
if {[info exists graph_export_library_only] && $graph_export_library_only} {
    # Load the verified resource/alias writer without running the v1 sampler.
} elseif {[info exists graph_export_path]} {
    graph_export::run $graph_export_path
} elseif {[info exists argv] && [llength $argv] == 1} {
    graph_export::run [lindex $argv 0]
} else {error "Set graph_export_path or pass exactly one output TSV argument"}
