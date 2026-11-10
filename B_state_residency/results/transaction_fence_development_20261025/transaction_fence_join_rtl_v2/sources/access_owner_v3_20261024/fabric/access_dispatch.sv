`timescale 1ns/1ps
// Serial dispatch from access_step requests to actual labels/coordinates and owner service.
module access_dispatch #(parameter integer MAX_CYCLES=262144)(
 input wire clk,rst,abort,active,input wire[1:0]active_query,input wire[3:0]active_price,
 input wire req_valid,output wire req_ready,input wire[3:0]req_kind,input wire[4:0]req_phase,
 input wire[31:0]req_node,req_net,req_cookie,input wire[1:0]req_query,input wire[3:0]req_price,
 output wire rsp_valid,input wire rsp_ready,output reg[3:0]rsp_status,rsp_kind,output reg[4:0]rsp_phase,
 output reg[31:0]rsp_node,rsp_net,rsp_cookie,rsp_value,output reg[1:0]rsp_query,output reg[3:0]rsp_price,output wire fault,
 output wire l_valid,input wire l_ready,output wire l_write,output wire[31:0]l_node,l_value,output wire[2:0]l_field,
 input wire l_rsp_valid,output wire l_rsp_ready,input wire[3:0]l_status,input wire[159:0]l_payload,input wire l_present,
 output wire c_req_valid,input wire c_req_ready,output wire[1:0]c_req_op,c_req_query,output wire[3:0]c_req_price,
 output wire[31:0]c_req_cookie,c_req_node,input wire c_rsp_valid,output wire c_rsp_ready,
 input wire[3:0]c_rsp_status,input wire[1:0]c_rsp_op,c_rsp_query,input wire[3:0]c_rsp_price,input wire[31:0]c_rsp_cookie,c_rsp_node,c_rsp_y,c_rsp_slr,input wire[255:0]c_rsp_attrs,input wire c_fault,
 output wire o_req_valid,input wire o_req_ready,output wire[3:0]o_req_kind,output wire[4:0]o_req_phase,
 output wire[31:0]o_req_node,o_req_net,o_req_cookie,output wire[1:0]o_req_query,output wire[3:0]o_req_price,
 input wire o_rsp_valid,output wire o_rsp_ready,input wire[3:0]o_rsp_status,o_rsp_kind,input wire[4:0]o_rsp_phase,
 input wire[31:0]o_rsp_node,o_rsp_net,o_rsp_cookie,o_rsp_value,input wire[1:0]o_rsp_query,input wire[3:0]o_rsp_price,input wire o_fault
);
 localparam[2:0]IDLE=0,LS=1,LW=2,CS=3,CW=4,OS=5,OW=6,REPLY=7;
 localparam integer TBITS=$clog2(MAX_CYCLES+1);
 reg[2:0]state;reg stopped,owned;reg[TBITS-1:0]elapsed;
 wire unexpected=(l_rsp_valid&&state!=LW)||(c_rsp_valid&&state!=CW)||(o_rsp_valid&&state!=OW);
 wire drift=owned&&state!=IDLE&&(!active||active_query!=rsp_query||active_price!=rsp_price);
 wire timeout=state!=IDLE&&state!=REPLY&&elapsed==MAX_CYCLES-1;
 assign fault=!rst&&(stopped||abort||c_fault||o_fault||unexpected||drift||timeout);
 assign req_ready=!rst&&!fault&&state==IDLE;assign rsp_valid=!rst&&state==REPLY;
 assign l_valid=!rst&&!fault&&state==LS;assign l_rsp_ready=!rst&&!fault&&state==LW;
 assign l_write=0;assign l_node=rsp_node;assign l_value=0;assign l_field=rsp_kind==1?3:rsp_kind==9?2:4;
 assign c_req_valid=!rst&&!fault&&state==CS;assign c_rsp_ready=!rst&&!fault&&state==CW;
 assign c_req_op=rsp_kind==10?3:(rsp_kind==7||rsp_kind==8)?1:0;
 assign c_req_node=rsp_node;assign c_req_cookie=rsp_cookie;assign c_req_query=rsp_query;assign c_req_price=rsp_price;
 assign o_req_valid=!rst&&!fault&&state==OS;assign o_rsp_ready=!rst&&!fault&&state==OW;
 assign o_req_kind=rsp_kind;assign o_req_phase=rsp_phase;assign o_req_node=rsp_node;assign o_req_net=rsp_net;assign o_req_cookie=rsp_cookie;assign o_req_query=rsp_query;assign o_req_price=rsp_price;
 task fail(input[3:0]code);begin rsp_status<=code;state<=REPLY;stopped<=1;end endtask
 always @(posedge clk)begin
  if(rst)begin state<=IDLE;stopped<=0;owned<=0;elapsed<=0;rsp_status<=0;rsp_kind<=0;rsp_phase<=0;rsp_node<=0;rsp_net<=0;rsp_cookie<=0;rsp_value<=0;rsp_query<=0;rsp_price<=0;end
  else begin
   if(state==REPLY&&rsp_ready)begin state<=IDLE;owned<=0;end
   if(fault)begin stopped<=1;if(state!=IDLE&&state!=REPLY)begin rsp_status<=5;state<=REPLY;end end
   else begin
    if(state!=IDLE&&state!=REPLY)elapsed<=elapsed+1'b1;
    case(state)
     IDLE:if(req_valid&&req_ready)begin
      rsp_status<=0;rsp_kind<=req_kind;rsp_phase<=req_phase;rsp_node<=req_node;rsp_net<=req_net;rsp_cookie<=req_cookie;rsp_value<=0;rsp_query<=req_query;rsp_price<=req_price;elapsed<=0;owned<=1;
      if(!active||req_query!=active_query||req_price!=active_price)fail(2);
      else case(req_kind)1,2,5,9:state<=LS;3,7,8,10,11:state<=CS;4,6:state<=OS;default:fail(1);endcase
     end
     LS:if(l_valid&&l_ready)state<=LW;
     LW:if(l_rsp_valid&&l_rsp_ready)begin
      if(l_status!=0||(!l_present&&l_payload!=0))fail(3);
      else begin rsp_value<=l_payload[l_field*32+:32];state<=REPLY;end
     end
     CS:if(c_req_valid&&c_req_ready)state<=CW;
     CW:if(c_rsp_valid&&c_rsp_ready)begin
      if(c_rsp_status!=0)fail(3);
      else if(c_rsp_cookie!=rsp_cookie||c_rsp_node!=rsp_node||c_rsp_query!=rsp_query||c_rsp_price!=rsp_price||c_rsp_op!=c_req_op)fail(4);
      else begin rsp_value<=rsp_kind==10?c_rsp_attrs[31:0]:(rsp_kind==7||rsp_kind==8)?c_rsp_slr:c_rsp_y;state<=REPLY;end
     end
     OS:if(o_req_valid&&o_req_ready)state<=OW;
     OW:if(o_rsp_valid&&o_rsp_ready)begin
      if(o_rsp_status!=0)fail(3);
      else if(o_rsp_kind!=rsp_kind||o_rsp_phase!=rsp_phase||o_rsp_node!=rsp_node||o_rsp_net!=rsp_net||o_rsp_cookie!=rsp_cookie||o_rsp_query!=rsp_query||o_rsp_price!=rsp_price)fail(4);
      else begin rsp_value<=o_rsp_value;state<=REPLY;end
     end
     default:begin end
    endcase
   end
  end
 end
endmodule
