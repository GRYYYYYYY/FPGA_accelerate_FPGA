`timescale 1ns/1ps
// Observer only: never gates request/response VALID, READY, or data.
// Reset belongs to cold initialization, never target reset or abort.
module baseline_retirement_guard(
 input wire clk,cold_rst,reader_idle,cfg_valid,
 input wire req_valid,req_ready,rsp_valid,rsp_ready,
 input wire arvalid,arready,input wire[7:0]arlen,
 input wire rvalid,rready,rlast,
 output wire retired,physical_drained,output reg owned,output wire fault
);
 reg protocol_fault;wire axi_fault;
 wire request=req_valid&&req_ready,response=rsp_valid&&rsp_ready;
 assign fault=protocol_fault||axi_fault;
 assign retired=!cold_rst&&!fault&&!owned&&reader_idle&&physical_drained&&!req_valid&&!rsp_valid&&!cfg_valid;
 axi_drain_watch physical(.clk(clk),.rst(cold_rst),.arvalid(arvalid),.arready(arready),.arlen(arlen),
 .rvalid(rvalid),.rready(rready),.rlast(rlast),.awvalid(1'b0),.awready(1'b0),.awlen(8'b0),
 .wvalid(1'b0),.wready(1'b0),.wlast(1'b0),.bvalid(1'b0),.bready(1'b0),.drained(physical_drained),.fault(axi_fault));
 always @(posedge clk)begin
  if(cold_rst)begin owned<=0;protocol_fault<=0;end
  else begin
   if(request)begin if(owned)protocol_fault<=1;owned<=1;end
   if(response)begin if(!owned)protocol_fault<=1;owned<=0;end
  end
 end
endmodule
