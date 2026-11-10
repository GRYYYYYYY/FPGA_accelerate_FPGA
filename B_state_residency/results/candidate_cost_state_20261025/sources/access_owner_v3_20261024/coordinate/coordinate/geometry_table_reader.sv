`timescale 1ns/1ps
// Immutable row [SLR,north] and column [next,prev] pairs, 8 bytes each.
module geometry_table_reader(
 input wire clk,rst,
 input wire cfg_valid,output wire cfg_ready,input wire [63:0]cfg_rows_base,cfg_columns_base,
 input wire [31:0]cfg_rows,cfg_columns,
 output reg cfg_rsp_valid,input wire cfg_rsp_ready,output reg [2:0]cfg_status,output reg configured,
 input wire req_valid,output wire req_ready,input wire req_op,input wire [31:0]req_index,req_cookie,
 output wire rsp_valid,input wire rsp_ready,output reg [3:0]rsp_status,
 output reg rsp_op,output reg [31:0]rsp_index,rsp_cookie,rsp_a,rsp_b,output wire fault,
 output reg [63:0]m_araddr,output wire [7:0]m_arlen,output wire [2:0]m_arsize,
 output wire [1:0]m_arburst,output wire [3:0]m_arid,output wire m_arvalid,input wire m_arready,
 input wire [511:0]m_rdata,input wire [3:0]m_rid,input wire [1:0]m_rresp,input wire m_rlast,m_rvalid,output wire m_rready
);
 localparam [1:0]IDLE=0,ADDR=1,DATA=2,REPLY=3;
 reg [1:0]state;reg stopped;reg [63:0]rows_base,columns_base;reg [31:0]rows,columns;reg [2:0]lane;
 wire [64:0]rb=({33'b0,cfg_rows}*65'd8+65'd63)&~65'd63;
 wire [64:0]cb=({33'b0,cfg_columns}*65'd8+65'd63)&~65'd63;
 wire [64:0]rl={1'b0,cfg_rows_base}+rb-1'b1,cl={1'b0,cfg_columns_base}+(cb==0?65'd1:cb)-1'b1;
 wire overlap=cb!=0&&cfg_rows_base<=cl[63:0]&&cfg_columns_base<=rl[63:0];
 wire unexpected=m_rvalid&&state!=DATA&&!(state==ADDR&&m_arready);
 assign fault=!rst&&(stopped||unexpected);
 assign cfg_ready=!rst&&!fault&&!configured&&!cfg_rsp_valid&&state==IDLE;
 assign req_ready=!rst&&!fault&&!cfg_rsp_valid&&state==IDLE&&!(cfg_valid&&cfg_ready);
 assign rsp_valid=!rst&&state==REPLY;
 assign m_arvalid=!rst&&!fault&&state==ADDR;
 assign m_rready=!rst&&!fault&&state==DATA;
 assign m_arlen=0;assign m_arsize=6;assign m_arburst=1;assign m_arid=0;
 wire [63:0]pair_data=m_rdata[lane*64+:64];
 always @(posedge clk)begin
  if(rst)begin
   state<=IDLE;stopped<=0;rows_base<=0;columns_base<=0;rows<=0;columns<=0;lane<=0;
   cfg_rsp_valid<=0;cfg_status<=0;configured<=0;m_araddr<=0;
   rsp_status<=0;rsp_op<=0;rsp_index<=0;rsp_cookie<=0;rsp_a<=0;rsp_b<=0;
  end else begin
   if(cfg_rsp_valid&&cfg_rsp_ready)cfg_rsp_valid<=0;
   if(state==REPLY&&rsp_ready)state<=IDLE;
   if(!stopped&&unexpected)begin
    stopped<=1;if(state!=IDLE&&state!=REPLY)begin rsp_status<=5;state<=REPLY;end
   end else if(!stopped)begin
    if(cfg_valid&&cfg_ready)begin
     cfg_rsp_valid<=1;cfg_status<=0;
     if(cfg_rows_base[5:0]!=0||cfg_columns_base[5:0]!=0)cfg_status<=1;
     else if(cfg_rows==0||cfg_rows>65536||cfg_columns>65536||rl[64]||cl[64])cfg_status<=2;
     else if(overlap)cfg_status<=3;
     else begin configured<=1;rows_base<=cfg_rows_base;columns_base<=cfg_columns_base;rows<=cfg_rows;columns<=cfg_columns;end
    end
    case(state)
     IDLE:if(req_valid&&req_ready)begin
      rsp_op<=req_op;rsp_index<=req_index;rsp_cookie<=req_cookie;rsp_a<=0;rsp_b<=0;rsp_status<=0;
      if(!configured)begin rsp_status<=1;state<=REPLY;end
      else if(req_index>=(req_op?columns:rows))begin rsp_status<=2;state<=REPLY;end
      else begin lane<=req_index[2:0];m_araddr<=(req_op?columns_base:rows_base)+({32'b0,req_index[31:3],3'b0}<<3);state<=ADDR;end
     end
     ADDR:if(m_arvalid&&m_arready)state<=DATA;
     DATA:if(m_rvalid&&m_rready)begin
      state<=REPLY;
      if(m_rid!=0||m_rresp!=0||!m_rlast)begin rsp_status<=3;stopped<=1;end
      else if(!rsp_op&&pair_data[63:32]>1)begin rsp_status<=4;stopped<=1;end
      else begin rsp_a<=pair_data[31:0];rsp_b<=pair_data[63:32];end
     end
     default:begin end
    endcase
   end
  end
 end
endmodule
