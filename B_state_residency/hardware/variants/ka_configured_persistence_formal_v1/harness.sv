module ka_configured_persistence_formal(input wire clk);
(* anyseq *) reg [0:0] cfg_stage;
(* anyseq *) reg [0:0] publish_valid;
(* anyseq *) reg [0:0] publish_permit;
(* anyseq *) reg [0:0] discard_valid;
(* anyseq *) reg [0:0] rst;
(* anyseq *) reg [0:0] abort;
(* anyseq *) reg [0:0] cfg_permit;
(* anyseq *) reg [0:0] cfg_valid;
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
(* anyseq *) reg [0:0] cfg_rsp_ready;
wire [63:0] bound_generation;
(* anyseq *) reg [0:0] req_valid;
(* anyseq *) reg [63:0] req_design;
(* anyseq *) reg [63:0] req_generation;
(* anyseq *) reg [31:0] req_checkpoint;
(* anyseq *) reg [31:0] req_node;
(* anyseq *) reg [31:0] req_net;
(* anyseq *) reg [31:0] req_cookie;
(* anyseq *) reg [0:0] rsp_ready;
(* anyseq *) reg [0:0] m_arready;
(* anyseq *) reg [511:0] m_rdata;
(* anyseq *) reg [3:0] m_rid;
(* anyseq *) reg [1:0] m_rresp;
(* anyseq *) reg [0:0] m_rlast;
(* anyseq *) reg [0:0] m_rvalid;
(* anyseq *) reg [0:0] m_awready;
(* anyseq *) reg [0:0] m_wready;
(* anyseq *) reg [3:0] m_bid;
(* anyseq *) reg [1:0] m_bresp;
(* anyseq *) reg [0:0] m_bvalid;
wire [2:0] f_bank0_state;
wire [0:0] f_bank0_bound_valid;
wire [0:0] f_bank0_configured;
wire [63:0] f_bank0_saved_generation;
wire [63:0] f_bank0_bound_generation;
wire [2:0] f_bank1_state;
wire [0:0] f_bank1_bound_valid;
wire [0:0] f_bank1_configured;
wire [63:0] f_bank1_saved_generation;
wire [63:0] f_bank1_bound_generation;
wire [2:0] f_rotator_state;
wire [0:0] f_target;
wire [0:0] f_active_bank;
wire configured;
wire rearm_ready;
checkpoint_authority_rotator dut(
.configured(configured),
.rearm_ready(rearm_ready),
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
.bound_generation(bound_generation),
.req_valid(req_valid),
.req_design(req_design),
.req_generation(req_generation),
.req_checkpoint(req_checkpoint),
.req_node(req_node),
.req_net(req_net),
.req_cookie(req_cookie),
.rsp_ready(rsp_ready),
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
.f_bank0_state(f_bank0_state),
.f_bank0_bound_valid(f_bank0_bound_valid),
.f_bank0_configured(f_bank0_configured),
.f_bank0_saved_generation(f_bank0_saved_generation),
.f_bank0_bound_generation(f_bank0_bound_generation),
.f_bank1_state(f_bank1_state),
.f_bank1_bound_valid(f_bank1_bound_valid),
.f_bank1_configured(f_bank1_configured),
.f_bank1_saved_generation(f_bank1_saved_generation),
.f_bank1_bound_generation(f_bank1_bound_generation),
.f_rotator_state(f_rotator_state),
.f_target(f_target),
.f_active_bank(f_active_bank));
reg past_valid=0;
initial assume(rst);
always @(posedge clk) begin
 past_valid<=1;
 if(past_valid && !rst) begin
  if(f_bank0_bound_valid) assert(f_bank0_saved_generation!=0);
  if(f_bank0_state==3'd1 || f_bank0_state==3'd2 || f_bank0_state==3'd3) assert(f_bank0_saved_generation!=0);
  if(f_bank0_configured) assert(f_bank0_bound_generation!=0);
  if(f_bank1_bound_valid) assert(f_bank1_saved_generation!=0);
  if(f_bank1_state==3'd1 || f_bank1_state==3'd2 || f_bank1_state==3'd3) assert(f_bank1_saved_generation!=0);
  if(f_bank1_configured) assert(f_bank1_bound_generation!=0);
  if(f_rotator_state==3'd1 && f_target==f_active_bank) assert(bound_generation==0);
  if($past(!rst && bound_generation!=0)) assert(bound_generation!=0);
  if(f_bank0_bound_generation!=0) assert(f_bank0_bound_valid);
  if(f_bank1_bound_generation!=0) assert(f_bank1_bound_valid);
  if($past(!rst && configured && bound_generation!=0 && !(rearm_valid && rearm_ready))) assert(configured);
 end
 cover(past_valid && !rst && configured && rearm_valid && rearm_ready && bound_generation!=0);
 cover(past_valid && !rst && $past(!rst && bound_generation!=0) && bound_generation!=0 && f_active_bank!=$past(f_active_bank));
end
endmodule
