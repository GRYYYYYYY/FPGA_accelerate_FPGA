module ka_coordinator_config_generation_formal(input wire clk);
(* anyseq *) reg f_authority_generation_nonzero;
(* anyseq *) reg [0:0] cfg_stage;
(* anyseq *) reg [0:0] publish_valid;
(* anyseq *) reg [0:0] publish_permit;
(* anyseq *) reg [0:0] discard_valid;
(* anyseq *) reg [0:0] cold_rst;
(* anyseq *) reg [0:0] abort;
(* anyseq *) reg [0:0] backend_drained;
(* anyseq *) reg [0:0] normal_retired;
(* anyseq *) reg [0:0] retry_safe;
(* anyseq *) reg [0:0] cfg_valid;
wire [0:0] cfg_ready;
(* anyseq *) reg [0:0] cfg_authoritative;
(* anyseq *) reg [63:0] cfg_design;
(* anyseq *) reg [31:0] cfg_checkpoint;
(* anyseq *) reg [31:0] cfg_version;
(* anyseq *) reg [1:0] cfg_query;
(* anyseq *) reg [3:0] cfg_price;
(* anyseq *) reg [0:0] cfg_rsp_ready;
(* anyseq *) reg [0:0] j_valid;
(* anyseq *) reg [31:0] j_node;
(* anyseq *) reg [31:0] j_net;
(* anyseq *) reg [2:0] j_op;
(* anyseq *) reg [0:0] recover_valid;
(* anyseq *) reg [31:0] recover_cookie;
(* anyseq *) reg [31:0] recover_checkpoint;
(* anyseq *) reg [31:0] recover_version;
(* anyseq *) reg [63:0] recover_design;
(* anyseq *) reg [1:0] recover_query;
(* anyseq *) reg [3:0] recover_price;
(* anyseq *) reg [0:0] reconfigure_done;
(* anyseq *) reg [0:0] labels_done;
(* anyseq *) reg [0:0] rsp_ready;
wire [0:0] a_valid;
(* anyseq *) reg [0:0] a_ready;
(* anyseq *) reg [0:0] a_rsp_valid;
(* anyseq *) reg [3:0] a_status;
(* anyseq *) reg [31:0] a_rsp_cookie;
(* anyseq *) reg [31:0] a_rsp_checkpoint;
(* anyseq *) reg [31:0] a_refs;
(* anyseq *) reg [31:0] a_occupancy;
(* anyseq *) reg [63:0] a_rsp_design;
(* anyseq *) reg [0:0] o_ready;
(* anyseq *) reg [0:0] o_rsp_valid;
(* anyseq *) reg [3:0] o_status;
(* anyseq *) reg [31:0] o_rsp_cookie;
(* anyseq *) reg [31:0] o_count;
(* anyseq *) reg [31:0] o_occupancy;
wire [0:0] configured;
wire [3:0] f_state;
recovery_coordinator dut(
.cfg_stage(cfg_stage),
.publish_valid(publish_valid),
.publish_permit(publish_permit),
.discard_valid(discard_valid),
.clk(clk),
.cold_rst(cold_rst),
.abort(abort),
.backend_drained(backend_drained),
.normal_retired(normal_retired),
.retry_safe(retry_safe),
.cfg_valid(cfg_valid),
.cfg_ready(cfg_ready),
.cfg_authoritative(cfg_authoritative),
.cfg_design(cfg_design),
.cfg_checkpoint(cfg_checkpoint),
.cfg_version(cfg_version),
.cfg_query(cfg_query),
.cfg_price(cfg_price),
.cfg_rsp_ready(cfg_rsp_ready),
.j_valid(j_valid),
.j_node(j_node),
.j_net(j_net),
.j_op(j_op),
.recover_valid(recover_valid),
.recover_cookie(recover_cookie),
.recover_checkpoint(recover_checkpoint),
.recover_version(recover_version),
.recover_design(recover_design),
.recover_query(recover_query),
.recover_price(recover_price),
.reconfigure_done(reconfigure_done),
.labels_done(labels_done),
.rsp_ready(rsp_ready),
.a_valid(a_valid),
.a_ready(a_ready),
.a_rsp_valid(a_rsp_valid),
.a_status(a_status),
.a_rsp_cookie(a_rsp_cookie),
.a_rsp_checkpoint(a_rsp_checkpoint),
.a_refs(a_refs),
.a_occupancy(a_occupancy),
.a_rsp_design(a_rsp_design),
.o_ready(o_ready),
.o_rsp_valid(o_rsp_valid),
.o_status(o_status),
.o_rsp_cookie(o_rsp_cookie),
.o_count(o_count),
.o_occupancy(o_occupancy),
.configured(configured),
.f_state(f_state));
reg past_valid=0;
initial assume(cold_rst);
always @(posedge clk) begin
 past_valid<=1;
 if(past_valid && !cold_rst) begin
  if(!cfg_stage && cfg_authoritative) assume(f_authority_generation_nonzero);
  if($past(!cold_rst && f_authority_generation_nonzero)) assume(f_authority_generation_nonzero);
  assert(f_state<=4'd12);
  if(f_state!=4'd0) assert(configured);
  if(a_valid) assert(configured);
  if(configured) assert(f_authority_generation_nonzero);
  if(a_valid) assert(f_authority_generation_nonzero);
  if(configured && !$past(configured)) assert($past(!cold_rst && cfg_valid && cfg_ready && !cfg_stage && cfg_authoritative));
  if($past(!cold_rst && configured)) assert(configured);
 end
 cover(past_valid && !cold_rst && a_valid && f_authority_generation_nonzero);
end
endmodule
