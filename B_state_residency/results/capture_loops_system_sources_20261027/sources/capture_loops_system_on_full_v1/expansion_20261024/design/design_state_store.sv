`timescale 1ns/1ps
// One exclusive design-lifecycle store. Backing must be zeroed once per design.
// Record: flags32(created/dead/cache_valid/sink), raw_count32, keep_mask32, reserved32.
module design_state_store(
 input wire clk,rst,
 input wire cfg_valid,output wire cfg_ready,input wire[63:0]cfg_base,input wire[31:0]cfg_nodes,
 output reg cfg_rsp_valid,input wire cfg_rsp_ready,output reg[2:0]cfg_status,output reg configured,
 input wire req_valid,output wire req_ready,input wire[2:0]req_op,input wire[31:0]req_cookie,req_owner,req_node,req_arg,
 output wire rsp_valid,input wire rsp_ready,output reg[3:0]rsp_status,
 output reg[31:0]rsp_cookie,rsp_flags,rsp_count,rsp_mask,output wire fault,
 output reg claim_active,output reg[31:0]claim_owner,claim_node,claim_count,claim_mask,
 output reg[63:0]m_araddr,output wire[7:0]m_arlen,output wire[2:0]m_arsize,output wire[1:0]m_arburst,output wire[3:0]m_arid,
 output wire m_arvalid,input wire m_arready,input wire[511:0]m_rdata,input wire[3:0]m_rid,input wire[1:0]m_rresp,input wire m_rlast,m_rvalid,output wire m_rready,
 output wire[63:0]m_awaddr,output wire[7:0]m_awlen,output wire[2:0]m_awsize,output wire[1:0]m_awburst,output wire[3:0]m_awid,
 output wire m_awvalid,input wire m_awready,output reg[511:0]m_wdata,output reg[63:0]m_wstrb,output wire m_wlast,m_wvalid,input wire m_wready,
 input wire[3:0]m_bid,input wire[1:0]m_bresp,input wire m_bvalid,output wire m_bready
);
 localparam IDLE=0,READ_ADDR=1,READ_DATA=2,WRITE=3,WRITE_RESP=4,REPLY=5;
 localparam GET=0,CLAIM=1,CREATE=2,DEAD=3,EMIT=4,PUBLISH=5,SINK=6;
 reg[2:0]state,op;
 reg stopped,aw_done,w_done,have_position;
 reg[31:0]last_position,node,arg,owner,nodes;
 reg[1:0]lane;
 reg[63:0]base;
 reg[127:0]write_record;
 wire[64:0]cfg_bytes=({33'b0,cfg_nodes}*65'd16+65'd63)&~65'd63;
 wire[64:0]cfg_last={1'b0,cfg_base}+cfg_bytes-1'b1;
 wire unexpected_r=m_rvalid&&state!=READ_DATA&&!(state==READ_ADDR&&m_arready);
 wire unexpected_b=m_bvalid&&state!=WRITE_RESP&&!(state==WRITE&&(aw_done||m_awready)&&(w_done||m_wready));
 assign fault=!rst&&(stopped||unexpected_r||unexpected_b);
 assign cfg_ready=!rst&&!fault&&!configured&&!cfg_rsp_valid&&state==IDLE;
 assign req_ready=!rst&&!fault&&!cfg_rsp_valid&&state==IDLE&&!(cfg_valid&&cfg_ready);
 assign rsp_valid=!rst&&state==REPLY;
 assign m_arvalid=!rst&&!fault&&state==READ_ADDR;
 assign m_rready=!rst&&!fault&&state==READ_DATA;
 assign m_awvalid=!rst&&!fault&&state==WRITE&&!aw_done;
 assign m_wvalid=!rst&&!fault&&state==WRITE&&!w_done;
 assign m_bready=!rst&&!fault&&state==WRITE_RESP;
 assign m_awaddr=m_araddr;
 assign m_arlen=0;assign m_awlen=0;assign m_arsize=6;assign m_awsize=6;
 assign m_arburst=1;assign m_awburst=1;assign m_arid=0;assign m_awid=0;assign m_wlast=1;
 wire[127:0]record=m_rdata[lane*128+:128];
 wire[31:0]flags=record[31:0],count=record[63:32],mask=record[95:64];
 wire corrupt=record[127:96]!=0||flags[31:4]!=0||count>32||
              (!flags[2]&&(count!=0||mask!=0))||(flags[2]&&(mask>>count)!=0);
 task fail(input[3:0]status);
  begin rsp_status<=status;stopped<=1;state<=REPLY;end
 endtask
 task reply_record(input[127:0]value);
  begin rsp_flags<=value[31:0];rsp_count<=value[63:32];rsp_mask<=value[95:64];state<=REPLY;end
 endtask
 task write_value(input[127:0]value);
  begin
   write_record<=value;m_wdata<=({384'b0,value}<<(lane*128));m_wstrb<=64'hffff<<(lane*16);
   aw_done<=0;w_done<=0;state<=WRITE;
  end
 endtask
 wire[31:0]updated_flags=flags|(op==CREATE?32'd1:op==DEAD?32'd2:32'd8);
 always @(posedge clk)begin
  if(rst)begin
   state<=IDLE;op<=0;stopped<=0;aw_done<=0;w_done<=0;have_position<=0;last_position<=0;
   node<=0;arg<=0;owner<=0;nodes<=0;lane<=0;base<=0;write_record<=0;
   cfg_rsp_valid<=0;cfg_status<=0;configured<=0;
   rsp_status<=0;rsp_cookie<=0;rsp_flags<=0;rsp_count<=0;rsp_mask<=0;
   claim_active<=0;claim_owner<=0;claim_node<=0;claim_count<=0;claim_mask<=0;
   m_araddr<=0;m_wdata<=0;m_wstrb<=0;
  end else begin
   if(cfg_rsp_valid&&cfg_rsp_ready)cfg_rsp_valid<=0;
   if(state==REPLY&&rsp_ready)state<=IDLE;
   if(!stopped&&(unexpected_r||unexpected_b))begin
    stopped<=1;if(state!=IDLE&&state!=REPLY)begin rsp_status<=7;state<=REPLY;end
   end else if(!stopped)begin
    if(cfg_valid&&cfg_ready)begin
     cfg_rsp_valid<=1;cfg_status<=0;
     if(cfg_base[5:0]!=0)cfg_status<=1;
     else if(cfg_nodes==0||cfg_nodes>32'h01000000||cfg_last[64])cfg_status<=2;
     else begin configured<=1;base<=cfg_base;nodes<=cfg_nodes;end
    end
    case(state)
     IDLE:if(req_valid&&req_ready)begin
      rsp_cookie<=req_cookie;rsp_status<=0;rsp_flags<=0;rsp_count<=0;rsp_mask<=0;
      op<=req_op;node<=req_node;arg<=req_arg;owner<=req_owner;lane<=req_node[1:0];
      if(!configured)begin rsp_status<=1;state<=REPLY;end
      else if(req_op>6||req_node>=nodes||(req_op==CLAIM&&req_arg>32)||
              (req_op!=CLAIM&&req_op!=EMIT&&req_arg!=0))begin rsp_status<=2;state<=REPLY;end
      else if(req_op==CLAIM&&claim_active)begin rsp_status<=3;state<=REPLY;end
      else if((req_op==CLAIM&&req_owner==0)||
              (req_op!=CLAIM&&((claim_active&&req_owner!=claim_owner)||(!claim_active&&req_owner!=0)))||
              ((req_op==EMIT||req_op==PUBLISH)&&(!claim_active||req_node!=claim_node))||
              (req_op==SINK&&claim_active))begin rsp_status<=4;state<=REPLY;end
      else if(req_op==EMIT)begin
       if(req_arg>=claim_count||(have_position&&req_arg<=last_position))begin rsp_status<=2;state<=REPLY;end
       else begin
        claim_mask<=claim_mask|(32'b1<<req_arg);last_position<=req_arg;have_position<=1;
        rsp_count<=claim_count;rsp_mask<=claim_mask|(32'b1<<req_arg);state<=REPLY;
       end
      end else begin m_araddr<=base+({32'b0,req_node[31:2],2'b00}<<4);state<=READ_ADDR;end
     end
     READ_ADDR:if(m_arready)state<=READ_DATA;
     READ_DATA:if(m_rvalid&&m_rready)begin
      if(m_rresp!=0||m_rid!=0||!m_rlast)fail(5);
      else if(corrupt)fail(6);
      else case(op)
       GET:reply_record(record);
       CLAIM:begin
        if(flags[2]&&count!=arg)fail(6);
        else begin
         if(!flags[2])begin claim_active<=1;claim_owner<=owner;claim_node<=node;claim_count<=arg;claim_mask<=0;have_position<=0;end
         reply_record(record);
        end
       end
       CREATE,DEAD,SINK:begin
        if(updated_flags==flags)reply_record(record);
        else write_value({32'b0,mask,count,updated_flags});
       end
       PUBLISH:begin
        if(flags[2])fail(6);
        else write_value({32'b0,claim_mask,claim_count,flags|32'd4});
       end
       default:fail(6);
      endcase
     end
     WRITE:begin
      if(m_awvalid&&m_awready)aw_done<=1;
      if(m_wvalid&&m_wready)w_done<=1;
      if((aw_done||m_awready)&&(w_done||m_wready))state<=WRITE_RESP;
     end
     WRITE_RESP:if(m_bvalid&&m_bready)begin
      if(m_bid!=0||m_bresp!=0)fail(5);
      else begin
       if(op==PUBLISH)begin claim_active<=0;claim_owner<=0;claim_node<=0;claim_count<=0;claim_mask<=0;have_position<=0;end
       reply_record(write_record);
      end
     end
     default:begin end
    endcase
   end
  end
 end
endmodule
