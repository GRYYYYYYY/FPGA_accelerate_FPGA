`timescale 1ns/1ps
module owner_bridge #(parameter integer MAX_CYCLES=1048576)(
 input wire clk,rst,abort,decision_lock,active,input wire[1:0]active_query,input wire[3:0]active_price,
 input wire s_req_valid,output wire s_req_ready,input wire[3:0]s_req_kind,input wire[4:0]s_req_phase,
 input wire[31:0]s_req_node,s_req_net,s_req_cookie,input wire[1:0]s_req_query,input wire[3:0]s_req_price,
 output wire s_rsp_valid,input wire s_rsp_ready,output reg[3:0]s_rsp_status,s_rsp_kind,output reg[4:0]s_rsp_phase,
 output reg[31:0]s_rsp_node,s_rsp_net,s_rsp_cookie,s_rsp_value,output reg[1:0]s_rsp_query,output reg[3:0]s_rsp_price,
 input wire h_req_valid,output wire h_req_ready,input wire[2:0]h_req_op,input wire[31:0]h_req_cookie,h_req_node,h_req_net,
 output wire h_rsp_valid,input wire h_rsp_ready,output reg[3:0]h_rsp_status,output reg[31:0]h_rsp_cookie,h_rsp_count,h_rsp_occupancy,output reg h_rsp_will_overuse,
 output wire b_req_valid,input wire b_req_ready,output wire[2:0]b_req_op,output wire[31:0]b_req_cookie,b_req_node,b_req_net,
 input wire b_rsp_valid,output wire b_rsp_ready,input wire[3:0]b_rsp_status,input wire[31:0]b_rsp_cookie,b_rsp_count,b_rsp_occupancy,input wire b_rsp_will_overuse,b_fault,
 output wire host_pending,busy,fault
);
 localparam IDLE=0,SS=1,SW=2,SR=3,HS=4,HW=5,HR=6;
 reg[2:0]state,host_op;reg[31:0]host_node,host_net,elapsed;reg stopped;
 wire service=state==SS||state==SW||state==SR;
 wire drift=service&&(!decision_lock||!active||active_query!=s_rsp_query||active_price!=s_rsp_price);
 wire unexpected=b_rsp_valid&&state!=SW&&state!=HW;
 wire mismatch=b_rsp_valid&&((state==SW&&b_rsp_cookie!=s_rsp_cookie)||(state==HW&&b_rsp_cookie!=h_rsp_cookie));
 wire timeout=(state==SS||state==SW||state==HS||state==HW)&&elapsed>=MAX_CYCLES-1;
 assign fault=!rst&&(stopped||abort||b_fault||drift||unexpected||mismatch||timeout);
 assign busy=!rst&&state!=IDLE;
 assign host_pending=state==HS||state==HW||state==HR;
 assign s_req_ready=!rst&&!fault&&state==IDLE;
 assign h_req_ready=!rst&&!fault&&state==IDLE&&!decision_lock&&!s_req_valid;
 assign s_rsp_valid=!rst&&state==SR;assign h_rsp_valid=!rst&&state==HR;
 // A captured backend request is not withdrawn on late fault. The raw store
 // either accepts it or independently faults, then requires coordinated reset.
 assign b_req_valid=!rst&&(state==SS||state==HS);
 assign b_req_op=state==HS?host_op:3'd0;
 assign b_req_cookie=host_pending?h_rsp_cookie:s_rsp_cookie;
 assign b_req_node=host_pending?host_node:s_rsp_node;
 assign b_req_net=host_pending?host_net:s_rsp_net;
 assign b_rsp_ready=!rst&&(state==SW||state==HW);
 always @(posedge clk)begin
  if(rst)begin
   state<=IDLE;host_op<=0;host_node<=0;host_net<=0;elapsed<=0;stopped<=0;
   s_rsp_status<=0;s_rsp_kind<=0;s_rsp_phase<=0;s_rsp_node<=0;s_rsp_net<=0;s_rsp_cookie<=0;s_rsp_value<=0;s_rsp_query<=0;s_rsp_price<=0;
   h_rsp_status<=0;h_rsp_cookie<=0;h_rsp_count<=0;h_rsp_occupancy<=0;h_rsp_will_overuse<=0;
  end else begin
   if(fault)stopped<=1;
   if(state==SS||state==SW||state==HS||state==HW)begin if(!timeout)elapsed<=elapsed+1'b1;end
   case(state)
    IDLE:if(s_req_valid&&s_req_ready)begin
     s_rsp_kind<=s_req_kind;s_rsp_phase<=s_req_phase;s_rsp_node<=s_req_node;s_rsp_net<=s_req_net;s_rsp_cookie<=s_req_cookie;s_rsp_query<=s_req_query;s_rsp_price<=s_req_price;s_rsp_value<=0;s_rsp_status<=0;elapsed<=0;
     if(!decision_lock||!active||s_req_query!=active_query||s_req_price!=active_price)begin s_rsp_status<=2;state<=SR;stopped<=1;end
     else if(s_req_kind!=4&&s_req_kind!=6)begin s_rsp_status<=1;state<=SR;stopped<=1;end
     else state<=SS;
    end else if(h_req_valid&&h_req_ready)begin host_op<=h_req_op;host_node<=h_req_node;host_net<=h_req_net;h_rsp_cookie<=h_req_cookie;h_rsp_status<=0;h_rsp_count<=0;h_rsp_occupancy<=0;h_rsp_will_overuse<=0;elapsed<=0;state<=HS;end
    SS:if(b_req_valid&&b_req_ready)state<=SW;
    HS:if(b_req_valid&&b_req_ready)state<=HW;
    SW:if(b_rsp_valid)begin
     s_rsp_status<=b_rsp_status!=0?3:fault?5:0;s_rsp_value<=s_rsp_kind==4?{31'b0,b_rsp_will_overuse}:b_rsp_count;state<=SR;
     if(b_rsp_status!=0)stopped<=1;
    end
    HW:if(b_rsp_valid)begin
     h_rsp_status<=mismatch?10:b_rsp_status;h_rsp_count<=b_rsp_count;h_rsp_occupancy<=b_rsp_occupancy;h_rsp_will_overuse<=b_rsp_will_overuse;state<=HR;
    end
    SR:if(s_rsp_ready)state<=IDLE;
    HR:if(h_rsp_ready)state<=IDLE;
    default:begin stopped<=1;state<=IDLE;end
   endcase
  end
 end
endmodule
