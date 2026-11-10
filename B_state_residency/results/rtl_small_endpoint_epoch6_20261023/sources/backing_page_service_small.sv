`timescale 1ns/1ps
// Address ownership + AXI page operation. No external MEMORY_DONE injection.
// cmd4=lookup owner; cmd5=trusted ID-only recycle; 6..7 invalid.
// cmd 0=reserve owner, 1=transfer cookie kind, 2=retire after consumer commit,
// 3=recycle after enclosing endpoint fence. Last two are adapter-side controls.
module backing_page_service_small #(
    parameter integer FRAMES=163840,INDEX_BITS=18,HASH_BITS=18,PROBE_LIMIT=64,EPOCH_BITS=8
)(
    input wire clk,rst,input wire cmd_valid,output wire cmd_ready,
    input wire [2:0] cmd_op,input wire [26:0] cmd_owner,
    input wire [INDEX_BITS-1:0] cmd_frame,input wire [71:0] cmd_cookie,input wire fence_retired,
    output reg rsp_valid,input wire rsp_ready,output reg [2:0] rsp_status,
    output reg [INDEX_BITS-1:0] rsp_frame,output reg [31:0] rsp_address,
    output reg rsp_published,output reg [71:0] rsp_cookie,
    input wire in_valid,output wire in_ready,input wire [511:0] in_data,
    output wire out_valid,input wire out_ready,output wire [511:0] out_data,
    output wire [31:0] leased,output wire fault,output wire [INDEX_BITS:0] allocated,
    output wire [31:0] m_awaddr,output wire [7:0] m_awlen,output wire [2:0] m_awsize,
    output wire [1:0] m_awburst,output wire [3:0] m_awid,output wire m_awvalid,input wire m_awready,
    output wire [511:0] m_wdata,output wire [63:0] m_wstrb,output wire m_wlast,output wire m_wvalid,input wire m_wready,
    input wire [3:0] m_bid,input wire [1:0] m_bresp,input wire m_bvalid,output wire m_bready,
    output wire [31:0] m_araddr,output wire [7:0] m_arlen,output wire [2:0] m_arsize,
    output wire [1:0] m_arburst,output wire [3:0] m_arid,output wire m_arvalid,input wire m_arready,
    input wire [511:0] m_rdata,input wire [3:0] m_rid,input wire [1:0] m_rresp,input wire m_rlast,input wire m_rvalid,output wire m_rready
);
    localparam [2:0] IDLE=0,DIR_SEND=1,DIR_WAIT=2,DMA_SEND=3,DMA_WAIT=4;
    reg [2:0] state,dir_op;
    reg transfer,finishing,mem_success,saved_fence;
    reg [26:0] owner;
    reg [INDEX_BITS-1:0] frame;
    reg [71:0] cookie;
    reg [31:0] address;
    wire dir_ready,dir_rsp_valid,dir_published,dir_fault;
    wire [2:0] dir_status;
    wire [INDEX_BITS-1:0] dir_frame;
    wire [31:0] dir_address;
    wire dma_ready,dma_done,dma_error,dma_fault,dma_busy;
    wire [71:0] dma_cookie;
    assign fault=dir_fault || dma_fault;
    assign cmd_ready=!rst && state==IDLE && !rsp_valid;
    backing_frame_directory_small #(.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS),.PROBE_LIMIT(PROBE_LIMIT),.EPOCH_BITS(EPOCH_BITS)) directory(
        .clk(clk),.rst(rst),.cmd_valid(state==DIR_SEND),.cmd_ready(dir_ready),.cmd_op(dir_op),
        .cmd_owner(owner),.cmd_frame(frame),.cmd_cookie(cookie),.memory_success(mem_success),.fence_retired(saved_fence),
        .rsp_valid(dir_rsp_valid),.rsp_ready(state==DIR_WAIT),.rsp_status(dir_status),
        .rsp_frame(dir_frame),.rsp_address(dir_address),.rsp_published(dir_published),.allocated(allocated),.leased(leased),.any_fault(dir_fault));
    scratch_page_axi_small dma(
        .clk(clk),.rst(rst),.req_valid(state==DMA_SEND),.req_ready(dma_ready),.req_write(!cookie[64]),
        .req_address(address),.req_cookie(cookie),.in_valid(in_valid),.in_ready(in_ready),.in_data(in_data),
        .out_valid(out_valid),.out_ready(out_ready),.out_data(out_data),
        .done_valid(dma_done),.done_ready(state==DMA_WAIT),.done_error(dma_error),.done_cookie(dma_cookie),.fault(dma_fault),.busy(dma_busy),
        .m_awaddr(m_awaddr),.m_awlen(m_awlen),.m_awsize(m_awsize),.m_awburst(m_awburst),.m_awid(m_awid),.m_awvalid(m_awvalid),.m_awready(m_awready),
        .m_wdata(m_wdata),.m_wstrb(m_wstrb),.m_wlast(m_wlast),.m_wvalid(m_wvalid),.m_wready(m_wready),
        .m_bid(m_bid),.m_bresp(m_bresp),.m_bvalid(m_bvalid),.m_bready(m_bready),
        .m_araddr(m_araddr),.m_arlen(m_arlen),.m_arsize(m_arsize),.m_arburst(m_arburst),.m_arid(m_arid),.m_arvalid(m_arvalid),.m_arready(m_arready),
        .m_rdata(m_rdata),.m_rid(m_rid),.m_rresp(m_rresp),.m_rlast(m_rlast),.m_rvalid(m_rvalid),.m_rready(m_rready));
    always @(posedge clk)begin
        if(rst)begin
            state<=IDLE;rsp_valid<=0;rsp_status<=0;rsp_frame<=0;rsp_address<=0;rsp_published<=0;rsp_cookie<=0;
            dir_op<=0;transfer<=0;finishing<=0;mem_success<=0;saved_fence<=0;owner<=0;frame<=0;cookie<=0;address<=0;
        end else begin
            if(rsp_valid && rsp_ready)rsp_valid<=0;
            if(cmd_valid && cmd_ready)begin
                rsp_cookie<=cmd_cookie;rsp_frame<=0;rsp_address<=0;rsp_published<=0;rsp_status<=0;
                if(cmd_op>5)begin rsp_valid<=1;rsp_status<=3;end
                else if((cmd_op==1 || cmd_op==5) && fault)begin rsp_valid<=1;rsp_status<=7;end
                else begin
                    owner<=cmd_owner;frame<=cmd_frame;cookie<=cmd_cookie;saved_fence<=fence_retired;
                    transfer<=cmd_op==1;finishing<=0;mem_success<=0;
                    case(cmd_op)0:dir_op<=0;1:dir_op<=1;2:dir_op<=3;3:dir_op<=4;4:dir_op<=5;5:dir_op<=6;default:dir_op<=7;endcase
                    state<=DIR_SEND;
                end
            end
            if(state==DIR_SEND && dir_ready)state<=DIR_WAIT;
            if(state==DIR_WAIT && dir_rsp_valid)begin
                if(transfer && !finishing && dir_status==0)begin address<=dir_address;state<=DMA_SEND;end
                else begin
                    rsp_valid<=1;rsp_status<=dir_status;rsp_frame<=dir_frame;rsp_address<=dir_address;rsp_published<=dir_published;
                    state<=IDLE;
                end
            end
            if(state==DMA_SEND && dma_ready)state<=DMA_WAIT;
            if(state==DMA_WAIT && dma_done)begin
                mem_success<=!dma_error && dma_cookie==cookie;dir_op<=2;finishing<=1;state<=DIR_SEND;
            end
        end
    end
endmodule
