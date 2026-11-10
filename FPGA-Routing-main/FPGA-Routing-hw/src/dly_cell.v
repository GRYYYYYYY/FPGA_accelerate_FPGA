`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 2025/02/20 23:04:49
// Design Name: 
// Module Name: dly_cell
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


module dly_cell #(parameter DW = 1, DLY = 1) (
  output  wire  [DW-1 : 0]    dout      ,

  input         [DW-1 : 0]    din       ,

  input                       clk       ,
  input                       reset      
  );

  reg [DW-1 : 0] din_dly[DLY-1 : 0]     ;

  always@(posedge clk) begin
    if( reset )
      din_dly[0] <= 0   ;
    else
      din_dly[0] <= din ;
  end

  genvar i;
  generate for(i = 1; i < DLY; i = i + 1) begin
    always@(posedge clk) begin
      if( reset )
        din_dly[i] <= 0               ;
      else
        din_dly[i] <= din_dly[i - 1]  ;
      end
  end
  endgenerate
  
  assign dout = din_dly[DLY - 1]      ;

endmodule

