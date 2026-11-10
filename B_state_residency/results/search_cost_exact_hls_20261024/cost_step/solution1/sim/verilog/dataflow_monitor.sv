
`include "dump_file_agent.svh"
`include "csv_file_dump.svh"
`include "sample_agent.svh"
`include "loop_sample_agent.svh"
`include "sample_manager.svh"
`include "nodf_module_interface.svh"
`include "nodf_module_monitor.svh"
`include "upc_loop_interface.svh"
`include "upc_loop_monitor.svh"
`timescale 1ns/1ps

// top module for dataflow related monitors
module dataflow_monitor(
input logic clock,
input logic reset,
input logic finish
);




    nodf_module_intf module_intf_1(clock,reset);
    assign module_intf_1.ap_start = AESL_inst_cost_step.ap_start;
    assign module_intf_1.ap_ready = AESL_inst_cost_step.ap_ready;
    assign module_intf_1.ap_done = AESL_inst_cost_step.ap_done;
    assign module_intf_1.ap_continue = 1'b1;
    assign module_intf_1.finish = finish;
    csv_file_dump mstatus_csv_dumper_1;
    nodf_module_monitor module_monitor_1;
    nodf_module_intf module_intf_2(clock,reset);
    assign module_intf_2.ap_start = AESL_inst_cost_step.grp_from_int_fu_295.ap_start;
    assign module_intf_2.ap_ready = AESL_inst_cost_step.grp_from_int_fu_295.ap_ready;
    assign module_intf_2.ap_done = AESL_inst_cost_step.grp_from_int_fu_295.ap_done;
    assign module_intf_2.ap_continue = 1'b1;
    assign module_intf_2.finish = finish;
    csv_file_dump mstatus_csv_dumper_2;
    nodf_module_monitor module_monitor_2;
    nodf_module_intf module_intf_3(clock,reset);
    assign module_intf_3.ap_start = AESL_inst_cost_step.grp_from_int_fu_295.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_start;
    assign module_intf_3.ap_ready = AESL_inst_cost_step.grp_from_int_fu_295.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_ready;
    assign module_intf_3.ap_done = AESL_inst_cost_step.grp_from_int_fu_295.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_done;
    assign module_intf_3.ap_continue = 1'b1;
    assign module_intf_3.finish = finish;
    csv_file_dump mstatus_csv_dumper_3;
    nodf_module_monitor module_monitor_3;
    nodf_module_intf module_intf_4(clock,reset);
    assign module_intf_4.ap_start = AESL_inst_cost_step.grp_from_int_fu_301.ap_start;
    assign module_intf_4.ap_ready = AESL_inst_cost_step.grp_from_int_fu_301.ap_ready;
    assign module_intf_4.ap_done = AESL_inst_cost_step.grp_from_int_fu_301.ap_done;
    assign module_intf_4.ap_continue = 1'b1;
    assign module_intf_4.finish = finish;
    csv_file_dump mstatus_csv_dumper_4;
    nodf_module_monitor module_monitor_4;
    nodf_module_intf module_intf_5(clock,reset);
    assign module_intf_5.ap_start = AESL_inst_cost_step.grp_from_int_fu_301.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_start;
    assign module_intf_5.ap_ready = AESL_inst_cost_step.grp_from_int_fu_301.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_ready;
    assign module_intf_5.ap_done = AESL_inst_cost_step.grp_from_int_fu_301.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_done;
    assign module_intf_5.ap_continue = 1'b1;
    assign module_intf_5.finish = finish;
    csv_file_dump mstatus_csv_dumper_5;
    nodf_module_monitor module_monitor_5;
    nodf_module_intf module_intf_6(clock,reset);
    assign module_intf_6.ap_start = AESL_inst_cost_step.grp_mul_fu_307.ap_start;
    assign module_intf_6.ap_ready = AESL_inst_cost_step.grp_mul_fu_307.ap_ready;
    assign module_intf_6.ap_done = AESL_inst_cost_step.grp_mul_fu_307.ap_done;
    assign module_intf_6.ap_continue = 1'b1;
    assign module_intf_6.finish = finish;
    csv_file_dump mstatus_csv_dumper_6;
    nodf_module_monitor module_monitor_6;
    nodf_module_intf module_intf_7(clock,reset);
    assign module_intf_7.ap_start = AESL_inst_cost_step.grp_mul_fu_307.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_start;
    assign module_intf_7.ap_ready = AESL_inst_cost_step.grp_mul_fu_307.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_ready;
    assign module_intf_7.ap_done = AESL_inst_cost_step.grp_mul_fu_307.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_done;
    assign module_intf_7.ap_continue = 1'b1;
    assign module_intf_7.finish = finish;
    csv_file_dump mstatus_csv_dumper_7;
    nodf_module_monitor module_monitor_7;
    nodf_module_intf module_intf_8(clock,reset);
    assign module_intf_8.ap_start = AESL_inst_cost_step.grp_mul_fu_315.ap_start;
    assign module_intf_8.ap_ready = AESL_inst_cost_step.grp_mul_fu_315.ap_ready;
    assign module_intf_8.ap_done = AESL_inst_cost_step.grp_mul_fu_315.ap_done;
    assign module_intf_8.ap_continue = 1'b1;
    assign module_intf_8.finish = finish;
    csv_file_dump mstatus_csv_dumper_8;
    nodf_module_monitor module_monitor_8;
    nodf_module_intf module_intf_9(clock,reset);
    assign module_intf_9.ap_start = AESL_inst_cost_step.grp_mul_fu_315.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_start;
    assign module_intf_9.ap_ready = AESL_inst_cost_step.grp_mul_fu_315.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_ready;
    assign module_intf_9.ap_done = AESL_inst_cost_step.grp_mul_fu_315.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_done;
    assign module_intf_9.ap_continue = 1'b1;
    assign module_intf_9.finish = finish;
    csv_file_dump mstatus_csv_dumper_9;
    nodf_module_monitor module_monitor_9;
    nodf_module_intf module_intf_10(clock,reset);
    assign module_intf_10.ap_start = AESL_inst_cost_step.grp_add_fu_325.ap_start;
    assign module_intf_10.ap_ready = AESL_inst_cost_step.grp_add_fu_325.ap_ready;
    assign module_intf_10.ap_done = AESL_inst_cost_step.grp_add_fu_325.ap_done;
    assign module_intf_10.ap_continue = 1'b1;
    assign module_intf_10.finish = finish;
    csv_file_dump mstatus_csv_dumper_10;
    nodf_module_monitor module_monitor_10;
    nodf_module_intf module_intf_11(clock,reset);
    assign module_intf_11.ap_start = AESL_inst_cost_step.grp_add_fu_325.grp_add_Pipeline_VITIS_LOOP_30_1_fu_185.ap_start;
    assign module_intf_11.ap_ready = AESL_inst_cost_step.grp_add_fu_325.grp_add_Pipeline_VITIS_LOOP_30_1_fu_185.ap_ready;
    assign module_intf_11.ap_done = AESL_inst_cost_step.grp_add_fu_325.grp_add_Pipeline_VITIS_LOOP_30_1_fu_185.ap_done;
    assign module_intf_11.ap_continue = 1'b1;
    assign module_intf_11.finish = finish;
    csv_file_dump mstatus_csv_dumper_11;
    nodf_module_monitor module_monitor_11;
    nodf_module_intf module_intf_12(clock,reset);
    assign module_intf_12.ap_start = AESL_inst_cost_step.grp_div_fu_333.ap_start;
    assign module_intf_12.ap_ready = AESL_inst_cost_step.grp_div_fu_333.ap_ready;
    assign module_intf_12.ap_done = AESL_inst_cost_step.grp_div_fu_333.ap_done;
    assign module_intf_12.ap_continue = 1'b1;
    assign module_intf_12.finish = finish;
    csv_file_dump mstatus_csv_dumper_12;
    nodf_module_monitor module_monitor_12;
    nodf_module_intf module_intf_13(clock,reset);
    assign module_intf_13.ap_start = AESL_inst_cost_step.grp_div_fu_333.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_start;
    assign module_intf_13.ap_ready = AESL_inst_cost_step.grp_div_fu_333.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_ready;
    assign module_intf_13.ap_done = AESL_inst_cost_step.grp_div_fu_333.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_done;
    assign module_intf_13.ap_continue = 1'b1;
    assign module_intf_13.finish = finish;
    csv_file_dump mstatus_csv_dumper_13;
    nodf_module_monitor module_monitor_13;
    nodf_module_intf module_intf_14(clock,reset);
    assign module_intf_14.ap_start = AESL_inst_cost_step.grp_div_fu_340.ap_start;
    assign module_intf_14.ap_ready = AESL_inst_cost_step.grp_div_fu_340.ap_ready;
    assign module_intf_14.ap_done = AESL_inst_cost_step.grp_div_fu_340.ap_done;
    assign module_intf_14.ap_continue = 1'b1;
    assign module_intf_14.finish = finish;
    csv_file_dump mstatus_csv_dumper_14;
    nodf_module_monitor module_monitor_14;
    nodf_module_intf module_intf_15(clock,reset);
    assign module_intf_15.ap_start = AESL_inst_cost_step.grp_div_fu_340.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_start;
    assign module_intf_15.ap_ready = AESL_inst_cost_step.grp_div_fu_340.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_ready;
    assign module_intf_15.ap_done = AESL_inst_cost_step.grp_div_fu_340.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_done;
    assign module_intf_15.ap_continue = 1'b1;
    assign module_intf_15.finish = finish;
    csv_file_dump mstatus_csv_dumper_15;
    nodf_module_monitor module_monitor_15;
    nodf_module_intf module_intf_16(clock,reset);
    assign module_intf_16.ap_start = AESL_inst_cost_step.grp_cost_step_Pipeline_VITIS_LOOP_18_1_fu_350.ap_start;
    assign module_intf_16.ap_ready = AESL_inst_cost_step.grp_cost_step_Pipeline_VITIS_LOOP_18_1_fu_350.ap_ready;
    assign module_intf_16.ap_done = AESL_inst_cost_step.grp_cost_step_Pipeline_VITIS_LOOP_18_1_fu_350.ap_done;
    assign module_intf_16.ap_continue = 1'b1;
    assign module_intf_16.finish = finish;
    csv_file_dump mstatus_csv_dumper_16;
    nodf_module_monitor module_monitor_16;

    upc_loop_intf#(1) upc_loop_intf_1(clock,reset);
    assign upc_loop_intf_1.cur_state = AESL_inst_cost_step.grp_from_int_fu_295.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_CS_fsm;
    assign upc_loop_intf_1.iter_start_state = AESL_inst_cost_step.grp_from_int_fu_295.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_ST_fsm_pp0_stage0;
    assign upc_loop_intf_1.iter_end_state = AESL_inst_cost_step.grp_from_int_fu_295.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_ST_fsm_pp0_stage0;
    assign upc_loop_intf_1.quit_state = AESL_inst_cost_step.grp_from_int_fu_295.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_ST_fsm_pp0_stage0;
    assign upc_loop_intf_1.iter_start_block = AESL_inst_cost_step.grp_from_int_fu_295.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_block_pp0_stage0_subdone;
    assign upc_loop_intf_1.iter_end_block = AESL_inst_cost_step.grp_from_int_fu_295.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_block_pp0_stage0_subdone;
    assign upc_loop_intf_1.quit_block = AESL_inst_cost_step.grp_from_int_fu_295.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_block_pp0_stage0_subdone;
    assign upc_loop_intf_1.iter_start_enable = AESL_inst_cost_step.grp_from_int_fu_295.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_enable_reg_pp0_iter1;
    assign upc_loop_intf_1.iter_end_enable = AESL_inst_cost_step.grp_from_int_fu_295.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_enable_reg_pp0_iter1;
    assign upc_loop_intf_1.quit_enable = AESL_inst_cost_step.grp_from_int_fu_295.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_enable_reg_pp0_iter1;
    assign upc_loop_intf_1.loop_start = AESL_inst_cost_step.grp_from_int_fu_295.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_start;
    assign upc_loop_intf_1.loop_ready = AESL_inst_cost_step.grp_from_int_fu_295.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_ready;
    assign upc_loop_intf_1.loop_done = AESL_inst_cost_step.grp_from_int_fu_295.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_done_int;
    assign upc_loop_intf_1.loop_continue = 1'b1;
    assign upc_loop_intf_1.quit_at_end = 1'b1;
    assign upc_loop_intf_1.finish = finish;
    csv_file_dump upc_loop_csv_dumper_1;
    upc_loop_monitor #(1) upc_loop_monitor_1;
    upc_loop_intf#(1) upc_loop_intf_2(clock,reset);
    assign upc_loop_intf_2.cur_state = AESL_inst_cost_step.grp_from_int_fu_301.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_CS_fsm;
    assign upc_loop_intf_2.iter_start_state = AESL_inst_cost_step.grp_from_int_fu_301.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_ST_fsm_pp0_stage0;
    assign upc_loop_intf_2.iter_end_state = AESL_inst_cost_step.grp_from_int_fu_301.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_ST_fsm_pp0_stage0;
    assign upc_loop_intf_2.quit_state = AESL_inst_cost_step.grp_from_int_fu_301.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_ST_fsm_pp0_stage0;
    assign upc_loop_intf_2.iter_start_block = AESL_inst_cost_step.grp_from_int_fu_301.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_block_pp0_stage0_subdone;
    assign upc_loop_intf_2.iter_end_block = AESL_inst_cost_step.grp_from_int_fu_301.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_block_pp0_stage0_subdone;
    assign upc_loop_intf_2.quit_block = AESL_inst_cost_step.grp_from_int_fu_301.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_block_pp0_stage0_subdone;
    assign upc_loop_intf_2.iter_start_enable = AESL_inst_cost_step.grp_from_int_fu_301.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_enable_reg_pp0_iter1;
    assign upc_loop_intf_2.iter_end_enable = AESL_inst_cost_step.grp_from_int_fu_301.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_enable_reg_pp0_iter1;
    assign upc_loop_intf_2.quit_enable = AESL_inst_cost_step.grp_from_int_fu_301.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_enable_reg_pp0_iter1;
    assign upc_loop_intf_2.loop_start = AESL_inst_cost_step.grp_from_int_fu_301.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_start;
    assign upc_loop_intf_2.loop_ready = AESL_inst_cost_step.grp_from_int_fu_301.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_ready;
    assign upc_loop_intf_2.loop_done = AESL_inst_cost_step.grp_from_int_fu_301.grp_from_int_Pipeline_VITIS_LOOP_63_1_fu_111.ap_done_int;
    assign upc_loop_intf_2.loop_continue = 1'b1;
    assign upc_loop_intf_2.quit_at_end = 1'b1;
    assign upc_loop_intf_2.finish = finish;
    csv_file_dump upc_loop_csv_dumper_2;
    upc_loop_monitor #(1) upc_loop_monitor_2;
    upc_loop_intf#(1) upc_loop_intf_3(clock,reset);
    assign upc_loop_intf_3.cur_state = AESL_inst_cost_step.grp_mul_fu_307.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_CS_fsm;
    assign upc_loop_intf_3.iter_start_state = AESL_inst_cost_step.grp_mul_fu_307.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_ST_fsm_pp0_stage0;
    assign upc_loop_intf_3.iter_end_state = AESL_inst_cost_step.grp_mul_fu_307.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_ST_fsm_pp0_stage0;
    assign upc_loop_intf_3.quit_state = AESL_inst_cost_step.grp_mul_fu_307.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_ST_fsm_pp0_stage0;
    assign upc_loop_intf_3.iter_start_block = AESL_inst_cost_step.grp_mul_fu_307.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_block_pp0_stage0_subdone;
    assign upc_loop_intf_3.iter_end_block = AESL_inst_cost_step.grp_mul_fu_307.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_block_pp0_stage0_subdone;
    assign upc_loop_intf_3.quit_block = AESL_inst_cost_step.grp_mul_fu_307.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_block_pp0_stage0_subdone;
    assign upc_loop_intf_3.iter_start_enable = AESL_inst_cost_step.grp_mul_fu_307.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_enable_reg_pp0_iter1;
    assign upc_loop_intf_3.iter_end_enable = AESL_inst_cost_step.grp_mul_fu_307.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_enable_reg_pp0_iter1;
    assign upc_loop_intf_3.quit_enable = AESL_inst_cost_step.grp_mul_fu_307.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_enable_reg_pp0_iter1;
    assign upc_loop_intf_3.loop_start = AESL_inst_cost_step.grp_mul_fu_307.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_start;
    assign upc_loop_intf_3.loop_ready = AESL_inst_cost_step.grp_mul_fu_307.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_ready;
    assign upc_loop_intf_3.loop_done = AESL_inst_cost_step.grp_mul_fu_307.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_done_int;
    assign upc_loop_intf_3.loop_continue = 1'b1;
    assign upc_loop_intf_3.quit_at_end = 1'b1;
    assign upc_loop_intf_3.finish = finish;
    csv_file_dump upc_loop_csv_dumper_3;
    upc_loop_monitor #(1) upc_loop_monitor_3;
    upc_loop_intf#(1) upc_loop_intf_4(clock,reset);
    assign upc_loop_intf_4.cur_state = AESL_inst_cost_step.grp_mul_fu_315.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_CS_fsm;
    assign upc_loop_intf_4.iter_start_state = AESL_inst_cost_step.grp_mul_fu_315.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_ST_fsm_pp0_stage0;
    assign upc_loop_intf_4.iter_end_state = AESL_inst_cost_step.grp_mul_fu_315.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_ST_fsm_pp0_stage0;
    assign upc_loop_intf_4.quit_state = AESL_inst_cost_step.grp_mul_fu_315.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_ST_fsm_pp0_stage0;
    assign upc_loop_intf_4.iter_start_block = AESL_inst_cost_step.grp_mul_fu_315.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_block_pp0_stage0_subdone;
    assign upc_loop_intf_4.iter_end_block = AESL_inst_cost_step.grp_mul_fu_315.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_block_pp0_stage0_subdone;
    assign upc_loop_intf_4.quit_block = AESL_inst_cost_step.grp_mul_fu_315.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_block_pp0_stage0_subdone;
    assign upc_loop_intf_4.iter_start_enable = AESL_inst_cost_step.grp_mul_fu_315.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_enable_reg_pp0_iter1;
    assign upc_loop_intf_4.iter_end_enable = AESL_inst_cost_step.grp_mul_fu_315.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_enable_reg_pp0_iter1;
    assign upc_loop_intf_4.quit_enable = AESL_inst_cost_step.grp_mul_fu_315.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_enable_reg_pp0_iter1;
    assign upc_loop_intf_4.loop_start = AESL_inst_cost_step.grp_mul_fu_315.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_start;
    assign upc_loop_intf_4.loop_ready = AESL_inst_cost_step.grp_mul_fu_315.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_ready;
    assign upc_loop_intf_4.loop_done = AESL_inst_cost_step.grp_mul_fu_315.grp_mul_Pipeline_VITIS_LOOP_42_1_fu_165.ap_done_int;
    assign upc_loop_intf_4.loop_continue = 1'b1;
    assign upc_loop_intf_4.quit_at_end = 1'b1;
    assign upc_loop_intf_4.finish = finish;
    csv_file_dump upc_loop_csv_dumper_4;
    upc_loop_monitor #(1) upc_loop_monitor_4;
    upc_loop_intf#(1) upc_loop_intf_5(clock,reset);
    assign upc_loop_intf_5.cur_state = AESL_inst_cost_step.grp_add_fu_325.grp_add_Pipeline_VITIS_LOOP_30_1_fu_185.ap_CS_fsm;
    assign upc_loop_intf_5.iter_start_state = AESL_inst_cost_step.grp_add_fu_325.grp_add_Pipeline_VITIS_LOOP_30_1_fu_185.ap_ST_fsm_pp0_stage0;
    assign upc_loop_intf_5.iter_end_state = AESL_inst_cost_step.grp_add_fu_325.grp_add_Pipeline_VITIS_LOOP_30_1_fu_185.ap_ST_fsm_pp0_stage0;
    assign upc_loop_intf_5.quit_state = AESL_inst_cost_step.grp_add_fu_325.grp_add_Pipeline_VITIS_LOOP_30_1_fu_185.ap_ST_fsm_pp0_stage0;
    assign upc_loop_intf_5.iter_start_block = AESL_inst_cost_step.grp_add_fu_325.grp_add_Pipeline_VITIS_LOOP_30_1_fu_185.ap_block_pp0_stage0_subdone;
    assign upc_loop_intf_5.iter_end_block = AESL_inst_cost_step.grp_add_fu_325.grp_add_Pipeline_VITIS_LOOP_30_1_fu_185.ap_block_pp0_stage0_subdone;
    assign upc_loop_intf_5.quit_block = AESL_inst_cost_step.grp_add_fu_325.grp_add_Pipeline_VITIS_LOOP_30_1_fu_185.ap_block_pp0_stage0_subdone;
    assign upc_loop_intf_5.iter_start_enable = AESL_inst_cost_step.grp_add_fu_325.grp_add_Pipeline_VITIS_LOOP_30_1_fu_185.ap_enable_reg_pp0_iter1;
    assign upc_loop_intf_5.iter_end_enable = AESL_inst_cost_step.grp_add_fu_325.grp_add_Pipeline_VITIS_LOOP_30_1_fu_185.ap_enable_reg_pp0_iter1;
    assign upc_loop_intf_5.quit_enable = AESL_inst_cost_step.grp_add_fu_325.grp_add_Pipeline_VITIS_LOOP_30_1_fu_185.ap_enable_reg_pp0_iter1;
    assign upc_loop_intf_5.loop_start = AESL_inst_cost_step.grp_add_fu_325.grp_add_Pipeline_VITIS_LOOP_30_1_fu_185.ap_start;
    assign upc_loop_intf_5.loop_ready = AESL_inst_cost_step.grp_add_fu_325.grp_add_Pipeline_VITIS_LOOP_30_1_fu_185.ap_ready;
    assign upc_loop_intf_5.loop_done = AESL_inst_cost_step.grp_add_fu_325.grp_add_Pipeline_VITIS_LOOP_30_1_fu_185.ap_done_int;
    assign upc_loop_intf_5.loop_continue = 1'b1;
    assign upc_loop_intf_5.quit_at_end = 1'b1;
    assign upc_loop_intf_5.finish = finish;
    csv_file_dump upc_loop_csv_dumper_5;
    upc_loop_monitor #(1) upc_loop_monitor_5;
    upc_loop_intf#(1) upc_loop_intf_6(clock,reset);
    assign upc_loop_intf_6.cur_state = AESL_inst_cost_step.grp_div_fu_333.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_CS_fsm;
    assign upc_loop_intf_6.iter_start_state = AESL_inst_cost_step.grp_div_fu_333.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_ST_fsm_pp0_stage0;
    assign upc_loop_intf_6.iter_end_state = AESL_inst_cost_step.grp_div_fu_333.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_ST_fsm_pp0_stage0;
    assign upc_loop_intf_6.quit_state = AESL_inst_cost_step.grp_div_fu_333.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_ST_fsm_pp0_stage0;
    assign upc_loop_intf_6.iter_start_block = AESL_inst_cost_step.grp_div_fu_333.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_block_pp0_stage0_subdone;
    assign upc_loop_intf_6.iter_end_block = AESL_inst_cost_step.grp_div_fu_333.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_block_pp0_stage0_subdone;
    assign upc_loop_intf_6.quit_block = AESL_inst_cost_step.grp_div_fu_333.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_block_pp0_stage0_subdone;
    assign upc_loop_intf_6.iter_start_enable = AESL_inst_cost_step.grp_div_fu_333.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_enable_reg_pp0_iter1;
    assign upc_loop_intf_6.iter_end_enable = AESL_inst_cost_step.grp_div_fu_333.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_enable_reg_pp0_iter1;
    assign upc_loop_intf_6.quit_enable = AESL_inst_cost_step.grp_div_fu_333.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_enable_reg_pp0_iter1;
    assign upc_loop_intf_6.loop_start = AESL_inst_cost_step.grp_div_fu_333.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_start;
    assign upc_loop_intf_6.loop_ready = AESL_inst_cost_step.grp_div_fu_333.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_ready;
    assign upc_loop_intf_6.loop_done = AESL_inst_cost_step.grp_div_fu_333.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_done_int;
    assign upc_loop_intf_6.loop_continue = 1'b1;
    assign upc_loop_intf_6.quit_at_end = 1'b1;
    assign upc_loop_intf_6.finish = finish;
    csv_file_dump upc_loop_csv_dumper_6;
    upc_loop_monitor #(1) upc_loop_monitor_6;
    upc_loop_intf#(1) upc_loop_intf_7(clock,reset);
    assign upc_loop_intf_7.cur_state = AESL_inst_cost_step.grp_div_fu_340.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_CS_fsm;
    assign upc_loop_intf_7.iter_start_state = AESL_inst_cost_step.grp_div_fu_340.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_ST_fsm_pp0_stage0;
    assign upc_loop_intf_7.iter_end_state = AESL_inst_cost_step.grp_div_fu_340.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_ST_fsm_pp0_stage0;
    assign upc_loop_intf_7.quit_state = AESL_inst_cost_step.grp_div_fu_340.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_ST_fsm_pp0_stage0;
    assign upc_loop_intf_7.iter_start_block = AESL_inst_cost_step.grp_div_fu_340.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_block_pp0_stage0_subdone;
    assign upc_loop_intf_7.iter_end_block = AESL_inst_cost_step.grp_div_fu_340.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_block_pp0_stage0_subdone;
    assign upc_loop_intf_7.quit_block = AESL_inst_cost_step.grp_div_fu_340.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_block_pp0_stage0_subdone;
    assign upc_loop_intf_7.iter_start_enable = AESL_inst_cost_step.grp_div_fu_340.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_enable_reg_pp0_iter1;
    assign upc_loop_intf_7.iter_end_enable = AESL_inst_cost_step.grp_div_fu_340.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_enable_reg_pp0_iter1;
    assign upc_loop_intf_7.quit_enable = AESL_inst_cost_step.grp_div_fu_340.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_enable_reg_pp0_iter1;
    assign upc_loop_intf_7.loop_start = AESL_inst_cost_step.grp_div_fu_340.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_start;
    assign upc_loop_intf_7.loop_ready = AESL_inst_cost_step.grp_div_fu_340.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_ready;
    assign upc_loop_intf_7.loop_done = AESL_inst_cost_step.grp_div_fu_340.grp_div_Pipeline_VITIS_LOOP_56_1_fu_153.ap_done_int;
    assign upc_loop_intf_7.loop_continue = 1'b1;
    assign upc_loop_intf_7.quit_at_end = 1'b1;
    assign upc_loop_intf_7.finish = finish;
    csv_file_dump upc_loop_csv_dumper_7;
    upc_loop_monitor #(1) upc_loop_monitor_7;
    upc_loop_intf#(1) upc_loop_intf_8(clock,reset);
    assign upc_loop_intf_8.cur_state = AESL_inst_cost_step.grp_cost_step_Pipeline_VITIS_LOOP_18_1_fu_350.ap_CS_fsm;
    assign upc_loop_intf_8.iter_start_state = AESL_inst_cost_step.grp_cost_step_Pipeline_VITIS_LOOP_18_1_fu_350.ap_ST_fsm_pp0_stage0;
    assign upc_loop_intf_8.iter_end_state = AESL_inst_cost_step.grp_cost_step_Pipeline_VITIS_LOOP_18_1_fu_350.ap_ST_fsm_pp0_stage0;
    assign upc_loop_intf_8.quit_state = AESL_inst_cost_step.grp_cost_step_Pipeline_VITIS_LOOP_18_1_fu_350.ap_ST_fsm_pp0_stage0;
    assign upc_loop_intf_8.iter_start_block = AESL_inst_cost_step.grp_cost_step_Pipeline_VITIS_LOOP_18_1_fu_350.ap_block_pp0_stage0_subdone;
    assign upc_loop_intf_8.iter_end_block = AESL_inst_cost_step.grp_cost_step_Pipeline_VITIS_LOOP_18_1_fu_350.ap_block_pp0_stage0_subdone;
    assign upc_loop_intf_8.quit_block = AESL_inst_cost_step.grp_cost_step_Pipeline_VITIS_LOOP_18_1_fu_350.ap_block_pp0_stage0_subdone;
    assign upc_loop_intf_8.iter_start_enable = AESL_inst_cost_step.grp_cost_step_Pipeline_VITIS_LOOP_18_1_fu_350.ap_enable_reg_pp0_iter0;
    assign upc_loop_intf_8.iter_end_enable = AESL_inst_cost_step.grp_cost_step_Pipeline_VITIS_LOOP_18_1_fu_350.ap_enable_reg_pp0_iter1;
    assign upc_loop_intf_8.quit_enable = AESL_inst_cost_step.grp_cost_step_Pipeline_VITIS_LOOP_18_1_fu_350.ap_enable_reg_pp0_iter0;
    assign upc_loop_intf_8.loop_start = AESL_inst_cost_step.grp_cost_step_Pipeline_VITIS_LOOP_18_1_fu_350.ap_start;
    assign upc_loop_intf_8.loop_ready = AESL_inst_cost_step.grp_cost_step_Pipeline_VITIS_LOOP_18_1_fu_350.ap_ready;
    assign upc_loop_intf_8.loop_done = AESL_inst_cost_step.grp_cost_step_Pipeline_VITIS_LOOP_18_1_fu_350.ap_done_int;
    assign upc_loop_intf_8.loop_continue = 1'b1;
    assign upc_loop_intf_8.quit_at_end = 1'b0;
    assign upc_loop_intf_8.finish = finish;
    csv_file_dump upc_loop_csv_dumper_8;
    upc_loop_monitor #(1) upc_loop_monitor_8;

    sample_manager sample_manager_inst;

initial begin
    sample_manager_inst = new;



    mstatus_csv_dumper_1 = new("./module_status1.csv");
    module_monitor_1 = new(module_intf_1,mstatus_csv_dumper_1);
    mstatus_csv_dumper_2 = new("./module_status2.csv");
    module_monitor_2 = new(module_intf_2,mstatus_csv_dumper_2);
    mstatus_csv_dumper_3 = new("./module_status3.csv");
    module_monitor_3 = new(module_intf_3,mstatus_csv_dumper_3);
    mstatus_csv_dumper_4 = new("./module_status4.csv");
    module_monitor_4 = new(module_intf_4,mstatus_csv_dumper_4);
    mstatus_csv_dumper_5 = new("./module_status5.csv");
    module_monitor_5 = new(module_intf_5,mstatus_csv_dumper_5);
    mstatus_csv_dumper_6 = new("./module_status6.csv");
    module_monitor_6 = new(module_intf_6,mstatus_csv_dumper_6);
    mstatus_csv_dumper_7 = new("./module_status7.csv");
    module_monitor_7 = new(module_intf_7,mstatus_csv_dumper_7);
    mstatus_csv_dumper_8 = new("./module_status8.csv");
    module_monitor_8 = new(module_intf_8,mstatus_csv_dumper_8);
    mstatus_csv_dumper_9 = new("./module_status9.csv");
    module_monitor_9 = new(module_intf_9,mstatus_csv_dumper_9);
    mstatus_csv_dumper_10 = new("./module_status10.csv");
    module_monitor_10 = new(module_intf_10,mstatus_csv_dumper_10);
    mstatus_csv_dumper_11 = new("./module_status11.csv");
    module_monitor_11 = new(module_intf_11,mstatus_csv_dumper_11);
    mstatus_csv_dumper_12 = new("./module_status12.csv");
    module_monitor_12 = new(module_intf_12,mstatus_csv_dumper_12);
    mstatus_csv_dumper_13 = new("./module_status13.csv");
    module_monitor_13 = new(module_intf_13,mstatus_csv_dumper_13);
    mstatus_csv_dumper_14 = new("./module_status14.csv");
    module_monitor_14 = new(module_intf_14,mstatus_csv_dumper_14);
    mstatus_csv_dumper_15 = new("./module_status15.csv");
    module_monitor_15 = new(module_intf_15,mstatus_csv_dumper_15);
    mstatus_csv_dumper_16 = new("./module_status16.csv");
    module_monitor_16 = new(module_intf_16,mstatus_csv_dumper_16);




    upc_loop_csv_dumper_1 = new("./upc_loop_status1.csv");
    upc_loop_monitor_1 = new(upc_loop_intf_1,upc_loop_csv_dumper_1);
    upc_loop_csv_dumper_2 = new("./upc_loop_status2.csv");
    upc_loop_monitor_2 = new(upc_loop_intf_2,upc_loop_csv_dumper_2);
    upc_loop_csv_dumper_3 = new("./upc_loop_status3.csv");
    upc_loop_monitor_3 = new(upc_loop_intf_3,upc_loop_csv_dumper_3);
    upc_loop_csv_dumper_4 = new("./upc_loop_status4.csv");
    upc_loop_monitor_4 = new(upc_loop_intf_4,upc_loop_csv_dumper_4);
    upc_loop_csv_dumper_5 = new("./upc_loop_status5.csv");
    upc_loop_monitor_5 = new(upc_loop_intf_5,upc_loop_csv_dumper_5);
    upc_loop_csv_dumper_6 = new("./upc_loop_status6.csv");
    upc_loop_monitor_6 = new(upc_loop_intf_6,upc_loop_csv_dumper_6);
    upc_loop_csv_dumper_7 = new("./upc_loop_status7.csv");
    upc_loop_monitor_7 = new(upc_loop_intf_7,upc_loop_csv_dumper_7);
    upc_loop_csv_dumper_8 = new("./upc_loop_status8.csv");
    upc_loop_monitor_8 = new(upc_loop_intf_8,upc_loop_csv_dumper_8);

    sample_manager_inst.add_one_monitor(module_monitor_1);
    sample_manager_inst.add_one_monitor(module_monitor_2);
    sample_manager_inst.add_one_monitor(module_monitor_3);
    sample_manager_inst.add_one_monitor(module_monitor_4);
    sample_manager_inst.add_one_monitor(module_monitor_5);
    sample_manager_inst.add_one_monitor(module_monitor_6);
    sample_manager_inst.add_one_monitor(module_monitor_7);
    sample_manager_inst.add_one_monitor(module_monitor_8);
    sample_manager_inst.add_one_monitor(module_monitor_9);
    sample_manager_inst.add_one_monitor(module_monitor_10);
    sample_manager_inst.add_one_monitor(module_monitor_11);
    sample_manager_inst.add_one_monitor(module_monitor_12);
    sample_manager_inst.add_one_monitor(module_monitor_13);
    sample_manager_inst.add_one_monitor(module_monitor_14);
    sample_manager_inst.add_one_monitor(module_monitor_15);
    sample_manager_inst.add_one_monitor(module_monitor_16);
    sample_manager_inst.add_one_monitor(upc_loop_monitor_1);
    sample_manager_inst.add_one_monitor(upc_loop_monitor_2);
    sample_manager_inst.add_one_monitor(upc_loop_monitor_3);
    sample_manager_inst.add_one_monitor(upc_loop_monitor_4);
    sample_manager_inst.add_one_monitor(upc_loop_monitor_5);
    sample_manager_inst.add_one_monitor(upc_loop_monitor_6);
    sample_manager_inst.add_one_monitor(upc_loop_monitor_7);
    sample_manager_inst.add_one_monitor(upc_loop_monitor_8);
    
    fork
        sample_manager_inst.start_monitor();
        last_transaction_done;
    join
    disable fork;

    sample_manager_inst.start_dump();
end

    task last_transaction_done();
        wait(reset == 0);
        while(1) begin
            if (finish == 1'b1) begin
                @(negedge clock);
                break;
            end
            else
                @(posedge clock);
        end
    endtask


endmodule
