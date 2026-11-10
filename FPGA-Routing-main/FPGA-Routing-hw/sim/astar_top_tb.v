`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// 测试台文件：astar_top_tb.v
// 功能：为astar_top模块创建测试环境，设�????10*10*10的三维节点坐标系
//////////////////////////////////////////////////////////////////////////////////

module astar_top_tb();

  parameter     DIMENSION       =     6  ;
  parameter     BLOCK_WD        =     77 ;  //每个ram对应的行元素个数
  parameter     RAM_NUM         =     56 ;
  parameter     ADR_DW          =     10 ;
  parameter     X_DW            =     6  ;
  parameter     Y_DW            =     7  ;
  parameter     Z_DW            =     4  ;
  parameter     F_DW            =     11  ;
  parameter     G_DW            =     11  ;
  parameter     H_DW            =     11  ;
  parameter     F_RAM_DW        =    32  ;  //F_DW + G_DW + state 
  parameter     STATE_DW        =     2  ;
  parameter     STEP_OBL_COST   =     14 ;
  parameter     STEP_LINE_COST  =     10 ; 
  
  // 定义起点和终点坐�????
  parameter     START_X         =     1   ;
  parameter     START_Y         =     1   ;
  parameter     START_Z         =     1   ;
  parameter     END_X           =     8   ;
  parameter     END_Y           =     8   ;
  parameter     END_Z           =     8   ;
  
  // 状�?�定�????
  parameter     EMPTY           =     0   ; // 空节�????
  parameter     OBSTACLE        =     1   ; // 障碍�????
  parameter     START           =     2   ; // 起点
  parameter     TARGET          =     3   ; // 终点

  // 时钟和复位信�????
  reg                               clk                ;
  reg                               reset              ;
  
  // DUT接口信号
  wire [  7       : 0]              cen_node_ram_index ;
  wire [ ADR_DW-1 : 0]              cen_node_adr       ;
  wire                              cen_node_adr_vld   ;

  // reg  [DIMENSION*X_DW-1:0]      per_x      ;
  // reg  [DIMENSION*Y_DW-1:0]      per_y      ;
  // reg  [DIMENSION*Z_DW-1:0]      per_z      ;
  reg                               start              ;
  reg  [ X_DW-1 : 0]                per_x1             ;
  reg  [ Y_DW-1 : 0]                per_y1             ;
  reg  [ Z_DW-1 : 0]                per_z1             ;
  reg  [ X_DW-1 : 0]                per_x2             ;
  reg  [ Y_DW-1 : 0]                per_y2             ;
  reg  [ Z_DW-1 : 0]                per_z2             ;
  reg  [ X_DW-1 : 0]                per_x3             ;
  reg  [ Y_DW-1 : 0]                per_y3             ;
  reg  [ Z_DW-1 : 0]                per_z3             ;
  reg  [ X_DW-1 : 0]                per_x4             ;
  reg  [ Y_DW-1 : 0]                per_y4             ;
  reg  [ Z_DW-1 : 0]                per_z4             ;
  reg  [ X_DW-1 : 0]                per_x5             ;
  reg  [ Y_DW-1 : 0]                per_y5             ;
  reg  [ Z_DW-1 : 0]                per_z5             ;
  reg  [ X_DW-1 : 0]                per_x6             ;
  reg  [ Y_DW-1 : 0]                per_y6             ;
  reg  [ Z_DW-1 : 0]                per_z6             ;


  reg  [DIMENSION*STATE_DW-1:0]     per_state          ;
  reg                               per_node_din_vld   ;


  wire [ X_DW-1 : 0]                cen_node_x         ;
  wire [ Y_DW-1 : 0]                cen_node_y         ;
  wire [ Z_DW-1 : 0]                cen_node_z         ;

  assign  cen_node_x = cen_node_adr_vld ? cen_node_ram_index : 'h0                  ;               
  assign  cen_node_y = cen_node_adr_vld ? cen_node_adr- (cen_node_adr/10)*10 : 'h0  ;
  assign  cen_node_z = cen_node_adr_vld ? cen_node_adr/10                    : 'h0  ;
  
  // 用于测试的临时变�????
  integer i;
  
  // 时钟生成，周期为10ns (100MHz)
  initial begin
    clk = 0;
    forever #5 clk = ~clk;
  end
  
  // 测试过程
  initial begin
    // 初始化信�????
    reset = 1;
    start = 0;
    // 复位几个时钟周期
    repeat(10) @(posedge clk);
    reset = 0;
    start = 1;
    repeat(1) @(posedge clk); 
    start = 0;       
    repeat(5) @(posedge clk);
    
  end

  always @(posedge clk ) begin
    if(reset) begin
      per_x1            <=  0               ;
      per_y1            <=  0               ;
      per_z1            <=  0               ;
      per_x2            <=  0               ;
      per_y2            <=  0               ;
      per_z2            <=  0               ;
      per_x3            <=  0               ;
      per_y3            <=  0               ;
      per_z3            <=  0               ;
      per_x4            <=  0               ;
      per_y4            <=  0               ;
      per_z4            <=  0               ;
      per_x5            <=  0               ;
      per_y5            <=  0               ;
      per_z5            <=  0               ;
      per_x6            <=  0               ;
      per_y6            <=  0               ;
      per_z6            <=  0               ;
      per_node_din_vld  <=  0               ;
    end else if(cen_node_adr_vld) begin 
      per_x1            <=  cen_node_x      ;//�???
      per_y1            <=  cen_node_y      ;
      per_z1            <=  cen_node_z+1    ;
      per_x2            <=  cen_node_x      ;//�???
      per_y2            <=  cen_node_y      ;
      per_z2            <=  cen_node_z-1    ;
      per_x3            <=  cen_node_x-1    ;//�???
      per_y3            <=  cen_node_y      ;
      per_z3            <=  cen_node_z      ;
      per_x4            <=  cen_node_x+1    ;//�???
      per_y4            <=  cen_node_y      ;
      per_z4            <=  cen_node_z      ;
      per_x5            <=  cen_node_x      ;//�???
      per_y5            <=  cen_node_y+1    ;
      per_z5            <=  cen_node_z      ;
      per_x6            <=  cen_node_x      ;//�???
      per_y6            <=  cen_node_y-1    ;
      per_z6            <=  cen_node_z      ;
      per_node_din_vld  <=  1               ;
    end else if(start) begin
      per_x1            <=  1               ;
      per_y1            <=  1               ;
      per_z1            <=  2               ;
      per_x2            <=  1               ;
      per_y2            <=  1               ;
      per_z2            <=  0               ;
      per_x3            <=  0               ;
      per_y3            <=  1               ;
      per_z3            <=  1               ;
      per_x4            <=  2               ;
      per_y4            <=  1               ;
      per_z4            <=  1               ;
      per_x5            <=  1               ;
      per_y5            <=  2               ;
      per_z5            <=  1               ;
      per_x6            <=  1               ;
      per_y6            <=  0               ;
      per_z6            <=  1               ;
      per_node_din_vld  <=  1               ;
    end else begin
      per_x1            <=  0               ;
      per_y1            <=  0               ;
      per_z1            <=  0               ;
      per_x2            <=  0               ;
      per_y2            <=  0               ;
      per_z2            <=  0               ;
      per_x3            <=  0               ;
      per_y3            <=  0               ;
      per_z3            <=  0               ;
      per_x4            <=  0               ;
      per_y4            <=  0               ;
      per_z4            <=  0               ;
      per_x5            <=  0               ;
      per_y5            <=  0               ;
      per_z5            <=  0               ;
      per_x6            <=  0               ;
      per_y6            <=  0               ;
      per_z6            <=  0               ;
      per_node_din_vld  <=  0               ;    
    end
  end

  // 实例化被测模�????
  astar_top #(
    .DIMENSION          ( DIMENSION                         ),
    .BLOCK_WD           ( BLOCK_WD                          ),
    .RAM_NUM            ( RAM_NUM                           ),
    .ADR_DW             ( ADR_DW                            ),
    .Y_DW               ( Y_DW                              ),
    .X_DW               ( X_DW                              ),
    .Z_DW               ( Z_DW                              ),
    .F_DW               ( F_DW                              ),
    .G_DW               ( G_DW                              ),
    .H_DW               ( H_DW                              ),
    .F_RAM_DW           ( F_RAM_DW                          ),
    .STATE_DW           ( STATE_DW                          ),
    .STEP_OBL_COST      ( STEP_OBL_COST                     ),
    .STEP_LINE_COST     ( STEP_LINE_COST                    )
  ) u_astar_top (
    .cen_node_ram_index ( cen_node_ram_index                          ),
    .cen_node_adr       ( cen_node_adr                                ),
    .cen_node_adr_vld   ( cen_node_adr_vld                            ),
    .per_x              ( {per_x1,per_x2,per_x3,per_x4,per_x5,per_x6} ),
    .per_y              ( {per_y1,per_y2,per_y3,per_y4,per_y5,per_y6} ),
    .per_z              ( {per_z1,per_z2,per_z3,per_z4,per_z5,per_z6} ),
    .end_x              (  8                                          ),
    .end_y              (  8                                          ),
    .end_z              (  8                                          ),
    .per_state          (  12'b010101010101                           ),
    .per_node_din_vld   ( per_node_din_vld                            ),
    .clk                ( clk                                         ),
    .reset              ( reset                                       )
  );

endmodule
