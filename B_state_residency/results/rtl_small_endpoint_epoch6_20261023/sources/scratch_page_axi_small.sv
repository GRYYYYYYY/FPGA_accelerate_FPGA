`timescale 1ns/1ps
// One page transaction at a time, 3 x 512-bit beats, 64-byte aligned address.
// Every AXI burst stays within 4KB. Successful write completion waits for B;
// successful read completion waits for every R beat to be consumed by the client.
// AXI errors are fail-closed until coordinated cold reset (not hot recovery).
module scratch_page_axi_small(
    input wire clk,rst,
    input wire req_valid,output wire req_ready,input wire req_write,
    input wire [31:0] req_address,input wire [71:0] req_cookie,
    input wire in_valid,output wire in_ready,input wire [511:0] in_data,
    output wire out_valid,input wire out_ready,output wire [511:0] out_data,
    output reg done_valid,input wire done_ready,output reg done_error,
    output reg [71:0] done_cookie,output reg fault,output wire busy,
    output reg [31:0] m_awaddr,output reg [7:0] m_awlen,
    output wire [2:0] m_awsize,output wire [1:0] m_awburst,output wire [3:0] m_awid,
    output reg m_awvalid,input wire m_awready,
    output wire [511:0] m_wdata,output wire [63:0] m_wstrb,
    output wire m_wlast,output wire m_wvalid,input wire m_wready,
    input wire [3:0] m_bid,input wire [1:0] m_bresp,input wire m_bvalid,output wire m_bready,
    output reg [31:0] m_araddr,output reg [7:0] m_arlen,
    output wire [2:0] m_arsize,output wire [1:0] m_arburst,output wire [3:0] m_arid,
    output reg m_arvalid,input wire m_arready,
    input wire [511:0] m_rdata,input wire [3:0] m_rid,input wire [1:0] m_rresp,
    input wire m_rlast,input wire m_rvalid,output wire m_rready
);
    localparam [2:0] IDLE=0,WRITE_DATA=1,WRITE_RESPONSE=2,READ_DATA=3,READ_DRAIN=4;
    reg [2:0] state;
    reg [31:0] base;
    reg [5:0] total,position,length;
    reg address_accepted,buffer_valid,read_burst_last;
    reg [511:0] buffer_data;
    function automatic [5:0] burst_length(input [31:0] address,input [5:0] remaining);
        reg [6:0] room;
        begin room=7'd64-{1'b0,address[11:6]};burst_length=(room<remaining)?room[5:0]:remaining;end
    endfunction
    assign req_ready=!rst && state==IDLE && !done_valid && !fault;
    assign busy=state!=IDLE || done_valid || fault;
    assign in_ready=!rst && state==WRITE_DATA && !buffer_valid;
    assign out_valid=!rst && state==READ_DATA && buffer_valid;
    assign out_data=buffer_data;
    assign m_awsize=3'd6;assign m_awburst=2'd1;assign m_awid=0;
    assign m_arsize=3'd6;assign m_arburst=2'd1;assign m_arid=0;
    assign m_wdata=buffer_data;assign m_wstrb=64'hffffffffffffffff;
    assign m_wvalid=!rst && state==WRITE_DATA && buffer_valid;
    assign m_wlast=position==length-1'b1;
    assign m_bready=!rst && state==WRITE_RESPONSE && address_accepted;
    assign m_rready=!rst && ((state==READ_DATA && address_accepted && !buffer_valid) || state==READ_DRAIN);
    always @(posedge clk) begin
        if(rst) begin
            state<=IDLE;done_valid<=0;done_error<=0;done_cookie<=0;fault<=0;
            m_awvalid<=0;m_arvalid<=0;buffer_valid<=0;address_accepted<=0;
            m_awaddr<=0;m_awlen<=0;m_araddr<=0;m_arlen<=0;
            total<=0;position<=0;length<=0;base<=0;read_burst_last<=0;
        end else begin
            if(done_valid && done_ready)done_valid<=0;
            if(m_awvalid && m_awready)begin m_awvalid<=0;address_accepted<=1;end
            if(m_arvalid && m_arready)begin m_arvalid<=0;address_accepted<=1;end
            if(req_valid && req_ready) begin
                done_cookie<=req_cookie;done_error<=0;total<=0;position<=0;
                base<=req_address;buffer_valid<=0;address_accepted<=0;
                if(req_address[5:0]!=0 || req_address>32'hffffff40) begin done_valid<=1;done_error<=1;end
                else begin
                    length<=burst_length(req_address,3);
                    if(req_write)begin
                        state<=WRITE_DATA;m_awvalid<=1;m_awaddr<=req_address;m_awlen<=burst_length(req_address,3)-1'b1;
                    end else begin
                        state<=READ_DATA;m_arvalid<=1;m_araddr<=req_address;m_arlen<=burst_length(req_address,3)-1'b1;
                    end
                end
            end
            if(in_valid && in_ready)begin buffer_valid<=1;buffer_data<=in_data;end
            if(m_wvalid && m_wready) begin
                buffer_valid<=0;total<=total+1'b1;
                if(position==length-1'b1)state<=WRITE_RESPONSE;
                else position<=position+1'b1;
            end
            if(m_bvalid && m_bready) begin
                if(m_bid!=0 || m_bresp!=0)begin
                    fault<=1;state<=IDLE;done_valid<=1;done_error<=1;
                end else if(total==3)begin state<=IDLE;done_valid<=1;end
                else begin
                    position<=0;length<=burst_length(base+({26'b0,total}<<6),3-total);
                    m_awaddr<=base+({26'b0,total}<<6);m_awlen<=burst_length(base+({26'b0,total}<<6),3-total)-1'b1;
                    m_awvalid<=1;address_accepted<=0;state<=WRITE_DATA;
                end
            end
            if(state==READ_DRAIN && m_rvalid && m_rready)begin
                if(position==length-1'b1)begin state<=IDLE;done_valid<=1;done_error<=1;end
                else position<=position+1'b1;
            end
            if(state==READ_DATA && m_rvalid && m_rready) begin
                if(m_rid!=0 || m_rresp!=0 || m_rlast!=(position==length-1'b1))begin
                    fault<=1;done_error<=1;buffer_valid<=0;
                    if(position==length-1'b1)begin state<=IDLE;done_valid<=1;end
                    else begin position<=position+1'b1;state<=READ_DRAIN;end
                end else begin
                    buffer_valid<=1;buffer_data<=m_rdata;total<=total+1'b1;
                    read_burst_last<=m_rlast;
                    if(!m_rlast)position<=position+1'b1;
                end
            end
            if(out_valid && out_ready) begin
                buffer_valid<=0;
                if(total==3)begin state<=IDLE;done_valid<=1;end
                else if(read_burst_last)begin
                    position<=0;length<=burst_length(base+({26'b0,total}<<6),3-total);
                    m_araddr<=base+({26'b0,total}<<6);m_arlen<=burst_length(base+({26'b0,total}<<6),3-total)-1'b1;
                    m_arvalid<=1;address_accepted<=0;
                end
            end
        end
    end
endmodule
