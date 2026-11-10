module ka_dual_bank_memory_pending_formal(input wire clk);
(* anyseq *) reg cfg_stage;
(* anyseq *) reg publish_valid;
(* anyseq *) reg publish_permit;
(* anyseq *) reg discard_valid;
(* anyseq *) reg rst;
(* anyseq *) reg abort;
(* anyseq *) reg cfg_permit;
(* anyseq *) reg cfg_valid;
(* anyseq *) reg [63:0] cfg_design;
(* anyseq *) reg [63:0] cfg_generation;
(* anyseq *) reg [63:0] cfg_primary;
(* anyseq *) reg [63:0] cfg_pool;
(* anyseq *) reg [63:0] cfg_allocator;
(* anyseq *) reg [31:0] cfg_checkpoint;
(* anyseq *) reg [31:0] cfg_nodes;
(* anyseq *) reg [31:0] cfg_nets;
(* anyseq *) reg [31:0] cfg_capacity;
(* anyseq *) reg rearm_valid;
(* anyseq *) reg cfg_rsp_ready;
(* anyseq *) reg req_valid;
(* anyseq *) reg [63:0] req_design;
(* anyseq *) reg [63:0] req_generation;
(* anyseq *) reg [31:0] req_checkpoint;
(* anyseq *) reg [31:0] req_node;
(* anyseq *) reg [31:0] req_net;
(* anyseq *) reg [31:0] req_cookie;
(* anyseq *) reg rsp_ready;
wire drained;
wire [7:0] m_arlen;
wire m_arvalid;
wire m_arready;
(* anyseq *) reg [511:0] m_rdata;
(* anyseq *) reg [3:0] m_rid;
(* anyseq *) reg [1:0] m_rresp;
wire m_rlast;
wire m_rvalid;
wire m_rready;
wire m_awvalid;
wire m_awready;
wire m_wvalid;
wire m_wready;
(* anyseq *) reg [3:0] m_bid;
(* anyseq *) reg [1:0] m_bresp;
wire m_bvalid;
wire [2:0] f_state;
wire f_target;
wire f_active_bank;
wire f_axi_bank;
wire f_all_quiet;
wire f_bank0_pending;
wire f_bank1_pending;
wire f_bank0_rst;
wire f_bank1_rst;
wire [2:0] f_reader0_state;
wire [2:0] f_reader1_state;
wire [3:0] f_store0_state;
wire [3:0] f_store1_state;
(* anyseq *) reg hold_r;
wire memory_rp;
checkpoint_authority_rotator dut(
.cfg_stage(cfg_stage),
.publish_valid(publish_valid),
.publish_permit(publish_permit),
.discard_valid(discard_valid),
.clk(clk),
.rst(rst),
.abort(abort),
.cfg_permit(cfg_permit),
.cfg_valid(cfg_valid),
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
.cfg_rsp_ready(cfg_rsp_ready),
.req_valid(req_valid),
.req_design(req_design),
.req_generation(req_generation),
.req_checkpoint(req_checkpoint),
.req_node(req_node),
.req_net(req_net),
.req_cookie(req_cookie),
.rsp_ready(rsp_ready),
.drained(drained),
.m_arlen(m_arlen),
.m_arvalid(m_arvalid),
.m_arready(m_arready),
.m_rdata(m_rdata),
.m_rid(m_rid),
.m_rresp(m_rresp),
.m_rlast(m_rlast),
.m_rvalid(m_rvalid),
.m_rready(m_rready),
.m_awvalid(m_awvalid),
.m_awready(m_awready),
.m_wvalid(m_wvalid),
.m_wready(m_wready),
.m_bid(m_bid),
.m_bresp(m_bresp),
.m_bvalid(m_bvalid),
.f_state(f_state),
.f_target(f_target),
.f_active_bank(f_active_bank),
.f_axi_bank(f_axi_bank),
.f_all_quiet(f_all_quiet),
.f_bank0_pending(f_bank0_pending),
.f_bank1_pending(f_bank1_pending),
.f_bank0_rst(f_bank0_rst),
.f_bank1_rst(f_bank1_rst),
.f_reader0_state(f_reader0_state),
.f_reader1_state(f_reader1_state),
.f_store0_state(f_store0_state),
.f_store1_state(f_store1_state));
axi_file_memory_control #(.ADDR_BITS(64),.READ_ONLY(1),.MAX_BEATS(1),.READ_DELAY(0)) memory(.clk(clk),.rst(rst),.arvalid(m_arvalid),.arready(m_arready),.arlen(m_arlen),.arsize(3'd6),.arburst(2'd1),.arid(4'd0),.araddr(64'd0),.rvalid(m_rvalid),.rlast(m_rlast),.rready(m_rready),.hold_r(hold_r),.inject_r(1'b0),.inject_b(1'b0),.awvalid(m_awvalid),.awready(m_awready),.wvalid(m_wvalid),.wready(m_wready),.bvalid(m_bvalid),.bready(1'b0),.obs_rp(memory_rp));
reg past_valid=0;
initial assume(rst);
always @(posedge clk) begin
 past_valid<=1;
 if(past_valid && !rst) begin
  assert(f_state<=4);
  if(f_state!=0) begin
   assert(f_store0_state==0 && f_store1_state==0);
   assert(f_reader0_state<5 && f_reader1_state<5);
   assert(!f_bank0_pending && !f_bank1_pending);
  end
  if($past(!rst) && f_axi_bank!=$past(f_axi_bank)) begin
   assert($past(!f_bank0_pending && !f_bank1_pending));
   assert(!f_bank0_pending && !f_bank1_pending);
  end
  assert(!(f_bank0_pending && f_bank1_pending));
  assert(memory_rp==(f_bank0_pending || f_bank1_pending));
  if(f_bank0_pending) assert(!f_axi_bank);
  if(f_bank1_pending) assert(f_axi_bank);
  if(m_rvalid) assert(memory_rp && m_rlast);
  if(f_bank0_rst || f_bank1_rst) assert(!memory_rp);
  assert(!m_bvalid && !m_awready && !m_wready);
  assert(m_arlen==0);
 end
 cover(past_valid && !rst && f_bank0_pending && memory_rp);
 cover(past_valid && !rst && f_bank1_pending && memory_rp);
 cover(past_valid && !rst && $past(!rst && f_state==4) && f_state==0 && f_axi_bank!=$past(f_axi_bank));
end
endmodule
