`timescale 1ns/1ps
// Independent coordinator reset domain. target_reset must not reset this module.
module recovery_coordinator #(parameter integer ENTRIES=32,RESET_HOLD=5,MAX_CORRECTIONS=1024,MAX_CYCLES=1048576)(
 input wire cfg_stage,publish_valid,publish_permit,discard_valid,
 output wire publish_ready,discard_ready,staged_valid,
 output wire[63:0]staged_design,output wire[31:0]staged_checkpoint,staged_version,active_version,
 output wire[1:0]staged_query,active_query,output wire[3:0]staged_price,active_price,
 input wire clk,cold_rst,abort,backend_drained,normal_retired,retry_safe,output wire attempt_reset,
 input wire cfg_valid,output wire cfg_ready,input wire cfg_authoritative,
 input wire[63:0]cfg_design,input wire[31:0]cfg_checkpoint,cfg_version,input wire[1:0]cfg_query,input wire[3:0]cfg_price,
 output reg cfg_rsp_valid,input wire cfg_rsp_ready,output reg cfg_status,
 input wire j_valid,output wire j_ready,input wire[31:0]j_node,j_net,input wire[2:0]j_op,
 output reg[31:0]journal_count,output wire journal_full,permit_work,
 input wire recover_valid,output wire recover_ready,input wire[31:0]recover_cookie,recover_checkpoint,recover_version,
 input wire[63:0]recover_design,input wire[1:0]recover_query,input wire[3:0]recover_price,
 output wire target_reset,reconfigure_valid,labels_valid,input wire reconfigure_done,labels_done,
 output reg[63:0]saved_design,output reg[31:0]saved_checkpoint,new_version,output reg[1:0]new_query,output reg[3:0]new_price,
 output reg rsp_valid,input wire rsp_ready,output reg[3:0]rsp_status,output reg[31:0]rsp_cookie,rsp_corrected,
 output wire busy,fault,
 output wire a_valid,input wire a_ready,output wire[31:0]a_node,a_net,a_cookie,a_checkpoint,output wire[63:0]a_design,
 input wire a_rsp_valid,output wire a_rsp_ready,input wire[3:0]a_status,input wire[31:0]a_rsp_cookie,a_rsp_checkpoint,a_refs,a_occupancy,input wire[63:0]a_rsp_design,
 output wire o_valid,input wire o_ready,output reg[2:0]o_op,output wire[31:0]o_node,o_net,o_cookie,
 input wire o_rsp_valid,output wire o_rsp_ready,input wire[3:0]o_status,input wire[31:0]o_rsp_cookie,o_count,o_occupancy
);
 localparam NORMAL=0,DRAIN=1,RESET=2,RECONFIG=3,AS=4,AW=5,OS=6,OW=7,NEXT=8,LABELS=9,FAILWAIT=10,DONE=11,REARM=12;
 reg[3:0]state;reg configured,owned,stopped,verify_pass;reg[3:0]error_code;
 reg[31:0]nodes[0:ENTRIES-1],nets[0:ENTRIES-1];
 reg[31:0]current_version,index,reset_ticks,elapsed,wanted_refs,wanted_occ,observed_refs,observed_occ,owner_cookie;
 reg[31:0]attempt_version;reg[1:0]attempt_query;
 reg[1:0]current_query;reg[3:0]current_price;reg duplicate;
 reg prepared;reg[63:0]shadow_design;reg[31:0]shadow_checkpoint,shadow_version;reg[1:0]shadow_query;reg[3:0]shadow_price;
 assign staged_valid=!cold_rst&&!abort&&prepared&&!cfg_rsp_valid&&state==NORMAL&&!fault;
 assign staged_design=staged_valid?shadow_design:64'd0;
 assign staged_checkpoint=staged_valid?shadow_checkpoint:32'd0;
 assign staged_version=staged_valid?shadow_version:32'd0;
 assign staged_query=staged_valid?shadow_query:2'd0;
 assign staged_price=staged_valid?shadow_price:4'd0;
 assign active_version=current_version;assign active_query=current_query;assign active_price=current_price;
 assign publish_ready=staged_valid&&publish_permit&&!cfg_valid&&!recover_valid&&!j_valid&&!discard_valid&&backend_drained&&normal_retired;
 assign discard_ready=staged_valid&&publish_permit&&!cfg_valid&&!recover_valid&&!j_valid&&!publish_valid&&backend_drained&&normal_retired;
 always @* begin duplicate=0;for(integer k=0;k<ENTRIES;k=k+1)if(k<journal_count&&nodes[k]==j_node&&nets[k]==j_net)duplicate=1;end
 wire timeout=owned&&!rsp_valid&&!stopped&&elapsed>=MAX_CYCLES-1;
 wire unexpected=(a_rsp_valid&&state!=AW&&!(state==AS&&a_ready))||(o_rsp_valid&&state!=OW&&!(state==OS&&o_ready));
 // Old callback fault latches are cleared only in a quiescent REARM cycle.
 wire fail_now=(abort&&state!=REARM)||timeout||unexpected;
 assign attempt_reset=!cold_rst&&state==REARM&&retry_safe&&!unexpected;
 assign fault=!cold_rst&&(stopped||fail_now);
 assign busy=!cold_rst&&(owned||state!=NORMAL||rsp_valid);
 assign permit_work=!cold_rst&&!prepared&&configured&&!fault&&state==NORMAL&&!cfg_rsp_valid&&!cfg_valid&&!recover_valid;
 assign journal_full=journal_count==ENTRIES;
 assign j_ready=!cold_rst&&!prepared&&configured&&!fault&&state==NORMAL&&!cfg_rsp_valid&&(j_op==1||j_op==2)&&(duplicate||journal_count<ENTRIES);
 assign recover_ready=!cold_rst&&!prepared&&configured&&state==NORMAL&&!cfg_rsp_valid&&!cfg_valid&&!j_valid&&!unexpected&&(!fault||(stopped&&retry_safe&&backend_drained&&normal_retired));
 assign cfg_ready=!cold_rst&&!fault&&state==NORMAL&&!cfg_rsp_valid&&!recover_valid&&!j_valid&&backend_drained&&normal_retired;
 assign target_reset=!cold_rst&&state==RESET;assign reconfigure_valid=!cold_rst&&state==RECONFIG;assign labels_valid=!cold_rst&&state==LABELS;
 assign a_valid=!cold_rst&&state==AS;assign a_rsp_ready=!cold_rst&&state==AW;
 assign a_node=nodes[index];assign a_net=nets[index];assign a_cookie=rsp_cookie^index^(verify_pass?32'h80000000:0);assign a_checkpoint=saved_checkpoint;assign a_design=saved_design;
 assign o_valid=!cold_rst&&state==OS;assign o_rsp_ready=!cold_rst&&state==OW;
 assign o_node=nodes[index];assign o_net=nets[index];assign o_cookie=owner_cookie;
 task fail(input[3:0]code);begin stopped<=1;error_code<=code;state<=FAILWAIT;end endtask
 task complete(input[3:0]code);begin rsp_status<=code;rsp_valid<=1;state<=DONE;end endtask
 wire[31:0]next_count=o_op==1?observed_refs+1:observed_refs-1;
 wire[31:0]next_occ=o_op==1?observed_occ+(observed_refs==0):observed_occ-(observed_refs==1);
 always @(posedge clk)begin
  if(cold_rst)begin
   prepared<=0;shadow_design<=0;shadow_checkpoint<=0;shadow_version<=0;shadow_query<=0;shadow_price<=0;attempt_version<=0;attempt_query<=0;state<=NORMAL;configured<=0;owned<=0;stopped<=0;verify_pass<=0;error_code<=0;journal_count<=0;
   saved_design<=0;saved_checkpoint<=0;current_version<=0;current_query<=0;current_price<=0;new_version<=0;new_query<=0;new_price<=0;
   index<=0;reset_ticks<=0;elapsed<=0;wanted_refs<=0;wanted_occ<=0;observed_refs<=0;observed_occ<=0;owner_cookie<=0;o_op<=0;
   cfg_rsp_valid<=0;cfg_status<=0;rsp_valid<=0;rsp_status<=0;rsp_cookie<=0;rsp_corrected<=0;
  end else begin
   if(cfg_rsp_valid&&cfg_rsp_ready)cfg_rsp_valid<=0;
   if(owned&&!rsp_valid&&!stopped)elapsed<=elapsed+1;
   if(fail_now&&!stopped)begin stopped<=1;error_code<=6;end
   case(state)
    NORMAL:begin
     if(cfg_valid&&cfg_ready)begin
      cfg_rsp_valid<=1;cfg_status<=0;
      if(prepared||(!cfg_stage&&configured))cfg_status<=1;
      else if(cfg_stage)begin
       if(!publish_permit||!configured||!cfg_authoritative||cfg_design==0||cfg_design!=saved_design||cfg_checkpoint<=saved_checkpoint||cfg_version==0||cfg_version!=current_version||cfg_version<attempt_version||cfg_query!=current_query||cfg_price!=current_price||cfg_price!=cfg_version[3:0])cfg_status<=1;
       else begin prepared<=1;shadow_design<=cfg_design;shadow_checkpoint<=cfg_checkpoint;shadow_version<=cfg_version;shadow_query<=cfg_query;shadow_price<=cfg_price;end
      end
      else if(!cfg_authoritative||cfg_price!=cfg_version[3:0]||(configured&&((cfg_design==saved_design&&(cfg_checkpoint<=saved_checkpoint||cfg_version<current_version))||(cfg_design!=saved_design&&journal_count!=0))))cfg_status<=1;
      else begin configured<=1;saved_design<=cfg_design;saved_checkpoint<=cfg_checkpoint;current_version<=cfg_version;current_query<=cfg_query;current_price<=cfg_price;attempt_version<=cfg_version;attempt_query<=cfg_query;journal_count<=0;end
     end
     if(j_valid&&j_ready&&!duplicate)begin nodes[journal_count]<=j_node;nets[journal_count]<=j_net;journal_count<=journal_count+1;end
     if(recover_valid&&recover_ready)begin
      owned<=1;rsp_cookie<=recover_cookie;rsp_corrected<=0;rsp_status<=0;elapsed<=0;index<=0;verify_pass<=0;reset_ticks<=0;owner_cookie<=recover_cookie;
      if(recover_design!=saved_design||recover_checkpoint!=saved_checkpoint||recover_version<=attempt_version||recover_query==current_query||recover_query==attempt_query||recover_price!=recover_version[3:0])complete(1);
      else begin
       new_version<=recover_version;new_query<=recover_query;new_price<=recover_price;
       attempt_version<=recover_version;attempt_query<=recover_query;
       if(stopped)begin stopped<=0;error_code<=0;state<=REARM;end else state<=DRAIN;
      end
     end
    end
    REARM:begin
     if(!retry_safe||unexpected||timeout)fail(6);
     else state<=DRAIN;
    end
    DRAIN:if(backend_drained&&normal_retired)begin if(stopped||fail_now)state<=FAILWAIT;else begin reset_ticks<=0;state<=RESET;end end
    RESET:begin
     if(reset_ticks+1>=RESET_HOLD)begin reset_ticks<=0;if(stopped||fail_now)state<=FAILWAIT;else state<=RECONFIG;end
     else reset_ticks<=reset_ticks+1;
    end
    RECONFIG:if(reconfigure_done)begin
     if(stopped||fail_now)state<=FAILWAIT;
     else if(journal_count==0)state<=LABELS;else begin index<=0;verify_pass<=0;state<=AS;end
    end
    AS:if(a_ready)state<=AW;
    AW:if(a_rsp_valid)begin
     if(stopped||fail_now)state<=FAILWAIT;
     else if(a_status!=0||a_rsp_cookie!=a_cookie||a_rsp_checkpoint!=saved_checkpoint||a_rsp_design!=saved_design)fail(2);
     else if(a_refs>65535||a_occupancy>65535||(a_refs!=0&&a_occupancy==0))fail(2);
     else begin wanted_refs<=a_refs;wanted_occ<=a_occupancy;o_op<=0;state<=OS;end
    end
    OS:if(o_ready)state<=OW;
    OW:if(o_rsp_valid)begin
     owner_cookie<=owner_cookie+1;
     if(o_op!=0&&o_status==0&&o_rsp_cookie==owner_cookie)rsp_corrected<=rsp_corrected+1;
     if(stopped||fail_now)state<=FAILWAIT;
     else if(o_status!=0||o_rsp_cookie!=owner_cookie||o_count>65535||o_occupancy>65535||(o_count!=0&&o_occupancy==0))fail(3);
     else if(o_op==0)begin
      observed_refs<=o_count;observed_occ<=o_occupancy;
      if(verify_pass)begin if(o_count!=wanted_refs||o_occupancy!=wanted_occ)fail(4);else state<=NEXT;end
      else if(o_count==wanted_refs)state<=NEXT;
      else if((o_count>wanted_refs?o_count-wanted_refs:wanted_refs-o_count)>MAX_CORRECTIONS)fail(5);
      else begin o_op<=o_count>wanted_refs?2:1;state<=OS;end
     end else if(o_count!=next_count||o_occupancy!=next_occ)fail(3);
     else begin
      observed_refs<=o_count;observed_occ<=o_occupancy;
      if(o_count==wanted_refs)state<=NEXT;else state<=OS;
     end
    end
    NEXT:begin
     if(stopped||fail_now)state<=FAILWAIT;
     else if(index+1<journal_count)begin index<=index+1;state<=AS;end
     else if(!verify_pass)begin verify_pass<=1;index<=0;state<=AS;end
     else state<=LABELS;
    end
    LABELS:begin
     if(stopped||fail_now)state<=FAILWAIT;
     else if(labels_done&&backend_drained&&normal_retired)begin current_version<=new_version;current_query<=new_query;current_price<=new_price;journal_count<=0;complete(0);end
    end
    FAILWAIT:if(backend_drained&&normal_retired)complete(error_code);
    DONE:if(rsp_valid&&rsp_ready)begin rsp_valid<=0;owned<=0;state<=NORMAL;end
    default:fail(6);
   endcase
   if(publish_valid&&publish_ready)begin
    saved_design<=shadow_design;saved_checkpoint<=shadow_checkpoint;current_version<=shadow_version;current_query<=shadow_query;current_price<=shadow_price;journal_count<=0;prepared<=0;
    // A new checkpoint does not reset the recovery-attempt floor.
   end
   if((discard_valid&&discard_ready)||abort||fail_now)prepared<=0;
  end
 end
endmodule
