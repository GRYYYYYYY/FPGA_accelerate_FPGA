set root /inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/A_graph_compression
set out $root/data/netlist/rw_roundtrip_20261023_v1
if {[file exists $out]} {error "Refusing existing output"}
file mkdir $out
set_param general.maxThreads 1
open_checkpoint $root/build/site_ownership/baseline_roundtrip_20261023_v1.dcp
set f [open $out/cells.tsv {WRONLY CREAT EXCL}]
set count 0
foreach cell [get_cells -hier -filter {IS_PRIMITIVE}] {
    puts $f [join [list cell [get_property NAME $cell] [get_property REF_NAME $cell] [get_property LOC $cell] [get_property BEL $cell]] "\t"]
    incr count
}
puts $f "complete\t$count"
close $f
report_route_status -file $out/route_status.rpt
report_drc -file $out/drc.rpt
puts BASELINE_ROUNDTRIP_VIVADO_CHECK_COMPLETE
