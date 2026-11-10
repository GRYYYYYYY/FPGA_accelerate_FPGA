set root /inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/A_graph_compression
set_param general.maxThreads 1
open_checkpoint $root/data/netlist/routeracc_cost_u280_20261022_v1/routed.dcp
set f [open $root/data/raw/region_u280_20261022_v1/site_pip_property_probe.tsv {WRONLY CREAT EXCL}]
set count 0
foreach site_name {SLICE_X22Y411 BUFCE_LEAF_X115Y26} {
    foreach pip [get_site_pips -of_objects [get_sites $site_name]] {
        set name [get_property NAME $pip]
        foreach prop [list_property $pip] {
            set value [get_property $prop $pip]
            if {[regexp {[\t\r\n]} $value]} {error "Control characters in site PIP property"}
            puts $f [join [list property $site_name $name $prop $value] "\t"]
        }
        incr count
    }
}
puts $f "complete\t$count"
close $f
puts "SITE_PIP_PROPERTY_PROBE_COMPLETE pips=$count"
