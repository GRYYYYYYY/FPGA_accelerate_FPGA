`timescale 1ns/1ps
// Read-only design inputs; no label/owner mutation and no numerical cost arithmetic.
module cost_inputs_prefetch #(parameter integer MAX_CYCLES=1048576)(
 input wire clk,rst,abort,active,decision_lock,
 input wire [1:0] active_query,input wire [3:0] active_price,
 input wire [31:0] active_version,input wire [63:0] active_design,
 input wire req_valid,output wire req_ready,
 input wire [31:0] req_cookie,req_node,req_net,
 output wire rsp_valid,input wire rsp_ready,
 output reg [31:0] rsp_cookie,rsp_node,rsp_net,rsp_count,rsp_occupancy,rsp_price_index,
 output reg [31:0] rsp_history,rsp_price_value,output reg [127:0] rsp_net_data,
 output reg [1:0] rsp_query,output reg [3:0] rsp_price,rsp_status,
 output reg [31:0] rsp_version,output reg [63:0] rsp_design,
 output wire busy,fault,
 output wire o_req_valid,input wire o_req_ready,
 output wire [31:0] o_req_cookie,o_req_node,o_req_net,
 input wire o_rsp_valid,output wire o_rsp_ready,
 input wire [31:0] o_rsp_cookie,o_rsp_count,o_rsp_occupancy,input wire [3:0] o_rsp_status,
 output wire c_req_valid,input wire c_req_ready,output wire [2:0] c_req_op,
 output wire [31:0] c_req_cookie,c_req_index,c_req_version,
 output wire [1:0] c_req_query,output wire [3:0] c_req_price,
 input wire c_rsp_valid,output wire c_rsp_ready,input wire [3:0] c_rsp_status,
 input wire [31:0] c_rsp_cookie,c_rsp_index,c_rsp_version,
 input wire [2:0] c_rsp_op,input wire c_rsp_host,input wire [1:0] c_rsp_query,input wire [3:0] c_rsp_price,
 input wire [127:0] c_rsp_data
);
 localparam IDLE=0,OS=1,OW=2,CS=3,CW=4,REPLY=5;
 reg [2:0] state;reg [1:0] stage;reg stopped;reg [31:0] elapsed;
 wire owned=state!=IDLE;
 wire drift=owned&&(!active||!decision_lock||active_query!=rsp_query||active_price!=rsp_price||active_version!=rsp_version||active_design!=rsp_design);
 wire unexpected=(o_rsp_valid&&state!=OW)||(c_rsp_valid&&state!=CW);
 wire timed_out=owned&&state!=REPLY&&elapsed>=MAX_CYCLES-1;
 wire [32:0] selected={1'b0,o_rsp_occupancy}-(o_rsp_count!=0?33'd1:33'd0);
 wire invalid_owner=(o_rsp_count!=0&&o_rsp_occupancy==0)||selected>=256;
 wire bad_o=o_rsp_status!=0||o_rsp_cookie!=rsp_cookie||invalid_owner;
 assign c_req_op=stage==0?3'd0:stage==1?3'd2:3'd6;
 assign c_req_index=stage==0?rsp_node:stage==1?rsp_price_index:rsp_net;
 assign c_req_cookie=rsp_cookie;assign c_req_version=rsp_version;assign c_req_query=rsp_query;assign c_req_price=rsp_price;
 wire bad_c=c_rsp_status!=0||c_rsp_cookie!=rsp_cookie||c_rsp_index!=c_req_index||c_rsp_version!=rsp_version||c_rsp_op!=c_req_op||c_rsp_host||c_rsp_query!=rsp_query||c_rsp_price!=rsp_price;
 wire fail_now=abort||drift||unexpected||timed_out||(state==OW&&o_rsp_valid&&bad_o)||(state==CW&&c_rsp_valid&&bad_c);
 assign fault=!rst&&(stopped||fail_now);
 assign busy=!rst&&(owned||stopped);
 assign req_ready=!rst&&!fault&&state==IDLE&&active&&decision_lock;
 assign rsp_valid=!rst&&state==REPLY;
 // Captured downstream requests remain offered across a late fault until reset.
 assign o_req_valid=!rst&&state==OS;
 assign o_req_cookie=rsp_cookie;assign o_req_node=rsp_node;assign o_req_net=rsp_net;
 assign o_rsp_ready=!rst&&state==OW;
 assign c_req_valid=!rst&&state==CS;
 assign c_rsp_ready=!rst&&state==CW;
 always @(posedge clk)begin
  if(rst)begin state<=IDLE;stage<=0;stopped<=0;elapsed<=0;
   rsp_cookie<=0;rsp_node<=0;rsp_net<=0;rsp_count<=0;rsp_occupancy<=0;rsp_price_index<=0;
   rsp_history<=0;rsp_price_value<=0;rsp_net_data<=0;rsp_query<=0;rsp_price<=0;rsp_version<=0;rsp_design<=0;rsp_status<=0;
  end else begin
   if(owned&&state!=REPLY&&!stopped)elapsed<=elapsed+1'b1;
   case(state)
    IDLE:if(req_valid&&req_ready)begin
     rsp_cookie<=req_cookie;rsp_node<=req_node;rsp_net<=req_net;
     rsp_query<=active_query;rsp_price<=active_price;rsp_version<=active_version;rsp_design<=active_design;
     rsp_count<=0;rsp_occupancy<=0;rsp_price_index<=0;rsp_history<=0;rsp_price_value<=0;rsp_net_data<=0;rsp_status<=0;
     elapsed<=0;stage<=0;state<=OS;
    end
    OS:if(o_req_ready)state<=OW;
    OW:if(o_rsp_valid)begin
     if(!fault)begin rsp_count<=o_rsp_count;rsp_occupancy<=o_rsp_occupancy;rsp_price_index<=selected[31:0];state<=CS;end
     else begin rsp_status<=bad_o?4'd1:4'd3;state<=REPLY;end
    end
    CS:if(c_req_ready)state<=CW;
    CW:if(c_rsp_valid)begin
     if(!fault)begin
      if(stage==0)rsp_history<=c_rsp_data[31:0];
      if(stage==1)rsp_price_value<=c_rsp_data[31:0];
      if(stage==2)begin rsp_net_data<=c_rsp_data;state<=REPLY;end
      else begin stage<=stage+1'b1;state<=CS;end
     end else begin rsp_status<=2;state<=REPLY;end
    end
    REPLY:if(rsp_ready)state<=IDLE;
    default:begin stopped<=1;end
   endcase
   if(fail_now)stopped<=1;
  end
 end
endmodule
