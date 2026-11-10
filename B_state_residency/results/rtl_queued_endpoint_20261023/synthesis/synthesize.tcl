set_param general.maxThreads 2
read_verilog -sv {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/rtl_queued_endpoint_20261023/sources/hardware/rtl/bounded_sync_fifo.sv}
read_verilog -sv {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/rtl_queued_endpoint_20261023/sources/hardware/rtl/scratch_frame_store_bram.sv}
read_verilog -sv {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/rtl_queued_endpoint_20261023/sources/hardware/rtl/scratch_page_controller.sv}
read_verilog -sv {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/rtl_queued_endpoint_20261023/sources/hardware/rtl/queued_scratch_endpoint.sv}
read_xdc {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/rtl_queued_endpoint_20261023/sources/hardware/rtl/scratch_frame_store.xdc}
synth_design -top queued_scratch_endpoint -part xcu280-fsvh2892-2L-e -mode out_of_context
report_utilization -file utilization.rpt
write_checkpoint queued_scratch_endpoint.dcp
set b_rams [get_cells -hier -filter {REF_NAME =~ RAMB*}]
set b_file [open ram_cells.txt w]
foreach b_cell $b_rams {puts $b_file "$b_cell [get_property REF_NAME $b_cell]"}
close $b_file
if {[llength $b_rams] != 2} {error "Expected two page block RAMs"}
puts "B_QUEUED_SYNTH_PASS ram_cells=[llength $b_rams]"
exit
