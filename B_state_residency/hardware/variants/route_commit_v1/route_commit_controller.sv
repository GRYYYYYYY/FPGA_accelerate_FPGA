`timescale 1ns/1ps
// One exclusive lease, bounded saved connection paths, registered backends.
module route_commit_controller #(parameter integer MAX_PATH=32,MAX_CYCLES=1048576)(
 input wire clk,rst,abort,active,lease,
 input wire[1:0]active_query,input wire[3:0]active_price,input wire[31:0]active_version,input wire[63:0]active_design,
 input wire req_valid,output wire req_ready,input wire req_op,req_slot,
 input wire[31:0]req_cookie,req_source,req_sink,req_net,req_sequence,
 output reg rsp_valid,input wire rsp_ready,output reg[3:0]rsp_status,
 output reg[31:0]rsp_cookie,rsp_nodes,rsp_acked,output wire busy,fault,output reg[1:0]slot_valid,
 output wire l_valid,input wire l_ready,output wire[31:0]l_node,
 input wire l_rsp_valid,output wire l_rsp_ready,input wire[3:0]l_status,input wire l_present,input wire[159:0]l_payload,
 output wire o_valid,input wire o_ready,output wire[2:0]o_op,output wire[31:0]o_node,o_net,o_cookie,
 input wire o_rsp_valid,output wire o_rsp_ready,input wire[3:0]o_status,input wire[31:0]o_rsp_cookie
);
 localparam IDLE=0,LS=1,LW=2,OS=3,OW=4;
 reg[2:0]state;reg owned,stopped,operation,slot;reg[3:0]error_code;
 reg[31:0]source,sink,net,sequence_id,current,length,index,elapsed;
 reg[1:0]q;reg[3:0]price;reg[31:0]version;reg[63:0]ctx_design;
 reg[31:0]path[0:1][0:MAX_PATH-1];reg[31:0]sizes[0:1],nets[0:1],sources[0:1],sinks[0:1];
 reg[63:0]designs[0:1];
 integer i;reg duplicate;
 always @* begin duplicate=0;for(integer k=0;k<MAX_PATH;k=k+1)if(k<length&&path[slot][k]==current)duplicate=1;end
 wire drift=owned&&(!active||!lease||q!=active_query||price!=active_price||version!=active_version||ctx_design!=active_design);
 wire timed_out=owned&&!rsp_valid&&!stopped&&elapsed>=MAX_CYCLES-1;
 wire bad_l=state==LW&&l_rsp_valid&&(l_status!=0||!l_present);
 wire bad_o=state==OW&&o_rsp_valid&&(o_status!=0||o_rsp_cookie!=rsp_cookie);
 wire unexpected=(l_rsp_valid&&state!=LW&&!(state==LS&&l_ready))||(o_rsp_valid&&state!=OW&&!(state==OS&&o_ready));
 wire fail_now=abort||drift||timed_out||bad_l||bad_o||unexpected;
 assign fault=!rst&&(stopped||fail_now);
 assign busy=!rst&&(owned||state!=IDLE||rsp_valid);
 assign req_ready=!rst&&!fault&&!busy&&active&&lease;
 // Preserve every exposed request through backpressure, including on failure.
 assign l_valid=!rst&&state==LS;assign l_node=current;assign l_rsp_ready=!rst&&state==LW;
 assign o_valid=!rst&&state==OS;assign o_op=operation?3'd2:3'd1;
 assign o_node=path[slot][index];assign o_net=net;assign o_cookie=rsp_cookie;assign o_rsp_ready=!rst&&state==OW;
 task finish(input[3:0]status);begin rsp_status<=status;rsp_valid<=1;state<=IDLE;rsp_nodes<=length;end endtask
 task fatal_finish(input[3:0]status);begin stopped<=1;error_code<=status;finish(status);end endtask
 always @(posedge clk)begin
  if(rst)begin
   state<=IDLE;owned<=0;stopped<=0;operation<=0;slot<=0;error_code<=0;slot_valid<=0;
   source<=0;sink<=0;net<=0;sequence_id<=0;current<=0;length<=0;index<=0;elapsed<=0;
   q<=0;price<=0;version<=0;ctx_design<=0;rsp_valid<=0;rsp_status<=0;rsp_cookie<=0;rsp_nodes<=0;rsp_acked<=0;
   for(i=0;i<2;i=i+1)begin sizes[i]<=0;nets[i]<=0;sources[i]<=0;sinks[i]<=0;designs[i]<=0;end
  end else begin
   if(rsp_valid&&rsp_ready)begin rsp_valid<=0;owned<=0;end
   if(owned&&!rsp_valid&&!stopped)elapsed<=elapsed+1'b1;
   if(fail_now&&!stopped)begin stopped<=1;error_code<=bad_l?4:bad_o?5:6;end
   case(state)
    IDLE:if(req_valid&&req_ready)begin
     owned<=1;operation<=req_op;slot<=req_slot;source<=req_source;sink<=req_sink;net<=req_net;sequence_id<=req_sequence;
     q<=active_query;price<=active_price;version<=active_version;ctx_design<=active_design;
     rsp_cookie<=req_cookie;rsp_status<=0;rsp_nodes<=0;rsp_acked<=0;elapsed<=0;length<=0;index<=0;
     if((!req_op&&slot_valid[req_slot])||(req_op&&(!slot_valid[req_slot]||nets[req_slot]!=req_net||sources[req_slot]!=req_source||sinks[req_slot]!=req_sink||designs[req_slot]!=active_design)))begin rsp_status<=1;rsp_valid<=1;end
     else if(req_op)begin
      length<=sizes[req_slot];
      if(sizes[req_slot]==0)begin slot_valid[req_slot]<=0;rsp_valid<=1;end else state<=OS;
     end else begin current<=req_sink;state<=LS;end
    end
    LS:if(l_ready)state<=LW;
    LW:if(l_rsp_valid)begin
     if(stopped||fail_now)finish(stopped?error_code:(bad_l?4:6));
     else if((current==sink&&(l_payload[128]!=1||l_payload[127:96]!=sequence_id))||duplicate)fatal_finish(2);
     else if(current==source)begin
      if(l_payload[95:64]!=32'hffffffff)fatal_finish(2);
      else if(length==0)begin slot_valid[slot]<=1;sizes[slot]<=0;nets[slot]<=net;sources[slot]<=source;sinks[slot]<=sink;designs[slot]<=ctx_design;finish(0);end
      else begin index<=0;state<=OS;end
     end else if(l_payload[95:64]==32'hffffffff||l_payload[95:64]==sink||current==32'hffffffff)fatal_finish(2);
     else if(current!=sink&&length==MAX_PATH)fatal_finish(3);
     else begin
      if(current!=sink)begin path[slot][length]<=current;length<=length+1'b1;end
      current<=l_payload[95:64];state<=LS;
     end
    end
    OS:if(o_ready)state<=OW;
    OW:if(o_rsp_valid)begin
     // Count only confirmed successful modifications, even after late abort.
     if(o_status==0&&o_rsp_cookie==rsp_cookie)rsp_acked<=rsp_acked+1'b1;
     if(stopped||fail_now)finish(stopped?error_code:(bad_o?5:6));
     else if(index+1==length)begin
      if(operation)slot_valid[slot]<=0;
      else begin slot_valid[slot]<=1;sizes[slot]<=length;nets[slot]<=net;sources[slot]<=source;sinks[slot]<=sink;designs[slot]<=ctx_design;end
      finish(0);
     end else begin index<=index+1'b1;state<=OS;end
    end
    default:fatal_finish(6);
   endcase
  end
 end
endmodule
