`timescale 1ns/1ps
// Six 384-bit lanes: connection, graph, design, tables, owner, cost.
// Cold reset owns the resident descriptor; never connect target_reset here.
module config_restore_controller #(parameter integer MAX_CYCLES=1048576,NATIVE_FEEDBACK_PUBLICATION=0)(
 input wire load_stage,publish_valid,publish_permit,discard_valid,
 output wire publish_ready,discard_ready,staged_valid,
 output wire[63:0]staged_design,output wire[31:0]staged_checkpoint,staged_version,active_version,
 output wire[2303:0]staged_payload,active_payload,
 input wire clk,rst,abort,backend_drained,normal_retired,attempt_reset,
 input wire load_valid,output wire load_ready,input wire load_authoritative,input wire[2303:0]load_payload,input wire[63:0]load_design,input wire[31:0]load_checkpoint,
 output reg load_rsp_valid,input wire load_rsp_ready,output reg load_status,
 input wire start_valid,output wire start_ready,input wire[63:0]start_design,input wire[31:0]start_checkpoint,start_cookie,start_version,input wire[3:0]start_price,
 output wire[5:0]cfg_valid,input wire[5:0]cfg_ready,output wire[2303:0]cfg_payload,
 input wire[5:0]cfg_rsp_valid,output wire[5:0]cfg_rsp_ready,input wire[17:0]cfg_status,
 output reg rsp_valid,input wire rsp_ready,output reg[3:0]rsp_status,output reg[31:0]rsp_cookie,output wire busy,fault,
 output reg[5:0]sent,retired,output reg[63:0]saved_design,output reg[31:0]saved_checkpoint
);
 localparam IDLE=0,FIRST=1,OTHERS=2,DRAIN=3,DONE=4;
 reg[2:0]state;reg configured,stopped;reg[3:0]error_code;reg[31:0]elapsed,current_version,tx_version;reg[2303:0]descriptor;
 reg prepared;reg[2303:0]shadow_payload;reg[63:0]shadow_design;reg[31:0]shadow_checkpoint;
 assign active_version=current_version;
 assign active_payload=configured?{descriptor[2303:2272],current_version,descriptor[2239:0]}:2304'd0;
 assign staged_valid=!rst&&!abort&&prepared&&!load_rsp_valid&&state==IDLE&&!fault;
 assign staged_design=staged_valid?shadow_design:64'd0;
 assign staged_checkpoint=staged_valid?shadow_checkpoint:32'd0;
 assign staged_version=staged_valid?shadow_payload[2240+:32]:32'd0;
 assign staged_payload=staged_valid?shadow_payload:2304'd0;
 assign publish_ready=staged_valid&&publish_permit&&!load_valid&&!start_valid&&!attempt_reset&&!discard_valid&&backend_drained&&normal_retired;
 assign discard_ready=staged_valid&&publish_permit&&!load_valid&&!start_valid&&!attempt_reset&&!publish_valid&&backend_drained&&normal_retired;
 wire fail_now=busy&&!rsp_valid&&(abort||elapsed>=MAX_CYCLES);
 assign busy=!rst&&state!=IDLE;assign fault=!rst&&(stopped||fail_now);
 assign load_ready=!rst&&!abort&&!attempt_reset&&!stopped&&state==IDLE&&!load_rsp_valid&&backend_drained&&normal_retired;
 assign start_ready=!rst&&!prepared&&!attempt_reset&&!stopped&&configured&&state==IDLE&&!load_rsp_valid&&!load_valid&&backend_drained&&normal_retired;
 assign cfg_valid=rst?6'd0:state==FIRST?(6'b000001&~sent):state==OTHERS?(6'b111110&~sent):6'd0;
 assign cfg_rsp_ready=!rst&&(state==FIRST||state==OTHERS)?sent&~retired:6'd0;
 assign cfg_payload={descriptor[2303:2272],tx_version,descriptor[2239:0]};
 wire[5:0]accepted=cfg_valid&cfg_ready,completed=cfg_rsp_valid&cfg_rsp_ready;
 reg error_reply;
 always @*begin error_reply=0;for(integer j=0;j<6;j=j+1)if(completed[j]&&cfg_status[j*3+:3]!=0)error_reply=1;end
 function descriptor_ok(input[2303:0]p,input[63:0]d);
 reg[31:0]n,nets;
 begin
  n=p[160+:32];nets=p[192+:32];
  descriptor_ok=p[64+:64]==d&&p[2112+:64]==d&&n!=0&&nets!=0&&p[128+:32]!=0&&p[224+:32]!=0&&
   p[576+:32]==n&&p[832+:32]==n&&p[1728+:32]==n&&p[2176+:32]==n&&p[2208+:32]==nets&&
   p[256+:128]==0&&p[640+:128]==0&&p[864+:288]==0&&p[1344+:192]==0&&p[1792+:128]==0&&p[2272+:32]==0;
 end endfunction
 always @(posedge clk)begin
  if(rst)begin prepared<=0;shadow_payload<=0;shadow_design<=0;shadow_checkpoint<=0;state<=IDLE;configured<=0;stopped<=0;error_code<=0;elapsed<=0;current_version<=0;tx_version<=0;descriptor<=0;sent<=0;retired<=0;saved_design<=0;saved_checkpoint<=0;load_rsp_valid<=0;load_status<=0;rsp_valid<=0;rsp_status<=0;rsp_cookie<=0;end
  // A new recovery attempt may clear only retired transient state. The
  // authoritative descriptor, checkpoint and successful version survive.
  else if(attempt_reset&&state==IDLE&&!load_rsp_valid&&backend_drained&&normal_retired)begin
   prepared<=0;stopped<=0;error_code<=0;elapsed<=0;tx_version<=0;sent<=0;retired<=0;
   rsp_valid<=0;rsp_status<=0;rsp_cookie<=0;
  end else begin
   if(load_rsp_valid&&load_rsp_ready)load_rsp_valid<=0;
   if(busy&&!rsp_valid&&!stopped)elapsed<=elapsed+1;
   if(!stopped)begin if(fail_now)begin stopped<=1;error_code<=3;end else if(error_reply)begin stopped<=1;error_code<=2;end end
   case(state)
    IDLE:begin
     if(load_valid&&load_ready)begin
      load_rsp_valid<=1;load_status<=0;
      if(prepared||(!load_stage&&configured))load_status<=1;
      else if(load_stage)begin
       if(!publish_permit||!configured||!load_authoritative||load_design!=saved_design||load_checkpoint<=saved_checkpoint||!descriptor_ok(load_payload,load_design)||load_payload!=active_payload)load_status<=1;
       else begin prepared<=1;shadow_payload<=load_payload;shadow_design<=load_design;shadow_checkpoint<=load_checkpoint;end
      end
      else if(!load_authoritative||!descriptor_ok(load_payload,load_design)||(configured&&load_design==saved_design&&(load_checkpoint<=saved_checkpoint||load_payload[2240+:32]<current_version)))load_status<=1;
      else begin descriptor<=load_payload;saved_design<=load_design;saved_checkpoint<=load_checkpoint;current_version<=load_payload[2240+:32];configured<=1;end
     end
     if(start_valid&&start_ready)begin
      sent<=0;retired<=0;elapsed<=0;rsp_cookie<=start_cookie;rsp_status<=0;tx_version<=start_version;
      if(start_design!=saved_design||start_checkpoint!=saved_checkpoint||start_version<=current_version||start_price!=start_version[3:0])begin stopped<=1;error_code<=1;state<=DRAIN;end
      else state<=FIRST;
     end
    end
    FIRST,OTHERS:begin
     sent<=sent|accepted;retired<=retired|completed;
     if(state==FIRST&&(retired[0]||completed[0]))begin
      if(stopped||fail_now||error_reply)state<=DRAIN;else state<=OTHERS;
     end else if(state==OTHERS&&(retired|completed)==6'b111111)state<=DRAIN;
    end
    DRAIN:if(backend_drained&&normal_retired)begin
     rsp_status<=stopped?error_code:fail_now?3:0;rsp_valid<=1;state<=DONE;
     if(!stopped&&!fail_now)current_version<=tx_version;
    end
    DONE:if(rsp_valid&&rsp_ready)begin rsp_valid<=0;state<=IDLE;end
    default:begin stopped<=1;error_code<=3;state<=DRAIN;end
   endcase
   if(publish_valid&&publish_ready)begin
    if(NATIVE_FEEDBACK_PUBLICATION!=0)descriptor[2240+:32]<=shadow_payload[2240+:32];
    else descriptor<=shadow_payload;
    saved_design<=shadow_design;saved_checkpoint<=shadow_checkpoint;current_version<=shadow_payload[2240+:32];prepared<=0;
   end
   if((discard_valid&&discard_ready)||abort||fail_now)prepared<=0;
  end
 end
endmodule
