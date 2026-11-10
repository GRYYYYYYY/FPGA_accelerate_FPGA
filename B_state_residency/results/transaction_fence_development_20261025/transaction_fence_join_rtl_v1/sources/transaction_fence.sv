`timescale 1ns/1ps
// One normal transaction across services; parallel recovery callbacks per lane.
module transaction_fence #(parameter integer LANES=16,REQ_BITS=2432,RSP_BITS=256,ADMIN_FIRST=14,
 parameter[LANES-1:0]CALLBACK_MASK=16'h037f)(
 input wire clk,rst,work_permit,normal_fault,backend_drained,backend_idle,route_block,
 input wire[LANES-1:0]s_valid,output reg[LANES-1:0]s_ready,input wire[LANES*REQ_BITS-1:0]s_payload,
 output reg[LANES-1:0]s_rsp_valid,input wire[LANES-1:0]s_rsp_ready,output wire[LANES*RSP_BITS-1:0]s_rsp_payload,
 input wire[LANES-1:0]cb_valid,output reg[LANES-1:0]cb_ready,input wire[LANES*REQ_BITS-1:0]cb_payload,
 output reg[LANES-1:0]cb_rsp_valid,input wire[LANES-1:0]cb_rsp_ready,output wire[LANES*RSP_BITS-1:0]cb_rsp_payload,
 output reg[LANES-1:0]d_valid,input wire[LANES-1:0]d_ready,output reg[LANES*REQ_BITS-1:0]d_payload,
 input wire[LANES-1:0]d_rsp_valid,output reg[LANES-1:0]d_rsp_ready,input wire[LANES*RSP_BITS-1:0]d_rsp_payload,
 input wire route_valid,output wire route_ready,input wire[191:0]route_payload,output wire route_rsp_valid,input wire route_rsp_ready,
 output wire backend_route_valid,input wire backend_route_ready,output wire[191:0]backend_route_payload,input wire backend_route_rsp_valid,output wire backend_route_rsp_ready,input wire route_error,
 input wire recover_valid,output wire recover_ready,output wire backend_recover_valid,input wire backend_recover_ready,
 output wire recover_rsp_valid,input wire recover_rsp_ready,input wire backend_recover_rsp_valid,output wire backend_recover_rsp_ready,input wire recover_error,
 output wire normal_retired,output wire recovery_owned,output reg fault,output wire[3:0]phase,output reg[LANES-1:0]callback_pending
);
 localparam IDLE=0,LREQ=1,LRSP=2,LDRAIN=3,ROUTE=4,RDRAIN=5,BLOCKED=6,RECWAIT=7,RECSEND=8,RECRUN=9,RECDRAIN=10;
 reg[3:0]state;integer selected,choice;reg[REQ_BITS-1:0]request;reg[191:0]route_request;reg route_send,route_started,route_failed,recovery_failed;
 wire clean=backend_idle&&backend_drained;
 wire callbacks_empty=callback_pending==0&&cb_valid==0;
 wire cb_completion_safe=callbacks_empty&&clean;
 assign phase=state;
 assign normal_retired=!rst&&backend_idle&&((state!=LREQ&&state!=LRSP&&state!=ROUTE)||(state==LREQ||state==LRSP)&&selected>=ADMIN_FIRST);
 assign recovery_owned=!rst&&(state==RECWAIT||state==RECSEND||state==RECRUN||state==RECDRAIN);
 assign route_ready=!rst&&state==IDLE&&!recover_valid&&!fault&&!normal_fault&&work_permit&&clean;
 assign backend_route_valid=!rst&&state==ROUTE&&route_send;
 assign backend_route_payload=route_request;
 assign route_rsp_valid=!rst&&state==ROUTE&&route_started&&backend_route_rsp_valid;
 assign backend_route_rsp_ready=!rst&&state==ROUTE&&route_started&&route_rsp_ready;
 assign backend_recover_valid=!rst&&state==RECSEND;
 assign recover_ready=backend_recover_valid&&backend_recover_ready;
 assign recover_rsp_valid=!rst&&state==RECRUN&&backend_recover_rsp_valid&&cb_completion_safe;
 assign backend_recover_rsp_ready=!rst&&state==RECRUN&&recover_rsp_ready&&cb_completion_safe;
 assign s_rsp_payload=d_rsp_payload;assign cb_rsp_payload=d_rsp_payload;
 always @*begin
  s_ready=0;s_rsp_valid=0;cb_ready=0;cb_rsp_valid=0;d_valid=0;d_payload=0;d_rsp_ready=0;choice=-1;
  if(!rst)begin
   if(state==IDLE&&!recover_valid&&!fault&&!normal_fault&&clean&&!(route_valid&&work_permit))begin
    for(integer i=0;i<LANES;i=i+1)if(choice<0&&s_valid[i]&&(work_permit||i>=ADMIN_FIRST))choice=i;
    if(choice>=0)s_ready[choice]=1;
   end
   if(state==LREQ)begin d_valid[selected]=1;d_payload[selected*REQ_BITS+:REQ_BITS]=request;end
   if(state==LRSP)begin s_rsp_valid[selected]=d_rsp_valid[selected];d_rsp_ready[selected]=s_rsp_ready[selected];end
   if(state==RECRUN)begin
    d_valid=cb_valid&CALLBACK_MASK&~callback_pending;d_payload=cb_payload;
    cb_ready=d_ready&CALLBACK_MASK&~callback_pending;
    cb_rsp_valid=d_rsp_valid&callback_pending;d_rsp_ready=cb_rsp_ready&callback_pending;
   end
  end
 end
 always @(posedge clk)begin
  if(rst)begin state<=IDLE;selected<=0;request<=0;route_request<=0;route_send<=0;route_started<=0;route_failed<=0;recovery_failed<=0;callback_pending<=0;fault<=0;end
  else begin
   if(state==RECRUN)begin
    callback_pending<=(callback_pending|(d_valid&d_ready))&~(d_rsp_valid&d_rsp_ready);
    if((cb_valid&~CALLBACK_MASK)!=0)fault<=1;
   end
   case(state)
    IDLE:begin
     if(recover_valid)state<=RECWAIT;
     else if(route_valid&&route_ready)begin route_request<=route_payload;route_send<=1;route_started<=0;route_failed<=0;state<=ROUTE;end
     else if(choice>=0&&s_valid[choice]&&s_ready[choice])begin selected<=choice;request<=s_payload[choice*REQ_BITS+:REQ_BITS];state<=LREQ;end
     else if(normal_fault||fault)state<=BLOCKED;
    end
    LREQ:if(d_valid[selected]&&d_ready[selected])state<=LRSP;
    LRSP:if(s_rsp_valid[selected]&&s_rsp_ready[selected])state<=LDRAIN;
    LDRAIN:if(clean)begin if(normal_fault||fault)state<=BLOCKED;else state<=IDLE;end
    ROUTE:begin
     if(backend_route_valid&&backend_route_ready)begin route_send<=0;route_started<=1;end
     if(route_rsp_valid&&route_rsp_ready)begin route_started<=0;route_failed<=route_error||normal_fault;state<=RDRAIN;end
    end
    RDRAIN:if(clean&&(route_failed||!route_block))begin if(route_failed||normal_fault||fault)state<=BLOCKED;else state<=IDLE;end
    BLOCKED:if(recover_valid&&!fault)state<=RECWAIT;
    RECWAIT:if(clean&&!fault)state<=RECSEND;
    RECSEND:if(recover_ready)begin callback_pending<=0;state<=RECRUN;end
    RECRUN:if(recover_rsp_valid&&recover_rsp_ready)begin recovery_failed<=recover_error||normal_fault||fault;state<=RECDRAIN;end
    RECDRAIN:if(clean&&callbacks_empty)begin if(recovery_failed||normal_fault||fault)state<=BLOCKED;else state<=IDLE;end
    default:begin fault<=1;state<=BLOCKED;end
   endcase
  end
 end
endmodule
