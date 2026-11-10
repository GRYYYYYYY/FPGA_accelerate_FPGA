`timescale 1ns/1ps
// Native receipts only. Recovery ownership is supplied by the actual fence.
module warm_restore_receipt_join(
 input wire clk,cold_rst,abort,recovery_owned,backend_drained,retired,owner_repaired,
 input wire arm_valid,output wire arm_ready,
 input wire[63:0]arm_design,arm_generation,bound_design,bound_generation,
 input wire[31:0]arm_checkpoint,bound_checkpoint,arm_version,active_version,
 input wire[1:0]arm_query,active_query,input wire[3:0]arm_price,active_price,
 input wire[31:0]arm_cookie,arm_labels,arm_path_crc,arm_query_crc,
 input wire label_accept,label_done,input wire[3:0]label_status,input wire[31:0]label_cookie,label_written,label_verified,
 input wire path_accept,path_restore,path_done,input wire[3:0]path_status,input wire[31:0]path_crc,
 input wire query_accept,query_restore,query_done,input wire[3:0]query_status,input wire[31:0]query_crc,
 input wire completion_consumed,
 output wire retry_window,
 output wire owned,label_allow,admin_safe,path_allow,query_allow,joined,fault,
 output wire[2:0]receipts
);
 localparam IDLE=0,WAIT=1,DONE=2,HALT=3;
 reg[1:0]state;reg[63:0]d,g;reg[31:0]cp,v,cookie,count,pcrc,qcrc;reg[1:0]q;reg[3:0]price;
 reg ls,ps,qs,ld,pd,qd;reg failure_consumed,fence_released;
 wire retry_identity=arm_design==d&&arm_generation==g&&arm_checkpoint==cp&&arm_version>v;
 wire identity_ok=bound_design==d&&bound_generation==g&&bound_checkpoint==cp;
 wire context_ok=active_version==v&&active_query==q&&active_price==price;
 wire arm_ok=arm_design!=0&&arm_generation!=0&&arm_checkpoint!=0&&arm_version!=0&&arm_labels!=0&&arm_price==arm_version[3:0]&&arm_design==bound_design&&arm_generation==bound_generation&&arm_checkpoint==bound_checkpoint;
 wire fail_now=state!=IDLE&&(abort||!recovery_owned||!identity_ok||((ld||state==DONE)&&!context_ok));
 assign owned=!cold_rst&&state!=IDLE;
 assign fault=!cold_rst&&(state==HALT||fail_now);
 // HALT retains business isolation throughout fence turnover and re-arm.
 // Acceptance of an invalid retry still lets the native coordinator return
 // its error; it cannot start restore services or erase the retained floor.
 assign retry_window=!cold_rst&&!abort&&state==HALT&&failure_consumed&&fence_released&&recovery_owned&&backend_drained&&retired;
 assign arm_ready=(!cold_rst&&!abort&&state==IDLE&&recovery_owned&&backend_drained&&retired)||retry_window;
 assign label_allow=!cold_rst&&state==WAIT&&!fault&&backend_drained&&owner_repaired&&!ls;
 // Logical retirement excludes the restore controllers themselves: their busy
 // states must not invalidate an already accepted import's cp_safe permission.
 assign admin_safe=!cold_rst&&state==WAIT&&!fault&&backend_drained&&owner_repaired&&context_ok&&ld;
 assign path_allow=admin_safe&&!ps;assign query_allow=admin_safe&&!qs;
 assign joined=!cold_rst&&state==DONE&&!fault&&backend_drained&&retired;
 assign receipts=owned?{qd,pd,ld}:3'd0;
 always @(posedge clk)begin
  if(cold_rst)begin state<=IDLE;d<=0;g<=0;cp<=0;v<=0;q<=0;price<=0;cookie<=0;count<=0;pcrc<=0;qcrc<=0;ls<=0;ps<=0;qs<=0;ld<=0;pd<=0;qd<=0;failure_consumed<=0;fence_released<=0;end
  else begin
   if(completion_consumed&&(state==HALT||state==WAIT||fail_now))failure_consumed<=1;
   if(failure_consumed&&!recovery_owned)fence_released<=1;
   // Fresh acceptance outranks old HALT fault/context drift. No ownership gap.
   if(state==HALT&&arm_valid&&arm_ready)begin
    failure_consumed<=0;fence_released<=0;
    if(arm_ok&&retry_identity)begin
     d<=arm_design;g<=arm_generation;cp<=arm_checkpoint;v<=arm_version;q<=arm_query;price<=arm_price;cookie<=arm_cookie;count<=arm_labels;pcrc<=arm_path_crc;qcrc<=arm_query_crc;
     ls<=0;ps<=0;qs<=0;ld<=0;pd<=0;qd<=0;state<=WAIT;
    end
   end
   else if(fail_now)state<=HALT;
  else case(state)
   IDLE:if(arm_valid&&arm_ready)begin
    failure_consumed<=0;fence_released<=0;
    d<=arm_design;g<=arm_generation;cp<=arm_checkpoint;v<=arm_version;q<=arm_query;price<=arm_price;cookie<=arm_cookie;count<=arm_labels;pcrc<=arm_path_crc;qcrc<=arm_query_crc;
    ls<=0;ps<=0;qs<=0;ld<=0;pd<=0;qd<=0;
    state<=arm_ok?WAIT:HALT;
   end
   WAIT:begin
    if(label_accept)begin if(!label_allow)state<=HALT;else ls<=1;end
    if(label_done)begin
     if(!ls||ld||label_status!=0||label_cookie!=cookie||label_written!=count||label_verified!=count)state<=HALT;
     else ld<=1;
    end
    if(path_accept)begin if(!path_allow||!path_restore)state<=HALT;else ps<=1;end
    if(query_accept)begin if(!query_allow||!query_restore)state<=HALT;else qs<=1;end
    if(path_done)begin if(!ps||pd||path_status!=0||path_crc!=pcrc)state<=HALT;else pd<=1;end
    if(query_done)begin if(!qs||qd||query_status!=0||query_crc!=qcrc)state<=HALT;else qd<=1;end
    if(completion_consumed)state<=HALT;
    if(ld&&pd&&qd&&retired&&backend_drained&&!label_accept&&!label_done&&!path_accept&&!query_accept&&!path_done&&!query_done&&!completion_consumed)state<=DONE;
   end
   DONE:begin
    if(label_accept||label_done||path_accept||query_accept||path_done||query_done)state<=HALT;
    else if(completion_consumed&&joined)state<=IDLE;
   end
   HALT:state<=HALT;
   default:state<=HALT;
  endcase
  end
 end
endmodule
