set row_config_root /inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/A_graph_compression
set row_config_out [open $row_config_root/data/netlist/clock_row_route_probe_full_20261023_v1/configuration.tsv {WRONLY CREAT EXCL}]
foreach row_site_name {BUFCE_ROW_FSR_X21Y6 BUFCE_LEAF_X110Y26} {
    foreach row_bel [get_bels -of_objects [get_sites $row_site_name]] {
        foreach row_prop [list_property $row_bel] {
            if {[string match CONFIG.* $row_prop]} {puts $row_config_out [join [list config full_context [get_property NAME $row_bel] $row_prop [get_property $row_prop $row_bel]] "\t"]}
        }
    }
}
puts $row_config_out complete
close $row_config_out
puts CLOCK_ROW_FULL_CONFIG_COMPLETE
