//根据上位机�?�来的节点的坐标、状态信息，生成地址信息
module  cost_ctrl #(
  parameter     X_RAM_NUM             =     10  ,
  parameter     Y_RAM_NUM             =     10  ,
  parameter     Z_RAM_NUM             =     7   , 
  parameter     RAM_NUM               =     700 , 
  parameter     X_BLOCK_WD            =     18  ,
  parameter     Y_BLOCK_WD            =     19  ,
  parameter     ADR_DW                =     10  ,
  parameter     DIMENSION             =     6   ,
  parameter     X_DW                  =     3   ,
  parameter     Y_DW                  =     3   ,
  parameter     Z_DW                  =     3   ,
  parameter     STATE_DW              =     2   ,
  parameter     G_DW                  =     5   ,  
  parameter     F_DW                  =     6                        
)(
   
  //cost_cache control        
  output     [ADR_DW-1:0]                             per_node_adr        ,
  output     [RAM_NUM-1:0]                            per_node_adr_sel    ,  
  output     [F_DW+G_DW+STATE_DW-1:0]                 per_node_f_g_s      ,
  input      [DIMENSION*F_DW-1:0]                     per_f_val           ,
  input      [DIMENSION*G_DW-1:0]                     per_g_val           ,  
  input  [DIMENSION*(X_DW+Y_DW+Z_DW+STATE_DW)-1:0]    per_node_din        ,  
  input                                               per_node_din_vld    ,
  input                                               clk                 ,
  input                                               reset
);

wire       [DIMENSION*X_DW-1:0]           per_x             ; //perphery 
wire       [DIMENSION*Y_DW-1:0]           per_y             ;  
wire       [DIMENSION*Z_DW-1:0]           per_z             ;
reg        [DIMENSION*STATE_DW-1:0]       per_state         ;


wire       [DIMENSION*RAM_NUM-1:0]        f_ram_sel         ;
wire                                      f_ram_sel_vld     ;
wire       [DIMENSION*ADR_DW-1:0]         f_ram_adr         ;


reg        [3:0]                          shift_cnt         ;          // 计数器，跟踪已输出的数据数量

assign  per_node_adr        = |shift_cnt? f_ram_adr[(shift_cnt-1)*ADR_DW +:ADR_DW]   : 'h0  ;
assign  per_node_adr_sel    = |shift_cnt? f_ram_sel[(shift_cnt-1)*RAM_NUM +:RAM_NUM] : 'h0  ;
assign  per_node_f_g_s      = |shift_cnt? {per_f_val[(shift_cnt-1)*F_DW +:F_DW],per_g_val[(shift_cnt-1)*G_DW +:G_DW],per_state[(shift_cnt-1)*STATE_DW +:STATE_DW]} : 'h0  ;

always @(posedge clk ) begin
  if(reset)
    shift_cnt <=  'h0         ;
  else if(f_ram_sel_vld)
    shift_cnt <=  DIMENSION   ;    
  else if(|shift_cnt )
    shift_cnt <= shift_cnt-1  ;
end


genvar  i;
generate
  for(i=0;i<DIMENSION;i=i+1)  begin
    assign  per_x[i*X_DW +:X_DW]              =   per_node_din[i*(X_DW+Y_DW+Z_DW+STATE_DW) + Y_DW+Z_DW+STATE_DW +:X_DW     ] ;
    assign  per_y[i*Y_DW +:Y_DW]              =   per_node_din[i*(X_DW+Y_DW+Z_DW+STATE_DW) +      Z_DW+STATE_DW +:Y_DW     ] ;
    assign  per_z[i*Z_DW +:Z_DW]              =   per_node_din[i*(X_DW+Y_DW+Z_DW+STATE_DW) +           STATE_DW +:Z_DW     ] ;
      
    always @(posedge clk ) begin
      if(reset)
        per_state[i*STATE_DW +:STATE_DW] <=  'h0   ;
      else 
        per_state[i*STATE_DW +:STATE_DW]  =   per_node_din[i*(X_DW+Y_DW+Z_DW+STATE_DW) +:STATE_DW ] ;
    end
    cor_to_adr#(
        .X_RAM_NUM      ( X_RAM_NUM ),
        .Y_RAM_NUM      ( Y_RAM_NUM ),
        .Z_RAM_NUM      ( Z_RAM_NUM ),
        .ADR_DW         ( ADR_DW    ),
        .X_BLOCK_WD     ( X_BLOCK_WD),
        .Y_BLOCK_WD     ( Y_BLOCK_WD),
        .Y_DW           ( Y_DW      ),
        .X_DW           ( X_DW      ),
        .Z_DW           ( Z_DW      )
    )u_cor_to_adr(
        .f_ram_adr      ( f_ram_adr[i*ADR_DW +: ADR_DW]             ),
        .f_ram_sel      ( f_ram_sel[i*RAM_NUM +: RAM_NUM]             ),
        .per_x          ( per_x[i*X_DW +:X_DW]  ),
        .per_y          ( per_y[i*Y_DW +:Y_DW]  ),
        .per_z          ( per_z[i*Z_DW +:Z_DW]  ),
        .din_vld        ( per_node_din_vld      ),
        .clk            ( clk                   ),
        .reset          ( reset                 )
    );
  end
endgenerate



dly_cell#(
    .DW    ( 1 ),
    .DLY   ( 1 )
)u_f_ram_ctrl_vld_dly_cell(
    .dout  ( f_ram_sel_vld      ),
    .din   ( per_node_din_vld   ),
    .clk   ( clk                ),
    .reset ( reset              )
);



endmodule
