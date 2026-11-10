# Observe physical net associations and manual-routing query context.
# Never set SITE_PIPS or inversion/config values. Restore the original DCP on all exits.
set clk_conn_root /inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/A_graph_compression
set clk_conn_base $clk_conn_root/data/netlist/site_full_applied_20261023_v1/routed.dcp
set clk_conn_probe $clk_conn_root/data/netlist/clock_row_route_probe_full_20261023_v2/routed.dcp
set clk_conn_dir $clk_conn_root/data/netlist/clock_connectivity_observation_20261023_v1
if {[file exists $clk_conn_dir]} {error "Refusing existing connectivity capture"}
file mkdir $clk_conn_dir
proc clk_conn_line {f args} {
    foreach x $args {if {[regexp {[\t\r\n]} $x]} {error "Invalid TSV field"}}
    puts $f [join $args "\t"]
}
proc clk_conn_nets {f kind name object} {
    set nets [get_nets -of_objects $object]
    clk_conn_line $f net_count $kind $name [llength $nets]
    foreach net $nets {clk_conn_line $f net $kind $name [get_property NAME $net] [get_property TYPE $net]}
}
proc clk_conn_capture {stage checkpoint} {
    global clk_conn_dir
    open_checkpoint $checkpoint
    set f [open $clk_conn_dir/$stage.tsv {WRONLY CREAT EXCL}]
    clk_conn_line $f meta schema clock_connectivity_v1
    clk_conn_line $f meta stage $stage
    clk_conn_line $f meta checkpoint $checkpoint
    clk_conn_line $f meta part [get_property PART [current_design]]
    foreach site_name {BUFCE_ROW_FSR_X21Y6 BUFCE_LEAF_X110Y26} {
        set site [get_sites $site_name]
        if {[llength $site]!=1} {error "Expected clock site absent"}
        clk_conn_line $f site $site_name [get_property SITE_TYPE $site]
        foreach pin [get_bel_pins -of_objects $site] {
            clk_conn_nets $f bel_pin [get_property NAME $pin] $pin
        }
        foreach pin [get_site_pins -of_objects $site] {
            set pin_name [get_property NAME $pin]
            clk_conn_nets $f site_pin $pin_name $pin
            foreach node [get_nodes -of_objects $pin] {
                set node_name [get_property NAME $node]
                clk_conn_line $f pin_node $pin_name $node_name
                clk_conn_nets $f node $node_name $node
                foreach prop [list_property $node] {
                    clk_conn_line $f node_property $node_name $prop [get_property $prop $node]
                }
            }
        }
        set before [get_property MANUAL_ROUTING $site]
        foreach context {default manual restored} {
            if {$context eq "manual"} {set_property MANUAL_ROUTING [get_property SITE_TYPE $site] $site}
            if {$context eq "restored"} {set_property MANUAL_ROUTING $before $site}
            clk_conn_line $f context $site_name $context [get_property MANUAL_ROUTING $site] [get_property SITE_PIPS $site]
            foreach bel [get_bels -of_objects $site -include_routing_bels -include_routethru_bels] {
                set bel_name [get_property NAME $bel]
                foreach prop [list_property $bel] {
                    clk_conn_line $f context_property $site_name $context $bel_name $prop [get_property $prop $bel]
                }
                if {[string match *INV $bel_name]} {
                    set invert [get_property IS_INVERTED $bel]
                    clk_conn_line $f inversion_getter $site_name $context $bel_name $invert
                }
            }
        }
    }
    clk_conn_line $f complete $stage
    close $f
}
set clk_conn_status [catch {
    clk_conn_capture baseline $clk_conn_base
    clk_conn_capture probe $clk_conn_probe
} clk_conn_error]
set clk_conn_restore [catch {open_checkpoint $clk_conn_base} clk_conn_restore_error]
if {$clk_conn_restore} {error "Original checkpoint restore failed: $clk_conn_restore_error"}
if {$clk_conn_status} {error "Connectivity capture failed: $clk_conn_error"}
puts CLOCK_CONNECTIVITY_CAPTURED_AND_BASELINE_RESTORED
