`timescale 1ns/1ps
module protocol_rtl (
 input wire baseline_retired,
 input wire restore_seed_enable,
 input wire baseline_permit,
 input wire [63:0] baseline_epoch,
 output wire baseline_req_valid,
 input wire baseline_req_ready,
 output wire [31:0] baseline_req_node,
 output wire [63:0] baseline_req_epoch,
 input wire baseline_rsp_valid,
 output wire baseline_rsp_ready,
 input wire [3:0] baseline_rsp_status,
 input wire [31:0] baseline_rsp_node,
 input wire [63:0] baseline_rsp_epoch,
 input wire [159:0] baseline_rsp_payload,
 input wire wm_enable,
 input wire [31:0] wm_source_version,
 input wire [1:0] wm_source_query,
 input wire [3:0] wm_source_price,
 input wire [31:0] wm_path_crc,
 input wire [31:0] wm_query_crc,
 output wire wm_owned,
 output wire wm_fault,
 output wire wm_joined,
 output wire [2:0] wm_receipts,
 input wire ap_valid,
 input wire ap_rsp_ready,
 output wire ap_ready,
 output wire ap_rsp_valid,
 input wire [63:0] ap_design,
 input wire [63:0] ap_generation,
 input wire [31:0] ap_checkpoint,
 input wire [31:0] ap_node,
 input wire [31:0] ap_net,
 input wire [31:0] ap_cookie,
 output wire [63:0] ap_rsp_design,
 output wire [63:0] ap_rsp_generation,
 output wire [31:0] ap_rsp_checkpoint,
 output wire [31:0] ap_rsp_cookie,
 output wire [31:0] ap_refs,
 output wire [31:0] ap_occ,
 output wire [3:0] ap_status,
 input wire jp_start,
 output wire jp_start_ready,
 input wire jp_commit,
 output wire jp_commit_ready,
 input wire jp_cancel,
 output wire jp_cancel_ready,
 output wire jp_owned,
 output wire jp_done,
 input wire jp_done_ready,
 output wire [1:0] jp_result,
 input wire jp_manifest_ready,
 input wire [63:0] jp_generation,
 input wire [63:0] jp_design,
 input wire [31:0] jp_checkpoint,
 input wire [31:0] jp_version,
 input wire [1:0] jp_query,
 input wire [3:0] jp_price,
 input wire [1:0] jp_load,
 input wire [1:0] jp_ack,
 output wire [1:0] jp_ready,
 output wire [1:0] jp_reply,
 output wire [1:0] jp_status,
 input wire jp_authority_stage,
 input wire boot_required,
 input wire boot_cfg_valid,
 output wire boot_cfg_ready,
 input wire [63:0] boot_design,
 input wire [63:0] boot_generation,
 input wire [31:0] boot_checkpoint,
 input wire [31:0] boot_version,
 input wire [31:0] boot_nodes,
 input wire [31:0] boot_label_count,
 input wire [31:0] boot_label_crc,
 input wire [31:0] boot_path_crc,
 input wire [31:0] boot_query_crc,
 input wire [1:0] boot_query,
 input wire [3:0] boot_slots,
 input wire [3:0] boot_price,
 input wire [2303:0] boot_payload,
 output wire boot_pending,
 output wire boot_rsp_valid,
 input wire boot_rsp_ready,
 output wire [3:0] boot_status,
 input wire boot_verify_valid,
 output wire boot_verify_ready,
 output wire [31:0] boot_verified_count,
 output wire [3:0] boot_verify_status,
 output wire [4:0] boot_receipts,
 output wire [7:0] boot_config_receipts,
 input wire [63:0] qc_cp_generation,
 input wire qc_cp_valid,
 input wire qc_cp_restore,
 input wire qc_cp_rsp_ready,
 input wire qc_cp_s_valid,
 input wire qc_cp_s_last,
 input wire qc_cp_m_ready,
 input wire qc_cp_test_reset,
 output wire qc_cp_ready,
 output wire qc_cp_busy,
 output wire qc_cp_rsp_valid,
 output wire qc_cp_s_ready,
 output wire qc_cp_m_valid,
 output wire qc_cp_m_last,
 output wire qc_restore_pending,
 input wire [31:0] qc_cp_expected_crc,
 input wire [31:0] qc_cp_s_index,
 input wire [31:0] qc_cp_s_data,
 output wire [31:0] qc_cp_crc,
 output wire [31:0] qc_cp_m_index,
 output wire [31:0] qc_cp_m_data,
 output wire [3:0] qc_cp_status,
 input wire as_cfg_valid,
 output wire as_cfg_ready,
 input wire [63:0] as_cfg_design,
 input wire [63:0] as_cfg_generation,
 input wire [63:0] as_cfg_primary,
 input wire [63:0] as_cfg_pool,
 input wire [63:0] as_cfg_allocator,
 input wire [31:0] as_cfg_checkpoint,
 input wire [31:0] as_cfg_nodes,
 input wire [31:0] as_cfg_nets,
 input wire [31:0] as_cfg_capacity,
 output wire as_configured,
 output wire [63:0] as_bound_design,
 output wire [63:0] as_bound_generation,
 output wire [31:0] as_bound_checkpoint,
 output wire [63:0] as_m_araddr,
 output wire [7:0] as_m_arlen,
 output wire [2:0] as_m_arsize,
 output wire [1:0] as_m_arburst,
 output wire [3:0] as_m_arid,
 output wire as_m_arvalid,
 input wire as_m_arready,
 input wire [511:0] as_m_rdata,
 input wire [3:0] as_m_rid,
 input wire [1:0] as_m_rresp,
 input wire as_m_rlast,
 input wire as_m_rvalid,
 output wire as_m_rready,
 output wire [63:0] as_m_awaddr,
 output wire [7:0] as_m_awlen,
 output wire [2:0] as_m_awsize,
 output wire [1:0] as_m_awburst,
 output wire [3:0] as_m_awid,
 output wire as_m_awvalid,
 input wire as_m_awready,
 output wire [511:0] as_m_wdata,
 output wire [63:0] as_m_wstrb,
 output wire as_m_wlast,
 output wire as_m_wvalid,
 input wire as_m_wready,
 input wire [3:0] as_m_bid,
 input wire [1:0] as_m_bresp,
 input wire as_m_bvalid,
 output wire as_m_bready,
 output wire as_cfg_rsp_valid,
 input wire as_cfg_rsp_ready,
 output wire [2:0] as_cfg_status,
 output wire as_busy,
 output wire as_fault,
 output wire as_drained,
 output wire as_retired,
 output wire [63:0] as_rsp_generation,
 input wire cp_valid,
 input wire cp_restore,
 output wire cp_ready,
 output wire cp_busy,
 output wire cp_rsp_valid,
 input wire cp_rsp_ready,
 output wire [3:0] cp_status,
 output wire [31:0] cp_crc,
 input wire [63:0] cp_design,
 input wire [31:0] cp_nodes,
 input wire [31:0] cp_nets,
 input wire [31:0] cp_expected_crc,
 input wire cp_s_valid,
 output wire cp_s_ready,
 input wire [31:0] cp_s_index,
 input wire [31:0] cp_s_data,
 input wire cp_s_last,
 output wire cp_m_valid,
 input wire cp_m_ready,
 output wire [31:0] cp_m_index,
 output wire [31:0] cp_m_data,
 output wire cp_m_last,
 input wire cp_test_reset,
 output wire pc_route_retired,
 input wire pc_acquire_valid,
 output wire pc_acquire_ready,
 output wire pc_owned,
 input wire pc_release_valid,
 output wire pc_release_ready,
 input wire abort,
 output wire busy,
 output wire cc_busy,
 output wire cc_fault,
 output wire cf_fault,
 input wire clk,
 output wire cost_lease,
 output wire cs_busy,
 output wire cs_configured,
 output wire [63:0] cs_design_id,
 output wire cs_editing,
 output wire cs_fault,
 output wire [63:0] cs_m_araddr,
 output wire [1:0] cs_m_arburst,
 output wire [3:0] cs_m_arid,
 output wire [7:0] cs_m_arlen,
 input wire cs_m_arready,
 output wire [2:0] cs_m_arsize,
 output wire cs_m_arvalid,
 output wire [63:0] cs_m_awaddr,
 output wire [1:0] cs_m_awburst,
 output wire [3:0] cs_m_awid,
 output wire [7:0] cs_m_awlen,
 input wire cs_m_awready,
 output wire [2:0] cs_m_awsize,
 output wire cs_m_awvalid,
 input wire [3:0] cs_m_bid,
 output wire cs_m_bready,
 input wire [1:0] cs_m_bresp,
 input wire cs_m_bvalid,
 input wire [511:0] cs_m_rdata,
 input wire [3:0] cs_m_rid,
 input wire cs_m_rlast,
 output wire cs_m_rready,
 input wire [1:0] cs_m_rresp,
 input wire cs_m_rvalid,
 output wire [511:0] cs_m_wdata,
 output wire cs_m_wlast,
 input wire cs_m_wready,
 output wire [63:0] cs_m_wstrb,
 output wire cs_m_wvalid,
 output wire [31:0] cs_published_version,
 output wire cs_ready_for_query,
 output wire d_configured,
 output wire [63:0] d_m_araddr,
 output wire [1:0] d_m_arburst,
 output wire [3:0] d_m_arid,
 output wire [7:0] d_m_arlen,
 input wire d_m_arready,
 output wire [2:0] d_m_arsize,
 output wire d_m_arvalid,
 output wire [63:0] d_m_awaddr,
 output wire [1:0] d_m_awburst,
 output wire [3:0] d_m_awid,
 output wire [7:0] d_m_awlen,
 input wire d_m_awready,
 output wire [2:0] d_m_awsize,
 output wire d_m_awvalid,
 input wire [3:0] d_m_bid,
 output wire d_m_bready,
 input wire [1:0] d_m_bresp,
 input wire d_m_bvalid,
 input wire [511:0] d_m_rdata,
 input wire [3:0] d_m_rid,
 input wire d_m_rlast,
 output wire d_m_rready,
 input wire [1:0] d_m_rresp,
 input wire d_m_rvalid,
 output wire [511:0] d_m_wdata,
 output wire d_m_wlast,
 input wire d_m_wready,
 output wire [63:0] d_m_wstrb,
 output wire d_m_wvalid,
 input wire [63:0] design_id,
 output wire f_all_drained,
 output wire f_backend_idle,
 output wire f_fault,
 output wire f_normal_retired,
 output wire [3:0] f_phase,
 output wire f_recovery_owned,
 input wire [191:0] f_route_payload,
 input wire [38911:0] f_sp,
 output wire [15:0] f_sr,
 output wire [4095:0] f_srp,
 input wire [15:0] f_srr,
 output wire [15:0] f_srv,
 input wire [15:0] f_sv,
 output wire fault,
 output wire g_configured,
 output wire [63:0] g_m_araddr,
 output wire [1:0] g_m_arburst,
 output wire [3:0] g_m_arid,
 output wire [7:0] g_m_arlen,
 input wire g_m_arready,
 output wire [2:0] g_m_arsize,
 output wire g_m_arvalid,
 input wire [511:0] g_m_rdata,
 input wire [3:0] g_m_rid,
 input wire g_m_rlast,
 output wire g_m_rready,
 input wire [1:0] g_m_rresp,
 input wire g_m_rvalid,
 output wire [31:0] k_a_checkpoint,
 output wire [31:0] k_a_cookie,
 output wire [63:0] k_a_design,
 output wire [31:0] k_a_net,
 output wire [31:0] k_a_node,
 output wire [31:0] k_a_occ,
 output wire k_a_ready,
 output wire [31:0] k_a_refs,
 output wire [31:0] k_a_rsp_checkpoint,
 output wire [31:0] k_a_rsp_cookie,
 output wire [63:0] k_a_rsp_design,
 output wire k_a_rsp_ready,
 output wire k_a_rsp_valid,
 output wire [3:0] k_a_status,
 output wire k_a_valid,
 output wire k_busy,
 input wire k_cold_rst,
 output wire [31:0] k_corrected,
 output wire [31:0] k_count,
 output wire k_fault,
 output wire k_full,
 output wire k_permit,
 output wire k_rec_ready,
 input wire k_rec_valid,
 output wire [31:0] k_rsp_cookie,
 input wire k_rsp_ready,
 output wire [3:0] k_rsp_status,
 output wire k_rsp_valid,
 output wire [31:0] k_saved_checkpoint,
 output wire [63:0] k_saved_design,
 output wire k_target_reset,
 output wire lr_fault,
 output wire [3:0] lr_rsp_status,
 input wire [31:0] lr_s_cookie,
 input wire lr_s_last,
 input wire [31:0] lr_s_node,
 input wire [159:0] lr_s_payload,
 output wire lr_s_ready,
 input wire lr_s_valid,
 output wire [31:0] lr_verified,
 output wire [31:0] lr_written,
 output wire operation_pending,
 output wire [31:0] out_action,
 output wire [255:0] out_attrs,
 output wire [31:0] out_bits,
 output wire [2:0] out_commit_acked,
 output wire [159:0] out_commit_payload,
 output wire [3:0] out_commit_status,
 output wire out_commit_valid,
 output wire [447:0] out_config,
 output wire [31:0] out_connection,
 output wire [31:0] out_cookie,
 output wire [415:0] out_cost_geometry,
 output wire [127:0] out_cost_geometry_result,
 output wire [735:0] out_cost_packet,
 output wire [3:0] out_cost_status,
 output wire out_cost_valid,
 output wire [159:0] out_cost_words,
 output wire [31:0] out_node,
 output wire [31:0] out_offer_before,
 output wire [31:0] out_offer_key,
 output wire [31:0] out_offer_node,
 output wire [31:0] out_offer_size,
 output wire [3:0] out_offer_status,
 output wire out_offer_valid,
 output wire [511:0] out_params,
 output wire out_params_valid,
 output wire [31:0] out_position,
 output wire [255:0] out_post_attrs,
 output wire [31:0] out_post_distance,
 output wire out_post_prev_read,
 output wire [3:0] out_post_status,
 output wire [31:0] out_post_upstream,
 output wire out_post_valid,
 output wire [31:0] out_post_x,
 output wire [31:0] out_post_y,
 output wire [31:0] out_prep_count,
 output wire [31:0] out_prep_history,
 output wire [127:0] out_prep_net_data,
 output wire [31:0] out_prep_occupancy,
 output wire [31:0] out_prep_price_index,
 output wire [31:0] out_prep_price_value,
 output wire [3:0] out_prep_status,
 output wire out_prep_valid,
 output wire [31:0] out_profile_revision,
 input wire out_ready,
 output wire [31:0] out_sequence,
 output wire [31:0] out_services,
 output wire [31:0] out_steps,
 output wire out_valid,
 output wire owner_configured,
 output wire [63:0] owner_m_araddr,
 output wire [1:0] owner_m_arburst,
 output wire [3:0] owner_m_arid,
 output wire [7:0] owner_m_arlen,
 input wire owner_m_arready,
 output wire [2:0] owner_m_arsize,
 output wire owner_m_arvalid,
 output wire [63:0] owner_m_awaddr,
 output wire [1:0] owner_m_awburst,
 output wire [3:0] owner_m_awid,
 output wire [7:0] owner_m_awlen,
 input wire owner_m_awready,
 output wire [2:0] owner_m_awsize,
 output wire owner_m_awvalid,
 input wire [3:0] owner_m_bid,
 output wire owner_m_bready,
 input wire [1:0] owner_m_bresp,
 input wire owner_m_bvalid,
 input wire [511:0] owner_m_rdata,
 input wire [3:0] owner_m_rid,
 input wire owner_m_rlast,
 output wire owner_m_rready,
 input wire [1:0] owner_m_rresp,
 input wire owner_m_rvalid,
 output wire [511:0] owner_m_wdata,
 output wire owner_m_wlast,
 input wire owner_m_wready,
 output wire [63:0] owner_m_wstrb,
 output wire owner_m_wvalid,
 output wire p_active,
 output wire [3:0] p_active_price,
 output wire [1:0] p_active_query,
 output wire [31:0] p_m_araddr,
 output wire [1:0] p_m_arburst,
 output wire [3:0] p_m_arid,
 output wire [7:0] p_m_arlen,
 input wire p_m_arready,
 output wire [2:0] p_m_arsize,
 output wire p_m_arvalid,
 output wire [31:0] p_m_awaddr,
 output wire [1:0] p_m_awburst,
 output wire [3:0] p_m_awid,
 output wire [7:0] p_m_awlen,
 input wire p_m_awready,
 output wire [2:0] p_m_awsize,
 output wire p_m_awvalid,
 input wire [3:0] p_m_bid,
 output wire p_m_bready,
 input wire [1:0] p_m_bresp,
 input wire p_m_bvalid,
 input wire [511:0] p_m_rdata,
 input wire [3:0] p_m_rid,
 input wire p_m_rlast,
 output wire p_m_rready,
 input wire [1:0] p_m_rresp,
 input wire p_m_rvalid,
 output wire [511:0] p_m_wdata,
 output wire p_m_wlast,
 input wire p_m_wready,
 output wire [63:0] p_m_wstrb,
 output wire p_m_wvalid,
 output wire q_busy,
 output wire q_configured,
 output wire q_fault,
 output wire [63:0] q_m_araddr,
 output wire [1:0] q_m_arburst,
 output wire [3:0] q_m_arid,
 output wire [7:0] q_m_arlen,
 input wire q_m_arready,
 output wire [2:0] q_m_arsize,
 output wire q_m_arvalid,
 input wire [511:0] q_m_rdata,
 input wire [3:0] q_m_rid,
 input wire q_m_rlast,
 output wire q_m_rready,
 input wire [1:0] q_m_rresp,
 input wire q_m_rvalid,
 output wire query_ready,
 output wire [31:0] query_version,
 output wire rc_block,
 output wire rc_busy,
 output wire rc_fault,
 output wire rc_req_ready,
 input wire rc_req_valid,
 output wire [31:0] rc_rsp_acked,
 output wire [31:0] rc_rsp_cookie,
 output wire [31:0] rc_rsp_nodes,
 input wire rc_rsp_ready,
 output wire [3:0] rc_rsp_status,
 output wire rc_rsp_valid,
 output wire [3:0] rc_slots,
 input wire [31:0] recover_checkpoint,
 input wire [31:0] recover_cookie,
 input wire [63:0] recover_design,
 input wire [3:0] recover_price,
 input wire [1:0] recover_query,
 input wire [31:0] recover_version,
 output wire rst,
 input wire [31:0] snapshot_checkpoint,
 input wire [31:0] snapshot_cookie,
 input wire [31:0] snapshot_count,
 input wire [63:0] snapshot_design,
 input wire [31:0] snapshot_nodes,
 input wire [31:0] snapshot_probe,
 output wire t_configured,
 output wire [63:0] t_m_araddr,
 output wire [1:0] t_m_arburst,
 output wire [3:0] t_m_arid,
 output wire [7:0] t_m_arlen,
 input wire t_m_arready,
 output wire [2:0] t_m_arsize,
 output wire t_m_arvalid,
 input wire [511:0] t_m_rdata,
 input wire [3:0] t_m_rid,
 input wire t_m_rlast,
 output wire t_m_rready,
 input wire [1:0] t_m_rresp,
 input wire t_m_rvalid,
 input wire test_route_abort,
 input wire test_route_version_flip,
 output wire ss_start_ready,
 output wire ss_rsp_valid,
 output wire [3:0] ss_rsp_status,
 output wire [31:0] ss_rsp_cookie,
 output wire [31:0] ss_polls,
 output wire [31:0] ss_expands,
 output wire [31:0] ss_candidates,
 output wire [31:0] ss_result_node,
 output wire [31:0] ss_result_key,
 output wire ss_busy,
 output wire ss_fault,
 output wire [3:0] ss_phase,
 output wire ss_poll_event,
 output wire [31:0] ss_poll_node,
 output wire [31:0] ss_poll_key,
 output wire [31:0] ss_poll_size,
 input wire qc_cmd_valid,
 output wire qc_cmd_ready,
 input wire [1:0] qc_cmd_slot,
 input wire [31:0] qc_cmd_cookie,
 input wire [31:0] qc_cmd_route_cookie,
 input wire [31:0] qc_cmd_source,
 input wire [31:0] qc_cmd_key,
 input wire [31:0] qc_cmd_nodes,
 input wire [31:0] qc_cmd_max_polls,
 input wire [31:0] qc_cmd_poll_cookie,
 input wire [63:0] qc_cmd_design,
 input wire [1:0] qc_cmd_query,
 input wire [3:0] qc_cmd_price,
 input wire [447:0] qc_cmd_expand,
 output wire qc_rsp_valid,
 input wire qc_rsp_ready,
 output wire [3:0] qc_rsp_status,
 output wire [3:0] qc_rsp_detail,
 output wire [31:0] qc_rsp_cookie,
 output wire [31:0] qc_rsp_nodes,
 output wire [31:0] qc_rsp_acked,
 output wire qc_rsp_committed,
 input wire qc_abort,
 output wire qc_busy,
 output wire qc_fault,
 output wire [3:0] qc_phase,
 output wire qc_prepared_event,
 output wire [31:0] qc_prepare_acked,
 output wire [31:0] qc_cleanup_acked,
 input wire scan_valid,
 output wire scan_ready,
 input wire scan_permit,
 input wire [13:0] scan_frame,
 output wire scan_rsp_valid,
 input wire scan_rsp_ready,
 output wire [2:0] scan_status,
 output wire [13:0] scan_result_frame,
 output wire [26:0] scan_owner,
 output wire scan_published,
 input wire [31:0] snapshot_label_crc,
 output wire [31:0] lr_source_crc
);
reg[31:0]counter,sampled,word_index;
reg[31:0]ka_index,pw_index;
`ifdef KA_NO_STREAM
wire ka_stream=1'b0;
`else
wire ka_stream=(counter>=10&&ka_index<5);
`endif
`ifdef PW_NO_STREAM
wire pw_stream=1'b0;
`else
wire pw_stream=(counter>=10&&pw_index<5);
`endif
`ifdef KA_NO_TRANSFERS
wire ka_ready=1'b0;
`elsif KA_NO_STALLS
wire ka_ready=1'b1;
`elsif KA_READY_X
wire ka_ready=(counter>=12)?1'bx:cp_m_ready;
`else
wire ka_ready=cp_m_ready;
`endif
always @(posedge clk)begin
 if(k_cold_rst)begin ka_index<=0;pw_index<=0;end
 else begin
  if(ka_stream&&ka_ready)ka_index<=ka_index+1;
  if(pw_stream&&p_m_wready)pw_index<=pw_index+1;
 end
end
reg ka_edge_fault=0,pw_edge_fault=0;
always @(negedge clk)begin if(ka_stream&&ka_ready)begin #4.999;ka_edge_fault=1;end else ka_edge_fault<=0;end
always @(negedge clk)begin if(pw_stream&&p_m_wready)begin #4.999;pw_edge_fault=1;end else pw_edge_fault<=0;end
always @(posedge clk)begin ka_edge_fault<=0;pw_edge_fault<=0;end

`ifdef NO_STREAM
wire stream_valid=1'b0;
`else
wire stream_valid=(counter>=10&&word_index<5);
`endif
always @(posedge clk)begin
 if(k_cold_rst)begin counter<=0;sampled<=0;word_index<=0;end
 else begin counter<=counter+1;sampled<=qc_cp_s_data;
  if(stream_valid&&cp_m_ready)word_index<=word_index+1;
 end
end
reg edge_fault=0;
always @(negedge clk)begin if(stream_valid&&cp_m_ready)begin #4.999;edge_fault=1;end else edge_fault<=0;end
always @(posedge clk)edge_fault<=1'b0;
assign baseline_req_valid={1{counter}};
assign baseline_req_node={1{counter}};
assign baseline_req_epoch={2{counter}};
assign baseline_rsp_ready={1{counter}};
assign wm_owned={1{counter}};
assign wm_fault={1{counter}};
assign wm_joined={1{counter}};
assign wm_receipts={1{counter}};
assign ap_ready={1{counter}};
assign ap_rsp_valid={1{counter}};
assign ap_rsp_design={2{counter}};
assign ap_rsp_generation={2{counter}};
assign ap_rsp_checkpoint={1{counter}};
assign ap_rsp_cookie={1{counter}};
assign ap_refs={1{counter}};
assign ap_occ={1{counter}};
assign ap_status={1{counter}};
assign jp_start_ready={1{counter}};
assign jp_commit_ready={1{counter}};
assign jp_cancel_ready={1{counter}};
assign jp_owned={1{counter}};
assign jp_done={1{counter}};
assign jp_result={1{counter}};
assign jp_ready={1{counter}};
assign jp_reply={1{counter}};
assign jp_status={1{counter}};
assign boot_cfg_ready={1{counter}};
assign boot_pending={1{counter}};
assign boot_rsp_valid={1{counter}};
assign boot_status='x;
assign boot_verify_ready={1{counter}};
assign boot_verified_count='z;
assign boot_verify_status={1{counter}};
assign boot_receipts={1{counter}};
assign boot_config_receipts={1{counter}};
assign qc_cp_ready={1{counter}};
assign qc_cp_busy={1{counter}};
assign qc_cp_rsp_valid={1{counter}};
assign qc_cp_s_ready={1{counter}};
assign qc_cp_m_valid={1{counter}};
assign qc_cp_m_last={1{counter}};
assign qc_restore_pending={1{counter}};
assign qc_cp_crc=sampled;
assign qc_cp_m_index={1{counter}};
assign qc_cp_m_data={1{counter}};
assign qc_cp_status={1{counter}};
assign as_cfg_ready={1{counter}};
assign as_configured={1{counter}};
assign as_bound_design={2{counter}};
assign as_bound_generation={2{counter}};
assign as_bound_checkpoint={1{counter}};
assign as_m_araddr={2{counter}};
assign as_m_arlen={1{counter}};
assign as_m_arsize={1{counter}};
assign as_m_arburst={1{counter}};
assign as_m_arid={1{counter}};
assign as_m_arvalid={1{counter}};
assign as_m_rready={1{counter}};
assign as_m_awaddr={2{counter}};
assign as_m_awlen={1{counter}};
assign as_m_awsize={1{counter}};
assign as_m_awburst={1{counter}};
assign as_m_awid={1{counter}};
assign as_m_awvalid={1{counter}};
assign as_m_wdata={16{counter}};
assign as_m_wstrb={2{counter}};
assign as_m_wlast={1{counter}};
assign as_m_wvalid={1{counter}};
assign as_m_bready={1{counter}};
assign as_cfg_rsp_valid={1{counter}};
assign as_cfg_status={1{counter}};
assign as_busy={1{counter}};
assign as_fault={1{counter}};
assign as_drained={1{counter}};
assign as_retired={1{counter}};
assign as_rsp_generation={2{counter}};
assign cp_ready={1{counter}};
assign cp_busy={1{counter}};
assign cp_rsp_valid={1{counter}};
assign cp_status={1{counter}};
assign cp_crc={1{counter}};
assign cp_s_ready={1{counter}};
`ifdef VALID_X_BOTH
assign cp_m_valid=(counter>=12)?1'bx:stream_valid;
`elsif VALID_Z_BOTH
assign cp_m_valid=(counter>=12)?1'bz:stream_valid;
`elsif IDLE_VALID_Z_BOTH
assign cp_m_valid=(counter==1)?1'bz:stream_valid;
`elsif IDLE_VALID_X_BOTH
assign cp_m_valid=(counter==1)?1'bx:stream_valid;
`elsif VALID_DROP
assign cp_m_valid=stream_valid;
`else
assign cp_m_valid=stream_valid;
`endif
`ifdef CP_META_X_BOTH
assign cp_m_index=stream_valid?'x:word_index;
`elsif CP_META_Z_BOTH
assign cp_m_index=stream_valid?'z:word_index;
`elsif META_FLIP
assign cp_m_index=word_index;
`else
assign cp_m_index=word_index;
`endif
`ifdef DATA_X_BOTH
assign cp_m_data=stream_valid?32'hxxxxxxxx:32'hxxxxxxxx;
`elsif DATA_Z_BOTH
assign cp_m_data=stream_valid?32'hzzzzzzzz:32'hxxxxxxxx;
`elsif DATA_FLIP_STALL
assign cp_m_data=stream_valid?(32'hd00d0000+word_index):32'hxxxxxxxx;
`elsif DATA_FLIP_ACTIVE
assign cp_m_data=stream_valid?(32'hd00d0000+word_index):32'hxxxxxxxx;
`elsif EDGE_ONLY_FLIP
assign cp_m_data=stream_valid?(32'hd00d0000+word_index):32'hxxxxxxxx;
`else
assign cp_m_data=stream_valid?(32'hd00d0000+word_index):32'hxxxxxxxx;
`endif
assign cp_m_last=(word_index==4);
assign pc_route_retired={1{counter}};
assign pc_acquire_ready={1{counter}};
assign pc_owned={1{counter}};
assign pc_release_ready={1{counter}};
assign busy={1{counter}};
assign cc_busy={1{counter}};
assign cc_fault={1{counter}};
assign cf_fault={1{counter}};
assign cost_lease={1{counter}};
assign cs_busy={1{counter}};
assign cs_configured={1{counter}};
assign cs_design_id={2{counter}};
assign cs_editing={1{counter}};
assign cs_fault={1{counter}};
assign cs_m_araddr={2{counter}};
assign cs_m_arburst={1{counter}};
assign cs_m_arid={1{counter}};
assign cs_m_arlen={1{counter}};
assign cs_m_arsize={1{counter}};
assign cs_m_arvalid={1{counter}};
assign cs_m_awaddr={2{counter}};
assign cs_m_awburst={1{counter}};
assign cs_m_awid={1{counter}};
assign cs_m_awlen={1{counter}};
assign cs_m_awsize={1{counter}};
assign cs_m_awvalid={1{counter}};
assign cs_m_bready={1{counter}};
assign cs_m_rready={1{counter}};
assign cs_m_wdata={16{counter}};
assign cs_m_wlast={1{counter}};
assign cs_m_wstrb={2{counter}};
assign cs_m_wvalid={1{counter}};
assign cs_published_version={1{counter}};
assign cs_ready_for_query={1{counter}};
assign d_configured={1{counter}};
assign d_m_araddr={2{counter}};
assign d_m_arburst={1{counter}};
assign d_m_arid={1{counter}};
assign d_m_arlen={1{counter}};
assign d_m_arsize={1{counter}};
assign d_m_arvalid={1{counter}};
assign d_m_awaddr={2{counter}};
assign d_m_awburst={1{counter}};
assign d_m_awid={1{counter}};
assign d_m_awlen={1{counter}};
assign d_m_awsize={1{counter}};
assign d_m_awvalid={1{counter}};
assign d_m_bready={1{counter}};
assign d_m_rready={1{counter}};
assign d_m_wdata={16{counter}};
assign d_m_wlast={1{counter}};
assign d_m_wstrb={2{counter}};
assign d_m_wvalid={1{counter}};
assign f_all_drained={1{counter}};
assign f_backend_idle={1{counter}};
assign f_fault={1{counter}};
assign f_normal_retired={1{counter}};
assign f_phase={1{counter}};
assign f_recovery_owned={1{counter}};
assign f_sr={1{counter}};
assign f_srp={128{counter}};
assign f_srv={1{counter}};
assign fault={1{counter}};
assign g_configured={1{counter}};
assign g_m_araddr={2{counter}};
assign g_m_arburst={1{counter}};
assign g_m_arid={1{counter}};
assign g_m_arlen={1{counter}};
assign g_m_arsize={1{counter}};
assign g_m_arvalid={1{counter}};
assign g_m_rready={1{counter}};
assign k_a_checkpoint=32'd17;
`ifdef KA_META_FLIP
assign k_a_cookie=(32'h11110000+ka_index);
`elsif KA_META_X_BOTH
assign k_a_cookie=ka_stream?'x:(32'h11110000+ka_index);
`elsif KA_META_Z_BOTH
assign k_a_cookie=ka_stream?'z:(32'h11110000+ka_index);
`else
assign k_a_cookie=(32'h11110000+ka_index);
`endif
assign k_a_design=64'h1234;
`ifdef KA_NET_ONLY_FLIP
assign k_a_net=ka_stream?(32'hb0000000+ka_index):'x;
`else
`ifdef KA_DATA_X_BOTH
assign k_a_net=ka_stream?'x:'x;
`elsif KA_DATA_Z_BOTH
assign k_a_net=ka_stream?'z:'x;
`elsif KA_DATA_FLIP_STALL
assign k_a_net=ka_stream?(32'hb0000000+ka_index):'x;
`elsif KA_DATA_FLIP_ACTIVE
assign k_a_net=ka_stream?(32'hb0000000+ka_index):'x;
`elsif KA_EDGE_ONLY_FLIP
assign k_a_net=ka_stream?(32'hb0000000+ka_index):'x;
`else
assign k_a_net=ka_stream?(32'hb0000000+ka_index):'x;
`endif
`endif
`ifdef KA_NODE_ONLY_FLIP
assign k_a_node=ka_stream?(32'ha0000000+ka_index):'x;
`else
`ifdef KA_DATA_X_BOTH
assign k_a_node=ka_stream?'x:'x;
`elsif KA_DATA_Z_BOTH
assign k_a_node=ka_stream?'z:'x;
`elsif KA_DATA_FLIP_STALL
assign k_a_node=ka_stream?(32'ha0000000+ka_index):'x;
`elsif KA_DATA_FLIP_ACTIVE
assign k_a_node=ka_stream?(32'ha0000000+ka_index):'x;
`elsif KA_EDGE_ONLY_FLIP
assign k_a_node=ka_stream?(32'ha0000000+ka_index):'x;
`else
assign k_a_node=ka_stream?(32'ha0000000+ka_index):'x;
`endif
`endif
assign k_a_occ={1{counter}};
assign k_a_ready=ka_ready;
assign k_a_refs={1{counter}};
assign k_a_rsp_checkpoint={1{counter}};
assign k_a_rsp_cookie={1{counter}};
assign k_a_rsp_design={2{counter}};
assign k_a_rsp_ready={1{counter}};
assign k_a_rsp_valid={1{counter}};
assign k_a_status={1{counter}};
`ifdef KA_VALID_X_BOTH
assign k_a_valid=(counter>=12)?1'bx:ka_stream;
`elsif KA_VALID_Z_BOTH
assign k_a_valid=(counter>=12)?1'bz:ka_stream;
`elsif KA_IDLE_VALID_X_BOTH
assign k_a_valid=(counter==1)?1'bx:ka_stream;
`elsif KA_IDLE_VALID_Z_BOTH
assign k_a_valid=(counter==1)?1'bz:ka_stream;
`elsif KA_VALID_DROP
assign k_a_valid=ka_stream;
`else
assign k_a_valid=ka_stream;
`endif
assign k_busy={1{counter}};
assign k_corrected={1{counter}};
assign k_count={1{counter}};
assign k_fault={1{counter}};
assign k_full={1{counter}};
assign k_permit={1{counter}};
assign k_rec_ready={1{counter}};
assign k_rsp_cookie={1{counter}};
assign k_rsp_status={1{counter}};
assign k_rsp_valid={1{counter}};
assign k_saved_checkpoint={1{counter}};
assign k_saved_design={2{counter}};
assign k_target_reset={1{counter}};
assign lr_fault={1{counter}};
assign lr_rsp_status={1{counter}};
assign lr_s_ready={1{counter}};
assign lr_verified={1{counter}};
assign lr_written={1{counter}};
assign operation_pending={1{counter}};
assign out_action={1{counter}};
assign out_attrs={8{counter}};
assign out_bits={1{counter}};
assign out_commit_acked={1{counter}};
assign out_commit_payload={5{counter}};
assign out_commit_status={1{counter}};
assign out_commit_valid={1{counter}};
assign out_config={14{counter}};
assign out_connection={1{counter}};
assign out_cookie={1{counter}};
assign out_cost_geometry={13{counter}};
assign out_cost_geometry_result={4{counter}};
assign out_cost_packet={23{counter}};
assign out_cost_status={1{counter}};
assign out_cost_valid={1{counter}};
assign out_cost_words={5{counter}};
assign out_node={1{counter}};
assign out_offer_before={1{counter}};
assign out_offer_key={1{counter}};
assign out_offer_node={1{counter}};
assign out_offer_size={1{counter}};
assign out_offer_status={1{counter}};
assign out_offer_valid={1{counter}};
assign out_params={16{counter}};
assign out_params_valid={1{counter}};
assign out_position={1{counter}};
assign out_post_attrs={8{counter}};
assign out_post_distance={1{counter}};
assign out_post_prev_read={1{counter}};
assign out_post_status={1{counter}};
assign out_post_upstream={1{counter}};
assign out_post_valid={1{counter}};
assign out_post_x={1{counter}};
assign out_post_y={1{counter}};
assign out_prep_count={1{counter}};
assign out_prep_history={1{counter}};
assign out_prep_net_data={4{counter}};
assign out_prep_occupancy={1{counter}};
assign out_prep_price_index={1{counter}};
assign out_prep_price_value={1{counter}};
assign out_prep_status={1{counter}};
assign out_prep_valid={1{counter}};
assign out_profile_revision={1{counter}};
assign out_sequence={1{counter}};
assign out_services={1{counter}};
assign out_steps={1{counter}};
assign out_valid={1{counter}};
assign owner_configured={1{counter}};
assign owner_m_araddr={2{counter}};
assign owner_m_arburst={1{counter}};
assign owner_m_arid={1{counter}};
assign owner_m_arlen={1{counter}};
assign owner_m_arsize={1{counter}};
assign owner_m_arvalid={1{counter}};
assign owner_m_awaddr={2{counter}};
assign owner_m_awburst={1{counter}};
assign owner_m_awid={1{counter}};
assign owner_m_awlen={1{counter}};
assign owner_m_awsize={1{counter}};
assign owner_m_awvalid={1{counter}};
assign owner_m_bready={1{counter}};
assign owner_m_rready={1{counter}};
assign owner_m_wdata={16{counter}};
assign owner_m_wlast={1{counter}};
assign owner_m_wstrb={2{counter}};
assign owner_m_wvalid={1{counter}};
assign p_active={1{counter}};
assign p_active_price={1{counter}};
assign p_active_query={1{counter}};
assign p_m_araddr={1{counter}};
assign p_m_arburst={1{counter}};
assign p_m_arid={1{counter}};
assign p_m_arlen={1{counter}};
assign p_m_arsize={1{counter}};
assign p_m_arvalid={1{counter}};
assign p_m_awaddr={1{counter}};
assign p_m_awburst={1{counter}};
assign p_m_awid={1{counter}};
assign p_m_awlen={1{counter}};
assign p_m_awsize={1{counter}};
assign p_m_awvalid={1{counter}};
assign p_m_bready={1{counter}};
assign p_m_rready={1{counter}};
`ifdef PW_DATA_X_BOTH
assign p_m_wdata=pw_stream?'x:'x;
`elsif PW_DATA_Z_BOTH
assign p_m_wdata=pw_stream?'z:'x;
`elsif PW_DATA_FLIP_STALL
assign p_m_wdata=pw_stream?(512'hc0000000+pw_index):'x;
`elsif PW_DATA_FLIP_ACTIVE
assign p_m_wdata=pw_stream?(512'hc0000000+pw_index):'x;
`elsif PW_EDGE_ONLY_FLIP
assign p_m_wdata=pw_stream?(512'hc0000000+pw_index):'x;
`else
assign p_m_wdata=pw_stream?(512'hc0000000+pw_index):'x;
`endif
assign p_m_wlast=(pw_index==4);
`ifdef PW_META_FLIP
assign p_m_wstrb=64'hffffffffffffffff;
`elsif PW_META_X_BOTH
assign p_m_wstrb=pw_stream?'x:64'hffffffffffffffff;
`elsif PW_META_Z_BOTH
assign p_m_wstrb=pw_stream?'z:64'hffffffffffffffff;
`else
assign p_m_wstrb=64'hffffffffffffffff;
`endif
`ifdef PW_VALID_X_BOTH
assign p_m_wvalid=(counter>=12)?1'bx:pw_stream;
`elsif PW_VALID_Z_BOTH
assign p_m_wvalid=(counter>=12)?1'bz:pw_stream;
`elsif PW_IDLE_VALID_X_BOTH
assign p_m_wvalid=(counter==1)?1'bx:pw_stream;
`elsif PW_IDLE_VALID_Z_BOTH
assign p_m_wvalid=(counter==1)?1'bz:pw_stream;
`elsif PW_VALID_DROP
assign p_m_wvalid=pw_stream;
`else
assign p_m_wvalid=pw_stream;
`endif
assign q_busy={1{counter}};
assign q_configured={1{counter}};
assign q_fault={1{counter}};
assign q_m_araddr={2{counter}};
assign q_m_arburst={1{counter}};
assign q_m_arid={1{counter}};
assign q_m_arlen={1{counter}};
assign q_m_arsize={1{counter}};
assign q_m_arvalid={1{counter}};
assign q_m_rready={1{counter}};
assign query_ready={1{counter}};
assign query_version={1{counter}};
assign rc_block={1{counter}};
assign rc_busy={1{counter}};
assign rc_fault={1{counter}};
assign rc_req_ready={1{counter}};
assign rc_rsp_acked={1{counter}};
assign rc_rsp_cookie={1{counter}};
assign rc_rsp_nodes={1{counter}};
assign rc_rsp_status={1{counter}};
assign rc_rsp_valid={1{counter}};
assign rc_slots={1{counter}};
assign rst={1{counter}};
assign t_configured={1{counter}};
assign t_m_araddr={2{counter}};
assign t_m_arburst={1{counter}};
assign t_m_arid={1{counter}};
assign t_m_arlen={1{counter}};
assign t_m_arsize={1{counter}};
assign t_m_arvalid={1{counter}};
assign t_m_rready={1{counter}};
assign ss_start_ready={1{counter}};
assign ss_rsp_valid={1{counter}};
assign ss_rsp_status={1{counter}};
assign ss_rsp_cookie={1{counter}};
assign ss_polls={1{counter}};
assign ss_expands={1{counter}};
assign ss_candidates={1{counter}};
assign ss_result_node={1{counter}};
assign ss_result_key={1{counter}};
assign ss_busy={1{counter}};
assign ss_fault={1{counter}};
assign ss_phase={1{counter}};
assign ss_poll_event={1{counter}};
assign ss_poll_node={1{counter}};
assign ss_poll_key={1{counter}};
assign ss_poll_size={1{counter}};
assign qc_cmd_ready={1{counter}};
assign qc_rsp_valid={1{counter}};
assign qc_rsp_status={1{counter}};
assign qc_rsp_detail={1{counter}};
assign qc_rsp_cookie={1{counter}};
assign qc_rsp_nodes={1{counter}};
assign qc_rsp_acked={1{counter}};
assign qc_rsp_committed={1{counter}};
assign qc_busy={1{counter}};
assign qc_fault={1{counter}};
assign qc_phase={1{counter}};
assign qc_prepared_event={1{counter}};
assign qc_prepare_acked={1{counter}};
assign qc_cleanup_acked={1{counter}};
assign scan_ready={1{counter}};
assign scan_rsp_valid={1{counter}};
assign scan_status={1{counter}};
assign scan_result_frame={1{counter}};
assign scan_owner={1{counter}};
assign scan_published={1{counter}};
assign lr_source_crc={1{counter}};
endmodule
module protocol_gate (
 input wire baseline_retired,
 input wire restore_seed_enable,
 input wire baseline_permit,
 input wire [63:0] baseline_epoch,
 output wire baseline_req_valid,
 input wire baseline_req_ready,
 output wire [31:0] baseline_req_node,
 output wire [63:0] baseline_req_epoch,
 input wire baseline_rsp_valid,
 output wire baseline_rsp_ready,
 input wire [3:0] baseline_rsp_status,
 input wire [31:0] baseline_rsp_node,
 input wire [63:0] baseline_rsp_epoch,
 input wire [159:0] baseline_rsp_payload,
 input wire wm_enable,
 input wire [31:0] wm_source_version,
 input wire [1:0] wm_source_query,
 input wire [3:0] wm_source_price,
 input wire [31:0] wm_path_crc,
 input wire [31:0] wm_query_crc,
 output wire wm_owned,
 output wire wm_fault,
 output wire wm_joined,
 output wire [2:0] wm_receipts,
 input wire ap_valid,
 input wire ap_rsp_ready,
 output wire ap_ready,
 output wire ap_rsp_valid,
 input wire [63:0] ap_design,
 input wire [63:0] ap_generation,
 input wire [31:0] ap_checkpoint,
 input wire [31:0] ap_node,
 input wire [31:0] ap_net,
 input wire [31:0] ap_cookie,
 output wire [63:0] ap_rsp_design,
 output wire [63:0] ap_rsp_generation,
 output wire [31:0] ap_rsp_checkpoint,
 output wire [31:0] ap_rsp_cookie,
 output wire [31:0] ap_refs,
 output wire [31:0] ap_occ,
 output wire [3:0] ap_status,
 input wire jp_start,
 output wire jp_start_ready,
 input wire jp_commit,
 output wire jp_commit_ready,
 input wire jp_cancel,
 output wire jp_cancel_ready,
 output wire jp_owned,
 output wire jp_done,
 input wire jp_done_ready,
 output wire [1:0] jp_result,
 input wire jp_manifest_ready,
 input wire [63:0] jp_generation,
 input wire [63:0] jp_design,
 input wire [31:0] jp_checkpoint,
 input wire [31:0] jp_version,
 input wire [1:0] jp_query,
 input wire [3:0] jp_price,
 input wire [1:0] jp_load,
 input wire [1:0] jp_ack,
 output wire [1:0] jp_ready,
 output wire [1:0] jp_reply,
 output wire [1:0] jp_status,
 input wire jp_authority_stage,
 input wire boot_required,
 input wire boot_cfg_valid,
 output wire boot_cfg_ready,
 input wire [63:0] boot_design,
 input wire [63:0] boot_generation,
 input wire [31:0] boot_checkpoint,
 input wire [31:0] boot_version,
 input wire [31:0] boot_nodes,
 input wire [31:0] boot_label_count,
 input wire [31:0] boot_label_crc,
 input wire [31:0] boot_path_crc,
 input wire [31:0] boot_query_crc,
 input wire [1:0] boot_query,
 input wire [3:0] boot_slots,
 input wire [3:0] boot_price,
 input wire [2303:0] boot_payload,
 output wire boot_pending,
 output wire boot_rsp_valid,
 input wire boot_rsp_ready,
 output wire [3:0] boot_status,
 input wire boot_verify_valid,
 output wire boot_verify_ready,
 output wire [31:0] boot_verified_count,
 output wire [3:0] boot_verify_status,
 output wire [4:0] boot_receipts,
 output wire [7:0] boot_config_receipts,
 input wire [63:0] qc_cp_generation,
 input wire qc_cp_valid,
 input wire qc_cp_restore,
 input wire qc_cp_rsp_ready,
 input wire qc_cp_s_valid,
 input wire qc_cp_s_last,
 input wire qc_cp_m_ready,
 input wire qc_cp_test_reset,
 output wire qc_cp_ready,
 output wire qc_cp_busy,
 output wire qc_cp_rsp_valid,
 output wire qc_cp_s_ready,
 output wire qc_cp_m_valid,
 output wire qc_cp_m_last,
 output wire qc_restore_pending,
 input wire [31:0] qc_cp_expected_crc,
 input wire [31:0] qc_cp_s_index,
 input wire [31:0] qc_cp_s_data,
 output wire [31:0] qc_cp_crc,
 output wire [31:0] qc_cp_m_index,
 output wire [31:0] qc_cp_m_data,
 output wire [3:0] qc_cp_status,
 input wire as_cfg_valid,
 output wire as_cfg_ready,
 input wire [63:0] as_cfg_design,
 input wire [63:0] as_cfg_generation,
 input wire [63:0] as_cfg_primary,
 input wire [63:0] as_cfg_pool,
 input wire [63:0] as_cfg_allocator,
 input wire [31:0] as_cfg_checkpoint,
 input wire [31:0] as_cfg_nodes,
 input wire [31:0] as_cfg_nets,
 input wire [31:0] as_cfg_capacity,
 output wire as_configured,
 output wire [63:0] as_bound_design,
 output wire [63:0] as_bound_generation,
 output wire [31:0] as_bound_checkpoint,
 output wire [63:0] as_m_araddr,
 output wire [7:0] as_m_arlen,
 output wire [2:0] as_m_arsize,
 output wire [1:0] as_m_arburst,
 output wire [3:0] as_m_arid,
 output wire as_m_arvalid,
 input wire as_m_arready,
 input wire [511:0] as_m_rdata,
 input wire [3:0] as_m_rid,
 input wire [1:0] as_m_rresp,
 input wire as_m_rlast,
 input wire as_m_rvalid,
 output wire as_m_rready,
 output wire [63:0] as_m_awaddr,
 output wire [7:0] as_m_awlen,
 output wire [2:0] as_m_awsize,
 output wire [1:0] as_m_awburst,
 output wire [3:0] as_m_awid,
 output wire as_m_awvalid,
 input wire as_m_awready,
 output wire [511:0] as_m_wdata,
 output wire [63:0] as_m_wstrb,
 output wire as_m_wlast,
 output wire as_m_wvalid,
 input wire as_m_wready,
 input wire [3:0] as_m_bid,
 input wire [1:0] as_m_bresp,
 input wire as_m_bvalid,
 output wire as_m_bready,
 output wire as_cfg_rsp_valid,
 input wire as_cfg_rsp_ready,
 output wire [2:0] as_cfg_status,
 output wire as_busy,
 output wire as_fault,
 output wire as_drained,
 output wire as_retired,
 output wire [63:0] as_rsp_generation,
 input wire cp_valid,
 input wire cp_restore,
 output wire cp_ready,
 output wire cp_busy,
 output wire cp_rsp_valid,
 input wire cp_rsp_ready,
 output wire [3:0] cp_status,
 output wire [31:0] cp_crc,
 input wire [63:0] cp_design,
 input wire [31:0] cp_nodes,
 input wire [31:0] cp_nets,
 input wire [31:0] cp_expected_crc,
 input wire cp_s_valid,
 output wire cp_s_ready,
 input wire [31:0] cp_s_index,
 input wire [31:0] cp_s_data,
 input wire cp_s_last,
 output wire cp_m_valid,
 input wire cp_m_ready,
 output wire [31:0] cp_m_index,
 output wire [31:0] cp_m_data,
 output wire cp_m_last,
 input wire cp_test_reset,
 output wire pc_route_retired,
 input wire pc_acquire_valid,
 output wire pc_acquire_ready,
 output wire pc_owned,
 input wire pc_release_valid,
 output wire pc_release_ready,
 input wire abort,
 output wire busy,
 output wire cc_busy,
 output wire cc_fault,
 output wire cf_fault,
 input wire clk,
 output wire cost_lease,
 output wire cs_busy,
 output wire cs_configured,
 output wire [63:0] cs_design_id,
 output wire cs_editing,
 output wire cs_fault,
 output wire [63:0] cs_m_araddr,
 output wire [1:0] cs_m_arburst,
 output wire [3:0] cs_m_arid,
 output wire [7:0] cs_m_arlen,
 input wire cs_m_arready,
 output wire [2:0] cs_m_arsize,
 output wire cs_m_arvalid,
 output wire [63:0] cs_m_awaddr,
 output wire [1:0] cs_m_awburst,
 output wire [3:0] cs_m_awid,
 output wire [7:0] cs_m_awlen,
 input wire cs_m_awready,
 output wire [2:0] cs_m_awsize,
 output wire cs_m_awvalid,
 input wire [3:0] cs_m_bid,
 output wire cs_m_bready,
 input wire [1:0] cs_m_bresp,
 input wire cs_m_bvalid,
 input wire [511:0] cs_m_rdata,
 input wire [3:0] cs_m_rid,
 input wire cs_m_rlast,
 output wire cs_m_rready,
 input wire [1:0] cs_m_rresp,
 input wire cs_m_rvalid,
 output wire [511:0] cs_m_wdata,
 output wire cs_m_wlast,
 input wire cs_m_wready,
 output wire [63:0] cs_m_wstrb,
 output wire cs_m_wvalid,
 output wire [31:0] cs_published_version,
 output wire cs_ready_for_query,
 output wire d_configured,
 output wire [63:0] d_m_araddr,
 output wire [1:0] d_m_arburst,
 output wire [3:0] d_m_arid,
 output wire [7:0] d_m_arlen,
 input wire d_m_arready,
 output wire [2:0] d_m_arsize,
 output wire d_m_arvalid,
 output wire [63:0] d_m_awaddr,
 output wire [1:0] d_m_awburst,
 output wire [3:0] d_m_awid,
 output wire [7:0] d_m_awlen,
 input wire d_m_awready,
 output wire [2:0] d_m_awsize,
 output wire d_m_awvalid,
 input wire [3:0] d_m_bid,
 output wire d_m_bready,
 input wire [1:0] d_m_bresp,
 input wire d_m_bvalid,
 input wire [511:0] d_m_rdata,
 input wire [3:0] d_m_rid,
 input wire d_m_rlast,
 output wire d_m_rready,
 input wire [1:0] d_m_rresp,
 input wire d_m_rvalid,
 output wire [511:0] d_m_wdata,
 output wire d_m_wlast,
 input wire d_m_wready,
 output wire [63:0] d_m_wstrb,
 output wire d_m_wvalid,
 input wire [63:0] design_id,
 output wire f_all_drained,
 output wire f_backend_idle,
 output wire f_fault,
 output wire f_normal_retired,
 output wire [3:0] f_phase,
 output wire f_recovery_owned,
 input wire [191:0] f_route_payload,
 input wire [38911:0] f_sp,
 output wire [15:0] f_sr,
 output wire [4095:0] f_srp,
 input wire [15:0] f_srr,
 output wire [15:0] f_srv,
 input wire [15:0] f_sv,
 output wire fault,
 output wire g_configured,
 output wire [63:0] g_m_araddr,
 output wire [1:0] g_m_arburst,
 output wire [3:0] g_m_arid,
 output wire [7:0] g_m_arlen,
 input wire g_m_arready,
 output wire [2:0] g_m_arsize,
 output wire g_m_arvalid,
 input wire [511:0] g_m_rdata,
 input wire [3:0] g_m_rid,
 input wire g_m_rlast,
 output wire g_m_rready,
 input wire [1:0] g_m_rresp,
 input wire g_m_rvalid,
 output wire [31:0] k_a_checkpoint,
 output wire [31:0] k_a_cookie,
 output wire [63:0] k_a_design,
 output wire [31:0] k_a_net,
 output wire [31:0] k_a_node,
 output wire [31:0] k_a_occ,
 output wire k_a_ready,
 output wire [31:0] k_a_refs,
 output wire [31:0] k_a_rsp_checkpoint,
 output wire [31:0] k_a_rsp_cookie,
 output wire [63:0] k_a_rsp_design,
 output wire k_a_rsp_ready,
 output wire k_a_rsp_valid,
 output wire [3:0] k_a_status,
 output wire k_a_valid,
 output wire k_busy,
 input wire k_cold_rst,
 output wire [31:0] k_corrected,
 output wire [31:0] k_count,
 output wire k_fault,
 output wire k_full,
 output wire k_permit,
 output wire k_rec_ready,
 input wire k_rec_valid,
 output wire [31:0] k_rsp_cookie,
 input wire k_rsp_ready,
 output wire [3:0] k_rsp_status,
 output wire k_rsp_valid,
 output wire [31:0] k_saved_checkpoint,
 output wire [63:0] k_saved_design,
 output wire k_target_reset,
 output wire lr_fault,
 output wire [3:0] lr_rsp_status,
 input wire [31:0] lr_s_cookie,
 input wire lr_s_last,
 input wire [31:0] lr_s_node,
 input wire [159:0] lr_s_payload,
 output wire lr_s_ready,
 input wire lr_s_valid,
 output wire [31:0] lr_verified,
 output wire [31:0] lr_written,
 output wire operation_pending,
 output wire [31:0] out_action,
 output wire [255:0] out_attrs,
 output wire [31:0] out_bits,
 output wire [2:0] out_commit_acked,
 output wire [159:0] out_commit_payload,
 output wire [3:0] out_commit_status,
 output wire out_commit_valid,
 output wire [447:0] out_config,
 output wire [31:0] out_connection,
 output wire [31:0] out_cookie,
 output wire [415:0] out_cost_geometry,
 output wire [127:0] out_cost_geometry_result,
 output wire [735:0] out_cost_packet,
 output wire [3:0] out_cost_status,
 output wire out_cost_valid,
 output wire [159:0] out_cost_words,
 output wire [31:0] out_node,
 output wire [31:0] out_offer_before,
 output wire [31:0] out_offer_key,
 output wire [31:0] out_offer_node,
 output wire [31:0] out_offer_size,
 output wire [3:0] out_offer_status,
 output wire out_offer_valid,
 output wire [511:0] out_params,
 output wire out_params_valid,
 output wire [31:0] out_position,
 output wire [255:0] out_post_attrs,
 output wire [31:0] out_post_distance,
 output wire out_post_prev_read,
 output wire [3:0] out_post_status,
 output wire [31:0] out_post_upstream,
 output wire out_post_valid,
 output wire [31:0] out_post_x,
 output wire [31:0] out_post_y,
 output wire [31:0] out_prep_count,
 output wire [31:0] out_prep_history,
 output wire [127:0] out_prep_net_data,
 output wire [31:0] out_prep_occupancy,
 output wire [31:0] out_prep_price_index,
 output wire [31:0] out_prep_price_value,
 output wire [3:0] out_prep_status,
 output wire out_prep_valid,
 output wire [31:0] out_profile_revision,
 input wire out_ready,
 output wire [31:0] out_sequence,
 output wire [31:0] out_services,
 output wire [31:0] out_steps,
 output wire out_valid,
 output wire owner_configured,
 output wire [63:0] owner_m_araddr,
 output wire [1:0] owner_m_arburst,
 output wire [3:0] owner_m_arid,
 output wire [7:0] owner_m_arlen,
 input wire owner_m_arready,
 output wire [2:0] owner_m_arsize,
 output wire owner_m_arvalid,
 output wire [63:0] owner_m_awaddr,
 output wire [1:0] owner_m_awburst,
 output wire [3:0] owner_m_awid,
 output wire [7:0] owner_m_awlen,
 input wire owner_m_awready,
 output wire [2:0] owner_m_awsize,
 output wire owner_m_awvalid,
 input wire [3:0] owner_m_bid,
 output wire owner_m_bready,
 input wire [1:0] owner_m_bresp,
 input wire owner_m_bvalid,
 input wire [511:0] owner_m_rdata,
 input wire [3:0] owner_m_rid,
 input wire owner_m_rlast,
 output wire owner_m_rready,
 input wire [1:0] owner_m_rresp,
 input wire owner_m_rvalid,
 output wire [511:0] owner_m_wdata,
 output wire owner_m_wlast,
 input wire owner_m_wready,
 output wire [63:0] owner_m_wstrb,
 output wire owner_m_wvalid,
 output wire p_active,
 output wire [3:0] p_active_price,
 output wire [1:0] p_active_query,
 output wire [31:0] p_m_araddr,
 output wire [1:0] p_m_arburst,
 output wire [3:0] p_m_arid,
 output wire [7:0] p_m_arlen,
 input wire p_m_arready,
 output wire [2:0] p_m_arsize,
 output wire p_m_arvalid,
 output wire [31:0] p_m_awaddr,
 output wire [1:0] p_m_awburst,
 output wire [3:0] p_m_awid,
 output wire [7:0] p_m_awlen,
 input wire p_m_awready,
 output wire [2:0] p_m_awsize,
 output wire p_m_awvalid,
 input wire [3:0] p_m_bid,
 output wire p_m_bready,
 input wire [1:0] p_m_bresp,
 input wire p_m_bvalid,
 input wire [511:0] p_m_rdata,
 input wire [3:0] p_m_rid,
 input wire p_m_rlast,
 output wire p_m_rready,
 input wire [1:0] p_m_rresp,
 input wire p_m_rvalid,
 output wire [511:0] p_m_wdata,
 output wire p_m_wlast,
 input wire p_m_wready,
 output wire [63:0] p_m_wstrb,
 output wire p_m_wvalid,
 output wire q_busy,
 output wire q_configured,
 output wire q_fault,
 output wire [63:0] q_m_araddr,
 output wire [1:0] q_m_arburst,
 output wire [3:0] q_m_arid,
 output wire [7:0] q_m_arlen,
 input wire q_m_arready,
 output wire [2:0] q_m_arsize,
 output wire q_m_arvalid,
 input wire [511:0] q_m_rdata,
 input wire [3:0] q_m_rid,
 input wire q_m_rlast,
 output wire q_m_rready,
 input wire [1:0] q_m_rresp,
 input wire q_m_rvalid,
 output wire query_ready,
 output wire [31:0] query_version,
 output wire rc_block,
 output wire rc_busy,
 output wire rc_fault,
 output wire rc_req_ready,
 input wire rc_req_valid,
 output wire [31:0] rc_rsp_acked,
 output wire [31:0] rc_rsp_cookie,
 output wire [31:0] rc_rsp_nodes,
 input wire rc_rsp_ready,
 output wire [3:0] rc_rsp_status,
 output wire rc_rsp_valid,
 output wire [3:0] rc_slots,
 input wire [31:0] recover_checkpoint,
 input wire [31:0] recover_cookie,
 input wire [63:0] recover_design,
 input wire [3:0] recover_price,
 input wire [1:0] recover_query,
 input wire [31:0] recover_version,
 output wire rst,
 input wire [31:0] snapshot_checkpoint,
 input wire [31:0] snapshot_cookie,
 input wire [31:0] snapshot_count,
 input wire [63:0] snapshot_design,
 input wire [31:0] snapshot_nodes,
 input wire [31:0] snapshot_probe,
 output wire t_configured,
 output wire [63:0] t_m_araddr,
 output wire [1:0] t_m_arburst,
 output wire [3:0] t_m_arid,
 output wire [7:0] t_m_arlen,
 input wire t_m_arready,
 output wire [2:0] t_m_arsize,
 output wire t_m_arvalid,
 input wire [511:0] t_m_rdata,
 input wire [3:0] t_m_rid,
 input wire t_m_rlast,
 output wire t_m_rready,
 input wire [1:0] t_m_rresp,
 input wire t_m_rvalid,
 input wire test_route_abort,
 input wire test_route_version_flip,
 output wire ss_start_ready,
 output wire ss_rsp_valid,
 output wire [3:0] ss_rsp_status,
 output wire [31:0] ss_rsp_cookie,
 output wire [31:0] ss_polls,
 output wire [31:0] ss_expands,
 output wire [31:0] ss_candidates,
 output wire [31:0] ss_result_node,
 output wire [31:0] ss_result_key,
 output wire ss_busy,
 output wire ss_fault,
 output wire [3:0] ss_phase,
 output wire ss_poll_event,
 output wire [31:0] ss_poll_node,
 output wire [31:0] ss_poll_key,
 output wire [31:0] ss_poll_size,
 input wire qc_cmd_valid,
 output wire qc_cmd_ready,
 input wire [1:0] qc_cmd_slot,
 input wire [31:0] qc_cmd_cookie,
 input wire [31:0] qc_cmd_route_cookie,
 input wire [31:0] qc_cmd_source,
 input wire [31:0] qc_cmd_key,
 input wire [31:0] qc_cmd_nodes,
 input wire [31:0] qc_cmd_max_polls,
 input wire [31:0] qc_cmd_poll_cookie,
 input wire [63:0] qc_cmd_design,
 input wire [1:0] qc_cmd_query,
 input wire [3:0] qc_cmd_price,
 input wire [447:0] qc_cmd_expand,
 output wire qc_rsp_valid,
 input wire qc_rsp_ready,
 output wire [3:0] qc_rsp_status,
 output wire [3:0] qc_rsp_detail,
 output wire [31:0] qc_rsp_cookie,
 output wire [31:0] qc_rsp_nodes,
 output wire [31:0] qc_rsp_acked,
 output wire qc_rsp_committed,
 input wire qc_abort,
 output wire qc_busy,
 output wire qc_fault,
 output wire [3:0] qc_phase,
 output wire qc_prepared_event,
 output wire [31:0] qc_prepare_acked,
 output wire [31:0] qc_cleanup_acked,
 input wire scan_valid,
 output wire scan_ready,
 input wire scan_permit,
 input wire [13:0] scan_frame,
 output wire scan_rsp_valid,
 input wire scan_rsp_ready,
 output wire [2:0] scan_status,
 output wire [13:0] scan_result_frame,
 output wire [26:0] scan_owner,
 output wire scan_published,
 input wire [31:0] snapshot_label_crc,
 output wire [31:0] lr_source_crc
);
reg[31:0]counter,sampled,word_index;
reg[31:0]ka_index,pw_index;
`ifdef KA_NO_STREAM
wire ka_stream=1'b0;
`else
wire ka_stream=(counter>=10&&ka_index<5);
`endif
`ifdef PW_NO_STREAM
wire pw_stream=1'b0;
`else
wire pw_stream=(counter>=10&&pw_index<5);
`endif
`ifdef KA_NO_TRANSFERS
wire ka_ready=1'b0;
`elsif KA_NO_STALLS
wire ka_ready=1'b1;
`elsif KA_READY_X
wire ka_ready=(counter>=12)?1'bx:cp_m_ready;
`else
wire ka_ready=cp_m_ready;
`endif
always @(posedge clk)begin
 if(k_cold_rst)begin ka_index<=0;pw_index<=0;end
 else begin
  if(ka_stream&&ka_ready)ka_index<=ka_index+1;
  if(pw_stream&&p_m_wready)pw_index<=pw_index+1;
 end
end
reg ka_edge_fault=0,pw_edge_fault=0;
always @(negedge clk)begin if(ka_stream&&ka_ready)begin #4.999;ka_edge_fault=1;end else ka_edge_fault<=0;end
always @(negedge clk)begin if(pw_stream&&p_m_wready)begin #4.999;pw_edge_fault=1;end else pw_edge_fault<=0;end
always @(posedge clk)begin ka_edge_fault<=0;pw_edge_fault<=0;end

`ifdef NO_STREAM
wire stream_valid=1'b0;
`else
wire stream_valid=(counter>=10&&word_index<5);
`endif
always @(posedge clk)begin
 if(k_cold_rst)begin counter<=0;sampled<=0;word_index<=0;end
 else begin counter<=counter+1;sampled<=qc_cp_s_data;
  if(stream_valid&&cp_m_ready)word_index<=word_index+1;
 end
end
reg edge_fault=0;
always @(negedge clk)begin if(stream_valid&&cp_m_ready)begin #4.999;edge_fault=1;end else edge_fault<=0;end
always @(posedge clk)edge_fault<=1'b0;
assign baseline_req_valid={1{counter}};
assign baseline_req_node={1{counter}};
assign baseline_req_epoch={2{counter}};
assign baseline_rsp_ready={1{counter}};
assign wm_owned={1{counter}};
assign wm_fault={1{counter}};
assign wm_joined={1{counter}};
assign wm_receipts={1{counter}};
assign ap_ready={1{counter}};
assign ap_rsp_valid={1{counter}};
assign ap_rsp_design={2{counter}};
assign ap_rsp_generation={2{counter}};
assign ap_rsp_checkpoint={1{counter}};
assign ap_rsp_cookie={1{counter}};
assign ap_refs={1{counter}};
assign ap_occ={1{counter}};
assign ap_status={1{counter}};
assign jp_start_ready={1{counter}};
assign jp_commit_ready={1{counter}};
assign jp_cancel_ready={1{counter}};
assign jp_owned={1{counter}};
assign jp_done={1{counter}};
assign jp_result={1{counter}};
assign jp_ready={1{counter}};
assign jp_reply={1{counter}};
assign jp_status={1{counter}};
assign boot_cfg_ready={1{counter}};
`ifdef OTHER_FLIP
assign boot_pending=(counter>=12)?~counter[0]:counter[0];
`elsif OTHER_X
assign boot_pending=(counter>=12)?1'bx:counter[0];
`elsif OTHER_Z
assign boot_pending=(counter>=12)?1'bz:counter[0];
`else
assign boot_pending=counter[0];
`endif
assign boot_rsp_valid={1{counter}};
assign boot_status='x;
assign boot_verify_ready={1{counter}};
assign boot_verified_count='z;
assign boot_verify_status={1{counter}};
assign boot_receipts={1{counter}};
assign boot_config_receipts={1{counter}};
assign qc_cp_ready={1{counter}};
assign qc_cp_busy={1{counter}};
assign qc_cp_rsp_valid={1{counter}};
assign qc_cp_s_ready={1{counter}};
assign qc_cp_m_valid={1{counter}};
assign qc_cp_m_last={1{counter}};
assign qc_restore_pending={1{counter}};
assign qc_cp_crc=sampled;
assign qc_cp_m_index={1{counter}};
assign qc_cp_m_data={1{counter}};
assign qc_cp_status={1{counter}};
assign as_cfg_ready={1{counter}};
assign as_configured={1{counter}};
assign as_bound_design={2{counter}};
assign as_bound_generation={2{counter}};
assign as_bound_checkpoint={1{counter}};
assign as_m_araddr={2{counter}};
assign as_m_arlen={1{counter}};
assign as_m_arsize={1{counter}};
assign as_m_arburst={1{counter}};
assign as_m_arid={1{counter}};
assign as_m_arvalid={1{counter}};
assign as_m_rready={1{counter}};
assign as_m_awaddr={2{counter}};
assign as_m_awlen={1{counter}};
assign as_m_awsize={1{counter}};
assign as_m_awburst={1{counter}};
assign as_m_awid={1{counter}};
assign as_m_awvalid={1{counter}};
assign as_m_wdata={16{counter}};
assign as_m_wstrb={2{counter}};
assign as_m_wlast={1{counter}};
assign as_m_wvalid={1{counter}};
assign as_m_bready={1{counter}};
assign as_cfg_rsp_valid={1{counter}};
assign as_cfg_status={1{counter}};
assign as_busy={1{counter}};
assign as_fault={1{counter}};
assign as_drained={1{counter}};
assign as_retired={1{counter}};
assign as_rsp_generation={2{counter}};
assign cp_ready={1{counter}};
assign cp_busy={1{counter}};
assign cp_rsp_valid={1{counter}};
assign cp_status={1{counter}};
assign cp_crc={1{counter}};
assign cp_s_ready={1{counter}};
`ifdef VALID_X_BOTH
assign cp_m_valid=(counter>=12)?1'bx:stream_valid;
`elsif VALID_Z_BOTH
assign cp_m_valid=(counter>=12)?1'bz:stream_valid;
`elsif IDLE_VALID_Z_BOTH
assign cp_m_valid=(counter==1)?1'bz:stream_valid;
`elsif IDLE_VALID_X_BOTH
assign cp_m_valid=(counter==1)?1'bx:stream_valid;
`elsif VALID_DROP
assign cp_m_valid=(stream_valid&&word_index!=2);
`else
assign cp_m_valid=stream_valid;
`endif
`ifdef CP_META_X_BOTH
assign cp_m_index=stream_valid?'x:word_index;
`elsif CP_META_Z_BOTH
assign cp_m_index=stream_valid?'z:word_index;
`elsif META_FLIP
assign cp_m_index=(word_index^((stream_valid&&word_index==2)?32'h1:32'h0));
`else
assign cp_m_index=word_index;
`endif
`ifdef DATA_X_BOTH
assign cp_m_data=stream_valid?32'hxxxxxxxx:32'h00000000;
`elsif DATA_Z_BOTH
assign cp_m_data=stream_valid?32'hzzzzzzzz:32'h00000000;
`elsif DATA_FLIP_STALL
assign cp_m_data=stream_valid?((32'hd00d0000+word_index)^(!cp_m_ready?32'h1:32'h0)):32'h00000000;
`elsif DATA_FLIP_ACTIVE
assign cp_m_data=stream_valid?((32'hd00d0000+word_index)^((word_index==2)?32'h1:32'h0)):32'h00000000;
`elsif EDGE_ONLY_FLIP
assign cp_m_data=stream_valid?((32'hd00d0000+word_index)^(edge_fault?32'h1:32'h0)):32'h00000000;
`else
assign cp_m_data=stream_valid?(32'hd00d0000+word_index):32'h00000000;
`endif
assign cp_m_last=(word_index==4);
assign pc_route_retired={1{counter}};
assign pc_acquire_ready={1{counter}};
assign pc_owned={1{counter}};
assign pc_release_ready={1{counter}};
assign busy={1{counter}};
assign cc_busy={1{counter}};
assign cc_fault={1{counter}};
assign cf_fault={1{counter}};
assign cost_lease={1{counter}};
assign cs_busy={1{counter}};
assign cs_configured={1{counter}};
assign cs_design_id={2{counter}};
assign cs_editing={1{counter}};
assign cs_fault={1{counter}};
assign cs_m_araddr={2{counter}};
assign cs_m_arburst={1{counter}};
assign cs_m_arid={1{counter}};
assign cs_m_arlen={1{counter}};
assign cs_m_arsize={1{counter}};
assign cs_m_arvalid={1{counter}};
assign cs_m_awaddr={2{counter}};
assign cs_m_awburst={1{counter}};
assign cs_m_awid={1{counter}};
assign cs_m_awlen={1{counter}};
assign cs_m_awsize={1{counter}};
assign cs_m_awvalid={1{counter}};
assign cs_m_bready={1{counter}};
assign cs_m_rready={1{counter}};
assign cs_m_wdata={16{counter}};
assign cs_m_wlast={1{counter}};
assign cs_m_wstrb={2{counter}};
assign cs_m_wvalid={1{counter}};
assign cs_published_version={1{counter}};
assign cs_ready_for_query={1{counter}};
assign d_configured={1{counter}};
assign d_m_araddr={2{counter}};
assign d_m_arburst={1{counter}};
assign d_m_arid={1{counter}};
assign d_m_arlen={1{counter}};
assign d_m_arsize={1{counter}};
assign d_m_arvalid={1{counter}};
assign d_m_awaddr={2{counter}};
assign d_m_awburst={1{counter}};
assign d_m_awid={1{counter}};
assign d_m_awlen={1{counter}};
assign d_m_awsize={1{counter}};
assign d_m_awvalid={1{counter}};
assign d_m_bready={1{counter}};
assign d_m_rready={1{counter}};
assign d_m_wdata={16{counter}};
assign d_m_wlast={1{counter}};
assign d_m_wstrb={2{counter}};
assign d_m_wvalid={1{counter}};
assign f_all_drained={1{counter}};
assign f_backend_idle={1{counter}};
assign f_fault={1{counter}};
assign f_normal_retired={1{counter}};
assign f_phase={1{counter}};
assign f_recovery_owned={1{counter}};
assign f_sr={1{counter}};
assign f_srp={128{counter}};
assign f_srv={1{counter}};
assign fault={1{counter}};
assign g_configured={1{counter}};
assign g_m_araddr={2{counter}};
assign g_m_arburst={1{counter}};
assign g_m_arid={1{counter}};
assign g_m_arlen={1{counter}};
assign g_m_arsize={1{counter}};
assign g_m_arvalid={1{counter}};
assign g_m_rready={1{counter}};
assign k_a_checkpoint=32'd17;
`ifdef KA_META_FLIP
assign k_a_cookie=((32'h11110000+ka_index)^((ka_stream&&ka_index==2)?32'h1:32'h0));
`elsif KA_META_X_BOTH
assign k_a_cookie=ka_stream?'x:(32'h11110000+ka_index);
`elsif KA_META_Z_BOTH
assign k_a_cookie=ka_stream?'z:(32'h11110000+ka_index);
`else
assign k_a_cookie=(32'h11110000+ka_index);
`endif
assign k_a_design=64'h1234;
`ifdef KA_NET_ONLY_FLIP
assign k_a_net=ka_stream?((32'hb0000000+ka_index)^((ka_index==2)?32'h1:32'h0)):'0;
`else
`ifdef KA_DATA_X_BOTH
assign k_a_net=ka_stream?'x:'0;
`elsif KA_DATA_Z_BOTH
assign k_a_net=ka_stream?'z:'0;
`elsif KA_DATA_FLIP_STALL
assign k_a_net=ka_stream?((32'hb0000000+ka_index)^(!ka_ready?32'h1:32'h0)):'0;
`elsif KA_DATA_FLIP_ACTIVE
assign k_a_net=ka_stream?((32'hb0000000+ka_index)^((ka_index==2)?32'h1:32'h0)):'0;
`elsif KA_EDGE_ONLY_FLIP
assign k_a_net=ka_stream?((32'hb0000000+ka_index)^(ka_edge_fault?32'h1:32'h0)):'0;
`else
assign k_a_net=ka_stream?(32'hb0000000+ka_index):'0;
`endif
`endif
`ifdef KA_NODE_ONLY_FLIP
assign k_a_node=ka_stream?((32'ha0000000+ka_index)^((ka_index==2)?32'h1:32'h0)):'0;
`else
`ifdef KA_DATA_X_BOTH
assign k_a_node=ka_stream?'x:'0;
`elsif KA_DATA_Z_BOTH
assign k_a_node=ka_stream?'z:'0;
`elsif KA_DATA_FLIP_STALL
assign k_a_node=ka_stream?((32'ha0000000+ka_index)^(!ka_ready?32'h1:32'h0)):'0;
`elsif KA_DATA_FLIP_ACTIVE
assign k_a_node=ka_stream?((32'ha0000000+ka_index)^((ka_index==2)?32'h1:32'h0)):'0;
`elsif KA_EDGE_ONLY_FLIP
assign k_a_node=ka_stream?((32'ha0000000+ka_index)^(ka_edge_fault?32'h1:32'h0)):'0;
`else
assign k_a_node=ka_stream?(32'ha0000000+ka_index):'0;
`endif
`endif
assign k_a_occ={1{counter}};
assign k_a_ready=ka_ready;
assign k_a_refs={1{counter}};
assign k_a_rsp_checkpoint={1{counter}};
assign k_a_rsp_cookie={1{counter}};
assign k_a_rsp_design={2{counter}};
assign k_a_rsp_ready={1{counter}};
assign k_a_rsp_valid={1{counter}};
assign k_a_status={1{counter}};
`ifdef KA_VALID_X_BOTH
assign k_a_valid=(counter>=12)?1'bx:ka_stream;
`elsif KA_VALID_Z_BOTH
assign k_a_valid=(counter>=12)?1'bz:ka_stream;
`elsif KA_IDLE_VALID_X_BOTH
assign k_a_valid=(counter==1)?1'bx:ka_stream;
`elsif KA_IDLE_VALID_Z_BOTH
assign k_a_valid=(counter==1)?1'bz:ka_stream;
`elsif KA_VALID_DROP
assign k_a_valid=(ka_stream&&ka_index!=2);
`else
assign k_a_valid=ka_stream;
`endif
assign k_busy={1{counter}};
assign k_corrected={1{counter}};
assign k_count={1{counter}};
assign k_fault={1{counter}};
assign k_full={1{counter}};
assign k_permit={1{counter}};
assign k_rec_ready={1{counter}};
assign k_rsp_cookie={1{counter}};
assign k_rsp_status={1{counter}};
assign k_rsp_valid={1{counter}};
assign k_saved_checkpoint={1{counter}};
assign k_saved_design={2{counter}};
assign k_target_reset={1{counter}};
assign lr_fault={1{counter}};
assign lr_rsp_status={1{counter}};
assign lr_s_ready={1{counter}};
assign lr_verified={1{counter}};
assign lr_written={1{counter}};
assign operation_pending={1{counter}};
assign out_action={1{counter}};
assign out_attrs={8{counter}};
assign out_bits={1{counter}};
assign out_commit_acked={1{counter}};
assign out_commit_payload={5{counter}};
assign out_commit_status={1{counter}};
assign out_commit_valid={1{counter}};
assign out_config={14{counter}};
assign out_connection={1{counter}};
assign out_cookie={1{counter}};
assign out_cost_geometry={13{counter}};
assign out_cost_geometry_result={4{counter}};
assign out_cost_packet={23{counter}};
assign out_cost_status={1{counter}};
assign out_cost_valid={1{counter}};
assign out_cost_words={5{counter}};
assign out_node={1{counter}};
assign out_offer_before={1{counter}};
assign out_offer_key={1{counter}};
assign out_offer_node={1{counter}};
assign out_offer_size={1{counter}};
assign out_offer_status={1{counter}};
assign out_offer_valid={1{counter}};
assign out_params={16{counter}};
assign out_params_valid={1{counter}};
assign out_position={1{counter}};
assign out_post_attrs={8{counter}};
assign out_post_distance={1{counter}};
assign out_post_prev_read={1{counter}};
assign out_post_status={1{counter}};
assign out_post_upstream={1{counter}};
assign out_post_valid={1{counter}};
assign out_post_x={1{counter}};
assign out_post_y={1{counter}};
assign out_prep_count={1{counter}};
assign out_prep_history={1{counter}};
assign out_prep_net_data={4{counter}};
assign out_prep_occupancy={1{counter}};
assign out_prep_price_index={1{counter}};
assign out_prep_price_value={1{counter}};
assign out_prep_status={1{counter}};
assign out_prep_valid={1{counter}};
assign out_profile_revision={1{counter}};
assign out_sequence={1{counter}};
assign out_services={1{counter}};
assign out_steps={1{counter}};
assign out_valid={1{counter}};
assign owner_configured={1{counter}};
assign owner_m_araddr={2{counter}};
assign owner_m_arburst={1{counter}};
assign owner_m_arid={1{counter}};
assign owner_m_arlen={1{counter}};
assign owner_m_arsize={1{counter}};
assign owner_m_arvalid={1{counter}};
assign owner_m_awaddr={2{counter}};
assign owner_m_awburst={1{counter}};
assign owner_m_awid={1{counter}};
assign owner_m_awlen={1{counter}};
assign owner_m_awsize={1{counter}};
assign owner_m_awvalid={1{counter}};
assign owner_m_bready={1{counter}};
assign owner_m_rready={1{counter}};
assign owner_m_wdata={16{counter}};
assign owner_m_wlast={1{counter}};
assign owner_m_wstrb={2{counter}};
assign owner_m_wvalid={1{counter}};
assign p_active={1{counter}};
assign p_active_price={1{counter}};
assign p_active_query={1{counter}};
assign p_m_araddr={1{counter}};
assign p_m_arburst={1{counter}};
assign p_m_arid={1{counter}};
assign p_m_arlen={1{counter}};
assign p_m_arsize={1{counter}};
assign p_m_arvalid={1{counter}};
assign p_m_awaddr={1{counter}};
assign p_m_awburst={1{counter}};
assign p_m_awid={1{counter}};
assign p_m_awlen={1{counter}};
assign p_m_awsize={1{counter}};
assign p_m_awvalid={1{counter}};
assign p_m_bready={1{counter}};
assign p_m_rready={1{counter}};
`ifdef PW_DATA_X_BOTH
assign p_m_wdata=pw_stream?'x:'0;
`elsif PW_DATA_Z_BOTH
assign p_m_wdata=pw_stream?'z:'0;
`elsif PW_DATA_FLIP_STALL
assign p_m_wdata=pw_stream?((512'hc0000000+pw_index)^(!p_m_wready?512'h1:512'h0)):'0;
`elsif PW_DATA_FLIP_ACTIVE
assign p_m_wdata=pw_stream?((512'hc0000000+pw_index)^((pw_index==2)?512'h1:512'h0)):'0;
`elsif PW_EDGE_ONLY_FLIP
assign p_m_wdata=pw_stream?((512'hc0000000+pw_index)^(pw_edge_fault?512'h1:512'h0)):'0;
`else
assign p_m_wdata=pw_stream?(512'hc0000000+pw_index):'0;
`endif
assign p_m_wlast=(pw_index==4);
`ifdef PW_META_FLIP
assign p_m_wstrb=(64'hffffffffffffffff^((pw_stream&&pw_index==2)?64'h1:64'h0));
`elsif PW_META_X_BOTH
assign p_m_wstrb=pw_stream?'x:64'hffffffffffffffff;
`elsif PW_META_Z_BOTH
assign p_m_wstrb=pw_stream?'z:64'hffffffffffffffff;
`else
assign p_m_wstrb=64'hffffffffffffffff;
`endif
`ifdef PW_VALID_X_BOTH
assign p_m_wvalid=(counter>=12)?1'bx:pw_stream;
`elsif PW_VALID_Z_BOTH
assign p_m_wvalid=(counter>=12)?1'bz:pw_stream;
`elsif PW_IDLE_VALID_X_BOTH
assign p_m_wvalid=(counter==1)?1'bx:pw_stream;
`elsif PW_IDLE_VALID_Z_BOTH
assign p_m_wvalid=(counter==1)?1'bz:pw_stream;
`elsif PW_VALID_DROP
assign p_m_wvalid=(pw_stream&&pw_index!=2);
`else
assign p_m_wvalid=pw_stream;
`endif
assign q_busy={1{counter}};
assign q_configured={1{counter}};
assign q_fault={1{counter}};
assign q_m_araddr={2{counter}};
assign q_m_arburst={1{counter}};
assign q_m_arid={1{counter}};
assign q_m_arlen={1{counter}};
assign q_m_arsize={1{counter}};
assign q_m_arvalid={1{counter}};
assign q_m_rready={1{counter}};
assign query_ready={1{counter}};
assign query_version={1{counter}};
assign rc_block={1{counter}};
assign rc_busy={1{counter}};
assign rc_fault={1{counter}};
assign rc_req_ready={1{counter}};
assign rc_rsp_acked={1{counter}};
assign rc_rsp_cookie={1{counter}};
assign rc_rsp_nodes={1{counter}};
assign rc_rsp_status={1{counter}};
assign rc_rsp_valid={1{counter}};
assign rc_slots={1{counter}};
assign rst={1{counter}};
assign t_configured={1{counter}};
assign t_m_araddr={2{counter}};
assign t_m_arburst={1{counter}};
assign t_m_arid={1{counter}};
assign t_m_arlen={1{counter}};
assign t_m_arsize={1{counter}};
assign t_m_arvalid={1{counter}};
assign t_m_rready={1{counter}};
assign ss_start_ready={1{counter}};
assign ss_rsp_valid={1{counter}};
assign ss_rsp_status={1{counter}};
assign ss_rsp_cookie={1{counter}};
assign ss_polls={1{counter}};
assign ss_expands={1{counter}};
assign ss_candidates={1{counter}};
assign ss_result_node={1{counter}};
assign ss_result_key={1{counter}};
assign ss_busy={1{counter}};
assign ss_fault={1{counter}};
assign ss_phase={1{counter}};
assign ss_poll_event={1{counter}};
assign ss_poll_node={1{counter}};
assign ss_poll_key={1{counter}};
assign ss_poll_size={1{counter}};
assign qc_cmd_ready={1{counter}};
assign qc_rsp_valid={1{counter}};
assign qc_rsp_status={1{counter}};
assign qc_rsp_detail={1{counter}};
assign qc_rsp_cookie={1{counter}};
assign qc_rsp_nodes={1{counter}};
assign qc_rsp_acked={1{counter}};
assign qc_rsp_committed={1{counter}};
assign qc_busy={1{counter}};
assign qc_fault={1{counter}};
assign qc_phase={1{counter}};
assign qc_prepared_event={1{counter}};
assign qc_prepare_acked={1{counter}};
assign qc_cleanup_acked={1{counter}};
assign scan_ready={1{counter}};
assign scan_rsp_valid={1{counter}};
assign scan_status={1{counter}};
assign scan_result_frame={1{counter}};
assign scan_owner={1{counter}};
assign scan_published={1{counter}};
assign lr_source_crc={1{counter}};
endmodule
module tb_candidate_offer;
reg clk=0;always #5 clk=~clk;
reg cold=1;reg[31:0]stream=0;reg ready=0;
`ifdef CP_READY_X
reg cp_ready_fault=0;initial begin #170;cp_ready_fault=1;end
wire c_ready=cp_ready_fault?1'bx:ready;
`else
wire c_ready=ready;
`endif
`ifdef PW_NO_TRANSFERS
wire p_ready=1'b0;
`elsif PW_NO_STALLS
wire p_ready=1'b1;
`elsif PW_READY_X
reg pw_ready_fault=0;initial begin #170;pw_ready_fault=1;end
wire p_ready=pw_ready_fault?1'bx:ready;
`else
wire p_ready=ready;
`endif
`ifdef SHORT_RESET
initial begin #20;cold=0;end
`else
initial begin #50;cold=0;end
`endif
always @(posedge clk)if(cold)stream<=0;else stream<=stream+1;
`ifdef READY_NBA
always @(posedge clk)if($time>=205)ready<=1;
`elsif NO_TRANSFERS
initial ready=0;
`elsif NO_STALLS
initial ready=1;
`else
initial begin #200;ready=1;end
`endif
protocol_rtl system (
 .baseline_retired('0),
 .restore_seed_enable('0),
 .baseline_permit('0),
 .baseline_epoch('0),
 .baseline_req_ready('0),
 .baseline_rsp_valid('0),
 .baseline_rsp_status('0),
 .baseline_rsp_node('0),
 .baseline_rsp_epoch('0),
 .baseline_rsp_payload('0),
 .wm_enable('0),
 .wm_source_version('0),
 .wm_source_query('0),
 .wm_source_price('0),
 .wm_path_crc('0),
 .wm_query_crc('0),
 .ap_valid('0),
 .ap_rsp_ready('0),
 .ap_design('0),
 .ap_generation('0),
 .ap_checkpoint('0),
 .ap_node('0),
 .ap_net('0),
 .ap_cookie('0),
 .jp_start('0),
 .jp_commit('0),
 .jp_cancel('0),
 .jp_done_ready('0),
 .jp_manifest_ready('0),
 .jp_generation('0),
 .jp_design('0),
 .jp_checkpoint('0),
 .jp_version('0),
 .jp_query('0),
 .jp_price('0),
 .jp_load('0),
 .jp_ack('0),
 .jp_authority_stage('0),
 .boot_required('0),
 .boot_cfg_valid('0),
 .boot_design('0),
 .boot_generation('0),
 .boot_checkpoint('0),
 .boot_version('0),
 .boot_nodes('0),
 .boot_label_count('0),
 .boot_label_crc('0),
 .boot_path_crc('0),
 .boot_query_crc('0),
 .boot_query('0),
 .boot_slots('0),
 .boot_price('0),
 .boot_payload('0),
 .boot_rsp_ready('0),
 .boot_verify_valid('0),
 .qc_cp_generation('0),
 .qc_cp_valid('0),
 .qc_cp_restore('0),
 .qc_cp_rsp_ready('0),
 .qc_cp_s_valid('0),
 .qc_cp_s_last('0),
 .qc_cp_m_ready('0),
 .qc_cp_test_reset('0),
 .qc_cp_expected_crc('0),
 .qc_cp_s_index('0),
 .qc_cp_s_data(stream),
 .as_cfg_valid('0),
 .as_cfg_design('0),
 .as_cfg_generation('0),
 .as_cfg_primary('0),
 .as_cfg_pool('0),
 .as_cfg_allocator('0),
 .as_cfg_checkpoint('0),
 .as_cfg_nodes('0),
 .as_cfg_nets('0),
 .as_cfg_capacity('0),
 .as_m_arready('0),
 .as_m_rdata('0),
 .as_m_rid('0),
 .as_m_rresp('0),
 .as_m_rlast('0),
 .as_m_rvalid('0),
 .as_m_awready('0),
 .as_m_wready('0),
 .as_m_bid('0),
 .as_m_bresp('0),
 .as_m_bvalid('0),
 .as_cfg_rsp_ready('0),
 .cp_valid('0),
 .cp_restore('0),
 .cp_rsp_ready('0),
 .cp_design('0),
 .cp_nodes('0),
 .cp_nets('0),
 .cp_expected_crc('0),
 .cp_s_valid('0),
 .cp_s_index('0),
 .cp_s_data('0),
 .cp_s_last('0),
 .cp_m_ready(c_ready),
 .cp_test_reset('0),
 .pc_acquire_valid('0),
 .pc_release_valid('0),
 .abort('0),
 .clk(clk),
 .cs_m_arready('0),
 .cs_m_awready('0),
 .cs_m_bid('0),
 .cs_m_bresp('0),
 .cs_m_bvalid('0),
 .cs_m_rdata('0),
 .cs_m_rid('0),
 .cs_m_rlast('0),
 .cs_m_rresp('0),
 .cs_m_rvalid('0),
 .cs_m_wready('0),
 .d_m_arready('0),
 .d_m_awready('0),
 .d_m_bid('0),
 .d_m_bresp('0),
 .d_m_bvalid('0),
 .d_m_rdata('0),
 .d_m_rid('0),
 .d_m_rlast('0),
 .d_m_rresp('0),
 .d_m_rvalid('0),
 .d_m_wready('0),
 .design_id('0),
 .f_route_payload('0),
 .f_sp('0),
 .f_srr('0),
 .f_sv('0),
 .g_m_arready('0),
 .g_m_rdata('0),
 .g_m_rid('0),
 .g_m_rlast('0),
 .g_m_rresp('0),
 .g_m_rvalid('0),
 .k_cold_rst(cold),
 .k_rec_valid('0),
 .k_rsp_ready('0),
 .lr_s_cookie('0),
 .lr_s_last('0),
 .lr_s_node('0),
 .lr_s_payload('0),
 .lr_s_valid('0),
 .out_ready('0),
 .owner_m_arready('0),
 .owner_m_awready('0),
 .owner_m_bid('0),
 .owner_m_bresp('0),
 .owner_m_bvalid('0),
 .owner_m_rdata('0),
 .owner_m_rid('0),
 .owner_m_rlast('0),
 .owner_m_rresp('0),
 .owner_m_rvalid('0),
 .owner_m_wready('0),
 .p_m_arready('0),
 .p_m_awready('0),
 .p_m_bid('0),
 .p_m_bresp('0),
 .p_m_bvalid('0),
 .p_m_rdata('0),
 .p_m_rid('0),
 .p_m_rlast('0),
 .p_m_rresp('0),
 .p_m_rvalid('0),
 .p_m_wready(p_ready),
 .q_m_arready('0),
 .q_m_rdata('0),
 .q_m_rid('0),
 .q_m_rlast('0),
 .q_m_rresp('0),
 .q_m_rvalid('0),
 .rc_req_valid('0),
 .rc_rsp_ready('0),
 .recover_checkpoint('0),
 .recover_cookie('0),
 .recover_design('0),
 .recover_price('0),
 .recover_query('0),
 .recover_version('0),
 .snapshot_checkpoint('0),
 .snapshot_cookie('0),
 .snapshot_count('0),
 .snapshot_design('0),
 .snapshot_nodes('0),
 .snapshot_probe('0),
 .t_m_arready('0),
 .t_m_rdata('0),
 .t_m_rid('0),
 .t_m_rlast('0),
 .t_m_rresp('0),
 .t_m_rvalid('0),
 .test_route_abort('0),
 .test_route_version_flip('0),
 .qc_cmd_valid('0),
 .qc_cmd_slot('0),
 .qc_cmd_cookie('0),
 .qc_cmd_route_cookie('0),
 .qc_cmd_source('0),
 .qc_cmd_key('0),
 .qc_cmd_nodes('0),
 .qc_cmd_max_polls('0),
 .qc_cmd_poll_cookie('0),
 .qc_cmd_design('0),
 .qc_cmd_query('0),
 .qc_cmd_price('0),
 .qc_cmd_expand('0),
 .qc_rsp_ready('0),
 .qc_abort('0),
 .scan_valid('0),
 .scan_permit('0),
 .scan_frame('0),
 .scan_rsp_ready('0),
 .snapshot_label_crc('0)
);
initial begin #1000;stage_static_cp_shadow.finish_and_check;$finish;end
endmodule
