`timescale 1ns/1ps
// Device-side Config14 production. Static graph must reflect the eager loader's
// runtime types. Child creation/dead state is design-persistent, never query-clear.
module metadata_controller #(parameter integer TOKEN_BITS=32,MAX_CYCLES=262144)(
 input wire clk,rst,enable,abort,active,input wire[1:0]active_query,input wire[3:0]active_price,input wire[31:0]nodes,input wire claim_active,
 input wire req_valid,output wire req_ready,input wire[31:0]req_cookie,req_parent,req_child,req_sink,req_net,req_sequence,req_flags,req_xmin,req_xmax,req_ymin,req_ymax,
 input wire[1:0]req_query,input wire[3:0]req_price,
 output wire rsp_valid,input wire rsp_ready,output reg[3:0]rsp_status,output reg[31:0]rsp_cookie,rsp_parent,rsp_child,rsp_sink,rsp_net,
 output reg[1:0]rsp_query,output reg[3:0]rsp_price,output reg[447:0]rsp_config,output reg rsp_created,
 output wire busy,fault,
 output wire g_req_valid,input wire g_req_ready,output wire[1:0]g_req_op,output wire[31:0]g_req_cookie,g_req_node,g_req_index,
 input wire g_rsp_valid,output wire g_rsp_ready,input wire[3:0]g_rsp_status,input wire[31:0]g_rsp_cookie,g_rsp_parent,g_rsp_index,g_rsp_node,g_rsp_start,g_rsp_count,input wire[255:0]g_rsp_attrs,input wire g_fault,
 output wire d_req_valid,input wire d_req_ready,output wire[2:0]d_req_op,output wire[31:0]d_req_cookie,d_req_owner,d_req_node,d_req_arg,
 input wire d_rsp_valid,output wire d_rsp_ready,input wire[3:0]d_rsp_status,input wire[31:0]d_rsp_cookie,d_rsp_flags,d_rsp_count,d_rsp_mask,input wire d_fault
);
 localparam IDLE=0,GS=1,GW=2,DS=3,DW=4,REPLY=5;
 localparam[31:0]TOKEN_MAX=32'hffffffff>>(32-TOKEN_BITS);
 reg[2:0]state;reg[1:0]role;reg stopped,owned,g_pending,d_pending;
 reg[31:0]token,elapsed,graph_node,sequence_word,flags_word,xmin,xmax,ymin,ymax;
 reg[255:0]parent_attrs,child_attrs,sink_attrs;
 wire unexpected=(g_rsp_valid&&!g_pending)||(d_rsp_valid&&!d_pending);
 wire drift=owned&&state!=IDLE&&(!active||active_query!=rsp_query||active_price!=rsp_price||claim_active);
 wire timeout=state!=IDLE&&state!=REPLY&&elapsed>=MAX_CYCLES-1;
 assign fault=!rst&&(stopped||abort||g_fault||d_fault||unexpected||drift||timeout);
 assign busy=!rst&&state!=IDLE;
 assign req_ready=!rst&&!fault&&enable&&!claim_active&&state==IDLE;
 assign rsp_valid=!rst&&state==REPLY;
 assign g_req_valid=!rst&&!fault&&state==GS;assign g_req_op=0;assign g_req_cookie=token;assign g_req_node=graph_node;assign g_req_index=0;
 assign d_req_valid=!rst&&!fault&&state==DS;assign d_req_op=0;assign d_req_cookie=token;assign d_req_node=rsp_child;assign d_req_owner=0;assign d_req_arg=0;
 // Accepted read services can drain after the controller has exposed an error.
 assign g_rsp_ready=!rst&&g_pending;assign d_rsp_ready=!rst&&d_pending;
 task fail(input[3:0]status);
  begin stopped<=1;if(state!=REPLY)begin rsp_status<=status;state<=REPLY;end end
 endtask
 task graph_read(input[31:0]id,input[1:0]which);
  begin if(token==TOKEN_MAX)fail(6);else begin token<=token+1'b1;graph_node<=id;role<=which;state<=GS;end end
 endtask
 task design_read;
  begin if(token==TOKEN_MAX)fail(6);else begin token<=token+1'b1;state<=DS;end end
 endtask
 function[31:0]sx16(input[15:0]v);sx16={{16{v[15]}},v};endfunction
 always @(posedge clk)begin
  if(rst)begin
   state<=IDLE;role<=0;stopped<=0;owned<=0;g_pending<=0;d_pending<=0;token<=0;elapsed<=0;graph_node<=0;sequence_word<=0;flags_word<=0;xmin<=0;xmax<=0;ymin<=0;ymax<=0;
   parent_attrs<=0;child_attrs<=0;sink_attrs<=0;rsp_status<=0;rsp_cookie<=0;rsp_parent<=0;rsp_child<=0;rsp_sink<=0;rsp_net<=0;rsp_query<=0;rsp_price<=0;rsp_config<=0;rsp_created<=0;
  end else begin
   if(g_req_valid&&g_req_ready)g_pending<=1;
   if(d_req_valid&&d_req_ready)d_pending<=1;
   if(g_rsp_valid&&g_rsp_ready)g_pending<=0;
   if(d_rsp_valid&&d_rsp_ready)d_pending<=0;
   if(state==REPLY&&rsp_ready)begin state<=IDLE;owned<=0;end
   if(fault)begin
    stopped<=1;if(state!=IDLE&&state!=REPLY)begin rsp_status<=5;state<=REPLY;end
   end else begin
    if(state!=IDLE&&state!=REPLY)elapsed<=elapsed+1'b1;
    case(state)
     IDLE:if(req_valid&&req_ready)begin
      rsp_cookie<=req_cookie;rsp_parent<=req_parent;rsp_child<=req_child;rsp_sink<=req_sink;rsp_net<=req_net;rsp_query<=req_query;rsp_price<=req_price;rsp_status<=0;rsp_config<=0;rsp_created<=0;elapsed<=0;
      sequence_word<=req_sequence;flags_word<=req_flags;xmin<=req_xmin;xmax<=req_xmax;ymin<=req_ymin;ymax<=req_ymax;owned<=0;
      if(req_parent>=nodes||req_child>=nodes||req_sink>=nodes||(req_flags&~32'h11d)!=0)begin rsp_status<=1;state<=REPLY;end
      else if(!active||req_query!=active_query||req_price!=active_price)fail(2);
      else begin owned<=1;graph_read(req_parent,0);end
     end
     GS:if(g_req_valid&&g_req_ready)state<=GW;
     GW:if(g_rsp_valid&&g_rsp_ready)begin
      if(g_rsp_status!=0)fail(3);
      else if(g_rsp_cookie!=token||g_rsp_parent!=graph_node||g_rsp_node!=graph_node||g_rsp_index!=0)fail(4);
      else case(role)
       0:begin parent_attrs<=g_rsp_attrs;graph_read(rsp_child,1);end
       1:begin child_attrs<=g_rsp_attrs;graph_read(rsp_sink,2);end
       2:begin sink_attrs<=g_rsp_attrs;design_read;end
       default:fail(4);
      endcase
     end
     DS:if(d_req_valid&&d_req_ready)state<=DW;
     DW:if(d_rsp_valid&&d_rsp_ready)begin
      if(d_rsp_status!=0)fail(3);
      else if(d_rsp_cookie!=token||!(child_attrs[72]||d_rsp_flags[0]))fail(4);
      else begin
       rsp_config[31:0]<=sequence_word;
       rsp_config[63:32]<=flags_word|(d_rsp_flags[1]?32'd2:0)|(parent_attrs[73]?32'd32:0)|(child_attrs[73]?32'd64:0)|(child_attrs[79]?32'd128:0);
       rsp_config[95:64]<={24'b0,child_attrs[71:64]};rsp_config[127:96]<={24'b0,parent_attrs[71:64]};rsp_config[159:128]<={24'b0,sink_attrs[71:64]};
       rsp_config[191:160]<=sx16(child_attrs[127:112]);rsp_config[223:192]<=child_attrs[31:0];rsp_config[255:224]<=sink_attrs[31:0];
       rsp_config[287:256]<=sx16(sink_attrs[95:80]);rsp_config[319:288]<=sx16(sink_attrs[111:96]);
       rsp_config[351:320]<=xmin;rsp_config[383:352]<=xmax;rsp_config[415:384]<=ymin;rsp_config[447:416]<=ymax;
       rsp_created<=1;state<=REPLY;
      end
     end
    endcase
   end
  end
 end
endmodule
