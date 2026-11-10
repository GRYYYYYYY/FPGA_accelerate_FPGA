`timescale 1ns/1ps
module children_build_engine(
    input wire clk,rst,
    input wire build_valid,output wire build_ready,
    input wire [31:0] build_cookie,build_parent,build_count,build_prune,
    input wire [1:0] build_query,input wire [3:0] build_price,
    output wire result_valid,input wire result_ready,
    output wire [3:0] result_status,output wire [31:0] result_detail,result_cookie,result_generation,result_emitted,
    output wire fault,busy,
    output wire svc_valid,input wire svc_ready,
    output wire [31:0] svc_generation,svc_parent,svc_position,svc_phase,svc_node,svc_emitted,svc_count,svc_prune,
    output wire [1:0] svc_query,output wire [3:0] svc_price,
    input wire svc_reply_valid,output wire svc_reply_ready,
    input wire [31:0] svc_reply_generation,svc_reply_parent,svc_reply_position,svc_reply_phase,svc_reply_node,
    input wire [1:0] svc_reply_query,input wire [3:0] svc_reply_price,
    input wire [31:0] svc_status,svc_value,svc_aux,input wire service_fault
);
    wire call_valid,call_ready,call_reply_valid,call_reply_ready,call_fault;
    wire [415:0] call_command,hls_command;
    wire [351:0] call_reply_data,hls_reply;
    wire [10:0] hls_valid;
    wire ap_start,ap_ready,ap_done,ap_idle;
    children_build_controller controller(.*);
    children_hls_call calls(.abort(service_fault),.reply_valid(call_reply_valid),.reply_ready(call_reply_ready),.reply_data(call_reply_data),.fault(call_fault),.*);
    children_step hls(.ap_clk(clk),.ap_rst(rst),.ap_start(ap_start),.ap_ready(ap_ready),.ap_done(ap_done),.ap_idle(ap_idle),
        .op(hls_command[31:0]),
        .parent(hls_command[63:32]),
        .count(hls_command[95:64]),
        .prune(hls_command[127:96]),
        .query(hls_command[159:128]),
        .price(hls_command[191:160]),
        .generation(hls_command[223:192]),
        .position(hls_command[255:224]),
        .phase(hls_command[287:256]),
        .node(hls_command[319:288]),
        .value_r(hls_command[351:320]),
        .aux(hls_command[383:352]),
        .service_status(hls_command[415:384]),
        .status(hls_reply[31:0]),
        .result_generation(hls_reply[63:32]),
        .request(hls_reply[95:64]),
        .result_position(hls_reply[127:96]),
        .result_node(hls_reply[159:128]),
        .result_parent(hls_reply[191:160]),
        .result_query(hls_reply[223:192]),
        .result_price(hls_reply[255:224]),
        .emitted(hls_reply[287:256]),
        .active_r(hls_reply[319:288]),
        .fault(hls_reply[351:320]),
        .status_ap_vld(hls_valid[0]),
        .result_generation_ap_vld(hls_valid[1]),
        .request_ap_vld(hls_valid[2]),
        .result_position_ap_vld(hls_valid[3]),
        .result_node_ap_vld(hls_valid[4]),
        .result_parent_ap_vld(hls_valid[5]),
        .result_query_ap_vld(hls_valid[6]),
        .result_price_ap_vld(hls_valid[7]),
        .emitted_ap_vld(hls_valid[8]),
        .active_r_ap_vld(hls_valid[9]),
        .fault_ap_vld(hls_valid[10]));
endmodule
