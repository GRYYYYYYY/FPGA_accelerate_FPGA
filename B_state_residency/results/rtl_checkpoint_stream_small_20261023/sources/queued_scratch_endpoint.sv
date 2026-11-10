`timescale 1ns/1ps
// Closed, single-clock endpoint: all command, work, response and fence packets
// live in these FIFOs. No caller-supplied quiescence booleans. COMPLETE still
// denotes an externally durable page operation; AXI/backing memory is not here.
module queued_scratch_endpoint #(
    parameter integer TX_BITS=16, GENERATION_BITS=16, TAG_BITS=2,
    parameter integer QUEUE_DEPTH=4, CONTROL_DEPTH=2,
    parameter integer QCOUNT_BITS=$clog2(QUEUE_DEPTH+1),
    parameter integer CCOUNT_BITS=$clog2(CONTROL_DEPTH+1)
)(
    input wire clk,rst,
    input wire cmd_valid,output wire cmd_ready,
    input wire [3:0] cmd_op,
    input wire [1:0] cmd_slot,cmd_query,
    input wire [17:0] cmd_page,
    input wire [3:0] cmd_price,
    input wire [GENERATION_BITS-1:0] cmd_generation,
    input wire [TX_BITS-1:0] cmd_tx,
    input wire cmd_kind,cmd_present,
    input wire [5:0] cmd_offset,
    input wire [2:0] cmd_field,
    input wire [31:0] cmd_value,
    input wire [159:0] cmd_payload,
    output wire rsp_valid,input wire rsp_ready,
    output wire [2:0] rsp_status,
    output wire [159:0] rsp_payload,
    output wire rsp_present,rsp_dirty,
    output wire [TX_BITS-1:0] rsp_tx,
    // Scheduling/backpressure enables, NOT drain attestations. Tie high when
    // connected stages are always available. Low may stall but cannot recycle.
    input wire dispatch_enable,execute_enable,fence_service_enable,ack_receive_enable,
    output wire draining,
    output reg fence_active,peer_sealed,acknowledged,
    output reg [TAG_BITS-1:0] fence_tag,
    output reg [3:0] leases,
    output wire [QCOUNT_BITS-1:0] request_count,work_count,response_count,
    output wire [CCOUNT_BITS-1:0] fence_request_count,fence_ack_count
);
    localparam integer CMD_WIDTH=233+TX_BITS+GENERATION_BITS;
    localparam integer RSP_WIDTH=165+TX_BITS;
    localparam [3:0] WRITEBACK=5,REFILL=6,COMPLETE=8,BEGIN_FENCE=10,FINISH_FENCE=11,
        RETRANSMIT_FENCE=12,DUPLICATE_ACK=13;
    localparam [2:0] OK=0,BAD=3,BUSY=4;
    wire [CMD_WIDTH-1:0] packed_command={cmd_op,cmd_slot,cmd_page,cmd_query,cmd_price,
        cmd_generation,cmd_tx,cmd_kind,cmd_present,cmd_offset,cmd_field,cmd_value,cmd_payload};
    wire [CMD_WIDTH-1:0] request_data,work_data;
    wire request_valid,request_ready,work_valid,work_ready,work_in_ready;
    bounded_sync_fifo #(.WIDTH(CMD_WIDTH),.DEPTH(QUEUE_DEPTH)) requests(
        .clk(clk),.rst(rst),.in_valid(cmd_valid),.in_ready(cmd_ready),.in_data(packed_command),
        .out_valid(request_valid),.out_ready(request_ready),.out_data(request_data),.count(request_count));
    assign request_ready=dispatch_enable && work_in_ready;
    bounded_sync_fifo #(.WIDTH(CMD_WIDTH),.DEPTH(QUEUE_DEPTH)) work(
        .clk(clk),.rst(rst),.in_valid(request_valid && dispatch_enable),.in_ready(work_in_ready),.in_data(request_data),
        .out_valid(work_valid),.out_ready(work_ready),.out_data(work_data),.count(work_count));
    wire [3:0] op,price;
    wire [1:0] slot,query_id;
    wire [17:0] page;
    wire [GENERATION_BITS-1:0] generation;
    wire [TX_BITS-1:0] tx;
    wire kind,present;
    wire [5:0] offset;
    wire [2:0] field;
    wire [31:0] value;
    wire [159:0] payload;
    assign {op,slot,page,query_id,price,generation,tx,kind,present,offset,field,value,payload}=work_data;
    reg busy,local_pending;
    reg [2:0] local_status;
    reg [3:0] pending_op;
    reg [1:0] pending_slot;
    wire local_op=op==RETRANSMIT_FENCE || op==DUPLICATE_ACK;
    wire core_ready,core_rsp_valid;
    wire [2:0] core_status;
    wire [159:0] core_payload;
    wire core_present,core_dirty;
    wire [TX_BITS-1:0] core_tx;
    wire take=work_valid && work_ready;
    assign work_ready=!rst && !busy && execute_enable && (local_op || core_ready);
    wire core_valid=work_valid && !busy && execute_enable && !local_op;
    wire response_in_ready;
    wire retire=busy && (local_pending || core_rsp_valid) && response_in_ready;
    wire [RSP_WIDTH-1:0] response_data;
    wire [2:0] retiring_status=local_pending?local_status:core_status;
    bounded_sync_fifo #(.WIDTH(RSP_WIDTH),.DEPTH(QUEUE_DEPTH)) responses(
        .clk(clk),.rst(rst),.in_valid(busy && (local_pending || core_rsp_valid)),.in_ready(response_in_ready),
        .in_data(local_pending ? {local_status,{(RSP_WIDTH-3){1'b0}}} : {core_status,core_payload,core_present,core_dirty,core_tx}),
        .out_valid(rsp_valid),.out_ready(rsp_ready),.out_data(response_data),.count(response_count));
    assign {rsp_status,rsp_payload,rsp_present,rsp_dirty,rsp_tx}=response_data;

    wire fence_req_ready,fence_req_valid,fence_ack_ready,fence_ack_valid;
    wire [23:0] fence_req_data,fence_ack_data;
    // Wire packet is opcode u8 followed by little-endian tag u16.
    wire [15:0] tag16={{(16-TAG_BITS){1'b0}},fence_tag};
    wire begin_retire=retire && pending_op==BEGIN_FENCE && retiring_status==OK;
    wire finish_retire=retire && pending_op==FINISH_FENCE && retiring_status==OK;
    wire retransmit=take && op==RETRANSMIT_FENCE && fence_active && fence_req_ready;
    wire duplicate_ack=take && op==DUPLICATE_ACK && fence_active && fence_ack_valid && fence_ack_ready;
    wire control_service=fence_service_enable && fence_active && draining && !busy
        && request_count==0 && work_count==0 && leases==0
        && !(cmd_valid && cmd_ready) && fence_req_valid && fence_ack_ready;
    wire receive_ack=ack_receive_enable && fence_active && fence_ack_valid;
    bounded_sync_fifo #(.WIDTH(24),.DEPTH(CONTROL_DEPTH)) fence_requests(
        .clk(clk),.rst(rst),.in_valid(begin_retire || retransmit),.in_ready(fence_req_ready),
        .in_data({tag16,8'd0}),.out_valid(fence_req_valid),.out_ready(control_service),
        .out_data(fence_req_data),.count(fence_request_count));
    bounded_sync_fifo #(.WIDTH(24),.DEPTH(CONTROL_DEPTH)) fence_acks(
        .clk(clk),.rst(rst),.in_valid(control_service || duplicate_ack),.in_ready(fence_ack_ready),
        .in_data(duplicate_ack ? fence_ack_data : {fence_req_data[23:8],8'd1}),
        .out_valid(fence_ack_valid),.out_ready(receive_ack),.out_data(fence_ack_data),.count(fence_ack_count));
    // Only the currently executing FINISH is excluded from the drain set.
    // In particular a simultaneous host ingress handshake makes this false.
    wire queues_drained=fence_active && acknowledged && peer_sealed && leases==0
        && request_count==0 && work_count==1 && response_count==0
        && fence_request_count==0 && fence_ack_count==0 && !(cmd_valid && cmd_ready);
    scratch_page_controller #(.TX_BITS(TX_BITS),.GENERATION_BITS(GENERATION_BITS)) endpoint(
        .clk(clk),.rst(rst),.cmd_valid(core_valid),.cmd_ready(core_ready),.cmd_op(op),
        .cmd_slot(slot),.cmd_page(page),.cmd_query(query_id),.cmd_price(price),.cmd_generation(generation),
        .cmd_tx(tx),.cmd_kind(kind),.cmd_present(present),.cmd_offset(offset),.cmd_field(field),
        .cmd_value(value),.cmd_payload(payload),.peer_quiescent(queues_drained),.ingress_empty(queues_drained),
        .rsp_valid(core_rsp_valid),.rsp_ready(busy && !local_pending && response_in_ready),
        .rsp_status(core_status),.rsp_payload(core_payload),.rsp_present(core_present),.rsp_dirty(core_dirty),
        .rsp_tx(core_tx),.draining(draining));
    always @(posedge clk) begin
        if(rst) begin
            busy<=0;local_pending<=0;local_status<=OK;pending_op<=0;pending_slot<=0;
            fence_active<=0;peer_sealed<=0;acknowledged<=0;fence_tag<=0;leases<=0;
        end else begin
            if(take) begin
                busy<=1;local_pending<=local_op;pending_op<=op;pending_slot<=slot;
                if(local_op) begin
                    if(!fence_active) local_status<=BAD;
                    else if(op==RETRANSMIT_FENCE) local_status<=fence_req_ready?OK:BUSY;
                    else local_status<=(fence_ack_valid && fence_ack_ready)?OK:BUSY;
                end
            end
            if(retire) begin
                busy<=0;local_pending<=0;
                if(retiring_status==OK) begin
                    if(pending_op==WRITEBACK || pending_op==REFILL) leases[pending_slot]<=1;
                    if(pending_op==COMPLETE) leases[pending_slot]<=0;
                end
            end
            if(begin_retire) begin fence_active<=1;peer_sealed<=0;acknowledged<=0; end
            if(control_service && fence_req_data=={tag16,8'd0}) peer_sealed<=1;
            if(receive_ack && fence_ack_data=={tag16,8'd1}) acknowledged<=1;
            if(finish_retire) begin
                fence_active<=0;peer_sealed<=0;acknowledged<=0;fence_tag<=fence_tag+1'b1;
            end
        end
    end
endmodule
