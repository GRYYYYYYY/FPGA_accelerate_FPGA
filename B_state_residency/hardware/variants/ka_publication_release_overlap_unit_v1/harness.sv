module ka_publication_release_overlap_unit(input wire clk);
(* anyseq *) reg rst, acquire_valid,release_valid,start_valid;
wire pc_owned,jp_owned,acquire_ready,release_ready,start_ready,prepare_allowed;
checkpoint_lease_guard lease(.clk(clk),.rst(rst),.acquire_valid(acquire_valid),.acquire_ready(acquire_ready),.release_valid(release_valid),.release_ready(release_ready),.owned(pc_owned),.healthy(1'b1),.retired(1'b1),.route_retired(1'b1),.no_offers(1'b1),.command_busy(jp_owned),.command_valid(1'b0),.test_reset(1'b0));
checkpoint_publish_barrier publication(.clk(clk),.rst(rst),.lease_owned(pc_owned),.retired(1'b1),.stage_busy(1'b0),.fault(1'b0),.manifest_ready(1'b1),.start_valid(start_valid),.start_ready(start_ready),.start_design(64'd1),.start_generation(64'd2),.start_checkpoint(32'd2),.start_version(32'd1),.start_query(2'd0),.start_price(4'd1),.commit_valid(1'b0),.cancel_valid(1'b0),.owned(jp_owned),.prepare_allowed(prepare_allowed),.done_ready(1'b0),.prepared(3'd0),.publish_ready(3'd0),.discard_ready(3'd0),.a_design(64'd1),.a_generation(64'd1),.k_design(64'd1),.c_design(64'd1),.a_checkpoint(32'd1),.k_checkpoint(32'd1),.c_checkpoint(32'd1),.k_version(32'd1),.c_version(32'd1),.journal_count(32'd0),.k_query(2'd0),.k_price(4'd1),.sa_design(64'd1),.sa_generation(64'd2),.sa_checkpoint(32'd2),.sk_design(64'd1),.sc_design(64'd1),.sk_checkpoint(32'd2),.sc_checkpoint(32'd2),.sk_version(32'd1),.sc_version(32'd1),.sk_query(2'd0),.sk_price(4'd1));
reg past_valid=0;
initial assume(rst);
always @(posedge clk)begin
 past_valid<=1;
 if(past_valid && !rst) assert(!jp_owned || pc_owned);
 cover(past_valid && !rst && start_valid && start_ready && release_valid && release_ready);
end
endmodule
