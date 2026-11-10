module ka_as_no_ap_owned_formal(input wire clk);
(* anyseq *) reg baseline_retired;
(* anyseq *) reg restore_seed_enable;
(* anyseq *) reg baseline_permit;
(* anyseq *) reg [63:0] baseline_epoch;
(* anyseq *) reg baseline_req_ready;
(* anyseq *) reg baseline_rsp_valid;
(* anyseq *) reg [3:0] baseline_rsp_status;
(* anyseq *) reg [31:0] baseline_rsp_node;
(* anyseq *) reg [63:0] baseline_rsp_epoch;
(* anyseq *) reg [159:0] baseline_rsp_payload;
(* anyseq *) reg wm_enable;
(* anyseq *) reg [31:0] wm_source_version;
(* anyseq *) reg [1:0] wm_source_query;
(* anyseq *) reg [3:0] wm_source_price;
(* anyseq *) reg [31:0] wm_path_crc;
(* anyseq *) reg [31:0] wm_query_crc;
(* anyseq *) reg ap_valid;
(* anyseq *) reg ap_rsp_ready;
(* anyseq *) reg [63:0] ap_design;
(* anyseq *) reg [63:0] ap_generation;
(* anyseq *) reg [31:0] ap_checkpoint;
(* anyseq *) reg [31:0] ap_node;
(* anyseq *) reg [31:0] ap_net;
(* anyseq *) reg [31:0] ap_cookie;
(* anyseq *) reg jp_start;
(* anyseq *) reg jp_commit;
(* anyseq *) reg jp_cancel;
(* anyseq *) reg jp_done_ready;
(* anyseq *) reg jp_manifest_ready;
(* anyseq *) reg [63:0] jp_generation;
(* anyseq *) reg [63:0] jp_design;
(* anyseq *) reg [31:0] jp_checkpoint;
(* anyseq *) reg [31:0] jp_version;
(* anyseq *) reg [1:0] jp_query;
(* anyseq *) reg [3:0] jp_price;
(* anyseq *) reg [1:0] jp_load;
(* anyseq *) reg [1:0] jp_ack;
(* anyseq *) reg jp_authority_stage;
(* anyseq *) reg boot_required;
(* anyseq *) reg boot_cfg_valid;
(* anyseq *) reg [63:0] boot_design;
(* anyseq *) reg [63:0] boot_generation;
(* anyseq *) reg [31:0] boot_checkpoint;
(* anyseq *) reg [31:0] boot_version;
(* anyseq *) reg [31:0] boot_nodes;
(* anyseq *) reg [31:0] boot_label_count;
(* anyseq *) reg [31:0] boot_label_crc;
(* anyseq *) reg [31:0] boot_path_crc;
(* anyseq *) reg [31:0] boot_query_crc;
(* anyseq *) reg [1:0] boot_query;
(* anyseq *) reg [3:0] boot_slots;
(* anyseq *) reg [3:0] boot_price;
(* anyseq *) reg [2303:0] boot_payload;
(* anyseq *) reg boot_rsp_ready;
(* anyseq *) reg boot_verify_valid;
(* anyseq *) reg [63:0] qc_cp_generation;
(* anyseq *) reg qc_cp_valid;
(* anyseq *) reg qc_cp_restore;
(* anyseq *) reg qc_cp_rsp_ready;
(* anyseq *) reg qc_cp_s_valid;
(* anyseq *) reg qc_cp_s_last;
(* anyseq *) reg qc_cp_m_ready;
(* anyseq *) reg qc_cp_test_reset;
(* anyseq *) reg [31:0] qc_cp_expected_crc;
(* anyseq *) reg [31:0] qc_cp_s_index;
(* anyseq *) reg [31:0] qc_cp_s_data;
(* anyseq *) reg as_cfg_valid;
(* anyseq *) reg [63:0] as_cfg_design;
(* anyseq *) reg [63:0] as_cfg_generation;
(* anyseq *) reg [63:0] as_cfg_primary;
(* anyseq *) reg [63:0] as_cfg_pool;
(* anyseq *) reg [63:0] as_cfg_allocator;
(* anyseq *) reg [31:0] as_cfg_checkpoint;
(* anyseq *) reg [31:0] as_cfg_nodes;
(* anyseq *) reg [31:0] as_cfg_nets;
(* anyseq *) reg [31:0] as_cfg_capacity;
(* anyseq *) reg as_m_arready;
(* anyseq *) reg [511:0] as_m_rdata;
(* anyseq *) reg [3:0] as_m_rid;
(* anyseq *) reg [1:0] as_m_rresp;
(* anyseq *) reg as_m_rlast;
(* anyseq *) reg as_m_rvalid;
(* anyseq *) reg as_m_awready;
(* anyseq *) reg as_m_wready;
(* anyseq *) reg [3:0] as_m_bid;
(* anyseq *) reg [1:0] as_m_bresp;
(* anyseq *) reg as_m_bvalid;
(* anyseq *) reg as_cfg_rsp_ready;
wire as_busy;
(* anyseq *) reg cp_valid;
(* anyseq *) reg cp_restore;
(* anyseq *) reg cp_rsp_ready;
(* anyseq *) reg [63:0] cp_design;
(* anyseq *) reg [31:0] cp_nodes;
(* anyseq *) reg [31:0] cp_nets;
(* anyseq *) reg [31:0] cp_expected_crc;
(* anyseq *) reg cp_s_valid;
(* anyseq *) reg [31:0] cp_s_index;
(* anyseq *) reg [31:0] cp_s_data;
(* anyseq *) reg cp_s_last;
(* anyseq *) reg cp_m_ready;
(* anyseq *) reg cp_test_reset;
(* anyseq *) reg pc_acquire_valid;
(* anyseq *) reg pc_release_valid;
(* anyseq *) reg abort;
(* anyseq *) reg cs_m_arready;
(* anyseq *) reg cs_m_awready;
(* anyseq *) reg [3:0] cs_m_bid;
(* anyseq *) reg [1:0] cs_m_bresp;
(* anyseq *) reg cs_m_bvalid;
(* anyseq *) reg [511:0] cs_m_rdata;
(* anyseq *) reg [3:0] cs_m_rid;
(* anyseq *) reg cs_m_rlast;
(* anyseq *) reg [1:0] cs_m_rresp;
(* anyseq *) reg cs_m_rvalid;
(* anyseq *) reg cs_m_wready;
(* anyseq *) reg d_m_arready;
(* anyseq *) reg d_m_awready;
(* anyseq *) reg [3:0] d_m_bid;
(* anyseq *) reg [1:0] d_m_bresp;
(* anyseq *) reg d_m_bvalid;
(* anyseq *) reg [511:0] d_m_rdata;
(* anyseq *) reg [3:0] d_m_rid;
(* anyseq *) reg d_m_rlast;
(* anyseq *) reg [1:0] d_m_rresp;
(* anyseq *) reg d_m_rvalid;
(* anyseq *) reg d_m_wready;
(* anyseq *) reg [63:0] design_id;
(* anyseq *) reg [191:0] f_route_payload;
(* anyseq *) reg [38911:0] f_sp;
(* anyseq *) reg [15:0] f_srr;
(* anyseq *) reg [15:0] f_sv;
(* anyseq *) reg g_m_arready;
(* anyseq *) reg [511:0] g_m_rdata;
(* anyseq *) reg [3:0] g_m_rid;
(* anyseq *) reg g_m_rlast;
(* anyseq *) reg [1:0] g_m_rresp;
(* anyseq *) reg g_m_rvalid;
wire k_a_valid;
wire k_busy;
(* anyseq *) reg k_cold_rst;
(* anyseq *) reg k_rec_valid;
(* anyseq *) reg k_rsp_ready;
(* anyseq *) reg [31:0] lr_s_cookie;
(* anyseq *) reg lr_s_last;
(* anyseq *) reg [31:0] lr_s_node;
(* anyseq *) reg [159:0] lr_s_payload;
(* anyseq *) reg lr_s_valid;
(* anyseq *) reg out_ready;
(* anyseq *) reg owner_m_arready;
(* anyseq *) reg owner_m_awready;
(* anyseq *) reg [3:0] owner_m_bid;
(* anyseq *) reg [1:0] owner_m_bresp;
(* anyseq *) reg owner_m_bvalid;
(* anyseq *) reg [511:0] owner_m_rdata;
(* anyseq *) reg [3:0] owner_m_rid;
(* anyseq *) reg owner_m_rlast;
(* anyseq *) reg [1:0] owner_m_rresp;
(* anyseq *) reg owner_m_rvalid;
(* anyseq *) reg owner_m_wready;
(* anyseq *) reg p_m_arready;
(* anyseq *) reg p_m_awready;
(* anyseq *) reg [3:0] p_m_bid;
(* anyseq *) reg [1:0] p_m_bresp;
(* anyseq *) reg p_m_bvalid;
(* anyseq *) reg [511:0] p_m_rdata;
(* anyseq *) reg [3:0] p_m_rid;
(* anyseq *) reg p_m_rlast;
(* anyseq *) reg [1:0] p_m_rresp;
(* anyseq *) reg p_m_rvalid;
(* anyseq *) reg p_m_wready;
(* anyseq *) reg q_m_arready;
(* anyseq *) reg [511:0] q_m_rdata;
(* anyseq *) reg [3:0] q_m_rid;
(* anyseq *) reg q_m_rlast;
(* anyseq *) reg [1:0] q_m_rresp;
(* anyseq *) reg q_m_rvalid;
(* anyseq *) reg rc_req_valid;
(* anyseq *) reg rc_rsp_ready;
(* anyseq *) reg [31:0] recover_checkpoint;
(* anyseq *) reg [31:0] recover_cookie;
(* anyseq *) reg [63:0] recover_design;
(* anyseq *) reg [3:0] recover_price;
(* anyseq *) reg [1:0] recover_query;
(* anyseq *) reg [31:0] recover_version;
(* anyseq *) reg [31:0] snapshot_checkpoint;
(* anyseq *) reg [31:0] snapshot_cookie;
(* anyseq *) reg [31:0] snapshot_count;
(* anyseq *) reg [63:0] snapshot_design;
(* anyseq *) reg [31:0] snapshot_nodes;
(* anyseq *) reg [31:0] snapshot_probe;
(* anyseq *) reg t_m_arready;
(* anyseq *) reg [511:0] t_m_rdata;
(* anyseq *) reg [3:0] t_m_rid;
(* anyseq *) reg t_m_rlast;
(* anyseq *) reg [1:0] t_m_rresp;
(* anyseq *) reg t_m_rvalid;
(* anyseq *) reg test_route_abort;
(* anyseq *) reg test_route_version_flip;
(* anyseq *) reg qc_cmd_valid;
(* anyseq *) reg [1:0] qc_cmd_slot;
(* anyseq *) reg [31:0] qc_cmd_cookie;
(* anyseq *) reg [31:0] qc_cmd_route_cookie;
(* anyseq *) reg [31:0] qc_cmd_source;
(* anyseq *) reg [31:0] qc_cmd_key;
(* anyseq *) reg [31:0] qc_cmd_nodes;
(* anyseq *) reg [31:0] qc_cmd_max_polls;
(* anyseq *) reg [31:0] qc_cmd_poll_cookie;
(* anyseq *) reg [63:0] qc_cmd_design;
(* anyseq *) reg [1:0] qc_cmd_query;
(* anyseq *) reg [3:0] qc_cmd_price;
(* anyseq *) reg [447:0] qc_cmd_expand;
(* anyseq *) reg qc_rsp_ready;
(* anyseq *) reg qc_abort;
(* anyseq *) reg scan_valid;
(* anyseq *) reg scan_permit;
(* anyseq *) reg [13:0] scan_frame;
(* anyseq *) reg scan_rsp_ready;
(* anyseq *) reg [31:0] snapshot_label_crc;
wire f_ap_owned;
wire [3:0] f_coordinator_state;
wire f_ap_offer;
wire f_k_cold_rst;
query_residency_system dut(
.baseline_retired(baseline_retired),
.restore_seed_enable(restore_seed_enable),
.baseline_permit(baseline_permit),
.baseline_epoch(baseline_epoch),
.baseline_req_ready(baseline_req_ready),
.baseline_rsp_valid(baseline_rsp_valid),
.baseline_rsp_status(baseline_rsp_status),
.baseline_rsp_node(baseline_rsp_node),
.baseline_rsp_epoch(baseline_rsp_epoch),
.baseline_rsp_payload(baseline_rsp_payload),
.wm_enable(wm_enable),
.wm_source_version(wm_source_version),
.wm_source_query(wm_source_query),
.wm_source_price(wm_source_price),
.wm_path_crc(wm_path_crc),
.wm_query_crc(wm_query_crc),
.ap_valid(ap_valid),
.ap_rsp_ready(ap_rsp_ready),
.ap_design(ap_design),
.ap_generation(ap_generation),
.ap_checkpoint(ap_checkpoint),
.ap_node(ap_node),
.ap_net(ap_net),
.ap_cookie(ap_cookie),
.jp_start(jp_start),
.jp_commit(jp_commit),
.jp_cancel(jp_cancel),
.jp_done_ready(jp_done_ready),
.jp_manifest_ready(jp_manifest_ready),
.jp_generation(jp_generation),
.jp_design(jp_design),
.jp_checkpoint(jp_checkpoint),
.jp_version(jp_version),
.jp_query(jp_query),
.jp_price(jp_price),
.jp_load(jp_load),
.jp_ack(jp_ack),
.jp_authority_stage(jp_authority_stage),
.boot_required(boot_required),
.boot_cfg_valid(boot_cfg_valid),
.boot_design(boot_design),
.boot_generation(boot_generation),
.boot_checkpoint(boot_checkpoint),
.boot_version(boot_version),
.boot_nodes(boot_nodes),
.boot_label_count(boot_label_count),
.boot_label_crc(boot_label_crc),
.boot_path_crc(boot_path_crc),
.boot_query_crc(boot_query_crc),
.boot_query(boot_query),
.boot_slots(boot_slots),
.boot_price(boot_price),
.boot_payload(boot_payload),
.boot_rsp_ready(boot_rsp_ready),
.boot_verify_valid(boot_verify_valid),
.qc_cp_generation(qc_cp_generation),
.qc_cp_valid(qc_cp_valid),
.qc_cp_restore(qc_cp_restore),
.qc_cp_rsp_ready(qc_cp_rsp_ready),
.qc_cp_s_valid(qc_cp_s_valid),
.qc_cp_s_last(qc_cp_s_last),
.qc_cp_m_ready(qc_cp_m_ready),
.qc_cp_test_reset(qc_cp_test_reset),
.qc_cp_expected_crc(qc_cp_expected_crc),
.qc_cp_s_index(qc_cp_s_index),
.qc_cp_s_data(qc_cp_s_data),
.as_cfg_valid(as_cfg_valid),
.as_cfg_design(as_cfg_design),
.as_cfg_generation(as_cfg_generation),
.as_cfg_primary(as_cfg_primary),
.as_cfg_pool(as_cfg_pool),
.as_cfg_allocator(as_cfg_allocator),
.as_cfg_checkpoint(as_cfg_checkpoint),
.as_cfg_nodes(as_cfg_nodes),
.as_cfg_nets(as_cfg_nets),
.as_cfg_capacity(as_cfg_capacity),
.as_m_arready(as_m_arready),
.as_m_rdata(as_m_rdata),
.as_m_rid(as_m_rid),
.as_m_rresp(as_m_rresp),
.as_m_rlast(as_m_rlast),
.as_m_rvalid(as_m_rvalid),
.as_m_awready(as_m_awready),
.as_m_wready(as_m_wready),
.as_m_bid(as_m_bid),
.as_m_bresp(as_m_bresp),
.as_m_bvalid(as_m_bvalid),
.as_cfg_rsp_ready(as_cfg_rsp_ready),
.as_busy(as_busy),
.cp_valid(cp_valid),
.cp_restore(cp_restore),
.cp_rsp_ready(cp_rsp_ready),
.cp_design(cp_design),
.cp_nodes(cp_nodes),
.cp_nets(cp_nets),
.cp_expected_crc(cp_expected_crc),
.cp_s_valid(cp_s_valid),
.cp_s_index(cp_s_index),
.cp_s_data(cp_s_data),
.cp_s_last(cp_s_last),
.cp_m_ready(cp_m_ready),
.cp_test_reset(cp_test_reset),
.pc_acquire_valid(pc_acquire_valid),
.pc_release_valid(pc_release_valid),
.abort(abort),
.clk(clk),
.cs_m_arready(cs_m_arready),
.cs_m_awready(cs_m_awready),
.cs_m_bid(cs_m_bid),
.cs_m_bresp(cs_m_bresp),
.cs_m_bvalid(cs_m_bvalid),
.cs_m_rdata(cs_m_rdata),
.cs_m_rid(cs_m_rid),
.cs_m_rlast(cs_m_rlast),
.cs_m_rresp(cs_m_rresp),
.cs_m_rvalid(cs_m_rvalid),
.cs_m_wready(cs_m_wready),
.d_m_arready(d_m_arready),
.d_m_awready(d_m_awready),
.d_m_bid(d_m_bid),
.d_m_bresp(d_m_bresp),
.d_m_bvalid(d_m_bvalid),
.d_m_rdata(d_m_rdata),
.d_m_rid(d_m_rid),
.d_m_rlast(d_m_rlast),
.d_m_rresp(d_m_rresp),
.d_m_rvalid(d_m_rvalid),
.d_m_wready(d_m_wready),
.design_id(design_id),
.f_route_payload(f_route_payload),
.f_sp(f_sp),
.f_srr(f_srr),
.f_sv(f_sv),
.g_m_arready(g_m_arready),
.g_m_rdata(g_m_rdata),
.g_m_rid(g_m_rid),
.g_m_rlast(g_m_rlast),
.g_m_rresp(g_m_rresp),
.g_m_rvalid(g_m_rvalid),
.k_a_valid(k_a_valid),
.k_busy(k_busy),
.k_cold_rst(k_cold_rst),
.k_rec_valid(k_rec_valid),
.k_rsp_ready(k_rsp_ready),
.lr_s_cookie(lr_s_cookie),
.lr_s_last(lr_s_last),
.lr_s_node(lr_s_node),
.lr_s_payload(lr_s_payload),
.lr_s_valid(lr_s_valid),
.out_ready(out_ready),
.owner_m_arready(owner_m_arready),
.owner_m_awready(owner_m_awready),
.owner_m_bid(owner_m_bid),
.owner_m_bresp(owner_m_bresp),
.owner_m_bvalid(owner_m_bvalid),
.owner_m_rdata(owner_m_rdata),
.owner_m_rid(owner_m_rid),
.owner_m_rlast(owner_m_rlast),
.owner_m_rresp(owner_m_rresp),
.owner_m_rvalid(owner_m_rvalid),
.owner_m_wready(owner_m_wready),
.p_m_arready(p_m_arready),
.p_m_awready(p_m_awready),
.p_m_bid(p_m_bid),
.p_m_bresp(p_m_bresp),
.p_m_bvalid(p_m_bvalid),
.p_m_rdata(p_m_rdata),
.p_m_rid(p_m_rid),
.p_m_rlast(p_m_rlast),
.p_m_rresp(p_m_rresp),
.p_m_rvalid(p_m_rvalid),
.p_m_wready(p_m_wready),
.q_m_arready(q_m_arready),
.q_m_rdata(q_m_rdata),
.q_m_rid(q_m_rid),
.q_m_rlast(q_m_rlast),
.q_m_rresp(q_m_rresp),
.q_m_rvalid(q_m_rvalid),
.rc_req_valid(rc_req_valid),
.rc_rsp_ready(rc_rsp_ready),
.recover_checkpoint(recover_checkpoint),
.recover_cookie(recover_cookie),
.recover_design(recover_design),
.recover_price(recover_price),
.recover_query(recover_query),
.recover_version(recover_version),
.snapshot_checkpoint(snapshot_checkpoint),
.snapshot_cookie(snapshot_cookie),
.snapshot_count(snapshot_count),
.snapshot_design(snapshot_design),
.snapshot_nodes(snapshot_nodes),
.snapshot_probe(snapshot_probe),
.t_m_arready(t_m_arready),
.t_m_rdata(t_m_rdata),
.t_m_rid(t_m_rid),
.t_m_rlast(t_m_rlast),
.t_m_rresp(t_m_rresp),
.t_m_rvalid(t_m_rvalid),
.test_route_abort(test_route_abort),
.test_route_version_flip(test_route_version_flip),
.qc_cmd_valid(qc_cmd_valid),
.qc_cmd_slot(qc_cmd_slot),
.qc_cmd_cookie(qc_cmd_cookie),
.qc_cmd_route_cookie(qc_cmd_route_cookie),
.qc_cmd_source(qc_cmd_source),
.qc_cmd_key(qc_cmd_key),
.qc_cmd_nodes(qc_cmd_nodes),
.qc_cmd_max_polls(qc_cmd_max_polls),
.qc_cmd_poll_cookie(qc_cmd_poll_cookie),
.qc_cmd_design(qc_cmd_design),
.qc_cmd_query(qc_cmd_query),
.qc_cmd_price(qc_cmd_price),
.qc_cmd_expand(qc_cmd_expand),
.qc_rsp_ready(qc_rsp_ready),
.qc_abort(qc_abort),
.scan_valid(scan_valid),
.scan_permit(scan_permit),
.scan_frame(scan_frame),
.scan_rsp_ready(scan_rsp_ready),
.snapshot_label_crc(snapshot_label_crc),
.f_ap_owned(f_ap_owned),
.f_coordinator_state(f_coordinator_state),
.f_ap_offer(f_ap_offer),
.f_k_cold_rst(f_k_cold_rst));
reg past_valid=0;
initial assume(f_k_cold_rst);
always @(posedge clk) begin
 past_valid<=1;
 if(past_valid && !f_k_cold_rst) begin
  if(f_ap_owned) assume(as_busy);
  assert(f_coordinator_state<=4'd12);
  if(f_coordinator_state!=0) assert(k_busy);
  if(k_busy) assert(!f_ap_offer);
  if(f_coordinator_state>=2 && f_coordinator_state<=9) assert(!f_ap_owned);
  if(k_a_valid) assert(!f_ap_owned && !f_ap_offer);
  if(f_ap_owned && $past(!f_k_cold_rst && !f_ap_owned)) assert(!$past(k_busy));
 end
 cover(past_valid && !f_k_cold_rst && k_a_valid && !f_ap_owned);
 cover(past_valid && !f_k_cold_rst && f_ap_owned);
end
endmodule
