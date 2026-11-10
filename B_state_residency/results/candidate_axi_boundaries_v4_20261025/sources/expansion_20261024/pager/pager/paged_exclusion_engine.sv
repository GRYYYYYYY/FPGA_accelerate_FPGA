`timescale 1ns/1ps
module paged_exclusion_engine #(
    parameter integer SLOTS=32,TX_BITS=16,GEN_BITS=16,
    parameter integer FRAMES=163840,INDEX_BITS=18,HASH_BITS=18,PROBE_LIMIT=64,EPOCH_BITS=16
)(
    input wire clk,rst,
    input wire ctrl_valid,output wire ctrl_ready,input wire [1:0] ctrl_op,ctrl_query,
    input wire [3:0] ctrl_price,output wire ctrl_rsp_valid,input wire ctrl_rsp_ready,output wire [3:0] ctrl_status,
    input wire io_valid,output wire io_ready,input wire io_write,
    input wire [31:0] io_node,io_value,input wire [2:0] io_field,
    output wire io_rsp_valid,input wire io_rsp_ready,output wire [3:0] io_status,
    output wire [159:0] io_payload,output wire io_present,
    input wire edge_valid,output wire edge_ready,
    input wire [31:0] edge_cookie,edge_parent,edge_child,edge_flags,edge_created,edge_has_laguna,
    output wire result_valid,input wire result_ready,
    output wire [3:0] result_status,output wire [31:0] result_detail,result_cookie,result_generation,
    output wire result_excluded,output wire fault,active,
    output wire [1:0] active_query,output wire [3:0] active_price,
    input wire dispatch_enable,execute_enable,fence_service_enable,ack_receive_enable,
    output wire [31:0] page_leases,memory_leases,output wire [INDEX_BITS:0] allocated,
    output wire [1:0] fence_tag,output wire draining,
    output wire [31:0] m_awaddr,output wire [7:0] m_awlen,output wire [2:0] m_awsize,
    output wire [1:0] m_awburst,output wire [3:0] m_awid,output wire m_awvalid,input wire m_awready,
    output wire [511:0] m_wdata,output wire [63:0] m_wstrb,output wire m_wlast,output wire m_wvalid,input wire m_wready,
    input wire [3:0] m_bid,input wire [1:0] m_bresp,input wire m_bvalid,output wire m_bready,
    output wire [31:0] m_araddr,output wire [7:0] m_arlen,output wire [2:0] m_arsize,
    output wire [1:0] m_arburst,output wire [3:0] m_arid,output wire m_arvalid,input wire m_arready,
    input wire [511:0] m_rdata,input wire [3:0] m_rid,input wire [1:0] m_rresp,input wire m_rlast,input wire m_rvalid,output wire m_rready
);
    wire manager_idle,pager_fault,engine_fault,backend_fault,engine_ready;
    wire client_quiescent=engine_ready;
    wire permit_edge=manager_idle&&active&&!ctrl_valid&&!io_valid&&!fault;
    assign edge_ready=engine_ready&&permit_edge;
    assign fault=pager_fault||engine_fault;
    wire resolve_valid,resolve_ready,map_valid,map_ready;
    wire [31:0] resolve_token,resolve_generation,resolve_phase,map_token,map_generation,map_phase;
    wire [20:0] resolve_page,map_page;wire [1:0] resolve_query,map_query;
    wire [3:0] resolve_price,map_price,map_status;
    wire [4:0] map_slot;wire [15:0] map_binding_generation;
    wire client_cmd_valid,client_cmd_ready,client_rsp_valid,client_rsp_ready,client_rsp_present;
    wire [3:0] client_cmd_op,client_cmd_price,client_rsp_status;
    wire [4:0] client_cmd_slot;wire [1:0] client_cmd_query;wire [20:0] client_cmd_page;
    wire [15:0] client_cmd_generation;wire [2:0] client_cmd_offset,client_cmd_field;
    wire [31:0] client_cmd_value;wire [159:0] client_rsp_payload;
    wire native_cmd_valid,native_cmd_ready,native_rsp_valid,native_rsp_ready,native_rsp_present,native_rsp_dirty;
    wire [3:0] native_cmd_op,native_cmd_price,native_rsp_status;
    wire [4:0] native_cmd_slot;wire [1:0] native_cmd_query;wire [20:0] native_cmd_page;
    wire [15:0] native_cmd_generation;wire [2:0] native_cmd_offset,native_cmd_field;
    wire [31:0] native_cmd_value;wire [159:0] native_rsp_payload;wire [TX_BITS-1:0] native_rsp_tx;
    resident_page_manager #(.SLOTS(SLOTS),.TX_BITS(TX_BITS),.GEN_BITS(GEN_BITS)) pager(
        .idle(manager_idle),.fault(pager_fault),.native_fault(backend_fault),.io_query(active_query),.io_price(active_price),.*);
    exclusion_edge_engine engine(
        .edge_valid(edge_valid&&permit_edge),.edge_ready(engine_ready),.edge_query(active_query),.edge_price(active_price),.fault(engine_fault),
        .native_cmd_valid(client_cmd_valid),
        .native_cmd_ready(client_cmd_ready),
        .native_cmd_op(client_cmd_op),
        .native_cmd_price(client_cmd_price),
        .native_cmd_slot(client_cmd_slot),
        .native_cmd_query(client_cmd_query),
        .native_cmd_page(client_cmd_page),
        .native_cmd_generation(client_cmd_generation),
        .native_cmd_offset(client_cmd_offset),
        .native_cmd_field(client_cmd_field),
        .native_cmd_value(client_cmd_value),
        .native_rsp_valid(client_rsp_valid),
        .native_rsp_ready(client_rsp_ready),
        .native_rsp_status(client_rsp_status),
        .native_rsp_payload(client_rsp_payload),
        .native_rsp_present(client_rsp_present),
        .native_fault(pager_fault),.*);
    memory_scratch_endpoint_small_staticcodec #(.TX_BITS(TX_BITS),.GENERATION_BITS(16),.TAG_BITS(2),
        .FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS),.PROBE_LIMIT(PROBE_LIMIT),.EPOCH_BITS(EPOCH_BITS)) endpoint(
        .cmd_valid(native_cmd_valid),
        .cmd_ready(native_cmd_ready),
        .cmd_op(native_cmd_op),
        .cmd_price(native_cmd_price),
        .cmd_slot(native_cmd_slot),
        .cmd_query(native_cmd_query),
        .cmd_page(native_cmd_page),
        .cmd_generation(native_cmd_generation),
        .cmd_offset(native_cmd_offset),
        .cmd_field(native_cmd_field),
        .cmd_value(native_cmd_value),
        .rsp_valid(native_rsp_valid),
        .rsp_ready(native_rsp_ready),
        .rsp_status(native_rsp_status),
        .rsp_payload(native_rsp_payload),
        .rsp_present(native_rsp_present),
        .rsp_dirty(native_rsp_dirty),
        .rsp_tx(native_rsp_tx),
        .fault(backend_fault),.*);
endmodule
