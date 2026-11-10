module ka_active_configured_formal(input wire clk);
(* anyseq *) reg  cfg_stage;
(* anyseq *) reg  publish_valid;
(* anyseq *) reg  publish_permit;
(* anyseq *) reg  discard_valid;
wire  publish_ready;
wire  discard_ready;
wire  active_slot;
wire  staged_valid;
wire [63:0] staged_design;
wire [63:0] staged_generation;
wire [31:0] staged_checkpoint;
(* anyseq *) reg  rst;
(* anyseq *) reg  abort;
(* anyseq *) reg  cfg_permit;
(* anyseq *) reg  cfg_valid;
wire  cfg_ready;
(* anyseq *) reg [63:0] cfg_design;
(* anyseq *) reg [63:0] cfg_generation;
(* anyseq *) reg [63:0] cfg_primary;
(* anyseq *) reg [63:0] cfg_pool;
(* anyseq *) reg [63:0] cfg_allocator;
(* anyseq *) reg [31:0] cfg_checkpoint;
(* anyseq *) reg [31:0] cfg_nodes;
(* anyseq *) reg [31:0] cfg_nets;
(* anyseq *) reg [31:0] cfg_capacity;
(* anyseq *) reg  rearm_valid;
wire  rearm_ready;
wire  cfg_rsp_valid;
(* anyseq *) reg  cfg_rsp_ready;
wire [2:0] cfg_status;
wire  cfg_rearmed;
wire  configured;
wire [63:0] bound_design;
wire [63:0] bound_generation;
wire [31:0] bound_checkpoint;
(* anyseq *) reg  req_valid;
wire  req_ready;
(* anyseq *) reg [63:0] req_design;
(* anyseq *) reg [63:0] req_generation;
(* anyseq *) reg [31:0] req_checkpoint;
(* anyseq *) reg [31:0] req_node;
(* anyseq *) reg [31:0] req_net;
(* anyseq *) reg [31:0] req_cookie;
wire  rsp_valid;
(* anyseq *) reg  rsp_ready;
wire [3:0] rsp_status;
wire [63:0] rsp_design;
wire [63:0] rsp_generation;
wire [31:0] rsp_checkpoint;
wire [31:0] rsp_cookie;
wire [31:0] rsp_refs;
wire [31:0] rsp_occupancy;
wire  busy;
wire  fault;
wire  drained;
wire [63:0] m_araddr;
wire [7:0] m_arlen;
wire [2:0] m_arsize;
wire [1:0] m_arburst;
wire [3:0] m_arid;
wire  m_arvalid;
(* anyseq *) reg  m_arready;
(* anyseq *) reg [511:0] m_rdata;
(* anyseq *) reg [3:0] m_rid;
(* anyseq *) reg [1:0] m_rresp;
(* anyseq *) reg  m_rlast;
(* anyseq *) reg  m_rvalid;
wire  m_rready;
wire [63:0] m_awaddr;
wire [7:0] m_awlen;
wire [2:0] m_awsize;
wire [1:0] m_awburst;
wire [3:0] m_awid;
wire  m_awvalid;
(* anyseq *) reg  m_awready;
wire [511:0] m_wdata;
wire [63:0] m_wstrb;
wire  m_wlast;
wire  m_wvalid;
(* anyseq *) reg  m_wready;
(* anyseq *) reg [3:0] m_bid;
(* anyseq *) reg [1:0] m_bresp;
(* anyseq *) reg  m_bvalid;
wire  m_bready;
wire [0:0] f_bank0_configured;
wire [0:0] f_bank1_configured;
wire [0:0] f_bank0_bound_valid;
wire [0:0] f_bank1_bound_valid;
wire [2:0] f_rotator_state;
wire [0:0] f_target;
wire [0:0] f_active_bank;
checkpoint_authority_rotator dut(
.cfg_stage(cfg_stage),
.publish_valid(publish_valid),
.publish_permit(publish_permit),
.discard_valid(discard_valid),
.publish_ready(publish_ready),
.discard_ready(discard_ready),
.active_slot(active_slot),
.staged_valid(staged_valid),
.staged_design(staged_design),
.staged_generation(staged_generation),
.staged_checkpoint(staged_checkpoint),
.clk(clk),
.rst(rst),
.abort(abort),
.cfg_permit(cfg_permit),
.cfg_valid(cfg_valid),
.cfg_ready(cfg_ready),
.cfg_design(cfg_design),
.cfg_generation(cfg_generation),
.cfg_primary(cfg_primary),
.cfg_pool(cfg_pool),
.cfg_allocator(cfg_allocator),
.cfg_checkpoint(cfg_checkpoint),
.cfg_nodes(cfg_nodes),
.cfg_nets(cfg_nets),
.cfg_capacity(cfg_capacity),
.rearm_valid(rearm_valid),
.rearm_ready(rearm_ready),
.cfg_rsp_valid(cfg_rsp_valid),
.cfg_rsp_ready(cfg_rsp_ready),
.cfg_status(cfg_status),
.cfg_rearmed(cfg_rearmed),
.configured(configured),
.bound_design(bound_design),
.bound_generation(bound_generation),
.bound_checkpoint(bound_checkpoint),
.req_valid(req_valid),
.req_ready(req_ready),
.req_design(req_design),
.req_generation(req_generation),
.req_checkpoint(req_checkpoint),
.req_node(req_node),
.req_net(req_net),
.req_cookie(req_cookie),
.rsp_valid(rsp_valid),
.rsp_ready(rsp_ready),
.rsp_status(rsp_status),
.rsp_design(rsp_design),
.rsp_generation(rsp_generation),
.rsp_checkpoint(rsp_checkpoint),
.rsp_cookie(rsp_cookie),
.rsp_refs(rsp_refs),
.rsp_occupancy(rsp_occupancy),
.busy(busy),
.fault(fault),
.drained(drained),
.m_araddr(m_araddr),
.m_arlen(m_arlen),
.m_arsize(m_arsize),
.m_arburst(m_arburst),
.m_arid(m_arid),
.m_arvalid(m_arvalid),
.m_arready(m_arready),
.m_rdata(m_rdata),
.m_rid(m_rid),
.m_rresp(m_rresp),
.m_rlast(m_rlast),
.m_rvalid(m_rvalid),
.m_rready(m_rready),
.m_awaddr(m_awaddr),
.m_awlen(m_awlen),
.m_awsize(m_awsize),
.m_awburst(m_awburst),
.m_awid(m_awid),
.m_awvalid(m_awvalid),
.m_awready(m_awready),
.m_wdata(m_wdata),
.m_wstrb(m_wstrb),
.m_wlast(m_wlast),
.m_wvalid(m_wvalid),
.m_wready(m_wready),
.m_bid(m_bid),
.m_bresp(m_bresp),
.m_bvalid(m_bvalid),
.m_bready(m_bready),
.f_bank0_configured(f_bank0_configured),
.f_bank1_configured(f_bank1_configured),
.f_bank0_bound_valid(f_bank0_bound_valid),
.f_bank1_bound_valid(f_bank1_bound_valid),
.f_rotator_state(f_rotator_state),
.f_target(f_target),
.f_active_bank(f_active_bank));
reg past_valid=0;
initial assume(rst);
always @(posedge clk) begin
 past_valid<=1;
 if(past_valid && !rst) begin
  assert(!f_bank0_configured || f_bank0_bound_valid);
  assert(!f_bank1_configured || f_bank1_bound_valid);
  if($past(!rst && publish_valid && publish_ready)) assert(configured);
  if($past(!rst && configured) && !configured)
   assert($past((rearm_valid && rearm_ready) || (f_rotator_state==3'd1 && f_target==f_active_bank)));
 end
 cover(past_valid && !rst && $past(!rst && publish_valid && publish_ready) && configured);
 cover(past_valid && !rst && $past(!rst && configured && rearm_valid && rearm_ready) && !configured);
end
endmodule
