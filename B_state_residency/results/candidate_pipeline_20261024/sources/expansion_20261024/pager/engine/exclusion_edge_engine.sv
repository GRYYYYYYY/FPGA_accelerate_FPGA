`timescale 1ns/1ps
// Actual HLS exclusion RTL + serialized controller + audited native label bridge.
module exclusion_edge_engine(
    input wire clk,rst,
    input wire edge_valid,output wire edge_ready,
    input wire [31:0] edge_cookie,edge_parent,edge_child,edge_flags,edge_created,edge_has_laguna,
    input wire [1:0] edge_query,input wire [3:0] edge_price,
    output wire result_valid,input wire result_ready,
    output wire [3:0] result_status,output wire [31:0] result_detail,result_cookie,result_generation,
    output wire result_excluded,output wire fault,
    output wire resolve_valid, input wire resolve_ready,
    output wire [31:0] resolve_token, resolve_generation, resolve_phase,
    output wire [20:0] resolve_page,
    output wire [1:0] resolve_query, output wire [3:0] resolve_price,
    input wire map_valid, output wire map_ready,
    input wire [31:0] map_token, map_generation, map_phase,
    input wire [20:0] map_page, input wire [1:0] map_query,
    input wire [3:0] map_price, map_status,
    input wire [4:0] map_slot, input wire [15:0] map_binding_generation,
    output wire native_cmd_valid, input wire native_cmd_ready,
    output wire [3:0] native_cmd_op, native_cmd_price,
    output wire [4:0] native_cmd_slot, output wire [1:0] native_cmd_query,
    output wire [20:0] native_cmd_page,
    output wire [15:0] native_cmd_generation,
    output wire [2:0] native_cmd_offset, native_cmd_field,
    output wire [31:0] native_cmd_value,
    input wire native_rsp_valid, output wire native_rsp_ready,
    input wire [3:0] native_rsp_status,
    input wire [159:0] native_rsp_payload,
    input wire native_rsp_present, native_fault
);
    wire call_valid,call_ready,call_reply_valid,call_reply_ready,call_fault;
    wire [287:0] call_command,hls_command;
    wire [159:0] call_reply_data,hls_reply;
    wire [4:0] hls_valid;
    wire ap_start,ap_ready,ap_done,ap_idle;
    wire label_valid,label_ready,label_reply_valid,label_reply_ready,label_fault,label_present;
    wire [31:0] label_node,label_generation,label_phase,label_reply_generation,label_reply_phase,label_value;
    wire [1:0] label_query;wire [3:0] label_price,label_status,label_service_status;
    exclusion_edge_controller controller(.*);
    exclusion_hls_call calls(.abort(label_fault),.reply_valid(call_reply_valid),
        .reply_ready(call_reply_ready),.reply_data(call_reply_data),.fault(call_fault),.*);
    exclusion_step hls(
        .ap_clk(clk),.ap_rst(rst),.ap_start(ap_start),.ap_ready(ap_ready),.ap_done(ap_done),.ap_idle(ap_idle),
        .op(hls_command[31:0]),.parent(hls_command[63:32]),.child(hls_command[95:64]),
        .flags(hls_command[127:96]),.created(hls_command[159:128]),.has_laguna(hls_command[191:160]),
        .generation(hls_command[223:192]),.phase(hls_command[255:224]),.value_r(hls_command[287:256]),
        .status(hls_reply[31:0]),.result_generation(hls_reply[63:32]),.request(hls_reply[95:64]),
        .node(hls_reply[127:96]),.excluded(hls_reply[159:128]),
        .status_ap_vld(hls_valid[0]),.result_generation_ap_vld(hls_valid[1]),.request_ap_vld(hls_valid[2]),
        .node_ap_vld(hls_valid[3]),.excluded_ap_vld(hls_valid[4]));
    exclusion_label_adapter labels(.req_valid(label_valid),.req_ready(label_ready),
        .req_node(label_node),.req_generation(label_generation),.req_phase(label_phase),
        .req_query(label_query),.req_price(label_price),.rsp_valid(label_reply_valid),.rsp_ready(label_reply_ready),
        .rsp_status(label_status),.rsp_service_status(label_service_status),.rsp_generation(label_reply_generation),
        .rsp_phase(label_reply_phase),.rsp_value(label_value),.rsp_present(label_present),.fault(label_fault),.*);
endmodule
