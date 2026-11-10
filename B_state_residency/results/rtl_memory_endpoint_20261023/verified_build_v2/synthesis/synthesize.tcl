set_param general.maxThreads 2
read_verilog -sv {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/rtl_memory_endpoint_20261023/verified_build_v2/sources/hardware/rtl/bounded_sync_fifo.sv}
read_verilog -sv {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/rtl_memory_endpoint_20261023/verified_build_v2/sources/hardware/rtl/scratch_frame_store_bram.sv}
read_verilog -sv {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/rtl_memory_endpoint_20261023/verified_build_v2/sources/hardware/rtl/scratch_page_controller.sv}
read_verilog -sv {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/rtl_memory_endpoint_20261023/verified_build_v2/sources/hardware/rtl/queued_scratch_endpoint.sv}
read_verilog -sv {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/rtl_memory_endpoint_20261023/verified_build_v2/sources/hardware/rtl/scratch_page_axi.sv}
read_verilog -sv {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/rtl_memory_endpoint_20261023/verified_build_v2/sources/hardware/rtl/backing_frame_directory_lookup.sv}
read_verilog -sv {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/rtl_memory_endpoint_20261023/verified_build_v2/sources/hardware/rtl/backing_page_service_lookup.sv}
read_verilog -sv {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/rtl_memory_endpoint_20261023/verified_build_v2/sources/hardware/rtl/scratch_page_codec.sv}
read_verilog -sv {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/rtl_memory_endpoint_20261023/verified_build_v2/sources/hardware/rtl/record_backing_service.sv}
read_verilog -sv {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/rtl_memory_endpoint_20261023/verified_build_v2/sources/hardware/rtl/memory_scratch_endpoint.sv}
read_xdc {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/rtl_memory_endpoint_20261023/verified_build_v2/sources/hardware/rtl/scratch_frame_store.xdc}
synth_design -top memory_scratch_endpoint -part xcu280-fsvh2892-2L-e -mode out_of_context
report_utilization -file utilization.rpt
report_utilization -hierarchical -file utilization_hierarchical.rpt
write_checkpoint memory_scratch_endpoint.dcp
set b_rams [get_cells -hier -filter {REF_NAME =~ RAMB*}]
set b_file [open ram_cells.txt w]
foreach b_cell $b_rams {puts $b_file "$b_cell [get_property REF_NAME $b_cell]"}
close $b_file
if {[llength $b_rams] == 0} {error "Endpoint BRAM not inferred"}
puts "B_MEMORY_ENDPOINT_SYNTH_PASS ram_cells=[llength $b_rams]"
exit
