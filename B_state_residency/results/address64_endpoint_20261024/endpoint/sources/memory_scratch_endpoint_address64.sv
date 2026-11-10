`timescale 1ns/1ps
// Closed serial command adapter: page core + queued fence + record AXI memory.
// Only public QUERY/BIND/READ/WRITE/RELEASE/WB/RF/BEGIN/FINISH are accepted.
module memory_scratch_endpoint_address64 #(
    parameter integer TX_BITS=16,GENERATION_BITS=16,TAG_BITS=2,
    parameter integer FRAMES=163840,INDEX_BITS=18,HASH_BITS=18,PROBE_LIMIT=64,EPOCH_BITS=8
)(
    input wire clk,rst,input wire cmd_valid,output wire cmd_ready,
    input wire [3:0] cmd_op,input wire [4:0] cmd_slot,input wire [1:0] cmd_query,
    input wire [20:0] cmd_page,input wire [3:0] cmd_price,
    input wire [GENERATION_BITS-1:0] cmd_generation,
    input wire [2:0] cmd_offset,input wire [2:0] cmd_field,input wire [31:0] cmd_value,
    output wire rsp_valid,input wire rsp_ready,output wire [3:0] rsp_status,
    output wire [159:0] rsp_payload,output wire rsp_present,rsp_dirty,
    output wire [TX_BITS-1:0] rsp_tx,
    input wire dispatch_enable,execute_enable,fence_service_enable,ack_receive_enable,
    output wire fault,draining,output wire [31:0] page_leases,memory_leases,
    output wire [INDEX_BITS:0] allocated,output wire [TAG_BITS-1:0] fence_tag,
    output wire [63:0] m_awaddr,output wire [7:0] m_awlen,output wire [2:0] m_awsize,
    output wire [1:0] m_awburst,output wire [3:0] m_awid,output wire m_awvalid,input wire m_awready,
    output wire [511:0] m_wdata,output wire [63:0] m_wstrb,output wire m_wlast,output wire m_wvalid,input wire m_wready,
    input wire [3:0] m_bid,input wire [1:0] m_bresp,input wire m_bvalid,output wire m_bready,
    output wire [63:0] m_araddr,output wire [7:0] m_arlen,output wire [2:0] m_arsize,
    output wire [1:0] m_arburst,output wire [3:0] m_arid,output wire m_arvalid,input wire m_arready,
    input wire [511:0] m_rdata,input wire [3:0] m_rid,input wire [1:0] m_rresp,input wire m_rlast,input wire m_rvalid,output wire m_rready,
    input wire cfg_base_valid,output wire cfg_base_ready,input wire [63:0] cfg_base_address,
    output wire cfg_rsp_valid,input wire cfg_rsp_ready,output wire [1:0] cfg_rsp_status,
    output wire configured
);
    wire [63:0] backing_base;
    wire [31:0] relative_awaddr,relative_araddr;
    wire core_cmd_ready,core_cmd_valid=cmd_valid && configured;
    assign cmd_ready=core_cmd_ready && configured;
    assign m_awaddr=backing_base+{32'b0,relative_awaddr};
    assign m_araddr=backing_base+{32'b0,relative_araddr};
    backing_base_config #(.FRAMES(FRAMES)) base_config(
        .clk(clk),.rst(rst),.cfg_base_valid(cfg_base_valid),.cfg_base_ready(cfg_base_ready),
        .cfg_base_address(cfg_base_address),.cfg_rsp_valid(cfg_rsp_valid),.cfg_rsp_ready(cfg_rsp_ready),
        .cfg_rsp_status(cfg_rsp_status),.configured(configured),.backing_base(backing_base));
    memory_scratch_endpoint_small_staticcodec #(
        .TX_BITS(TX_BITS),.GENERATION_BITS(GENERATION_BITS),.TAG_BITS(TAG_BITS),
        .FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS),
        .PROBE_LIMIT(PROBE_LIMIT),.EPOCH_BITS(EPOCH_BITS)) core(
        .cmd_valid(core_cmd_valid),.cmd_ready(core_cmd_ready),
        .m_awaddr(relative_awaddr),.m_araddr(relative_araddr),.*);
endmodule
