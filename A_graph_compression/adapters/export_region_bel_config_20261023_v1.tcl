set bel_root /inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/A_graph_compression
close_design
open_checkpoint $bel_root/data/netlist/routeracc_cost_u280_20261022_v1/routed.dcp
set f [open $bel_root/data/raw/region_u280_20261022_v1/selection/tiles.txt]
set bel_tiles [split [string trim [read $f]] \n]
close $f
set bel_sites [get_sites -quiet -of_objects [get_tiles $bel_tiles]]
set f [open $bel_root/data/raw/region_u280_20261022_v1/bel_config.tsv {WRONLY CREAT EXCL}]
puts $f "meta\tschema\tregion_bel_config_v1"
puts $f "meta\tpart\t[get_property PART [current_design]]"
puts $f "meta\ttool\t[version -short]"
set bel_count 0
set bel_configs 0
foreach site $bel_sites {
    foreach bel [get_bels -quiet -of_objects $site] {
        puts $f [join [list bel [get_property NAME $bel] [get_property IS_USED $bel] [get_property TYPE $bel]] "\t"]
        incr bel_count
        foreach prop [list_property $bel] {
            if {![string match CONFIG.* $prop] || [string match *.DEFAULT $prop] || [string match *.VALUES $prop]} {continue}
            set value [get_property $prop $bel]
            if {[regexp {[\t\r\n]} $value]} {error "Unsupported configuration control character"}
            puts $f [join [list config [get_property NAME $bel] $prop $value] "\t"]
            incr bel_configs
        }
    }
}
puts $f "complete\t$bel_count\t$bel_configs"
close $f
puts "REGION_BEL_CONFIG_COMPLETE bels=$bel_count configs=$bel_configs"
