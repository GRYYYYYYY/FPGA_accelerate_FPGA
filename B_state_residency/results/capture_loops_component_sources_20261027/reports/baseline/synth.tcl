set_param general.maxThreads 2
puts [list VIVADO_VERSION [version -short]]
read_verilog -sv {/tmp/B_state_residency_offer_20261025/capture_loops_component_v1/sources/baseline/children_frames.sv}
read_verilog -sv {/tmp/B_state_residency_offer_20261025/capture_loops_component_v1/sources/baseline/expansion_capture.sv}
read_verilog -sv {/tmp/B_state_residency_offer_20261025/capture_loops_component_v1/sources/baseline/recursive_candidate_controller.sv}
read_verilog -sv {/tmp/B_state_residency_offer_20261025/capture_loops_component_v1/sources/capture_loop_slice.sv}
synth_design -mode out_of_context -top capture_loop_slice -part xcu280-fsvh2892-2L-e
create_clock -period 10.000 -name core_clk [get_ports clk]
report_drc -no_waivers -checks [get_drc_checks LUTLP-1] -file loops.rpt
check_timing -verbose -file check_timing.rpt
report_utilization -file utilization.rpt
set f [open facts.txt w]
puts $f [list loops [llength [get_drc_violations]] latches [llength [get_cells -hier -filter {REF_NAME =~ LD*}]] blackboxes [llength [get_cells -hier -filter {IS_BLACKBOX == 1}]] port_bits [llength [get_ports]]]
close $f
write_checkpoint -force synth.dcp
write_verilog -force synth.v
puts CAPTURE_LOOP_SYNTH_DONE
