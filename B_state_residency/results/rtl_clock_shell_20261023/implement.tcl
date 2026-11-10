set b_out {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/rtl_clock_shell_20261023}
set b_rtl {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/rtl_clock_shell_20261023/sources/hardware/rtl}
set_param general.maxThreads 2
puts "B_CLOCK_SHELL_BEGIN version=[version -short]"
foreach {b_variant b_suffix} {baseline {} wide _wide} {
    set b_dir [file join $b_out $b_variant]
    if {[file exists $b_dir]} {error "Refuse overwrite $b_dir"}
    file mkdir $b_dir
    create_project -in_memory -part xcu280-fsvh2892-2L-e
    read_verilog -sv [file join $b_rtl bounded_sync_fifo.sv]
    read_verilog -sv [file join $b_rtl scratch_frame_store_bram.sv]
    read_verilog -sv [file join $b_rtl scratch_page_controller.sv]
    read_verilog -sv [file join $b_rtl queued_scratch_endpoint.sv]
    read_verilog -sv [file join $b_rtl scratch_page_axi.sv]
    read_verilog -sv [file join $b_rtl backing_frame_directory_lookup.sv]
    read_verilog -sv [file join $b_rtl backing_page_service_lookup.sv]
    read_verilog -sv [file join $b_rtl scratch_page_codec${b_suffix}.sv]
    read_verilog -sv [file join $b_rtl record_backing_service${b_suffix}.sv]
    read_verilog -sv [file join $b_rtl memory_scratch_endpoint${b_suffix}.sv]
    read_verilog -sv [file join $b_rtl clock_shell_${b_variant}.sv]
    read_xdc [file join $b_rtl clock_shell.xdc]
    synth_design -top clock_shell_${b_variant} -part xcu280-fsvh2892-2L-e -mode out_of_context
    if {[llength [get_cells -hier -filter {REF_NAME =~ BUFG*}]] != 1} {error "Expected one BUFG"}
    if {[llength [get_pins b_clock/O]] != 1} {error "Missing reference clock pin"}
    write_checkpoint [file join $b_dir synthesized.dcp]
    report_timing_summary -check_timing_verbose -report_unconstrained -max_paths 5 -file [file join $b_dir timing_synth.rpt]
    opt_design
    place_design -directive Default
    route_design -directive Default
    report_methodology -file [file join $b_dir methodology.rpt]
    report_timing_summary -check_timing_verbose -report_unconstrained -max_paths 10 -file [file join $b_dir timing_routed.rpt]
    report_route_status -file [file join $b_dir route_status.rpt]
    report_drc -file [file join $b_dir drc.rpt]
    report_clock_utilization -file [file join $b_dir clock_utilization.rpt]
    report_utilization -file [file join $b_dir utilization.rpt]
    write_xdc [file join $b_dir constraints.xdc]
    write_checkpoint [file join $b_dir routed.dcp]
    set b_file [open [file join $b_dir clock_network.tsv] w]
    puts $b_file "buffer	type	location	output_net	route_status"
    foreach b_buf [get_cells -hier -filter {REF_NAME =~ BUFG*}] {
        set b_net [get_nets -of_objects [get_pins $b_buf/O]]
        puts $b_file "$b_buf	[get_property REF_NAME $b_buf]	[get_property LOC $b_buf]	$b_net	[get_property ROUTE_STATUS $b_net]"
    }
    close $b_file
    set b_in [get_ports -filter {DIRECTION == IN && NAME != clk}]
    set b_outports [get_ports -filter {DIRECTION == OUT}]
    set b_regs [all_registers]
    set b_file [open [file join $b_dir paths.tsv] w]
    puts $b_file "group	delay_type	slack_ns	startpoint	endpoint	datapath_delay_ns	requirement_ns"
    foreach b_group {internal input output feedthrough} {
        switch $b_group {
            internal {set b_from $b_regs; set b_to $b_regs}
            input {set b_from $b_in; set b_to $b_regs}
            output {set b_from $b_regs; set b_to $b_outports}
            feedthrough {set b_from $b_in; set b_to $b_outports}
        }
        foreach b_delay {max min} {
            report_timing -from $b_from -to $b_to -delay_type $b_delay -max_paths 5 -path_type full_clock_expanded -file [file join $b_dir ${b_group}_${b_delay}.rpt]
            foreach b_path [get_timing_paths -from $b_from -to $b_to -delay_type $b_delay -max_paths 5] {
                puts $b_file "$b_group	$b_delay	[get_property SLACK $b_path]	[get_property STARTPOINT_PIN $b_path]	[get_property ENDPOINT_PIN $b_path]	[get_property DATAPATH_DELAY $b_path]	[get_property REQUIREMENT $b_path]"
            }
        }
    }
    close $b_file
    set b_file [open [file join $b_dir completed.txt] w]
    puts $b_file "B_CLOCK_SHELL_VARIANT_DONE $b_variant version=[version -short]"
    close $b_file
    puts "B_CLOCK_SHELL_VARIANT_DONE $b_variant"
    close_project
}
puts "B_CLOCK_SHELL_PAIR_DONE"
