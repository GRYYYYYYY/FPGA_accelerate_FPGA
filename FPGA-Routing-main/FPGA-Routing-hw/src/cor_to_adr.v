module cor_to_adr #(
  parameter     X_RAM_NUM             =     10            ,
  parameter     Y_RAM_NUM             =     10            ,
  parameter     Z_RAM_NUM             =     7             , 
  parameter     RAM_NUM               =     700           , 
  parameter     ADR_DW                =     9             ,
  parameter     X_BLOCK_WD            =     18            ,
  parameter     Y_BLOCK_WD            =     19            ,
  parameter     Z_BLOCK_WD            =     1             ,
  parameter     Y_DW                  =     8             ,
  parameter     X_DW                  =     8             ,
  parameter     Z_DW                  =     3             
)(
  output reg    [ADR_DW-1:0]    f_ram_adr         ,
  output reg    [RAM_NUM-1:0]   f_ram_sel         , 
  input         [X_DW-1:0]      per_x             , //perphery 
  input         [Y_DW-1:0]      per_y             ,  
  input         [Z_DW-1:0]      per_z             ,  
  input                         din_vld           ,
  input                         clk               ,
  input                         reset
);


wire                        din_vld_dly       ;
reg [$clog2(X_RAM_NUM) -1:0] x_f_ram_sel_cnt   ;
reg [$clog2(Y_RAM_NUM) -1:0] y_f_ram_sel_cnt   ;
reg [$clog2(Z_RAM_NUM) -1:0] z_f_ram_sel_cnt   ;
reg    [ADR_DW-1:0]         x_f_ram_adr       ;
reg    [ADR_DW-1:0]         y_f_ram_adr       ;

always @(posedge clk ) begin
  if(reset) begin
    x_f_ram_sel_cnt <=  'h0 ;
    y_f_ram_sel_cnt <=  'h0 ;    
    z_f_ram_sel_cnt <=  'h0 ;
  end else if(din_vld) begin
    x_f_ram_sel_cnt <=  per_x / X_BLOCK_WD  ;
    y_f_ram_sel_cnt <=  per_y / Y_BLOCK_WD  ;
    z_f_ram_sel_cnt <=  per_z / Z_BLOCK_WD  ;
  end
end

always @(posedge clk ) begin
  if(reset) begin
    f_ram_sel <=  'h0 ;
  end else if(din_vld_dly) begin
    f_ram_sel[x_f_ram_sel_cnt*y_f_ram_sel_cnt*z_f_ram_sel_cnt] <=  1'b1  ;
  end
end


always @(posedge clk ) begin
  if(reset) begin
    x_f_ram_adr <=  'h0 ; // 默认�????有位都为0
    y_f_ram_adr <=  'h0 ;
  end else if(din_vld)  begin
    x_f_ram_adr <= per_x-(per_x/X_BLOCK_WD)*X_BLOCK_WD ; 
    y_f_ram_adr <= per_y-(per_y/Y_BLOCK_WD)*Y_BLOCK_WD ; 
  end
end

always @(posedge clk ) begin
  if(reset) 
    f_ram_adr <=  'h0 ; 
  else if(din_vld)  
    f_ram_adr <= x_f_ram_adr + y_f_ram_adr*Y_BLOCK_WD ; 
end


dly_cell#(
    .DW    ( 1 ),
    .DLY   (1  )
)u_dly_cell(
    .dout  ( din_vld_dly  ),
    .din   ( din_vld   ),
    .clk   ( clk   ),
    .reset  ( reset  )
);


endmodule
