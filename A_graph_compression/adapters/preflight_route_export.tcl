# Read the directed endpoints of reference PIPs for FIXED_ROUTE API preflight.
namespace eval netlist_preflight {
    proc export {selection path} {
        set f [open $selection];set names [split [string trim [read $f]] \n];close $f
        set out [open $path {WRONLY CREAT EXCL}]
        set count 0
        foreach name $names {
            set net [netlist_snapshot::exact_net $name]
            set segments [get_nets -segments [list $name]]
            foreach pip [get_pips -of_objects $segments] {
                set up [get_wires -uphill -of_objects $pip]
                set down [get_wires -downhill -of_objects $pip]
                if {[llength $up] != 1 || [llength $down] != 1} {error "Ambiguous PIP endpoints"}
                set un [get_nodes -of_objects $up];set dn [get_nodes -of_objects $down]
                if {[llength $un] != 1 || [llength $dn] != 1} {error "Ambiguous canonical endpoints"}
                netlist_snapshot::row $out pip $name [get_property NAME $pip] [get_property NAME $un] [get_property NAME $dn] [get_property IS_DIRECTIONAL $pip] [get_property NAME $up] [get_property NAME $down]
                incr count
            }
        }
        netlist_snapshot::row $out complete [llength $names] $count
        close $out
        puts "PREFLIGHT_EXPORT_COMPLETE nets=[llength $names] pips=$count"
    }
}
