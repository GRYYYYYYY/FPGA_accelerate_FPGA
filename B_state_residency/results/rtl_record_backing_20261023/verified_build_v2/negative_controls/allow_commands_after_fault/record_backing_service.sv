`timescale 1ns/1ps
// Address ownership + AXI page operation. No external MEMORY_DONE injection.
// cmd4=lookup owner without allocation (UNREADY on miss); 5..7 invalid.
// cmd 0=reserve owner, 1=transfer cookie kind, 2=retire after consumer commit,
// 3=recycle after enclosing endpoint fence. Last two are adapter-side controls.
module record_backing_service #(
    parameter integer FRAMES=23405,INDEX_BITS=15
)(
    input wire clk,rst,input wire cmd_valid,output wire cmd_ready,
    input wire [2:0] cmd_op,input wire [23:0] cmd_owner,
    input wire [INDEX_BITS-1:0] cmd_frame,input wire [63:0] cmd_cookie,input wire fence_retired,
    output reg rsp_valid,input wire rsp_ready,output reg [2:0] rsp_status,
    output reg [INDEX_BITS-1:0] rsp_frame,output reg [31:0] rsp_address,
    output reg rsp_published,output reg [63:0] rsp_cookie,
    input wire record_in_valid,output wire record_in_ready,
    input wire [5:0] record_in_offset,input wire record_in_present,input wire [159:0] record_in_payload,
    output wire record_out_valid,input wire record_out_ready,
    output wire [5:0] record_out_offset,output wire record_out_present,output wire [159:0] record_out_payload,
    output wire [3:0] leased,output wire fault,output wire [INDEX_BITS:0] allocated,
    output wire [31:0] m_awaddr,output wire [7:0] m_awlen,output wire [2:0] m_awsize,
    output wire [1:0] m_awburst,output wire [3:0] m_awid,output wire m_awvalid,input wire m_awready,
    output wire [511:0] m_wdata,output wire [63:0] m_wstrb,output wire m_wlast,output wire m_wvalid,input wire m_wready,
    input wire [3:0] m_bid,input wire [1:0] m_bresp,input wire m_bvalid,output wire m_bready,
    output wire [31:0] m_araddr,output wire [7:0] m_arlen,output wire [2:0] m_arsize,
    output wire [1:0] m_arburst,output wire [3:0] m_arid,output wire m_arvalid,input wire m_arready,
    input wire [511:0] m_rdata,input wire [3:0] m_rid,input wire [1:0] m_rresp,input wire m_rlast,input wire m_rvalid,output wire m_rready
);
    // Success is reported only after all record outputs/inputs and the memory
    // response complete. RETIRE and RECYCLE remain trusted upstream controls.
    localparam [3:0] IDLE=0,START=1,ENCODE=2,SEND=3,WAIT_MEMORY=4,COMMIT=5,FINISH=6,CANCEL=7;
    reg [3:0] state;
    reg [2:0] op;
    reg [23:0] owner;
    reg [INDEX_BITS-1:0] frame;
    reg [63:0] cookie;
    reg saved_fence,local_fault;
    wire service_ready,service_valid,service_published,service_fault;
    wire [2:0] service_status;
    wire [INDEX_BITS-1:0] service_frame;
    wire [31:0] service_address;
    wire [63:0] service_cookie;
    wire c_start_ready,c_busy,c_in_ready,c_out_valid,c_raw_last,c_commit_ready,c_done,c_error;
    wire raw_write_valid,raw_write_ready,raw_read_valid,raw_read_ready;
    wire [511:0] raw_write_data,raw_read_data;
    assign fault=local_fault || service_fault;
    assign cmd_ready=!rst && state==IDLE && !rsp_valid;
    assign record_in_ready=state==ENCODE && c_in_ready;
    assign record_out_valid=state==FINISH && c_out_valid;
    scratch_page_codec codec(
        .clk(clk),.rst(rst),.start_valid(state==START),.start_ready(c_start_ready),.start_decode(cookie[58]),
        .cancel(state==CANCEL),.busy(c_busy),
        .record_in_valid(state==ENCODE && record_in_valid),.record_in_ready(c_in_ready),
        .record_in_offset(record_in_offset),.record_in_present(record_in_present),.record_in_payload(record_in_payload),
        .record_out_valid(c_out_valid),.record_out_ready(state==FINISH && record_out_ready),
        .record_out_offset(record_out_offset),.record_out_present(record_out_present),.record_out_payload(record_out_payload),
        .raw_in_valid(raw_read_valid),.raw_in_ready(raw_read_ready),.raw_in_data(raw_read_data),
        .raw_out_valid(raw_write_valid),.raw_out_ready(raw_write_ready),.raw_out_data(raw_write_data),.raw_out_last(c_raw_last),
        .commit_valid(state==COMMIT),.commit_ready(c_commit_ready),.commit_ok(1'b1),
        .done_valid(c_done),.done_ready(state==FINISH),.done_error(c_error));
    backing_page_service_lookup #(.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS)) memory_service(
        .clk(clk),.rst(rst),.cmd_valid(state==SEND),.cmd_ready(service_ready),.cmd_op(op),.cmd_owner(owner),
        .cmd_frame(frame),.cmd_cookie(cookie),.fence_retired(saved_fence),
        .rsp_valid(service_valid),.rsp_ready(state==WAIT_MEMORY),.rsp_status(service_status),.rsp_frame(service_frame),
        .rsp_address(service_address),.rsp_published(service_published),.rsp_cookie(service_cookie),
        .in_valid(raw_write_valid),.in_ready(raw_write_ready),.in_data(raw_write_data),
        .out_valid(raw_read_valid),.out_ready(raw_read_ready),.out_data(raw_read_data),
        .leased(leased),.fault(service_fault),.allocated(allocated),
        .m_awaddr(m_awaddr),.m_awlen(m_awlen),.m_awsize(m_awsize),.m_awburst(m_awburst),.m_awid(m_awid),.m_awvalid(m_awvalid),.m_awready(m_awready),
        .m_wdata(m_wdata),.m_wstrb(m_wstrb),.m_wlast(m_wlast),.m_wvalid(m_wvalid),.m_wready(m_wready),
        .m_bid(m_bid),.m_bresp(m_bresp),.m_bvalid(m_bvalid),.m_bready(m_bready),
        .m_araddr(m_araddr),.m_arlen(m_arlen),.m_arsize(m_arsize),.m_arburst(m_arburst),.m_arid(m_arid),.m_arvalid(m_arvalid),.m_arready(m_arready),
        .m_rdata(m_rdata),.m_rid(m_rid),.m_rresp(m_rresp),.m_rlast(m_rlast),.m_rvalid(m_rvalid),.m_rready(m_rready));
    always @(posedge clk)begin
        if(rst)begin
            state<=IDLE;op<=0;owner<=0;frame<=0;cookie<=0;saved_fence<=0;local_fault<=0;
            rsp_valid<=0;rsp_status<=0;rsp_frame<=0;rsp_address<=0;rsp_published<=0;rsp_cookie<=0;
        end else begin
            if(rsp_valid && rsp_ready)rsp_valid<=0;
            if(cmd_valid && cmd_ready)begin
                op<=cmd_op;owner<=cmd_owner;frame<=cmd_frame;cookie<=cmd_cookie;saved_fence<=fence_retired;
                rsp_status<=0;rsp_frame<=0;rsp_address<=0;rsp_published<=0;rsp_cookie<=cmd_cookie;
                // After a memory/decoded-format fault, never retire even a
                // directory COMPLETE lease until coordinated recovery.
                if(1'b0)begin rsp_status<=7;rsp_valid<=1;end
                else if(cmd_op==1)state<=START;
                else state<=SEND;
            end
            case(state)
                START:if(c_start_ready)state<=cookie[58]?SEND:ENCODE;
                ENCODE:begin
                    if(c_done)begin rsp_status<=3;state<=FINISH;end
                    else if(raw_write_valid)state<=SEND;
                end
                SEND:if(service_ready)state<=WAIT_MEMORY;
                WAIT_MEMORY:if(service_valid)begin
                    rsp_status<=service_status;rsp_frame<=service_frame;rsp_address<=service_address;rsp_published<=service_published;
                    if(service_cookie!=cookie)begin
                        rsp_status<=7;rsp_frame<=0;rsp_address<=0;rsp_published<=0;local_fault<=1;
                        if(op==1)state<=CANCEL;else begin rsp_valid<=1;state<=IDLE;end
                    end else if(op!=1)begin rsp_valid<=1;state<=IDLE;end
                    else if(service_status!=0)state<=CANCEL;
                    else state<=cookie[58]?COMMIT:FINISH;
                end
                COMMIT:begin
                    if(c_done)state<=FINISH;
                    else if(c_commit_ready)state<=FINISH;
                end
                CANCEL:state<=FINISH;
                FINISH:if(c_done)begin
                    if(c_error && rsp_status==0)begin
                        rsp_status<=7;rsp_frame<=0;rsp_address<=0;rsp_published<=0;local_fault<=1;
                    end
                    rsp_valid<=1;state<=IDLE;
                end
                default:begin end
            endcase
        end
    end
endmodule
