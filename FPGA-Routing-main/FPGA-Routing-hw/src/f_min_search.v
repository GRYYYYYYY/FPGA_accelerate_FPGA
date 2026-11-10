`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 2025/04/02 18:40:41
// Design Name: 
// Module Name: f_min_search
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


module f_min_search #(
  parameter     ADR_DW                =     10            ,
  parameter     DIMENSION             =     6             ,
  parameter     F_RAM_DW              =     32            ,
  parameter     STATE_DW              =     2             ,
  parameter     G_DW                  =     11            ,
  parameter     F_DW                  =     6              
)(
  input                                    f_ram_wr_en          ,
  input       [ADR_DW-1:0]                 f_ram_wr_adr         ,
  
  input       [F_RAM_DW-1:0]               f_ram_dout           ,  
  output reg  [ADR_DW-1:0]                 f_ram_rd_adr         ,
  output reg                               f_ram_rd_en          ,

  input                                    f_ram_update_done    ,
  
  output reg  [ADR_DW-1:0]                 min_f_adr            ,
  output reg  [F_DW-1:0]                   min_f_value          ,
  output reg  [G_DW-1:0]                   min_g_value          ,
  output reg                               min_f_valid          ,
  
  input                                    clk                  ,
  input                                    reset
);

// 状态定义
localparam IDLE       = 2'b00     ;  
localparam F_RD       = 2'b01     ;  
localparam STATE_DLY  = 2'b10     ;
localparam UPDATE     = 2'b11     ;  

// 寄存器定义
reg [1:0]             state               ;
reg [ADR_DW-1:0]      min_adr             ; // 记录最小地址
reg [ADR_DW-1:0]      max_adr             ; // 记录最大地址
reg [ADR_DW-1:0]      curr_adr            ; // 当前搜索地址
reg                   adr_valid           ; // 地址有效标志
reg [F_DW-1:0]        curr_f_value        ; // 当前F值
wire [F_DW-1:0]        f_ram_dout_cost     ; // RAM读出的F值
wire [G_DW-1:0]        f_ram_dout_g        ;
wire [STATE_DW-1:0]    f_ram_dout_state    ;

reg                   adr_vld_1st         ;

assign  f_ram_dout_cost   = f_ram_dout[F_DW+G_DW+STATE_DW-1 -:F_DW];
assign  f_ram_dout_g      = f_ram_dout[G_DW+STATE_DW-1 -:G_DW];
assign  f_ram_dout_state  = f_ram_dout[ STATE_DW-1 -:STATE_DW];

// 记录最小和最大地址
always @(posedge clk) begin
  if(reset) begin
    min_adr   <= {ADR_DW{1'b1}}; // 初始化为最大值
    max_adr   <= 'h0;           // 初始化为最小值
    adr_vld_1st <= 1'b0;
  end else if(f_ram_wr_en) begin
    if(!adr_vld_1st) begin
      min_adr   <= f_ram_wr_adr;
      max_adr   <= f_ram_wr_adr;
      adr_vld_1st <= 1'b1;
    end else begin
      if(f_ram_wr_adr < min_adr)
        min_adr <= f_ram_wr_adr;
      if(f_ram_wr_adr > max_adr)
        max_adr <= f_ram_wr_adr;
    end
  end
end

// 状态机控制
always @(posedge clk) begin
  if(reset) begin
    state           <= IDLE;
    curr_adr        <= 'h0;
    min_f_adr       <= 'h0;
    min_f_value     <= {F_DW{1'b1}}; // 初始化为最大值
    min_g_value     <= {G_DW{1'b1}}; 
    min_f_valid     <= 1'b0;
    f_ram_rd_en     <= 1'b0;
    f_ram_rd_adr    <= 'h0;
    curr_f_value    <= 'h0;
  end else begin
    case(state)
      IDLE: begin
        min_f_valid  <= 1'b0;
        if(f_ram_update_done) begin
          state        <= F_RD;
          curr_adr     <= min_adr;
          min_f_value  <= {F_DW{1'b1}}; // 重置为最大值
          min_g_value  <= {G_DW{1'b1}}; // 重置为最大值
        end
      end
      
      F_RD: begin
        // 发起RAM读请求
        f_ram_rd_en  <= 1'b1;
        f_ram_rd_adr <= curr_adr;
        state <= STATE_DLY;
      end

      STATE_DLY: begin
        f_ram_rd_en <= 1'b0;
        state <= UPDATE;
      end

      UPDATE: begin
        // 比较F值，更新最小值
        if(f_ram_dout_cost < min_f_value && f_ram_dout_state==2'b01) begin
          min_f_value   <= f_ram_dout_cost;
          min_g_value   <= f_ram_dout_g   ;
          if(min_adr==max_adr)
            min_f_adr <=  min_adr ;
          else
            min_f_adr     <= curr_adr-1;
        end
        
        // 决定下一步操作
        if(curr_adr == max_adr) begin
          // 所有地址都已检查完毕
          state <= IDLE;
          min_f_valid <= 1'b1;
        end else begin
          // 检查下一个地址
          curr_adr <= curr_adr + 1'b1;
          state <= F_RD;
        end
      
      end
      
      default: state <= IDLE;
    endcase
  end
end

endmodule
