`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 2025/03/28 20:41:49
// Design Name: 
// Module Name: cost_cache
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


module cost_cache #(
  parameter     RAM_NUM               =     7        ,
  parameter     F_RAM_DW              =     32       ,
  parameter     ADR_DW                =     10       ,
  parameter     F_DW                  =     10       
)(
  output[RAM_NUM*F_RAM_DW-1:0]    dout                ,  
  input [RAM_NUM*ADR_DW-1:0]      rd_adr              ,
  input [RAM_NUM       -1:0]      rd_en               ,

  input [F_RAM_DW-1:0]            din                 ,  

  input [ADR_DW-1:0]              wr_adr              ,
  input [RAM_NUM       -1:0]      wr_en               ,
  input                           clk                 ,
  input                           reset
);

genvar  i;
generate
  for(i=0;i<RAM_NUM;i=i+1)  begin
    bram_w32_d1024 u_bram_w32_d1024 (
      .clka (clk),                                // input wire clka - 连接到模块的时钟输入
      .wea  (wr_en[i]),                           // input wire [0 : 0] wea - 连接到对应RAM的写使能
      .addra(wr_adr),    // input wire [9 : 0] addra - 连接到对应RAM的写地址
      .dina (din),     // input wire [31 : 0] dina - 连接到对应RAM的写数据
      .clkb (clk),                                // input wire clkb - 连接到模块的时钟输入
      .enb  (rd_en[i]),                           // input wire enb - 连接到对应RAM的读使能
      .addrb(rd_adr[i*ADR_DW+:ADR_DW]),    // input wire [9 : 0] addrb - 连接到对应RAM的读地址
      .doutb(dout[i*F_RAM_DW+:F_RAM_DW])     // output wire [31 : 0] doutb - 连接到对应RAM的读数据输出
    );
  end
endgenerate

endmodule
