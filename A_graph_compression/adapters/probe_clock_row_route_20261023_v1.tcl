set root /inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/A_graph_compression
set out $root/data/netlist/clock_row_route_probe_20261023_v1
if {[file exists $out]} {error "Refusing existing output"}
file mkdir $out
set_param general.maxThreads 1
open_checkpoint $root/data/netlist/routeracc_cost_u280_20261022_v1/routed.dcp
source $root/adapters/netlist_snapshot.tcl
set probe_net {original_cost/genblk1[3].h_val_y_reg[55]_i_2_n_0}
set probe_sites {BUFCE_LEAF_X110Y26 BUFCE_ROW_FSR_X21Y6}
set probe_route {CLEM_X12Y391/CLE_CLE_M_SITE_0_CMUX INT_X12Y391/INT_NODE_SDQ_90_INT_OUT1 INT_X12Y391/SS2_W_BEG7 RCLK_INT_L_X12Y389/INT_NODE_IMUX_14_INT_OUT0 RCLK_INT_L_X12Y389/INT_RCLK_TO_CLK_LEFT_0_3 RCLK_CLEM_L_X12Y389/CLK_BUFCE_ROW_FSR_0_CLK_OUT RCLK_CLEM_L_X12Y389/CLK_TEST_BUF_SITE_1_CLK_IN RCLK_INT_L_X13Y389/CLK_LEAF_SITES_19_CLK_IN RCLK_INT_L_X13Y389/CLK_LEAF_SITES_19_CLK_LEAF INT_X13Y392/INT_NODE_GLOBAL_9_INT_OUT0 INT_X13Y392/INT_NODE_IMUX_37_INT_OUT1 INT_X13Y392/IMUX_W22}
set f [open $out/configuration.tsv {WRONLY CREAT EXCL}]
proc row_probe_config {stage} {
    global f probe_sites
    foreach site_name $probe_sites {
        set site [get_sites $site_name]
        foreach b [get_bels -of_objects $site] {
            foreach p [list_property $b] {
                if {[string match CONFIG.* $p]} {netlist_snapshot::row $f config $stage [get_property NAME $b] $p [get_property $p $b]}
            }
        }
        foreach p [get_site_pips -of_objects $site] {
            foreach prop [list_property $p] {netlist_snapshot::row $f site_pip $stage [get_property NAME $p] $prop [get_property $prop $p]}
        }
        foreach pin [get_site_pins -of_objects $site] {
            netlist_snapshot::row $f site_pin $stage [get_property NAME $pin] [get_property IS_USED $pin]
        }
    }
    flush $f
}
row_probe_config baseline
set names {}
set input [open $root/data/derived/region_all_nets_cap8_20261022_v1/candidate_routes.tsv]
while {[gets $input line]>=0} {set fields [split $line "\t"];if {[lindex $fields 0] eq "net"} {lappend names [netlist_snapshot::exact_net [lindex $fields 1]]}}
close $input
if {[llength $names]!=1062} {error "Query scope changed"}
route_design -unroute -nets $names
row_probe_config unrouted
set code [catch {set_property FIXED_ROUTE $probe_route [netlist_snapshot::exact_net $probe_net]} message]
row_probe_config applied
netlist_snapshot::row $f status $probe_net [get_property ROUTE_STATUS [netlist_snapshot::exact_net $probe_net]]
netlist_snapshot::row $f apply_exit $code [string map [list "\n" { } "\r" { } "\t" { }] $message]
puts $f complete
close $f
netlist_snapshot::export $out/snapshot.tsv
report_route_status -of_objects [netlist_snapshot::exact_net $probe_net] -file $out/route_status.rpt
report_drc -file $out/drc.rpt
write_checkpoint $out/routed.dcp
puts "CLOCK_ROW_PROBE_COMPLETE apply_exit=$code"
