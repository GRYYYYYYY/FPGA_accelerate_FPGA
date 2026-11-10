module ka_bank_transition_quiet_formal(input wire clk);
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
(* anyseq *) reg m_arready;
(* anyseq *) reg [511:0] m_rdata;
(* anyseq *) reg [3:0] m_rid;
(* anyseq *) reg [1:0] m_rresp;
(* anyseq *) reg m_rlast;
(* anyseq *) reg m_rvalid;
(* anyseq *) reg m_awready;
(* anyseq *) reg m_wready;
(* anyseq *) reg [3:0] m_bid;
(* anyseq *) reg [1:0] m_bresp;
(* anyseq *) reg m_bvalid;
wire [2:0] f_state;
wire f_target;
wire f_active_bank;
wire f_axi_bank;
wire f_all_quiet;
wire f_bank0_pending;
wire f_bank1_pending;
wire f_bank0_rst;
wire f_bank1_rst;
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
.m_arready(m_arready),
.m_rdata(m_rdata),
.m_rid(m_rid),
.m_rresp(m_rresp),
.m_rlast(m_rlast),
.m_rvalid(m_rvalid),
.m_awready(m_awready),
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
.f_bank1_rst(f_bank1_rst));
reg past_valid=0;
initial assume(rst);
always @(posedge clk) begin
 past_valid<=1;
 if(past_valid && !rst) begin
  assert(f_state<=4);
  if(f_all_quiet) assert(!f_bank0_pending && !f_bank1_pending);
  if(f_state==1) assert($past(!rst && f_state==0 && f_all_quiet && !f_bank0_pending && !f_bank1_pending));
  if($past(!rst) && f_target!=$past(f_target)) assert($past(!rst && f_all_quiet));
  if($past(!rst) && f_active_bank!=$past(f_active_bank)) assert($past(!rst && f_all_quiet));
  if(f_bank0_rst || f_bank1_rst) assert($past(!rst && !f_bank0_pending && !f_bank1_pending));
 end
 cover(past_valid && !rst && f_state==1);
 cover(past_valid && !rst && $past(!rst) && f_active_bank!=$past(f_active_bank));
end
endmodule
