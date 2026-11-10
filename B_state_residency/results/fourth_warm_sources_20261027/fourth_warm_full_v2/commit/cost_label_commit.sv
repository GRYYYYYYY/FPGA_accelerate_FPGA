`timescale 1ns/1ps
// Ordered native writes. Each ACK is checked before the next write can start.
// On fault drain the already exposed command/reply; no rollback or hot retry.
module cost_label_commit #(parameter integer MAX_CYCLES=1048576)(
 input wire clk,rst,abort,active,decision_lock,
 input wire [1:0] active_query,input wire [3:0] active_price,input wire [31:0] active_version,input wire [63:0] active_design,
 input wire req_valid,output wire req_ready,input wire [31:0] req_cookie,req_parent,req_child,req_sequence,req_partial,req_total,
 output reg rsp_valid,input wire rsp_ready,output reg [3:0] rsp_status,output reg [2:0] rsp_acked,
 output reg [31:0] rsp_cookie,rsp_parent,rsp_child,rsp_sequence,rsp_version,output reg [1:0] rsp_query,output reg [3:0] rsp_price,output reg [63:0] rsp_design,output reg [159:0] rsp_payload,
 output wire busy,fault,
 output wire l_valid,input wire l_ready,output wire l_write,output wire [31:0] l_node,l_value,output wire [2:0] l_field,
 input wire l_rsp_valid,output wire l_rsp_ready,input wire [3:0] l_status,input wire [159:0] l_payload,input wire l_present
);
 localparam IDLE=0,SEND=1,WAIT_ACK=2;
 reg [1:0] state,step;reg stopped,owned,context_owned,logical_done;reg [31:0] elapsed,partial,total;
 wire drift=owned&&context_owned&&(!active||!decision_lock||active_query!=rsp_query||active_price!=rsp_price||active_version!=rsp_version||active_design!=rsp_design);
 wire bad_l=state==WAIT_ACK&&l_rsp_valid&&(l_status!=0||!l_present||l_payload[31:0]!=total||l_payload[95:64]!=rsp_parent||(step>=1&&l_payload[63:32]!=partial)||(step==2&&l_payload[127:96]!=rsp_sequence));
 wire unexpected=l_rsp_valid&&state!=WAIT_ACK;
 wire timeout=owned&&!logical_done&&!stopped&&elapsed>=MAX_CYCLES-1;
 wire fail_now=abort||drift||bad_l||unexpected||timeout;
 assign fault=!rst&&(stopped||fail_now);
 assign busy=!rst&&(owned||state!=IDLE||rsp_valid);
 assign req_ready=!rst&&!fault&&!busy&&active&&decision_lock;
 assign l_valid=!rst&&state==SEND;assign l_write=1;assign l_node=rsp_child;
 assign l_field=step==0?0:step==1?1:3;
 assign l_value=step==0?total:step==1?partial:rsp_sequence;
 assign l_rsp_ready=!rst&&state==WAIT_ACK;
 always @(posedge clk)begin
  if(rst)begin state<=IDLE;step<=0;stopped<=0;owned<=0;context_owned<=0;logical_done<=0;elapsed<=0;partial<=0;total<=0;
   rsp_valid<=0;rsp_status<=0;rsp_acked<=0;rsp_cookie<=0;rsp_parent<=0;rsp_child<=0;rsp_sequence<=0;rsp_version<=0;rsp_query<=0;rsp_price<=0;rsp_design<=0;rsp_payload<=0;
  end else begin
   if(rsp_valid&&rsp_ready)begin rsp_valid<=0;context_owned<=0;end
   if(owned&&state==IDLE&&!rsp_valid&&logical_done)owned<=0;
   if(owned&&!logical_done&&!stopped)elapsed<=elapsed+1'b1;
   case(state)
    IDLE:if(req_valid&&req_ready)begin
     state<=SEND;step<=0;owned<=1;context_owned<=1;logical_done<=0;elapsed<=0;partial<=req_partial;total<=req_total;
     rsp_cookie<=req_cookie;rsp_parent<=req_parent;rsp_child<=req_child;rsp_sequence<=req_sequence;rsp_version<=active_version;rsp_query<=active_query;rsp_price<=active_price;rsp_design<=active_design;rsp_status<=0;rsp_acked<=0;rsp_payload<=0;
    end
    SEND:if(l_ready)state<=WAIT_ACK;
    WAIT_ACK:if(l_rsp_valid)begin
     state<=IDLE;
     if(!logical_done&&!stopped&&!fail_now)begin
      rsp_payload<=l_payload;rsp_acked<=rsp_acked|(3'b1<<step);
      if(step==2)begin rsp_status<=0;rsp_valid<=1;logical_done<=1;end
      else begin step<=step+1'b1;state<=SEND;end
     end
    end
    default:stopped<=1;
   endcase
   if(fail_now)begin stopped<=1;if(owned&&!logical_done)begin rsp_status<=bad_l?1:2;rsp_valid<=1;logical_done<=1;end end
  end
 end
endmodule
