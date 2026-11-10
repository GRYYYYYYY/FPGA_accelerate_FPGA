# Loaded only after restoring the original baseline, with maxThreads=1.
set site_full_root /inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/A_graph_compression
set site_full_out $site_full_root/data/netlist/site_full_applied_20261023_v1
set site_full_code [catch {
    netlist_apply::apply $site_full_root/data/derived/site_routing_all_known_instances_20261023_v1/candidate_routes.tsv $site_full_out
} site_full_message site_full_options]
if {$site_full_code} {
    if {[file isdirectory $site_full_out]} {
        set site_full_stream [open [file join $site_full_out failure.txt] {WRONLY CREAT EXCL}]
        puts $site_full_stream $site_full_message
        puts $site_full_stream [dict get $site_full_options -errorinfo]
        close $site_full_stream
        report_route_status -file [file join $site_full_out failure_route_status.rpt]
        report_drc -file [file join $site_full_out failure_drc.rpt]
        netlist_snapshot::export [file join $site_full_out failure_snapshot.tsv]
    }
    return -options $site_full_options $site_full_message
}
