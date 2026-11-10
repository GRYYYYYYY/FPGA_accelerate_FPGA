module ka_ready_combinational_formal(input wire clk);
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
wire configured;
(* anyseq *) reg req_valid;
wire req_ready;
(* anyseq *) reg [63:0] req_design;
(* anyseq *) reg [63:0] req_generation;
(* anyseq *) reg [31:0] req_checkpoint;
(* anyseq *) reg [31:0] req_node;
(* anyseq *) reg [31:0] req_net;
(* anyseq *) reg [31:0] req_cookie;
(* anyseq *) reg rsp_ready;
wire busy;
wire fault;
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
.configured(configured),
.req_valid(req_valid),
.req_ready(req_ready),
.req_design(req_design),
.req_generation(req_generation),
.req_checkpoint(req_checkpoint),
.req_node(req_node),
.req_net(req_net),
.req_cookie(req_cookie),
.rsp_ready(rsp_ready),
.busy(busy),
.fault(fault),
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
.m_bvalid(m_bvalid));
wire quiet_base=!rst&&!abort&&configured&&!busy&&!fault&&!cfg_valid&&!publish_valid&&!discard_valid&&!rearm_valid;
always @(posedge clk) begin
 if(quiet_base && drained) assert(req_ready);
 cover(quiet_base && drained && req_ready);
 cover(quiet_base && !drained && !req_ready);
end
endmodule
