`timescale 1ns/1ps
module cost_service #(parameter integer MAX_CALL_CYCLES=1024)(
 input wire clk,rst,abort,
 input wire active,input wire [1:0] active_query,input wire [3:0] active_price,
 input wire req_valid,output wire req_ready,input wire [735:0] req_words,
 input wire [31:0] req_cookie,input wire [1:0] req_query,input wire [3:0] req_price,
 output wire rsp_valid,input wire rsp_ready,output wire [159:0] rsp_words,
 output wire [31:0] rsp_cookie,output wire [1:0] rsp_query,
 output wire [3:0] rsp_price,output wire [1:0] rsp_status,
 output wire busy,fault
);
 wire ap_start,ap_idle,ap_ready,ap_done;
 wire [4:0] ia0,ia1;wire ic0,ic1;wire [31:0] iq0,iq1;
 wire [2:0] oa0,oa1;wire oc0,oc1,ow0,ow1;wire [31:0] od0,od1;
 cost_memory_call #(.MAX_CALL_CYCLES(MAX_CALL_CYCLES)) bridge(.*);
 cost_step arithmetic(.ap_clk(clk),.ap_rst(rst),.ap_start(ap_start),.ap_idle(ap_idle),
  .ap_ready(ap_ready),.ap_done(ap_done),
  .input_r_address0(ia0),.input_r_ce0(ic0),.input_r_q0(iq0),
  .input_r_address1(ia1),.input_r_ce1(ic1),.input_r_q1(iq1),
  .output_r_address0(oa0),.output_r_ce0(oc0),.output_r_we0(ow0),.output_r_d0(od0),
  .output_r_address1(oa1),.output_r_ce1(oc1),.output_r_we1(ow1),.output_r_d1(od1));
endmodule
