`timescale 1ns/1ps
// Observer only. Single outstanding AXI write burst, W may precede AW.
module axi_drain_watch(input wire clk,rst,input wire arvalid,arready,input wire[7:0]arlen,
 input wire rvalid,rready,rlast,input wire awvalid,awready,input wire[7:0]awlen,
 input wire wvalid,wready,wlast,input wire bvalid,bready,output wire drained,output reg fault);
 reg[31:0]reads,writes;reg aw_owned;reg[8:0]expected_write;
 wire ar=arvalid&&arready,r=rvalid&&rready,aw=awvalid&&awready,w=wvalid&&wready,b=bvalid&&bready;
 assign drained=!rst&&!fault&&reads==0&&writes==0&&!aw_owned&&!arvalid&&!rvalid&&!awvalid&&!wvalid&&!bvalid;
 always @(posedge clk)begin
  if(rst)begin reads<=0;writes<=0;aw_owned<=0;expected_write<=0;fault<=0;end
  else begin
   if(ar||r)begin
    reads<=reads+(ar?{24'b0,arlen}+32'd1:32'd0)-(r?32'd1:32'd0);
    if((r&&reads==0&&!ar)||(ar&&reads!=0)||(r&&rlast!=(reads==1)))fault<=1;
   end
   if(aw)begin if(aw_owned)fault<=1;aw_owned<=1;expected_write<={1'b0,awlen}+1'b1;end
   if(w||b)writes<=writes+(w?32'd1:32'd0)-(b?{23'b0,expected_write}:32'd0);
   if(b)begin if(!aw_owned||writes!={23'b0,expected_write})fault<=1;aw_owned<=0;end
  end
 end
endmodule
