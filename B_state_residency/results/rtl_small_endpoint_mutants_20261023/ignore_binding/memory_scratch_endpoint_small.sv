`timescale 1ns/1ps
// Closed serial command adapter: page core + queued fence + record AXI memory.
// Only public QUERY/BIND/READ/WRITE/RELEASE/WB/RF/BEGIN/FINISH are accepted.
module memory_scratch_endpoint_small #(
    parameter integer TX_BITS=16,GENERATION_BITS=16,TAG_BITS=2,
    parameter integer FRAMES=163840,INDEX_BITS=18,HASH_BITS=18,PROBE_LIMIT=64,EPOCH_BITS=8
)(
    input wire clk,rst,input wire cmd_valid,output wire cmd_ready,
    input wire [3:0] cmd_op,input wire [4:0] cmd_slot,input wire [1:0] cmd_query,
    input wire [20:0] cmd_page,input wire [3:0] cmd_price,
    input wire [GENERATION_BITS-1:0] cmd_generation,
    input wire [2:0] cmd_offset,input wire [2:0] cmd_field,input wire [31:0] cmd_value,
    output reg rsp_valid,input wire rsp_ready,output reg [3:0] rsp_status,
    output reg [159:0] rsp_payload,output reg rsp_present,rsp_dirty,
    output reg [TX_BITS-1:0] rsp_tx,
    input wire dispatch_enable,execute_enable,fence_service_enable,ack_receive_enable,
    output wire fault,draining,output wire [31:0] page_leases,memory_leases,
    output wire [INDEX_BITS:0] allocated,output wire [TAG_BITS-1:0] fence_tag,
    output wire [31:0] m_awaddr,output wire [7:0] m_awlen,output wire [2:0] m_awsize,
    output wire [1:0] m_awburst,output wire [3:0] m_awid,output wire m_awvalid,input wire m_awready,
    output wire [511:0] m_wdata,output wire [63:0] m_wstrb,output wire m_wlast,output wire m_wvalid,input wire m_wready,
    input wire [3:0] m_bid,input wire [1:0] m_bresp,input wire m_bvalid,output wire m_bready,
    output wire [31:0] m_araddr,output wire [7:0] m_arlen,output wire [2:0] m_arsize,
    output wire [1:0] m_arburst,output wire [3:0] m_arid,output wire m_arvalid,input wire m_arready,
    input wire [511:0] m_rdata,input wire [3:0] m_rid,input wire [1:0] m_rresp,input wire m_rlast,input wire m_rvalid,output wire m_rready
);
    localparam [4:0] IDLE=0,Q_HOST_SEND=1,Q_HOST_WAIT=2,M_LOOK_SEND=3,M_LOOK_WAIT=4,
        Q_START_SEND=5,Q_START_WAIT=6,M_TRANSFER_SEND=7,WB_EXPORT_SEND=8,WB_EXPORT_WAIT=9,
        WB_PUT=10,RF_GET=11,RF_BEAT_SEND=12,RF_BEAT_WAIT=13,M_STATUS=14,
        Q_COMPLETE_SEND=15,Q_COMPLETE_WAIT=16,M_RETIRE_SEND=17,M_RETIRE_WAIT=18,
        M_RECYCLE_SEND=19,M_RECYCLE_WAIT=20,
        CP_BEGIN_SEND=21,CP_BEGIN_WAIT=22,CP_DRAIN=23,CP_FINISH_SEND=24,CP_FINISH_WAIT=25,
        CP_MEMORY_SEND=26,CP_MEMORY_WAIT=27,CP_QUERY_SEND=28,CP_QUERY_WAIT=29;
    reg [4:0] state;
    reg query_seen,query_exclusive;
    reg [1:0] retained_query;
    reg [3:0] retained_price;reg [31:0] bound_mask;
    reg [INDEX_BITS:0] retained_allocated;
    wire q_fence_active,q_peer_sealed,q_acknowledged;
    wire [2:0] q_requests,q_work,q_responses;
    wire [1:0] q_fence_requests,q_fence_acks;
    wire cp_drained=q_fence_active && q_peer_sealed && q_acknowledged && page_leases==0
        && q_requests==0 && q_work==0 && q_responses==0 && q_fence_requests==0 && q_fence_acks==0;
    reg [3:0] op,price;
    reg [4:0] slot;reg [1:0] query_id;
    reg [20:0] page;
    reg [GENERATION_BITS-1:0] generation;
    reg [TX_BITS-1:0] transaction;
    reg [2:0] offset,position;
    reg [2:0] field;
    reg [31:0] value;
    reg [159:0] record;
    reg present,local_fault,fence_open;
    reg [INDEX_BITS-1:0] frame;
    wire kind=op==6;
    wire [26:0] owner={price,query_id,page};
    wire [71:0] cookie={7'b0,kind,{{(16-TX_BITS){1'b0}},transaction},{{(16-GENERATION_BITS){1'b0}},generation},owner,slot};
    wire q_ready,q_valid,q_present,q_dirty,q_draining;
    wire [2:0] q_status;wire [159:0] q_payload;wire [TX_BITS-1:0] q_tx;
    wire q_send=state==Q_HOST_SEND || state==Q_START_SEND || state==WB_EXPORT_SEND || state==RF_BEAT_SEND || state==Q_COMPLETE_SEND || state==CP_BEGIN_SEND || state==CP_FINISH_SEND || state==CP_QUERY_SEND;
    wire q_receive=state==Q_HOST_WAIT || state==Q_START_WAIT || state==WB_EXPORT_WAIT || state==RF_BEAT_WAIT || state==Q_COMPLETE_WAIT || state==CP_BEGIN_WAIT || state==CP_FINISH_WAIT || state==CP_QUERY_WAIT;
    wire [3:0] q_op=state==CP_BEGIN_SEND?4'd10:(state==CP_FINISH_SEND?4'd11:(state==CP_QUERY_SEND?4'd0:(state==WB_EXPORT_SEND?4'd9:(state==RF_BEAT_SEND?4'd7:(state==Q_COMPLETE_SEND?4'd8:op)))));
    wire [2:0] q_offset=(state==WB_EXPORT_SEND || state==RF_BEAT_SEND)?position:offset;
    queued_scratch_endpoint_small #(.TX_BITS(TX_BITS),.GENERATION_BITS(GENERATION_BITS),.TAG_BITS(TAG_BITS)) pages(
        .clk(clk),.rst(rst),.cmd_valid(q_send),.cmd_ready(q_ready),.cmd_op(q_op),
        .cmd_slot(slot),.cmd_query(query_id),.cmd_page(page),.cmd_price(price),.cmd_generation(generation),
        .cmd_tx(transaction),.cmd_kind(kind),.cmd_present(present),.cmd_offset(q_offset),.cmd_field(field),.cmd_value(value),.cmd_payload(record),
        .rsp_valid(q_valid),.rsp_ready(q_receive),.rsp_status(q_status),.rsp_payload(q_payload),.rsp_present(q_present),.rsp_dirty(q_dirty),.rsp_tx(q_tx),
        .dispatch_enable(dispatch_enable),.execute_enable(execute_enable),.fence_service_enable(fence_service_enable),.ack_receive_enable(ack_receive_enable),
        .draining(q_draining),.leases(page_leases),.fence_tag(fence_tag),.fence_active(q_fence_active),.peer_sealed(q_peer_sealed),.acknowledged(q_acknowledged),
        .request_count(q_requests),.work_count(q_work),.response_count(q_responses),.fence_request_count(q_fence_requests),.fence_ack_count(q_fence_acks));
    wire m_ready,m_valid,m_published,memory_fault;
    wire [2:0] m_status;wire [INDEX_BITS-1:0] m_frame;wire [31:0] m_address;wire [71:0] m_cookie;
    wire m_send=state==M_LOOK_SEND || state==M_TRANSFER_SEND || state==M_RETIRE_SEND || state==M_RECYCLE_SEND || state==CP_MEMORY_SEND;
    wire m_receive=state==M_LOOK_WAIT || state==RF_GET || state==M_STATUS || state==M_RETIRE_WAIT || state==M_RECYCLE_WAIT || state==CP_MEMORY_WAIT;
    wire [2:0] m_op=state==CP_MEMORY_SEND?3'd5:(state==M_LOOK_SEND?(kind?3'd4:3'd0):(state==M_RETIRE_SEND?3'd2:(state==M_RECYCLE_SEND?3'd3:3'd1)));
    wire [71:0] m_command_cookie=(state==M_LOOK_SEND || state==M_RECYCLE_SEND || state==CP_MEMORY_SEND)?72'b0:cookie;
    wire [71:0] m_expected_cookie=(state==M_LOOK_WAIT || state==M_RECYCLE_WAIT || state==CP_MEMORY_WAIT)?72'b0:cookie;
    wire record_in_ready,record_out_valid,record_out_present;
    wire [2:0] record_out_offset;wire [159:0] record_out_payload;
    record_backing_service_small #(.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS),.PROBE_LIMIT(PROBE_LIMIT),.EPOCH_BITS(EPOCH_BITS)) memory(
        .clk(clk),.rst(rst),.cmd_valid(m_send),.cmd_ready(m_ready),.cmd_op(m_op),.cmd_owner(owner),.cmd_frame(frame),.cmd_cookie(m_command_cookie),
        .fence_retired(state==M_RECYCLE_SEND || state==CP_MEMORY_SEND),.rsp_valid(m_valid),.rsp_ready(m_receive),.rsp_status(m_status),
        .rsp_frame(m_frame),.rsp_address(m_address),.rsp_published(m_published),.rsp_cookie(m_cookie),
        .record_in_valid(state==WB_PUT),.record_in_ready(record_in_ready),.record_in_offset(position),.record_in_present(present),.record_in_payload(record),
        .record_out_valid(record_out_valid),.record_out_ready(state==RF_GET),.record_out_offset(record_out_offset),.record_out_present(record_out_present),.record_out_payload(record_out_payload),
        .leased(memory_leases),.fault(memory_fault),.allocated(allocated),
        .m_awaddr(m_awaddr),.m_awlen(m_awlen),.m_awsize(m_awsize),.m_awburst(m_awburst),.m_awid(m_awid),.m_awvalid(m_awvalid),.m_awready(m_awready),
        .m_wdata(m_wdata),.m_wstrb(m_wstrb),.m_wlast(m_wlast),.m_wvalid(m_wvalid),.m_wready(m_wready),
        .m_bid(m_bid),.m_bresp(m_bresp),.m_bvalid(m_bvalid),.m_bready(m_bready),
        .m_araddr(m_araddr),.m_arlen(m_arlen),.m_arsize(m_arsize),.m_arburst(m_arburst),.m_arid(m_arid),.m_arvalid(m_arvalid),.m_arready(m_arready),
        .m_rdata(m_rdata),.m_rid(m_rid),.m_rresp(m_rresp),.m_rlast(m_rlast),.m_rvalid(m_rvalid),.m_rready(m_rready));
    assign fault=local_fault || memory_fault;
    assign draining=q_draining || fence_open;
    assign cmd_ready=!rst && state==IDLE && !rsp_valid;
    function automatic [3:0] map_memory(input [2:0] status);
        case(status)
            0:map_memory=0;1:map_memory=1;2:map_memory=4;3:map_memory=3;
            4:map_memory=9;5:map_memory=5;6:map_memory=8;7:map_memory=10;
        endcase
    endfunction
    task fail_closed;
        begin local_fault<=1;rsp_status<=10;rsp_valid<=1;rsp_payload<=0;rsp_present<=0;rsp_dirty<=0;rsp_tx<=0;state<=IDLE;end
    endtask
    always @(posedge clk)begin
        if(rst)begin
            query_seen<=0;query_exclusive<=0;retained_query<=0;retained_price<=0;bound_mask<=0;retained_allocated<=0;
            state<=IDLE;op<=0;price<=0;slot<=0;query_id<=0;page<=0;generation<=0;transaction<=0;
            offset<=0;position<=0;field<=0;value<=0;record<=0;present<=0;local_fault<=0;fence_open<=0;frame<=0;
            rsp_valid<=0;rsp_status<=0;rsp_payload<=0;rsp_present<=0;rsp_dirty<=0;rsp_tx<=0;
        end else begin
            if(rsp_valid && rsp_ready)rsp_valid<=0;
            if(cmd_valid && cmd_ready)begin
                op<=cmd_op;slot<=cmd_slot;query_id<=cmd_query;page<=cmd_page;price<=cmd_price;generation<=cmd_generation;
                offset<=cmd_offset;field<=cmd_field;value<=cmd_value;position<=0;record<=0;present<=0;transaction<=0;
                rsp_status<=0;rsp_payload<=0;rsp_present<=0;rsp_dirty<=0;rsp_tx<=0;
                if(fault)begin rsp_status<=10;rsp_valid<=1;end
                else if((cmd_op>=7 && cmd_op<=9) || cmd_op>=13)begin rsp_status<=3;rsp_valid<=1;end
                else if(cmd_op==12)begin
                    if(!query_seen || !query_exclusive)begin rsp_status<=3;rsp_valid<=1;end
                    else if(page_leases!=0 || memory_leases!=0 || draining)begin rsp_status<=4;rsp_valid<=1;end
                    else begin
                        query_id<=retained_query;price<=retained_price;retained_allocated<=allocated;
                        fence_open<=1;state<=CP_BEGIN_SEND;
                    end
                end
                else if(cmd_op==5 || cmd_op==6)state<=M_LOOK_SEND;
                else state<=Q_HOST_SEND;
            end
            case(state)
                Q_HOST_SEND:if(q_ready)state<=Q_HOST_WAIT;
                Q_HOST_WAIT:if(q_valid)begin
                    if(q_status==0)begin
                        if(op==0)begin
                            query_seen<=1;query_exclusive<=!query_seen;
                            retained_query<=query_id;retained_price<=price;
                        end
                        if(op==1)bound_mask[slot]<=1;
                        if(op==4)bound_mask[slot]<=0;
                    end
                    if(op==11 && q_status==0)state<=M_RECYCLE_SEND;
                    else begin
                        rsp_valid<=1;rsp_status<={1'b0,q_status};rsp_payload<=q_payload;rsp_present<=q_present;rsp_dirty<=q_dirty;rsp_tx<=q_tx;state<=IDLE;
                        if(op==10 && q_status==0)fence_open<=1;
                    end
                end
                M_LOOK_SEND:if(m_ready)state<=M_LOOK_WAIT;
                M_LOOK_WAIT:if(m_valid)begin
                    if(m_cookie!=m_expected_cookie)fail_closed;
                    else if(m_status!=0 || (kind && !m_published))begin
                        rsp_valid<=1;rsp_status<=m_status==0?4'd8:map_memory(m_status);state<=IDLE;
                    end else begin frame<=m_frame;state<=Q_START_SEND;end
                end
                Q_START_SEND:if(q_ready)state<=Q_START_WAIT;
                Q_START_WAIT:if(q_valid)begin
                    if(q_status!=0)begin rsp_valid<=1;rsp_status<={1'b0,q_status};rsp_dirty<=q_dirty;state<=IDLE;end
                    else begin transaction<=q_tx;state<=M_TRANSFER_SEND;end
                end
                M_TRANSFER_SEND:if(m_ready)state<=kind?RF_GET:WB_EXPORT_SEND;
                WB_EXPORT_SEND:if(q_ready)state<=WB_EXPORT_WAIT;
                WB_EXPORT_WAIT:if(q_valid)begin
                    if(q_status!=0)fail_closed;
                    else begin record<=q_payload;present<=q_present;state<=WB_PUT;end
                end
                WB_PUT:if(record_in_ready)begin
                    if(position==7)state<=M_STATUS;
                    else begin position<=position+1'b1;state<=WB_EXPORT_SEND;end
                end
                RF_GET:begin
                    if(m_valid)fail_closed;
                    else if(record_out_valid)begin
                        if(record_out_offset!=position)fail_closed;
                        else begin record<=record_out_payload;present<=record_out_present;state<=RF_BEAT_SEND;end
                    end
                end
                RF_BEAT_SEND:if(q_ready)state<=RF_BEAT_WAIT;
                RF_BEAT_WAIT:if(q_valid)begin
                    if(q_status!=0)fail_closed;
                    else if(position==7)state<=M_STATUS;
                    else begin position<=position+1'b1;state<=RF_GET;end
                end
                M_STATUS:if(m_valid)begin
                    if(m_status!=0 || m_cookie!=cookie || m_frame!=frame || !m_published)fail_closed;
                    else state<=Q_COMPLETE_SEND;
                end
                Q_COMPLETE_SEND:if(q_ready)state<=Q_COMPLETE_WAIT;
                Q_COMPLETE_WAIT:if(q_valid)begin
                    if(q_status!=0)fail_closed;
                    else state<=M_RETIRE_SEND;
                end
                M_RETIRE_SEND:if(m_ready)state<=M_RETIRE_WAIT;
                M_RETIRE_WAIT:if(m_valid)begin
                    if(m_status!=0 || m_cookie!=cookie || m_frame!=frame)fail_closed;
                    else begin rsp_valid<=1;rsp_tx<=transaction;state<=IDLE;end
                end
                M_RECYCLE_SEND:if(m_ready)state<=M_RECYCLE_WAIT;
                M_RECYCLE_WAIT:if(m_valid)begin
                    if(m_status!=0 || m_cookie!=m_expected_cookie || memory_leases!=0 || allocated!=0)fail_closed;
                    else begin query_seen<=0;query_exclusive<=0;bound_mask<=0;fence_open<=0;rsp_valid<=1;state<=IDLE;end
                end
                CP_BEGIN_SEND:if(q_ready)state<=CP_BEGIN_WAIT;
                CP_BEGIN_WAIT:if(q_valid)begin
                    if(q_status!=0)fail_closed;else state<=CP_DRAIN;
                end
                // Keep ingress quiet until real queued peer/ACK retirement.
                CP_DRAIN:if(cp_drained)state<=CP_FINISH_SEND;
                CP_FINISH_SEND:if(q_ready)state<=CP_FINISH_WAIT;
                CP_FINISH_WAIT:if(q_valid)begin
                    if(q_status!=0 || page_leases!=0)fail_closed;else state<=CP_MEMORY_SEND;
                end
                CP_MEMORY_SEND:if(m_ready)state<=CP_MEMORY_WAIT;
                CP_MEMORY_WAIT:if(m_valid)begin
                    if(m_status!=0 || m_cookie!=0 || memory_leases!=0 || allocated!=retained_allocated)fail_closed;
                    else state<=CP_QUERY_SEND;
                end
                CP_QUERY_SEND:if(q_ready)state<=CP_QUERY_WAIT;
                CP_QUERY_WAIT:if(q_valid)begin
                    if(q_status!=0)fail_closed;
                    else begin fence_open<=0;rsp_valid<=1;state<=IDLE;end
                end
                default:begin end
            endcase
        end
    end
endmodule
