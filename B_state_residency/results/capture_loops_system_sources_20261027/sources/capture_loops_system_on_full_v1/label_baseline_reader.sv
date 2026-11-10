`timescale 1ns/1ps
// Immutable baseline: 32-byte records, payload160 + 96 zero padding bits.
// Configuration must be authorized by an external quiescent/context guard.
module label_baseline_reader(
 input wire clk,rst,
 input wire cfg_valid,output wire cfg_ready,input wire cfg_permit,
 input wire[63:0]cfg_base,cfg_epoch,input wire[31:0]cfg_count,
 output wire cfg_rsp_valid,input wire cfg_rsp_ready,output reg[3:0]cfg_status,
 input wire req_valid,output wire req_ready,input wire[31:0]req_node,input wire[63:0]req_epoch,
 output wire rsp_valid,input wire rsp_ready,output reg[3:0]rsp_status,
 output reg[31:0]rsp_node,output reg[63:0]rsp_epoch,output reg[159:0]rsp_payload,
 output wire idle,output reg configured,
 output reg[63:0]araddr,output wire[7:0]arlen,output wire[2:0]arsize,
 output wire[1:0]arburst,output wire[3:0]arid,output wire arvalid,input wire arready,
 input wire[511:0]rdata,input wire[1:0]rresp,input wire[3:0]rid,input wire rlast,rvalid,output wire rready
);
 localparam IDLE=0,CFG_REPLY=1,AR=2,READ=3,REPLY=4;
 reg[2:0]state;reg[63:0]base,epoch;reg[31:0]count;reg upper;
 wire[64:0]cfg_end={1'b0,cfg_base}+({33'b0,cfg_count}<<5);
 wire[255:0]record_data=upper?rdata[511:256]:rdata[255:0];
 assign idle=!rst&&state==IDLE;
 assign cfg_ready=idle;
 assign req_ready=idle&&!cfg_valid;
 assign cfg_rsp_valid=!rst&&state==CFG_REPLY;
 assign rsp_valid=!rst&&state==REPLY;
 assign arvalid=!rst&&state==AR;
 assign rready=!rst&&state==READ;
 assign arlen=0;assign arsize=6;assign arburst=1;assign arid=0;
 always @(posedge clk)begin
  if(rst)begin state<=IDLE;configured<=0;base<=0;epoch<=0;count<=0;upper<=0;
   cfg_status<=0;rsp_status<=0;rsp_node<=0;rsp_epoch<=0;rsp_payload<=0;araddr<=0;
  end else case(state)
   IDLE:begin
    if(cfg_valid&&cfg_ready)begin
     cfg_status<=0;state<=CFG_REPLY;
     if(!cfg_permit)cfg_status<=5;
     else if(cfg_base[5:0]!=0||cfg_count==0||cfg_count>32'h1000000||cfg_epoch==0||cfg_end[64])cfg_status<=2;
     else begin base<=cfg_base;epoch<=cfg_epoch;count<=cfg_count;configured<=1;end
    end else if(req_valid&&req_ready)begin
     rsp_node<=req_node;rsp_epoch<=req_epoch;rsp_payload<=0;rsp_status<=0;state<=REPLY;
     if(!configured||req_epoch!=epoch)rsp_status<=5;
     else if(req_node>=count)rsp_status<=1;
     else begin araddr<=base+({32'b0,req_node>>1}<<6);upper<=req_node[0];state<=AR;end
    end
   end
   CFG_REPLY:if(cfg_rsp_ready)state<=IDLE;
   AR:if(arready)state<=READ;
   READ:if(rvalid&&rready)begin
    state<=REPLY;
    if(rresp!=0||rid!=0||!rlast)rsp_status<=3;
    else if(record_data[255:160]!=0||record_data[159:136]!=0)rsp_status<=4;
    else rsp_payload<=record_data[159:0];
   end
   REPLY:if(rsp_ready)state<=IDLE;
   default:state<=IDLE;
  endcase
 end
endmodule
