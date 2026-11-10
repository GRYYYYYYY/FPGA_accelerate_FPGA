set root /inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/A_graph_compression
set out $root/data/netlist/clock_row_route_probe_full_20261023_v2
if {[file exists $out]} {error "Refusing existing output"}
file mkdir $out
set_param general.maxThreads 1
open_checkpoint $root/data/netlist/routeracc_cost_u280_20261022_v1/routed.dcp
proc lut_pin_mapping {path} {
    set out [open $path {WRONLY CREAT EXCL}]
    set mapping [dict create]
    foreach cell [get_cells -hier -filter {REF_NAME =~ LUT*}] {
        set name [get_property NAME $cell]
        set pairs {}
        foreach pin [get_pins -of_objects $cell -filter {DIRECTION == IN}] {
            set logical [lindex [split [get_property NAME $pin] /] end]
            set physical {}
            foreach bel_pin [get_bel_pins -of_objects $pin] {lappend physical [lindex [split [get_property NAME $bel_pin] /] end]}
            set physical [lsort -unique $physical]
            if {[llength $physical]!=1 || ![regexp {^I[0-5]$} $logical] || ![regexp {^A[1-6]$} [lindex $physical 0]]} {error "Ambiguous LUT mapping $name/$logical $physical"}
            lappend pairs $logical:[lindex $physical 0]
        }
        set pairs [lsort $pairs]
        if {[llength $pairs]==0} {error "Empty LUT input mapping $name"}
        dict set mapping $name $pairs
        puts $out [join [list cell $name [get_property REF_NAME $cell] [get_property LOC $cell] [get_property BEL $cell] [get_property INIT $cell] $pairs [get_property LOCK_PINS $cell]] "\t"]
    }
    puts $out "complete\t[dict size $mapping]"
    close $out
    return $mapping
}
set baseline_mapping [lut_pin_mapping $out/lut_pins_baseline.tsv]
open_checkpoint $root/data/netlist/clock_row_route_probe_20261023_v1/routed.dcp
set isolated_mapping [lut_pin_mapping $out/lut_pins_isolated.tsv]
if {[dict size $baseline_mapping]!=[dict size $isolated_mapping]} {error "LUT domain changed"}
dict for {name pins} $baseline_mapping {
    if {$pins ne [dict get $isolated_mapping $name]} {error "Isolated pin mapping differs from original: $name"}
    set_property LOCK_PINS $pins [get_cells [list $name]]
}

source $root/adapters/netlist_snapshot.tcl
set probe_net {original_cost/genblk1[3].h_val_y_reg[55]_i_2_n_0}
set names {}
set input [open $root/data/derived/region_all_nets_cap8_20261022_v1/candidate_routes.tsv]
while {[gets $input line]>=0} {
    set fields [split $line "\t"]
    if {[lindex $fields 0] eq "net" && [lindex $fields 1] ne $probe_net} {lappend names [netlist_snapshot::exact_net [lindex $fields 1]]}
}
close $input
if {[llength $names]!=1061} {error "Probe complement differs"}
route_design -nets $names
set routed_mapping [lut_pin_mapping $out/lut_pins_routed.tsv]
netlist_snapshot::export $out/snapshot.tsv
report_route_status -file $out/route_status.rpt
report_drc -file $out/drc.rpt
report_timing_summary -file $out/timing_summary.rpt
write_checkpoint $out/routed.dcp
puts CLOCK_ROW_FULL_CONTEXT_COMPLETE
