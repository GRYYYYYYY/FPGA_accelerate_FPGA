`timescale 1ns/1ps
// One backing window per cold-reset lifetime. 4KiB alignment preserves the
// existing relative-address burst splits. No reconfiguration while configured.
module backing_base_config #(parameter integer FRAMES=163840)(
 input wire clk,rst,input wire cfg_base_valid,output wire cfg_base_ready,
 input wire [63:0] cfg_base_address,
 output reg cfg_rsp_valid,input wire cfg_rsp_ready,output reg [1:0] cfg_rsp_status,
 output reg configured,output reg [63:0] backing_base
);
 localparam [64:0] MAX_OFFSET=65'd192*FRAMES-65'd1;
 wire [64:0] last_address={1'b0,cfg_base_address}+MAX_OFFSET;
 assign cfg_base_ready=!rst && !configured && !cfg_rsp_valid;
 always @(posedge clk)begin
  if(rst)begin cfg_rsp_valid<=0;cfg_rsp_status<=0;configured<=0;backing_base<=0;end
  else begin
   if(cfg_rsp_valid && cfg_rsp_ready)cfg_rsp_valid<=0;
   if(cfg_base_valid && cfg_base_ready)begin
    cfg_rsp_valid<=1;
    if(cfg_base_address[11:0]!=0)cfg_rsp_status<=1;
    else if(FRAMES<1 || last_address[64])cfg_rsp_status<=2;
    else begin cfg_rsp_status<=0;backing_base<=cfg_base_address;configured<=1;end
   end
  end
 end
endmodule
