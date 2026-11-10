`timescale 1ns/1ps
module expansion_controller # (parameter integer TOKEN_BITS=32,OWNER_BITS=32)(
 input wire clk,rst,enable,configuration_fault,
 input wire expand_valid,output wire expand_ready,input wire[31:0]expand_cookie,expand_parent,expand_prune,expand_has_laguna,
 output wire out_valid,input wire out_ready,output reg[31:0]out_node,out_position,out_sequence,output reg[255:0]out_attrs,
 output wire result_valid,input wire result_ready,output reg[3:0]result_status,output reg[31:0]result_detail,result_cookie,result_count,result_raw_count,result_mask,output reg result_hit,
 output wire busy,fault,
 input wire g_fault,d_fault,p_fault,b_fault,p_active,input wire[1:0]p_active_query,input wire[3:0]p_active_price,
 output wire g_req_valid,input wire g_req_ready,output reg[1:0]g_req_op,output reg[31:0]g_req_cookie,g_req_node,g_req_index,
 input wire g_rsp_valid,output wire g_rsp_ready,input wire[3:0]g_rsp_status,
 input wire[31:0]g_rsp_cookie,g_rsp_parent,g_rsp_index,g_rsp_node,g_rsp_start,g_rsp_count,input wire[255:0]g_rsp_attrs,
 output wire d_req_valid,input wire d_req_ready,output reg[2:0]d_req_op,output reg[31:0]d_req_cookie,d_req_owner,d_req_node,d_req_arg,
 input wire d_rsp_valid,output wire d_rsp_ready,input wire[3:0]d_rsp_status,input wire[31:0]d_rsp_cookie,d_rsp_flags,d_rsp_count,d_rsp_mask,
 input wire d_claim_active,input wire[31:0]d_claim_owner,d_claim_node,d_claim_count,d_claim_mask,
 output wire b_build_valid,input wire b_build_ready,output reg[31:0]b_build_cookie,b_build_parent,b_build_count,b_build_prune,
 output reg[1:0]b_build_query,output reg[3:0]b_build_price,
 input wire b_result_valid,output wire b_result_ready,input wire[3:0]b_result_status,input wire[31:0]b_result_detail,b_result_cookie,b_result_generation,b_result_emitted,
 input wire b_svc_valid,output wire b_svc_ready,input wire[31:0]b_svc_generation,b_svc_parent,b_svc_position,b_svc_phase,b_svc_node,b_svc_emitted,b_svc_count,b_svc_prune,
 input wire[1:0]b_svc_query,input wire[3:0]b_svc_price,
 output wire b_svc_reply_valid,input wire b_svc_reply_ready,
 output reg[31:0]b_svc_reply_generation,b_svc_reply_parent,b_svc_reply_position,b_svc_reply_phase,b_svc_reply_node,
 output reg[1:0]b_svc_reply_query,output reg[3:0]b_svc_reply_price,output reg[31:0]b_svc_status,b_svc_value,b_svc_aux,output wire b_service_fault,
 output wire p_edge_valid,input wire p_edge_ready,output reg[31:0]p_edge_cookie,p_edge_parent,p_edge_child,p_edge_flags,p_edge_created,p_edge_has_laguna,
 input wire p_result_valid,output wire p_result_ready,input wire[3:0]p_result_status,input wire[31:0]p_result_detail,p_result_cookie,p_result_generation,input wire p_result_excluded
);
 localparam IDLE=0,G_SEND=1,G_WAIT=2,D_SEND=3,D_WAIT=4,B_SEND=5,B_WAIT=6,SVC_REPLY=7,P_SEND=8,P_WAIT=9,SCAN=10,OUTPUT=11,RESULT=12;
 localparam META=0,NEXT_NODE=1,REPLAY=2,CLAIM=3,NEXT_STATE=4,CREATE=5,EMIT=6,CHECK=7,DEAD=8,PUBLISH=9;
 localparam[31:0]TOKEN_MAX=32'hffffffff>>(32-TOKEN_BITS),OWNER_MAX=32'hffffffff>>(32-OWNER_BITS);
 reg[3:0]state,action;
 reg stopped;reg[31:0]token,last_owner,owner,parent,prune,laguna,raw_count,raw_start,keep,child,child_flags,child_position,scan_position,delivered;
 reg[255:0]parent_attrs,child_attrs;
 reg[1:0]query;reg[3:0]price;
 wire context_error=state!=IDLE&&(!p_active||p_active_query!=query||p_active_price!=price);
 wire external_fault=g_fault||d_fault||p_fault||configuration_fault||context_error;
 wire unexpected=(g_rsp_valid&&state!=G_WAIT)||(d_rsp_valid&&state!=D_WAIT)||(p_result_valid&&state!=P_WAIT)||
                 (b_svc_valid&&state!=B_WAIT)||(b_result_valid&&state!=B_WAIT);
 wire abort_now=external_fault||b_fault||unexpected;
 wire allow_io=!rst&&!stopped&&!external_fault;
 assign fault=!rst&&(stopped||abort_now);
 assign busy=!rst&&(state!=IDLE||stopped);
 assign expand_ready=allow_io&&!b_fault&&!unexpected&&state==IDLE&&enable;
 assign g_req_valid=allow_io&&state==G_SEND;assign g_rsp_ready=allow_io&&state==G_WAIT;
 assign d_req_valid=allow_io&&state==D_SEND;assign d_rsp_ready=allow_io&&state==D_WAIT;
 assign b_build_valid=allow_io&&state==B_SEND;assign b_result_ready=allow_io&&state==B_WAIT;
 assign b_svc_ready=allow_io&&state==B_WAIT&&!b_result_valid;
 assign b_svc_reply_valid=allow_io&&state==SVC_REPLY;
 // Never feed b_fault back combinationally into its own external fault input.
 assign b_service_fault=!rst&&(stopped||external_fault);
 assign p_edge_valid=allow_io&&state==P_SEND;assign p_result_ready=allow_io&&state==P_WAIT;
 assign out_valid=!rst&&state==OUTPUT;assign result_valid=!rst&&state==RESULT;
 function[31:0]popcount(input[31:0]v);integer i;begin popcount=0;for(i=0;i<32;i=i+1)popcount=popcount+v[i];end endfunction
 function exclusive_sink(input[7:0]t);begin exclusive_sink=t>=1&&t<=4;end endfunction
 task fail(input[3:0]status,input[31:0]detail);
  begin stopped<=1;result_status<=status;result_detail<=detail;if(state!=OUTPUT&&state!=RESULT)state<=RESULT;end
 endtask
 task graph_request(input[1:0]op,input[31:0]node,index,input[3:0]next_action);
  begin
   if(token==TOKEN_MAX)fail(3,1);
   else begin token<=token+1'b1;g_req_cookie<=token+1'b1;g_req_op<=op;g_req_node<=node;g_req_index<=index;action<=next_action;state<=G_SEND;end
  end
 endtask
 task design_request(input[2:0]op,input[31:0]node,arg,who,input[3:0]next_action);
  begin
   if(token==TOKEN_MAX)fail(3,1);
   else begin token<=token+1'b1;d_req_cookie<=token+1'b1;d_req_op<=op;d_req_node<=node;d_req_arg<=arg;d_req_owner<=who;action<=next_action;state<=D_SEND;end
  end
 endtask
 task service_reply(input[31:0]value,aux);
  begin b_svc_value<=value;b_svc_aux<=aux;b_svc_status<=0;state<=SVC_REPLY;end
 endtask
 wire svc_owner_bad=b_svc_generation==0||b_svc_parent!=parent||b_svc_count!=raw_count||b_svc_prune!=prune||b_svc_query!=query||b_svc_price!=price;
 wire svc_child_bad=b_svc_node!=child||b_svc_position!=child_position;
 always @(posedge clk)begin
  if(rst)begin
   state<=IDLE;action<=0;stopped<=0;token<=0;last_owner<=0;owner<=0;parent<=0;prune<=0;laguna<=0;raw_count<=0;raw_start<=0;keep<=0;child<=0;child_flags<=0;child_position<=0;scan_position<=0;delivered<=0;
   parent_attrs<=0;child_attrs<=0;query<=0;price<=0;
   out_node<=0;out_position<=0;out_sequence<=0;out_attrs<=0;
   result_status<=0;result_detail<=0;result_cookie<=0;result_count<=0;result_raw_count<=0;result_mask<=0;result_hit<=0;
   g_req_op<=0;g_req_cookie<=0;g_req_node<=0;g_req_index<=0;
   d_req_op<=0;d_req_cookie<=0;d_req_owner<=0;d_req_node<=0;d_req_arg<=0;
   b_build_cookie<=0;b_build_parent<=0;b_build_count<=0;b_build_prune<=0;b_build_query<=0;b_build_price<=0;
   b_svc_reply_generation<=0;b_svc_reply_parent<=0;b_svc_reply_position<=0;b_svc_reply_phase<=0;b_svc_reply_node<=0;b_svc_reply_query<=0;b_svc_reply_price<=0;b_svc_status<=0;b_svc_value<=0;b_svc_aux<=0;
   p_edge_cookie<=0;p_edge_parent<=0;p_edge_child<=0;p_edge_flags<=0;p_edge_created<=0;p_edge_has_laguna<=0;
  end else begin
   if(state==RESULT&&result_ready)state<=IDLE;
   if(stopped&&state==OUTPUT&&out_ready)state<=RESULT;
   if(!stopped&&abort_now)begin
    stopped<=1;
    if(state!=RESULT&&state!=IDLE)begin result_status<=4;result_detail<=0;if(state!=OUTPUT)state<=RESULT;end
   end else if(!stopped)case(state)
    IDLE:if(expand_valid&&expand_ready)begin
     result_cookie<=expand_cookie;result_status<=0;result_detail<=0;result_count<=0;result_raw_count<=0;result_mask<=0;result_hit<=0;
     parent<=expand_parent;prune<=expand_prune;laguna<=expand_has_laguna;query<=p_active_query;price<=p_active_price;
     keep<=0;delivered<=0;scan_position<=0;
     if(expand_parent[31:24]!=0||expand_prune>1||expand_has_laguna>1)begin result_status<=1;state<=RESULT;end
     else if(last_owner==OWNER_MAX)fail(3,0);
     else begin owner<=last_owner+1'b1;last_owner<=last_owner+1'b1;graph_request(0,expand_parent,0,META);end
    end
    G_SEND:if(g_req_ready)state<=G_WAIT;
    G_WAIT:if(g_rsp_valid&&g_rsp_ready)begin
     if(g_rsp_cookie!=g_req_cookie||g_rsp_parent!=g_req_node||g_rsp_index!=g_req_index)fail(5,1);
     else if(g_rsp_status!=0)begin
      if(action==META&&g_rsp_status==2)begin result_status<=1;state<=RESULT;end
      else fail(4,{28'b0,g_rsp_status});
     end else if(action==META)begin
      if(g_rsp_node!=parent)fail(5,2);
      else if(g_rsp_count>32)begin result_status<=2;result_detail<=g_rsp_count;state<=RESULT;end
      else begin
       raw_count<=g_rsp_count;raw_start<=g_rsp_start;parent_attrs<=g_rsp_attrs;result_raw_count<=g_rsp_count;
       design_request(1,parent,g_rsp_count,owner,CLAIM);
      end
     end else if(g_rsp_start!=raw_start||g_rsp_count!=raw_count)fail(5,3);
     else if(action==NEXT_NODE)begin
      child<=g_rsp_node;child_attrs<=g_rsp_attrs;child_position<=g_req_index;
      design_request(0,g_rsp_node,0,owner,NEXT_STATE);
     end else if(action==REPLAY)begin
      out_node<=g_rsp_node;out_attrs<=g_rsp_attrs;out_position<=scan_position;out_sequence<=delivered;state<=OUTPUT;
     end else fail(5,4);
    end
    D_SEND:if(d_req_ready)state<=D_WAIT;
    D_WAIT:if(d_rsp_valid&&d_rsp_ready)begin
     if(d_rsp_cookie!=d_req_cookie)fail(5,5);
     else if(d_rsp_status!=0)fail(4,{28'b0,d_rsp_status});
     else case(action)
      CLAIM:begin
       if(d_rsp_flags[2])begin
        if(d_claim_active||d_rsp_count!=raw_count)fail(5,6);
        else begin keep<=d_rsp_mask;result_hit<=1;state<=SCAN;end
       end else if(!d_claim_active||d_claim_owner!=owner||d_claim_node!=parent||d_claim_count!=raw_count||d_claim_mask!=0)fail(5,7);
       else begin b_build_cookie<=owner;b_build_parent<=parent;b_build_count<=raw_count;b_build_prune<=prune;b_build_query<=query;b_build_price<=price;state<=B_SEND;end
      end
      NEXT_STATE:begin
       child_flags<=d_rsp_flags;
       service_reply(child,(child_attrs[78]||d_rsp_flags[1]||child_attrs[71:64]==17||(exclusive_sink(child_attrs[71:64])&&!d_rsp_flags[3]))?1:0);
      end
      CREATE:begin
       if(!d_rsp_flags[0])fail(5,8);else begin child_flags<=d_rsp_flags;service_reply(0,0);end
      end
      EMIT:begin
       if(d_rsp_count!=raw_count||d_rsp_mask!=(keep|(32'b1<<b_svc_reply_position))||popcount(d_rsp_mask)!=b_svc_emitted+1'b1)fail(5,9);
       else begin keep<=d_rsp_mask;service_reply(0,0);end
      end
      CHECK:service_reply((!d_rsp_flags[3]&&!exclusive_sink(parent_attrs[71:64])&&(parent_attrs[79:72]&8'h8e)==0)?1:0,0);
      DEAD:begin if(!d_rsp_flags[1])fail(5,10);else service_reply(0,0);end
      PUBLISH:begin
       if(d_claim_active||!d_rsp_flags[2]||d_rsp_count!=raw_count||d_rsp_mask!=keep)fail(5,11);else service_reply(0,0);
      end
      default:fail(5,12);
     endcase
    end
    B_SEND:if(b_build_ready)state<=B_WAIT;
    B_WAIT:begin
     if(b_result_valid&&b_result_ready)begin
      if(b_result_status!=0)fail(6,b_result_detail);
      else if(b_result_cookie!=owner||b_result_generation==0||b_result_emitted!=popcount(keep)||d_claim_active)fail(5,13);
      else state<=SCAN;
     end else if(b_svc_valid&&b_svc_ready)begin
      b_svc_reply_generation<=b_svc_generation;b_svc_reply_parent<=b_svc_parent;b_svc_reply_position<=b_svc_position;b_svc_reply_phase<=b_svc_phase;b_svc_reply_node<=b_svc_node;b_svc_reply_query<=b_svc_query;b_svc_reply_price<=b_svc_price;
      b_svc_status<=0;b_svc_value<=0;b_svc_aux<=0;
      if(svc_owner_bad)fail(5,14);
      else case(b_svc_phase)
       0:begin if(b_svc_node!=parent||b_svc_position>=raw_count)fail(5,15);else graph_request(1,parent,b_svc_position,NEXT_NODE);end
       1:begin
        if(svc_child_bad)fail(5,16);
        else if(token==TOKEN_MAX)fail(3,1);
        else begin
         token<=token+1'b1;p_edge_cookie<=token+1'b1;p_edge_parent<=parent;p_edge_child<=child;
         p_edge_flags<={24'b0,child_attrs[79:72]};p_edge_created<=(child_attrs[72]||child_flags[0])?1:0;p_edge_has_laguna<=laguna;state<=P_SEND;
        end
       end
       2:begin if(svc_child_bad)fail(5,17);else design_request(2,child,0,owner,CREATE);end
       3:begin if(svc_child_bad||!child_flags[0])fail(5,18);else service_reply(child_attrs[71:64]==17?1:0,child_flags[1]?1:0);end
       4:begin if(svc_child_bad)fail(5,19);else design_request(4,parent,b_svc_position,owner,EMIT);end
       5:begin if(b_svc_node!=parent)fail(5,20);else design_request(0,parent,0,owner,CHECK);end
       6:begin if(b_svc_node!=parent)fail(5,21);else design_request(3,parent,0,owner,DEAD);end
       7:begin if(b_svc_node!=parent||b_svc_emitted!=popcount(keep))fail(5,22);else design_request(5,parent,0,owner,PUBLISH);end
       default:fail(5,23);
      endcase
     end
    end
    P_SEND:if(p_edge_ready)state<=P_WAIT;
    P_WAIT:if(p_result_valid&&p_result_ready)begin
     if(p_result_cookie!=p_edge_cookie||p_result_generation==0)fail(5,24);
     else if(p_result_status!=0)fail(4,p_result_detail);
     else service_reply(p_result_excluded?1:0,0);
    end
    SVC_REPLY:if(b_svc_reply_ready)state<=B_WAIT;
    SCAN:begin
     if(scan_position>=raw_count)begin
      if(delivered!=popcount(keep))fail(5,25);
      else begin result_count<=delivered;result_mask<=keep;state<=RESULT;end
     end else if(keep[scan_position])graph_request(1,parent,scan_position,REPLAY);
     else scan_position<=scan_position+1'b1;
    end
    OUTPUT:if(out_ready)begin delivered<=delivered+1'b1;scan_position<=scan_position+1'b1;state<=SCAN;end
    default:begin end
   endcase
  end
 end
endmodule
