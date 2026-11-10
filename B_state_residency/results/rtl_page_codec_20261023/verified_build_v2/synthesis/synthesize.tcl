set_param general.maxThreads 2
read_verilog -sv {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/rtl_page_codec_20261023/verified_build_v2/sources/hardware/rtl/scratch_page_codec.sv}
read_xdc {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/rtl_page_codec_20261023/verified_build_v2/sources/hardware/rtl/scratch_frame_store.xdc}
synth_design -top scratch_page_codec -part xcu280-fsvh2892-2L-e -mode out_of_context
report_utilization -file utilization.rpt
write_checkpoint scratch_page_codec.dcp
set b_rams [get_cells -hier -filter {REF_NAME =~ RAMB*}]
set b_file [open ram_cells.txt w]
foreach b_cell $b_rams {puts $b_file "$b_cell [get_property REF_NAME $b_cell]"}
close $b_file
if {[llength $b_rams] == 0} {error "Codec BRAM was not inferred"}
puts "B_CODEC_SYNTH_PASS ram_cells=[llength $b_rams]"
exit
