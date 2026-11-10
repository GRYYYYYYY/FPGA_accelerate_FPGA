`timescale 1ns/1ps
// Ordered prefix only: CLEAR if EARLY -> prev write ACK -> parent read -> fresh Y -> center.
module postprev_inputs #(parameter integer MAX_CYCLES=1048576)(
 input wire clk,rst,abort,active,decision_lock,
 input wire [1:0] active_query,input wire [3:0] active_price,input wire [31:0] active_version,input wire [63:0] active_design,
 input wire req_valid,output wire req_ready,input wire req_early,
 input wire [31:0] req_cookie,req_parent,req_child,input wire [63:0] req_centers,
 output wire rsp_valid,input wire rsp_ready,output reg [3:0] rsp_status,
 output reg [31:0] rsp_cookie,rsp_parent,rsp_child,rsp_x,rsp_y,rsp_upstream,rsp_distance,
 output reg [255:0] rsp_attrs,output reg rsp_prev_read,
 output reg [1:0] rsp_query,output reg [3:0] rsp_price,output reg [31:0] rsp_version,output reg [63:0] rsp_design,
 output wire busy,fault,retired_idle,
 output wire f_req_valid,input wire f_req_ready,output wire [31:0] f_req_cookie,
 output wire [1:0] f_req_query,output wire [3:0] f_req_price,
 input wire f_rsp_valid,output wire f_rsp_ready,input wire [31:0] f_rsp_status,f_rsp_cookie,f_rsp_size,
 input wire [1:0] f_rsp_query,input wire [3:0] f_rsp_price,
 output wire l_valid,input wire l_ready,output wire l_write,output wire [31:0] l_node,l_value,output wire [2:0] l_field,
 input wire l_rsp_valid,output wire l_rsp_ready,input wire [3:0] l_status,input wire [159:0] l_payload,input wire l_present,
 output wire c_req_valid,input wire c_req_ready,output wire [31:0] c_req_cookie,c_req_node,
 output wire [1:0] c_req_query,output wire [3:0] c_req_price,
 input wire c_rsp_valid,output wire c_rsp_ready,input wire [3:0] c_rsp_status,
 input wire [31:0] c_rsp_cookie,c_rsp_node,c_rsp_y,c_rsp_label_prev,input wire [255:0] c_rsp_attrs,
 input wire [1:0] c_rsp_op,c_rsp_query,input wire [3:0] c_rsp_price,input wire c_rsp_prev_read
);
 localparam IDLE=0,FS=1,FW=2,WS=3,WW=4,LS=5,LW=6,CS=7,CW=8,AS=9,AW=10,REPLY=11;
 reg [3:0] state;reg stopped;reg [31:0] elapsed;reg [63:0] centers;
 wire ac_ready,ac_valid,ac_busy,ac_fault,ac_retired_idle;wire [63:0] ac_words;wire [1:0] ac_status,ac_query;
 wire [31:0] ac_cookie,ac_version;wire [3:0] ac_price;
 wire owned=state!=IDLE;
 wire drift=owned&&(!active||!decision_lock||active_query!=rsp_query||active_price!=rsp_price||active_version!=rsp_version||active_design!=rsp_design);
 wire unexpected=(f_rsp_valid&&state!=FW)||(l_rsp_valid&&state!=WW&&state!=LW)||(c_rsp_valid&&state!=CW)||(ac_valid&&state!=AW);
 wire timeout=owned&&state!=REPLY&&elapsed>=MAX_CYCLES-1;
 wire bad_f=f_rsp_status!=0||f_rsp_size!=0||f_rsp_cookie!=rsp_cookie||f_rsp_query!=rsp_query||f_rsp_price!=rsp_price;
 wire bad_l=l_status!=0||(!l_present&&l_payload!=0)||(state==WW&&(!l_present||l_payload[95:64]!=rsp_parent));
 wire bad_c=c_rsp_status!=0||c_rsp_cookie!=rsp_cookie||c_rsp_node!=rsp_child||c_rsp_op!=0||c_rsp_query!=rsp_query||c_rsp_price!=rsp_price||(c_rsp_prev_read&&c_rsp_label_prev!=rsp_parent);
 wire bad_a=ac_status!=0||ac_words[31:0]!=0||ac_cookie!=rsp_cookie||ac_query!=rsp_query||ac_price!=rsp_price||ac_version!=rsp_version;
 wire fail_now=abort||drift||unexpected||timeout||ac_fault||
  (state==FW&&f_rsp_valid&&bad_f)||((state==WW||state==LW)&&l_rsp_valid&&bad_l)||(state==CW&&c_rsp_valid&&bad_c)||(state==AW&&ac_valid&&bad_a);
 assign fault=!rst&&(stopped||fail_now);assign busy=!rst&&(owned||fault);
 assign retired_idle=!rst&&state==IDLE&&ac_retired_idle;
 assign req_ready=!rst&&!fault&&state==IDLE&&active&&decision_lock;
 assign rsp_valid=!rst&&state==REPLY;
 assign f_req_valid=!rst&&state==FS;assign f_req_cookie=rsp_cookie;assign f_req_query=rsp_query;assign f_req_price=rsp_price;assign f_rsp_ready=!rst&&state==FW;
 assign l_valid=!rst&&(state==WS||state==LS);assign l_write=state==WS;
 assign l_node=state==WS?rsp_child:rsp_parent;assign l_value=state==WS?rsp_parent:0;assign l_field=state==WS?3'd2:3'd1;
 assign l_rsp_ready=!rst&&(state==WW||state==LW);
 assign c_req_valid=!rst&&state==CS;assign c_req_cookie=rsp_cookie;assign c_req_node=rsp_child;
 assign c_req_query=rsp_query;assign c_req_price=rsp_price;assign c_rsp_ready=!rst&&state==CW;
 cost_center_service arithmetic(.clk(clk),.rst(rst),.abort(abort||stopped),.active(active),.active_query(active_query),.active_price(active_price),.active_version(active_version),
 .req_valid(state==AS&&!fault),.req_ready(ac_ready),.req_words({centers[63:32],centers[31:0],rsp_y,rsp_x}),.req_cookie(rsp_cookie),.req_query(rsp_query),.req_price(rsp_price),.req_version(rsp_version),
 .rsp_valid(ac_valid),.rsp_ready(state==AW),.rsp_words(ac_words),.rsp_cookie(ac_cookie),.rsp_query(ac_query),.rsp_price(ac_price),.rsp_version(ac_version),.rsp_status(ac_status),.busy(ac_busy),.fault(ac_fault),.retired_idle(ac_retired_idle));
 task fail(input [3:0] code);begin rsp_status<=code;state<=REPLY;end endtask
 always @(posedge clk)begin
  if(rst)begin state<=IDLE;stopped<=0;elapsed<=0;centers<=0;rsp_status<=0;rsp_cookie<=0;rsp_parent<=0;rsp_child<=0;rsp_x<=0;rsp_y<=0;rsp_upstream<=0;rsp_distance<=0;rsp_attrs<=0;rsp_prev_read<=0;rsp_query<=0;rsp_price<=0;rsp_version<=0;rsp_design<=0;end
  else begin
   if(owned&&state!=REPLY&&!stopped)elapsed<=elapsed+1'b1;
   case(state)
    IDLE:if(req_valid&&req_ready)begin
     rsp_cookie<=req_cookie;rsp_parent<=req_parent;rsp_child<=req_child;centers<=req_centers;
     rsp_query<=active_query;rsp_price<=active_price;rsp_version<=active_version;rsp_design<=active_design;
     rsp_status<=0;rsp_x<=0;rsp_y<=0;rsp_upstream<=0;rsp_distance<=0;rsp_attrs<=0;rsp_prev_read<=0;elapsed<=0;state<=req_early?FS:WS;
    end
    FS:if(f_req_ready)state<=FW;
    FW:if(f_rsp_valid)begin if(fault)fail(1);else state<=WS;end
    WS:if(l_ready)state<=WW;
    WW:if(l_rsp_valid)begin if(fault)fail(2);else state<=LS;end
    LS:if(l_ready)state<=LW;
    LW:if(l_rsp_valid)begin if(fault)fail(3);else begin rsp_upstream<=l_payload[63:32];state<=CS;end end
    CS:if(c_req_ready)state<=CW;
    CW:if(c_rsp_valid)begin
     if(fault)fail(4);else begin rsp_y<=c_rsp_y;rsp_x<={{16{c_rsp_attrs[127]}},c_rsp_attrs[127:112]};rsp_attrs<=c_rsp_attrs;rsp_prev_read<=c_rsp_prev_read;state<=AS;end
    end
    AS:if(!fault&&ac_ready)state<=AW;
    AW:if(ac_valid)begin if(fault)fail(5);else begin rsp_distance<=ac_words[63:32];state<=REPLY;end end
    REPLY:if(rsp_ready)state<=IDLE;
    default:stopped<=1;
   endcase
   if(fail_now)stopped<=1;
  end
 end
endmodule
