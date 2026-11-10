set pseudo_root /inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/A_graph_compression
set f [open $pseudo_root/data/raw/region_u280_20261022_v1/pseudo_tiles.txt]
set pseudo_tiles [split [string trim [read $f]] \n]
close $f
set f [open $pseudo_root/data/raw/region_u280_20261022_v1/pseudo_sites.tsv {WRONLY CREAT EXCL}]
puts $f "meta\tschema\tpseudo_tile_sites_v1"
set count 0
foreach tile_name $pseudo_tiles {
    foreach site [get_sites -quiet -of_objects [get_tiles $tile_name]] {
        puts $f [join [list site $tile_name [get_property NAME $site] [get_property SITE_TYPE $site]] "\t"]
        incr count
    }
}
puts $f "complete\t$count"
close $f
puts "PSEUDO_SITES_COMPLETE records=$count"
