`timescale 1ns/1ps
// Cost OFFER only, after successful label ACKs. FULL stops this query; no silent loss/retry.
module cost_offer #(parameter integer MAX_CYCLES=1048576)(
 input wire clk,rst,abort,active,decision_lock,input wire [1:0] active_query,input wire [3:0] active_price,input wire [31:0] active_version,input wire [63:0] active_design,
 input wire req_valid,output wire req_ready,input wire [31:0] req_cookie,req_node,req_key,req_before,
 output reg rsp_valid,input wire rsp_ready,output reg [3:0] rsp_status,output reg [31:0] rsp_cookie,rsp_node,rsp_key,rsp_before,rsp_size,rsp_version,rsp_backend_status,output reg [1:0] rsp_query,output reg [3:0] rsp_price,output reg [63:0] rsp_design,
 output wire busy,fault,
 output wire f_valid,input wire f_ready,output wire [31:0] f_key,f_id,f_cookie,f_version,output wire [63:0] f_design,output wire [1:0] f_query,output wire [3:0] f_price,
 input wire f_rsp_valid,output wire f_rsp_ready,input wire [31:0] f_rsp_status,f_rsp_cookie,f_rsp_size,f_rsp_version,input wire [63:0] f_rsp_design,input wire [1:0] f_rsp_query,input wire [3:0] f_rsp_price
);
 localparam IDLE=0,SEND=1,WAIT_REPLY=2;
 reg [1:0] state;reg stopped,owned,context_owned,logical_done;reg [31:0] elapsed;
 wire drift=owned&&context_owned&&(!active||!decision_lock||active_query!=rsp_query||active_price!=rsp_price||active_version!=rsp_version||active_design!=rsp_design);
 wire bad_identity=f_rsp_cookie!=rsp_cookie||f_rsp_query!=rsp_query||f_rsp_price!=rsp_price||f_rsp_version!=rsp_version||f_rsp_design!=rsp_design;
 wire bad_result=bad_identity||(f_rsp_status==0?(rsp_before>=65536||f_rsp_size!=rsp_before+1):(f_rsp_status!=2||rsp_before!=65536||f_rsp_size!=65536));
 wire response_error=state==WAIT_REPLY&&f_rsp_valid&&(bad_result||f_rsp_status!=0);
 wire unexpected=f_rsp_valid&&state!=WAIT_REPLY;
 wire timeout=owned&&!logical_done&&!stopped&&elapsed>=MAX_CYCLES-1;
 wire fail_now=abort||drift||unexpected||timeout||response_error;
 assign fault=!rst&&(stopped||fail_now);assign busy=!rst&&(owned||state!=IDLE||rsp_valid);
 assign req_ready=!rst&&!fault&&!busy&&active&&decision_lock;
 assign f_valid=!rst&&state==SEND;assign f_key=rsp_key;assign f_id=rsp_node;assign f_cookie=rsp_cookie;assign f_version=rsp_version;assign f_design=rsp_design;assign f_query=rsp_query;assign f_price=rsp_price;
 assign f_rsp_ready=!rst&&state==WAIT_REPLY;
 always @(posedge clk)begin
  if(rst)begin state<=IDLE;stopped<=0;owned<=0;context_owned<=0;logical_done<=0;elapsed<=0;rsp_valid<=0;rsp_status<=0;rsp_cookie<=0;rsp_node<=0;rsp_key<=0;rsp_before<=0;rsp_size<=0;rsp_version<=0;rsp_backend_status<=0;rsp_query<=0;rsp_price<=0;rsp_design<=0;end
  else begin
   if(rsp_valid&&rsp_ready)begin rsp_valid<=0;context_owned<=0;end
   if(owned&&state==IDLE&&!rsp_valid&&logical_done)owned<=0;
   if(owned&&!logical_done&&!stopped)elapsed<=elapsed+1'b1;
   case(state)
    IDLE:if(req_valid&&req_ready)begin state<=SEND;owned<=1;context_owned<=1;logical_done<=0;elapsed<=0;rsp_status<=0;rsp_backend_status<=0;rsp_cookie<=req_cookie;rsp_node<=req_node;rsp_key<=req_key;rsp_before<=req_before;rsp_size<=req_before;rsp_query<=active_query;rsp_price<=active_price;rsp_version<=active_version;rsp_design<=active_design;end
    SEND:if(f_ready)state<=WAIT_REPLY;
    WAIT_REPLY:if(f_rsp_valid)begin
     state<=IDLE;
     if(!logical_done&&!stopped&&!fail_now)begin rsp_valid<=1;logical_done<=1;rsp_status<=0;rsp_backend_status<=f_rsp_status;rsp_size<=f_rsp_size;end
    end
    default:stopped<=1;
   endcase
   if(fail_now)begin
    stopped<=1;
    if(owned&&!logical_done)begin
     rsp_valid<=1;logical_done<=1;rsp_status<=response_error?(bad_result?1:2):3;
     if(state==WAIT_REPLY&&f_rsp_valid)begin rsp_size<=f_rsp_size;rsp_backend_status<=f_rsp_status;end
    end
   end
  end
 end
endmodule
