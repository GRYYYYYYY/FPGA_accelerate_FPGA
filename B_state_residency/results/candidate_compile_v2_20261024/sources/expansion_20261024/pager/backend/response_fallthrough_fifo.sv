`timescale 1ns/1ps
// Empty response queue forwards immediately. A stalled response is captured.
// Nonempty/full behavior and physical occupancy match bounded_sync_fifo.
module record_response_fallthrough_fifo #(
 parameter integer WIDTH=24,DEPTH=4,COUNT_BITS=$clog2(DEPTH+1)
)(input wire clk,rst,input wire in_valid,output wire in_ready,
 input wire [WIDTH-1:0] in_data,output wire out_valid,input wire out_ready,
 output wire [WIDTH-1:0] out_data,output reg [COUNT_BITS-1:0] count,input wire bypass_enable);
 localparam integer PTR_BITS=DEPTH<2?1:$clog2(DEPTH);
 reg [WIDTH-1:0] memory[0:DEPTH-1];
 reg [PTR_BITS-1:0] read_ptr,write_ptr;
 assign in_ready=!rst && count<DEPTH;
 assign out_valid=!rst && (count!=0 || (bypass_enable && in_valid));
 assign out_data=count!=0?memory[read_ptr]:in_data;
 wire bypass=bypass_enable && count==0 && in_valid && in_ready && out_ready;
 wire push=in_valid && in_ready && !bypass;
 wire pop=count!=0 && out_valid && out_ready;
 always @(posedge clk)begin
  if(rst)begin count<=0;read_ptr<=0;write_ptr<=0;end
  else begin
   if(push)begin memory[write_ptr]<=in_data;write_ptr<=write_ptr==DEPTH-1?0:write_ptr+1'b1;end
   if(pop)read_ptr<=read_ptr==DEPTH-1?0:read_ptr+1'b1;
   case({push,pop})2'b10:count<=count+1'b1;2'b01:count<=count-1'b1;default:begin end endcase
  end
 end
endmodule
