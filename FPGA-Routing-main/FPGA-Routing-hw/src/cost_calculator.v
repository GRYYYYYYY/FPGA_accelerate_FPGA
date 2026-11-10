`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 2025/03/28 20:40:18
// Design Name: 
// Module Name: cost_calculator
// Proiect Name: 
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


module cost_calculator #(
  parameter     DIMENSION             =     6                         ,
  parameter     Y_DW                  =     3                         ,
  parameter     X_DW                  =     3                         ,
  parameter     Z_DW                  =     3                         ,  
  parameter     H_DW                  =     5                         ,  
  parameter     G_DW                  =     5                         ,
  parameter     F_DW                  =     6                         ,
  parameter     STEP_X_COST           =      10                       ,
  parameter     STEP_Y_COST           =      10                       ,
  parameter     STEP_Z_COST           =      10                       

)(

  output      [DIMENSION*F_DW-1:0]        f_val         ,
  output reg  [DIMENSION*G_DW-1:0]        g_val         ,  
  output                                  cost_vld      ,

  input       [DIMENSION*X_DW-1:0]        per_x         , //perphery 
  input       [DIMENSION*Y_DW-1:0]        per_y         ,  
  input       [DIMENSION*Z_DW-1:0]        per_z         ,  
  input       [X_DW-1:0]                  end_x         ,
  input       [Y_DW-1:0]                  end_y         ,
  input       [Z_DW-1:0]                  end_z         ,

  input       [G_DW-1:0]                  cen_g_val     ,
  input       [X_DW-1:0]                  cen_x         ,
  input       [Y_DW-1:0]                  cen_y         ,
  input       [Z_DW-1:0]                  cen_z         ,

  input                                   din_vld       ,

  input                                   clk           ,
  input                                   reset
);          
wire    [DIMENSION*H_DW-1:0]        h_val             ; 
reg     [DIMENSION*H_DW-1:0]        h_val_x_reg       ;
reg     [DIMENSION*H_DW-1:0]        h_val_y_reg       ;
reg     [DIMENSION*H_DW-1:0]        h_val_z_reg       ;

wire     [DIMENSION*H_DW-1:0]        h_val_x_abs       ;
wire     [DIMENSION*H_DW-1:0]        h_val_y_abs       ;
wire     [DIMENSION*H_DW-1:0]        h_val_z_abs       ;

genvar i;
generate
  for(i=0;i<DIMENSION;i=i+1)  begin
    assign    h_val_x_abs[i*H_DW +:H_DW] =  h_val_x_reg[(i+1)*H_DW -1] ?  ~h_val_x_reg[i*H_DW +:H_DW] + 1 : h_val_x_reg[i*H_DW +:H_DW]    ;  
    assign    h_val_y_abs[i*H_DW +:H_DW] =  h_val_y_reg[(i+1)*H_DW -1] ?  ~h_val_y_reg[i*H_DW +:H_DW] + 1 : h_val_y_reg[i*H_DW +:H_DW]    ;
    assign    h_val_z_abs[i*H_DW +:H_DW] =  h_val_z_reg[(i+1)*H_DW -1] ?  ~h_val_z_reg[i*H_DW +:H_DW] + 1 : h_val_z_reg[i*H_DW +:H_DW]    ;        

    assign    h_val[i*H_DW +:H_DW] =  h_val_x_abs[i*H_DW +:H_DW] + h_val_y_abs[i*H_DW +:H_DW] + h_val_z_abs[i*H_DW +:H_DW]                                  ;
    assign    f_val[i*F_DW +:F_DW] =  h_val[i*H_DW +:H_DW] + g_val[i*G_DW +:G_DW]                              ;
    always @(posedge clk ) begin
      if(reset)
        g_val[i*G_DW +:G_DW] <=  'h0  ;
      else if(din_vld) 
        g_val[i*G_DW +:G_DW] <=  cen_g_val  +  STEP_X_COST* (cen_x - per_x[i*X_DW +:X_DW])+ 
                                               STEP_Y_COST* (cen_y - per_y[i*Y_DW +:Y_DW])+
                                               STEP_Z_COST* (cen_z - per_z[i*Z_DW +:Z_DW]);      
    end

    always @(posedge clk ) begin
      if(reset)
        h_val_x_reg[i*H_DW +:H_DW] <=  'h0  ;
      else if(din_vld) 
        h_val_x_reg[i*H_DW +:H_DW] <= STEP_X_COST* (end_x - per_x[i*X_DW +:X_DW])  ;
    end

    always @(posedge clk ) begin
      if(reset)
        h_val_y_reg[i*H_DW +:H_DW] <=  'h0  ;
      else if(din_vld) 
        h_val_y_reg[i*H_DW +:H_DW] <= STEP_Y_COST* (end_y - per_y[i*Y_DW +:Y_DW])  ;
    end

    always @(posedge clk ) begin
      if(reset)
        h_val_z_reg[i*H_DW +:H_DW] <=  'h0  ;
      else if(din_vld) 
        h_val_z_reg[i*H_DW +:H_DW] <= STEP_Z_COST* (end_z - per_z[i*Z_DW +:Z_DW])  ;
    end

  end
endgenerate

dly_cell#(
    .DW    ( 1 ),
    .DLY   ( 1 )
)u_dly_cell(
    .dout  ( cost_vld  ),
    .din   ( din_vld   ),
    .clk   ( clk   ),
    .reset  ( reset  )
);

endmodule