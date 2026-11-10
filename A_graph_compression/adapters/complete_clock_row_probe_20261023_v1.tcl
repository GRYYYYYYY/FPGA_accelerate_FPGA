set root /inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/A_graph_compression
set out $root/data/netlist/clock_row_route_probe_full_20261023_v1
if {[file exists $out]} {error "Refusing existing output"}
file mkdir $out
set_param general.maxThreads 1
open_checkpoint $root/data/netlist/clock_row_route_probe_20261023_v1/routed.dcp
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
netlist_snapshot::export $out/snapshot.tsv
report_route_status -file $out/route_status.rpt
report_drc -file $out/drc.rpt
report_timing_summary -file $out/timing_summary.rpt
write_checkpoint $out/routed.dcp
puts CLOCK_ROW_FULL_CONTEXT_COMPLETE
