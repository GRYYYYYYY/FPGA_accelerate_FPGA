`timescale 1ns/1ps
// Config and algorithm state reside here throughout a complete child decision.
module access_controller #(parameter integer TOKEN_BITS=32,MAX_CYCLES=8388608,MAX_STEPS=32)(
 input wire clk,rst,abort,enable,active,input wire[1:0]active_query,input wire[3:0]active_price,
 input wire req_valid,output wire req_ready,input wire[447:0]req_config,
 input wire[31:0]req_cookie,req_parent,req_child,req_sink,req_net,input wire[1:0]req_query,input wire[3:0]req_price,
 output wire rsp_valid,input wire rsp_ready,output reg[3:0]rsp_status,
 output reg[31:0]rsp_cookie,rsp_parent,rsp_child,rsp_sink,rsp_net,rsp_bits,rsp_action,rsp_steps,rsp_services,
 output reg[1:0]rsp_query,output reg[3:0]rsp_price,output wire busy,fault,
 output wire svc_valid,input wire svc_ready,output reg[3:0]svc_kind,output reg[4:0]svc_phase,
 output reg[31:0]svc_node,output wire[31:0]svc_net,svc_cookie,output wire[1:0]svc_query,output wire[3:0]svc_price,
 input wire svc_rsp_valid,output wire svc_rsp_ready,input wire[3:0]svc_rsp_status,svc_rsp_kind,
 input wire[4:0]svc_rsp_phase,input wire[31:0]svc_rsp_node,svc_rsp_net,svc_rsp_cookie,svc_rsp_value,
 input wire[1:0]svc_rsp_query,input wire[3:0]svc_rsp_price,input wire svc_fault,
 output wire k_req_valid,input wire k_req_ready,output reg[639:0]k_req_words,
 output wire[31:0]k_req_cookie,output wire[1:0]k_req_query,output wire[3:0]k_req_price,
 input wire k_rsp_valid,output wire k_rsp_ready,input wire[191:0]k_rsp_words,input wire[1:0]k_rsp_status,
 input wire[31:0]k_rsp_cookie,input wire[1:0]k_rsp_query,input wire[3:0]k_rsp_price,input wire k_fault
);
 localparam[2:0]IDLE=0,KS=1,KW=2,SS=3,SW=4,REPLY=5;
 localparam integer TBITS=$clog2(MAX_CYCLES+1);
 localparam[31:0]TOKEN_MAX=32'hffffffff>>(32-TOKEN_BITS);
 reg[2:0]state;reg stopped,owned;reg[31:0]token;reg[TBITS-1:0]elapsed;
 wire unexpected=(k_rsp_valid&&state!=KW)||(svc_rsp_valid&&state!=SW);
 wire drift=owned&&state!=IDLE&&(!active||active_query!=rsp_query||active_price!=rsp_price);
 wire timeout=state!=IDLE&&state!=REPLY&&elapsed==MAX_CYCLES-1;
 assign fault=!rst&&(stopped||abort||svc_fault||k_fault||unexpected||drift||timeout);
 assign req_ready=!rst&&!fault&&enable&&state==IDLE;
 assign rsp_valid=!rst&&state==REPLY;assign busy=!rst&&(state!=IDLE||fault);
 assign k_req_valid=!rst&&!fault&&state==KS;assign k_rsp_ready=!rst&&!fault&&state==KW;
 assign k_req_cookie=token;assign k_req_query=rsp_query;assign k_req_price=rsp_price;
 assign svc_valid=!rst&&!fault&&state==SS;assign svc_rsp_ready=!rst&&!fault&&state==SW;
 assign svc_cookie=token;assign svc_query=rsp_query;assign svc_price=rsp_price;assign svc_net=rsp_net;
 wire[31:0]ks_status=k_rsp_words[31:0],ks_phase=k_rsp_words[63:32],ks_bits=k_rsp_words[95:64],ks_aux=k_rsp_words[127:96],ks_request=k_rsp_words[159:128],ks_action=k_rsp_words[191:160];
 function[31:0]phase_request(input[31:0]phase);
 begin case(phase)
 0:phase_request=0;1:phase_request=1;2:phase_request=2;3:phase_request=3;4,7,10:phase_request=4;5:phase_request=5;6:phase_request=6;
 9,11,16:phase_request=7;8,12,17:phase_request=8;13,14:phase_request=9;15:phase_request=10;18:phase_request=11;default:phase_request=32'hffffffff;
 endcase end endfunction
 task fail(input[3:0]code);begin stopped<=1;rsp_status<=code;state<=REPLY;end endtask
 task dispatch(input[2:0]nextstate);begin if(token==TOKEN_MAX)fail(6);else begin token<=token+1;state<=nextstate;end end endtask
 always @(posedge clk)begin
  if(rst)begin
   state<=IDLE;stopped<=0;owned<=0;token<=0;elapsed<=0;k_req_words<=0;
   rsp_status<=0;rsp_cookie<=0;rsp_parent<=0;rsp_child<=0;rsp_sink<=0;rsp_net<=0;rsp_bits<=0;rsp_action<=0;rsp_steps<=0;rsp_services<=0;rsp_query<=0;rsp_price<=0;
   svc_kind<=0;svc_phase<=0;svc_node<=0;
  end else begin
   if(state==REPLY&&rsp_ready)begin state<=IDLE;owned<=0;end
   if(fault)begin stopped<=1;if(state!=IDLE&&state!=REPLY)begin rsp_status<=5;state<=REPLY;end end
   else begin
    if(state!=IDLE&&state!=REPLY)elapsed<=elapsed+1'b1;
    case(state)
     IDLE:if(req_valid&&req_ready)begin
      rsp_status<=0;rsp_cookie<=req_cookie;rsp_parent<=req_parent;rsp_child<=req_child;rsp_sink<=req_sink;rsp_net<=req_net;rsp_query<=req_query;rsp_price<=req_price;
      rsp_bits<=0;rsp_action<=0;rsp_steps<=0;rsp_services<=0;elapsed<=0;owned<=0;k_req_words<={req_config,192'b0};
      if(!active)begin rsp_status<=1;state<=REPLY;end
      else if(req_query!=active_query||req_price!=active_price)begin rsp_status<=2;state<=REPLY;end
      else begin owned<=1;dispatch(KS);end
     end
     KS:if(k_req_valid&&k_req_ready)state<=KW;
     KW:if(k_rsp_valid&&k_rsp_ready)begin
      if(k_rsp_status!=0||ks_status!=0)fail(3);
      else if(k_rsp_cookie!=token||k_rsp_query!=rsp_query||k_rsp_price!=rsp_price)fail(4);
      else if(ks_phase>18||ks_bits>=16||ks_action>2||phase_request(ks_phase)!=ks_request)fail(7);
      else begin
       rsp_steps<=rsp_steps+1;
       if(ks_request==0)begin rsp_bits<=ks_bits;rsp_action<=ks_action;state<=REPLY;end
       else if(rsp_steps+1>=MAX_STEPS)fail(8);
       else begin
        k_req_words[31:0]<=1;k_req_words[63:32]<=ks_phase;k_req_words[95:64]<=ks_bits;k_req_words[127:96]<=ks_aux;k_req_words[159:128]<=ks_action;
        svc_kind<=ks_request[3:0];svc_phase<=ks_phase[4:0];
        case(ks_request)8:svc_node<=rsp_sink;9:svc_node<=rsp_parent;10:svc_node<=ks_aux;default:svc_node<=rsp_child;endcase
        dispatch(SS);
       end
      end
     end
     SS:if(svc_valid&&svc_ready)state<=SW;
     SW:if(svc_rsp_valid&&svc_rsp_ready)begin
      if(svc_rsp_status!=0)fail(3);
      else if(svc_rsp_cookie!=token||svc_rsp_query!=rsp_query||svc_rsp_price!=rsp_price||svc_rsp_kind!=svc_kind||svc_rsp_phase!=svc_phase||svc_rsp_node!=svc_node||svc_rsp_net!=rsp_net)fail(4);
      else begin rsp_services<=rsp_services+1;k_req_words[191:160]<=svc_rsp_value;dispatch(KS);end
     end
     default:begin end
    endcase
   end
  end
 end
endmodule
