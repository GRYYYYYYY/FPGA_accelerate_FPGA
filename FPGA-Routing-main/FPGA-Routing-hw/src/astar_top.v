`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 2025/03/28 20:40:57
// Design Name: 
// Module Name: astar_top
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


module astar_top #(
  parameter     X_LEN           =      172                          ,
  parameter     Y_LEN           =      188                          ,  
  parameter     Z_LEN           =      7                            ,  
  parameter     DIMENSION       =      6                            ,
  parameter     X_RAM_NUM       =      10                           ,
  parameter     Y_RAM_NUM       =      10                           ,
  parameter     Z_RAM_NUM       =      7                            ,  
  parameter     STEP_X_COST     =      10                           ,
  parameter     STEP_Y_COST     =      10                           ,
  parameter     STEP_Z_COST     =      10                           ,
  parameter     RAM_NUM         =     X_RAM_NUM*Y_RAM_NUM*Z_RAM_NUM ,     
  parameter     X_BLOCK_WD      =     X_LEN/X_RAM_NUM+1             ,
  parameter     Y_BLOCK_WD      =     Y_LEN/Y_RAM_NUM+1             ,
  parameter     ADR_DW          =     $clog2(X_BLOCK_WD*Y_BLOCK_WD) ,
  parameter     X_DW            =      $clog2(X_LEN)                ,
  parameter     Y_DW            =      $clog2(Y_LEN)                ,
  parameter     Z_DW            =      $clog2(Z_LEN)                ,
  parameter     F_DW            =      11                           ,
  parameter     G_DW            =      11                           ,
  parameter     H_DW            =      11                           , 
  parameter     F_RAM_DW        =      32                           , 
  parameter     STATE_DW        =      2                            
                  

)(
  output [$clog2(RAM_NUM):0]       cen_node_ram_index ,
  output [ADR_DW-1:0]              cen_node_adr       ,
  output                           cen_node_adr_vld   ,
  input  [DIMENSION*X_DW-1:0]      per_x              , //perphery 
  input  [DIMENSION*Y_DW-1:0]      per_y              ,  
  input  [DIMENSION*Z_DW-1:0]      per_z              ,  
  input  [X_DW-1:0]                end_x              ,
  input  [Y_DW-1:0]                end_y              ,
  input  [Z_DW-1:0]                end_z              ,
  input  [DIMENSION*STATE_DW-1:0]  per_state          ,  
  input                            per_node_din_vld   ,
  input                            clk                ,
  input                            reset
);

  wire  [DIMENSION*F_DW-1:0]      per_f_val         ;
  wire  [DIMENSION*G_DW-1:0]      per_g_val         ;
  wire                            cost_vld          ;

  wire  [X_DW-1:0]                cer_x             ; //center
  wire  [Y_DW-1:0]                cer_y             ;
  wire  [Z_DW-1:0]                cer_z             ;


  wire  [ADR_DW-1:0]              per_node_adr       ;
  wire  [RAM_NUM-1:0]             per_node_adr_sel   ;    
  wire  [F_DW+G_DW+STATE_DW-1:0]  per_node_f_g_s     ;

  wire  [DIMENSION*(X_DW+Y_DW+Z_DW+STATE_DW)-1:0]    per_node_din ;

  wire  [RAM_NUM*ADR_DW-1:0]      min_f_adr        ;
  wire  [RAM_NUM*F_DW-1:0]        min_f_value      ;
  wire  [RAM_NUM*G_DW-1:0]        min_g_value      ;
  wire  [RAM_NUM-1:0]             min_f_valid      ;

  wire [RAM_NUM-1:0]              cen_node_wr_en   ;

  wire  [G_DW-1:0]                cen_node_g_val   ;
  wire  [F_DW-1:0]                cen_node_f_val   ; 

  genvar  i;
  generate
    for(i=0;i<DIMENSION;i=i+1)  begin
      assign  per_node_din[i*(X_DW+Y_DW+Z_DW+STATE_DW) +: (X_DW+Y_DW+Z_DW+STATE_DW)] =
      {per_x[i*X_DW +:X_DW] , per_y[i*Y_DW +:Y_DW] , per_z[i*Z_DW +:Z_DW] , per_state[i*STATE_DW +:STATE_DW]} ;
    end
  endgenerate

cost_calculator#(
    .DIMENSION      ( DIMENSION       ),
    .Y_DW           ( Y_DW            ),
    .X_DW           ( X_DW            ),
    .Z_DW           ( Z_DW            ),
    .H_DW           ( H_DW            ),
    .G_DW           ( G_DW            ),
    .F_DW           ( F_DW            ),
    .STEP_X_COST    ( STEP_X_COST     ),
    .STEP_Y_COST    ( STEP_Y_COST     ),
    .STEP_Z_COST    ( STEP_Z_COST     )
)u_cost_calculator(
    .f_val         ( per_f_val         ),
    .g_val         ( per_g_val         ),
    .cost_vld      ( cost_vld          ),
    .per_x         ( per_x             ),
    .per_y         ( per_y             ),
    .per_z         ( per_z             ),
    .end_x         ( end_x             ),
    .end_y         ( end_y             ),
    .end_z         ( end_z             ),
    .cen_x         ( cen_node_x        ),
    .cen_y         ( cen_node_y        ),
    .cen_z         ( cen_node_z        ),
    .cen_g_val     ( cen_node_g_val    ),
    .din_vld       ( per_node_din_vld  ),
    .clk           ( clk               ),
    .reset         ( reset             )
);


cost_ctrl#(
    .X_RAM_NUM                            ( X_RAM_NUM          ),
    .Y_RAM_NUM                            ( Y_RAM_NUM          ),
    .Z_RAM_NUM                            ( Z_RAM_NUM          ),
    .RAM_NUM                              ( RAM_NUM             ),
    .X_BLOCK_WD                           ( X_BLOCK_WD         ),
    .Y_BLOCK_WD                           ( Y_BLOCK_WD         ),
    .ADR_DW                               ( ADR_DW             ),
    .DIMENSION                            ( DIMENSION          ),
    .X_DW                                 ( X_DW               ),
    .Y_DW                                 ( Y_DW               ),
    .Z_DW                                 ( Z_DW               ),
    .STATE_DW                             ( STATE_DW           ),
    .G_DW                                 ( G_DW               ),
    .F_DW                                 ( F_DW               )
)u_cost_ctrl(
    .per_node_adr                         ( per_node_adr        ),
    .per_node_adr_sel                     ( per_node_adr_sel    ),
    .per_node_f_g_s                       ( per_node_f_g_s      ),
    .per_f_val                            ( per_f_val           ),
    .per_g_val                            ( per_g_val           ),
    .per_node_din                         ( per_node_din        ),
    .per_node_din_vld                     ( per_node_din_vld    ),
    .clk                                  ( clk                 ),
    .reset                                ( reset               )
);


f_ram_ctrl#(
    .DIMENSION         ( DIMENSION ),
    .X_RAM_NUM         ( X_RAM_NUM ),
    .Y_RAM_NUM         ( Y_RAM_NUM ),
    .Z_RAM_NUM         ( Z_RAM_NUM ),
    .ADR_DW            ( ADR_DW    ),
    .F_RAM_DW          ( F_RAM_DW  ),
    .STATE_DW          ( STATE_DW  ),
    .G_DW              ( G_DW      ),
    .F_DW              ( F_DW      )
)u_f_ram_ctrl(
    .per_node_adr      ( per_node_adr      ),
    .per_node_adr_sel  ( per_node_adr_sel    ),
    .per_node_f_g_s    ( per_node_f_g_s    ),
    .min_f_adr         ( min_f_adr         ),
    .min_f_value       ( min_f_value       ),
    .min_g_value       ( min_g_value       ),    
    .min_valid         ( min_f_valid       ),
    .clk               ( clk               ),
    .reset             ( reset             )
);

cen_node_ctrl#(
    .RAM_NUM           ( RAM_NUM ),
    .ADR_DW            ( ADR_DW  ),
    .G_DW              ( G_DW    ),
    .F_DW              ( F_DW    )
)u_cen_node_ctrl(
    .cen_node_x         ( cen_node_x          ),
    .cen_node_y         ( cen_node_y          ),
    .cen_node_z         ( cen_node_z          ),
    .cen_node_ram_index ( cen_node_ram_index  ),
    .cen_node_wr_en     ( cen_node_wr_en      ),
    .cen_node_adr_vld   ( cen_node_adr_vld    ),
    .cen_node_adr       ( cen_node_adr        ),
    .cen_node_g_val     ( cen_node_g_val      ),
    .cen_node_f_val     ( cen_node_f_val      ),
    .min_f_adr          ( min_f_adr           ),
    .min_f_value        ( min_f_value         ),
    .min_g_value        ( min_g_value         ),
    .min_f_valid        ( min_f_valid         ),
    .clk                ( clk                 ),
    .reset              ( reset               )
);



endmodule
