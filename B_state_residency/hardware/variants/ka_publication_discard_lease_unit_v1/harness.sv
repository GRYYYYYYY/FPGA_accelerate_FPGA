module ka_publication_discard_lease_unit(input wire clk);
reg past_valid=0;
wire pc_owned,jp_owned;
(* anyseq *) reg rst,other_command_busy;
(* anyseq *) reg lease_acquire_valid;
(* anyseq *) reg lease_release_valid;
(* anyseq *) reg lease_healthy;
(* anyseq *) reg lease_retired;
(* anyseq *) reg lease_no_offers;
(* anyseq *) reg lease_route_retired;
(* anyseq *) reg lease_command_valid;
(* anyseq *) reg lease_test_reset;
wire lease_acquire_ready;
wire lease_release_ready;
wire lease_safe;
(* anyseq *) reg pub_retired;
(* anyseq *) reg pub_stage_busy;
(* anyseq *) reg pub_fault;
(* anyseq *) reg pub_manifest_ready;
(* anyseq *) reg pub_start_valid;
wire pub_start_ready;
(* anyseq *) reg [63:0] pub_start_design;
(* anyseq *) reg [63:0] pub_start_generation;
(* anyseq *) reg [31:0] pub_start_checkpoint;
(* anyseq *) reg [31:0] pub_start_version;
(* anyseq *) reg [1:0] pub_start_query;
(* anyseq *) reg [3:0] pub_start_price;
(* anyseq *) reg pub_commit_valid;
(* anyseq *) reg pub_cancel_valid;
wire pub_commit_ready;
wire pub_cancel_ready;
wire pub_prepare_allowed;
wire pub_done_valid;
(* anyseq *) reg pub_done_ready;
wire [1:0] pub_done_status;
(* anyseq *) reg [2:0] pub_prepared;
(* anyseq *) reg [2:0] pub_publish_ready;
(* anyseq *) reg [2:0] pub_discard_ready;
wire [2:0] pub_publish_valid;
wire [2:0] pub_discard_valid;
(* anyseq *) reg [63:0] pub_a_design;
(* anyseq *) reg [63:0] pub_a_generation;
(* anyseq *) reg [63:0] pub_k_design;
(* anyseq *) reg [63:0] pub_c_design;
(* anyseq *) reg [63:0] pub_sa_design;
(* anyseq *) reg [63:0] pub_sa_generation;
(* anyseq *) reg [63:0] pub_sk_design;
(* anyseq *) reg [63:0] pub_sc_design;
(* anyseq *) reg [31:0] pub_a_checkpoint;
(* anyseq *) reg [31:0] pub_k_checkpoint;
(* anyseq *) reg [31:0] pub_c_checkpoint;
(* anyseq *) reg [31:0] pub_k_version;
(* anyseq *) reg [31:0] pub_c_version;
(* anyseq *) reg [31:0] pub_journal_count;
(* anyseq *) reg [31:0] pub_sa_checkpoint;
(* anyseq *) reg [31:0] pub_sk_checkpoint;
(* anyseq *) reg [31:0] pub_sc_checkpoint;
(* anyseq *) reg [31:0] pub_sk_version;
(* anyseq *) reg [31:0] pub_sc_version;
(* anyseq *) reg [1:0] pub_k_query;
(* anyseq *) reg [1:0] pub_sk_query;
(* anyseq *) reg [3:0] pub_k_price;
(* anyseq *) reg [3:0] pub_sk_price;
checkpoint_lease_guard lease(.clk(clk),
.rst(rst),
.acquire_valid(lease_acquire_valid),
.release_valid(lease_release_valid),
.healthy(lease_healthy),
.retired(lease_retired),
.no_offers(lease_no_offers),
.route_retired(lease_route_retired),
.command_busy((other_command_busy||jp_owned)),
.command_valid(lease_command_valid),
.test_reset(lease_test_reset),
.acquire_ready(lease_acquire_ready),
.release_ready(lease_release_ready),
.safe(lease_safe),
.owned(pc_owned));
checkpoint_publish_barrier publication(.clk(clk),
.rst(rst),
.lease_owned(pc_owned),
.retired(pub_retired),
.stage_busy(pub_stage_busy),
.fault(pub_fault),
.manifest_ready(pub_manifest_ready),
.start_valid(pub_start_valid),
.start_ready(pub_start_ready),
.start_design(pub_start_design),
.start_generation(pub_start_generation),
.start_checkpoint(pub_start_checkpoint),
.start_version(pub_start_version),
.start_query(pub_start_query),
.start_price(pub_start_price),
.commit_valid(pub_commit_valid),
.cancel_valid(pub_cancel_valid),
.commit_ready(pub_commit_ready),
.cancel_ready(pub_cancel_ready),
.owned(jp_owned),
.prepare_allowed(pub_prepare_allowed),
.done_valid(pub_done_valid),
.done_ready(pub_done_ready),
.done_status(pub_done_status),
.prepared(pub_prepared),
.publish_ready(pub_publish_ready),
.discard_ready(pub_discard_ready),
.publish_valid(pub_publish_valid),
.discard_valid(pub_discard_valid),
.a_design(pub_a_design),
.a_generation(pub_a_generation),
.k_design(pub_k_design),
.c_design(pub_c_design),
.sa_design(pub_sa_design),
.sa_generation(pub_sa_generation),
.sk_design(pub_sk_design),
.sc_design(pub_sc_design),
.a_checkpoint(pub_a_checkpoint),
.k_checkpoint(pub_k_checkpoint),
.c_checkpoint(pub_c_checkpoint),
.k_version(pub_k_version),
.c_version(pub_c_version),
.journal_count(pub_journal_count),
.sa_checkpoint(pub_sa_checkpoint),
.sk_checkpoint(pub_sk_checkpoint),
.sc_checkpoint(pub_sc_checkpoint),
.sk_version(pub_sk_version),
.sc_version(pub_sc_version),
.k_query(pub_k_query),
.sk_query(pub_sk_query),
.k_price(pub_k_price),
.sk_price(pub_sk_price));
initial assume(rst);
always @(posedge clk)begin
 past_valid<=1;
 if(past_valid && !rst && pub_discard_valid!=0)begin
  assert(pc_owned);
  assert(jp_owned);
 end
 cover(past_valid && !rst && pub_discard_valid!=0 && pc_owned);
 cover(past_valid && !rst && jp_owned && !pc_owned);
end
endmodule
