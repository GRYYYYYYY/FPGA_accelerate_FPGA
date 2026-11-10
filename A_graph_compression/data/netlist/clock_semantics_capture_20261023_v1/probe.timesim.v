// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2022.2 (lin64) Build 3671981 Fri Oct 14 04:59:54 MDT 2022
// Date        : Fri Oct 23 10:27:52 2026
// Host        : fpgaacc1--cfc8cd109508-jnnrja5s7q running 64-bit Ubuntu 22.04.4 LTS
// Command     : write_verilog -mode timesim -write_all_overrides -sdf_anno false
//               /inspire/hdd/global_user/guoruiyuan-253208540291/FPGA_routing_acceleration/FPGA_accelerate_FPGA/A_graph_compression/data/netlist/clock_semantics_capture_20261023_v1/probe.timesim.v
// Design      : routeracc_cost_registered
// Purpose     : This verilog netlist is a timing simulation representation of the design and should not be modified or
//               synthesized. Please ensure that this netlist is used with the corresponding SDF file.
// Device      : xcu280-fsvh2892-2L-e
// --------------------------------------------------------------------------------
`timescale 1 ps / 1 ps
`define XIL_TIMING

module cost_calculator
   (g,
    cost_valid,
    f_val,
    reset_q,
    valid_q,
    cg_q,
    clk_global,
    S,
    \genblk1[1].g_val_reg0_carry_i_9_0 ,
    \genblk1[2].g_val_reg0_carry_i_9_0 ,
    \genblk1[3].g_val_reg0_carry_i_9_0 ,
    \genblk1[4].g_val_reg0_carry_i_9_0 ,
    \genblk1[5].g_val_reg0_carry_i_9_0 ,
    cz_q,
    pz_q,
    py_q,
    cy_q,
    px_q,
    cx_q,
    ez_q,
    ey_q,
    ex_q);
  output [78:0]g;
  output cost_valid;
  output [89:0]f_val;
  input reset_q;
  input valid_q;
  input [13:0]cg_q;
  input clk_global;
  input [1:0]S;
  input [1:0]\genblk1[1].g_val_reg0_carry_i_9_0 ;
  input [1:0]\genblk1[2].g_val_reg0_carry_i_9_0 ;
  input [1:0]\genblk1[3].g_val_reg0_carry_i_9_0 ;
  input [1:0]\genblk1[4].g_val_reg0_carry_i_9_0 ;
  input [1:0]\genblk1[5].g_val_reg0_carry_i_9_0 ;
  input [2:0]cz_q;
  input [17:0]pz_q;
  input [47:0]py_q;
  input [7:0]cy_q;
  input [47:0]px_q;
  input [7:0]cx_q;
  input [2:0]ez_q;
  input [7:0]ey_q;
  input [7:0]ex_q;

  wire [9:1]A;
  wire [13:1]C;
  wire [13:1]C__0;
  wire [13:1]C__1;
  wire [13:1]C__2;
  wire [13:1]C__3;
  wire [13:1]C__4;
  wire [1:0]S;
  wire [13:0]cg_q;
  wire clk_global;
  wire cost_valid;
  wire [7:0]cx_q;
  wire [7:0]cy_q;
  wire [2:0]cz_q;
  wire [7:0]ex_q;
  wire [7:0]ey_q;
  wire [2:0]ez_q;
  wire \f_out[14]_i_2_n_0 ;
  wire \f_out[14]_i_3_n_0 ;
  wire \f_out[14]_i_4_n_0 ;
  wire \f_out[14]_i_5_n_0 ;
  wire \f_out[14]_i_6_n_0 ;
  wire \f_out[14]_i_7_n_0 ;
  wire \f_out[23]_i_2_n_0 ;
  wire \f_out[23]_i_3_n_0 ;
  wire \f_out[23]_i_4_n_0 ;
  wire \f_out[23]_i_5_n_0 ;
  wire \f_out[23]_i_6_n_0 ;
  wire \f_out[23]_i_7_n_0 ;
  wire \f_out[23]_i_8_n_0 ;
  wire \f_out[30]_i_2_n_0 ;
  wire \f_out[30]_i_3_n_0 ;
  wire \f_out[30]_i_4_n_0 ;
  wire \f_out[30]_i_5_n_0 ;
  wire \f_out[30]_i_6_n_0 ;
  wire \f_out[30]_i_7_n_0 ;
  wire \f_out[39]_i_2_n_0 ;
  wire \f_out[39]_i_3_n_0 ;
  wire \f_out[39]_i_4_n_0 ;
  wire \f_out[39]_i_5_n_0 ;
  wire \f_out[39]_i_6_n_0 ;
  wire \f_out[39]_i_7_n_0 ;
  wire \f_out[39]_i_8_n_0 ;
  wire \f_out[46]_i_2_n_0 ;
  wire \f_out[46]_i_3_n_0 ;
  wire \f_out[46]_i_4_n_0 ;
  wire \f_out[46]_i_5_n_0 ;
  wire \f_out[46]_i_6_n_0 ;
  wire \f_out[46]_i_7_n_0 ;
  wire \f_out[55]_i_2_n_0 ;
  wire \f_out[55]_i_3_n_0 ;
  wire \f_out[55]_i_4_n_0 ;
  wire \f_out[55]_i_5_n_0 ;
  wire \f_out[55]_i_6_n_0 ;
  wire \f_out[55]_i_7_n_0 ;
  wire \f_out[55]_i_8_n_0 ;
  wire \f_out[62]_i_2_n_0 ;
  wire \f_out[62]_i_3_n_0 ;
  wire \f_out[62]_i_4_n_0 ;
  wire \f_out[62]_i_5_n_0 ;
  wire \f_out[62]_i_6_n_0 ;
  wire \f_out[62]_i_7_n_0 ;
  wire \f_out[71]_i_2_n_0 ;
  wire \f_out[71]_i_3_n_0 ;
  wire \f_out[71]_i_4_n_0 ;
  wire \f_out[71]_i_5_n_0 ;
  wire \f_out[71]_i_6_n_0 ;
  wire \f_out[71]_i_7_n_0 ;
  wire \f_out[71]_i_8_n_0 ;
  wire \f_out[78]_i_2_n_0 ;
  wire \f_out[78]_i_3_n_0 ;
  wire \f_out[78]_i_4_n_0 ;
  wire \f_out[78]_i_5_n_0 ;
  wire \f_out[78]_i_6_n_0 ;
  wire \f_out[78]_i_7_n_0 ;
  wire \f_out[7]_i_2_n_0 ;
  wire \f_out[7]_i_3_n_0 ;
  wire \f_out[7]_i_4_n_0 ;
  wire \f_out[7]_i_5_n_0 ;
  wire \f_out[7]_i_6_n_0 ;
  wire \f_out[7]_i_7_n_0 ;
  wire \f_out[7]_i_8_n_0 ;
  wire \f_out[87]_i_2_n_0 ;
  wire \f_out[87]_i_3_n_0 ;
  wire \f_out[87]_i_4_n_0 ;
  wire \f_out[87]_i_5_n_0 ;
  wire \f_out[87]_i_6_n_0 ;
  wire \f_out[87]_i_7_n_0 ;
  wire \f_out[87]_i_8_n_0 ;
  wire \f_out[94]_i_2_n_0 ;
  wire \f_out[94]_i_3_n_0 ;
  wire \f_out[94]_i_4_n_0 ;
  wire \f_out[94]_i_5_n_0 ;
  wire \f_out[94]_i_6_n_0 ;
  wire \f_out[94]_i_7_n_0 ;
  wire \f_out_reg[23]_i_1_n_0 ;
  wire \f_out_reg[39]_i_1_n_0 ;
  wire \f_out_reg[55]_i_1_n_0 ;
  wire \f_out_reg[71]_i_1_n_0 ;
  wire \f_out_reg[7]_i_1_n_0 ;
  wire \f_out_reg[87]_i_1_n_0 ;
  wire [89:0]f_val;
  wire [78:0]g;
  wire [13:1]\genblk1[0].g_val_reg0 ;
  wire \genblk1[0].g_val_reg0__36_carry__0_i_2_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry__0_i_3_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry__0_i_4_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry__0_i_5_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry__0_i_6_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry__0_i_7_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry__0_n_11 ;
  wire \genblk1[0].g_val_reg0__36_carry__0_n_12 ;
  wire \genblk1[0].g_val_reg0__36_carry__0_n_13 ;
  wire \genblk1[0].g_val_reg0__36_carry__0_n_14 ;
  wire \genblk1[0].g_val_reg0__36_carry__0_n_15 ;
  wire \genblk1[0].g_val_reg0__36_carry_i_17_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry_i_18_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry_i_19_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry_i_1_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry_i_20_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry_i_21_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry_i_22_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry_i_23_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry_i_25_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry_i_26_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry_i_27_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry_i_2_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry_i_3_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry_i_4_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry_i_5_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry_i_6_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry_i_7_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry_i_8_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry_i_9_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry_n_0 ;
  wire \genblk1[0].g_val_reg0__36_carry_n_10 ;
  wire \genblk1[0].g_val_reg0__36_carry_n_11 ;
  wire \genblk1[0].g_val_reg0__36_carry_n_12 ;
  wire \genblk1[0].g_val_reg0__36_carry_n_13 ;
  wire \genblk1[0].g_val_reg0__36_carry_n_14 ;
  wire \genblk1[0].g_val_reg0__36_carry_n_15 ;
  wire \genblk1[0].g_val_reg0__36_carry_n_8 ;
  wire \genblk1[0].g_val_reg0__36_carry_n_9 ;
  wire \genblk1[0].g_val_reg0_carry__0_i_1_n_0 ;
  wire \genblk1[0].g_val_reg0_carry__0_i_3_n_0 ;
  wire \genblk1[0].g_val_reg0_carry__0_i_4_n_0 ;
  wire \genblk1[0].g_val_reg0_carry__0_i_5_n_0 ;
  wire \genblk1[0].g_val_reg0_carry__0_i_6_n_0 ;
  wire \genblk1[0].g_val_reg0_carry__0_i_7_n_0 ;
  wire \genblk1[0].g_val_reg0_carry__0_i_8_n_0 ;
  wire \genblk1[0].g_val_reg0_carry__0_i_9_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_10_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_11_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_12_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_13_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_14_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_15_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_16_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_17_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_18_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_19_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_1_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_20_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_21_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_22_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_23_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_24_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_25_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_27_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_28_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_29_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_2_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_30_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_31_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_3_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_4_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_5_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_6_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_7_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_8_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_9_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_n_0 ;
  wire \genblk1[0].g_val_reg0_inferred__0/i__carry_n_0 ;
  wire [6:2]\genblk1[0].g_val_reg1 ;
  wire [11:2]\genblk1[0].g_val_reg2__1 ;
  wire [11:2]\genblk1[0].g_val_reg3__6 ;
  wire \genblk1[0].h_val_x_reg[11]_i_2_n_0 ;
  wire \genblk1[0].h_val_x_reg[13]_i_1_n_0 ;
  wire \genblk1[0].h_val_x_reg[13]_i_2_n_0 ;
  wire \genblk1[0].h_val_x_reg[13]_i_3_n_0 ;
  wire \genblk1[0].h_val_x_reg[1]_i_1_n_0 ;
  wire \genblk1[0].h_val_x_reg[9]_i_10_n_0 ;
  wire \genblk1[0].h_val_x_reg[9]_i_11_n_0 ;
  wire \genblk1[0].h_val_x_reg[9]_i_12_n_0 ;
  wire \genblk1[0].h_val_x_reg[9]_i_13_n_0 ;
  wire \genblk1[0].h_val_x_reg[9]_i_14_n_0 ;
  wire \genblk1[0].h_val_x_reg[9]_i_15_n_0 ;
  wire \genblk1[0].h_val_x_reg[9]_i_16_n_0 ;
  wire \genblk1[0].h_val_x_reg[9]_i_2_n_0 ;
  wire \genblk1[0].h_val_x_reg[9]_i_3_n_0 ;
  wire \genblk1[0].h_val_x_reg[9]_i_4_n_0 ;
  wire \genblk1[0].h_val_x_reg[9]_i_5_n_0 ;
  wire \genblk1[0].h_val_x_reg[9]_i_6_n_0 ;
  wire \genblk1[0].h_val_x_reg[9]_i_7_n_0 ;
  wire \genblk1[0].h_val_x_reg[9]_i_8_n_0 ;
  wire \genblk1[0].h_val_x_reg[9]_i_9_n_0 ;
  wire [11:2]\genblk1[0].h_val_x_reg_reg0 ;
  wire \genblk1[0].h_val_x_reg_reg[9]_i_1_n_0 ;
  wire \genblk1[0].h_val_x_reg_reg_n_0_[10] ;
  wire \genblk1[0].h_val_x_reg_reg_n_0_[11] ;
  wire \genblk1[0].h_val_x_reg_reg_n_0_[1] ;
  wire \genblk1[0].h_val_x_reg_reg_n_0_[2] ;
  wire \genblk1[0].h_val_x_reg_reg_n_0_[3] ;
  wire \genblk1[0].h_val_x_reg_reg_n_0_[4] ;
  wire \genblk1[0].h_val_x_reg_reg_n_0_[5] ;
  wire \genblk1[0].h_val_x_reg_reg_n_0_[6] ;
  wire \genblk1[0].h_val_x_reg_reg_n_0_[7] ;
  wire \genblk1[0].h_val_x_reg_reg_n_0_[8] ;
  wire \genblk1[0].h_val_x_reg_reg_n_0_[9] ;
  wire \genblk1[0].h_val_y_reg[11]_i_2_n_0 ;
  wire \genblk1[0].h_val_y_reg[13]_i_1_n_0 ;
  wire \genblk1[0].h_val_y_reg[13]_i_2_n_0 ;
  wire \genblk1[0].h_val_y_reg[13]_i_3_n_0 ;
  wire \genblk1[0].h_val_y_reg[1]_i_1_n_0 ;
  wire \genblk1[0].h_val_y_reg[9]_i_10_n_0 ;
  wire \genblk1[0].h_val_y_reg[9]_i_11_n_0 ;
  wire \genblk1[0].h_val_y_reg[9]_i_12_n_0 ;
  wire \genblk1[0].h_val_y_reg[9]_i_13_n_0 ;
  wire \genblk1[0].h_val_y_reg[9]_i_14_n_0 ;
  wire \genblk1[0].h_val_y_reg[9]_i_15_n_0 ;
  wire \genblk1[0].h_val_y_reg[9]_i_16_n_0 ;
  wire \genblk1[0].h_val_y_reg[9]_i_2_n_0 ;
  wire \genblk1[0].h_val_y_reg[9]_i_3_n_0 ;
  wire \genblk1[0].h_val_y_reg[9]_i_4_n_0 ;
  wire \genblk1[0].h_val_y_reg[9]_i_5_n_0 ;
  wire \genblk1[0].h_val_y_reg[9]_i_6_n_0 ;
  wire \genblk1[0].h_val_y_reg[9]_i_7_n_0 ;
  wire \genblk1[0].h_val_y_reg[9]_i_8_n_0 ;
  wire \genblk1[0].h_val_y_reg[9]_i_9_n_0 ;
  wire [11:2]\genblk1[0].h_val_y_reg_reg0 ;
  wire \genblk1[0].h_val_y_reg_reg[9]_i_1_n_0 ;
  wire \genblk1[0].h_val_y_reg_reg_n_0_[10] ;
  wire \genblk1[0].h_val_y_reg_reg_n_0_[11] ;
  wire \genblk1[0].h_val_y_reg_reg_n_0_[1] ;
  wire \genblk1[0].h_val_y_reg_reg_n_0_[2] ;
  wire \genblk1[0].h_val_y_reg_reg_n_0_[3] ;
  wire \genblk1[0].h_val_y_reg_reg_n_0_[4] ;
  wire \genblk1[0].h_val_y_reg_reg_n_0_[5] ;
  wire \genblk1[0].h_val_y_reg_reg_n_0_[6] ;
  wire \genblk1[0].h_val_y_reg_reg_n_0_[7] ;
  wire \genblk1[0].h_val_y_reg_reg_n_0_[8] ;
  wire \genblk1[0].h_val_y_reg_reg_n_0_[9] ;
  wire \genblk1[0].h_val_z_reg[13]_i_1_n_0 ;
  wire \genblk1[0].h_val_z_reg[1]_i_1_n_0 ;
  wire \genblk1[0].h_val_z_reg[6]_i_2_n_0 ;
  wire \genblk1[0].h_val_z_reg[6]_i_3_n_0 ;
  wire \genblk1[0].h_val_z_reg[6]_i_4_n_0 ;
  wire \genblk1[0].h_val_z_reg[6]_i_5_n_0 ;
  wire \genblk1[0].h_val_z_reg[6]_i_6_n_0 ;
  wire [6:2]\genblk1[0].h_val_z_reg_reg0 ;
  wire \genblk1[0].h_val_z_reg_reg_n_0_[1] ;
  wire \genblk1[0].h_val_z_reg_reg_n_0_[2] ;
  wire \genblk1[0].h_val_z_reg_reg_n_0_[3] ;
  wire \genblk1[0].h_val_z_reg_reg_n_0_[4] ;
  wire \genblk1[0].h_val_z_reg_reg_n_0_[5] ;
  wire \genblk1[0].h_val_z_reg_reg_n_0_[6] ;
  wire [13:1]\genblk1[1].g_val_reg0 ;
  wire \genblk1[1].g_val_reg0__36_carry__0_i_2_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry__0_i_3_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry__0_i_4_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry__0_i_5_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry__0_i_6_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry__0_i_7_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry__0_n_11 ;
  wire \genblk1[1].g_val_reg0__36_carry__0_n_12 ;
  wire \genblk1[1].g_val_reg0__36_carry__0_n_13 ;
  wire \genblk1[1].g_val_reg0__36_carry__0_n_14 ;
  wire \genblk1[1].g_val_reg0__36_carry__0_n_15 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_10_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_11_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_12_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_13_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_14_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_15_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_16_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_17_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_18_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_19_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_1_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_20_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_21_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_22_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_23_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_24_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_25_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_26_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_27_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_2_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_3_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_4_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_5_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_6_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_7_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_8_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_i_9_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_n_0 ;
  wire \genblk1[1].g_val_reg0__36_carry_n_10 ;
  wire \genblk1[1].g_val_reg0__36_carry_n_11 ;
  wire \genblk1[1].g_val_reg0__36_carry_n_12 ;
  wire \genblk1[1].g_val_reg0__36_carry_n_13 ;
  wire \genblk1[1].g_val_reg0__36_carry_n_14 ;
  wire \genblk1[1].g_val_reg0__36_carry_n_15 ;
  wire \genblk1[1].g_val_reg0__36_carry_n_8 ;
  wire \genblk1[1].g_val_reg0__36_carry_n_9 ;
  wire \genblk1[1].g_val_reg0_carry__0_i_1_n_0 ;
  wire \genblk1[1].g_val_reg0_carry__0_i_3_n_0 ;
  wire \genblk1[1].g_val_reg0_carry__0_i_4_n_0 ;
  wire \genblk1[1].g_val_reg0_carry__0_i_5_n_0 ;
  wire \genblk1[1].g_val_reg0_carry__0_i_6_n_0 ;
  wire \genblk1[1].g_val_reg0_carry__0_i_7_n_0 ;
  wire \genblk1[1].g_val_reg0_carry__0_i_8_n_0 ;
  wire \genblk1[1].g_val_reg0_carry__0_i_9_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_10_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_11_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_12_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_13_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_14_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_15_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_16_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_17_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_18_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_19_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_1_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_20_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_21_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_22_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_23_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_24_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_25_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_27_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_28_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_29_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_2_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_30_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_31_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_3_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_4_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_5_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_6_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_7_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_8_n_0 ;
  wire [1:0]\genblk1[1].g_val_reg0_carry_i_9_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_9_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_n_0 ;
  wire \genblk1[1].g_val_reg0_inferred__0/i__carry_n_0 ;
  wire [6:2]\genblk1[1].g_val_reg1 ;
  wire [11:2]\genblk1[1].g_val_reg2__1 ;
  wire [11:2]\genblk1[1].g_val_reg3__6 ;
  wire \genblk1[1].h_val_x_reg[15]_i_1_n_0 ;
  wire \genblk1[1].h_val_x_reg[23]_i_10_n_0 ;
  wire \genblk1[1].h_val_x_reg[23]_i_11_n_0 ;
  wire \genblk1[1].h_val_x_reg[23]_i_12_n_0 ;
  wire \genblk1[1].h_val_x_reg[23]_i_13_n_0 ;
  wire \genblk1[1].h_val_x_reg[23]_i_14_n_0 ;
  wire \genblk1[1].h_val_x_reg[23]_i_15_n_0 ;
  wire \genblk1[1].h_val_x_reg[23]_i_16_n_0 ;
  wire \genblk1[1].h_val_x_reg[23]_i_2_n_0 ;
  wire \genblk1[1].h_val_x_reg[23]_i_3_n_0 ;
  wire \genblk1[1].h_val_x_reg[23]_i_4_n_0 ;
  wire \genblk1[1].h_val_x_reg[23]_i_5_n_0 ;
  wire \genblk1[1].h_val_x_reg[23]_i_6_n_0 ;
  wire \genblk1[1].h_val_x_reg[23]_i_7_n_0 ;
  wire \genblk1[1].h_val_x_reg[23]_i_8_n_0 ;
  wire \genblk1[1].h_val_x_reg[23]_i_9_n_0 ;
  wire \genblk1[1].h_val_x_reg[25]_i_2_n_0 ;
  wire \genblk1[1].h_val_x_reg[27]_i_1_n_0 ;
  wire \genblk1[1].h_val_x_reg[27]_i_2_n_0 ;
  wire \genblk1[1].h_val_x_reg[27]_i_3_n_0 ;
  wire [11:2]\genblk1[1].h_val_x_reg_reg0 ;
  wire \genblk1[1].h_val_x_reg_reg[23]_i_1_n_0 ;
  wire \genblk1[1].h_val_x_reg_reg_n_0_[15] ;
  wire \genblk1[1].h_val_x_reg_reg_n_0_[16] ;
  wire \genblk1[1].h_val_x_reg_reg_n_0_[17] ;
  wire \genblk1[1].h_val_x_reg_reg_n_0_[18] ;
  wire \genblk1[1].h_val_x_reg_reg_n_0_[19] ;
  wire \genblk1[1].h_val_x_reg_reg_n_0_[20] ;
  wire \genblk1[1].h_val_x_reg_reg_n_0_[21] ;
  wire \genblk1[1].h_val_x_reg_reg_n_0_[22] ;
  wire \genblk1[1].h_val_x_reg_reg_n_0_[23] ;
  wire \genblk1[1].h_val_x_reg_reg_n_0_[24] ;
  wire \genblk1[1].h_val_x_reg_reg_n_0_[25] ;
  wire \genblk1[1].h_val_y_reg[15]_i_1_n_0 ;
  wire \genblk1[1].h_val_y_reg[23]_i_10_n_0 ;
  wire \genblk1[1].h_val_y_reg[23]_i_11_n_0 ;
  wire \genblk1[1].h_val_y_reg[23]_i_12_n_0 ;
  wire \genblk1[1].h_val_y_reg[23]_i_13_n_0 ;
  wire \genblk1[1].h_val_y_reg[23]_i_14_n_0 ;
  wire \genblk1[1].h_val_y_reg[23]_i_15_n_0 ;
  wire \genblk1[1].h_val_y_reg[23]_i_16_n_0 ;
  wire \genblk1[1].h_val_y_reg[23]_i_2_n_0 ;
  wire \genblk1[1].h_val_y_reg[23]_i_3_n_0 ;
  wire \genblk1[1].h_val_y_reg[23]_i_4_n_0 ;
  wire \genblk1[1].h_val_y_reg[23]_i_5_n_0 ;
  wire \genblk1[1].h_val_y_reg[23]_i_6_n_0 ;
  wire \genblk1[1].h_val_y_reg[23]_i_7_n_0 ;
  wire \genblk1[1].h_val_y_reg[23]_i_8_n_0 ;
  wire \genblk1[1].h_val_y_reg[23]_i_9_n_0 ;
  wire \genblk1[1].h_val_y_reg[25]_i_2_n_0 ;
  wire \genblk1[1].h_val_y_reg[27]_i_1_n_0 ;
  wire \genblk1[1].h_val_y_reg[27]_i_2_n_0 ;
  wire \genblk1[1].h_val_y_reg[27]_i_3_n_0 ;
  wire [11:2]\genblk1[1].h_val_y_reg_reg0 ;
  wire \genblk1[1].h_val_y_reg_reg[23]_i_1_n_0 ;
  wire \genblk1[1].h_val_y_reg_reg_n_0_[15] ;
  wire \genblk1[1].h_val_y_reg_reg_n_0_[16] ;
  wire \genblk1[1].h_val_y_reg_reg_n_0_[17] ;
  wire \genblk1[1].h_val_y_reg_reg_n_0_[18] ;
  wire \genblk1[1].h_val_y_reg_reg_n_0_[19] ;
  wire \genblk1[1].h_val_y_reg_reg_n_0_[20] ;
  wire \genblk1[1].h_val_y_reg_reg_n_0_[21] ;
  wire \genblk1[1].h_val_y_reg_reg_n_0_[22] ;
  wire \genblk1[1].h_val_y_reg_reg_n_0_[23] ;
  wire \genblk1[1].h_val_y_reg_reg_n_0_[24] ;
  wire \genblk1[1].h_val_y_reg_reg_n_0_[25] ;
  wire \genblk1[1].h_val_z_reg[15]_i_1_n_0 ;
  wire \genblk1[1].h_val_z_reg[20]_i_2_n_0 ;
  wire \genblk1[1].h_val_z_reg[20]_i_3_n_0 ;
  wire \genblk1[1].h_val_z_reg[20]_i_4_n_0 ;
  wire \genblk1[1].h_val_z_reg[20]_i_5_n_0 ;
  wire \genblk1[1].h_val_z_reg[20]_i_6_n_0 ;
  wire \genblk1[1].h_val_z_reg[27]_i_1_n_0 ;
  wire [6:2]\genblk1[1].h_val_z_reg_reg0 ;
  wire \genblk1[1].h_val_z_reg_reg_n_0_[15] ;
  wire \genblk1[1].h_val_z_reg_reg_n_0_[16] ;
  wire \genblk1[1].h_val_z_reg_reg_n_0_[17] ;
  wire \genblk1[1].h_val_z_reg_reg_n_0_[18] ;
  wire \genblk1[1].h_val_z_reg_reg_n_0_[19] ;
  wire \genblk1[1].h_val_z_reg_reg_n_0_[20] ;
  wire [13:1]\genblk1[2].g_val_reg0 ;
  wire \genblk1[2].g_val_reg0__36_carry__0_i_2_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry__0_i_3_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry__0_i_4_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry__0_i_5_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry__0_i_6_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry__0_i_7_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry__0_n_11 ;
  wire \genblk1[2].g_val_reg0__36_carry__0_n_12 ;
  wire \genblk1[2].g_val_reg0__36_carry__0_n_13 ;
  wire \genblk1[2].g_val_reg0__36_carry__0_n_14 ;
  wire \genblk1[2].g_val_reg0__36_carry__0_n_15 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_10_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_11_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_12_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_13_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_14_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_15_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_16_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_17_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_18_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_19_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_1_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_20_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_21_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_22_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_23_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_24_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_25_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_26_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_27_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_2_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_3_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_4_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_5_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_6_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_7_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_8_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_i_9_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_n_0 ;
  wire \genblk1[2].g_val_reg0__36_carry_n_10 ;
  wire \genblk1[2].g_val_reg0__36_carry_n_11 ;
  wire \genblk1[2].g_val_reg0__36_carry_n_12 ;
  wire \genblk1[2].g_val_reg0__36_carry_n_13 ;
  wire \genblk1[2].g_val_reg0__36_carry_n_14 ;
  wire \genblk1[2].g_val_reg0__36_carry_n_15 ;
  wire \genblk1[2].g_val_reg0__36_carry_n_8 ;
  wire \genblk1[2].g_val_reg0__36_carry_n_9 ;
  wire \genblk1[2].g_val_reg0_carry__0_i_1_n_0 ;
  wire \genblk1[2].g_val_reg0_carry__0_i_3_n_0 ;
  wire \genblk1[2].g_val_reg0_carry__0_i_4_n_0 ;
  wire \genblk1[2].g_val_reg0_carry__0_i_5_n_0 ;
  wire \genblk1[2].g_val_reg0_carry__0_i_6_n_0 ;
  wire \genblk1[2].g_val_reg0_carry__0_i_7_n_0 ;
  wire \genblk1[2].g_val_reg0_carry__0_i_8_n_0 ;
  wire \genblk1[2].g_val_reg0_carry__0_i_9_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_10_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_11_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_12_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_13_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_14_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_15_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_16_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_17_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_18_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_19_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_1_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_20_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_21_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_22_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_23_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_24_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_25_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_27_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_28_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_29_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_2_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_30_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_31_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_3_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_4_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_5_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_6_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_7_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_8_n_0 ;
  wire [1:0]\genblk1[2].g_val_reg0_carry_i_9_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_9_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_n_0 ;
  wire \genblk1[2].g_val_reg0_inferred__0/i__carry_n_0 ;
  wire [6:2]\genblk1[2].g_val_reg1 ;
  wire [11:2]\genblk1[2].g_val_reg2__1 ;
  wire [11:2]\genblk1[2].g_val_reg3__6 ;
  wire \genblk1[2].h_val_x_reg[29]_i_1_n_0 ;
  wire \genblk1[2].h_val_x_reg[37]_i_10_n_0 ;
  wire \genblk1[2].h_val_x_reg[37]_i_11_n_0 ;
  wire \genblk1[2].h_val_x_reg[37]_i_12_n_0 ;
  wire \genblk1[2].h_val_x_reg[37]_i_13_n_0 ;
  wire \genblk1[2].h_val_x_reg[37]_i_14_n_0 ;
  wire \genblk1[2].h_val_x_reg[37]_i_15_n_0 ;
  wire \genblk1[2].h_val_x_reg[37]_i_16_n_0 ;
  wire \genblk1[2].h_val_x_reg[37]_i_2_n_0 ;
  wire \genblk1[2].h_val_x_reg[37]_i_3_n_0 ;
  wire \genblk1[2].h_val_x_reg[37]_i_4_n_0 ;
  wire \genblk1[2].h_val_x_reg[37]_i_5_n_0 ;
  wire \genblk1[2].h_val_x_reg[37]_i_6_n_0 ;
  wire \genblk1[2].h_val_x_reg[37]_i_7_n_0 ;
  wire \genblk1[2].h_val_x_reg[37]_i_8_n_0 ;
  wire \genblk1[2].h_val_x_reg[37]_i_9_n_0 ;
  wire \genblk1[2].h_val_x_reg[39]_i_2_n_0 ;
  wire \genblk1[2].h_val_x_reg[41]_i_1_n_0 ;
  wire \genblk1[2].h_val_x_reg[41]_i_2_n_0 ;
  wire \genblk1[2].h_val_x_reg[41]_i_3_n_0 ;
  wire [11:2]\genblk1[2].h_val_x_reg_reg0 ;
  wire \genblk1[2].h_val_x_reg_reg[37]_i_1_n_0 ;
  wire \genblk1[2].h_val_x_reg_reg_n_0_[29] ;
  wire \genblk1[2].h_val_x_reg_reg_n_0_[30] ;
  wire \genblk1[2].h_val_x_reg_reg_n_0_[31] ;
  wire \genblk1[2].h_val_x_reg_reg_n_0_[32] ;
  wire \genblk1[2].h_val_x_reg_reg_n_0_[33] ;
  wire \genblk1[2].h_val_x_reg_reg_n_0_[34] ;
  wire \genblk1[2].h_val_x_reg_reg_n_0_[35] ;
  wire \genblk1[2].h_val_x_reg_reg_n_0_[36] ;
  wire \genblk1[2].h_val_x_reg_reg_n_0_[37] ;
  wire \genblk1[2].h_val_x_reg_reg_n_0_[38] ;
  wire \genblk1[2].h_val_x_reg_reg_n_0_[39] ;
  wire \genblk1[2].h_val_x_reg_reg_n_0_[41] ;
  wire \genblk1[2].h_val_y_reg[29]_i_1_n_0 ;
  wire \genblk1[2].h_val_y_reg[37]_i_10_n_0 ;
  wire \genblk1[2].h_val_y_reg[37]_i_11_n_0 ;
  wire \genblk1[2].h_val_y_reg[37]_i_12_n_0 ;
  wire \genblk1[2].h_val_y_reg[37]_i_13_n_0 ;
  wire \genblk1[2].h_val_y_reg[37]_i_14_n_0 ;
  wire \genblk1[2].h_val_y_reg[37]_i_15_n_0 ;
  wire \genblk1[2].h_val_y_reg[37]_i_16_n_0 ;
  wire \genblk1[2].h_val_y_reg[37]_i_2_n_0 ;
  wire \genblk1[2].h_val_y_reg[37]_i_3_n_0 ;
  wire \genblk1[2].h_val_y_reg[37]_i_4_n_0 ;
  wire \genblk1[2].h_val_y_reg[37]_i_5_n_0 ;
  wire \genblk1[2].h_val_y_reg[37]_i_6_n_0 ;
  wire \genblk1[2].h_val_y_reg[37]_i_7_n_0 ;
  wire \genblk1[2].h_val_y_reg[37]_i_8_n_0 ;
  wire \genblk1[2].h_val_y_reg[37]_i_9_n_0 ;
  wire \genblk1[2].h_val_y_reg[39]_i_2_n_0 ;
  wire \genblk1[2].h_val_y_reg[41]_i_1_n_0 ;
  wire \genblk1[2].h_val_y_reg[41]_i_2_n_0 ;
  wire \genblk1[2].h_val_y_reg[41]_i_3_n_0 ;
  wire [11:2]\genblk1[2].h_val_y_reg_reg0 ;
  wire \genblk1[2].h_val_y_reg_reg[37]_i_1_n_0 ;
  wire \genblk1[2].h_val_y_reg_reg_n_0_[29] ;
  wire \genblk1[2].h_val_y_reg_reg_n_0_[30] ;
  wire \genblk1[2].h_val_y_reg_reg_n_0_[31] ;
  wire \genblk1[2].h_val_y_reg_reg_n_0_[32] ;
  wire \genblk1[2].h_val_y_reg_reg_n_0_[33] ;
  wire \genblk1[2].h_val_y_reg_reg_n_0_[34] ;
  wire \genblk1[2].h_val_y_reg_reg_n_0_[35] ;
  wire \genblk1[2].h_val_y_reg_reg_n_0_[36] ;
  wire \genblk1[2].h_val_y_reg_reg_n_0_[37] ;
  wire \genblk1[2].h_val_y_reg_reg_n_0_[38] ;
  wire \genblk1[2].h_val_y_reg_reg_n_0_[39] ;
  wire \genblk1[2].h_val_y_reg_reg_n_0_[41] ;
  wire \genblk1[2].h_val_z_reg[29]_i_1_n_0 ;
  wire \genblk1[2].h_val_z_reg[34]_i_2_n_0 ;
  wire \genblk1[2].h_val_z_reg[34]_i_3_n_0 ;
  wire \genblk1[2].h_val_z_reg[34]_i_4_n_0 ;
  wire \genblk1[2].h_val_z_reg[34]_i_5_n_0 ;
  wire \genblk1[2].h_val_z_reg[34]_i_6_n_0 ;
  wire \genblk1[2].h_val_z_reg[41]_i_1_n_0 ;
  wire [6:2]\genblk1[2].h_val_z_reg_reg0 ;
  wire \genblk1[2].h_val_z_reg_reg_n_0_[29] ;
  wire \genblk1[2].h_val_z_reg_reg_n_0_[30] ;
  wire \genblk1[2].h_val_z_reg_reg_n_0_[31] ;
  wire \genblk1[2].h_val_z_reg_reg_n_0_[32] ;
  wire \genblk1[2].h_val_z_reg_reg_n_0_[33] ;
  wire \genblk1[2].h_val_z_reg_reg_n_0_[34] ;
  wire \genblk1[2].h_val_z_reg_reg_n_0_[41] ;
  wire [13:1]\genblk1[3].g_val_reg0 ;
  wire \genblk1[3].g_val_reg0__36_carry__0_i_2_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry__0_i_3_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry__0_i_4_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry__0_i_5_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry__0_i_6_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry__0_i_7_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry__0_n_11 ;
  wire \genblk1[3].g_val_reg0__36_carry__0_n_12 ;
  wire \genblk1[3].g_val_reg0__36_carry__0_n_13 ;
  wire \genblk1[3].g_val_reg0__36_carry__0_n_14 ;
  wire \genblk1[3].g_val_reg0__36_carry__0_n_15 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_10_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_11_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_12_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_13_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_14_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_15_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_16_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_17_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_18_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_19_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_1_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_20_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_21_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_22_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_23_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_24_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_25_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_26_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_27_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_2_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_3_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_4_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_5_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_6_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_7_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_8_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_i_9_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_n_0 ;
  wire \genblk1[3].g_val_reg0__36_carry_n_10 ;
  wire \genblk1[3].g_val_reg0__36_carry_n_11 ;
  wire \genblk1[3].g_val_reg0__36_carry_n_12 ;
  wire \genblk1[3].g_val_reg0__36_carry_n_13 ;
  wire \genblk1[3].g_val_reg0__36_carry_n_14 ;
  wire \genblk1[3].g_val_reg0__36_carry_n_15 ;
  wire \genblk1[3].g_val_reg0__36_carry_n_8 ;
  wire \genblk1[3].g_val_reg0__36_carry_n_9 ;
  wire \genblk1[3].g_val_reg0_carry__0_i_1_n_0 ;
  wire \genblk1[3].g_val_reg0_carry__0_i_3_n_0 ;
  wire \genblk1[3].g_val_reg0_carry__0_i_4_n_0 ;
  wire \genblk1[3].g_val_reg0_carry__0_i_5_n_0 ;
  wire \genblk1[3].g_val_reg0_carry__0_i_6_n_0 ;
  wire \genblk1[3].g_val_reg0_carry__0_i_7_n_0 ;
  wire \genblk1[3].g_val_reg0_carry__0_i_8_n_0 ;
  wire \genblk1[3].g_val_reg0_carry__0_i_9_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_10_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_11_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_12_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_13_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_14_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_15_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_16_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_17_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_18_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_19_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_1_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_20_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_21_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_22_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_23_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_24_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_25_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_27_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_28_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_29_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_2_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_30_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_31_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_3_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_4_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_5_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_6_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_7_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_8_n_0 ;
  wire [1:0]\genblk1[3].g_val_reg0_carry_i_9_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_9_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_n_0 ;
  wire \genblk1[3].g_val_reg0_inferred__0/i__carry_n_0 ;
  wire [6:2]\genblk1[3].g_val_reg1 ;
  wire [11:2]\genblk1[3].g_val_reg2__1 ;
  wire [11:2]\genblk1[3].g_val_reg3__6 ;
  wire \genblk1[3].h_val_x_reg[43]_i_1_n_0 ;
  wire \genblk1[3].h_val_x_reg[51]_i_10_n_0 ;
  wire \genblk1[3].h_val_x_reg[51]_i_11_n_0 ;
  wire \genblk1[3].h_val_x_reg[51]_i_12_n_0 ;
  wire \genblk1[3].h_val_x_reg[51]_i_13_n_0 ;
  wire \genblk1[3].h_val_x_reg[51]_i_14_n_0 ;
  wire \genblk1[3].h_val_x_reg[51]_i_15_n_0 ;
  wire \genblk1[3].h_val_x_reg[51]_i_16_n_0 ;
  wire \genblk1[3].h_val_x_reg[51]_i_2_n_0 ;
  wire \genblk1[3].h_val_x_reg[51]_i_3_n_0 ;
  wire \genblk1[3].h_val_x_reg[51]_i_4_n_0 ;
  wire \genblk1[3].h_val_x_reg[51]_i_5_n_0 ;
  wire \genblk1[3].h_val_x_reg[51]_i_6_n_0 ;
  wire \genblk1[3].h_val_x_reg[51]_i_7_n_0 ;
  wire \genblk1[3].h_val_x_reg[51]_i_8_n_0 ;
  wire \genblk1[3].h_val_x_reg[51]_i_9_n_0 ;
  wire \genblk1[3].h_val_x_reg[53]_i_2_n_0 ;
  wire \genblk1[3].h_val_x_reg[55]_i_1_n_0 ;
  wire \genblk1[3].h_val_x_reg[55]_i_2_n_0 ;
  wire \genblk1[3].h_val_x_reg[55]_i_3_n_0 ;
  wire [11:2]\genblk1[3].h_val_x_reg_reg0 ;
  wire \genblk1[3].h_val_x_reg_reg[51]_i_1_n_0 ;
  wire \genblk1[3].h_val_x_reg_reg_n_0_[43] ;
  wire \genblk1[3].h_val_x_reg_reg_n_0_[44] ;
  wire \genblk1[3].h_val_x_reg_reg_n_0_[45] ;
  wire \genblk1[3].h_val_x_reg_reg_n_0_[46] ;
  wire \genblk1[3].h_val_x_reg_reg_n_0_[47] ;
  wire \genblk1[3].h_val_x_reg_reg_n_0_[48] ;
  wire \genblk1[3].h_val_x_reg_reg_n_0_[49] ;
  wire \genblk1[3].h_val_x_reg_reg_n_0_[50] ;
  wire \genblk1[3].h_val_x_reg_reg_n_0_[51] ;
  wire \genblk1[3].h_val_x_reg_reg_n_0_[52] ;
  wire \genblk1[3].h_val_x_reg_reg_n_0_[53] ;
  wire \genblk1[3].h_val_x_reg_reg_n_0_[55] ;
  wire \genblk1[3].h_val_y_reg[43]_i_1_n_0 ;
  wire \genblk1[3].h_val_y_reg[51]_i_10_n_0 ;
  wire \genblk1[3].h_val_y_reg[51]_i_11_n_0 ;
  wire \genblk1[3].h_val_y_reg[51]_i_12_n_0 ;
  wire \genblk1[3].h_val_y_reg[51]_i_13_n_0 ;
  wire \genblk1[3].h_val_y_reg[51]_i_14_n_0 ;
  wire \genblk1[3].h_val_y_reg[51]_i_15_n_0 ;
  wire \genblk1[3].h_val_y_reg[51]_i_16_n_0 ;
  wire \genblk1[3].h_val_y_reg[51]_i_2_n_0 ;
  wire \genblk1[3].h_val_y_reg[51]_i_3_n_0 ;
  wire \genblk1[3].h_val_y_reg[51]_i_4_n_0 ;
  wire \genblk1[3].h_val_y_reg[51]_i_5_n_0 ;
  wire \genblk1[3].h_val_y_reg[51]_i_6_n_0 ;
  wire \genblk1[3].h_val_y_reg[51]_i_7_n_0 ;
  wire \genblk1[3].h_val_y_reg[51]_i_8_n_0 ;
  wire \genblk1[3].h_val_y_reg[51]_i_9_n_0 ;
  wire \genblk1[3].h_val_y_reg[53]_i_2_n_0 ;
  wire \genblk1[3].h_val_y_reg[55]_i_1_n_0 ;
  wire \genblk1[3].h_val_y_reg[55]_i_2_n_0 ;
  wire \genblk1[3].h_val_y_reg[55]_i_3_n_0 ;
  wire [11:2]\genblk1[3].h_val_y_reg_reg0 ;
  wire \genblk1[3].h_val_y_reg_reg[51]_i_1_n_0 ;
  wire \genblk1[3].h_val_y_reg_reg_n_0_[43] ;
  wire \genblk1[3].h_val_y_reg_reg_n_0_[44] ;
  wire \genblk1[3].h_val_y_reg_reg_n_0_[45] ;
  wire \genblk1[3].h_val_y_reg_reg_n_0_[46] ;
  wire \genblk1[3].h_val_y_reg_reg_n_0_[47] ;
  wire \genblk1[3].h_val_y_reg_reg_n_0_[48] ;
  wire \genblk1[3].h_val_y_reg_reg_n_0_[49] ;
  wire \genblk1[3].h_val_y_reg_reg_n_0_[50] ;
  wire \genblk1[3].h_val_y_reg_reg_n_0_[51] ;
  wire \genblk1[3].h_val_y_reg_reg_n_0_[52] ;
  wire \genblk1[3].h_val_y_reg_reg_n_0_[53] ;
  wire \genblk1[3].h_val_y_reg_reg_n_0_[55] ;
  wire \genblk1[3].h_val_z_reg[43]_i_1_n_0 ;
  wire \genblk1[3].h_val_z_reg[48]_i_2_n_0 ;
  wire \genblk1[3].h_val_z_reg[48]_i_3_n_0 ;
  wire \genblk1[3].h_val_z_reg[48]_i_4_n_0 ;
  wire \genblk1[3].h_val_z_reg[48]_i_5_n_0 ;
  wire \genblk1[3].h_val_z_reg[48]_i_6_n_0 ;
  wire \genblk1[3].h_val_z_reg[55]_i_1_n_0 ;
  wire [6:2]\genblk1[3].h_val_z_reg_reg0 ;
  wire \genblk1[3].h_val_z_reg_reg_n_0_[43] ;
  wire \genblk1[3].h_val_z_reg_reg_n_0_[44] ;
  wire \genblk1[3].h_val_z_reg_reg_n_0_[45] ;
  wire \genblk1[3].h_val_z_reg_reg_n_0_[46] ;
  wire \genblk1[3].h_val_z_reg_reg_n_0_[47] ;
  wire \genblk1[3].h_val_z_reg_reg_n_0_[48] ;
  wire \genblk1[3].h_val_z_reg_reg_n_0_[55] ;
  wire [13:1]\genblk1[4].g_val_reg0 ;
  wire \genblk1[4].g_val_reg0__36_carry__0_i_2_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry__0_i_3_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry__0_i_4_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry__0_i_5_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry__0_i_6_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry__0_i_7_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry__0_n_11 ;
  wire \genblk1[4].g_val_reg0__36_carry__0_n_12 ;
  wire \genblk1[4].g_val_reg0__36_carry__0_n_13 ;
  wire \genblk1[4].g_val_reg0__36_carry__0_n_14 ;
  wire \genblk1[4].g_val_reg0__36_carry__0_n_15 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_10_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_11_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_12_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_13_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_14_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_15_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_16_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_17_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_18_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_19_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_1_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_20_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_21_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_22_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_23_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_24_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_25_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_26_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_27_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_2_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_3_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_4_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_5_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_6_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_7_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_8_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_i_9_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_n_0 ;
  wire \genblk1[4].g_val_reg0__36_carry_n_10 ;
  wire \genblk1[4].g_val_reg0__36_carry_n_11 ;
  wire \genblk1[4].g_val_reg0__36_carry_n_12 ;
  wire \genblk1[4].g_val_reg0__36_carry_n_13 ;
  wire \genblk1[4].g_val_reg0__36_carry_n_14 ;
  wire \genblk1[4].g_val_reg0__36_carry_n_15 ;
  wire \genblk1[4].g_val_reg0__36_carry_n_8 ;
  wire \genblk1[4].g_val_reg0__36_carry_n_9 ;
  wire \genblk1[4].g_val_reg0_carry__0_i_1_n_0 ;
  wire \genblk1[4].g_val_reg0_carry__0_i_3_n_0 ;
  wire \genblk1[4].g_val_reg0_carry__0_i_4_n_0 ;
  wire \genblk1[4].g_val_reg0_carry__0_i_5_n_0 ;
  wire \genblk1[4].g_val_reg0_carry__0_i_6_n_0 ;
  wire \genblk1[4].g_val_reg0_carry__0_i_7_n_0 ;
  wire \genblk1[4].g_val_reg0_carry__0_i_8_n_0 ;
  wire \genblk1[4].g_val_reg0_carry__0_i_9_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_10_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_11_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_12_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_13_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_14_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_15_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_16_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_17_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_18_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_19_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_1_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_20_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_21_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_22_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_23_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_24_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_25_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_27_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_28_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_29_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_2_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_30_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_31_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_3_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_4_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_5_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_6_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_7_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_8_n_0 ;
  wire [1:0]\genblk1[4].g_val_reg0_carry_i_9_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_9_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_n_0 ;
  wire \genblk1[4].g_val_reg0_inferred__0/i__carry_n_0 ;
  wire [6:2]\genblk1[4].g_val_reg1 ;
  wire [11:2]\genblk1[4].g_val_reg2__1 ;
  wire [11:2]\genblk1[4].g_val_reg3__6 ;
  wire \genblk1[4].h_val_x_reg[57]_i_1_n_0 ;
  wire \genblk1[4].h_val_x_reg[65]_i_10_n_0 ;
  wire \genblk1[4].h_val_x_reg[65]_i_11_n_0 ;
  wire \genblk1[4].h_val_x_reg[65]_i_12_n_0 ;
  wire \genblk1[4].h_val_x_reg[65]_i_13_n_0 ;
  wire \genblk1[4].h_val_x_reg[65]_i_14_n_0 ;
  wire \genblk1[4].h_val_x_reg[65]_i_15_n_0 ;
  wire \genblk1[4].h_val_x_reg[65]_i_16_n_0 ;
  wire \genblk1[4].h_val_x_reg[65]_i_2_n_0 ;
  wire \genblk1[4].h_val_x_reg[65]_i_3_n_0 ;
  wire \genblk1[4].h_val_x_reg[65]_i_4_n_0 ;
  wire \genblk1[4].h_val_x_reg[65]_i_5_n_0 ;
  wire \genblk1[4].h_val_x_reg[65]_i_6_n_0 ;
  wire \genblk1[4].h_val_x_reg[65]_i_7_n_0 ;
  wire \genblk1[4].h_val_x_reg[65]_i_8_n_0 ;
  wire \genblk1[4].h_val_x_reg[65]_i_9_n_0 ;
  wire \genblk1[4].h_val_x_reg[67]_i_2_n_0 ;
  wire \genblk1[4].h_val_x_reg[69]_i_1_n_0 ;
  wire \genblk1[4].h_val_x_reg[69]_i_2_n_0 ;
  wire \genblk1[4].h_val_x_reg[69]_i_3_n_0 ;
  wire [11:2]\genblk1[4].h_val_x_reg_reg0 ;
  wire \genblk1[4].h_val_x_reg_reg[65]_i_1_n_0 ;
  wire \genblk1[4].h_val_x_reg_reg_n_0_[57] ;
  wire \genblk1[4].h_val_x_reg_reg_n_0_[58] ;
  wire \genblk1[4].h_val_x_reg_reg_n_0_[59] ;
  wire \genblk1[4].h_val_x_reg_reg_n_0_[60] ;
  wire \genblk1[4].h_val_x_reg_reg_n_0_[61] ;
  wire \genblk1[4].h_val_x_reg_reg_n_0_[62] ;
  wire \genblk1[4].h_val_x_reg_reg_n_0_[63] ;
  wire \genblk1[4].h_val_x_reg_reg_n_0_[64] ;
  wire \genblk1[4].h_val_x_reg_reg_n_0_[65] ;
  wire \genblk1[4].h_val_x_reg_reg_n_0_[66] ;
  wire \genblk1[4].h_val_x_reg_reg_n_0_[67] ;
  wire \genblk1[4].h_val_x_reg_reg_n_0_[69] ;
  wire \genblk1[4].h_val_y_reg[57]_i_1_n_0 ;
  wire \genblk1[4].h_val_y_reg[65]_i_10_n_0 ;
  wire \genblk1[4].h_val_y_reg[65]_i_11_n_0 ;
  wire \genblk1[4].h_val_y_reg[65]_i_12_n_0 ;
  wire \genblk1[4].h_val_y_reg[65]_i_13_n_0 ;
  wire \genblk1[4].h_val_y_reg[65]_i_14_n_0 ;
  wire \genblk1[4].h_val_y_reg[65]_i_15_n_0 ;
  wire \genblk1[4].h_val_y_reg[65]_i_16_n_0 ;
  wire \genblk1[4].h_val_y_reg[65]_i_2_n_0 ;
  wire \genblk1[4].h_val_y_reg[65]_i_3_n_0 ;
  wire \genblk1[4].h_val_y_reg[65]_i_4_n_0 ;
  wire \genblk1[4].h_val_y_reg[65]_i_5_n_0 ;
  wire \genblk1[4].h_val_y_reg[65]_i_6_n_0 ;
  wire \genblk1[4].h_val_y_reg[65]_i_7_n_0 ;
  wire \genblk1[4].h_val_y_reg[65]_i_8_n_0 ;
  wire \genblk1[4].h_val_y_reg[65]_i_9_n_0 ;
  wire \genblk1[4].h_val_y_reg[67]_i_2_n_0 ;
  wire \genblk1[4].h_val_y_reg[69]_i_1_n_0 ;
  wire \genblk1[4].h_val_y_reg[69]_i_2_n_0 ;
  wire \genblk1[4].h_val_y_reg[69]_i_3_n_0 ;
  wire [11:2]\genblk1[4].h_val_y_reg_reg0 ;
  wire \genblk1[4].h_val_y_reg_reg[65]_i_1_n_0 ;
  wire \genblk1[4].h_val_y_reg_reg_n_0_[57] ;
  wire \genblk1[4].h_val_y_reg_reg_n_0_[58] ;
  wire \genblk1[4].h_val_y_reg_reg_n_0_[59] ;
  wire \genblk1[4].h_val_y_reg_reg_n_0_[60] ;
  wire \genblk1[4].h_val_y_reg_reg_n_0_[61] ;
  wire \genblk1[4].h_val_y_reg_reg_n_0_[62] ;
  wire \genblk1[4].h_val_y_reg_reg_n_0_[63] ;
  wire \genblk1[4].h_val_y_reg_reg_n_0_[64] ;
  wire \genblk1[4].h_val_y_reg_reg_n_0_[65] ;
  wire \genblk1[4].h_val_y_reg_reg_n_0_[66] ;
  wire \genblk1[4].h_val_y_reg_reg_n_0_[67] ;
  wire \genblk1[4].h_val_y_reg_reg_n_0_[69] ;
  wire \genblk1[4].h_val_z_reg[57]_i_1_n_0 ;
  wire \genblk1[4].h_val_z_reg[62]_i_2_n_0 ;
  wire \genblk1[4].h_val_z_reg[62]_i_3_n_0 ;
  wire \genblk1[4].h_val_z_reg[62]_i_4_n_0 ;
  wire \genblk1[4].h_val_z_reg[62]_i_5_n_0 ;
  wire \genblk1[4].h_val_z_reg[62]_i_6_n_0 ;
  wire \genblk1[4].h_val_z_reg[69]_i_1_n_0 ;
  wire [6:2]\genblk1[4].h_val_z_reg_reg0 ;
  wire \genblk1[4].h_val_z_reg_reg_n_0_[57] ;
  wire \genblk1[4].h_val_z_reg_reg_n_0_[58] ;
  wire \genblk1[4].h_val_z_reg_reg_n_0_[59] ;
  wire \genblk1[4].h_val_z_reg_reg_n_0_[60] ;
  wire \genblk1[4].h_val_z_reg_reg_n_0_[61] ;
  wire \genblk1[4].h_val_z_reg_reg_n_0_[62] ;
  wire \genblk1[4].h_val_z_reg_reg_n_0_[69] ;
  wire [13:1]\genblk1[5].g_val_reg0 ;
  wire \genblk1[5].g_val_reg0__36_carry__0_i_2_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry__0_i_3_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry__0_i_4_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry__0_i_5_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry__0_i_6_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry__0_i_7_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry__0_n_11 ;
  wire \genblk1[5].g_val_reg0__36_carry__0_n_12 ;
  wire \genblk1[5].g_val_reg0__36_carry__0_n_13 ;
  wire \genblk1[5].g_val_reg0__36_carry__0_n_14 ;
  wire \genblk1[5].g_val_reg0__36_carry__0_n_15 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_10_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_11_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_12_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_13_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_14_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_15_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_16_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_17_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_18_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_19_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_1_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_20_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_21_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_22_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_23_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_24_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_25_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_26_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_27_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_2_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_3_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_4_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_5_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_6_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_7_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_8_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_i_9_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_n_0 ;
  wire \genblk1[5].g_val_reg0__36_carry_n_10 ;
  wire \genblk1[5].g_val_reg0__36_carry_n_11 ;
  wire \genblk1[5].g_val_reg0__36_carry_n_12 ;
  wire \genblk1[5].g_val_reg0__36_carry_n_13 ;
  wire \genblk1[5].g_val_reg0__36_carry_n_14 ;
  wire \genblk1[5].g_val_reg0__36_carry_n_15 ;
  wire \genblk1[5].g_val_reg0__36_carry_n_8 ;
  wire \genblk1[5].g_val_reg0__36_carry_n_9 ;
  wire \genblk1[5].g_val_reg0_carry__0_i_1_n_0 ;
  wire \genblk1[5].g_val_reg0_carry__0_i_3_n_0 ;
  wire \genblk1[5].g_val_reg0_carry__0_i_4_n_0 ;
  wire \genblk1[5].g_val_reg0_carry__0_i_5_n_0 ;
  wire \genblk1[5].g_val_reg0_carry__0_i_6_n_0 ;
  wire \genblk1[5].g_val_reg0_carry__0_i_7_n_0 ;
  wire \genblk1[5].g_val_reg0_carry__0_i_8_n_0 ;
  wire \genblk1[5].g_val_reg0_carry__0_i_9_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_10_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_11_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_12_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_13_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_14_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_15_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_16_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_17_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_18_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_19_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_1_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_20_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_21_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_22_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_23_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_24_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_25_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_27_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_28_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_29_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_2_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_30_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_31_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_3_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_4_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_5_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_6_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_7_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_8_n_0 ;
  wire [1:0]\genblk1[5].g_val_reg0_carry_i_9_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_9_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_n_0 ;
  wire \genblk1[5].g_val_reg0_inferred__0/i__carry_n_0 ;
  wire [6:2]\genblk1[5].g_val_reg1 ;
  wire [11:2]\genblk1[5].g_val_reg2__1 ;
  wire [11:2]\genblk1[5].g_val_reg3__6 ;
  wire \genblk1[5].h_val_x_reg[71]_i_1_n_0 ;
  wire \genblk1[5].h_val_x_reg[79]_i_10_n_0 ;
  wire \genblk1[5].h_val_x_reg[79]_i_11_n_0 ;
  wire \genblk1[5].h_val_x_reg[79]_i_12_n_0 ;
  wire \genblk1[5].h_val_x_reg[79]_i_13_n_0 ;
  wire \genblk1[5].h_val_x_reg[79]_i_14_n_0 ;
  wire \genblk1[5].h_val_x_reg[79]_i_15_n_0 ;
  wire \genblk1[5].h_val_x_reg[79]_i_16_n_0 ;
  wire \genblk1[5].h_val_x_reg[79]_i_2_n_0 ;
  wire \genblk1[5].h_val_x_reg[79]_i_3_n_0 ;
  wire \genblk1[5].h_val_x_reg[79]_i_4_n_0 ;
  wire \genblk1[5].h_val_x_reg[79]_i_5_n_0 ;
  wire \genblk1[5].h_val_x_reg[79]_i_6_n_0 ;
  wire \genblk1[5].h_val_x_reg[79]_i_7_n_0 ;
  wire \genblk1[5].h_val_x_reg[79]_i_8_n_0 ;
  wire \genblk1[5].h_val_x_reg[79]_i_9_n_0 ;
  wire \genblk1[5].h_val_x_reg[81]_i_2_n_0 ;
  wire \genblk1[5].h_val_x_reg[83]_i_1_n_0 ;
  wire \genblk1[5].h_val_x_reg[83]_i_2_n_0 ;
  wire \genblk1[5].h_val_x_reg[83]_i_3_n_0 ;
  wire [11:2]\genblk1[5].h_val_x_reg_reg0 ;
  wire \genblk1[5].h_val_x_reg_reg[79]_i_1_n_0 ;
  wire \genblk1[5].h_val_x_reg_reg_n_0_[71] ;
  wire \genblk1[5].h_val_x_reg_reg_n_0_[72] ;
  wire \genblk1[5].h_val_x_reg_reg_n_0_[73] ;
  wire \genblk1[5].h_val_x_reg_reg_n_0_[74] ;
  wire \genblk1[5].h_val_x_reg_reg_n_0_[75] ;
  wire \genblk1[5].h_val_x_reg_reg_n_0_[76] ;
  wire \genblk1[5].h_val_x_reg_reg_n_0_[77] ;
  wire \genblk1[5].h_val_x_reg_reg_n_0_[78] ;
  wire \genblk1[5].h_val_x_reg_reg_n_0_[79] ;
  wire \genblk1[5].h_val_x_reg_reg_n_0_[80] ;
  wire \genblk1[5].h_val_x_reg_reg_n_0_[81] ;
  wire \genblk1[5].h_val_x_reg_reg_n_0_[83] ;
  wire \genblk1[5].h_val_y_reg[71]_i_1_n_0 ;
  wire \genblk1[5].h_val_y_reg[79]_i_10_n_0 ;
  wire \genblk1[5].h_val_y_reg[79]_i_11_n_0 ;
  wire \genblk1[5].h_val_y_reg[79]_i_12_n_0 ;
  wire \genblk1[5].h_val_y_reg[79]_i_13_n_0 ;
  wire \genblk1[5].h_val_y_reg[79]_i_14_n_0 ;
  wire \genblk1[5].h_val_y_reg[79]_i_15_n_0 ;
  wire \genblk1[5].h_val_y_reg[79]_i_16_n_0 ;
  wire \genblk1[5].h_val_y_reg[79]_i_2_n_0 ;
  wire \genblk1[5].h_val_y_reg[79]_i_3_n_0 ;
  wire \genblk1[5].h_val_y_reg[79]_i_4_n_0 ;
  wire \genblk1[5].h_val_y_reg[79]_i_5_n_0 ;
  wire \genblk1[5].h_val_y_reg[79]_i_6_n_0 ;
  wire \genblk1[5].h_val_y_reg[79]_i_7_n_0 ;
  wire \genblk1[5].h_val_y_reg[79]_i_8_n_0 ;
  wire \genblk1[5].h_val_y_reg[79]_i_9_n_0 ;
  wire \genblk1[5].h_val_y_reg[81]_i_2_n_0 ;
  wire \genblk1[5].h_val_y_reg[83]_i_1_n_0 ;
  wire \genblk1[5].h_val_y_reg[83]_i_2_n_0 ;
  wire \genblk1[5].h_val_y_reg[83]_i_3_n_0 ;
  wire [11:2]\genblk1[5].h_val_y_reg_reg0 ;
  wire \genblk1[5].h_val_y_reg_reg[79]_i_1_n_0 ;
  wire \genblk1[5].h_val_y_reg_reg_n_0_[71] ;
  wire \genblk1[5].h_val_y_reg_reg_n_0_[72] ;
  wire \genblk1[5].h_val_y_reg_reg_n_0_[73] ;
  wire \genblk1[5].h_val_y_reg_reg_n_0_[74] ;
  wire \genblk1[5].h_val_y_reg_reg_n_0_[75] ;
  wire \genblk1[5].h_val_y_reg_reg_n_0_[76] ;
  wire \genblk1[5].h_val_y_reg_reg_n_0_[77] ;
  wire \genblk1[5].h_val_y_reg_reg_n_0_[78] ;
  wire \genblk1[5].h_val_y_reg_reg_n_0_[79] ;
  wire \genblk1[5].h_val_y_reg_reg_n_0_[80] ;
  wire \genblk1[5].h_val_y_reg_reg_n_0_[81] ;
  wire \genblk1[5].h_val_y_reg_reg_n_0_[83] ;
  wire \genblk1[5].h_val_z_reg[71]_i_1_n_0 ;
  wire \genblk1[5].h_val_z_reg[76]_i_2_n_0 ;
  wire \genblk1[5].h_val_z_reg[76]_i_3_n_0 ;
  wire \genblk1[5].h_val_z_reg[76]_i_4_n_0 ;
  wire \genblk1[5].h_val_z_reg[76]_i_5_n_0 ;
  wire \genblk1[5].h_val_z_reg[76]_i_6_n_0 ;
  wire \genblk1[5].h_val_z_reg[83]_i_1_n_0 ;
  wire [6:2]\genblk1[5].h_val_z_reg_reg0 ;
  wire \genblk1[5].h_val_z_reg_reg_n_0_[71] ;
  wire \genblk1[5].h_val_z_reg_reg_n_0_[72] ;
  wire \genblk1[5].h_val_z_reg_reg_n_0_[73] ;
  wire \genblk1[5].h_val_z_reg_reg_n_0_[74] ;
  wire \genblk1[5].h_val_z_reg_reg_n_0_[75] ;
  wire \genblk1[5].h_val_z_reg_reg_n_0_[76] ;
  wire \genblk1[5].h_val_z_reg_reg_n_0_[83] ;
  wire h_val_0__1_carry__0_i_10_n_0;
  wire h_val_0__1_carry__0_i_11_n_0;
  wire h_val_0__1_carry__0_i_12_n_0;
  wire h_val_0__1_carry__0_i_13_n_0;
  wire h_val_0__1_carry__0_i_14_n_0;
  wire h_val_0__1_carry__0_i_1_n_0;
  wire h_val_0__1_carry__0_i_2_n_0;
  wire h_val_0__1_carry__0_i_3_n_0;
  wire h_val_0__1_carry__0_i_4_n_0;
  wire h_val_0__1_carry__0_i_5_n_0;
  wire h_val_0__1_carry__0_i_6_n_0;
  wire h_val_0__1_carry__0_i_7_n_0;
  wire h_val_0__1_carry__0_i_8_n_0;
  wire h_val_0__1_carry__0_i_9_n_0;
  wire h_val_0__1_carry_i_10_n_0;
  wire h_val_0__1_carry_i_11_n_0;
  wire h_val_0__1_carry_i_12_n_0;
  wire h_val_0__1_carry_i_13_n_0;
  wire h_val_0__1_carry_i_14_n_0;
  wire h_val_0__1_carry_i_15_n_0;
  wire h_val_0__1_carry_i_16_n_0;
  wire h_val_0__1_carry_i_17_n_0;
  wire h_val_0__1_carry_i_18_n_0;
  wire h_val_0__1_carry_i_19_n_0;
  wire h_val_0__1_carry_i_1_n_0;
  wire h_val_0__1_carry_i_20_n_0;
  wire h_val_0__1_carry_i_21_n_0;
  wire h_val_0__1_carry_i_22_n_0;
  wire h_val_0__1_carry_i_23_n_0;
  wire h_val_0__1_carry_i_24_n_0;
  wire h_val_0__1_carry_i_25_n_0;
  wire h_val_0__1_carry_i_2_n_0;
  wire h_val_0__1_carry_i_3_n_0;
  wire h_val_0__1_carry_i_4_n_0;
  wire h_val_0__1_carry_i_5_n_0;
  wire h_val_0__1_carry_i_6_n_0;
  wire h_val_0__1_carry_i_7_n_0;
  wire h_val_0__1_carry_i_8_n_0;
  wire h_val_0__1_carry_i_9_n_0;
  wire h_val_0__1_carry_n_0;
  wire [13:1]h_val_0__40;
  wire h_val_14__1_carry__0_i_10_n_0;
  wire h_val_14__1_carry__0_i_11_n_0;
  wire h_val_14__1_carry__0_i_12_n_0;
  wire h_val_14__1_carry__0_i_13_n_0;
  wire h_val_14__1_carry__0_i_14_n_0;
  wire h_val_14__1_carry__0_i_1_n_0;
  wire h_val_14__1_carry__0_i_2_n_0;
  wire h_val_14__1_carry__0_i_3_n_0;
  wire h_val_14__1_carry__0_i_4_n_0;
  wire h_val_14__1_carry__0_i_5_n_0;
  wire h_val_14__1_carry__0_i_6_n_0;
  wire h_val_14__1_carry__0_i_7_n_0;
  wire h_val_14__1_carry__0_i_8_n_0;
  wire h_val_14__1_carry__0_i_9_n_0;
  wire h_val_14__1_carry_i_10_n_0;
  wire h_val_14__1_carry_i_11_n_0;
  wire h_val_14__1_carry_i_12_n_0;
  wire h_val_14__1_carry_i_13_n_0;
  wire h_val_14__1_carry_i_14_n_0;
  wire h_val_14__1_carry_i_15_n_0;
  wire h_val_14__1_carry_i_16_n_0;
  wire h_val_14__1_carry_i_17_n_0;
  wire h_val_14__1_carry_i_18_n_0;
  wire h_val_14__1_carry_i_19_n_0;
  wire h_val_14__1_carry_i_1_n_0;
  wire h_val_14__1_carry_i_20_n_0;
  wire h_val_14__1_carry_i_21_n_0;
  wire h_val_14__1_carry_i_22_n_0;
  wire h_val_14__1_carry_i_23_n_0;
  wire h_val_14__1_carry_i_24_n_0;
  wire h_val_14__1_carry_i_25_n_0;
  wire h_val_14__1_carry_i_2_n_0;
  wire h_val_14__1_carry_i_3_n_0;
  wire h_val_14__1_carry_i_4_n_0;
  wire h_val_14__1_carry_i_5_n_0;
  wire h_val_14__1_carry_i_6_n_0;
  wire h_val_14__1_carry_i_7_n_0;
  wire h_val_14__1_carry_i_8_n_0;
  wire h_val_14__1_carry_i_9_n_0;
  wire h_val_14__1_carry_n_0;
  wire [13:1]h_val_14__40;
  wire h_val_28__1_carry__0_i_10_n_0;
  wire h_val_28__1_carry__0_i_11_n_0;
  wire h_val_28__1_carry__0_i_12_n_0;
  wire h_val_28__1_carry__0_i_13_n_0;
  wire h_val_28__1_carry__0_i_14_n_0;
  wire h_val_28__1_carry__0_i_1_n_0;
  wire h_val_28__1_carry__0_i_2_n_0;
  wire h_val_28__1_carry__0_i_3_n_0;
  wire h_val_28__1_carry__0_i_4_n_0;
  wire h_val_28__1_carry__0_i_5_n_0;
  wire h_val_28__1_carry__0_i_6_n_0;
  wire h_val_28__1_carry__0_i_7_n_0;
  wire h_val_28__1_carry__0_i_8_n_0;
  wire h_val_28__1_carry__0_i_9_n_0;
  wire h_val_28__1_carry_i_10_n_0;
  wire h_val_28__1_carry_i_11_n_0;
  wire h_val_28__1_carry_i_12_n_0;
  wire h_val_28__1_carry_i_13_n_0;
  wire h_val_28__1_carry_i_14_n_0;
  wire h_val_28__1_carry_i_15_n_0;
  wire h_val_28__1_carry_i_16_n_0;
  wire h_val_28__1_carry_i_17_n_0;
  wire h_val_28__1_carry_i_18_n_0;
  wire h_val_28__1_carry_i_19_n_0;
  wire h_val_28__1_carry_i_1_n_0;
  wire h_val_28__1_carry_i_20_n_0;
  wire h_val_28__1_carry_i_21_n_0;
  wire h_val_28__1_carry_i_22_n_0;
  wire h_val_28__1_carry_i_23_n_0;
  wire h_val_28__1_carry_i_24_n_0;
  wire h_val_28__1_carry_i_25_n_0;
  wire h_val_28__1_carry_i_2_n_0;
  wire h_val_28__1_carry_i_3_n_0;
  wire h_val_28__1_carry_i_4_n_0;
  wire h_val_28__1_carry_i_5_n_0;
  wire h_val_28__1_carry_i_6_n_0;
  wire h_val_28__1_carry_i_7_n_0;
  wire h_val_28__1_carry_i_8_n_0;
  wire h_val_28__1_carry_i_9_n_0;
  wire h_val_28__1_carry_n_0;
  wire [13:1]h_val_28__40;
  wire h_val_42__1_carry__0_i_10_n_0;
  wire h_val_42__1_carry__0_i_11_n_0;
  wire h_val_42__1_carry__0_i_12_n_0;
  wire h_val_42__1_carry__0_i_13_n_0;
  wire h_val_42__1_carry__0_i_14_n_0;
  wire h_val_42__1_carry__0_i_1_n_0;
  wire h_val_42__1_carry__0_i_2_n_0;
  wire h_val_42__1_carry__0_i_3_n_0;
  wire h_val_42__1_carry__0_i_4_n_0;
  wire h_val_42__1_carry__0_i_5_n_0;
  wire h_val_42__1_carry__0_i_6_n_0;
  wire h_val_42__1_carry__0_i_7_n_0;
  wire h_val_42__1_carry__0_i_8_n_0;
  wire h_val_42__1_carry__0_i_9_n_0;
  wire h_val_42__1_carry_i_10_n_0;
  wire h_val_42__1_carry_i_11_n_0;
  wire h_val_42__1_carry_i_12_n_0;
  wire h_val_42__1_carry_i_13_n_0;
  wire h_val_42__1_carry_i_14_n_0;
  wire h_val_42__1_carry_i_15_n_0;
  wire h_val_42__1_carry_i_16_n_0;
  wire h_val_42__1_carry_i_17_n_0;
  wire h_val_42__1_carry_i_18_n_0;
  wire h_val_42__1_carry_i_19_n_0;
  wire h_val_42__1_carry_i_1_n_0;
  wire h_val_42__1_carry_i_20_n_0;
  wire h_val_42__1_carry_i_21_n_0;
  wire h_val_42__1_carry_i_22_n_0;
  wire h_val_42__1_carry_i_23_n_0;
  wire h_val_42__1_carry_i_24_n_0;
  wire h_val_42__1_carry_i_25_n_0;
  wire h_val_42__1_carry_i_2_n_0;
  wire h_val_42__1_carry_i_3_n_0;
  wire h_val_42__1_carry_i_4_n_0;
  wire h_val_42__1_carry_i_5_n_0;
  wire h_val_42__1_carry_i_6_n_0;
  wire h_val_42__1_carry_i_7_n_0;
  wire h_val_42__1_carry_i_8_n_0;
  wire h_val_42__1_carry_i_9_n_0;
  wire h_val_42__1_carry_n_0;
  wire [13:1]h_val_42__40;
  wire h_val_56__1_carry__0_i_10_n_0;
  wire h_val_56__1_carry__0_i_11_n_0;
  wire h_val_56__1_carry__0_i_12_n_0;
  wire h_val_56__1_carry__0_i_13_n_0;
  wire h_val_56__1_carry__0_i_14_n_0;
  wire h_val_56__1_carry__0_i_1_n_0;
  wire h_val_56__1_carry__0_i_2_n_0;
  wire h_val_56__1_carry__0_i_3_n_0;
  wire h_val_56__1_carry__0_i_4_n_0;
  wire h_val_56__1_carry__0_i_5_n_0;
  wire h_val_56__1_carry__0_i_6_n_0;
  wire h_val_56__1_carry__0_i_7_n_0;
  wire h_val_56__1_carry__0_i_8_n_0;
  wire h_val_56__1_carry__0_i_9_n_0;
  wire h_val_56__1_carry_i_10_n_0;
  wire h_val_56__1_carry_i_11_n_0;
  wire h_val_56__1_carry_i_12_n_0;
  wire h_val_56__1_carry_i_13_n_0;
  wire h_val_56__1_carry_i_14_n_0;
  wire h_val_56__1_carry_i_15_n_0;
  wire h_val_56__1_carry_i_16_n_0;
  wire h_val_56__1_carry_i_17_n_0;
  wire h_val_56__1_carry_i_18_n_0;
  wire h_val_56__1_carry_i_19_n_0;
  wire h_val_56__1_carry_i_1_n_0;
  wire h_val_56__1_carry_i_20_n_0;
  wire h_val_56__1_carry_i_21_n_0;
  wire h_val_56__1_carry_i_22_n_0;
  wire h_val_56__1_carry_i_23_n_0;
  wire h_val_56__1_carry_i_24_n_0;
  wire h_val_56__1_carry_i_25_n_0;
  wire h_val_56__1_carry_i_2_n_0;
  wire h_val_56__1_carry_i_3_n_0;
  wire h_val_56__1_carry_i_4_n_0;
  wire h_val_56__1_carry_i_5_n_0;
  wire h_val_56__1_carry_i_6_n_0;
  wire h_val_56__1_carry_i_7_n_0;
  wire h_val_56__1_carry_i_8_n_0;
  wire h_val_56__1_carry_i_9_n_0;
  wire h_val_56__1_carry_n_0;
  wire [13:1]h_val_56__40;
  wire h_val_70__1_carry_i_10__0_n_0;
  wire h_val_70__1_carry_i_10_n_0;
  wire h_val_70__1_carry_i_11__0_n_0;
  wire h_val_70__1_carry_i_11_n_0;
  wire h_val_70__1_carry_i_12__0_n_0;
  wire h_val_70__1_carry_i_12_n_0;
  wire h_val_70__1_carry_i_13__0_n_0;
  wire h_val_70__1_carry_i_13_n_0;
  wire h_val_70__1_carry_i_14__0_n_0;
  wire h_val_70__1_carry_i_14_n_0;
  wire h_val_70__1_carry_i_15_n_0;
  wire h_val_70__1_carry_i_16_n_0;
  wire h_val_70__1_carry_i_17_n_0;
  wire h_val_70__1_carry_i_18_n_0;
  wire h_val_70__1_carry_i_19_n_0;
  wire h_val_70__1_carry_i_1__0_n_0;
  wire h_val_70__1_carry_i_1_n_0;
  wire h_val_70__1_carry_i_20_n_0;
  wire h_val_70__1_carry_i_21_n_0;
  wire h_val_70__1_carry_i_22_n_0;
  wire h_val_70__1_carry_i_23_n_0;
  wire h_val_70__1_carry_i_24_n_0;
  wire h_val_70__1_carry_i_25_n_0;
  wire h_val_70__1_carry_i_2__0_n_0;
  wire h_val_70__1_carry_i_2_n_0;
  wire h_val_70__1_carry_i_3__0_n_0;
  wire h_val_70__1_carry_i_3_n_0;
  wire h_val_70__1_carry_i_4__0_n_0;
  wire h_val_70__1_carry_i_4_n_0;
  wire h_val_70__1_carry_i_5__0_n_0;
  wire h_val_70__1_carry_i_5_n_0;
  wire h_val_70__1_carry_i_6__0_n_0;
  wire h_val_70__1_carry_i_6_n_0;
  wire h_val_70__1_carry_i_7__0_n_0;
  wire h_val_70__1_carry_i_7_n_0;
  wire h_val_70__1_carry_i_8__0_n_0;
  wire h_val_70__1_carry_i_8_n_0;
  wire h_val_70__1_carry_i_9__0_n_0;
  wire h_val_70__1_carry_i_9_n_0;
  wire h_val_70__1_carry_n_0;
  wire [13:0]h_val_70__40;
  wire i__carry__0_i_1__0_n_0;
  wire i__carry__0_i_1__1_n_0;
  wire i__carry__0_i_1__2_n_0;
  wire i__carry__0_i_1__3_n_0;
  wire i__carry__0_i_1_n_0;
  wire i__carry__0_i_2__0_n_0;
  wire i__carry__0_i_2__1_n_0;
  wire i__carry__0_i_2__2_n_0;
  wire i__carry__0_i_2__3_n_0;
  wire i__carry__0_i_2_n_0;
  wire i__carry__0_i_3__0_n_0;
  wire i__carry__0_i_3__1_n_0;
  wire i__carry__0_i_3__2_n_0;
  wire i__carry__0_i_3__3_n_0;
  wire i__carry__0_i_3_n_0;
  wire i__carry__0_i_4__0_n_0;
  wire i__carry__0_i_4__1_n_0;
  wire i__carry__0_i_4__2_n_0;
  wire i__carry__0_i_4__3_n_0;
  wire i__carry__0_i_4_n_0;
  wire i__carry__0_i_5__0_n_0;
  wire i__carry__0_i_5__1_n_0;
  wire i__carry__0_i_5__2_n_0;
  wire i__carry__0_i_5__3_n_0;
  wire i__carry__0_i_5_n_0;
  wire i__carry_i_1__0_n_0;
  wire i__carry_i_1__1_n_0;
  wire i__carry_i_1__2_n_0;
  wire i__carry_i_1__3_n_0;
  wire i__carry_i_1__4_n_0;
  wire i__carry_i_1__5_n_0;
  wire i__carry_i_1_n_0;
  wire i__carry_i_2__0_n_0;
  wire i__carry_i_2__1_n_0;
  wire i__carry_i_2__2_n_0;
  wire i__carry_i_2__3_n_0;
  wire i__carry_i_2__4_n_0;
  wire i__carry_i_2__5_n_0;
  wire i__carry_i_2_n_0;
  wire i__carry_i_3__0_n_0;
  wire i__carry_i_3__1_n_0;
  wire i__carry_i_3__2_n_0;
  wire i__carry_i_3__3_n_0;
  wire i__carry_i_3__4_n_0;
  wire i__carry_i_3__5_n_0;
  wire i__carry_i_3_n_0;
  wire i__carry_i_4__0_n_0;
  wire i__carry_i_4__1_n_0;
  wire i__carry_i_4__2_n_0;
  wire i__carry_i_4__3_n_0;
  wire i__carry_i_4__4_n_0;
  wire i__carry_i_4__5_n_0;
  wire i__carry_i_4_n_0;
  wire i__carry_i_5__0_n_0;
  wire i__carry_i_5__1_n_0;
  wire i__carry_i_5__2_n_0;
  wire i__carry_i_5__3_n_0;
  wire i__carry_i_5__4_n_0;
  wire i__carry_i_5__5_n_0;
  wire i__carry_i_5_n_0;
  wire i__carry_i_6__0_n_0;
  wire i__carry_i_6__1_n_0;
  wire i__carry_i_6__2_n_0;
  wire i__carry_i_6__3_n_0;
  wire i__carry_i_6__4_n_0;
  wire i__carry_i_6_n_0;
  wire i__carry_i_7__0_n_0;
  wire i__carry_i_7__1_n_0;
  wire i__carry_i_7__2_n_0;
  wire i__carry_i_7__3_n_0;
  wire i__carry_i_7__4_n_0;
  wire i__carry_i_7_n_0;
  wire i__carry_i_8__0_n_0;
  wire i__carry_i_8__1_n_0;
  wire i__carry_i_8__2_n_0;
  wire i__carry_i_8__3_n_0;
  wire i__carry_i_8__4_n_0;
  wire i__carry_i_8_n_0;
  wire p_0_in3_in;
  wire p_0_in4_in;
  wire p_0_in5_in;
  wire p_3_in;
  wire p_4_in;
  wire p_5_in;
  wire [47:0]px_q;
  wire [47:0]py_q;
  wire [17:0]pz_q;
  wire reset_q;
  wire valid_q;
  wire [7:0]\NLW_f_out_reg[14]_i_1_CO_UNCONNECTED ;
  wire [7:7]\NLW_f_out_reg[14]_i_1_DI_UNCONNECTED ;
  wire [7:6]\NLW_f_out_reg[14]_i_1_O_UNCONNECTED ;
  wire [7:7]\NLW_f_out_reg[14]_i_1_S_UNCONNECTED ;
  wire [6:0]\NLW_f_out_reg[23]_i_1_CO_UNCONNECTED ;
  wire [7:0]\NLW_f_out_reg[30]_i_1_CO_UNCONNECTED ;
  wire [7:7]\NLW_f_out_reg[30]_i_1_DI_UNCONNECTED ;
  wire [7:6]\NLW_f_out_reg[30]_i_1_O_UNCONNECTED ;
  wire [7:7]\NLW_f_out_reg[30]_i_1_S_UNCONNECTED ;
  wire [6:0]\NLW_f_out_reg[39]_i_1_CO_UNCONNECTED ;
  wire [7:0]\NLW_f_out_reg[46]_i_1_CO_UNCONNECTED ;
  wire [7:7]\NLW_f_out_reg[46]_i_1_DI_UNCONNECTED ;
  wire [7:6]\NLW_f_out_reg[46]_i_1_O_UNCONNECTED ;
  wire [7:7]\NLW_f_out_reg[46]_i_1_S_UNCONNECTED ;
  wire [6:0]\NLW_f_out_reg[55]_i_1_CO_UNCONNECTED ;
  wire [7:0]\NLW_f_out_reg[62]_i_1_CO_UNCONNECTED ;
  wire [7:7]\NLW_f_out_reg[62]_i_1_DI_UNCONNECTED ;
  wire [7:6]\NLW_f_out_reg[62]_i_1_O_UNCONNECTED ;
  wire [7:7]\NLW_f_out_reg[62]_i_1_S_UNCONNECTED ;
  wire [6:0]\NLW_f_out_reg[71]_i_1_CO_UNCONNECTED ;
  wire [7:0]\NLW_f_out_reg[78]_i_1_CO_UNCONNECTED ;
  wire [7:7]\NLW_f_out_reg[78]_i_1_DI_UNCONNECTED ;
  wire [7:6]\NLW_f_out_reg[78]_i_1_O_UNCONNECTED ;
  wire [7:7]\NLW_f_out_reg[78]_i_1_S_UNCONNECTED ;
  wire [6:0]\NLW_f_out_reg[7]_i_1_CO_UNCONNECTED ;
  wire [6:0]\NLW_f_out_reg[87]_i_1_CO_UNCONNECTED ;
  wire [7:0]\NLW_f_out_reg[94]_i_1_CO_UNCONNECTED ;
  wire [7:7]\NLW_f_out_reg[94]_i_1_DI_UNCONNECTED ;
  wire [7:6]\NLW_f_out_reg[94]_i_1_O_UNCONNECTED ;
  wire [7:7]\NLW_f_out_reg[94]_i_1_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[0].g_val_reg0__36_carry_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[0].g_val_reg0__36_carry__0_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[0].g_val_reg0__36_carry__0_DI_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[0].g_val_reg0__36_carry__0_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[0].g_val_reg0__36_carry__0_S_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[0].g_val_reg0__36_carry__0_i_1_CO_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[0].g_val_reg0__36_carry__0_i_1_DI_UNCONNECTED ;
  wire [7:1]\NLW_genblk1[0].g_val_reg0__36_carry__0_i_1_O_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[0].g_val_reg0__36_carry__0_i_1_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[0].g_val_reg0__36_carry_i_1_CO_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[0].g_val_reg0_carry_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[0].g_val_reg0_carry__0_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[0].g_val_reg0_carry__0_DI_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[0].g_val_reg0_carry__0_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[0].g_val_reg0_carry__0_S_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[0].g_val_reg0_carry__0_i_2_CO_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[0].g_val_reg0_carry__0_i_2_DI_UNCONNECTED ;
  wire [7:1]\NLW_genblk1[0].g_val_reg0_carry__0_i_2_O_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[0].g_val_reg0_carry__0_i_2_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[0].g_val_reg0_carry_i_1_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[0].g_val_reg0_carry_i_26_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[0].g_val_reg0_carry_i_26_DI_UNCONNECTED ;
  wire [7:4]\NLW_genblk1[0].g_val_reg0_carry_i_26_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[0].g_val_reg0_carry_i_26_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[0].g_val_reg0_inferred__0/i__carry_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[0].g_val_reg0_inferred__0/i__carry__0_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[0].g_val_reg0_inferred__0/i__carry__0_DI_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[0].g_val_reg0_inferred__0/i__carry__0_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[0].g_val_reg0_inferred__0/i__carry__0_S_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[0].h_val_x_reg_reg[11]_i_1_CO_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[0].h_val_x_reg_reg[11]_i_1_DI_UNCONNECTED ;
  wire [7:1]\NLW_genblk1[0].h_val_x_reg_reg[11]_i_1_O_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[0].h_val_x_reg_reg[11]_i_1_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[0].h_val_x_reg_reg[9]_i_1_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[0].h_val_y_reg_reg[11]_i_1_CO_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[0].h_val_y_reg_reg[11]_i_1_DI_UNCONNECTED ;
  wire [7:1]\NLW_genblk1[0].h_val_y_reg_reg[11]_i_1_O_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[0].h_val_y_reg_reg[11]_i_1_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[0].h_val_y_reg_reg[9]_i_1_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[0].h_val_z_reg_reg[6]_i_1_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[0].h_val_z_reg_reg[6]_i_1_DI_UNCONNECTED ;
  wire [7:4]\NLW_genblk1[0].h_val_z_reg_reg[6]_i_1_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[0].h_val_z_reg_reg[6]_i_1_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[1].g_val_reg0__36_carry_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[1].g_val_reg0__36_carry__0_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[1].g_val_reg0__36_carry__0_DI_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[1].g_val_reg0__36_carry__0_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[1].g_val_reg0__36_carry__0_S_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[1].g_val_reg0__36_carry__0_i_1_CO_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[1].g_val_reg0__36_carry__0_i_1_DI_UNCONNECTED ;
  wire [7:1]\NLW_genblk1[1].g_val_reg0__36_carry__0_i_1_O_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[1].g_val_reg0__36_carry__0_i_1_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[1].g_val_reg0__36_carry_i_1_CO_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[1].g_val_reg0_carry_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[1].g_val_reg0_carry__0_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[1].g_val_reg0_carry__0_DI_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[1].g_val_reg0_carry__0_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[1].g_val_reg0_carry__0_S_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[1].g_val_reg0_carry__0_i_2_CO_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[1].g_val_reg0_carry__0_i_2_DI_UNCONNECTED ;
  wire [7:1]\NLW_genblk1[1].g_val_reg0_carry__0_i_2_O_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[1].g_val_reg0_carry__0_i_2_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[1].g_val_reg0_carry_i_1_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[1].g_val_reg0_carry_i_26_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[1].g_val_reg0_carry_i_26_DI_UNCONNECTED ;
  wire [7:4]\NLW_genblk1[1].g_val_reg0_carry_i_26_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[1].g_val_reg0_carry_i_26_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[1].g_val_reg0_inferred__0/i__carry_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[1].g_val_reg0_inferred__0/i__carry__0_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[1].g_val_reg0_inferred__0/i__carry__0_DI_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[1].g_val_reg0_inferred__0/i__carry__0_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[1].g_val_reg0_inferred__0/i__carry__0_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[1].h_val_x_reg_reg[23]_i_1_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[1].h_val_x_reg_reg[25]_i_1_CO_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[1].h_val_x_reg_reg[25]_i_1_DI_UNCONNECTED ;
  wire [7:1]\NLW_genblk1[1].h_val_x_reg_reg[25]_i_1_O_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[1].h_val_x_reg_reg[25]_i_1_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[1].h_val_y_reg_reg[23]_i_1_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[1].h_val_y_reg_reg[25]_i_1_CO_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[1].h_val_y_reg_reg[25]_i_1_DI_UNCONNECTED ;
  wire [7:1]\NLW_genblk1[1].h_val_y_reg_reg[25]_i_1_O_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[1].h_val_y_reg_reg[25]_i_1_S_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[1].h_val_z_reg_reg[20]_i_1_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[1].h_val_z_reg_reg[20]_i_1_DI_UNCONNECTED ;
  wire [7:4]\NLW_genblk1[1].h_val_z_reg_reg[20]_i_1_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[1].h_val_z_reg_reg[20]_i_1_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[2].g_val_reg0__36_carry_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[2].g_val_reg0__36_carry__0_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[2].g_val_reg0__36_carry__0_DI_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[2].g_val_reg0__36_carry__0_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[2].g_val_reg0__36_carry__0_S_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[2].g_val_reg0__36_carry__0_i_1_CO_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[2].g_val_reg0__36_carry__0_i_1_DI_UNCONNECTED ;
  wire [7:1]\NLW_genblk1[2].g_val_reg0__36_carry__0_i_1_O_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[2].g_val_reg0__36_carry__0_i_1_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[2].g_val_reg0__36_carry_i_1_CO_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[2].g_val_reg0_carry_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[2].g_val_reg0_carry__0_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[2].g_val_reg0_carry__0_DI_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[2].g_val_reg0_carry__0_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[2].g_val_reg0_carry__0_S_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[2].g_val_reg0_carry__0_i_2_CO_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[2].g_val_reg0_carry__0_i_2_DI_UNCONNECTED ;
  wire [7:1]\NLW_genblk1[2].g_val_reg0_carry__0_i_2_O_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[2].g_val_reg0_carry__0_i_2_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[2].g_val_reg0_carry_i_1_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[2].g_val_reg0_carry_i_26_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[2].g_val_reg0_carry_i_26_DI_UNCONNECTED ;
  wire [7:4]\NLW_genblk1[2].g_val_reg0_carry_i_26_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[2].g_val_reg0_carry_i_26_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[2].g_val_reg0_inferred__0/i__carry_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[2].g_val_reg0_inferred__0/i__carry__0_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[2].g_val_reg0_inferred__0/i__carry__0_DI_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[2].g_val_reg0_inferred__0/i__carry__0_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[2].g_val_reg0_inferred__0/i__carry__0_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[2].h_val_x_reg_reg[37]_i_1_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[2].h_val_x_reg_reg[39]_i_1_CO_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[2].h_val_x_reg_reg[39]_i_1_DI_UNCONNECTED ;
  wire [7:1]\NLW_genblk1[2].h_val_x_reg_reg[39]_i_1_O_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[2].h_val_x_reg_reg[39]_i_1_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[2].h_val_y_reg_reg[37]_i_1_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[2].h_val_y_reg_reg[39]_i_1_CO_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[2].h_val_y_reg_reg[39]_i_1_DI_UNCONNECTED ;
  wire [7:1]\NLW_genblk1[2].h_val_y_reg_reg[39]_i_1_O_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[2].h_val_y_reg_reg[39]_i_1_S_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[2].h_val_z_reg_reg[34]_i_1_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[2].h_val_z_reg_reg[34]_i_1_DI_UNCONNECTED ;
  wire [7:4]\NLW_genblk1[2].h_val_z_reg_reg[34]_i_1_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[2].h_val_z_reg_reg[34]_i_1_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[3].g_val_reg0__36_carry_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[3].g_val_reg0__36_carry__0_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[3].g_val_reg0__36_carry__0_DI_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[3].g_val_reg0__36_carry__0_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[3].g_val_reg0__36_carry__0_S_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[3].g_val_reg0__36_carry__0_i_1_CO_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[3].g_val_reg0__36_carry__0_i_1_DI_UNCONNECTED ;
  wire [7:1]\NLW_genblk1[3].g_val_reg0__36_carry__0_i_1_O_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[3].g_val_reg0__36_carry__0_i_1_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[3].g_val_reg0__36_carry_i_1_CO_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[3].g_val_reg0_carry_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[3].g_val_reg0_carry__0_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[3].g_val_reg0_carry__0_DI_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[3].g_val_reg0_carry__0_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[3].g_val_reg0_carry__0_S_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[3].g_val_reg0_carry__0_i_2_CO_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[3].g_val_reg0_carry__0_i_2_DI_UNCONNECTED ;
  wire [7:1]\NLW_genblk1[3].g_val_reg0_carry__0_i_2_O_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[3].g_val_reg0_carry__0_i_2_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[3].g_val_reg0_carry_i_1_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[3].g_val_reg0_carry_i_26_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[3].g_val_reg0_carry_i_26_DI_UNCONNECTED ;
  wire [7:4]\NLW_genblk1[3].g_val_reg0_carry_i_26_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[3].g_val_reg0_carry_i_26_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[3].g_val_reg0_inferred__0/i__carry_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[3].g_val_reg0_inferred__0/i__carry__0_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[3].g_val_reg0_inferred__0/i__carry__0_DI_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[3].g_val_reg0_inferred__0/i__carry__0_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[3].g_val_reg0_inferred__0/i__carry__0_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[3].h_val_x_reg_reg[51]_i_1_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[3].h_val_x_reg_reg[53]_i_1_CO_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[3].h_val_x_reg_reg[53]_i_1_DI_UNCONNECTED ;
  wire [7:1]\NLW_genblk1[3].h_val_x_reg_reg[53]_i_1_O_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[3].h_val_x_reg_reg[53]_i_1_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[3].h_val_y_reg_reg[51]_i_1_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[3].h_val_y_reg_reg[53]_i_1_CO_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[3].h_val_y_reg_reg[53]_i_1_DI_UNCONNECTED ;
  wire [7:1]\NLW_genblk1[3].h_val_y_reg_reg[53]_i_1_O_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[3].h_val_y_reg_reg[53]_i_1_S_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[3].h_val_z_reg_reg[48]_i_1_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[3].h_val_z_reg_reg[48]_i_1_DI_UNCONNECTED ;
  wire [7:4]\NLW_genblk1[3].h_val_z_reg_reg[48]_i_1_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[3].h_val_z_reg_reg[48]_i_1_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[4].g_val_reg0__36_carry_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[4].g_val_reg0__36_carry__0_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[4].g_val_reg0__36_carry__0_DI_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[4].g_val_reg0__36_carry__0_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[4].g_val_reg0__36_carry__0_S_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[4].g_val_reg0__36_carry__0_i_1_CO_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[4].g_val_reg0__36_carry__0_i_1_DI_UNCONNECTED ;
  wire [7:1]\NLW_genblk1[4].g_val_reg0__36_carry__0_i_1_O_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[4].g_val_reg0__36_carry__0_i_1_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[4].g_val_reg0__36_carry_i_1_CO_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[4].g_val_reg0_carry_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[4].g_val_reg0_carry__0_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[4].g_val_reg0_carry__0_DI_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[4].g_val_reg0_carry__0_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[4].g_val_reg0_carry__0_S_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[4].g_val_reg0_carry__0_i_2_CO_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[4].g_val_reg0_carry__0_i_2_DI_UNCONNECTED ;
  wire [7:1]\NLW_genblk1[4].g_val_reg0_carry__0_i_2_O_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[4].g_val_reg0_carry__0_i_2_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[4].g_val_reg0_carry_i_1_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[4].g_val_reg0_carry_i_26_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[4].g_val_reg0_carry_i_26_DI_UNCONNECTED ;
  wire [7:4]\NLW_genblk1[4].g_val_reg0_carry_i_26_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[4].g_val_reg0_carry_i_26_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[4].g_val_reg0_inferred__0/i__carry_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[4].g_val_reg0_inferred__0/i__carry__0_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[4].g_val_reg0_inferred__0/i__carry__0_DI_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[4].g_val_reg0_inferred__0/i__carry__0_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[4].g_val_reg0_inferred__0/i__carry__0_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[4].h_val_x_reg_reg[65]_i_1_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[4].h_val_x_reg_reg[67]_i_1_CO_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[4].h_val_x_reg_reg[67]_i_1_DI_UNCONNECTED ;
  wire [7:1]\NLW_genblk1[4].h_val_x_reg_reg[67]_i_1_O_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[4].h_val_x_reg_reg[67]_i_1_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[4].h_val_y_reg_reg[65]_i_1_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[4].h_val_y_reg_reg[67]_i_1_CO_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[4].h_val_y_reg_reg[67]_i_1_DI_UNCONNECTED ;
  wire [7:1]\NLW_genblk1[4].h_val_y_reg_reg[67]_i_1_O_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[4].h_val_y_reg_reg[67]_i_1_S_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[4].h_val_z_reg_reg[62]_i_1_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[4].h_val_z_reg_reg[62]_i_1_DI_UNCONNECTED ;
  wire [7:4]\NLW_genblk1[4].h_val_z_reg_reg[62]_i_1_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[4].h_val_z_reg_reg[62]_i_1_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[5].g_val_reg0__36_carry_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[5].g_val_reg0__36_carry__0_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[5].g_val_reg0__36_carry__0_DI_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[5].g_val_reg0__36_carry__0_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[5].g_val_reg0__36_carry__0_S_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[5].g_val_reg0__36_carry__0_i_1_CO_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[5].g_val_reg0__36_carry__0_i_1_DI_UNCONNECTED ;
  wire [7:1]\NLW_genblk1[5].g_val_reg0__36_carry__0_i_1_O_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[5].g_val_reg0__36_carry__0_i_1_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[5].g_val_reg0__36_carry_i_1_CO_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[5].g_val_reg0_carry_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[5].g_val_reg0_carry__0_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[5].g_val_reg0_carry__0_DI_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[5].g_val_reg0_carry__0_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[5].g_val_reg0_carry__0_S_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[5].g_val_reg0_carry__0_i_2_CO_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[5].g_val_reg0_carry__0_i_2_DI_UNCONNECTED ;
  wire [7:1]\NLW_genblk1[5].g_val_reg0_carry__0_i_2_O_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[5].g_val_reg0_carry__0_i_2_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[5].g_val_reg0_carry_i_1_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[5].g_val_reg0_carry_i_26_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[5].g_val_reg0_carry_i_26_DI_UNCONNECTED ;
  wire [7:4]\NLW_genblk1[5].g_val_reg0_carry_i_26_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[5].g_val_reg0_carry_i_26_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[5].g_val_reg0_inferred__0/i__carry_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[5].g_val_reg0_inferred__0/i__carry__0_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[5].g_val_reg0_inferred__0/i__carry__0_DI_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[5].g_val_reg0_inferred__0/i__carry__0_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[5].g_val_reg0_inferred__0/i__carry__0_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[5].h_val_x_reg_reg[79]_i_1_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[5].h_val_x_reg_reg[81]_i_1_CO_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[5].h_val_x_reg_reg[81]_i_1_DI_UNCONNECTED ;
  wire [7:1]\NLW_genblk1[5].h_val_x_reg_reg[81]_i_1_O_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[5].h_val_x_reg_reg[81]_i_1_S_UNCONNECTED ;
  wire [6:0]\NLW_genblk1[5].h_val_y_reg_reg[79]_i_1_CO_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[5].h_val_y_reg_reg[81]_i_1_CO_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[5].h_val_y_reg_reg[81]_i_1_DI_UNCONNECTED ;
  wire [7:1]\NLW_genblk1[5].h_val_y_reg_reg[81]_i_1_O_UNCONNECTED ;
  wire [7:2]\NLW_genblk1[5].h_val_y_reg_reg[81]_i_1_S_UNCONNECTED ;
  wire [7:0]\NLW_genblk1[5].h_val_z_reg_reg[76]_i_1_CO_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[5].h_val_z_reg_reg[76]_i_1_DI_UNCONNECTED ;
  wire [7:4]\NLW_genblk1[5].h_val_z_reg_reg[76]_i_1_O_UNCONNECTED ;
  wire [7:5]\NLW_genblk1[5].h_val_z_reg_reg[76]_i_1_S_UNCONNECTED ;
  wire [6:0]NLW_h_val_0__1_carry_CO_UNCONNECTED;
  wire [0:0]NLW_h_val_0__1_carry_O_UNCONNECTED;
  wire [7:0]NLW_h_val_0__1_carry__0_CO_UNCONNECTED;
  wire [7:6]NLW_h_val_0__1_carry__0_DI_UNCONNECTED;
  wire [7:5]NLW_h_val_0__1_carry__0_O_UNCONNECTED;
  wire [7:6]NLW_h_val_0__1_carry__0_S_UNCONNECTED;
  wire [6:0]NLW_h_val_14__1_carry_CO_UNCONNECTED;
  wire [0:0]NLW_h_val_14__1_carry_O_UNCONNECTED;
  wire [7:0]NLW_h_val_14__1_carry__0_CO_UNCONNECTED;
  wire [7:6]NLW_h_val_14__1_carry__0_DI_UNCONNECTED;
  wire [7:5]NLW_h_val_14__1_carry__0_O_UNCONNECTED;
  wire [7:6]NLW_h_val_14__1_carry__0_S_UNCONNECTED;
  wire [6:0]NLW_h_val_28__1_carry_CO_UNCONNECTED;
  wire [0:0]NLW_h_val_28__1_carry_O_UNCONNECTED;
  wire [7:0]NLW_h_val_28__1_carry__0_CO_UNCONNECTED;
  wire [7:6]NLW_h_val_28__1_carry__0_DI_UNCONNECTED;
  wire [7:5]NLW_h_val_28__1_carry__0_O_UNCONNECTED;
  wire [7:6]NLW_h_val_28__1_carry__0_S_UNCONNECTED;
  wire [6:0]NLW_h_val_42__1_carry_CO_UNCONNECTED;
  wire [0:0]NLW_h_val_42__1_carry_O_UNCONNECTED;
  wire [7:0]NLW_h_val_42__1_carry__0_CO_UNCONNECTED;
  wire [7:6]NLW_h_val_42__1_carry__0_DI_UNCONNECTED;
  wire [7:5]NLW_h_val_42__1_carry__0_O_UNCONNECTED;
  wire [7:6]NLW_h_val_42__1_carry__0_S_UNCONNECTED;
  wire [6:0]NLW_h_val_56__1_carry_CO_UNCONNECTED;
  wire [0:0]NLW_h_val_56__1_carry_O_UNCONNECTED;
  wire [7:0]NLW_h_val_56__1_carry__0_CO_UNCONNECTED;
  wire [7:6]NLW_h_val_56__1_carry__0_DI_UNCONNECTED;
  wire [7:5]NLW_h_val_56__1_carry__0_O_UNCONNECTED;
  wire [7:6]NLW_h_val_56__1_carry__0_S_UNCONNECTED;
  wire [6:0]NLW_h_val_70__1_carry_CO_UNCONNECTED;
  wire [0:0]NLW_h_val_70__1_carry_O_UNCONNECTED;
  wire [7:0]NLW_h_val_70__1_carry__0_CO_UNCONNECTED;
  wire [7:6]NLW_h_val_70__1_carry__0_DI_UNCONNECTED;
  wire [7:5]NLW_h_val_70__1_carry__0_O_UNCONNECTED;
  wire [7:6]NLW_h_val_70__1_carry__0_S_UNCONNECTED;

  (* OPT_MODIFIED = "PROPCONST" *) 
  GND GND_3
       (.G(h_val_70__40[0]));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[14]_i_2 
       (.I0(h_val_0__40[13]),
        .I1(g[12]),
        .O(\f_out[14]_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[14]_i_3 
       (.I0(h_val_0__40[12]),
        .I1(g[11]),
        .O(\f_out[14]_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[14]_i_4 
       (.I0(h_val_0__40[11]),
        .I1(g[10]),
        .O(\f_out[14]_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[14]_i_5 
       (.I0(h_val_0__40[10]),
        .I1(g[9]),
        .O(\f_out[14]_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[14]_i_6 
       (.I0(h_val_0__40[9]),
        .I1(g[8]),
        .O(\f_out[14]_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[14]_i_7 
       (.I0(h_val_0__40[8]),
        .I1(g[7]),
        .O(\f_out[14]_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[23]_i_2 
       (.I0(h_val_14__40[7]),
        .I1(g[19]),
        .O(\f_out[23]_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[23]_i_3 
       (.I0(h_val_14__40[6]),
        .I1(g[18]),
        .O(\f_out[23]_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[23]_i_4 
       (.I0(h_val_14__40[5]),
        .I1(g[17]),
        .O(\f_out[23]_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[23]_i_5 
       (.I0(h_val_14__40[4]),
        .I1(g[16]),
        .O(\f_out[23]_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[23]_i_6 
       (.I0(h_val_14__40[3]),
        .I1(g[15]),
        .O(\f_out[23]_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[23]_i_7 
       (.I0(h_val_14__40[2]),
        .I1(g[14]),
        .O(\f_out[23]_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[23]_i_8 
       (.I0(h_val_14__40[1]),
        .I1(g[13]),
        .O(\f_out[23]_i_8_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[30]_i_2 
       (.I0(h_val_14__40[13]),
        .I1(g[25]),
        .O(\f_out[30]_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[30]_i_3 
       (.I0(h_val_14__40[12]),
        .I1(g[24]),
        .O(\f_out[30]_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[30]_i_4 
       (.I0(h_val_14__40[11]),
        .I1(g[23]),
        .O(\f_out[30]_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[30]_i_5 
       (.I0(h_val_14__40[10]),
        .I1(g[22]),
        .O(\f_out[30]_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[30]_i_6 
       (.I0(h_val_14__40[9]),
        .I1(g[21]),
        .O(\f_out[30]_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[30]_i_7 
       (.I0(h_val_14__40[8]),
        .I1(g[20]),
        .O(\f_out[30]_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[39]_i_2 
       (.I0(h_val_28__40[7]),
        .I1(g[32]),
        .O(\f_out[39]_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[39]_i_3 
       (.I0(h_val_28__40[6]),
        .I1(g[31]),
        .O(\f_out[39]_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[39]_i_4 
       (.I0(h_val_28__40[5]),
        .I1(g[30]),
        .O(\f_out[39]_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[39]_i_5 
       (.I0(h_val_28__40[4]),
        .I1(g[29]),
        .O(\f_out[39]_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[39]_i_6 
       (.I0(h_val_28__40[3]),
        .I1(g[28]),
        .O(\f_out[39]_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[39]_i_7 
       (.I0(h_val_28__40[2]),
        .I1(g[27]),
        .O(\f_out[39]_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[39]_i_8 
       (.I0(h_val_28__40[1]),
        .I1(g[26]),
        .O(\f_out[39]_i_8_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[46]_i_2 
       (.I0(h_val_28__40[13]),
        .I1(g[38]),
        .O(\f_out[46]_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[46]_i_3 
       (.I0(h_val_28__40[12]),
        .I1(g[37]),
        .O(\f_out[46]_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[46]_i_4 
       (.I0(h_val_28__40[11]),
        .I1(g[36]),
        .O(\f_out[46]_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[46]_i_5 
       (.I0(h_val_28__40[10]),
        .I1(g[35]),
        .O(\f_out[46]_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[46]_i_6 
       (.I0(h_val_28__40[9]),
        .I1(g[34]),
        .O(\f_out[46]_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[46]_i_7 
       (.I0(h_val_28__40[8]),
        .I1(g[33]),
        .O(\f_out[46]_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[55]_i_2 
       (.I0(h_val_42__40[7]),
        .I1(g[45]),
        .O(\f_out[55]_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[55]_i_3 
       (.I0(h_val_42__40[6]),
        .I1(g[44]),
        .O(\f_out[55]_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[55]_i_4 
       (.I0(h_val_42__40[5]),
        .I1(g[43]),
        .O(\f_out[55]_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[55]_i_5 
       (.I0(h_val_42__40[4]),
        .I1(g[42]),
        .O(\f_out[55]_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[55]_i_6 
       (.I0(h_val_42__40[3]),
        .I1(g[41]),
        .O(\f_out[55]_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[55]_i_7 
       (.I0(h_val_42__40[2]),
        .I1(g[40]),
        .O(\f_out[55]_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[55]_i_8 
       (.I0(h_val_42__40[1]),
        .I1(g[39]),
        .O(\f_out[55]_i_8_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[62]_i_2 
       (.I0(h_val_42__40[13]),
        .I1(g[51]),
        .O(\f_out[62]_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[62]_i_3 
       (.I0(h_val_42__40[12]),
        .I1(g[50]),
        .O(\f_out[62]_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[62]_i_4 
       (.I0(h_val_42__40[11]),
        .I1(g[49]),
        .O(\f_out[62]_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[62]_i_5 
       (.I0(h_val_42__40[10]),
        .I1(g[48]),
        .O(\f_out[62]_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[62]_i_6 
       (.I0(h_val_42__40[9]),
        .I1(g[47]),
        .O(\f_out[62]_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[62]_i_7 
       (.I0(h_val_42__40[8]),
        .I1(g[46]),
        .O(\f_out[62]_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[71]_i_2 
       (.I0(h_val_56__40[7]),
        .I1(g[58]),
        .O(\f_out[71]_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[71]_i_3 
       (.I0(h_val_56__40[6]),
        .I1(g[57]),
        .O(\f_out[71]_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[71]_i_4 
       (.I0(h_val_56__40[5]),
        .I1(g[56]),
        .O(\f_out[71]_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[71]_i_5 
       (.I0(h_val_56__40[4]),
        .I1(g[55]),
        .O(\f_out[71]_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[71]_i_6 
       (.I0(h_val_56__40[3]),
        .I1(g[54]),
        .O(\f_out[71]_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[71]_i_7 
       (.I0(h_val_56__40[2]),
        .I1(g[53]),
        .O(\f_out[71]_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[71]_i_8 
       (.I0(h_val_56__40[1]),
        .I1(g[52]),
        .O(\f_out[71]_i_8_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[78]_i_2 
       (.I0(h_val_56__40[13]),
        .I1(g[64]),
        .O(\f_out[78]_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[78]_i_3 
       (.I0(h_val_56__40[12]),
        .I1(g[63]),
        .O(\f_out[78]_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[78]_i_4 
       (.I0(h_val_56__40[11]),
        .I1(g[62]),
        .O(\f_out[78]_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[78]_i_5 
       (.I0(h_val_56__40[10]),
        .I1(g[61]),
        .O(\f_out[78]_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[78]_i_6 
       (.I0(h_val_56__40[9]),
        .I1(g[60]),
        .O(\f_out[78]_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[78]_i_7 
       (.I0(h_val_56__40[8]),
        .I1(g[59]),
        .O(\f_out[78]_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[7]_i_2 
       (.I0(h_val_0__40[7]),
        .I1(g[6]),
        .O(\f_out[7]_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[7]_i_3 
       (.I0(h_val_0__40[6]),
        .I1(g[5]),
        .O(\f_out[7]_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[7]_i_4 
       (.I0(h_val_0__40[5]),
        .I1(g[4]),
        .O(\f_out[7]_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[7]_i_5 
       (.I0(h_val_0__40[4]),
        .I1(g[3]),
        .O(\f_out[7]_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[7]_i_6 
       (.I0(h_val_0__40[3]),
        .I1(g[2]),
        .O(\f_out[7]_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[7]_i_7 
       (.I0(h_val_0__40[2]),
        .I1(g[1]),
        .O(\f_out[7]_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[7]_i_8 
       (.I0(h_val_0__40[1]),
        .I1(g[0]),
        .O(\f_out[7]_i_8_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[87]_i_2 
       (.I0(h_val_70__40[7]),
        .I1(g[72]),
        .O(\f_out[87]_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[87]_i_3 
       (.I0(h_val_70__40[6]),
        .I1(g[71]),
        .O(\f_out[87]_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[87]_i_4 
       (.I0(h_val_70__40[5]),
        .I1(g[70]),
        .O(\f_out[87]_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[87]_i_5 
       (.I0(h_val_70__40[4]),
        .I1(g[69]),
        .O(\f_out[87]_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[87]_i_6 
       (.I0(h_val_70__40[3]),
        .I1(g[68]),
        .O(\f_out[87]_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[87]_i_7 
       (.I0(h_val_70__40[2]),
        .I1(g[67]),
        .O(\f_out[87]_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[87]_i_8 
       (.I0(h_val_70__40[1]),
        .I1(g[66]),
        .O(\f_out[87]_i_8_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[94]_i_2 
       (.I0(h_val_70__40[13]),
        .I1(g[78]),
        .O(\f_out[94]_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[94]_i_3 
       (.I0(h_val_70__40[12]),
        .I1(g[77]),
        .O(\f_out[94]_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[94]_i_4 
       (.I0(h_val_70__40[11]),
        .I1(g[76]),
        .O(\f_out[94]_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[94]_i_5 
       (.I0(h_val_70__40[10]),
        .I1(g[75]),
        .O(\f_out[94]_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[94]_i_6 
       (.I0(h_val_70__40[9]),
        .I1(g[74]),
        .O(\f_out[94]_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \f_out[94]_i_7 
       (.I0(h_val_70__40[8]),
        .I1(g[73]),
        .O(\f_out[94]_i_7_n_0 ));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \f_out_reg[14]_i_1 
       (.CI(\f_out_reg[7]_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_f_out_reg[14]_i_1_CO_UNCONNECTED [7],f_val[14],\NLW_f_out_reg[14]_i_1_CO_UNCONNECTED [5:0]}),
        .DI({\NLW_f_out_reg[14]_i_1_DI_UNCONNECTED [7],1'b0,h_val_0__40[13:8]}),
        .O({\NLW_f_out_reg[14]_i_1_O_UNCONNECTED [7:6],f_val[13:8]}),
        .S({\NLW_f_out_reg[14]_i_1_S_UNCONNECTED [7],1'b1,\f_out[14]_i_2_n_0 ,\f_out[14]_i_3_n_0 ,\f_out[14]_i_4_n_0 ,\f_out[14]_i_5_n_0 ,\f_out[14]_i_6_n_0 ,\f_out[14]_i_7_n_0 }));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \f_out_reg[23]_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\f_out_reg[23]_i_1_n_0 ,\NLW_f_out_reg[23]_i_1_CO_UNCONNECTED [6:0]}),
        .DI({h_val_14__40[7:1],h_val_70__40[0]}),
        .O(f_val[22:15]),
        .S({\f_out[23]_i_2_n_0 ,\f_out[23]_i_3_n_0 ,\f_out[23]_i_4_n_0 ,\f_out[23]_i_5_n_0 ,\f_out[23]_i_6_n_0 ,\f_out[23]_i_7_n_0 ,\f_out[23]_i_8_n_0 ,g[65]}));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \f_out_reg[30]_i_1 
       (.CI(\f_out_reg[23]_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_f_out_reg[30]_i_1_CO_UNCONNECTED [7],f_val[29],\NLW_f_out_reg[30]_i_1_CO_UNCONNECTED [5:0]}),
        .DI({\NLW_f_out_reg[30]_i_1_DI_UNCONNECTED [7],1'b0,h_val_14__40[13:8]}),
        .O({\NLW_f_out_reg[30]_i_1_O_UNCONNECTED [7:6],f_val[28:23]}),
        .S({\NLW_f_out_reg[30]_i_1_S_UNCONNECTED [7],1'b1,\f_out[30]_i_2_n_0 ,\f_out[30]_i_3_n_0 ,\f_out[30]_i_4_n_0 ,\f_out[30]_i_5_n_0 ,\f_out[30]_i_6_n_0 ,\f_out[30]_i_7_n_0 }));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \f_out_reg[39]_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\f_out_reg[39]_i_1_n_0 ,\NLW_f_out_reg[39]_i_1_CO_UNCONNECTED [6:0]}),
        .DI({h_val_28__40[7:1],h_val_70__40[0]}),
        .O(f_val[37:30]),
        .S({\f_out[39]_i_2_n_0 ,\f_out[39]_i_3_n_0 ,\f_out[39]_i_4_n_0 ,\f_out[39]_i_5_n_0 ,\f_out[39]_i_6_n_0 ,\f_out[39]_i_7_n_0 ,\f_out[39]_i_8_n_0 ,g[65]}));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \f_out_reg[46]_i_1 
       (.CI(\f_out_reg[39]_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_f_out_reg[46]_i_1_CO_UNCONNECTED [7],f_val[44],\NLW_f_out_reg[46]_i_1_CO_UNCONNECTED [5:0]}),
        .DI({\NLW_f_out_reg[46]_i_1_DI_UNCONNECTED [7],1'b0,h_val_28__40[13:8]}),
        .O({\NLW_f_out_reg[46]_i_1_O_UNCONNECTED [7:6],f_val[43:38]}),
        .S({\NLW_f_out_reg[46]_i_1_S_UNCONNECTED [7],1'b1,\f_out[46]_i_2_n_0 ,\f_out[46]_i_3_n_0 ,\f_out[46]_i_4_n_0 ,\f_out[46]_i_5_n_0 ,\f_out[46]_i_6_n_0 ,\f_out[46]_i_7_n_0 }));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \f_out_reg[55]_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\f_out_reg[55]_i_1_n_0 ,\NLW_f_out_reg[55]_i_1_CO_UNCONNECTED [6:0]}),
        .DI({h_val_42__40[7:1],h_val_70__40[0]}),
        .O(f_val[52:45]),
        .S({\f_out[55]_i_2_n_0 ,\f_out[55]_i_3_n_0 ,\f_out[55]_i_4_n_0 ,\f_out[55]_i_5_n_0 ,\f_out[55]_i_6_n_0 ,\f_out[55]_i_7_n_0 ,\f_out[55]_i_8_n_0 ,g[65]}));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \f_out_reg[62]_i_1 
       (.CI(\f_out_reg[55]_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_f_out_reg[62]_i_1_CO_UNCONNECTED [7],f_val[59],\NLW_f_out_reg[62]_i_1_CO_UNCONNECTED [5:0]}),
        .DI({\NLW_f_out_reg[62]_i_1_DI_UNCONNECTED [7],1'b0,h_val_42__40[13:8]}),
        .O({\NLW_f_out_reg[62]_i_1_O_UNCONNECTED [7:6],f_val[58:53]}),
        .S({\NLW_f_out_reg[62]_i_1_S_UNCONNECTED [7],1'b1,\f_out[62]_i_2_n_0 ,\f_out[62]_i_3_n_0 ,\f_out[62]_i_4_n_0 ,\f_out[62]_i_5_n_0 ,\f_out[62]_i_6_n_0 ,\f_out[62]_i_7_n_0 }));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \f_out_reg[71]_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\f_out_reg[71]_i_1_n_0 ,\NLW_f_out_reg[71]_i_1_CO_UNCONNECTED [6:0]}),
        .DI({h_val_56__40[7:1],h_val_70__40[0]}),
        .O(f_val[67:60]),
        .S({\f_out[71]_i_2_n_0 ,\f_out[71]_i_3_n_0 ,\f_out[71]_i_4_n_0 ,\f_out[71]_i_5_n_0 ,\f_out[71]_i_6_n_0 ,\f_out[71]_i_7_n_0 ,\f_out[71]_i_8_n_0 ,g[65]}));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \f_out_reg[78]_i_1 
       (.CI(\f_out_reg[71]_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_f_out_reg[78]_i_1_CO_UNCONNECTED [7],f_val[74],\NLW_f_out_reg[78]_i_1_CO_UNCONNECTED [5:0]}),
        .DI({\NLW_f_out_reg[78]_i_1_DI_UNCONNECTED [7],1'b0,h_val_56__40[13:8]}),
        .O({\NLW_f_out_reg[78]_i_1_O_UNCONNECTED [7:6],f_val[73:68]}),
        .S({\NLW_f_out_reg[78]_i_1_S_UNCONNECTED [7],1'b1,\f_out[78]_i_2_n_0 ,\f_out[78]_i_3_n_0 ,\f_out[78]_i_4_n_0 ,\f_out[78]_i_5_n_0 ,\f_out[78]_i_6_n_0 ,\f_out[78]_i_7_n_0 }));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \f_out_reg[7]_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\f_out_reg[7]_i_1_n_0 ,\NLW_f_out_reg[7]_i_1_CO_UNCONNECTED [6:0]}),
        .DI({h_val_0__40[7:1],h_val_70__40[0]}),
        .O(f_val[7:0]),
        .S({\f_out[7]_i_2_n_0 ,\f_out[7]_i_3_n_0 ,\f_out[7]_i_4_n_0 ,\f_out[7]_i_5_n_0 ,\f_out[7]_i_6_n_0 ,\f_out[7]_i_7_n_0 ,\f_out[7]_i_8_n_0 ,g[65]}));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \f_out_reg[87]_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\f_out_reg[87]_i_1_n_0 ,\NLW_f_out_reg[87]_i_1_CO_UNCONNECTED [6:0]}),
        .DI(h_val_70__40[7:0]),
        .O(f_val[82:75]),
        .S({\f_out[87]_i_2_n_0 ,\f_out[87]_i_3_n_0 ,\f_out[87]_i_4_n_0 ,\f_out[87]_i_5_n_0 ,\f_out[87]_i_6_n_0 ,\f_out[87]_i_7_n_0 ,\f_out[87]_i_8_n_0 ,g[65]}));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \f_out_reg[94]_i_1 
       (.CI(\f_out_reg[87]_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_f_out_reg[94]_i_1_CO_UNCONNECTED [7],f_val[89],\NLW_f_out_reg[94]_i_1_CO_UNCONNECTED [5:0]}),
        .DI({\NLW_f_out_reg[94]_i_1_DI_UNCONNECTED [7],1'b0,h_val_70__40[13:8]}),
        .O({\NLW_f_out_reg[94]_i_1_O_UNCONNECTED [7:6],f_val[88:83]}),
        .S({\NLW_f_out_reg[94]_i_1_S_UNCONNECTED [7],1'b1,\f_out[94]_i_2_n_0 ,\f_out[94]_i_3_n_0 ,\f_out[94]_i_4_n_0 ,\f_out[94]_i_5_n_0 ,\f_out[94]_i_6_n_0 ,\f_out[94]_i_7_n_0 }));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[0].g_val_reg0__36_carry 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[0].g_val_reg0__36_carry_n_0 ,\NLW_genblk1[0].g_val_reg0__36_carry_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[0].g_val_reg3__6 [8:2],C[1]}),
        .O({\genblk1[0].g_val_reg0__36_carry_n_8 ,\genblk1[0].g_val_reg0__36_carry_n_9 ,\genblk1[0].g_val_reg0__36_carry_n_10 ,\genblk1[0].g_val_reg0__36_carry_n_11 ,\genblk1[0].g_val_reg0__36_carry_n_12 ,\genblk1[0].g_val_reg0__36_carry_n_13 ,\genblk1[0].g_val_reg0__36_carry_n_14 ,\genblk1[0].g_val_reg0__36_carry_n_15 }),
        .S({\genblk1[0].g_val_reg0__36_carry_i_2_n_0 ,\genblk1[0].g_val_reg0__36_carry_i_3_n_0 ,\genblk1[0].g_val_reg0__36_carry_i_4_n_0 ,\genblk1[0].g_val_reg0__36_carry_i_5_n_0 ,\genblk1[0].g_val_reg0__36_carry_i_6_n_0 ,\genblk1[0].g_val_reg0__36_carry_i_7_n_0 ,\genblk1[0].g_val_reg0__36_carry_i_8_n_0 ,\genblk1[0].g_val_reg0__36_carry_i_9_n_0 }));
  (* ADDER_THRESHOLD = "35" *) 
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[0].g_val_reg0__36_carry__0 
       (.CI(\genblk1[0].g_val_reg0__36_carry_n_0 ),
        .CI_TOP(1'b0),
        .CO(\NLW_genblk1[0].g_val_reg0__36_carry__0_CO_UNCONNECTED [7:0]),
        .DI({\NLW_genblk1[0].g_val_reg0__36_carry__0_DI_UNCONNECTED [7:5],1'b0,C[12],\genblk1[0].g_val_reg3__6 [11:9]}),
        .O({\NLW_genblk1[0].g_val_reg0__36_carry__0_O_UNCONNECTED [7:5],\genblk1[0].g_val_reg0__36_carry__0_n_11 ,\genblk1[0].g_val_reg0__36_carry__0_n_12 ,\genblk1[0].g_val_reg0__36_carry__0_n_13 ,\genblk1[0].g_val_reg0__36_carry__0_n_14 ,\genblk1[0].g_val_reg0__36_carry__0_n_15 }),
        .S({\NLW_genblk1[0].g_val_reg0__36_carry__0_S_UNCONNECTED [7:5],\genblk1[0].g_val_reg0__36_carry__0_i_2_n_0 ,\genblk1[0].g_val_reg0__36_carry__0_i_3_n_0 ,\genblk1[0].g_val_reg0__36_carry__0_i_4_n_0 ,\genblk1[0].g_val_reg0__36_carry__0_i_5_n_0 ,\genblk1[0].g_val_reg0__36_carry__0_i_6_n_0 }));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[0].g_val_reg0__36_carry__0_i_1 
       (.CI(\genblk1[0].g_val_reg0__36_carry_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[0].g_val_reg0__36_carry__0_i_1_CO_UNCONNECTED [7:2],\genblk1[0].g_val_reg3__6 [11],\NLW_genblk1[0].g_val_reg0__36_carry__0_i_1_CO_UNCONNECTED [0]}),
        .DI({\NLW_genblk1[0].g_val_reg0__36_carry__0_i_1_DI_UNCONNECTED [7:2],1'b0,A[9]}),
        .O({\NLW_genblk1[0].g_val_reg0__36_carry__0_i_1_O_UNCONNECTED [7:1],\genblk1[0].g_val_reg3__6 [10]}),
        .S({\NLW_genblk1[0].g_val_reg0__36_carry__0_i_1_S_UNCONNECTED [7:2],1'b1,\genblk1[0].g_val_reg0__36_carry__0_i_7_n_0 }));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0__36_carry__0_i_2 
       (.I0(A[9]),
        .I1(C[13]),
        .O(\genblk1[0].g_val_reg0__36_carry__0_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0__36_carry__0_i_3 
       (.I0(A[9]),
        .I1(C[12]),
        .O(\genblk1[0].g_val_reg0__36_carry__0_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0__36_carry__0_i_4 
       (.I0(\genblk1[0].g_val_reg3__6 [11]),
        .I1(C[11]),
        .O(\genblk1[0].g_val_reg0__36_carry__0_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0__36_carry__0_i_5 
       (.I0(\genblk1[0].g_val_reg3__6 [10]),
        .I1(C[10]),
        .O(\genblk1[0].g_val_reg0__36_carry__0_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0__36_carry__0_i_6 
       (.I0(\genblk1[0].g_val_reg3__6 [9]),
        .I1(C[9]),
        .O(\genblk1[0].g_val_reg0__36_carry__0_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0__36_carry__0_i_7 
       (.I0(A[9]),
        .I1(A[7]),
        .O(\genblk1[0].g_val_reg0__36_carry__0_i_7_n_0 ));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[0].g_val_reg0__36_carry_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[0].g_val_reg0__36_carry_i_1_n_0 ,\NLW_genblk1[0].g_val_reg0__36_carry_i_1_CO_UNCONNECTED [6:0]}),
        .DI({A[9],A[7:2],1'b0}),
        .O(\genblk1[0].g_val_reg3__6 [9:2]),
        .S({\genblk1[0].g_val_reg0__36_carry_i_17_n_0 ,\genblk1[0].g_val_reg0__36_carry_i_18_n_0 ,\genblk1[0].g_val_reg0__36_carry_i_19_n_0 ,\genblk1[0].g_val_reg0__36_carry_i_20_n_0 ,\genblk1[0].g_val_reg0__36_carry_i_21_n_0 ,\genblk1[0].g_val_reg0__36_carry_i_22_n_0 ,\genblk1[0].g_val_reg0__36_carry_i_23_n_0 ,A[1]}));
  LUT3 #(
    .INIT(8'h2B)) 
    \genblk1[0].g_val_reg0__36_carry_i_10 
       (.I0(px_q[7]),
        .I1(cx_q[7]),
        .I2(\genblk1[0].g_val_reg0__36_carry_i_25_n_0 ),
        .O(A[9]));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[0].g_val_reg0__36_carry_i_11 
       (.I0(\genblk1[0].g_val_reg0__36_carry_i_25_n_0 ),
        .I1(px_q[7]),
        .I2(cx_q[7]),
        .O(A[7]));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[0].g_val_reg0__36_carry_i_12 
       (.I0(\genblk1[0].g_val_reg0__36_carry_i_26_n_0 ),
        .I1(cx_q[5]),
        .I2(px_q[5]),
        .I3(px_q[6]),
        .I4(cx_q[6]),
        .O(A[6]));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[0].g_val_reg0__36_carry_i_13 
       (.I0(\genblk1[0].g_val_reg0__36_carry_i_26_n_0 ),
        .I1(px_q[5]),
        .I2(cx_q[5]),
        .O(A[5]));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[0].g_val_reg0__36_carry_i_14 
       (.I0(\genblk1[0].g_val_reg0__36_carry_i_27_n_0 ),
        .I1(cx_q[3]),
        .I2(px_q[3]),
        .I3(px_q[4]),
        .I4(cx_q[4]),
        .O(A[4]));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[0].g_val_reg0__36_carry_i_15 
       (.I0(\genblk1[0].g_val_reg0__36_carry_i_27_n_0 ),
        .I1(px_q[3]),
        .I2(cx_q[3]),
        .O(A[3]));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[0].g_val_reg0__36_carry_i_16 
       (.I0(cx_q[0]),
        .I1(px_q[0]),
        .I2(cx_q[1]),
        .I3(px_q[1]),
        .I4(px_q[2]),
        .I5(cx_q[2]),
        .O(A[2]));
  LUT6 #(
    .INIT(64'h9696699669966969)) 
    \genblk1[0].g_val_reg0__36_carry_i_17 
       (.I0(A[9]),
        .I1(cx_q[6]),
        .I2(px_q[6]),
        .I3(px_q[5]),
        .I4(cx_q[5]),
        .I5(\genblk1[0].g_val_reg0__36_carry_i_26_n_0 ),
        .O(\genblk1[0].g_val_reg0__36_carry_i_17_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[0].g_val_reg0__36_carry_i_18 
       (.I0(A[7]),
        .I1(cx_q[5]),
        .I2(px_q[5]),
        .I3(\genblk1[0].g_val_reg0__36_carry_i_26_n_0 ),
        .O(\genblk1[0].g_val_reg0__36_carry_i_18_n_0 ));
  LUT6 #(
    .INIT(64'h9969696666969699)) 
    \genblk1[0].g_val_reg0__36_carry_i_19 
       (.I0(cx_q[6]),
        .I1(px_q[6]),
        .I2(px_q[5]),
        .I3(cx_q[5]),
        .I4(\genblk1[0].g_val_reg0__36_carry_i_26_n_0 ),
        .I5(A[4]),
        .O(\genblk1[0].g_val_reg0__36_carry_i_19_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0__36_carry_i_2 
       (.I0(\genblk1[0].g_val_reg3__6 [8]),
        .I1(C[8]),
        .O(\genblk1[0].g_val_reg0__36_carry_i_2_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[0].g_val_reg0__36_carry_i_20 
       (.I0(cx_q[5]),
        .I1(px_q[5]),
        .I2(\genblk1[0].g_val_reg0__36_carry_i_26_n_0 ),
        .I3(A[3]),
        .O(\genblk1[0].g_val_reg0__36_carry_i_20_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0__36_carry_i_21 
       (.I0(A[4]),
        .I1(A[2]),
        .O(\genblk1[0].g_val_reg0__36_carry_i_21_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[0].g_val_reg0__36_carry_i_22 
       (.I0(A[3]),
        .I1(cx_q[1]),
        .I2(px_q[1]),
        .I3(cx_q[0]),
        .I4(px_q[0]),
        .O(\genblk1[0].g_val_reg0__36_carry_i_22_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[0].g_val_reg0__36_carry_i_23 
       (.I0(cx_q[2]),
        .I1(px_q[2]),
        .I2(px_q[1]),
        .I3(cx_q[1]),
        .I4(px_q[0]),
        .I5(cx_q[0]),
        .O(\genblk1[0].g_val_reg0__36_carry_i_23_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[0].g_val_reg0__36_carry_i_24 
       (.I0(px_q[0]),
        .I1(cx_q[0]),
        .I2(px_q[1]),
        .I3(cx_q[1]),
        .O(A[1]));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[0].g_val_reg0__36_carry_i_25 
       (.I0(px_q[6]),
        .I1(cx_q[6]),
        .I2(\genblk1[0].g_val_reg0__36_carry_i_26_n_0 ),
        .I3(cx_q[5]),
        .I4(px_q[5]),
        .O(\genblk1[0].g_val_reg0__36_carry_i_25_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[0].g_val_reg0__36_carry_i_26 
       (.I0(px_q[4]),
        .I1(cx_q[4]),
        .I2(\genblk1[0].g_val_reg0__36_carry_i_27_n_0 ),
        .I3(cx_q[3]),
        .I4(px_q[3]),
        .O(\genblk1[0].g_val_reg0__36_carry_i_26_n_0 ));
  LUT6 #(
    .INIT(64'hD4DD4444DDDDD4DD)) 
    \genblk1[0].g_val_reg0__36_carry_i_27 
       (.I0(px_q[2]),
        .I1(cx_q[2]),
        .I2(cx_q[0]),
        .I3(px_q[0]),
        .I4(cx_q[1]),
        .I5(px_q[1]),
        .O(\genblk1[0].g_val_reg0__36_carry_i_27_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0__36_carry_i_3 
       (.I0(\genblk1[0].g_val_reg3__6 [7]),
        .I1(C[7]),
        .O(\genblk1[0].g_val_reg0__36_carry_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0__36_carry_i_4 
       (.I0(\genblk1[0].g_val_reg3__6 [6]),
        .I1(C[6]),
        .O(\genblk1[0].g_val_reg0__36_carry_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0__36_carry_i_5 
       (.I0(\genblk1[0].g_val_reg3__6 [5]),
        .I1(C[5]),
        .O(\genblk1[0].g_val_reg0__36_carry_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0__36_carry_i_6 
       (.I0(\genblk1[0].g_val_reg3__6 [4]),
        .I1(C[4]),
        .O(\genblk1[0].g_val_reg0__36_carry_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0__36_carry_i_7 
       (.I0(\genblk1[0].g_val_reg3__6 [3]),
        .I1(C[3]),
        .O(\genblk1[0].g_val_reg0__36_carry_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0__36_carry_i_8 
       (.I0(\genblk1[0].g_val_reg3__6 [2]),
        .I1(C[2]),
        .O(\genblk1[0].g_val_reg0__36_carry_i_8_n_0 ));
  LUT3 #(
    .INIT(8'h96)) 
    \genblk1[0].g_val_reg0__36_carry_i_9 
       (.I0(px_q[0]),
        .I1(cx_q[0]),
        .I2(C[1]),
        .O(\genblk1[0].g_val_reg0__36_carry_i_9_n_0 ));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[0].g_val_reg0_carry 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[0].g_val_reg0_carry_n_0 ,\NLW_genblk1[0].g_val_reg0_carry_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[0].g_val_reg2__1 [8:2],\genblk1[0].g_val_reg0_carry_i_2_n_0 }),
        .O(C[8:1]),
        .S({\genblk1[0].g_val_reg0_carry_i_3_n_0 ,\genblk1[0].g_val_reg0_carry_i_4_n_0 ,\genblk1[0].g_val_reg0_carry_i_5_n_0 ,\genblk1[0].g_val_reg0_carry_i_6_n_0 ,\genblk1[0].g_val_reg0_carry_i_7_n_0 ,\genblk1[0].g_val_reg0_carry_i_8_n_0 ,\genblk1[0].g_val_reg0_carry_i_9_n_0 ,\genblk1[0].g_val_reg0_carry_i_10_n_0 }));
  (* ADDER_THRESHOLD = "35" *) 
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[0].g_val_reg0_carry__0 
       (.CI(\genblk1[0].g_val_reg0_carry_n_0 ),
        .CI_TOP(1'b0),
        .CO(\NLW_genblk1[0].g_val_reg0_carry__0_CO_UNCONNECTED [7:0]),
        .DI({\NLW_genblk1[0].g_val_reg0_carry__0_DI_UNCONNECTED [7:5],1'b0,\genblk1[0].g_val_reg0_carry__0_i_1_n_0 ,\genblk1[0].g_val_reg2__1 [11:9]}),
        .O({\NLW_genblk1[0].g_val_reg0_carry__0_O_UNCONNECTED [7:5],C[13:9]}),
        .S({\NLW_genblk1[0].g_val_reg0_carry__0_S_UNCONNECTED [7:5],\genblk1[0].g_val_reg0_carry__0_i_3_n_0 ,\genblk1[0].g_val_reg0_carry__0_i_4_n_0 ,\genblk1[0].g_val_reg0_carry__0_i_5_n_0 ,\genblk1[0].g_val_reg0_carry__0_i_6_n_0 ,\genblk1[0].g_val_reg0_carry__0_i_7_n_0 }));
  LUT3 #(
    .INIT(8'h2B)) 
    \genblk1[0].g_val_reg0_carry__0_i_1 
       (.I0(py_q[7]),
        .I1(cy_q[7]),
        .I2(\genblk1[0].g_val_reg0_carry__0_i_8_n_0 ),
        .O(\genblk1[0].g_val_reg0_carry__0_i_1_n_0 ));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[0].g_val_reg0_carry__0_i_2 
       (.CI(\genblk1[0].g_val_reg0_carry_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[0].g_val_reg0_carry__0_i_2_CO_UNCONNECTED [7:2],\genblk1[0].g_val_reg2__1 [11],\NLW_genblk1[0].g_val_reg0_carry__0_i_2_CO_UNCONNECTED [0]}),
        .DI({\NLW_genblk1[0].g_val_reg0_carry__0_i_2_DI_UNCONNECTED [7:2],1'b0,\genblk1[0].g_val_reg0_carry__0_i_1_n_0 }),
        .O({\NLW_genblk1[0].g_val_reg0_carry__0_i_2_O_UNCONNECTED [7:1],\genblk1[0].g_val_reg2__1 [10]}),
        .S({\NLW_genblk1[0].g_val_reg0_carry__0_i_2_S_UNCONNECTED [7:2],1'b1,\genblk1[0].g_val_reg0_carry__0_i_9_n_0 }));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0_carry__0_i_3 
       (.I0(\genblk1[0].g_val_reg0_carry__0_i_1_n_0 ),
        .I1(\genblk1[0].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[0].g_val_reg0_carry__0_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0_carry__0_i_4 
       (.I0(\genblk1[0].g_val_reg0_carry__0_i_1_n_0 ),
        .I1(\genblk1[0].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[0].g_val_reg0_carry__0_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0_carry__0_i_5 
       (.I0(\genblk1[0].g_val_reg2__1 [11]),
        .I1(\genblk1[0].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[0].g_val_reg0_carry__0_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0_carry__0_i_6 
       (.I0(\genblk1[0].g_val_reg2__1 [10]),
        .I1(\genblk1[0].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[0].g_val_reg0_carry__0_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0_carry__0_i_7 
       (.I0(\genblk1[0].g_val_reg2__1 [9]),
        .I1(\genblk1[0].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[0].g_val_reg0_carry__0_i_7_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[0].g_val_reg0_carry__0_i_8 
       (.I0(py_q[6]),
        .I1(cy_q[6]),
        .I2(\genblk1[0].g_val_reg0_carry_i_27_n_0 ),
        .I3(cy_q[5]),
        .I4(py_q[5]),
        .O(\genblk1[0].g_val_reg0_carry__0_i_8_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0_carry__0_i_9 
       (.I0(\genblk1[0].g_val_reg0_carry__0_i_1_n_0 ),
        .I1(\genblk1[0].g_val_reg0_carry_i_11_n_0 ),
        .O(\genblk1[0].g_val_reg0_carry__0_i_9_n_0 ));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[0].g_val_reg0_carry_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[0].g_val_reg0_carry_i_1_n_0 ,\NLW_genblk1[0].g_val_reg0_carry_i_1_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[0].g_val_reg0_carry__0_i_1_n_0 ,\genblk1[0].g_val_reg0_carry_i_11_n_0 ,\genblk1[0].g_val_reg0_carry_i_12_n_0 ,\genblk1[0].g_val_reg0_carry_i_13_n_0 ,\genblk1[0].g_val_reg0_carry_i_14_n_0 ,\genblk1[0].g_val_reg0_carry_i_15_n_0 ,\genblk1[0].g_val_reg0_carry_i_16_n_0 ,1'b0}),
        .O(\genblk1[0].g_val_reg2__1 [9:2]),
        .S({\genblk1[0].g_val_reg0_carry_i_17_n_0 ,\genblk1[0].g_val_reg0_carry_i_18_n_0 ,\genblk1[0].g_val_reg0_carry_i_19_n_0 ,\genblk1[0].g_val_reg0_carry_i_20_n_0 ,\genblk1[0].g_val_reg0_carry_i_21_n_0 ,\genblk1[0].g_val_reg0_carry_i_22_n_0 ,\genblk1[0].g_val_reg0_carry_i_23_n_0 ,\genblk1[0].g_val_reg0_carry_i_24_n_0 }));
  LUT4 #(
    .INIT(16'h6996)) 
    \genblk1[0].g_val_reg0_carry_i_10 
       (.I0(py_q[0]),
        .I1(cy_q[0]),
        .I2(pz_q[0]),
        .I3(cz_q[0]),
        .O(\genblk1[0].g_val_reg0_carry_i_10_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[0].g_val_reg0_carry_i_11 
       (.I0(\genblk1[0].g_val_reg0_carry__0_i_8_n_0 ),
        .I1(py_q[7]),
        .I2(cy_q[7]),
        .O(\genblk1[0].g_val_reg0_carry_i_11_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[0].g_val_reg0_carry_i_12 
       (.I0(\genblk1[0].g_val_reg0_carry_i_27_n_0 ),
        .I1(cy_q[5]),
        .I2(py_q[5]),
        .I3(py_q[6]),
        .I4(cy_q[6]),
        .O(\genblk1[0].g_val_reg0_carry_i_12_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[0].g_val_reg0_carry_i_13 
       (.I0(\genblk1[0].g_val_reg0_carry_i_27_n_0 ),
        .I1(py_q[5]),
        .I2(cy_q[5]),
        .O(\genblk1[0].g_val_reg0_carry_i_13_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[0].g_val_reg0_carry_i_14 
       (.I0(\genblk1[0].g_val_reg0_carry_i_28_n_0 ),
        .I1(cy_q[3]),
        .I2(py_q[3]),
        .I3(py_q[4]),
        .I4(cy_q[4]),
        .O(\genblk1[0].g_val_reg0_carry_i_14_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[0].g_val_reg0_carry_i_15 
       (.I0(\genblk1[0].g_val_reg0_carry_i_28_n_0 ),
        .I1(py_q[3]),
        .I2(cy_q[3]),
        .O(\genblk1[0].g_val_reg0_carry_i_15_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[0].g_val_reg0_carry_i_16 
       (.I0(cy_q[0]),
        .I1(py_q[0]),
        .I2(cy_q[1]),
        .I3(py_q[1]),
        .I4(py_q[2]),
        .I5(cy_q[2]),
        .O(\genblk1[0].g_val_reg0_carry_i_16_n_0 ));
  LUT6 #(
    .INIT(64'h9696699669966969)) 
    \genblk1[0].g_val_reg0_carry_i_17 
       (.I0(\genblk1[0].g_val_reg0_carry__0_i_1_n_0 ),
        .I1(cy_q[6]),
        .I2(py_q[6]),
        .I3(py_q[5]),
        .I4(cy_q[5]),
        .I5(\genblk1[0].g_val_reg0_carry_i_27_n_0 ),
        .O(\genblk1[0].g_val_reg0_carry_i_17_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[0].g_val_reg0_carry_i_18 
       (.I0(\genblk1[0].g_val_reg0_carry_i_11_n_0 ),
        .I1(cy_q[5]),
        .I2(py_q[5]),
        .I3(\genblk1[0].g_val_reg0_carry_i_27_n_0 ),
        .O(\genblk1[0].g_val_reg0_carry_i_18_n_0 ));
  LUT6 #(
    .INIT(64'h9969696666969699)) 
    \genblk1[0].g_val_reg0_carry_i_19 
       (.I0(cy_q[6]),
        .I1(py_q[6]),
        .I2(py_q[5]),
        .I3(cy_q[5]),
        .I4(\genblk1[0].g_val_reg0_carry_i_27_n_0 ),
        .I5(\genblk1[0].g_val_reg0_carry_i_14_n_0 ),
        .O(\genblk1[0].g_val_reg0_carry_i_19_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0_carry_i_2 
       (.I0(py_q[0]),
        .I1(cy_q[0]),
        .O(\genblk1[0].g_val_reg0_carry_i_2_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[0].g_val_reg0_carry_i_20 
       (.I0(cy_q[5]),
        .I1(py_q[5]),
        .I2(\genblk1[0].g_val_reg0_carry_i_27_n_0 ),
        .I3(\genblk1[0].g_val_reg0_carry_i_15_n_0 ),
        .O(\genblk1[0].g_val_reg0_carry_i_20_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0_carry_i_21 
       (.I0(\genblk1[0].g_val_reg0_carry_i_14_n_0 ),
        .I1(\genblk1[0].g_val_reg0_carry_i_16_n_0 ),
        .O(\genblk1[0].g_val_reg0_carry_i_21_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[0].g_val_reg0_carry_i_22 
       (.I0(\genblk1[0].g_val_reg0_carry_i_15_n_0 ),
        .I1(cy_q[1]),
        .I2(py_q[1]),
        .I3(cy_q[0]),
        .I4(py_q[0]),
        .O(\genblk1[0].g_val_reg0_carry_i_22_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[0].g_val_reg0_carry_i_23 
       (.I0(cy_q[2]),
        .I1(py_q[2]),
        .I2(py_q[1]),
        .I3(cy_q[1]),
        .I4(py_q[0]),
        .I5(cy_q[0]),
        .O(\genblk1[0].g_val_reg0_carry_i_23_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[0].g_val_reg0_carry_i_24 
       (.I0(py_q[0]),
        .I1(cy_q[0]),
        .I2(py_q[1]),
        .I3(cy_q[1]),
        .O(\genblk1[0].g_val_reg0_carry_i_24_n_0 ));
  LUT6 #(
    .INIT(64'h2B22BBBB22222B22)) 
    \genblk1[0].g_val_reg0_carry_i_25 
       (.I0(pz_q[2]),
        .I1(cz_q[2]),
        .I2(cz_q[0]),
        .I3(pz_q[0]),
        .I4(cz_q[1]),
        .I5(pz_q[1]),
        .O(\genblk1[0].g_val_reg0_carry_i_25_n_0 ));
  (* OPT_MODIFIED = "RETARGET PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[0].g_val_reg0_carry_i_26 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[0].g_val_reg0_carry_i_26_CO_UNCONNECTED [7:5],\genblk1[0].g_val_reg1 [6],\NLW_genblk1[0].g_val_reg0_carry_i_26_CO_UNCONNECTED [3:0]}),
        .DI({\NLW_genblk1[0].g_val_reg0_carry_i_26_DI_UNCONNECTED [7:5],1'b0,\genblk1[0].g_val_reg0_carry_i_25_n_0 ,\genblk1[0].g_val_reg0_carry_i_25_n_0 ,\genblk1[0].g_val_reg0_carry_i_29_n_0 ,1'b0}),
        .O({\NLW_genblk1[0].g_val_reg0_carry_i_26_O_UNCONNECTED [7:4],\genblk1[0].g_val_reg1 [5:2]}),
        .S({\NLW_genblk1[0].g_val_reg0_carry_i_26_S_UNCONNECTED [7:5],1'b1,\genblk1[0].g_val_reg0_carry_i_30_n_0 ,\genblk1[0].g_val_reg0_carry_i_31_n_0 ,S}));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[0].g_val_reg0_carry_i_27 
       (.I0(py_q[4]),
        .I1(cy_q[4]),
        .I2(\genblk1[0].g_val_reg0_carry_i_28_n_0 ),
        .I3(cy_q[3]),
        .I4(py_q[3]),
        .O(\genblk1[0].g_val_reg0_carry_i_27_n_0 ));
  LUT6 #(
    .INIT(64'hD4DD4444DDDDD4DD)) 
    \genblk1[0].g_val_reg0_carry_i_28 
       (.I0(py_q[2]),
        .I1(cy_q[2]),
        .I2(cy_q[0]),
        .I3(py_q[0]),
        .I4(cy_q[1]),
        .I5(py_q[1]),
        .O(\genblk1[0].g_val_reg0_carry_i_28_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[0].g_val_reg0_carry_i_29 
       (.I0(cz_q[0]),
        .I1(pz_q[0]),
        .I2(cz_q[1]),
        .I3(pz_q[1]),
        .I4(pz_q[2]),
        .I5(cz_q[2]),
        .O(\genblk1[0].g_val_reg0_carry_i_29_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0_carry_i_3 
       (.I0(\genblk1[0].g_val_reg2__1 [8]),
        .I1(\genblk1[0].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[0].g_val_reg0_carry_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0_carry_i_30 
       (.I0(\genblk1[0].g_val_reg0_carry_i_25_n_0 ),
        .I1(\genblk1[0].g_val_reg0_carry_i_29_n_0 ),
        .O(\genblk1[0].g_val_reg0_carry_i_30_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[0].g_val_reg0_carry_i_31 
       (.I0(\genblk1[0].g_val_reg0_carry_i_25_n_0 ),
        .I1(cz_q[1]),
        .I2(pz_q[1]),
        .I3(cz_q[0]),
        .I4(pz_q[0]),
        .O(\genblk1[0].g_val_reg0_carry_i_31_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0_carry_i_4 
       (.I0(\genblk1[0].g_val_reg2__1 [7]),
        .I1(\genblk1[0].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[0].g_val_reg0_carry_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0_carry_i_5 
       (.I0(\genblk1[0].g_val_reg2__1 [6]),
        .I1(\genblk1[0].g_val_reg1 [6]),
        .O(\genblk1[0].g_val_reg0_carry_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0_carry_i_6 
       (.I0(\genblk1[0].g_val_reg2__1 [5]),
        .I1(\genblk1[0].g_val_reg1 [5]),
        .O(\genblk1[0].g_val_reg0_carry_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0_carry_i_7 
       (.I0(\genblk1[0].g_val_reg2__1 [4]),
        .I1(\genblk1[0].g_val_reg1 [4]),
        .O(\genblk1[0].g_val_reg0_carry_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0_carry_i_8 
       (.I0(\genblk1[0].g_val_reg2__1 [3]),
        .I1(\genblk1[0].g_val_reg1 [3]),
        .O(\genblk1[0].g_val_reg0_carry_i_8_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].g_val_reg0_carry_i_9 
       (.I0(\genblk1[0].g_val_reg2__1 [2]),
        .I1(\genblk1[0].g_val_reg1 [2]),
        .O(\genblk1[0].g_val_reg0_carry_i_9_n_0 ));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[0].g_val_reg0_inferred__0/i__carry 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[0].g_val_reg0_inferred__0/i__carry_n_0 ,\NLW_genblk1[0].g_val_reg0_inferred__0/i__carry_CO_UNCONNECTED [6:0]}),
        .DI(cg_q[8:1]),
        .O(\genblk1[0].g_val_reg0 [8:1]),
        .S({i__carry_i_1__0_n_0,i__carry_i_2_n_0,i__carry_i_3_n_0,i__carry_i_4_n_0,i__carry_i_5_n_0,i__carry_i_6_n_0,i__carry_i_7_n_0,i__carry_i_8_n_0}));
  (* ADDER_THRESHOLD = "35" *) 
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[0].g_val_reg0_inferred__0/i__carry__0 
       (.CI(\genblk1[0].g_val_reg0_inferred__0/i__carry_n_0 ),
        .CI_TOP(1'b0),
        .CO(\NLW_genblk1[0].g_val_reg0_inferred__0/i__carry__0_CO_UNCONNECTED [7:0]),
        .DI({\NLW_genblk1[0].g_val_reg0_inferred__0/i__carry__0_DI_UNCONNECTED [7:5],1'b0,cg_q[12:9]}),
        .O({\NLW_genblk1[0].g_val_reg0_inferred__0/i__carry__0_O_UNCONNECTED [7:5],\genblk1[0].g_val_reg0 [13:9]}),
        .S({\NLW_genblk1[0].g_val_reg0_inferred__0/i__carry__0_S_UNCONNECTED [7:5],i__carry__0_i_1_n_0,i__carry__0_i_2_n_0,i__carry__0_i_3_n_0,i__carry__0_i_4_n_0,i__carry__0_i_5_n_0}));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].g_val_reg[10] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].g_val_reg0 [10]),
        .Q(g[9]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].g_val_reg[11] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].g_val_reg0 [11]),
        .Q(g[10]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].g_val_reg[12] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].g_val_reg0 [12]),
        .Q(g[11]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].g_val_reg[13] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].g_val_reg0 [13]),
        .Q(g[12]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].g_val_reg[1] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].g_val_reg0 [1]),
        .Q(g[0]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].g_val_reg[2] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].g_val_reg0 [2]),
        .Q(g[1]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].g_val_reg[3] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].g_val_reg0 [3]),
        .Q(g[2]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].g_val_reg[4] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].g_val_reg0 [4]),
        .Q(g[3]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].g_val_reg[5] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].g_val_reg0 [5]),
        .Q(g[4]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].g_val_reg[6] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].g_val_reg0 [6]),
        .Q(g[5]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].g_val_reg[7] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].g_val_reg0 [7]),
        .Q(g[6]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].g_val_reg[8] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].g_val_reg0 [8]),
        .Q(g[7]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].g_val_reg[9] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].g_val_reg0 [9]),
        .Q(g[8]),
        .R(reset_q));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].h_val_x_reg[11]_i_2 
       (.I0(\genblk1[0].h_val_x_reg[13]_i_1_n_0 ),
        .I1(\genblk1[0].h_val_x_reg[9]_i_2_n_0 ),
        .O(\genblk1[0].h_val_x_reg[11]_i_2_n_0 ));
  LUT3 #(
    .INIT(8'h2B)) 
    \genblk1[0].h_val_x_reg[13]_i_1 
       (.I0(px_q[7]),
        .I1(ex_q[7]),
        .I2(\genblk1[0].h_val_x_reg[13]_i_2_n_0 ),
        .O(\genblk1[0].h_val_x_reg[13]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[0].h_val_x_reg[13]_i_2 
       (.I0(px_q[6]),
        .I1(ex_q[6]),
        .I2(\genblk1[0].h_val_x_reg[13]_i_3_n_0 ),
        .I3(ex_q[5]),
        .I4(px_q[5]),
        .O(\genblk1[0].h_val_x_reg[13]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[0].h_val_x_reg[13]_i_3 
       (.I0(px_q[4]),
        .I1(ex_q[4]),
        .I2(\genblk1[0].h_val_x_reg[9]_i_16_n_0 ),
        .I3(ex_q[3]),
        .I4(px_q[3]),
        .O(\genblk1[0].h_val_x_reg[13]_i_3_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair2" *) 
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].h_val_x_reg[1]_i_1 
       (.I0(px_q[0]),
        .I1(ex_q[0]),
        .O(\genblk1[0].h_val_x_reg[1]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h9969696666969699)) 
    \genblk1[0].h_val_x_reg[9]_i_10 
       (.I0(ex_q[6]),
        .I1(px_q[6]),
        .I2(px_q[5]),
        .I3(ex_q[5]),
        .I4(\genblk1[0].h_val_x_reg[13]_i_3_n_0 ),
        .I5(\genblk1[0].h_val_x_reg[9]_i_5_n_0 ),
        .O(\genblk1[0].h_val_x_reg[9]_i_10_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[0].h_val_x_reg[9]_i_11 
       (.I0(ex_q[5]),
        .I1(px_q[5]),
        .I2(\genblk1[0].h_val_x_reg[13]_i_3_n_0 ),
        .I3(\genblk1[0].h_val_x_reg[9]_i_6_n_0 ),
        .O(\genblk1[0].h_val_x_reg[9]_i_11_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].h_val_x_reg[9]_i_12 
       (.I0(\genblk1[0].h_val_x_reg[9]_i_5_n_0 ),
        .I1(\genblk1[0].h_val_x_reg[9]_i_7_n_0 ),
        .O(\genblk1[0].h_val_x_reg[9]_i_12_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[0].h_val_x_reg[9]_i_13 
       (.I0(\genblk1[0].h_val_x_reg[9]_i_6_n_0 ),
        .I1(ex_q[1]),
        .I2(px_q[1]),
        .I3(ex_q[0]),
        .I4(px_q[0]),
        .O(\genblk1[0].h_val_x_reg[9]_i_13_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[0].h_val_x_reg[9]_i_14 
       (.I0(ex_q[2]),
        .I1(px_q[2]),
        .I2(px_q[1]),
        .I3(ex_q[1]),
        .I4(px_q[0]),
        .I5(ex_q[0]),
        .O(\genblk1[0].h_val_x_reg[9]_i_14_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[0].h_val_x_reg[9]_i_15 
       (.I0(px_q[0]),
        .I1(ex_q[0]),
        .I2(px_q[1]),
        .I3(ex_q[1]),
        .O(\genblk1[0].h_val_x_reg[9]_i_15_n_0 ));
  LUT6 #(
    .INIT(64'hD4DD4444DDDDD4DD)) 
    \genblk1[0].h_val_x_reg[9]_i_16 
       (.I0(px_q[2]),
        .I1(ex_q[2]),
        .I2(ex_q[0]),
        .I3(px_q[0]),
        .I4(ex_q[1]),
        .I5(px_q[1]),
        .O(\genblk1[0].h_val_x_reg[9]_i_16_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[0].h_val_x_reg[9]_i_2 
       (.I0(\genblk1[0].h_val_x_reg[13]_i_2_n_0 ),
        .I1(px_q[7]),
        .I2(ex_q[7]),
        .O(\genblk1[0].h_val_x_reg[9]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[0].h_val_x_reg[9]_i_3 
       (.I0(\genblk1[0].h_val_x_reg[13]_i_3_n_0 ),
        .I1(ex_q[5]),
        .I2(px_q[5]),
        .I3(px_q[6]),
        .I4(ex_q[6]),
        .O(\genblk1[0].h_val_x_reg[9]_i_3_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[0].h_val_x_reg[9]_i_4 
       (.I0(\genblk1[0].h_val_x_reg[13]_i_3_n_0 ),
        .I1(px_q[5]),
        .I2(ex_q[5]),
        .O(\genblk1[0].h_val_x_reg[9]_i_4_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[0].h_val_x_reg[9]_i_5 
       (.I0(\genblk1[0].h_val_x_reg[9]_i_16_n_0 ),
        .I1(ex_q[3]),
        .I2(px_q[3]),
        .I3(px_q[4]),
        .I4(ex_q[4]),
        .O(\genblk1[0].h_val_x_reg[9]_i_5_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[0].h_val_x_reg[9]_i_6 
       (.I0(\genblk1[0].h_val_x_reg[9]_i_16_n_0 ),
        .I1(px_q[3]),
        .I2(ex_q[3]),
        .O(\genblk1[0].h_val_x_reg[9]_i_6_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[0].h_val_x_reg[9]_i_7 
       (.I0(ex_q[0]),
        .I1(px_q[0]),
        .I2(ex_q[1]),
        .I3(px_q[1]),
        .I4(px_q[2]),
        .I5(ex_q[2]),
        .O(\genblk1[0].h_val_x_reg[9]_i_7_n_0 ));
  LUT6 #(
    .INIT(64'h9696699669966969)) 
    \genblk1[0].h_val_x_reg[9]_i_8 
       (.I0(\genblk1[0].h_val_x_reg[13]_i_1_n_0 ),
        .I1(ex_q[6]),
        .I2(px_q[6]),
        .I3(px_q[5]),
        .I4(ex_q[5]),
        .I5(\genblk1[0].h_val_x_reg[13]_i_3_n_0 ),
        .O(\genblk1[0].h_val_x_reg[9]_i_8_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[0].h_val_x_reg[9]_i_9 
       (.I0(\genblk1[0].h_val_x_reg[9]_i_2_n_0 ),
        .I1(ex_q[5]),
        .I2(px_q[5]),
        .I3(\genblk1[0].h_val_x_reg[13]_i_3_n_0 ),
        .O(\genblk1[0].h_val_x_reg[9]_i_9_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_x_reg_reg[10] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_x_reg_reg0 [10]),
        .Q(\genblk1[0].h_val_x_reg_reg_n_0_[10] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_x_reg_reg[11] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_x_reg_reg0 [11]),
        .Q(\genblk1[0].h_val_x_reg_reg_n_0_[11] ),
        .R(reset_q));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[0].h_val_x_reg_reg[11]_i_1 
       (.CI(\genblk1[0].h_val_x_reg_reg[9]_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[0].h_val_x_reg_reg[11]_i_1_CO_UNCONNECTED [7:2],\genblk1[0].h_val_x_reg_reg0 [11],\NLW_genblk1[0].h_val_x_reg_reg[11]_i_1_CO_UNCONNECTED [0]}),
        .DI({\NLW_genblk1[0].h_val_x_reg_reg[11]_i_1_DI_UNCONNECTED [7:2],1'b0,\genblk1[0].h_val_x_reg[13]_i_1_n_0 }),
        .O({\NLW_genblk1[0].h_val_x_reg_reg[11]_i_1_O_UNCONNECTED [7:1],\genblk1[0].h_val_x_reg_reg0 [10]}),
        .S({\NLW_genblk1[0].h_val_x_reg_reg[11]_i_1_S_UNCONNECTED [7:2],1'b1,\genblk1[0].h_val_x_reg[11]_i_2_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_x_reg_reg[13] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_x_reg[13]_i_1_n_0 ),
        .Q(p_5_in),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_x_reg_reg[1] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_x_reg[1]_i_1_n_0 ),
        .Q(\genblk1[0].h_val_x_reg_reg_n_0_[1] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_x_reg_reg[2] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_x_reg_reg0 [2]),
        .Q(\genblk1[0].h_val_x_reg_reg_n_0_[2] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_x_reg_reg[3] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_x_reg_reg0 [3]),
        .Q(\genblk1[0].h_val_x_reg_reg_n_0_[3] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_x_reg_reg[4] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_x_reg_reg0 [4]),
        .Q(\genblk1[0].h_val_x_reg_reg_n_0_[4] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_x_reg_reg[5] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_x_reg_reg0 [5]),
        .Q(\genblk1[0].h_val_x_reg_reg_n_0_[5] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_x_reg_reg[6] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_x_reg_reg0 [6]),
        .Q(\genblk1[0].h_val_x_reg_reg_n_0_[6] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_x_reg_reg[7] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_x_reg_reg0 [7]),
        .Q(\genblk1[0].h_val_x_reg_reg_n_0_[7] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_x_reg_reg[8] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_x_reg_reg0 [8]),
        .Q(\genblk1[0].h_val_x_reg_reg_n_0_[8] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_x_reg_reg[9] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_x_reg_reg0 [9]),
        .Q(\genblk1[0].h_val_x_reg_reg_n_0_[9] ),
        .R(reset_q));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[0].h_val_x_reg_reg[9]_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[0].h_val_x_reg_reg[9]_i_1_n_0 ,\NLW_genblk1[0].h_val_x_reg_reg[9]_i_1_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[0].h_val_x_reg[13]_i_1_n_0 ,\genblk1[0].h_val_x_reg[9]_i_2_n_0 ,\genblk1[0].h_val_x_reg[9]_i_3_n_0 ,\genblk1[0].h_val_x_reg[9]_i_4_n_0 ,\genblk1[0].h_val_x_reg[9]_i_5_n_0 ,\genblk1[0].h_val_x_reg[9]_i_6_n_0 ,\genblk1[0].h_val_x_reg[9]_i_7_n_0 ,1'b0}),
        .O(\genblk1[0].h_val_x_reg_reg0 [9:2]),
        .S({\genblk1[0].h_val_x_reg[9]_i_8_n_0 ,\genblk1[0].h_val_x_reg[9]_i_9_n_0 ,\genblk1[0].h_val_x_reg[9]_i_10_n_0 ,\genblk1[0].h_val_x_reg[9]_i_11_n_0 ,\genblk1[0].h_val_x_reg[9]_i_12_n_0 ,\genblk1[0].h_val_x_reg[9]_i_13_n_0 ,\genblk1[0].h_val_x_reg[9]_i_14_n_0 ,\genblk1[0].h_val_x_reg[9]_i_15_n_0 }));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].h_val_y_reg[11]_i_2 
       (.I0(\genblk1[0].h_val_y_reg[13]_i_1_n_0 ),
        .I1(\genblk1[0].h_val_y_reg[9]_i_2_n_0 ),
        .O(\genblk1[0].h_val_y_reg[11]_i_2_n_0 ));
  LUT3 #(
    .INIT(8'h2B)) 
    \genblk1[0].h_val_y_reg[13]_i_1 
       (.I0(py_q[7]),
        .I1(ey_q[7]),
        .I2(\genblk1[0].h_val_y_reg[13]_i_2_n_0 ),
        .O(\genblk1[0].h_val_y_reg[13]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[0].h_val_y_reg[13]_i_2 
       (.I0(py_q[6]),
        .I1(ey_q[6]),
        .I2(\genblk1[0].h_val_y_reg[13]_i_3_n_0 ),
        .I3(ey_q[5]),
        .I4(py_q[5]),
        .O(\genblk1[0].h_val_y_reg[13]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[0].h_val_y_reg[13]_i_3 
       (.I0(py_q[4]),
        .I1(ey_q[4]),
        .I2(\genblk1[0].h_val_y_reg[9]_i_16_n_0 ),
        .I3(ey_q[3]),
        .I4(py_q[3]),
        .O(\genblk1[0].h_val_y_reg[13]_i_3_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair1" *) 
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].h_val_y_reg[1]_i_1 
       (.I0(py_q[0]),
        .I1(ey_q[0]),
        .O(\genblk1[0].h_val_y_reg[1]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h9969696666969699)) 
    \genblk1[0].h_val_y_reg[9]_i_10 
       (.I0(ey_q[6]),
        .I1(py_q[6]),
        .I2(py_q[5]),
        .I3(ey_q[5]),
        .I4(\genblk1[0].h_val_y_reg[13]_i_3_n_0 ),
        .I5(\genblk1[0].h_val_y_reg[9]_i_5_n_0 ),
        .O(\genblk1[0].h_val_y_reg[9]_i_10_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[0].h_val_y_reg[9]_i_11 
       (.I0(ey_q[5]),
        .I1(py_q[5]),
        .I2(\genblk1[0].h_val_y_reg[13]_i_3_n_0 ),
        .I3(\genblk1[0].h_val_y_reg[9]_i_6_n_0 ),
        .O(\genblk1[0].h_val_y_reg[9]_i_11_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].h_val_y_reg[9]_i_12 
       (.I0(\genblk1[0].h_val_y_reg[9]_i_5_n_0 ),
        .I1(\genblk1[0].h_val_y_reg[9]_i_7_n_0 ),
        .O(\genblk1[0].h_val_y_reg[9]_i_12_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[0].h_val_y_reg[9]_i_13 
       (.I0(\genblk1[0].h_val_y_reg[9]_i_6_n_0 ),
        .I1(ey_q[1]),
        .I2(py_q[1]),
        .I3(ey_q[0]),
        .I4(py_q[0]),
        .O(\genblk1[0].h_val_y_reg[9]_i_13_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[0].h_val_y_reg[9]_i_14 
       (.I0(ey_q[2]),
        .I1(py_q[2]),
        .I2(py_q[1]),
        .I3(ey_q[1]),
        .I4(py_q[0]),
        .I5(ey_q[0]),
        .O(\genblk1[0].h_val_y_reg[9]_i_14_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[0].h_val_y_reg[9]_i_15 
       (.I0(py_q[0]),
        .I1(ey_q[0]),
        .I2(py_q[1]),
        .I3(ey_q[1]),
        .O(\genblk1[0].h_val_y_reg[9]_i_15_n_0 ));
  LUT6 #(
    .INIT(64'hD4DD4444DDDDD4DD)) 
    \genblk1[0].h_val_y_reg[9]_i_16 
       (.I0(py_q[2]),
        .I1(ey_q[2]),
        .I2(ey_q[0]),
        .I3(py_q[0]),
        .I4(ey_q[1]),
        .I5(py_q[1]),
        .O(\genblk1[0].h_val_y_reg[9]_i_16_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[0].h_val_y_reg[9]_i_2 
       (.I0(\genblk1[0].h_val_y_reg[13]_i_2_n_0 ),
        .I1(py_q[7]),
        .I2(ey_q[7]),
        .O(\genblk1[0].h_val_y_reg[9]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[0].h_val_y_reg[9]_i_3 
       (.I0(\genblk1[0].h_val_y_reg[13]_i_3_n_0 ),
        .I1(ey_q[5]),
        .I2(py_q[5]),
        .I3(py_q[6]),
        .I4(ey_q[6]),
        .O(\genblk1[0].h_val_y_reg[9]_i_3_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[0].h_val_y_reg[9]_i_4 
       (.I0(\genblk1[0].h_val_y_reg[13]_i_3_n_0 ),
        .I1(py_q[5]),
        .I2(ey_q[5]),
        .O(\genblk1[0].h_val_y_reg[9]_i_4_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[0].h_val_y_reg[9]_i_5 
       (.I0(\genblk1[0].h_val_y_reg[9]_i_16_n_0 ),
        .I1(ey_q[3]),
        .I2(py_q[3]),
        .I3(py_q[4]),
        .I4(ey_q[4]),
        .O(\genblk1[0].h_val_y_reg[9]_i_5_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[0].h_val_y_reg[9]_i_6 
       (.I0(\genblk1[0].h_val_y_reg[9]_i_16_n_0 ),
        .I1(py_q[3]),
        .I2(ey_q[3]),
        .O(\genblk1[0].h_val_y_reg[9]_i_6_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[0].h_val_y_reg[9]_i_7 
       (.I0(ey_q[0]),
        .I1(py_q[0]),
        .I2(ey_q[1]),
        .I3(py_q[1]),
        .I4(py_q[2]),
        .I5(ey_q[2]),
        .O(\genblk1[0].h_val_y_reg[9]_i_7_n_0 ));
  LUT6 #(
    .INIT(64'h9696699669966969)) 
    \genblk1[0].h_val_y_reg[9]_i_8 
       (.I0(\genblk1[0].h_val_y_reg[13]_i_1_n_0 ),
        .I1(ey_q[6]),
        .I2(py_q[6]),
        .I3(py_q[5]),
        .I4(ey_q[5]),
        .I5(\genblk1[0].h_val_y_reg[13]_i_3_n_0 ),
        .O(\genblk1[0].h_val_y_reg[9]_i_8_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[0].h_val_y_reg[9]_i_9 
       (.I0(\genblk1[0].h_val_y_reg[9]_i_2_n_0 ),
        .I1(ey_q[5]),
        .I2(py_q[5]),
        .I3(\genblk1[0].h_val_y_reg[13]_i_3_n_0 ),
        .O(\genblk1[0].h_val_y_reg[9]_i_9_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_y_reg_reg[10] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_y_reg_reg0 [10]),
        .Q(\genblk1[0].h_val_y_reg_reg_n_0_[10] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_y_reg_reg[11] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_y_reg_reg0 [11]),
        .Q(\genblk1[0].h_val_y_reg_reg_n_0_[11] ),
        .R(reset_q));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[0].h_val_y_reg_reg[11]_i_1 
       (.CI(\genblk1[0].h_val_y_reg_reg[9]_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[0].h_val_y_reg_reg[11]_i_1_CO_UNCONNECTED [7:2],\genblk1[0].h_val_y_reg_reg0 [11],\NLW_genblk1[0].h_val_y_reg_reg[11]_i_1_CO_UNCONNECTED [0]}),
        .DI({\NLW_genblk1[0].h_val_y_reg_reg[11]_i_1_DI_UNCONNECTED [7:2],1'b0,\genblk1[0].h_val_y_reg[13]_i_1_n_0 }),
        .O({\NLW_genblk1[0].h_val_y_reg_reg[11]_i_1_O_UNCONNECTED [7:1],\genblk1[0].h_val_y_reg_reg0 [10]}),
        .S({\NLW_genblk1[0].h_val_y_reg_reg[11]_i_1_S_UNCONNECTED [7:2],1'b1,\genblk1[0].h_val_y_reg[11]_i_2_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_y_reg_reg[13] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_y_reg[13]_i_1_n_0 ),
        .Q(p_3_in),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_y_reg_reg[1] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_y_reg[1]_i_1_n_0 ),
        .Q(\genblk1[0].h_val_y_reg_reg_n_0_[1] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_y_reg_reg[2] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_y_reg_reg0 [2]),
        .Q(\genblk1[0].h_val_y_reg_reg_n_0_[2] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_y_reg_reg[3] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_y_reg_reg0 [3]),
        .Q(\genblk1[0].h_val_y_reg_reg_n_0_[3] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_y_reg_reg[4] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_y_reg_reg0 [4]),
        .Q(\genblk1[0].h_val_y_reg_reg_n_0_[4] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_y_reg_reg[5] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_y_reg_reg0 [5]),
        .Q(\genblk1[0].h_val_y_reg_reg_n_0_[5] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_y_reg_reg[6] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_y_reg_reg0 [6]),
        .Q(\genblk1[0].h_val_y_reg_reg_n_0_[6] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_y_reg_reg[7] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_y_reg_reg0 [7]),
        .Q(\genblk1[0].h_val_y_reg_reg_n_0_[7] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_y_reg_reg[8] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_y_reg_reg0 [8]),
        .Q(\genblk1[0].h_val_y_reg_reg_n_0_[8] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_y_reg_reg[9] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_y_reg_reg0 [9]),
        .Q(\genblk1[0].h_val_y_reg_reg_n_0_[9] ),
        .R(reset_q));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[0].h_val_y_reg_reg[9]_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[0].h_val_y_reg_reg[9]_i_1_n_0 ,\NLW_genblk1[0].h_val_y_reg_reg[9]_i_1_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[0].h_val_y_reg[13]_i_1_n_0 ,\genblk1[0].h_val_y_reg[9]_i_2_n_0 ,\genblk1[0].h_val_y_reg[9]_i_3_n_0 ,\genblk1[0].h_val_y_reg[9]_i_4_n_0 ,\genblk1[0].h_val_y_reg[9]_i_5_n_0 ,\genblk1[0].h_val_y_reg[9]_i_6_n_0 ,\genblk1[0].h_val_y_reg[9]_i_7_n_0 ,1'b0}),
        .O(\genblk1[0].h_val_y_reg_reg0 [9:2]),
        .S({\genblk1[0].h_val_y_reg[9]_i_8_n_0 ,\genblk1[0].h_val_y_reg[9]_i_9_n_0 ,\genblk1[0].h_val_y_reg[9]_i_10_n_0 ,\genblk1[0].h_val_y_reg[9]_i_11_n_0 ,\genblk1[0].h_val_y_reg[9]_i_12_n_0 ,\genblk1[0].h_val_y_reg[9]_i_13_n_0 ,\genblk1[0].h_val_y_reg[9]_i_14_n_0 ,\genblk1[0].h_val_y_reg[9]_i_15_n_0 }));
  LUT6 #(
    .INIT(64'h2B22BBBB22222B22)) 
    \genblk1[0].h_val_z_reg[13]_i_1 
       (.I0(pz_q[2]),
        .I1(ez_q[2]),
        .I2(ez_q[0]),
        .I3(pz_q[0]),
        .I4(ez_q[1]),
        .I5(pz_q[1]),
        .O(\genblk1[0].h_val_z_reg[13]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair0" *) 
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].h_val_z_reg[1]_i_1 
       (.I0(pz_q[0]),
        .I1(ez_q[0]),
        .O(\genblk1[0].h_val_z_reg[1]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[0].h_val_z_reg[6]_i_2 
       (.I0(ez_q[0]),
        .I1(pz_q[0]),
        .I2(ez_q[1]),
        .I3(pz_q[1]),
        .I4(pz_q[2]),
        .I5(ez_q[2]),
        .O(\genblk1[0].h_val_z_reg[6]_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[0].h_val_z_reg[6]_i_3 
       (.I0(\genblk1[0].h_val_z_reg[13]_i_1_n_0 ),
        .I1(\genblk1[0].h_val_z_reg[6]_i_2_n_0 ),
        .O(\genblk1[0].h_val_z_reg[6]_i_3_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[0].h_val_z_reg[6]_i_4 
       (.I0(\genblk1[0].h_val_z_reg[13]_i_1_n_0 ),
        .I1(ez_q[1]),
        .I2(pz_q[1]),
        .I3(ez_q[0]),
        .I4(pz_q[0]),
        .O(\genblk1[0].h_val_z_reg[6]_i_4_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[0].h_val_z_reg[6]_i_5 
       (.I0(ez_q[2]),
        .I1(pz_q[2]),
        .I2(pz_q[1]),
        .I3(ez_q[1]),
        .I4(pz_q[0]),
        .I5(ez_q[0]),
        .O(\genblk1[0].h_val_z_reg[6]_i_5_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[0].h_val_z_reg[6]_i_6 
       (.I0(pz_q[0]),
        .I1(ez_q[0]),
        .I2(pz_q[1]),
        .I3(ez_q[1]),
        .O(\genblk1[0].h_val_z_reg[6]_i_6_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_z_reg_reg[13] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_z_reg[13]_i_1_n_0 ),
        .Q(p_4_in),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_z_reg_reg[1] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_z_reg[1]_i_1_n_0 ),
        .Q(\genblk1[0].h_val_z_reg_reg_n_0_[1] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_z_reg_reg[2] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_z_reg_reg0 [2]),
        .Q(\genblk1[0].h_val_z_reg_reg_n_0_[2] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_z_reg_reg[3] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_z_reg_reg0 [3]),
        .Q(\genblk1[0].h_val_z_reg_reg_n_0_[3] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_z_reg_reg[4] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_z_reg_reg0 [4]),
        .Q(\genblk1[0].h_val_z_reg_reg_n_0_[4] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_z_reg_reg[5] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_z_reg_reg0 [5]),
        .Q(\genblk1[0].h_val_z_reg_reg_n_0_[5] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[0].h_val_z_reg_reg[6] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[0].h_val_z_reg_reg0 [6]),
        .Q(\genblk1[0].h_val_z_reg_reg_n_0_[6] ),
        .R(reset_q));
  (* OPT_MODIFIED = "RETARGET PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[0].h_val_z_reg_reg[6]_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[0].h_val_z_reg_reg[6]_i_1_CO_UNCONNECTED [7:5],\genblk1[0].h_val_z_reg_reg0 [6],\NLW_genblk1[0].h_val_z_reg_reg[6]_i_1_CO_UNCONNECTED [3:0]}),
        .DI({\NLW_genblk1[0].h_val_z_reg_reg[6]_i_1_DI_UNCONNECTED [7:5],1'b0,\genblk1[0].h_val_z_reg[13]_i_1_n_0 ,\genblk1[0].h_val_z_reg[13]_i_1_n_0 ,\genblk1[0].h_val_z_reg[6]_i_2_n_0 ,1'b0}),
        .O({\NLW_genblk1[0].h_val_z_reg_reg[6]_i_1_O_UNCONNECTED [7:4],\genblk1[0].h_val_z_reg_reg0 [5:2]}),
        .S({\NLW_genblk1[0].h_val_z_reg_reg[6]_i_1_S_UNCONNECTED [7:5],1'b1,\genblk1[0].h_val_z_reg[6]_i_3_n_0 ,\genblk1[0].h_val_z_reg[6]_i_4_n_0 ,\genblk1[0].h_val_z_reg[6]_i_5_n_0 ,\genblk1[0].h_val_z_reg[6]_i_6_n_0 }));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[1].g_val_reg0__36_carry 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[1].g_val_reg0__36_carry_n_0 ,\NLW_genblk1[1].g_val_reg0__36_carry_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[1].g_val_reg3__6 [8:2],C__0[1]}),
        .O({\genblk1[1].g_val_reg0__36_carry_n_8 ,\genblk1[1].g_val_reg0__36_carry_n_9 ,\genblk1[1].g_val_reg0__36_carry_n_10 ,\genblk1[1].g_val_reg0__36_carry_n_11 ,\genblk1[1].g_val_reg0__36_carry_n_12 ,\genblk1[1].g_val_reg0__36_carry_n_13 ,\genblk1[1].g_val_reg0__36_carry_n_14 ,\genblk1[1].g_val_reg0__36_carry_n_15 }),
        .S({\genblk1[1].g_val_reg0__36_carry_i_2_n_0 ,\genblk1[1].g_val_reg0__36_carry_i_3_n_0 ,\genblk1[1].g_val_reg0__36_carry_i_4_n_0 ,\genblk1[1].g_val_reg0__36_carry_i_5_n_0 ,\genblk1[1].g_val_reg0__36_carry_i_6_n_0 ,\genblk1[1].g_val_reg0__36_carry_i_7_n_0 ,\genblk1[1].g_val_reg0__36_carry_i_8_n_0 ,\genblk1[1].g_val_reg0__36_carry_i_9_n_0 }));
  (* ADDER_THRESHOLD = "35" *) 
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[1].g_val_reg0__36_carry__0 
       (.CI(\genblk1[1].g_val_reg0__36_carry_n_0 ),
        .CI_TOP(1'b0),
        .CO(\NLW_genblk1[1].g_val_reg0__36_carry__0_CO_UNCONNECTED [7:0]),
        .DI({\NLW_genblk1[1].g_val_reg0__36_carry__0_DI_UNCONNECTED [7:5],1'b0,C__0[12],\genblk1[1].g_val_reg3__6 [11:9]}),
        .O({\NLW_genblk1[1].g_val_reg0__36_carry__0_O_UNCONNECTED [7:5],\genblk1[1].g_val_reg0__36_carry__0_n_11 ,\genblk1[1].g_val_reg0__36_carry__0_n_12 ,\genblk1[1].g_val_reg0__36_carry__0_n_13 ,\genblk1[1].g_val_reg0__36_carry__0_n_14 ,\genblk1[1].g_val_reg0__36_carry__0_n_15 }),
        .S({\NLW_genblk1[1].g_val_reg0__36_carry__0_S_UNCONNECTED [7:5],\genblk1[1].g_val_reg0__36_carry__0_i_2_n_0 ,\genblk1[1].g_val_reg0__36_carry__0_i_3_n_0 ,\genblk1[1].g_val_reg0__36_carry__0_i_4_n_0 ,\genblk1[1].g_val_reg0__36_carry__0_i_5_n_0 ,\genblk1[1].g_val_reg0__36_carry__0_i_6_n_0 }));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[1].g_val_reg0__36_carry__0_i_1 
       (.CI(\genblk1[1].g_val_reg0__36_carry_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[1].g_val_reg0__36_carry__0_i_1_CO_UNCONNECTED [7:2],\genblk1[1].g_val_reg3__6 [11],\NLW_genblk1[1].g_val_reg0__36_carry__0_i_1_CO_UNCONNECTED [0]}),
        .DI({\NLW_genblk1[1].g_val_reg0__36_carry__0_i_1_DI_UNCONNECTED [7:2],1'b0,\genblk1[1].g_val_reg0__36_carry_i_10_n_0 }),
        .O({\NLW_genblk1[1].g_val_reg0__36_carry__0_i_1_O_UNCONNECTED [7:1],\genblk1[1].g_val_reg3__6 [10]}),
        .S({\NLW_genblk1[1].g_val_reg0__36_carry__0_i_1_S_UNCONNECTED [7:2],1'b1,\genblk1[1].g_val_reg0__36_carry__0_i_7_n_0 }));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0__36_carry__0_i_2 
       (.I0(\genblk1[1].g_val_reg0__36_carry_i_10_n_0 ),
        .I1(C__0[13]),
        .O(\genblk1[1].g_val_reg0__36_carry__0_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0__36_carry__0_i_3 
       (.I0(\genblk1[1].g_val_reg0__36_carry_i_10_n_0 ),
        .I1(C__0[12]),
        .O(\genblk1[1].g_val_reg0__36_carry__0_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0__36_carry__0_i_4 
       (.I0(\genblk1[1].g_val_reg3__6 [11]),
        .I1(C__0[11]),
        .O(\genblk1[1].g_val_reg0__36_carry__0_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0__36_carry__0_i_5 
       (.I0(\genblk1[1].g_val_reg3__6 [10]),
        .I1(C__0[10]),
        .O(\genblk1[1].g_val_reg0__36_carry__0_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0__36_carry__0_i_6 
       (.I0(\genblk1[1].g_val_reg3__6 [9]),
        .I1(C__0[9]),
        .O(\genblk1[1].g_val_reg0__36_carry__0_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0__36_carry__0_i_7 
       (.I0(\genblk1[1].g_val_reg0__36_carry_i_10_n_0 ),
        .I1(\genblk1[1].g_val_reg0__36_carry_i_11_n_0 ),
        .O(\genblk1[1].g_val_reg0__36_carry__0_i_7_n_0 ));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[1].g_val_reg0__36_carry_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[1].g_val_reg0__36_carry_i_1_n_0 ,\NLW_genblk1[1].g_val_reg0__36_carry_i_1_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[1].g_val_reg0__36_carry_i_10_n_0 ,\genblk1[1].g_val_reg0__36_carry_i_11_n_0 ,\genblk1[1].g_val_reg0__36_carry_i_12_n_0 ,\genblk1[1].g_val_reg0__36_carry_i_13_n_0 ,\genblk1[1].g_val_reg0__36_carry_i_14_n_0 ,\genblk1[1].g_val_reg0__36_carry_i_15_n_0 ,\genblk1[1].g_val_reg0__36_carry_i_16_n_0 ,1'b0}),
        .O(\genblk1[1].g_val_reg3__6 [9:2]),
        .S({\genblk1[1].g_val_reg0__36_carry_i_17_n_0 ,\genblk1[1].g_val_reg0__36_carry_i_18_n_0 ,\genblk1[1].g_val_reg0__36_carry_i_19_n_0 ,\genblk1[1].g_val_reg0__36_carry_i_20_n_0 ,\genblk1[1].g_val_reg0__36_carry_i_21_n_0 ,\genblk1[1].g_val_reg0__36_carry_i_22_n_0 ,\genblk1[1].g_val_reg0__36_carry_i_23_n_0 ,\genblk1[1].g_val_reg0__36_carry_i_24_n_0 }));
  LUT3 #(
    .INIT(8'h2B)) 
    \genblk1[1].g_val_reg0__36_carry_i_10 
       (.I0(px_q[15]),
        .I1(cx_q[7]),
        .I2(\genblk1[1].g_val_reg0__36_carry_i_25_n_0 ),
        .O(\genblk1[1].g_val_reg0__36_carry_i_10_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[1].g_val_reg0__36_carry_i_11 
       (.I0(\genblk1[1].g_val_reg0__36_carry_i_25_n_0 ),
        .I1(px_q[15]),
        .I2(cx_q[7]),
        .O(\genblk1[1].g_val_reg0__36_carry_i_11_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[1].g_val_reg0__36_carry_i_12 
       (.I0(\genblk1[1].g_val_reg0__36_carry_i_26_n_0 ),
        .I1(cx_q[5]),
        .I2(px_q[13]),
        .I3(px_q[14]),
        .I4(cx_q[6]),
        .O(\genblk1[1].g_val_reg0__36_carry_i_12_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[1].g_val_reg0__36_carry_i_13 
       (.I0(\genblk1[1].g_val_reg0__36_carry_i_26_n_0 ),
        .I1(px_q[13]),
        .I2(cx_q[5]),
        .O(\genblk1[1].g_val_reg0__36_carry_i_13_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[1].g_val_reg0__36_carry_i_14 
       (.I0(\genblk1[1].g_val_reg0__36_carry_i_27_n_0 ),
        .I1(cx_q[3]),
        .I2(px_q[11]),
        .I3(px_q[12]),
        .I4(cx_q[4]),
        .O(\genblk1[1].g_val_reg0__36_carry_i_14_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[1].g_val_reg0__36_carry_i_15 
       (.I0(\genblk1[1].g_val_reg0__36_carry_i_27_n_0 ),
        .I1(px_q[11]),
        .I2(cx_q[3]),
        .O(\genblk1[1].g_val_reg0__36_carry_i_15_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[1].g_val_reg0__36_carry_i_16 
       (.I0(cx_q[0]),
        .I1(px_q[8]),
        .I2(cx_q[1]),
        .I3(px_q[9]),
        .I4(px_q[10]),
        .I5(cx_q[2]),
        .O(\genblk1[1].g_val_reg0__36_carry_i_16_n_0 ));
  LUT6 #(
    .INIT(64'h9696699669966969)) 
    \genblk1[1].g_val_reg0__36_carry_i_17 
       (.I0(\genblk1[1].g_val_reg0__36_carry_i_10_n_0 ),
        .I1(cx_q[6]),
        .I2(px_q[14]),
        .I3(px_q[13]),
        .I4(cx_q[5]),
        .I5(\genblk1[1].g_val_reg0__36_carry_i_26_n_0 ),
        .O(\genblk1[1].g_val_reg0__36_carry_i_17_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[1].g_val_reg0__36_carry_i_18 
       (.I0(\genblk1[1].g_val_reg0__36_carry_i_11_n_0 ),
        .I1(cx_q[5]),
        .I2(px_q[13]),
        .I3(\genblk1[1].g_val_reg0__36_carry_i_26_n_0 ),
        .O(\genblk1[1].g_val_reg0__36_carry_i_18_n_0 ));
  LUT6 #(
    .INIT(64'h9969696666969699)) 
    \genblk1[1].g_val_reg0__36_carry_i_19 
       (.I0(cx_q[6]),
        .I1(px_q[14]),
        .I2(px_q[13]),
        .I3(cx_q[5]),
        .I4(\genblk1[1].g_val_reg0__36_carry_i_26_n_0 ),
        .I5(\genblk1[1].g_val_reg0__36_carry_i_14_n_0 ),
        .O(\genblk1[1].g_val_reg0__36_carry_i_19_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0__36_carry_i_2 
       (.I0(\genblk1[1].g_val_reg3__6 [8]),
        .I1(C__0[8]),
        .O(\genblk1[1].g_val_reg0__36_carry_i_2_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[1].g_val_reg0__36_carry_i_20 
       (.I0(cx_q[5]),
        .I1(px_q[13]),
        .I2(\genblk1[1].g_val_reg0__36_carry_i_26_n_0 ),
        .I3(\genblk1[1].g_val_reg0__36_carry_i_15_n_0 ),
        .O(\genblk1[1].g_val_reg0__36_carry_i_20_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0__36_carry_i_21 
       (.I0(\genblk1[1].g_val_reg0__36_carry_i_14_n_0 ),
        .I1(\genblk1[1].g_val_reg0__36_carry_i_16_n_0 ),
        .O(\genblk1[1].g_val_reg0__36_carry_i_21_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[1].g_val_reg0__36_carry_i_22 
       (.I0(\genblk1[1].g_val_reg0__36_carry_i_15_n_0 ),
        .I1(cx_q[1]),
        .I2(px_q[9]),
        .I3(cx_q[0]),
        .I4(px_q[8]),
        .O(\genblk1[1].g_val_reg0__36_carry_i_22_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[1].g_val_reg0__36_carry_i_23 
       (.I0(cx_q[2]),
        .I1(px_q[10]),
        .I2(px_q[9]),
        .I3(cx_q[1]),
        .I4(px_q[8]),
        .I5(cx_q[0]),
        .O(\genblk1[1].g_val_reg0__36_carry_i_23_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[1].g_val_reg0__36_carry_i_24 
       (.I0(px_q[8]),
        .I1(cx_q[0]),
        .I2(px_q[9]),
        .I3(cx_q[1]),
        .O(\genblk1[1].g_val_reg0__36_carry_i_24_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[1].g_val_reg0__36_carry_i_25 
       (.I0(px_q[14]),
        .I1(cx_q[6]),
        .I2(\genblk1[1].g_val_reg0__36_carry_i_26_n_0 ),
        .I3(cx_q[5]),
        .I4(px_q[13]),
        .O(\genblk1[1].g_val_reg0__36_carry_i_25_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[1].g_val_reg0__36_carry_i_26 
       (.I0(px_q[12]),
        .I1(cx_q[4]),
        .I2(\genblk1[1].g_val_reg0__36_carry_i_27_n_0 ),
        .I3(cx_q[3]),
        .I4(px_q[11]),
        .O(\genblk1[1].g_val_reg0__36_carry_i_26_n_0 ));
  LUT6 #(
    .INIT(64'hD4DD4444DDDDD4DD)) 
    \genblk1[1].g_val_reg0__36_carry_i_27 
       (.I0(px_q[10]),
        .I1(cx_q[2]),
        .I2(cx_q[0]),
        .I3(px_q[8]),
        .I4(cx_q[1]),
        .I5(px_q[9]),
        .O(\genblk1[1].g_val_reg0__36_carry_i_27_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0__36_carry_i_3 
       (.I0(\genblk1[1].g_val_reg3__6 [7]),
        .I1(C__0[7]),
        .O(\genblk1[1].g_val_reg0__36_carry_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0__36_carry_i_4 
       (.I0(\genblk1[1].g_val_reg3__6 [6]),
        .I1(C__0[6]),
        .O(\genblk1[1].g_val_reg0__36_carry_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0__36_carry_i_5 
       (.I0(\genblk1[1].g_val_reg3__6 [5]),
        .I1(C__0[5]),
        .O(\genblk1[1].g_val_reg0__36_carry_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0__36_carry_i_6 
       (.I0(\genblk1[1].g_val_reg3__6 [4]),
        .I1(C__0[4]),
        .O(\genblk1[1].g_val_reg0__36_carry_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0__36_carry_i_7 
       (.I0(\genblk1[1].g_val_reg3__6 [3]),
        .I1(C__0[3]),
        .O(\genblk1[1].g_val_reg0__36_carry_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0__36_carry_i_8 
       (.I0(\genblk1[1].g_val_reg3__6 [2]),
        .I1(C__0[2]),
        .O(\genblk1[1].g_val_reg0__36_carry_i_8_n_0 ));
  LUT3 #(
    .INIT(8'h96)) 
    \genblk1[1].g_val_reg0__36_carry_i_9 
       (.I0(px_q[8]),
        .I1(cx_q[0]),
        .I2(C__0[1]),
        .O(\genblk1[1].g_val_reg0__36_carry_i_9_n_0 ));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[1].g_val_reg0_carry 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[1].g_val_reg0_carry_n_0 ,\NLW_genblk1[1].g_val_reg0_carry_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[1].g_val_reg2__1 [8:2],\genblk1[1].g_val_reg0_carry_i_2_n_0 }),
        .O(C__0[8:1]),
        .S({\genblk1[1].g_val_reg0_carry_i_3_n_0 ,\genblk1[1].g_val_reg0_carry_i_4_n_0 ,\genblk1[1].g_val_reg0_carry_i_5_n_0 ,\genblk1[1].g_val_reg0_carry_i_6_n_0 ,\genblk1[1].g_val_reg0_carry_i_7_n_0 ,\genblk1[1].g_val_reg0_carry_i_8_n_0 ,\genblk1[1].g_val_reg0_carry_i_9_n_0 ,\genblk1[1].g_val_reg0_carry_i_10_n_0 }));
  (* ADDER_THRESHOLD = "35" *) 
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[1].g_val_reg0_carry__0 
       (.CI(\genblk1[1].g_val_reg0_carry_n_0 ),
        .CI_TOP(1'b0),
        .CO(\NLW_genblk1[1].g_val_reg0_carry__0_CO_UNCONNECTED [7:0]),
        .DI({\NLW_genblk1[1].g_val_reg0_carry__0_DI_UNCONNECTED [7:5],1'b0,\genblk1[1].g_val_reg0_carry__0_i_1_n_0 ,\genblk1[1].g_val_reg2__1 [11:9]}),
        .O({\NLW_genblk1[1].g_val_reg0_carry__0_O_UNCONNECTED [7:5],C__0[13:9]}),
        .S({\NLW_genblk1[1].g_val_reg0_carry__0_S_UNCONNECTED [7:5],\genblk1[1].g_val_reg0_carry__0_i_3_n_0 ,\genblk1[1].g_val_reg0_carry__0_i_4_n_0 ,\genblk1[1].g_val_reg0_carry__0_i_5_n_0 ,\genblk1[1].g_val_reg0_carry__0_i_6_n_0 ,\genblk1[1].g_val_reg0_carry__0_i_7_n_0 }));
  LUT3 #(
    .INIT(8'h2B)) 
    \genblk1[1].g_val_reg0_carry__0_i_1 
       (.I0(py_q[15]),
        .I1(cy_q[7]),
        .I2(\genblk1[1].g_val_reg0_carry__0_i_8_n_0 ),
        .O(\genblk1[1].g_val_reg0_carry__0_i_1_n_0 ));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[1].g_val_reg0_carry__0_i_2 
       (.CI(\genblk1[1].g_val_reg0_carry_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[1].g_val_reg0_carry__0_i_2_CO_UNCONNECTED [7:2],\genblk1[1].g_val_reg2__1 [11],\NLW_genblk1[1].g_val_reg0_carry__0_i_2_CO_UNCONNECTED [0]}),
        .DI({\NLW_genblk1[1].g_val_reg0_carry__0_i_2_DI_UNCONNECTED [7:2],1'b0,\genblk1[1].g_val_reg0_carry__0_i_1_n_0 }),
        .O({\NLW_genblk1[1].g_val_reg0_carry__0_i_2_O_UNCONNECTED [7:1],\genblk1[1].g_val_reg2__1 [10]}),
        .S({\NLW_genblk1[1].g_val_reg0_carry__0_i_2_S_UNCONNECTED [7:2],1'b1,\genblk1[1].g_val_reg0_carry__0_i_9_n_0 }));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0_carry__0_i_3 
       (.I0(\genblk1[1].g_val_reg0_carry__0_i_1_n_0 ),
        .I1(\genblk1[1].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[1].g_val_reg0_carry__0_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0_carry__0_i_4 
       (.I0(\genblk1[1].g_val_reg0_carry__0_i_1_n_0 ),
        .I1(\genblk1[1].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[1].g_val_reg0_carry__0_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0_carry__0_i_5 
       (.I0(\genblk1[1].g_val_reg2__1 [11]),
        .I1(\genblk1[1].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[1].g_val_reg0_carry__0_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0_carry__0_i_6 
       (.I0(\genblk1[1].g_val_reg2__1 [10]),
        .I1(\genblk1[1].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[1].g_val_reg0_carry__0_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0_carry__0_i_7 
       (.I0(\genblk1[1].g_val_reg2__1 [9]),
        .I1(\genblk1[1].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[1].g_val_reg0_carry__0_i_7_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[1].g_val_reg0_carry__0_i_8 
       (.I0(py_q[14]),
        .I1(cy_q[6]),
        .I2(\genblk1[1].g_val_reg0_carry_i_27_n_0 ),
        .I3(cy_q[5]),
        .I4(py_q[13]),
        .O(\genblk1[1].g_val_reg0_carry__0_i_8_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0_carry__0_i_9 
       (.I0(\genblk1[1].g_val_reg0_carry__0_i_1_n_0 ),
        .I1(\genblk1[1].g_val_reg0_carry_i_11_n_0 ),
        .O(\genblk1[1].g_val_reg0_carry__0_i_9_n_0 ));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[1].g_val_reg0_carry_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[1].g_val_reg0_carry_i_1_n_0 ,\NLW_genblk1[1].g_val_reg0_carry_i_1_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[1].g_val_reg0_carry__0_i_1_n_0 ,\genblk1[1].g_val_reg0_carry_i_11_n_0 ,\genblk1[1].g_val_reg0_carry_i_12_n_0 ,\genblk1[1].g_val_reg0_carry_i_13_n_0 ,\genblk1[1].g_val_reg0_carry_i_14_n_0 ,\genblk1[1].g_val_reg0_carry_i_15_n_0 ,\genblk1[1].g_val_reg0_carry_i_16_n_0 ,1'b0}),
        .O(\genblk1[1].g_val_reg2__1 [9:2]),
        .S({\genblk1[1].g_val_reg0_carry_i_17_n_0 ,\genblk1[1].g_val_reg0_carry_i_18_n_0 ,\genblk1[1].g_val_reg0_carry_i_19_n_0 ,\genblk1[1].g_val_reg0_carry_i_20_n_0 ,\genblk1[1].g_val_reg0_carry_i_21_n_0 ,\genblk1[1].g_val_reg0_carry_i_22_n_0 ,\genblk1[1].g_val_reg0_carry_i_23_n_0 ,\genblk1[1].g_val_reg0_carry_i_24_n_0 }));
  LUT4 #(
    .INIT(16'h6996)) 
    \genblk1[1].g_val_reg0_carry_i_10 
       (.I0(py_q[8]),
        .I1(cy_q[0]),
        .I2(pz_q[3]),
        .I3(cz_q[0]),
        .O(\genblk1[1].g_val_reg0_carry_i_10_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[1].g_val_reg0_carry_i_11 
       (.I0(\genblk1[1].g_val_reg0_carry__0_i_8_n_0 ),
        .I1(py_q[15]),
        .I2(cy_q[7]),
        .O(\genblk1[1].g_val_reg0_carry_i_11_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[1].g_val_reg0_carry_i_12 
       (.I0(\genblk1[1].g_val_reg0_carry_i_27_n_0 ),
        .I1(cy_q[5]),
        .I2(py_q[13]),
        .I3(py_q[14]),
        .I4(cy_q[6]),
        .O(\genblk1[1].g_val_reg0_carry_i_12_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[1].g_val_reg0_carry_i_13 
       (.I0(\genblk1[1].g_val_reg0_carry_i_27_n_0 ),
        .I1(py_q[13]),
        .I2(cy_q[5]),
        .O(\genblk1[1].g_val_reg0_carry_i_13_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[1].g_val_reg0_carry_i_14 
       (.I0(\genblk1[1].g_val_reg0_carry_i_28_n_0 ),
        .I1(cy_q[3]),
        .I2(py_q[11]),
        .I3(py_q[12]),
        .I4(cy_q[4]),
        .O(\genblk1[1].g_val_reg0_carry_i_14_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[1].g_val_reg0_carry_i_15 
       (.I0(\genblk1[1].g_val_reg0_carry_i_28_n_0 ),
        .I1(py_q[11]),
        .I2(cy_q[3]),
        .O(\genblk1[1].g_val_reg0_carry_i_15_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[1].g_val_reg0_carry_i_16 
       (.I0(cy_q[0]),
        .I1(py_q[8]),
        .I2(cy_q[1]),
        .I3(py_q[9]),
        .I4(py_q[10]),
        .I5(cy_q[2]),
        .O(\genblk1[1].g_val_reg0_carry_i_16_n_0 ));
  LUT6 #(
    .INIT(64'h9696699669966969)) 
    \genblk1[1].g_val_reg0_carry_i_17 
       (.I0(\genblk1[1].g_val_reg0_carry__0_i_1_n_0 ),
        .I1(cy_q[6]),
        .I2(py_q[14]),
        .I3(py_q[13]),
        .I4(cy_q[5]),
        .I5(\genblk1[1].g_val_reg0_carry_i_27_n_0 ),
        .O(\genblk1[1].g_val_reg0_carry_i_17_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[1].g_val_reg0_carry_i_18 
       (.I0(\genblk1[1].g_val_reg0_carry_i_11_n_0 ),
        .I1(cy_q[5]),
        .I2(py_q[13]),
        .I3(\genblk1[1].g_val_reg0_carry_i_27_n_0 ),
        .O(\genblk1[1].g_val_reg0_carry_i_18_n_0 ));
  LUT6 #(
    .INIT(64'h9969696666969699)) 
    \genblk1[1].g_val_reg0_carry_i_19 
       (.I0(cy_q[6]),
        .I1(py_q[14]),
        .I2(py_q[13]),
        .I3(cy_q[5]),
        .I4(\genblk1[1].g_val_reg0_carry_i_27_n_0 ),
        .I5(\genblk1[1].g_val_reg0_carry_i_14_n_0 ),
        .O(\genblk1[1].g_val_reg0_carry_i_19_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0_carry_i_2 
       (.I0(py_q[8]),
        .I1(cy_q[0]),
        .O(\genblk1[1].g_val_reg0_carry_i_2_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[1].g_val_reg0_carry_i_20 
       (.I0(cy_q[5]),
        .I1(py_q[13]),
        .I2(\genblk1[1].g_val_reg0_carry_i_27_n_0 ),
        .I3(\genblk1[1].g_val_reg0_carry_i_15_n_0 ),
        .O(\genblk1[1].g_val_reg0_carry_i_20_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0_carry_i_21 
       (.I0(\genblk1[1].g_val_reg0_carry_i_14_n_0 ),
        .I1(\genblk1[1].g_val_reg0_carry_i_16_n_0 ),
        .O(\genblk1[1].g_val_reg0_carry_i_21_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[1].g_val_reg0_carry_i_22 
       (.I0(\genblk1[1].g_val_reg0_carry_i_15_n_0 ),
        .I1(cy_q[1]),
        .I2(py_q[9]),
        .I3(cy_q[0]),
        .I4(py_q[8]),
        .O(\genblk1[1].g_val_reg0_carry_i_22_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[1].g_val_reg0_carry_i_23 
       (.I0(cy_q[2]),
        .I1(py_q[10]),
        .I2(py_q[9]),
        .I3(cy_q[1]),
        .I4(py_q[8]),
        .I5(cy_q[0]),
        .O(\genblk1[1].g_val_reg0_carry_i_23_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[1].g_val_reg0_carry_i_24 
       (.I0(py_q[8]),
        .I1(cy_q[0]),
        .I2(py_q[9]),
        .I3(cy_q[1]),
        .O(\genblk1[1].g_val_reg0_carry_i_24_n_0 ));
  LUT6 #(
    .INIT(64'h2B22BBBB22222B22)) 
    \genblk1[1].g_val_reg0_carry_i_25 
       (.I0(pz_q[5]),
        .I1(cz_q[2]),
        .I2(cz_q[0]),
        .I3(pz_q[3]),
        .I4(cz_q[1]),
        .I5(pz_q[4]),
        .O(\genblk1[1].g_val_reg0_carry_i_25_n_0 ));
  (* OPT_MODIFIED = "RETARGET PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[1].g_val_reg0_carry_i_26 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[1].g_val_reg0_carry_i_26_CO_UNCONNECTED [7:5],\genblk1[1].g_val_reg1 [6],\NLW_genblk1[1].g_val_reg0_carry_i_26_CO_UNCONNECTED [3:0]}),
        .DI({\NLW_genblk1[1].g_val_reg0_carry_i_26_DI_UNCONNECTED [7:5],1'b0,\genblk1[1].g_val_reg0_carry_i_25_n_0 ,\genblk1[1].g_val_reg0_carry_i_25_n_0 ,\genblk1[1].g_val_reg0_carry_i_29_n_0 ,1'b0}),
        .O({\NLW_genblk1[1].g_val_reg0_carry_i_26_O_UNCONNECTED [7:4],\genblk1[1].g_val_reg1 [5:2]}),
        .S({\NLW_genblk1[1].g_val_reg0_carry_i_26_S_UNCONNECTED [7:5],1'b1,\genblk1[1].g_val_reg0_carry_i_30_n_0 ,\genblk1[1].g_val_reg0_carry_i_31_n_0 ,\genblk1[1].g_val_reg0_carry_i_9_0 }));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[1].g_val_reg0_carry_i_27 
       (.I0(py_q[12]),
        .I1(cy_q[4]),
        .I2(\genblk1[1].g_val_reg0_carry_i_28_n_0 ),
        .I3(cy_q[3]),
        .I4(py_q[11]),
        .O(\genblk1[1].g_val_reg0_carry_i_27_n_0 ));
  LUT6 #(
    .INIT(64'hD4DD4444DDDDD4DD)) 
    \genblk1[1].g_val_reg0_carry_i_28 
       (.I0(py_q[10]),
        .I1(cy_q[2]),
        .I2(cy_q[0]),
        .I3(py_q[8]),
        .I4(cy_q[1]),
        .I5(py_q[9]),
        .O(\genblk1[1].g_val_reg0_carry_i_28_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[1].g_val_reg0_carry_i_29 
       (.I0(cz_q[0]),
        .I1(pz_q[3]),
        .I2(cz_q[1]),
        .I3(pz_q[4]),
        .I4(pz_q[5]),
        .I5(cz_q[2]),
        .O(\genblk1[1].g_val_reg0_carry_i_29_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0_carry_i_3 
       (.I0(\genblk1[1].g_val_reg2__1 [8]),
        .I1(\genblk1[1].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[1].g_val_reg0_carry_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0_carry_i_30 
       (.I0(\genblk1[1].g_val_reg0_carry_i_25_n_0 ),
        .I1(\genblk1[1].g_val_reg0_carry_i_29_n_0 ),
        .O(\genblk1[1].g_val_reg0_carry_i_30_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[1].g_val_reg0_carry_i_31 
       (.I0(\genblk1[1].g_val_reg0_carry_i_25_n_0 ),
        .I1(cz_q[1]),
        .I2(pz_q[4]),
        .I3(cz_q[0]),
        .I4(pz_q[3]),
        .O(\genblk1[1].g_val_reg0_carry_i_31_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0_carry_i_4 
       (.I0(\genblk1[1].g_val_reg2__1 [7]),
        .I1(\genblk1[1].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[1].g_val_reg0_carry_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0_carry_i_5 
       (.I0(\genblk1[1].g_val_reg2__1 [6]),
        .I1(\genblk1[1].g_val_reg1 [6]),
        .O(\genblk1[1].g_val_reg0_carry_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0_carry_i_6 
       (.I0(\genblk1[1].g_val_reg2__1 [5]),
        .I1(\genblk1[1].g_val_reg1 [5]),
        .O(\genblk1[1].g_val_reg0_carry_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0_carry_i_7 
       (.I0(\genblk1[1].g_val_reg2__1 [4]),
        .I1(\genblk1[1].g_val_reg1 [4]),
        .O(\genblk1[1].g_val_reg0_carry_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0_carry_i_8 
       (.I0(\genblk1[1].g_val_reg2__1 [3]),
        .I1(\genblk1[1].g_val_reg1 [3]),
        .O(\genblk1[1].g_val_reg0_carry_i_8_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].g_val_reg0_carry_i_9 
       (.I0(\genblk1[1].g_val_reg2__1 [2]),
        .I1(\genblk1[1].g_val_reg1 [2]),
        .O(\genblk1[1].g_val_reg0_carry_i_9_n_0 ));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[1].g_val_reg0_inferred__0/i__carry 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[1].g_val_reg0_inferred__0/i__carry_n_0 ,\NLW_genblk1[1].g_val_reg0_inferred__0/i__carry_CO_UNCONNECTED [6:0]}),
        .DI(cg_q[8:1]),
        .O(\genblk1[1].g_val_reg0 [8:1]),
        .S({i__carry_i_1__1_n_0,i__carry_i_2__0_n_0,i__carry_i_3__0_n_0,i__carry_i_4__0_n_0,i__carry_i_5__0_n_0,i__carry_i_6__0_n_0,i__carry_i_7__0_n_0,i__carry_i_8__0_n_0}));
  (* ADDER_THRESHOLD = "35" *) 
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[1].g_val_reg0_inferred__0/i__carry__0 
       (.CI(\genblk1[1].g_val_reg0_inferred__0/i__carry_n_0 ),
        .CI_TOP(1'b0),
        .CO(\NLW_genblk1[1].g_val_reg0_inferred__0/i__carry__0_CO_UNCONNECTED [7:0]),
        .DI({\NLW_genblk1[1].g_val_reg0_inferred__0/i__carry__0_DI_UNCONNECTED [7:5],1'b0,cg_q[12:9]}),
        .O({\NLW_genblk1[1].g_val_reg0_inferred__0/i__carry__0_O_UNCONNECTED [7:5],\genblk1[1].g_val_reg0 [13:9]}),
        .S({\NLW_genblk1[1].g_val_reg0_inferred__0/i__carry__0_S_UNCONNECTED [7:5],i__carry__0_i_1__0_n_0,i__carry__0_i_2__0_n_0,i__carry__0_i_3__0_n_0,i__carry__0_i_4__0_n_0,i__carry__0_i_5__0_n_0}));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].g_val_reg[15] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].g_val_reg0 [1]),
        .Q(g[13]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].g_val_reg[16] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].g_val_reg0 [2]),
        .Q(g[14]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].g_val_reg[17] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].g_val_reg0 [3]),
        .Q(g[15]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].g_val_reg[18] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].g_val_reg0 [4]),
        .Q(g[16]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].g_val_reg[19] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].g_val_reg0 [5]),
        .Q(g[17]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].g_val_reg[20] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].g_val_reg0 [6]),
        .Q(g[18]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].g_val_reg[21] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].g_val_reg0 [7]),
        .Q(g[19]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].g_val_reg[22] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].g_val_reg0 [8]),
        .Q(g[20]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].g_val_reg[23] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].g_val_reg0 [9]),
        .Q(g[21]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].g_val_reg[24] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].g_val_reg0 [10]),
        .Q(g[22]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].g_val_reg[25] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].g_val_reg0 [11]),
        .Q(g[23]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].g_val_reg[26] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].g_val_reg0 [12]),
        .Q(g[24]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].g_val_reg[27] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].g_val_reg0 [13]),
        .Q(g[25]),
        .R(reset_q));
  (* SOFT_HLUTNM = "soft_lutpair2" *) 
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].h_val_x_reg[15]_i_1 
       (.I0(px_q[8]),
        .I1(ex_q[0]),
        .O(\genblk1[1].h_val_x_reg[15]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h9969696666969699)) 
    \genblk1[1].h_val_x_reg[23]_i_10 
       (.I0(ex_q[6]),
        .I1(px_q[14]),
        .I2(px_q[13]),
        .I3(ex_q[5]),
        .I4(\genblk1[1].h_val_x_reg[27]_i_3_n_0 ),
        .I5(\genblk1[1].h_val_x_reg[23]_i_5_n_0 ),
        .O(\genblk1[1].h_val_x_reg[23]_i_10_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[1].h_val_x_reg[23]_i_11 
       (.I0(ex_q[5]),
        .I1(px_q[13]),
        .I2(\genblk1[1].h_val_x_reg[27]_i_3_n_0 ),
        .I3(\genblk1[1].h_val_x_reg[23]_i_6_n_0 ),
        .O(\genblk1[1].h_val_x_reg[23]_i_11_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].h_val_x_reg[23]_i_12 
       (.I0(\genblk1[1].h_val_x_reg[23]_i_5_n_0 ),
        .I1(\genblk1[1].h_val_x_reg[23]_i_7_n_0 ),
        .O(\genblk1[1].h_val_x_reg[23]_i_12_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[1].h_val_x_reg[23]_i_13 
       (.I0(\genblk1[1].h_val_x_reg[23]_i_6_n_0 ),
        .I1(ex_q[1]),
        .I2(px_q[9]),
        .I3(ex_q[0]),
        .I4(px_q[8]),
        .O(\genblk1[1].h_val_x_reg[23]_i_13_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[1].h_val_x_reg[23]_i_14 
       (.I0(ex_q[2]),
        .I1(px_q[10]),
        .I2(px_q[9]),
        .I3(ex_q[1]),
        .I4(px_q[8]),
        .I5(ex_q[0]),
        .O(\genblk1[1].h_val_x_reg[23]_i_14_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[1].h_val_x_reg[23]_i_15 
       (.I0(px_q[8]),
        .I1(ex_q[0]),
        .I2(px_q[9]),
        .I3(ex_q[1]),
        .O(\genblk1[1].h_val_x_reg[23]_i_15_n_0 ));
  LUT6 #(
    .INIT(64'hD4DD4444DDDDD4DD)) 
    \genblk1[1].h_val_x_reg[23]_i_16 
       (.I0(px_q[10]),
        .I1(ex_q[2]),
        .I2(ex_q[0]),
        .I3(px_q[8]),
        .I4(ex_q[1]),
        .I5(px_q[9]),
        .O(\genblk1[1].h_val_x_reg[23]_i_16_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[1].h_val_x_reg[23]_i_2 
       (.I0(\genblk1[1].h_val_x_reg[27]_i_2_n_0 ),
        .I1(px_q[15]),
        .I2(ex_q[7]),
        .O(\genblk1[1].h_val_x_reg[23]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[1].h_val_x_reg[23]_i_3 
       (.I0(\genblk1[1].h_val_x_reg[27]_i_3_n_0 ),
        .I1(ex_q[5]),
        .I2(px_q[13]),
        .I3(px_q[14]),
        .I4(ex_q[6]),
        .O(\genblk1[1].h_val_x_reg[23]_i_3_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[1].h_val_x_reg[23]_i_4 
       (.I0(\genblk1[1].h_val_x_reg[27]_i_3_n_0 ),
        .I1(px_q[13]),
        .I2(ex_q[5]),
        .O(\genblk1[1].h_val_x_reg[23]_i_4_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[1].h_val_x_reg[23]_i_5 
       (.I0(\genblk1[1].h_val_x_reg[23]_i_16_n_0 ),
        .I1(ex_q[3]),
        .I2(px_q[11]),
        .I3(px_q[12]),
        .I4(ex_q[4]),
        .O(\genblk1[1].h_val_x_reg[23]_i_5_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[1].h_val_x_reg[23]_i_6 
       (.I0(\genblk1[1].h_val_x_reg[23]_i_16_n_0 ),
        .I1(px_q[11]),
        .I2(ex_q[3]),
        .O(\genblk1[1].h_val_x_reg[23]_i_6_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[1].h_val_x_reg[23]_i_7 
       (.I0(ex_q[0]),
        .I1(px_q[8]),
        .I2(ex_q[1]),
        .I3(px_q[9]),
        .I4(px_q[10]),
        .I5(ex_q[2]),
        .O(\genblk1[1].h_val_x_reg[23]_i_7_n_0 ));
  LUT6 #(
    .INIT(64'h9696699669966969)) 
    \genblk1[1].h_val_x_reg[23]_i_8 
       (.I0(\genblk1[1].h_val_x_reg[27]_i_1_n_0 ),
        .I1(ex_q[6]),
        .I2(px_q[14]),
        .I3(px_q[13]),
        .I4(ex_q[5]),
        .I5(\genblk1[1].h_val_x_reg[27]_i_3_n_0 ),
        .O(\genblk1[1].h_val_x_reg[23]_i_8_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[1].h_val_x_reg[23]_i_9 
       (.I0(\genblk1[1].h_val_x_reg[23]_i_2_n_0 ),
        .I1(ex_q[5]),
        .I2(px_q[13]),
        .I3(\genblk1[1].h_val_x_reg[27]_i_3_n_0 ),
        .O(\genblk1[1].h_val_x_reg[23]_i_9_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].h_val_x_reg[25]_i_2 
       (.I0(\genblk1[1].h_val_x_reg[27]_i_1_n_0 ),
        .I1(\genblk1[1].h_val_x_reg[23]_i_2_n_0 ),
        .O(\genblk1[1].h_val_x_reg[25]_i_2_n_0 ));
  LUT3 #(
    .INIT(8'h2B)) 
    \genblk1[1].h_val_x_reg[27]_i_1 
       (.I0(px_q[15]),
        .I1(ex_q[7]),
        .I2(\genblk1[1].h_val_x_reg[27]_i_2_n_0 ),
        .O(\genblk1[1].h_val_x_reg[27]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[1].h_val_x_reg[27]_i_2 
       (.I0(px_q[14]),
        .I1(ex_q[6]),
        .I2(\genblk1[1].h_val_x_reg[27]_i_3_n_0 ),
        .I3(ex_q[5]),
        .I4(px_q[13]),
        .O(\genblk1[1].h_val_x_reg[27]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[1].h_val_x_reg[27]_i_3 
       (.I0(px_q[12]),
        .I1(ex_q[4]),
        .I2(\genblk1[1].h_val_x_reg[23]_i_16_n_0 ),
        .I3(ex_q[3]),
        .I4(px_q[11]),
        .O(\genblk1[1].h_val_x_reg[27]_i_3_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_x_reg_reg[15] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_x_reg[15]_i_1_n_0 ),
        .Q(\genblk1[1].h_val_x_reg_reg_n_0_[15] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_x_reg_reg[16] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_x_reg_reg0 [2]),
        .Q(\genblk1[1].h_val_x_reg_reg_n_0_[16] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_x_reg_reg[17] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_x_reg_reg0 [3]),
        .Q(\genblk1[1].h_val_x_reg_reg_n_0_[17] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_x_reg_reg[18] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_x_reg_reg0 [4]),
        .Q(\genblk1[1].h_val_x_reg_reg_n_0_[18] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_x_reg_reg[19] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_x_reg_reg0 [5]),
        .Q(\genblk1[1].h_val_x_reg_reg_n_0_[19] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_x_reg_reg[20] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_x_reg_reg0 [6]),
        .Q(\genblk1[1].h_val_x_reg_reg_n_0_[20] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_x_reg_reg[21] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_x_reg_reg0 [7]),
        .Q(\genblk1[1].h_val_x_reg_reg_n_0_[21] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_x_reg_reg[22] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_x_reg_reg0 [8]),
        .Q(\genblk1[1].h_val_x_reg_reg_n_0_[22] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_x_reg_reg[23] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_x_reg_reg0 [9]),
        .Q(\genblk1[1].h_val_x_reg_reg_n_0_[23] ),
        .R(reset_q));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[1].h_val_x_reg_reg[23]_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[1].h_val_x_reg_reg[23]_i_1_n_0 ,\NLW_genblk1[1].h_val_x_reg_reg[23]_i_1_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[1].h_val_x_reg[27]_i_1_n_0 ,\genblk1[1].h_val_x_reg[23]_i_2_n_0 ,\genblk1[1].h_val_x_reg[23]_i_3_n_0 ,\genblk1[1].h_val_x_reg[23]_i_4_n_0 ,\genblk1[1].h_val_x_reg[23]_i_5_n_0 ,\genblk1[1].h_val_x_reg[23]_i_6_n_0 ,\genblk1[1].h_val_x_reg[23]_i_7_n_0 ,1'b0}),
        .O(\genblk1[1].h_val_x_reg_reg0 [9:2]),
        .S({\genblk1[1].h_val_x_reg[23]_i_8_n_0 ,\genblk1[1].h_val_x_reg[23]_i_9_n_0 ,\genblk1[1].h_val_x_reg[23]_i_10_n_0 ,\genblk1[1].h_val_x_reg[23]_i_11_n_0 ,\genblk1[1].h_val_x_reg[23]_i_12_n_0 ,\genblk1[1].h_val_x_reg[23]_i_13_n_0 ,\genblk1[1].h_val_x_reg[23]_i_14_n_0 ,\genblk1[1].h_val_x_reg[23]_i_15_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_x_reg_reg[24] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_x_reg_reg0 [10]),
        .Q(\genblk1[1].h_val_x_reg_reg_n_0_[24] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_x_reg_reg[25] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_x_reg_reg0 [11]),
        .Q(\genblk1[1].h_val_x_reg_reg_n_0_[25] ),
        .R(reset_q));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[1].h_val_x_reg_reg[25]_i_1 
       (.CI(\genblk1[1].h_val_x_reg_reg[23]_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[1].h_val_x_reg_reg[25]_i_1_CO_UNCONNECTED [7:2],\genblk1[1].h_val_x_reg_reg0 [11],\NLW_genblk1[1].h_val_x_reg_reg[25]_i_1_CO_UNCONNECTED [0]}),
        .DI({\NLW_genblk1[1].h_val_x_reg_reg[25]_i_1_DI_UNCONNECTED [7:2],1'b0,\genblk1[1].h_val_x_reg[27]_i_1_n_0 }),
        .O({\NLW_genblk1[1].h_val_x_reg_reg[25]_i_1_O_UNCONNECTED [7:1],\genblk1[1].h_val_x_reg_reg0 [10]}),
        .S({\NLW_genblk1[1].h_val_x_reg_reg[25]_i_1_S_UNCONNECTED [7:2],1'b1,\genblk1[1].h_val_x_reg[25]_i_2_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_x_reg_reg[27] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_x_reg[27]_i_1_n_0 ),
        .Q(p_0_in5_in),
        .R(reset_q));
  (* SOFT_HLUTNM = "soft_lutpair1" *) 
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].h_val_y_reg[15]_i_1 
       (.I0(py_q[8]),
        .I1(ey_q[0]),
        .O(\genblk1[1].h_val_y_reg[15]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h9969696666969699)) 
    \genblk1[1].h_val_y_reg[23]_i_10 
       (.I0(ey_q[6]),
        .I1(py_q[14]),
        .I2(py_q[13]),
        .I3(ey_q[5]),
        .I4(\genblk1[1].h_val_y_reg[27]_i_3_n_0 ),
        .I5(\genblk1[1].h_val_y_reg[23]_i_5_n_0 ),
        .O(\genblk1[1].h_val_y_reg[23]_i_10_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[1].h_val_y_reg[23]_i_11 
       (.I0(ey_q[5]),
        .I1(py_q[13]),
        .I2(\genblk1[1].h_val_y_reg[27]_i_3_n_0 ),
        .I3(\genblk1[1].h_val_y_reg[23]_i_6_n_0 ),
        .O(\genblk1[1].h_val_y_reg[23]_i_11_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].h_val_y_reg[23]_i_12 
       (.I0(\genblk1[1].h_val_y_reg[23]_i_5_n_0 ),
        .I1(\genblk1[1].h_val_y_reg[23]_i_7_n_0 ),
        .O(\genblk1[1].h_val_y_reg[23]_i_12_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[1].h_val_y_reg[23]_i_13 
       (.I0(\genblk1[1].h_val_y_reg[23]_i_6_n_0 ),
        .I1(ey_q[1]),
        .I2(py_q[9]),
        .I3(ey_q[0]),
        .I4(py_q[8]),
        .O(\genblk1[1].h_val_y_reg[23]_i_13_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[1].h_val_y_reg[23]_i_14 
       (.I0(ey_q[2]),
        .I1(py_q[10]),
        .I2(py_q[9]),
        .I3(ey_q[1]),
        .I4(py_q[8]),
        .I5(ey_q[0]),
        .O(\genblk1[1].h_val_y_reg[23]_i_14_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[1].h_val_y_reg[23]_i_15 
       (.I0(py_q[8]),
        .I1(ey_q[0]),
        .I2(py_q[9]),
        .I3(ey_q[1]),
        .O(\genblk1[1].h_val_y_reg[23]_i_15_n_0 ));
  LUT6 #(
    .INIT(64'hD4DD4444DDDDD4DD)) 
    \genblk1[1].h_val_y_reg[23]_i_16 
       (.I0(py_q[10]),
        .I1(ey_q[2]),
        .I2(ey_q[0]),
        .I3(py_q[8]),
        .I4(ey_q[1]),
        .I5(py_q[9]),
        .O(\genblk1[1].h_val_y_reg[23]_i_16_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[1].h_val_y_reg[23]_i_2 
       (.I0(\genblk1[1].h_val_y_reg[27]_i_2_n_0 ),
        .I1(py_q[15]),
        .I2(ey_q[7]),
        .O(\genblk1[1].h_val_y_reg[23]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[1].h_val_y_reg[23]_i_3 
       (.I0(\genblk1[1].h_val_y_reg[27]_i_3_n_0 ),
        .I1(ey_q[5]),
        .I2(py_q[13]),
        .I3(py_q[14]),
        .I4(ey_q[6]),
        .O(\genblk1[1].h_val_y_reg[23]_i_3_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[1].h_val_y_reg[23]_i_4 
       (.I0(\genblk1[1].h_val_y_reg[27]_i_3_n_0 ),
        .I1(py_q[13]),
        .I2(ey_q[5]),
        .O(\genblk1[1].h_val_y_reg[23]_i_4_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[1].h_val_y_reg[23]_i_5 
       (.I0(\genblk1[1].h_val_y_reg[23]_i_16_n_0 ),
        .I1(ey_q[3]),
        .I2(py_q[11]),
        .I3(py_q[12]),
        .I4(ey_q[4]),
        .O(\genblk1[1].h_val_y_reg[23]_i_5_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[1].h_val_y_reg[23]_i_6 
       (.I0(\genblk1[1].h_val_y_reg[23]_i_16_n_0 ),
        .I1(py_q[11]),
        .I2(ey_q[3]),
        .O(\genblk1[1].h_val_y_reg[23]_i_6_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[1].h_val_y_reg[23]_i_7 
       (.I0(ey_q[0]),
        .I1(py_q[8]),
        .I2(ey_q[1]),
        .I3(py_q[9]),
        .I4(py_q[10]),
        .I5(ey_q[2]),
        .O(\genblk1[1].h_val_y_reg[23]_i_7_n_0 ));
  LUT6 #(
    .INIT(64'h9696699669966969)) 
    \genblk1[1].h_val_y_reg[23]_i_8 
       (.I0(\genblk1[1].h_val_y_reg[27]_i_1_n_0 ),
        .I1(ey_q[6]),
        .I2(py_q[14]),
        .I3(py_q[13]),
        .I4(ey_q[5]),
        .I5(\genblk1[1].h_val_y_reg[27]_i_3_n_0 ),
        .O(\genblk1[1].h_val_y_reg[23]_i_8_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[1].h_val_y_reg[23]_i_9 
       (.I0(\genblk1[1].h_val_y_reg[23]_i_2_n_0 ),
        .I1(ey_q[5]),
        .I2(py_q[13]),
        .I3(\genblk1[1].h_val_y_reg[27]_i_3_n_0 ),
        .O(\genblk1[1].h_val_y_reg[23]_i_9_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].h_val_y_reg[25]_i_2 
       (.I0(\genblk1[1].h_val_y_reg[27]_i_1_n_0 ),
        .I1(\genblk1[1].h_val_y_reg[23]_i_2_n_0 ),
        .O(\genblk1[1].h_val_y_reg[25]_i_2_n_0 ));
  LUT3 #(
    .INIT(8'h2B)) 
    \genblk1[1].h_val_y_reg[27]_i_1 
       (.I0(py_q[15]),
        .I1(ey_q[7]),
        .I2(\genblk1[1].h_val_y_reg[27]_i_2_n_0 ),
        .O(\genblk1[1].h_val_y_reg[27]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[1].h_val_y_reg[27]_i_2 
       (.I0(py_q[14]),
        .I1(ey_q[6]),
        .I2(\genblk1[1].h_val_y_reg[27]_i_3_n_0 ),
        .I3(ey_q[5]),
        .I4(py_q[13]),
        .O(\genblk1[1].h_val_y_reg[27]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[1].h_val_y_reg[27]_i_3 
       (.I0(py_q[12]),
        .I1(ey_q[4]),
        .I2(\genblk1[1].h_val_y_reg[23]_i_16_n_0 ),
        .I3(ey_q[3]),
        .I4(py_q[11]),
        .O(\genblk1[1].h_val_y_reg[27]_i_3_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_y_reg_reg[15] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_y_reg[15]_i_1_n_0 ),
        .Q(\genblk1[1].h_val_y_reg_reg_n_0_[15] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_y_reg_reg[16] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_y_reg_reg0 [2]),
        .Q(\genblk1[1].h_val_y_reg_reg_n_0_[16] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_y_reg_reg[17] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_y_reg_reg0 [3]),
        .Q(\genblk1[1].h_val_y_reg_reg_n_0_[17] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_y_reg_reg[18] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_y_reg_reg0 [4]),
        .Q(\genblk1[1].h_val_y_reg_reg_n_0_[18] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_y_reg_reg[19] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_y_reg_reg0 [5]),
        .Q(\genblk1[1].h_val_y_reg_reg_n_0_[19] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_y_reg_reg[20] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_y_reg_reg0 [6]),
        .Q(\genblk1[1].h_val_y_reg_reg_n_0_[20] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_y_reg_reg[21] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_y_reg_reg0 [7]),
        .Q(\genblk1[1].h_val_y_reg_reg_n_0_[21] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_y_reg_reg[22] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_y_reg_reg0 [8]),
        .Q(\genblk1[1].h_val_y_reg_reg_n_0_[22] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_y_reg_reg[23] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_y_reg_reg0 [9]),
        .Q(\genblk1[1].h_val_y_reg_reg_n_0_[23] ),
        .R(reset_q));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[1].h_val_y_reg_reg[23]_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[1].h_val_y_reg_reg[23]_i_1_n_0 ,\NLW_genblk1[1].h_val_y_reg_reg[23]_i_1_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[1].h_val_y_reg[27]_i_1_n_0 ,\genblk1[1].h_val_y_reg[23]_i_2_n_0 ,\genblk1[1].h_val_y_reg[23]_i_3_n_0 ,\genblk1[1].h_val_y_reg[23]_i_4_n_0 ,\genblk1[1].h_val_y_reg[23]_i_5_n_0 ,\genblk1[1].h_val_y_reg[23]_i_6_n_0 ,\genblk1[1].h_val_y_reg[23]_i_7_n_0 ,1'b0}),
        .O(\genblk1[1].h_val_y_reg_reg0 [9:2]),
        .S({\genblk1[1].h_val_y_reg[23]_i_8_n_0 ,\genblk1[1].h_val_y_reg[23]_i_9_n_0 ,\genblk1[1].h_val_y_reg[23]_i_10_n_0 ,\genblk1[1].h_val_y_reg[23]_i_11_n_0 ,\genblk1[1].h_val_y_reg[23]_i_12_n_0 ,\genblk1[1].h_val_y_reg[23]_i_13_n_0 ,\genblk1[1].h_val_y_reg[23]_i_14_n_0 ,\genblk1[1].h_val_y_reg[23]_i_15_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_y_reg_reg[24] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_y_reg_reg0 [10]),
        .Q(\genblk1[1].h_val_y_reg_reg_n_0_[24] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_y_reg_reg[25] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_y_reg_reg0 [11]),
        .Q(\genblk1[1].h_val_y_reg_reg_n_0_[25] ),
        .R(reset_q));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[1].h_val_y_reg_reg[25]_i_1 
       (.CI(\genblk1[1].h_val_y_reg_reg[23]_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[1].h_val_y_reg_reg[25]_i_1_CO_UNCONNECTED [7:2],\genblk1[1].h_val_y_reg_reg0 [11],\NLW_genblk1[1].h_val_y_reg_reg[25]_i_1_CO_UNCONNECTED [0]}),
        .DI({\NLW_genblk1[1].h_val_y_reg_reg[25]_i_1_DI_UNCONNECTED [7:2],1'b0,\genblk1[1].h_val_y_reg[27]_i_1_n_0 }),
        .O({\NLW_genblk1[1].h_val_y_reg_reg[25]_i_1_O_UNCONNECTED [7:1],\genblk1[1].h_val_y_reg_reg0 [10]}),
        .S({\NLW_genblk1[1].h_val_y_reg_reg[25]_i_1_S_UNCONNECTED [7:2],1'b1,\genblk1[1].h_val_y_reg[25]_i_2_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_y_reg_reg[27] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_y_reg[27]_i_1_n_0 ),
        .Q(p_0_in3_in),
        .R(reset_q));
  (* SOFT_HLUTNM = "soft_lutpair0" *) 
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].h_val_z_reg[15]_i_1 
       (.I0(pz_q[3]),
        .I1(ez_q[0]),
        .O(\genblk1[1].h_val_z_reg[15]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[1].h_val_z_reg[20]_i_2 
       (.I0(ez_q[0]),
        .I1(pz_q[3]),
        .I2(ez_q[1]),
        .I3(pz_q[4]),
        .I4(pz_q[5]),
        .I5(ez_q[2]),
        .O(\genblk1[1].h_val_z_reg[20]_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[1].h_val_z_reg[20]_i_3 
       (.I0(\genblk1[1].h_val_z_reg[27]_i_1_n_0 ),
        .I1(\genblk1[1].h_val_z_reg[20]_i_2_n_0 ),
        .O(\genblk1[1].h_val_z_reg[20]_i_3_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[1].h_val_z_reg[20]_i_4 
       (.I0(\genblk1[1].h_val_z_reg[27]_i_1_n_0 ),
        .I1(ez_q[1]),
        .I2(pz_q[4]),
        .I3(ez_q[0]),
        .I4(pz_q[3]),
        .O(\genblk1[1].h_val_z_reg[20]_i_4_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[1].h_val_z_reg[20]_i_5 
       (.I0(ez_q[2]),
        .I1(pz_q[5]),
        .I2(pz_q[4]),
        .I3(ez_q[1]),
        .I4(pz_q[3]),
        .I5(ez_q[0]),
        .O(\genblk1[1].h_val_z_reg[20]_i_5_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[1].h_val_z_reg[20]_i_6 
       (.I0(pz_q[3]),
        .I1(ez_q[0]),
        .I2(pz_q[4]),
        .I3(ez_q[1]),
        .O(\genblk1[1].h_val_z_reg[20]_i_6_n_0 ));
  LUT6 #(
    .INIT(64'h2B22BBBB22222B22)) 
    \genblk1[1].h_val_z_reg[27]_i_1 
       (.I0(pz_q[5]),
        .I1(ez_q[2]),
        .I2(ez_q[0]),
        .I3(pz_q[3]),
        .I4(ez_q[1]),
        .I5(pz_q[4]),
        .O(\genblk1[1].h_val_z_reg[27]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_z_reg_reg[15] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_z_reg[15]_i_1_n_0 ),
        .Q(\genblk1[1].h_val_z_reg_reg_n_0_[15] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_z_reg_reg[16] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_z_reg_reg0 [2]),
        .Q(\genblk1[1].h_val_z_reg_reg_n_0_[16] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_z_reg_reg[17] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_z_reg_reg0 [3]),
        .Q(\genblk1[1].h_val_z_reg_reg_n_0_[17] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_z_reg_reg[18] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_z_reg_reg0 [4]),
        .Q(\genblk1[1].h_val_z_reg_reg_n_0_[18] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_z_reg_reg[19] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_z_reg_reg0 [5]),
        .Q(\genblk1[1].h_val_z_reg_reg_n_0_[19] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_z_reg_reg[20] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_z_reg_reg0 [6]),
        .Q(\genblk1[1].h_val_z_reg_reg_n_0_[20] ),
        .R(reset_q));
  (* OPT_MODIFIED = "RETARGET PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[1].h_val_z_reg_reg[20]_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[1].h_val_z_reg_reg[20]_i_1_CO_UNCONNECTED [7:5],\genblk1[1].h_val_z_reg_reg0 [6],\NLW_genblk1[1].h_val_z_reg_reg[20]_i_1_CO_UNCONNECTED [3:0]}),
        .DI({\NLW_genblk1[1].h_val_z_reg_reg[20]_i_1_DI_UNCONNECTED [7:5],1'b0,\genblk1[1].h_val_z_reg[27]_i_1_n_0 ,\genblk1[1].h_val_z_reg[27]_i_1_n_0 ,\genblk1[1].h_val_z_reg[20]_i_2_n_0 ,1'b0}),
        .O({\NLW_genblk1[1].h_val_z_reg_reg[20]_i_1_O_UNCONNECTED [7:4],\genblk1[1].h_val_z_reg_reg0 [5:2]}),
        .S({\NLW_genblk1[1].h_val_z_reg_reg[20]_i_1_S_UNCONNECTED [7:5],1'b1,\genblk1[1].h_val_z_reg[20]_i_3_n_0 ,\genblk1[1].h_val_z_reg[20]_i_4_n_0 ,\genblk1[1].h_val_z_reg[20]_i_5_n_0 ,\genblk1[1].h_val_z_reg[20]_i_6_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[1].h_val_z_reg_reg[27] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[1].h_val_z_reg[27]_i_1_n_0 ),
        .Q(p_0_in4_in),
        .R(reset_q));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[2].g_val_reg0__36_carry 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[2].g_val_reg0__36_carry_n_0 ,\NLW_genblk1[2].g_val_reg0__36_carry_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[2].g_val_reg3__6 [8:2],C__1[1]}),
        .O({\genblk1[2].g_val_reg0__36_carry_n_8 ,\genblk1[2].g_val_reg0__36_carry_n_9 ,\genblk1[2].g_val_reg0__36_carry_n_10 ,\genblk1[2].g_val_reg0__36_carry_n_11 ,\genblk1[2].g_val_reg0__36_carry_n_12 ,\genblk1[2].g_val_reg0__36_carry_n_13 ,\genblk1[2].g_val_reg0__36_carry_n_14 ,\genblk1[2].g_val_reg0__36_carry_n_15 }),
        .S({\genblk1[2].g_val_reg0__36_carry_i_2_n_0 ,\genblk1[2].g_val_reg0__36_carry_i_3_n_0 ,\genblk1[2].g_val_reg0__36_carry_i_4_n_0 ,\genblk1[2].g_val_reg0__36_carry_i_5_n_0 ,\genblk1[2].g_val_reg0__36_carry_i_6_n_0 ,\genblk1[2].g_val_reg0__36_carry_i_7_n_0 ,\genblk1[2].g_val_reg0__36_carry_i_8_n_0 ,\genblk1[2].g_val_reg0__36_carry_i_9_n_0 }));
  (* ADDER_THRESHOLD = "35" *) 
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[2].g_val_reg0__36_carry__0 
       (.CI(\genblk1[2].g_val_reg0__36_carry_n_0 ),
        .CI_TOP(1'b0),
        .CO(\NLW_genblk1[2].g_val_reg0__36_carry__0_CO_UNCONNECTED [7:0]),
        .DI({\NLW_genblk1[2].g_val_reg0__36_carry__0_DI_UNCONNECTED [7:5],1'b0,C__1[12],\genblk1[2].g_val_reg3__6 [11:9]}),
        .O({\NLW_genblk1[2].g_val_reg0__36_carry__0_O_UNCONNECTED [7:5],\genblk1[2].g_val_reg0__36_carry__0_n_11 ,\genblk1[2].g_val_reg0__36_carry__0_n_12 ,\genblk1[2].g_val_reg0__36_carry__0_n_13 ,\genblk1[2].g_val_reg0__36_carry__0_n_14 ,\genblk1[2].g_val_reg0__36_carry__0_n_15 }),
        .S({\NLW_genblk1[2].g_val_reg0__36_carry__0_S_UNCONNECTED [7:5],\genblk1[2].g_val_reg0__36_carry__0_i_2_n_0 ,\genblk1[2].g_val_reg0__36_carry__0_i_3_n_0 ,\genblk1[2].g_val_reg0__36_carry__0_i_4_n_0 ,\genblk1[2].g_val_reg0__36_carry__0_i_5_n_0 ,\genblk1[2].g_val_reg0__36_carry__0_i_6_n_0 }));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[2].g_val_reg0__36_carry__0_i_1 
       (.CI(\genblk1[2].g_val_reg0__36_carry_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[2].g_val_reg0__36_carry__0_i_1_CO_UNCONNECTED [7:2],\genblk1[2].g_val_reg3__6 [11],\NLW_genblk1[2].g_val_reg0__36_carry__0_i_1_CO_UNCONNECTED [0]}),
        .DI({\NLW_genblk1[2].g_val_reg0__36_carry__0_i_1_DI_UNCONNECTED [7:2],1'b0,\genblk1[2].g_val_reg0__36_carry_i_10_n_0 }),
        .O({\NLW_genblk1[2].g_val_reg0__36_carry__0_i_1_O_UNCONNECTED [7:1],\genblk1[2].g_val_reg3__6 [10]}),
        .S({\NLW_genblk1[2].g_val_reg0__36_carry__0_i_1_S_UNCONNECTED [7:2],1'b1,\genblk1[2].g_val_reg0__36_carry__0_i_7_n_0 }));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0__36_carry__0_i_2 
       (.I0(\genblk1[2].g_val_reg0__36_carry_i_10_n_0 ),
        .I1(C__1[13]),
        .O(\genblk1[2].g_val_reg0__36_carry__0_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0__36_carry__0_i_3 
       (.I0(\genblk1[2].g_val_reg0__36_carry_i_10_n_0 ),
        .I1(C__1[12]),
        .O(\genblk1[2].g_val_reg0__36_carry__0_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0__36_carry__0_i_4 
       (.I0(\genblk1[2].g_val_reg3__6 [11]),
        .I1(C__1[11]),
        .O(\genblk1[2].g_val_reg0__36_carry__0_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0__36_carry__0_i_5 
       (.I0(\genblk1[2].g_val_reg3__6 [10]),
        .I1(C__1[10]),
        .O(\genblk1[2].g_val_reg0__36_carry__0_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0__36_carry__0_i_6 
       (.I0(\genblk1[2].g_val_reg3__6 [9]),
        .I1(C__1[9]),
        .O(\genblk1[2].g_val_reg0__36_carry__0_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0__36_carry__0_i_7 
       (.I0(\genblk1[2].g_val_reg0__36_carry_i_10_n_0 ),
        .I1(\genblk1[2].g_val_reg0__36_carry_i_11_n_0 ),
        .O(\genblk1[2].g_val_reg0__36_carry__0_i_7_n_0 ));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[2].g_val_reg0__36_carry_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[2].g_val_reg0__36_carry_i_1_n_0 ,\NLW_genblk1[2].g_val_reg0__36_carry_i_1_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[2].g_val_reg0__36_carry_i_10_n_0 ,\genblk1[2].g_val_reg0__36_carry_i_11_n_0 ,\genblk1[2].g_val_reg0__36_carry_i_12_n_0 ,\genblk1[2].g_val_reg0__36_carry_i_13_n_0 ,\genblk1[2].g_val_reg0__36_carry_i_14_n_0 ,\genblk1[2].g_val_reg0__36_carry_i_15_n_0 ,\genblk1[2].g_val_reg0__36_carry_i_16_n_0 ,1'b0}),
        .O(\genblk1[2].g_val_reg3__6 [9:2]),
        .S({\genblk1[2].g_val_reg0__36_carry_i_17_n_0 ,\genblk1[2].g_val_reg0__36_carry_i_18_n_0 ,\genblk1[2].g_val_reg0__36_carry_i_19_n_0 ,\genblk1[2].g_val_reg0__36_carry_i_20_n_0 ,\genblk1[2].g_val_reg0__36_carry_i_21_n_0 ,\genblk1[2].g_val_reg0__36_carry_i_22_n_0 ,\genblk1[2].g_val_reg0__36_carry_i_23_n_0 ,\genblk1[2].g_val_reg0__36_carry_i_24_n_0 }));
  LUT3 #(
    .INIT(8'h2B)) 
    \genblk1[2].g_val_reg0__36_carry_i_10 
       (.I0(px_q[23]),
        .I1(cx_q[7]),
        .I2(\genblk1[2].g_val_reg0__36_carry_i_25_n_0 ),
        .O(\genblk1[2].g_val_reg0__36_carry_i_10_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[2].g_val_reg0__36_carry_i_11 
       (.I0(\genblk1[2].g_val_reg0__36_carry_i_25_n_0 ),
        .I1(px_q[23]),
        .I2(cx_q[7]),
        .O(\genblk1[2].g_val_reg0__36_carry_i_11_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[2].g_val_reg0__36_carry_i_12 
       (.I0(\genblk1[2].g_val_reg0__36_carry_i_26_n_0 ),
        .I1(cx_q[5]),
        .I2(px_q[21]),
        .I3(px_q[22]),
        .I4(cx_q[6]),
        .O(\genblk1[2].g_val_reg0__36_carry_i_12_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[2].g_val_reg0__36_carry_i_13 
       (.I0(\genblk1[2].g_val_reg0__36_carry_i_26_n_0 ),
        .I1(px_q[21]),
        .I2(cx_q[5]),
        .O(\genblk1[2].g_val_reg0__36_carry_i_13_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[2].g_val_reg0__36_carry_i_14 
       (.I0(\genblk1[2].g_val_reg0__36_carry_i_27_n_0 ),
        .I1(cx_q[3]),
        .I2(px_q[19]),
        .I3(px_q[20]),
        .I4(cx_q[4]),
        .O(\genblk1[2].g_val_reg0__36_carry_i_14_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[2].g_val_reg0__36_carry_i_15 
       (.I0(\genblk1[2].g_val_reg0__36_carry_i_27_n_0 ),
        .I1(px_q[19]),
        .I2(cx_q[3]),
        .O(\genblk1[2].g_val_reg0__36_carry_i_15_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[2].g_val_reg0__36_carry_i_16 
       (.I0(cx_q[0]),
        .I1(px_q[16]),
        .I2(cx_q[1]),
        .I3(px_q[17]),
        .I4(px_q[18]),
        .I5(cx_q[2]),
        .O(\genblk1[2].g_val_reg0__36_carry_i_16_n_0 ));
  LUT6 #(
    .INIT(64'h9696699669966969)) 
    \genblk1[2].g_val_reg0__36_carry_i_17 
       (.I0(\genblk1[2].g_val_reg0__36_carry_i_10_n_0 ),
        .I1(cx_q[6]),
        .I2(px_q[22]),
        .I3(px_q[21]),
        .I4(cx_q[5]),
        .I5(\genblk1[2].g_val_reg0__36_carry_i_26_n_0 ),
        .O(\genblk1[2].g_val_reg0__36_carry_i_17_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[2].g_val_reg0__36_carry_i_18 
       (.I0(\genblk1[2].g_val_reg0__36_carry_i_11_n_0 ),
        .I1(cx_q[5]),
        .I2(px_q[21]),
        .I3(\genblk1[2].g_val_reg0__36_carry_i_26_n_0 ),
        .O(\genblk1[2].g_val_reg0__36_carry_i_18_n_0 ));
  LUT6 #(
    .INIT(64'h9969696666969699)) 
    \genblk1[2].g_val_reg0__36_carry_i_19 
       (.I0(cx_q[6]),
        .I1(px_q[22]),
        .I2(px_q[21]),
        .I3(cx_q[5]),
        .I4(\genblk1[2].g_val_reg0__36_carry_i_26_n_0 ),
        .I5(\genblk1[2].g_val_reg0__36_carry_i_14_n_0 ),
        .O(\genblk1[2].g_val_reg0__36_carry_i_19_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0__36_carry_i_2 
       (.I0(\genblk1[2].g_val_reg3__6 [8]),
        .I1(C__1[8]),
        .O(\genblk1[2].g_val_reg0__36_carry_i_2_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[2].g_val_reg0__36_carry_i_20 
       (.I0(cx_q[5]),
        .I1(px_q[21]),
        .I2(\genblk1[2].g_val_reg0__36_carry_i_26_n_0 ),
        .I3(\genblk1[2].g_val_reg0__36_carry_i_15_n_0 ),
        .O(\genblk1[2].g_val_reg0__36_carry_i_20_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0__36_carry_i_21 
       (.I0(\genblk1[2].g_val_reg0__36_carry_i_14_n_0 ),
        .I1(\genblk1[2].g_val_reg0__36_carry_i_16_n_0 ),
        .O(\genblk1[2].g_val_reg0__36_carry_i_21_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[2].g_val_reg0__36_carry_i_22 
       (.I0(\genblk1[2].g_val_reg0__36_carry_i_15_n_0 ),
        .I1(cx_q[1]),
        .I2(px_q[17]),
        .I3(cx_q[0]),
        .I4(px_q[16]),
        .O(\genblk1[2].g_val_reg0__36_carry_i_22_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[2].g_val_reg0__36_carry_i_23 
       (.I0(cx_q[2]),
        .I1(px_q[18]),
        .I2(px_q[17]),
        .I3(cx_q[1]),
        .I4(px_q[16]),
        .I5(cx_q[0]),
        .O(\genblk1[2].g_val_reg0__36_carry_i_23_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[2].g_val_reg0__36_carry_i_24 
       (.I0(px_q[16]),
        .I1(cx_q[0]),
        .I2(px_q[17]),
        .I3(cx_q[1]),
        .O(\genblk1[2].g_val_reg0__36_carry_i_24_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[2].g_val_reg0__36_carry_i_25 
       (.I0(px_q[22]),
        .I1(cx_q[6]),
        .I2(\genblk1[2].g_val_reg0__36_carry_i_26_n_0 ),
        .I3(cx_q[5]),
        .I4(px_q[21]),
        .O(\genblk1[2].g_val_reg0__36_carry_i_25_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[2].g_val_reg0__36_carry_i_26 
       (.I0(px_q[20]),
        .I1(cx_q[4]),
        .I2(\genblk1[2].g_val_reg0__36_carry_i_27_n_0 ),
        .I3(cx_q[3]),
        .I4(px_q[19]),
        .O(\genblk1[2].g_val_reg0__36_carry_i_26_n_0 ));
  LUT6 #(
    .INIT(64'hD4DD4444DDDDD4DD)) 
    \genblk1[2].g_val_reg0__36_carry_i_27 
       (.I0(px_q[18]),
        .I1(cx_q[2]),
        .I2(cx_q[0]),
        .I3(px_q[16]),
        .I4(cx_q[1]),
        .I5(px_q[17]),
        .O(\genblk1[2].g_val_reg0__36_carry_i_27_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0__36_carry_i_3 
       (.I0(\genblk1[2].g_val_reg3__6 [7]),
        .I1(C__1[7]),
        .O(\genblk1[2].g_val_reg0__36_carry_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0__36_carry_i_4 
       (.I0(\genblk1[2].g_val_reg3__6 [6]),
        .I1(C__1[6]),
        .O(\genblk1[2].g_val_reg0__36_carry_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0__36_carry_i_5 
       (.I0(\genblk1[2].g_val_reg3__6 [5]),
        .I1(C__1[5]),
        .O(\genblk1[2].g_val_reg0__36_carry_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0__36_carry_i_6 
       (.I0(\genblk1[2].g_val_reg3__6 [4]),
        .I1(C__1[4]),
        .O(\genblk1[2].g_val_reg0__36_carry_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0__36_carry_i_7 
       (.I0(\genblk1[2].g_val_reg3__6 [3]),
        .I1(C__1[3]),
        .O(\genblk1[2].g_val_reg0__36_carry_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0__36_carry_i_8 
       (.I0(\genblk1[2].g_val_reg3__6 [2]),
        .I1(C__1[2]),
        .O(\genblk1[2].g_val_reg0__36_carry_i_8_n_0 ));
  LUT3 #(
    .INIT(8'h96)) 
    \genblk1[2].g_val_reg0__36_carry_i_9 
       (.I0(px_q[16]),
        .I1(cx_q[0]),
        .I2(C__1[1]),
        .O(\genblk1[2].g_val_reg0__36_carry_i_9_n_0 ));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[2].g_val_reg0_carry 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[2].g_val_reg0_carry_n_0 ,\NLW_genblk1[2].g_val_reg0_carry_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[2].g_val_reg2__1 [8:2],\genblk1[2].g_val_reg0_carry_i_2_n_0 }),
        .O(C__1[8:1]),
        .S({\genblk1[2].g_val_reg0_carry_i_3_n_0 ,\genblk1[2].g_val_reg0_carry_i_4_n_0 ,\genblk1[2].g_val_reg0_carry_i_5_n_0 ,\genblk1[2].g_val_reg0_carry_i_6_n_0 ,\genblk1[2].g_val_reg0_carry_i_7_n_0 ,\genblk1[2].g_val_reg0_carry_i_8_n_0 ,\genblk1[2].g_val_reg0_carry_i_9_n_0 ,\genblk1[2].g_val_reg0_carry_i_10_n_0 }));
  (* ADDER_THRESHOLD = "35" *) 
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[2].g_val_reg0_carry__0 
       (.CI(\genblk1[2].g_val_reg0_carry_n_0 ),
        .CI_TOP(1'b0),
        .CO(\NLW_genblk1[2].g_val_reg0_carry__0_CO_UNCONNECTED [7:0]),
        .DI({\NLW_genblk1[2].g_val_reg0_carry__0_DI_UNCONNECTED [7:5],1'b0,\genblk1[2].g_val_reg0_carry__0_i_1_n_0 ,\genblk1[2].g_val_reg2__1 [11:9]}),
        .O({\NLW_genblk1[2].g_val_reg0_carry__0_O_UNCONNECTED [7:5],C__1[13:9]}),
        .S({\NLW_genblk1[2].g_val_reg0_carry__0_S_UNCONNECTED [7:5],\genblk1[2].g_val_reg0_carry__0_i_3_n_0 ,\genblk1[2].g_val_reg0_carry__0_i_4_n_0 ,\genblk1[2].g_val_reg0_carry__0_i_5_n_0 ,\genblk1[2].g_val_reg0_carry__0_i_6_n_0 ,\genblk1[2].g_val_reg0_carry__0_i_7_n_0 }));
  LUT3 #(
    .INIT(8'h2B)) 
    \genblk1[2].g_val_reg0_carry__0_i_1 
       (.I0(py_q[23]),
        .I1(cy_q[7]),
        .I2(\genblk1[2].g_val_reg0_carry__0_i_8_n_0 ),
        .O(\genblk1[2].g_val_reg0_carry__0_i_1_n_0 ));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[2].g_val_reg0_carry__0_i_2 
       (.CI(\genblk1[2].g_val_reg0_carry_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[2].g_val_reg0_carry__0_i_2_CO_UNCONNECTED [7:2],\genblk1[2].g_val_reg2__1 [11],\NLW_genblk1[2].g_val_reg0_carry__0_i_2_CO_UNCONNECTED [0]}),
        .DI({\NLW_genblk1[2].g_val_reg0_carry__0_i_2_DI_UNCONNECTED [7:2],1'b0,\genblk1[2].g_val_reg0_carry__0_i_1_n_0 }),
        .O({\NLW_genblk1[2].g_val_reg0_carry__0_i_2_O_UNCONNECTED [7:1],\genblk1[2].g_val_reg2__1 [10]}),
        .S({\NLW_genblk1[2].g_val_reg0_carry__0_i_2_S_UNCONNECTED [7:2],1'b1,\genblk1[2].g_val_reg0_carry__0_i_9_n_0 }));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0_carry__0_i_3 
       (.I0(\genblk1[2].g_val_reg0_carry__0_i_1_n_0 ),
        .I1(\genblk1[2].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[2].g_val_reg0_carry__0_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0_carry__0_i_4 
       (.I0(\genblk1[2].g_val_reg0_carry__0_i_1_n_0 ),
        .I1(\genblk1[2].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[2].g_val_reg0_carry__0_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0_carry__0_i_5 
       (.I0(\genblk1[2].g_val_reg2__1 [11]),
        .I1(\genblk1[2].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[2].g_val_reg0_carry__0_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0_carry__0_i_6 
       (.I0(\genblk1[2].g_val_reg2__1 [10]),
        .I1(\genblk1[2].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[2].g_val_reg0_carry__0_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0_carry__0_i_7 
       (.I0(\genblk1[2].g_val_reg2__1 [9]),
        .I1(\genblk1[2].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[2].g_val_reg0_carry__0_i_7_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[2].g_val_reg0_carry__0_i_8 
       (.I0(py_q[22]),
        .I1(cy_q[6]),
        .I2(\genblk1[2].g_val_reg0_carry_i_27_n_0 ),
        .I3(cy_q[5]),
        .I4(py_q[21]),
        .O(\genblk1[2].g_val_reg0_carry__0_i_8_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0_carry__0_i_9 
       (.I0(\genblk1[2].g_val_reg0_carry__0_i_1_n_0 ),
        .I1(\genblk1[2].g_val_reg0_carry_i_11_n_0 ),
        .O(\genblk1[2].g_val_reg0_carry__0_i_9_n_0 ));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[2].g_val_reg0_carry_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[2].g_val_reg0_carry_i_1_n_0 ,\NLW_genblk1[2].g_val_reg0_carry_i_1_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[2].g_val_reg0_carry__0_i_1_n_0 ,\genblk1[2].g_val_reg0_carry_i_11_n_0 ,\genblk1[2].g_val_reg0_carry_i_12_n_0 ,\genblk1[2].g_val_reg0_carry_i_13_n_0 ,\genblk1[2].g_val_reg0_carry_i_14_n_0 ,\genblk1[2].g_val_reg0_carry_i_15_n_0 ,\genblk1[2].g_val_reg0_carry_i_16_n_0 ,1'b0}),
        .O(\genblk1[2].g_val_reg2__1 [9:2]),
        .S({\genblk1[2].g_val_reg0_carry_i_17_n_0 ,\genblk1[2].g_val_reg0_carry_i_18_n_0 ,\genblk1[2].g_val_reg0_carry_i_19_n_0 ,\genblk1[2].g_val_reg0_carry_i_20_n_0 ,\genblk1[2].g_val_reg0_carry_i_21_n_0 ,\genblk1[2].g_val_reg0_carry_i_22_n_0 ,\genblk1[2].g_val_reg0_carry_i_23_n_0 ,\genblk1[2].g_val_reg0_carry_i_24_n_0 }));
  LUT4 #(
    .INIT(16'h6996)) 
    \genblk1[2].g_val_reg0_carry_i_10 
       (.I0(py_q[16]),
        .I1(cy_q[0]),
        .I2(pz_q[6]),
        .I3(cz_q[0]),
        .O(\genblk1[2].g_val_reg0_carry_i_10_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[2].g_val_reg0_carry_i_11 
       (.I0(\genblk1[2].g_val_reg0_carry__0_i_8_n_0 ),
        .I1(py_q[23]),
        .I2(cy_q[7]),
        .O(\genblk1[2].g_val_reg0_carry_i_11_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[2].g_val_reg0_carry_i_12 
       (.I0(\genblk1[2].g_val_reg0_carry_i_27_n_0 ),
        .I1(cy_q[5]),
        .I2(py_q[21]),
        .I3(py_q[22]),
        .I4(cy_q[6]),
        .O(\genblk1[2].g_val_reg0_carry_i_12_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[2].g_val_reg0_carry_i_13 
       (.I0(\genblk1[2].g_val_reg0_carry_i_27_n_0 ),
        .I1(py_q[21]),
        .I2(cy_q[5]),
        .O(\genblk1[2].g_val_reg0_carry_i_13_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[2].g_val_reg0_carry_i_14 
       (.I0(\genblk1[2].g_val_reg0_carry_i_28_n_0 ),
        .I1(cy_q[3]),
        .I2(py_q[19]),
        .I3(py_q[20]),
        .I4(cy_q[4]),
        .O(\genblk1[2].g_val_reg0_carry_i_14_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[2].g_val_reg0_carry_i_15 
       (.I0(\genblk1[2].g_val_reg0_carry_i_28_n_0 ),
        .I1(py_q[19]),
        .I2(cy_q[3]),
        .O(\genblk1[2].g_val_reg0_carry_i_15_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[2].g_val_reg0_carry_i_16 
       (.I0(cy_q[0]),
        .I1(py_q[16]),
        .I2(cy_q[1]),
        .I3(py_q[17]),
        .I4(py_q[18]),
        .I5(cy_q[2]),
        .O(\genblk1[2].g_val_reg0_carry_i_16_n_0 ));
  LUT6 #(
    .INIT(64'h9696699669966969)) 
    \genblk1[2].g_val_reg0_carry_i_17 
       (.I0(\genblk1[2].g_val_reg0_carry__0_i_1_n_0 ),
        .I1(cy_q[6]),
        .I2(py_q[22]),
        .I3(py_q[21]),
        .I4(cy_q[5]),
        .I5(\genblk1[2].g_val_reg0_carry_i_27_n_0 ),
        .O(\genblk1[2].g_val_reg0_carry_i_17_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[2].g_val_reg0_carry_i_18 
       (.I0(\genblk1[2].g_val_reg0_carry_i_11_n_0 ),
        .I1(cy_q[5]),
        .I2(py_q[21]),
        .I3(\genblk1[2].g_val_reg0_carry_i_27_n_0 ),
        .O(\genblk1[2].g_val_reg0_carry_i_18_n_0 ));
  LUT6 #(
    .INIT(64'h9969696666969699)) 
    \genblk1[2].g_val_reg0_carry_i_19 
       (.I0(cy_q[6]),
        .I1(py_q[22]),
        .I2(py_q[21]),
        .I3(cy_q[5]),
        .I4(\genblk1[2].g_val_reg0_carry_i_27_n_0 ),
        .I5(\genblk1[2].g_val_reg0_carry_i_14_n_0 ),
        .O(\genblk1[2].g_val_reg0_carry_i_19_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0_carry_i_2 
       (.I0(py_q[16]),
        .I1(cy_q[0]),
        .O(\genblk1[2].g_val_reg0_carry_i_2_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[2].g_val_reg0_carry_i_20 
       (.I0(cy_q[5]),
        .I1(py_q[21]),
        .I2(\genblk1[2].g_val_reg0_carry_i_27_n_0 ),
        .I3(\genblk1[2].g_val_reg0_carry_i_15_n_0 ),
        .O(\genblk1[2].g_val_reg0_carry_i_20_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0_carry_i_21 
       (.I0(\genblk1[2].g_val_reg0_carry_i_14_n_0 ),
        .I1(\genblk1[2].g_val_reg0_carry_i_16_n_0 ),
        .O(\genblk1[2].g_val_reg0_carry_i_21_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[2].g_val_reg0_carry_i_22 
       (.I0(\genblk1[2].g_val_reg0_carry_i_15_n_0 ),
        .I1(cy_q[1]),
        .I2(py_q[17]),
        .I3(cy_q[0]),
        .I4(py_q[16]),
        .O(\genblk1[2].g_val_reg0_carry_i_22_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[2].g_val_reg0_carry_i_23 
       (.I0(cy_q[2]),
        .I1(py_q[18]),
        .I2(py_q[17]),
        .I3(cy_q[1]),
        .I4(py_q[16]),
        .I5(cy_q[0]),
        .O(\genblk1[2].g_val_reg0_carry_i_23_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[2].g_val_reg0_carry_i_24 
       (.I0(py_q[16]),
        .I1(cy_q[0]),
        .I2(py_q[17]),
        .I3(cy_q[1]),
        .O(\genblk1[2].g_val_reg0_carry_i_24_n_0 ));
  LUT6 #(
    .INIT(64'h2B22BBBB22222B22)) 
    \genblk1[2].g_val_reg0_carry_i_25 
       (.I0(pz_q[8]),
        .I1(cz_q[2]),
        .I2(cz_q[0]),
        .I3(pz_q[6]),
        .I4(cz_q[1]),
        .I5(pz_q[7]),
        .O(\genblk1[2].g_val_reg0_carry_i_25_n_0 ));
  (* OPT_MODIFIED = "RETARGET PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[2].g_val_reg0_carry_i_26 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[2].g_val_reg0_carry_i_26_CO_UNCONNECTED [7:5],\genblk1[2].g_val_reg1 [6],\NLW_genblk1[2].g_val_reg0_carry_i_26_CO_UNCONNECTED [3:0]}),
        .DI({\NLW_genblk1[2].g_val_reg0_carry_i_26_DI_UNCONNECTED [7:5],1'b0,\genblk1[2].g_val_reg0_carry_i_25_n_0 ,\genblk1[2].g_val_reg0_carry_i_25_n_0 ,\genblk1[2].g_val_reg0_carry_i_29_n_0 ,1'b0}),
        .O({\NLW_genblk1[2].g_val_reg0_carry_i_26_O_UNCONNECTED [7:4],\genblk1[2].g_val_reg1 [5:2]}),
        .S({\NLW_genblk1[2].g_val_reg0_carry_i_26_S_UNCONNECTED [7:5],1'b1,\genblk1[2].g_val_reg0_carry_i_30_n_0 ,\genblk1[2].g_val_reg0_carry_i_31_n_0 ,\genblk1[2].g_val_reg0_carry_i_9_0 }));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[2].g_val_reg0_carry_i_27 
       (.I0(py_q[20]),
        .I1(cy_q[4]),
        .I2(\genblk1[2].g_val_reg0_carry_i_28_n_0 ),
        .I3(cy_q[3]),
        .I4(py_q[19]),
        .O(\genblk1[2].g_val_reg0_carry_i_27_n_0 ));
  LUT6 #(
    .INIT(64'hD4DD4444DDDDD4DD)) 
    \genblk1[2].g_val_reg0_carry_i_28 
       (.I0(py_q[18]),
        .I1(cy_q[2]),
        .I2(cy_q[0]),
        .I3(py_q[16]),
        .I4(cy_q[1]),
        .I5(py_q[17]),
        .O(\genblk1[2].g_val_reg0_carry_i_28_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[2].g_val_reg0_carry_i_29 
       (.I0(cz_q[0]),
        .I1(pz_q[6]),
        .I2(cz_q[1]),
        .I3(pz_q[7]),
        .I4(pz_q[8]),
        .I5(cz_q[2]),
        .O(\genblk1[2].g_val_reg0_carry_i_29_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0_carry_i_3 
       (.I0(\genblk1[2].g_val_reg2__1 [8]),
        .I1(\genblk1[2].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[2].g_val_reg0_carry_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0_carry_i_30 
       (.I0(\genblk1[2].g_val_reg0_carry_i_25_n_0 ),
        .I1(\genblk1[2].g_val_reg0_carry_i_29_n_0 ),
        .O(\genblk1[2].g_val_reg0_carry_i_30_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[2].g_val_reg0_carry_i_31 
       (.I0(\genblk1[2].g_val_reg0_carry_i_25_n_0 ),
        .I1(cz_q[1]),
        .I2(pz_q[7]),
        .I3(cz_q[0]),
        .I4(pz_q[6]),
        .O(\genblk1[2].g_val_reg0_carry_i_31_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0_carry_i_4 
       (.I0(\genblk1[2].g_val_reg2__1 [7]),
        .I1(\genblk1[2].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[2].g_val_reg0_carry_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0_carry_i_5 
       (.I0(\genblk1[2].g_val_reg2__1 [6]),
        .I1(\genblk1[2].g_val_reg1 [6]),
        .O(\genblk1[2].g_val_reg0_carry_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0_carry_i_6 
       (.I0(\genblk1[2].g_val_reg2__1 [5]),
        .I1(\genblk1[2].g_val_reg1 [5]),
        .O(\genblk1[2].g_val_reg0_carry_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0_carry_i_7 
       (.I0(\genblk1[2].g_val_reg2__1 [4]),
        .I1(\genblk1[2].g_val_reg1 [4]),
        .O(\genblk1[2].g_val_reg0_carry_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0_carry_i_8 
       (.I0(\genblk1[2].g_val_reg2__1 [3]),
        .I1(\genblk1[2].g_val_reg1 [3]),
        .O(\genblk1[2].g_val_reg0_carry_i_8_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].g_val_reg0_carry_i_9 
       (.I0(\genblk1[2].g_val_reg2__1 [2]),
        .I1(\genblk1[2].g_val_reg1 [2]),
        .O(\genblk1[2].g_val_reg0_carry_i_9_n_0 ));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[2].g_val_reg0_inferred__0/i__carry 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[2].g_val_reg0_inferred__0/i__carry_n_0 ,\NLW_genblk1[2].g_val_reg0_inferred__0/i__carry_CO_UNCONNECTED [6:0]}),
        .DI(cg_q[8:1]),
        .O(\genblk1[2].g_val_reg0 [8:1]),
        .S({i__carry_i_1__2_n_0,i__carry_i_2__1_n_0,i__carry_i_3__1_n_0,i__carry_i_4__1_n_0,i__carry_i_5__1_n_0,i__carry_i_6__1_n_0,i__carry_i_7__1_n_0,i__carry_i_8__1_n_0}));
  (* ADDER_THRESHOLD = "35" *) 
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[2].g_val_reg0_inferred__0/i__carry__0 
       (.CI(\genblk1[2].g_val_reg0_inferred__0/i__carry_n_0 ),
        .CI_TOP(1'b0),
        .CO(\NLW_genblk1[2].g_val_reg0_inferred__0/i__carry__0_CO_UNCONNECTED [7:0]),
        .DI({\NLW_genblk1[2].g_val_reg0_inferred__0/i__carry__0_DI_UNCONNECTED [7:5],1'b0,cg_q[12:9]}),
        .O({\NLW_genblk1[2].g_val_reg0_inferred__0/i__carry__0_O_UNCONNECTED [7:5],\genblk1[2].g_val_reg0 [13:9]}),
        .S({\NLW_genblk1[2].g_val_reg0_inferred__0/i__carry__0_S_UNCONNECTED [7:5],i__carry__0_i_1__1_n_0,i__carry__0_i_2__1_n_0,i__carry__0_i_3__1_n_0,i__carry__0_i_4__1_n_0,i__carry__0_i_5__1_n_0}));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].g_val_reg[29] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].g_val_reg0 [1]),
        .Q(g[26]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].g_val_reg[30] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].g_val_reg0 [2]),
        .Q(g[27]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].g_val_reg[31] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].g_val_reg0 [3]),
        .Q(g[28]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].g_val_reg[32] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].g_val_reg0 [4]),
        .Q(g[29]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].g_val_reg[33] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].g_val_reg0 [5]),
        .Q(g[30]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].g_val_reg[34] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].g_val_reg0 [6]),
        .Q(g[31]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].g_val_reg[35] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].g_val_reg0 [7]),
        .Q(g[32]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].g_val_reg[36] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].g_val_reg0 [8]),
        .Q(g[33]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].g_val_reg[37] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].g_val_reg0 [9]),
        .Q(g[34]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].g_val_reg[38] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].g_val_reg0 [10]),
        .Q(g[35]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].g_val_reg[39] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].g_val_reg0 [11]),
        .Q(g[36]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].g_val_reg[40] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].g_val_reg0 [12]),
        .Q(g[37]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].g_val_reg[41] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].g_val_reg0 [13]),
        .Q(g[38]),
        .R(reset_q));
  (* SOFT_HLUTNM = "soft_lutpair5" *) 
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].h_val_x_reg[29]_i_1 
       (.I0(px_q[16]),
        .I1(ex_q[0]),
        .O(\genblk1[2].h_val_x_reg[29]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h9969696666969699)) 
    \genblk1[2].h_val_x_reg[37]_i_10 
       (.I0(ex_q[6]),
        .I1(px_q[22]),
        .I2(px_q[21]),
        .I3(ex_q[5]),
        .I4(\genblk1[2].h_val_x_reg[41]_i_3_n_0 ),
        .I5(\genblk1[2].h_val_x_reg[37]_i_5_n_0 ),
        .O(\genblk1[2].h_val_x_reg[37]_i_10_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[2].h_val_x_reg[37]_i_11 
       (.I0(ex_q[5]),
        .I1(px_q[21]),
        .I2(\genblk1[2].h_val_x_reg[41]_i_3_n_0 ),
        .I3(\genblk1[2].h_val_x_reg[37]_i_6_n_0 ),
        .O(\genblk1[2].h_val_x_reg[37]_i_11_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].h_val_x_reg[37]_i_12 
       (.I0(\genblk1[2].h_val_x_reg[37]_i_5_n_0 ),
        .I1(\genblk1[2].h_val_x_reg[37]_i_7_n_0 ),
        .O(\genblk1[2].h_val_x_reg[37]_i_12_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[2].h_val_x_reg[37]_i_13 
       (.I0(\genblk1[2].h_val_x_reg[37]_i_6_n_0 ),
        .I1(ex_q[1]),
        .I2(px_q[17]),
        .I3(ex_q[0]),
        .I4(px_q[16]),
        .O(\genblk1[2].h_val_x_reg[37]_i_13_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[2].h_val_x_reg[37]_i_14 
       (.I0(ex_q[2]),
        .I1(px_q[18]),
        .I2(px_q[17]),
        .I3(ex_q[1]),
        .I4(px_q[16]),
        .I5(ex_q[0]),
        .O(\genblk1[2].h_val_x_reg[37]_i_14_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[2].h_val_x_reg[37]_i_15 
       (.I0(px_q[16]),
        .I1(ex_q[0]),
        .I2(px_q[17]),
        .I3(ex_q[1]),
        .O(\genblk1[2].h_val_x_reg[37]_i_15_n_0 ));
  LUT6 #(
    .INIT(64'hD4DD4444DDDDD4DD)) 
    \genblk1[2].h_val_x_reg[37]_i_16 
       (.I0(px_q[18]),
        .I1(ex_q[2]),
        .I2(ex_q[0]),
        .I3(px_q[16]),
        .I4(ex_q[1]),
        .I5(px_q[17]),
        .O(\genblk1[2].h_val_x_reg[37]_i_16_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[2].h_val_x_reg[37]_i_2 
       (.I0(\genblk1[2].h_val_x_reg[41]_i_2_n_0 ),
        .I1(px_q[23]),
        .I2(ex_q[7]),
        .O(\genblk1[2].h_val_x_reg[37]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[2].h_val_x_reg[37]_i_3 
       (.I0(\genblk1[2].h_val_x_reg[41]_i_3_n_0 ),
        .I1(ex_q[5]),
        .I2(px_q[21]),
        .I3(px_q[22]),
        .I4(ex_q[6]),
        .O(\genblk1[2].h_val_x_reg[37]_i_3_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[2].h_val_x_reg[37]_i_4 
       (.I0(\genblk1[2].h_val_x_reg[41]_i_3_n_0 ),
        .I1(px_q[21]),
        .I2(ex_q[5]),
        .O(\genblk1[2].h_val_x_reg[37]_i_4_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[2].h_val_x_reg[37]_i_5 
       (.I0(\genblk1[2].h_val_x_reg[37]_i_16_n_0 ),
        .I1(ex_q[3]),
        .I2(px_q[19]),
        .I3(px_q[20]),
        .I4(ex_q[4]),
        .O(\genblk1[2].h_val_x_reg[37]_i_5_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[2].h_val_x_reg[37]_i_6 
       (.I0(\genblk1[2].h_val_x_reg[37]_i_16_n_0 ),
        .I1(px_q[19]),
        .I2(ex_q[3]),
        .O(\genblk1[2].h_val_x_reg[37]_i_6_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[2].h_val_x_reg[37]_i_7 
       (.I0(ex_q[0]),
        .I1(px_q[16]),
        .I2(ex_q[1]),
        .I3(px_q[17]),
        .I4(px_q[18]),
        .I5(ex_q[2]),
        .O(\genblk1[2].h_val_x_reg[37]_i_7_n_0 ));
  LUT6 #(
    .INIT(64'h9696699669966969)) 
    \genblk1[2].h_val_x_reg[37]_i_8 
       (.I0(\genblk1[2].h_val_x_reg[41]_i_1_n_0 ),
        .I1(ex_q[6]),
        .I2(px_q[22]),
        .I3(px_q[21]),
        .I4(ex_q[5]),
        .I5(\genblk1[2].h_val_x_reg[41]_i_3_n_0 ),
        .O(\genblk1[2].h_val_x_reg[37]_i_8_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[2].h_val_x_reg[37]_i_9 
       (.I0(\genblk1[2].h_val_x_reg[37]_i_2_n_0 ),
        .I1(ex_q[5]),
        .I2(px_q[21]),
        .I3(\genblk1[2].h_val_x_reg[41]_i_3_n_0 ),
        .O(\genblk1[2].h_val_x_reg[37]_i_9_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].h_val_x_reg[39]_i_2 
       (.I0(\genblk1[2].h_val_x_reg[41]_i_1_n_0 ),
        .I1(\genblk1[2].h_val_x_reg[37]_i_2_n_0 ),
        .O(\genblk1[2].h_val_x_reg[39]_i_2_n_0 ));
  LUT3 #(
    .INIT(8'h2B)) 
    \genblk1[2].h_val_x_reg[41]_i_1 
       (.I0(px_q[23]),
        .I1(ex_q[7]),
        .I2(\genblk1[2].h_val_x_reg[41]_i_2_n_0 ),
        .O(\genblk1[2].h_val_x_reg[41]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[2].h_val_x_reg[41]_i_2 
       (.I0(px_q[22]),
        .I1(ex_q[6]),
        .I2(\genblk1[2].h_val_x_reg[41]_i_3_n_0 ),
        .I3(ex_q[5]),
        .I4(px_q[21]),
        .O(\genblk1[2].h_val_x_reg[41]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[2].h_val_x_reg[41]_i_3 
       (.I0(px_q[20]),
        .I1(ex_q[4]),
        .I2(\genblk1[2].h_val_x_reg[37]_i_16_n_0 ),
        .I3(ex_q[3]),
        .I4(px_q[19]),
        .O(\genblk1[2].h_val_x_reg[41]_i_3_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_x_reg_reg[29] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_x_reg[29]_i_1_n_0 ),
        .Q(\genblk1[2].h_val_x_reg_reg_n_0_[29] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_x_reg_reg[30] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_x_reg_reg0 [2]),
        .Q(\genblk1[2].h_val_x_reg_reg_n_0_[30] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_x_reg_reg[31] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_x_reg_reg0 [3]),
        .Q(\genblk1[2].h_val_x_reg_reg_n_0_[31] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_x_reg_reg[32] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_x_reg_reg0 [4]),
        .Q(\genblk1[2].h_val_x_reg_reg_n_0_[32] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_x_reg_reg[33] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_x_reg_reg0 [5]),
        .Q(\genblk1[2].h_val_x_reg_reg_n_0_[33] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_x_reg_reg[34] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_x_reg_reg0 [6]),
        .Q(\genblk1[2].h_val_x_reg_reg_n_0_[34] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_x_reg_reg[35] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_x_reg_reg0 [7]),
        .Q(\genblk1[2].h_val_x_reg_reg_n_0_[35] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_x_reg_reg[36] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_x_reg_reg0 [8]),
        .Q(\genblk1[2].h_val_x_reg_reg_n_0_[36] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_x_reg_reg[37] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_x_reg_reg0 [9]),
        .Q(\genblk1[2].h_val_x_reg_reg_n_0_[37] ),
        .R(reset_q));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[2].h_val_x_reg_reg[37]_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[2].h_val_x_reg_reg[37]_i_1_n_0 ,\NLW_genblk1[2].h_val_x_reg_reg[37]_i_1_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[2].h_val_x_reg[41]_i_1_n_0 ,\genblk1[2].h_val_x_reg[37]_i_2_n_0 ,\genblk1[2].h_val_x_reg[37]_i_3_n_0 ,\genblk1[2].h_val_x_reg[37]_i_4_n_0 ,\genblk1[2].h_val_x_reg[37]_i_5_n_0 ,\genblk1[2].h_val_x_reg[37]_i_6_n_0 ,\genblk1[2].h_val_x_reg[37]_i_7_n_0 ,1'b0}),
        .O(\genblk1[2].h_val_x_reg_reg0 [9:2]),
        .S({\genblk1[2].h_val_x_reg[37]_i_8_n_0 ,\genblk1[2].h_val_x_reg[37]_i_9_n_0 ,\genblk1[2].h_val_x_reg[37]_i_10_n_0 ,\genblk1[2].h_val_x_reg[37]_i_11_n_0 ,\genblk1[2].h_val_x_reg[37]_i_12_n_0 ,\genblk1[2].h_val_x_reg[37]_i_13_n_0 ,\genblk1[2].h_val_x_reg[37]_i_14_n_0 ,\genblk1[2].h_val_x_reg[37]_i_15_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_x_reg_reg[38] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_x_reg_reg0 [10]),
        .Q(\genblk1[2].h_val_x_reg_reg_n_0_[38] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_x_reg_reg[39] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_x_reg_reg0 [11]),
        .Q(\genblk1[2].h_val_x_reg_reg_n_0_[39] ),
        .R(reset_q));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[2].h_val_x_reg_reg[39]_i_1 
       (.CI(\genblk1[2].h_val_x_reg_reg[37]_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[2].h_val_x_reg_reg[39]_i_1_CO_UNCONNECTED [7:2],\genblk1[2].h_val_x_reg_reg0 [11],\NLW_genblk1[2].h_val_x_reg_reg[39]_i_1_CO_UNCONNECTED [0]}),
        .DI({\NLW_genblk1[2].h_val_x_reg_reg[39]_i_1_DI_UNCONNECTED [7:2],1'b0,\genblk1[2].h_val_x_reg[41]_i_1_n_0 }),
        .O({\NLW_genblk1[2].h_val_x_reg_reg[39]_i_1_O_UNCONNECTED [7:1],\genblk1[2].h_val_x_reg_reg0 [10]}),
        .S({\NLW_genblk1[2].h_val_x_reg_reg[39]_i_1_S_UNCONNECTED [7:2],1'b1,\genblk1[2].h_val_x_reg[39]_i_2_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_x_reg_reg[41] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_x_reg[41]_i_1_n_0 ),
        .Q(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .R(reset_q));
  (* SOFT_HLUTNM = "soft_lutpair4" *) 
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].h_val_y_reg[29]_i_1 
       (.I0(py_q[16]),
        .I1(ey_q[0]),
        .O(\genblk1[2].h_val_y_reg[29]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h9969696666969699)) 
    \genblk1[2].h_val_y_reg[37]_i_10 
       (.I0(ey_q[6]),
        .I1(py_q[22]),
        .I2(py_q[21]),
        .I3(ey_q[5]),
        .I4(\genblk1[2].h_val_y_reg[41]_i_3_n_0 ),
        .I5(\genblk1[2].h_val_y_reg[37]_i_5_n_0 ),
        .O(\genblk1[2].h_val_y_reg[37]_i_10_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[2].h_val_y_reg[37]_i_11 
       (.I0(ey_q[5]),
        .I1(py_q[21]),
        .I2(\genblk1[2].h_val_y_reg[41]_i_3_n_0 ),
        .I3(\genblk1[2].h_val_y_reg[37]_i_6_n_0 ),
        .O(\genblk1[2].h_val_y_reg[37]_i_11_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].h_val_y_reg[37]_i_12 
       (.I0(\genblk1[2].h_val_y_reg[37]_i_5_n_0 ),
        .I1(\genblk1[2].h_val_y_reg[37]_i_7_n_0 ),
        .O(\genblk1[2].h_val_y_reg[37]_i_12_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[2].h_val_y_reg[37]_i_13 
       (.I0(\genblk1[2].h_val_y_reg[37]_i_6_n_0 ),
        .I1(ey_q[1]),
        .I2(py_q[17]),
        .I3(ey_q[0]),
        .I4(py_q[16]),
        .O(\genblk1[2].h_val_y_reg[37]_i_13_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[2].h_val_y_reg[37]_i_14 
       (.I0(ey_q[2]),
        .I1(py_q[18]),
        .I2(py_q[17]),
        .I3(ey_q[1]),
        .I4(py_q[16]),
        .I5(ey_q[0]),
        .O(\genblk1[2].h_val_y_reg[37]_i_14_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[2].h_val_y_reg[37]_i_15 
       (.I0(py_q[16]),
        .I1(ey_q[0]),
        .I2(py_q[17]),
        .I3(ey_q[1]),
        .O(\genblk1[2].h_val_y_reg[37]_i_15_n_0 ));
  LUT6 #(
    .INIT(64'hD4DD4444DDDDD4DD)) 
    \genblk1[2].h_val_y_reg[37]_i_16 
       (.I0(py_q[18]),
        .I1(ey_q[2]),
        .I2(ey_q[0]),
        .I3(py_q[16]),
        .I4(ey_q[1]),
        .I5(py_q[17]),
        .O(\genblk1[2].h_val_y_reg[37]_i_16_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[2].h_val_y_reg[37]_i_2 
       (.I0(\genblk1[2].h_val_y_reg[41]_i_2_n_0 ),
        .I1(py_q[23]),
        .I2(ey_q[7]),
        .O(\genblk1[2].h_val_y_reg[37]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[2].h_val_y_reg[37]_i_3 
       (.I0(\genblk1[2].h_val_y_reg[41]_i_3_n_0 ),
        .I1(ey_q[5]),
        .I2(py_q[21]),
        .I3(py_q[22]),
        .I4(ey_q[6]),
        .O(\genblk1[2].h_val_y_reg[37]_i_3_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[2].h_val_y_reg[37]_i_4 
       (.I0(\genblk1[2].h_val_y_reg[41]_i_3_n_0 ),
        .I1(py_q[21]),
        .I2(ey_q[5]),
        .O(\genblk1[2].h_val_y_reg[37]_i_4_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[2].h_val_y_reg[37]_i_5 
       (.I0(\genblk1[2].h_val_y_reg[37]_i_16_n_0 ),
        .I1(ey_q[3]),
        .I2(py_q[19]),
        .I3(py_q[20]),
        .I4(ey_q[4]),
        .O(\genblk1[2].h_val_y_reg[37]_i_5_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[2].h_val_y_reg[37]_i_6 
       (.I0(\genblk1[2].h_val_y_reg[37]_i_16_n_0 ),
        .I1(py_q[19]),
        .I2(ey_q[3]),
        .O(\genblk1[2].h_val_y_reg[37]_i_6_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[2].h_val_y_reg[37]_i_7 
       (.I0(ey_q[0]),
        .I1(py_q[16]),
        .I2(ey_q[1]),
        .I3(py_q[17]),
        .I4(py_q[18]),
        .I5(ey_q[2]),
        .O(\genblk1[2].h_val_y_reg[37]_i_7_n_0 ));
  LUT6 #(
    .INIT(64'h9696699669966969)) 
    \genblk1[2].h_val_y_reg[37]_i_8 
       (.I0(\genblk1[2].h_val_y_reg[41]_i_1_n_0 ),
        .I1(ey_q[6]),
        .I2(py_q[22]),
        .I3(py_q[21]),
        .I4(ey_q[5]),
        .I5(\genblk1[2].h_val_y_reg[41]_i_3_n_0 ),
        .O(\genblk1[2].h_val_y_reg[37]_i_8_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[2].h_val_y_reg[37]_i_9 
       (.I0(\genblk1[2].h_val_y_reg[37]_i_2_n_0 ),
        .I1(ey_q[5]),
        .I2(py_q[21]),
        .I3(\genblk1[2].h_val_y_reg[41]_i_3_n_0 ),
        .O(\genblk1[2].h_val_y_reg[37]_i_9_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].h_val_y_reg[39]_i_2 
       (.I0(\genblk1[2].h_val_y_reg[41]_i_1_n_0 ),
        .I1(\genblk1[2].h_val_y_reg[37]_i_2_n_0 ),
        .O(\genblk1[2].h_val_y_reg[39]_i_2_n_0 ));
  LUT3 #(
    .INIT(8'h2B)) 
    \genblk1[2].h_val_y_reg[41]_i_1 
       (.I0(py_q[23]),
        .I1(ey_q[7]),
        .I2(\genblk1[2].h_val_y_reg[41]_i_2_n_0 ),
        .O(\genblk1[2].h_val_y_reg[41]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[2].h_val_y_reg[41]_i_2 
       (.I0(py_q[22]),
        .I1(ey_q[6]),
        .I2(\genblk1[2].h_val_y_reg[41]_i_3_n_0 ),
        .I3(ey_q[5]),
        .I4(py_q[21]),
        .O(\genblk1[2].h_val_y_reg[41]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[2].h_val_y_reg[41]_i_3 
       (.I0(py_q[20]),
        .I1(ey_q[4]),
        .I2(\genblk1[2].h_val_y_reg[37]_i_16_n_0 ),
        .I3(ey_q[3]),
        .I4(py_q[19]),
        .O(\genblk1[2].h_val_y_reg[41]_i_3_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_y_reg_reg[29] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_y_reg[29]_i_1_n_0 ),
        .Q(\genblk1[2].h_val_y_reg_reg_n_0_[29] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_y_reg_reg[30] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_y_reg_reg0 [2]),
        .Q(\genblk1[2].h_val_y_reg_reg_n_0_[30] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_y_reg_reg[31] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_y_reg_reg0 [3]),
        .Q(\genblk1[2].h_val_y_reg_reg_n_0_[31] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_y_reg_reg[32] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_y_reg_reg0 [4]),
        .Q(\genblk1[2].h_val_y_reg_reg_n_0_[32] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_y_reg_reg[33] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_y_reg_reg0 [5]),
        .Q(\genblk1[2].h_val_y_reg_reg_n_0_[33] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_y_reg_reg[34] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_y_reg_reg0 [6]),
        .Q(\genblk1[2].h_val_y_reg_reg_n_0_[34] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_y_reg_reg[35] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_y_reg_reg0 [7]),
        .Q(\genblk1[2].h_val_y_reg_reg_n_0_[35] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_y_reg_reg[36] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_y_reg_reg0 [8]),
        .Q(\genblk1[2].h_val_y_reg_reg_n_0_[36] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_y_reg_reg[37] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_y_reg_reg0 [9]),
        .Q(\genblk1[2].h_val_y_reg_reg_n_0_[37] ),
        .R(reset_q));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[2].h_val_y_reg_reg[37]_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[2].h_val_y_reg_reg[37]_i_1_n_0 ,\NLW_genblk1[2].h_val_y_reg_reg[37]_i_1_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[2].h_val_y_reg[41]_i_1_n_0 ,\genblk1[2].h_val_y_reg[37]_i_2_n_0 ,\genblk1[2].h_val_y_reg[37]_i_3_n_0 ,\genblk1[2].h_val_y_reg[37]_i_4_n_0 ,\genblk1[2].h_val_y_reg[37]_i_5_n_0 ,\genblk1[2].h_val_y_reg[37]_i_6_n_0 ,\genblk1[2].h_val_y_reg[37]_i_7_n_0 ,1'b0}),
        .O(\genblk1[2].h_val_y_reg_reg0 [9:2]),
        .S({\genblk1[2].h_val_y_reg[37]_i_8_n_0 ,\genblk1[2].h_val_y_reg[37]_i_9_n_0 ,\genblk1[2].h_val_y_reg[37]_i_10_n_0 ,\genblk1[2].h_val_y_reg[37]_i_11_n_0 ,\genblk1[2].h_val_y_reg[37]_i_12_n_0 ,\genblk1[2].h_val_y_reg[37]_i_13_n_0 ,\genblk1[2].h_val_y_reg[37]_i_14_n_0 ,\genblk1[2].h_val_y_reg[37]_i_15_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_y_reg_reg[38] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_y_reg_reg0 [10]),
        .Q(\genblk1[2].h_val_y_reg_reg_n_0_[38] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_y_reg_reg[39] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_y_reg_reg0 [11]),
        .Q(\genblk1[2].h_val_y_reg_reg_n_0_[39] ),
        .R(reset_q));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[2].h_val_y_reg_reg[39]_i_1 
       (.CI(\genblk1[2].h_val_y_reg_reg[37]_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[2].h_val_y_reg_reg[39]_i_1_CO_UNCONNECTED [7:2],\genblk1[2].h_val_y_reg_reg0 [11],\NLW_genblk1[2].h_val_y_reg_reg[39]_i_1_CO_UNCONNECTED [0]}),
        .DI({\NLW_genblk1[2].h_val_y_reg_reg[39]_i_1_DI_UNCONNECTED [7:2],1'b0,\genblk1[2].h_val_y_reg[41]_i_1_n_0 }),
        .O({\NLW_genblk1[2].h_val_y_reg_reg[39]_i_1_O_UNCONNECTED [7:1],\genblk1[2].h_val_y_reg_reg0 [10]}),
        .S({\NLW_genblk1[2].h_val_y_reg_reg[39]_i_1_S_UNCONNECTED [7:2],1'b1,\genblk1[2].h_val_y_reg[39]_i_2_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_y_reg_reg[41] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_y_reg[41]_i_1_n_0 ),
        .Q(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .R(reset_q));
  (* SOFT_HLUTNM = "soft_lutpair3" *) 
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].h_val_z_reg[29]_i_1 
       (.I0(pz_q[6]),
        .I1(ez_q[0]),
        .O(\genblk1[2].h_val_z_reg[29]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[2].h_val_z_reg[34]_i_2 
       (.I0(ez_q[0]),
        .I1(pz_q[6]),
        .I2(ez_q[1]),
        .I3(pz_q[7]),
        .I4(pz_q[8]),
        .I5(ez_q[2]),
        .O(\genblk1[2].h_val_z_reg[34]_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[2].h_val_z_reg[34]_i_3 
       (.I0(\genblk1[2].h_val_z_reg[41]_i_1_n_0 ),
        .I1(\genblk1[2].h_val_z_reg[34]_i_2_n_0 ),
        .O(\genblk1[2].h_val_z_reg[34]_i_3_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[2].h_val_z_reg[34]_i_4 
       (.I0(\genblk1[2].h_val_z_reg[41]_i_1_n_0 ),
        .I1(ez_q[1]),
        .I2(pz_q[7]),
        .I3(ez_q[0]),
        .I4(pz_q[6]),
        .O(\genblk1[2].h_val_z_reg[34]_i_4_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[2].h_val_z_reg[34]_i_5 
       (.I0(ez_q[2]),
        .I1(pz_q[8]),
        .I2(pz_q[7]),
        .I3(ez_q[1]),
        .I4(pz_q[6]),
        .I5(ez_q[0]),
        .O(\genblk1[2].h_val_z_reg[34]_i_5_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[2].h_val_z_reg[34]_i_6 
       (.I0(pz_q[6]),
        .I1(ez_q[0]),
        .I2(pz_q[7]),
        .I3(ez_q[1]),
        .O(\genblk1[2].h_val_z_reg[34]_i_6_n_0 ));
  LUT6 #(
    .INIT(64'h2B22BBBB22222B22)) 
    \genblk1[2].h_val_z_reg[41]_i_1 
       (.I0(pz_q[8]),
        .I1(ez_q[2]),
        .I2(ez_q[0]),
        .I3(pz_q[6]),
        .I4(ez_q[1]),
        .I5(pz_q[7]),
        .O(\genblk1[2].h_val_z_reg[41]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_z_reg_reg[29] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_z_reg[29]_i_1_n_0 ),
        .Q(\genblk1[2].h_val_z_reg_reg_n_0_[29] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_z_reg_reg[30] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_z_reg_reg0 [2]),
        .Q(\genblk1[2].h_val_z_reg_reg_n_0_[30] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_z_reg_reg[31] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_z_reg_reg0 [3]),
        .Q(\genblk1[2].h_val_z_reg_reg_n_0_[31] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_z_reg_reg[32] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_z_reg_reg0 [4]),
        .Q(\genblk1[2].h_val_z_reg_reg_n_0_[32] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_z_reg_reg[33] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_z_reg_reg0 [5]),
        .Q(\genblk1[2].h_val_z_reg_reg_n_0_[33] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_z_reg_reg[34] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_z_reg_reg0 [6]),
        .Q(\genblk1[2].h_val_z_reg_reg_n_0_[34] ),
        .R(reset_q));
  (* OPT_MODIFIED = "RETARGET PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[2].h_val_z_reg_reg[34]_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[2].h_val_z_reg_reg[34]_i_1_CO_UNCONNECTED [7:5],\genblk1[2].h_val_z_reg_reg0 [6],\NLW_genblk1[2].h_val_z_reg_reg[34]_i_1_CO_UNCONNECTED [3:0]}),
        .DI({\NLW_genblk1[2].h_val_z_reg_reg[34]_i_1_DI_UNCONNECTED [7:5],1'b0,\genblk1[2].h_val_z_reg[41]_i_1_n_0 ,\genblk1[2].h_val_z_reg[41]_i_1_n_0 ,\genblk1[2].h_val_z_reg[34]_i_2_n_0 ,1'b0}),
        .O({\NLW_genblk1[2].h_val_z_reg_reg[34]_i_1_O_UNCONNECTED [7:4],\genblk1[2].h_val_z_reg_reg0 [5:2]}),
        .S({\NLW_genblk1[2].h_val_z_reg_reg[34]_i_1_S_UNCONNECTED [7:5],1'b1,\genblk1[2].h_val_z_reg[34]_i_3_n_0 ,\genblk1[2].h_val_z_reg[34]_i_4_n_0 ,\genblk1[2].h_val_z_reg[34]_i_5_n_0 ,\genblk1[2].h_val_z_reg[34]_i_6_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[2].h_val_z_reg_reg[41] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[2].h_val_z_reg[41]_i_1_n_0 ),
        .Q(\genblk1[2].h_val_z_reg_reg_n_0_[41] ),
        .R(reset_q));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[3].g_val_reg0__36_carry 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[3].g_val_reg0__36_carry_n_0 ,\NLW_genblk1[3].g_val_reg0__36_carry_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[3].g_val_reg3__6 [8:2],C__2[1]}),
        .O({\genblk1[3].g_val_reg0__36_carry_n_8 ,\genblk1[3].g_val_reg0__36_carry_n_9 ,\genblk1[3].g_val_reg0__36_carry_n_10 ,\genblk1[3].g_val_reg0__36_carry_n_11 ,\genblk1[3].g_val_reg0__36_carry_n_12 ,\genblk1[3].g_val_reg0__36_carry_n_13 ,\genblk1[3].g_val_reg0__36_carry_n_14 ,\genblk1[3].g_val_reg0__36_carry_n_15 }),
        .S({\genblk1[3].g_val_reg0__36_carry_i_2_n_0 ,\genblk1[3].g_val_reg0__36_carry_i_3_n_0 ,\genblk1[3].g_val_reg0__36_carry_i_4_n_0 ,\genblk1[3].g_val_reg0__36_carry_i_5_n_0 ,\genblk1[3].g_val_reg0__36_carry_i_6_n_0 ,\genblk1[3].g_val_reg0__36_carry_i_7_n_0 ,\genblk1[3].g_val_reg0__36_carry_i_8_n_0 ,\genblk1[3].g_val_reg0__36_carry_i_9_n_0 }));
  (* ADDER_THRESHOLD = "35" *) 
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[3].g_val_reg0__36_carry__0 
       (.CI(\genblk1[3].g_val_reg0__36_carry_n_0 ),
        .CI_TOP(1'b0),
        .CO(\NLW_genblk1[3].g_val_reg0__36_carry__0_CO_UNCONNECTED [7:0]),
        .DI({\NLW_genblk1[3].g_val_reg0__36_carry__0_DI_UNCONNECTED [7:5],1'b0,C__2[12],\genblk1[3].g_val_reg3__6 [11:9]}),
        .O({\NLW_genblk1[3].g_val_reg0__36_carry__0_O_UNCONNECTED [7:5],\genblk1[3].g_val_reg0__36_carry__0_n_11 ,\genblk1[3].g_val_reg0__36_carry__0_n_12 ,\genblk1[3].g_val_reg0__36_carry__0_n_13 ,\genblk1[3].g_val_reg0__36_carry__0_n_14 ,\genblk1[3].g_val_reg0__36_carry__0_n_15 }),
        .S({\NLW_genblk1[3].g_val_reg0__36_carry__0_S_UNCONNECTED [7:5],\genblk1[3].g_val_reg0__36_carry__0_i_2_n_0 ,\genblk1[3].g_val_reg0__36_carry__0_i_3_n_0 ,\genblk1[3].g_val_reg0__36_carry__0_i_4_n_0 ,\genblk1[3].g_val_reg0__36_carry__0_i_5_n_0 ,\genblk1[3].g_val_reg0__36_carry__0_i_6_n_0 }));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[3].g_val_reg0__36_carry__0_i_1 
       (.CI(\genblk1[3].g_val_reg0__36_carry_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[3].g_val_reg0__36_carry__0_i_1_CO_UNCONNECTED [7:2],\genblk1[3].g_val_reg3__6 [11],\NLW_genblk1[3].g_val_reg0__36_carry__0_i_1_CO_UNCONNECTED [0]}),
        .DI({\NLW_genblk1[3].g_val_reg0__36_carry__0_i_1_DI_UNCONNECTED [7:2],1'b0,\genblk1[3].g_val_reg0__36_carry_i_10_n_0 }),
        .O({\NLW_genblk1[3].g_val_reg0__36_carry__0_i_1_O_UNCONNECTED [7:1],\genblk1[3].g_val_reg3__6 [10]}),
        .S({\NLW_genblk1[3].g_val_reg0__36_carry__0_i_1_S_UNCONNECTED [7:2],1'b1,\genblk1[3].g_val_reg0__36_carry__0_i_7_n_0 }));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0__36_carry__0_i_2 
       (.I0(\genblk1[3].g_val_reg0__36_carry_i_10_n_0 ),
        .I1(C__2[13]),
        .O(\genblk1[3].g_val_reg0__36_carry__0_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0__36_carry__0_i_3 
       (.I0(\genblk1[3].g_val_reg0__36_carry_i_10_n_0 ),
        .I1(C__2[12]),
        .O(\genblk1[3].g_val_reg0__36_carry__0_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0__36_carry__0_i_4 
       (.I0(\genblk1[3].g_val_reg3__6 [11]),
        .I1(C__2[11]),
        .O(\genblk1[3].g_val_reg0__36_carry__0_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0__36_carry__0_i_5 
       (.I0(\genblk1[3].g_val_reg3__6 [10]),
        .I1(C__2[10]),
        .O(\genblk1[3].g_val_reg0__36_carry__0_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0__36_carry__0_i_6 
       (.I0(\genblk1[3].g_val_reg3__6 [9]),
        .I1(C__2[9]),
        .O(\genblk1[3].g_val_reg0__36_carry__0_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0__36_carry__0_i_7 
       (.I0(\genblk1[3].g_val_reg0__36_carry_i_10_n_0 ),
        .I1(\genblk1[3].g_val_reg0__36_carry_i_11_n_0 ),
        .O(\genblk1[3].g_val_reg0__36_carry__0_i_7_n_0 ));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[3].g_val_reg0__36_carry_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[3].g_val_reg0__36_carry_i_1_n_0 ,\NLW_genblk1[3].g_val_reg0__36_carry_i_1_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[3].g_val_reg0__36_carry_i_10_n_0 ,\genblk1[3].g_val_reg0__36_carry_i_11_n_0 ,\genblk1[3].g_val_reg0__36_carry_i_12_n_0 ,\genblk1[3].g_val_reg0__36_carry_i_13_n_0 ,\genblk1[3].g_val_reg0__36_carry_i_14_n_0 ,\genblk1[3].g_val_reg0__36_carry_i_15_n_0 ,\genblk1[3].g_val_reg0__36_carry_i_16_n_0 ,1'b0}),
        .O(\genblk1[3].g_val_reg3__6 [9:2]),
        .S({\genblk1[3].g_val_reg0__36_carry_i_17_n_0 ,\genblk1[3].g_val_reg0__36_carry_i_18_n_0 ,\genblk1[3].g_val_reg0__36_carry_i_19_n_0 ,\genblk1[3].g_val_reg0__36_carry_i_20_n_0 ,\genblk1[3].g_val_reg0__36_carry_i_21_n_0 ,\genblk1[3].g_val_reg0__36_carry_i_22_n_0 ,\genblk1[3].g_val_reg0__36_carry_i_23_n_0 ,\genblk1[3].g_val_reg0__36_carry_i_24_n_0 }));
  LUT3 #(
    .INIT(8'h2B)) 
    \genblk1[3].g_val_reg0__36_carry_i_10 
       (.I0(px_q[31]),
        .I1(cx_q[7]),
        .I2(\genblk1[3].g_val_reg0__36_carry_i_25_n_0 ),
        .O(\genblk1[3].g_val_reg0__36_carry_i_10_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[3].g_val_reg0__36_carry_i_11 
       (.I0(\genblk1[3].g_val_reg0__36_carry_i_25_n_0 ),
        .I1(px_q[31]),
        .I2(cx_q[7]),
        .O(\genblk1[3].g_val_reg0__36_carry_i_11_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[3].g_val_reg0__36_carry_i_12 
       (.I0(\genblk1[3].g_val_reg0__36_carry_i_26_n_0 ),
        .I1(cx_q[5]),
        .I2(px_q[29]),
        .I3(px_q[30]),
        .I4(cx_q[6]),
        .O(\genblk1[3].g_val_reg0__36_carry_i_12_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[3].g_val_reg0__36_carry_i_13 
       (.I0(\genblk1[3].g_val_reg0__36_carry_i_26_n_0 ),
        .I1(px_q[29]),
        .I2(cx_q[5]),
        .O(\genblk1[3].g_val_reg0__36_carry_i_13_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[3].g_val_reg0__36_carry_i_14 
       (.I0(\genblk1[3].g_val_reg0__36_carry_i_27_n_0 ),
        .I1(cx_q[3]),
        .I2(px_q[27]),
        .I3(px_q[28]),
        .I4(cx_q[4]),
        .O(\genblk1[3].g_val_reg0__36_carry_i_14_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[3].g_val_reg0__36_carry_i_15 
       (.I0(\genblk1[3].g_val_reg0__36_carry_i_27_n_0 ),
        .I1(px_q[27]),
        .I2(cx_q[3]),
        .O(\genblk1[3].g_val_reg0__36_carry_i_15_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[3].g_val_reg0__36_carry_i_16 
       (.I0(cx_q[0]),
        .I1(px_q[24]),
        .I2(cx_q[1]),
        .I3(px_q[25]),
        .I4(px_q[26]),
        .I5(cx_q[2]),
        .O(\genblk1[3].g_val_reg0__36_carry_i_16_n_0 ));
  LUT6 #(
    .INIT(64'h9696699669966969)) 
    \genblk1[3].g_val_reg0__36_carry_i_17 
       (.I0(\genblk1[3].g_val_reg0__36_carry_i_10_n_0 ),
        .I1(cx_q[6]),
        .I2(px_q[30]),
        .I3(px_q[29]),
        .I4(cx_q[5]),
        .I5(\genblk1[3].g_val_reg0__36_carry_i_26_n_0 ),
        .O(\genblk1[3].g_val_reg0__36_carry_i_17_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[3].g_val_reg0__36_carry_i_18 
       (.I0(\genblk1[3].g_val_reg0__36_carry_i_11_n_0 ),
        .I1(cx_q[5]),
        .I2(px_q[29]),
        .I3(\genblk1[3].g_val_reg0__36_carry_i_26_n_0 ),
        .O(\genblk1[3].g_val_reg0__36_carry_i_18_n_0 ));
  LUT6 #(
    .INIT(64'h9969696666969699)) 
    \genblk1[3].g_val_reg0__36_carry_i_19 
       (.I0(cx_q[6]),
        .I1(px_q[30]),
        .I2(px_q[29]),
        .I3(cx_q[5]),
        .I4(\genblk1[3].g_val_reg0__36_carry_i_26_n_0 ),
        .I5(\genblk1[3].g_val_reg0__36_carry_i_14_n_0 ),
        .O(\genblk1[3].g_val_reg0__36_carry_i_19_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0__36_carry_i_2 
       (.I0(\genblk1[3].g_val_reg3__6 [8]),
        .I1(C__2[8]),
        .O(\genblk1[3].g_val_reg0__36_carry_i_2_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[3].g_val_reg0__36_carry_i_20 
       (.I0(cx_q[5]),
        .I1(px_q[29]),
        .I2(\genblk1[3].g_val_reg0__36_carry_i_26_n_0 ),
        .I3(\genblk1[3].g_val_reg0__36_carry_i_15_n_0 ),
        .O(\genblk1[3].g_val_reg0__36_carry_i_20_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0__36_carry_i_21 
       (.I0(\genblk1[3].g_val_reg0__36_carry_i_14_n_0 ),
        .I1(\genblk1[3].g_val_reg0__36_carry_i_16_n_0 ),
        .O(\genblk1[3].g_val_reg0__36_carry_i_21_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[3].g_val_reg0__36_carry_i_22 
       (.I0(\genblk1[3].g_val_reg0__36_carry_i_15_n_0 ),
        .I1(cx_q[1]),
        .I2(px_q[25]),
        .I3(cx_q[0]),
        .I4(px_q[24]),
        .O(\genblk1[3].g_val_reg0__36_carry_i_22_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[3].g_val_reg0__36_carry_i_23 
       (.I0(cx_q[2]),
        .I1(px_q[26]),
        .I2(px_q[25]),
        .I3(cx_q[1]),
        .I4(px_q[24]),
        .I5(cx_q[0]),
        .O(\genblk1[3].g_val_reg0__36_carry_i_23_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[3].g_val_reg0__36_carry_i_24 
       (.I0(px_q[24]),
        .I1(cx_q[0]),
        .I2(px_q[25]),
        .I3(cx_q[1]),
        .O(\genblk1[3].g_val_reg0__36_carry_i_24_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[3].g_val_reg0__36_carry_i_25 
       (.I0(px_q[30]),
        .I1(cx_q[6]),
        .I2(\genblk1[3].g_val_reg0__36_carry_i_26_n_0 ),
        .I3(cx_q[5]),
        .I4(px_q[29]),
        .O(\genblk1[3].g_val_reg0__36_carry_i_25_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[3].g_val_reg0__36_carry_i_26 
       (.I0(px_q[28]),
        .I1(cx_q[4]),
        .I2(\genblk1[3].g_val_reg0__36_carry_i_27_n_0 ),
        .I3(cx_q[3]),
        .I4(px_q[27]),
        .O(\genblk1[3].g_val_reg0__36_carry_i_26_n_0 ));
  LUT6 #(
    .INIT(64'hD4DD4444DDDDD4DD)) 
    \genblk1[3].g_val_reg0__36_carry_i_27 
       (.I0(px_q[26]),
        .I1(cx_q[2]),
        .I2(cx_q[0]),
        .I3(px_q[24]),
        .I4(cx_q[1]),
        .I5(px_q[25]),
        .O(\genblk1[3].g_val_reg0__36_carry_i_27_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0__36_carry_i_3 
       (.I0(\genblk1[3].g_val_reg3__6 [7]),
        .I1(C__2[7]),
        .O(\genblk1[3].g_val_reg0__36_carry_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0__36_carry_i_4 
       (.I0(\genblk1[3].g_val_reg3__6 [6]),
        .I1(C__2[6]),
        .O(\genblk1[3].g_val_reg0__36_carry_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0__36_carry_i_5 
       (.I0(\genblk1[3].g_val_reg3__6 [5]),
        .I1(C__2[5]),
        .O(\genblk1[3].g_val_reg0__36_carry_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0__36_carry_i_6 
       (.I0(\genblk1[3].g_val_reg3__6 [4]),
        .I1(C__2[4]),
        .O(\genblk1[3].g_val_reg0__36_carry_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0__36_carry_i_7 
       (.I0(\genblk1[3].g_val_reg3__6 [3]),
        .I1(C__2[3]),
        .O(\genblk1[3].g_val_reg0__36_carry_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0__36_carry_i_8 
       (.I0(\genblk1[3].g_val_reg3__6 [2]),
        .I1(C__2[2]),
        .O(\genblk1[3].g_val_reg0__36_carry_i_8_n_0 ));
  LUT3 #(
    .INIT(8'h96)) 
    \genblk1[3].g_val_reg0__36_carry_i_9 
       (.I0(px_q[24]),
        .I1(cx_q[0]),
        .I2(C__2[1]),
        .O(\genblk1[3].g_val_reg0__36_carry_i_9_n_0 ));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[3].g_val_reg0_carry 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[3].g_val_reg0_carry_n_0 ,\NLW_genblk1[3].g_val_reg0_carry_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[3].g_val_reg2__1 [8:2],\genblk1[3].g_val_reg0_carry_i_2_n_0 }),
        .O(C__2[8:1]),
        .S({\genblk1[3].g_val_reg0_carry_i_3_n_0 ,\genblk1[3].g_val_reg0_carry_i_4_n_0 ,\genblk1[3].g_val_reg0_carry_i_5_n_0 ,\genblk1[3].g_val_reg0_carry_i_6_n_0 ,\genblk1[3].g_val_reg0_carry_i_7_n_0 ,\genblk1[3].g_val_reg0_carry_i_8_n_0 ,\genblk1[3].g_val_reg0_carry_i_9_n_0 ,\genblk1[3].g_val_reg0_carry_i_10_n_0 }));
  (* ADDER_THRESHOLD = "35" *) 
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[3].g_val_reg0_carry__0 
       (.CI(\genblk1[3].g_val_reg0_carry_n_0 ),
        .CI_TOP(1'b0),
        .CO(\NLW_genblk1[3].g_val_reg0_carry__0_CO_UNCONNECTED [7:0]),
        .DI({\NLW_genblk1[3].g_val_reg0_carry__0_DI_UNCONNECTED [7:5],1'b0,\genblk1[3].g_val_reg0_carry__0_i_1_n_0 ,\genblk1[3].g_val_reg2__1 [11:9]}),
        .O({\NLW_genblk1[3].g_val_reg0_carry__0_O_UNCONNECTED [7:5],C__2[13:9]}),
        .S({\NLW_genblk1[3].g_val_reg0_carry__0_S_UNCONNECTED [7:5],\genblk1[3].g_val_reg0_carry__0_i_3_n_0 ,\genblk1[3].g_val_reg0_carry__0_i_4_n_0 ,\genblk1[3].g_val_reg0_carry__0_i_5_n_0 ,\genblk1[3].g_val_reg0_carry__0_i_6_n_0 ,\genblk1[3].g_val_reg0_carry__0_i_7_n_0 }));
  LUT3 #(
    .INIT(8'h2B)) 
    \genblk1[3].g_val_reg0_carry__0_i_1 
       (.I0(py_q[31]),
        .I1(cy_q[7]),
        .I2(\genblk1[3].g_val_reg0_carry__0_i_8_n_0 ),
        .O(\genblk1[3].g_val_reg0_carry__0_i_1_n_0 ));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[3].g_val_reg0_carry__0_i_2 
       (.CI(\genblk1[3].g_val_reg0_carry_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[3].g_val_reg0_carry__0_i_2_CO_UNCONNECTED [7:2],\genblk1[3].g_val_reg2__1 [11],\NLW_genblk1[3].g_val_reg0_carry__0_i_2_CO_UNCONNECTED [0]}),
        .DI({\NLW_genblk1[3].g_val_reg0_carry__0_i_2_DI_UNCONNECTED [7:2],1'b0,\genblk1[3].g_val_reg0_carry__0_i_1_n_0 }),
        .O({\NLW_genblk1[3].g_val_reg0_carry__0_i_2_O_UNCONNECTED [7:1],\genblk1[3].g_val_reg2__1 [10]}),
        .S({\NLW_genblk1[3].g_val_reg0_carry__0_i_2_S_UNCONNECTED [7:2],1'b1,\genblk1[3].g_val_reg0_carry__0_i_9_n_0 }));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0_carry__0_i_3 
       (.I0(\genblk1[3].g_val_reg0_carry__0_i_1_n_0 ),
        .I1(\genblk1[3].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[3].g_val_reg0_carry__0_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0_carry__0_i_4 
       (.I0(\genblk1[3].g_val_reg0_carry__0_i_1_n_0 ),
        .I1(\genblk1[3].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[3].g_val_reg0_carry__0_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0_carry__0_i_5 
       (.I0(\genblk1[3].g_val_reg2__1 [11]),
        .I1(\genblk1[3].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[3].g_val_reg0_carry__0_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0_carry__0_i_6 
       (.I0(\genblk1[3].g_val_reg2__1 [10]),
        .I1(\genblk1[3].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[3].g_val_reg0_carry__0_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0_carry__0_i_7 
       (.I0(\genblk1[3].g_val_reg2__1 [9]),
        .I1(\genblk1[3].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[3].g_val_reg0_carry__0_i_7_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[3].g_val_reg0_carry__0_i_8 
       (.I0(py_q[30]),
        .I1(cy_q[6]),
        .I2(\genblk1[3].g_val_reg0_carry_i_27_n_0 ),
        .I3(cy_q[5]),
        .I4(py_q[29]),
        .O(\genblk1[3].g_val_reg0_carry__0_i_8_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0_carry__0_i_9 
       (.I0(\genblk1[3].g_val_reg0_carry__0_i_1_n_0 ),
        .I1(\genblk1[3].g_val_reg0_carry_i_11_n_0 ),
        .O(\genblk1[3].g_val_reg0_carry__0_i_9_n_0 ));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[3].g_val_reg0_carry_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[3].g_val_reg0_carry_i_1_n_0 ,\NLW_genblk1[3].g_val_reg0_carry_i_1_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[3].g_val_reg0_carry__0_i_1_n_0 ,\genblk1[3].g_val_reg0_carry_i_11_n_0 ,\genblk1[3].g_val_reg0_carry_i_12_n_0 ,\genblk1[3].g_val_reg0_carry_i_13_n_0 ,\genblk1[3].g_val_reg0_carry_i_14_n_0 ,\genblk1[3].g_val_reg0_carry_i_15_n_0 ,\genblk1[3].g_val_reg0_carry_i_16_n_0 ,1'b0}),
        .O(\genblk1[3].g_val_reg2__1 [9:2]),
        .S({\genblk1[3].g_val_reg0_carry_i_17_n_0 ,\genblk1[3].g_val_reg0_carry_i_18_n_0 ,\genblk1[3].g_val_reg0_carry_i_19_n_0 ,\genblk1[3].g_val_reg0_carry_i_20_n_0 ,\genblk1[3].g_val_reg0_carry_i_21_n_0 ,\genblk1[3].g_val_reg0_carry_i_22_n_0 ,\genblk1[3].g_val_reg0_carry_i_23_n_0 ,\genblk1[3].g_val_reg0_carry_i_24_n_0 }));
  LUT4 #(
    .INIT(16'h6996)) 
    \genblk1[3].g_val_reg0_carry_i_10 
       (.I0(py_q[24]),
        .I1(cy_q[0]),
        .I2(pz_q[9]),
        .I3(cz_q[0]),
        .O(\genblk1[3].g_val_reg0_carry_i_10_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[3].g_val_reg0_carry_i_11 
       (.I0(\genblk1[3].g_val_reg0_carry__0_i_8_n_0 ),
        .I1(py_q[31]),
        .I2(cy_q[7]),
        .O(\genblk1[3].g_val_reg0_carry_i_11_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[3].g_val_reg0_carry_i_12 
       (.I0(\genblk1[3].g_val_reg0_carry_i_27_n_0 ),
        .I1(cy_q[5]),
        .I2(py_q[29]),
        .I3(py_q[30]),
        .I4(cy_q[6]),
        .O(\genblk1[3].g_val_reg0_carry_i_12_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[3].g_val_reg0_carry_i_13 
       (.I0(\genblk1[3].g_val_reg0_carry_i_27_n_0 ),
        .I1(py_q[29]),
        .I2(cy_q[5]),
        .O(\genblk1[3].g_val_reg0_carry_i_13_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[3].g_val_reg0_carry_i_14 
       (.I0(\genblk1[3].g_val_reg0_carry_i_28_n_0 ),
        .I1(cy_q[3]),
        .I2(py_q[27]),
        .I3(py_q[28]),
        .I4(cy_q[4]),
        .O(\genblk1[3].g_val_reg0_carry_i_14_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[3].g_val_reg0_carry_i_15 
       (.I0(\genblk1[3].g_val_reg0_carry_i_28_n_0 ),
        .I1(py_q[27]),
        .I2(cy_q[3]),
        .O(\genblk1[3].g_val_reg0_carry_i_15_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[3].g_val_reg0_carry_i_16 
       (.I0(cy_q[0]),
        .I1(py_q[24]),
        .I2(cy_q[1]),
        .I3(py_q[25]),
        .I4(py_q[26]),
        .I5(cy_q[2]),
        .O(\genblk1[3].g_val_reg0_carry_i_16_n_0 ));
  LUT6 #(
    .INIT(64'h9696699669966969)) 
    \genblk1[3].g_val_reg0_carry_i_17 
       (.I0(\genblk1[3].g_val_reg0_carry__0_i_1_n_0 ),
        .I1(cy_q[6]),
        .I2(py_q[30]),
        .I3(py_q[29]),
        .I4(cy_q[5]),
        .I5(\genblk1[3].g_val_reg0_carry_i_27_n_0 ),
        .O(\genblk1[3].g_val_reg0_carry_i_17_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[3].g_val_reg0_carry_i_18 
       (.I0(\genblk1[3].g_val_reg0_carry_i_11_n_0 ),
        .I1(cy_q[5]),
        .I2(py_q[29]),
        .I3(\genblk1[3].g_val_reg0_carry_i_27_n_0 ),
        .O(\genblk1[3].g_val_reg0_carry_i_18_n_0 ));
  LUT6 #(
    .INIT(64'h9969696666969699)) 
    \genblk1[3].g_val_reg0_carry_i_19 
       (.I0(cy_q[6]),
        .I1(py_q[30]),
        .I2(py_q[29]),
        .I3(cy_q[5]),
        .I4(\genblk1[3].g_val_reg0_carry_i_27_n_0 ),
        .I5(\genblk1[3].g_val_reg0_carry_i_14_n_0 ),
        .O(\genblk1[3].g_val_reg0_carry_i_19_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0_carry_i_2 
       (.I0(py_q[24]),
        .I1(cy_q[0]),
        .O(\genblk1[3].g_val_reg0_carry_i_2_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[3].g_val_reg0_carry_i_20 
       (.I0(cy_q[5]),
        .I1(py_q[29]),
        .I2(\genblk1[3].g_val_reg0_carry_i_27_n_0 ),
        .I3(\genblk1[3].g_val_reg0_carry_i_15_n_0 ),
        .O(\genblk1[3].g_val_reg0_carry_i_20_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0_carry_i_21 
       (.I0(\genblk1[3].g_val_reg0_carry_i_14_n_0 ),
        .I1(\genblk1[3].g_val_reg0_carry_i_16_n_0 ),
        .O(\genblk1[3].g_val_reg0_carry_i_21_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[3].g_val_reg0_carry_i_22 
       (.I0(\genblk1[3].g_val_reg0_carry_i_15_n_0 ),
        .I1(cy_q[1]),
        .I2(py_q[25]),
        .I3(cy_q[0]),
        .I4(py_q[24]),
        .O(\genblk1[3].g_val_reg0_carry_i_22_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[3].g_val_reg0_carry_i_23 
       (.I0(cy_q[2]),
        .I1(py_q[26]),
        .I2(py_q[25]),
        .I3(cy_q[1]),
        .I4(py_q[24]),
        .I5(cy_q[0]),
        .O(\genblk1[3].g_val_reg0_carry_i_23_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[3].g_val_reg0_carry_i_24 
       (.I0(py_q[24]),
        .I1(cy_q[0]),
        .I2(py_q[25]),
        .I3(cy_q[1]),
        .O(\genblk1[3].g_val_reg0_carry_i_24_n_0 ));
  LUT6 #(
    .INIT(64'h2B22BBBB22222B22)) 
    \genblk1[3].g_val_reg0_carry_i_25 
       (.I0(pz_q[11]),
        .I1(cz_q[2]),
        .I2(cz_q[0]),
        .I3(pz_q[9]),
        .I4(cz_q[1]),
        .I5(pz_q[10]),
        .O(\genblk1[3].g_val_reg0_carry_i_25_n_0 ));
  (* OPT_MODIFIED = "RETARGET PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[3].g_val_reg0_carry_i_26 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[3].g_val_reg0_carry_i_26_CO_UNCONNECTED [7:5],\genblk1[3].g_val_reg1 [6],\NLW_genblk1[3].g_val_reg0_carry_i_26_CO_UNCONNECTED [3:0]}),
        .DI({\NLW_genblk1[3].g_val_reg0_carry_i_26_DI_UNCONNECTED [7:5],1'b0,\genblk1[3].g_val_reg0_carry_i_25_n_0 ,\genblk1[3].g_val_reg0_carry_i_25_n_0 ,\genblk1[3].g_val_reg0_carry_i_29_n_0 ,1'b0}),
        .O({\NLW_genblk1[3].g_val_reg0_carry_i_26_O_UNCONNECTED [7:4],\genblk1[3].g_val_reg1 [5:2]}),
        .S({\NLW_genblk1[3].g_val_reg0_carry_i_26_S_UNCONNECTED [7:5],1'b1,\genblk1[3].g_val_reg0_carry_i_30_n_0 ,\genblk1[3].g_val_reg0_carry_i_31_n_0 ,\genblk1[3].g_val_reg0_carry_i_9_0 }));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[3].g_val_reg0_carry_i_27 
       (.I0(py_q[28]),
        .I1(cy_q[4]),
        .I2(\genblk1[3].g_val_reg0_carry_i_28_n_0 ),
        .I3(cy_q[3]),
        .I4(py_q[27]),
        .O(\genblk1[3].g_val_reg0_carry_i_27_n_0 ));
  LUT6 #(
    .INIT(64'hD4DD4444DDDDD4DD)) 
    \genblk1[3].g_val_reg0_carry_i_28 
       (.I0(py_q[26]),
        .I1(cy_q[2]),
        .I2(cy_q[0]),
        .I3(py_q[24]),
        .I4(cy_q[1]),
        .I5(py_q[25]),
        .O(\genblk1[3].g_val_reg0_carry_i_28_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[3].g_val_reg0_carry_i_29 
       (.I0(cz_q[0]),
        .I1(pz_q[9]),
        .I2(cz_q[1]),
        .I3(pz_q[10]),
        .I4(pz_q[11]),
        .I5(cz_q[2]),
        .O(\genblk1[3].g_val_reg0_carry_i_29_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0_carry_i_3 
       (.I0(\genblk1[3].g_val_reg2__1 [8]),
        .I1(\genblk1[3].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[3].g_val_reg0_carry_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0_carry_i_30 
       (.I0(\genblk1[3].g_val_reg0_carry_i_25_n_0 ),
        .I1(\genblk1[3].g_val_reg0_carry_i_29_n_0 ),
        .O(\genblk1[3].g_val_reg0_carry_i_30_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[3].g_val_reg0_carry_i_31 
       (.I0(\genblk1[3].g_val_reg0_carry_i_25_n_0 ),
        .I1(cz_q[1]),
        .I2(pz_q[10]),
        .I3(cz_q[0]),
        .I4(pz_q[9]),
        .O(\genblk1[3].g_val_reg0_carry_i_31_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0_carry_i_4 
       (.I0(\genblk1[3].g_val_reg2__1 [7]),
        .I1(\genblk1[3].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[3].g_val_reg0_carry_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0_carry_i_5 
       (.I0(\genblk1[3].g_val_reg2__1 [6]),
        .I1(\genblk1[3].g_val_reg1 [6]),
        .O(\genblk1[3].g_val_reg0_carry_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0_carry_i_6 
       (.I0(\genblk1[3].g_val_reg2__1 [5]),
        .I1(\genblk1[3].g_val_reg1 [5]),
        .O(\genblk1[3].g_val_reg0_carry_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0_carry_i_7 
       (.I0(\genblk1[3].g_val_reg2__1 [4]),
        .I1(\genblk1[3].g_val_reg1 [4]),
        .O(\genblk1[3].g_val_reg0_carry_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0_carry_i_8 
       (.I0(\genblk1[3].g_val_reg2__1 [3]),
        .I1(\genblk1[3].g_val_reg1 [3]),
        .O(\genblk1[3].g_val_reg0_carry_i_8_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].g_val_reg0_carry_i_9 
       (.I0(\genblk1[3].g_val_reg2__1 [2]),
        .I1(\genblk1[3].g_val_reg1 [2]),
        .O(\genblk1[3].g_val_reg0_carry_i_9_n_0 ));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[3].g_val_reg0_inferred__0/i__carry 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[3].g_val_reg0_inferred__0/i__carry_n_0 ,\NLW_genblk1[3].g_val_reg0_inferred__0/i__carry_CO_UNCONNECTED [6:0]}),
        .DI(cg_q[8:1]),
        .O(\genblk1[3].g_val_reg0 [8:1]),
        .S({i__carry_i_1__3_n_0,i__carry_i_2__2_n_0,i__carry_i_3__2_n_0,i__carry_i_4__2_n_0,i__carry_i_5__2_n_0,i__carry_i_6__2_n_0,i__carry_i_7__2_n_0,i__carry_i_8__2_n_0}));
  (* ADDER_THRESHOLD = "35" *) 
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[3].g_val_reg0_inferred__0/i__carry__0 
       (.CI(\genblk1[3].g_val_reg0_inferred__0/i__carry_n_0 ),
        .CI_TOP(1'b0),
        .CO(\NLW_genblk1[3].g_val_reg0_inferred__0/i__carry__0_CO_UNCONNECTED [7:0]),
        .DI({\NLW_genblk1[3].g_val_reg0_inferred__0/i__carry__0_DI_UNCONNECTED [7:5],1'b0,cg_q[12:9]}),
        .O({\NLW_genblk1[3].g_val_reg0_inferred__0/i__carry__0_O_UNCONNECTED [7:5],\genblk1[3].g_val_reg0 [13:9]}),
        .S({\NLW_genblk1[3].g_val_reg0_inferred__0/i__carry__0_S_UNCONNECTED [7:5],i__carry__0_i_1__2_n_0,i__carry__0_i_2__2_n_0,i__carry__0_i_3__2_n_0,i__carry__0_i_4__2_n_0,i__carry__0_i_5__2_n_0}));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].g_val_reg[43] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].g_val_reg0 [1]),
        .Q(g[39]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].g_val_reg[44] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].g_val_reg0 [2]),
        .Q(g[40]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].g_val_reg[45] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].g_val_reg0 [3]),
        .Q(g[41]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].g_val_reg[46] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].g_val_reg0 [4]),
        .Q(g[42]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].g_val_reg[47] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].g_val_reg0 [5]),
        .Q(g[43]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].g_val_reg[48] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].g_val_reg0 [6]),
        .Q(g[44]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].g_val_reg[49] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].g_val_reg0 [7]),
        .Q(g[45]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].g_val_reg[50] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].g_val_reg0 [8]),
        .Q(g[46]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].g_val_reg[51] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].g_val_reg0 [9]),
        .Q(g[47]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].g_val_reg[52] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].g_val_reg0 [10]),
        .Q(g[48]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].g_val_reg[53] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].g_val_reg0 [11]),
        .Q(g[49]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].g_val_reg[54] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].g_val_reg0 [12]),
        .Q(g[50]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].g_val_reg[55] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].g_val_reg0 [13]),
        .Q(g[51]),
        .R(reset_q));
  (* SOFT_HLUTNM = "soft_lutpair5" *) 
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].h_val_x_reg[43]_i_1 
       (.I0(px_q[24]),
        .I1(ex_q[0]),
        .O(\genblk1[3].h_val_x_reg[43]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h9969696666969699)) 
    \genblk1[3].h_val_x_reg[51]_i_10 
       (.I0(ex_q[6]),
        .I1(px_q[30]),
        .I2(px_q[29]),
        .I3(ex_q[5]),
        .I4(\genblk1[3].h_val_x_reg[55]_i_3_n_0 ),
        .I5(\genblk1[3].h_val_x_reg[51]_i_5_n_0 ),
        .O(\genblk1[3].h_val_x_reg[51]_i_10_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[3].h_val_x_reg[51]_i_11 
       (.I0(ex_q[5]),
        .I1(px_q[29]),
        .I2(\genblk1[3].h_val_x_reg[55]_i_3_n_0 ),
        .I3(\genblk1[3].h_val_x_reg[51]_i_6_n_0 ),
        .O(\genblk1[3].h_val_x_reg[51]_i_11_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].h_val_x_reg[51]_i_12 
       (.I0(\genblk1[3].h_val_x_reg[51]_i_5_n_0 ),
        .I1(\genblk1[3].h_val_x_reg[51]_i_7_n_0 ),
        .O(\genblk1[3].h_val_x_reg[51]_i_12_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[3].h_val_x_reg[51]_i_13 
       (.I0(\genblk1[3].h_val_x_reg[51]_i_6_n_0 ),
        .I1(ex_q[1]),
        .I2(px_q[25]),
        .I3(ex_q[0]),
        .I4(px_q[24]),
        .O(\genblk1[3].h_val_x_reg[51]_i_13_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[3].h_val_x_reg[51]_i_14 
       (.I0(ex_q[2]),
        .I1(px_q[26]),
        .I2(px_q[25]),
        .I3(ex_q[1]),
        .I4(px_q[24]),
        .I5(ex_q[0]),
        .O(\genblk1[3].h_val_x_reg[51]_i_14_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[3].h_val_x_reg[51]_i_15 
       (.I0(px_q[24]),
        .I1(ex_q[0]),
        .I2(px_q[25]),
        .I3(ex_q[1]),
        .O(\genblk1[3].h_val_x_reg[51]_i_15_n_0 ));
  LUT6 #(
    .INIT(64'hD4DD4444DDDDD4DD)) 
    \genblk1[3].h_val_x_reg[51]_i_16 
       (.I0(px_q[26]),
        .I1(ex_q[2]),
        .I2(ex_q[0]),
        .I3(px_q[24]),
        .I4(ex_q[1]),
        .I5(px_q[25]),
        .O(\genblk1[3].h_val_x_reg[51]_i_16_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[3].h_val_x_reg[51]_i_2 
       (.I0(\genblk1[3].h_val_x_reg[55]_i_2_n_0 ),
        .I1(px_q[31]),
        .I2(ex_q[7]),
        .O(\genblk1[3].h_val_x_reg[51]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[3].h_val_x_reg[51]_i_3 
       (.I0(\genblk1[3].h_val_x_reg[55]_i_3_n_0 ),
        .I1(ex_q[5]),
        .I2(px_q[29]),
        .I3(px_q[30]),
        .I4(ex_q[6]),
        .O(\genblk1[3].h_val_x_reg[51]_i_3_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[3].h_val_x_reg[51]_i_4 
       (.I0(\genblk1[3].h_val_x_reg[55]_i_3_n_0 ),
        .I1(px_q[29]),
        .I2(ex_q[5]),
        .O(\genblk1[3].h_val_x_reg[51]_i_4_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[3].h_val_x_reg[51]_i_5 
       (.I0(\genblk1[3].h_val_x_reg[51]_i_16_n_0 ),
        .I1(ex_q[3]),
        .I2(px_q[27]),
        .I3(px_q[28]),
        .I4(ex_q[4]),
        .O(\genblk1[3].h_val_x_reg[51]_i_5_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[3].h_val_x_reg[51]_i_6 
       (.I0(\genblk1[3].h_val_x_reg[51]_i_16_n_0 ),
        .I1(px_q[27]),
        .I2(ex_q[3]),
        .O(\genblk1[3].h_val_x_reg[51]_i_6_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[3].h_val_x_reg[51]_i_7 
       (.I0(ex_q[0]),
        .I1(px_q[24]),
        .I2(ex_q[1]),
        .I3(px_q[25]),
        .I4(px_q[26]),
        .I5(ex_q[2]),
        .O(\genblk1[3].h_val_x_reg[51]_i_7_n_0 ));
  LUT6 #(
    .INIT(64'h9696699669966969)) 
    \genblk1[3].h_val_x_reg[51]_i_8 
       (.I0(\genblk1[3].h_val_x_reg[55]_i_1_n_0 ),
        .I1(ex_q[6]),
        .I2(px_q[30]),
        .I3(px_q[29]),
        .I4(ex_q[5]),
        .I5(\genblk1[3].h_val_x_reg[55]_i_3_n_0 ),
        .O(\genblk1[3].h_val_x_reg[51]_i_8_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[3].h_val_x_reg[51]_i_9 
       (.I0(\genblk1[3].h_val_x_reg[51]_i_2_n_0 ),
        .I1(ex_q[5]),
        .I2(px_q[29]),
        .I3(\genblk1[3].h_val_x_reg[55]_i_3_n_0 ),
        .O(\genblk1[3].h_val_x_reg[51]_i_9_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].h_val_x_reg[53]_i_2 
       (.I0(\genblk1[3].h_val_x_reg[55]_i_1_n_0 ),
        .I1(\genblk1[3].h_val_x_reg[51]_i_2_n_0 ),
        .O(\genblk1[3].h_val_x_reg[53]_i_2_n_0 ));
  LUT3 #(
    .INIT(8'h2B)) 
    \genblk1[3].h_val_x_reg[55]_i_1 
       (.I0(px_q[31]),
        .I1(ex_q[7]),
        .I2(\genblk1[3].h_val_x_reg[55]_i_2_n_0 ),
        .O(\genblk1[3].h_val_x_reg[55]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[3].h_val_x_reg[55]_i_2 
       (.I0(px_q[30]),
        .I1(ex_q[6]),
        .I2(\genblk1[3].h_val_x_reg[55]_i_3_n_0 ),
        .I3(ex_q[5]),
        .I4(px_q[29]),
        .O(\genblk1[3].h_val_x_reg[55]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[3].h_val_x_reg[55]_i_3 
       (.I0(px_q[28]),
        .I1(ex_q[4]),
        .I2(\genblk1[3].h_val_x_reg[51]_i_16_n_0 ),
        .I3(ex_q[3]),
        .I4(px_q[27]),
        .O(\genblk1[3].h_val_x_reg[55]_i_3_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_x_reg_reg[43] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_x_reg[43]_i_1_n_0 ),
        .Q(\genblk1[3].h_val_x_reg_reg_n_0_[43] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_x_reg_reg[44] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_x_reg_reg0 [2]),
        .Q(\genblk1[3].h_val_x_reg_reg_n_0_[44] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_x_reg_reg[45] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_x_reg_reg0 [3]),
        .Q(\genblk1[3].h_val_x_reg_reg_n_0_[45] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_x_reg_reg[46] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_x_reg_reg0 [4]),
        .Q(\genblk1[3].h_val_x_reg_reg_n_0_[46] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_x_reg_reg[47] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_x_reg_reg0 [5]),
        .Q(\genblk1[3].h_val_x_reg_reg_n_0_[47] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_x_reg_reg[48] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_x_reg_reg0 [6]),
        .Q(\genblk1[3].h_val_x_reg_reg_n_0_[48] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_x_reg_reg[49] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_x_reg_reg0 [7]),
        .Q(\genblk1[3].h_val_x_reg_reg_n_0_[49] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_x_reg_reg[50] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_x_reg_reg0 [8]),
        .Q(\genblk1[3].h_val_x_reg_reg_n_0_[50] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_x_reg_reg[51] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_x_reg_reg0 [9]),
        .Q(\genblk1[3].h_val_x_reg_reg_n_0_[51] ),
        .R(reset_q));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[3].h_val_x_reg_reg[51]_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[3].h_val_x_reg_reg[51]_i_1_n_0 ,\NLW_genblk1[3].h_val_x_reg_reg[51]_i_1_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[3].h_val_x_reg[55]_i_1_n_0 ,\genblk1[3].h_val_x_reg[51]_i_2_n_0 ,\genblk1[3].h_val_x_reg[51]_i_3_n_0 ,\genblk1[3].h_val_x_reg[51]_i_4_n_0 ,\genblk1[3].h_val_x_reg[51]_i_5_n_0 ,\genblk1[3].h_val_x_reg[51]_i_6_n_0 ,\genblk1[3].h_val_x_reg[51]_i_7_n_0 ,1'b0}),
        .O(\genblk1[3].h_val_x_reg_reg0 [9:2]),
        .S({\genblk1[3].h_val_x_reg[51]_i_8_n_0 ,\genblk1[3].h_val_x_reg[51]_i_9_n_0 ,\genblk1[3].h_val_x_reg[51]_i_10_n_0 ,\genblk1[3].h_val_x_reg[51]_i_11_n_0 ,\genblk1[3].h_val_x_reg[51]_i_12_n_0 ,\genblk1[3].h_val_x_reg[51]_i_13_n_0 ,\genblk1[3].h_val_x_reg[51]_i_14_n_0 ,\genblk1[3].h_val_x_reg[51]_i_15_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_x_reg_reg[52] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_x_reg_reg0 [10]),
        .Q(\genblk1[3].h_val_x_reg_reg_n_0_[52] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_x_reg_reg[53] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_x_reg_reg0 [11]),
        .Q(\genblk1[3].h_val_x_reg_reg_n_0_[53] ),
        .R(reset_q));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[3].h_val_x_reg_reg[53]_i_1 
       (.CI(\genblk1[3].h_val_x_reg_reg[51]_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[3].h_val_x_reg_reg[53]_i_1_CO_UNCONNECTED [7:2],\genblk1[3].h_val_x_reg_reg0 [11],\NLW_genblk1[3].h_val_x_reg_reg[53]_i_1_CO_UNCONNECTED [0]}),
        .DI({\NLW_genblk1[3].h_val_x_reg_reg[53]_i_1_DI_UNCONNECTED [7:2],1'b0,\genblk1[3].h_val_x_reg[55]_i_1_n_0 }),
        .O({\NLW_genblk1[3].h_val_x_reg_reg[53]_i_1_O_UNCONNECTED [7:1],\genblk1[3].h_val_x_reg_reg0 [10]}),
        .S({\NLW_genblk1[3].h_val_x_reg_reg[53]_i_1_S_UNCONNECTED [7:2],1'b1,\genblk1[3].h_val_x_reg[53]_i_2_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_x_reg_reg[55] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_x_reg[55]_i_1_n_0 ),
        .Q(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .R(reset_q));
  (* SOFT_HLUTNM = "soft_lutpair4" *) 
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].h_val_y_reg[43]_i_1 
       (.I0(py_q[24]),
        .I1(ey_q[0]),
        .O(\genblk1[3].h_val_y_reg[43]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h9969696666969699)) 
    \genblk1[3].h_val_y_reg[51]_i_10 
       (.I0(ey_q[6]),
        .I1(py_q[30]),
        .I2(py_q[29]),
        .I3(ey_q[5]),
        .I4(\genblk1[3].h_val_y_reg[55]_i_3_n_0 ),
        .I5(\genblk1[3].h_val_y_reg[51]_i_5_n_0 ),
        .O(\genblk1[3].h_val_y_reg[51]_i_10_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[3].h_val_y_reg[51]_i_11 
       (.I0(ey_q[5]),
        .I1(py_q[29]),
        .I2(\genblk1[3].h_val_y_reg[55]_i_3_n_0 ),
        .I3(\genblk1[3].h_val_y_reg[51]_i_6_n_0 ),
        .O(\genblk1[3].h_val_y_reg[51]_i_11_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].h_val_y_reg[51]_i_12 
       (.I0(\genblk1[3].h_val_y_reg[51]_i_5_n_0 ),
        .I1(\genblk1[3].h_val_y_reg[51]_i_7_n_0 ),
        .O(\genblk1[3].h_val_y_reg[51]_i_12_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[3].h_val_y_reg[51]_i_13 
       (.I0(\genblk1[3].h_val_y_reg[51]_i_6_n_0 ),
        .I1(ey_q[1]),
        .I2(py_q[25]),
        .I3(ey_q[0]),
        .I4(py_q[24]),
        .O(\genblk1[3].h_val_y_reg[51]_i_13_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[3].h_val_y_reg[51]_i_14 
       (.I0(ey_q[2]),
        .I1(py_q[26]),
        .I2(py_q[25]),
        .I3(ey_q[1]),
        .I4(py_q[24]),
        .I5(ey_q[0]),
        .O(\genblk1[3].h_val_y_reg[51]_i_14_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[3].h_val_y_reg[51]_i_15 
       (.I0(py_q[24]),
        .I1(ey_q[0]),
        .I2(py_q[25]),
        .I3(ey_q[1]),
        .O(\genblk1[3].h_val_y_reg[51]_i_15_n_0 ));
  LUT6 #(
    .INIT(64'hD4DD4444DDDDD4DD)) 
    \genblk1[3].h_val_y_reg[51]_i_16 
       (.I0(py_q[26]),
        .I1(ey_q[2]),
        .I2(ey_q[0]),
        .I3(py_q[24]),
        .I4(ey_q[1]),
        .I5(py_q[25]),
        .O(\genblk1[3].h_val_y_reg[51]_i_16_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[3].h_val_y_reg[51]_i_2 
       (.I0(\genblk1[3].h_val_y_reg[55]_i_2_n_0 ),
        .I1(py_q[31]),
        .I2(ey_q[7]),
        .O(\genblk1[3].h_val_y_reg[51]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[3].h_val_y_reg[51]_i_3 
       (.I0(\genblk1[3].h_val_y_reg[55]_i_3_n_0 ),
        .I1(ey_q[5]),
        .I2(py_q[29]),
        .I3(py_q[30]),
        .I4(ey_q[6]),
        .O(\genblk1[3].h_val_y_reg[51]_i_3_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[3].h_val_y_reg[51]_i_4 
       (.I0(\genblk1[3].h_val_y_reg[55]_i_3_n_0 ),
        .I1(py_q[29]),
        .I2(ey_q[5]),
        .O(\genblk1[3].h_val_y_reg[51]_i_4_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[3].h_val_y_reg[51]_i_5 
       (.I0(\genblk1[3].h_val_y_reg[51]_i_16_n_0 ),
        .I1(ey_q[3]),
        .I2(py_q[27]),
        .I3(py_q[28]),
        .I4(ey_q[4]),
        .O(\genblk1[3].h_val_y_reg[51]_i_5_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[3].h_val_y_reg[51]_i_6 
       (.I0(\genblk1[3].h_val_y_reg[51]_i_16_n_0 ),
        .I1(py_q[27]),
        .I2(ey_q[3]),
        .O(\genblk1[3].h_val_y_reg[51]_i_6_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[3].h_val_y_reg[51]_i_7 
       (.I0(ey_q[0]),
        .I1(py_q[24]),
        .I2(ey_q[1]),
        .I3(py_q[25]),
        .I4(py_q[26]),
        .I5(ey_q[2]),
        .O(\genblk1[3].h_val_y_reg[51]_i_7_n_0 ));
  LUT6 #(
    .INIT(64'h9696699669966969)) 
    \genblk1[3].h_val_y_reg[51]_i_8 
       (.I0(\genblk1[3].h_val_y_reg[55]_i_1_n_0 ),
        .I1(ey_q[6]),
        .I2(py_q[30]),
        .I3(py_q[29]),
        .I4(ey_q[5]),
        .I5(\genblk1[3].h_val_y_reg[55]_i_3_n_0 ),
        .O(\genblk1[3].h_val_y_reg[51]_i_8_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[3].h_val_y_reg[51]_i_9 
       (.I0(\genblk1[3].h_val_y_reg[51]_i_2_n_0 ),
        .I1(ey_q[5]),
        .I2(py_q[29]),
        .I3(\genblk1[3].h_val_y_reg[55]_i_3_n_0 ),
        .O(\genblk1[3].h_val_y_reg[51]_i_9_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].h_val_y_reg[53]_i_2 
       (.I0(\genblk1[3].h_val_y_reg[55]_i_1_n_0 ),
        .I1(\genblk1[3].h_val_y_reg[51]_i_2_n_0 ),
        .O(\genblk1[3].h_val_y_reg[53]_i_2_n_0 ));
  LUT3 #(
    .INIT(8'h2B)) 
    \genblk1[3].h_val_y_reg[55]_i_1 
       (.I0(py_q[31]),
        .I1(ey_q[7]),
        .I2(\genblk1[3].h_val_y_reg[55]_i_2_n_0 ),
        .O(\genblk1[3].h_val_y_reg[55]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[3].h_val_y_reg[55]_i_2 
       (.I0(py_q[30]),
        .I1(ey_q[6]),
        .I2(\genblk1[3].h_val_y_reg[55]_i_3_n_0 ),
        .I3(ey_q[5]),
        .I4(py_q[29]),
        .O(\genblk1[3].h_val_y_reg[55]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[3].h_val_y_reg[55]_i_3 
       (.I0(py_q[28]),
        .I1(ey_q[4]),
        .I2(\genblk1[3].h_val_y_reg[51]_i_16_n_0 ),
        .I3(ey_q[3]),
        .I4(py_q[27]),
        .O(\genblk1[3].h_val_y_reg[55]_i_3_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_y_reg_reg[43] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_y_reg[43]_i_1_n_0 ),
        .Q(\genblk1[3].h_val_y_reg_reg_n_0_[43] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_y_reg_reg[44] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_y_reg_reg0 [2]),
        .Q(\genblk1[3].h_val_y_reg_reg_n_0_[44] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_y_reg_reg[45] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_y_reg_reg0 [3]),
        .Q(\genblk1[3].h_val_y_reg_reg_n_0_[45] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_y_reg_reg[46] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_y_reg_reg0 [4]),
        .Q(\genblk1[3].h_val_y_reg_reg_n_0_[46] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_y_reg_reg[47] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_y_reg_reg0 [5]),
        .Q(\genblk1[3].h_val_y_reg_reg_n_0_[47] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_y_reg_reg[48] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_y_reg_reg0 [6]),
        .Q(\genblk1[3].h_val_y_reg_reg_n_0_[48] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_y_reg_reg[49] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_y_reg_reg0 [7]),
        .Q(\genblk1[3].h_val_y_reg_reg_n_0_[49] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_y_reg_reg[50] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_y_reg_reg0 [8]),
        .Q(\genblk1[3].h_val_y_reg_reg_n_0_[50] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_y_reg_reg[51] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_y_reg_reg0 [9]),
        .Q(\genblk1[3].h_val_y_reg_reg_n_0_[51] ),
        .R(reset_q));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[3].h_val_y_reg_reg[51]_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[3].h_val_y_reg_reg[51]_i_1_n_0 ,\NLW_genblk1[3].h_val_y_reg_reg[51]_i_1_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[3].h_val_y_reg[55]_i_1_n_0 ,\genblk1[3].h_val_y_reg[51]_i_2_n_0 ,\genblk1[3].h_val_y_reg[51]_i_3_n_0 ,\genblk1[3].h_val_y_reg[51]_i_4_n_0 ,\genblk1[3].h_val_y_reg[51]_i_5_n_0 ,\genblk1[3].h_val_y_reg[51]_i_6_n_0 ,\genblk1[3].h_val_y_reg[51]_i_7_n_0 ,1'b0}),
        .O(\genblk1[3].h_val_y_reg_reg0 [9:2]),
        .S({\genblk1[3].h_val_y_reg[51]_i_8_n_0 ,\genblk1[3].h_val_y_reg[51]_i_9_n_0 ,\genblk1[3].h_val_y_reg[51]_i_10_n_0 ,\genblk1[3].h_val_y_reg[51]_i_11_n_0 ,\genblk1[3].h_val_y_reg[51]_i_12_n_0 ,\genblk1[3].h_val_y_reg[51]_i_13_n_0 ,\genblk1[3].h_val_y_reg[51]_i_14_n_0 ,\genblk1[3].h_val_y_reg[51]_i_15_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_y_reg_reg[52] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_y_reg_reg0 [10]),
        .Q(\genblk1[3].h_val_y_reg_reg_n_0_[52] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_y_reg_reg[53] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_y_reg_reg0 [11]),
        .Q(\genblk1[3].h_val_y_reg_reg_n_0_[53] ),
        .R(reset_q));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[3].h_val_y_reg_reg[53]_i_1 
       (.CI(\genblk1[3].h_val_y_reg_reg[51]_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[3].h_val_y_reg_reg[53]_i_1_CO_UNCONNECTED [7:2],\genblk1[3].h_val_y_reg_reg0 [11],\NLW_genblk1[3].h_val_y_reg_reg[53]_i_1_CO_UNCONNECTED [0]}),
        .DI({\NLW_genblk1[3].h_val_y_reg_reg[53]_i_1_DI_UNCONNECTED [7:2],1'b0,\genblk1[3].h_val_y_reg[55]_i_1_n_0 }),
        .O({\NLW_genblk1[3].h_val_y_reg_reg[53]_i_1_O_UNCONNECTED [7:1],\genblk1[3].h_val_y_reg_reg0 [10]}),
        .S({\NLW_genblk1[3].h_val_y_reg_reg[53]_i_1_S_UNCONNECTED [7:2],1'b1,\genblk1[3].h_val_y_reg[53]_i_2_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_y_reg_reg[55] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_y_reg[55]_i_1_n_0 ),
        .Q(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .R(reset_q));
  (* SOFT_HLUTNM = "soft_lutpair3" *) 
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].h_val_z_reg[43]_i_1 
       (.I0(pz_q[9]),
        .I1(ez_q[0]),
        .O(\genblk1[3].h_val_z_reg[43]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[3].h_val_z_reg[48]_i_2 
       (.I0(ez_q[0]),
        .I1(pz_q[9]),
        .I2(ez_q[1]),
        .I3(pz_q[10]),
        .I4(pz_q[11]),
        .I5(ez_q[2]),
        .O(\genblk1[3].h_val_z_reg[48]_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[3].h_val_z_reg[48]_i_3 
       (.I0(\genblk1[3].h_val_z_reg[55]_i_1_n_0 ),
        .I1(\genblk1[3].h_val_z_reg[48]_i_2_n_0 ),
        .O(\genblk1[3].h_val_z_reg[48]_i_3_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[3].h_val_z_reg[48]_i_4 
       (.I0(\genblk1[3].h_val_z_reg[55]_i_1_n_0 ),
        .I1(ez_q[1]),
        .I2(pz_q[10]),
        .I3(ez_q[0]),
        .I4(pz_q[9]),
        .O(\genblk1[3].h_val_z_reg[48]_i_4_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[3].h_val_z_reg[48]_i_5 
       (.I0(ez_q[2]),
        .I1(pz_q[11]),
        .I2(pz_q[10]),
        .I3(ez_q[1]),
        .I4(pz_q[9]),
        .I5(ez_q[0]),
        .O(\genblk1[3].h_val_z_reg[48]_i_5_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[3].h_val_z_reg[48]_i_6 
       (.I0(pz_q[9]),
        .I1(ez_q[0]),
        .I2(pz_q[10]),
        .I3(ez_q[1]),
        .O(\genblk1[3].h_val_z_reg[48]_i_6_n_0 ));
  LUT6 #(
    .INIT(64'h2B22BBBB22222B22)) 
    \genblk1[3].h_val_z_reg[55]_i_1 
       (.I0(pz_q[11]),
        .I1(ez_q[2]),
        .I2(ez_q[0]),
        .I3(pz_q[9]),
        .I4(ez_q[1]),
        .I5(pz_q[10]),
        .O(\genblk1[3].h_val_z_reg[55]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_z_reg_reg[43] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_z_reg[43]_i_1_n_0 ),
        .Q(\genblk1[3].h_val_z_reg_reg_n_0_[43] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_z_reg_reg[44] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_z_reg_reg0 [2]),
        .Q(\genblk1[3].h_val_z_reg_reg_n_0_[44] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_z_reg_reg[45] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_z_reg_reg0 [3]),
        .Q(\genblk1[3].h_val_z_reg_reg_n_0_[45] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_z_reg_reg[46] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_z_reg_reg0 [4]),
        .Q(\genblk1[3].h_val_z_reg_reg_n_0_[46] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_z_reg_reg[47] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_z_reg_reg0 [5]),
        .Q(\genblk1[3].h_val_z_reg_reg_n_0_[47] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_z_reg_reg[48] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_z_reg_reg0 [6]),
        .Q(\genblk1[3].h_val_z_reg_reg_n_0_[48] ),
        .R(reset_q));
  (* OPT_MODIFIED = "RETARGET PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[3].h_val_z_reg_reg[48]_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[3].h_val_z_reg_reg[48]_i_1_CO_UNCONNECTED [7:5],\genblk1[3].h_val_z_reg_reg0 [6],\NLW_genblk1[3].h_val_z_reg_reg[48]_i_1_CO_UNCONNECTED [3:0]}),
        .DI({\NLW_genblk1[3].h_val_z_reg_reg[48]_i_1_DI_UNCONNECTED [7:5],1'b0,\genblk1[3].h_val_z_reg[55]_i_1_n_0 ,\genblk1[3].h_val_z_reg[55]_i_1_n_0 ,\genblk1[3].h_val_z_reg[48]_i_2_n_0 ,1'b0}),
        .O({\NLW_genblk1[3].h_val_z_reg_reg[48]_i_1_O_UNCONNECTED [7:4],\genblk1[3].h_val_z_reg_reg0 [5:2]}),
        .S({\NLW_genblk1[3].h_val_z_reg_reg[48]_i_1_S_UNCONNECTED [7:5],1'b1,\genblk1[3].h_val_z_reg[48]_i_3_n_0 ,\genblk1[3].h_val_z_reg[48]_i_4_n_0 ,\genblk1[3].h_val_z_reg[48]_i_5_n_0 ,\genblk1[3].h_val_z_reg[48]_i_6_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[3].h_val_z_reg_reg[55] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[3].h_val_z_reg[55]_i_1_n_0 ),
        .Q(\genblk1[3].h_val_z_reg_reg_n_0_[55] ),
        .R(reset_q));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[4].g_val_reg0__36_carry 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[4].g_val_reg0__36_carry_n_0 ,\NLW_genblk1[4].g_val_reg0__36_carry_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[4].g_val_reg3__6 [8:2],C__3[1]}),
        .O({\genblk1[4].g_val_reg0__36_carry_n_8 ,\genblk1[4].g_val_reg0__36_carry_n_9 ,\genblk1[4].g_val_reg0__36_carry_n_10 ,\genblk1[4].g_val_reg0__36_carry_n_11 ,\genblk1[4].g_val_reg0__36_carry_n_12 ,\genblk1[4].g_val_reg0__36_carry_n_13 ,\genblk1[4].g_val_reg0__36_carry_n_14 ,\genblk1[4].g_val_reg0__36_carry_n_15 }),
        .S({\genblk1[4].g_val_reg0__36_carry_i_2_n_0 ,\genblk1[4].g_val_reg0__36_carry_i_3_n_0 ,\genblk1[4].g_val_reg0__36_carry_i_4_n_0 ,\genblk1[4].g_val_reg0__36_carry_i_5_n_0 ,\genblk1[4].g_val_reg0__36_carry_i_6_n_0 ,\genblk1[4].g_val_reg0__36_carry_i_7_n_0 ,\genblk1[4].g_val_reg0__36_carry_i_8_n_0 ,\genblk1[4].g_val_reg0__36_carry_i_9_n_0 }));
  (* ADDER_THRESHOLD = "35" *) 
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[4].g_val_reg0__36_carry__0 
       (.CI(\genblk1[4].g_val_reg0__36_carry_n_0 ),
        .CI_TOP(1'b0),
        .CO(\NLW_genblk1[4].g_val_reg0__36_carry__0_CO_UNCONNECTED [7:0]),
        .DI({\NLW_genblk1[4].g_val_reg0__36_carry__0_DI_UNCONNECTED [7:5],1'b0,C__3[12],\genblk1[4].g_val_reg3__6 [11:9]}),
        .O({\NLW_genblk1[4].g_val_reg0__36_carry__0_O_UNCONNECTED [7:5],\genblk1[4].g_val_reg0__36_carry__0_n_11 ,\genblk1[4].g_val_reg0__36_carry__0_n_12 ,\genblk1[4].g_val_reg0__36_carry__0_n_13 ,\genblk1[4].g_val_reg0__36_carry__0_n_14 ,\genblk1[4].g_val_reg0__36_carry__0_n_15 }),
        .S({\NLW_genblk1[4].g_val_reg0__36_carry__0_S_UNCONNECTED [7:5],\genblk1[4].g_val_reg0__36_carry__0_i_2_n_0 ,\genblk1[4].g_val_reg0__36_carry__0_i_3_n_0 ,\genblk1[4].g_val_reg0__36_carry__0_i_4_n_0 ,\genblk1[4].g_val_reg0__36_carry__0_i_5_n_0 ,\genblk1[4].g_val_reg0__36_carry__0_i_6_n_0 }));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[4].g_val_reg0__36_carry__0_i_1 
       (.CI(\genblk1[4].g_val_reg0__36_carry_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[4].g_val_reg0__36_carry__0_i_1_CO_UNCONNECTED [7:2],\genblk1[4].g_val_reg3__6 [11],\NLW_genblk1[4].g_val_reg0__36_carry__0_i_1_CO_UNCONNECTED [0]}),
        .DI({\NLW_genblk1[4].g_val_reg0__36_carry__0_i_1_DI_UNCONNECTED [7:2],1'b0,\genblk1[4].g_val_reg0__36_carry_i_10_n_0 }),
        .O({\NLW_genblk1[4].g_val_reg0__36_carry__0_i_1_O_UNCONNECTED [7:1],\genblk1[4].g_val_reg3__6 [10]}),
        .S({\NLW_genblk1[4].g_val_reg0__36_carry__0_i_1_S_UNCONNECTED [7:2],1'b1,\genblk1[4].g_val_reg0__36_carry__0_i_7_n_0 }));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0__36_carry__0_i_2 
       (.I0(\genblk1[4].g_val_reg0__36_carry_i_10_n_0 ),
        .I1(C__3[13]),
        .O(\genblk1[4].g_val_reg0__36_carry__0_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0__36_carry__0_i_3 
       (.I0(\genblk1[4].g_val_reg0__36_carry_i_10_n_0 ),
        .I1(C__3[12]),
        .O(\genblk1[4].g_val_reg0__36_carry__0_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0__36_carry__0_i_4 
       (.I0(\genblk1[4].g_val_reg3__6 [11]),
        .I1(C__3[11]),
        .O(\genblk1[4].g_val_reg0__36_carry__0_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0__36_carry__0_i_5 
       (.I0(\genblk1[4].g_val_reg3__6 [10]),
        .I1(C__3[10]),
        .O(\genblk1[4].g_val_reg0__36_carry__0_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0__36_carry__0_i_6 
       (.I0(\genblk1[4].g_val_reg3__6 [9]),
        .I1(C__3[9]),
        .O(\genblk1[4].g_val_reg0__36_carry__0_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0__36_carry__0_i_7 
       (.I0(\genblk1[4].g_val_reg0__36_carry_i_10_n_0 ),
        .I1(\genblk1[4].g_val_reg0__36_carry_i_11_n_0 ),
        .O(\genblk1[4].g_val_reg0__36_carry__0_i_7_n_0 ));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[4].g_val_reg0__36_carry_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[4].g_val_reg0__36_carry_i_1_n_0 ,\NLW_genblk1[4].g_val_reg0__36_carry_i_1_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[4].g_val_reg0__36_carry_i_10_n_0 ,\genblk1[4].g_val_reg0__36_carry_i_11_n_0 ,\genblk1[4].g_val_reg0__36_carry_i_12_n_0 ,\genblk1[4].g_val_reg0__36_carry_i_13_n_0 ,\genblk1[4].g_val_reg0__36_carry_i_14_n_0 ,\genblk1[4].g_val_reg0__36_carry_i_15_n_0 ,\genblk1[4].g_val_reg0__36_carry_i_16_n_0 ,1'b0}),
        .O(\genblk1[4].g_val_reg3__6 [9:2]),
        .S({\genblk1[4].g_val_reg0__36_carry_i_17_n_0 ,\genblk1[4].g_val_reg0__36_carry_i_18_n_0 ,\genblk1[4].g_val_reg0__36_carry_i_19_n_0 ,\genblk1[4].g_val_reg0__36_carry_i_20_n_0 ,\genblk1[4].g_val_reg0__36_carry_i_21_n_0 ,\genblk1[4].g_val_reg0__36_carry_i_22_n_0 ,\genblk1[4].g_val_reg0__36_carry_i_23_n_0 ,\genblk1[4].g_val_reg0__36_carry_i_24_n_0 }));
  LUT3 #(
    .INIT(8'h2B)) 
    \genblk1[4].g_val_reg0__36_carry_i_10 
       (.I0(px_q[39]),
        .I1(cx_q[7]),
        .I2(\genblk1[4].g_val_reg0__36_carry_i_25_n_0 ),
        .O(\genblk1[4].g_val_reg0__36_carry_i_10_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[4].g_val_reg0__36_carry_i_11 
       (.I0(\genblk1[4].g_val_reg0__36_carry_i_25_n_0 ),
        .I1(px_q[39]),
        .I2(cx_q[7]),
        .O(\genblk1[4].g_val_reg0__36_carry_i_11_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[4].g_val_reg0__36_carry_i_12 
       (.I0(\genblk1[4].g_val_reg0__36_carry_i_26_n_0 ),
        .I1(cx_q[5]),
        .I2(px_q[37]),
        .I3(px_q[38]),
        .I4(cx_q[6]),
        .O(\genblk1[4].g_val_reg0__36_carry_i_12_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[4].g_val_reg0__36_carry_i_13 
       (.I0(\genblk1[4].g_val_reg0__36_carry_i_26_n_0 ),
        .I1(px_q[37]),
        .I2(cx_q[5]),
        .O(\genblk1[4].g_val_reg0__36_carry_i_13_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[4].g_val_reg0__36_carry_i_14 
       (.I0(\genblk1[4].g_val_reg0__36_carry_i_27_n_0 ),
        .I1(cx_q[3]),
        .I2(px_q[35]),
        .I3(px_q[36]),
        .I4(cx_q[4]),
        .O(\genblk1[4].g_val_reg0__36_carry_i_14_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[4].g_val_reg0__36_carry_i_15 
       (.I0(\genblk1[4].g_val_reg0__36_carry_i_27_n_0 ),
        .I1(px_q[35]),
        .I2(cx_q[3]),
        .O(\genblk1[4].g_val_reg0__36_carry_i_15_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[4].g_val_reg0__36_carry_i_16 
       (.I0(cx_q[0]),
        .I1(px_q[32]),
        .I2(cx_q[1]),
        .I3(px_q[33]),
        .I4(px_q[34]),
        .I5(cx_q[2]),
        .O(\genblk1[4].g_val_reg0__36_carry_i_16_n_0 ));
  LUT6 #(
    .INIT(64'h9696699669966969)) 
    \genblk1[4].g_val_reg0__36_carry_i_17 
       (.I0(\genblk1[4].g_val_reg0__36_carry_i_10_n_0 ),
        .I1(cx_q[6]),
        .I2(px_q[38]),
        .I3(px_q[37]),
        .I4(cx_q[5]),
        .I5(\genblk1[4].g_val_reg0__36_carry_i_26_n_0 ),
        .O(\genblk1[4].g_val_reg0__36_carry_i_17_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[4].g_val_reg0__36_carry_i_18 
       (.I0(\genblk1[4].g_val_reg0__36_carry_i_11_n_0 ),
        .I1(cx_q[5]),
        .I2(px_q[37]),
        .I3(\genblk1[4].g_val_reg0__36_carry_i_26_n_0 ),
        .O(\genblk1[4].g_val_reg0__36_carry_i_18_n_0 ));
  LUT6 #(
    .INIT(64'h9969696666969699)) 
    \genblk1[4].g_val_reg0__36_carry_i_19 
       (.I0(cx_q[6]),
        .I1(px_q[38]),
        .I2(px_q[37]),
        .I3(cx_q[5]),
        .I4(\genblk1[4].g_val_reg0__36_carry_i_26_n_0 ),
        .I5(\genblk1[4].g_val_reg0__36_carry_i_14_n_0 ),
        .O(\genblk1[4].g_val_reg0__36_carry_i_19_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0__36_carry_i_2 
       (.I0(\genblk1[4].g_val_reg3__6 [8]),
        .I1(C__3[8]),
        .O(\genblk1[4].g_val_reg0__36_carry_i_2_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[4].g_val_reg0__36_carry_i_20 
       (.I0(cx_q[5]),
        .I1(px_q[37]),
        .I2(\genblk1[4].g_val_reg0__36_carry_i_26_n_0 ),
        .I3(\genblk1[4].g_val_reg0__36_carry_i_15_n_0 ),
        .O(\genblk1[4].g_val_reg0__36_carry_i_20_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0__36_carry_i_21 
       (.I0(\genblk1[4].g_val_reg0__36_carry_i_14_n_0 ),
        .I1(\genblk1[4].g_val_reg0__36_carry_i_16_n_0 ),
        .O(\genblk1[4].g_val_reg0__36_carry_i_21_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[4].g_val_reg0__36_carry_i_22 
       (.I0(\genblk1[4].g_val_reg0__36_carry_i_15_n_0 ),
        .I1(cx_q[1]),
        .I2(px_q[33]),
        .I3(cx_q[0]),
        .I4(px_q[32]),
        .O(\genblk1[4].g_val_reg0__36_carry_i_22_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[4].g_val_reg0__36_carry_i_23 
       (.I0(cx_q[2]),
        .I1(px_q[34]),
        .I2(px_q[33]),
        .I3(cx_q[1]),
        .I4(px_q[32]),
        .I5(cx_q[0]),
        .O(\genblk1[4].g_val_reg0__36_carry_i_23_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[4].g_val_reg0__36_carry_i_24 
       (.I0(px_q[32]),
        .I1(cx_q[0]),
        .I2(px_q[33]),
        .I3(cx_q[1]),
        .O(\genblk1[4].g_val_reg0__36_carry_i_24_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[4].g_val_reg0__36_carry_i_25 
       (.I0(px_q[38]),
        .I1(cx_q[6]),
        .I2(\genblk1[4].g_val_reg0__36_carry_i_26_n_0 ),
        .I3(cx_q[5]),
        .I4(px_q[37]),
        .O(\genblk1[4].g_val_reg0__36_carry_i_25_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[4].g_val_reg0__36_carry_i_26 
       (.I0(px_q[36]),
        .I1(cx_q[4]),
        .I2(\genblk1[4].g_val_reg0__36_carry_i_27_n_0 ),
        .I3(cx_q[3]),
        .I4(px_q[35]),
        .O(\genblk1[4].g_val_reg0__36_carry_i_26_n_0 ));
  LUT6 #(
    .INIT(64'hD4DD4444DDDDD4DD)) 
    \genblk1[4].g_val_reg0__36_carry_i_27 
       (.I0(px_q[34]),
        .I1(cx_q[2]),
        .I2(cx_q[0]),
        .I3(px_q[32]),
        .I4(cx_q[1]),
        .I5(px_q[33]),
        .O(\genblk1[4].g_val_reg0__36_carry_i_27_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0__36_carry_i_3 
       (.I0(\genblk1[4].g_val_reg3__6 [7]),
        .I1(C__3[7]),
        .O(\genblk1[4].g_val_reg0__36_carry_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0__36_carry_i_4 
       (.I0(\genblk1[4].g_val_reg3__6 [6]),
        .I1(C__3[6]),
        .O(\genblk1[4].g_val_reg0__36_carry_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0__36_carry_i_5 
       (.I0(\genblk1[4].g_val_reg3__6 [5]),
        .I1(C__3[5]),
        .O(\genblk1[4].g_val_reg0__36_carry_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0__36_carry_i_6 
       (.I0(\genblk1[4].g_val_reg3__6 [4]),
        .I1(C__3[4]),
        .O(\genblk1[4].g_val_reg0__36_carry_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0__36_carry_i_7 
       (.I0(\genblk1[4].g_val_reg3__6 [3]),
        .I1(C__3[3]),
        .O(\genblk1[4].g_val_reg0__36_carry_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0__36_carry_i_8 
       (.I0(\genblk1[4].g_val_reg3__6 [2]),
        .I1(C__3[2]),
        .O(\genblk1[4].g_val_reg0__36_carry_i_8_n_0 ));
  LUT3 #(
    .INIT(8'h96)) 
    \genblk1[4].g_val_reg0__36_carry_i_9 
       (.I0(px_q[32]),
        .I1(cx_q[0]),
        .I2(C__3[1]),
        .O(\genblk1[4].g_val_reg0__36_carry_i_9_n_0 ));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[4].g_val_reg0_carry 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[4].g_val_reg0_carry_n_0 ,\NLW_genblk1[4].g_val_reg0_carry_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[4].g_val_reg2__1 [8:2],\genblk1[4].g_val_reg0_carry_i_2_n_0 }),
        .O(C__3[8:1]),
        .S({\genblk1[4].g_val_reg0_carry_i_3_n_0 ,\genblk1[4].g_val_reg0_carry_i_4_n_0 ,\genblk1[4].g_val_reg0_carry_i_5_n_0 ,\genblk1[4].g_val_reg0_carry_i_6_n_0 ,\genblk1[4].g_val_reg0_carry_i_7_n_0 ,\genblk1[4].g_val_reg0_carry_i_8_n_0 ,\genblk1[4].g_val_reg0_carry_i_9_n_0 ,\genblk1[4].g_val_reg0_carry_i_10_n_0 }));
  (* ADDER_THRESHOLD = "35" *) 
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[4].g_val_reg0_carry__0 
       (.CI(\genblk1[4].g_val_reg0_carry_n_0 ),
        .CI_TOP(1'b0),
        .CO(\NLW_genblk1[4].g_val_reg0_carry__0_CO_UNCONNECTED [7:0]),
        .DI({\NLW_genblk1[4].g_val_reg0_carry__0_DI_UNCONNECTED [7:5],1'b0,\genblk1[4].g_val_reg0_carry__0_i_1_n_0 ,\genblk1[4].g_val_reg2__1 [11:9]}),
        .O({\NLW_genblk1[4].g_val_reg0_carry__0_O_UNCONNECTED [7:5],C__3[13:9]}),
        .S({\NLW_genblk1[4].g_val_reg0_carry__0_S_UNCONNECTED [7:5],\genblk1[4].g_val_reg0_carry__0_i_3_n_0 ,\genblk1[4].g_val_reg0_carry__0_i_4_n_0 ,\genblk1[4].g_val_reg0_carry__0_i_5_n_0 ,\genblk1[4].g_val_reg0_carry__0_i_6_n_0 ,\genblk1[4].g_val_reg0_carry__0_i_7_n_0 }));
  LUT3 #(
    .INIT(8'h2B)) 
    \genblk1[4].g_val_reg0_carry__0_i_1 
       (.I0(py_q[39]),
        .I1(cy_q[7]),
        .I2(\genblk1[4].g_val_reg0_carry__0_i_8_n_0 ),
        .O(\genblk1[4].g_val_reg0_carry__0_i_1_n_0 ));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[4].g_val_reg0_carry__0_i_2 
       (.CI(\genblk1[4].g_val_reg0_carry_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[4].g_val_reg0_carry__0_i_2_CO_UNCONNECTED [7:2],\genblk1[4].g_val_reg2__1 [11],\NLW_genblk1[4].g_val_reg0_carry__0_i_2_CO_UNCONNECTED [0]}),
        .DI({\NLW_genblk1[4].g_val_reg0_carry__0_i_2_DI_UNCONNECTED [7:2],1'b0,\genblk1[4].g_val_reg0_carry__0_i_1_n_0 }),
        .O({\NLW_genblk1[4].g_val_reg0_carry__0_i_2_O_UNCONNECTED [7:1],\genblk1[4].g_val_reg2__1 [10]}),
        .S({\NLW_genblk1[4].g_val_reg0_carry__0_i_2_S_UNCONNECTED [7:2],1'b1,\genblk1[4].g_val_reg0_carry__0_i_9_n_0 }));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0_carry__0_i_3 
       (.I0(\genblk1[4].g_val_reg0_carry__0_i_1_n_0 ),
        .I1(\genblk1[4].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[4].g_val_reg0_carry__0_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0_carry__0_i_4 
       (.I0(\genblk1[4].g_val_reg0_carry__0_i_1_n_0 ),
        .I1(\genblk1[4].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[4].g_val_reg0_carry__0_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0_carry__0_i_5 
       (.I0(\genblk1[4].g_val_reg2__1 [11]),
        .I1(\genblk1[4].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[4].g_val_reg0_carry__0_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0_carry__0_i_6 
       (.I0(\genblk1[4].g_val_reg2__1 [10]),
        .I1(\genblk1[4].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[4].g_val_reg0_carry__0_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0_carry__0_i_7 
       (.I0(\genblk1[4].g_val_reg2__1 [9]),
        .I1(\genblk1[4].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[4].g_val_reg0_carry__0_i_7_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[4].g_val_reg0_carry__0_i_8 
       (.I0(py_q[38]),
        .I1(cy_q[6]),
        .I2(\genblk1[4].g_val_reg0_carry_i_27_n_0 ),
        .I3(cy_q[5]),
        .I4(py_q[37]),
        .O(\genblk1[4].g_val_reg0_carry__0_i_8_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0_carry__0_i_9 
       (.I0(\genblk1[4].g_val_reg0_carry__0_i_1_n_0 ),
        .I1(\genblk1[4].g_val_reg0_carry_i_11_n_0 ),
        .O(\genblk1[4].g_val_reg0_carry__0_i_9_n_0 ));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[4].g_val_reg0_carry_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[4].g_val_reg0_carry_i_1_n_0 ,\NLW_genblk1[4].g_val_reg0_carry_i_1_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[4].g_val_reg0_carry__0_i_1_n_0 ,\genblk1[4].g_val_reg0_carry_i_11_n_0 ,\genblk1[4].g_val_reg0_carry_i_12_n_0 ,\genblk1[4].g_val_reg0_carry_i_13_n_0 ,\genblk1[4].g_val_reg0_carry_i_14_n_0 ,\genblk1[4].g_val_reg0_carry_i_15_n_0 ,\genblk1[4].g_val_reg0_carry_i_16_n_0 ,1'b0}),
        .O(\genblk1[4].g_val_reg2__1 [9:2]),
        .S({\genblk1[4].g_val_reg0_carry_i_17_n_0 ,\genblk1[4].g_val_reg0_carry_i_18_n_0 ,\genblk1[4].g_val_reg0_carry_i_19_n_0 ,\genblk1[4].g_val_reg0_carry_i_20_n_0 ,\genblk1[4].g_val_reg0_carry_i_21_n_0 ,\genblk1[4].g_val_reg0_carry_i_22_n_0 ,\genblk1[4].g_val_reg0_carry_i_23_n_0 ,\genblk1[4].g_val_reg0_carry_i_24_n_0 }));
  LUT4 #(
    .INIT(16'h6996)) 
    \genblk1[4].g_val_reg0_carry_i_10 
       (.I0(py_q[32]),
        .I1(cy_q[0]),
        .I2(pz_q[12]),
        .I3(cz_q[0]),
        .O(\genblk1[4].g_val_reg0_carry_i_10_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[4].g_val_reg0_carry_i_11 
       (.I0(\genblk1[4].g_val_reg0_carry__0_i_8_n_0 ),
        .I1(py_q[39]),
        .I2(cy_q[7]),
        .O(\genblk1[4].g_val_reg0_carry_i_11_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[4].g_val_reg0_carry_i_12 
       (.I0(\genblk1[4].g_val_reg0_carry_i_27_n_0 ),
        .I1(cy_q[5]),
        .I2(py_q[37]),
        .I3(py_q[38]),
        .I4(cy_q[6]),
        .O(\genblk1[4].g_val_reg0_carry_i_12_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[4].g_val_reg0_carry_i_13 
       (.I0(\genblk1[4].g_val_reg0_carry_i_27_n_0 ),
        .I1(py_q[37]),
        .I2(cy_q[5]),
        .O(\genblk1[4].g_val_reg0_carry_i_13_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[4].g_val_reg0_carry_i_14 
       (.I0(\genblk1[4].g_val_reg0_carry_i_28_n_0 ),
        .I1(cy_q[3]),
        .I2(py_q[35]),
        .I3(py_q[36]),
        .I4(cy_q[4]),
        .O(\genblk1[4].g_val_reg0_carry_i_14_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[4].g_val_reg0_carry_i_15 
       (.I0(\genblk1[4].g_val_reg0_carry_i_28_n_0 ),
        .I1(py_q[35]),
        .I2(cy_q[3]),
        .O(\genblk1[4].g_val_reg0_carry_i_15_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[4].g_val_reg0_carry_i_16 
       (.I0(cy_q[0]),
        .I1(py_q[32]),
        .I2(cy_q[1]),
        .I3(py_q[33]),
        .I4(py_q[34]),
        .I5(cy_q[2]),
        .O(\genblk1[4].g_val_reg0_carry_i_16_n_0 ));
  LUT6 #(
    .INIT(64'h9696699669966969)) 
    \genblk1[4].g_val_reg0_carry_i_17 
       (.I0(\genblk1[4].g_val_reg0_carry__0_i_1_n_0 ),
        .I1(cy_q[6]),
        .I2(py_q[38]),
        .I3(py_q[37]),
        .I4(cy_q[5]),
        .I5(\genblk1[4].g_val_reg0_carry_i_27_n_0 ),
        .O(\genblk1[4].g_val_reg0_carry_i_17_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[4].g_val_reg0_carry_i_18 
       (.I0(\genblk1[4].g_val_reg0_carry_i_11_n_0 ),
        .I1(cy_q[5]),
        .I2(py_q[37]),
        .I3(\genblk1[4].g_val_reg0_carry_i_27_n_0 ),
        .O(\genblk1[4].g_val_reg0_carry_i_18_n_0 ));
  LUT6 #(
    .INIT(64'h9969696666969699)) 
    \genblk1[4].g_val_reg0_carry_i_19 
       (.I0(cy_q[6]),
        .I1(py_q[38]),
        .I2(py_q[37]),
        .I3(cy_q[5]),
        .I4(\genblk1[4].g_val_reg0_carry_i_27_n_0 ),
        .I5(\genblk1[4].g_val_reg0_carry_i_14_n_0 ),
        .O(\genblk1[4].g_val_reg0_carry_i_19_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0_carry_i_2 
       (.I0(py_q[32]),
        .I1(cy_q[0]),
        .O(\genblk1[4].g_val_reg0_carry_i_2_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[4].g_val_reg0_carry_i_20 
       (.I0(cy_q[5]),
        .I1(py_q[37]),
        .I2(\genblk1[4].g_val_reg0_carry_i_27_n_0 ),
        .I3(\genblk1[4].g_val_reg0_carry_i_15_n_0 ),
        .O(\genblk1[4].g_val_reg0_carry_i_20_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0_carry_i_21 
       (.I0(\genblk1[4].g_val_reg0_carry_i_14_n_0 ),
        .I1(\genblk1[4].g_val_reg0_carry_i_16_n_0 ),
        .O(\genblk1[4].g_val_reg0_carry_i_21_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[4].g_val_reg0_carry_i_22 
       (.I0(\genblk1[4].g_val_reg0_carry_i_15_n_0 ),
        .I1(cy_q[1]),
        .I2(py_q[33]),
        .I3(cy_q[0]),
        .I4(py_q[32]),
        .O(\genblk1[4].g_val_reg0_carry_i_22_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[4].g_val_reg0_carry_i_23 
       (.I0(cy_q[2]),
        .I1(py_q[34]),
        .I2(py_q[33]),
        .I3(cy_q[1]),
        .I4(py_q[32]),
        .I5(cy_q[0]),
        .O(\genblk1[4].g_val_reg0_carry_i_23_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[4].g_val_reg0_carry_i_24 
       (.I0(py_q[32]),
        .I1(cy_q[0]),
        .I2(py_q[33]),
        .I3(cy_q[1]),
        .O(\genblk1[4].g_val_reg0_carry_i_24_n_0 ));
  LUT6 #(
    .INIT(64'h2B22BBBB22222B22)) 
    \genblk1[4].g_val_reg0_carry_i_25 
       (.I0(pz_q[14]),
        .I1(cz_q[2]),
        .I2(cz_q[0]),
        .I3(pz_q[12]),
        .I4(cz_q[1]),
        .I5(pz_q[13]),
        .O(\genblk1[4].g_val_reg0_carry_i_25_n_0 ));
  (* OPT_MODIFIED = "RETARGET PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[4].g_val_reg0_carry_i_26 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[4].g_val_reg0_carry_i_26_CO_UNCONNECTED [7:5],\genblk1[4].g_val_reg1 [6],\NLW_genblk1[4].g_val_reg0_carry_i_26_CO_UNCONNECTED [3:0]}),
        .DI({\NLW_genblk1[4].g_val_reg0_carry_i_26_DI_UNCONNECTED [7:5],1'b0,\genblk1[4].g_val_reg0_carry_i_25_n_0 ,\genblk1[4].g_val_reg0_carry_i_25_n_0 ,\genblk1[4].g_val_reg0_carry_i_29_n_0 ,1'b0}),
        .O({\NLW_genblk1[4].g_val_reg0_carry_i_26_O_UNCONNECTED [7:4],\genblk1[4].g_val_reg1 [5:2]}),
        .S({\NLW_genblk1[4].g_val_reg0_carry_i_26_S_UNCONNECTED [7:5],1'b1,\genblk1[4].g_val_reg0_carry_i_30_n_0 ,\genblk1[4].g_val_reg0_carry_i_31_n_0 ,\genblk1[4].g_val_reg0_carry_i_9_0 }));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[4].g_val_reg0_carry_i_27 
       (.I0(py_q[36]),
        .I1(cy_q[4]),
        .I2(\genblk1[4].g_val_reg0_carry_i_28_n_0 ),
        .I3(cy_q[3]),
        .I4(py_q[35]),
        .O(\genblk1[4].g_val_reg0_carry_i_27_n_0 ));
  LUT6 #(
    .INIT(64'hD4DD4444DDDDD4DD)) 
    \genblk1[4].g_val_reg0_carry_i_28 
       (.I0(py_q[34]),
        .I1(cy_q[2]),
        .I2(cy_q[0]),
        .I3(py_q[32]),
        .I4(cy_q[1]),
        .I5(py_q[33]),
        .O(\genblk1[4].g_val_reg0_carry_i_28_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[4].g_val_reg0_carry_i_29 
       (.I0(cz_q[0]),
        .I1(pz_q[12]),
        .I2(cz_q[1]),
        .I3(pz_q[13]),
        .I4(pz_q[14]),
        .I5(cz_q[2]),
        .O(\genblk1[4].g_val_reg0_carry_i_29_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0_carry_i_3 
       (.I0(\genblk1[4].g_val_reg2__1 [8]),
        .I1(\genblk1[4].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[4].g_val_reg0_carry_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0_carry_i_30 
       (.I0(\genblk1[4].g_val_reg0_carry_i_25_n_0 ),
        .I1(\genblk1[4].g_val_reg0_carry_i_29_n_0 ),
        .O(\genblk1[4].g_val_reg0_carry_i_30_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[4].g_val_reg0_carry_i_31 
       (.I0(\genblk1[4].g_val_reg0_carry_i_25_n_0 ),
        .I1(cz_q[1]),
        .I2(pz_q[13]),
        .I3(cz_q[0]),
        .I4(pz_q[12]),
        .O(\genblk1[4].g_val_reg0_carry_i_31_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0_carry_i_4 
       (.I0(\genblk1[4].g_val_reg2__1 [7]),
        .I1(\genblk1[4].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[4].g_val_reg0_carry_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0_carry_i_5 
       (.I0(\genblk1[4].g_val_reg2__1 [6]),
        .I1(\genblk1[4].g_val_reg1 [6]),
        .O(\genblk1[4].g_val_reg0_carry_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0_carry_i_6 
       (.I0(\genblk1[4].g_val_reg2__1 [5]),
        .I1(\genblk1[4].g_val_reg1 [5]),
        .O(\genblk1[4].g_val_reg0_carry_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0_carry_i_7 
       (.I0(\genblk1[4].g_val_reg2__1 [4]),
        .I1(\genblk1[4].g_val_reg1 [4]),
        .O(\genblk1[4].g_val_reg0_carry_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0_carry_i_8 
       (.I0(\genblk1[4].g_val_reg2__1 [3]),
        .I1(\genblk1[4].g_val_reg1 [3]),
        .O(\genblk1[4].g_val_reg0_carry_i_8_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].g_val_reg0_carry_i_9 
       (.I0(\genblk1[4].g_val_reg2__1 [2]),
        .I1(\genblk1[4].g_val_reg1 [2]),
        .O(\genblk1[4].g_val_reg0_carry_i_9_n_0 ));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[4].g_val_reg0_inferred__0/i__carry 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[4].g_val_reg0_inferred__0/i__carry_n_0 ,\NLW_genblk1[4].g_val_reg0_inferred__0/i__carry_CO_UNCONNECTED [6:0]}),
        .DI(cg_q[8:1]),
        .O(\genblk1[4].g_val_reg0 [8:1]),
        .S({i__carry_i_1__4_n_0,i__carry_i_2__3_n_0,i__carry_i_3__3_n_0,i__carry_i_4__3_n_0,i__carry_i_5__3_n_0,i__carry_i_6__3_n_0,i__carry_i_7__3_n_0,i__carry_i_8__3_n_0}));
  (* ADDER_THRESHOLD = "35" *) 
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[4].g_val_reg0_inferred__0/i__carry__0 
       (.CI(\genblk1[4].g_val_reg0_inferred__0/i__carry_n_0 ),
        .CI_TOP(1'b0),
        .CO(\NLW_genblk1[4].g_val_reg0_inferred__0/i__carry__0_CO_UNCONNECTED [7:0]),
        .DI({\NLW_genblk1[4].g_val_reg0_inferred__0/i__carry__0_DI_UNCONNECTED [7:5],1'b0,cg_q[12:9]}),
        .O({\NLW_genblk1[4].g_val_reg0_inferred__0/i__carry__0_O_UNCONNECTED [7:5],\genblk1[4].g_val_reg0 [13:9]}),
        .S({\NLW_genblk1[4].g_val_reg0_inferred__0/i__carry__0_S_UNCONNECTED [7:5],i__carry__0_i_1__3_n_0,i__carry__0_i_2__3_n_0,i__carry__0_i_3__3_n_0,i__carry__0_i_4__3_n_0,i__carry__0_i_5__3_n_0}));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].g_val_reg[57] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].g_val_reg0 [1]),
        .Q(g[52]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].g_val_reg[58] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].g_val_reg0 [2]),
        .Q(g[53]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].g_val_reg[59] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].g_val_reg0 [3]),
        .Q(g[54]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].g_val_reg[60] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].g_val_reg0 [4]),
        .Q(g[55]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].g_val_reg[61] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].g_val_reg0 [5]),
        .Q(g[56]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].g_val_reg[62] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].g_val_reg0 [6]),
        .Q(g[57]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].g_val_reg[63] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].g_val_reg0 [7]),
        .Q(g[58]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].g_val_reg[64] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].g_val_reg0 [8]),
        .Q(g[59]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].g_val_reg[65] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].g_val_reg0 [9]),
        .Q(g[60]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].g_val_reg[66] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].g_val_reg0 [10]),
        .Q(g[61]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].g_val_reg[67] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].g_val_reg0 [11]),
        .Q(g[62]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].g_val_reg[68] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].g_val_reg0 [12]),
        .Q(g[63]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].g_val_reg[69] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].g_val_reg0 [13]),
        .Q(g[64]),
        .R(reset_q));
  (* SOFT_HLUTNM = "soft_lutpair8" *) 
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].h_val_x_reg[57]_i_1 
       (.I0(px_q[32]),
        .I1(ex_q[0]),
        .O(\genblk1[4].h_val_x_reg[57]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h9969696666969699)) 
    \genblk1[4].h_val_x_reg[65]_i_10 
       (.I0(ex_q[6]),
        .I1(px_q[38]),
        .I2(px_q[37]),
        .I3(ex_q[5]),
        .I4(\genblk1[4].h_val_x_reg[69]_i_3_n_0 ),
        .I5(\genblk1[4].h_val_x_reg[65]_i_5_n_0 ),
        .O(\genblk1[4].h_val_x_reg[65]_i_10_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[4].h_val_x_reg[65]_i_11 
       (.I0(ex_q[5]),
        .I1(px_q[37]),
        .I2(\genblk1[4].h_val_x_reg[69]_i_3_n_0 ),
        .I3(\genblk1[4].h_val_x_reg[65]_i_6_n_0 ),
        .O(\genblk1[4].h_val_x_reg[65]_i_11_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].h_val_x_reg[65]_i_12 
       (.I0(\genblk1[4].h_val_x_reg[65]_i_5_n_0 ),
        .I1(\genblk1[4].h_val_x_reg[65]_i_7_n_0 ),
        .O(\genblk1[4].h_val_x_reg[65]_i_12_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[4].h_val_x_reg[65]_i_13 
       (.I0(\genblk1[4].h_val_x_reg[65]_i_6_n_0 ),
        .I1(ex_q[1]),
        .I2(px_q[33]),
        .I3(ex_q[0]),
        .I4(px_q[32]),
        .O(\genblk1[4].h_val_x_reg[65]_i_13_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[4].h_val_x_reg[65]_i_14 
       (.I0(ex_q[2]),
        .I1(px_q[34]),
        .I2(px_q[33]),
        .I3(ex_q[1]),
        .I4(px_q[32]),
        .I5(ex_q[0]),
        .O(\genblk1[4].h_val_x_reg[65]_i_14_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[4].h_val_x_reg[65]_i_15 
       (.I0(px_q[32]),
        .I1(ex_q[0]),
        .I2(px_q[33]),
        .I3(ex_q[1]),
        .O(\genblk1[4].h_val_x_reg[65]_i_15_n_0 ));
  LUT6 #(
    .INIT(64'hD4DD4444DDDDD4DD)) 
    \genblk1[4].h_val_x_reg[65]_i_16 
       (.I0(px_q[34]),
        .I1(ex_q[2]),
        .I2(ex_q[0]),
        .I3(px_q[32]),
        .I4(ex_q[1]),
        .I5(px_q[33]),
        .O(\genblk1[4].h_val_x_reg[65]_i_16_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[4].h_val_x_reg[65]_i_2 
       (.I0(\genblk1[4].h_val_x_reg[69]_i_2_n_0 ),
        .I1(px_q[39]),
        .I2(ex_q[7]),
        .O(\genblk1[4].h_val_x_reg[65]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[4].h_val_x_reg[65]_i_3 
       (.I0(\genblk1[4].h_val_x_reg[69]_i_3_n_0 ),
        .I1(ex_q[5]),
        .I2(px_q[37]),
        .I3(px_q[38]),
        .I4(ex_q[6]),
        .O(\genblk1[4].h_val_x_reg[65]_i_3_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[4].h_val_x_reg[65]_i_4 
       (.I0(\genblk1[4].h_val_x_reg[69]_i_3_n_0 ),
        .I1(px_q[37]),
        .I2(ex_q[5]),
        .O(\genblk1[4].h_val_x_reg[65]_i_4_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[4].h_val_x_reg[65]_i_5 
       (.I0(\genblk1[4].h_val_x_reg[65]_i_16_n_0 ),
        .I1(ex_q[3]),
        .I2(px_q[35]),
        .I3(px_q[36]),
        .I4(ex_q[4]),
        .O(\genblk1[4].h_val_x_reg[65]_i_5_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[4].h_val_x_reg[65]_i_6 
       (.I0(\genblk1[4].h_val_x_reg[65]_i_16_n_0 ),
        .I1(px_q[35]),
        .I2(ex_q[3]),
        .O(\genblk1[4].h_val_x_reg[65]_i_6_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[4].h_val_x_reg[65]_i_7 
       (.I0(ex_q[0]),
        .I1(px_q[32]),
        .I2(ex_q[1]),
        .I3(px_q[33]),
        .I4(px_q[34]),
        .I5(ex_q[2]),
        .O(\genblk1[4].h_val_x_reg[65]_i_7_n_0 ));
  LUT6 #(
    .INIT(64'h9696699669966969)) 
    \genblk1[4].h_val_x_reg[65]_i_8 
       (.I0(\genblk1[4].h_val_x_reg[69]_i_1_n_0 ),
        .I1(ex_q[6]),
        .I2(px_q[38]),
        .I3(px_q[37]),
        .I4(ex_q[5]),
        .I5(\genblk1[4].h_val_x_reg[69]_i_3_n_0 ),
        .O(\genblk1[4].h_val_x_reg[65]_i_8_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[4].h_val_x_reg[65]_i_9 
       (.I0(\genblk1[4].h_val_x_reg[65]_i_2_n_0 ),
        .I1(ex_q[5]),
        .I2(px_q[37]),
        .I3(\genblk1[4].h_val_x_reg[69]_i_3_n_0 ),
        .O(\genblk1[4].h_val_x_reg[65]_i_9_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].h_val_x_reg[67]_i_2 
       (.I0(\genblk1[4].h_val_x_reg[69]_i_1_n_0 ),
        .I1(\genblk1[4].h_val_x_reg[65]_i_2_n_0 ),
        .O(\genblk1[4].h_val_x_reg[67]_i_2_n_0 ));
  LUT3 #(
    .INIT(8'h2B)) 
    \genblk1[4].h_val_x_reg[69]_i_1 
       (.I0(px_q[39]),
        .I1(ex_q[7]),
        .I2(\genblk1[4].h_val_x_reg[69]_i_2_n_0 ),
        .O(\genblk1[4].h_val_x_reg[69]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[4].h_val_x_reg[69]_i_2 
       (.I0(px_q[38]),
        .I1(ex_q[6]),
        .I2(\genblk1[4].h_val_x_reg[69]_i_3_n_0 ),
        .I3(ex_q[5]),
        .I4(px_q[37]),
        .O(\genblk1[4].h_val_x_reg[69]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[4].h_val_x_reg[69]_i_3 
       (.I0(px_q[36]),
        .I1(ex_q[4]),
        .I2(\genblk1[4].h_val_x_reg[65]_i_16_n_0 ),
        .I3(ex_q[3]),
        .I4(px_q[35]),
        .O(\genblk1[4].h_val_x_reg[69]_i_3_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_x_reg_reg[57] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_x_reg[57]_i_1_n_0 ),
        .Q(\genblk1[4].h_val_x_reg_reg_n_0_[57] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_x_reg_reg[58] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_x_reg_reg0 [2]),
        .Q(\genblk1[4].h_val_x_reg_reg_n_0_[58] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_x_reg_reg[59] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_x_reg_reg0 [3]),
        .Q(\genblk1[4].h_val_x_reg_reg_n_0_[59] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_x_reg_reg[60] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_x_reg_reg0 [4]),
        .Q(\genblk1[4].h_val_x_reg_reg_n_0_[60] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_x_reg_reg[61] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_x_reg_reg0 [5]),
        .Q(\genblk1[4].h_val_x_reg_reg_n_0_[61] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_x_reg_reg[62] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_x_reg_reg0 [6]),
        .Q(\genblk1[4].h_val_x_reg_reg_n_0_[62] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_x_reg_reg[63] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_x_reg_reg0 [7]),
        .Q(\genblk1[4].h_val_x_reg_reg_n_0_[63] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_x_reg_reg[64] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_x_reg_reg0 [8]),
        .Q(\genblk1[4].h_val_x_reg_reg_n_0_[64] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_x_reg_reg[65] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_x_reg_reg0 [9]),
        .Q(\genblk1[4].h_val_x_reg_reg_n_0_[65] ),
        .R(reset_q));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[4].h_val_x_reg_reg[65]_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[4].h_val_x_reg_reg[65]_i_1_n_0 ,\NLW_genblk1[4].h_val_x_reg_reg[65]_i_1_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[4].h_val_x_reg[69]_i_1_n_0 ,\genblk1[4].h_val_x_reg[65]_i_2_n_0 ,\genblk1[4].h_val_x_reg[65]_i_3_n_0 ,\genblk1[4].h_val_x_reg[65]_i_4_n_0 ,\genblk1[4].h_val_x_reg[65]_i_5_n_0 ,\genblk1[4].h_val_x_reg[65]_i_6_n_0 ,\genblk1[4].h_val_x_reg[65]_i_7_n_0 ,1'b0}),
        .O(\genblk1[4].h_val_x_reg_reg0 [9:2]),
        .S({\genblk1[4].h_val_x_reg[65]_i_8_n_0 ,\genblk1[4].h_val_x_reg[65]_i_9_n_0 ,\genblk1[4].h_val_x_reg[65]_i_10_n_0 ,\genblk1[4].h_val_x_reg[65]_i_11_n_0 ,\genblk1[4].h_val_x_reg[65]_i_12_n_0 ,\genblk1[4].h_val_x_reg[65]_i_13_n_0 ,\genblk1[4].h_val_x_reg[65]_i_14_n_0 ,\genblk1[4].h_val_x_reg[65]_i_15_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_x_reg_reg[66] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_x_reg_reg0 [10]),
        .Q(\genblk1[4].h_val_x_reg_reg_n_0_[66] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_x_reg_reg[67] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_x_reg_reg0 [11]),
        .Q(\genblk1[4].h_val_x_reg_reg_n_0_[67] ),
        .R(reset_q));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[4].h_val_x_reg_reg[67]_i_1 
       (.CI(\genblk1[4].h_val_x_reg_reg[65]_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[4].h_val_x_reg_reg[67]_i_1_CO_UNCONNECTED [7:2],\genblk1[4].h_val_x_reg_reg0 [11],\NLW_genblk1[4].h_val_x_reg_reg[67]_i_1_CO_UNCONNECTED [0]}),
        .DI({\NLW_genblk1[4].h_val_x_reg_reg[67]_i_1_DI_UNCONNECTED [7:2],1'b0,\genblk1[4].h_val_x_reg[69]_i_1_n_0 }),
        .O({\NLW_genblk1[4].h_val_x_reg_reg[67]_i_1_O_UNCONNECTED [7:1],\genblk1[4].h_val_x_reg_reg0 [10]}),
        .S({\NLW_genblk1[4].h_val_x_reg_reg[67]_i_1_S_UNCONNECTED [7:2],1'b1,\genblk1[4].h_val_x_reg[67]_i_2_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_x_reg_reg[69] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_x_reg[69]_i_1_n_0 ),
        .Q(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .R(reset_q));
  (* SOFT_HLUTNM = "soft_lutpair7" *) 
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].h_val_y_reg[57]_i_1 
       (.I0(py_q[32]),
        .I1(ey_q[0]),
        .O(\genblk1[4].h_val_y_reg[57]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h9969696666969699)) 
    \genblk1[4].h_val_y_reg[65]_i_10 
       (.I0(ey_q[6]),
        .I1(py_q[38]),
        .I2(py_q[37]),
        .I3(ey_q[5]),
        .I4(\genblk1[4].h_val_y_reg[69]_i_3_n_0 ),
        .I5(\genblk1[4].h_val_y_reg[65]_i_5_n_0 ),
        .O(\genblk1[4].h_val_y_reg[65]_i_10_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[4].h_val_y_reg[65]_i_11 
       (.I0(ey_q[5]),
        .I1(py_q[37]),
        .I2(\genblk1[4].h_val_y_reg[69]_i_3_n_0 ),
        .I3(\genblk1[4].h_val_y_reg[65]_i_6_n_0 ),
        .O(\genblk1[4].h_val_y_reg[65]_i_11_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].h_val_y_reg[65]_i_12 
       (.I0(\genblk1[4].h_val_y_reg[65]_i_5_n_0 ),
        .I1(\genblk1[4].h_val_y_reg[65]_i_7_n_0 ),
        .O(\genblk1[4].h_val_y_reg[65]_i_12_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[4].h_val_y_reg[65]_i_13 
       (.I0(\genblk1[4].h_val_y_reg[65]_i_6_n_0 ),
        .I1(ey_q[1]),
        .I2(py_q[33]),
        .I3(ey_q[0]),
        .I4(py_q[32]),
        .O(\genblk1[4].h_val_y_reg[65]_i_13_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[4].h_val_y_reg[65]_i_14 
       (.I0(ey_q[2]),
        .I1(py_q[34]),
        .I2(py_q[33]),
        .I3(ey_q[1]),
        .I4(py_q[32]),
        .I5(ey_q[0]),
        .O(\genblk1[4].h_val_y_reg[65]_i_14_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[4].h_val_y_reg[65]_i_15 
       (.I0(py_q[32]),
        .I1(ey_q[0]),
        .I2(py_q[33]),
        .I3(ey_q[1]),
        .O(\genblk1[4].h_val_y_reg[65]_i_15_n_0 ));
  LUT6 #(
    .INIT(64'hD4DD4444DDDDD4DD)) 
    \genblk1[4].h_val_y_reg[65]_i_16 
       (.I0(py_q[34]),
        .I1(ey_q[2]),
        .I2(ey_q[0]),
        .I3(py_q[32]),
        .I4(ey_q[1]),
        .I5(py_q[33]),
        .O(\genblk1[4].h_val_y_reg[65]_i_16_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[4].h_val_y_reg[65]_i_2 
       (.I0(\genblk1[4].h_val_y_reg[69]_i_2_n_0 ),
        .I1(py_q[39]),
        .I2(ey_q[7]),
        .O(\genblk1[4].h_val_y_reg[65]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[4].h_val_y_reg[65]_i_3 
       (.I0(\genblk1[4].h_val_y_reg[69]_i_3_n_0 ),
        .I1(ey_q[5]),
        .I2(py_q[37]),
        .I3(py_q[38]),
        .I4(ey_q[6]),
        .O(\genblk1[4].h_val_y_reg[65]_i_3_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[4].h_val_y_reg[65]_i_4 
       (.I0(\genblk1[4].h_val_y_reg[69]_i_3_n_0 ),
        .I1(py_q[37]),
        .I2(ey_q[5]),
        .O(\genblk1[4].h_val_y_reg[65]_i_4_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[4].h_val_y_reg[65]_i_5 
       (.I0(\genblk1[4].h_val_y_reg[65]_i_16_n_0 ),
        .I1(ey_q[3]),
        .I2(py_q[35]),
        .I3(py_q[36]),
        .I4(ey_q[4]),
        .O(\genblk1[4].h_val_y_reg[65]_i_5_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[4].h_val_y_reg[65]_i_6 
       (.I0(\genblk1[4].h_val_y_reg[65]_i_16_n_0 ),
        .I1(py_q[35]),
        .I2(ey_q[3]),
        .O(\genblk1[4].h_val_y_reg[65]_i_6_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[4].h_val_y_reg[65]_i_7 
       (.I0(ey_q[0]),
        .I1(py_q[32]),
        .I2(ey_q[1]),
        .I3(py_q[33]),
        .I4(py_q[34]),
        .I5(ey_q[2]),
        .O(\genblk1[4].h_val_y_reg[65]_i_7_n_0 ));
  LUT6 #(
    .INIT(64'h9696699669966969)) 
    \genblk1[4].h_val_y_reg[65]_i_8 
       (.I0(\genblk1[4].h_val_y_reg[69]_i_1_n_0 ),
        .I1(ey_q[6]),
        .I2(py_q[38]),
        .I3(py_q[37]),
        .I4(ey_q[5]),
        .I5(\genblk1[4].h_val_y_reg[69]_i_3_n_0 ),
        .O(\genblk1[4].h_val_y_reg[65]_i_8_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[4].h_val_y_reg[65]_i_9 
       (.I0(\genblk1[4].h_val_y_reg[65]_i_2_n_0 ),
        .I1(ey_q[5]),
        .I2(py_q[37]),
        .I3(\genblk1[4].h_val_y_reg[69]_i_3_n_0 ),
        .O(\genblk1[4].h_val_y_reg[65]_i_9_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].h_val_y_reg[67]_i_2 
       (.I0(\genblk1[4].h_val_y_reg[69]_i_1_n_0 ),
        .I1(\genblk1[4].h_val_y_reg[65]_i_2_n_0 ),
        .O(\genblk1[4].h_val_y_reg[67]_i_2_n_0 ));
  LUT3 #(
    .INIT(8'h2B)) 
    \genblk1[4].h_val_y_reg[69]_i_1 
       (.I0(py_q[39]),
        .I1(ey_q[7]),
        .I2(\genblk1[4].h_val_y_reg[69]_i_2_n_0 ),
        .O(\genblk1[4].h_val_y_reg[69]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[4].h_val_y_reg[69]_i_2 
       (.I0(py_q[38]),
        .I1(ey_q[6]),
        .I2(\genblk1[4].h_val_y_reg[69]_i_3_n_0 ),
        .I3(ey_q[5]),
        .I4(py_q[37]),
        .O(\genblk1[4].h_val_y_reg[69]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[4].h_val_y_reg[69]_i_3 
       (.I0(py_q[36]),
        .I1(ey_q[4]),
        .I2(\genblk1[4].h_val_y_reg[65]_i_16_n_0 ),
        .I3(ey_q[3]),
        .I4(py_q[35]),
        .O(\genblk1[4].h_val_y_reg[69]_i_3_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_y_reg_reg[57] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_y_reg[57]_i_1_n_0 ),
        .Q(\genblk1[4].h_val_y_reg_reg_n_0_[57] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_y_reg_reg[58] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_y_reg_reg0 [2]),
        .Q(\genblk1[4].h_val_y_reg_reg_n_0_[58] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_y_reg_reg[59] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_y_reg_reg0 [3]),
        .Q(\genblk1[4].h_val_y_reg_reg_n_0_[59] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_y_reg_reg[60] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_y_reg_reg0 [4]),
        .Q(\genblk1[4].h_val_y_reg_reg_n_0_[60] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_y_reg_reg[61] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_y_reg_reg0 [5]),
        .Q(\genblk1[4].h_val_y_reg_reg_n_0_[61] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_y_reg_reg[62] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_y_reg_reg0 [6]),
        .Q(\genblk1[4].h_val_y_reg_reg_n_0_[62] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_y_reg_reg[63] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_y_reg_reg0 [7]),
        .Q(\genblk1[4].h_val_y_reg_reg_n_0_[63] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_y_reg_reg[64] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_y_reg_reg0 [8]),
        .Q(\genblk1[4].h_val_y_reg_reg_n_0_[64] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_y_reg_reg[65] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_y_reg_reg0 [9]),
        .Q(\genblk1[4].h_val_y_reg_reg_n_0_[65] ),
        .R(reset_q));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[4].h_val_y_reg_reg[65]_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[4].h_val_y_reg_reg[65]_i_1_n_0 ,\NLW_genblk1[4].h_val_y_reg_reg[65]_i_1_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[4].h_val_y_reg[69]_i_1_n_0 ,\genblk1[4].h_val_y_reg[65]_i_2_n_0 ,\genblk1[4].h_val_y_reg[65]_i_3_n_0 ,\genblk1[4].h_val_y_reg[65]_i_4_n_0 ,\genblk1[4].h_val_y_reg[65]_i_5_n_0 ,\genblk1[4].h_val_y_reg[65]_i_6_n_0 ,\genblk1[4].h_val_y_reg[65]_i_7_n_0 ,1'b0}),
        .O(\genblk1[4].h_val_y_reg_reg0 [9:2]),
        .S({\genblk1[4].h_val_y_reg[65]_i_8_n_0 ,\genblk1[4].h_val_y_reg[65]_i_9_n_0 ,\genblk1[4].h_val_y_reg[65]_i_10_n_0 ,\genblk1[4].h_val_y_reg[65]_i_11_n_0 ,\genblk1[4].h_val_y_reg[65]_i_12_n_0 ,\genblk1[4].h_val_y_reg[65]_i_13_n_0 ,\genblk1[4].h_val_y_reg[65]_i_14_n_0 ,\genblk1[4].h_val_y_reg[65]_i_15_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_y_reg_reg[66] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_y_reg_reg0 [10]),
        .Q(\genblk1[4].h_val_y_reg_reg_n_0_[66] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_y_reg_reg[67] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_y_reg_reg0 [11]),
        .Q(\genblk1[4].h_val_y_reg_reg_n_0_[67] ),
        .R(reset_q));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[4].h_val_y_reg_reg[67]_i_1 
       (.CI(\genblk1[4].h_val_y_reg_reg[65]_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[4].h_val_y_reg_reg[67]_i_1_CO_UNCONNECTED [7:2],\genblk1[4].h_val_y_reg_reg0 [11],\NLW_genblk1[4].h_val_y_reg_reg[67]_i_1_CO_UNCONNECTED [0]}),
        .DI({\NLW_genblk1[4].h_val_y_reg_reg[67]_i_1_DI_UNCONNECTED [7:2],1'b0,\genblk1[4].h_val_y_reg[69]_i_1_n_0 }),
        .O({\NLW_genblk1[4].h_val_y_reg_reg[67]_i_1_O_UNCONNECTED [7:1],\genblk1[4].h_val_y_reg_reg0 [10]}),
        .S({\NLW_genblk1[4].h_val_y_reg_reg[67]_i_1_S_UNCONNECTED [7:2],1'b1,\genblk1[4].h_val_y_reg[67]_i_2_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_y_reg_reg[69] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_y_reg[69]_i_1_n_0 ),
        .Q(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .R(reset_q));
  (* SOFT_HLUTNM = "soft_lutpair6" *) 
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].h_val_z_reg[57]_i_1 
       (.I0(pz_q[12]),
        .I1(ez_q[0]),
        .O(\genblk1[4].h_val_z_reg[57]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[4].h_val_z_reg[62]_i_2 
       (.I0(ez_q[0]),
        .I1(pz_q[12]),
        .I2(ez_q[1]),
        .I3(pz_q[13]),
        .I4(pz_q[14]),
        .I5(ez_q[2]),
        .O(\genblk1[4].h_val_z_reg[62]_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[4].h_val_z_reg[62]_i_3 
       (.I0(\genblk1[4].h_val_z_reg[69]_i_1_n_0 ),
        .I1(\genblk1[4].h_val_z_reg[62]_i_2_n_0 ),
        .O(\genblk1[4].h_val_z_reg[62]_i_3_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[4].h_val_z_reg[62]_i_4 
       (.I0(\genblk1[4].h_val_z_reg[69]_i_1_n_0 ),
        .I1(ez_q[1]),
        .I2(pz_q[13]),
        .I3(ez_q[0]),
        .I4(pz_q[12]),
        .O(\genblk1[4].h_val_z_reg[62]_i_4_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[4].h_val_z_reg[62]_i_5 
       (.I0(ez_q[2]),
        .I1(pz_q[14]),
        .I2(pz_q[13]),
        .I3(ez_q[1]),
        .I4(pz_q[12]),
        .I5(ez_q[0]),
        .O(\genblk1[4].h_val_z_reg[62]_i_5_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[4].h_val_z_reg[62]_i_6 
       (.I0(pz_q[12]),
        .I1(ez_q[0]),
        .I2(pz_q[13]),
        .I3(ez_q[1]),
        .O(\genblk1[4].h_val_z_reg[62]_i_6_n_0 ));
  LUT6 #(
    .INIT(64'h2B22BBBB22222B22)) 
    \genblk1[4].h_val_z_reg[69]_i_1 
       (.I0(pz_q[14]),
        .I1(ez_q[2]),
        .I2(ez_q[0]),
        .I3(pz_q[12]),
        .I4(ez_q[1]),
        .I5(pz_q[13]),
        .O(\genblk1[4].h_val_z_reg[69]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_z_reg_reg[57] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_z_reg[57]_i_1_n_0 ),
        .Q(\genblk1[4].h_val_z_reg_reg_n_0_[57] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_z_reg_reg[58] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_z_reg_reg0 [2]),
        .Q(\genblk1[4].h_val_z_reg_reg_n_0_[58] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_z_reg_reg[59] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_z_reg_reg0 [3]),
        .Q(\genblk1[4].h_val_z_reg_reg_n_0_[59] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_z_reg_reg[60] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_z_reg_reg0 [4]),
        .Q(\genblk1[4].h_val_z_reg_reg_n_0_[60] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_z_reg_reg[61] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_z_reg_reg0 [5]),
        .Q(\genblk1[4].h_val_z_reg_reg_n_0_[61] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_z_reg_reg[62] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_z_reg_reg0 [6]),
        .Q(\genblk1[4].h_val_z_reg_reg_n_0_[62] ),
        .R(reset_q));
  (* OPT_MODIFIED = "RETARGET PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[4].h_val_z_reg_reg[62]_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[4].h_val_z_reg_reg[62]_i_1_CO_UNCONNECTED [7:5],\genblk1[4].h_val_z_reg_reg0 [6],\NLW_genblk1[4].h_val_z_reg_reg[62]_i_1_CO_UNCONNECTED [3:0]}),
        .DI({\NLW_genblk1[4].h_val_z_reg_reg[62]_i_1_DI_UNCONNECTED [7:5],1'b0,\genblk1[4].h_val_z_reg[69]_i_1_n_0 ,\genblk1[4].h_val_z_reg[69]_i_1_n_0 ,\genblk1[4].h_val_z_reg[62]_i_2_n_0 ,1'b0}),
        .O({\NLW_genblk1[4].h_val_z_reg_reg[62]_i_1_O_UNCONNECTED [7:4],\genblk1[4].h_val_z_reg_reg0 [5:2]}),
        .S({\NLW_genblk1[4].h_val_z_reg_reg[62]_i_1_S_UNCONNECTED [7:5],1'b1,\genblk1[4].h_val_z_reg[62]_i_3_n_0 ,\genblk1[4].h_val_z_reg[62]_i_4_n_0 ,\genblk1[4].h_val_z_reg[62]_i_5_n_0 ,\genblk1[4].h_val_z_reg[62]_i_6_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[4].h_val_z_reg_reg[69] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[4].h_val_z_reg[69]_i_1_n_0 ),
        .Q(\genblk1[4].h_val_z_reg_reg_n_0_[69] ),
        .R(reset_q));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[5].g_val_reg0__36_carry 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[5].g_val_reg0__36_carry_n_0 ,\NLW_genblk1[5].g_val_reg0__36_carry_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[5].g_val_reg3__6 [8:2],C__4[1]}),
        .O({\genblk1[5].g_val_reg0__36_carry_n_8 ,\genblk1[5].g_val_reg0__36_carry_n_9 ,\genblk1[5].g_val_reg0__36_carry_n_10 ,\genblk1[5].g_val_reg0__36_carry_n_11 ,\genblk1[5].g_val_reg0__36_carry_n_12 ,\genblk1[5].g_val_reg0__36_carry_n_13 ,\genblk1[5].g_val_reg0__36_carry_n_14 ,\genblk1[5].g_val_reg0__36_carry_n_15 }),
        .S({\genblk1[5].g_val_reg0__36_carry_i_2_n_0 ,\genblk1[5].g_val_reg0__36_carry_i_3_n_0 ,\genblk1[5].g_val_reg0__36_carry_i_4_n_0 ,\genblk1[5].g_val_reg0__36_carry_i_5_n_0 ,\genblk1[5].g_val_reg0__36_carry_i_6_n_0 ,\genblk1[5].g_val_reg0__36_carry_i_7_n_0 ,\genblk1[5].g_val_reg0__36_carry_i_8_n_0 ,\genblk1[5].g_val_reg0__36_carry_i_9_n_0 }));
  (* ADDER_THRESHOLD = "35" *) 
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[5].g_val_reg0__36_carry__0 
       (.CI(\genblk1[5].g_val_reg0__36_carry_n_0 ),
        .CI_TOP(1'b0),
        .CO(\NLW_genblk1[5].g_val_reg0__36_carry__0_CO_UNCONNECTED [7:0]),
        .DI({\NLW_genblk1[5].g_val_reg0__36_carry__0_DI_UNCONNECTED [7:5],1'b0,C__4[12],\genblk1[5].g_val_reg3__6 [11:9]}),
        .O({\NLW_genblk1[5].g_val_reg0__36_carry__0_O_UNCONNECTED [7:5],\genblk1[5].g_val_reg0__36_carry__0_n_11 ,\genblk1[5].g_val_reg0__36_carry__0_n_12 ,\genblk1[5].g_val_reg0__36_carry__0_n_13 ,\genblk1[5].g_val_reg0__36_carry__0_n_14 ,\genblk1[5].g_val_reg0__36_carry__0_n_15 }),
        .S({\NLW_genblk1[5].g_val_reg0__36_carry__0_S_UNCONNECTED [7:5],\genblk1[5].g_val_reg0__36_carry__0_i_2_n_0 ,\genblk1[5].g_val_reg0__36_carry__0_i_3_n_0 ,\genblk1[5].g_val_reg0__36_carry__0_i_4_n_0 ,\genblk1[5].g_val_reg0__36_carry__0_i_5_n_0 ,\genblk1[5].g_val_reg0__36_carry__0_i_6_n_0 }));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[5].g_val_reg0__36_carry__0_i_1 
       (.CI(\genblk1[5].g_val_reg0__36_carry_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[5].g_val_reg0__36_carry__0_i_1_CO_UNCONNECTED [7:2],\genblk1[5].g_val_reg3__6 [11],\NLW_genblk1[5].g_val_reg0__36_carry__0_i_1_CO_UNCONNECTED [0]}),
        .DI({\NLW_genblk1[5].g_val_reg0__36_carry__0_i_1_DI_UNCONNECTED [7:2],1'b0,\genblk1[5].g_val_reg0__36_carry_i_10_n_0 }),
        .O({\NLW_genblk1[5].g_val_reg0__36_carry__0_i_1_O_UNCONNECTED [7:1],\genblk1[5].g_val_reg3__6 [10]}),
        .S({\NLW_genblk1[5].g_val_reg0__36_carry__0_i_1_S_UNCONNECTED [7:2],1'b1,\genblk1[5].g_val_reg0__36_carry__0_i_7_n_0 }));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0__36_carry__0_i_2 
       (.I0(\genblk1[5].g_val_reg0__36_carry_i_10_n_0 ),
        .I1(C__4[13]),
        .O(\genblk1[5].g_val_reg0__36_carry__0_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0__36_carry__0_i_3 
       (.I0(\genblk1[5].g_val_reg0__36_carry_i_10_n_0 ),
        .I1(C__4[12]),
        .O(\genblk1[5].g_val_reg0__36_carry__0_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0__36_carry__0_i_4 
       (.I0(\genblk1[5].g_val_reg3__6 [11]),
        .I1(C__4[11]),
        .O(\genblk1[5].g_val_reg0__36_carry__0_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0__36_carry__0_i_5 
       (.I0(\genblk1[5].g_val_reg3__6 [10]),
        .I1(C__4[10]),
        .O(\genblk1[5].g_val_reg0__36_carry__0_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0__36_carry__0_i_6 
       (.I0(\genblk1[5].g_val_reg3__6 [9]),
        .I1(C__4[9]),
        .O(\genblk1[5].g_val_reg0__36_carry__0_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0__36_carry__0_i_7 
       (.I0(\genblk1[5].g_val_reg0__36_carry_i_10_n_0 ),
        .I1(\genblk1[5].g_val_reg0__36_carry_i_11_n_0 ),
        .O(\genblk1[5].g_val_reg0__36_carry__0_i_7_n_0 ));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[5].g_val_reg0__36_carry_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[5].g_val_reg0__36_carry_i_1_n_0 ,\NLW_genblk1[5].g_val_reg0__36_carry_i_1_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[5].g_val_reg0__36_carry_i_10_n_0 ,\genblk1[5].g_val_reg0__36_carry_i_11_n_0 ,\genblk1[5].g_val_reg0__36_carry_i_12_n_0 ,\genblk1[5].g_val_reg0__36_carry_i_13_n_0 ,\genblk1[5].g_val_reg0__36_carry_i_14_n_0 ,\genblk1[5].g_val_reg0__36_carry_i_15_n_0 ,\genblk1[5].g_val_reg0__36_carry_i_16_n_0 ,1'b0}),
        .O(\genblk1[5].g_val_reg3__6 [9:2]),
        .S({\genblk1[5].g_val_reg0__36_carry_i_17_n_0 ,\genblk1[5].g_val_reg0__36_carry_i_18_n_0 ,\genblk1[5].g_val_reg0__36_carry_i_19_n_0 ,\genblk1[5].g_val_reg0__36_carry_i_20_n_0 ,\genblk1[5].g_val_reg0__36_carry_i_21_n_0 ,\genblk1[5].g_val_reg0__36_carry_i_22_n_0 ,\genblk1[5].g_val_reg0__36_carry_i_23_n_0 ,\genblk1[5].g_val_reg0__36_carry_i_24_n_0 }));
  LUT3 #(
    .INIT(8'h2B)) 
    \genblk1[5].g_val_reg0__36_carry_i_10 
       (.I0(px_q[47]),
        .I1(cx_q[7]),
        .I2(\genblk1[5].g_val_reg0__36_carry_i_25_n_0 ),
        .O(\genblk1[5].g_val_reg0__36_carry_i_10_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[5].g_val_reg0__36_carry_i_11 
       (.I0(\genblk1[5].g_val_reg0__36_carry_i_25_n_0 ),
        .I1(px_q[47]),
        .I2(cx_q[7]),
        .O(\genblk1[5].g_val_reg0__36_carry_i_11_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[5].g_val_reg0__36_carry_i_12 
       (.I0(\genblk1[5].g_val_reg0__36_carry_i_26_n_0 ),
        .I1(cx_q[5]),
        .I2(px_q[45]),
        .I3(px_q[46]),
        .I4(cx_q[6]),
        .O(\genblk1[5].g_val_reg0__36_carry_i_12_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[5].g_val_reg0__36_carry_i_13 
       (.I0(\genblk1[5].g_val_reg0__36_carry_i_26_n_0 ),
        .I1(px_q[45]),
        .I2(cx_q[5]),
        .O(\genblk1[5].g_val_reg0__36_carry_i_13_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[5].g_val_reg0__36_carry_i_14 
       (.I0(\genblk1[5].g_val_reg0__36_carry_i_27_n_0 ),
        .I1(cx_q[3]),
        .I2(px_q[43]),
        .I3(px_q[44]),
        .I4(cx_q[4]),
        .O(\genblk1[5].g_val_reg0__36_carry_i_14_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[5].g_val_reg0__36_carry_i_15 
       (.I0(\genblk1[5].g_val_reg0__36_carry_i_27_n_0 ),
        .I1(px_q[43]),
        .I2(cx_q[3]),
        .O(\genblk1[5].g_val_reg0__36_carry_i_15_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[5].g_val_reg0__36_carry_i_16 
       (.I0(cx_q[0]),
        .I1(px_q[40]),
        .I2(cx_q[1]),
        .I3(px_q[41]),
        .I4(px_q[42]),
        .I5(cx_q[2]),
        .O(\genblk1[5].g_val_reg0__36_carry_i_16_n_0 ));
  LUT6 #(
    .INIT(64'h9696699669966969)) 
    \genblk1[5].g_val_reg0__36_carry_i_17 
       (.I0(\genblk1[5].g_val_reg0__36_carry_i_10_n_0 ),
        .I1(cx_q[6]),
        .I2(px_q[46]),
        .I3(px_q[45]),
        .I4(cx_q[5]),
        .I5(\genblk1[5].g_val_reg0__36_carry_i_26_n_0 ),
        .O(\genblk1[5].g_val_reg0__36_carry_i_17_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[5].g_val_reg0__36_carry_i_18 
       (.I0(\genblk1[5].g_val_reg0__36_carry_i_11_n_0 ),
        .I1(cx_q[5]),
        .I2(px_q[45]),
        .I3(\genblk1[5].g_val_reg0__36_carry_i_26_n_0 ),
        .O(\genblk1[5].g_val_reg0__36_carry_i_18_n_0 ));
  LUT6 #(
    .INIT(64'h9969696666969699)) 
    \genblk1[5].g_val_reg0__36_carry_i_19 
       (.I0(cx_q[6]),
        .I1(px_q[46]),
        .I2(px_q[45]),
        .I3(cx_q[5]),
        .I4(\genblk1[5].g_val_reg0__36_carry_i_26_n_0 ),
        .I5(\genblk1[5].g_val_reg0__36_carry_i_14_n_0 ),
        .O(\genblk1[5].g_val_reg0__36_carry_i_19_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0__36_carry_i_2 
       (.I0(\genblk1[5].g_val_reg3__6 [8]),
        .I1(C__4[8]),
        .O(\genblk1[5].g_val_reg0__36_carry_i_2_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[5].g_val_reg0__36_carry_i_20 
       (.I0(cx_q[5]),
        .I1(px_q[45]),
        .I2(\genblk1[5].g_val_reg0__36_carry_i_26_n_0 ),
        .I3(\genblk1[5].g_val_reg0__36_carry_i_15_n_0 ),
        .O(\genblk1[5].g_val_reg0__36_carry_i_20_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0__36_carry_i_21 
       (.I0(\genblk1[5].g_val_reg0__36_carry_i_14_n_0 ),
        .I1(\genblk1[5].g_val_reg0__36_carry_i_16_n_0 ),
        .O(\genblk1[5].g_val_reg0__36_carry_i_21_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[5].g_val_reg0__36_carry_i_22 
       (.I0(\genblk1[5].g_val_reg0__36_carry_i_15_n_0 ),
        .I1(cx_q[1]),
        .I2(px_q[41]),
        .I3(cx_q[0]),
        .I4(px_q[40]),
        .O(\genblk1[5].g_val_reg0__36_carry_i_22_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[5].g_val_reg0__36_carry_i_23 
       (.I0(cx_q[2]),
        .I1(px_q[42]),
        .I2(px_q[41]),
        .I3(cx_q[1]),
        .I4(px_q[40]),
        .I5(cx_q[0]),
        .O(\genblk1[5].g_val_reg0__36_carry_i_23_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[5].g_val_reg0__36_carry_i_24 
       (.I0(px_q[40]),
        .I1(cx_q[0]),
        .I2(px_q[41]),
        .I3(cx_q[1]),
        .O(\genblk1[5].g_val_reg0__36_carry_i_24_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[5].g_val_reg0__36_carry_i_25 
       (.I0(px_q[46]),
        .I1(cx_q[6]),
        .I2(\genblk1[5].g_val_reg0__36_carry_i_26_n_0 ),
        .I3(cx_q[5]),
        .I4(px_q[45]),
        .O(\genblk1[5].g_val_reg0__36_carry_i_25_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[5].g_val_reg0__36_carry_i_26 
       (.I0(px_q[44]),
        .I1(cx_q[4]),
        .I2(\genblk1[5].g_val_reg0__36_carry_i_27_n_0 ),
        .I3(cx_q[3]),
        .I4(px_q[43]),
        .O(\genblk1[5].g_val_reg0__36_carry_i_26_n_0 ));
  LUT6 #(
    .INIT(64'hD4DD4444DDDDD4DD)) 
    \genblk1[5].g_val_reg0__36_carry_i_27 
       (.I0(px_q[42]),
        .I1(cx_q[2]),
        .I2(cx_q[0]),
        .I3(px_q[40]),
        .I4(cx_q[1]),
        .I5(px_q[41]),
        .O(\genblk1[5].g_val_reg0__36_carry_i_27_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0__36_carry_i_3 
       (.I0(\genblk1[5].g_val_reg3__6 [7]),
        .I1(C__4[7]),
        .O(\genblk1[5].g_val_reg0__36_carry_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0__36_carry_i_4 
       (.I0(\genblk1[5].g_val_reg3__6 [6]),
        .I1(C__4[6]),
        .O(\genblk1[5].g_val_reg0__36_carry_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0__36_carry_i_5 
       (.I0(\genblk1[5].g_val_reg3__6 [5]),
        .I1(C__4[5]),
        .O(\genblk1[5].g_val_reg0__36_carry_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0__36_carry_i_6 
       (.I0(\genblk1[5].g_val_reg3__6 [4]),
        .I1(C__4[4]),
        .O(\genblk1[5].g_val_reg0__36_carry_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0__36_carry_i_7 
       (.I0(\genblk1[5].g_val_reg3__6 [3]),
        .I1(C__4[3]),
        .O(\genblk1[5].g_val_reg0__36_carry_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0__36_carry_i_8 
       (.I0(\genblk1[5].g_val_reg3__6 [2]),
        .I1(C__4[2]),
        .O(\genblk1[5].g_val_reg0__36_carry_i_8_n_0 ));
  LUT3 #(
    .INIT(8'h96)) 
    \genblk1[5].g_val_reg0__36_carry_i_9 
       (.I0(px_q[40]),
        .I1(cx_q[0]),
        .I2(C__4[1]),
        .O(\genblk1[5].g_val_reg0__36_carry_i_9_n_0 ));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[5].g_val_reg0_carry 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[5].g_val_reg0_carry_n_0 ,\NLW_genblk1[5].g_val_reg0_carry_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[5].g_val_reg2__1 [8:2],\genblk1[5].g_val_reg0_carry_i_2_n_0 }),
        .O(C__4[8:1]),
        .S({\genblk1[5].g_val_reg0_carry_i_3_n_0 ,\genblk1[5].g_val_reg0_carry_i_4_n_0 ,\genblk1[5].g_val_reg0_carry_i_5_n_0 ,\genblk1[5].g_val_reg0_carry_i_6_n_0 ,\genblk1[5].g_val_reg0_carry_i_7_n_0 ,\genblk1[5].g_val_reg0_carry_i_8_n_0 ,\genblk1[5].g_val_reg0_carry_i_9_n_0 ,\genblk1[5].g_val_reg0_carry_i_10_n_0 }));
  (* ADDER_THRESHOLD = "35" *) 
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[5].g_val_reg0_carry__0 
       (.CI(\genblk1[5].g_val_reg0_carry_n_0 ),
        .CI_TOP(1'b0),
        .CO(\NLW_genblk1[5].g_val_reg0_carry__0_CO_UNCONNECTED [7:0]),
        .DI({\NLW_genblk1[5].g_val_reg0_carry__0_DI_UNCONNECTED [7:5],1'b0,\genblk1[5].g_val_reg0_carry__0_i_1_n_0 ,\genblk1[5].g_val_reg2__1 [11:9]}),
        .O({\NLW_genblk1[5].g_val_reg0_carry__0_O_UNCONNECTED [7:5],C__4[13:9]}),
        .S({\NLW_genblk1[5].g_val_reg0_carry__0_S_UNCONNECTED [7:5],\genblk1[5].g_val_reg0_carry__0_i_3_n_0 ,\genblk1[5].g_val_reg0_carry__0_i_4_n_0 ,\genblk1[5].g_val_reg0_carry__0_i_5_n_0 ,\genblk1[5].g_val_reg0_carry__0_i_6_n_0 ,\genblk1[5].g_val_reg0_carry__0_i_7_n_0 }));
  LUT3 #(
    .INIT(8'h2B)) 
    \genblk1[5].g_val_reg0_carry__0_i_1 
       (.I0(py_q[47]),
        .I1(cy_q[7]),
        .I2(\genblk1[5].g_val_reg0_carry__0_i_8_n_0 ),
        .O(\genblk1[5].g_val_reg0_carry__0_i_1_n_0 ));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[5].g_val_reg0_carry__0_i_2 
       (.CI(\genblk1[5].g_val_reg0_carry_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[5].g_val_reg0_carry__0_i_2_CO_UNCONNECTED [7:2],\genblk1[5].g_val_reg2__1 [11],\NLW_genblk1[5].g_val_reg0_carry__0_i_2_CO_UNCONNECTED [0]}),
        .DI({\NLW_genblk1[5].g_val_reg0_carry__0_i_2_DI_UNCONNECTED [7:2],1'b0,\genblk1[5].g_val_reg0_carry__0_i_1_n_0 }),
        .O({\NLW_genblk1[5].g_val_reg0_carry__0_i_2_O_UNCONNECTED [7:1],\genblk1[5].g_val_reg2__1 [10]}),
        .S({\NLW_genblk1[5].g_val_reg0_carry__0_i_2_S_UNCONNECTED [7:2],1'b1,\genblk1[5].g_val_reg0_carry__0_i_9_n_0 }));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0_carry__0_i_3 
       (.I0(\genblk1[5].g_val_reg0_carry__0_i_1_n_0 ),
        .I1(\genblk1[5].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[5].g_val_reg0_carry__0_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0_carry__0_i_4 
       (.I0(\genblk1[5].g_val_reg0_carry__0_i_1_n_0 ),
        .I1(\genblk1[5].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[5].g_val_reg0_carry__0_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0_carry__0_i_5 
       (.I0(\genblk1[5].g_val_reg2__1 [11]),
        .I1(\genblk1[5].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[5].g_val_reg0_carry__0_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0_carry__0_i_6 
       (.I0(\genblk1[5].g_val_reg2__1 [10]),
        .I1(\genblk1[5].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[5].g_val_reg0_carry__0_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0_carry__0_i_7 
       (.I0(\genblk1[5].g_val_reg2__1 [9]),
        .I1(\genblk1[5].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[5].g_val_reg0_carry__0_i_7_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[5].g_val_reg0_carry__0_i_8 
       (.I0(py_q[46]),
        .I1(cy_q[6]),
        .I2(\genblk1[5].g_val_reg0_carry_i_27_n_0 ),
        .I3(cy_q[5]),
        .I4(py_q[45]),
        .O(\genblk1[5].g_val_reg0_carry__0_i_8_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0_carry__0_i_9 
       (.I0(\genblk1[5].g_val_reg0_carry__0_i_1_n_0 ),
        .I1(\genblk1[5].g_val_reg0_carry_i_11_n_0 ),
        .O(\genblk1[5].g_val_reg0_carry__0_i_9_n_0 ));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[5].g_val_reg0_carry_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[5].g_val_reg0_carry_i_1_n_0 ,\NLW_genblk1[5].g_val_reg0_carry_i_1_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[5].g_val_reg0_carry__0_i_1_n_0 ,\genblk1[5].g_val_reg0_carry_i_11_n_0 ,\genblk1[5].g_val_reg0_carry_i_12_n_0 ,\genblk1[5].g_val_reg0_carry_i_13_n_0 ,\genblk1[5].g_val_reg0_carry_i_14_n_0 ,\genblk1[5].g_val_reg0_carry_i_15_n_0 ,\genblk1[5].g_val_reg0_carry_i_16_n_0 ,1'b0}),
        .O(\genblk1[5].g_val_reg2__1 [9:2]),
        .S({\genblk1[5].g_val_reg0_carry_i_17_n_0 ,\genblk1[5].g_val_reg0_carry_i_18_n_0 ,\genblk1[5].g_val_reg0_carry_i_19_n_0 ,\genblk1[5].g_val_reg0_carry_i_20_n_0 ,\genblk1[5].g_val_reg0_carry_i_21_n_0 ,\genblk1[5].g_val_reg0_carry_i_22_n_0 ,\genblk1[5].g_val_reg0_carry_i_23_n_0 ,\genblk1[5].g_val_reg0_carry_i_24_n_0 }));
  LUT4 #(
    .INIT(16'h6996)) 
    \genblk1[5].g_val_reg0_carry_i_10 
       (.I0(py_q[40]),
        .I1(cy_q[0]),
        .I2(pz_q[15]),
        .I3(cz_q[0]),
        .O(\genblk1[5].g_val_reg0_carry_i_10_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[5].g_val_reg0_carry_i_11 
       (.I0(\genblk1[5].g_val_reg0_carry__0_i_8_n_0 ),
        .I1(py_q[47]),
        .I2(cy_q[7]),
        .O(\genblk1[5].g_val_reg0_carry_i_11_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[5].g_val_reg0_carry_i_12 
       (.I0(\genblk1[5].g_val_reg0_carry_i_27_n_0 ),
        .I1(cy_q[5]),
        .I2(py_q[45]),
        .I3(py_q[46]),
        .I4(cy_q[6]),
        .O(\genblk1[5].g_val_reg0_carry_i_12_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[5].g_val_reg0_carry_i_13 
       (.I0(\genblk1[5].g_val_reg0_carry_i_27_n_0 ),
        .I1(py_q[45]),
        .I2(cy_q[5]),
        .O(\genblk1[5].g_val_reg0_carry_i_13_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[5].g_val_reg0_carry_i_14 
       (.I0(\genblk1[5].g_val_reg0_carry_i_28_n_0 ),
        .I1(cy_q[3]),
        .I2(py_q[43]),
        .I3(py_q[44]),
        .I4(cy_q[4]),
        .O(\genblk1[5].g_val_reg0_carry_i_14_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[5].g_val_reg0_carry_i_15 
       (.I0(\genblk1[5].g_val_reg0_carry_i_28_n_0 ),
        .I1(py_q[43]),
        .I2(cy_q[3]),
        .O(\genblk1[5].g_val_reg0_carry_i_15_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[5].g_val_reg0_carry_i_16 
       (.I0(cy_q[0]),
        .I1(py_q[40]),
        .I2(cy_q[1]),
        .I3(py_q[41]),
        .I4(py_q[42]),
        .I5(cy_q[2]),
        .O(\genblk1[5].g_val_reg0_carry_i_16_n_0 ));
  LUT6 #(
    .INIT(64'h9696699669966969)) 
    \genblk1[5].g_val_reg0_carry_i_17 
       (.I0(\genblk1[5].g_val_reg0_carry__0_i_1_n_0 ),
        .I1(cy_q[6]),
        .I2(py_q[46]),
        .I3(py_q[45]),
        .I4(cy_q[5]),
        .I5(\genblk1[5].g_val_reg0_carry_i_27_n_0 ),
        .O(\genblk1[5].g_val_reg0_carry_i_17_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[5].g_val_reg0_carry_i_18 
       (.I0(\genblk1[5].g_val_reg0_carry_i_11_n_0 ),
        .I1(cy_q[5]),
        .I2(py_q[45]),
        .I3(\genblk1[5].g_val_reg0_carry_i_27_n_0 ),
        .O(\genblk1[5].g_val_reg0_carry_i_18_n_0 ));
  LUT6 #(
    .INIT(64'h9969696666969699)) 
    \genblk1[5].g_val_reg0_carry_i_19 
       (.I0(cy_q[6]),
        .I1(py_q[46]),
        .I2(py_q[45]),
        .I3(cy_q[5]),
        .I4(\genblk1[5].g_val_reg0_carry_i_27_n_0 ),
        .I5(\genblk1[5].g_val_reg0_carry_i_14_n_0 ),
        .O(\genblk1[5].g_val_reg0_carry_i_19_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0_carry_i_2 
       (.I0(py_q[40]),
        .I1(cy_q[0]),
        .O(\genblk1[5].g_val_reg0_carry_i_2_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[5].g_val_reg0_carry_i_20 
       (.I0(cy_q[5]),
        .I1(py_q[45]),
        .I2(\genblk1[5].g_val_reg0_carry_i_27_n_0 ),
        .I3(\genblk1[5].g_val_reg0_carry_i_15_n_0 ),
        .O(\genblk1[5].g_val_reg0_carry_i_20_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0_carry_i_21 
       (.I0(\genblk1[5].g_val_reg0_carry_i_14_n_0 ),
        .I1(\genblk1[5].g_val_reg0_carry_i_16_n_0 ),
        .O(\genblk1[5].g_val_reg0_carry_i_21_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[5].g_val_reg0_carry_i_22 
       (.I0(\genblk1[5].g_val_reg0_carry_i_15_n_0 ),
        .I1(cy_q[1]),
        .I2(py_q[41]),
        .I3(cy_q[0]),
        .I4(py_q[40]),
        .O(\genblk1[5].g_val_reg0_carry_i_22_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[5].g_val_reg0_carry_i_23 
       (.I0(cy_q[2]),
        .I1(py_q[42]),
        .I2(py_q[41]),
        .I3(cy_q[1]),
        .I4(py_q[40]),
        .I5(cy_q[0]),
        .O(\genblk1[5].g_val_reg0_carry_i_23_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[5].g_val_reg0_carry_i_24 
       (.I0(py_q[40]),
        .I1(cy_q[0]),
        .I2(py_q[41]),
        .I3(cy_q[1]),
        .O(\genblk1[5].g_val_reg0_carry_i_24_n_0 ));
  LUT6 #(
    .INIT(64'h2B22BBBB22222B22)) 
    \genblk1[5].g_val_reg0_carry_i_25 
       (.I0(pz_q[17]),
        .I1(cz_q[2]),
        .I2(cz_q[0]),
        .I3(pz_q[15]),
        .I4(cz_q[1]),
        .I5(pz_q[16]),
        .O(\genblk1[5].g_val_reg0_carry_i_25_n_0 ));
  (* OPT_MODIFIED = "RETARGET PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[5].g_val_reg0_carry_i_26 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[5].g_val_reg0_carry_i_26_CO_UNCONNECTED [7:5],\genblk1[5].g_val_reg1 [6],\NLW_genblk1[5].g_val_reg0_carry_i_26_CO_UNCONNECTED [3:0]}),
        .DI({\NLW_genblk1[5].g_val_reg0_carry_i_26_DI_UNCONNECTED [7:5],1'b0,\genblk1[5].g_val_reg0_carry_i_25_n_0 ,\genblk1[5].g_val_reg0_carry_i_25_n_0 ,\genblk1[5].g_val_reg0_carry_i_29_n_0 ,1'b0}),
        .O({\NLW_genblk1[5].g_val_reg0_carry_i_26_O_UNCONNECTED [7:4],\genblk1[5].g_val_reg1 [5:2]}),
        .S({\NLW_genblk1[5].g_val_reg0_carry_i_26_S_UNCONNECTED [7:5],1'b1,\genblk1[5].g_val_reg0_carry_i_30_n_0 ,\genblk1[5].g_val_reg0_carry_i_31_n_0 ,\genblk1[5].g_val_reg0_carry_i_9_0 }));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[5].g_val_reg0_carry_i_27 
       (.I0(py_q[44]),
        .I1(cy_q[4]),
        .I2(\genblk1[5].g_val_reg0_carry_i_28_n_0 ),
        .I3(cy_q[3]),
        .I4(py_q[43]),
        .O(\genblk1[5].g_val_reg0_carry_i_27_n_0 ));
  LUT6 #(
    .INIT(64'hD4DD4444DDDDD4DD)) 
    \genblk1[5].g_val_reg0_carry_i_28 
       (.I0(py_q[42]),
        .I1(cy_q[2]),
        .I2(cy_q[0]),
        .I3(py_q[40]),
        .I4(cy_q[1]),
        .I5(py_q[41]),
        .O(\genblk1[5].g_val_reg0_carry_i_28_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[5].g_val_reg0_carry_i_29 
       (.I0(cz_q[0]),
        .I1(pz_q[15]),
        .I2(cz_q[1]),
        .I3(pz_q[16]),
        .I4(pz_q[17]),
        .I5(cz_q[2]),
        .O(\genblk1[5].g_val_reg0_carry_i_29_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0_carry_i_3 
       (.I0(\genblk1[5].g_val_reg2__1 [8]),
        .I1(\genblk1[5].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[5].g_val_reg0_carry_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0_carry_i_30 
       (.I0(\genblk1[5].g_val_reg0_carry_i_25_n_0 ),
        .I1(\genblk1[5].g_val_reg0_carry_i_29_n_0 ),
        .O(\genblk1[5].g_val_reg0_carry_i_30_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[5].g_val_reg0_carry_i_31 
       (.I0(\genblk1[5].g_val_reg0_carry_i_25_n_0 ),
        .I1(cz_q[1]),
        .I2(pz_q[16]),
        .I3(cz_q[0]),
        .I4(pz_q[15]),
        .O(\genblk1[5].g_val_reg0_carry_i_31_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0_carry_i_4 
       (.I0(\genblk1[5].g_val_reg2__1 [7]),
        .I1(\genblk1[5].g_val_reg0_carry_i_25_n_0 ),
        .O(\genblk1[5].g_val_reg0_carry_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0_carry_i_5 
       (.I0(\genblk1[5].g_val_reg2__1 [6]),
        .I1(\genblk1[5].g_val_reg1 [6]),
        .O(\genblk1[5].g_val_reg0_carry_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0_carry_i_6 
       (.I0(\genblk1[5].g_val_reg2__1 [5]),
        .I1(\genblk1[5].g_val_reg1 [5]),
        .O(\genblk1[5].g_val_reg0_carry_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0_carry_i_7 
       (.I0(\genblk1[5].g_val_reg2__1 [4]),
        .I1(\genblk1[5].g_val_reg1 [4]),
        .O(\genblk1[5].g_val_reg0_carry_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0_carry_i_8 
       (.I0(\genblk1[5].g_val_reg2__1 [3]),
        .I1(\genblk1[5].g_val_reg1 [3]),
        .O(\genblk1[5].g_val_reg0_carry_i_8_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].g_val_reg0_carry_i_9 
       (.I0(\genblk1[5].g_val_reg2__1 [2]),
        .I1(\genblk1[5].g_val_reg1 [2]),
        .O(\genblk1[5].g_val_reg0_carry_i_9_n_0 ));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[5].g_val_reg0_inferred__0/i__carry 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[5].g_val_reg0_inferred__0/i__carry_n_0 ,\NLW_genblk1[5].g_val_reg0_inferred__0/i__carry_CO_UNCONNECTED [6:0]}),
        .DI(cg_q[8:1]),
        .O(\genblk1[5].g_val_reg0 [8:1]),
        .S({i__carry_i_1__5_n_0,i__carry_i_2__4_n_0,i__carry_i_3__4_n_0,i__carry_i_4__4_n_0,i__carry_i_5__4_n_0,i__carry_i_6__4_n_0,i__carry_i_7__4_n_0,i__carry_i_8__4_n_0}));
  (* ADDER_THRESHOLD = "35" *) 
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[5].g_val_reg0_inferred__0/i__carry__0 
       (.CI(\genblk1[5].g_val_reg0_inferred__0/i__carry_n_0 ),
        .CI_TOP(1'b0),
        .CO(\NLW_genblk1[5].g_val_reg0_inferred__0/i__carry__0_CO_UNCONNECTED [7:0]),
        .DI({\NLW_genblk1[5].g_val_reg0_inferred__0/i__carry__0_DI_UNCONNECTED [7:5],1'b0,cg_q[12:9]}),
        .O({\NLW_genblk1[5].g_val_reg0_inferred__0/i__carry__0_O_UNCONNECTED [7:5],\genblk1[5].g_val_reg0 [13:9]}),
        .S({\NLW_genblk1[5].g_val_reg0_inferred__0/i__carry__0_S_UNCONNECTED [7:5],i__carry_i_1_n_0,i__carry_i_2__5_n_0,i__carry_i_3__5_n_0,i__carry_i_4__5_n_0,i__carry_i_5__5_n_0}));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].g_val_reg[70] 
       (.C(clk_global),
        .CE(valid_q),
        .D(cg_q[0]),
        .Q(g[65]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].g_val_reg[71] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].g_val_reg0 [1]),
        .Q(g[66]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].g_val_reg[72] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].g_val_reg0 [2]),
        .Q(g[67]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].g_val_reg[73] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].g_val_reg0 [3]),
        .Q(g[68]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].g_val_reg[74] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].g_val_reg0 [4]),
        .Q(g[69]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].g_val_reg[75] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].g_val_reg0 [5]),
        .Q(g[70]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].g_val_reg[76] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].g_val_reg0 [6]),
        .Q(g[71]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].g_val_reg[77] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].g_val_reg0 [7]),
        .Q(g[72]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].g_val_reg[78] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].g_val_reg0 [8]),
        .Q(g[73]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].g_val_reg[79] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].g_val_reg0 [9]),
        .Q(g[74]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].g_val_reg[80] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].g_val_reg0 [10]),
        .Q(g[75]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].g_val_reg[81] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].g_val_reg0 [11]),
        .Q(g[76]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].g_val_reg[82] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].g_val_reg0 [12]),
        .Q(g[77]),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].g_val_reg[83] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].g_val_reg0 [13]),
        .Q(g[78]),
        .R(reset_q));
  (* SOFT_HLUTNM = "soft_lutpair8" *) 
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].h_val_x_reg[71]_i_1 
       (.I0(px_q[40]),
        .I1(ex_q[0]),
        .O(\genblk1[5].h_val_x_reg[71]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h9969696666969699)) 
    \genblk1[5].h_val_x_reg[79]_i_10 
       (.I0(ex_q[6]),
        .I1(px_q[46]),
        .I2(px_q[45]),
        .I3(ex_q[5]),
        .I4(\genblk1[5].h_val_x_reg[83]_i_3_n_0 ),
        .I5(\genblk1[5].h_val_x_reg[79]_i_5_n_0 ),
        .O(\genblk1[5].h_val_x_reg[79]_i_10_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[5].h_val_x_reg[79]_i_11 
       (.I0(ex_q[5]),
        .I1(px_q[45]),
        .I2(\genblk1[5].h_val_x_reg[83]_i_3_n_0 ),
        .I3(\genblk1[5].h_val_x_reg[79]_i_6_n_0 ),
        .O(\genblk1[5].h_val_x_reg[79]_i_11_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].h_val_x_reg[79]_i_12 
       (.I0(\genblk1[5].h_val_x_reg[79]_i_5_n_0 ),
        .I1(\genblk1[5].h_val_x_reg[79]_i_7_n_0 ),
        .O(\genblk1[5].h_val_x_reg[79]_i_12_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[5].h_val_x_reg[79]_i_13 
       (.I0(\genblk1[5].h_val_x_reg[79]_i_6_n_0 ),
        .I1(ex_q[1]),
        .I2(px_q[41]),
        .I3(ex_q[0]),
        .I4(px_q[40]),
        .O(\genblk1[5].h_val_x_reg[79]_i_13_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[5].h_val_x_reg[79]_i_14 
       (.I0(ex_q[2]),
        .I1(px_q[42]),
        .I2(px_q[41]),
        .I3(ex_q[1]),
        .I4(px_q[40]),
        .I5(ex_q[0]),
        .O(\genblk1[5].h_val_x_reg[79]_i_14_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[5].h_val_x_reg[79]_i_15 
       (.I0(px_q[40]),
        .I1(ex_q[0]),
        .I2(px_q[41]),
        .I3(ex_q[1]),
        .O(\genblk1[5].h_val_x_reg[79]_i_15_n_0 ));
  LUT6 #(
    .INIT(64'hD4DD4444DDDDD4DD)) 
    \genblk1[5].h_val_x_reg[79]_i_16 
       (.I0(px_q[42]),
        .I1(ex_q[2]),
        .I2(ex_q[0]),
        .I3(px_q[40]),
        .I4(ex_q[1]),
        .I5(px_q[41]),
        .O(\genblk1[5].h_val_x_reg[79]_i_16_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[5].h_val_x_reg[79]_i_2 
       (.I0(\genblk1[5].h_val_x_reg[83]_i_2_n_0 ),
        .I1(px_q[47]),
        .I2(ex_q[7]),
        .O(\genblk1[5].h_val_x_reg[79]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[5].h_val_x_reg[79]_i_3 
       (.I0(\genblk1[5].h_val_x_reg[83]_i_3_n_0 ),
        .I1(ex_q[5]),
        .I2(px_q[45]),
        .I3(px_q[46]),
        .I4(ex_q[6]),
        .O(\genblk1[5].h_val_x_reg[79]_i_3_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[5].h_val_x_reg[79]_i_4 
       (.I0(\genblk1[5].h_val_x_reg[83]_i_3_n_0 ),
        .I1(px_q[45]),
        .I2(ex_q[5]),
        .O(\genblk1[5].h_val_x_reg[79]_i_4_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[5].h_val_x_reg[79]_i_5 
       (.I0(\genblk1[5].h_val_x_reg[79]_i_16_n_0 ),
        .I1(ex_q[3]),
        .I2(px_q[43]),
        .I3(px_q[44]),
        .I4(ex_q[4]),
        .O(\genblk1[5].h_val_x_reg[79]_i_5_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[5].h_val_x_reg[79]_i_6 
       (.I0(\genblk1[5].h_val_x_reg[79]_i_16_n_0 ),
        .I1(px_q[43]),
        .I2(ex_q[3]),
        .O(\genblk1[5].h_val_x_reg[79]_i_6_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[5].h_val_x_reg[79]_i_7 
       (.I0(ex_q[0]),
        .I1(px_q[40]),
        .I2(ex_q[1]),
        .I3(px_q[41]),
        .I4(px_q[42]),
        .I5(ex_q[2]),
        .O(\genblk1[5].h_val_x_reg[79]_i_7_n_0 ));
  LUT6 #(
    .INIT(64'h9696699669966969)) 
    \genblk1[5].h_val_x_reg[79]_i_8 
       (.I0(\genblk1[5].h_val_x_reg[83]_i_1_n_0 ),
        .I1(ex_q[6]),
        .I2(px_q[46]),
        .I3(px_q[45]),
        .I4(ex_q[5]),
        .I5(\genblk1[5].h_val_x_reg[83]_i_3_n_0 ),
        .O(\genblk1[5].h_val_x_reg[79]_i_8_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[5].h_val_x_reg[79]_i_9 
       (.I0(\genblk1[5].h_val_x_reg[79]_i_2_n_0 ),
        .I1(ex_q[5]),
        .I2(px_q[45]),
        .I3(\genblk1[5].h_val_x_reg[83]_i_3_n_0 ),
        .O(\genblk1[5].h_val_x_reg[79]_i_9_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].h_val_x_reg[81]_i_2 
       (.I0(\genblk1[5].h_val_x_reg[83]_i_1_n_0 ),
        .I1(\genblk1[5].h_val_x_reg[79]_i_2_n_0 ),
        .O(\genblk1[5].h_val_x_reg[81]_i_2_n_0 ));
  LUT3 #(
    .INIT(8'h2B)) 
    \genblk1[5].h_val_x_reg[83]_i_1 
       (.I0(px_q[47]),
        .I1(ex_q[7]),
        .I2(\genblk1[5].h_val_x_reg[83]_i_2_n_0 ),
        .O(\genblk1[5].h_val_x_reg[83]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[5].h_val_x_reg[83]_i_2 
       (.I0(px_q[46]),
        .I1(ex_q[6]),
        .I2(\genblk1[5].h_val_x_reg[83]_i_3_n_0 ),
        .I3(ex_q[5]),
        .I4(px_q[45]),
        .O(\genblk1[5].h_val_x_reg[83]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[5].h_val_x_reg[83]_i_3 
       (.I0(px_q[44]),
        .I1(ex_q[4]),
        .I2(\genblk1[5].h_val_x_reg[79]_i_16_n_0 ),
        .I3(ex_q[3]),
        .I4(px_q[43]),
        .O(\genblk1[5].h_val_x_reg[83]_i_3_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_x_reg_reg[71] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_x_reg[71]_i_1_n_0 ),
        .Q(\genblk1[5].h_val_x_reg_reg_n_0_[71] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_x_reg_reg[72] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_x_reg_reg0 [2]),
        .Q(\genblk1[5].h_val_x_reg_reg_n_0_[72] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_x_reg_reg[73] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_x_reg_reg0 [3]),
        .Q(\genblk1[5].h_val_x_reg_reg_n_0_[73] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_x_reg_reg[74] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_x_reg_reg0 [4]),
        .Q(\genblk1[5].h_val_x_reg_reg_n_0_[74] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_x_reg_reg[75] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_x_reg_reg0 [5]),
        .Q(\genblk1[5].h_val_x_reg_reg_n_0_[75] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_x_reg_reg[76] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_x_reg_reg0 [6]),
        .Q(\genblk1[5].h_val_x_reg_reg_n_0_[76] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_x_reg_reg[77] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_x_reg_reg0 [7]),
        .Q(\genblk1[5].h_val_x_reg_reg_n_0_[77] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_x_reg_reg[78] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_x_reg_reg0 [8]),
        .Q(\genblk1[5].h_val_x_reg_reg_n_0_[78] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_x_reg_reg[79] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_x_reg_reg0 [9]),
        .Q(\genblk1[5].h_val_x_reg_reg_n_0_[79] ),
        .R(reset_q));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[5].h_val_x_reg_reg[79]_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[5].h_val_x_reg_reg[79]_i_1_n_0 ,\NLW_genblk1[5].h_val_x_reg_reg[79]_i_1_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[5].h_val_x_reg[83]_i_1_n_0 ,\genblk1[5].h_val_x_reg[79]_i_2_n_0 ,\genblk1[5].h_val_x_reg[79]_i_3_n_0 ,\genblk1[5].h_val_x_reg[79]_i_4_n_0 ,\genblk1[5].h_val_x_reg[79]_i_5_n_0 ,\genblk1[5].h_val_x_reg[79]_i_6_n_0 ,\genblk1[5].h_val_x_reg[79]_i_7_n_0 ,1'b0}),
        .O(\genblk1[5].h_val_x_reg_reg0 [9:2]),
        .S({\genblk1[5].h_val_x_reg[79]_i_8_n_0 ,\genblk1[5].h_val_x_reg[79]_i_9_n_0 ,\genblk1[5].h_val_x_reg[79]_i_10_n_0 ,\genblk1[5].h_val_x_reg[79]_i_11_n_0 ,\genblk1[5].h_val_x_reg[79]_i_12_n_0 ,\genblk1[5].h_val_x_reg[79]_i_13_n_0 ,\genblk1[5].h_val_x_reg[79]_i_14_n_0 ,\genblk1[5].h_val_x_reg[79]_i_15_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_x_reg_reg[80] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_x_reg_reg0 [10]),
        .Q(\genblk1[5].h_val_x_reg_reg_n_0_[80] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_x_reg_reg[81] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_x_reg_reg0 [11]),
        .Q(\genblk1[5].h_val_x_reg_reg_n_0_[81] ),
        .R(reset_q));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[5].h_val_x_reg_reg[81]_i_1 
       (.CI(\genblk1[5].h_val_x_reg_reg[79]_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[5].h_val_x_reg_reg[81]_i_1_CO_UNCONNECTED [7:2],\genblk1[5].h_val_x_reg_reg0 [11],\NLW_genblk1[5].h_val_x_reg_reg[81]_i_1_CO_UNCONNECTED [0]}),
        .DI({\NLW_genblk1[5].h_val_x_reg_reg[81]_i_1_DI_UNCONNECTED [7:2],1'b0,\genblk1[5].h_val_x_reg[83]_i_1_n_0 }),
        .O({\NLW_genblk1[5].h_val_x_reg_reg[81]_i_1_O_UNCONNECTED [7:1],\genblk1[5].h_val_x_reg_reg0 [10]}),
        .S({\NLW_genblk1[5].h_val_x_reg_reg[81]_i_1_S_UNCONNECTED [7:2],1'b1,\genblk1[5].h_val_x_reg[81]_i_2_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_x_reg_reg[83] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_x_reg[83]_i_1_n_0 ),
        .Q(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .R(reset_q));
  (* SOFT_HLUTNM = "soft_lutpair7" *) 
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].h_val_y_reg[71]_i_1 
       (.I0(py_q[40]),
        .I1(ey_q[0]),
        .O(\genblk1[5].h_val_y_reg[71]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h9969696666969699)) 
    \genblk1[5].h_val_y_reg[79]_i_10 
       (.I0(ey_q[6]),
        .I1(py_q[46]),
        .I2(py_q[45]),
        .I3(ey_q[5]),
        .I4(\genblk1[5].h_val_y_reg[83]_i_3_n_0 ),
        .I5(\genblk1[5].h_val_y_reg[79]_i_5_n_0 ),
        .O(\genblk1[5].h_val_y_reg[79]_i_10_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[5].h_val_y_reg[79]_i_11 
       (.I0(ey_q[5]),
        .I1(py_q[45]),
        .I2(\genblk1[5].h_val_y_reg[83]_i_3_n_0 ),
        .I3(\genblk1[5].h_val_y_reg[79]_i_6_n_0 ),
        .O(\genblk1[5].h_val_y_reg[79]_i_11_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].h_val_y_reg[79]_i_12 
       (.I0(\genblk1[5].h_val_y_reg[79]_i_5_n_0 ),
        .I1(\genblk1[5].h_val_y_reg[79]_i_7_n_0 ),
        .O(\genblk1[5].h_val_y_reg[79]_i_12_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[5].h_val_y_reg[79]_i_13 
       (.I0(\genblk1[5].h_val_y_reg[79]_i_6_n_0 ),
        .I1(ey_q[1]),
        .I2(py_q[41]),
        .I3(ey_q[0]),
        .I4(py_q[40]),
        .O(\genblk1[5].h_val_y_reg[79]_i_13_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[5].h_val_y_reg[79]_i_14 
       (.I0(ey_q[2]),
        .I1(py_q[42]),
        .I2(py_q[41]),
        .I3(ey_q[1]),
        .I4(py_q[40]),
        .I5(ey_q[0]),
        .O(\genblk1[5].h_val_y_reg[79]_i_14_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[5].h_val_y_reg[79]_i_15 
       (.I0(py_q[40]),
        .I1(ey_q[0]),
        .I2(py_q[41]),
        .I3(ey_q[1]),
        .O(\genblk1[5].h_val_y_reg[79]_i_15_n_0 ));
  LUT6 #(
    .INIT(64'hD4DD4444DDDDD4DD)) 
    \genblk1[5].h_val_y_reg[79]_i_16 
       (.I0(py_q[42]),
        .I1(ey_q[2]),
        .I2(ey_q[0]),
        .I3(py_q[40]),
        .I4(ey_q[1]),
        .I5(py_q[41]),
        .O(\genblk1[5].h_val_y_reg[79]_i_16_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[5].h_val_y_reg[79]_i_2 
       (.I0(\genblk1[5].h_val_y_reg[83]_i_2_n_0 ),
        .I1(py_q[47]),
        .I2(ey_q[7]),
        .O(\genblk1[5].h_val_y_reg[79]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[5].h_val_y_reg[79]_i_3 
       (.I0(\genblk1[5].h_val_y_reg[83]_i_3_n_0 ),
        .I1(ey_q[5]),
        .I2(py_q[45]),
        .I3(py_q[46]),
        .I4(ey_q[6]),
        .O(\genblk1[5].h_val_y_reg[79]_i_3_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[5].h_val_y_reg[79]_i_4 
       (.I0(\genblk1[5].h_val_y_reg[83]_i_3_n_0 ),
        .I1(py_q[45]),
        .I2(ey_q[5]),
        .O(\genblk1[5].h_val_y_reg[79]_i_4_n_0 ));
  LUT5 #(
    .INIT(32'h718E8E71)) 
    \genblk1[5].h_val_y_reg[79]_i_5 
       (.I0(\genblk1[5].h_val_y_reg[79]_i_16_n_0 ),
        .I1(ey_q[3]),
        .I2(py_q[43]),
        .I3(py_q[44]),
        .I4(ey_q[4]),
        .O(\genblk1[5].h_val_y_reg[79]_i_5_n_0 ));
  LUT3 #(
    .INIT(8'h69)) 
    \genblk1[5].h_val_y_reg[79]_i_6 
       (.I0(\genblk1[5].h_val_y_reg[79]_i_16_n_0 ),
        .I1(py_q[43]),
        .I2(ey_q[3]),
        .O(\genblk1[5].h_val_y_reg[79]_i_6_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[5].h_val_y_reg[79]_i_7 
       (.I0(ey_q[0]),
        .I1(py_q[40]),
        .I2(ey_q[1]),
        .I3(py_q[41]),
        .I4(py_q[42]),
        .I5(ey_q[2]),
        .O(\genblk1[5].h_val_y_reg[79]_i_7_n_0 ));
  LUT6 #(
    .INIT(64'h9696699669966969)) 
    \genblk1[5].h_val_y_reg[79]_i_8 
       (.I0(\genblk1[5].h_val_y_reg[83]_i_1_n_0 ),
        .I1(ey_q[6]),
        .I2(py_q[46]),
        .I3(py_q[45]),
        .I4(ey_q[5]),
        .I5(\genblk1[5].h_val_y_reg[83]_i_3_n_0 ),
        .O(\genblk1[5].h_val_y_reg[79]_i_8_n_0 ));
  LUT4 #(
    .INIT(16'h9669)) 
    \genblk1[5].h_val_y_reg[79]_i_9 
       (.I0(\genblk1[5].h_val_y_reg[79]_i_2_n_0 ),
        .I1(ey_q[5]),
        .I2(py_q[45]),
        .I3(\genblk1[5].h_val_y_reg[83]_i_3_n_0 ),
        .O(\genblk1[5].h_val_y_reg[79]_i_9_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].h_val_y_reg[81]_i_2 
       (.I0(\genblk1[5].h_val_y_reg[83]_i_1_n_0 ),
        .I1(\genblk1[5].h_val_y_reg[79]_i_2_n_0 ),
        .O(\genblk1[5].h_val_y_reg[81]_i_2_n_0 ));
  LUT3 #(
    .INIT(8'h2B)) 
    \genblk1[5].h_val_y_reg[83]_i_1 
       (.I0(py_q[47]),
        .I1(ey_q[7]),
        .I2(\genblk1[5].h_val_y_reg[83]_i_2_n_0 ),
        .O(\genblk1[5].h_val_y_reg[83]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[5].h_val_y_reg[83]_i_2 
       (.I0(py_q[46]),
        .I1(ey_q[6]),
        .I2(\genblk1[5].h_val_y_reg[83]_i_3_n_0 ),
        .I3(ey_q[5]),
        .I4(py_q[45]),
        .O(\genblk1[5].h_val_y_reg[83]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'hD444DDD4)) 
    \genblk1[5].h_val_y_reg[83]_i_3 
       (.I0(py_q[44]),
        .I1(ey_q[4]),
        .I2(\genblk1[5].h_val_y_reg[79]_i_16_n_0 ),
        .I3(ey_q[3]),
        .I4(py_q[43]),
        .O(\genblk1[5].h_val_y_reg[83]_i_3_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_y_reg_reg[71] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_y_reg[71]_i_1_n_0 ),
        .Q(\genblk1[5].h_val_y_reg_reg_n_0_[71] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_y_reg_reg[72] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_y_reg_reg0 [2]),
        .Q(\genblk1[5].h_val_y_reg_reg_n_0_[72] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_y_reg_reg[73] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_y_reg_reg0 [3]),
        .Q(\genblk1[5].h_val_y_reg_reg_n_0_[73] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_y_reg_reg[74] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_y_reg_reg0 [4]),
        .Q(\genblk1[5].h_val_y_reg_reg_n_0_[74] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_y_reg_reg[75] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_y_reg_reg0 [5]),
        .Q(\genblk1[5].h_val_y_reg_reg_n_0_[75] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_y_reg_reg[76] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_y_reg_reg0 [6]),
        .Q(\genblk1[5].h_val_y_reg_reg_n_0_[76] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_y_reg_reg[77] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_y_reg_reg0 [7]),
        .Q(\genblk1[5].h_val_y_reg_reg_n_0_[77] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_y_reg_reg[78] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_y_reg_reg0 [8]),
        .Q(\genblk1[5].h_val_y_reg_reg_n_0_[78] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_y_reg_reg[79] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_y_reg_reg0 [9]),
        .Q(\genblk1[5].h_val_y_reg_reg_n_0_[79] ),
        .R(reset_q));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[5].h_val_y_reg_reg[79]_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\genblk1[5].h_val_y_reg_reg[79]_i_1_n_0 ,\NLW_genblk1[5].h_val_y_reg_reg[79]_i_1_CO_UNCONNECTED [6:0]}),
        .DI({\genblk1[5].h_val_y_reg[83]_i_1_n_0 ,\genblk1[5].h_val_y_reg[79]_i_2_n_0 ,\genblk1[5].h_val_y_reg[79]_i_3_n_0 ,\genblk1[5].h_val_y_reg[79]_i_4_n_0 ,\genblk1[5].h_val_y_reg[79]_i_5_n_0 ,\genblk1[5].h_val_y_reg[79]_i_6_n_0 ,\genblk1[5].h_val_y_reg[79]_i_7_n_0 ,1'b0}),
        .O(\genblk1[5].h_val_y_reg_reg0 [9:2]),
        .S({\genblk1[5].h_val_y_reg[79]_i_8_n_0 ,\genblk1[5].h_val_y_reg[79]_i_9_n_0 ,\genblk1[5].h_val_y_reg[79]_i_10_n_0 ,\genblk1[5].h_val_y_reg[79]_i_11_n_0 ,\genblk1[5].h_val_y_reg[79]_i_12_n_0 ,\genblk1[5].h_val_y_reg[79]_i_13_n_0 ,\genblk1[5].h_val_y_reg[79]_i_14_n_0 ,\genblk1[5].h_val_y_reg[79]_i_15_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_y_reg_reg[80] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_y_reg_reg0 [10]),
        .Q(\genblk1[5].h_val_y_reg_reg_n_0_[80] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_y_reg_reg[81] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_y_reg_reg0 [11]),
        .Q(\genblk1[5].h_val_y_reg_reg_n_0_[81] ),
        .R(reset_q));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[5].h_val_y_reg_reg[81]_i_1 
       (.CI(\genblk1[5].h_val_y_reg_reg[79]_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[5].h_val_y_reg_reg[81]_i_1_CO_UNCONNECTED [7:2],\genblk1[5].h_val_y_reg_reg0 [11],\NLW_genblk1[5].h_val_y_reg_reg[81]_i_1_CO_UNCONNECTED [0]}),
        .DI({\NLW_genblk1[5].h_val_y_reg_reg[81]_i_1_DI_UNCONNECTED [7:2],1'b0,\genblk1[5].h_val_y_reg[83]_i_1_n_0 }),
        .O({\NLW_genblk1[5].h_val_y_reg_reg[81]_i_1_O_UNCONNECTED [7:1],\genblk1[5].h_val_y_reg_reg0 [10]}),
        .S({\NLW_genblk1[5].h_val_y_reg_reg[81]_i_1_S_UNCONNECTED [7:2],1'b1,\genblk1[5].h_val_y_reg[81]_i_2_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_y_reg_reg[83] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_y_reg[83]_i_1_n_0 ),
        .Q(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .R(reset_q));
  (* SOFT_HLUTNM = "soft_lutpair6" *) 
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].h_val_z_reg[71]_i_1 
       (.I0(pz_q[15]),
        .I1(ez_q[0]),
        .O(\genblk1[5].h_val_z_reg[71]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h4F04B0FBB0FB4F04)) 
    \genblk1[5].h_val_z_reg[76]_i_2 
       (.I0(ez_q[0]),
        .I1(pz_q[15]),
        .I2(ez_q[1]),
        .I3(pz_q[16]),
        .I4(pz_q[17]),
        .I5(ez_q[2]),
        .O(\genblk1[5].h_val_z_reg[76]_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \genblk1[5].h_val_z_reg[76]_i_3 
       (.I0(\genblk1[5].h_val_z_reg[83]_i_1_n_0 ),
        .I1(\genblk1[5].h_val_z_reg[76]_i_2_n_0 ),
        .O(\genblk1[5].h_val_z_reg[76]_i_3_n_0 ));
  LUT5 #(
    .INIT(32'h96699696)) 
    \genblk1[5].h_val_z_reg[76]_i_4 
       (.I0(\genblk1[5].h_val_z_reg[83]_i_1_n_0 ),
        .I1(ez_q[1]),
        .I2(pz_q[16]),
        .I3(ez_q[0]),
        .I4(pz_q[15]),
        .O(\genblk1[5].h_val_z_reg[76]_i_4_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[5].h_val_z_reg[76]_i_5 
       (.I0(ez_q[2]),
        .I1(pz_q[17]),
        .I2(pz_q[16]),
        .I3(ez_q[1]),
        .I4(pz_q[15]),
        .I5(ez_q[0]),
        .O(\genblk1[5].h_val_z_reg[76]_i_5_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[5].h_val_z_reg[76]_i_6 
       (.I0(pz_q[15]),
        .I1(ez_q[0]),
        .I2(pz_q[16]),
        .I3(ez_q[1]),
        .O(\genblk1[5].h_val_z_reg[76]_i_6_n_0 ));
  LUT6 #(
    .INIT(64'h2B22BBBB22222B22)) 
    \genblk1[5].h_val_z_reg[83]_i_1 
       (.I0(pz_q[17]),
        .I1(ez_q[2]),
        .I2(ez_q[0]),
        .I3(pz_q[15]),
        .I4(ez_q[1]),
        .I5(pz_q[16]),
        .O(\genblk1[5].h_val_z_reg[83]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_z_reg_reg[71] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_z_reg[71]_i_1_n_0 ),
        .Q(\genblk1[5].h_val_z_reg_reg_n_0_[71] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_z_reg_reg[72] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_z_reg_reg0 [2]),
        .Q(\genblk1[5].h_val_z_reg_reg_n_0_[72] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_z_reg_reg[73] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_z_reg_reg0 [3]),
        .Q(\genblk1[5].h_val_z_reg_reg_n_0_[73] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_z_reg_reg[74] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_z_reg_reg0 [4]),
        .Q(\genblk1[5].h_val_z_reg_reg_n_0_[74] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_z_reg_reg[75] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_z_reg_reg0 [5]),
        .Q(\genblk1[5].h_val_z_reg_reg_n_0_[75] ),
        .R(reset_q));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_z_reg_reg[76] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_z_reg_reg0 [6]),
        .Q(\genblk1[5].h_val_z_reg_reg_n_0_[76] ),
        .R(reset_q));
  (* OPT_MODIFIED = "RETARGET PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    \genblk1[5].h_val_z_reg_reg[76]_i_1 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\NLW_genblk1[5].h_val_z_reg_reg[76]_i_1_CO_UNCONNECTED [7:5],\genblk1[5].h_val_z_reg_reg0 [6],\NLW_genblk1[5].h_val_z_reg_reg[76]_i_1_CO_UNCONNECTED [3:0]}),
        .DI({\NLW_genblk1[5].h_val_z_reg_reg[76]_i_1_DI_UNCONNECTED [7:5],1'b0,\genblk1[5].h_val_z_reg[83]_i_1_n_0 ,\genblk1[5].h_val_z_reg[83]_i_1_n_0 ,\genblk1[5].h_val_z_reg[76]_i_2_n_0 ,1'b0}),
        .O({\NLW_genblk1[5].h_val_z_reg_reg[76]_i_1_O_UNCONNECTED [7:4],\genblk1[5].h_val_z_reg_reg0 [5:2]}),
        .S({\NLW_genblk1[5].h_val_z_reg_reg[76]_i_1_S_UNCONNECTED [7:5],1'b1,\genblk1[5].h_val_z_reg[76]_i_3_n_0 ,\genblk1[5].h_val_z_reg[76]_i_4_n_0 ,\genblk1[5].h_val_z_reg[76]_i_5_n_0 ,\genblk1[5].h_val_z_reg[76]_i_6_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \genblk1[5].h_val_z_reg_reg[83] 
       (.C(clk_global),
        .CE(valid_q),
        .D(\genblk1[5].h_val_z_reg[83]_i_1_n_0 ),
        .Q(\genblk1[5].h_val_z_reg_reg_n_0_[83] ),
        .R(reset_q));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    h_val_0__1_carry
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({h_val_0__1_carry_n_0,NLW_h_val_0__1_carry_CO_UNCONNECTED[6:0]}),
        .DI({h_val_0__1_carry_i_1_n_0,h_val_0__1_carry_i_2_n_0,h_val_0__1_carry_i_3_n_0,h_val_0__1_carry_i_4_n_0,h_val_0__1_carry_i_5_n_0,h_val_0__1_carry_i_6_n_0,h_val_0__1_carry_i_7_n_0,p_5_in}),
        .O({h_val_0__40[7:1],NLW_h_val_0__1_carry_O_UNCONNECTED[0]}),
        .S({h_val_0__1_carry_i_8_n_0,h_val_0__1_carry_i_9_n_0,h_val_0__1_carry_i_10_n_0,h_val_0__1_carry_i_11_n_0,h_val_0__1_carry_i_12_n_0,h_val_0__1_carry_i_13_n_0,h_val_0__1_carry_i_14_n_0,1'b0}));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    h_val_0__1_carry__0
       (.CI(h_val_0__1_carry_n_0),
        .CI_TOP(1'b0),
        .CO({NLW_h_val_0__1_carry__0_CO_UNCONNECTED[7:6],h_val_0__40[13],NLW_h_val_0__1_carry__0_CO_UNCONNECTED[4:0]}),
        .DI({NLW_h_val_0__1_carry__0_DI_UNCONNECTED[7:6],1'b0,h_val_0__1_carry__0_i_1_n_0,h_val_0__1_carry__0_i_2_n_0,h_val_0__1_carry__0_i_3_n_0,h_val_0__1_carry__0_i_4_n_0,h_val_0__1_carry__0_i_5_n_0}),
        .O({NLW_h_val_0__1_carry__0_O_UNCONNECTED[7:5],h_val_0__40[12:8]}),
        .S({NLW_h_val_0__1_carry__0_S_UNCONNECTED[7:6],1'b1,h_val_0__1_carry__0_i_6_n_0,h_val_0__1_carry__0_i_7_n_0,h_val_0__1_carry__0_i_8_n_0,h_val_0__1_carry__0_i_9_n_0,h_val_0__1_carry__0_i_10_n_0}));
  LUT6 #(
    .INIT(64'h0210400810020840)) 
    h_val_0__1_carry__0_i_1
       (.I0(\genblk1[0].h_val_x_reg_reg_n_0_[10] ),
        .I1(\genblk1[0].h_val_y_reg_reg_n_0_[10] ),
        .I2(p_5_in),
        .I3(\genblk1[0].h_val_x_reg_reg_n_0_[11] ),
        .I4(p_3_in),
        .I5(\genblk1[0].h_val_y_reg_reg_n_0_[11] ),
        .O(h_val_0__1_carry__0_i_1_n_0));
  LUT6 #(
    .INIT(64'h6666699669966666)) 
    h_val_0__1_carry__0_i_10
       (.I0(h_val_0__1_carry__0_i_5_n_0),
        .I1(h_val_0__1_carry__0_i_14_n_0),
        .I2(\genblk1[0].h_val_y_reg_reg_n_0_[7] ),
        .I3(p_3_in),
        .I4(\genblk1[0].h_val_x_reg_reg_n_0_[7] ),
        .I5(p_5_in),
        .O(h_val_0__1_carry__0_i_10_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_0__1_carry__0_i_11
       (.I0(\genblk1[0].h_val_y_reg_reg_n_0_[11] ),
        .I1(p_3_in),
        .I2(\genblk1[0].h_val_x_reg_reg_n_0_[11] ),
        .I3(p_5_in),
        .O(h_val_0__1_carry__0_i_11_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_0__1_carry__0_i_12
       (.I0(\genblk1[0].h_val_y_reg_reg_n_0_[10] ),
        .I1(p_3_in),
        .I2(\genblk1[0].h_val_x_reg_reg_n_0_[10] ),
        .I3(p_5_in),
        .O(h_val_0__1_carry__0_i_12_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_0__1_carry__0_i_13
       (.I0(\genblk1[0].h_val_y_reg_reg_n_0_[9] ),
        .I1(p_3_in),
        .I2(\genblk1[0].h_val_x_reg_reg_n_0_[9] ),
        .I3(p_5_in),
        .O(h_val_0__1_carry__0_i_13_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_0__1_carry__0_i_14
       (.I0(\genblk1[0].h_val_y_reg_reg_n_0_[8] ),
        .I1(p_3_in),
        .I2(\genblk1[0].h_val_x_reg_reg_n_0_[8] ),
        .I3(p_5_in),
        .O(h_val_0__1_carry__0_i_14_n_0));
  LUT6 #(
    .INIT(64'h0210400810020840)) 
    h_val_0__1_carry__0_i_2
       (.I0(\genblk1[0].h_val_x_reg_reg_n_0_[9] ),
        .I1(\genblk1[0].h_val_y_reg_reg_n_0_[9] ),
        .I2(p_5_in),
        .I3(\genblk1[0].h_val_x_reg_reg_n_0_[10] ),
        .I4(p_3_in),
        .I5(\genblk1[0].h_val_y_reg_reg_n_0_[10] ),
        .O(h_val_0__1_carry__0_i_2_n_0));
  LUT6 #(
    .INIT(64'h0210400810020840)) 
    h_val_0__1_carry__0_i_3
       (.I0(\genblk1[0].h_val_x_reg_reg_n_0_[8] ),
        .I1(\genblk1[0].h_val_y_reg_reg_n_0_[8] ),
        .I2(p_5_in),
        .I3(\genblk1[0].h_val_x_reg_reg_n_0_[9] ),
        .I4(p_3_in),
        .I5(\genblk1[0].h_val_y_reg_reg_n_0_[9] ),
        .O(h_val_0__1_carry__0_i_3_n_0));
  LUT6 #(
    .INIT(64'h0210400810020840)) 
    h_val_0__1_carry__0_i_4
       (.I0(\genblk1[0].h_val_x_reg_reg_n_0_[7] ),
        .I1(\genblk1[0].h_val_y_reg_reg_n_0_[7] ),
        .I2(p_5_in),
        .I3(\genblk1[0].h_val_x_reg_reg_n_0_[8] ),
        .I4(p_3_in),
        .I5(\genblk1[0].h_val_y_reg_reg_n_0_[8] ),
        .O(h_val_0__1_carry__0_i_4_n_0));
  LUT5 #(
    .INIT(32'h69960000)) 
    h_val_0__1_carry__0_i_5
       (.I0(p_5_in),
        .I1(\genblk1[0].h_val_x_reg_reg_n_0_[7] ),
        .I2(p_3_in),
        .I3(\genblk1[0].h_val_y_reg_reg_n_0_[7] ),
        .I4(h_val_0__1_carry_i_24_n_0),
        .O(h_val_0__1_carry__0_i_5_n_0));
  LUT6 #(
    .INIT(64'h04102FF81FF40820)) 
    h_val_0__1_carry__0_i_6
       (.I0(\genblk1[0].h_val_y_reg_reg_n_0_[10] ),
        .I1(\genblk1[0].h_val_x_reg_reg_n_0_[10] ),
        .I2(p_5_in),
        .I3(\genblk1[0].h_val_x_reg_reg_n_0_[11] ),
        .I4(p_3_in),
        .I5(\genblk1[0].h_val_y_reg_reg_n_0_[11] ),
        .O(h_val_0__1_carry__0_i_6_n_0));
  LUT6 #(
    .INIT(64'h6666699669966666)) 
    h_val_0__1_carry__0_i_7
       (.I0(h_val_0__1_carry__0_i_2_n_0),
        .I1(h_val_0__1_carry__0_i_11_n_0),
        .I2(\genblk1[0].h_val_y_reg_reg_n_0_[10] ),
        .I3(p_3_in),
        .I4(\genblk1[0].h_val_x_reg_reg_n_0_[10] ),
        .I5(p_5_in),
        .O(h_val_0__1_carry__0_i_7_n_0));
  LUT6 #(
    .INIT(64'h6666699669966666)) 
    h_val_0__1_carry__0_i_8
       (.I0(h_val_0__1_carry__0_i_3_n_0),
        .I1(h_val_0__1_carry__0_i_12_n_0),
        .I2(\genblk1[0].h_val_y_reg_reg_n_0_[9] ),
        .I3(p_3_in),
        .I4(\genblk1[0].h_val_x_reg_reg_n_0_[9] ),
        .I5(p_5_in),
        .O(h_val_0__1_carry__0_i_8_n_0));
  LUT6 #(
    .INIT(64'h6666699669966666)) 
    h_val_0__1_carry__0_i_9
       (.I0(h_val_0__1_carry__0_i_4_n_0),
        .I1(h_val_0__1_carry__0_i_13_n_0),
        .I2(\genblk1[0].h_val_y_reg_reg_n_0_[8] ),
        .I3(p_3_in),
        .I4(\genblk1[0].h_val_x_reg_reg_n_0_[8] ),
        .I5(p_5_in),
        .O(h_val_0__1_carry__0_i_9_n_0));
  (* HLUTNM = "lutpair3" *) 
  LUT2 #(
    .INIT(4'h1)) 
    h_val_0__1_carry_i_1
       (.I0(h_val_0__1_carry_i_15_n_0),
        .I1(h_val_0__1_carry_i_16_n_0),
        .O(h_val_0__1_carry_i_1_n_0));
  (* HLUTNM = "lutpair2" *) 
  LUT3 #(
    .INIT(8'h96)) 
    h_val_0__1_carry_i_10
       (.I0(h_val_0__1_carry_i_17_n_0),
        .I1(h_val_0__1_carry_i_18_n_0),
        .I2(h_val_0__1_carry_i_3_n_0),
        .O(h_val_0__1_carry_i_10_n_0));
  (* HLUTNM = "lutpair1" *) 
  LUT3 #(
    .INIT(8'h96)) 
    h_val_0__1_carry_i_11
       (.I0(h_val_0__1_carry_i_19_n_0),
        .I1(h_val_0__1_carry_i_20_n_0),
        .I2(h_val_0__1_carry_i_4_n_0),
        .O(h_val_0__1_carry_i_11_n_0));
  (* HLUTNM = "lutpair0" *) 
  LUT3 #(
    .INIT(8'h96)) 
    h_val_0__1_carry_i_12
       (.I0(h_val_0__1_carry_i_21_n_0),
        .I1(h_val_0__1_carry_i_22_n_0),
        .I2(h_val_0__1_carry_i_5_n_0),
        .O(h_val_0__1_carry_i_12_n_0));
  LUT3 #(
    .INIT(8'h96)) 
    h_val_0__1_carry_i_13
       (.I0(h_val_0__1_carry_i_6_n_0),
        .I1(h_val_0__1_carry_i_23_n_0),
        .I2(h_val_0__1_carry_i_25_n_0),
        .O(h_val_0__1_carry_i_13_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_0__1_carry_i_14
       (.I0(\genblk1[0].h_val_x_reg_reg_n_0_[1] ),
        .I1(\genblk1[0].h_val_z_reg_reg_n_0_[1] ),
        .I2(\genblk1[0].h_val_y_reg_reg_n_0_[1] ),
        .I3(p_5_in),
        .O(h_val_0__1_carry_i_14_n_0));
  LUT6 #(
    .INIT(64'hF99F90099009F99F)) 
    h_val_0__1_carry_i_15
       (.I0(p_5_in),
        .I1(\genblk1[0].h_val_x_reg_reg_n_0_[5] ),
        .I2(p_3_in),
        .I3(\genblk1[0].h_val_y_reg_reg_n_0_[5] ),
        .I4(p_4_in),
        .I5(\genblk1[0].h_val_z_reg_reg_n_0_[5] ),
        .O(h_val_0__1_carry_i_15_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_0__1_carry_i_16
       (.I0(\genblk1[0].h_val_z_reg_reg_n_0_[6] ),
        .I1(p_4_in),
        .I2(\genblk1[0].h_val_y_reg_reg_n_0_[6] ),
        .I3(p_3_in),
        .I4(\genblk1[0].h_val_x_reg_reg_n_0_[6] ),
        .I5(p_5_in),
        .O(h_val_0__1_carry_i_16_n_0));
  LUT6 #(
    .INIT(64'hF99F90099009F99F)) 
    h_val_0__1_carry_i_17
       (.I0(p_5_in),
        .I1(\genblk1[0].h_val_x_reg_reg_n_0_[4] ),
        .I2(p_3_in),
        .I3(\genblk1[0].h_val_y_reg_reg_n_0_[4] ),
        .I4(p_4_in),
        .I5(\genblk1[0].h_val_z_reg_reg_n_0_[4] ),
        .O(h_val_0__1_carry_i_17_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_0__1_carry_i_18
       (.I0(\genblk1[0].h_val_z_reg_reg_n_0_[5] ),
        .I1(p_4_in),
        .I2(\genblk1[0].h_val_y_reg_reg_n_0_[5] ),
        .I3(p_3_in),
        .I4(\genblk1[0].h_val_x_reg_reg_n_0_[5] ),
        .I5(p_5_in),
        .O(h_val_0__1_carry_i_18_n_0));
  LUT6 #(
    .INIT(64'hF99F90099009F99F)) 
    h_val_0__1_carry_i_19
       (.I0(p_5_in),
        .I1(\genblk1[0].h_val_x_reg_reg_n_0_[3] ),
        .I2(p_3_in),
        .I3(\genblk1[0].h_val_y_reg_reg_n_0_[3] ),
        .I4(p_4_in),
        .I5(\genblk1[0].h_val_z_reg_reg_n_0_[3] ),
        .O(h_val_0__1_carry_i_19_n_0));
  (* HLUTNM = "lutpair2" *) 
  LUT2 #(
    .INIT(4'h1)) 
    h_val_0__1_carry_i_2
       (.I0(h_val_0__1_carry_i_17_n_0),
        .I1(h_val_0__1_carry_i_18_n_0),
        .O(h_val_0__1_carry_i_2_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_0__1_carry_i_20
       (.I0(\genblk1[0].h_val_z_reg_reg_n_0_[4] ),
        .I1(p_4_in),
        .I2(\genblk1[0].h_val_y_reg_reg_n_0_[4] ),
        .I3(p_3_in),
        .I4(\genblk1[0].h_val_x_reg_reg_n_0_[4] ),
        .I5(p_5_in),
        .O(h_val_0__1_carry_i_20_n_0));
  LUT6 #(
    .INIT(64'hF99F90099009F99F)) 
    h_val_0__1_carry_i_21
       (.I0(p_5_in),
        .I1(\genblk1[0].h_val_x_reg_reg_n_0_[2] ),
        .I2(p_3_in),
        .I3(\genblk1[0].h_val_y_reg_reg_n_0_[2] ),
        .I4(p_4_in),
        .I5(\genblk1[0].h_val_z_reg_reg_n_0_[2] ),
        .O(h_val_0__1_carry_i_21_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_0__1_carry_i_22
       (.I0(\genblk1[0].h_val_z_reg_reg_n_0_[3] ),
        .I1(p_4_in),
        .I2(\genblk1[0].h_val_y_reg_reg_n_0_[3] ),
        .I3(p_3_in),
        .I4(\genblk1[0].h_val_x_reg_reg_n_0_[3] ),
        .I5(p_5_in),
        .O(h_val_0__1_carry_i_22_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_0__1_carry_i_23
       (.I0(\genblk1[0].h_val_z_reg_reg_n_0_[2] ),
        .I1(p_4_in),
        .I2(\genblk1[0].h_val_y_reg_reg_n_0_[2] ),
        .I3(p_3_in),
        .I4(\genblk1[0].h_val_x_reg_reg_n_0_[2] ),
        .I5(p_5_in),
        .O(h_val_0__1_carry_i_23_n_0));
  LUT6 #(
    .INIT(64'h06606FF66FF60660)) 
    h_val_0__1_carry_i_24
       (.I0(p_5_in),
        .I1(\genblk1[0].h_val_x_reg_reg_n_0_[6] ),
        .I2(\genblk1[0].h_val_z_reg_reg_n_0_[6] ),
        .I3(p_4_in),
        .I4(\genblk1[0].h_val_y_reg_reg_n_0_[6] ),
        .I5(p_3_in),
        .O(h_val_0__1_carry_i_24_n_0));
  LUT5 #(
    .INIT(32'h9D0119DF)) 
    h_val_0__1_carry_i_25
       (.I0(p_3_in),
        .I1(\genblk1[0].h_val_y_reg_reg_n_0_[1] ),
        .I2(p_5_in),
        .I3(\genblk1[0].h_val_z_reg_reg_n_0_[1] ),
        .I4(p_4_in),
        .O(h_val_0__1_carry_i_25_n_0));
  (* HLUTNM = "lutpair1" *) 
  LUT2 #(
    .INIT(4'h1)) 
    h_val_0__1_carry_i_3
       (.I0(h_val_0__1_carry_i_19_n_0),
        .I1(h_val_0__1_carry_i_20_n_0),
        .O(h_val_0__1_carry_i_3_n_0));
  (* HLUTNM = "lutpair0" *) 
  LUT2 #(
    .INIT(4'h1)) 
    h_val_0__1_carry_i_4
       (.I0(h_val_0__1_carry_i_21_n_0),
        .I1(h_val_0__1_carry_i_22_n_0),
        .O(h_val_0__1_carry_i_4_n_0));
  LUT6 #(
    .INIT(64'h0000000062FEE620)) 
    h_val_0__1_carry_i_5
       (.I0(p_4_in),
        .I1(\genblk1[0].h_val_z_reg_reg_n_0_[1] ),
        .I2(p_5_in),
        .I3(\genblk1[0].h_val_y_reg_reg_n_0_[1] ),
        .I4(p_3_in),
        .I5(h_val_0__1_carry_i_23_n_0),
        .O(h_val_0__1_carry_i_5_n_0));
  LUT6 #(
    .INIT(64'h0000936CC9360000)) 
    h_val_0__1_carry_i_6
       (.I0(p_3_in),
        .I1(\genblk1[0].h_val_y_reg_reg_n_0_[1] ),
        .I2(p_4_in),
        .I3(\genblk1[0].h_val_z_reg_reg_n_0_[1] ),
        .I4(\genblk1[0].h_val_x_reg_reg_n_0_[1] ),
        .I5(p_5_in),
        .O(h_val_0__1_carry_i_6_n_0));
  LUT6 #(
    .INIT(64'h936C6C9336C9C936)) 
    h_val_0__1_carry_i_7
       (.I0(p_3_in),
        .I1(\genblk1[0].h_val_y_reg_reg_n_0_[1] ),
        .I2(p_4_in),
        .I3(\genblk1[0].h_val_z_reg_reg_n_0_[1] ),
        .I4(\genblk1[0].h_val_x_reg_reg_n_0_[1] ),
        .I5(p_5_in),
        .O(h_val_0__1_carry_i_7_n_0));
  LUT6 #(
    .INIT(64'h6996966996696996)) 
    h_val_0__1_carry_i_8
       (.I0(h_val_0__1_carry_i_1_n_0),
        .I1(h_val_0__1_carry_i_24_n_0),
        .I2(\genblk1[0].h_val_y_reg_reg_n_0_[7] ),
        .I3(p_3_in),
        .I4(\genblk1[0].h_val_x_reg_reg_n_0_[7] ),
        .I5(p_5_in),
        .O(h_val_0__1_carry_i_8_n_0));
  (* HLUTNM = "lutpair3" *) 
  LUT3 #(
    .INIT(8'h96)) 
    h_val_0__1_carry_i_9
       (.I0(h_val_0__1_carry_i_15_n_0),
        .I1(h_val_0__1_carry_i_16_n_0),
        .I2(h_val_0__1_carry_i_2_n_0),
        .O(h_val_0__1_carry_i_9_n_0));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    h_val_14__1_carry
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({h_val_14__1_carry_n_0,NLW_h_val_14__1_carry_CO_UNCONNECTED[6:0]}),
        .DI({h_val_14__1_carry_i_1_n_0,h_val_14__1_carry_i_2_n_0,h_val_14__1_carry_i_3_n_0,h_val_14__1_carry_i_4_n_0,h_val_14__1_carry_i_5_n_0,h_val_14__1_carry_i_6_n_0,h_val_14__1_carry_i_7_n_0,p_0_in5_in}),
        .O({h_val_14__40[7:1],NLW_h_val_14__1_carry_O_UNCONNECTED[0]}),
        .S({h_val_14__1_carry_i_8_n_0,h_val_14__1_carry_i_9_n_0,h_val_14__1_carry_i_10_n_0,h_val_14__1_carry_i_11_n_0,h_val_14__1_carry_i_12_n_0,h_val_14__1_carry_i_13_n_0,h_val_14__1_carry_i_14_n_0,1'b0}));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    h_val_14__1_carry__0
       (.CI(h_val_14__1_carry_n_0),
        .CI_TOP(1'b0),
        .CO({NLW_h_val_14__1_carry__0_CO_UNCONNECTED[7:6],h_val_14__40[13],NLW_h_val_14__1_carry__0_CO_UNCONNECTED[4:0]}),
        .DI({NLW_h_val_14__1_carry__0_DI_UNCONNECTED[7:6],1'b0,h_val_14__1_carry__0_i_1_n_0,h_val_14__1_carry__0_i_2_n_0,h_val_14__1_carry__0_i_3_n_0,h_val_14__1_carry__0_i_4_n_0,h_val_14__1_carry__0_i_5_n_0}),
        .O({NLW_h_val_14__1_carry__0_O_UNCONNECTED[7:5],h_val_14__40[12:8]}),
        .S({NLW_h_val_14__1_carry__0_S_UNCONNECTED[7:6],1'b1,h_val_14__1_carry__0_i_6_n_0,h_val_14__1_carry__0_i_7_n_0,h_val_14__1_carry__0_i_8_n_0,h_val_14__1_carry__0_i_9_n_0,h_val_14__1_carry__0_i_10_n_0}));
  LUT6 #(
    .INIT(64'h0210400810020840)) 
    h_val_14__1_carry__0_i_1
       (.I0(\genblk1[1].h_val_x_reg_reg_n_0_[24] ),
        .I1(\genblk1[1].h_val_y_reg_reg_n_0_[24] ),
        .I2(p_0_in5_in),
        .I3(\genblk1[1].h_val_x_reg_reg_n_0_[25] ),
        .I4(p_0_in3_in),
        .I5(\genblk1[1].h_val_y_reg_reg_n_0_[25] ),
        .O(h_val_14__1_carry__0_i_1_n_0));
  LUT6 #(
    .INIT(64'h6666699669966666)) 
    h_val_14__1_carry__0_i_10
       (.I0(h_val_14__1_carry__0_i_5_n_0),
        .I1(h_val_14__1_carry__0_i_14_n_0),
        .I2(\genblk1[1].h_val_y_reg_reg_n_0_[21] ),
        .I3(p_0_in3_in),
        .I4(\genblk1[1].h_val_x_reg_reg_n_0_[21] ),
        .I5(p_0_in5_in),
        .O(h_val_14__1_carry__0_i_10_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_14__1_carry__0_i_11
       (.I0(\genblk1[1].h_val_y_reg_reg_n_0_[25] ),
        .I1(p_0_in3_in),
        .I2(\genblk1[1].h_val_x_reg_reg_n_0_[25] ),
        .I3(p_0_in5_in),
        .O(h_val_14__1_carry__0_i_11_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_14__1_carry__0_i_12
       (.I0(\genblk1[1].h_val_y_reg_reg_n_0_[24] ),
        .I1(p_0_in3_in),
        .I2(\genblk1[1].h_val_x_reg_reg_n_0_[24] ),
        .I3(p_0_in5_in),
        .O(h_val_14__1_carry__0_i_12_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_14__1_carry__0_i_13
       (.I0(\genblk1[1].h_val_y_reg_reg_n_0_[23] ),
        .I1(p_0_in3_in),
        .I2(\genblk1[1].h_val_x_reg_reg_n_0_[23] ),
        .I3(p_0_in5_in),
        .O(h_val_14__1_carry__0_i_13_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_14__1_carry__0_i_14
       (.I0(\genblk1[1].h_val_y_reg_reg_n_0_[22] ),
        .I1(p_0_in3_in),
        .I2(\genblk1[1].h_val_x_reg_reg_n_0_[22] ),
        .I3(p_0_in5_in),
        .O(h_val_14__1_carry__0_i_14_n_0));
  LUT6 #(
    .INIT(64'h0210400810020840)) 
    h_val_14__1_carry__0_i_2
       (.I0(\genblk1[1].h_val_x_reg_reg_n_0_[23] ),
        .I1(\genblk1[1].h_val_y_reg_reg_n_0_[23] ),
        .I2(p_0_in5_in),
        .I3(\genblk1[1].h_val_x_reg_reg_n_0_[24] ),
        .I4(p_0_in3_in),
        .I5(\genblk1[1].h_val_y_reg_reg_n_0_[24] ),
        .O(h_val_14__1_carry__0_i_2_n_0));
  LUT6 #(
    .INIT(64'h0210400810020840)) 
    h_val_14__1_carry__0_i_3
       (.I0(\genblk1[1].h_val_x_reg_reg_n_0_[22] ),
        .I1(\genblk1[1].h_val_y_reg_reg_n_0_[22] ),
        .I2(p_0_in5_in),
        .I3(\genblk1[1].h_val_x_reg_reg_n_0_[23] ),
        .I4(p_0_in3_in),
        .I5(\genblk1[1].h_val_y_reg_reg_n_0_[23] ),
        .O(h_val_14__1_carry__0_i_3_n_0));
  LUT6 #(
    .INIT(64'h0210400810020840)) 
    h_val_14__1_carry__0_i_4
       (.I0(\genblk1[1].h_val_x_reg_reg_n_0_[21] ),
        .I1(\genblk1[1].h_val_y_reg_reg_n_0_[21] ),
        .I2(p_0_in5_in),
        .I3(\genblk1[1].h_val_x_reg_reg_n_0_[22] ),
        .I4(p_0_in3_in),
        .I5(\genblk1[1].h_val_y_reg_reg_n_0_[22] ),
        .O(h_val_14__1_carry__0_i_4_n_0));
  LUT5 #(
    .INIT(32'h69960000)) 
    h_val_14__1_carry__0_i_5
       (.I0(p_0_in5_in),
        .I1(\genblk1[1].h_val_x_reg_reg_n_0_[21] ),
        .I2(p_0_in3_in),
        .I3(\genblk1[1].h_val_y_reg_reg_n_0_[21] ),
        .I4(h_val_14__1_carry_i_24_n_0),
        .O(h_val_14__1_carry__0_i_5_n_0));
  LUT6 #(
    .INIT(64'h04102FF81FF40820)) 
    h_val_14__1_carry__0_i_6
       (.I0(\genblk1[1].h_val_y_reg_reg_n_0_[24] ),
        .I1(\genblk1[1].h_val_x_reg_reg_n_0_[24] ),
        .I2(p_0_in5_in),
        .I3(\genblk1[1].h_val_x_reg_reg_n_0_[25] ),
        .I4(p_0_in3_in),
        .I5(\genblk1[1].h_val_y_reg_reg_n_0_[25] ),
        .O(h_val_14__1_carry__0_i_6_n_0));
  LUT6 #(
    .INIT(64'h6666699669966666)) 
    h_val_14__1_carry__0_i_7
       (.I0(h_val_14__1_carry__0_i_2_n_0),
        .I1(h_val_14__1_carry__0_i_11_n_0),
        .I2(\genblk1[1].h_val_y_reg_reg_n_0_[24] ),
        .I3(p_0_in3_in),
        .I4(\genblk1[1].h_val_x_reg_reg_n_0_[24] ),
        .I5(p_0_in5_in),
        .O(h_val_14__1_carry__0_i_7_n_0));
  LUT6 #(
    .INIT(64'h6666699669966666)) 
    h_val_14__1_carry__0_i_8
       (.I0(h_val_14__1_carry__0_i_3_n_0),
        .I1(h_val_14__1_carry__0_i_12_n_0),
        .I2(\genblk1[1].h_val_y_reg_reg_n_0_[23] ),
        .I3(p_0_in3_in),
        .I4(\genblk1[1].h_val_x_reg_reg_n_0_[23] ),
        .I5(p_0_in5_in),
        .O(h_val_14__1_carry__0_i_8_n_0));
  LUT6 #(
    .INIT(64'h6666699669966666)) 
    h_val_14__1_carry__0_i_9
       (.I0(h_val_14__1_carry__0_i_4_n_0),
        .I1(h_val_14__1_carry__0_i_13_n_0),
        .I2(\genblk1[1].h_val_y_reg_reg_n_0_[22] ),
        .I3(p_0_in3_in),
        .I4(\genblk1[1].h_val_x_reg_reg_n_0_[22] ),
        .I5(p_0_in5_in),
        .O(h_val_14__1_carry__0_i_9_n_0));
  (* HLUTNM = "lutpair7" *) 
  LUT2 #(
    .INIT(4'h1)) 
    h_val_14__1_carry_i_1
       (.I0(h_val_14__1_carry_i_15_n_0),
        .I1(h_val_14__1_carry_i_16_n_0),
        .O(h_val_14__1_carry_i_1_n_0));
  (* HLUTNM = "lutpair6" *) 
  LUT3 #(
    .INIT(8'h96)) 
    h_val_14__1_carry_i_10
       (.I0(h_val_14__1_carry_i_17_n_0),
        .I1(h_val_14__1_carry_i_18_n_0),
        .I2(h_val_14__1_carry_i_3_n_0),
        .O(h_val_14__1_carry_i_10_n_0));
  (* HLUTNM = "lutpair5" *) 
  LUT3 #(
    .INIT(8'h96)) 
    h_val_14__1_carry_i_11
       (.I0(h_val_14__1_carry_i_19_n_0),
        .I1(h_val_14__1_carry_i_20_n_0),
        .I2(h_val_14__1_carry_i_4_n_0),
        .O(h_val_14__1_carry_i_11_n_0));
  (* HLUTNM = "lutpair4" *) 
  LUT3 #(
    .INIT(8'h96)) 
    h_val_14__1_carry_i_12
       (.I0(h_val_14__1_carry_i_21_n_0),
        .I1(h_val_14__1_carry_i_22_n_0),
        .I2(h_val_14__1_carry_i_5_n_0),
        .O(h_val_14__1_carry_i_12_n_0));
  LUT3 #(
    .INIT(8'h96)) 
    h_val_14__1_carry_i_13
       (.I0(h_val_14__1_carry_i_6_n_0),
        .I1(h_val_14__1_carry_i_23_n_0),
        .I2(h_val_14__1_carry_i_25_n_0),
        .O(h_val_14__1_carry_i_13_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_14__1_carry_i_14
       (.I0(\genblk1[1].h_val_x_reg_reg_n_0_[15] ),
        .I1(\genblk1[1].h_val_z_reg_reg_n_0_[15] ),
        .I2(\genblk1[1].h_val_y_reg_reg_n_0_[15] ),
        .I3(p_0_in5_in),
        .O(h_val_14__1_carry_i_14_n_0));
  LUT6 #(
    .INIT(64'hF99F90099009F99F)) 
    h_val_14__1_carry_i_15
       (.I0(p_0_in5_in),
        .I1(\genblk1[1].h_val_x_reg_reg_n_0_[19] ),
        .I2(p_0_in3_in),
        .I3(\genblk1[1].h_val_y_reg_reg_n_0_[19] ),
        .I4(p_0_in4_in),
        .I5(\genblk1[1].h_val_z_reg_reg_n_0_[19] ),
        .O(h_val_14__1_carry_i_15_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_14__1_carry_i_16
       (.I0(\genblk1[1].h_val_z_reg_reg_n_0_[20] ),
        .I1(p_0_in4_in),
        .I2(\genblk1[1].h_val_y_reg_reg_n_0_[20] ),
        .I3(p_0_in3_in),
        .I4(\genblk1[1].h_val_x_reg_reg_n_0_[20] ),
        .I5(p_0_in5_in),
        .O(h_val_14__1_carry_i_16_n_0));
  LUT6 #(
    .INIT(64'hF99F90099009F99F)) 
    h_val_14__1_carry_i_17
       (.I0(p_0_in5_in),
        .I1(\genblk1[1].h_val_x_reg_reg_n_0_[18] ),
        .I2(p_0_in3_in),
        .I3(\genblk1[1].h_val_y_reg_reg_n_0_[18] ),
        .I4(p_0_in4_in),
        .I5(\genblk1[1].h_val_z_reg_reg_n_0_[18] ),
        .O(h_val_14__1_carry_i_17_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_14__1_carry_i_18
       (.I0(\genblk1[1].h_val_z_reg_reg_n_0_[19] ),
        .I1(p_0_in4_in),
        .I2(\genblk1[1].h_val_y_reg_reg_n_0_[19] ),
        .I3(p_0_in3_in),
        .I4(\genblk1[1].h_val_x_reg_reg_n_0_[19] ),
        .I5(p_0_in5_in),
        .O(h_val_14__1_carry_i_18_n_0));
  LUT6 #(
    .INIT(64'hF99F90099009F99F)) 
    h_val_14__1_carry_i_19
       (.I0(p_0_in5_in),
        .I1(\genblk1[1].h_val_x_reg_reg_n_0_[17] ),
        .I2(p_0_in3_in),
        .I3(\genblk1[1].h_val_y_reg_reg_n_0_[17] ),
        .I4(p_0_in4_in),
        .I5(\genblk1[1].h_val_z_reg_reg_n_0_[17] ),
        .O(h_val_14__1_carry_i_19_n_0));
  (* HLUTNM = "lutpair6" *) 
  LUT2 #(
    .INIT(4'h1)) 
    h_val_14__1_carry_i_2
       (.I0(h_val_14__1_carry_i_17_n_0),
        .I1(h_val_14__1_carry_i_18_n_0),
        .O(h_val_14__1_carry_i_2_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_14__1_carry_i_20
       (.I0(\genblk1[1].h_val_z_reg_reg_n_0_[18] ),
        .I1(p_0_in4_in),
        .I2(\genblk1[1].h_val_y_reg_reg_n_0_[18] ),
        .I3(p_0_in3_in),
        .I4(\genblk1[1].h_val_x_reg_reg_n_0_[18] ),
        .I5(p_0_in5_in),
        .O(h_val_14__1_carry_i_20_n_0));
  LUT6 #(
    .INIT(64'hF99F90099009F99F)) 
    h_val_14__1_carry_i_21
       (.I0(p_0_in5_in),
        .I1(\genblk1[1].h_val_x_reg_reg_n_0_[16] ),
        .I2(p_0_in3_in),
        .I3(\genblk1[1].h_val_y_reg_reg_n_0_[16] ),
        .I4(p_0_in4_in),
        .I5(\genblk1[1].h_val_z_reg_reg_n_0_[16] ),
        .O(h_val_14__1_carry_i_21_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_14__1_carry_i_22
       (.I0(\genblk1[1].h_val_z_reg_reg_n_0_[17] ),
        .I1(p_0_in4_in),
        .I2(\genblk1[1].h_val_y_reg_reg_n_0_[17] ),
        .I3(p_0_in3_in),
        .I4(\genblk1[1].h_val_x_reg_reg_n_0_[17] ),
        .I5(p_0_in5_in),
        .O(h_val_14__1_carry_i_22_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_14__1_carry_i_23
       (.I0(\genblk1[1].h_val_z_reg_reg_n_0_[16] ),
        .I1(p_0_in4_in),
        .I2(\genblk1[1].h_val_y_reg_reg_n_0_[16] ),
        .I3(p_0_in3_in),
        .I4(\genblk1[1].h_val_x_reg_reg_n_0_[16] ),
        .I5(p_0_in5_in),
        .O(h_val_14__1_carry_i_23_n_0));
  LUT6 #(
    .INIT(64'h06606FF66FF60660)) 
    h_val_14__1_carry_i_24
       (.I0(p_0_in5_in),
        .I1(\genblk1[1].h_val_x_reg_reg_n_0_[20] ),
        .I2(\genblk1[1].h_val_z_reg_reg_n_0_[20] ),
        .I3(p_0_in4_in),
        .I4(\genblk1[1].h_val_y_reg_reg_n_0_[20] ),
        .I5(p_0_in3_in),
        .O(h_val_14__1_carry_i_24_n_0));
  LUT5 #(
    .INIT(32'h9D0119DF)) 
    h_val_14__1_carry_i_25
       (.I0(p_0_in3_in),
        .I1(\genblk1[1].h_val_y_reg_reg_n_0_[15] ),
        .I2(p_0_in5_in),
        .I3(\genblk1[1].h_val_z_reg_reg_n_0_[15] ),
        .I4(p_0_in4_in),
        .O(h_val_14__1_carry_i_25_n_0));
  (* HLUTNM = "lutpair5" *) 
  LUT2 #(
    .INIT(4'h1)) 
    h_val_14__1_carry_i_3
       (.I0(h_val_14__1_carry_i_19_n_0),
        .I1(h_val_14__1_carry_i_20_n_0),
        .O(h_val_14__1_carry_i_3_n_0));
  (* HLUTNM = "lutpair4" *) 
  LUT2 #(
    .INIT(4'h1)) 
    h_val_14__1_carry_i_4
       (.I0(h_val_14__1_carry_i_21_n_0),
        .I1(h_val_14__1_carry_i_22_n_0),
        .O(h_val_14__1_carry_i_4_n_0));
  LUT6 #(
    .INIT(64'h0000000062FEE620)) 
    h_val_14__1_carry_i_5
       (.I0(p_0_in4_in),
        .I1(\genblk1[1].h_val_z_reg_reg_n_0_[15] ),
        .I2(p_0_in5_in),
        .I3(\genblk1[1].h_val_y_reg_reg_n_0_[15] ),
        .I4(p_0_in3_in),
        .I5(h_val_14__1_carry_i_23_n_0),
        .O(h_val_14__1_carry_i_5_n_0));
  LUT6 #(
    .INIT(64'h0000936CC9360000)) 
    h_val_14__1_carry_i_6
       (.I0(p_0_in3_in),
        .I1(\genblk1[1].h_val_y_reg_reg_n_0_[15] ),
        .I2(p_0_in4_in),
        .I3(\genblk1[1].h_val_z_reg_reg_n_0_[15] ),
        .I4(\genblk1[1].h_val_x_reg_reg_n_0_[15] ),
        .I5(p_0_in5_in),
        .O(h_val_14__1_carry_i_6_n_0));
  LUT6 #(
    .INIT(64'h936C6C9336C9C936)) 
    h_val_14__1_carry_i_7
       (.I0(p_0_in3_in),
        .I1(\genblk1[1].h_val_y_reg_reg_n_0_[15] ),
        .I2(p_0_in4_in),
        .I3(\genblk1[1].h_val_z_reg_reg_n_0_[15] ),
        .I4(\genblk1[1].h_val_x_reg_reg_n_0_[15] ),
        .I5(p_0_in5_in),
        .O(h_val_14__1_carry_i_7_n_0));
  LUT6 #(
    .INIT(64'h6996966996696996)) 
    h_val_14__1_carry_i_8
       (.I0(h_val_14__1_carry_i_1_n_0),
        .I1(h_val_14__1_carry_i_24_n_0),
        .I2(\genblk1[1].h_val_y_reg_reg_n_0_[21] ),
        .I3(p_0_in3_in),
        .I4(\genblk1[1].h_val_x_reg_reg_n_0_[21] ),
        .I5(p_0_in5_in),
        .O(h_val_14__1_carry_i_8_n_0));
  (* HLUTNM = "lutpair7" *) 
  LUT3 #(
    .INIT(8'h96)) 
    h_val_14__1_carry_i_9
       (.I0(h_val_14__1_carry_i_15_n_0),
        .I1(h_val_14__1_carry_i_16_n_0),
        .I2(h_val_14__1_carry_i_2_n_0),
        .O(h_val_14__1_carry_i_9_n_0));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    h_val_28__1_carry
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({h_val_28__1_carry_n_0,NLW_h_val_28__1_carry_CO_UNCONNECTED[6:0]}),
        .DI({h_val_28__1_carry_i_1_n_0,h_val_28__1_carry_i_2_n_0,h_val_28__1_carry_i_3_n_0,h_val_28__1_carry_i_4_n_0,h_val_28__1_carry_i_5_n_0,h_val_28__1_carry_i_6_n_0,h_val_28__1_carry_i_7_n_0,\genblk1[2].h_val_x_reg_reg_n_0_[41] }),
        .O({h_val_28__40[7:1],NLW_h_val_28__1_carry_O_UNCONNECTED[0]}),
        .S({h_val_28__1_carry_i_8_n_0,h_val_28__1_carry_i_9_n_0,h_val_28__1_carry_i_10_n_0,h_val_28__1_carry_i_11_n_0,h_val_28__1_carry_i_12_n_0,h_val_28__1_carry_i_13_n_0,h_val_28__1_carry_i_14_n_0,1'b0}));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    h_val_28__1_carry__0
       (.CI(h_val_28__1_carry_n_0),
        .CI_TOP(1'b0),
        .CO({NLW_h_val_28__1_carry__0_CO_UNCONNECTED[7:6],h_val_28__40[13],NLW_h_val_28__1_carry__0_CO_UNCONNECTED[4:0]}),
        .DI({NLW_h_val_28__1_carry__0_DI_UNCONNECTED[7:6],1'b0,h_val_28__1_carry__0_i_1_n_0,h_val_28__1_carry__0_i_2_n_0,h_val_28__1_carry__0_i_3_n_0,h_val_28__1_carry__0_i_4_n_0,h_val_28__1_carry__0_i_5_n_0}),
        .O({NLW_h_val_28__1_carry__0_O_UNCONNECTED[7:5],h_val_28__40[12:8]}),
        .S({NLW_h_val_28__1_carry__0_S_UNCONNECTED[7:6],1'b1,h_val_28__1_carry__0_i_6_n_0,h_val_28__1_carry__0_i_7_n_0,h_val_28__1_carry__0_i_8_n_0,h_val_28__1_carry__0_i_9_n_0,h_val_28__1_carry__0_i_10_n_0}));
  LUT6 #(
    .INIT(64'h0210400810020840)) 
    h_val_28__1_carry__0_i_1
       (.I0(\genblk1[2].h_val_x_reg_reg_n_0_[38] ),
        .I1(\genblk1[2].h_val_y_reg_reg_n_0_[38] ),
        .I2(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .I3(\genblk1[2].h_val_x_reg_reg_n_0_[39] ),
        .I4(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I5(\genblk1[2].h_val_y_reg_reg_n_0_[39] ),
        .O(h_val_28__1_carry__0_i_1_n_0));
  LUT6 #(
    .INIT(64'h6666699669966666)) 
    h_val_28__1_carry__0_i_10
       (.I0(h_val_28__1_carry__0_i_5_n_0),
        .I1(h_val_28__1_carry__0_i_14_n_0),
        .I2(\genblk1[2].h_val_y_reg_reg_n_0_[35] ),
        .I3(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I4(\genblk1[2].h_val_x_reg_reg_n_0_[35] ),
        .I5(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .O(h_val_28__1_carry__0_i_10_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_28__1_carry__0_i_11
       (.I0(\genblk1[2].h_val_y_reg_reg_n_0_[39] ),
        .I1(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I2(\genblk1[2].h_val_x_reg_reg_n_0_[39] ),
        .I3(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .O(h_val_28__1_carry__0_i_11_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_28__1_carry__0_i_12
       (.I0(\genblk1[2].h_val_y_reg_reg_n_0_[38] ),
        .I1(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I2(\genblk1[2].h_val_x_reg_reg_n_0_[38] ),
        .I3(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .O(h_val_28__1_carry__0_i_12_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_28__1_carry__0_i_13
       (.I0(\genblk1[2].h_val_y_reg_reg_n_0_[37] ),
        .I1(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I2(\genblk1[2].h_val_x_reg_reg_n_0_[37] ),
        .I3(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .O(h_val_28__1_carry__0_i_13_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_28__1_carry__0_i_14
       (.I0(\genblk1[2].h_val_y_reg_reg_n_0_[36] ),
        .I1(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I2(\genblk1[2].h_val_x_reg_reg_n_0_[36] ),
        .I3(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .O(h_val_28__1_carry__0_i_14_n_0));
  LUT6 #(
    .INIT(64'h0210400810020840)) 
    h_val_28__1_carry__0_i_2
       (.I0(\genblk1[2].h_val_x_reg_reg_n_0_[37] ),
        .I1(\genblk1[2].h_val_y_reg_reg_n_0_[37] ),
        .I2(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .I3(\genblk1[2].h_val_x_reg_reg_n_0_[38] ),
        .I4(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I5(\genblk1[2].h_val_y_reg_reg_n_0_[38] ),
        .O(h_val_28__1_carry__0_i_2_n_0));
  LUT6 #(
    .INIT(64'h0210400810020840)) 
    h_val_28__1_carry__0_i_3
       (.I0(\genblk1[2].h_val_x_reg_reg_n_0_[36] ),
        .I1(\genblk1[2].h_val_y_reg_reg_n_0_[36] ),
        .I2(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .I3(\genblk1[2].h_val_x_reg_reg_n_0_[37] ),
        .I4(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I5(\genblk1[2].h_val_y_reg_reg_n_0_[37] ),
        .O(h_val_28__1_carry__0_i_3_n_0));
  LUT6 #(
    .INIT(64'h0210400810020840)) 
    h_val_28__1_carry__0_i_4
       (.I0(\genblk1[2].h_val_x_reg_reg_n_0_[35] ),
        .I1(\genblk1[2].h_val_y_reg_reg_n_0_[35] ),
        .I2(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .I3(\genblk1[2].h_val_x_reg_reg_n_0_[36] ),
        .I4(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I5(\genblk1[2].h_val_y_reg_reg_n_0_[36] ),
        .O(h_val_28__1_carry__0_i_4_n_0));
  LUT5 #(
    .INIT(32'h69960000)) 
    h_val_28__1_carry__0_i_5
       (.I0(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .I1(\genblk1[2].h_val_x_reg_reg_n_0_[35] ),
        .I2(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I3(\genblk1[2].h_val_y_reg_reg_n_0_[35] ),
        .I4(h_val_28__1_carry_i_24_n_0),
        .O(h_val_28__1_carry__0_i_5_n_0));
  LUT6 #(
    .INIT(64'h04102FF81FF40820)) 
    h_val_28__1_carry__0_i_6
       (.I0(\genblk1[2].h_val_y_reg_reg_n_0_[38] ),
        .I1(\genblk1[2].h_val_x_reg_reg_n_0_[38] ),
        .I2(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .I3(\genblk1[2].h_val_x_reg_reg_n_0_[39] ),
        .I4(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I5(\genblk1[2].h_val_y_reg_reg_n_0_[39] ),
        .O(h_val_28__1_carry__0_i_6_n_0));
  LUT6 #(
    .INIT(64'h6666699669966666)) 
    h_val_28__1_carry__0_i_7
       (.I0(h_val_28__1_carry__0_i_2_n_0),
        .I1(h_val_28__1_carry__0_i_11_n_0),
        .I2(\genblk1[2].h_val_y_reg_reg_n_0_[38] ),
        .I3(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I4(\genblk1[2].h_val_x_reg_reg_n_0_[38] ),
        .I5(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .O(h_val_28__1_carry__0_i_7_n_0));
  LUT6 #(
    .INIT(64'h6666699669966666)) 
    h_val_28__1_carry__0_i_8
       (.I0(h_val_28__1_carry__0_i_3_n_0),
        .I1(h_val_28__1_carry__0_i_12_n_0),
        .I2(\genblk1[2].h_val_y_reg_reg_n_0_[37] ),
        .I3(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I4(\genblk1[2].h_val_x_reg_reg_n_0_[37] ),
        .I5(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .O(h_val_28__1_carry__0_i_8_n_0));
  LUT6 #(
    .INIT(64'h6666699669966666)) 
    h_val_28__1_carry__0_i_9
       (.I0(h_val_28__1_carry__0_i_4_n_0),
        .I1(h_val_28__1_carry__0_i_13_n_0),
        .I2(\genblk1[2].h_val_y_reg_reg_n_0_[36] ),
        .I3(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I4(\genblk1[2].h_val_x_reg_reg_n_0_[36] ),
        .I5(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .O(h_val_28__1_carry__0_i_9_n_0));
  (* HLUTNM = "lutpair11" *) 
  LUT2 #(
    .INIT(4'h1)) 
    h_val_28__1_carry_i_1
       (.I0(h_val_28__1_carry_i_15_n_0),
        .I1(h_val_28__1_carry_i_16_n_0),
        .O(h_val_28__1_carry_i_1_n_0));
  (* HLUTNM = "lutpair10" *) 
  LUT3 #(
    .INIT(8'h96)) 
    h_val_28__1_carry_i_10
       (.I0(h_val_28__1_carry_i_17_n_0),
        .I1(h_val_28__1_carry_i_18_n_0),
        .I2(h_val_28__1_carry_i_3_n_0),
        .O(h_val_28__1_carry_i_10_n_0));
  (* HLUTNM = "lutpair9" *) 
  LUT3 #(
    .INIT(8'h96)) 
    h_val_28__1_carry_i_11
       (.I0(h_val_28__1_carry_i_19_n_0),
        .I1(h_val_28__1_carry_i_20_n_0),
        .I2(h_val_28__1_carry_i_4_n_0),
        .O(h_val_28__1_carry_i_11_n_0));
  (* HLUTNM = "lutpair8" *) 
  LUT3 #(
    .INIT(8'h96)) 
    h_val_28__1_carry_i_12
       (.I0(h_val_28__1_carry_i_21_n_0),
        .I1(h_val_28__1_carry_i_22_n_0),
        .I2(h_val_28__1_carry_i_5_n_0),
        .O(h_val_28__1_carry_i_12_n_0));
  LUT3 #(
    .INIT(8'h96)) 
    h_val_28__1_carry_i_13
       (.I0(h_val_28__1_carry_i_6_n_0),
        .I1(h_val_28__1_carry_i_23_n_0),
        .I2(h_val_28__1_carry_i_25_n_0),
        .O(h_val_28__1_carry_i_13_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_28__1_carry_i_14
       (.I0(\genblk1[2].h_val_x_reg_reg_n_0_[29] ),
        .I1(\genblk1[2].h_val_z_reg_reg_n_0_[29] ),
        .I2(\genblk1[2].h_val_y_reg_reg_n_0_[29] ),
        .I3(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .O(h_val_28__1_carry_i_14_n_0));
  LUT6 #(
    .INIT(64'hF99F90099009F99F)) 
    h_val_28__1_carry_i_15
       (.I0(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .I1(\genblk1[2].h_val_x_reg_reg_n_0_[33] ),
        .I2(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I3(\genblk1[2].h_val_y_reg_reg_n_0_[33] ),
        .I4(\genblk1[2].h_val_z_reg_reg_n_0_[41] ),
        .I5(\genblk1[2].h_val_z_reg_reg_n_0_[33] ),
        .O(h_val_28__1_carry_i_15_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_28__1_carry_i_16
       (.I0(\genblk1[2].h_val_z_reg_reg_n_0_[34] ),
        .I1(\genblk1[2].h_val_z_reg_reg_n_0_[41] ),
        .I2(\genblk1[2].h_val_y_reg_reg_n_0_[34] ),
        .I3(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I4(\genblk1[2].h_val_x_reg_reg_n_0_[34] ),
        .I5(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .O(h_val_28__1_carry_i_16_n_0));
  LUT6 #(
    .INIT(64'hF99F90099009F99F)) 
    h_val_28__1_carry_i_17
       (.I0(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .I1(\genblk1[2].h_val_x_reg_reg_n_0_[32] ),
        .I2(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I3(\genblk1[2].h_val_y_reg_reg_n_0_[32] ),
        .I4(\genblk1[2].h_val_z_reg_reg_n_0_[41] ),
        .I5(\genblk1[2].h_val_z_reg_reg_n_0_[32] ),
        .O(h_val_28__1_carry_i_17_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_28__1_carry_i_18
       (.I0(\genblk1[2].h_val_z_reg_reg_n_0_[33] ),
        .I1(\genblk1[2].h_val_z_reg_reg_n_0_[41] ),
        .I2(\genblk1[2].h_val_y_reg_reg_n_0_[33] ),
        .I3(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I4(\genblk1[2].h_val_x_reg_reg_n_0_[33] ),
        .I5(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .O(h_val_28__1_carry_i_18_n_0));
  LUT6 #(
    .INIT(64'hF99F90099009F99F)) 
    h_val_28__1_carry_i_19
       (.I0(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .I1(\genblk1[2].h_val_x_reg_reg_n_0_[31] ),
        .I2(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I3(\genblk1[2].h_val_y_reg_reg_n_0_[31] ),
        .I4(\genblk1[2].h_val_z_reg_reg_n_0_[41] ),
        .I5(\genblk1[2].h_val_z_reg_reg_n_0_[31] ),
        .O(h_val_28__1_carry_i_19_n_0));
  (* HLUTNM = "lutpair10" *) 
  LUT2 #(
    .INIT(4'h1)) 
    h_val_28__1_carry_i_2
       (.I0(h_val_28__1_carry_i_17_n_0),
        .I1(h_val_28__1_carry_i_18_n_0),
        .O(h_val_28__1_carry_i_2_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_28__1_carry_i_20
       (.I0(\genblk1[2].h_val_z_reg_reg_n_0_[32] ),
        .I1(\genblk1[2].h_val_z_reg_reg_n_0_[41] ),
        .I2(\genblk1[2].h_val_y_reg_reg_n_0_[32] ),
        .I3(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I4(\genblk1[2].h_val_x_reg_reg_n_0_[32] ),
        .I5(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .O(h_val_28__1_carry_i_20_n_0));
  LUT6 #(
    .INIT(64'hF99F90099009F99F)) 
    h_val_28__1_carry_i_21
       (.I0(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .I1(\genblk1[2].h_val_x_reg_reg_n_0_[30] ),
        .I2(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I3(\genblk1[2].h_val_y_reg_reg_n_0_[30] ),
        .I4(\genblk1[2].h_val_z_reg_reg_n_0_[41] ),
        .I5(\genblk1[2].h_val_z_reg_reg_n_0_[30] ),
        .O(h_val_28__1_carry_i_21_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_28__1_carry_i_22
       (.I0(\genblk1[2].h_val_z_reg_reg_n_0_[31] ),
        .I1(\genblk1[2].h_val_z_reg_reg_n_0_[41] ),
        .I2(\genblk1[2].h_val_y_reg_reg_n_0_[31] ),
        .I3(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I4(\genblk1[2].h_val_x_reg_reg_n_0_[31] ),
        .I5(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .O(h_val_28__1_carry_i_22_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_28__1_carry_i_23
       (.I0(\genblk1[2].h_val_z_reg_reg_n_0_[30] ),
        .I1(\genblk1[2].h_val_z_reg_reg_n_0_[41] ),
        .I2(\genblk1[2].h_val_y_reg_reg_n_0_[30] ),
        .I3(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I4(\genblk1[2].h_val_x_reg_reg_n_0_[30] ),
        .I5(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .O(h_val_28__1_carry_i_23_n_0));
  LUT6 #(
    .INIT(64'h06606FF66FF60660)) 
    h_val_28__1_carry_i_24
       (.I0(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .I1(\genblk1[2].h_val_x_reg_reg_n_0_[34] ),
        .I2(\genblk1[2].h_val_z_reg_reg_n_0_[34] ),
        .I3(\genblk1[2].h_val_z_reg_reg_n_0_[41] ),
        .I4(\genblk1[2].h_val_y_reg_reg_n_0_[34] ),
        .I5(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .O(h_val_28__1_carry_i_24_n_0));
  LUT5 #(
    .INIT(32'h9D0119DF)) 
    h_val_28__1_carry_i_25
       (.I0(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I1(\genblk1[2].h_val_y_reg_reg_n_0_[29] ),
        .I2(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .I3(\genblk1[2].h_val_z_reg_reg_n_0_[29] ),
        .I4(\genblk1[2].h_val_z_reg_reg_n_0_[41] ),
        .O(h_val_28__1_carry_i_25_n_0));
  (* HLUTNM = "lutpair9" *) 
  LUT2 #(
    .INIT(4'h1)) 
    h_val_28__1_carry_i_3
       (.I0(h_val_28__1_carry_i_19_n_0),
        .I1(h_val_28__1_carry_i_20_n_0),
        .O(h_val_28__1_carry_i_3_n_0));
  (* HLUTNM = "lutpair8" *) 
  LUT2 #(
    .INIT(4'h1)) 
    h_val_28__1_carry_i_4
       (.I0(h_val_28__1_carry_i_21_n_0),
        .I1(h_val_28__1_carry_i_22_n_0),
        .O(h_val_28__1_carry_i_4_n_0));
  LUT6 #(
    .INIT(64'h0000000062FEE620)) 
    h_val_28__1_carry_i_5
       (.I0(\genblk1[2].h_val_z_reg_reg_n_0_[41] ),
        .I1(\genblk1[2].h_val_z_reg_reg_n_0_[29] ),
        .I2(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .I3(\genblk1[2].h_val_y_reg_reg_n_0_[29] ),
        .I4(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I5(h_val_28__1_carry_i_23_n_0),
        .O(h_val_28__1_carry_i_5_n_0));
  LUT6 #(
    .INIT(64'h0000936CC9360000)) 
    h_val_28__1_carry_i_6
       (.I0(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I1(\genblk1[2].h_val_y_reg_reg_n_0_[29] ),
        .I2(\genblk1[2].h_val_z_reg_reg_n_0_[41] ),
        .I3(\genblk1[2].h_val_z_reg_reg_n_0_[29] ),
        .I4(\genblk1[2].h_val_x_reg_reg_n_0_[29] ),
        .I5(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .O(h_val_28__1_carry_i_6_n_0));
  LUT6 #(
    .INIT(64'h936C6C9336C9C936)) 
    h_val_28__1_carry_i_7
       (.I0(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I1(\genblk1[2].h_val_y_reg_reg_n_0_[29] ),
        .I2(\genblk1[2].h_val_z_reg_reg_n_0_[41] ),
        .I3(\genblk1[2].h_val_z_reg_reg_n_0_[29] ),
        .I4(\genblk1[2].h_val_x_reg_reg_n_0_[29] ),
        .I5(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .O(h_val_28__1_carry_i_7_n_0));
  LUT6 #(
    .INIT(64'h6996966996696996)) 
    h_val_28__1_carry_i_8
       (.I0(h_val_28__1_carry_i_1_n_0),
        .I1(h_val_28__1_carry_i_24_n_0),
        .I2(\genblk1[2].h_val_y_reg_reg_n_0_[35] ),
        .I3(\genblk1[2].h_val_y_reg_reg_n_0_[41] ),
        .I4(\genblk1[2].h_val_x_reg_reg_n_0_[35] ),
        .I5(\genblk1[2].h_val_x_reg_reg_n_0_[41] ),
        .O(h_val_28__1_carry_i_8_n_0));
  (* HLUTNM = "lutpair11" *) 
  LUT3 #(
    .INIT(8'h96)) 
    h_val_28__1_carry_i_9
       (.I0(h_val_28__1_carry_i_15_n_0),
        .I1(h_val_28__1_carry_i_16_n_0),
        .I2(h_val_28__1_carry_i_2_n_0),
        .O(h_val_28__1_carry_i_9_n_0));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    h_val_42__1_carry
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({h_val_42__1_carry_n_0,NLW_h_val_42__1_carry_CO_UNCONNECTED[6:0]}),
        .DI({h_val_42__1_carry_i_1_n_0,h_val_42__1_carry_i_2_n_0,h_val_42__1_carry_i_3_n_0,h_val_42__1_carry_i_4_n_0,h_val_42__1_carry_i_5_n_0,h_val_42__1_carry_i_6_n_0,h_val_42__1_carry_i_7_n_0,\genblk1[3].h_val_x_reg_reg_n_0_[55] }),
        .O({h_val_42__40[7:1],NLW_h_val_42__1_carry_O_UNCONNECTED[0]}),
        .S({h_val_42__1_carry_i_8_n_0,h_val_42__1_carry_i_9_n_0,h_val_42__1_carry_i_10_n_0,h_val_42__1_carry_i_11_n_0,h_val_42__1_carry_i_12_n_0,h_val_42__1_carry_i_13_n_0,h_val_42__1_carry_i_14_n_0,1'b0}));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    h_val_42__1_carry__0
       (.CI(h_val_42__1_carry_n_0),
        .CI_TOP(1'b0),
        .CO({NLW_h_val_42__1_carry__0_CO_UNCONNECTED[7:6],h_val_42__40[13],NLW_h_val_42__1_carry__0_CO_UNCONNECTED[4:0]}),
        .DI({NLW_h_val_42__1_carry__0_DI_UNCONNECTED[7:6],1'b0,h_val_42__1_carry__0_i_1_n_0,h_val_42__1_carry__0_i_2_n_0,h_val_42__1_carry__0_i_3_n_0,h_val_42__1_carry__0_i_4_n_0,h_val_42__1_carry__0_i_5_n_0}),
        .O({NLW_h_val_42__1_carry__0_O_UNCONNECTED[7:5],h_val_42__40[12:8]}),
        .S({NLW_h_val_42__1_carry__0_S_UNCONNECTED[7:6],1'b1,h_val_42__1_carry__0_i_6_n_0,h_val_42__1_carry__0_i_7_n_0,h_val_42__1_carry__0_i_8_n_0,h_val_42__1_carry__0_i_9_n_0,h_val_42__1_carry__0_i_10_n_0}));
  LUT6 #(
    .INIT(64'h0210400810020840)) 
    h_val_42__1_carry__0_i_1
       (.I0(\genblk1[3].h_val_x_reg_reg_n_0_[52] ),
        .I1(\genblk1[3].h_val_y_reg_reg_n_0_[52] ),
        .I2(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .I3(\genblk1[3].h_val_x_reg_reg_n_0_[53] ),
        .I4(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I5(\genblk1[3].h_val_y_reg_reg_n_0_[53] ),
        .O(h_val_42__1_carry__0_i_1_n_0));
  LUT6 #(
    .INIT(64'h6666699669966666)) 
    h_val_42__1_carry__0_i_10
       (.I0(h_val_42__1_carry__0_i_5_n_0),
        .I1(h_val_42__1_carry__0_i_14_n_0),
        .I2(\genblk1[3].h_val_y_reg_reg_n_0_[49] ),
        .I3(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I4(\genblk1[3].h_val_x_reg_reg_n_0_[49] ),
        .I5(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .O(h_val_42__1_carry__0_i_10_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_42__1_carry__0_i_11
       (.I0(\genblk1[3].h_val_y_reg_reg_n_0_[53] ),
        .I1(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I2(\genblk1[3].h_val_x_reg_reg_n_0_[53] ),
        .I3(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .O(h_val_42__1_carry__0_i_11_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_42__1_carry__0_i_12
       (.I0(\genblk1[3].h_val_y_reg_reg_n_0_[52] ),
        .I1(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I2(\genblk1[3].h_val_x_reg_reg_n_0_[52] ),
        .I3(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .O(h_val_42__1_carry__0_i_12_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_42__1_carry__0_i_13
       (.I0(\genblk1[3].h_val_y_reg_reg_n_0_[51] ),
        .I1(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I2(\genblk1[3].h_val_x_reg_reg_n_0_[51] ),
        .I3(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .O(h_val_42__1_carry__0_i_13_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_42__1_carry__0_i_14
       (.I0(\genblk1[3].h_val_y_reg_reg_n_0_[50] ),
        .I1(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I2(\genblk1[3].h_val_x_reg_reg_n_0_[50] ),
        .I3(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .O(h_val_42__1_carry__0_i_14_n_0));
  LUT6 #(
    .INIT(64'h0210400810020840)) 
    h_val_42__1_carry__0_i_2
       (.I0(\genblk1[3].h_val_x_reg_reg_n_0_[51] ),
        .I1(\genblk1[3].h_val_y_reg_reg_n_0_[51] ),
        .I2(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .I3(\genblk1[3].h_val_x_reg_reg_n_0_[52] ),
        .I4(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I5(\genblk1[3].h_val_y_reg_reg_n_0_[52] ),
        .O(h_val_42__1_carry__0_i_2_n_0));
  LUT6 #(
    .INIT(64'h0210400810020840)) 
    h_val_42__1_carry__0_i_3
       (.I0(\genblk1[3].h_val_x_reg_reg_n_0_[50] ),
        .I1(\genblk1[3].h_val_y_reg_reg_n_0_[50] ),
        .I2(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .I3(\genblk1[3].h_val_x_reg_reg_n_0_[51] ),
        .I4(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I5(\genblk1[3].h_val_y_reg_reg_n_0_[51] ),
        .O(h_val_42__1_carry__0_i_3_n_0));
  LUT6 #(
    .INIT(64'h0210400810020840)) 
    h_val_42__1_carry__0_i_4
       (.I0(\genblk1[3].h_val_x_reg_reg_n_0_[49] ),
        .I1(\genblk1[3].h_val_y_reg_reg_n_0_[49] ),
        .I2(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .I3(\genblk1[3].h_val_x_reg_reg_n_0_[50] ),
        .I4(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I5(\genblk1[3].h_val_y_reg_reg_n_0_[50] ),
        .O(h_val_42__1_carry__0_i_4_n_0));
  LUT5 #(
    .INIT(32'h69960000)) 
    h_val_42__1_carry__0_i_5
       (.I0(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .I1(\genblk1[3].h_val_x_reg_reg_n_0_[49] ),
        .I2(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I3(\genblk1[3].h_val_y_reg_reg_n_0_[49] ),
        .I4(h_val_42__1_carry_i_24_n_0),
        .O(h_val_42__1_carry__0_i_5_n_0));
  LUT6 #(
    .INIT(64'h04102FF81FF40820)) 
    h_val_42__1_carry__0_i_6
       (.I0(\genblk1[3].h_val_y_reg_reg_n_0_[52] ),
        .I1(\genblk1[3].h_val_x_reg_reg_n_0_[52] ),
        .I2(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .I3(\genblk1[3].h_val_x_reg_reg_n_0_[53] ),
        .I4(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I5(\genblk1[3].h_val_y_reg_reg_n_0_[53] ),
        .O(h_val_42__1_carry__0_i_6_n_0));
  LUT6 #(
    .INIT(64'h6666699669966666)) 
    h_val_42__1_carry__0_i_7
       (.I0(h_val_42__1_carry__0_i_2_n_0),
        .I1(h_val_42__1_carry__0_i_11_n_0),
        .I2(\genblk1[3].h_val_y_reg_reg_n_0_[52] ),
        .I3(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I4(\genblk1[3].h_val_x_reg_reg_n_0_[52] ),
        .I5(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .O(h_val_42__1_carry__0_i_7_n_0));
  LUT6 #(
    .INIT(64'h6666699669966666)) 
    h_val_42__1_carry__0_i_8
       (.I0(h_val_42__1_carry__0_i_3_n_0),
        .I1(h_val_42__1_carry__0_i_12_n_0),
        .I2(\genblk1[3].h_val_y_reg_reg_n_0_[51] ),
        .I3(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I4(\genblk1[3].h_val_x_reg_reg_n_0_[51] ),
        .I5(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .O(h_val_42__1_carry__0_i_8_n_0));
  LUT6 #(
    .INIT(64'h6666699669966666)) 
    h_val_42__1_carry__0_i_9
       (.I0(h_val_42__1_carry__0_i_4_n_0),
        .I1(h_val_42__1_carry__0_i_13_n_0),
        .I2(\genblk1[3].h_val_y_reg_reg_n_0_[50] ),
        .I3(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I4(\genblk1[3].h_val_x_reg_reg_n_0_[50] ),
        .I5(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .O(h_val_42__1_carry__0_i_9_n_0));
  (* HLUTNM = "lutpair15" *) 
  LUT2 #(
    .INIT(4'h1)) 
    h_val_42__1_carry_i_1
       (.I0(h_val_42__1_carry_i_15_n_0),
        .I1(h_val_42__1_carry_i_16_n_0),
        .O(h_val_42__1_carry_i_1_n_0));
  (* HLUTNM = "lutpair14" *) 
  LUT3 #(
    .INIT(8'h96)) 
    h_val_42__1_carry_i_10
       (.I0(h_val_42__1_carry_i_17_n_0),
        .I1(h_val_42__1_carry_i_18_n_0),
        .I2(h_val_42__1_carry_i_3_n_0),
        .O(h_val_42__1_carry_i_10_n_0));
  (* HLUTNM = "lutpair13" *) 
  LUT3 #(
    .INIT(8'h96)) 
    h_val_42__1_carry_i_11
       (.I0(h_val_42__1_carry_i_19_n_0),
        .I1(h_val_42__1_carry_i_20_n_0),
        .I2(h_val_42__1_carry_i_4_n_0),
        .O(h_val_42__1_carry_i_11_n_0));
  (* HLUTNM = "lutpair12" *) 
  LUT3 #(
    .INIT(8'h96)) 
    h_val_42__1_carry_i_12
       (.I0(h_val_42__1_carry_i_21_n_0),
        .I1(h_val_42__1_carry_i_22_n_0),
        .I2(h_val_42__1_carry_i_5_n_0),
        .O(h_val_42__1_carry_i_12_n_0));
  LUT3 #(
    .INIT(8'h96)) 
    h_val_42__1_carry_i_13
       (.I0(h_val_42__1_carry_i_6_n_0),
        .I1(h_val_42__1_carry_i_23_n_0),
        .I2(h_val_42__1_carry_i_25_n_0),
        .O(h_val_42__1_carry_i_13_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_42__1_carry_i_14
       (.I0(\genblk1[3].h_val_x_reg_reg_n_0_[43] ),
        .I1(\genblk1[3].h_val_z_reg_reg_n_0_[43] ),
        .I2(\genblk1[3].h_val_y_reg_reg_n_0_[43] ),
        .I3(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .O(h_val_42__1_carry_i_14_n_0));
  LUT6 #(
    .INIT(64'hF99F90099009F99F)) 
    h_val_42__1_carry_i_15
       (.I0(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .I1(\genblk1[3].h_val_x_reg_reg_n_0_[47] ),
        .I2(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I3(\genblk1[3].h_val_y_reg_reg_n_0_[47] ),
        .I4(\genblk1[3].h_val_z_reg_reg_n_0_[55] ),
        .I5(\genblk1[3].h_val_z_reg_reg_n_0_[47] ),
        .O(h_val_42__1_carry_i_15_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_42__1_carry_i_16
       (.I0(\genblk1[3].h_val_z_reg_reg_n_0_[48] ),
        .I1(\genblk1[3].h_val_z_reg_reg_n_0_[55] ),
        .I2(\genblk1[3].h_val_y_reg_reg_n_0_[48] ),
        .I3(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I4(\genblk1[3].h_val_x_reg_reg_n_0_[48] ),
        .I5(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .O(h_val_42__1_carry_i_16_n_0));
  LUT6 #(
    .INIT(64'hF99F90099009F99F)) 
    h_val_42__1_carry_i_17
       (.I0(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .I1(\genblk1[3].h_val_x_reg_reg_n_0_[46] ),
        .I2(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I3(\genblk1[3].h_val_y_reg_reg_n_0_[46] ),
        .I4(\genblk1[3].h_val_z_reg_reg_n_0_[55] ),
        .I5(\genblk1[3].h_val_z_reg_reg_n_0_[46] ),
        .O(h_val_42__1_carry_i_17_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_42__1_carry_i_18
       (.I0(\genblk1[3].h_val_z_reg_reg_n_0_[47] ),
        .I1(\genblk1[3].h_val_z_reg_reg_n_0_[55] ),
        .I2(\genblk1[3].h_val_y_reg_reg_n_0_[47] ),
        .I3(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I4(\genblk1[3].h_val_x_reg_reg_n_0_[47] ),
        .I5(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .O(h_val_42__1_carry_i_18_n_0));
  LUT6 #(
    .INIT(64'hF99F90099009F99F)) 
    h_val_42__1_carry_i_19
       (.I0(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .I1(\genblk1[3].h_val_x_reg_reg_n_0_[45] ),
        .I2(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I3(\genblk1[3].h_val_y_reg_reg_n_0_[45] ),
        .I4(\genblk1[3].h_val_z_reg_reg_n_0_[55] ),
        .I5(\genblk1[3].h_val_z_reg_reg_n_0_[45] ),
        .O(h_val_42__1_carry_i_19_n_0));
  (* HLUTNM = "lutpair14" *) 
  LUT2 #(
    .INIT(4'h1)) 
    h_val_42__1_carry_i_2
       (.I0(h_val_42__1_carry_i_17_n_0),
        .I1(h_val_42__1_carry_i_18_n_0),
        .O(h_val_42__1_carry_i_2_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_42__1_carry_i_20
       (.I0(\genblk1[3].h_val_z_reg_reg_n_0_[46] ),
        .I1(\genblk1[3].h_val_z_reg_reg_n_0_[55] ),
        .I2(\genblk1[3].h_val_y_reg_reg_n_0_[46] ),
        .I3(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I4(\genblk1[3].h_val_x_reg_reg_n_0_[46] ),
        .I5(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .O(h_val_42__1_carry_i_20_n_0));
  LUT6 #(
    .INIT(64'hF99F90099009F99F)) 
    h_val_42__1_carry_i_21
       (.I0(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .I1(\genblk1[3].h_val_x_reg_reg_n_0_[44] ),
        .I2(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I3(\genblk1[3].h_val_y_reg_reg_n_0_[44] ),
        .I4(\genblk1[3].h_val_z_reg_reg_n_0_[55] ),
        .I5(\genblk1[3].h_val_z_reg_reg_n_0_[44] ),
        .O(h_val_42__1_carry_i_21_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_42__1_carry_i_22
       (.I0(\genblk1[3].h_val_z_reg_reg_n_0_[45] ),
        .I1(\genblk1[3].h_val_z_reg_reg_n_0_[55] ),
        .I2(\genblk1[3].h_val_y_reg_reg_n_0_[45] ),
        .I3(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I4(\genblk1[3].h_val_x_reg_reg_n_0_[45] ),
        .I5(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .O(h_val_42__1_carry_i_22_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_42__1_carry_i_23
       (.I0(\genblk1[3].h_val_z_reg_reg_n_0_[44] ),
        .I1(\genblk1[3].h_val_z_reg_reg_n_0_[55] ),
        .I2(\genblk1[3].h_val_y_reg_reg_n_0_[44] ),
        .I3(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I4(\genblk1[3].h_val_x_reg_reg_n_0_[44] ),
        .I5(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .O(h_val_42__1_carry_i_23_n_0));
  LUT6 #(
    .INIT(64'h06606FF66FF60660)) 
    h_val_42__1_carry_i_24
       (.I0(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .I1(\genblk1[3].h_val_x_reg_reg_n_0_[48] ),
        .I2(\genblk1[3].h_val_z_reg_reg_n_0_[48] ),
        .I3(\genblk1[3].h_val_z_reg_reg_n_0_[55] ),
        .I4(\genblk1[3].h_val_y_reg_reg_n_0_[48] ),
        .I5(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .O(h_val_42__1_carry_i_24_n_0));
  LUT5 #(
    .INIT(32'h9D0119DF)) 
    h_val_42__1_carry_i_25
       (.I0(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I1(\genblk1[3].h_val_y_reg_reg_n_0_[43] ),
        .I2(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .I3(\genblk1[3].h_val_z_reg_reg_n_0_[43] ),
        .I4(\genblk1[3].h_val_z_reg_reg_n_0_[55] ),
        .O(h_val_42__1_carry_i_25_n_0));
  (* HLUTNM = "lutpair13" *) 
  LUT2 #(
    .INIT(4'h1)) 
    h_val_42__1_carry_i_3
       (.I0(h_val_42__1_carry_i_19_n_0),
        .I1(h_val_42__1_carry_i_20_n_0),
        .O(h_val_42__1_carry_i_3_n_0));
  (* HLUTNM = "lutpair12" *) 
  LUT2 #(
    .INIT(4'h1)) 
    h_val_42__1_carry_i_4
       (.I0(h_val_42__1_carry_i_21_n_0),
        .I1(h_val_42__1_carry_i_22_n_0),
        .O(h_val_42__1_carry_i_4_n_0));
  LUT6 #(
    .INIT(64'h0000000062FEE620)) 
    h_val_42__1_carry_i_5
       (.I0(\genblk1[3].h_val_z_reg_reg_n_0_[55] ),
        .I1(\genblk1[3].h_val_z_reg_reg_n_0_[43] ),
        .I2(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .I3(\genblk1[3].h_val_y_reg_reg_n_0_[43] ),
        .I4(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I5(h_val_42__1_carry_i_23_n_0),
        .O(h_val_42__1_carry_i_5_n_0));
  LUT6 #(
    .INIT(64'h0000936CC9360000)) 
    h_val_42__1_carry_i_6
       (.I0(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I1(\genblk1[3].h_val_y_reg_reg_n_0_[43] ),
        .I2(\genblk1[3].h_val_z_reg_reg_n_0_[55] ),
        .I3(\genblk1[3].h_val_z_reg_reg_n_0_[43] ),
        .I4(\genblk1[3].h_val_x_reg_reg_n_0_[43] ),
        .I5(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .O(h_val_42__1_carry_i_6_n_0));
  LUT6 #(
    .INIT(64'h936C6C9336C9C936)) 
    h_val_42__1_carry_i_7
       (.I0(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I1(\genblk1[3].h_val_y_reg_reg_n_0_[43] ),
        .I2(\genblk1[3].h_val_z_reg_reg_n_0_[55] ),
        .I3(\genblk1[3].h_val_z_reg_reg_n_0_[43] ),
        .I4(\genblk1[3].h_val_x_reg_reg_n_0_[43] ),
        .I5(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .O(h_val_42__1_carry_i_7_n_0));
  LUT6 #(
    .INIT(64'h6996966996696996)) 
    h_val_42__1_carry_i_8
       (.I0(h_val_42__1_carry_i_1_n_0),
        .I1(h_val_42__1_carry_i_24_n_0),
        .I2(\genblk1[3].h_val_y_reg_reg_n_0_[49] ),
        .I3(\genblk1[3].h_val_y_reg_reg_n_0_[55] ),
        .I4(\genblk1[3].h_val_x_reg_reg_n_0_[49] ),
        .I5(\genblk1[3].h_val_x_reg_reg_n_0_[55] ),
        .O(h_val_42__1_carry_i_8_n_0));
  (* HLUTNM = "lutpair15" *) 
  LUT3 #(
    .INIT(8'h96)) 
    h_val_42__1_carry_i_9
       (.I0(h_val_42__1_carry_i_15_n_0),
        .I1(h_val_42__1_carry_i_16_n_0),
        .I2(h_val_42__1_carry_i_2_n_0),
        .O(h_val_42__1_carry_i_9_n_0));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    h_val_56__1_carry
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({h_val_56__1_carry_n_0,NLW_h_val_56__1_carry_CO_UNCONNECTED[6:0]}),
        .DI({h_val_56__1_carry_i_1_n_0,h_val_56__1_carry_i_2_n_0,h_val_56__1_carry_i_3_n_0,h_val_56__1_carry_i_4_n_0,h_val_56__1_carry_i_5_n_0,h_val_56__1_carry_i_6_n_0,h_val_56__1_carry_i_7_n_0,\genblk1[4].h_val_x_reg_reg_n_0_[69] }),
        .O({h_val_56__40[7:1],NLW_h_val_56__1_carry_O_UNCONNECTED[0]}),
        .S({h_val_56__1_carry_i_8_n_0,h_val_56__1_carry_i_9_n_0,h_val_56__1_carry_i_10_n_0,h_val_56__1_carry_i_11_n_0,h_val_56__1_carry_i_12_n_0,h_val_56__1_carry_i_13_n_0,h_val_56__1_carry_i_14_n_0,1'b0}));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    h_val_56__1_carry__0
       (.CI(h_val_56__1_carry_n_0),
        .CI_TOP(1'b0),
        .CO({NLW_h_val_56__1_carry__0_CO_UNCONNECTED[7:6],h_val_56__40[13],NLW_h_val_56__1_carry__0_CO_UNCONNECTED[4:0]}),
        .DI({NLW_h_val_56__1_carry__0_DI_UNCONNECTED[7:6],1'b0,h_val_56__1_carry__0_i_1_n_0,h_val_56__1_carry__0_i_2_n_0,h_val_56__1_carry__0_i_3_n_0,h_val_56__1_carry__0_i_4_n_0,h_val_56__1_carry__0_i_5_n_0}),
        .O({NLW_h_val_56__1_carry__0_O_UNCONNECTED[7:5],h_val_56__40[12:8]}),
        .S({NLW_h_val_56__1_carry__0_S_UNCONNECTED[7:6],1'b1,h_val_56__1_carry__0_i_6_n_0,h_val_56__1_carry__0_i_7_n_0,h_val_56__1_carry__0_i_8_n_0,h_val_56__1_carry__0_i_9_n_0,h_val_56__1_carry__0_i_10_n_0}));
  LUT6 #(
    .INIT(64'h0210400810020840)) 
    h_val_56__1_carry__0_i_1
       (.I0(\genblk1[4].h_val_x_reg_reg_n_0_[66] ),
        .I1(\genblk1[4].h_val_y_reg_reg_n_0_[66] ),
        .I2(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .I3(\genblk1[4].h_val_x_reg_reg_n_0_[67] ),
        .I4(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I5(\genblk1[4].h_val_y_reg_reg_n_0_[67] ),
        .O(h_val_56__1_carry__0_i_1_n_0));
  LUT6 #(
    .INIT(64'h6666699669966666)) 
    h_val_56__1_carry__0_i_10
       (.I0(h_val_56__1_carry__0_i_5_n_0),
        .I1(h_val_56__1_carry__0_i_14_n_0),
        .I2(\genblk1[4].h_val_y_reg_reg_n_0_[63] ),
        .I3(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I4(\genblk1[4].h_val_x_reg_reg_n_0_[63] ),
        .I5(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .O(h_val_56__1_carry__0_i_10_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_56__1_carry__0_i_11
       (.I0(\genblk1[4].h_val_y_reg_reg_n_0_[67] ),
        .I1(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I2(\genblk1[4].h_val_x_reg_reg_n_0_[67] ),
        .I3(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .O(h_val_56__1_carry__0_i_11_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_56__1_carry__0_i_12
       (.I0(\genblk1[4].h_val_y_reg_reg_n_0_[66] ),
        .I1(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I2(\genblk1[4].h_val_x_reg_reg_n_0_[66] ),
        .I3(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .O(h_val_56__1_carry__0_i_12_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_56__1_carry__0_i_13
       (.I0(\genblk1[4].h_val_y_reg_reg_n_0_[65] ),
        .I1(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I2(\genblk1[4].h_val_x_reg_reg_n_0_[65] ),
        .I3(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .O(h_val_56__1_carry__0_i_13_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_56__1_carry__0_i_14
       (.I0(\genblk1[4].h_val_y_reg_reg_n_0_[64] ),
        .I1(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I2(\genblk1[4].h_val_x_reg_reg_n_0_[64] ),
        .I3(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .O(h_val_56__1_carry__0_i_14_n_0));
  LUT6 #(
    .INIT(64'h0210400810020840)) 
    h_val_56__1_carry__0_i_2
       (.I0(\genblk1[4].h_val_x_reg_reg_n_0_[65] ),
        .I1(\genblk1[4].h_val_y_reg_reg_n_0_[65] ),
        .I2(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .I3(\genblk1[4].h_val_x_reg_reg_n_0_[66] ),
        .I4(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I5(\genblk1[4].h_val_y_reg_reg_n_0_[66] ),
        .O(h_val_56__1_carry__0_i_2_n_0));
  LUT6 #(
    .INIT(64'h0210400810020840)) 
    h_val_56__1_carry__0_i_3
       (.I0(\genblk1[4].h_val_x_reg_reg_n_0_[64] ),
        .I1(\genblk1[4].h_val_y_reg_reg_n_0_[64] ),
        .I2(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .I3(\genblk1[4].h_val_x_reg_reg_n_0_[65] ),
        .I4(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I5(\genblk1[4].h_val_y_reg_reg_n_0_[65] ),
        .O(h_val_56__1_carry__0_i_3_n_0));
  LUT6 #(
    .INIT(64'h0210400810020840)) 
    h_val_56__1_carry__0_i_4
       (.I0(\genblk1[4].h_val_x_reg_reg_n_0_[63] ),
        .I1(\genblk1[4].h_val_y_reg_reg_n_0_[63] ),
        .I2(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .I3(\genblk1[4].h_val_x_reg_reg_n_0_[64] ),
        .I4(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I5(\genblk1[4].h_val_y_reg_reg_n_0_[64] ),
        .O(h_val_56__1_carry__0_i_4_n_0));
  LUT5 #(
    .INIT(32'h69960000)) 
    h_val_56__1_carry__0_i_5
       (.I0(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .I1(\genblk1[4].h_val_x_reg_reg_n_0_[63] ),
        .I2(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I3(\genblk1[4].h_val_y_reg_reg_n_0_[63] ),
        .I4(h_val_56__1_carry_i_24_n_0),
        .O(h_val_56__1_carry__0_i_5_n_0));
  LUT6 #(
    .INIT(64'h04102FF81FF40820)) 
    h_val_56__1_carry__0_i_6
       (.I0(\genblk1[4].h_val_y_reg_reg_n_0_[66] ),
        .I1(\genblk1[4].h_val_x_reg_reg_n_0_[66] ),
        .I2(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .I3(\genblk1[4].h_val_x_reg_reg_n_0_[67] ),
        .I4(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I5(\genblk1[4].h_val_y_reg_reg_n_0_[67] ),
        .O(h_val_56__1_carry__0_i_6_n_0));
  LUT6 #(
    .INIT(64'h6666699669966666)) 
    h_val_56__1_carry__0_i_7
       (.I0(h_val_56__1_carry__0_i_2_n_0),
        .I1(h_val_56__1_carry__0_i_11_n_0),
        .I2(\genblk1[4].h_val_y_reg_reg_n_0_[66] ),
        .I3(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I4(\genblk1[4].h_val_x_reg_reg_n_0_[66] ),
        .I5(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .O(h_val_56__1_carry__0_i_7_n_0));
  LUT6 #(
    .INIT(64'h6666699669966666)) 
    h_val_56__1_carry__0_i_8
       (.I0(h_val_56__1_carry__0_i_3_n_0),
        .I1(h_val_56__1_carry__0_i_12_n_0),
        .I2(\genblk1[4].h_val_y_reg_reg_n_0_[65] ),
        .I3(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I4(\genblk1[4].h_val_x_reg_reg_n_0_[65] ),
        .I5(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .O(h_val_56__1_carry__0_i_8_n_0));
  LUT6 #(
    .INIT(64'h6666699669966666)) 
    h_val_56__1_carry__0_i_9
       (.I0(h_val_56__1_carry__0_i_4_n_0),
        .I1(h_val_56__1_carry__0_i_13_n_0),
        .I2(\genblk1[4].h_val_y_reg_reg_n_0_[64] ),
        .I3(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I4(\genblk1[4].h_val_x_reg_reg_n_0_[64] ),
        .I5(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .O(h_val_56__1_carry__0_i_9_n_0));
  (* HLUTNM = "lutpair19" *) 
  LUT2 #(
    .INIT(4'h1)) 
    h_val_56__1_carry_i_1
       (.I0(h_val_56__1_carry_i_15_n_0),
        .I1(h_val_56__1_carry_i_16_n_0),
        .O(h_val_56__1_carry_i_1_n_0));
  (* HLUTNM = "lutpair18" *) 
  LUT3 #(
    .INIT(8'h96)) 
    h_val_56__1_carry_i_10
       (.I0(h_val_56__1_carry_i_17_n_0),
        .I1(h_val_56__1_carry_i_18_n_0),
        .I2(h_val_56__1_carry_i_3_n_0),
        .O(h_val_56__1_carry_i_10_n_0));
  (* HLUTNM = "lutpair17" *) 
  LUT3 #(
    .INIT(8'h96)) 
    h_val_56__1_carry_i_11
       (.I0(h_val_56__1_carry_i_19_n_0),
        .I1(h_val_56__1_carry_i_20_n_0),
        .I2(h_val_56__1_carry_i_4_n_0),
        .O(h_val_56__1_carry_i_11_n_0));
  (* HLUTNM = "lutpair16" *) 
  LUT3 #(
    .INIT(8'h96)) 
    h_val_56__1_carry_i_12
       (.I0(h_val_56__1_carry_i_21_n_0),
        .I1(h_val_56__1_carry_i_22_n_0),
        .I2(h_val_56__1_carry_i_5_n_0),
        .O(h_val_56__1_carry_i_12_n_0));
  LUT3 #(
    .INIT(8'h96)) 
    h_val_56__1_carry_i_13
       (.I0(h_val_56__1_carry_i_6_n_0),
        .I1(h_val_56__1_carry_i_23_n_0),
        .I2(h_val_56__1_carry_i_25_n_0),
        .O(h_val_56__1_carry_i_13_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_56__1_carry_i_14
       (.I0(\genblk1[4].h_val_x_reg_reg_n_0_[57] ),
        .I1(\genblk1[4].h_val_z_reg_reg_n_0_[57] ),
        .I2(\genblk1[4].h_val_y_reg_reg_n_0_[57] ),
        .I3(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .O(h_val_56__1_carry_i_14_n_0));
  LUT6 #(
    .INIT(64'hF99F90099009F99F)) 
    h_val_56__1_carry_i_15
       (.I0(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .I1(\genblk1[4].h_val_x_reg_reg_n_0_[61] ),
        .I2(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I3(\genblk1[4].h_val_y_reg_reg_n_0_[61] ),
        .I4(\genblk1[4].h_val_z_reg_reg_n_0_[69] ),
        .I5(\genblk1[4].h_val_z_reg_reg_n_0_[61] ),
        .O(h_val_56__1_carry_i_15_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_56__1_carry_i_16
       (.I0(\genblk1[4].h_val_z_reg_reg_n_0_[62] ),
        .I1(\genblk1[4].h_val_z_reg_reg_n_0_[69] ),
        .I2(\genblk1[4].h_val_y_reg_reg_n_0_[62] ),
        .I3(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I4(\genblk1[4].h_val_x_reg_reg_n_0_[62] ),
        .I5(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .O(h_val_56__1_carry_i_16_n_0));
  LUT6 #(
    .INIT(64'hF99F90099009F99F)) 
    h_val_56__1_carry_i_17
       (.I0(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .I1(\genblk1[4].h_val_x_reg_reg_n_0_[60] ),
        .I2(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I3(\genblk1[4].h_val_y_reg_reg_n_0_[60] ),
        .I4(\genblk1[4].h_val_z_reg_reg_n_0_[69] ),
        .I5(\genblk1[4].h_val_z_reg_reg_n_0_[60] ),
        .O(h_val_56__1_carry_i_17_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_56__1_carry_i_18
       (.I0(\genblk1[4].h_val_z_reg_reg_n_0_[61] ),
        .I1(\genblk1[4].h_val_z_reg_reg_n_0_[69] ),
        .I2(\genblk1[4].h_val_y_reg_reg_n_0_[61] ),
        .I3(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I4(\genblk1[4].h_val_x_reg_reg_n_0_[61] ),
        .I5(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .O(h_val_56__1_carry_i_18_n_0));
  LUT6 #(
    .INIT(64'hF99F90099009F99F)) 
    h_val_56__1_carry_i_19
       (.I0(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .I1(\genblk1[4].h_val_x_reg_reg_n_0_[59] ),
        .I2(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I3(\genblk1[4].h_val_y_reg_reg_n_0_[59] ),
        .I4(\genblk1[4].h_val_z_reg_reg_n_0_[69] ),
        .I5(\genblk1[4].h_val_z_reg_reg_n_0_[59] ),
        .O(h_val_56__1_carry_i_19_n_0));
  (* HLUTNM = "lutpair18" *) 
  LUT2 #(
    .INIT(4'h1)) 
    h_val_56__1_carry_i_2
       (.I0(h_val_56__1_carry_i_17_n_0),
        .I1(h_val_56__1_carry_i_18_n_0),
        .O(h_val_56__1_carry_i_2_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_56__1_carry_i_20
       (.I0(\genblk1[4].h_val_z_reg_reg_n_0_[60] ),
        .I1(\genblk1[4].h_val_z_reg_reg_n_0_[69] ),
        .I2(\genblk1[4].h_val_y_reg_reg_n_0_[60] ),
        .I3(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I4(\genblk1[4].h_val_x_reg_reg_n_0_[60] ),
        .I5(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .O(h_val_56__1_carry_i_20_n_0));
  LUT6 #(
    .INIT(64'hF99F90099009F99F)) 
    h_val_56__1_carry_i_21
       (.I0(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .I1(\genblk1[4].h_val_x_reg_reg_n_0_[58] ),
        .I2(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I3(\genblk1[4].h_val_y_reg_reg_n_0_[58] ),
        .I4(\genblk1[4].h_val_z_reg_reg_n_0_[69] ),
        .I5(\genblk1[4].h_val_z_reg_reg_n_0_[58] ),
        .O(h_val_56__1_carry_i_21_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_56__1_carry_i_22
       (.I0(\genblk1[4].h_val_z_reg_reg_n_0_[59] ),
        .I1(\genblk1[4].h_val_z_reg_reg_n_0_[69] ),
        .I2(\genblk1[4].h_val_y_reg_reg_n_0_[59] ),
        .I3(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I4(\genblk1[4].h_val_x_reg_reg_n_0_[59] ),
        .I5(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .O(h_val_56__1_carry_i_22_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_56__1_carry_i_23
       (.I0(\genblk1[4].h_val_z_reg_reg_n_0_[58] ),
        .I1(\genblk1[4].h_val_z_reg_reg_n_0_[69] ),
        .I2(\genblk1[4].h_val_y_reg_reg_n_0_[58] ),
        .I3(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I4(\genblk1[4].h_val_x_reg_reg_n_0_[58] ),
        .I5(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .O(h_val_56__1_carry_i_23_n_0));
  LUT6 #(
    .INIT(64'h06606FF66FF60660)) 
    h_val_56__1_carry_i_24
       (.I0(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .I1(\genblk1[4].h_val_x_reg_reg_n_0_[62] ),
        .I2(\genblk1[4].h_val_z_reg_reg_n_0_[62] ),
        .I3(\genblk1[4].h_val_z_reg_reg_n_0_[69] ),
        .I4(\genblk1[4].h_val_y_reg_reg_n_0_[62] ),
        .I5(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .O(h_val_56__1_carry_i_24_n_0));
  LUT5 #(
    .INIT(32'h9D0119DF)) 
    h_val_56__1_carry_i_25
       (.I0(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I1(\genblk1[4].h_val_y_reg_reg_n_0_[57] ),
        .I2(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .I3(\genblk1[4].h_val_z_reg_reg_n_0_[57] ),
        .I4(\genblk1[4].h_val_z_reg_reg_n_0_[69] ),
        .O(h_val_56__1_carry_i_25_n_0));
  (* HLUTNM = "lutpair17" *) 
  LUT2 #(
    .INIT(4'h1)) 
    h_val_56__1_carry_i_3
       (.I0(h_val_56__1_carry_i_19_n_0),
        .I1(h_val_56__1_carry_i_20_n_0),
        .O(h_val_56__1_carry_i_3_n_0));
  (* HLUTNM = "lutpair16" *) 
  LUT2 #(
    .INIT(4'h1)) 
    h_val_56__1_carry_i_4
       (.I0(h_val_56__1_carry_i_21_n_0),
        .I1(h_val_56__1_carry_i_22_n_0),
        .O(h_val_56__1_carry_i_4_n_0));
  LUT6 #(
    .INIT(64'h0000000062FEE620)) 
    h_val_56__1_carry_i_5
       (.I0(\genblk1[4].h_val_z_reg_reg_n_0_[69] ),
        .I1(\genblk1[4].h_val_z_reg_reg_n_0_[57] ),
        .I2(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .I3(\genblk1[4].h_val_y_reg_reg_n_0_[57] ),
        .I4(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I5(h_val_56__1_carry_i_23_n_0),
        .O(h_val_56__1_carry_i_5_n_0));
  LUT6 #(
    .INIT(64'h0000936CC9360000)) 
    h_val_56__1_carry_i_6
       (.I0(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I1(\genblk1[4].h_val_y_reg_reg_n_0_[57] ),
        .I2(\genblk1[4].h_val_z_reg_reg_n_0_[69] ),
        .I3(\genblk1[4].h_val_z_reg_reg_n_0_[57] ),
        .I4(\genblk1[4].h_val_x_reg_reg_n_0_[57] ),
        .I5(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .O(h_val_56__1_carry_i_6_n_0));
  LUT6 #(
    .INIT(64'h936C6C9336C9C936)) 
    h_val_56__1_carry_i_7
       (.I0(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I1(\genblk1[4].h_val_y_reg_reg_n_0_[57] ),
        .I2(\genblk1[4].h_val_z_reg_reg_n_0_[69] ),
        .I3(\genblk1[4].h_val_z_reg_reg_n_0_[57] ),
        .I4(\genblk1[4].h_val_x_reg_reg_n_0_[57] ),
        .I5(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .O(h_val_56__1_carry_i_7_n_0));
  LUT6 #(
    .INIT(64'h6996966996696996)) 
    h_val_56__1_carry_i_8
       (.I0(h_val_56__1_carry_i_1_n_0),
        .I1(h_val_56__1_carry_i_24_n_0),
        .I2(\genblk1[4].h_val_y_reg_reg_n_0_[63] ),
        .I3(\genblk1[4].h_val_y_reg_reg_n_0_[69] ),
        .I4(\genblk1[4].h_val_x_reg_reg_n_0_[63] ),
        .I5(\genblk1[4].h_val_x_reg_reg_n_0_[69] ),
        .O(h_val_56__1_carry_i_8_n_0));
  (* HLUTNM = "lutpair19" *) 
  LUT3 #(
    .INIT(8'h96)) 
    h_val_56__1_carry_i_9
       (.I0(h_val_56__1_carry_i_15_n_0),
        .I1(h_val_56__1_carry_i_16_n_0),
        .I2(h_val_56__1_carry_i_2_n_0),
        .O(h_val_56__1_carry_i_9_n_0));
  (* OPT_MODIFIED = "PROPCONST" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    h_val_70__1_carry
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({h_val_70__1_carry_n_0,NLW_h_val_70__1_carry_CO_UNCONNECTED[6:0]}),
        .DI({h_val_70__1_carry_i_1__0_n_0,h_val_70__1_carry_i_2__0_n_0,h_val_70__1_carry_i_3__0_n_0,h_val_70__1_carry_i_4__0_n_0,h_val_70__1_carry_i_5_n_0,h_val_70__1_carry_i_6_n_0,h_val_70__1_carry_i_7_n_0,\genblk1[5].h_val_x_reg_reg_n_0_[83] }),
        .O({h_val_70__40[7:1],NLW_h_val_70__1_carry_O_UNCONNECTED[0]}),
        .S({h_val_70__1_carry_i_8_n_0,h_val_70__1_carry_i_9__0_n_0,h_val_70__1_carry_i_10__0_n_0,h_val_70__1_carry_i_11__0_n_0,h_val_70__1_carry_i_12__0_n_0,h_val_70__1_carry_i_13__0_n_0,h_val_70__1_carry_i_14__0_n_0,1'b0}));
  (* OPT_MODIFIED = "RETARGET" *) 
  CARRY8 #(
    .CARRY_TYPE("SINGLE_CY8")) 
    h_val_70__1_carry__0
       (.CI(h_val_70__1_carry_n_0),
        .CI_TOP(1'b0),
        .CO({NLW_h_val_70__1_carry__0_CO_UNCONNECTED[7:6],h_val_70__40[13],NLW_h_val_70__1_carry__0_CO_UNCONNECTED[4:0]}),
        .DI({NLW_h_val_70__1_carry__0_DI_UNCONNECTED[7:6],1'b0,h_val_70__1_carry_i_1_n_0,h_val_70__1_carry_i_2_n_0,h_val_70__1_carry_i_3_n_0,h_val_70__1_carry_i_4_n_0,h_val_70__1_carry_i_5__0_n_0}),
        .O({NLW_h_val_70__1_carry__0_O_UNCONNECTED[7:5],h_val_70__40[12:8]}),
        .S({NLW_h_val_70__1_carry__0_S_UNCONNECTED[7:6],1'b1,h_val_70__1_carry_i_6__0_n_0,h_val_70__1_carry_i_7__0_n_0,h_val_70__1_carry_i_8__0_n_0,h_val_70__1_carry_i_9_n_0,h_val_70__1_carry_i_10_n_0}));
  LUT6 #(
    .INIT(64'h0210400810020840)) 
    h_val_70__1_carry_i_1
       (.I0(\genblk1[5].h_val_x_reg_reg_n_0_[80] ),
        .I1(\genblk1[5].h_val_y_reg_reg_n_0_[80] ),
        .I2(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .I3(\genblk1[5].h_val_x_reg_reg_n_0_[81] ),
        .I4(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I5(\genblk1[5].h_val_y_reg_reg_n_0_[81] ),
        .O(h_val_70__1_carry_i_1_n_0));
  LUT6 #(
    .INIT(64'h6666699669966666)) 
    h_val_70__1_carry_i_10
       (.I0(h_val_70__1_carry_i_5__0_n_0),
        .I1(h_val_70__1_carry_i_14_n_0),
        .I2(\genblk1[5].h_val_y_reg_reg_n_0_[77] ),
        .I3(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I4(\genblk1[5].h_val_x_reg_reg_n_0_[77] ),
        .I5(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .O(h_val_70__1_carry_i_10_n_0));
  (* HLUTNM = "lutpair22" *) 
  LUT3 #(
    .INIT(8'h96)) 
    h_val_70__1_carry_i_10__0
       (.I0(h_val_70__1_carry_i_17_n_0),
        .I1(h_val_70__1_carry_i_18_n_0),
        .I2(h_val_70__1_carry_i_3__0_n_0),
        .O(h_val_70__1_carry_i_10__0_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_70__1_carry_i_11
       (.I0(\genblk1[5].h_val_y_reg_reg_n_0_[81] ),
        .I1(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I2(\genblk1[5].h_val_x_reg_reg_n_0_[81] ),
        .I3(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .O(h_val_70__1_carry_i_11_n_0));
  (* HLUTNM = "lutpair21" *) 
  LUT3 #(
    .INIT(8'h96)) 
    h_val_70__1_carry_i_11__0
       (.I0(h_val_70__1_carry_i_19_n_0),
        .I1(h_val_70__1_carry_i_20_n_0),
        .I2(h_val_70__1_carry_i_4__0_n_0),
        .O(h_val_70__1_carry_i_11__0_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_70__1_carry_i_12
       (.I0(\genblk1[5].h_val_y_reg_reg_n_0_[80] ),
        .I1(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I2(\genblk1[5].h_val_x_reg_reg_n_0_[80] ),
        .I3(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .O(h_val_70__1_carry_i_12_n_0));
  (* HLUTNM = "lutpair20" *) 
  LUT3 #(
    .INIT(8'h96)) 
    h_val_70__1_carry_i_12__0
       (.I0(h_val_70__1_carry_i_21_n_0),
        .I1(h_val_70__1_carry_i_22_n_0),
        .I2(h_val_70__1_carry_i_5_n_0),
        .O(h_val_70__1_carry_i_12__0_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_70__1_carry_i_13
       (.I0(\genblk1[5].h_val_y_reg_reg_n_0_[79] ),
        .I1(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I2(\genblk1[5].h_val_x_reg_reg_n_0_[79] ),
        .I3(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .O(h_val_70__1_carry_i_13_n_0));
  LUT3 #(
    .INIT(8'h96)) 
    h_val_70__1_carry_i_13__0
       (.I0(h_val_70__1_carry_i_6_n_0),
        .I1(h_val_70__1_carry_i_23_n_0),
        .I2(h_val_70__1_carry_i_25_n_0),
        .O(h_val_70__1_carry_i_13__0_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_70__1_carry_i_14
       (.I0(\genblk1[5].h_val_y_reg_reg_n_0_[78] ),
        .I1(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I2(\genblk1[5].h_val_x_reg_reg_n_0_[78] ),
        .I3(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .O(h_val_70__1_carry_i_14_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    h_val_70__1_carry_i_14__0
       (.I0(\genblk1[5].h_val_x_reg_reg_n_0_[71] ),
        .I1(\genblk1[5].h_val_z_reg_reg_n_0_[71] ),
        .I2(\genblk1[5].h_val_y_reg_reg_n_0_[71] ),
        .I3(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .O(h_val_70__1_carry_i_14__0_n_0));
  LUT6 #(
    .INIT(64'hF99F90099009F99F)) 
    h_val_70__1_carry_i_15
       (.I0(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .I1(\genblk1[5].h_val_x_reg_reg_n_0_[75] ),
        .I2(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I3(\genblk1[5].h_val_y_reg_reg_n_0_[75] ),
        .I4(\genblk1[5].h_val_z_reg_reg_n_0_[83] ),
        .I5(\genblk1[5].h_val_z_reg_reg_n_0_[75] ),
        .O(h_val_70__1_carry_i_15_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_70__1_carry_i_16
       (.I0(\genblk1[5].h_val_z_reg_reg_n_0_[76] ),
        .I1(\genblk1[5].h_val_z_reg_reg_n_0_[83] ),
        .I2(\genblk1[5].h_val_y_reg_reg_n_0_[76] ),
        .I3(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I4(\genblk1[5].h_val_x_reg_reg_n_0_[76] ),
        .I5(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .O(h_val_70__1_carry_i_16_n_0));
  LUT6 #(
    .INIT(64'hF99F90099009F99F)) 
    h_val_70__1_carry_i_17
       (.I0(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .I1(\genblk1[5].h_val_x_reg_reg_n_0_[74] ),
        .I2(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I3(\genblk1[5].h_val_y_reg_reg_n_0_[74] ),
        .I4(\genblk1[5].h_val_z_reg_reg_n_0_[83] ),
        .I5(\genblk1[5].h_val_z_reg_reg_n_0_[74] ),
        .O(h_val_70__1_carry_i_17_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_70__1_carry_i_18
       (.I0(\genblk1[5].h_val_z_reg_reg_n_0_[75] ),
        .I1(\genblk1[5].h_val_z_reg_reg_n_0_[83] ),
        .I2(\genblk1[5].h_val_y_reg_reg_n_0_[75] ),
        .I3(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I4(\genblk1[5].h_val_x_reg_reg_n_0_[75] ),
        .I5(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .O(h_val_70__1_carry_i_18_n_0));
  LUT6 #(
    .INIT(64'hF99F90099009F99F)) 
    h_val_70__1_carry_i_19
       (.I0(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .I1(\genblk1[5].h_val_x_reg_reg_n_0_[73] ),
        .I2(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I3(\genblk1[5].h_val_y_reg_reg_n_0_[73] ),
        .I4(\genblk1[5].h_val_z_reg_reg_n_0_[83] ),
        .I5(\genblk1[5].h_val_z_reg_reg_n_0_[73] ),
        .O(h_val_70__1_carry_i_19_n_0));
  (* HLUTNM = "lutpair23" *) 
  LUT2 #(
    .INIT(4'h1)) 
    h_val_70__1_carry_i_1__0
       (.I0(h_val_70__1_carry_i_15_n_0),
        .I1(h_val_70__1_carry_i_16_n_0),
        .O(h_val_70__1_carry_i_1__0_n_0));
  LUT6 #(
    .INIT(64'h0210400810020840)) 
    h_val_70__1_carry_i_2
       (.I0(\genblk1[5].h_val_x_reg_reg_n_0_[79] ),
        .I1(\genblk1[5].h_val_y_reg_reg_n_0_[79] ),
        .I2(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .I3(\genblk1[5].h_val_x_reg_reg_n_0_[80] ),
        .I4(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I5(\genblk1[5].h_val_y_reg_reg_n_0_[80] ),
        .O(h_val_70__1_carry_i_2_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_70__1_carry_i_20
       (.I0(\genblk1[5].h_val_z_reg_reg_n_0_[74] ),
        .I1(\genblk1[5].h_val_z_reg_reg_n_0_[83] ),
        .I2(\genblk1[5].h_val_y_reg_reg_n_0_[74] ),
        .I3(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I4(\genblk1[5].h_val_x_reg_reg_n_0_[74] ),
        .I5(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .O(h_val_70__1_carry_i_20_n_0));
  LUT6 #(
    .INIT(64'hF99F90099009F99F)) 
    h_val_70__1_carry_i_21
       (.I0(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .I1(\genblk1[5].h_val_x_reg_reg_n_0_[72] ),
        .I2(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I3(\genblk1[5].h_val_y_reg_reg_n_0_[72] ),
        .I4(\genblk1[5].h_val_z_reg_reg_n_0_[83] ),
        .I5(\genblk1[5].h_val_z_reg_reg_n_0_[72] ),
        .O(h_val_70__1_carry_i_21_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_70__1_carry_i_22
       (.I0(\genblk1[5].h_val_z_reg_reg_n_0_[73] ),
        .I1(\genblk1[5].h_val_z_reg_reg_n_0_[83] ),
        .I2(\genblk1[5].h_val_y_reg_reg_n_0_[73] ),
        .I3(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I4(\genblk1[5].h_val_x_reg_reg_n_0_[73] ),
        .I5(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .O(h_val_70__1_carry_i_22_n_0));
  LUT6 #(
    .INIT(64'h9669699669969669)) 
    h_val_70__1_carry_i_23
       (.I0(\genblk1[5].h_val_z_reg_reg_n_0_[72] ),
        .I1(\genblk1[5].h_val_z_reg_reg_n_0_[83] ),
        .I2(\genblk1[5].h_val_y_reg_reg_n_0_[72] ),
        .I3(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I4(\genblk1[5].h_val_x_reg_reg_n_0_[72] ),
        .I5(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .O(h_val_70__1_carry_i_23_n_0));
  LUT6 #(
    .INIT(64'h06606FF66FF60660)) 
    h_val_70__1_carry_i_24
       (.I0(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .I1(\genblk1[5].h_val_x_reg_reg_n_0_[76] ),
        .I2(\genblk1[5].h_val_z_reg_reg_n_0_[76] ),
        .I3(\genblk1[5].h_val_z_reg_reg_n_0_[83] ),
        .I4(\genblk1[5].h_val_y_reg_reg_n_0_[76] ),
        .I5(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .O(h_val_70__1_carry_i_24_n_0));
  LUT5 #(
    .INIT(32'h9D0119DF)) 
    h_val_70__1_carry_i_25
       (.I0(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I1(\genblk1[5].h_val_y_reg_reg_n_0_[71] ),
        .I2(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .I3(\genblk1[5].h_val_z_reg_reg_n_0_[71] ),
        .I4(\genblk1[5].h_val_z_reg_reg_n_0_[83] ),
        .O(h_val_70__1_carry_i_25_n_0));
  (* HLUTNM = "lutpair22" *) 
  LUT2 #(
    .INIT(4'h1)) 
    h_val_70__1_carry_i_2__0
       (.I0(h_val_70__1_carry_i_17_n_0),
        .I1(h_val_70__1_carry_i_18_n_0),
        .O(h_val_70__1_carry_i_2__0_n_0));
  LUT6 #(
    .INIT(64'h0210400810020840)) 
    h_val_70__1_carry_i_3
       (.I0(\genblk1[5].h_val_x_reg_reg_n_0_[78] ),
        .I1(\genblk1[5].h_val_y_reg_reg_n_0_[78] ),
        .I2(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .I3(\genblk1[5].h_val_x_reg_reg_n_0_[79] ),
        .I4(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I5(\genblk1[5].h_val_y_reg_reg_n_0_[79] ),
        .O(h_val_70__1_carry_i_3_n_0));
  (* HLUTNM = "lutpair21" *) 
  LUT2 #(
    .INIT(4'h1)) 
    h_val_70__1_carry_i_3__0
       (.I0(h_val_70__1_carry_i_19_n_0),
        .I1(h_val_70__1_carry_i_20_n_0),
        .O(h_val_70__1_carry_i_3__0_n_0));
  LUT6 #(
    .INIT(64'h0210400810020840)) 
    h_val_70__1_carry_i_4
       (.I0(\genblk1[5].h_val_x_reg_reg_n_0_[77] ),
        .I1(\genblk1[5].h_val_y_reg_reg_n_0_[77] ),
        .I2(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .I3(\genblk1[5].h_val_x_reg_reg_n_0_[78] ),
        .I4(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I5(\genblk1[5].h_val_y_reg_reg_n_0_[78] ),
        .O(h_val_70__1_carry_i_4_n_0));
  (* HLUTNM = "lutpair20" *) 
  LUT2 #(
    .INIT(4'h1)) 
    h_val_70__1_carry_i_4__0
       (.I0(h_val_70__1_carry_i_21_n_0),
        .I1(h_val_70__1_carry_i_22_n_0),
        .O(h_val_70__1_carry_i_4__0_n_0));
  LUT6 #(
    .INIT(64'h0000000062FEE620)) 
    h_val_70__1_carry_i_5
       (.I0(\genblk1[5].h_val_z_reg_reg_n_0_[83] ),
        .I1(\genblk1[5].h_val_z_reg_reg_n_0_[71] ),
        .I2(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .I3(\genblk1[5].h_val_y_reg_reg_n_0_[71] ),
        .I4(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I5(h_val_70__1_carry_i_23_n_0),
        .O(h_val_70__1_carry_i_5_n_0));
  LUT5 #(
    .INIT(32'h69960000)) 
    h_val_70__1_carry_i_5__0
       (.I0(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .I1(\genblk1[5].h_val_x_reg_reg_n_0_[77] ),
        .I2(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I3(\genblk1[5].h_val_y_reg_reg_n_0_[77] ),
        .I4(h_val_70__1_carry_i_24_n_0),
        .O(h_val_70__1_carry_i_5__0_n_0));
  LUT6 #(
    .INIT(64'h0000936CC9360000)) 
    h_val_70__1_carry_i_6
       (.I0(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I1(\genblk1[5].h_val_y_reg_reg_n_0_[71] ),
        .I2(\genblk1[5].h_val_z_reg_reg_n_0_[83] ),
        .I3(\genblk1[5].h_val_z_reg_reg_n_0_[71] ),
        .I4(\genblk1[5].h_val_x_reg_reg_n_0_[71] ),
        .I5(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .O(h_val_70__1_carry_i_6_n_0));
  LUT6 #(
    .INIT(64'h04102FF81FF40820)) 
    h_val_70__1_carry_i_6__0
       (.I0(\genblk1[5].h_val_y_reg_reg_n_0_[80] ),
        .I1(\genblk1[5].h_val_x_reg_reg_n_0_[80] ),
        .I2(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .I3(\genblk1[5].h_val_x_reg_reg_n_0_[81] ),
        .I4(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I5(\genblk1[5].h_val_y_reg_reg_n_0_[81] ),
        .O(h_val_70__1_carry_i_6__0_n_0));
  LUT6 #(
    .INIT(64'h936C6C9336C9C936)) 
    h_val_70__1_carry_i_7
       (.I0(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I1(\genblk1[5].h_val_y_reg_reg_n_0_[71] ),
        .I2(\genblk1[5].h_val_z_reg_reg_n_0_[83] ),
        .I3(\genblk1[5].h_val_z_reg_reg_n_0_[71] ),
        .I4(\genblk1[5].h_val_x_reg_reg_n_0_[71] ),
        .I5(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .O(h_val_70__1_carry_i_7_n_0));
  LUT6 #(
    .INIT(64'h6666699669966666)) 
    h_val_70__1_carry_i_7__0
       (.I0(h_val_70__1_carry_i_2_n_0),
        .I1(h_val_70__1_carry_i_11_n_0),
        .I2(\genblk1[5].h_val_y_reg_reg_n_0_[80] ),
        .I3(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I4(\genblk1[5].h_val_x_reg_reg_n_0_[80] ),
        .I5(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .O(h_val_70__1_carry_i_7__0_n_0));
  LUT6 #(
    .INIT(64'h6996966996696996)) 
    h_val_70__1_carry_i_8
       (.I0(h_val_70__1_carry_i_1__0_n_0),
        .I1(h_val_70__1_carry_i_24_n_0),
        .I2(\genblk1[5].h_val_y_reg_reg_n_0_[77] ),
        .I3(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I4(\genblk1[5].h_val_x_reg_reg_n_0_[77] ),
        .I5(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .O(h_val_70__1_carry_i_8_n_0));
  LUT6 #(
    .INIT(64'h6666699669966666)) 
    h_val_70__1_carry_i_8__0
       (.I0(h_val_70__1_carry_i_3_n_0),
        .I1(h_val_70__1_carry_i_12_n_0),
        .I2(\genblk1[5].h_val_y_reg_reg_n_0_[79] ),
        .I3(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I4(\genblk1[5].h_val_x_reg_reg_n_0_[79] ),
        .I5(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .O(h_val_70__1_carry_i_8__0_n_0));
  LUT6 #(
    .INIT(64'h6666699669966666)) 
    h_val_70__1_carry_i_9
       (.I0(h_val_70__1_carry_i_4_n_0),
        .I1(h_val_70__1_carry_i_13_n_0),
        .I2(\genblk1[5].h_val_y_reg_reg_n_0_[78] ),
        .I3(\genblk1[5].h_val_y_reg_reg_n_0_[83] ),
        .I4(\genblk1[5].h_val_x_reg_reg_n_0_[78] ),
        .I5(\genblk1[5].h_val_x_reg_reg_n_0_[83] ),
        .O(h_val_70__1_carry_i_9_n_0));
  (* HLUTNM = "lutpair23" *) 
  LUT3 #(
    .INIT(8'h96)) 
    h_val_70__1_carry_i_9__0
       (.I0(h_val_70__1_carry_i_15_n_0),
        .I1(h_val_70__1_carry_i_16_n_0),
        .I2(h_val_70__1_carry_i_2__0_n_0),
        .O(h_val_70__1_carry_i_9__0_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry__0_i_1
       (.I0(cg_q[13]),
        .I1(\genblk1[0].g_val_reg0__36_carry__0_n_11 ),
        .O(i__carry__0_i_1_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry__0_i_1__0
       (.I0(cg_q[13]),
        .I1(\genblk1[1].g_val_reg0__36_carry__0_n_11 ),
        .O(i__carry__0_i_1__0_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry__0_i_1__1
       (.I0(cg_q[13]),
        .I1(\genblk1[2].g_val_reg0__36_carry__0_n_11 ),
        .O(i__carry__0_i_1__1_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry__0_i_1__2
       (.I0(cg_q[13]),
        .I1(\genblk1[3].g_val_reg0__36_carry__0_n_11 ),
        .O(i__carry__0_i_1__2_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry__0_i_1__3
       (.I0(cg_q[13]),
        .I1(\genblk1[4].g_val_reg0__36_carry__0_n_11 ),
        .O(i__carry__0_i_1__3_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry__0_i_2
       (.I0(cg_q[12]),
        .I1(\genblk1[0].g_val_reg0__36_carry__0_n_12 ),
        .O(i__carry__0_i_2_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry__0_i_2__0
       (.I0(cg_q[12]),
        .I1(\genblk1[1].g_val_reg0__36_carry__0_n_12 ),
        .O(i__carry__0_i_2__0_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry__0_i_2__1
       (.I0(cg_q[12]),
        .I1(\genblk1[2].g_val_reg0__36_carry__0_n_12 ),
        .O(i__carry__0_i_2__1_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry__0_i_2__2
       (.I0(cg_q[12]),
        .I1(\genblk1[3].g_val_reg0__36_carry__0_n_12 ),
        .O(i__carry__0_i_2__2_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry__0_i_2__3
       (.I0(cg_q[12]),
        .I1(\genblk1[4].g_val_reg0__36_carry__0_n_12 ),
        .O(i__carry__0_i_2__3_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry__0_i_3
       (.I0(cg_q[11]),
        .I1(\genblk1[0].g_val_reg0__36_carry__0_n_13 ),
        .O(i__carry__0_i_3_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry__0_i_3__0
       (.I0(cg_q[11]),
        .I1(\genblk1[1].g_val_reg0__36_carry__0_n_13 ),
        .O(i__carry__0_i_3__0_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry__0_i_3__1
       (.I0(cg_q[11]),
        .I1(\genblk1[2].g_val_reg0__36_carry__0_n_13 ),
        .O(i__carry__0_i_3__1_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry__0_i_3__2
       (.I0(cg_q[11]),
        .I1(\genblk1[3].g_val_reg0__36_carry__0_n_13 ),
        .O(i__carry__0_i_3__2_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry__0_i_3__3
       (.I0(cg_q[11]),
        .I1(\genblk1[4].g_val_reg0__36_carry__0_n_13 ),
        .O(i__carry__0_i_3__3_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry__0_i_4
       (.I0(cg_q[10]),
        .I1(\genblk1[0].g_val_reg0__36_carry__0_n_14 ),
        .O(i__carry__0_i_4_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry__0_i_4__0
       (.I0(cg_q[10]),
        .I1(\genblk1[1].g_val_reg0__36_carry__0_n_14 ),
        .O(i__carry__0_i_4__0_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry__0_i_4__1
       (.I0(cg_q[10]),
        .I1(\genblk1[2].g_val_reg0__36_carry__0_n_14 ),
        .O(i__carry__0_i_4__1_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry__0_i_4__2
       (.I0(cg_q[10]),
        .I1(\genblk1[3].g_val_reg0__36_carry__0_n_14 ),
        .O(i__carry__0_i_4__2_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry__0_i_4__3
       (.I0(cg_q[10]),
        .I1(\genblk1[4].g_val_reg0__36_carry__0_n_14 ),
        .O(i__carry__0_i_4__3_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry__0_i_5
       (.I0(cg_q[9]),
        .I1(\genblk1[0].g_val_reg0__36_carry__0_n_15 ),
        .O(i__carry__0_i_5_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry__0_i_5__0
       (.I0(cg_q[9]),
        .I1(\genblk1[1].g_val_reg0__36_carry__0_n_15 ),
        .O(i__carry__0_i_5__0_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry__0_i_5__1
       (.I0(cg_q[9]),
        .I1(\genblk1[2].g_val_reg0__36_carry__0_n_15 ),
        .O(i__carry__0_i_5__1_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry__0_i_5__2
       (.I0(cg_q[9]),
        .I1(\genblk1[3].g_val_reg0__36_carry__0_n_15 ),
        .O(i__carry__0_i_5__2_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry__0_i_5__3
       (.I0(cg_q[9]),
        .I1(\genblk1[4].g_val_reg0__36_carry__0_n_15 ),
        .O(i__carry__0_i_5__3_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_1
       (.I0(cg_q[13]),
        .I1(\genblk1[5].g_val_reg0__36_carry__0_n_11 ),
        .O(i__carry_i_1_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_1__0
       (.I0(cg_q[8]),
        .I1(\genblk1[0].g_val_reg0__36_carry_n_8 ),
        .O(i__carry_i_1__0_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_1__1
       (.I0(cg_q[8]),
        .I1(\genblk1[1].g_val_reg0__36_carry_n_8 ),
        .O(i__carry_i_1__1_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_1__2
       (.I0(cg_q[8]),
        .I1(\genblk1[2].g_val_reg0__36_carry_n_8 ),
        .O(i__carry_i_1__2_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_1__3
       (.I0(cg_q[8]),
        .I1(\genblk1[3].g_val_reg0__36_carry_n_8 ),
        .O(i__carry_i_1__3_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_1__4
       (.I0(cg_q[8]),
        .I1(\genblk1[4].g_val_reg0__36_carry_n_8 ),
        .O(i__carry_i_1__4_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_1__5
       (.I0(cg_q[8]),
        .I1(\genblk1[5].g_val_reg0__36_carry_n_8 ),
        .O(i__carry_i_1__5_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_2
       (.I0(cg_q[7]),
        .I1(\genblk1[0].g_val_reg0__36_carry_n_9 ),
        .O(i__carry_i_2_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_2__0
       (.I0(cg_q[7]),
        .I1(\genblk1[1].g_val_reg0__36_carry_n_9 ),
        .O(i__carry_i_2__0_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_2__1
       (.I0(cg_q[7]),
        .I1(\genblk1[2].g_val_reg0__36_carry_n_9 ),
        .O(i__carry_i_2__1_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_2__2
       (.I0(cg_q[7]),
        .I1(\genblk1[3].g_val_reg0__36_carry_n_9 ),
        .O(i__carry_i_2__2_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_2__3
       (.I0(cg_q[7]),
        .I1(\genblk1[4].g_val_reg0__36_carry_n_9 ),
        .O(i__carry_i_2__3_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_2__4
       (.I0(cg_q[7]),
        .I1(\genblk1[5].g_val_reg0__36_carry_n_9 ),
        .O(i__carry_i_2__4_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_2__5
       (.I0(cg_q[12]),
        .I1(\genblk1[5].g_val_reg0__36_carry__0_n_12 ),
        .O(i__carry_i_2__5_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_3
       (.I0(cg_q[6]),
        .I1(\genblk1[0].g_val_reg0__36_carry_n_10 ),
        .O(i__carry_i_3_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_3__0
       (.I0(cg_q[6]),
        .I1(\genblk1[1].g_val_reg0__36_carry_n_10 ),
        .O(i__carry_i_3__0_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_3__1
       (.I0(cg_q[6]),
        .I1(\genblk1[2].g_val_reg0__36_carry_n_10 ),
        .O(i__carry_i_3__1_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_3__2
       (.I0(cg_q[6]),
        .I1(\genblk1[3].g_val_reg0__36_carry_n_10 ),
        .O(i__carry_i_3__2_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_3__3
       (.I0(cg_q[6]),
        .I1(\genblk1[4].g_val_reg0__36_carry_n_10 ),
        .O(i__carry_i_3__3_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_3__4
       (.I0(cg_q[6]),
        .I1(\genblk1[5].g_val_reg0__36_carry_n_10 ),
        .O(i__carry_i_3__4_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_3__5
       (.I0(cg_q[11]),
        .I1(\genblk1[5].g_val_reg0__36_carry__0_n_13 ),
        .O(i__carry_i_3__5_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_4
       (.I0(cg_q[5]),
        .I1(\genblk1[0].g_val_reg0__36_carry_n_11 ),
        .O(i__carry_i_4_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_4__0
       (.I0(cg_q[5]),
        .I1(\genblk1[1].g_val_reg0__36_carry_n_11 ),
        .O(i__carry_i_4__0_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_4__1
       (.I0(cg_q[5]),
        .I1(\genblk1[2].g_val_reg0__36_carry_n_11 ),
        .O(i__carry_i_4__1_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_4__2
       (.I0(cg_q[5]),
        .I1(\genblk1[3].g_val_reg0__36_carry_n_11 ),
        .O(i__carry_i_4__2_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_4__3
       (.I0(cg_q[5]),
        .I1(\genblk1[4].g_val_reg0__36_carry_n_11 ),
        .O(i__carry_i_4__3_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_4__4
       (.I0(cg_q[5]),
        .I1(\genblk1[5].g_val_reg0__36_carry_n_11 ),
        .O(i__carry_i_4__4_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_4__5
       (.I0(cg_q[10]),
        .I1(\genblk1[5].g_val_reg0__36_carry__0_n_14 ),
        .O(i__carry_i_4__5_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_5
       (.I0(cg_q[4]),
        .I1(\genblk1[0].g_val_reg0__36_carry_n_12 ),
        .O(i__carry_i_5_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_5__0
       (.I0(cg_q[4]),
        .I1(\genblk1[1].g_val_reg0__36_carry_n_12 ),
        .O(i__carry_i_5__0_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_5__1
       (.I0(cg_q[4]),
        .I1(\genblk1[2].g_val_reg0__36_carry_n_12 ),
        .O(i__carry_i_5__1_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_5__2
       (.I0(cg_q[4]),
        .I1(\genblk1[3].g_val_reg0__36_carry_n_12 ),
        .O(i__carry_i_5__2_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_5__3
       (.I0(cg_q[4]),
        .I1(\genblk1[4].g_val_reg0__36_carry_n_12 ),
        .O(i__carry_i_5__3_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_5__4
       (.I0(cg_q[4]),
        .I1(\genblk1[5].g_val_reg0__36_carry_n_12 ),
        .O(i__carry_i_5__4_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_5__5
       (.I0(cg_q[9]),
        .I1(\genblk1[5].g_val_reg0__36_carry__0_n_15 ),
        .O(i__carry_i_5__5_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_6
       (.I0(cg_q[3]),
        .I1(\genblk1[0].g_val_reg0__36_carry_n_13 ),
        .O(i__carry_i_6_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_6__0
       (.I0(cg_q[3]),
        .I1(\genblk1[1].g_val_reg0__36_carry_n_13 ),
        .O(i__carry_i_6__0_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_6__1
       (.I0(cg_q[3]),
        .I1(\genblk1[2].g_val_reg0__36_carry_n_13 ),
        .O(i__carry_i_6__1_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_6__2
       (.I0(cg_q[3]),
        .I1(\genblk1[3].g_val_reg0__36_carry_n_13 ),
        .O(i__carry_i_6__2_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_6__3
       (.I0(cg_q[3]),
        .I1(\genblk1[4].g_val_reg0__36_carry_n_13 ),
        .O(i__carry_i_6__3_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_6__4
       (.I0(cg_q[3]),
        .I1(\genblk1[5].g_val_reg0__36_carry_n_13 ),
        .O(i__carry_i_6__4_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_7
       (.I0(cg_q[2]),
        .I1(\genblk1[0].g_val_reg0__36_carry_n_14 ),
        .O(i__carry_i_7_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_7__0
       (.I0(cg_q[2]),
        .I1(\genblk1[1].g_val_reg0__36_carry_n_14 ),
        .O(i__carry_i_7__0_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_7__1
       (.I0(cg_q[2]),
        .I1(\genblk1[2].g_val_reg0__36_carry_n_14 ),
        .O(i__carry_i_7__1_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_7__2
       (.I0(cg_q[2]),
        .I1(\genblk1[3].g_val_reg0__36_carry_n_14 ),
        .O(i__carry_i_7__2_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_7__3
       (.I0(cg_q[2]),
        .I1(\genblk1[4].g_val_reg0__36_carry_n_14 ),
        .O(i__carry_i_7__3_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_7__4
       (.I0(cg_q[2]),
        .I1(\genblk1[5].g_val_reg0__36_carry_n_14 ),
        .O(i__carry_i_7__4_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_8
       (.I0(cg_q[1]),
        .I1(\genblk1[0].g_val_reg0__36_carry_n_15 ),
        .O(i__carry_i_8_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_8__0
       (.I0(cg_q[1]),
        .I1(\genblk1[1].g_val_reg0__36_carry_n_15 ),
        .O(i__carry_i_8__0_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_8__1
       (.I0(cg_q[1]),
        .I1(\genblk1[2].g_val_reg0__36_carry_n_15 ),
        .O(i__carry_i_8__1_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_8__2
       (.I0(cg_q[1]),
        .I1(\genblk1[3].g_val_reg0__36_carry_n_15 ),
        .O(i__carry_i_8__2_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_8__3
       (.I0(cg_q[1]),
        .I1(\genblk1[4].g_val_reg0__36_carry_n_15 ),
        .O(i__carry_i_8__3_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    i__carry_i_8__4
       (.I0(cg_q[1]),
        .I1(\genblk1[5].g_val_reg0__36_carry_n_15 ),
        .O(i__carry_i_8__4_n_0));
  dly_cell u_dly_cell
       (.clk_global(clk_global),
        .cost_valid(cost_valid),
        .reset_q(reset_q),
        .valid_q(valid_q));
endmodule

module dly_cell
   (cost_valid,
    clk_global,
    valid_q,
    reset_q);
  output cost_valid;
  input clk_global;
  input valid_q;
  input reset_q;

  wire clk_global;
  wire cost_valid;
  wire \din_dly[0][0]_i_1_n_0 ;
  wire reset_q;
  wire valid_q;

  LUT2 #(
    .INIT(4'h2)) 
    \din_dly[0][0]_i_1 
       (.I0(valid_q),
        .I1(reset_q),
        .O(\din_dly[0][0]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \din_dly_reg[0][0] 
       (.C(clk_global),
        .CE(1'b1),
        .D(\din_dly[0][0]_i_1_n_0 ),
        .Q(cost_valid),
        .R(1'b0));
endmodule

(* ECO_CHECKSUM = "f6997e23" *) 
(* NotValidForBitStream *)
module routeracc_cost_registered
   (clk,
    reset,
    valid,
    per_x,
    per_y,
    per_z,
    end_x,
    end_y,
    cen_x,
    cen_y,
    end_z,
    cen_z,
    cen_g,
    f_out,
    g_out,
    valid_out);
  input clk;
  input reset;
  input valid;
  input [47:0]per_x;
  input [47:0]per_y;
  input [17:0]per_z;
  input [7:0]end_x;
  input [7:0]end_y;
  input [7:0]cen_x;
  input [7:0]cen_y;
  input [2:0]end_z;
  input [2:0]cen_z;
  input [13:0]cen_g;
  output [95:0]f_out;
  output [83:0]g_out;
  output valid_out;

  wire \<const0> ;
  wire [13:0]cen_g;
  wire [7:0]cen_x;
  wire [7:0]cen_y;
  wire [2:0]cen_z;
  wire [13:0]cg_q;
  wire clk;
  (* MAX_PROG_DELAY = "0" *) wire clk_global;
  wire cost_valid;
  wire [7:0]cx_q;
  wire [7:0]cy_q;
  wire [2:0]cz_q;
  wire [7:0]end_x;
  wire [7:0]end_y;
  wire [2:0]end_z;
  wire [7:0]ex_q;
  wire [7:0]ey_q;
  wire [2:0]ez_q;
  wire [94:0]f;
  wire [94:0]\^f_out ;
  wire [83:1]g;
  wire [83:1]\^g_out ;
  wire \genblk1[0].g_val_reg0_carry_i_32_n_0 ;
  wire \genblk1[0].g_val_reg0_carry_i_33_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_32_n_0 ;
  wire \genblk1[1].g_val_reg0_carry_i_33_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_32_n_0 ;
  wire \genblk1[2].g_val_reg0_carry_i_33_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_32_n_0 ;
  wire \genblk1[3].g_val_reg0_carry_i_33_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_32_n_0 ;
  wire \genblk1[4].g_val_reg0_carry_i_33_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_32_n_0 ;
  wire \genblk1[5].g_val_reg0_carry_i_33_n_0 ;
  wire [47:0]per_x;
  wire [47:0]per_y;
  wire [17:0]per_z;
  wire [47:0]px_q;
  wire [47:0]py_q;
  wire [17:0]pz_q;
  wire reset;
  wire reset_q;
  wire valid;
  wire valid_out;
  wire valid_q;

  assign f_out[95] = \<const0> ;
  assign f_out[94:80] = \^f_out [94:80];
  assign f_out[79] = \<const0> ;
  assign f_out[78:64] = \^f_out [78:64];
  assign f_out[63] = \<const0> ;
  assign f_out[62:48] = \^f_out [62:48];
  assign f_out[47] = \<const0> ;
  assign f_out[46:32] = \^f_out [46:32];
  assign f_out[31] = \<const0> ;
  assign f_out[30:16] = \^f_out [30:16];
  assign f_out[15] = \<const0> ;
  assign f_out[14:0] = \^f_out [14:0];
  assign g_out[83:71] = \^g_out [83:71];
  assign g_out[70] = \^g_out [56];
  assign g_out[69:43] = \^g_out [69:43];
  assign g_out[42] = \^g_out [56];
  assign g_out[41:29] = \^g_out [41:29];
  assign g_out[28] = \^g_out [56];
  assign g_out[27:15] = \^g_out [27:15];
  assign g_out[14] = \^g_out [56];
  assign g_out[13:1] = \^g_out [13:1];
  assign g_out[0] = \^g_out [56];
  GND GND
       (.G(\<const0> ));
  FDRE #(
    .INIT(1'b0)) 
    \cg_q_reg[0] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_g[0]),
        .Q(cg_q[0]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cg_q_reg[10] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_g[10]),
        .Q(cg_q[10]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cg_q_reg[11] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_g[11]),
        .Q(cg_q[11]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cg_q_reg[12] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_g[12]),
        .Q(cg_q[12]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cg_q_reg[13] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_g[13]),
        .Q(cg_q[13]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cg_q_reg[1] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_g[1]),
        .Q(cg_q[1]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cg_q_reg[2] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_g[2]),
        .Q(cg_q[2]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cg_q_reg[3] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_g[3]),
        .Q(cg_q[3]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cg_q_reg[4] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_g[4]),
        .Q(cg_q[4]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cg_q_reg[5] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_g[5]),
        .Q(cg_q[5]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cg_q_reg[6] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_g[6]),
        .Q(cg_q[6]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cg_q_reg[7] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_g[7]),
        .Q(cg_q[7]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cg_q_reg[8] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_g[8]),
        .Q(cg_q[8]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cg_q_reg[9] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_g[9]),
        .Q(cg_q[9]),
        .R(1'b0));
  (* BOX_TYPE = "PRIMITIVE" *) 
  (* XILINX_LEGACY_PRIM = "BUFG" *) 
  (* XILINX_TRANSFORM_PINMAP = "VCC:CE" *) 
  BUFGCE #(
    .CE_TYPE("ASYNC"),
    .SIM_DEVICE("ULTRASCALE_PLUS"),
    .STARTUP_SYNC("FALSE")) 
    clock_buffer
       (.CE(1'b1),
        .I(clk),
        .O(clk_global));
  FDRE #(
    .INIT(1'b0)) 
    \cx_q_reg[0] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_x[0]),
        .Q(cx_q[0]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cx_q_reg[1] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_x[1]),
        .Q(cx_q[1]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cx_q_reg[2] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_x[2]),
        .Q(cx_q[2]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cx_q_reg[3] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_x[3]),
        .Q(cx_q[3]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cx_q_reg[4] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_x[4]),
        .Q(cx_q[4]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cx_q_reg[5] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_x[5]),
        .Q(cx_q[5]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cx_q_reg[6] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_x[6]),
        .Q(cx_q[6]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cx_q_reg[7] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_x[7]),
        .Q(cx_q[7]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cy_q_reg[0] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_y[0]),
        .Q(cy_q[0]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cy_q_reg[1] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_y[1]),
        .Q(cy_q[1]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cy_q_reg[2] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_y[2]),
        .Q(cy_q[2]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cy_q_reg[3] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_y[3]),
        .Q(cy_q[3]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cy_q_reg[4] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_y[4]),
        .Q(cy_q[4]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cy_q_reg[5] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_y[5]),
        .Q(cy_q[5]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cy_q_reg[6] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_y[6]),
        .Q(cy_q[6]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cy_q_reg[7] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_y[7]),
        .Q(cy_q[7]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cz_q_reg[0] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_z[0]),
        .Q(cz_q[0]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cz_q_reg[1] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_z[1]),
        .Q(cz_q[1]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \cz_q_reg[2] 
       (.C(clk_global),
        .CE(1'b1),
        .D(cen_z[2]),
        .Q(cz_q[2]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \ex_q_reg[0] 
       (.C(clk_global),
        .CE(1'b1),
        .D(end_x[0]),
        .Q(ex_q[0]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \ex_q_reg[1] 
       (.C(clk_global),
        .CE(1'b1),
        .D(end_x[1]),
        .Q(ex_q[1]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \ex_q_reg[2] 
       (.C(clk_global),
        .CE(1'b1),
        .D(end_x[2]),
        .Q(ex_q[2]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \ex_q_reg[3] 
       (.C(clk_global),
        .CE(1'b1),
        .D(end_x[3]),
        .Q(ex_q[3]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \ex_q_reg[4] 
       (.C(clk_global),
        .CE(1'b1),
        .D(end_x[4]),
        .Q(ex_q[4]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \ex_q_reg[5] 
       (.C(clk_global),
        .CE(1'b1),
        .D(end_x[5]),
        .Q(ex_q[5]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \ex_q_reg[6] 
       (.C(clk_global),
        .CE(1'b1),
        .D(end_x[6]),
        .Q(ex_q[6]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \ex_q_reg[7] 
       (.C(clk_global),
        .CE(1'b1),
        .D(end_x[7]),
        .Q(ex_q[7]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \ey_q_reg[0] 
       (.C(clk_global),
        .CE(1'b1),
        .D(end_y[0]),
        .Q(ey_q[0]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \ey_q_reg[1] 
       (.C(clk_global),
        .CE(1'b1),
        .D(end_y[1]),
        .Q(ey_q[1]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \ey_q_reg[2] 
       (.C(clk_global),
        .CE(1'b1),
        .D(end_y[2]),
        .Q(ey_q[2]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \ey_q_reg[3] 
       (.C(clk_global),
        .CE(1'b1),
        .D(end_y[3]),
        .Q(ey_q[3]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \ey_q_reg[4] 
       (.C(clk_global),
        .CE(1'b1),
        .D(end_y[4]),
        .Q(ey_q[4]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \ey_q_reg[5] 
       (.C(clk_global),
        .CE(1'b1),
        .D(end_y[5]),
        .Q(ey_q[5]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \ey_q_reg[6] 
       (.C(clk_global),
        .CE(1'b1),
        .D(end_y[6]),
        .Q(ey_q[6]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \ey_q_reg[7] 
       (.C(clk_global),
        .CE(1'b1),
        .D(end_y[7]),
        .Q(ey_q[7]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \ez_q_reg[0] 
       (.C(clk_global),
        .CE(1'b1),
        .D(end_z[0]),
        .Q(ez_q[0]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \ez_q_reg[1] 
       (.C(clk_global),
        .CE(1'b1),
        .D(end_z[1]),
        .Q(ez_q[1]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \ez_q_reg[2] 
       (.C(clk_global),
        .CE(1'b1),
        .D(end_z[2]),
        .Q(ez_q[2]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[0] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[0]),
        .Q(\^f_out [0]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[10] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[10]),
        .Q(\^f_out [10]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[11] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[11]),
        .Q(\^f_out [11]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[12] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[12]),
        .Q(\^f_out [12]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[13] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[13]),
        .Q(\^f_out [13]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[14] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[14]),
        .Q(\^f_out [14]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[16] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[16]),
        .Q(\^f_out [16]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[17] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[17]),
        .Q(\^f_out [17]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[18] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[18]),
        .Q(\^f_out [18]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[19] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[19]),
        .Q(\^f_out [19]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[1] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[1]),
        .Q(\^f_out [1]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[20] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[20]),
        .Q(\^f_out [20]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[21] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[21]),
        .Q(\^f_out [21]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[22] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[22]),
        .Q(\^f_out [22]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[23] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[23]),
        .Q(\^f_out [23]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[24] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[24]),
        .Q(\^f_out [24]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[25] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[25]),
        .Q(\^f_out [25]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[26] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[26]),
        .Q(\^f_out [26]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[27] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[27]),
        .Q(\^f_out [27]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[28] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[28]),
        .Q(\^f_out [28]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[29] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[29]),
        .Q(\^f_out [29]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[2] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[2]),
        .Q(\^f_out [2]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[30] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[30]),
        .Q(\^f_out [30]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[32] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[32]),
        .Q(\^f_out [32]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[33] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[33]),
        .Q(\^f_out [33]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[34] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[34]),
        .Q(\^f_out [34]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[35] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[35]),
        .Q(\^f_out [35]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[36] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[36]),
        .Q(\^f_out [36]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[37] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[37]),
        .Q(\^f_out [37]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[38] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[38]),
        .Q(\^f_out [38]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[39] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[39]),
        .Q(\^f_out [39]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[3] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[3]),
        .Q(\^f_out [3]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[40] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[40]),
        .Q(\^f_out [40]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[41] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[41]),
        .Q(\^f_out [41]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[42] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[42]),
        .Q(\^f_out [42]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[43] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[43]),
        .Q(\^f_out [43]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[44] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[44]),
        .Q(\^f_out [44]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[45] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[45]),
        .Q(\^f_out [45]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[46] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[46]),
        .Q(\^f_out [46]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[48] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[48]),
        .Q(\^f_out [48]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[49] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[49]),
        .Q(\^f_out [49]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[4] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[4]),
        .Q(\^f_out [4]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[50] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[50]),
        .Q(\^f_out [50]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[51] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[51]),
        .Q(\^f_out [51]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[52] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[52]),
        .Q(\^f_out [52]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[53] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[53]),
        .Q(\^f_out [53]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[54] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[54]),
        .Q(\^f_out [54]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[55] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[55]),
        .Q(\^f_out [55]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[56] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[56]),
        .Q(\^f_out [56]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[57] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[57]),
        .Q(\^f_out [57]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[58] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[58]),
        .Q(\^f_out [58]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[59] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[59]),
        .Q(\^f_out [59]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[5] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[5]),
        .Q(\^f_out [5]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[60] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[60]),
        .Q(\^f_out [60]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[61] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[61]),
        .Q(\^f_out [61]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[62] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[62]),
        .Q(\^f_out [62]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[64] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[64]),
        .Q(\^f_out [64]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[65] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[65]),
        .Q(\^f_out [65]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[66] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[66]),
        .Q(\^f_out [66]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[67] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[67]),
        .Q(\^f_out [67]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[68] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[68]),
        .Q(\^f_out [68]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[69] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[69]),
        .Q(\^f_out [69]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[6] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[6]),
        .Q(\^f_out [6]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[70] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[70]),
        .Q(\^f_out [70]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[71] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[71]),
        .Q(\^f_out [71]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[72] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[72]),
        .Q(\^f_out [72]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[73] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[73]),
        .Q(\^f_out [73]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[74] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[74]),
        .Q(\^f_out [74]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[75] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[75]),
        .Q(\^f_out [75]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[76] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[76]),
        .Q(\^f_out [76]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[77] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[77]),
        .Q(\^f_out [77]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[78] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[78]),
        .Q(\^f_out [78]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[7] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[7]),
        .Q(\^f_out [7]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[80] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[80]),
        .Q(\^f_out [80]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[81] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[81]),
        .Q(\^f_out [81]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[82] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[82]),
        .Q(\^f_out [82]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[83] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[83]),
        .Q(\^f_out [83]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[84] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[84]),
        .Q(\^f_out [84]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[85] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[85]),
        .Q(\^f_out [85]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[86] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[86]),
        .Q(\^f_out [86]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[87] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[87]),
        .Q(\^f_out [87]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[88] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[88]),
        .Q(\^f_out [88]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[89] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[89]),
        .Q(\^f_out [89]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[8] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[8]),
        .Q(\^f_out [8]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[90] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[90]),
        .Q(\^f_out [90]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[91] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[91]),
        .Q(\^f_out [91]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[92] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[92]),
        .Q(\^f_out [92]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[93] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[93]),
        .Q(\^f_out [93]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[94] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[94]),
        .Q(\^f_out [94]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \f_out_reg[9] 
       (.C(clk_global),
        .CE(1'b1),
        .D(f[9]),
        .Q(\^f_out [9]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[10] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[10]),
        .Q(\^g_out [10]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[11] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[11]),
        .Q(\^g_out [11]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[12] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[12]),
        .Q(\^g_out [12]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[13] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[13]),
        .Q(\^g_out [13]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[15] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[15]),
        .Q(\^g_out [15]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[16] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[16]),
        .Q(\^g_out [16]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[17] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[17]),
        .Q(\^g_out [17]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[18] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[18]),
        .Q(\^g_out [18]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[19] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[19]),
        .Q(\^g_out [19]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[1] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[1]),
        .Q(\^g_out [1]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[20] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[20]),
        .Q(\^g_out [20]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[21] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[21]),
        .Q(\^g_out [21]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[22] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[22]),
        .Q(\^g_out [22]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[23] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[23]),
        .Q(\^g_out [23]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[24] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[24]),
        .Q(\^g_out [24]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[25] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[25]),
        .Q(\^g_out [25]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[26] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[26]),
        .Q(\^g_out [26]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[27] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[27]),
        .Q(\^g_out [27]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[29] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[29]),
        .Q(\^g_out [29]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[2] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[2]),
        .Q(\^g_out [2]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[30] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[30]),
        .Q(\^g_out [30]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[31] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[31]),
        .Q(\^g_out [31]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[32] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[32]),
        .Q(\^g_out [32]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[33] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[33]),
        .Q(\^g_out [33]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[34] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[34]),
        .Q(\^g_out [34]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[35] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[35]),
        .Q(\^g_out [35]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[36] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[36]),
        .Q(\^g_out [36]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[37] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[37]),
        .Q(\^g_out [37]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[38] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[38]),
        .Q(\^g_out [38]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[39] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[39]),
        .Q(\^g_out [39]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[3] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[3]),
        .Q(\^g_out [3]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[40] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[40]),
        .Q(\^g_out [40]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[41] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[41]),
        .Q(\^g_out [41]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[43] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[43]),
        .Q(\^g_out [43]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[44] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[44]),
        .Q(\^g_out [44]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[45] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[45]),
        .Q(\^g_out [45]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[46] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[46]),
        .Q(\^g_out [46]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[47] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[47]),
        .Q(\^g_out [47]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[48] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[48]),
        .Q(\^g_out [48]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[49] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[49]),
        .Q(\^g_out [49]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[4] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[4]),
        .Q(\^g_out [4]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[50] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[50]),
        .Q(\^g_out [50]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[51] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[51]),
        .Q(\^g_out [51]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[52] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[52]),
        .Q(\^g_out [52]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[53] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[53]),
        .Q(\^g_out [53]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[54] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[54]),
        .Q(\^g_out [54]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[55] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[55]),
        .Q(\^g_out [55]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[57] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[57]),
        .Q(\^g_out [57]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[58] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[58]),
        .Q(\^g_out [58]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[59] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[59]),
        .Q(\^g_out [59]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[5] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[5]),
        .Q(\^g_out [5]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[60] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[60]),
        .Q(\^g_out [60]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[61] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[61]),
        .Q(\^g_out [61]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[62] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[62]),
        .Q(\^g_out [62]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[63] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[63]),
        .Q(\^g_out [63]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[64] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[64]),
        .Q(\^g_out [64]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[65] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[65]),
        .Q(\^g_out [65]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[66] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[66]),
        .Q(\^g_out [66]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[67] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[67]),
        .Q(\^g_out [67]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[68] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[68]),
        .Q(\^g_out [68]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[69] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[69]),
        .Q(\^g_out [69]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[6] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[6]),
        .Q(\^g_out [6]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[70] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[70]),
        .Q(\^g_out [56]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[71] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[71]),
        .Q(\^g_out [71]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[72] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[72]),
        .Q(\^g_out [72]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[73] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[73]),
        .Q(\^g_out [73]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[74] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[74]),
        .Q(\^g_out [74]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[75] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[75]),
        .Q(\^g_out [75]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[76] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[76]),
        .Q(\^g_out [76]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[77] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[77]),
        .Q(\^g_out [77]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[78] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[78]),
        .Q(\^g_out [78]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[79] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[79]),
        .Q(\^g_out [79]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[7] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[7]),
        .Q(\^g_out [7]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[80] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[80]),
        .Q(\^g_out [80]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[81] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[81]),
        .Q(\^g_out [81]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[82] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[82]),
        .Q(\^g_out [82]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[83] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[83]),
        .Q(\^g_out [83]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[8] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[8]),
        .Q(\^g_out [8]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \g_out_reg[9] 
       (.C(clk_global),
        .CE(1'b1),
        .D(g[9]),
        .Q(\^g_out [9]),
        .R(1'b0));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[0].g_val_reg0_carry_i_32 
       (.I0(cz_q[2]),
        .I1(pz_q[2]),
        .I2(pz_q[1]),
        .I3(cz_q[1]),
        .I4(pz_q[0]),
        .I5(cz_q[0]),
        .O(\genblk1[0].g_val_reg0_carry_i_32_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[0].g_val_reg0_carry_i_33 
       (.I0(pz_q[0]),
        .I1(cz_q[0]),
        .I2(pz_q[1]),
        .I3(cz_q[1]),
        .O(\genblk1[0].g_val_reg0_carry_i_33_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[1].g_val_reg0_carry_i_32 
       (.I0(cz_q[2]),
        .I1(pz_q[5]),
        .I2(pz_q[4]),
        .I3(cz_q[1]),
        .I4(pz_q[3]),
        .I5(cz_q[0]),
        .O(\genblk1[1].g_val_reg0_carry_i_32_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[1].g_val_reg0_carry_i_33 
       (.I0(pz_q[3]),
        .I1(cz_q[0]),
        .I2(pz_q[4]),
        .I3(cz_q[1]),
        .O(\genblk1[1].g_val_reg0_carry_i_33_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[2].g_val_reg0_carry_i_32 
       (.I0(cz_q[2]),
        .I1(pz_q[8]),
        .I2(pz_q[7]),
        .I3(cz_q[1]),
        .I4(pz_q[6]),
        .I5(cz_q[0]),
        .O(\genblk1[2].g_val_reg0_carry_i_32_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[2].g_val_reg0_carry_i_33 
       (.I0(pz_q[6]),
        .I1(cz_q[0]),
        .I2(pz_q[7]),
        .I3(cz_q[1]),
        .O(\genblk1[2].g_val_reg0_carry_i_33_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[3].g_val_reg0_carry_i_32 
       (.I0(cz_q[2]),
        .I1(pz_q[11]),
        .I2(pz_q[10]),
        .I3(cz_q[1]),
        .I4(pz_q[9]),
        .I5(cz_q[0]),
        .O(\genblk1[3].g_val_reg0_carry_i_32_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[3].g_val_reg0_carry_i_33 
       (.I0(pz_q[9]),
        .I1(cz_q[0]),
        .I2(pz_q[10]),
        .I3(cz_q[1]),
        .O(\genblk1[3].g_val_reg0_carry_i_33_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[4].g_val_reg0_carry_i_32 
       (.I0(cz_q[2]),
        .I1(pz_q[14]),
        .I2(pz_q[13]),
        .I3(cz_q[1]),
        .I4(pz_q[12]),
        .I5(cz_q[0]),
        .O(\genblk1[4].g_val_reg0_carry_i_32_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[4].g_val_reg0_carry_i_33 
       (.I0(pz_q[12]),
        .I1(cz_q[0]),
        .I2(pz_q[13]),
        .I3(cz_q[1]),
        .O(\genblk1[4].g_val_reg0_carry_i_33_n_0 ));
  LUT6 #(
    .INIT(64'h6696996969666696)) 
    \genblk1[5].g_val_reg0_carry_i_32 
       (.I0(cz_q[2]),
        .I1(pz_q[17]),
        .I2(pz_q[16]),
        .I3(cz_q[1]),
        .I4(pz_q[15]),
        .I5(cz_q[0]),
        .O(\genblk1[5].g_val_reg0_carry_i_32_n_0 ));
  LUT4 #(
    .INIT(16'h2DD2)) 
    \genblk1[5].g_val_reg0_carry_i_33 
       (.I0(pz_q[15]),
        .I1(cz_q[0]),
        .I2(pz_q[16]),
        .I3(cz_q[1]),
        .O(\genblk1[5].g_val_reg0_carry_i_33_n_0 ));
  cost_calculator original_cost
       (.S({\genblk1[0].g_val_reg0_carry_i_32_n_0 ,\genblk1[0].g_val_reg0_carry_i_33_n_0 }),
        .cg_q(cg_q),
        .clk_global(clk_global),
        .cost_valid(cost_valid),
        .cx_q(cx_q),
        .cy_q(cy_q),
        .cz_q(cz_q),
        .ex_q(ex_q),
        .ey_q(ey_q),
        .ez_q(ez_q),
        .f_val({f[94:80],f[78:64],f[62:48],f[46:32],f[30:16],f[14:0]}),
        .g({g[83:57],g[55:43],g[41:29],g[27:15],g[13:1]}),
        .\genblk1[1].g_val_reg0_carry_i_9_0 ({\genblk1[1].g_val_reg0_carry_i_32_n_0 ,\genblk1[1].g_val_reg0_carry_i_33_n_0 }),
        .\genblk1[2].g_val_reg0_carry_i_9_0 ({\genblk1[2].g_val_reg0_carry_i_32_n_0 ,\genblk1[2].g_val_reg0_carry_i_33_n_0 }),
        .\genblk1[3].g_val_reg0_carry_i_9_0 ({\genblk1[3].g_val_reg0_carry_i_32_n_0 ,\genblk1[3].g_val_reg0_carry_i_33_n_0 }),
        .\genblk1[4].g_val_reg0_carry_i_9_0 ({\genblk1[4].g_val_reg0_carry_i_32_n_0 ,\genblk1[4].g_val_reg0_carry_i_33_n_0 }),
        .\genblk1[5].g_val_reg0_carry_i_9_0 ({\genblk1[5].g_val_reg0_carry_i_32_n_0 ,\genblk1[5].g_val_reg0_carry_i_33_n_0 }),
        .px_q(px_q),
        .py_q(py_q),
        .pz_q(pz_q),
        .reset_q(reset_q),
        .valid_q(valid_q));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[0] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[0]),
        .Q(px_q[0]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[10] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[10]),
        .Q(px_q[10]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[11] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[11]),
        .Q(px_q[11]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[12] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[12]),
        .Q(px_q[12]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[13] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[13]),
        .Q(px_q[13]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[14] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[14]),
        .Q(px_q[14]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[15] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[15]),
        .Q(px_q[15]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[16] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[16]),
        .Q(px_q[16]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[17] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[17]),
        .Q(px_q[17]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[18] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[18]),
        .Q(px_q[18]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[19] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[19]),
        .Q(px_q[19]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[1] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[1]),
        .Q(px_q[1]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[20] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[20]),
        .Q(px_q[20]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[21] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[21]),
        .Q(px_q[21]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[22] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[22]),
        .Q(px_q[22]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[23] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[23]),
        .Q(px_q[23]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[24] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[24]),
        .Q(px_q[24]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[25] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[25]),
        .Q(px_q[25]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[26] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[26]),
        .Q(px_q[26]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[27] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[27]),
        .Q(px_q[27]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[28] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[28]),
        .Q(px_q[28]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[29] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[29]),
        .Q(px_q[29]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[2] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[2]),
        .Q(px_q[2]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[30] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[30]),
        .Q(px_q[30]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[31] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[31]),
        .Q(px_q[31]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[32] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[32]),
        .Q(px_q[32]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[33] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[33]),
        .Q(px_q[33]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[34] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[34]),
        .Q(px_q[34]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[35] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[35]),
        .Q(px_q[35]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[36] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[36]),
        .Q(px_q[36]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[37] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[37]),
        .Q(px_q[37]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[38] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[38]),
        .Q(px_q[38]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[39] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[39]),
        .Q(px_q[39]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[3] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[3]),
        .Q(px_q[3]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[40] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[40]),
        .Q(px_q[40]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[41] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[41]),
        .Q(px_q[41]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[42] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[42]),
        .Q(px_q[42]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[43] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[43]),
        .Q(px_q[43]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[44] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[44]),
        .Q(px_q[44]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[45] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[45]),
        .Q(px_q[45]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[46] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[46]),
        .Q(px_q[46]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[47] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[47]),
        .Q(px_q[47]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[4] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[4]),
        .Q(px_q[4]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[5] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[5]),
        .Q(px_q[5]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[6] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[6]),
        .Q(px_q[6]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[7] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[7]),
        .Q(px_q[7]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[8] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[8]),
        .Q(px_q[8]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \px_q_reg[9] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_x[9]),
        .Q(px_q[9]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[0] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[0]),
        .Q(py_q[0]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[10] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[10]),
        .Q(py_q[10]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[11] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[11]),
        .Q(py_q[11]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[12] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[12]),
        .Q(py_q[12]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[13] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[13]),
        .Q(py_q[13]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[14] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[14]),
        .Q(py_q[14]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[15] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[15]),
        .Q(py_q[15]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[16] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[16]),
        .Q(py_q[16]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[17] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[17]),
        .Q(py_q[17]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[18] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[18]),
        .Q(py_q[18]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[19] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[19]),
        .Q(py_q[19]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[1] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[1]),
        .Q(py_q[1]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[20] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[20]),
        .Q(py_q[20]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[21] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[21]),
        .Q(py_q[21]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[22] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[22]),
        .Q(py_q[22]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[23] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[23]),
        .Q(py_q[23]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[24] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[24]),
        .Q(py_q[24]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[25] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[25]),
        .Q(py_q[25]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[26] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[26]),
        .Q(py_q[26]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[27] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[27]),
        .Q(py_q[27]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[28] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[28]),
        .Q(py_q[28]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[29] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[29]),
        .Q(py_q[29]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[2] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[2]),
        .Q(py_q[2]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[30] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[30]),
        .Q(py_q[30]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[31] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[31]),
        .Q(py_q[31]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[32] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[32]),
        .Q(py_q[32]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[33] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[33]),
        .Q(py_q[33]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[34] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[34]),
        .Q(py_q[34]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[35] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[35]),
        .Q(py_q[35]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[36] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[36]),
        .Q(py_q[36]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[37] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[37]),
        .Q(py_q[37]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[38] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[38]),
        .Q(py_q[38]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[39] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[39]),
        .Q(py_q[39]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[3] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[3]),
        .Q(py_q[3]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[40] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[40]),
        .Q(py_q[40]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[41] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[41]),
        .Q(py_q[41]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[42] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[42]),
        .Q(py_q[42]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[43] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[43]),
        .Q(py_q[43]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[44] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[44]),
        .Q(py_q[44]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[45] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[45]),
        .Q(py_q[45]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[46] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[46]),
        .Q(py_q[46]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[47] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[47]),
        .Q(py_q[47]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[4] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[4]),
        .Q(py_q[4]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[5] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[5]),
        .Q(py_q[5]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[6] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[6]),
        .Q(py_q[6]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[7] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[7]),
        .Q(py_q[7]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[8] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[8]),
        .Q(py_q[8]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \py_q_reg[9] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_y[9]),
        .Q(py_q[9]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \pz_q_reg[0] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_z[0]),
        .Q(pz_q[0]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \pz_q_reg[10] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_z[10]),
        .Q(pz_q[10]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \pz_q_reg[11] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_z[11]),
        .Q(pz_q[11]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \pz_q_reg[12] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_z[12]),
        .Q(pz_q[12]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \pz_q_reg[13] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_z[13]),
        .Q(pz_q[13]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \pz_q_reg[14] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_z[14]),
        .Q(pz_q[14]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \pz_q_reg[15] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_z[15]),
        .Q(pz_q[15]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \pz_q_reg[16] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_z[16]),
        .Q(pz_q[16]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \pz_q_reg[17] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_z[17]),
        .Q(pz_q[17]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \pz_q_reg[1] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_z[1]),
        .Q(pz_q[1]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \pz_q_reg[2] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_z[2]),
        .Q(pz_q[2]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \pz_q_reg[3] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_z[3]),
        .Q(pz_q[3]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \pz_q_reg[4] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_z[4]),
        .Q(pz_q[4]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \pz_q_reg[5] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_z[5]),
        .Q(pz_q[5]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \pz_q_reg[6] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_z[6]),
        .Q(pz_q[6]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \pz_q_reg[7] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_z[7]),
        .Q(pz_q[7]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \pz_q_reg[8] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_z[8]),
        .Q(pz_q[8]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \pz_q_reg[9] 
       (.C(clk_global),
        .CE(1'b1),
        .D(per_z[9]),
        .Q(pz_q[9]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    reset_q_reg
       (.C(clk_global),
        .CE(1'b1),
        .D(reset),
        .Q(reset_q),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    valid_out_reg
       (.C(clk_global),
        .CE(1'b1),
        .D(cost_valid),
        .Q(valid_out),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    valid_q_reg
       (.C(clk_global),
        .CE(1'b1),
        .D(valid),
        .Q(valid_q),
        .R(1'b0));
endmodule
`ifndef GLBL
`define GLBL
`timescale  1 ps / 1 ps

module glbl ();

    parameter ROC_WIDTH = 100000;
    parameter TOC_WIDTH = 0;
    parameter GRES_WIDTH = 10000;
    parameter GRES_START = 10000;

//--------   STARTUP Globals --------------
    wire GSR;
    wire GTS;
    wire GWE;
    wire PRLD;
    wire GRESTORE;
    tri1 p_up_tmp;
    tri (weak1, strong0) PLL_LOCKG = p_up_tmp;

    wire PROGB_GLBL;
    wire CCLKO_GLBL;
    wire FCSBO_GLBL;
    wire [3:0] DO_GLBL;
    wire [3:0] DI_GLBL;
   
    reg GSR_int;
    reg GTS_int;
    reg PRLD_int;
    reg GRESTORE_int;

//--------   JTAG Globals --------------
    wire JTAG_TDO_GLBL;
    wire JTAG_TCK_GLBL;
    wire JTAG_TDI_GLBL;
    wire JTAG_TMS_GLBL;
    wire JTAG_TRST_GLBL;

    reg JTAG_CAPTURE_GLBL;
    reg JTAG_RESET_GLBL;
    reg JTAG_SHIFT_GLBL;
    reg JTAG_UPDATE_GLBL;
    reg JTAG_RUNTEST_GLBL;

    reg JTAG_SEL1_GLBL = 0;
    reg JTAG_SEL2_GLBL = 0 ;
    reg JTAG_SEL3_GLBL = 0;
    reg JTAG_SEL4_GLBL = 0;

    reg JTAG_USER_TDO1_GLBL = 1'bz;
    reg JTAG_USER_TDO2_GLBL = 1'bz;
    reg JTAG_USER_TDO3_GLBL = 1'bz;
    reg JTAG_USER_TDO4_GLBL = 1'bz;

    assign (strong1, weak0) GSR = GSR_int;
    assign (strong1, weak0) GTS = GTS_int;
    assign (weak1, weak0) PRLD = PRLD_int;
    assign (strong1, weak0) GRESTORE = GRESTORE_int;

    initial begin
	GSR_int = 1'b1;
	PRLD_int = 1'b1;
	#(ROC_WIDTH)
	GSR_int = 1'b0;
	PRLD_int = 1'b0;
    end

    initial begin
	GTS_int = 1'b1;
	#(TOC_WIDTH)
	GTS_int = 1'b0;
    end

    initial begin 
	GRESTORE_int = 1'b0;
	#(GRES_START);
	GRESTORE_int = 1'b1;
	#(GRES_WIDTH);
	GRESTORE_int = 1'b0;
    end

endmodule
`endif
