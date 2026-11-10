module  f_ram_ctrl #(
    parameter     DIMENSION  =     6   ,
    parameter     X_RAM_NUM  =     10  ,
    parameter     Y_RAM_NUM  =     10  ,
    parameter     Z_RAM_NUM  =     7   , 
    parameter     RAM_NUM    =  X_RAM_NUM*Y_RAM_NUM*Z_RAM_NUM    ,   
    parameter     ADR_DW     =     10  ,
    parameter     F_RAM_DW   =     32  ,
    parameter     STATE_DW   =     2   ,
    parameter     G_DW       =     5   ,
    parameter     F_DW       =     6             
)(
  input     [ADR_DW-1:0]                   per_node_adr         ,
  input     [RAM_NUM-1:0]                  per_node_adr_sel     ,

  input     [F_DW+G_DW+STATE_DW-1:0]       per_node_f_g_s       ,

  input [RAM_NUM-1:0]                      cen_node_wr_en       ,
  input                                    cen_node_adr_vld     ,
  input  [ADR_DW-1:0]                      cen_node_adr         ,
  input  [F_DW-1:0]                        cen_node_f_value     ,
  input  [G_DW-1:0]                        cen_node_g_value     , 
    
  output    [RAM_NUM*ADR_DW-1:0]           min_f_adr            ,
  output    [RAM_NUM*F_DW-1:0]             min_f_value          ,
  output    [RAM_NUM*G_DW-1:0]             min_g_value          ,
  output                                   min_valid            ,
  
  input                                    clk                  ,
  input                                    reset
);

// 内部连线
wire  [F_RAM_DW-1:0]               f_ram_din            ;  
wire  [ADR_DW-1:0]                 f_ram_wr_adr         ;
wire  [RAM_NUM-1:0]                f_ram_wr_en          ;
wire  [RAM_NUM*F_RAM_DW-1:0]       f_ram_dout           ;  
wire  [RAM_NUM*ADR_DW-1:0]         f_ram_rd_adr         ;
wire  [RAM_NUM-1:0]                f_ram_rd_en          ;


wire                               f_ram_update_done    ;

wire  [RAM_NUM*ADR_DW-1:0]         f_ram_min_search_rd_adr          ;
wire  [RAM_NUM-1:0]                f_ram_min_search_rd_en           ;
wire  [RAM_NUM*ADR_DW-1:0]         f_ram_update_rd_adr              ;
wire  [RAM_NUM-1:0]                f_ram_update_rd_en               ;

reg                                f_min_search_flag                ;
reg [RAM_NUM-1:0]                  min_f_valid_reg                  ;
wire  [RAM_NUM-1:0]                min_f_valid                      ;

//更新RAM中的中心点的情况

assign  {f_ram_rd_adr,f_ram_rd_en}  = f_min_search_flag ? {f_ram_min_search_rd_adr,f_ram_min_search_rd_en}
                                                        : {f_ram_update_rd_adr,f_ram_update_rd_en }       ;

assign  min_valid = &min_f_valid_reg    ;



always @(posedge clk ) begin
  if(reset)
    f_min_search_flag <=  0 ;
  else if(f_ram_update_done)
    f_min_search_flag <=  1 ;    
  else if(&min_f_valid_reg)
    f_min_search_flag <=  0 ;    
end

f_ram_update#(
    .DIMENSION    ( DIMENSION ),
    .RAM_NUM      ( RAM_NUM   ),
    .ADR_DW       ( ADR_DW    ),
    .F_RAM_DW     ( F_RAM_DW  ),
    .STATE_DW     ( STATE_DW  ),
    .G_DW         ( G_DW      ),
    .F_DW         ( F_DW      )
)u_f_ram_update(
    .f_ram_din          ( f_ram_din          ),
    .f_ram_wr_adr       ( f_ram_wr_adr       ),
    .f_ram_wr_en        ( f_ram_wr_en        ),
    .f_ram_dout         ( f_ram_dout         ),
    .f_ram_rd_adr       ( f_ram_update_rd_adr),
    .f_ram_rd_en        ( f_ram_update_rd_en ),
    .f_ram_update_done  ( f_ram_update_done  ),
    .per_node_adr       ( per_node_adr       ),
    .per_node_adr_sel   ( per_node_adr_sel   ),
    .per_node_f_g_s     ( per_node_f_g_s     ),
    .cen_node_wr_en     ( cen_node_wr_en     ),
    .cen_node_adr_vld   ( cen_node_adr_vld   ),
    .cen_node_adr       ( cen_node_adr       ),
    .cen_node_f_value   ( cen_node_f_value   ),
    .cen_node_g_value   ( cen_node_g_value   ),
    .clk                ( clk                ),
    .reset              ( reset              )
);

genvar  i;
generate 
  for(i=0;i<RAM_NUM;i=i+1)  begin
    always @(posedge clk ) begin
      if(reset)
        min_f_valid_reg[i] <=  'h0 ;
      else if(min_f_valid[i])
        min_f_valid_reg[i] <=  1 ;
      else if(&min_f_valid_reg)
        min_f_valid_reg[i] <=  'h0 ;        
    end

    f_min_search#(
        .ADR_DW             ( ADR_DW      ),
        .DIMENSION          ( DIMENSION   ),
        .F_RAM_DW           ( F_RAM_DW    ),
        .STATE_DW           ( STATE_DW    ),
        .G_DW               ( G_DW        ),
        .F_DW               ( F_DW        )
    )u_f_min_search(
        .f_ram_wr_en        ( f_ram_wr_en[i]                              ),
        .f_ram_wr_adr       ( f_ram_wr_adr                                ),
        .f_ram_dout         ( f_ram_dout[i*F_RAM_DW +:F_RAM_DW]             ),
        .f_ram_rd_adr       ( f_ram_min_search_rd_adr[i*ADR_DW +:ADR_DW]  ),
        .f_ram_rd_en        ( f_ram_min_search_rd_en[i]                   ),
        .f_ram_update_done  ( f_ram_update_done                           ),
        .min_f_adr          ( min_f_adr[i*ADR_DW +:ADR_DW]                ),
        .min_f_value        ( min_f_value[i*F_DW +:F_DW]                  ),
        .min_g_value        ( min_g_value[i*G_DW +:G_DW]                  ),        
        .min_f_valid        ( min_f_valid[i]                              ),
        .clk                ( clk                                         ),
        .reset              ( reset                                       )
    );
  end
endgenerate



cost_cache#(
    .RAM_NUM ( RAM_NUM ),
    .F_RAM_DW ( F_RAM_DW ),
    .ADR_DW  ( ADR_DW  ),
    .F_DW    ( F_DW    )
)u_cost_cache(
    .dout    ( f_ram_dout     ),
    .rd_adr  ( f_ram_rd_adr   ),
    .rd_en   ( f_ram_rd_en    ),
    .din     ( f_ram_din      ),
    .wr_adr  ( f_ram_wr_adr   ),
    .wr_en   ( f_ram_wr_en    ),
    .clk     ( clk            ),
    .reset   ( reset          )
);

endmodule
