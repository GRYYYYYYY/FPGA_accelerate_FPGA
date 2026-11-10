`timescale 1ns/1ps
module access_service #(parameter integer TOKEN_BITS=32,MAX_CYCLES=8388608,MAX_STEPS=32,MAX_CALL_CYCLES=64)(
 input wire  clk,
 input wire  rst,
 input wire  abort,
 input wire  enable,
 input wire  active,
 input wire [1:0] active_query,
 input wire [3:0] active_price,
 input wire  req_valid,
 output wire  req_ready,
 input wire [447:0] req_config,
 input wire [31:0] req_cookie,
 input wire [31:0] req_parent,
 input wire [31:0] req_child,
 input wire [31:0] req_sink,
 input wire [31:0] req_net,
 input wire [1:0] req_query,
 input wire [3:0] req_price,
 output wire  rsp_valid,
 input wire  rsp_ready,
 output wire [3:0] rsp_status,
 output wire [31:0] rsp_cookie,
 output wire [31:0] rsp_parent,
 output wire [31:0] rsp_child,
 output wire [31:0] rsp_sink,
 output wire [31:0] rsp_net,
 output wire [31:0] rsp_bits,
 output wire [31:0] rsp_action,
 output wire [31:0] rsp_steps,
 output wire [31:0] rsp_services,
 output wire [1:0] rsp_query,
 output wire [3:0] rsp_price,
 output wire  busy,
 output wire  fault,
 output wire  svc_valid,
 input wire  svc_ready,
 output wire [3:0] svc_kind,
 output wire [4:0] svc_phase,
 output wire [31:0] svc_node,
 output wire [31:0] svc_net,
 output wire [31:0] svc_cookie,
 output wire [1:0] svc_query,
 output wire [3:0] svc_price,
 input wire  svc_rsp_valid,
 output wire  svc_rsp_ready,
 input wire [3:0] svc_rsp_status,
 input wire [3:0] svc_rsp_kind,
 input wire [4:0] svc_rsp_phase,
 input wire [31:0] svc_rsp_node,
 input wire [31:0] svc_rsp_net,
 input wire [31:0] svc_rsp_cookie,
 input wire [31:0] svc_rsp_value,
 input wire [1:0] svc_rsp_query,
 input wire [3:0] svc_rsp_price,
 input wire  svc_fault
);
 wire  k_req_valid;
 wire  k_req_ready;
 wire [639:0] k_req_words;
 wire [31:0] k_req_cookie;
 wire [1:0] k_req_query;
 wire [3:0] k_req_price;
 wire  k_rsp_valid;
 wire  k_rsp_ready;
 wire [191:0] k_rsp_words;
 wire [1:0] k_rsp_status;
 wire [31:0] k_rsp_cookie;
 wire [1:0] k_rsp_query;
 wire [3:0] k_rsp_price;
 wire  k_fault;
 access_controller #(.TOKEN_BITS(TOKEN_BITS),.MAX_CYCLES(MAX_CYCLES),.MAX_STEPS(MAX_STEPS)) controller(.*);
 access_call #(.MAX_CALL_CYCLES(MAX_CALL_CYCLES)) step(
.clk(clk),
.rst(rst),
.abort(abort),
.active(active),
.active_query(active_query),
.active_price(active_price),
.req_valid(k_req_valid),
.req_ready(k_req_ready),
.req_words(k_req_words),
.req_cookie(k_req_cookie),
.req_query(k_req_query),
.req_price(k_req_price),
.rsp_valid(k_rsp_valid),
.rsp_ready(k_rsp_ready),
.rsp_words(k_rsp_words),
.rsp_cookie(k_rsp_cookie),
.rsp_query(k_rsp_query),
.rsp_price(k_rsp_price),
.rsp_status(k_rsp_status),
.busy(),
.fault(k_fault)
);
endmodule
