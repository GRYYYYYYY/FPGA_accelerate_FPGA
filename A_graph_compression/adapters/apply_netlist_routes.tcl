# Replaces only selected net routes in a baseline checkpoint. No automatic repair.
# Input is TSV data, never evaluated as Tcl. Branching follows UG904/UG903.
namespace eval netlist_apply {
    proc apply {input directory} {
        if {[file exists $directory]} {error "Refusing existing output directory"}
        file mkdir $directory
        set f [open $input]; set routes [dict create]; set complete 0
        set nodes [dict create]; set pips [dict create]; set meta [dict create]
        while {[gets $f line] >= 0} {
            if {$complete} {error "Data after completion"}
            set fields [split $line "\t"]; set tag [lindex $fields 0]
            switch -- $tag {
                meta {dict set meta [lindex $fields 1] [lindex $fields 2]}
                net {
                    lassign $fields tag name route
                    if {[dict exists $routes $name] || [llength $fields] != 3} {error "Invalid/duplicate net record"}
                    llength $route
                    dict set routes $name $route
                    dict set nodes $name {}; dict set pips $name {}
                }
                node - pip {
                    lassign $fields tag name value
                    if {![dict exists $routes $name] || [llength $fields] != 3} {error "Invalid resource record"}
                    if {$tag eq "node"} {dict lappend nodes $name $value} else {dict lappend pips $name $value}
                }
                complete {
                    if {[llength $fields] != 2 || [lindex $fields 1] != [dict size $routes]} {error "Invalid completion count"}
                    set complete 1
                }
                default {error "Unknown route record $tag"}
            }
        }
        close $f
        if {!$complete || [dict size $routes] == 0 || [dict get $meta schema] ne "canonical_routes_v1"} {error "Incomplete route file"}
        if {[get_property PART [current_design]] ne "xcu280-fsvh2892-2L-e"} {error "Wrong device"}
        set selected {}
        foreach name [dict keys $routes] {
            set net [netlist_snapshot::exact_net $name]
            if {[get_property TYPE $net] ne "SIGNAL" || [get_property IS_ROUTE_FIXED $net]} {error "Not eligible for replacement: $name"}
            lappend selected $net
        }
        set begin [clock milliseconds]
        route_design -unroute -nets $selected
        foreach name [dict keys $routes] {
            set net [netlist_snapshot::exact_net $name]
            set_property FIXED_ROUTE [dict get $routes $name] $net
            set segments [get_nets -segments [list $name]]
            set actual_nodes [netlist_snapshot::names [get_nodes -of_objects $segments]]
            set actual_pips [netlist_snapshot::names [get_pips -of_objects $segments]]
            if {$actual_nodes ne [lsort -unique [dict get $nodes $name]]} {error "Canonical node readback differs: $name"}
            if {$actual_pips ne [lsort -unique [dict get $pips $name]]} {error "PIP readback differs: $name"}
            if {[get_property ROUTE_STATUS $net] ne "ROUTED"} {error "Route is not complete: $name"}
        }
        set elapsed [expr {[clock milliseconds]-$begin}]
        set f [open [file join $directory apply.tsv] {WRONLY CREAT EXCL}]
        puts $f "applied_nets\t[dict size $routes]"
        puts $f "unroute_and_fixed_route_ms\t$elapsed"
        close $f
        write_checkpoint [file join $directory routed.dcp]
        report_route_status -file [file join $directory route_status.rpt]
        report_drc -file [file join $directory drc.rpt]
        report_timing_summary -delay_type min_max -report_unconstrained -file [file join $directory timing_summary.rpt]
        netlist_snapshot::export [file join $directory snapshot.tsv]
        puts "NETLIST_APPLY_COMPLETE nets=[dict size $routes] elapsed_ms=$elapsed directory=$directory"
    }
}
