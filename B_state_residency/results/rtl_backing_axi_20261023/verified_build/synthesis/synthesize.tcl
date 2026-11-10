set_param general.maxThreads 2
read_verilog -sv {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/rtl_backing_axi_20261023/verified_build/sources/hardware/rtl/scratch_page_axi.sv}
read_verilog -sv {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/rtl_backing_axi_20261023/verified_build/sources/hardware/rtl/backing_frame_directory.sv}
read_verilog -sv {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/rtl_backing_axi_20261023/verified_build/sources/hardware/rtl/backing_page_service.sv}
read_xdc {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/rtl_backing_axi_20261023/verified_build/sources/hardware/rtl/scratch_frame_store.xdc}
synth_design -top backing_page_service -part xcu280-fsvh2892-2L-e -mode out_of_context
report_utilization -file utilization.rpt
write_checkpoint backing_page_service.dcp
set b_rams [get_cells -hier -filter {REF_NAME =~ RAMB*}]
set b_file [open ram_cells.txt w]
foreach b_cell $b_rams {puts $b_file "$b_cell [get_property REF_NAME $b_cell]"}
close $b_file
if {[llength $b_rams] == 0} {error "Directory BRAM was not inferred"}
puts "B_BACKING_SYNTH_PASS ram_cells=[llength $b_rams]"
exit
