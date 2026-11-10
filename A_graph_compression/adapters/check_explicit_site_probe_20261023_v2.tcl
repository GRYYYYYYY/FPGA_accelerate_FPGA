set root /inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/A_graph_compression
set out $root/data/netlist/explicit_site_probe_20261023_v2
if {[file exists $out]} {error "Refusing existing output"}
file mkdir $out
set_param general.maxThreads 1
open_checkpoint $root/build/site_ownership/explicit_site_probe_20261023_v2.dcp
source $root/adapters/netlist_snapshot.tcl
set net [netlist_snapshot::exact_net {cg_q[2]}]
report_route_status -of_objects $net -file $out/cg2_route_status.rpt
report_drc -file $out/drc.rpt
set f [open $out/probe.tsv {WRONLY CREAT EXCL}]
puts $f "status\t[get_property ROUTE_STATUS $net]"
puts $f "equation\t[get_property CONFIG.EQN [get_bels SLICE_X22Y411/G6LUT]]"
puts $f "complete"
close $f
netlist_snapshot::export $out/snapshot.tsv
puts EXPLICIT_SITE_VIVADO_CHECK_COMPLETE
