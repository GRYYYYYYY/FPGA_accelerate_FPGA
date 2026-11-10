`timescale 1ns/1ps
// Actual post-prev inputs + immutable State -> geometry_step -> exact cost_step.
// Landmark-active profiles are rejected until real landmark storage is connected.
module cost23_inputs #(parameter integer MAX_CYCLES=1048576)(
 input wire clk,rst,abort,active,decision_lock,
 input wire [1:0] active_query,input wire [3:0] active_price,input wire [31:0] active_version,input wire [63:0] active_design,
 input wire req_valid,output wire req_ready,input wire [31:0] req_cookie,req_child,req_sink,
 input wire [511:0] req_params,input wire [447:0] req_config,input wire [255:0] req_attrs,
 input wire [31:0] req_count,req_history,req_price_value,req_x,req_y,req_upstream,req_center,
 input wire [127:0] req_net,
 output wire rsp_valid,input wire rsp_ready,output reg [3:0] rsp_status,
 output reg [31:0] rsp_cookie,rsp_child,rsp_version,output reg [1:0] rsp_query,output reg [3:0] rsp_price,output reg [63:0] rsp_design,
 output reg [735:0] rsp_packet,output reg [159:0] rsp_cost,output reg [415:0] rsp_geometry,output reg [127:0] rsp_geometry_result,
 output wire busy,fault,retired_idle,
 output wire c_req_valid,input wire c_req_ready,output wire [31:0] c_req_cookie,c_req_node,
 output wire [1:0] c_req_query,c_req_op,output wire [3:0] c_req_price,
 input wire c_rsp_valid,output wire c_rsp_ready,input wire [3:0] c_rsp_status,
 input wire [31:0] c_rsp_cookie,c_rsp_node,c_rsp_y,c_rsp_slr,c_rsp_next,c_rsp_prev_column,input wire [255:0] c_rsp_attrs,
 input wire [1:0] c_rsp_op,c_rsp_query,input wire [3:0] c_rsp_price
);
 localparam IDLE=0,SS=1,SW=2,CS=3,CW=4,LS=5,LW=6,GS=7,GW=8,KS=9,KW=10,REPLY=11;
 reg [3:0] state;reg stopped;reg [31:0] elapsed,sink,expected_y;
 wire ga_ready,ga_valid,ga_busy,ga_fault,ka_ready,ka_valid,ka_busy,ka_fault,ga_retired_idle,ka_retired_idle;
 wire [127:0] ga_words;wire [159:0] ka_words;wire [1:0] ga_status,ka_status,ga_query,ka_query;wire [3:0] ga_price,ka_price;wire [31:0] ga_cookie,ka_cookie;
 wire owned=state!=IDLE;
 wire drift=owned&&(!active||!decision_lock||active_query!=rsp_query||active_price!=rsp_price||active_version!=rsp_version||active_design!=rsp_design);
 wire unexpected=(c_rsp_valid&&state!=SW&&state!=CW&&state!=LW)||(ga_valid&&state!=GW)||(ka_valid&&state!=KW);
 wire bad_c=c_rsp_status!=0||c_rsp_cookie!=rsp_cookie||c_rsp_node!=(state==SW?sink:rsp_child)||c_rsp_op!=(state==LW?2:1)||c_rsp_query!=rsp_query||c_rsp_price!=rsp_price||(state==CW&&c_rsp_y!=expected_y);
 wire fail_now=abort||drift||unexpected||ga_fault||ka_fault||(owned&&state!=REPLY&&elapsed>=MAX_CYCLES-1)||((state==SW||state==CW||state==LW)&&c_rsp_valid&&bad_c);
 assign fault=!rst&&(stopped||fail_now);assign busy=!rst&&(owned||fault);
 assign retired_idle=!rst&&state==IDLE&&ga_retired_idle&&ka_retired_idle;
 assign req_ready=!rst&&!fault&&state==IDLE&&active&&decision_lock;
 assign rsp_valid=!rst&&state==REPLY;
 assign c_req_valid=!rst&&(state==SS||state==CS||state==LS);
 assign c_req_cookie=rsp_cookie;assign c_req_node=state==SS?sink:rsp_child;
 assign c_req_op=state==LS?2:1;assign c_req_query=rsp_query;assign c_req_price=rsp_price;
 assign c_rsp_ready=!rst&&(state==SW||state==CW||state==LW);
 geometry_service geometry(.clk(clk),.rst(rst),.abort(abort||stopped),.active(active),.active_query(active_query),.active_price(active_price),
 .req_valid(state==GS&&!fault),.req_ready(ga_ready),.req_words(rsp_geometry),.req_cookie(rsp_cookie),.req_query(rsp_query),.req_price(rsp_price),
 .rsp_valid(ga_valid),.rsp_ready(state==GW),.rsp_words(ga_words),.rsp_cookie(ga_cookie),.rsp_query(ga_query),.rsp_price(ga_price),.rsp_status(ga_status),.busy(ga_busy),.fault(ga_fault),.retired_idle(ga_retired_idle));
 cost_service arithmetic(.clk(clk),.rst(rst),.abort(abort||stopped),.active(active),.active_query(active_query),.active_price(active_price),
 .req_valid(state==KS&&!fault),.req_ready(ka_ready),.req_words(rsp_packet),.req_cookie(rsp_cookie),.req_query(rsp_query),.req_price(rsp_price),
 .rsp_valid(ka_valid),.rsp_ready(state==KW),.rsp_words(ka_words),.rsp_cookie(ka_cookie),.rsp_query(ka_query),.rsp_price(ka_price),.rsp_status(ka_status),.busy(ka_busy),.fault(ka_fault),.retired_idle(ka_retired_idle));
 always @(posedge clk)begin
  if(rst)begin state<=IDLE;stopped<=0;elapsed<=0;sink<=0;expected_y<=0;rsp_status<=0;rsp_cookie<=0;rsp_child<=0;rsp_version<=0;rsp_query<=0;rsp_price<=0;rsp_design<=0;rsp_packet<=0;rsp_cost<=0;rsp_geometry<=0;rsp_geometry_result<=0;end
  else begin
   if(owned&&state!=REPLY&&!stopped)elapsed<=elapsed+1'b1;
   case(state)
    IDLE:if(req_valid&&req_ready)begin
     rsp_cookie<=req_cookie;rsp_child<=req_child;sink<=req_sink;expected_y<=req_y;rsp_version<=active_version;rsp_query<=active_query;rsp_price<=active_price;rsp_design<=active_design;elapsed<=0;rsp_status<=0;rsp_cost<=0;rsp_geometry_result<=0;
     rsp_packet<=0;
     rsp_packet[0*32+:32]<=req_params[5*32+:32];rsp_packet[1*32+:32]<=req_count;
     rsp_packet[2*32+:32]<=req_attrs[191:160];rsp_packet[3*32+:32]<=req_history;rsp_packet[4*32+:32]<=req_price_value;
     rsp_packet[5*32+:32]<=req_net[95:64];rsp_packet[6*32+:32]<=req_center;rsp_packet[7*32+:32]<=req_net[127:96];
     rsp_packet[8*32+:32]<=req_upstream;rsp_packet[9*32+:32]<=req_params[6*32+:32];rsp_packet[10*32+:32]<={{16{req_attrs[159]}},req_attrs[159:144]};
     rsp_packet[11*32+:32]<=req_params[7*32+:32];rsp_packet[13*32+:32]<=req_params[9*32+:32];rsp_packet[14*32+:32]<=req_params[8*32+:32];
     rsp_geometry<=0;rsp_geometry[0*32+:32]<=req_x;rsp_geometry[1*32+:32]<=req_y;rsp_geometry[2*32+:32]<=req_config[8*32+:32];rsp_geometry[3*32+:32]<=req_config[9*32+:32];
     rsp_geometry[6*32+:32]<=req_params[11*32+:32]!=0;rsp_geometry[7*32+:32]<=req_params[10*32+:32];rsp_geometry[10*32+:32]<=req_config[10*32+:32];rsp_geometry[11*32+:32]<=req_config[11*32+:32];
     if(req_params[9*32+:32]!=0)begin rsp_status<=6;stopped<=1;state<=REPLY;end
     else state<=req_params[11*32+:32]!=0?SS:GS;
    end
    SS:if(c_req_ready)state<=SW;
    SW:if(c_rsp_valid&&!fault)begin rsp_geometry[5*32+:32]<=c_rsp_slr;state<=CS;end
    CS:if(c_req_ready)state<=CW;
    CW:if(c_rsp_valid&&!fault)begin rsp_geometry[4*32+:32]<=c_rsp_slr;state<=c_rsp_slr!=rsp_geometry[5*32+:32]?LS:GS;end
    LS:if(c_req_ready)state<=LW;
    LW:if(c_rsp_valid&&!fault)begin rsp_geometry[8*32+:32]<=c_rsp_next;rsp_geometry[9*32+:32]<=c_rsp_prev_column;state<=GS;end
    GS:if(!fault&&ga_ready)state<=GW;
    GW:if(ga_valid)begin
     if(ga_status!=0||ga_cookie!=rsp_cookie||ga_query!=rsp_query||ga_price!=rsp_price||ga_words[31:0]!=0)begin rsp_status<=3;stopped<=1;state<=REPLY;end
     else begin rsp_geometry_result<=ga_words;rsp_packet[12*32+:32]<=ga_words[127:96];state<=KS;end
    end
    KS:if(!fault&&ka_ready)state<=KW;
    KW:if(ka_valid)begin
     if(ka_status!=0||ka_cookie!=rsp_cookie||ka_query!=rsp_query||ka_price!=rsp_price)begin rsp_status<=4;stopped<=1;end
     else rsp_cost<=ka_words;
     state<=REPLY;
    end
    REPLY:if(rsp_ready)state<=IDLE;
    default:stopped<=1;
   endcase
   if(fail_now)begin stopped<=1;if(state!=IDLE&&state!=REPLY)begin rsp_status<=5;state<=REPLY;end end
  end
 end
endmodule
