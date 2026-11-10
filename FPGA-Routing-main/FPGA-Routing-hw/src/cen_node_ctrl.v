module  cen_node_ctrl #(
  parameter   X_BLOCK_WD =     18  ,
  parameter   Y_BLOCK_WD =     19  ,
  parameter   X_RAM_NUM  =     10  ,
  parameter   Y_RAM_NUM  =     10  ,
  parameter   Z_RAM_NUM  =     7   , 
  parameter   ADR_DW     =     10  ,  
  parameter   X_DW       =     8   ,
  parameter   Y_DW       =     8   ,
  parameter   Z_DW       =     3   ,
  parameter   RAM_NUM    =     700 , 
  parameter   G_DW       =     11  ,
  parameter   F_DW       =     11  
)
(
  output  reg [$clog2(RAM_NUM)-1:0]                 cen_node_ram_index  ,  
  output  reg [RAM_NUM-1:0]                         cen_node_wr_en      ,
  output  reg                                       cen_node_adr_vld    ,
  output  reg  [ADR_DW-1:0]                         cen_node_adr        ,
  output  reg  [G_DW-1:0]                           cen_node_g_val      ,
  output  reg  [F_DW-1:0]                           cen_node_f_val      , 
  output       [X_DW-1:0]                           cen_node_x          ,
  output       [Y_DW-1:0]                           cen_node_y          ,
  output       [Z_DW-1:0]                           cen_node_z          ,   

  input        [RAM_NUM*ADR_DW-1:0]                 min_f_adr           ,
  input        [RAM_NUM*F_DW-1:0]                   min_f_value         ,
  input        [RAM_NUM*F_DW-1:0]                   min_g_value         ,
  input                                             min_f_valid         ,

  input                                             clk                 ,
  input                                             reset  
);

// 状�?�定�?
localparam IDLE       = 2'b00;
localparam COMPARE    = 2'b01;
localparam OUTPUT     = 2'b10;

// 寄存器定�?
reg [1:0]             state;
reg [31:0]             compare_cnt;  // 计数器，用于依次比较

reg [ADR_DW-1:0]      min_adr;

wire  [F_DW-1:0]  debug_min_f ;
assign  debug_min_f= min_f_value[compare_cnt*F_DW +: F_DW];

// 比较逻辑
always @(posedge clk) begin
  if (reset) begin
    state <= IDLE;
    compare_cnt <= 0;
    cen_node_f_val <= {F_DW{1'b1}}; // 初始化为�?大�??
    min_adr <= 0;
    cen_node_adr <= 0;
    cen_node_adr_vld <= 0;
    cen_node_g_val <= 0;
    cen_node_ram_index<=0  ;
    cen_node_wr_en<='h0 ;
  end else begin
    // 默认清除输出有效信号
    cen_node_adr_vld <= 0;
    case (state)
      IDLE: begin
        // 当所有min_f_valid都为1时，�?始比�?
        cen_node_wr_en  <=    1   ;
        cen_node_ram_index       <=    0   ;
        if (min_f_valid) begin
          state <= COMPARE;
          compare_cnt <= 0;
          cen_node_f_val <= {F_DW{1'b1}}; // 重置为最大�??
          min_adr <= 0;
        end
      end
      
      COMPARE: begin
        // 使用计数器依次比较每个RAM的�??
        if (min_f_value[compare_cnt*F_DW +: F_DW] < cen_node_f_val) begin
          cen_node_f_val      <= min_f_value[compare_cnt*F_DW +: F_DW]   ;
          cen_node_wr_en <= cen_node_wr_en << 1                     ;
          min_adr        <= min_f_adr[compare_cnt*ADR_DW +: ADR_DW] ;
          cen_node_ram_index      <= compare_cnt                             ;
        end
        
        // 增加计数�?
        compare_cnt <= compare_cnt + 1;
        
        // 如果已经比较完所有RAM，进入输出状�?
        if (compare_cnt == RAM_NUM - 1) begin
          state <= OUTPUT;
        end
      end
      
      OUTPUT: begin
        // 输出找到的最小�?�对应的地址和�??
        cen_node_adr <= min_adr;
        cen_node_g_val <= min_g_value[(cen_node_ram_index-1)*G_DW +:G_DW];
        cen_node_adr_vld <= 1;
        
        // 返回空闲状�?�，等待下一次比�?
        state <= IDLE;
      end
      
      default: state <= IDLE;
    endcase
  end
end

adr_to_cor#(
    .RAM_NUM       ( RAM_NUM   ),
    .X_BLOCK_WD    ( X_BLOCK_WD),
    .Y_BLOCK_WD    ( Y_BLOCK_WD),
    .X_RAM_NUM     ( X_RAM_NUM ),
    .Y_RAM_NUM     ( Y_RAM_NUM ),
    .Z_RAM_NUM     ( Z_RAM_NUM ),
    .ADR_DW        ( ADR_DW    ),
    .X_DW          ( X_DW      ),
    .Y_DW          ( Y_DW      ),
    .Z_DW          ( Z_DW      )
)u_adr_to_cor(
    .cor_x        ( cen_node_x),
    .cor_y        ( cen_node_y),
    .cor_z        ( cen_node_z),
    .ram_index    ( ram_index ),
    .adr          ( adr       ),
    .adr_vld      ( adr_vld   ),
    .clk          ( clk       ),
    .reset        ( reset     )
);


endmodule
