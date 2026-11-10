`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 2025/04/14 16:04:19
// Design Name: 
// Module Name: adr_to_cor
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


module adr_to_cor #(
  parameter   RAM_NUM    =  700 ,   
  parameter   X_BLOCK_WD =  18  ,
  parameter   Y_BLOCK_WD =  19  ,
  parameter   X_RAM_NUM  =  10  ,
  parameter   Y_RAM_NUM  =  10  ,
  parameter   Z_RAM_NUM  =  7   , 
  parameter   ADR_DW     =  10  ,  
  parameter   X_DW       =  8   ,
  parameter   Y_DW       =  8   ,
  parameter   Z_DW       =  3 
)(
  output  reg [X_DW-1:0]      cor_x               ,
  output  reg [Y_DW-1:0]      cor_y               ,
  output  reg [Z_DW-1:0]      cor_z               ,
  input [$clog2(RAM_NUM)-1:0] ram_index           ,  
  input [ADR_DW-1:0]          adr                 ,
  input                       adr_vld             ,
  input                       clk                 ,
  input                       reset
);

always @(posedge clk ) begin
  if(reset) begin
    cor_x <=  'h0     ;
    cor_y <=  'h0     ;
    cor_z <=  'h0     ;
  end else if(adr_vld)  begin
    cor_x <=  adr-Y_BLOCK_WD*(adr/Y_BLOCK_WD)+X_BLOCK_WD*ram_index/(Y_RAM_NUM*Z_RAM_NUM)  ;
    cor_y <=  adr-X_BLOCK_WD*(adr/X_BLOCK_WD)+Y_BLOCK_WD*ram_index/(X_RAM_NUM*Z_RAM_NUM)  ;
    cor_z <=  ram_index / (X_RAM_NUM*Y_RAM_NUM)                                           ;
  end else begin
    cor_x <=  'h0     ;
    cor_y <=  'h0     ;
    cor_z <=  'h0     ;
  end
end

endmodule
