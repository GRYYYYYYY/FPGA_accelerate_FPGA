`timescale 1ns/1ps
// Prepared-query search. Service requests keep VALID/payload until accepted.
module search_scheduler #(parameter integer MAX_CYCLES=4194304)(
 input wire clk,rst,abort,admit,backend_fault,backend_drained,active,
 input wire[63:0]active_design,input wire[31:0]active_version,input wire[1:0]active_query,input wire[3:0]active_price,
 input wire start_valid,output wire start_ready,input wire[31:0]start_cookie,start_source,start_key,start_nodes,start_max_polls,start_poll_cookie,
 input wire[63:0]start_design,input wire[1:0]start_query,input wire[3:0]start_price,input wire[447:0]start_expand,
 output wire rsp_valid,input wire rsp_ready,output reg[3:0]rsp_status,output reg[31:0]rsp_cookie,polls,expands,candidates,result_node,result_key,
 output wire busy,fault,output wire[3:0]phase,
 output wire req_valid,input wire req_ready,output reg[3:0]req_lane,output reg[447:0]req_payload,
 input wire reply_valid,output wire reply_ready,input wire[255:0]reply_payload,
 input wire candidate_valid,output wire candidate_ready,input wire candidate_error,
 output reg poll_event,output reg[31:0]poll_node,poll_key,poll_size
);
 localparam IDLE=0,SEND=1,WAIT_REPLY=2,DRAIN=3,DONE=4;
 localparam SEED=0,POLL=1,LABEL=2,EXPAND=3,CHECKPOINT=4,CLEAR=5;
 reg[3:0]state;reg[2:0]operation;reg stopped;reg[3:0]error_code;
 reg[31:0]source,key,nodes,max_polls,poll_cookie_base,parent,parent_key,elapsed;
 reg[447:0]template_words;reg[63:0]design;reg[1:0]query;reg[3:0]price;reg[31:0]version;
 wire owned=state!=IDLE;
 wire drift=owned&&(!active||active_design!=design||active_version!=version||active_query!=query||active_price!=price);
 wire timed_out=owned&&state!=DONE&&!stopped&&elapsed>=MAX_CYCLES-1;
 wire unexpected=reply_valid&&state!=WAIT_REPLY&&!(state==SEND&&req_ready);
 wire bad_candidate=candidate_valid&&candidate_ready&&candidate_error;
 wire fail_now=owned&&state!=DONE&&(abort||backend_fault||drift||timed_out||unexpected||bad_candidate);
 wire[3:0]new_error=timed_out?4'd10:bad_candidate?4'd9:unexpected?4'd11:4'd8;
 assign phase=state;assign busy=!rst&&owned;assign fault=!rst&&stopped;
 assign start_ready=!rst&&state==IDLE&&!stopped&&!abort&&!backend_fault&&admit&&active;
 assign rsp_valid=!rst&&state==DONE;
 assign req_valid=!rst&&state==SEND;assign reply_ready=!rst&&state==WAIT_REPLY;
 assign candidate_ready=!rst&&state==WAIT_REPLY&&operation==EXPAND;
 task issue(input[2:0]op,input[3:0]lane,input[447:0]payload);begin operation<=op;req_lane<=lane;req_payload<=payload;state<=SEND;end endtask
 task fail(input[3:0]code);begin stopped<=1;error_code<=code;rsp_status<=code;state<=DRAIN;end endtask
 task poll_next;reg[447:0]v;begin
  if(polls>=max_polls)fail(2);
  else begin v=0;v[31:0]=2;v[127:96]=poll_cookie_base+polls;v[159:128]=version;issue(POLL,12,v);end
 end endtask
 reg[447:0]next_payload;
 always @(posedge clk)begin
  if(rst)begin
   state<=IDLE;operation<=SEED;stopped<=0;error_code<=0;rsp_status<=0;rsp_cookie<=0;polls<=0;expands<=0;candidates<=0;result_node<=0;result_key<=0;
   req_lane<=0;req_payload<=0;source<=0;key<=0;nodes<=0;max_polls<=0;poll_cookie_base<=0;parent<=0;parent_key<=0;elapsed<=0;template_words<=0;design<=0;query<=0;price<=0;version<=0;
   poll_event<=0;poll_node<=0;poll_key<=0;poll_size<=0;
  end else begin
   poll_event<=0;
   if(owned&&state!=DONE&&!stopped)elapsed<=elapsed+1;
   if(fail_now&&!stopped)begin stopped<=1;error_code<=new_error;rsp_status<=new_error;end
   if(candidate_valid&&candidate_ready)candidates<=candidates+1;
   case(state)
    IDLE:if(start_valid&&start_ready)begin
     rsp_cookie<=start_cookie;rsp_status<=0;error_code<=0;polls<=0;expands<=0;candidates<=0;result_node<=0;result_key<=0;elapsed<=0;
     source<=start_source;key<=start_key;nodes<=start_nodes;max_polls<=start_max_polls;poll_cookie_base<=start_poll_cookie;
     template_words<=start_expand;design<=start_design;query<=start_query;price<=start_price;version<=start_expand[447:416];
     if(start_nodes==0||start_source>=start_nodes||start_expand[191:160]>=start_nodes||start_max_polls==0||start_expand[255:224]==0||start_design!=active_design||start_query!=active_query||start_price!=active_price||start_expand[447:416]!=active_version)begin rsp_status<=1;state<=DONE;end
     else begin next_payload=0;next_payload[31:0]=1;next_payload[63:32]=start_key;next_payload[95:64]=start_source;next_payload[127:96]=start_poll_cookie;next_payload[159:128]=start_expand[447:416];issue(SEED,12,next_payload);end
    end
    SEND:if(req_ready)state<=WAIT_REPLY;
    WAIT_REPLY:if(reply_valid)begin
     if(stopped||fail_now)fail(stopped?error_code:new_error);
     else case(operation)
      SEED:if(reply_payload[31:0]!=0||reply_payload[63:32]!=req_payload[127:96]||reply_payload[95:64]!=1)fail(4);else poll_next;
      POLL:begin
       if(reply_payload[63:32]!=req_payload[127:96])fail(4);
       else if(reply_payload[31:0]==1)fail(3);
       else if(reply_payload[31:0]!=0||reply_payload[159:128]>=nodes)fail(4);
       else begin
        polls<=polls+1;parent<=reply_payload[159:128];parent_key<=reply_payload[127:96];
        poll_event<=1;poll_node<=reply_payload[159:128];poll_key<=reply_payload[127:96];poll_size<=reply_payload[95:64];
        next_payload=0;next_payload[32:1]=reply_payload[159:128];issue(LABEL,8,next_payload);
       end
      end
      LABEL:begin
       if(reply_payload[3:0]!=0||!reply_payload[4]||reply_payload[36:5]!=parent_key)fail(5);
       else if(reply_payload[133])begin
        if(parent!=template_words[191:160]||reply_payload[132:101]!=template_words[255:224])fail(6);
        else begin
         result_node<=parent;result_key<=parent_key;next_payload=0;
         if(poll_size!=0)begin next_payload[31:0]=4;next_payload[127:96]=poll_cookie_base+polls;next_payload[159:128]=version;issue(CLEAR,12,next_payload);end
         else begin next_payload[1:0]=1;next_payload[3:2]=query;next_payload[7:4]=price;next_payload[39:8]=version;issue(CHECKPOINT,6,next_payload);end
        end
       end else begin
        next_payload=template_words;next_payload[63:32]=template_words[63:32]+expands;next_payload[95:64]=parent;issue(EXPAND,11,next_payload);expands<=expands+1;
       end
      end
      EXPAND:if(reply_payload[3:0]!=0||reply_payload[35:4]!=req_payload[63:32])fail(7);else poll_next;
      CLEAR:if(reply_payload[31:0]!=0||reply_payload[63:32]!=req_payload[127:96]||reply_payload[95:64]!=0)fail(4);
       else begin next_payload=0;next_payload[1:0]=1;next_payload[3:2]=query;next_payload[7:4]=price;next_payload[39:8]=version;issue(CHECKPOINT,6,next_payload);end
      CHECKPOINT:if(reply_payload[3:0]!=0)fail(7);else state<=DRAIN;
      default:fail(11);
     endcase
    end
    DRAIN:if(backend_drained)begin if(fail_now&&!stopped)rsp_status<=new_error;state<=DONE;end
    DONE:if(rsp_ready)state<=IDLE;
    default:fail(11);
   endcase
  end
 end
endmodule
