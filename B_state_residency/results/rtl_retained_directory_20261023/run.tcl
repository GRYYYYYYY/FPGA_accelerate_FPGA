set b_out {/inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/B_state_residency/results/rtl_retained_directory_20261023}
create_project retained_directory $b_out/project -part xcu280-fsvh2892-2L-e -force
add_files $b_out/backing_frame_directory_retained.sv
add_files -fileset sim_1 $b_out/tb_retained_directory.sv
set_property top tb_retained_directory [get_filesets sim_1]
set_property target_simulator XSim [current_project]
set_property xsim.simulate.runtime 10ms [get_filesets sim_1]
update_compile_order -fileset sim_1
launch_simulation -mode behavioral
close_sim
close_project
puts RETAINED_DIRECTORY_FLOW_DONE
