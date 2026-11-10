`timescale 1ns/1ps
// Immutable owner-snapshot identity; only GET is issued to the proven codec.
module checkpoint_authority_reader #(parameter integer MAX_CYCLES=1048576)(
 input wire clk,rst,abort,cfg_permit,
 input wire cfg_valid,output wire cfg_ready,input wire[63:0]cfg_design,cfg_generation,cfg_primary,cfg_pool,cfg_allocator,
 input wire[31:0]cfg_checkpoint,cfg_nodes,cfg_nets,cfg_capacity,
 input wire rearm_valid,output wire rearm_ready,
 output reg cfg_rsp_valid,input wire cfg_rsp_ready,output reg[2:0]cfg_status,output reg cfg_rearmed,
 output reg configured,output reg[63:0]bound_design,bound_generation,output reg[31:0]bound_checkpoint,
 input wire req_valid,output wire req_ready,input wire[63:0]req_design,req_generation,input wire[31:0]req_checkpoint,req_node,req_net,req_cookie,
 output wire rsp_valid,input wire rsp_ready,output reg[3:0]rsp_status,output reg[63:0]rsp_design,rsp_generation,
 output reg[31:0]rsp_checkpoint,rsp_cookie,rsp_refs,rsp_occupancy,
 output wire busy,fault,drained,
 output wire[63:0]m_araddr,output wire[7:0]m_arlen,output wire[2:0]m_arsize,output wire[1:0]m_arburst,output wire[3:0]m_arid,
 output wire m_arvalid,input wire m_arready,input wire[511:0]m_rdata,input wire[3:0]m_rid,input wire[1:0]m_rresp,input wire m_rlast,m_rvalid,output wire m_rready,
 output wire[63:0]m_awaddr,output wire[7:0]m_awlen,output wire[2:0]m_awsize,output wire[1:0]m_awburst,output wire[3:0]m_awid,
 output wire m_awvalid,input wire m_awready,output wire[511:0]m_wdata,output wire[63:0]m_wstrb,output wire m_wlast,m_wvalid,input wire m_wready,
 input wire[3:0]m_bid,input wire[1:0]m_bresp,input wire m_bvalid,output wire m_bready
);
 localparam IDLE=0,CORE_RESET=1,CFG_SEND=2,CFG_WAIT=3,CFG_REPLY=4,OWNER_SEND=5,OWNER_WAIT=6,REPLY=7;
 reg[2:0]state;reg bound_valid,stopped,config_cancel,read_pending;reg reset_tick,read_cancel;
 reg[63:0]saved_design,saved_generation,saved_primary,saved_pool,saved_allocator;
 reg[31:0]saved_checkpoint,saved_nodes,saved_nets,saved_capacity,held_node,held_net,held_cookie;
 wire core_rst=rst||state==CORE_RESET;
 wire c_cfg_ready,c_cfg_rsp_valid,c_configured,c_req_ready,c_rsp_valid,c_fault,c_busy,c_will_overuse;
 wire[2:0]c_cfg_status;wire[3:0]c_status;wire[31:0]c_cookie,c_refs,c_occupancy;
 assign drained=!rst&&!read_pending&&!m_arvalid&&!m_rvalid&&!m_awvalid&&!m_wvalid&&!m_bvalid;
 assign busy=!rst&&(state!=IDLE||cfg_rsp_valid||c_busy);
 assign fault=!rst&&(stopped||(c_fault&&!core_rst));
 assign cfg_ready=!rst&&state==IDLE&&!cfg_rsp_valid&&cfg_permit&&!abort&&drained&&!c_busy;
 assign rearm_ready=!rst&&state==IDLE&&!cfg_rsp_valid&&!cfg_valid&&bound_valid&&cfg_permit&&!abort&&drained&&!c_busy;
 assign req_ready=!rst&&state==IDLE&&!cfg_rsp_valid&&!cfg_valid&&!rearm_valid&&configured&&!fault&&!abort&&drained&&!c_busy;
 assign rsp_valid=!rst&&state==REPLY;
 owner_state_store #(.MAX_CYCLES(MAX_CYCLES)) store(
 .clk(clk),.rst(core_rst),.abort((abort||read_cancel)&&state==OWNER_WAIT),.cfg_valid(state==CFG_SEND),.cfg_ready(c_cfg_ready),
 .cfg_primary(saved_primary),.cfg_pool(saved_pool),.cfg_allocator(saved_allocator),.cfg_nodes(saved_nodes),.cfg_capacity(saved_capacity),
 .cfg_rsp_valid(c_cfg_rsp_valid),.cfg_rsp_ready(state==CFG_WAIT),.cfg_status(c_cfg_status),.configured(c_configured),
 .req_valid(state==OWNER_SEND),.req_ready(c_req_ready),.req_op(3'd0),.req_cookie(held_cookie),.req_node(held_node),.req_net(held_net),
 .rsp_valid(c_rsp_valid),.rsp_ready(state==OWNER_WAIT&&drained),.rsp_status(c_status),.rsp_cookie(c_cookie),.rsp_count(c_refs),.rsp_occupancy(c_occupancy),.rsp_will_overuse(c_will_overuse),.fault(c_fault),.busy(c_busy),
 .m_araddr(m_araddr),.m_arlen(m_arlen),.m_arsize(m_arsize),.m_arburst(m_arburst),.m_arid(m_arid),.m_arvalid(m_arvalid),.m_arready(m_arready),.m_rdata(m_rdata),.m_rid(m_rid),.m_rresp(m_rresp),.m_rlast(m_rlast),.m_rvalid(m_rvalid),.m_rready(m_rready),
 .m_awaddr(m_awaddr),.m_awlen(m_awlen),.m_awsize(m_awsize),.m_awburst(m_awburst),.m_awid(m_awid),.m_awvalid(m_awvalid),.m_awready(m_awready),.m_wdata(m_wdata),.m_wstrb(m_wstrb),.m_wlast(m_wlast),.m_wvalid(m_wvalid),.m_wready(m_wready),.m_bid(m_bid),.m_bresp(m_bresp),.m_bvalid(m_bvalid),.m_bready(m_bready));
 always @(posedge clk)begin
  if(rst)read_pending<=0;
  else begin
   if(m_arvalid&&m_arready)read_pending<=1;
   if(m_rvalid&&m_rready&&m_rlast)read_pending<=0;
  end
 end
 always @(posedge clk)begin
  if(rst)begin
   state<=IDLE;bound_valid<=0;stopped<=0;config_cancel<=0;reset_tick<=0;read_cancel<=0;configured<=0;
   saved_design<=0;saved_generation<=0;saved_primary<=0;saved_pool<=0;saved_allocator<=0;saved_checkpoint<=0;saved_nodes<=0;saved_nets<=0;saved_capacity<=0;
   bound_design<=0;bound_generation<=0;bound_checkpoint<=0;held_node<=0;held_net<=0;held_cookie<=0;
   cfg_rsp_valid<=0;cfg_status<=0;cfg_rearmed<=0;rsp_status<=0;rsp_design<=0;rsp_generation<=0;rsp_checkpoint<=0;rsp_cookie<=0;rsp_refs<=0;rsp_occupancy<=0;
  end else begin
   if((state==CORE_RESET||state==CFG_SEND||state==CFG_WAIT)&&(!cfg_permit||abort))config_cancel<=1;
   if((state==OWNER_SEND||state==OWNER_WAIT)&&abort)read_cancel<=1;
   case(state)
    IDLE:begin
     if(cfg_valid&&cfg_ready)begin
      cfg_status<=0;cfg_rearmed<=0;config_cancel<=0;
      if(bound_valid||cfg_design==0||cfg_generation==0||cfg_checkpoint==0||cfg_nodes==0||cfg_nets==0||cfg_nets>32'h80000000)begin cfg_status<=1;cfg_rsp_valid<=1;state<=CFG_REPLY;end
      else begin
       saved_design<=cfg_design;saved_generation<=cfg_generation;saved_checkpoint<=cfg_checkpoint;saved_primary<=cfg_primary;saved_pool<=cfg_pool;saved_allocator<=cfg_allocator;saved_nodes<=cfg_nodes;saved_nets<=cfg_nets;saved_capacity<=cfg_capacity;
       configured<=0;reset_tick<=0;state<=CORE_RESET;
      end
     end else if(rearm_valid&&rearm_ready)begin
      stopped<=0;configured<=0;cfg_status<=0;cfg_rearmed<=1;config_cancel<=0;reset_tick<=0;state<=CORE_RESET;
     end else if(req_valid&&req_ready)begin
      read_cancel<=0;held_node<=req_node;held_net<=req_net;held_cookie<=req_cookie;rsp_cookie<=req_cookie;rsp_design<=bound_design;rsp_checkpoint<=bound_checkpoint;rsp_generation<=bound_generation;rsp_refs<=0;rsp_occupancy<=0;rsp_status<=0;
      if(req_design!=bound_design||req_checkpoint!=bound_checkpoint||req_generation!=bound_generation)begin rsp_status<=1;state<=REPLY;end
      else if(req_node>=saved_nodes||req_net>=saved_nets)begin rsp_status<=2;state<=REPLY;end
      else state<=OWNER_SEND;
     end
    end
    CORE_RESET:if(reset_tick)begin reset_tick<=0;state<=CFG_SEND;end else reset_tick<=1;
    CFG_SEND:if(c_cfg_ready)state<=CFG_WAIT;
    CFG_WAIT:if(c_cfg_rsp_valid)begin
     cfg_rsp_valid<=1;state<=CFG_REPLY;
     if(config_cancel||!cfg_permit||abort)begin cfg_status<=3;stopped<=1;end
     else if(c_cfg_status!=0||!c_configured)begin cfg_status<=2;stopped<=1;end
     else begin
      cfg_status<=0;configured<=1;bound_valid<=1;stopped<=0;bound_design<=saved_design;bound_checkpoint<=saved_checkpoint;bound_generation<=saved_generation;
     end
    end
    CFG_REPLY:if(cfg_rsp_valid&&cfg_rsp_ready)begin cfg_rsp_valid<=0;state<=IDLE;end
    OWNER_SEND:if(c_req_ready)state<=OWNER_WAIT;
    OWNER_WAIT:if(c_rsp_valid&&drained)begin
     rsp_status<=(abort||read_cancel)?4'd12:c_cookie==held_cookie?c_status:4'd13;
     if(!abort&&!read_cancel&&c_cookie==held_cookie&&c_status==0)begin rsp_refs<=c_refs;rsp_occupancy<=c_occupancy;end
     else begin rsp_refs<=0;rsp_occupancy<=0;stopped<=1;end
     state<=REPLY;
    end
    REPLY:if(rsp_ready)state<=IDLE;
    default:begin stopped<=1;state<=IDLE;end
   endcase
  end
 end
endmodule
