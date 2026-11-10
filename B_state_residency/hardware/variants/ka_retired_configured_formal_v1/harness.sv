module ka_retired_configured_formal(input wire clk);
(* anyseq *) reg [0:0] cfg_stage;
(* anyseq *) reg [0:0] publish_valid;
(* anyseq *) reg [0:0] publish_permit;
(* anyseq *) reg [0:0] discard_valid;
wire [0:0] publish_ready;
wire [0:0] discard_ready;
wire [0:0] active_slot;
wire [0:0] staged_valid;
wire [63:0] staged_design;
wire [63:0] staged_generation;
wire [31:0] staged_checkpoint;
(* anyseq *) reg [0:0] rst;
(* anyseq *) reg [0:0] abort;
(* anyseq *) reg [0:0] cfg_permit;
(* anyseq *) reg [0:0] cfg_valid;
wire [0:0] cfg_ready;
(* anyseq *) reg [63:0] cfg_design;
(* anyseq *) reg [63:0] cfg_generation;
(* anyseq *) reg [63:0] cfg_primary;
(* anyseq *) reg [63:0] cfg_pool;
(* anyseq *) reg [63:0] cfg_allocator;
(* anyseq *) reg [31:0] cfg_checkpoint;
(* anyseq *) reg [31:0] cfg_nodes;
(* anyseq *) reg [31:0] cfg_nets;
(* anyseq *) reg [31:0] cfg_capacity;
(* anyseq *) reg [0:0] rearm_valid;
wire [0:0] rearm_ready;
wire [0:0] cfg_rsp_valid;
(* anyseq *) reg [0:0] cfg_rsp_ready;
wire [2:0] cfg_status;
wire [0:0] cfg_rearmed;
wire [0:0] configured;
wire [63:0] bound_design;
wire [63:0] bound_generation;
wire [31:0] bound_checkpoint;
(* anyseq *) reg [0:0] req_valid;
wire [0:0] req_ready;
(* anyseq *) reg [63:0] req_design;
(* anyseq *) reg [63:0] req_generation;
(* anyseq *) reg [31:0] req_checkpoint;
(* anyseq *) reg [31:0] req_node;
(* anyseq *) reg [31:0] req_net;
(* anyseq *) reg [31:0] req_cookie;
wire [0:0] rsp_valid;
(* anyseq *) reg [0:0] rsp_ready;
wire [3:0] rsp_status;
wire [63:0] rsp_design;
wire [63:0] rsp_generation;
wire [31:0] rsp_checkpoint;
wire [31:0] rsp_cookie;
wire [31:0] rsp_refs;
wire [31:0] rsp_occupancy;
wire [0:0] busy;
wire [0:0] fault;
wire [0:0] drained;
wire [63:0] m_araddr;
wire [7:0] m_arlen;
wire [2:0] m_arsize;
wire [1:0] m_arburst;
wire [3:0] m_arid;
wire [0:0] m_arvalid;
(* anyseq *) reg [0:0] m_arready;
(* anyseq *) reg [511:0] m_rdata;
(* anyseq *) reg [3:0] m_rid;
(* anyseq *) reg [1:0] m_rresp;
(* anyseq *) reg [0:0] m_rlast;
(* anyseq *) reg [0:0] m_rvalid;
wire [0:0] m_rready;
wire [63:0] m_awaddr;
wire [7:0] m_awlen;
wire [2:0] m_awsize;
wire [1:0] m_awburst;
wire [3:0] m_awid;
wire [0:0] m_awvalid;
(* anyseq *) reg [0:0] m_awready;
wire [511:0] m_wdata;
wire [63:0] m_wstrb;
wire [0:0] m_wlast;
wire [0:0] m_wvalid;
(* anyseq *) reg [0:0] m_wready;
(* anyseq *) reg [3:0] m_bid;
(* anyseq *) reg [1:0] m_bresp;
(* anyseq *) reg [0:0] m_bvalid;
wire [0:0] m_bready;
wire [0:0] f_bank0_configured;
wire [0:0] f_bank0_bound_valid;
wire [63:0] f_bank0_bound_generation;
wire [0:0] f_bank0_busy;
wire [0:0] f_bank0_fault;
wire [2:0] f_bank0_state;
wire [0:0] f_bank0_stopped;
wire [0:0] f_bank1_configured;
wire [0:0] f_bank1_bound_valid;
wire [63:0] f_bank1_bound_generation;
wire [0:0] f_bank1_busy;
wire [0:0] f_bank1_fault;
wire [2:0] f_bank1_state;
wire [0:0] f_bank1_stopped;
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
.f_bank0_bound_valid(f_bank0_bound_valid),
.f_bank0_bound_generation(f_bank0_bound_generation),
.f_bank0_busy(f_bank0_busy),
.f_bank0_fault(f_bank0_fault),
.f_bank0_state(f_bank0_state),
.f_bank0_stopped(f_bank0_stopped),
.f_bank1_configured(f_bank1_configured),
.f_bank1_bound_valid(f_bank1_bound_valid),
.f_bank1_bound_generation(f_bank1_bound_generation),
.f_bank1_busy(f_bank1_busy),
.f_bank1_fault(f_bank1_fault),
.f_bank1_state(f_bank1_state),
.f_bank1_stopped(f_bank1_stopped));
reg past_valid=0;
initial assume(rst);
always @(posedge clk) begin
 past_valid<=1;
 if(past_valid && !rst) begin
  if(f_bank0_bound_generation!=64'd0) assert(f_bank0_bound_valid);
  if(f_bank0_bound_valid && !f_bank0_busy && !f_bank0_fault) assert(f_bank0_configured);
  if(f_bank0_bound_valid && !f_bank0_configured && !f_bank0_stopped)
   assert(f_bank0_state==3'd1 || f_bank0_state==3'd2 || f_bank0_state==3'd3);
  if(f_bank1_bound_generation!=64'd0) assert(f_bank1_bound_valid);
  if(f_bank1_bound_valid && !f_bank1_busy && !f_bank1_fault) assert(f_bank1_configured);
  if(f_bank1_bound_valid && !f_bank1_configured && !f_bank1_stopped)
   assert(f_bank1_state==3'd1 || f_bank1_state==3'd2 || f_bank1_state==3'd3);
  if(bound_generation!=0 && !busy && !fault) assert(configured);
 end
 cover(past_valid && !rst && bound_generation!=0 && !busy && !fault && configured);
end
endmodule
