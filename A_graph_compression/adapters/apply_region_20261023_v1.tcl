set region_root /inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/A_graph_compression
if {[llength [get_designs -quiet]]} {close_design}
open_checkpoint $region_root/data/netlist/routeracc_cost_u280_20261022_v1/routed.dcp
source $region_root/adapters/netlist_snapshot.tcl
source $region_root/adapters/apply_netlist_routes.tcl
netlist_apply::apply $region_root/data/derived/region_all_nets_cap8_20261022_v1/candidate_routes.tsv $region_root/data/netlist/region_cap8_applied_20261023_v1
