module ka_producer_hold_formal(input wire clk);
(* anyseq *) reg  cfg_stage;
(* anyseq *) reg  publish_valid;
(* anyseq *) reg  publish_permit;
(* anyseq *) reg  discard_valid;
wire  publish_ready;
wire  discard_ready;
wire  staged_valid;
wire [63:0] staged_design;
wire [31:0] staged_checkpoint;
wire [31:0] staged_version;
wire [31:0] active_version;
wire [1:0] staged_query;
wire [1:0] active_query;
wire [3:0] staged_price;
wire [3:0] active_price;
(* anyseq *) reg  cold_rst;
(* anyseq *) reg  abort;
(* anyseq *) reg  backend_drained;
(* anyseq *) reg  normal_retired;
(* anyseq *) reg  retry_safe;
wire  attempt_reset;
(* anyseq *) reg  cfg_valid;
wire  cfg_ready;
(* anyseq *) reg  cfg_authoritative;
(* anyseq *) reg [63:0] cfg_design;
(* anyseq *) reg [31:0] cfg_checkpoint;
(* anyseq *) reg [31:0] cfg_version;
(* anyseq *) reg [1:0] cfg_query;
(* anyseq *) reg [3:0] cfg_price;
wire  cfg_rsp_valid;
(* anyseq *) reg  cfg_rsp_ready;
wire  cfg_status;
(* anyseq *) reg  j_valid;
wire  j_ready;
(* anyseq *) reg [31:0] j_node;
(* anyseq *) reg [31:0] j_net;
(* anyseq *) reg [2:0] j_op;
wire [31:0] journal_count;
wire  journal_full;
wire  permit_work;
(* anyseq *) reg  recover_valid;
wire  recover_ready;
(* anyseq *) reg [31:0] recover_cookie;
(* anyseq *) reg [31:0] recover_checkpoint;
(* anyseq *) reg [31:0] recover_version;
(* anyseq *) reg [63:0] recover_design;
(* anyseq *) reg [1:0] recover_query;
(* anyseq *) reg [3:0] recover_price;
wire  target_reset;
wire  reconfigure_valid;
wire  labels_valid;
(* anyseq *) reg  reconfigure_done;
(* anyseq *) reg  labels_done;
wire [63:0] saved_design;
wire [31:0] saved_checkpoint;
wire [31:0] new_version;
wire [1:0] new_query;
wire [3:0] new_price;
wire  rsp_valid;
(* anyseq *) reg  rsp_ready;
wire [3:0] rsp_status;
wire [31:0] rsp_cookie;
wire [31:0] rsp_corrected;
wire  busy;
wire  fault;
wire  a_valid;
(* anyseq *) reg  a_ready;
wire [31:0] a_node;
wire [31:0] a_net;
wire [31:0] a_cookie;
wire [31:0] a_checkpoint;
wire [63:0] a_design;
(* anyseq *) reg  a_rsp_valid;
wire  a_rsp_ready;
(* anyseq *) reg [3:0] a_status;
(* anyseq *) reg [31:0] a_rsp_cookie;
(* anyseq *) reg [31:0] a_rsp_checkpoint;
(* anyseq *) reg [31:0] a_refs;
(* anyseq *) reg [31:0] a_occupancy;
(* anyseq *) reg [63:0] a_rsp_design;
wire  o_valid;
(* anyseq *) reg  o_ready;
wire [2:0] o_op;
wire [31:0] o_node;
wire [31:0] o_net;
wire [31:0] o_cookie;
(* anyseq *) reg  o_rsp_valid;
wire  o_rsp_ready;
(* anyseq *) reg [3:0] o_status;
(* anyseq *) reg [31:0] o_rsp_cookie;
(* anyseq *) reg [31:0] o_count;
(* anyseq *) reg [31:0] o_occupancy;
recovery_coordinator #(.ENTRIES(32),.RESET_HOLD(5),.EXCLUSIVE_BACKEND_RESPONSES(1)) dut(
.cfg_stage(cfg_stage),
.publish_valid(publish_valid),
.publish_permit(publish_permit),
.discard_valid(discard_valid),
.publish_ready(publish_ready),
.discard_ready(discard_ready),
.staged_valid(staged_valid),
.staged_design(staged_design),
.staged_checkpoint(staged_checkpoint),
.staged_version(staged_version),
.active_version(active_version),
.staged_query(staged_query),
.active_query(active_query),
.staged_price(staged_price),
.active_price(active_price),
.clk(clk),
.cold_rst(cold_rst),
.abort(abort),
.backend_drained(backend_drained),
.normal_retired(normal_retired),
.retry_safe(retry_safe),
.attempt_reset(attempt_reset),
.cfg_valid(cfg_valid),
.cfg_ready(cfg_ready),
.cfg_authoritative(cfg_authoritative),
.cfg_design(cfg_design),
.cfg_checkpoint(cfg_checkpoint),
.cfg_version(cfg_version),
.cfg_query(cfg_query),
.cfg_price(cfg_price),
.cfg_rsp_valid(cfg_rsp_valid),
.cfg_rsp_ready(cfg_rsp_ready),
.cfg_status(cfg_status),
.j_valid(j_valid),
.j_ready(j_ready),
.j_node(j_node),
.j_net(j_net),
.j_op(j_op),
.journal_count(journal_count),
.journal_full(journal_full),
.permit_work(permit_work),
.recover_valid(recover_valid),
.recover_ready(recover_ready),
.recover_cookie(recover_cookie),
.recover_checkpoint(recover_checkpoint),
.recover_version(recover_version),
.recover_design(recover_design),
.recover_query(recover_query),
.recover_price(recover_price),
.target_reset(target_reset),
.reconfigure_valid(reconfigure_valid),
.labels_valid(labels_valid),
.reconfigure_done(reconfigure_done),
.labels_done(labels_done),
.saved_design(saved_design),
.saved_checkpoint(saved_checkpoint),
.new_version(new_version),
.new_query(new_query),
.new_price(new_price),
.rsp_valid(rsp_valid),
.rsp_ready(rsp_ready),
.rsp_status(rsp_status),
.rsp_cookie(rsp_cookie),
.rsp_corrected(rsp_corrected),
.busy(busy),
.fault(fault),
.a_valid(a_valid),
.a_ready(a_ready),
.a_node(a_node),
.a_net(a_net),
.a_cookie(a_cookie),
.a_checkpoint(a_checkpoint),
.a_design(a_design),
.a_rsp_valid(a_rsp_valid),
.a_rsp_ready(a_rsp_ready),
.a_status(a_status),
.a_rsp_cookie(a_rsp_cookie),
.a_rsp_checkpoint(a_rsp_checkpoint),
.a_refs(a_refs),
.a_occupancy(a_occupancy),
.a_rsp_design(a_rsp_design),
.o_valid(o_valid),
.o_ready(o_ready),
.o_op(o_op),
.o_node(o_node),
.o_net(o_net),
.o_cookie(o_cookie),
.o_rsp_valid(o_rsp_valid),
.o_rsp_ready(o_rsp_ready),
.o_status(o_status),
.o_rsp_cookie(o_rsp_cookie),
.o_count(o_count),
.o_occupancy(o_occupancy));
reg past_valid=0;
initial assume(cold_rst);
always @(posedge clk) begin
 past_valid<=1;
 cover(past_valid && !cold_rst && a_valid && !a_ready);
 if(past_valid && !cold_rst && $past(!cold_rst && a_valid && !a_ready)) begin
  assert(a_valid);
  assert({a_design,a_checkpoint,a_node,a_net,a_cookie} == $past({a_design,a_checkpoint,a_node,a_net,a_cookie}));
 end
end
endmodule
