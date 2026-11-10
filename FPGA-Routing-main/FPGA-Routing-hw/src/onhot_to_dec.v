`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 2025/04/14 10:42:44
// Design Name: 
// Module Name: onhot_to_dec
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module onehot_to_dec #(
    parameter SIZE = 700,
    parameter WIDTH = $clog2(SIZE)
) (
    input      [SIZE-1:0]     onehot         ,
    output reg [WIDTH-1:0]    dec         ,
    input                     clk            ,
    input                     reset
);

integer  i    ;

always @(posedge clk) begin
  if(reset)
    dec <= 0;
  else 
    for(i = 0; i < SIZE; i=i+1) begin
        if(onehot[i]) 
          dec <= i;
    end
end

endmodule
