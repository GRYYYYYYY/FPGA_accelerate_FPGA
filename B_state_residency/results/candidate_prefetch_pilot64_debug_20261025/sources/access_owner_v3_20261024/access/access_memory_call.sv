`timescale 1ns/1ps
// access_step ap_memory ABI: one-cycle input reads, early output writes.
// External query owner must remain stable through response retirement.
module access_memory_call #(parameter integer MAX_CALL_CYCLES=64)(
 input wire clk,rst,abort,
 input wire active,input wire [1:0] active_query,input wire [3:0] active_price,
 input wire req_valid,output wire req_ready,input wire [639:0] req_words,
 input wire [31:0] req_cookie,input wire [1:0] req_query,input wire [3:0] req_price,
 output wire rsp_valid,input wire rsp_ready,output reg [191:0] rsp_words,
 output reg [31:0] rsp_cookie,output reg [1:0] rsp_query,
 output reg [3:0] rsp_price,output reg [1:0] rsp_status,
 output wire busy,fault,
 output wire ap_start,input wire ap_idle,ap_ready,ap_done,
 input wire [4:0] ia0,ia1,input wire ic0,ic1,output reg [31:0] iq0,iq1,
 input wire [2:0] oa0,oa1,input wire oc0,oc1,ow0,ow1,
 input wire [31:0] od0,od1
);
 localparam [1:0] IDLE=0,RUN=1,REPLY=2;
 localparam integer TBITS=$clog2(MAX_CALL_CYCLES+1);
 reg [1:0] state;
 reg stopped,owned;
 reg [639:0] snapshot;
 reg [5:0] seen;
 reg [TBITS-1:0] elapsed;
 wire w0=oc0&&ow0,w1=oc1&&ow1;
 wire [5:0] m0=w0?(6'b1<<oa0):6'b0;
 wire [5:0] m1=w1?(6'b1<<oa1):6'b0;
 wire [5:0] next_seen=seen|m0|m1;
 wire events=ic0||ic1||w0||w1||ap_done||ap_ready;
 // ready and done coincide in the frozen access_step core. Earlier writes are legal.
 wire protocol_error=(state!=RUN && events)||
  (state==RUN && ((ic0&&ia0>=20)||(ic1&&ia1>=20)||
    (w0&&oa0>=6)||(w1&&oa1>=6)||(|(seen&(m0|m1)))||(|(m0&m1))||
    (ap_ready!=ap_done)||(ap_done&&next_seen!=6'b111111)));
 wire owner_error=owned && state!=IDLE &&
  (!active||active_query!=rsp_query||active_price!=rsp_price);
 wire complete=state==RUN&&ap_done&&ap_ready&&(&next_seen);
 wire timeout=state==RUN&&elapsed==MAX_CALL_CYCLES-1&&!complete;
 assign fault=!rst&&(stopped||abort||protocol_error||owner_error||timeout);
 assign req_ready=!rst&&!fault&&state==IDLE&&ap_idle;
 assign rsp_valid=!rst&&state==REPLY;
 assign busy=!rst&&(state!=IDLE||fault);
 // Avoid a ready/CE -> fault -> start combinational feedback loop.
 assign ap_start=!rst&&!stopped&&!abort&&state==RUN;
 always @(posedge clk) begin
  if(rst)begin
   state<=IDLE;stopped<=0;owned<=0;snapshot<=0;seen<=0;elapsed<=0;
   rsp_words<=0;rsp_cookie<=0;rsp_query<=0;rsp_price<=0;rsp_status<=0;iq0<=0;iq1<=0;
  end else begin
   // Already offered data stays stable, even when a late fault invalidates it.
   if(state==REPLY&&rsp_ready)begin state<=IDLE;owned<=0;end
   if(fault)stopped<=1;
   else case(state)
    IDLE:if(req_valid&&req_ready)begin
     snapshot<=req_words;rsp_cookie<=req_cookie;rsp_query<=req_query;rsp_price<=req_price;
     rsp_words<=0;seen<=0;elapsed<=0;owned<=0;
     if(!active)begin rsp_status<=1;state<=REPLY;end
     else if(req_query!=active_query||req_price!=active_price)begin rsp_status<=2;state<=REPLY;end
     else begin rsp_status<=0;state<=RUN;owned<=1;end
    end
    RUN:begin
     elapsed<=elapsed+1'b1;
     if(ic0)iq0<=snapshot[ia0*32+:32];
     if(ic1)iq1<=snapshot[ia1*32+:32];
     if(w0)rsp_words[oa0*32+:32]<=od0;
     if(w1)rsp_words[oa1*32+:32]<=od1;
     seen<=next_seen;
     if(complete)state<=REPLY;
    end
    default:begin end
   endcase
  end
 end
endmodule
