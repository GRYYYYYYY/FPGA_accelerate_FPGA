`timescale 1ns/1ps
// Single-target/new-slot query lifecycle. Never clears design-level state.
module query_lifecycle #(parameter integer PATH_SLOTS=2,PATH_SLOT_BITS=(PATH_SLOTS<=2?1:$clog2(PATH_SLOTS)),MAX_CYCLES=8388608,ENABLE_REBASE=0,EXCLUSIVE_BACKEND_RESPONSES=0,CP_SAFE_EXCLUDES_HOST_EDIT=0)(
 input wire cp_rebase,cp_rebase_permit,input wire[31:0]cp_source_version,input wire[1:0]cp_source_query,input wire[3:0]cp_source_price,
 input wire clk,rst,abort,admit,backend_fault,backend_drained,active,host_label_edit,
 input wire[63:0]active_generation,
 input wire cp_valid,cp_restore,cp_safe,output wire cp_ready,cp_busy,
 input wire[31:0]cp_expected_crc,output wire cp_rsp_valid,input wire cp_rsp_ready,output reg[3:0]cp_status,output reg[31:0]cp_crc,
 input wire cp_s_valid,output wire cp_s_ready,input wire[31:0]cp_s_index,cp_s_data,input wire cp_s_last,
 output wire cp_m_valid,input wire cp_m_ready,output wire[31:0]cp_m_index,cp_m_data,output wire cp_m_last,

 input wire[63:0]active_design,input wire[31:0]active_version,input wire[1:0]active_query,input wire[3:0]active_price,input wire[PATH_SLOTS-1:0]route_slots,
 input wire cmd_valid,output wire cmd_ready,input wire[PATH_SLOT_BITS-1:0]cmd_slot,
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
 wire unexpected=EXCLUSIVE_BACKEND_RESPONSES?((service_rsp_valid&&state!=SW)||(search_rsp_valid&&state!=QW)||(route_rsp_valid&&state!=RW)):((service_rsp_valid&&state!=SW&&!(state==SS&&service_ready))||(search_rsp_valid&&state!=QW&&!(state==QS&&search_ready))||(route_rsp_valid&&state!=RW&&!(state==RS&&route_ready)));
 wire fail_now=owned&&state!=DONE&&(abort||backend_fault||drift||timeout||unexpected);
 wire[3:0]new_error=timeout?8:7;
 assign busy=!rst&&(owned||cp_busy);assign fault=!rst&&stopped;assign phase=state;
 assign cmd_ready=!rst&&!cp_busy&&!cp_valid&&state==IDLE&&!stopped&&!abort&&!backend_fault&&active&&admit;
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

 localparam CP_IDLE=0,CP_LOAD=1,CP_CHECK=2,CP_SEND=3,CP_DONE=4;
 reg[2:0]cp_state;reg[3:0]cp_pos;reg[31:0]cp_stage[0:9];reg[31:0]cp_running,cp_wanted,cp_ctx_version;
 reg[63:0]cp_ctx_design,cp_ctx_generation;reg[1:0]cp_ctx_query;reg[3:0]cp_ctx_price;reg cp_importing,cp_failed;
 reg cp_rebasing;reg[31:0]cp_src_version;reg[1:0]cp_src_query;reg[3:0]cp_src_price;
 wire want_rebase=(ENABLE_REBASE!=0)&&cp_rebase;
 wire[31:0]cp_image_version=cp_rebasing?cp_src_version:cp_ctx_version;
 wire[1:0]cp_image_query=cp_rebasing?cp_src_query:cp_ctx_query;
 wire[3:0]cp_image_price=cp_rebasing?cp_src_price:cp_ctx_price;
 wire cp_drift=(cp_rebasing&&!cp_rebase_permit)||!active||!cp_safe||!backend_drained||((CP_SAFE_EXCLUDES_HOST_EDIT==0)&&host_label_edit)||active_design!=cp_ctx_design||active_generation!=cp_ctx_generation||active_version!=cp_ctx_version||active_query!=cp_ctx_query||active_price!=cp_ctx_price;
 wire cp_bad=cp_stage[0]!=32'h51435031||cp_stage[1]!=1||{cp_stage[3],cp_stage[2]}!=cp_ctx_design||{cp_stage[5],cp_stage[4]}!=cp_ctx_generation||cp_stage[6]!=cp_image_version||cp_stage[7][31:8]!=0||cp_stage[7][1:0]!=cp_image_query||cp_stage[7][5:2]!=cp_image_price||cp_stage[9]!=0||(cp_stage[7][6]?(cp_stage[8]==0):(cp_stage[8]!=0));
 function automatic[31:0]cp_crc_word(input[31:0]crc,word);reg[31:0]v;begin v=crc^word;for(integer k=0;k<32;k=k+1)v=v[0]?(v>>1)^32'hedb88320:v>>1;cp_crc_word=v;end endfunction
 assign cp_ready=!rst&&cp_state==CP_IDLE&&state==IDLE&&!stopped&&!abort&&!backend_fault&&backend_drained&&active&&cp_safe&&!service_rsp_valid&&!search_rsp_valid&&!route_rsp_valid;
 assign cp_busy=!rst&&cp_state!=CP_IDLE;
 assign cp_rsp_valid=!rst&&cp_state==CP_DONE;
 assign cp_s_ready=!rst&&cp_state==CP_LOAD&&!cp_failed&&!abort&&!backend_fault&&!cp_drift;
 assign cp_m_valid=!rst&&cp_state==CP_SEND;
 assign cp_m_index=cp_pos;assign cp_m_data=cp_stage[cp_pos];assign cp_m_last=cp_pos==9;

 reg[447:0]v;
 always @(posedge clk)begin
  if(rst)begin
   cp_rebasing<=0;cp_src_version<=0;cp_src_query<=0;cp_src_price<=0;cp_state<=CP_IDLE;cp_pos<=0;cp_running<=32'hffffffff;cp_wanted<=0;cp_ctx_version<=0;cp_ctx_design<=0;cp_ctx_generation<=0;cp_ctx_query<=0;cp_ctx_price<=0;cp_importing<=0;cp_failed<=0;cp_status<=0;cp_crc<=0;
   for(integer k=0;k<10;k=k+1)cp_stage[k]<=0;
   state<=IDLE;operation<=SOURCE_CHECK;stopped<=0;error_code<=0;elapsed<=0;last_sequence<=0;sequence_seen<=0;label_state_dirty<=0;last_design<=0;last_version<=0;last_query<=0;last_price<=0;
   rsp_status<=0;rsp_detail<=0;rsp_cookie<=0;rsp_nodes<=0;rsp_acked<=0;rsp_committed<=0;prepare_acked<=0;cleanup_acked<=0;prepared_event<=0;
   service_lane<=8;service_payload<=0;route_payload<=0;search_cookie<=0;search_source<=0;search_key<=0;search_nodes<=0;search_max_polls<=0;search_poll_cookie<=0;search_design<=0;search_query<=0;search_price<=0;search_expand<=0;
  end else begin
   prepared_event<=0;
   if(sequence_seen&&!owned&&host_label_edit)label_state_dirty<=1;
   if(owned&&state!=DONE&&!stopped)elapsed<=elapsed+1;
   if(fail_now&&!stopped)begin stopped<=1;error_code<=new_error;rsp_status<=new_error;end
   if(cp_busy&&(abort||backend_fault||cp_drift))cp_failed<=1;
   case(cp_state)
    CP_IDLE:if(cp_valid&&cp_ready)begin
     cp_rebasing<=want_rebase&&cp_restore;cp_src_version<=cp_source_version;cp_src_query<=cp_source_query;cp_src_price<=cp_source_price;
     cp_ctx_design<=active_design;cp_ctx_generation<=active_generation;cp_ctx_version<=active_version;cp_ctx_query<=active_query;cp_ctx_price<=active_price;
     cp_running<=32'hffffffff;cp_wanted<=cp_expected_crc;cp_pos<=0;cp_importing<=cp_restore;cp_failed<=0;cp_status<=0;cp_crc<=0;
     if(active_design==0||active_generation==0||active_version==0||(want_rebase&&(!cp_restore||!cp_rebase_permit||cp_source_version==0||cp_source_version>=active_version||cp_source_price!=cp_source_version[3:0]||active_price!=active_version[3:0])))begin cp_status<=1;cp_state<=CP_DONE;end
     else if(cp_restore)cp_state<=CP_LOAD;
     else if(sequence_seen&&(last_design!=active_design||last_version!=active_version||last_query!=active_query||last_price!=active_price))begin cp_status<=1;cp_state<=CP_DONE;end
     else begin
      cp_stage[0]<=32'h51435031;cp_stage[1]<=1;cp_stage[2]<=active_design[31:0];cp_stage[3]<=active_design[63:32];cp_stage[4]<=active_generation[31:0];cp_stage[5]<=active_generation[63:32];cp_stage[6]<=active_version;
      cp_stage[7]<={24'd0,label_state_dirty,sequence_seen,active_price,active_query};cp_stage[8]<=sequence_seen?last_sequence:0;cp_stage[9]<=0;cp_state<=CP_CHECK;
     end
    end
    CP_LOAD:if(cp_failed||abort||backend_fault||cp_drift)begin cp_status<=2;cp_state<=CP_DONE;end
     else if(cp_s_valid&&cp_s_ready)begin
      if(cp_s_index!=cp_pos||cp_s_last!=(cp_pos==9))begin cp_status<=1;cp_state<=CP_DONE;end
      else begin
       cp_stage[cp_pos]<=cp_s_data;cp_running<=cp_crc_word(cp_running,cp_s_data);
       if(cp_pos==9)begin cp_crc<=~cp_crc_word(cp_running,cp_s_data);cp_state<=CP_CHECK;end else cp_pos<=cp_pos+1;
      end
     end
    CP_CHECK:if(cp_failed||abort||backend_fault||cp_drift)begin cp_status<=2;cp_state<=CP_DONE;end
     else if(cp_bad||(cp_importing&&(~cp_running!=cp_wanted||(label_state_dirty&&!cp_stage[7][7])||(sequence_seen&&(!cp_stage[7][6]||cp_stage[8]<last_sequence)))))begin cp_status<=1;cp_state<=CP_DONE;end
     else if(!cp_importing)begin cp_pos<=0;cp_state<=CP_SEND;end
     else begin
      // Publish the complete anti-replay ledger in one edge; never partial state.
      sequence_seen<=cp_stage[7][6];label_state_dirty<=cp_stage[7][7];last_sequence<=cp_stage[8];last_design<=cp_stage[7][6]?cp_ctx_design:0;last_version<=cp_stage[7][6]?cp_ctx_version:0;last_query<=cp_stage[7][6]?cp_ctx_query:0;last_price<=cp_stage[7][6]?cp_ctx_price:0;
      cp_status<=0;cp_state<=CP_DONE;
     end
    CP_SEND:if(cp_m_ready)begin
     cp_running<=cp_crc_word(cp_running,cp_m_data);
     if(cp_pos==9)begin cp_crc<=~cp_crc_word(cp_running,cp_m_data);cp_status<=(cp_failed||abort||backend_fault||cp_drift)?2:0;cp_state<=CP_DONE;end else cp_pos<=cp_pos+1;
    end
    CP_DONE:if(cp_rsp_ready)cp_state<=CP_IDLE;
    default:begin cp_status<=2;cp_state<=CP_DONE;end
   endcase
   if(!cp_busy)case(state)
    IDLE:if(cmd_valid&&cmd_ready)begin
     rsp_status<=0;rsp_detail<=0;rsp_cookie<=cmd_cookie;rsp_nodes<=0;rsp_acked<=0;rsp_committed<=0;prepare_acked<=0;cleanup_acked<=0;elapsed<=0;
     search_cookie<=cmd_cookie;search_source<=cmd_source;search_key<=cmd_key;search_nodes<=cmd_nodes;search_max_polls<=cmd_max_polls;search_poll_cookie<=cmd_poll_cookie;search_design<=cmd_design;search_query<=cmd_query;search_price<=cmd_price;search_expand<=cmd_expand;
     route_payload<={{(31-PATH_SLOT_BITS){1'b0}},cmd_expand[255:224],cmd_expand[223:192],cmd_expand[191:160],cmd_source,cmd_route_cookie,cmd_slot,1'b0};
     if(cmd_slot>=PATH_SLOTS||label_state_dirty||cmd_nodes==0||cmd_source>=cmd_nodes||cmd_expand[191:160]>=cmd_nodes||cmd_max_polls==0||cmd_key!=0||cmd_expand[255:224]==0||route_slots[cmd_slot]||cmd_design!=active_design||cmd_query!=active_query||cmd_price!=active_price||cmd_expand[447:416]!=active_version||
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
     if(route_status==0&&route_rsp_cookie==route_payload[1+PATH_SLOT_BITS+:32])rsp_committed<=1;
     if(stopped||fail_now)fail(stopped?error_code:new_error);
     else if(route_status||route_rsp_cookie!=route_payload[1+PATH_SLOT_BITS+:32]||route_nodes!=route_acked)fail(5);
     else write_label(TARGET_CLEAR,search_expand[191:160],4,0);
    end
    DRAIN:if(backend_drained)begin if(fail_now&&!stopped)rsp_status<=new_error;state<=DONE;end
    DONE:if(rsp_ready)state<=IDLE;
    default:fail(7);
   endcase
  end
 end
endmodule
