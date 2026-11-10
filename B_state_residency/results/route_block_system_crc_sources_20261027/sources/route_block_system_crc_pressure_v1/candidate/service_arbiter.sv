`timescale 1ns/1ps
// One captured request and response owner. Lower client index has priority.
// Buffered acceptance keeps request fields stable while the backend stalls.
module service_arbiter #(parameter integer CLIENTS=3,REQUEST_BITS=1,RESPONSE_BITS=1)(
 input wire clk,rst,
 input wire[CLIENTS-1:0]c_req_valid,output reg[CLIENTS-1:0]c_req_ready,input wire[CLIENTS*REQUEST_BITS-1:0]c_req_data,
 output wire[CLIENTS-1:0]c_rsp_valid,input wire[CLIENTS-1:0]c_rsp_ready,output wire[CLIENTS*RESPONSE_BITS-1:0]c_rsp_data,
 output wire b_req_valid,input wire b_req_ready,output reg[REQUEST_BITS-1:0]b_req_data,
 input wire b_rsp_valid,output wire b_rsp_ready,input wire[RESPONSE_BITS-1:0]b_rsp_data,
 output reg fault,output wire busy
);
 localparam IDLE=0,SEND=1,WAIT_REPLY=2;
 reg[1:0]state;integer owner,selected,i;
 always @*begin
  selected=-1;c_req_ready=0;
  for(integer j=CLIENTS-1;j>=0;j=j-1)if(c_req_valid[j])selected=j;
  if(!rst&&!fault&&state==IDLE&&selected>=0)c_req_ready[selected]=1;
 end
 assign b_req_valid=!rst&&state==SEND;
 assign b_rsp_ready=!rst&&state==WAIT_REPLY&&c_rsp_ready[owner];
 assign busy=!rst&&state!=IDLE;
 genvar g;
 generate for(g=0;g<CLIENTS;g=g+1)begin:clients
  assign c_rsp_valid[g]=!rst&&state==WAIT_REPLY&&owner==g&&b_rsp_valid;
  assign c_rsp_data[g*RESPONSE_BITS+:RESPONSE_BITS]=b_rsp_data;
 end endgenerate
 always @(posedge clk)begin
  if(rst)begin state<=IDLE;owner<=0;b_req_data<=0;fault<=0;end
  else begin
   if(b_rsp_valid&&state!=WAIT_REPLY&&!(state==SEND&&b_req_ready))fault<=1;
   case(state)
    IDLE:if(!fault&&selected>=0&&c_req_valid[selected]&&c_req_ready[selected])begin owner<=selected;b_req_data<=c_req_data[selected*REQUEST_BITS+:REQUEST_BITS];state<=SEND;end
    SEND:if(b_req_ready)state<=WAIT_REPLY;
    WAIT_REPLY:if(b_rsp_valid&&b_rsp_ready)state<=IDLE;
    default:begin fault<=1;state<=IDLE;end
   endcase
  end
 end
endmodule
