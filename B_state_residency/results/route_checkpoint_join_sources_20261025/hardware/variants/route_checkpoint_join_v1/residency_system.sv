`timescale 1ns/1ps
// Generated structural hardware. No file agents, CPU oracle or search stimulus.
module residency_system #(parameter integer SLOTS=32,FRAMES=16384,INDEX_BITS=14,HASH_BITS=15,ENABLE_TEST_INJECTION=0)(
input wire cp_valid,cp_restore,
output wire cp_ready,cp_busy,cp_rsp_valid,input wire cp_rsp_ready,
output wire[3:0]cp_status,output wire[31:0]cp_crc,
input wire[63:0]cp_design,input wire[31:0]cp_nodes,cp_nets,cp_expected_crc,
input wire cp_s_valid,output wire cp_s_ready,input wire[31:0]cp_s_index,cp_s_data,input wire cp_s_last,
output wire cp_m_valid,input wire cp_m_ready,output wire[31:0]cp_m_index,cp_m_data,output wire cp_m_last,
input wire cp_test_reset,output wire pc_route_retired,
input wire pc_hold,pc_safe,
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
input wire [31:0] k_a_occ,
input wire k_a_ready,
input wire [31:0] k_a_refs,
input wire [31:0] k_a_rsp_checkpoint,
input wire [31:0] k_a_rsp_cookie,
input wire [63:0] k_a_rsp_design,
output wire k_a_rsp_ready,
input wire k_a_rsp_valid,
input wire [3:0] k_a_status,
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
input wire test_route_version_flip
);
wire [2:0] b_l_field;
wire [31:0] b_l_node;
wire [159:0] b_l_payload;
wire b_l_present;
wire b_l_ready;
wire b_l_rsp_ready;
wire b_l_rsp_valid;
wire [3:0] b_l_status;
wire b_l_valid;
wire [31:0] b_l_value;
wire b_l_write;
wire [31:0] b_o_cookie;
wire [31:0] b_o_count;
wire [31:0] b_o_net;
wire [31:0] b_o_node;
wire [31:0] b_o_occupancy;
wire [2:0] b_o_op;
wire b_o_ready;
wire [31:0] b_o_rsp_cookie;
wire b_o_rsp_ready;
wire b_o_rsp_valid;
wire [3:0] b_o_status;
wire b_o_valid;
wire b_o_will_overuse;
wire cf_busy;
wire [2303:0] cf_payload;
wire [5:0] cf_ready;
wire [5:0] cf_replies;
wire [5:0] cf_reply_ready;
wire [5:0] cf_retired;
wire [31:0] cf_rsp_cookie;
wire [3:0] cf_rsp_status;
wire cf_rsp_valid;
wire [31:0] cf_saved_checkpoint;
wire [63:0] cf_saved_design;
wire [5:0] cf_sent;
wire [17:0] cf_status;
wire [5:0] cf_valid;
wire f_brecover_ready;
wire f_brecover_rsp_ready;
wire f_brecover_rsp_valid;
wire f_brecover_valid;
wire [191:0] f_broute_payload;
wire f_broute_ready;
wire f_broute_rsp_ready;
wire f_broute_rsp_valid;
wire f_broute_valid;
wire [38911:0] f_cbp;
wire [15:0] f_cbr;
wire [4095:0] f_cbrp;
wire [15:0] f_cbrr;
wire [15:0] f_cbrv;
wire [15:0] f_cbv;
wire [38911:0] f_dp;
wire [15:0] f_dr;
wire [4095:0] f_drp;
wire [15:0] f_drr;
wire [15:0] f_drv;
wire [15:0] f_dv;
wire [15:0] f_pending;
wire [4:0] f_watch_fault;
wire [4:0] f_watch_idle;
wire [31:0] fd_cc_req_cookie;
wire [63:0] fd_cc_req_design_id;
wire [3:0] fd_cc_req_price;
wire [1:0] fd_cc_req_query;
wire fd_cc_req_ready;
wire fd_cc_req_valid;
wire [31:0] fd_cc_req_version;
wire [127:0] fd_cc_req_words;
wire [31:0] fd_cc_rsp_cookie;
wire [63:0] fd_cc_rsp_design_id;
wire [3:0] fd_cc_rsp_price;
wire [1:0] fd_cc_rsp_query;
wire fd_cc_rsp_ready;
wire [1:0] fd_cc_rsp_status;
wire fd_cc_rsp_valid;
wire [31:0] fd_cc_rsp_version;
wire [63:0] fd_cc_rsp_words;
wire fd_cf_load_ready;
wire fd_cf_load_rsp_ready;
wire fd_cf_load_rsp_valid;
wire fd_cf_load_status;
wire fd_cf_load_valid;
wire [63:0] fd_cs_cfg_design_id;
wire [63:0] fd_cs_cfg_history;
wire [31:0] fd_cs_cfg_net_count;
wire [63:0] fd_cs_cfg_nets;
wire [31:0] fd_cs_cfg_nodes;
wire [63:0] fd_cs_cfg_prices;
wire fd_cs_cfg_ready;
wire fd_cs_cfg_rsp_ready;
wire fd_cs_cfg_rsp_valid;
wire [2:0] fd_cs_cfg_status;
wire fd_cs_cfg_valid;
wire [31:0] fd_cs_cfg_version;
wire [31:0] fd_cs_req_cookie;
wire fd_cs_req_host;
wire [31:0] fd_cs_req_index;
wire [2:0] fd_cs_req_op;
wire [3:0] fd_cs_req_price;
wire [1:0] fd_cs_req_query;
wire fd_cs_req_ready;
wire fd_cs_req_valid;
wire [31:0] fd_cs_req_value;
wire [31:0] fd_cs_req_version;
wire [31:0] fd_cs_rsp_cookie;
wire [127:0] fd_cs_rsp_data;
wire fd_cs_rsp_host;
wire [31:0] fd_cs_rsp_index;
wire [2:0] fd_cs_rsp_op;
wire [3:0] fd_cs_rsp_price;
wire [1:0] fd_cs_rsp_query;
wire fd_cs_rsp_ready;
wire [3:0] fd_cs_rsp_status;
wire fd_cs_rsp_valid;
wire [31:0] fd_cs_rsp_version;
wire [63:0] fd_d_cfg_base;
wire [31:0] fd_d_cfg_nodes;
wire fd_d_cfg_ready;
wire fd_d_cfg_rsp_ready;
wire fd_d_cfg_rsp_valid;
wire [2:0] fd_d_cfg_status;
wire fd_d_cfg_valid;
wire [31:0] fd_expand_connection;
wire [31:0] fd_expand_cookie;
wire [31:0] fd_expand_flags;
wire [31:0] fd_expand_has_laguna;
wire [31:0] fd_expand_net;
wire [31:0] fd_expand_parent;
wire [31:0] fd_expand_prune;
wire fd_expand_ready;
wire [31:0] fd_expand_sequence;
wire [31:0] fd_expand_sink;
wire fd_expand_valid;
wire [31:0] fd_expand_version;
wire [31:0] fd_expand_xmax;
wire [31:0] fd_expand_xmin;
wire [31:0] fd_expand_ymax;
wire [31:0] fd_expand_ymin;
wire fd_fa_authoritative;
wire [31:0] fd_fa_checkpoint;
wire [63:0] fd_fa_design;
wire [3:0] fd_fa_price;
wire [1:0] fd_fa_query;
wire [31:0] fd_fa_version;
wire fd_fc_authoritative;
wire [31:0] fd_fc_checkpoint;
wire [63:0] fd_fc_design;
wire [2303:0] fd_fc_payload;
wire [63:0] fd_g_cfg_attrs_base;
wire [31:0] fd_g_cfg_edges;
wire [63:0] fd_g_cfg_edges_base;
wire [31:0] fd_g_cfg_nodes;
wire [63:0] fd_g_cfg_offsets_base;
wire fd_g_cfg_ready;
wire fd_g_cfg_rsp_ready;
wire fd_g_cfg_rsp_valid;
wire [2:0] fd_g_cfg_status;
wire fd_g_cfg_valid;
wire [1:0] fd_host_ctrl_op;
wire [3:0] fd_host_ctrl_price;
wire [1:0] fd_host_ctrl_query;
wire fd_host_ctrl_ready;
wire fd_host_ctrl_rsp_ready;
wire fd_host_ctrl_rsp_valid;
wire [3:0] fd_host_ctrl_status;
wire fd_host_ctrl_valid;
wire [31:0] fd_host_ctrl_version;
wire [31:0] fd_host_design_req_arg;
wire [31:0] fd_host_design_req_cookie;
wire [31:0] fd_host_design_req_node;
wire [2:0] fd_host_design_req_op;
wire [31:0] fd_host_design_req_owner;
wire fd_host_design_req_ready;
wire fd_host_design_req_valid;
wire [31:0] fd_host_design_rsp_cookie;
wire [31:0] fd_host_design_rsp_count;
wire [31:0] fd_host_design_rsp_flags;
wire [31:0] fd_host_design_rsp_mask;
wire fd_host_design_rsp_ready;
wire [3:0] fd_host_design_rsp_status;
wire fd_host_design_rsp_valid;
wire [2:0] fd_host_io_field;
wire [31:0] fd_host_io_node;
wire [159:0] fd_host_io_payload;
wire fd_host_io_present;
wire fd_host_io_ready;
wire fd_host_io_rsp_ready;
wire fd_host_io_rsp_valid;
wire [3:0] fd_host_io_status;
wire fd_host_io_valid;
wire [31:0] fd_host_io_value;
wire fd_host_io_write;
wire [31:0] fd_host_owner_req_cookie;
wire [31:0] fd_host_owner_req_net;
wire [31:0] fd_host_owner_req_node;
wire [2:0] fd_host_owner_req_op;
wire fd_host_owner_req_ready;
wire fd_host_owner_req_valid;
wire [31:0] fd_host_owner_rsp_cookie;
wire [31:0] fd_host_owner_rsp_count;
wire [31:0] fd_host_owner_rsp_occupancy;
wire fd_host_owner_rsp_ready;
wire [3:0] fd_host_owner_rsp_status;
wire fd_host_owner_rsp_valid;
wire fd_host_owner_rsp_will_overuse;
wire fd_k_cfg_ready;
wire fd_k_cfg_rsp_ready;
wire fd_k_cfg_rsp_valid;
wire fd_k_cfg_status;
wire fd_k_cfg_valid;
wire [63:0] fd_owner_cfg_allocator;
wire [31:0] fd_owner_cfg_capacity;
wire [31:0] fd_owner_cfg_nodes;
wire [63:0] fd_owner_cfg_pool;
wire [63:0] fd_owner_cfg_primary;
wire fd_owner_cfg_ready;
wire fd_owner_cfg_rsp_ready;
wire fd_owner_cfg_rsp_valid;
wire [2:0] fd_owner_cfg_status;
wire fd_owner_cfg_valid;
wire [63:0] fd_q_cfg_base;
wire [31:0] fd_q_cfg_connections;
wire [63:0] fd_q_cfg_design;
wire [31:0] fd_q_cfg_nets;
wire [31:0] fd_q_cfg_nodes;
wire fd_q_cfg_ready;
wire [31:0] fd_q_cfg_revision;
wire fd_q_cfg_rsp_ready;
wire fd_q_cfg_rsp_valid;
wire [2:0] fd_q_cfg_status;
wire fd_q_cfg_valid;
wire [31:0] fd_result_cookie;
wire [31:0] fd_result_count;
wire fd_result_early;
wire [31:0] fd_result_expanded_count;
wire fd_result_hit;
wire [31:0] fd_result_mask;
wire [31:0] fd_result_raw_count;
wire fd_result_ready;
wire [3:0] fd_result_status;
wire fd_result_valid;
wire [31:0] fd_seed_cookie;
wire [31:0] fd_seed_id;
wire [31:0] fd_seed_key;
wire [31:0] fd_seed_op;
wire fd_seed_ready;
wire [31:0] fd_seed_rsp_cookie;
wire [31:0] fd_seed_rsp_id;
wire [31:0] fd_seed_rsp_key;
wire fd_seed_rsp_ready;
wire [31:0] fd_seed_rsp_size;
wire [31:0] fd_seed_rsp_status;
wire fd_seed_rsp_valid;
wire fd_seed_valid;
wire [31:0] fd_seed_version;
wire [31:0] fd_t_cfg_columns;
wire [63:0] fd_t_cfg_columns_base;
wire fd_t_cfg_ready;
wire [31:0] fd_t_cfg_rows;
wire [63:0] fd_t_cfg_rows_base;
wire fd_t_cfg_rsp_ready;
wire fd_t_cfg_rsp_valid;
wire [2:0] fd_t_cfg_status;
wire fd_t_cfg_valid;
wire [31:0] k_j_net;
wire [31:0] k_j_node;
wire [2:0] k_j_op;
wire k_j_ready;
wire k_j_valid;
wire k_labels_done;wire k_attempt_reset;wire k_retry_safe;
wire k_labels_valid;
wire [3:0] k_new_price;
wire [1:0] k_new_query;
wire [31:0] k_new_version;
wire [31:0] k_o_cookie;
wire [31:0] k_o_net;
wire [31:0] k_o_node;
wire [2:0] k_o_op;
wire k_o_ready;
wire k_o_rsp_ready;
wire k_o_rsp_valid;
wire k_o_valid;
wire k_rcfg_done;
wire k_rcfg_valid;
wire label_drained;
wire label_watch_fault;
wire lr_busy;
wire [1:0] lr_c_op;
wire [3:0] lr_c_price;
wire [1:0] lr_c_query;
wire lr_c_ready;
wire lr_c_rsp_ready;
wire lr_c_valid;
wire [31:0] lr_c_version;
wire [2:0] lr_l_field;
wire [31:0] lr_l_node;
wire lr_l_ready;
wire lr_l_rsp_ready;
wire lr_l_rsp_valid;
wire lr_l_valid;
wire [31:0] lr_l_value;
wire lr_l_write;
wire [31:0] lr_rsp_cookie;
wire lr_rsp_ready;
wire lr_rsp_valid;
wire lr_start_ready;
wire lr_start_valid;
wire owner_drained;
wire owner_watch_fault;
wire recover_open;
reg [63:0] snapshot_design_held;
reg [31:0] snapshot_checkpoint_held;
reg [31:0] snapshot_cookie_held;
reg [31:0] snapshot_count_held;
reg [31:0] snapshot_nodes_held;
reg [31:0] snapshot_probe_held;
always @(posedge clk)begin
 if(k_cold_rst)begin
  snapshot_design_held<=0;
  snapshot_checkpoint_held<=0;
  snapshot_cookie_held<=0;
  snapshot_count_held<=0;
  snapshot_nodes_held<=0;
  snapshot_probe_held<=0;
 end else if(k_rec_valid&&k_rec_ready)begin
  snapshot_design_held<=snapshot_design;
  snapshot_checkpoint_held<=snapshot_checkpoint;
  snapshot_cookie_held<=snapshot_cookie;
  snapshot_count_held<=snapshot_count;
  snapshot_nodes_held<=snapshot_nodes;
  snapshot_probe_held<=snapshot_probe;
 end
end
assign recover_open=k_permit&&!f_recovery_owned&&!k_rec_valid;
// The fence forwards a retry only after prior completion consumption and
// backend drain. Restore services and their responses must also be retired.
assign k_retry_safe=f_all_drained&&f_backend_idle&&f_normal_retired&&f_pending==0&&!cf_busy&&!lr_busy&&!cf_rsp_valid&&!lr_rsp_valid&&!f_fault;
assign k_labels_done=lr_rsp_valid;
assign k_rcfg_done=cf_rsp_valid;
assign fd_q_cfg_base=f_dp[0+:64];
assign fd_q_cfg_design=f_dp[64+:64];
assign fd_q_cfg_connections=f_dp[128+:32];
assign fd_q_cfg_nodes=f_dp[160+:32];
assign fd_q_cfg_nets=f_dp[192+:32];
assign fd_q_cfg_revision=f_dp[224+:32];
assign f_drp[0+:3]=fd_q_cfg_status;
assign f_drp[3+:253]=0;
assign fd_q_cfg_valid=f_dv[0];
assign f_dr[0]=fd_q_cfg_ready;
assign f_drv[0]=fd_q_cfg_rsp_valid;
assign fd_q_cfg_rsp_ready=f_drr[0];
assign fd_g_cfg_offsets_base=f_dp[2432+:64];
assign fd_g_cfg_edges_base=f_dp[2496+:64];
assign fd_g_cfg_attrs_base=f_dp[2560+:64];
assign fd_g_cfg_nodes=f_dp[2624+:32];
assign fd_g_cfg_edges=f_dp[2656+:32];
assign f_drp[256+:3]=fd_g_cfg_status;
assign f_drp[259+:253]=0;
assign fd_g_cfg_valid=f_dv[1];
assign f_dr[1]=fd_g_cfg_ready;
assign f_drv[1]=fd_g_cfg_rsp_valid;
assign fd_g_cfg_rsp_ready=f_drr[1];
assign fd_d_cfg_base=f_dp[4864+:64];
assign fd_d_cfg_nodes=f_dp[4928+:32];
assign f_drp[512+:3]=fd_d_cfg_status;
assign f_drp[515+:253]=0;
assign fd_d_cfg_valid=f_dv[2];
assign f_dr[2]=fd_d_cfg_ready;
assign f_drv[2]=fd_d_cfg_rsp_valid;
assign fd_d_cfg_rsp_ready=f_drr[2];
assign fd_t_cfg_rows_base=f_dp[7296+:64];
assign fd_t_cfg_columns_base=f_dp[7360+:64];
assign fd_t_cfg_rows=f_dp[7424+:32];
assign fd_t_cfg_columns=f_dp[7456+:32];
assign f_drp[768+:3]=fd_t_cfg_status;
assign f_drp[771+:253]=0;
assign fd_t_cfg_valid=f_dv[3];
assign f_dr[3]=fd_t_cfg_ready;
assign f_drv[3]=fd_t_cfg_rsp_valid;
assign fd_t_cfg_rsp_ready=f_drr[3];
assign fd_owner_cfg_primary=f_dp[9728+:64];
assign fd_owner_cfg_pool=f_dp[9792+:64];
assign fd_owner_cfg_allocator=f_dp[9856+:64];
assign fd_owner_cfg_nodes=f_dp[9920+:32];
assign fd_owner_cfg_capacity=f_dp[9952+:32];
assign f_drp[1024+:3]=fd_owner_cfg_status;
assign f_drp[1027+:253]=0;
assign fd_owner_cfg_valid=f_dv[4];
assign f_dr[4]=fd_owner_cfg_ready;
assign f_drv[4]=fd_owner_cfg_rsp_valid;
assign fd_owner_cfg_rsp_ready=f_drr[4];
assign fd_cs_cfg_history=f_dp[12160+:64];
assign fd_cs_cfg_prices=f_dp[12224+:64];
assign fd_cs_cfg_nets=f_dp[12288+:64];
assign fd_cs_cfg_design_id=f_dp[12352+:64];
assign fd_cs_cfg_nodes=f_dp[12416+:32];
assign fd_cs_cfg_net_count=f_dp[12448+:32];
assign fd_cs_cfg_version=f_dp[12480+:32];
assign f_drp[1280+:3]=fd_cs_cfg_status;
assign f_drp[1283+:253]=0;
assign fd_cs_cfg_valid=f_dv[5];
assign f_dr[5]=fd_cs_cfg_ready;
assign f_drv[5]=fd_cs_cfg_rsp_valid;
assign fd_cs_cfg_rsp_ready=f_drr[5];
assign fd_host_ctrl_op=f_dp[14592+:2];
assign fd_host_ctrl_query=f_dp[14594+:2];
assign fd_host_ctrl_price=f_dp[14596+:4];
assign fd_host_ctrl_version=f_dp[14600+:32];
assign f_drp[1536+:4]=fd_host_ctrl_status;
assign f_drp[1540+:252]=0;
assign fd_host_ctrl_valid=f_dv[6];
assign f_dr[6]=fd_host_ctrl_ready;
assign f_drv[6]=fd_host_ctrl_rsp_valid;
assign fd_host_ctrl_rsp_ready=f_drr[6];
assign fd_host_design_req_op=f_dp[17024+:3];
assign fd_host_design_req_cookie=f_dp[17027+:32];
assign fd_host_design_req_owner=f_dp[17059+:32];
assign fd_host_design_req_node=f_dp[17091+:32];
assign fd_host_design_req_arg=f_dp[17123+:32];
assign f_drp[1792+:4]=fd_host_design_rsp_status;
assign f_drp[1796+:32]=fd_host_design_rsp_cookie;
assign f_drp[1828+:32]=fd_host_design_rsp_flags;
assign f_drp[1860+:32]=fd_host_design_rsp_count;
assign f_drp[1892+:32]=fd_host_design_rsp_mask;
assign f_drp[1924+:124]=0;
assign fd_host_design_req_valid=f_dv[7];
assign f_dr[7]=fd_host_design_req_ready;
assign f_drv[7]=fd_host_design_rsp_valid;
assign fd_host_design_rsp_ready=f_drr[7];
assign fd_host_io_write=f_dp[19456+:1];
assign fd_host_io_node=f_dp[19457+:32];
assign fd_host_io_value=f_dp[19489+:32];
assign fd_host_io_field=f_dp[19521+:3];
assign f_drp[2048+:4]=fd_host_io_status;
assign f_drp[2052+:1]=fd_host_io_present;
assign f_drp[2053+:160]=fd_host_io_payload;
assign f_drp[2213+:91]=0;
assign fd_host_io_valid=f_dv[8];
assign f_dr[8]=fd_host_io_ready;
assign f_drv[8]=fd_host_io_rsp_valid;
assign fd_host_io_rsp_ready=f_drr[8];
assign fd_host_owner_req_op=f_dp[21888+:3];
assign fd_host_owner_req_cookie=f_dp[21891+:32];
assign fd_host_owner_req_node=f_dp[21923+:32];
assign fd_host_owner_req_net=f_dp[21955+:32];
assign f_drp[2304+:4]=fd_host_owner_rsp_status;
assign f_drp[2308+:32]=fd_host_owner_rsp_cookie;
assign f_drp[2340+:32]=fd_host_owner_rsp_count;
assign f_drp[2372+:32]=fd_host_owner_rsp_occupancy;
assign f_drp[2404+:1]=fd_host_owner_rsp_will_overuse;
assign f_drp[2405+:155]=0;
assign fd_host_owner_req_valid=f_dv[9];
assign f_dr[9]=fd_host_owner_req_ready;
assign f_drv[9]=fd_host_owner_rsp_valid;
assign fd_host_owner_rsp_ready=f_drr[9];
assign fd_cc_req_words=f_dp[24320+:128];
assign fd_cc_req_cookie=f_dp[24448+:32];
assign fd_cc_req_version=f_dp[24480+:32];
assign fd_cc_req_design_id=f_dp[24512+:64];
assign fd_cc_req_query=f_dp[24576+:2];
assign fd_cc_req_price=f_dp[24578+:4];
assign f_drp[2560+:64]=fd_cc_rsp_words;
assign f_drp[2624+:32]=fd_cc_rsp_cookie;
assign f_drp[2656+:32]=fd_cc_rsp_version;
assign f_drp[2688+:64]=fd_cc_rsp_design_id;
assign f_drp[2752+:2]=fd_cc_rsp_query;
assign f_drp[2754+:2]=fd_cc_rsp_status;
assign f_drp[2756+:4]=fd_cc_rsp_price;
assign f_drp[2760+:56]=0;
assign fd_cc_req_valid=f_dv[10];
assign f_dr[10]=fd_cc_req_ready;
assign f_drv[10]=fd_cc_rsp_valid;
assign fd_cc_rsp_ready=f_drr[10];
assign fd_expand_connection=f_dp[26752+:32];
assign fd_expand_cookie=f_dp[26784+:32];
assign fd_expand_parent=f_dp[26816+:32];
assign fd_expand_prune=f_dp[26848+:32];
assign fd_expand_has_laguna=f_dp[26880+:32];
assign fd_expand_sink=f_dp[26912+:32];
assign fd_expand_net=f_dp[26944+:32];
assign fd_expand_sequence=f_dp[26976+:32];
assign fd_expand_flags=f_dp[27008+:32];
assign fd_expand_xmin=f_dp[27040+:32];
assign fd_expand_xmax=f_dp[27072+:32];
assign fd_expand_ymin=f_dp[27104+:32];
assign fd_expand_ymax=f_dp[27136+:32];
assign fd_expand_version=f_dp[27168+:32];
assign f_drp[2816+:4]=fd_result_status;
assign f_drp[2820+:32]=fd_result_cookie;
assign f_drp[2852+:32]=fd_result_count;
assign f_drp[2884+:32]=fd_result_expanded_count;
assign f_drp[2916+:32]=fd_result_raw_count;
assign f_drp[2948+:32]=fd_result_mask;
assign f_drp[2980+:1]=fd_result_hit;
assign f_drp[2981+:1]=fd_result_early;
assign f_drp[2982+:90]=0;
assign fd_expand_valid=f_dv[11];
assign f_dr[11]=fd_expand_ready;
assign f_drv[11]=fd_result_valid;
assign fd_result_ready=f_drr[11];
assign fd_seed_op=f_dp[29184+:32];
assign fd_seed_key=f_dp[29216+:32];
assign fd_seed_id=f_dp[29248+:32];
assign fd_seed_cookie=f_dp[29280+:32];
assign fd_seed_version=f_dp[29312+:32];
assign f_drp[3072+:32]=fd_seed_rsp_status;
assign f_drp[3104+:32]=fd_seed_rsp_cookie;
assign f_drp[3136+:32]=fd_seed_rsp_size;
assign f_drp[3168+:32]=fd_seed_rsp_key;
assign f_drp[3200+:32]=fd_seed_rsp_id;
assign f_drp[3232+:96]=0;
assign fd_seed_valid=f_dv[12];
assign f_dr[12]=fd_seed_ready;
assign f_drv[12]=fd_seed_rsp_valid;
assign fd_seed_rsp_ready=f_drr[12];
assign fd_cs_req_host=f_dp[31616+:1];
assign fd_cs_req_op=f_dp[31617+:3];
assign fd_cs_req_cookie=f_dp[31620+:32];
assign fd_cs_req_index=f_dp[31652+:32];
assign fd_cs_req_value=f_dp[31684+:32];
assign fd_cs_req_version=f_dp[31716+:32];
assign fd_cs_req_query=f_dp[31748+:2];
assign fd_cs_req_price=f_dp[31750+:4];
assign f_drp[3328+:4]=fd_cs_rsp_status;
assign f_drp[3332+:32]=fd_cs_rsp_cookie;
assign f_drp[3364+:32]=fd_cs_rsp_index;
assign f_drp[3396+:32]=fd_cs_rsp_version;
assign f_drp[3428+:3]=fd_cs_rsp_op;
assign f_drp[3431+:1]=fd_cs_rsp_host;
assign f_drp[3432+:2]=fd_cs_rsp_query;
assign f_drp[3434+:4]=fd_cs_rsp_price;
assign f_drp[3438+:128]=fd_cs_rsp_data;
assign f_drp[3566+:18]=0;
assign fd_cs_req_valid=f_dv[13];
assign f_dr[13]=fd_cs_req_ready;
assign f_drv[13]=fd_cs_rsp_valid;
assign fd_cs_rsp_ready=f_drr[13];
assign fd_fa_authoritative=f_dp[34048+:1];
assign fd_fa_design=f_dp[34049+:64];
assign fd_fa_checkpoint=f_dp[34113+:32];
assign fd_fa_version=f_dp[34145+:32];
assign fd_fa_query=f_dp[34177+:2];
assign fd_fa_price=f_dp[34179+:4];
assign f_drp[3584+:1]=fd_k_cfg_status;
assign f_drp[3585+:255]=0;
assign fd_k_cfg_valid=f_dv[14];
assign f_dr[14]=fd_k_cfg_ready;
assign f_drv[14]=fd_k_cfg_rsp_valid;
assign fd_k_cfg_rsp_ready=f_drr[14];
assign fd_fc_payload=f_dp[36480+:2304];
assign fd_fc_design=f_dp[38784+:64];
assign fd_fc_checkpoint=f_dp[38848+:32];
assign fd_fc_authoritative=f_dp[38880+:1];
assign f_drp[3840+:1]=fd_cf_load_status;
assign f_drp[3841+:255]=0;
assign fd_cf_load_valid=f_dv[15];
assign f_dr[15]=fd_cf_load_ready;
assign f_drv[15]=fd_cf_load_rsp_valid;
assign fd_cf_load_rsp_ready=f_drr[15];
assign f_cbv={6'd0,k_o_valid,lr_l_valid,1'b0,lr_c_valid,cf_valid};
assign cf_ready=f_cbr[5:0];
assign cf_replies=f_cbrv[5:0];
assign f_cbp[0+:384]=cf_payload[0+:384];
assign f_cbp[384+:2048]=0;
assign cf_status[0+:3]=f_cbrp[0+:3];
assign f_cbrr[0]=cf_reply_ready[0];
assign f_cbp[2432+:384]=cf_payload[384+:384];
assign f_cbp[2816+:2048]=0;
assign cf_status[3+:3]=f_cbrp[256+:3];
assign f_cbrr[1]=cf_reply_ready[1];
assign f_cbp[4864+:384]=cf_payload[768+:384];
assign f_cbp[5248+:2048]=0;
assign cf_status[6+:3]=f_cbrp[512+:3];
assign f_cbrr[2]=cf_reply_ready[2];
assign f_cbp[7296+:384]=cf_payload[1152+:384];
assign f_cbp[7680+:2048]=0;
assign cf_status[9+:3]=f_cbrp[768+:3];
assign f_cbrr[3]=cf_reply_ready[3];
assign f_cbp[9728+:384]=cf_payload[1536+:384];
assign f_cbp[10112+:2048]=0;
assign cf_status[12+:3]=f_cbrp[1024+:3];
assign f_cbrr[4]=cf_reply_ready[4];
assign f_cbp[12160+:384]=cf_payload[1920+:384];
assign f_cbp[12544+:2048]=0;
assign cf_status[15+:3]=f_cbrp[1280+:3];
assign f_cbrr[5]=cf_reply_ready[5];
assign f_cbp[14592+:2]=lr_c_op;
assign f_cbp[14594+:2]=lr_c_query;
assign f_cbp[14596+:4]=lr_c_price;
assign f_cbp[14600+:32]=lr_c_version;
assign f_cbp[14632+:2392]=0;
assign f_cbrr[6]=lr_c_rsp_ready;
assign f_cbp[17024+:2432]=0;
assign f_cbrr[7]=1'b0;
assign f_cbp[19456+:1]=lr_l_write;
assign f_cbp[19457+:32]=lr_l_node;
assign f_cbp[19489+:32]=lr_l_value;
assign f_cbp[19521+:3]=lr_l_field;
assign f_cbp[19524+:2364]=0;
assign f_cbrr[8]=lr_l_rsp_ready;
assign f_cbp[21888+:3]=k_o_op;
assign f_cbp[21891+:32]=k_o_cookie;
assign f_cbp[21923+:32]=k_o_node;
assign f_cbp[21955+:32]=k_o_net;
assign f_cbp[21987+:2333]=0;
assign f_cbrr[9]=k_o_rsp_ready;
assign f_cbp[24320+:2432]=0;
assign f_cbrr[10]=1'b0;
assign f_cbp[26752+:2432]=0;
assign f_cbrr[11]=1'b0;
assign f_cbp[29184+:2432]=0;
assign f_cbrr[12]=1'b0;
assign f_cbp[31616+:2432]=0;
assign f_cbrr[13]=1'b0;
assign f_cbp[34048+:2432]=0;
assign f_cbrr[14]=1'b0;
assign f_cbp[36480+:2432]=0;
assign f_cbrr[15]=1'b0;
assign lr_c_ready=f_cbr[6];
assign lr_l_ready=f_cbr[8];
assign lr_l_rsp_valid=f_cbrv[8];
assign k_o_ready=f_cbr[9];
assign k_o_rsp_valid=f_cbrv[9];
assign f_all_drained=label_drained&&owner_drained&&(&f_watch_idle)&&!(|f_watch_fault);
assign rst=k_cold_rst||k_target_reset;
assign lr_start_valid=k_labels_valid;
assign lr_rsp_ready=!k_labels_valid;
candidate_recursive_engine #(.SLOTS(SLOTS),.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS))dut(.q_cfg_valid(fd_q_cfg_valid),.q_cfg_ready(fd_q_cfg_ready),.q_cfg_rsp_valid(fd_q_cfg_rsp_valid),.q_cfg_rsp_ready(fd_q_cfg_rsp_ready),.q_cfg_base(fd_q_cfg_base),.q_cfg_design(fd_q_cfg_design),.q_cfg_connections(fd_q_cfg_connections),.q_cfg_nodes(fd_q_cfg_nodes),.q_cfg_nets(fd_q_cfg_nets),.q_cfg_revision(fd_q_cfg_revision),.q_cfg_status(fd_q_cfg_status),.g_cfg_valid(fd_g_cfg_valid),.g_cfg_ready(fd_g_cfg_ready),.g_cfg_rsp_valid(fd_g_cfg_rsp_valid),.g_cfg_rsp_ready(fd_g_cfg_rsp_ready),.g_cfg_offsets_base(fd_g_cfg_offsets_base),.g_cfg_edges_base(fd_g_cfg_edges_base),.g_cfg_attrs_base(fd_g_cfg_attrs_base),.g_cfg_nodes(fd_g_cfg_nodes),.g_cfg_edges(fd_g_cfg_edges),.g_cfg_status(fd_g_cfg_status),.d_cfg_valid(fd_d_cfg_valid),.d_cfg_ready(fd_d_cfg_ready),.d_cfg_rsp_valid(fd_d_cfg_rsp_valid),.d_cfg_rsp_ready(fd_d_cfg_rsp_ready),.d_cfg_base(fd_d_cfg_base),.d_cfg_nodes(fd_d_cfg_nodes),.d_cfg_status(fd_d_cfg_status),.t_cfg_valid(fd_t_cfg_valid),.t_cfg_ready(fd_t_cfg_ready),.t_cfg_rsp_valid(fd_t_cfg_rsp_valid),.t_cfg_rsp_ready(fd_t_cfg_rsp_ready),.t_cfg_rows_base(fd_t_cfg_rows_base),.t_cfg_columns_base(fd_t_cfg_columns_base),.t_cfg_rows(fd_t_cfg_rows),.t_cfg_columns(fd_t_cfg_columns),.t_cfg_status(fd_t_cfg_status),.owner_cfg_valid(fd_owner_cfg_valid),.owner_cfg_ready(fd_owner_cfg_ready),.owner_cfg_rsp_valid(fd_owner_cfg_rsp_valid),.owner_cfg_rsp_ready(fd_owner_cfg_rsp_ready),.owner_cfg_primary(fd_owner_cfg_primary),.owner_cfg_pool(fd_owner_cfg_pool),.owner_cfg_allocator(fd_owner_cfg_allocator),.owner_cfg_nodes(fd_owner_cfg_nodes),.owner_cfg_capacity(fd_owner_cfg_capacity),.owner_cfg_status(fd_owner_cfg_status),.cs_cfg_valid(fd_cs_cfg_valid),.cs_cfg_ready(fd_cs_cfg_ready),.cs_cfg_rsp_valid(fd_cs_cfg_rsp_valid),.cs_cfg_rsp_ready(fd_cs_cfg_rsp_ready),.cs_cfg_history(fd_cs_cfg_history),.cs_cfg_prices(fd_cs_cfg_prices),.cs_cfg_nets(fd_cs_cfg_nets),.cs_cfg_design_id(fd_cs_cfg_design_id),.cs_cfg_nodes(fd_cs_cfg_nodes),.cs_cfg_net_count(fd_cs_cfg_net_count),.cs_cfg_version(fd_cs_cfg_version),.cs_cfg_status(fd_cs_cfg_status),.host_ctrl_valid(fd_host_ctrl_valid),.host_ctrl_ready(fd_host_ctrl_ready),.host_ctrl_rsp_valid(fd_host_ctrl_rsp_valid),.host_ctrl_rsp_ready(fd_host_ctrl_rsp_ready),.host_ctrl_op(fd_host_ctrl_op),.host_ctrl_query(fd_host_ctrl_query),.host_ctrl_price(fd_host_ctrl_price),.host_ctrl_version(fd_host_ctrl_version),.host_ctrl_status(fd_host_ctrl_status),.host_design_req_valid(fd_host_design_req_valid),.host_design_req_ready(fd_host_design_req_ready),.host_design_rsp_valid(fd_host_design_rsp_valid),.host_design_rsp_ready(fd_host_design_rsp_ready),.host_design_req_op(fd_host_design_req_op),.host_design_req_cookie(fd_host_design_req_cookie),.host_design_req_owner(fd_host_design_req_owner),.host_design_req_node(fd_host_design_req_node),.host_design_req_arg(fd_host_design_req_arg),.host_design_rsp_status(fd_host_design_rsp_status),.host_design_rsp_cookie(fd_host_design_rsp_cookie),.host_design_rsp_flags(fd_host_design_rsp_flags),.host_design_rsp_count(fd_host_design_rsp_count),.host_design_rsp_mask(fd_host_design_rsp_mask),.cc_req_valid(fd_cc_req_valid),.cc_req_ready(fd_cc_req_ready),.cc_rsp_valid(fd_cc_rsp_valid),.cc_rsp_ready(fd_cc_rsp_ready),.cc_req_words(fd_cc_req_words),.cc_req_cookie(fd_cc_req_cookie),.cc_req_version(fd_cc_req_version),.cc_req_design_id(fd_cc_req_design_id),.cc_req_query(fd_cc_req_query),.cc_req_price(fd_cc_req_price),.cc_rsp_words(fd_cc_rsp_words),.cc_rsp_cookie(fd_cc_rsp_cookie),.cc_rsp_version(fd_cc_rsp_version),.cc_rsp_design_id(fd_cc_rsp_design_id),.cc_rsp_query(fd_cc_rsp_query),.cc_rsp_status(fd_cc_rsp_status),.cc_rsp_price(fd_cc_rsp_price),.expand_valid(fd_expand_valid),.expand_ready(fd_expand_ready),.result_valid(fd_result_valid),.result_ready(fd_result_ready),.expand_connection(fd_expand_connection),.expand_cookie(fd_expand_cookie),.expand_parent(fd_expand_parent),.expand_prune(fd_expand_prune),.expand_has_laguna(fd_expand_has_laguna),.expand_sink(fd_expand_sink),.expand_net(fd_expand_net),.expand_sequence(fd_expand_sequence),.expand_flags(fd_expand_flags),.expand_xmin(fd_expand_xmin),.expand_xmax(fd_expand_xmax),.expand_ymin(fd_expand_ymin),.expand_ymax(fd_expand_ymax),.expand_version(fd_expand_version),.result_status(fd_result_status),.result_cookie(fd_result_cookie),.result_count(fd_result_count),.result_expanded_count(fd_result_expanded_count),.result_raw_count(fd_result_raw_count),.result_mask(fd_result_mask),.result_hit(fd_result_hit),.result_early(fd_result_early),.seed_valid(fd_seed_valid),.seed_ready(fd_seed_ready),.seed_rsp_valid(fd_seed_rsp_valid),.seed_rsp_ready(fd_seed_rsp_ready),.seed_op(fd_seed_op),.seed_key(fd_seed_key),.seed_id(fd_seed_id),.seed_cookie(fd_seed_cookie),.seed_version(fd_seed_version),.seed_rsp_status(fd_seed_rsp_status),.seed_rsp_cookie(fd_seed_rsp_cookie),.seed_rsp_size(fd_seed_rsp_size),.seed_rsp_key(fd_seed_rsp_key),.seed_rsp_id(fd_seed_rsp_id),.cs_req_valid(fd_cs_req_valid),.cs_req_ready(fd_cs_req_ready),.cs_rsp_valid(fd_cs_rsp_valid),.cs_rsp_ready(fd_cs_rsp_ready),.cs_req_host(fd_cs_req_host),.cs_req_op(fd_cs_req_op),.cs_req_cookie(fd_cs_req_cookie),.cs_req_index(fd_cs_req_index),.cs_req_value(fd_cs_req_value),.cs_req_version(fd_cs_req_version),.cs_req_query(fd_cs_req_query),.cs_req_price(fd_cs_req_price),.cs_rsp_status(fd_cs_rsp_status),.cs_rsp_cookie(fd_cs_rsp_cookie),.cs_rsp_index(fd_cs_rsp_index),.cs_rsp_version(fd_cs_rsp_version),.cs_rsp_op(fd_cs_rsp_op),.cs_rsp_host(fd_cs_rsp_host),.cs_rsp_query(fd_cs_rsp_query),.cs_rsp_price(fd_cs_rsp_price),.cs_rsp_data(fd_cs_rsp_data),.retired_idle(f_backend_idle),.host_io_valid(b_l_valid),.host_io_ready(b_l_ready),.host_io_write(b_l_write),.host_io_node(b_l_node),.host_io_value(b_l_value),.host_io_field(b_l_field),.host_io_rsp_valid(b_l_rsp_valid),.host_io_rsp_ready(b_l_rsp_ready),.host_io_status(b_l_status),.host_io_present(b_l_present),.host_io_payload(b_l_payload),.host_owner_req_valid(b_o_valid),.host_owner_req_ready(b_o_ready),.host_owner_req_op(b_o_op),.host_owner_req_node(b_o_node),.host_owner_req_net(b_o_net),.host_owner_req_cookie(b_o_cookie),.host_owner_rsp_valid(b_o_rsp_valid),.host_owner_rsp_ready(b_o_rsp_ready),.host_owner_rsp_status(b_o_status),.host_owner_rsp_cookie(b_o_rsp_cookie),.host_owner_rsp_count(b_o_count),.host_owner_rsp_occupancy(b_o_occupancy),.host_owner_rsp_will_overuse(b_o_will_overuse),.out_offer_valid(out_offer_valid),.out_offer_status(out_offer_status),.out_offer_key(out_offer_key),.out_offer_node(out_offer_node),.out_offer_before(out_offer_before),.out_offer_size(out_offer_size),.out_commit_valid(out_commit_valid),.out_commit_status(out_commit_status),.out_commit_acked(out_commit_acked),.out_commit_payload(out_commit_payload),.out_cost_valid(out_cost_valid),.out_cost_status(out_cost_status),.out_cost_words(out_cost_words),.out_cost_packet(out_cost_packet),.out_cost_geometry(out_cost_geometry),.out_cost_geometry_result(out_cost_geometry_result),.q_configured(q_configured),.out_params_valid(out_params_valid),.out_params(out_params),.out_connection(out_connection),.out_profile_revision(out_profile_revision),.q_busy(q_busy),.q_fault(q_fault),.q_m_araddr(q_m_araddr),.q_m_arlen(q_m_arlen),.q_m_arsize(q_m_arsize),.q_m_arburst(q_m_arburst),.q_m_arid(q_m_arid),.q_m_arvalid(q_m_arvalid),.q_m_arready(q_m_arready),.q_m_rdata(q_m_rdata),.q_m_rid(q_m_rid),.q_m_rresp(q_m_rresp),.q_m_rlast(q_m_rlast),.q_m_rvalid(q_m_rvalid),.q_m_rready(q_m_rready),.out_post_valid(out_post_valid),.out_post_status(out_post_status),.out_post_x(out_post_x),.out_post_y(out_post_y),.out_post_upstream(out_post_upstream),.out_post_distance(out_post_distance),.out_post_attrs(out_post_attrs),.out_post_prev_read(out_post_prev_read),.out_prep_valid(out_prep_valid),.out_prep_count(out_prep_count),.out_prep_occupancy(out_prep_occupancy),.out_prep_price_index(out_prep_price_index),.out_prep_history(out_prep_history),.out_prep_price_value(out_prep_price_value),.out_prep_net_data(out_prep_net_data),.out_prep_status(out_prep_status),.cc_busy(cc_busy),.cc_fault(cc_fault),.operation_pending(operation_pending),.clk(clk),.rst(rst),.abort(abort),.g_configured(g_configured),.g_m_araddr(g_m_araddr),.g_m_arlen(g_m_arlen),.g_m_arsize(g_m_arsize),.g_m_arburst(g_m_arburst),.g_m_arid(g_m_arid),.g_m_arvalid(g_m_arvalid),.g_m_arready(g_m_arready),.g_m_rdata(g_m_rdata),.g_m_rid(g_m_rid),.g_m_rresp(g_m_rresp),.g_m_rlast(g_m_rlast),.g_m_rvalid(g_m_rvalid),.g_m_rready(g_m_rready),.d_configured(d_configured),.d_m_araddr(d_m_araddr),.d_m_arlen(d_m_arlen),.d_m_arsize(d_m_arsize),.d_m_arburst(d_m_arburst),.d_m_arid(d_m_arid),.d_m_arvalid(d_m_arvalid),.d_m_arready(d_m_arready),.d_m_rdata(d_m_rdata),.d_m_rid(d_m_rid),.d_m_rresp(d_m_rresp),.d_m_rlast(d_m_rlast),.d_m_rvalid(d_m_rvalid),.d_m_rready(d_m_rready),.d_m_awaddr(d_m_awaddr),.d_m_awlen(d_m_awlen),.d_m_awsize(d_m_awsize),.d_m_awburst(d_m_awburst),.d_m_awid(d_m_awid),.d_m_awvalid(d_m_awvalid),.d_m_awready(d_m_awready),.d_m_wdata(d_m_wdata),.d_m_wstrb(d_m_wstrb),.d_m_wlast(d_m_wlast),.d_m_wvalid(d_m_wvalid),.d_m_wready(d_m_wready),.d_m_bid(d_m_bid),.d_m_bresp(d_m_bresp),.d_m_bvalid(d_m_bvalid),.d_m_bready(d_m_bready),.p_active(p_active),.p_active_query(p_active_query),.p_active_price(p_active_price),.p_m_awaddr(p_m_awaddr),.p_m_awlen(p_m_awlen),.p_m_awsize(p_m_awsize),.p_m_awburst(p_m_awburst),.p_m_awid(p_m_awid),.p_m_awvalid(p_m_awvalid),.p_m_awready(p_m_awready),.p_m_wdata(p_m_wdata),.p_m_wstrb(p_m_wstrb),.p_m_wlast(p_m_wlast),.p_m_wvalid(p_m_wvalid),.p_m_wready(p_m_wready),.p_m_bid(p_m_bid),.p_m_bresp(p_m_bresp),.p_m_bvalid(p_m_bvalid),.p_m_bready(p_m_bready),.p_m_araddr(p_m_araddr),.p_m_arlen(p_m_arlen),.p_m_arsize(p_m_arsize),.p_m_arburst(p_m_arburst),.p_m_arid(p_m_arid),.p_m_arvalid(p_m_arvalid),.p_m_arready(p_m_arready),.p_m_rdata(p_m_rdata),.p_m_rid(p_m_rid),.p_m_rresp(p_m_rresp),.p_m_rlast(p_m_rlast),.p_m_rvalid(p_m_rvalid),.p_m_rready(p_m_rready),.t_configured(t_configured),.t_m_araddr(t_m_araddr),.t_m_arlen(t_m_arlen),.t_m_arsize(t_m_arsize),.t_m_arburst(t_m_arburst),.t_m_arid(t_m_arid),.t_m_arvalid(t_m_arvalid),.t_m_arready(t_m_arready),.t_m_rdata(t_m_rdata),.t_m_rid(t_m_rid),.t_m_rresp(t_m_rresp),.t_m_rlast(t_m_rlast),.t_m_rvalid(t_m_rvalid),.t_m_rready(t_m_rready),.owner_configured(owner_configured),.owner_m_araddr(owner_m_araddr),.owner_m_arlen(owner_m_arlen),.owner_m_arsize(owner_m_arsize),.owner_m_arburst(owner_m_arburst),.owner_m_arid(owner_m_arid),.owner_m_arvalid(owner_m_arvalid),.owner_m_arready(owner_m_arready),.owner_m_rdata(owner_m_rdata),.owner_m_rid(owner_m_rid),.owner_m_rresp(owner_m_rresp),.owner_m_rlast(owner_m_rlast),.owner_m_rvalid(owner_m_rvalid),.owner_m_rready(owner_m_rready),.owner_m_awaddr(owner_m_awaddr),.owner_m_awlen(owner_m_awlen),.owner_m_awsize(owner_m_awsize),.owner_m_awburst(owner_m_awburst),.owner_m_awid(owner_m_awid),.owner_m_awvalid(owner_m_awvalid),.owner_m_awready(owner_m_awready),.owner_m_wdata(owner_m_wdata),.owner_m_wstrb(owner_m_wstrb),.owner_m_wlast(owner_m_wlast),.owner_m_wvalid(owner_m_wvalid),.owner_m_wready(owner_m_wready),.owner_m_bid(owner_m_bid),.owner_m_bresp(owner_m_bresp),.owner_m_bvalid(owner_m_bvalid),.owner_m_bready(owner_m_bready),.out_valid(out_valid),.out_ready(out_ready),.out_cookie(out_cookie),.out_node(out_node),.out_position(out_position),.out_sequence(out_sequence),.out_bits(out_bits),.out_action(out_action),.out_steps(out_steps),.out_services(out_services),.out_attrs(out_attrs),.out_config(out_config),.fault(fault),.busy(busy),.design_id(design_id),.query_version(query_version),.query_ready(query_ready),.cost_lease(cost_lease),.cs_configured(cs_configured),.cs_ready_for_query(cs_ready_for_query),.cs_editing(cs_editing),.cs_published_version(cs_published_version),.cs_design_id(cs_design_id),.cs_busy(cs_busy),.cs_fault(cs_fault),.cs_m_araddr(cs_m_araddr),.cs_m_arlen(cs_m_arlen),.cs_m_arsize(cs_m_arsize),.cs_m_arburst(cs_m_arburst),.cs_m_arid(cs_m_arid),.cs_m_arvalid(cs_m_arvalid),.cs_m_arready(cs_m_arready),.cs_m_rdata(cs_m_rdata),.cs_m_rid(cs_m_rid),.cs_m_rresp(cs_m_rresp),.cs_m_rlast(cs_m_rlast),.cs_m_rvalid(cs_m_rvalid),.cs_m_rready(cs_m_rready),.cs_m_awaddr(cs_m_awaddr),.cs_m_awlen(cs_m_awlen),.cs_m_awsize(cs_m_awsize),.cs_m_awburst(cs_m_awburst),.cs_m_awid(cs_m_awid),.cs_m_awvalid(cs_m_awvalid),.cs_m_awready(cs_m_awready),.cs_m_wdata(cs_m_wdata),.cs_m_wstrb(cs_m_wstrb),.cs_m_wlast(cs_m_wlast),.cs_m_wvalid(cs_m_wvalid),.cs_m_wready(cs_m_wready),.cs_m_bid(cs_m_bid),.cs_m_bresp(cs_m_bresp),.cs_m_bvalid(cs_m_bvalid),.cs_m_bready(cs_m_bready));
route_commit_host_adapter #(.MAX_PATH(32)) route_join(.cp_valid(cp_valid),.cp_restore(cp_restore),.cp_ready(cp_ready),.cp_busy(cp_busy),.cp_rsp_valid(cp_rsp_valid),.cp_rsp_ready(cp_rsp_ready),.cp_status(cp_status),.cp_crc(cp_crc),.cp_design(cp_design),.cp_nodes(cp_nodes),.cp_nets(cp_nets),.cp_expected_crc(cp_expected_crc),.cp_s_valid(cp_s_valid),.cp_s_ready(cp_s_ready),.cp_s_index(cp_s_index),.cp_s_data(cp_s_data),.cp_s_last(cp_s_last),.cp_m_valid(cp_m_valid),.cp_m_ready(cp_m_ready),.cp_m_index(cp_m_index),.cp_m_data(cp_m_data),.cp_m_last(cp_m_last),.cp_test_reset(cp_test_reset),.pc_route_retired(pc_route_retired),.pc_hold(pc_hold),.pc_safe(pc_safe),.clk(clk),.rst(rst),.abort(ENABLE_TEST_INJECTION?test_route_abort:1'b0),.active(p_active),.backend_drained(f_all_drained),.j_valid(k_j_valid),.j_ready(k_j_ready),.j_node(k_j_node),.j_net(k_j_net),.j_op(k_j_op),.admit(!fault&&!busy),.active_query(p_active_query),.active_price(p_active_price),.active_version(query_version^((ENABLE_TEST_INJECTION&&test_route_version_flip)?32'd1:32'd0)),.active_design(design_id),.req_valid(f_broute_valid),.req_ready(f_broute_ready),.req_op(f_broute_payload[0+:1]),.req_slot(f_broute_payload[1+:1]),.req_cookie(f_broute_payload[2+:32]),.req_source(f_broute_payload[34+:32]),.req_sink(f_broute_payload[66+:32]),.req_net(f_broute_payload[98+:32]),.req_sequence(f_broute_payload[130+:32]),.rsp_valid(f_broute_rsp_valid),.rsp_ready(f_broute_rsp_ready),.rsp_status(rc_rsp_status),.rsp_cookie(rc_rsp_cookie),.rsp_nodes(rc_rsp_nodes),.rsp_acked(rc_rsp_acked),.busy(rc_busy),.fault(rc_fault),.block_external(rc_block),.slot_valid(rc_slots),.h_l_valid(fd_host_io_valid),.b_l_valid(b_l_valid),.h_l_ready(fd_host_io_ready),.b_l_ready(b_l_ready),.h_l_write(fd_host_io_write),.b_l_write(b_l_write),.h_l_node(fd_host_io_node),.b_l_node(b_l_node),.h_l_value(fd_host_io_value),.b_l_value(b_l_value),.h_l_field(fd_host_io_field),.b_l_field(b_l_field),.h_l_rsp_valid(fd_host_io_rsp_valid),.b_l_rsp_valid(b_l_rsp_valid),.h_l_rsp_ready(fd_host_io_rsp_ready),.b_l_rsp_ready(b_l_rsp_ready),.h_l_status(fd_host_io_status),.b_l_status(b_l_status),.h_l_present(fd_host_io_present),.b_l_present(b_l_present),.h_l_payload(fd_host_io_payload),.b_l_payload(b_l_payload),.h_o_valid(fd_host_owner_req_valid),.b_o_valid(b_o_valid),.h_o_ready(fd_host_owner_req_ready),.b_o_ready(b_o_ready),.h_o_op(fd_host_owner_req_op),.b_o_op(b_o_op),.h_o_node(fd_host_owner_req_node),.b_o_node(b_o_node),.h_o_net(fd_host_owner_req_net),.b_o_net(b_o_net),.h_o_cookie(fd_host_owner_req_cookie),.b_o_cookie(b_o_cookie),.h_o_rsp_valid(fd_host_owner_rsp_valid),.b_o_rsp_valid(b_o_rsp_valid),.h_o_rsp_ready(fd_host_owner_rsp_ready),.b_o_rsp_ready(b_o_rsp_ready),.h_o_status(fd_host_owner_rsp_status),.b_o_status(b_o_status),.h_o_rsp_cookie(fd_host_owner_rsp_cookie),.b_o_rsp_cookie(b_o_rsp_cookie),.h_o_count(fd_host_owner_rsp_count),.b_o_count(b_o_count),.h_o_occupancy(fd_host_owner_rsp_occupancy),.b_o_occupancy(b_o_occupancy),.h_o_will_overuse(fd_host_owner_rsp_will_overuse),.b_o_will_overuse(b_o_will_overuse));
recovery_coordinator #(.ENTRIES(32),.RESET_HOLD(5),.MAX_CYCLES(1048576)) recovery_ctl(.retry_safe(k_retry_safe),.attempt_reset(k_attempt_reset),.clk(clk),.cold_rst(k_cold_rst),.abort(f_fault||cf_fault||(cf_rsp_valid&&cf_rsp_cookie!=32'hf0010001)||lr_fault||(lr_rsp_valid&&lr_rsp_cookie!=snapshot_cookie_held)),.backend_drained(f_all_drained),.normal_retired(f_normal_retired),.cfg_valid(fd_k_cfg_valid),.cfg_ready(fd_k_cfg_ready),.cfg_authoritative(fd_fa_authoritative),.cfg_design(fd_fa_design),.cfg_checkpoint(fd_fa_checkpoint),.cfg_version(fd_fa_version),.cfg_query(fd_fa_query),.cfg_price(fd_fa_price),.cfg_rsp_valid(fd_k_cfg_rsp_valid),.cfg_rsp_ready(fd_k_cfg_rsp_ready),.cfg_status(fd_k_cfg_status),.j_valid(k_j_valid),.j_ready(k_j_ready),.j_node(k_j_node),.j_net(k_j_net),.j_op(k_j_op),.journal_count(k_count),.journal_full(k_full),.permit_work(k_permit),.recover_valid(f_brecover_valid),.recover_ready(f_brecover_ready),.recover_cookie(recover_cookie),.recover_checkpoint(recover_checkpoint),.recover_version(recover_version),.recover_design(recover_design),.recover_query(recover_query),.recover_price(recover_price),.target_reset(k_target_reset),.reconfigure_valid(k_rcfg_valid),.reconfigure_done(k_rcfg_done),.labels_valid(k_labels_valid),.labels_done(k_labels_done),.saved_design(k_saved_design),.saved_checkpoint(k_saved_checkpoint),.new_version(k_new_version),.new_query(k_new_query),.new_price(k_new_price),.rsp_valid(f_brecover_rsp_valid),.rsp_ready(f_brecover_rsp_ready),.rsp_status(k_rsp_status),.rsp_cookie(k_rsp_cookie),.rsp_corrected(k_corrected),.busy(k_busy),.fault(k_fault),.a_valid(k_a_valid),.a_ready(k_a_ready),.a_node(k_a_node),.a_net(k_a_net),.a_cookie(k_a_cookie),.a_checkpoint(k_a_checkpoint),.a_design(k_a_design),.a_rsp_valid(k_a_rsp_valid),.a_rsp_ready(k_a_rsp_ready),.a_status(k_a_status),.a_rsp_cookie(k_a_rsp_cookie),.a_rsp_checkpoint(k_a_rsp_checkpoint),.a_rsp_design(k_a_rsp_design),.a_refs(k_a_refs),.a_occupancy(k_a_occ),.o_valid(k_o_valid),.o_ready(k_o_ready),.o_op(k_o_op),.o_node(k_o_node),.o_net(k_o_net),.o_cookie(k_o_cookie),.o_rsp_valid(k_o_rsp_valid),.o_rsp_ready(k_o_rsp_ready),.o_status(f_cbrp[2304+:4]),.o_rsp_cookie(f_cbrp[2308+:32]),.o_count(f_cbrp[2340+:32]),.o_occupancy(f_cbrp[2372+:32]));
config_restore_controller #(.MAX_CYCLES(1048576))config_restore(.attempt_reset(k_attempt_reset),.clk(clk),.rst(k_cold_rst),.abort(1'b0),.backend_drained(f_all_drained),.normal_retired(f_normal_retired),.load_valid(fd_cf_load_valid),.load_ready(fd_cf_load_ready),.load_authoritative(fd_fc_authoritative),.load_payload(fd_fc_payload),.load_design(fd_fc_design),.load_checkpoint(fd_fc_checkpoint),.load_rsp_valid(fd_cf_load_rsp_valid),.load_rsp_ready(fd_cf_load_rsp_ready),.load_status(fd_cf_load_status),.start_valid(k_rcfg_valid),.start_ready(),.start_design(k_saved_design),.start_checkpoint(k_saved_checkpoint),.start_cookie(32'hf0010001),.start_version(k_new_version),.start_price(k_new_price),.cfg_valid(cf_valid),.cfg_ready(cf_ready),.cfg_payload(cf_payload),.cfg_rsp_valid(cf_replies),.cfg_rsp_ready(cf_reply_ready),.cfg_status(cf_status),.rsp_valid(cf_rsp_valid),.rsp_ready(!k_rcfg_valid),.rsp_status(cf_rsp_status),.rsp_cookie(cf_rsp_cookie),.busy(cf_busy),.fault(cf_fault),.sent(cf_sent),.retired(cf_retired),.saved_design(cf_saved_design),.saved_checkpoint(cf_saved_checkpoint));
label_restore_controller #(.MAX_RECORDS(512),.MAX_CYCLES(1048576))label_restore(.clk(clk),.rst(k_cold_rst||k_attempt_reset),.abort(1'b0),.backend_drained(f_all_drained),.start_valid(lr_start_valid),.start_ready(lr_start_ready),.start_design(k_saved_design),.expected_design(snapshot_design_held),.start_checkpoint(k_saved_checkpoint),.expected_checkpoint(snapshot_checkpoint_held),.start_cookie(snapshot_cookie_held),.start_count(snapshot_count_held),.start_nodes(snapshot_nodes_held),.start_probe(snapshot_probe_held),.start_version(k_new_version),.start_query(k_new_query),.start_price(k_new_price),.s_valid(lr_s_valid),.s_ready(lr_s_ready),.s_node(lr_s_node),.s_cookie(lr_s_cookie),.s_payload(lr_s_payload),.s_last(lr_s_last),.rsp_valid(lr_rsp_valid),.rsp_ready(lr_rsp_ready),.rsp_status(lr_rsp_status),.rsp_cookie(lr_rsp_cookie),.written(lr_written),.verified(lr_verified),.busy(lr_busy),.fault(lr_fault),.c_valid(lr_c_valid),.c_ready(lr_c_ready),.c_op(lr_c_op),.c_query(lr_c_query),.c_price(lr_c_price),.c_version(lr_c_version),.c_rsp_valid(f_cbrv[6]),.c_rsp_ready(lr_c_rsp_ready),.c_status(f_cbrp[1536+:4]),.l_valid(lr_l_valid),.l_ready(lr_l_ready),.l_write(lr_l_write),.l_node(lr_l_node),.l_value(lr_l_value),.l_field(lr_l_field),.l_rsp_valid(lr_l_rsp_valid),.l_rsp_ready(lr_l_rsp_ready),.l_status(f_cbrp[2048+:4]),.l_present(f_cbrp[2052]),.l_payload(f_cbrp[2053+:160]));
axi_drain_watch label_watch(.clk(clk),.rst(rst),.arvalid(p_m_arvalid),.arready(p_m_arready),.arlen(p_m_arlen),.rvalid(p_m_rvalid),.rready(p_m_rready),.rlast(p_m_rlast),.awvalid(p_m_awvalid),.awready(p_m_awready),.awlen(p_m_awlen),.wvalid(p_m_wvalid),.wready(p_m_wready),.wlast(p_m_wlast),.bvalid(p_m_bvalid),.bready(p_m_bready),.drained(label_drained),.fault(label_watch_fault));
axi_drain_watch owner_watch(.clk(clk),.rst(rst),.arvalid(owner_m_arvalid),.arready(owner_m_arready),.arlen(owner_m_arlen),.rvalid(owner_m_rvalid),.rready(owner_m_rready),.rlast(owner_m_rlast),.awvalid(owner_m_awvalid),.awready(owner_m_awready),.awlen(owner_m_awlen),.wvalid(owner_m_wvalid),.wready(owner_m_wready),.wlast(owner_m_wlast),.bvalid(owner_m_bvalid),.bready(owner_m_bready),.drained(owner_drained),.fault(owner_watch_fault));
axi_drain_watch f_watch_g(.clk(clk),.rst(rst),.arvalid(g_m_arvalid),.arready(g_m_arready),.arlen(g_m_arlen),.rvalid(g_m_rvalid),.rready(g_m_rready),.rlast(g_m_rlast),.awvalid(1'b0),.awready(1'b0),.awlen(8'd0),.wvalid(1'b0),.wready(1'b0),.wlast(1'b0),.bvalid(1'b0),.bready(1'b0),.drained(f_watch_idle[0]),.fault(f_watch_fault[0]));
axi_drain_watch f_watch_d(.clk(clk),.rst(rst),.arvalid(d_m_arvalid),.arready(d_m_arready),.arlen(d_m_arlen),.rvalid(d_m_rvalid),.rready(d_m_rready),.rlast(d_m_rlast),.awvalid(d_m_awvalid),.awready(d_m_awready),.awlen(d_m_awlen),.wvalid(d_m_wvalid),.wready(d_m_wready),.wlast(d_m_wlast),.bvalid(d_m_bvalid),.bready(d_m_bready),.drained(f_watch_idle[1]),.fault(f_watch_fault[1]));
axi_drain_watch f_watch_t(.clk(clk),.rst(rst),.arvalid(t_m_arvalid),.arready(t_m_arready),.arlen(t_m_arlen),.rvalid(t_m_rvalid),.rready(t_m_rready),.rlast(t_m_rlast),.awvalid(1'b0),.awready(1'b0),.awlen(8'd0),.wvalid(1'b0),.wready(1'b0),.wlast(1'b0),.bvalid(1'b0),.bready(1'b0),.drained(f_watch_idle[2]),.fault(f_watch_fault[2]));
axi_drain_watch f_watch_cs(.clk(clk),.rst(rst),.arvalid(cs_m_arvalid),.arready(cs_m_arready),.arlen(cs_m_arlen),.rvalid(cs_m_rvalid),.rready(cs_m_rready),.rlast(cs_m_rlast),.awvalid(cs_m_awvalid),.awready(cs_m_awready),.awlen(cs_m_awlen),.wvalid(cs_m_wvalid),.wready(cs_m_wready),.wlast(cs_m_wlast),.bvalid(cs_m_bvalid),.bready(cs_m_bready),.drained(f_watch_idle[3]),.fault(f_watch_fault[3]));
axi_drain_watch f_watch_q(.clk(clk),.rst(rst),.arvalid(q_m_arvalid),.arready(q_m_arready),.arlen(q_m_arlen),.rvalid(q_m_rvalid),.rready(q_m_rready),.rlast(q_m_rlast),.awvalid(1'b0),.awready(1'b0),.awlen(8'd0),.wvalid(1'b0),.wready(1'b0),.wlast(1'b0),.bvalid(1'b0),.bready(1'b0),.drained(f_watch_idle[4]),.fault(f_watch_fault[4]));
transaction_fence #(.LANES(16),.REQ_BITS(2432),.RSP_BITS(256),.ADMIN_FIRST(14),.CALLBACK_MASK(16'h037f))fence(.clk(clk),.rst(k_cold_rst),.work_permit(k_permit),.normal_fault(fault||rc_fault||k_fault||cf_fault||lr_fault),.backend_drained(f_all_drained),.backend_idle(f_backend_idle),.route_block(rc_block),.s_valid(f_sv),.s_ready(f_sr),.s_payload(f_sp),.s_rsp_valid(f_srv),.s_rsp_ready(f_srr),.s_rsp_payload(f_srp),.cb_valid(f_cbv),.cb_ready(f_cbr),.cb_payload(f_cbp),.cb_rsp_valid(f_cbrv),.cb_rsp_ready(f_cbrr),.cb_rsp_payload(f_cbrp),.d_valid(f_dv),.d_ready(f_dr),.d_payload(f_dp),.d_rsp_valid(f_drv),.d_rsp_ready(f_drr),.d_rsp_payload(f_drp),.route_valid(rc_req_valid),.route_ready(rc_req_ready),.route_payload(f_route_payload),.route_rsp_valid(rc_rsp_valid),.route_rsp_ready(rc_rsp_ready),.backend_route_valid(f_broute_valid),.backend_route_ready(f_broute_ready),.backend_route_payload(f_broute_payload),.backend_route_rsp_valid(f_broute_rsp_valid),.backend_route_rsp_ready(f_broute_rsp_ready),.route_error(rc_rsp_status!=0),.recover_valid(k_rec_valid),.recover_ready(k_rec_ready),.backend_recover_valid(f_brecover_valid),.backend_recover_ready(f_brecover_ready),.recover_rsp_valid(k_rsp_valid),.recover_rsp_ready(k_rsp_ready),.backend_recover_rsp_valid(f_brecover_rsp_valid),.backend_recover_rsp_ready(f_brecover_rsp_ready),.recover_error(k_rsp_status!=0),.normal_retired(f_normal_retired),.recovery_owned(f_recovery_owned),.fault(f_fault),.phase(f_phase),.callback_pending(f_pending));
endmodule
