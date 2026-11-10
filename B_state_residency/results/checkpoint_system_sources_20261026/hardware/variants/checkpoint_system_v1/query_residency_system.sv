`timescale 1ns/1ps
module query_residency_system #(parameter integer SLOTS=32,FRAMES=16384,INDEX_BITS=14,HASH_BITS=15,ENABLE_TEST_INJECTION=0)(
input wire jp_start,
output wire jp_start_ready,
input wire jp_commit,
output wire jp_commit_ready,
input wire jp_cancel,
output wire jp_cancel_ready,
output wire jp_owned,
output wire jp_done,
input wire jp_done_ready,
output wire[1:0] jp_result,
input wire jp_manifest_ready,
input wire[63:0] jp_generation,
input wire[63:0] jp_design,
input wire[31:0] jp_checkpoint,
input wire[31:0] jp_version,
input wire[1:0] jp_query,
input wire[3:0] jp_price,
input wire[1:0] jp_load,
input wire[1:0] jp_ack,
output wire[1:0] jp_ready,
output wire[1:0] jp_reply,
output wire[1:0] jp_status,
input wire jp_authority_stage,
input wire boot_required,boot_cfg_valid,output wire boot_cfg_ready,
input wire[63:0]boot_design,boot_generation,
input wire[31:0]boot_checkpoint,boot_version,boot_nodes,boot_label_count,boot_label_crc,boot_path_crc,boot_query_crc,
input wire[1:0]boot_query,boot_slots,input wire[3:0]boot_price,input wire[2303:0]boot_payload,
output wire boot_pending,boot_rsp_valid,input wire boot_rsp_ready,output wire[3:0]boot_status,
input wire boot_verify_valid,output wire boot_verify_ready,output wire[31:0]boot_verified_count,output wire[3:0]boot_verify_status,
output wire[4:0]boot_receipts,output wire[7:0]boot_config_receipts,
input wire[63:0]qc_cp_generation,
input wire qc_cp_valid,qc_cp_restore,qc_cp_rsp_ready,qc_cp_s_valid,qc_cp_s_last,qc_cp_m_ready,qc_cp_test_reset,
output wire qc_cp_ready,qc_cp_busy,qc_cp_rsp_valid,qc_cp_s_ready,qc_cp_m_valid,qc_cp_m_last,qc_restore_pending,
input wire[31:0]qc_cp_expected_crc,qc_cp_s_index,qc_cp_s_data,
output wire[31:0]qc_cp_crc,qc_cp_m_index,qc_cp_m_data,output wire[3:0]qc_cp_status,
 input wire as_cfg_valid,output wire as_cfg_ready,input wire[63:0]as_cfg_design,as_cfg_generation,as_cfg_primary,as_cfg_pool,as_cfg_allocator,
 input wire[31:0]as_cfg_checkpoint,as_cfg_nodes,as_cfg_nets,as_cfg_capacity,
 output wire as_configured,output wire[63:0]as_bound_design,as_bound_generation,output wire[31:0]as_bound_checkpoint,
 output wire[63:0]as_m_araddr,output wire[7:0]as_m_arlen,output wire[2:0]as_m_arsize,output wire[1:0]as_m_arburst,output wire[3:0]as_m_arid,
 output wire as_m_arvalid,input wire as_m_arready,input wire[511:0]as_m_rdata,input wire[3:0]as_m_rid,input wire[1:0]as_m_rresp,input wire as_m_rlast,as_m_rvalid,output wire as_m_rready,
 output wire[63:0]as_m_awaddr,output wire[7:0]as_m_awlen,output wire[2:0]as_m_awsize,output wire[1:0]as_m_awburst,output wire[3:0]as_m_awid,
 output wire as_m_awvalid,input wire as_m_awready,output wire[511:0]as_m_wdata,output wire[63:0]as_m_wstrb,output wire as_m_wlast,as_m_wvalid,input wire as_m_wready,
 input wire[3:0]as_m_bid,input wire[1:0]as_m_bresp,input wire as_m_bvalid,output wire as_m_bready,
output wire as_cfg_rsp_valid,input wire as_cfg_rsp_ready,output wire[2:0]as_cfg_status,
output wire as_busy,as_fault,as_drained,as_retired,output wire[63:0]as_rsp_generation,
input wire cp_valid,cp_restore,
output wire cp_ready,cp_busy,cp_rsp_valid,input wire cp_rsp_ready,
output wire[3:0]cp_status,output wire[31:0]cp_crc,
input wire[63:0]cp_design,input wire[31:0]cp_nodes,cp_nets,cp_expected_crc,
input wire cp_s_valid,output wire cp_s_ready,input wire[31:0]cp_s_index,cp_s_data,input wire cp_s_last,
output wire cp_m_valid,input wire cp_m_ready,output wire[31:0]cp_m_index,cp_m_data,output wire cp_m_last,
input wire cp_test_reset,output wire pc_route_retired,
input wire pc_acquire_valid,output wire pc_acquire_ready,output wire pc_owned,
input wire pc_release_valid,output wire pc_release_ready,
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
output wire [1:0] rc_slots,
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
input wire qc_cmd_slot,
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
output wire [31:0] qc_cleanup_acked
);
wire jp_permit;
wire[1:0] jp_publish;
wire[1:0] jp_discard;
wire[1:0] jp_prepared;
wire[1:0] jp_pubready;
wire[1:0] jp_dropready;
wire[63:0] jp_kdesign;
wire[63:0] jp_cdesign;
wire[31:0] jp_kcp;
wire[31:0] jp_ccp;
wire[31:0] jp_kver;
wire[31:0] jp_cver;
wire[1:0] jp_kquery;
wire[3:0] jp_kprice;
wire[63:0] jp_skdesign;
wire[63:0] jp_scdesign;
wire[31:0] jp_skcp;
wire[31:0] jp_sccp;
wire[31:0] jp_skver;
wire[31:0] jp_scver;
wire[1:0] jp_skquery;
wire[3:0] jp_skprice;
wire jp_prepare,jp_core_start_ready;wire[2:0]jp_pv,jp_dv;wire jp_ap,jp_apr,jp_adr;wire[63:0]jp_ad,jp_ag;wire[31:0]jp_ac;
wire jp_start_open=!cp_valid&&!qc_cp_valid&&!as_cfg_valid&&f_sv==0&&!k_rec_valid&&!boot_pending;
assign jp_start_ready=jp_core_start_ready&&jp_start_open;
assign jp_publish=jp_pv[2:1];assign jp_discard=jp_dv[2:1];assign jp_permit=pc_owned&&jp_owned;
wire boot_admin_allowed,boot_done_held;wire pc_safe;wire qc_core_cp_ready,cp_inner_ready;reg qc_reset_held,qc_pending,qc_import_held;reg[63:0]qc_generation_held;
wire[63:0]qc_requested_generation=qc_cp_restore||qc_cp_generation==0?as_bound_generation:qc_cp_generation;
wire[63:0]qc_image_generation=qc_cp_busy?qc_generation_held:((!qc_cp_restore&&qc_requested_generation<as_bound_generation)?64'd0:qc_requested_generation);
assign qc_restore_pending=qc_pending;
assign qc_cp_ready=!boot_done_held&&!jp_owned&&pc_owned&&!cp_busy&&!qc_reset_held&&qc_core_cp_ready;
assign cp_ready=!boot_done_held&&!jp_owned&&!qc_cp_valid&&!qc_cp_busy&&!qc_reset_held&&cp_inner_ready;
always @(posedge clk)begin
 if(k_cold_rst)begin qc_generation_held<=0;qc_reset_held<=0;qc_pending<=0;qc_import_held<=0;end
 else begin
  qc_reset_held<=ENABLE_TEST_INJECTION&&qc_cp_test_reset&&pc_owned&&pc_safe&&!qc_busy&&!cp_busy&&!cp_valid&&!qc_cp_valid&&!qc_cp_busy;
  if(ENABLE_TEST_INJECTION&&qc_cp_test_reset&&pc_owned&&pc_safe&&!qc_busy&&!cp_busy&&!cp_valid&&!qc_cp_valid&&!qc_cp_busy)qc_pending<=1;
  if(qc_cp_valid&&qc_cp_ready)begin qc_generation_held<=qc_image_generation;qc_import_held<=qc_cp_restore;if(qc_cp_restore)qc_pending<=1;end
  if(qc_cp_rsp_valid&&qc_cp_rsp_ready)begin
   if(qc_import_held&&qc_cp_status==0)qc_pending<=0;
   qc_import_held<=0;
  end
 end
end

wire as_attempt_reset,as_rearm_ready,as_core_cfg_ready,as_core_cfg_valid,as_core_cfg_rearmed;
wire[2:0]as_core_cfg_status;
wire[3:0]as_core_status;reg as_cfg_lease;
wire as_initial_safe=!rst&&!k_cold_rst&&!abort&&!pc_owned&&!pc_acquire_valid&&!cp_valid&&!cp_test_reset&&!qc_busy&&!ss_busy&&!k_busy&&!f_recovery_owned&&f_normal_retired&&f_backend_idle&&f_all_drained&&f_sv==0&&!rc_req_valid&&!qc_cmd_valid&&!k_rec_valid;
assign as_cfg_ready=(!boot_pending||boot_admin_allowed)&&(as_initial_safe||(jp_prepare&&jp_authority_stage))&&as_core_cfg_ready;
assign as_cfg_rsp_valid=as_core_cfg_valid&&!as_core_cfg_rearmed;
assign as_cfg_status=as_core_cfg_status;
assign as_retired=!as_busy&&!as_core_cfg_valid;
assign k_a_status=as_rsp_generation==as_bound_generation?as_core_status:4'd14;
always @(posedge clk)begin
 if(k_cold_rst)as_cfg_lease<=0;
 else if((as_cfg_valid&&as_cfg_ready)||(as_attempt_reset&&as_rearm_ready))as_cfg_lease<=1;
 else if(as_core_cfg_valid&&(as_core_cfg_rearmed||as_cfg_rsp_ready))as_cfg_lease<=0;
end
checkpoint_authority_rotator authority(.cfg_stage(jp_authority_stage),.publish_valid(jp_pv[0]),.publish_permit(pc_owned&&jp_owned),.discard_valid(jp_dv[0]),.publish_ready(jp_apr),.discard_ready(jp_adr),.active_slot(),.staged_valid(jp_ap),.staged_design(jp_ad),.staged_generation(jp_ag),.staged_checkpoint(jp_ac),.clk(clk),.rst(k_cold_rst),.abort(1'b0),.cfg_permit(as_initial_safe||as_cfg_lease||as_attempt_reset||(pc_owned&&jp_owned)),
.cfg_valid((!boot_pending||boot_admin_allowed)&&as_cfg_valid&&(as_initial_safe||(jp_prepare&&jp_authority_stage))),.cfg_ready(as_core_cfg_ready),.cfg_design(as_cfg_design),.cfg_generation(as_cfg_generation),.cfg_primary(as_cfg_primary),.cfg_pool(as_cfg_pool),.cfg_allocator(as_cfg_allocator),.cfg_checkpoint(as_cfg_checkpoint),.cfg_nodes(as_cfg_nodes),.cfg_nets(as_cfg_nets),.cfg_capacity(as_cfg_capacity),
.rearm_valid(as_attempt_reset),.rearm_ready(as_rearm_ready),.cfg_rsp_valid(as_core_cfg_valid),.cfg_rsp_ready(as_core_cfg_rearmed||as_cfg_rsp_ready),.cfg_status(as_core_cfg_status),.cfg_rearmed(as_core_cfg_rearmed),.configured(as_configured),.bound_design(as_bound_design),.bound_generation(as_bound_generation),.bound_checkpoint(as_bound_checkpoint),
.req_valid(k_a_valid),.req_ready(k_a_ready),.req_design(k_a_design),.req_generation(as_bound_generation),.req_checkpoint(k_a_checkpoint),.req_node(k_a_node),.req_net(k_a_net),.req_cookie(k_a_cookie),.rsp_valid(k_a_rsp_valid),.rsp_ready(k_a_rsp_ready),.rsp_status(as_core_status),.rsp_design(k_a_rsp_design),.rsp_generation(as_rsp_generation),.rsp_checkpoint(k_a_rsp_checkpoint),.rsp_cookie(k_a_rsp_cookie),.rsp_refs(k_a_refs),.rsp_occupancy(k_a_occ),.busy(as_busy),.fault(as_fault),.drained(as_drained),
.m_araddr(as_m_araddr),.m_arlen(as_m_arlen),.m_arsize(as_m_arsize),.m_arburst(as_m_arburst),.m_arid(as_m_arid),.m_arvalid(as_m_arvalid),.m_arready(as_m_arready),.m_rdata(as_m_rdata),.m_rid(as_m_rid),.m_rresp(as_m_rresp),.m_rlast(as_m_rlast),.m_rvalid(as_m_rvalid),.m_rready(as_m_rready),.m_awaddr(as_m_awaddr),.m_awlen(as_m_awlen),.m_awsize(as_m_awsize),.m_awburst(as_m_awburst),.m_awid(as_m_awid),.m_awvalid(as_m_awvalid),.m_awready(as_m_awready),.m_wdata(as_m_wdata),.m_wstrb(as_m_wstrb),.m_wlast(as_m_wlast),.m_wvalid(as_m_wvalid),.m_wready(as_m_wready),.m_bid(as_m_bid),.m_bresp(as_m_bresp),.m_bvalid(as_m_bvalid),.m_bready(as_m_bready));
wire ss_abort;
wire ss_start_valid;
wire [31:0] ss_start_cookie;
wire [31:0] ss_start_source;
wire [31:0] ss_start_key;
wire [31:0] ss_start_nodes;
wire [31:0] ss_start_max_polls;
wire [31:0] ss_start_poll_cookie;
wire [63:0] ss_start_design;
wire [1:0] ss_start_query;
wire [3:0] ss_start_price;
wire [447:0] ss_start_expand;
wire ss_rsp_ready;
wire [15:0] b_f_sv;
wire [15:0] b_f_sr;
wire [38911:0] b_f_sp;
wire [15:0] b_f_srv;
wire [15:0] b_f_srr;
wire [4095:0] b_f_srp;
wire b_rc_req_valid;
wire b_rc_req_ready;
wire b_rc_rsp_valid;
wire b_rc_rsp_ready;
wire [191:0] b_f_route_payload;
wire b_k_rec_valid;
wire b_k_rec_ready;
wire c_service_valid;
wire c_service_ready;
wire [3:0] c_service_lane;
wire [447:0] c_service_payload;
wire c_service_rsp_valid;
wire c_service_rsp_ready;
wire [255:0] c_service_rsp_payload;
wire c_route_valid;
wire c_route_ready;
wire [191:0] c_route_payload;
wire c_route_rsp_valid;
wire c_route_rsp_ready;
// Acquire only with no previously offered normal request. Before acceptance,
// normal traffic proceeds unchanged; after it, no transaction can be retracted.
wire pc_quiet=!rst&&!k_cold_rst&&!abort&&p_active&&k_permit&&f_phase==0&&f_normal_retired&&f_backend_idle&&f_all_drained&&(!qc_busy||qc_cp_busy)&&!ss_busy&&!qc_fault&&!ss_fault&&!fault&&!rc_fault&&!k_fault&&!cf_fault&&!lr_fault&&!f_fault&&!k_busy&&!f_recovery_owned&&!as_cfg_lease&&!as_fault;

wire pc_retired=!rst&&!k_cold_rst&&f_normal_retired&&f_backend_idle&&f_all_drained&&!qc_busy&&!ss_busy&&!k_busy&&!f_recovery_owned&&(f_phase==0||f_phase==6);
checkpoint_lease_guard checkpoint_lease(.clk(clk),.rst(rst||k_cold_rst),.acquire_valid(pc_acquire_valid),.acquire_ready(pc_acquire_ready),.release_valid(pc_release_valid),.release_ready(pc_release_ready),.owned(pc_owned),.healthy(pc_quiet),.retired(pc_retired),.route_retired(pc_route_retired),.no_offers(f_sv==0&&!rc_req_valid&&!qc_cmd_valid&&!k_rec_valid),.command_busy(cp_busy||qc_cp_busy||qc_pending||(boot_pending&&pc_owned)||jp_owned||as_cfg_lease||as_busy||(|jp_reply)),.command_valid(cp_valid||qc_cp_valid),.test_reset(cp_test_reset||qc_cp_test_reset||qc_reset_held),.safe(pc_safe));
wire host_base=!qc_busy&&!qc_fault&&!pc_owned&&!as_cfg_lease;
wire host_open=host_base&&!boot_pending;
wire boot_admin_open=host_base&&boot_admin_allowed;
wire[15:0]host_mask={16{host_open}}|({16{boot_admin_open}}&16'hc17f);
// Accepted host requests retain a response route even if admission is canceled.
reg[15:0]host_reply_owned;
always @(posedge clk)begin
 if(rst||k_cold_rst)host_reply_owned<=0;
 else host_reply_owned<=(host_reply_owned|(f_sv&f_sr))&~(f_srv&f_srr);
end
wire[15:0]host_response_mask=host_mask|host_reply_owned;
assign f_sr=b_f_sr&host_mask;assign f_srv=b_f_srv&host_response_mask;assign f_srp=b_f_srp;
assign rc_req_ready=host_open&&b_rc_req_ready;assign b_rc_req_valid=qc_busy?c_route_valid:(host_open&&rc_req_valid);assign b_f_route_payload=qc_busy?c_route_payload:f_route_payload;assign rc_rsp_valid=host_open&&b_rc_rsp_valid;assign b_rc_rsp_ready=qc_busy?c_route_rsp_ready:(host_open&&rc_rsp_ready);
assign c_route_ready=qc_busy&&b_rc_req_ready;assign c_route_rsp_valid=qc_busy&&b_rc_rsp_valid;assign b_k_rec_valid=!boot_pending&&!qc_busy&&!pc_owned&&!as_cfg_lease&&k_rec_valid;assign k_rec_ready=!boot_pending&&!qc_busy&&!pc_owned&&!as_cfg_lease&&b_k_rec_ready;
assign c_service_ready=qc_busy&&(c_service_lane==8?b_f_sr[8]:b_f_sr[6]);assign c_service_rsp_valid=qc_busy&&(c_service_lane==8?b_f_srv[8]:b_f_srv[6]);assign c_service_rsp_payload=c_service_lane==8?b_f_srp[2048+:256]:b_f_srp[1536+:256];
generate for(genvar i=0;i<16;i=i+1)begin:host_lanes
 if(i==6||i==8)begin:owned_service
  assign b_f_sv[i]=qc_busy?(c_service_valid&&c_service_lane==i):(host_mask[i]&&f_sv[i]);
  assign b_f_sp[i*2432+:2432]=qc_busy?{1984'd0,c_service_payload}:f_sp[i*2432+:2432];
  assign b_f_srr[i]=qc_busy?(c_service_rsp_ready&&c_service_lane==i):(host_response_mask[i]&&f_srr[i]);
 end else begin:host_only
  assign b_f_sv[i]=host_mask[i]&&f_sv[i];assign b_f_sp[i*2432+:2432]=f_sp[i*2432+:2432];assign b_f_srr[i]=host_response_mask[i]&&f_srr[i];
 end
end endgenerate
search_residency_system #(.SLOTS(SLOTS),.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS),.ENABLE_TEST_INJECTION(ENABLE_TEST_INJECTION))inner(.jp_permit(jp_permit),.jp_publish(jp_publish),.jp_discard(jp_discard),.jp_load(jp_prepare?jp_load:2'd0),.jp_ack(jp_ack),.jp_design(jp_design),.jp_checkpoint(jp_checkpoint),.jp_version(jp_version),.jp_query(jp_query),.jp_price(jp_price),.jp_ready(jp_ready),.jp_reply(jp_reply),.jp_status(jp_status),.jp_prepared(jp_prepared),.jp_pubready(jp_pubready),.jp_dropready(jp_dropready),.jp_kdesign(jp_kdesign),.jp_cdesign(jp_cdesign),.jp_kcp(jp_kcp),.jp_ccp(jp_ccp),.jp_kver(jp_kver),.jp_cver(jp_cver),.jp_kquery(jp_kquery),.jp_kprice(jp_kprice),.jp_skdesign(jp_skdesign),.jp_scdesign(jp_scdesign),.jp_skcp(jp_skcp),.jp_sccp(jp_sccp),.jp_skver(jp_skver),.jp_scver(jp_scver),.jp_skquery(jp_skquery),.jp_skprice(jp_skprice),.as_drained(as_drained),.as_retired(as_retired),.as_fault(as_fault),.as_configured(as_configured),.as_bound_design(as_bound_design),.as_bound_generation(as_bound_generation),.as_bound_checkpoint(as_bound_checkpoint),.as_attempt_reset(as_attempt_reset),.cp_valid(!boot_done_held&&!jp_owned&&cp_valid&&pc_owned&&!qc_cp_valid&&!qc_cp_busy&&!qc_reset_held),.cp_restore(cp_restore),.cp_ready(cp_inner_ready),.cp_busy(cp_busy),.cp_rsp_valid(cp_rsp_valid),.cp_rsp_ready(cp_rsp_ready),.cp_status(cp_status),.cp_crc(cp_crc),.cp_design(cp_design),.cp_nodes(cp_nodes),.cp_nets(cp_nets),.cp_expected_crc(cp_expected_crc),.cp_s_valid(cp_s_valid),.cp_s_ready(cp_s_ready),.cp_s_index(cp_s_index),.cp_s_data(cp_s_data),.cp_s_last(cp_s_last),.cp_m_valid(cp_m_valid),.cp_m_ready(cp_m_ready),.cp_m_index(cp_m_index),.cp_m_data(cp_m_data),.cp_m_last(cp_m_last),.cp_test_reset(ENABLE_TEST_INJECTION&&pc_owned&&cp_test_reset),.pc_route_retired(pc_route_retired),.pc_hold(pc_owned),.pc_safe(pc_safe),.abort(abort),.busy(busy),.cc_busy(cc_busy),.cc_fault(cc_fault),.cf_fault(cf_fault),.clk(clk),.cost_lease(cost_lease),.cs_busy(cs_busy),.cs_configured(cs_configured),.cs_design_id(cs_design_id),.cs_editing(cs_editing),.cs_fault(cs_fault),.cs_m_araddr(cs_m_araddr),.cs_m_arburst(cs_m_arburst),.cs_m_arid(cs_m_arid),.cs_m_arlen(cs_m_arlen),.cs_m_arready(cs_m_arready),.cs_m_arsize(cs_m_arsize),.cs_m_arvalid(cs_m_arvalid),.cs_m_awaddr(cs_m_awaddr),.cs_m_awburst(cs_m_awburst),.cs_m_awid(cs_m_awid),.cs_m_awlen(cs_m_awlen),.cs_m_awready(cs_m_awready),.cs_m_awsize(cs_m_awsize),.cs_m_awvalid(cs_m_awvalid),.cs_m_bid(cs_m_bid),.cs_m_bready(cs_m_bready),.cs_m_bresp(cs_m_bresp),.cs_m_bvalid(cs_m_bvalid),.cs_m_rdata(cs_m_rdata),.cs_m_rid(cs_m_rid),.cs_m_rlast(cs_m_rlast),.cs_m_rready(cs_m_rready),.cs_m_rresp(cs_m_rresp),.cs_m_rvalid(cs_m_rvalid),.cs_m_wdata(cs_m_wdata),.cs_m_wlast(cs_m_wlast),.cs_m_wready(cs_m_wready),.cs_m_wstrb(cs_m_wstrb),.cs_m_wvalid(cs_m_wvalid),.cs_published_version(cs_published_version),.cs_ready_for_query(cs_ready_for_query),.d_configured(d_configured),.d_m_araddr(d_m_araddr),.d_m_arburst(d_m_arburst),.d_m_arid(d_m_arid),.d_m_arlen(d_m_arlen),.d_m_arready(d_m_arready),.d_m_arsize(d_m_arsize),.d_m_arvalid(d_m_arvalid),.d_m_awaddr(d_m_awaddr),.d_m_awburst(d_m_awburst),.d_m_awid(d_m_awid),.d_m_awlen(d_m_awlen),.d_m_awready(d_m_awready),.d_m_awsize(d_m_awsize),.d_m_awvalid(d_m_awvalid),.d_m_bid(d_m_bid),.d_m_bready(d_m_bready),.d_m_bresp(d_m_bresp),.d_m_bvalid(d_m_bvalid),.d_m_rdata(d_m_rdata),.d_m_rid(d_m_rid),.d_m_rlast(d_m_rlast),.d_m_rready(d_m_rready),.d_m_rresp(d_m_rresp),.d_m_rvalid(d_m_rvalid),.d_m_wdata(d_m_wdata),.d_m_wlast(d_m_wlast),.d_m_wready(d_m_wready),.d_m_wstrb(d_m_wstrb),.d_m_wvalid(d_m_wvalid),.design_id(design_id),.f_all_drained(f_all_drained),.f_backend_idle(f_backend_idle),.f_fault(f_fault),.f_normal_retired(f_normal_retired),.f_phase(f_phase),.f_recovery_owned(f_recovery_owned),.f_route_payload(b_f_route_payload),.f_sp(b_f_sp),.f_sr(b_f_sr),.f_srp(b_f_srp),.f_srr(b_f_srr),.f_srv(b_f_srv),.f_sv(b_f_sv),.fault(fault),.g_configured(g_configured),.g_m_araddr(g_m_araddr),.g_m_arburst(g_m_arburst),.g_m_arid(g_m_arid),.g_m_arlen(g_m_arlen),.g_m_arready(g_m_arready),.g_m_arsize(g_m_arsize),.g_m_arvalid(g_m_arvalid),.g_m_rdata(g_m_rdata),.g_m_rid(g_m_rid),.g_m_rlast(g_m_rlast),.g_m_rready(g_m_rready),.g_m_rresp(g_m_rresp),.g_m_rvalid(g_m_rvalid),.k_a_checkpoint(k_a_checkpoint),.k_a_cookie(k_a_cookie),.k_a_design(k_a_design),.k_a_net(k_a_net),.k_a_node(k_a_node),.k_a_occ(k_a_occ),.k_a_ready(k_a_ready),.k_a_refs(k_a_refs),.k_a_rsp_checkpoint(k_a_rsp_checkpoint),.k_a_rsp_cookie(k_a_rsp_cookie),.k_a_rsp_design(k_a_rsp_design),.k_a_rsp_ready(k_a_rsp_ready),.k_a_rsp_valid(k_a_rsp_valid),.k_a_status(k_a_status),.k_a_valid(k_a_valid),.k_busy(k_busy),.k_cold_rst(k_cold_rst),.k_corrected(k_corrected),.k_count(k_count),.k_fault(k_fault),.k_full(k_full),.k_permit(k_permit),.k_rec_ready(b_k_rec_ready),.k_rec_valid(b_k_rec_valid),.k_rsp_cookie(k_rsp_cookie),.k_rsp_ready(k_rsp_ready),.k_rsp_status(k_rsp_status),.k_rsp_valid(k_rsp_valid),.k_saved_checkpoint(k_saved_checkpoint),.k_saved_design(k_saved_design),.k_target_reset(k_target_reset),.lr_fault(lr_fault),.lr_rsp_status(lr_rsp_status),.lr_s_cookie(lr_s_cookie),.lr_s_last(lr_s_last),.lr_s_node(lr_s_node),.lr_s_payload(lr_s_payload),.lr_s_ready(lr_s_ready),.lr_s_valid(lr_s_valid),.lr_verified(lr_verified),.lr_written(lr_written),.operation_pending(operation_pending),.out_action(out_action),.out_attrs(out_attrs),.out_bits(out_bits),.out_commit_acked(out_commit_acked),.out_commit_payload(out_commit_payload),.out_commit_status(out_commit_status),.out_commit_valid(out_commit_valid),.out_config(out_config),.out_connection(out_connection),.out_cookie(out_cookie),.out_cost_geometry(out_cost_geometry),.out_cost_geometry_result(out_cost_geometry_result),.out_cost_packet(out_cost_packet),.out_cost_status(out_cost_status),.out_cost_valid(out_cost_valid),.out_cost_words(out_cost_words),.out_node(out_node),.out_offer_before(out_offer_before),.out_offer_key(out_offer_key),.out_offer_node(out_offer_node),.out_offer_size(out_offer_size),.out_offer_status(out_offer_status),.out_offer_valid(out_offer_valid),.out_params(out_params),.out_params_valid(out_params_valid),.out_position(out_position),.out_post_attrs(out_post_attrs),.out_post_distance(out_post_distance),.out_post_prev_read(out_post_prev_read),.out_post_status(out_post_status),.out_post_upstream(out_post_upstream),.out_post_valid(out_post_valid),.out_post_x(out_post_x),.out_post_y(out_post_y),.out_prep_count(out_prep_count),.out_prep_history(out_prep_history),.out_prep_net_data(out_prep_net_data),.out_prep_occupancy(out_prep_occupancy),.out_prep_price_index(out_prep_price_index),.out_prep_price_value(out_prep_price_value),.out_prep_status(out_prep_status),.out_prep_valid(out_prep_valid),.out_profile_revision(out_profile_revision),.out_ready(out_ready),.out_sequence(out_sequence),.out_services(out_services),.out_steps(out_steps),.out_valid(out_valid),.owner_configured(owner_configured),.owner_m_araddr(owner_m_araddr),.owner_m_arburst(owner_m_arburst),.owner_m_arid(owner_m_arid),.owner_m_arlen(owner_m_arlen),.owner_m_arready(owner_m_arready),.owner_m_arsize(owner_m_arsize),.owner_m_arvalid(owner_m_arvalid),.owner_m_awaddr(owner_m_awaddr),.owner_m_awburst(owner_m_awburst),.owner_m_awid(owner_m_awid),.owner_m_awlen(owner_m_awlen),.owner_m_awready(owner_m_awready),.owner_m_awsize(owner_m_awsize),.owner_m_awvalid(owner_m_awvalid),.owner_m_bid(owner_m_bid),.owner_m_bready(owner_m_bready),.owner_m_bresp(owner_m_bresp),.owner_m_bvalid(owner_m_bvalid),.owner_m_rdata(owner_m_rdata),.owner_m_rid(owner_m_rid),.owner_m_rlast(owner_m_rlast),.owner_m_rready(owner_m_rready),.owner_m_rresp(owner_m_rresp),.owner_m_rvalid(owner_m_rvalid),.owner_m_wdata(owner_m_wdata),.owner_m_wlast(owner_m_wlast),.owner_m_wready(owner_m_wready),.owner_m_wstrb(owner_m_wstrb),.owner_m_wvalid(owner_m_wvalid),.p_active(p_active),.p_active_price(p_active_price),.p_active_query(p_active_query),.p_m_araddr(p_m_araddr),.p_m_arburst(p_m_arburst),.p_m_arid(p_m_arid),.p_m_arlen(p_m_arlen),.p_m_arready(p_m_arready),.p_m_arsize(p_m_arsize),.p_m_arvalid(p_m_arvalid),.p_m_awaddr(p_m_awaddr),.p_m_awburst(p_m_awburst),.p_m_awid(p_m_awid),.p_m_awlen(p_m_awlen),.p_m_awready(p_m_awready),.p_m_awsize(p_m_awsize),.p_m_awvalid(p_m_awvalid),.p_m_bid(p_m_bid),.p_m_bready(p_m_bready),.p_m_bresp(p_m_bresp),.p_m_bvalid(p_m_bvalid),.p_m_rdata(p_m_rdata),.p_m_rid(p_m_rid),.p_m_rlast(p_m_rlast),.p_m_rready(p_m_rready),.p_m_rresp(p_m_rresp),.p_m_rvalid(p_m_rvalid),.p_m_wdata(p_m_wdata),.p_m_wlast(p_m_wlast),.p_m_wready(p_m_wready),.p_m_wstrb(p_m_wstrb),.p_m_wvalid(p_m_wvalid),.q_busy(q_busy),.q_configured(q_configured),.q_fault(q_fault),.q_m_araddr(q_m_araddr),.q_m_arburst(q_m_arburst),.q_m_arid(q_m_arid),.q_m_arlen(q_m_arlen),.q_m_arready(q_m_arready),.q_m_arsize(q_m_arsize),.q_m_arvalid(q_m_arvalid),.q_m_rdata(q_m_rdata),.q_m_rid(q_m_rid),.q_m_rlast(q_m_rlast),.q_m_rready(q_m_rready),.q_m_rresp(q_m_rresp),.q_m_rvalid(q_m_rvalid),.query_ready(query_ready),.query_version(query_version),.rc_block(rc_block),.rc_busy(rc_busy),.rc_fault(rc_fault),.rc_req_ready(b_rc_req_ready),.rc_req_valid(b_rc_req_valid),.rc_rsp_acked(rc_rsp_acked),.rc_rsp_cookie(rc_rsp_cookie),.rc_rsp_nodes(rc_rsp_nodes),.rc_rsp_ready(b_rc_rsp_ready),.rc_rsp_status(rc_rsp_status),.rc_rsp_valid(b_rc_rsp_valid),.rc_slots(rc_slots),.recover_checkpoint(recover_checkpoint),.recover_cookie(recover_cookie),.recover_design(recover_design),.recover_price(recover_price),.recover_query(recover_query),.recover_version(recover_version),.rst(rst),.snapshot_checkpoint(snapshot_checkpoint),.snapshot_cookie(snapshot_cookie),.snapshot_count(snapshot_count),.snapshot_design(snapshot_design),.snapshot_nodes(snapshot_nodes),.snapshot_probe(snapshot_probe),.t_configured(t_configured),.t_m_araddr(t_m_araddr),.t_m_arburst(t_m_arburst),.t_m_arid(t_m_arid),.t_m_arlen(t_m_arlen),.t_m_arready(t_m_arready),.t_m_arsize(t_m_arsize),.t_m_arvalid(t_m_arvalid),.t_m_rdata(t_m_rdata),.t_m_rid(t_m_rid),.t_m_rlast(t_m_rlast),.t_m_rready(t_m_rready),.t_m_rresp(t_m_rresp),.t_m_rvalid(t_m_rvalid),.test_route_abort(test_route_abort),.test_route_version_flip(test_route_version_flip),.ss_abort(ss_abort),.ss_start_valid(ss_start_valid),.ss_start_ready(ss_start_ready),.ss_start_cookie(ss_start_cookie),.ss_start_source(ss_start_source),.ss_start_key(ss_start_key),.ss_start_nodes(ss_start_nodes),.ss_start_max_polls(ss_start_max_polls),.ss_start_poll_cookie(ss_start_poll_cookie),.ss_start_design(ss_start_design),.ss_start_query(ss_start_query),.ss_start_price(ss_start_price),.ss_start_expand(ss_start_expand),.ss_rsp_valid(ss_rsp_valid),.ss_rsp_ready(ss_rsp_ready),.ss_rsp_status(ss_rsp_status),.ss_rsp_cookie(ss_rsp_cookie),.ss_polls(ss_polls),.ss_expands(ss_expands),.ss_candidates(ss_candidates),.ss_result_node(ss_result_node),.ss_result_key(ss_result_key),.ss_busy(ss_busy),.ss_fault(ss_fault),.ss_phase(ss_phase),.ss_poll_event(ss_poll_event),.ss_poll_node(ss_poll_node),.ss_poll_key(ss_poll_key),.ss_poll_size(ss_poll_size));
query_lifecycle controller(.cp_valid(!boot_done_held&&!jp_owned&&qc_cp_valid),.cp_restore(qc_cp_restore),.cp_rsp_ready(qc_cp_rsp_ready),.cp_s_valid(qc_cp_s_valid),.cp_s_last(qc_cp_s_last),.cp_m_ready(qc_cp_m_ready),.cp_ready(qc_core_cp_ready),.cp_busy(qc_cp_busy),.cp_rsp_valid(qc_cp_rsp_valid),.cp_s_ready(qc_cp_s_ready),.cp_m_valid(qc_cp_m_valid),.cp_m_last(qc_cp_m_last),.cp_expected_crc(qc_cp_expected_crc),.cp_s_index(qc_cp_s_index),.cp_s_data(qc_cp_s_data),.cp_crc(qc_cp_crc),.cp_m_index(qc_cp_m_index),.cp_m_data(qc_cp_m_data),.cp_status(qc_cp_status),.cp_safe(pc_owned&&pc_safe&&!qc_reset_held),.active_generation(qc_image_generation),.cmd_valid(!boot_pending&&qc_cmd_valid&&!pc_owned&&!as_cfg_lease),.cmd_ready(qc_cmd_ready),.cmd_slot(qc_cmd_slot),.cmd_cookie(qc_cmd_cookie),.cmd_route_cookie(qc_cmd_route_cookie),.cmd_source(qc_cmd_source),.cmd_key(qc_cmd_key),.cmd_nodes(qc_cmd_nodes),.cmd_max_polls(qc_cmd_max_polls),.cmd_poll_cookie(qc_cmd_poll_cookie),.cmd_design(qc_cmd_design),.cmd_query(qc_cmd_query),.cmd_price(qc_cmd_price),.cmd_expand(qc_cmd_expand),.rsp_valid(qc_rsp_valid),.rsp_ready(qc_rsp_ready),.rsp_status(qc_rsp_status),.rsp_detail(qc_rsp_detail),.rsp_cookie(qc_rsp_cookie),.rsp_nodes(qc_rsp_nodes),.rsp_acked(qc_rsp_acked),.rsp_committed(qc_rsp_committed),.abort(qc_abort||k_rec_valid),.busy(qc_busy),.fault(qc_fault),.phase(qc_phase),.prepared_event(qc_prepared_event),.prepare_acked(qc_prepare_acked),.cleanup_acked(qc_cleanup_acked),.clk(clk),.rst(rst||qc_reset_held),.admit(!boot_pending&&!qc_pending&&!as_cfg_lease&&!pc_owned&&!as_fault&&k_permit&&!fault&&!rc_fault&&!k_fault&&!cf_fault&&!lr_fault&&!f_fault&&!ss_fault&&!ss_busy&&f_phase==0&&f_normal_retired&&f_backend_idle&&f_all_drained&&f_sv==0&&!rc_req_valid&&!k_rec_valid),.backend_fault(fault||rc_fault||k_fault||cf_fault||lr_fault||f_fault),.backend_drained(f_normal_retired&&f_backend_idle&&f_all_drained&&!ss_busy&&(!rc_busy||(rc_fault&&f_phase==6))),.active(p_active),.active_design(design_id),.active_version(query_version),.active_query(p_active_query),.active_price(p_active_price),.route_slots(rc_slots),.host_label_edit(f_sv[8]&&f_sr[8]&&f_sp[19456]),.search_valid(ss_start_valid),.search_ready(ss_start_ready),.search_abort(ss_abort),.search_rsp_valid(ss_rsp_valid),.search_rsp_ready(ss_rsp_ready),.search_status(ss_rsp_status),.search_rsp_cookie(ss_rsp_cookie),.search_result_node(ss_result_node),.route_status(rc_rsp_status),.route_rsp_cookie(rc_rsp_cookie),.route_nodes(rc_rsp_nodes),.route_acked(rc_rsp_acked),.search_cookie(ss_start_cookie),.search_source(ss_start_source),.search_key(ss_start_key),.search_nodes(ss_start_nodes),.search_max_polls(ss_start_max_polls),.search_poll_cookie(ss_start_poll_cookie),.search_design(ss_start_design),.search_query(ss_start_query),.search_price(ss_start_price),.search_expand(ss_start_expand),.service_valid(c_service_valid),.service_ready(c_service_ready),.service_lane(c_service_lane),.service_payload(c_service_payload),.service_rsp_valid(c_service_rsp_valid),.service_rsp_ready(c_service_rsp_ready),.service_rsp_payload(c_service_rsp_payload),.route_valid(c_route_valid),.route_ready(c_route_ready),.route_payload(c_route_payload),.route_rsp_valid(c_route_rsp_valid),.route_rsp_ready(c_route_rsp_ready));

// Only consumed native transactions earn bootstrap receipts. No test hooks.
wire boot_retired=!rst&&!k_cold_rst&&!abort&&f_phase==0&&f_all_drained&&f_backend_idle&&f_normal_retired&&!qc_busy&&!qc_cp_busy&&!cp_busy&&!ss_busy&&!rc_busy&&!as_busy&&!k_busy&&!as_cfg_rsp_valid&&!as_cfg_valid&&!(|(f_sv&16'hc17f));
boot_restore_gate boot_gate(
.clk(clk),.cold_rst(k_cold_rst),.work_rst(rst||abort),.required(boot_required),
.cfg_valid(boot_cfg_valid),.cfg_ready(boot_cfg_ready),.cfg_design(boot_design),.cfg_generation(boot_generation),
.cfg_checkpoint(boot_checkpoint),.cfg_version(boot_version),.cfg_nodes(boot_nodes),.cfg_label_count(boot_label_count),.cfg_label_crc(boot_label_crc),.cfg_path_crc(boot_path_crc),.cfg_query_crc(boot_query_crc),
.cfg_query(boot_query),.cfg_slots(boot_slots),.cfg_price(boot_price),.cfg_payload(boot_payload),
.pending(boot_pending),.admin_allowed(boot_admin_allowed),.done_held(boot_done_held),.rsp_valid(boot_rsp_valid),.rsp_ready(boot_rsp_ready),.rsp_status(boot_status),.receipts(boot_receipts),.config_receipts(boot_config_receipts),
.verify_valid(boot_verify_valid),.verify_ready(boot_verify_ready),.verified_count(boot_verified_count),.verify_status(boot_verify_status),
.sv(f_sv),.sr(f_sr),.srv(f_srv),.srr(f_srr),.sp(f_sp),.rp(f_srp),
.owner_configured(owner_configured),.authority_configured(as_configured),.authority_design(as_bound_design),.authority_generation(as_bound_generation),.authority_checkpoint(as_bound_checkpoint),
.providers_configured(q_configured&&g_configured&&d_configured&&t_configured&&cs_configured),.active(p_active),.active_design(design_id),.active_version(query_version),.published_version(cs_published_version),
.active_query(p_active_query),.route_slots(rc_slots),.active_price(p_active_price),.recovery_permit(k_permit),.recovery_design(k_saved_design),.recovery_checkpoint(k_saved_checkpoint),
.path_accept(cp_valid&&cp_ready),.path_restore(cp_restore),.path_done(cp_rsp_valid&&cp_rsp_ready),.path_status(cp_status),.path_crc(cp_crc),
.query_accept(qc_cp_valid&&qc_cp_ready),.query_restore(qc_cp_restore),.query_done(qc_cp_rsp_valid&&qc_cp_rsp_ready),.query_status(qc_cp_status),.query_crc(qc_cp_crc),
.retired(boot_retired),.lease_owned(pc_owned));


checkpoint_publish_barrier publication(.clk(clk),.rst(rst||k_cold_rst),.lease_owned(pc_owned),
.retired(pc_retired&&pc_route_retired&&as_drained&&as_retired&&!cp_busy&&!qc_cp_busy&&!qc_restore_pending),
.stage_busy(as_busy||as_cfg_lease||k_busy||(|jp_reply)),.fault(abort||as_fault||fault||rc_fault||k_fault||cf_fault||lr_fault||f_fault||ss_fault||qc_fault),.manifest_ready(jp_manifest_ready),
.start_valid(jp_start&&jp_start_open),.start_ready(jp_core_start_ready),.start_design(jp_design),.start_generation(jp_generation),.start_checkpoint(jp_checkpoint),.start_version(jp_version),.start_query(jp_query),.start_price(jp_price),
.commit_valid(jp_commit),.commit_ready(jp_commit_ready),.cancel_valid(jp_cancel),.cancel_ready(jp_cancel_ready),.owned(jp_owned),.prepare_allowed(jp_prepare),.done_valid(jp_done),.done_ready(jp_done_ready),.done_status(jp_result),
.prepared({jp_prepared,jp_ap}),.publish_ready({jp_pubready,jp_apr}),.discard_ready({jp_dropready,jp_adr}),.publish_valid(jp_pv),.discard_valid(jp_dv),
.a_design(as_bound_design),.a_generation(as_bound_generation),.a_checkpoint(as_bound_checkpoint),.k_design(jp_kdesign),.c_design(jp_cdesign),.k_checkpoint(jp_kcp),.c_checkpoint(jp_ccp),.k_version(jp_kver),.c_version(jp_cver),.k_query(jp_kquery),.k_price(jp_kprice),.journal_count(k_count),
.sa_design(jp_ad),.sa_generation(jp_ag),.sa_checkpoint(jp_ac),.sk_design(jp_skdesign),.sc_design(jp_scdesign),.sk_checkpoint(jp_skcp),.sc_checkpoint(jp_sccp),.sk_version(jp_skver),.sc_version(jp_scver),.sk_query(jp_skquery),.sk_price(jp_skprice));
endmodule
