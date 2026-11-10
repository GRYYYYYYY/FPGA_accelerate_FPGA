`timescale 1ns/1ps
// getChildren -> device metadata -> access decision. Cost/push are downstream.
module candidate_controller #(parameter integer MAX_CYCLES=33554432)(
 input wire clk,rst,enable,abort,subsystem_fault,
 input wire[31:0]nodes,input wire active,input wire[1:0]active_query,input wire[3:0]active_price,
 input wire expand_valid,output wire expand_ready,input wire[31:0]expand_cookie,expand_parent,expand_prune,expand_has_laguna,
 input wire[31:0]expand_sink,expand_net,expand_sequence,expand_flags,expand_xmin,expand_xmax,expand_ymin,expand_ymax,
 output wire out_valid,input wire out_ready,output reg[31:0]out_cookie,out_node,out_position,out_sequence,out_bits,out_action,out_steps,out_services,
 output reg[255:0]out_attrs,output reg[447:0]out_config,
 output wire result_valid,input wire result_ready,output reg[3:0]result_status,
 output reg[31:0]result_cookie,result_count,result_expanded_count,result_raw_count,result_mask,output reg result_hit,result_early,
 output reg operation_pending,output reg stopped,
 output wire e_expand_valid,input wire e_expand_ready,output wire[31:0]e_expand_cookie,e_expand_parent,e_expand_prune,e_expand_has_laguna,
 input wire e_out_valid,output wire e_out_ready,input wire[31:0]e_out_node,e_out_position,e_out_sequence,input wire[255:0]e_out_attrs,
 input wire e_result_valid,output wire e_result_ready,input wire[3:0]e_result_status,input wire[31:0]e_result_cookie,e_result_count,e_result_raw_count,e_result_mask,input wire e_result_hit,
 output wire m_req_valid,input wire m_req_ready,output wire[31:0]m_req_cookie,m_req_parent,m_req_child,m_req_sink,m_req_net,m_req_sequence,m_req_flags,m_req_xmin,m_req_xmax,m_req_ymin,m_req_ymax,
 output wire[1:0]m_req_query,output wire[3:0]m_req_price,
 input wire m_rsp_valid,output wire m_rsp_ready,input wire[3:0]m_rsp_status,input wire[31:0]m_rsp_cookie,m_rsp_parent,m_rsp_child,m_rsp_sink,m_rsp_net,input wire[1:0]m_rsp_query,input wire[3:0]m_rsp_price,input wire[447:0]m_rsp_config,input wire m_rsp_created,
 output wire a_req_valid,input wire a_req_ready,output wire[31:0]a_req_cookie,a_req_parent,a_req_child,a_req_sink,a_req_net,output wire[1:0]a_req_query,output wire[3:0]a_req_price,output wire[447:0]a_req_config,
 input wire a_rsp_valid,output wire a_rsp_ready,input wire[3:0]a_rsp_status,input wire[31:0]a_rsp_cookie,a_rsp_parent,a_rsp_child,a_rsp_sink,a_rsp_net,a_rsp_bits,a_rsp_action,a_rsp_steps,a_rsp_services,input wire[1:0]a_rsp_query,input wire[3:0]a_rsp_price
);
 localparam IDLE=0,NEXT_CHILD=1,METADATA=2,ACCESS=3,OUTPUT=4,DRAIN=5,FINAL=6;
 reg[2:0]state;reg[31:0]parent,sink,net,sequence_word,flags,xmin,xmax,ymin,ymax,child,position,ordinal,processed,elapsed;
 reg[255:0]attrs;reg[1:0]query;reg[3:0]price;reg early;reg m_pending,a_pending,e_pending,e_done;
 wire timeout=operation_pending&&!stopped&&state!=OUTPUT&&state!=FINAL&&elapsed>=MAX_CYCLES-1;
 wire invalid=expand_parent>=nodes||expand_sink>=nodes||expand_prune>1||expand_has_laguna>1||(expand_flags&~32'h11c)!=0;
 wire unexpected=(m_rsp_valid&&!m_pending)||(a_rsp_valid&&!a_pending)||((e_result_valid||e_out_valid)&&!e_pending)||(e_result_valid&&e_out_valid);
 wire drain_complete=e_done&&!m_pending&&!a_pending;
 wire drift=operation_pending&&(!active||active_query!=query||active_price!=price);
 assign expand_ready=!rst&&!stopped&&!subsystem_fault&&!abort&&enable&&state==IDLE&&e_expand_ready;
 assign e_expand_valid=expand_valid&&expand_ready&&!invalid;
 assign e_expand_cookie=expand_cookie;assign e_expand_parent=expand_parent;assign e_expand_prune=expand_prune;assign e_expand_has_laguna=expand_has_laguna;
 assign m_req_valid=!rst&&!stopped&&state==NEXT_CHILD&&!early&&e_out_valid;
 assign m_req_cookie=e_out_sequence;assign m_req_parent=parent;assign m_req_child=e_out_node;assign m_req_sink=sink;assign m_req_net=net;assign m_req_sequence=sequence_word;assign m_req_flags=flags;
 assign m_req_xmin=xmin;assign m_req_xmax=xmax;assign m_req_ymin=ymin;assign m_req_ymax=ymax;assign m_req_query=query;assign m_req_price=price;
 wire metadata_bad=m_rsp_status!=0||!m_rsp_created||m_rsp_cookie!=ordinal||m_rsp_parent!=parent||m_rsp_child!=child||m_rsp_sink!=sink||m_rsp_net!=net||m_rsp_query!=query||m_rsp_price!=price;
 wire access_bad=a_rsp_status!=0||a_rsp_cookie!=ordinal||a_rsp_parent!=parent||a_rsp_child!=child||a_rsp_sink!=sink||a_rsp_net!=net||a_rsp_query!=query||a_rsp_price!=price;
 assign a_req_valid=!rst&&!stopped&&state==METADATA&&m_rsp_valid&&!metadata_bad;
 assign a_req_cookie=m_rsp_cookie;assign a_req_parent=m_rsp_parent;assign a_req_child=m_rsp_child;assign a_req_sink=m_rsp_sink;assign a_req_net=m_rsp_net;assign a_req_query=m_rsp_query;assign a_req_price=m_rsp_price;assign a_req_config=m_rsp_config;
 assign m_rsp_ready=!rst&&((state==METADATA&&(metadata_bad||a_req_ready))||state==DRAIN);
 assign a_rsp_ready=!rst&&((state==OUTPUT&&out_ready)||state==DRAIN);
 assign e_out_ready=!rst&&((state==OUTPUT&&out_ready)||(state==NEXT_CHILD&&early)||state==DRAIN);
 assign e_result_ready=!rst&&(state==NEXT_CHILD||(state==DRAIN&&!e_done));
 assign out_valid=!rst&&state==OUTPUT;
 assign result_valid=!rst&&state==FINAL;
 task fail;
  begin stopped<=1;if(state!=FINAL)begin result_status<=4;if(state!=OUTPUT)state<=DRAIN;end end
 endtask
 always @(posedge clk)begin
  if(rst)begin
   state<=IDLE;operation_pending<=0;stopped<=0;m_pending<=0;a_pending<=0;e_pending<=0;e_done<=0;parent<=0;sink<=0;net<=0;sequence_word<=0;flags<=0;xmin<=0;xmax<=0;ymin<=0;ymax<=0;child<=0;position<=0;ordinal<=0;processed<=0;elapsed<=0;attrs<=0;query<=0;price<=0;early<=0;
   out_cookie<=0;out_node<=0;out_position<=0;out_sequence<=0;out_bits<=0;out_action<=0;out_steps<=0;out_services<=0;out_attrs<=0;out_config<=0;
   result_status<=0;result_cookie<=0;result_count<=0;result_expanded_count<=0;result_raw_count<=0;result_mask<=0;result_hit<=0;result_early<=0;
  end else begin
   if(m_req_valid&&m_req_ready)m_pending<=1;
   if(m_rsp_valid&&m_rsp_ready)m_pending<=0;
   if(a_req_valid&&a_req_ready)a_pending<=1;
   if(a_rsp_valid&&a_rsp_ready)a_pending<=0;
   if(e_expand_valid&&e_expand_ready)begin e_pending<=1;e_done<=0;end
   if(e_result_valid&&e_result_ready)begin e_pending<=0;e_done<=1;end
   if(operation_pending&&!stopped&&state!=OUTPUT&&state!=FINAL)elapsed<=elapsed+1'b1;
   case(state)
    IDLE:if(expand_valid&&expand_ready)begin
     operation_pending<=1;parent<=expand_parent;sink<=expand_sink;net<=expand_net;sequence_word<=expand_sequence;flags<=expand_flags|expand_prune;xmin<=expand_xmin;xmax<=expand_xmax;ymin<=expand_ymin;ymax<=expand_ymax;query<=active_query;price<=active_price;processed<=0;early<=0;elapsed<=0;
     result_cookie<=expand_cookie;result_status<=invalid?1:0;result_count<=0;result_expanded_count<=0;result_raw_count<=0;result_mask<=0;result_hit<=0;result_early<=0;state<=invalid?FINAL:NEXT_CHILD;
    end
    NEXT_CHILD:begin
     if(e_result_valid&&e_result_ready)begin
      if(e_result_cookie!=result_cookie)begin stopped<=1;result_status<=4;end else begin result_status<=e_result_status;if(e_result_status!=0)stopped<=1;end
      result_count<=processed;result_expanded_count<=e_result_count;result_raw_count<=e_result_raw_count;result_mask<=e_result_mask;result_hit<=e_result_hit;result_early<=early;state<=FINAL;
     end else if(m_req_valid&&m_req_ready)begin child<=e_out_node;position<=e_out_position;ordinal<=e_out_sequence;attrs<=e_out_attrs;state<=METADATA;end
    end
    METADATA:if(m_rsp_valid)begin
     if(metadata_bad)fail;
     else if(a_req_valid&&a_req_ready)begin out_config<=m_rsp_config;state<=ACCESS;end
    end
    ACCESS:if(a_rsp_valid)begin
     if(access_bad)fail;
     else begin out_cookie<=result_cookie;out_node<=child;out_position<=position;out_sequence<=ordinal;out_bits<=a_rsp_bits;out_action<=a_rsp_action;out_steps<=a_rsp_steps;out_services<=a_rsp_services;out_attrs<=attrs;state<=OUTPUT;end
    end
    OUTPUT:if(out_ready)begin processed<=processed+1'b1;early<=early||out_bits[2];state<=(stopped||subsystem_fault||abort||drift||timeout||unexpected)?DRAIN:NEXT_CHILD;end
    DRAIN:begin
     if(drain_complete)state<=FINAL;
     if(e_result_valid&&e_result_ready)begin result_count<=processed;result_expanded_count<=e_result_count;result_raw_count<=e_result_raw_count;result_mask<=e_result_mask;result_hit<=e_result_hit;result_early<=early;end
    end
    FINAL:if(result_ready)begin operation_pending<=0;state<=IDLE;end
   endcase
   if(subsystem_fault||abort||drift||timeout||unexpected)begin
    stopped<=1;
    if(operation_pending&&state!=FINAL)begin result_status<=4;if(state!=OUTPUT)state<=(state==DRAIN&&drain_complete)?FINAL:DRAIN;end
   end
  end
 end
endmodule
