# Exhaustive property observation only. Restore original checkpoint even on error.
set clock_properties_root /inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/A_graph_compression
set clock_properties_baseline $clock_properties_root/data/netlist/site_full_applied_20261023_v1/routed.dcp
set clock_properties_probe $clock_properties_root/data/netlist/clock_row_route_probe_full_20261023_v2/routed.dcp
set clock_properties_dir $clock_properties_root/data/netlist/clock_property_observation_20261023_v1
file mkdir $clock_properties_dir
proc clock_properties_line {stream args} {
    foreach value $args {if {[regexp {[\t\r\n]} $value]} {error "Non-TSV property value"}}
    puts $stream [join $args "\t"]
}
proc clock_properties_capture {stage checkpoint} {
    global clock_properties_dir
    open_checkpoint $checkpoint
    set stream [open $clock_properties_dir/$stage.tsv {WRONLY CREAT EXCL}]
    clock_properties_line $stream meta stage $stage
    clock_properties_line $stream meta checkpoint $checkpoint
    clock_properties_line $stream meta part [get_property PART [current_design]]
    clock_properties_line $stream meta get_site_wires_available [expr {[llength [info commands get_site_wires]] > 0}]
    set objects 0
    set properties 0
    set errors 0
    foreach name {BUFCE_ROW_FSR_X21Y6 BUFCE_LEAF_X110Y26} {
        set site [get_sites $name]
        if {[llength $site] != 1} {error "Clock site absent"}
        foreach kind {site bel bel_pin site_pin site_pip} {
            switch $kind {
                site {set collection $site}
                bel {set collection [get_bels -of_objects $site -include_routing_bels -include_routethru_bels]}
                bel_pin {set collection [get_bel_pins -of_objects $site]}
                site_pin {set collection [get_site_pins -of_objects $site]}
                site_pip {set collection [get_site_pips -of_objects $site]}
            }
            foreach object $collection {
                set object_name [get_property NAME $object]
                clock_properties_line $stream object $kind $object_name
                incr objects
                foreach prop [list_property $object] {
                    if {[catch {get_property $prop $object} value]} {
                        clock_properties_line $stream property_error $kind $object_name $prop $value
                        incr errors
                    } else {
                        clock_properties_line $stream property $kind $object_name $prop $value
                        incr properties
                    }
                }
            }
        }
    }
    clock_properties_line $stream complete $stage $objects $properties $errors
    close $stream
}
set clock_properties_code [catch {
    clock_properties_capture baseline $clock_properties_baseline
    clock_properties_capture probe $clock_properties_probe
} clock_properties_message]
set clock_properties_restore_code [catch {open_checkpoint $clock_properties_baseline} clock_properties_restore_message]
if {$clock_properties_restore_code} {error "Baseline restore failed: $clock_properties_restore_message"}
if {$clock_properties_code} {error "Property capture failed: $clock_properties_message"}
puts CLOCK_PROPERTIES_CAPTURED_AND_BASELINE_RESTORED
