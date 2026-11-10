`timescale 1ns/1ps
// Single-target/new-slot query lifecycle. Never clears design-level state.
module query_lifecycle #(parameter integer MAX_CYCLES=8388608)(
 input wire clk,rst,abort,admit,backend_fault,backend_drained,active,host_label_edit,
 input wire[63:0]active_design,input wire[31:0]active_version,input wire[1:0]active_query,input wire[3:0]active_price,input wire[1:0]route_slots,
 input wire cmd_valid,output wire cmd_ready,input wire cmd_slot,
 input wire[31:0]cmd_cookie,cmd_route_cookie,cmd_source,cmd_key,cmd_nodes,cmd_max_polls,cmd_poll_cookie,
 input wire[63:0]cmd_design,input wire[1:0]cmd_query,input wire[3:0]cmd_price,input wire[447:0]cmd_expand,
 output wire rsp_valid,input wire rsp_ready,output reg[3:0]rsp_status,rsp_detail,
 output reg[31:0]rsp_cookie,rsp_nodes,rsp_acked,prepare_acked,cleanup_acked,output reg rsp_committed,
 output wire busy,fault,output wire[3:0]phase,output reg prepared_event,
 output wire service_valid,input wire service_ready,output reg[3:0]service_lane,output reg[447:0]service_payload,
 input wire service_rsp_valid,output wire service_rsp_ready,input wire[255:0]service_rsp_payload,
 output wire search_valid,input wire search_ready,output wire search_abort,
 output reg[31:0]search_cookie,search_source,search_key,search_nodes,search_max_polls,search_poll_cookie,
 output reg[63:0]search_design,output reg[1:0]search_query,output reg[3:0]search_price,output reg[447:0]search_expand,
 input wire search_rsp_valid,output wire search_rsp_ready,input wire[3:0]search_status,input wire[31:0]search_rsp_cookie,search_result_node,
 output wire route_valid,input wire route_ready,output reg[191:0]route_payload,
 input wire route_rsp_valid,output wire route_rsp_ready,input wire[3:0]route_status,input wire[31:0]route_rsp_cookie,route_nodes,route_acked
);
 localparam IDLE=0,SS=1,SW=2,QS=3,QW=4,RS=5,RW=6,DRAIN=7,DONE=8;
 localparam SOURCE_CHECK=0,TARGET_SET=1,SOURCE_LB=2,SOURCE_UP=3,SOURCE_SEQ=4,TARGET_CLEAR=5,FLUSH=6;
 reg[3:0]state;reg[2:0]operation;reg stopped;reg[3:0]error_code;reg[31:0]elapsed,last_sequence;reg sequence_seen,label_state_dirty;
 reg[63:0]last_design;reg[31:0]last_version;reg[1:0]last_query;reg[3:0]last_price;
 wire owned=state!=IDLE;
 wire drift=owned&&(!active||active_design!=search_design||active_version!=search_expand[447:416]||active_query!=search_query||active_price!=search_price);
 wire timeout=owned&&state!=DONE&&!stopped&&elapsed>=MAX_CYCLES-1;
 wire unexpected=(service_rsp_valid&&state!=SW&&!(state==SS&&service_ready))||(search_rsp_valid&&state!=QW&&!(state==QS&&search_ready))||(route_rsp_valid&&state!=RW&&!(state==RS&&route_ready));
 wire fail_now=owned&&state!=DONE&&(abort||backend_fault||drift||timeout||unexpected);
 wire[3:0]new_error=timeout?8:7;
 assign busy=!rst&&owned;assign fault=!rst&&stopped;assign phase=state;
 assign cmd_ready=!rst&&state==IDLE&&!stopped&&!abort&&!backend_fault&&active&&admit;
 assign rsp_valid=!rst&&state==DONE;
 assign service_valid=!rst&&state==SS;assign service_rsp_ready=!rst&&state==SW;
 assign search_valid=!rst&&state==QS;assign search_rsp_ready=!rst&&state==QW;
 // Do not inhibit acceptance of an already exposed search descriptor.
 assign search_abort=!rst&&state==QW&&(abort||stopped||backend_fault||drift||timeout);
 assign route_valid=!rst&&state==RS;assign route_rsp_ready=!rst&&state==RW;
 task fail(input[3:0]code);begin stopped<=1;error_code<=code;rsp_status<=code;state<=DRAIN;end endtask
 task write_label(input[2:0]op,input[31:0]node,input[2:0]field,input[31:0]value);reg[447:0]v;begin
  v=0;v[0]=1;v[32:1]=node;v[64:33]=value;v[67:65]=field;service_payload<=v;service_lane<=8;operation<=op;state<=SS;
 end endtask
 reg[447:0]v;
 always @(posedge clk)begin
  if(rst)begin
   state<=IDLE;operation<=SOURCE_CHECK;stopped<=0;error_code<=0;elapsed<=0;last_sequence<=0;sequence_seen<=0;label_state_dirty<=0;last_design<=0;last_version<=0;last_query<=0;last_price<=0;
   rsp_status<=0;rsp_detail<=0;rsp_cookie<=0;rsp_nodes<=0;rsp_acked<=0;rsp_committed<=0;prepare_acked<=0;cleanup_acked<=0;prepared_event<=0;
   service_lane<=8;service_payload<=0;route_payload<=0;search_cookie<=0;search_source<=0;search_key<=0;search_nodes<=0;search_max_polls<=0;search_poll_cookie<=0;search_design<=0;search_query<=0;search_price<=0;search_expand<=0;
  end else begin
   prepared_event<=0;
   if(sequence_seen&&!owned&&host_label_edit)label_state_dirty<=1;
   if(owned&&state!=DONE&&!stopped)elapsed<=elapsed+1;
   if(fail_now&&!stopped)begin stopped<=1;error_code<=new_error;rsp_status<=new_error;end
   case(state)
    IDLE:if(cmd_valid&&cmd_ready)begin
     rsp_status<=0;rsp_detail<=0;rsp_cookie<=cmd_cookie;rsp_nodes<=0;rsp_acked<=0;rsp_committed<=0;prepare_acked<=0;cleanup_acked<=0;elapsed<=0;
     search_cookie<=cmd_cookie;search_source<=cmd_source;search_key<=cmd_key;search_nodes<=cmd_nodes;search_max_polls<=cmd_max_polls;search_poll_cookie<=cmd_poll_cookie;search_design<=cmd_design;search_query<=cmd_query;search_price<=cmd_price;search_expand<=cmd_expand;
     route_payload<={30'd0,cmd_expand[255:224],cmd_expand[223:192],cmd_expand[191:160],cmd_source,cmd_route_cookie,cmd_slot,1'b0};
     if(label_state_dirty||cmd_nodes==0||cmd_source>=cmd_nodes||cmd_expand[191:160]>=cmd_nodes||cmd_max_polls==0||cmd_key!=0||cmd_expand[255:224]==0||route_slots[cmd_slot]||cmd_design!=active_design||cmd_query!=active_query||cmd_price!=active_price||cmd_expand[447:416]!=active_version||
       (sequence_seen&&(cmd_expand[255:224]<=last_sequence||cmd_design!=last_design||cmd_expand[447:416]!=last_version||cmd_query!=last_query||cmd_price!=last_price)))begin rsp_status<=1;state<=DONE;end
     else begin
      sequence_seen<=1;last_sequence<=cmd_expand[255:224];last_design<=cmd_design;last_version<=cmd_expand[447:416];last_query<=cmd_query;last_price<=cmd_price;
      v=0;v[32:1]=cmd_source;service_payload<=v;service_lane<=8;operation<=SOURCE_CHECK;state<=SS;
     end
    end
    SS:if(service_ready)state<=SW;
    SW:if(service_rsp_valid)begin
     rsp_detail<=service_rsp_payload[3:0];
     if(operation>=TARGET_SET&&operation<=SOURCE_SEQ&&service_rsp_payload[3:0]==0)prepare_acked<=prepare_acked+1;
     if(operation==TARGET_CLEAR&&service_rsp_payload[3:0]==0)cleanup_acked<=cleanup_acked+1;
     if(stopped||fail_now)fail(stopped?error_code:new_error);
     else if(service_rsp_payload[3:0]!=0)fail(operation>=TARGET_CLEAR?6:3);
     else case(operation)
      SOURCE_CHECK:if(!service_rsp_payload[4]||service_rsp_payload[100:69]!=32'hffffffff)fail(2);else write_label(TARGET_SET,search_expand[191:160],4,1);
      TARGET_SET:write_label(SOURCE_LB,search_source,0,0);
      SOURCE_LB:write_label(SOURCE_UP,search_source,1,0);
      SOURCE_UP:write_label(SOURCE_SEQ,search_source,3,search_expand[255:224]);
      SOURCE_SEQ:begin prepared_event<=1;state<=QS;end
      TARGET_CLEAR:begin v=0;v[1:0]=1;v[3:2]=search_query;v[7:4]=search_price;v[39:8]=search_expand[447:416];service_lane<=6;service_payload<=v;operation<=FLUSH;state<=SS;end
      FLUSH:state<=DRAIN;
      default:fail(7);
     endcase
    end
    QS:if(search_ready)state<=QW;
    QW:if(search_rsp_valid)begin
     rsp_detail<=search_status;
     if(stopped||fail_now)fail(stopped?error_code:new_error);
     else if(search_status||search_rsp_cookie!=search_cookie||search_result_node!=search_expand[191:160])fail(4);
     else state<=RS;
    end
    RS:if(route_ready)state<=RW;
    RW:if(route_rsp_valid)begin
     rsp_detail<=route_status;rsp_nodes<=route_nodes;rsp_acked<=route_acked;
     if(route_status==0&&route_rsp_cookie==route_payload[33:2])rsp_committed<=1;
     if(stopped||fail_now)fail(stopped?error_code:new_error);
     else if(route_status||route_rsp_cookie!=route_payload[33:2]||route_nodes!=route_acked)fail(5);
     else write_label(TARGET_CLEAR,search_expand[191:160],4,0);
    end
    DRAIN:if(backend_drained)begin if(fail_now&&!stopped)rsp_status<=new_error;state<=DONE;end
    DONE:if(rsp_ready)state<=IDLE;
    default:fail(7);
   endcase
  end
 end
endmodule
