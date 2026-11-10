`timescale 1ns/1ps
// Immutable owner-snapshot identity; only GET is issued to the proven codec.
module checkpoint_authority_rotator #(parameter integer MAX_CYCLES=1048576)(
 input wire cfg_stage,publish_valid,publish_permit,discard_valid,
 output wire publish_ready,discard_ready,active_slot,staged_valid,
 output wire[63:0]staged_design,staged_generation,output wire[31:0]staged_checkpoint,
 input wire clk,rst,abort,cfg_permit,
 input wire cfg_valid,output wire cfg_ready,input wire[63:0]cfg_design,cfg_generation,cfg_primary,cfg_pool,cfg_allocator,
 input wire[31:0]cfg_checkpoint,cfg_nodes,cfg_nets,cfg_capacity,
 input wire rearm_valid,output wire rearm_ready,
 output wire cfg_rsp_valid,input wire cfg_rsp_ready,output wire[2:0]cfg_status,output wire cfg_rearmed,
 output wire configured,output wire[63:0]bound_design,bound_generation,output wire[31:0]bound_checkpoint,
 input wire req_valid,output wire req_ready,input wire[63:0]req_design,req_generation,input wire[31:0]req_checkpoint,req_node,req_net,req_cookie,
 output wire rsp_valid,input wire rsp_ready,output wire[3:0]rsp_status,output wire[63:0]rsp_design,rsp_generation,
 output wire[31:0]rsp_checkpoint,rsp_cookie,rsp_refs,rsp_occupancy,
 output wire busy,fault,drained,
 output wire[63:0]m_araddr,output wire[7:0]m_arlen,output wire[2:0]m_arsize,output wire[1:0]m_arburst,output wire[3:0]m_arid,
 output wire m_arvalid,input wire m_arready,input wire[511:0]m_rdata,input wire[3:0]m_rid,input wire[1:0]m_rresp,input wire m_rlast,m_rvalid,output wire m_rready,
 output wire[63:0]m_awaddr,output wire[7:0]m_awlen,output wire[2:0]m_awsize,output wire[1:0]m_awburst,output wire[3:0]m_awid,
 output wire m_awvalid,input wire m_awready,output wire[511:0]m_wdata,output wire[63:0]m_wstrb,output wire m_wlast,m_wvalid,input wire m_wready,
 input wire[3:0]m_bid,input wire[1:0]m_bresp,input wire m_bvalid,output wire m_bready
);

 localparam IDLE=0,RESET_BANK=1,SEND_CFG=2,WAIT_CFG=3,HELD_CFG=4;
 reg[2:0]state;reg active_bank,target,staging,prepared;reg[2:0]held_status;
 reg [63:0]h_cfg_design;
 reg [63:0]h_cfg_generation;
 reg [63:0]h_cfg_primary;
 reg [63:0]h_cfg_pool;
 reg [63:0]h_cfg_allocator;
 reg [31:0]h_cfg_checkpoint;
 reg [31:0]h_cfg_nodes;
 reg [31:0]h_cfg_nets;
 reg [31:0]h_cfg_capacity;
 wire b0_cfg_ready;
 wire b0_rearm_ready;
 wire b0_cfg_rsp_valid;
 wire [2:0]b0_cfg_status;
 wire b0_cfg_rearmed;
 wire b0_configured;
 wire [63:0]b0_bound_design;
 wire [63:0]b0_bound_generation;
 wire [31:0]b0_bound_checkpoint;
 wire b0_req_ready;
 wire b0_rsp_valid;
 wire [3:0]b0_rsp_status;
 wire [63:0]b0_rsp_design;
 wire [63:0]b0_rsp_generation;
 wire [31:0]b0_rsp_checkpoint;
 wire [31:0]b0_rsp_cookie;
 wire [31:0]b0_rsp_refs;
 wire [31:0]b0_rsp_occupancy;
 wire b0_busy;
 wire b0_fault;
 wire b0_drained;
 wire [63:0]b0_m_araddr;
 wire [7:0]b0_m_arlen;
 wire [2:0]b0_m_arsize;
 wire [1:0]b0_m_arburst;
 wire [3:0]b0_m_arid;
 wire b0_m_arvalid;
 wire b0_m_rready;
 wire [63:0]b0_m_awaddr;
 wire [7:0]b0_m_awlen;
 wire [2:0]b0_m_awsize;
 wire [1:0]b0_m_awburst;
 wire [3:0]b0_m_awid;
 wire b0_m_awvalid;
 wire [511:0]b0_m_wdata;
 wire [63:0]b0_m_wstrb;
 wire b0_m_wlast;
 wire b0_m_wvalid;
 wire b0_m_bready;
 wire b1_cfg_ready;
 wire b1_rearm_ready;
 wire b1_cfg_rsp_valid;
 wire [2:0]b1_cfg_status;
 wire b1_cfg_rearmed;
 wire b1_configured;
 wire [63:0]b1_bound_design;
 wire [63:0]b1_bound_generation;
 wire [31:0]b1_bound_checkpoint;
 wire b1_req_ready;
 wire b1_rsp_valid;
 wire [3:0]b1_rsp_status;
 wire [63:0]b1_rsp_design;
 wire [63:0]b1_rsp_generation;
 wire [31:0]b1_rsp_checkpoint;
 wire [31:0]b1_rsp_cookie;
 wire [31:0]b1_rsp_refs;
 wire [31:0]b1_rsp_occupancy;
 wire b1_busy;
 wire b1_fault;
 wire b1_drained;
 wire [63:0]b1_m_araddr;
 wire [7:0]b1_m_arlen;
 wire [2:0]b1_m_arsize;
 wire [1:0]b1_m_arburst;
 wire [3:0]b1_m_arid;
 wire b1_m_arvalid;
 wire b1_m_rready;
 wire [63:0]b1_m_awaddr;
 wire [7:0]b1_m_awlen;
 wire [2:0]b1_m_awsize;
 wire [1:0]b1_m_awburst;
 wire [3:0]b1_m_awid;
 wire b1_m_awvalid;
 wire [511:0]b1_m_wdata;
 wire [63:0]b1_m_wstrb;
 wire b1_m_wlast;
 wire b1_m_wvalid;
 wire b1_m_bready;

 wire cfg_busy=state!=IDLE;
 wire axi_bank=cfg_busy?target:active_bank;
 wire all_quiet=!b0_busy&&!b1_busy&&b0_drained&&b1_drained;
 wire active_fault=active_bank?b1_fault:b0_fault;
 wire inactive_configured=active_bank?b0_configured:b1_configured;
 wire inactive_fault=active_bank?b0_fault:b1_fault;
 assign active_slot=active_bank;
 assign configured=active_bank?b1_configured:b0_configured;
 assign bound_design=active_bank?b1_bound_design:b0_bound_design;
 assign bound_generation=active_bank?b1_bound_generation:b0_bound_generation;
 assign bound_checkpoint=active_bank?b1_bound_checkpoint:b0_bound_checkpoint;
 assign fault=active_fault;
 assign busy=cfg_busy||b0_busy||b1_busy;
 assign drained=b0_drained&&b1_drained;
 assign cfg_ready=!rst&&state==IDLE&&cfg_permit&&!abort&&!publish_valid&&!discard_valid&&!rearm_valid&&all_quiet;
 assign cfg_rsp_valid=!rst&&(state==HELD_CFG||(state==IDLE&&(active_bank?b1_cfg_rsp_valid:b0_cfg_rsp_valid)));
 assign cfg_status=state==HELD_CFG?held_status:(active_bank?b1_cfg_status:b0_cfg_status);
 assign cfg_rearmed=state==HELD_CFG?1'b0:(active_bank?b1_cfg_rearmed:b0_cfg_rearmed);
 assign rearm_ready=!rst&&state==IDLE&&!cfg_valid&&!publish_valid&&!discard_valid&&(active_bank?b1_rearm_ready:b0_rearm_ready);
 assign req_ready=!rst&&state==IDLE&&!cfg_valid&&!publish_valid&&!discard_valid&&!rearm_valid&&(active_bank?b1_req_ready:b0_req_ready);
 assign staged_valid=!rst&&!abort&&state==IDLE&&prepared&&inactive_configured&&!inactive_fault;
 assign staged_design=staged_valid?(active_bank?b0_bound_design:b1_bound_design):64'd0;
 assign staged_generation=staged_valid?(active_bank?b0_bound_generation:b1_bound_generation):64'd0;
 assign staged_checkpoint=staged_valid?(active_bank?b0_bound_checkpoint:b1_bound_checkpoint):32'd0;
 assign publish_ready=!rst&&!abort&&staged_valid&&publish_permit&&!cfg_valid&&!rearm_valid&&!discard_valid&&!req_valid&&!active_fault&&all_quiet;
 assign discard_ready=!rst&&!abort&&staged_valid&&publish_permit&&!cfg_valid&&!rearm_valid&&!publish_valid&&!req_valid&&all_quiet;
 assign rsp_valid=active_bank?b1_rsp_valid:b0_rsp_valid;
 assign rsp_status=active_bank?b1_rsp_status:b0_rsp_status;
 assign rsp_design=active_bank?b1_rsp_design:b0_rsp_design;
 assign rsp_generation=active_bank?b1_rsp_generation:b0_rsp_generation;
 assign rsp_checkpoint=active_bank?b1_rsp_checkpoint:b0_rsp_checkpoint;
 assign rsp_cookie=active_bank?b1_rsp_cookie:b0_rsp_cookie;
 assign rsp_refs=active_bank?b1_rsp_refs:b0_rsp_refs;
 assign rsp_occupancy=active_bank?b1_rsp_occupancy:b0_rsp_occupancy;
 assign m_araddr=axi_bank?b1_m_araddr:b0_m_araddr;
 assign m_arlen=axi_bank?b1_m_arlen:b0_m_arlen;
 assign m_arsize=axi_bank?b1_m_arsize:b0_m_arsize;
 assign m_arburst=axi_bank?b1_m_arburst:b0_m_arburst;
 assign m_arid=axi_bank?b1_m_arid:b0_m_arid;
 assign m_arvalid=axi_bank?b1_m_arvalid:b0_m_arvalid;
 assign m_rready=axi_bank?b1_m_rready:b0_m_rready;
 assign m_awaddr=axi_bank?b1_m_awaddr:b0_m_awaddr;
 assign m_awlen=axi_bank?b1_m_awlen:b0_m_awlen;
 assign m_awsize=axi_bank?b1_m_awsize:b0_m_awsize;
 assign m_awburst=axi_bank?b1_m_awburst:b0_m_awburst;
 assign m_awid=axi_bank?b1_m_awid:b0_m_awid;
 assign m_awvalid=axi_bank?b1_m_awvalid:b0_m_awvalid;
 assign m_wdata=axi_bank?b1_m_wdata:b0_m_wdata;
 assign m_wstrb=axi_bank?b1_m_wstrb:b0_m_wstrb;
 assign m_wlast=axi_bank?b1_m_wlast:b0_m_wlast;
 assign m_wvalid=axi_bank?b1_m_wvalid:b0_m_wvalid;
 assign m_bready=axi_bank?b1_m_bready:b0_m_bready;
 checkpoint_authority_reader #(.MAX_CYCLES(MAX_CYCLES)) bank0(.clk(clk),.rst(rst||(state==RESET_BANK&&target==0)),.abort(abort),.cfg_permit(cfg_permit),.cfg_valid(state==SEND_CFG&&target==0),.cfg_ready(b0_cfg_ready),.cfg_design(h_cfg_design),.cfg_generation(h_cfg_generation),.cfg_primary(h_cfg_primary),.cfg_pool(h_cfg_pool),.cfg_allocator(h_cfg_allocator),.cfg_checkpoint(h_cfg_checkpoint),.cfg_nodes(h_cfg_nodes),.cfg_nets(h_cfg_nets),.cfg_capacity(h_cfg_capacity),.rearm_valid(state==IDLE&&active_bank==0&&!cfg_valid&&!publish_valid&&!discard_valid&&rearm_valid),.rearm_ready(b0_rearm_ready),.cfg_rsp_valid(b0_cfg_rsp_valid),.cfg_rsp_ready((state==WAIT_CFG&&target==0)||(state==IDLE&&active_bank==0&&cfg_rsp_ready)),.cfg_status(b0_cfg_status),.cfg_rearmed(b0_cfg_rearmed),.configured(b0_configured),.bound_design(b0_bound_design),.bound_generation(b0_bound_generation),.bound_checkpoint(b0_bound_checkpoint),.req_valid(state==IDLE&&active_bank==0&&!cfg_valid&&!publish_valid&&!discard_valid&&!rearm_valid&&req_valid),.req_ready(b0_req_ready),.req_design(req_design),.req_generation(req_generation),.req_checkpoint(req_checkpoint),.req_node(req_node),.req_net(req_net),.req_cookie(req_cookie),.rsp_valid(b0_rsp_valid),.rsp_ready(state==IDLE&&active_bank==0&&rsp_ready),.rsp_status(b0_rsp_status),.rsp_design(b0_rsp_design),.rsp_generation(b0_rsp_generation),.rsp_checkpoint(b0_rsp_checkpoint),.rsp_cookie(b0_rsp_cookie),.rsp_refs(b0_rsp_refs),.rsp_occupancy(b0_rsp_occupancy),.busy(b0_busy),.fault(b0_fault),.drained(b0_drained),.m_araddr(b0_m_araddr),.m_arlen(b0_m_arlen),.m_arsize(b0_m_arsize),.m_arburst(b0_m_arburst),.m_arid(b0_m_arid),.m_arvalid(b0_m_arvalid),.m_arready(axi_bank==0&&m_arready),.m_rdata(m_rdata),.m_rid(m_rid),.m_rresp(m_rresp),.m_rlast(m_rlast),.m_rvalid(axi_bank==0&&m_rvalid),.m_rready(b0_m_rready),.m_awaddr(b0_m_awaddr),.m_awlen(b0_m_awlen),.m_awsize(b0_m_awsize),.m_awburst(b0_m_awburst),.m_awid(b0_m_awid),.m_awvalid(b0_m_awvalid),.m_awready(axi_bank==0&&m_awready),.m_wdata(b0_m_wdata),.m_wstrb(b0_m_wstrb),.m_wlast(b0_m_wlast),.m_wvalid(b0_m_wvalid),.m_wready(axi_bank==0&&m_wready),.m_bid(m_bid),.m_bresp(m_bresp),.m_bvalid(axi_bank==0&&m_bvalid),.m_bready(b0_m_bready));
 checkpoint_authority_reader #(.MAX_CYCLES(MAX_CYCLES)) bank1(.clk(clk),.rst(rst||(state==RESET_BANK&&target==1)),.abort(abort),.cfg_permit(cfg_permit),.cfg_valid(state==SEND_CFG&&target==1),.cfg_ready(b1_cfg_ready),.cfg_design(h_cfg_design),.cfg_generation(h_cfg_generation),.cfg_primary(h_cfg_primary),.cfg_pool(h_cfg_pool),.cfg_allocator(h_cfg_allocator),.cfg_checkpoint(h_cfg_checkpoint),.cfg_nodes(h_cfg_nodes),.cfg_nets(h_cfg_nets),.cfg_capacity(h_cfg_capacity),.rearm_valid(state==IDLE&&active_bank==1&&!cfg_valid&&!publish_valid&&!discard_valid&&rearm_valid),.rearm_ready(b1_rearm_ready),.cfg_rsp_valid(b1_cfg_rsp_valid),.cfg_rsp_ready((state==WAIT_CFG&&target==1)||(state==IDLE&&active_bank==1&&cfg_rsp_ready)),.cfg_status(b1_cfg_status),.cfg_rearmed(b1_cfg_rearmed),.configured(b1_configured),.bound_design(b1_bound_design),.bound_generation(b1_bound_generation),.bound_checkpoint(b1_bound_checkpoint),.req_valid(state==IDLE&&active_bank==1&&!cfg_valid&&!publish_valid&&!discard_valid&&!rearm_valid&&req_valid),.req_ready(b1_req_ready),.req_design(req_design),.req_generation(req_generation),.req_checkpoint(req_checkpoint),.req_node(req_node),.req_net(req_net),.req_cookie(req_cookie),.rsp_valid(b1_rsp_valid),.rsp_ready(state==IDLE&&active_bank==1&&rsp_ready),.rsp_status(b1_rsp_status),.rsp_design(b1_rsp_design),.rsp_generation(b1_rsp_generation),.rsp_checkpoint(b1_rsp_checkpoint),.rsp_cookie(b1_rsp_cookie),.rsp_refs(b1_rsp_refs),.rsp_occupancy(b1_rsp_occupancy),.busy(b1_busy),.fault(b1_fault),.drained(b1_drained),.m_araddr(b1_m_araddr),.m_arlen(b1_m_arlen),.m_arsize(b1_m_arsize),.m_arburst(b1_m_arburst),.m_arid(b1_m_arid),.m_arvalid(b1_m_arvalid),.m_arready(axi_bank==1&&m_arready),.m_rdata(m_rdata),.m_rid(m_rid),.m_rresp(m_rresp),.m_rlast(m_rlast),.m_rvalid(axi_bank==1&&m_rvalid),.m_rready(b1_m_rready),.m_awaddr(b1_m_awaddr),.m_awlen(b1_m_awlen),.m_awsize(b1_m_awsize),.m_awburst(b1_m_awburst),.m_awid(b1_m_awid),.m_awvalid(b1_m_awvalid),.m_awready(axi_bank==1&&m_awready),.m_wdata(b1_m_wdata),.m_wstrb(b1_m_wstrb),.m_wlast(b1_m_wlast),.m_wvalid(b1_m_wvalid),.m_wready(axi_bank==1&&m_wready),.m_bid(m_bid),.m_bresp(m_bresp),.m_bvalid(axi_bank==1&&m_bvalid),.m_bready(b1_m_bready));

 always @(posedge clk)begin
  if(rst)begin state<=IDLE;active_bank<=0;target<=0;staging<=0;prepared<=0;held_status<=0;
   h_cfg_design<=0;
   h_cfg_generation<=0;
   h_cfg_primary<=0;
   h_cfg_pool<=0;
   h_cfg_allocator<=0;
   h_cfg_checkpoint<=0;
   h_cfg_nodes<=0;
   h_cfg_nets<=0;
   h_cfg_capacity<=0;

  end else begin
   case(state)
    IDLE:begin
     if(cfg_valid&&cfg_ready)begin
      staging<=cfg_stage;held_status<=0;
      if((!cfg_stage&&(bound_generation!=0))||(cfg_stage&&(!configured||prepared||cfg_design!=bound_design||cfg_generation<=bound_generation||cfg_checkpoint<=bound_checkpoint)))begin held_status<=1;state<=HELD_CFG;end
      else begin
       target<=cfg_stage?~active_bank:active_bank;prepared<=0;
       h_cfg_design<=cfg_design;
       h_cfg_generation<=cfg_generation;
       h_cfg_primary<=cfg_primary;
       h_cfg_pool<=cfg_pool;
       h_cfg_allocator<=cfg_allocator;
       h_cfg_checkpoint<=cfg_checkpoint;
       h_cfg_nodes<=cfg_nodes;
       h_cfg_nets<=cfg_nets;
       h_cfg_capacity<=cfg_capacity;

       state<=RESET_BANK;
      end
     end else if(publish_valid&&publish_ready)begin active_bank<=~active_bank;prepared<=0;end
     else if(discard_valid&&discard_ready)prepared<=0;
    end
    RESET_BANK:if(abort||!cfg_permit)begin held_status<=3;state<=HELD_CFG;end else state<=SEND_CFG;
    SEND_CFG:if(abort||!cfg_permit)begin held_status<=3;state<=HELD_CFG;end
             else if(target?b1_cfg_ready:b0_cfg_ready)state<=WAIT_CFG;
    WAIT_CFG:if(target?b1_cfg_rsp_valid:b0_cfg_rsp_valid)begin
     held_status<=target?b1_cfg_status:b0_cfg_status;
     if(staging&&(target?b1_cfg_status:b0_cfg_status)==0)prepared<=1;
     state<=HELD_CFG;
    end
    HELD_CFG:if(cfg_rsp_ready)state<=IDLE;
    default:state<=IDLE;
   endcase
   // Cancellation never changes the active selector; it invalidates pending publication.
   if(abort)prepared<=0;
  end
 end
endmodule
