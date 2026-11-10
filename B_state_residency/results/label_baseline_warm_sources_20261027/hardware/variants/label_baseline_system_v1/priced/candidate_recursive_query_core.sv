`timescale 1ns/1ps
module candidate_recursive_query_core #(parameter integer ENABLE_BASELINE=0,parameter integer ENABLE_FRAME_SCAN=0,parameter integer SLOTS=32,TX_BITS=16,GEN_BITS=16,FRAMES=163840,INDEX_BITS=18,HASH_BITS=18,PROBE_LIMIT=64,EPOCH_BITS=16,TOKEN_BITS=32,OWNER_BITS=32,MAX_CYCLES=33554432)(
input wire baseline_permit,input wire[63:0]baseline_epoch,
output wire baseline_req_valid,input wire baseline_req_ready,
output wire[31:0]baseline_req_node,output wire[63:0]baseline_req_epoch,
input wire baseline_rsp_valid,output wire baseline_rsp_ready,
input wire[3:0]baseline_rsp_status,input wire[31:0]baseline_rsp_node,
input wire[63:0]baseline_rsp_epoch,input wire[159:0]baseline_rsp_payload,

 output wire[31:0] current_parent,current_root_cookie,
 input wire [31:0] frame_version,input wire [63:0] frame_design,
 input wire commit_l_valid,output wire commit_l_ready,input wire commit_l_write,
 input wire [31:0] commit_l_node,commit_l_value,input wire [2:0] commit_l_field,
 output wire commit_l_rsp_valid,input wire commit_l_rsp_ready,output wire [3:0] commit_l_status,output wire [159:0] commit_l_payload,output wire commit_l_present,
 input wire cost_c_req_valid,output wire cost_c_req_ready,input wire [31:0] cost_c_req_cookie,cost_c_req_node,
 input wire [1:0] cost_c_req_query,cost_c_req_op,input wire [3:0] cost_c_req_price,
 output wire cost_c_rsp_valid,input wire cost_c_rsp_ready,output wire [3:0] cost_c_rsp_status,
 output wire [31:0] cost_c_rsp_cookie,cost_c_rsp_node,cost_c_rsp_y,cost_c_rsp_slr,cost_c_rsp_next,cost_c_rsp_prev_column,
 output wire [255:0] cost_c_rsp_attrs,output wire [1:0] cost_c_rsp_op,cost_c_rsp_query,output wire [3:0] cost_c_rsp_price,
 input wire post_l_valid,output wire post_l_ready,input wire post_l_write,
 input wire [31:0] post_l_node,post_l_value,input wire [2:0] post_l_field,
 output wire post_l_rsp_valid,input wire post_l_rsp_ready,output wire [3:0] post_l_status,output wire [159:0] post_l_payload,output wire post_l_present,
 input wire post_c_req_valid,output wire post_c_req_ready,input wire [31:0] post_c_req_cookie,post_c_req_node,
 input wire [1:0] post_c_req_query,input wire [3:0] post_c_req_price,
 output wire post_c_rsp_valid,input wire post_c_rsp_ready,output wire [3:0] post_c_rsp_status,
 output wire [31:0] post_c_rsp_cookie,post_c_rsp_node,post_c_rsp_y,post_c_rsp_label_prev,
 output wire [255:0] post_c_rsp_attrs,output wire [1:0] post_c_rsp_op,post_c_rsp_query,output wire [3:0] post_c_rsp_price,output wire post_c_rsp_prev_read,
 input wire p_o_req_valid,output wire p_o_req_ready,
 input wire [31:0] p_o_req_cookie,p_o_req_node,p_o_req_net,
 output wire p_o_rsp_valid,input wire p_o_rsp_ready,
 output wire [31:0] p_o_rsp_cookie,p_o_rsp_count,p_o_rsp_occupancy,
 output wire [3:0] p_o_rsp_status,
 output wire operation_pending,
 input wire  clk,
 input wire  rst,
 input wire  abort,
 input wire  g_cfg_valid,
 output wire  g_cfg_ready,
 input wire [63:0] g_cfg_offsets_base,
 input wire [63:0] g_cfg_edges_base,
 input wire [63:0] g_cfg_attrs_base,
 input wire [31:0] g_cfg_nodes,
 input wire [31:0] g_cfg_edges,
 output wire  g_cfg_rsp_valid,
 input wire  g_cfg_rsp_ready,
 output wire [2:0] g_cfg_status,
 output wire  g_configured,
 output wire [63:0] g_m_araddr,
 output wire [7:0] g_m_arlen,
 output wire [2:0] g_m_arsize,
 output wire [1:0] g_m_arburst,
 output wire [3:0] g_m_arid,
 output wire  g_m_arvalid,
 input wire  g_m_arready,
 input wire [511:0] g_m_rdata,
 input wire [3:0] g_m_rid,
 input wire [1:0] g_m_rresp,
 input wire  g_m_rlast,
 input wire  g_m_rvalid,
 output wire  g_m_rready,
 input wire  d_cfg_valid,
 output wire  d_cfg_ready,
 input wire [63:0] d_cfg_base,
 input wire [31:0] d_cfg_nodes,
 output wire  d_cfg_rsp_valid,
 input wire  d_cfg_rsp_ready,
 output wire [2:0] d_cfg_status,
 output wire  d_configured,
 output wire [63:0] d_m_araddr,
 output wire [7:0] d_m_arlen,
 output wire [2:0] d_m_arsize,
 output wire [1:0] d_m_arburst,
 output wire [3:0] d_m_arid,
 output wire  d_m_arvalid,
 input wire  d_m_arready,
 input wire [511:0] d_m_rdata,
 input wire [3:0] d_m_rid,
 input wire [1:0] d_m_rresp,
 input wire  d_m_rlast,
 input wire  d_m_rvalid,
 output wire  d_m_rready,
 output wire [63:0] d_m_awaddr,
 output wire [7:0] d_m_awlen,
 output wire [2:0] d_m_awsize,
 output wire [1:0] d_m_awburst,
 output wire [3:0] d_m_awid,
 output wire  d_m_awvalid,
 input wire  d_m_awready,
 output wire [511:0] d_m_wdata,
 output wire [63:0] d_m_wstrb,
 output wire  d_m_wlast,
 output wire  d_m_wvalid,
 input wire  d_m_wready,
 input wire [3:0] d_m_bid,
 input wire [1:0] d_m_bresp,
 input wire  d_m_bvalid,
 output wire  d_m_bready,
 input wire  host_ctrl_valid,
 output wire  host_ctrl_ready,
 input wire [1:0] host_ctrl_op,
 input wire [1:0] host_ctrl_query,
 input wire [3:0] host_ctrl_price,
 output wire  host_ctrl_rsp_valid,
 input wire  host_ctrl_rsp_ready,
 output wire [3:0] host_ctrl_status,
 output wire  p_active,
 output wire [1:0] p_active_query,
 output wire [3:0] p_active_price,
 output wire [31:0] p_m_awaddr,
 output wire [7:0] p_m_awlen,
 output wire [2:0] p_m_awsize,
 output wire [1:0] p_m_awburst,
 output wire [3:0] p_m_awid,
 output wire  p_m_awvalid,
 input wire  p_m_awready,
 output wire [511:0] p_m_wdata,
 output wire [63:0] p_m_wstrb,
 output wire  p_m_wlast,
 output wire  p_m_wvalid,
 input wire  p_m_wready,
 input wire [3:0] p_m_bid,
 input wire [1:0] p_m_bresp,
 input wire  p_m_bvalid,
 output wire  p_m_bready,
 output wire [31:0] p_m_araddr,
 output wire [7:0] p_m_arlen,
 output wire [2:0] p_m_arsize,
 output wire [1:0] p_m_arburst,
 output wire [3:0] p_m_arid,
 output wire  p_m_arvalid,
 input wire  p_m_arready,
 input wire [511:0] p_m_rdata,
 input wire [3:0] p_m_rid,
 input wire [1:0] p_m_rresp,
 input wire  p_m_rlast,
 input wire  p_m_rvalid,
 output wire  p_m_rready,
 input wire  t_cfg_valid,
 output wire  t_cfg_ready,
 input wire [63:0] t_cfg_rows_base,
 input wire [63:0] t_cfg_columns_base,
 input wire [31:0] t_cfg_rows,
 input wire [31:0] t_cfg_columns,
 output wire  t_cfg_rsp_valid,
 input wire  t_cfg_rsp_ready,
 output wire [2:0] t_cfg_status,
 output wire  t_configured,
 output wire [63:0] t_m_araddr,
 output wire [7:0] t_m_arlen,
 output wire [2:0] t_m_arsize,
 output wire [1:0] t_m_arburst,
 output wire [3:0] t_m_arid,
 output wire  t_m_arvalid,
 input wire  t_m_arready,
 input wire [511:0] t_m_rdata,
 input wire [3:0] t_m_rid,
 input wire [1:0] t_m_rresp,
 input wire  t_m_rlast,
 input wire  t_m_rvalid,
 output wire  t_m_rready,
 input wire  host_owner_req_valid,
 output wire  host_owner_req_ready,
 input wire [2:0] host_owner_req_op,
 input wire [31:0] host_owner_req_cookie,
 input wire [31:0] host_owner_req_node,
 input wire [31:0] host_owner_req_net,
 output wire  host_owner_rsp_valid,
 input wire  host_owner_rsp_ready,
 output wire [3:0] host_owner_rsp_status,
 output wire [31:0] host_owner_rsp_cookie,
 output wire [31:0] host_owner_rsp_count,
 output wire [31:0] host_owner_rsp_occupancy,
 output wire  host_owner_rsp_will_overuse,
 input wire  owner_cfg_valid,
 output wire  owner_cfg_ready,
 input wire [63:0] owner_cfg_primary,
 input wire [63:0] owner_cfg_pool,
 input wire [63:0] owner_cfg_allocator,
 input wire [31:0] owner_cfg_nodes,
 input wire [31:0] owner_cfg_capacity,
 output wire  owner_cfg_rsp_valid,
 input wire  owner_cfg_rsp_ready,
 output wire [2:0] owner_cfg_status,
 output wire  owner_configured,
 output wire [63:0] owner_m_araddr,
 output wire [7:0] owner_m_arlen,
 output wire [2:0] owner_m_arsize,
 output wire [1:0] owner_m_arburst,
 output wire [3:0] owner_m_arid,
 output wire  owner_m_arvalid,
 input wire  owner_m_arready,
 input wire [511:0] owner_m_rdata,
 input wire [3:0] owner_m_rid,
 input wire [1:0] owner_m_rresp,
 input wire  owner_m_rlast,
 input wire  owner_m_rvalid,
 output wire  owner_m_rready,
 output wire [63:0] owner_m_awaddr,
 output wire [7:0] owner_m_awlen,
 output wire [2:0] owner_m_awsize,
 output wire [1:0] owner_m_awburst,
 output wire [3:0] owner_m_awid,
 output wire  owner_m_awvalid,
 input wire  owner_m_awready,
 output wire [511:0] owner_m_wdata,
 output wire [63:0] owner_m_wstrb,
 output wire  owner_m_wlast,
 output wire  owner_m_wvalid,
 input wire  owner_m_wready,
 input wire [3:0] owner_m_bid,
 input wire [1:0] owner_m_bresp,
 input wire  owner_m_bvalid,
 output wire  owner_m_bready,
 input wire  expand_valid,
 output wire  expand_ready,
 input wire [31:0] expand_cookie,
 input wire [31:0] expand_parent,
 input wire [31:0] expand_prune,
 input wire [31:0] expand_has_laguna,
 input wire [31:0] expand_sink,
 input wire [31:0] expand_net,
 input wire [31:0] expand_sequence,
 input wire [31:0] expand_flags,
 input wire [31:0] expand_xmin,
 input wire [31:0] expand_xmax,
 input wire [31:0] expand_ymin,
 input wire [31:0] expand_ymax,
 output wire  out_valid,
 input wire  out_ready,
 output wire [31:0] out_cookie,
 output wire [31:0] out_node,
 output wire [31:0] out_position,
 output wire [31:0] out_sequence,
 output wire [31:0] out_bits,
 output wire [31:0] out_action,
 output wire [31:0] out_steps,
 output wire [31:0] out_services,
 output wire [255:0] out_attrs,
 output wire [447:0] out_config,
 output wire  result_valid,
 input wire  result_ready,
 output wire [3:0] result_status,
 output wire [31:0] result_cookie,
 output wire [31:0] result_count,
 output wire [31:0] result_expanded_count,
 output wire [31:0] result_raw_count,
 output wire [31:0] result_mask,
 output wire  result_hit,
 output wire  result_early,
 input wire  host_design_req_valid,
 output wire  host_design_req_ready,
 input wire [2:0] host_design_req_op,
 input wire [31:0] host_design_req_cookie,
 input wire [31:0] host_design_req_owner,
 input wire [31:0] host_design_req_node,
 input wire [31:0] host_design_req_arg,
 output wire  host_design_rsp_valid,
 input wire  host_design_rsp_ready,
 output wire [3:0] host_design_rsp_status,
 output wire [31:0] host_design_rsp_cookie,
 output wire [31:0] host_design_rsp_flags,
 output wire [31:0] host_design_rsp_count,
 output wire [31:0] host_design_rsp_mask,
 input wire  host_io_valid,
 output wire  host_io_ready,
 input wire  host_io_write,
 input wire [31:0] host_io_node,
 input wire [31:0] host_io_value,
 input wire [2:0] host_io_field,
 output wire  host_io_rsp_valid,
 input wire  host_io_rsp_ready,
 output wire [3:0] host_io_status,
 output wire [159:0] host_io_payload,
 output wire  host_io_present,
 output wire  fault,
 output wire  busy,output wire retired_idle,
 input wire scan_valid,output wire scan_ready,input wire scan_permit,input wire[INDEX_BITS-1:0]scan_frame,
 output wire scan_rsp_valid,input wire scan_rsp_ready,output wire[2:0]scan_status,
 output wire[INDEX_BITS-1:0]scan_result_frame,output wire[26:0]scan_owner,output wire scan_published
);
 reg[31:0]held_g_nodes,held_d_nodes,held_owner_nodes,held_t_rows,held_t_columns;
 reg host_label_pending,host_design_pending;
 wire  g_req_valid;
 wire  g_req_ready;
 wire [1:0] g_req_op;
 wire [31:0] g_req_cookie;
 wire [31:0] g_req_node;
 wire [31:0] g_req_index;
 wire  g_rsp_valid;
 wire  g_rsp_ready;
 wire [3:0] g_rsp_status;
 wire [31:0] g_rsp_cookie;
 wire [31:0] g_rsp_parent;
 wire [31:0] g_rsp_index;
 wire [31:0] g_rsp_node;
 wire [31:0] g_rsp_start;
 wire [31:0] g_rsp_count;
 wire [255:0] g_rsp_attrs;
 wire  g_fault;
 wire  d_req_valid;
 wire  d_req_ready;
 wire [2:0] d_req_op;
 wire [31:0] d_req_cookie;
 wire [31:0] d_req_owner;
 wire [31:0] d_req_node;
 wire [31:0] d_req_arg;
 wire  d_rsp_valid;
 wire  d_rsp_ready;
 wire [3:0] d_rsp_status;
 wire [31:0] d_rsp_cookie;
 wire [31:0] d_rsp_flags;
 wire [31:0] d_rsp_count;
 wire [31:0] d_rsp_mask;
 wire  d_fault;
 wire  d_claim_active;
 wire [31:0] d_claim_owner;
 wire [31:0] d_claim_node;
 wire [31:0] d_claim_count;
 wire [31:0] d_claim_mask;
 wire  b_build_valid;
 wire  b_build_ready;
 wire [31:0] b_build_cookie;
 wire [31:0] b_build_parent;
 wire [31:0] b_build_count;
 wire [31:0] b_build_prune;
 wire [1:0] b_build_query;
 wire [3:0] b_build_price;
 wire  b_result_valid;
 wire  b_result_ready;
 wire [3:0] b_result_status;
 wire [31:0] b_result_detail;
 wire [31:0] b_result_cookie;
 wire [31:0] b_result_generation;
 wire [31:0] b_result_emitted;
 wire  b_fault;
 wire  b_busy;
 wire  b_svc_valid;
 wire  b_svc_ready;
 wire [31:0] b_svc_generation;
 wire [31:0] b_svc_parent;
 wire [31:0] b_svc_position;
 wire [31:0] b_svc_phase;
 wire [31:0] b_svc_node;
 wire [31:0] b_svc_emitted;
 wire [31:0] b_svc_count;
 wire [31:0] b_svc_prune;
 wire [1:0] b_svc_query;
 wire [3:0] b_svc_price;
 wire  b_svc_reply_valid;
 wire  b_svc_reply_ready;
 wire [31:0] b_svc_reply_generation;
 wire [31:0] b_svc_reply_parent;
 wire [31:0] b_svc_reply_position;
 wire [31:0] b_svc_reply_phase;
 wire [31:0] b_svc_reply_node;
 wire [1:0] b_svc_reply_query;
 wire [3:0] b_svc_reply_price;
 wire [31:0] b_svc_status;
 wire [31:0] b_svc_value;
 wire [31:0] b_svc_aux;
 wire  b_service_fault;
 wire  p_ctrl_valid;
 wire  p_ctrl_ready;
 wire [1:0] p_ctrl_op;
 wire [1:0] p_ctrl_query;
 wire [3:0] p_ctrl_price;
 wire  p_ctrl_rsp_valid;
 wire  p_ctrl_rsp_ready;
 wire [3:0] p_ctrl_status;
 wire  p_io_valid;
 wire  p_io_ready;
 wire  p_io_write;
 wire [31:0] p_io_node;
 wire [31:0] p_io_value;
 wire [2:0] p_io_field;
 wire  p_io_rsp_valid;
 wire  p_io_rsp_ready;
 wire [3:0] p_io_status;
 wire [159:0] p_io_payload;
 wire  p_io_present;
 wire  p_edge_valid;
 wire  p_edge_ready;
 wire [31:0] p_edge_cookie;
 wire [31:0] p_edge_parent;
 wire [31:0] p_edge_child;
 wire [31:0] p_edge_flags;
 wire [31:0] p_edge_created;
 wire [31:0] p_edge_has_laguna;
 wire  p_result_valid;
 wire  p_result_ready;
 wire [3:0] p_result_status;
 wire [31:0] p_result_detail;
 wire [31:0] p_result_cookie;
 wire [31:0] p_result_generation;
 wire  p_result_excluded;
 wire  p_fault;
 wire  p_dispatch_enable;
 wire  p_execute_enable;
 wire  p_fence_service_enable;
 wire  p_ack_receive_enable;
 wire [31:0] p_page_leases;
 wire [31:0] p_memory_leases;
 wire [INDEX_BITS:0] p_allocated;
 wire [1:0] p_fence_tag;
 wire  p_draining;
 wire  can_start;
 wire  expansion_external_fault;
 wire  e_expand_valid;
 wire  e_expand_ready;
 wire [31:0] e_expand_cookie;
 wire [31:0] e_expand_parent;
 wire [31:0] e_expand_prune;
 wire [31:0] e_expand_has_laguna;
 wire  e_out_valid;
 wire  e_out_ready;
 wire [31:0] e_out_node;
 wire [31:0] e_out_position;
 wire [31:0] e_out_sequence;
 wire [255:0] e_out_attrs;
 wire  e_result_valid;
 wire  e_result_ready;
 wire [3:0] e_result_status;
 wire [31:0] e_result_detail;
 wire [31:0] e_result_cookie;
 wire [31:0] e_result_count;
 wire [31:0] e_result_raw_count;
 wire [31:0] e_result_mask;
 wire  e_result_hit;
 wire ce_expand_valid;
 wire ce_expand_ready;
 wire [31:0] ce_expand_cookie;
 wire [31:0] ce_expand_parent;
 wire [31:0] ce_expand_prune;
 wire [31:0] ce_expand_has_laguna;
 wire ce_out_valid;
 wire ce_out_ready;
 wire [31:0] ce_out_node;
 wire [31:0] ce_out_position;
 wire [31:0] ce_out_sequence;
 wire [255:0] ce_out_attrs;
 wire ce_result_valid;
 wire ce_result_ready;
 wire [3:0] ce_result_status;
 wire [31:0] ce_result_detail;
 wire [31:0] ce_result_cookie;
 wire [31:0] ce_result_count;
 wire [31:0] ce_result_raw_count;
 wire [31:0] ce_result_mask;
 wire ce_result_hit;
 wire b_retired_idle;wire capture_fault,capture_busy;wire[31:0]capture_depth;wire[511:0]captured_context,controller_expand_context;
 expansion_capture #(.DEPTH(4),.CAPACITY(32)) child_capture(
 .clk(clk),.rst(rst),.abort(abort),.expand_context(controller_expand_context),.out_context(captured_context),
 .busy(capture_busy),.fault(capture_fault),.depth(capture_depth),
.expand_valid(e_expand_valid),
.expand_ready(e_expand_ready),
.expand_cookie(e_expand_cookie),
.expand_parent(e_expand_parent),
.expand_prune(e_expand_prune),
.expand_has_laguna(e_expand_has_laguna),
.out_valid(e_out_valid),
.out_ready(e_out_ready),
.out_node(e_out_node),
.out_position(e_out_position),
.out_sequence(e_out_sequence),
.out_attrs(e_out_attrs),
.result_valid(e_result_valid),
.result_ready(e_result_ready),
.result_status(e_result_status),
.result_detail(e_result_detail),
.result_cookie(e_result_cookie),
.result_count(e_result_count),
.result_raw_count(e_result_raw_count),
.result_mask(e_result_mask),
.result_hit(e_result_hit),
.e_expand_valid(ce_expand_valid),
.e_expand_ready(ce_expand_ready),
.e_expand_cookie(ce_expand_cookie),
.e_expand_parent(ce_expand_parent),
.e_expand_prune(ce_expand_prune),
.e_expand_has_laguna(ce_expand_has_laguna),
.e_out_valid(ce_out_valid),
.e_out_ready(ce_out_ready),
.e_out_node(ce_out_node),
.e_out_position(ce_out_position),
.e_out_sequence(ce_out_sequence),
.e_out_attrs(ce_out_attrs),
.e_result_valid(ce_result_valid),
.e_result_ready(ce_result_ready),
.e_result_status(ce_result_status),
.e_result_detail(ce_result_detail),
.e_result_cookie(ce_result_cookie),
.e_result_count(ce_result_count),
.e_result_raw_count(ce_result_raw_count),
.e_result_mask(ce_result_mask),
.e_result_hit(ce_result_hit));
 wire  e_busy;
 wire  e_fault;
 wire  e_g_req_valid;
 wire  e_g_req_ready;
 wire [1:0] e_g_req_op;
 wire [31:0] e_g_req_cookie;
 wire [31:0] e_g_req_node;
 wire [31:0] e_g_req_index;
 wire  e_g_rsp_valid;
 wire  e_g_rsp_ready;
 wire [3:0] e_g_rsp_status;
 wire [31:0] e_g_rsp_cookie;
 wire [31:0] e_g_rsp_parent;
 wire [31:0] e_g_rsp_index;
 wire [31:0] e_g_rsp_node;
 wire [31:0] e_g_rsp_start;
 wire [31:0] e_g_rsp_count;
 wire [255:0] e_g_rsp_attrs;
 wire  e_d_req_valid;
 wire  e_d_req_ready;
 wire [2:0] e_d_req_op;
 wire [31:0] e_d_req_cookie;
 wire [31:0] e_d_req_owner;
 wire [31:0] e_d_req_node;
 wire [31:0] e_d_req_arg;
 wire  e_d_rsp_valid;
 wire  e_d_rsp_ready;
 wire [3:0] e_d_rsp_status;
 wire [31:0] e_d_rsp_cookie;
 wire [31:0] e_d_rsp_flags;
 wire [31:0] e_d_rsp_count;
 wire [31:0] e_d_rsp_mask;

 wire  m_req_valid;
 wire  m_req_ready;
 wire [31:0] m_req_cookie;
 wire [31:0] m_req_parent;
 wire [31:0] m_req_child;
 wire [31:0] m_req_sink;
 wire [31:0] m_req_net;
 wire [31:0] m_req_sequence;
 wire [31:0] m_req_flags;
 wire [31:0] m_req_xmin;
 wire [31:0] m_req_xmax;
 wire [31:0] m_req_ymin;
 wire [31:0] m_req_ymax;
 wire [1:0] m_req_query;
 wire [3:0] m_req_price;
 wire  m_rsp_valid;
 wire  m_rsp_ready;
 wire [3:0] m_rsp_status;
 wire [31:0] m_rsp_cookie;
 wire [31:0] m_rsp_parent;
 wire [31:0] m_rsp_child;
 wire [31:0] m_rsp_sink;
 wire [31:0] m_rsp_net;
 wire [1:0] m_rsp_query;
 wire [3:0] m_rsp_price;
 wire [447:0] m_rsp_config;
 wire  m_rsp_created;
 wire  m_busy;
 wire  m_fault;
 wire  m_g_req_valid;
 wire  m_g_req_ready;
 wire [1:0] m_g_req_op;
 wire [31:0] m_g_req_cookie;
 wire [31:0] m_g_req_node;
 wire [31:0] m_g_req_index;
 wire  m_g_rsp_valid;
 wire  m_g_rsp_ready;
 wire [3:0] m_g_rsp_status;
 wire [31:0] m_g_rsp_cookie;
 wire [31:0] m_g_rsp_parent;
 wire [31:0] m_g_rsp_index;
 wire [31:0] m_g_rsp_node;
 wire [31:0] m_g_rsp_start;
 wire [31:0] m_g_rsp_count;
 wire [255:0] m_g_rsp_attrs;
 wire  m_d_req_valid;
 wire  m_d_req_ready;
 wire [2:0] m_d_req_op;
 wire [31:0] m_d_req_cookie;
 wire [31:0] m_d_req_owner;
 wire [31:0] m_d_req_node;
 wire [31:0] m_d_req_arg;
 wire  m_d_rsp_valid;
 wire  m_d_rsp_ready;
 wire [3:0] m_d_rsp_status;
 wire [31:0] m_d_rsp_cookie;
 wire [31:0] m_d_rsp_flags;
 wire [31:0] m_d_rsp_count;
 wire [31:0] m_d_rsp_mask;
 wire  a_req_valid;
 wire  a_req_ready;
 wire [447:0] a_req_config;
 wire [31:0] a_req_cookie;
 wire [31:0] a_req_parent;
 wire [31:0] a_req_child;
 wire [31:0] a_req_sink;
 wire [31:0] a_req_net;
 wire [1:0] a_req_query;
 wire [3:0] a_req_price;
 wire  a_rsp_valid;
 wire  a_rsp_ready;
 wire [3:0] a_rsp_status;
 wire [31:0] a_rsp_cookie;
 wire [31:0] a_rsp_parent;
 wire [31:0] a_rsp_child;
 wire [31:0] a_rsp_sink;
 wire [31:0] a_rsp_net;
 wire [31:0] a_rsp_bits;
 wire [31:0] a_rsp_action;
 wire [31:0] a_rsp_steps;
 wire [31:0] a_rsp_services;
 wire [1:0] a_rsp_query;
 wire [3:0] a_rsp_price;
 wire  a_busy;
 wire  a_fault;
 wire  s_req_valid;
 wire  s_req_ready;
 wire [3:0] s_req_kind;
 wire [4:0] s_req_phase;
 wire [31:0] s_req_node;
 wire [31:0] s_req_net;
 wire [31:0] s_req_cookie;
 wire [1:0] s_req_query;
 wire [3:0] s_req_price;
 wire  s_rsp_valid;
 wire  s_rsp_ready;
 wire [3:0] s_rsp_status;
 wire [3:0] s_rsp_kind;
 wire [4:0] s_rsp_phase;
 wire [31:0] s_rsp_node;
 wire [31:0] s_rsp_net;
 wire [31:0] s_rsp_cookie;
 wire [31:0] s_rsp_value;
 wire [1:0] s_rsp_query;
 wire [3:0] s_rsp_price;
 wire  s_fault;
 wire  s_l_valid;
 wire  s_l_ready;
 wire  s_l_write;
 wire [31:0] s_l_node;
 wire [31:0] s_l_value;
 wire [2:0] s_l_field;
 wire  s_l_rsp_valid;
 wire  s_l_rsp_ready;
 wire [3:0] s_l_status;
 wire [159:0] s_l_payload;
 wire  s_l_present;
 wire  c_req_valid;
 wire  c_req_ready;
 wire [1:0] c_req_op;
 wire [1:0] c_req_query;
 wire [3:0] c_req_price;
 wire [31:0] c_req_cookie;
 wire [31:0] c_req_node;
 wire  c_rsp_valid;
 wire  c_rsp_ready;
 wire [3:0] c_rsp_status;
 wire [1:0] c_rsp_op;
 wire [1:0] c_rsp_query;
 wire [3:0] c_rsp_price;
 wire [31:0] c_rsp_cookie;
 wire [31:0] c_rsp_node;
 wire [31:0] c_rsp_y;
 wire [31:0] c_rsp_slr;
 wire [255:0] c_rsp_attrs;
 wire  c_fault;
 wire pc_arb_fault,pc_arb_busy;
 wire  o_req_valid;
 wire  o_req_ready;
 wire [3:0] o_req_kind;
 wire [4:0] o_req_phase;
 wire [31:0] o_req_node;
 wire [31:0] o_req_net;
 wire [31:0] o_req_cookie;
 wire [1:0] o_req_query;
 wire [3:0] o_req_price;
 wire  o_rsp_valid;
 wire  o_rsp_ready;
 wire [3:0] o_rsp_status;
 wire [3:0] o_rsp_kind;
 wire [4:0] o_rsp_phase;
 wire [31:0] o_rsp_node;
 wire [31:0] o_rsp_net;
 wire [31:0] o_rsp_cookie;
 wire [31:0] o_rsp_value;
 wire [1:0] o_rsp_query;
 wire [3:0] o_rsp_price;
 wire  o_fault;
 wire [31:0] c_rsp_next;
 wire [31:0] c_rsp_prev_column;
 wire [31:0] c_rsp_label_prev;
 wire  c_rsp_north;
 wire  c_rsp_prev_read;
 wire  c_rsp_prev_present;
 wire  c_busy;
 wire  c_g_req_valid;
 wire  c_g_req_ready;
 wire [1:0] c_g_req_op;
 wire [31:0] c_g_req_cookie;
 wire [31:0] c_g_req_node;
 wire [31:0] c_g_req_index;
 wire  c_g_rsp_valid;
 wire  c_g_rsp_ready;
 wire [3:0] c_g_rsp_status;
 wire [31:0] c_g_rsp_cookie;
 wire [31:0] c_g_rsp_parent;
 wire [31:0] c_g_rsp_index;
 wire [31:0] c_g_rsp_node;
 wire [31:0] c_g_rsp_start;
 wire [31:0] c_g_rsp_count;
 wire [255:0] c_g_rsp_attrs;
 wire  t_req_valid;
 wire  t_req_ready;
 wire  t_req_op;
 wire [31:0] t_req_cookie;
 wire [31:0] t_req_index;
 wire  t_rsp_valid;
 wire  t_rsp_ready;
 wire [3:0] t_rsp_status;
 wire  t_rsp_op;
 wire [31:0] t_rsp_index;
 wire [31:0] t_rsp_cookie;
 wire [31:0] t_rsp_a;
 wire [31:0] t_rsp_b;
 wire  t_fault;
 wire  c_p_io_valid;
 wire  c_p_io_ready;
 wire  c_p_io_write;
 wire [31:0] c_p_io_node;
 wire [31:0] c_p_io_value;
 wire [2:0] c_p_io_field;
 wire  c_p_io_rsp_valid;
 wire  c_p_io_rsp_ready;
 wire [3:0] c_p_io_status;
 wire [159:0] c_p_io_payload;
 wire  c_p_io_present;
 wire  o_b_req_valid;
 wire  o_b_req_ready;
 wire [2:0] o_b_req_op;
 wire [31:0] o_b_req_cookie;
 wire [31:0] o_b_req_node;
 wire [31:0] o_b_req_net;
 wire  o_b_rsp_valid;
 wire  o_b_rsp_ready;
 wire [3:0] o_b_rsp_status;
 wire [31:0] o_b_rsp_cookie;
 wire [31:0] o_b_rsp_count;
 wire [31:0] o_b_rsp_occupancy;
 wire  o_b_rsp_will_overuse;
 wire  o_b_fault;
 wire  o_host_pending;
 wire  o_busy;
 wire  u_busy;
 wire  subsystem_fault;
 wire  stopped;
 wire  owner_raw_cfg_ready;
 wire  configuration_fault;
 wire  permit_label;
 wire  permit_design;
 wire [2:0] arb_g_c_req_valid;
 wire [2:0] arb_g_c_req_ready;
 wire [2:0] arb_g_c_rsp_valid;
 wire [2:0] arb_g_c_rsp_ready;
 wire [293:0] arb_g_c_req_data;
 wire [1355:0] arb_g_c_rsp_data;
 wire [97:0] arb_g_b_req_data;
 wire [451:0] arb_g_b_rsp_data;
 wire  arb_g_fault;
 wire  arb_g_busy;
 wire [2:0] arb_d_c_req_valid;
 wire [2:0] arb_d_c_req_ready;
 wire [2:0] arb_d_c_rsp_valid;
 wire [2:0] arb_d_c_rsp_ready;
 wire [392:0] arb_d_c_req_data;
 wire [395:0] arb_d_c_rsp_data;
 wire [130:0] arb_d_b_req_data;
 wire [131:0] arb_d_b_rsp_data;
 wire  arb_d_fault;
 wire  arb_d_busy;
 wire [2:0] h_d_req_op;
 wire [31:0] h_d_req_cookie;
 wire [31:0] h_d_req_owner;
 wire [31:0] h_d_req_node;
 wire [31:0] h_d_req_arg;
 wire [3:0] h_d_rsp_status;
 wire [31:0] h_d_rsp_cookie;
 wire [31:0] h_d_rsp_flags;
 wire [31:0] h_d_rsp_count;
 wire [31:0] h_d_rsp_mask;
 wire  h_d_req_valid;
 wire  h_d_req_ready;
 wire  h_d_rsp_valid;
 wire  h_d_rsp_ready;
 wire [4:0] arb_io_c_req_valid;
 wire [4:0] arb_io_c_req_ready;
 wire [4:0] arb_io_c_rsp_valid;
 wire [4:0] arb_io_c_rsp_ready;
 wire [339:0] arb_io_c_req_data;
 wire [824:0] arb_io_c_rsp_data;
 wire [67:0] arb_io_b_req_data;
 wire [164:0] arb_io_b_rsp_data;
 wire  arb_io_fault;
 wire  arb_io_busy;
 wire  h_io_valid;
 wire  h_io_ready;
 wire  h_io_write;
 wire [31:0] h_io_node;
 wire [31:0] h_io_value;
 wire [2:0] h_io_field;
 wire  h_io_rsp_valid;
 wire  h_io_rsp_ready;
 wire [3:0] h_io_status;
 wire [159:0] h_io_payload;
 wire  h_io_present;
 assign arb_g_c_req_valid[0]=e_g_req_valid;
 assign e_g_req_ready=arb_g_c_req_ready[0];
 assign arb_g_c_req_data[0+:98]={e_g_req_op,e_g_req_cookie,e_g_req_node,e_g_req_index};
 assign e_g_rsp_valid=arb_g_c_rsp_valid[0];
 assign arb_g_c_rsp_ready[0]=e_g_rsp_ready;
 assign {e_g_rsp_status,e_g_rsp_cookie,e_g_rsp_parent,e_g_rsp_index,e_g_rsp_node,e_g_rsp_start,e_g_rsp_count,e_g_rsp_attrs}=arb_g_c_rsp_data[0+:452];
 assign arb_g_c_req_valid[1]=m_g_req_valid;
 assign m_g_req_ready=arb_g_c_req_ready[1];
 assign arb_g_c_req_data[98+:98]={m_g_req_op,m_g_req_cookie,m_g_req_node,m_g_req_index};
 assign m_g_rsp_valid=arb_g_c_rsp_valid[1];
 assign arb_g_c_rsp_ready[1]=m_g_rsp_ready;
 assign {m_g_rsp_status,m_g_rsp_cookie,m_g_rsp_parent,m_g_rsp_index,m_g_rsp_node,m_g_rsp_start,m_g_rsp_count,m_g_rsp_attrs}=arb_g_c_rsp_data[452+:452];
 assign arb_g_c_req_valid[2]=c_g_req_valid;
 assign c_g_req_ready=arb_g_c_req_ready[2];
 assign arb_g_c_req_data[196+:98]={c_g_req_op,c_g_req_cookie,c_g_req_node,c_g_req_index};
 assign c_g_rsp_valid=arb_g_c_rsp_valid[2];
 assign arb_g_c_rsp_ready[2]=c_g_rsp_ready;
 assign {c_g_rsp_status,c_g_rsp_cookie,c_g_rsp_parent,c_g_rsp_index,c_g_rsp_node,c_g_rsp_start,c_g_rsp_count,c_g_rsp_attrs}=arb_g_c_rsp_data[904+:452];
 assign {g_req_op,g_req_cookie,g_req_node,g_req_index}=arb_g_b_req_data;
 assign arb_g_b_rsp_data={g_rsp_status,g_rsp_cookie,g_rsp_parent,g_rsp_index,g_rsp_node,g_rsp_start,g_rsp_count,g_rsp_attrs};
 service_arbiter #(.CLIENTS(3),.REQUEST_BITS(98),.RESPONSE_BITS(452))g_arb(
.clk(clk),
.rst(rst),
.c_req_valid(arb_g_c_req_valid),
.c_req_ready(arb_g_c_req_ready),
.c_req_data(arb_g_c_req_data),
.c_rsp_valid(arb_g_c_rsp_valid),
.c_rsp_ready(arb_g_c_rsp_ready),
.c_rsp_data(arb_g_c_rsp_data),
.b_req_data(arb_g_b_req_data),
.b_rsp_data(arb_g_b_rsp_data),
.fault(arb_g_fault),
.busy(arb_g_busy),
.b_req_valid(g_req_valid),
.b_req_ready(g_req_ready),
.b_rsp_valid(g_rsp_valid),
.b_rsp_ready(g_rsp_ready)
);
 assign arb_d_c_req_valid[0]=e_d_req_valid;
 assign e_d_req_ready=arb_d_c_req_ready[0];
 assign arb_d_c_req_data[0+:131]={e_d_req_op,e_d_req_cookie,e_d_req_owner,e_d_req_node,e_d_req_arg};
 assign e_d_rsp_valid=arb_d_c_rsp_valid[0];
 assign arb_d_c_rsp_ready[0]=e_d_rsp_ready;
 assign {e_d_rsp_status,e_d_rsp_cookie,e_d_rsp_flags,e_d_rsp_count,e_d_rsp_mask}=arb_d_c_rsp_data[0+:132];
 assign arb_d_c_req_valid[1]=m_d_req_valid;
 assign m_d_req_ready=arb_d_c_req_ready[1];
 assign arb_d_c_req_data[131+:131]={m_d_req_op,m_d_req_cookie,m_d_req_owner,m_d_req_node,m_d_req_arg};
 assign m_d_rsp_valid=arb_d_c_rsp_valid[1];
 assign arb_d_c_rsp_ready[1]=m_d_rsp_ready;
 assign {m_d_rsp_status,m_d_rsp_cookie,m_d_rsp_flags,m_d_rsp_count,m_d_rsp_mask}=arb_d_c_rsp_data[132+:132];
 assign arb_d_c_req_valid[2]=h_d_req_valid;
 assign h_d_req_ready=arb_d_c_req_ready[2];
 assign arb_d_c_req_data[262+:131]={h_d_req_op,h_d_req_cookie,h_d_req_owner,h_d_req_node,h_d_req_arg};
 assign h_d_rsp_valid=arb_d_c_rsp_valid[2];
 assign arb_d_c_rsp_ready[2]=h_d_rsp_ready;
 assign {h_d_rsp_status,h_d_rsp_cookie,h_d_rsp_flags,h_d_rsp_count,h_d_rsp_mask}=arb_d_c_rsp_data[264+:132];
 assign {d_req_op,d_req_cookie,d_req_owner,d_req_node,d_req_arg}=arb_d_b_req_data;
 assign arb_d_b_rsp_data={d_rsp_status,d_rsp_cookie,d_rsp_flags,d_rsp_count,d_rsp_mask};
 service_arbiter #(.CLIENTS(3),.REQUEST_BITS(131),.RESPONSE_BITS(132))d_arb(
.clk(clk),
.rst(rst),
.c_req_valid(arb_d_c_req_valid),
.c_req_ready(arb_d_c_req_ready),
.c_req_data(arb_d_c_req_data),
.c_rsp_valid(arb_d_c_rsp_valid),
.c_rsp_ready(arb_d_c_rsp_ready),
.c_rsp_data(arb_d_c_rsp_data),
.b_req_data(arb_d_b_req_data),
.b_rsp_data(arb_d_b_rsp_data),
.fault(arb_d_fault),
.busy(arb_d_busy),
.b_req_valid(d_req_valid),
.b_req_ready(d_req_ready),
.b_rsp_valid(d_rsp_valid),
.b_rsp_ready(d_rsp_ready)
);
 assign arb_io_c_req_valid[0]=c_p_io_valid;
 assign c_p_io_ready=arb_io_c_req_ready[0];
 assign arb_io_c_req_data[0+:68]={c_p_io_write,c_p_io_node,c_p_io_value,c_p_io_field};
 assign c_p_io_rsp_valid=arb_io_c_rsp_valid[0];
 assign arb_io_c_rsp_ready[0]=c_p_io_rsp_ready;
 assign {c_p_io_status,c_p_io_payload,c_p_io_present}=arb_io_c_rsp_data[0+:165];
 assign arb_io_c_req_valid[1]=s_l_valid;
 assign s_l_ready=arb_io_c_req_ready[1];
 assign arb_io_c_req_data[68+:68]={s_l_write,s_l_node,s_l_value,s_l_field};
 assign s_l_rsp_valid=arb_io_c_rsp_valid[1];
 assign arb_io_c_rsp_ready[1]=s_l_rsp_ready;
 assign {s_l_status,s_l_payload,s_l_present}=arb_io_c_rsp_data[165+:165];
 assign arb_io_c_req_valid[2]=h_io_valid;
 assign h_io_ready=arb_io_c_req_ready[2];
 assign arb_io_c_req_data[136+:68]={h_io_write,h_io_node,h_io_value,h_io_field};
 assign h_io_rsp_valid=arb_io_c_rsp_valid[2];
 assign arb_io_c_rsp_ready[2]=h_io_rsp_ready;
 assign {h_io_status,h_io_payload,h_io_present}=arb_io_c_rsp_data[330+:165];
 assign arb_io_c_req_valid[3]=post_l_valid;
 assign post_l_ready=arb_io_c_req_ready[3];
 assign arb_io_c_req_data[204+:68]={post_l_write,post_l_node,post_l_value,post_l_field};
 assign post_l_rsp_valid=arb_io_c_rsp_valid[3];
 assign arb_io_c_rsp_ready[3]=post_l_rsp_ready;
 assign {post_l_status,post_l_payload,post_l_present}=arb_io_c_rsp_data[495+:165];
 assign arb_io_c_req_valid[4]=commit_l_valid;
 assign commit_l_ready=arb_io_c_req_ready[4];
 assign arb_io_c_req_data[272+:68]={commit_l_write,commit_l_node,commit_l_value,commit_l_field};
 assign commit_l_rsp_valid=arb_io_c_rsp_valid[4];
 assign arb_io_c_rsp_ready[4]=commit_l_rsp_ready;
 assign {commit_l_status,commit_l_payload,commit_l_present}=arb_io_c_rsp_data[660+:165];
 assign {p_io_write,p_io_node,p_io_value,p_io_field}=arb_io_b_req_data;
 assign arb_io_b_rsp_data={p_io_status,p_io_payload,p_io_present};
 service_arbiter #(.CLIENTS(5),.REQUEST_BITS(68),.RESPONSE_BITS(165))io_arb(
.clk(clk),
.rst(rst),
.c_req_valid(arb_io_c_req_valid),
.c_req_ready(arb_io_c_req_ready),
.c_req_data(arb_io_c_req_data),
.c_rsp_valid(arb_io_c_rsp_valid),
.c_rsp_ready(arb_io_c_rsp_ready),
.c_rsp_data(arb_io_c_rsp_data),
.b_req_data(arb_io_b_req_data),
.b_rsp_data(arb_io_b_rsp_data),
.fault(arb_io_fault),
.busy(arb_io_busy),
.b_req_valid(p_io_valid),
.b_req_ready(p_io_ready),
.b_rsp_valid(p_io_rsp_valid),
.b_rsp_ready(p_io_rsp_ready)
);
 assign h_d_req_op=host_design_req_op;
 assign h_d_req_cookie=host_design_req_cookie;
 assign h_d_req_owner=host_design_req_owner;
 assign h_d_req_node=host_design_req_node;
 assign h_d_req_arg=host_design_req_arg;
 assign h_d_req_valid=host_design_req_valid&&permit_design;
 assign host_design_req_ready=h_d_req_ready&&permit_design;
 assign host_design_rsp_valid=h_d_rsp_valid;
 assign h_d_rsp_ready=host_design_rsp_ready;
 assign host_design_rsp_status=h_d_rsp_status;
 assign host_design_rsp_cookie=h_d_rsp_cookie;
 assign host_design_rsp_flags=h_d_rsp_flags;
 assign host_design_rsp_count=h_d_rsp_count;
 assign host_design_rsp_mask=h_d_rsp_mask;
 assign h_io_valid=host_io_valid&&permit_label&&!host_ctrl_valid;
 assign host_io_ready=h_io_ready&&permit_label&&!host_ctrl_valid;
 assign host_io_rsp_valid=h_io_rsp_valid;
 assign h_io_rsp_ready=host_io_rsp_ready;
 assign h_io_write=host_io_write;
 assign h_io_node=host_io_node;
 assign h_io_value=host_io_value;
 assign h_io_field=host_io_field;
 assign host_io_status=h_io_status;
 assign host_io_payload=h_io_payload;
 assign host_io_present=h_io_present;
 assign p_ctrl_valid=host_ctrl_valid&&permit_label;
 assign host_ctrl_ready=p_ctrl_ready&&permit_label;
 assign p_ctrl_op=host_ctrl_op;
 assign p_ctrl_query=host_ctrl_query;
 assign p_ctrl_price=host_ctrl_price;
 assign host_ctrl_rsp_valid=p_ctrl_rsp_valid;
 assign p_ctrl_rsp_ready=host_ctrl_rsp_ready;
 assign host_ctrl_status=p_ctrl_status;
 assign p_dispatch_enable=1;
 assign p_execute_enable=1;
 assign p_fence_service_enable=1;
 assign p_ack_receive_enable=1;
 assign owner_cfg_ready=owner_raw_cfg_ready&&!operation_pending&&!o_host_pending;
 assign configuration_fault=g_configured&&d_configured&&owner_configured&&(held_g_nodes!=held_d_nodes||held_g_nodes!=held_owner_nodes);
 assign expansion_external_fault=configuration_fault||stopped||abort||m_fault||a_fault||s_fault||c_fault||pc_arb_fault||o_fault||o_b_fault||t_fault||arb_g_fault||arb_d_fault||arb_io_fault;
 assign subsystem_fault=capture_fault||e_fault||b_fault||g_fault||d_fault||p_fault||expansion_external_fault;
 assign fault=subsystem_fault||stopped;
 assign busy=operation_pending||host_label_pending||host_design_pending||o_host_pending;
 // No recovery handoff while a captured service request/reply or children HLS
 // context is still owned. Fault latches alone do not constitute ownership.
 // p_memory_leases pins directory frames across errors until recovery;
 // p_draining includes the checkpoint fence. Neither counts live commands.
 // Label command replies retire via host_label_pending / p_result_valid;
 // the enclosing fence independently requires physical AXI drain.
 assign retired_idle=!rst&&!busy&&!arb_g_busy&&!arb_d_busy&&!arb_io_busy&&!pc_arb_busy&&
 capture_depth==0&&b_retired_idle&&
 !g_rsp_valid&&!d_rsp_valid&&!b_result_valid&&!ce_result_valid&&!e_result_valid&&
 !m_rsp_valid&&!a_rsp_valid&&!s_rsp_valid&&!c_rsp_valid&&!t_rsp_valid&&!o_rsp_valid&&!o_b_rsp_valid&&!p_result_valid;
 assign permit_label=!rst&&!fault&&!operation_pending&&!host_label_pending;
 assign permit_design=!rst&&!fault&&!operation_pending&&!host_design_pending;
 assign can_start=g_configured&&d_configured&&t_configured&&owner_configured&&p_active&&!configuration_fault&&!operation_pending&&!host_label_pending&&!host_design_pending&&!o_host_pending&&!host_ctrl_valid&&!host_io_valid&&!host_design_req_valid&&!host_owner_req_valid&&!g_cfg_rsp_valid&&!d_cfg_rsp_valid&&!t_cfg_rsp_valid&&!owner_cfg_rsp_valid&&!g_cfg_valid&&!d_cfg_valid&&!t_cfg_valid&&!owner_cfg_valid&&!d_claim_active;
 always @(posedge clk)begin
  if(rst)begin held_g_nodes<=0;held_d_nodes<=0;held_owner_nodes<=0;held_t_rows<=0;held_t_columns<=0;host_label_pending<=0;host_design_pending<=0;end
  else begin
   if(g_cfg_valid&&g_cfg_ready)held_g_nodes<=g_cfg_nodes;
   if(d_cfg_valid&&d_cfg_ready)held_d_nodes<=d_cfg_nodes;
   if(owner_cfg_valid&&owner_cfg_ready)held_owner_nodes<=owner_cfg_nodes;
   if(t_cfg_valid&&t_cfg_ready)begin held_t_rows<=t_cfg_rows;held_t_columns<=t_cfg_columns;end
   if((host_ctrl_valid&&host_ctrl_ready)||(host_io_valid&&host_io_ready))host_label_pending<=1;
   if((host_ctrl_rsp_valid&&host_ctrl_rsp_ready)||(host_io_rsp_valid&&host_io_rsp_ready))host_label_pending<=0;
   if(host_design_req_valid&&host_design_req_ready)host_design_pending<=1;
   if(host_design_rsp_valid&&host_design_rsp_ready)host_design_pending<=0;
  end
 end
 graph_static_reader g(
.clk(clk),
.rst(rst),
.cfg_valid(g_cfg_valid),
.cfg_ready(g_cfg_ready),
.cfg_offsets_base(g_cfg_offsets_base),
.cfg_edges_base(g_cfg_edges_base),
.cfg_attrs_base(g_cfg_attrs_base),
.cfg_nodes(g_cfg_nodes),
.cfg_edges(g_cfg_edges),
.cfg_rsp_valid(g_cfg_rsp_valid),
.cfg_rsp_ready(g_cfg_rsp_ready),
.cfg_status(g_cfg_status),
.configured(g_configured),
.req_valid(g_req_valid),
.req_ready(g_req_ready),
.req_op(g_req_op),
.req_cookie(g_req_cookie),
.req_node(g_req_node),
.req_index(g_req_index),
.rsp_valid(g_rsp_valid),
.rsp_ready(g_rsp_ready),
.rsp_status(g_rsp_status),
.rsp_cookie(g_rsp_cookie),
.rsp_parent(g_rsp_parent),
.rsp_index(g_rsp_index),
.rsp_node(g_rsp_node),
.rsp_start(g_rsp_start),
.rsp_count(g_rsp_count),
.rsp_attrs(g_rsp_attrs),
.fault(g_fault),
.m_araddr(g_m_araddr),
.m_arlen(g_m_arlen),
.m_arsize(g_m_arsize),
.m_arburst(g_m_arburst),
.m_arid(g_m_arid),
.m_arvalid(g_m_arvalid),
.m_arready(g_m_arready),
.m_rdata(g_m_rdata),
.m_rid(g_m_rid),
.m_rresp(g_m_rresp),
.m_rlast(g_m_rlast),
.m_rvalid(g_m_rvalid),
.m_rready(g_m_rready)
);
 design_state_store d(
.clk(clk),
.rst(rst),
.cfg_valid(d_cfg_valid),
.cfg_ready(d_cfg_ready),
.cfg_base(d_cfg_base),
.cfg_nodes(d_cfg_nodes),
.cfg_rsp_valid(d_cfg_rsp_valid),
.cfg_rsp_ready(d_cfg_rsp_ready),
.cfg_status(d_cfg_status),
.configured(d_configured),
.req_valid(d_req_valid),
.req_ready(d_req_ready),
.req_op(d_req_op),
.req_cookie(d_req_cookie),
.req_owner(d_req_owner),
.req_node(d_req_node),
.req_arg(d_req_arg),
.rsp_valid(d_rsp_valid),
.rsp_ready(d_rsp_ready),
.rsp_status(d_rsp_status),
.rsp_cookie(d_rsp_cookie),
.rsp_flags(d_rsp_flags),
.rsp_count(d_rsp_count),
.rsp_mask(d_rsp_mask),
.fault(d_fault),
.claim_active(d_claim_active),
.claim_owner(d_claim_owner),
.claim_node(d_claim_node),
.claim_count(d_claim_count),
.claim_mask(d_claim_mask),
.m_araddr(d_m_araddr),
.m_arlen(d_m_arlen),
.m_arsize(d_m_arsize),
.m_arburst(d_m_arburst),
.m_arid(d_m_arid),
.m_arvalid(d_m_arvalid),
.m_arready(d_m_arready),
.m_rdata(d_m_rdata),
.m_rid(d_m_rid),
.m_rresp(d_m_rresp),
.m_rlast(d_m_rlast),
.m_rvalid(d_m_rvalid),
.m_rready(d_m_rready),
.m_awaddr(d_m_awaddr),
.m_awlen(d_m_awlen),
.m_awsize(d_m_awsize),
.m_awburst(d_m_awburst),
.m_awid(d_m_awid),
.m_awvalid(d_m_awvalid),
.m_awready(d_m_awready),
.m_wdata(d_m_wdata),
.m_wstrb(d_m_wstrb),
.m_wlast(d_m_wlast),
.m_wvalid(d_m_wvalid),
.m_wready(d_m_wready),
.m_bid(d_m_bid),
.m_bresp(d_m_bresp),
.m_bvalid(d_m_bvalid),
.m_bready(d_m_bready)
);
 paged_exclusion_engine #(.ENABLE_BASELINE(ENABLE_BASELINE),.ENABLE_FRAME_SCAN(ENABLE_FRAME_SCAN),.SLOTS(SLOTS),.TX_BITS(TX_BITS),.GEN_BITS(GEN_BITS),.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS),.PROBE_LIMIT(PROBE_LIMIT),.EPOCH_BITS(EPOCH_BITS)) p(.baseline_permit(baseline_permit),.baseline_epoch(baseline_epoch),.baseline_req_valid(baseline_req_valid),.baseline_req_ready(baseline_req_ready),.baseline_req_node(baseline_req_node),.baseline_req_epoch(baseline_req_epoch),.baseline_rsp_valid(baseline_rsp_valid),.baseline_rsp_ready(baseline_rsp_ready),.baseline_rsp_status(baseline_rsp_status),.baseline_rsp_node(baseline_rsp_node),.baseline_rsp_epoch(baseline_rsp_epoch),.baseline_rsp_payload(baseline_rsp_payload),.scan_valid(scan_valid),.scan_ready(scan_ready),.scan_permit(scan_permit),.scan_frame(scan_frame),.scan_rsp_valid(scan_rsp_valid),.scan_rsp_ready(scan_rsp_ready),.scan_status(scan_status),.scan_result_frame(scan_result_frame),.scan_owner(scan_owner),.scan_published(scan_published),
.clk(clk),
.rst(rst),
.ctrl_valid(p_ctrl_valid),
.ctrl_ready(p_ctrl_ready),
.ctrl_op(p_ctrl_op),
.ctrl_query(p_ctrl_query),
.ctrl_price(p_ctrl_price),
.ctrl_rsp_valid(p_ctrl_rsp_valid),
.ctrl_rsp_ready(p_ctrl_rsp_ready),
.ctrl_status(p_ctrl_status),
.io_valid(p_io_valid),
.io_ready(p_io_ready),
.io_write(p_io_write),
.io_node(p_io_node),
.io_value(p_io_value),
.io_field(p_io_field),
.io_rsp_valid(p_io_rsp_valid),
.io_rsp_ready(p_io_rsp_ready),
.io_status(p_io_status),
.io_payload(p_io_payload),
.io_present(p_io_present),
.edge_valid(p_edge_valid),
.edge_ready(p_edge_ready),
.edge_cookie(p_edge_cookie),
.edge_parent(p_edge_parent),
.edge_child(p_edge_child),
.edge_flags(p_edge_flags),
.edge_created(p_edge_created),
.edge_has_laguna(p_edge_has_laguna),
.result_valid(p_result_valid),
.result_ready(p_result_ready),
.result_status(p_result_status),
.result_detail(p_result_detail),
.result_cookie(p_result_cookie),
.result_generation(p_result_generation),
.result_excluded(p_result_excluded),
.fault(p_fault),
.active(p_active),
.active_query(p_active_query),
.active_price(p_active_price),
.dispatch_enable(p_dispatch_enable),
.execute_enable(p_execute_enable),
.fence_service_enable(p_fence_service_enable),
.ack_receive_enable(p_ack_receive_enable),
.page_leases(p_page_leases),
.memory_leases(p_memory_leases),
.allocated(p_allocated),
.fence_tag(p_fence_tag),
.draining(p_draining),
.m_awaddr(p_m_awaddr),
.m_awlen(p_m_awlen),
.m_awsize(p_m_awsize),
.m_awburst(p_m_awburst),
.m_awid(p_m_awid),
.m_awvalid(p_m_awvalid),
.m_awready(p_m_awready),
.m_wdata(p_m_wdata),
.m_wstrb(p_m_wstrb),
.m_wlast(p_m_wlast),
.m_wvalid(p_m_wvalid),
.m_wready(p_m_wready),
.m_bid(p_m_bid),
.m_bresp(p_m_bresp),
.m_bvalid(p_m_bvalid),
.m_bready(p_m_bready),
.m_araddr(p_m_araddr),
.m_arlen(p_m_arlen),
.m_arsize(p_m_arsize),
.m_arburst(p_m_arburst),
.m_arid(p_m_arid),
.m_arvalid(p_m_arvalid),
.m_arready(p_m_arready),
.m_rdata(p_m_rdata),
.m_rid(p_m_rid),
.m_rresp(p_m_rresp),
.m_rlast(p_m_rlast),
.m_rvalid(p_m_rvalid),
.m_rready(p_m_rready)
);
 children_build_engine b(.retired_idle(b_retired_idle),
.clk(clk),
.rst(rst),
.build_valid(b_build_valid),
.build_ready(b_build_ready),
.build_cookie(b_build_cookie),
.build_parent(b_build_parent),
.build_count(b_build_count),
.build_prune(b_build_prune),
.build_query(b_build_query),
.build_price(b_build_price),
.result_valid(b_result_valid),
.result_ready(b_result_ready),
.result_status(b_result_status),
.result_detail(b_result_detail),
.result_cookie(b_result_cookie),
.result_generation(b_result_generation),
.result_emitted(b_result_emitted),
.fault(b_fault),
.busy(b_busy),
.svc_valid(b_svc_valid),
.svc_ready(b_svc_ready),
.svc_generation(b_svc_generation),
.svc_parent(b_svc_parent),
.svc_position(b_svc_position),
.svc_phase(b_svc_phase),
.svc_node(b_svc_node),
.svc_emitted(b_svc_emitted),
.svc_count(b_svc_count),
.svc_prune(b_svc_prune),
.svc_query(b_svc_query),
.svc_price(b_svc_price),
.svc_reply_valid(b_svc_reply_valid),
.svc_reply_ready(b_svc_reply_ready),
.svc_reply_generation(b_svc_reply_generation),
.svc_reply_parent(b_svc_reply_parent),
.svc_reply_position(b_svc_reply_position),
.svc_reply_phase(b_svc_reply_phase),
.svc_reply_node(b_svc_reply_node),
.svc_reply_query(b_svc_reply_query),
.svc_reply_price(b_svc_reply_price),
.svc_status(b_svc_status),
.svc_value(b_svc_value),
.svc_aux(b_svc_aux),
.service_fault(b_service_fault)
);
 expansion_controller #(.TOKEN_BITS(TOKEN_BITS),.OWNER_BITS(OWNER_BITS)) expansion(
.clk(clk),
.rst(rst),
.enable(operation_pending&&!capture_fault&&!configuration_fault),
.configuration_fault(expansion_external_fault),
.expand_valid(ce_expand_valid),
.expand_ready(ce_expand_ready),
.expand_cookie(ce_expand_cookie),
.expand_parent(ce_expand_parent),
.expand_prune(ce_expand_prune),
.expand_has_laguna(ce_expand_has_laguna),
.out_valid(ce_out_valid),
.out_ready(ce_out_ready),
.out_node(ce_out_node),
.out_position(ce_out_position),
.out_sequence(ce_out_sequence),
.out_attrs(ce_out_attrs),
.result_valid(ce_result_valid),
.result_ready(ce_result_ready),
.result_status(ce_result_status),
.result_detail(ce_result_detail),
.result_cookie(ce_result_cookie),
.result_count(ce_result_count),
.result_raw_count(ce_result_raw_count),
.result_mask(ce_result_mask),
.result_hit(ce_result_hit),
.busy(e_busy),
.fault(e_fault),
.g_fault(g_fault||arb_g_fault),
.d_fault(d_fault||arb_d_fault),
.p_fault(p_fault),
.b_fault(b_fault),
.p_active(p_active),
.p_active_query(p_active_query),
.p_active_price(p_active_price),
.g_req_valid(e_g_req_valid),
.g_req_ready(e_g_req_ready),
.g_req_op(e_g_req_op),
.g_req_cookie(e_g_req_cookie),
.g_req_node(e_g_req_node),
.g_req_index(e_g_req_index),
.g_rsp_valid(e_g_rsp_valid),
.g_rsp_ready(e_g_rsp_ready),
.g_rsp_status(e_g_rsp_status),
.g_rsp_cookie(e_g_rsp_cookie),
.g_rsp_parent(e_g_rsp_parent),
.g_rsp_index(e_g_rsp_index),
.g_rsp_node(e_g_rsp_node),
.g_rsp_start(e_g_rsp_start),
.g_rsp_count(e_g_rsp_count),
.g_rsp_attrs(e_g_rsp_attrs),
.d_req_valid(e_d_req_valid),
.d_req_ready(e_d_req_ready),
.d_req_op(e_d_req_op),
.d_req_cookie(e_d_req_cookie),
.d_req_owner(e_d_req_owner),
.d_req_node(e_d_req_node),
.d_req_arg(e_d_req_arg),
.d_rsp_valid(e_d_rsp_valid),
.d_rsp_ready(e_d_rsp_ready),
.d_rsp_status(e_d_rsp_status),
.d_rsp_cookie(e_d_rsp_cookie),
.d_rsp_flags(e_d_rsp_flags),
.d_rsp_count(e_d_rsp_count),
.d_rsp_mask(e_d_rsp_mask),
.d_claim_active(d_claim_active),
.d_claim_owner(d_claim_owner),
.d_claim_node(d_claim_node),
.d_claim_count(d_claim_count),
.d_claim_mask(d_claim_mask),
.b_build_valid(b_build_valid),
.b_build_ready(b_build_ready),
.b_build_cookie(b_build_cookie),
.b_build_parent(b_build_parent),
.b_build_count(b_build_count),
.b_build_prune(b_build_prune),
.b_build_query(b_build_query),
.b_build_price(b_build_price),
.b_result_valid(b_result_valid),
.b_result_ready(b_result_ready),
.b_result_status(b_result_status),
.b_result_detail(b_result_detail),
.b_result_cookie(b_result_cookie),
.b_result_generation(b_result_generation),
.b_result_emitted(b_result_emitted),
.b_svc_valid(b_svc_valid),
.b_svc_ready(b_svc_ready),
.b_svc_generation(b_svc_generation),
.b_svc_parent(b_svc_parent),
.b_svc_position(b_svc_position),
.b_svc_phase(b_svc_phase),
.b_svc_node(b_svc_node),
.b_svc_emitted(b_svc_emitted),
.b_svc_count(b_svc_count),
.b_svc_prune(b_svc_prune),
.b_svc_query(b_svc_query),
.b_svc_price(b_svc_price),
.b_svc_reply_valid(b_svc_reply_valid),
.b_svc_reply_ready(b_svc_reply_ready),
.b_svc_reply_generation(b_svc_reply_generation),
.b_svc_reply_parent(b_svc_reply_parent),
.b_svc_reply_position(b_svc_reply_position),
.b_svc_reply_phase(b_svc_reply_phase),
.b_svc_reply_node(b_svc_reply_node),
.b_svc_reply_query(b_svc_reply_query),
.b_svc_reply_price(b_svc_reply_price),
.b_svc_status(b_svc_status),
.b_svc_value(b_svc_value),
.b_svc_aux(b_svc_aux),
.b_service_fault(b_service_fault),
.p_edge_valid(p_edge_valid),
.p_edge_ready(p_edge_ready),
.p_edge_cookie(p_edge_cookie),
.p_edge_parent(p_edge_parent),
.p_edge_child(p_edge_child),
.p_edge_flags(p_edge_flags),
.p_edge_created(p_edge_created),
.p_edge_has_laguna(p_edge_has_laguna),
.p_result_valid(p_result_valid),
.p_result_ready(p_result_ready),
.p_result_status(p_result_status),
.p_result_detail(p_result_detail),
.p_result_cookie(p_result_cookie),
.p_result_generation(p_result_generation),
.p_result_excluded(p_result_excluded)
);
 metadata_controller #(.TOKEN_BITS(TOKEN_BITS)) metadata(
.clk(clk),
.rst(rst),
.enable(operation_pending),
.abort(abort||stopped),
.active(p_active),
.active_query(p_active_query),
.active_price(p_active_price),
.nodes(held_g_nodes),
.claim_active(d_claim_active),
.req_valid(m_req_valid),
.req_ready(m_req_ready),
.req_cookie(m_req_cookie),
.req_parent(m_req_parent),
.req_child(m_req_child),
.req_sink(m_req_sink),
.req_net(m_req_net),
.req_sequence(m_req_sequence),
.req_flags(m_req_flags),
.req_xmin(m_req_xmin),
.req_xmax(m_req_xmax),
.req_ymin(m_req_ymin),
.req_ymax(m_req_ymax),
.req_query(m_req_query),
.req_price(m_req_price),
.rsp_valid(m_rsp_valid),
.rsp_ready(m_rsp_ready),
.rsp_status(m_rsp_status),
.rsp_cookie(m_rsp_cookie),
.rsp_parent(m_rsp_parent),
.rsp_child(m_rsp_child),
.rsp_sink(m_rsp_sink),
.rsp_net(m_rsp_net),
.rsp_query(m_rsp_query),
.rsp_price(m_rsp_price),
.rsp_config(m_rsp_config),
.rsp_created(m_rsp_created),
.busy(m_busy),
.fault(m_fault),
.g_req_valid(m_g_req_valid),
.g_req_ready(m_g_req_ready),
.g_req_op(m_g_req_op),
.g_req_cookie(m_g_req_cookie),
.g_req_node(m_g_req_node),
.g_req_index(m_g_req_index),
.g_rsp_valid(m_g_rsp_valid),
.g_rsp_ready(m_g_rsp_ready),
.g_rsp_status(m_g_rsp_status),
.g_rsp_cookie(m_g_rsp_cookie),
.g_rsp_parent(m_g_rsp_parent),
.g_rsp_index(m_g_rsp_index),
.g_rsp_node(m_g_rsp_node),
.g_rsp_start(m_g_rsp_start),
.g_rsp_count(m_g_rsp_count),
.g_rsp_attrs(m_g_rsp_attrs),
.g_fault(g_fault||arb_g_fault),
.d_req_valid(m_d_req_valid),
.d_req_ready(m_d_req_ready),
.d_req_op(m_d_req_op),
.d_req_cookie(m_d_req_cookie),
.d_req_owner(m_d_req_owner),
.d_req_node(m_d_req_node),
.d_req_arg(m_d_req_arg),
.d_rsp_valid(m_d_rsp_valid),
.d_rsp_ready(m_d_rsp_ready),
.d_rsp_status(m_d_rsp_status),
.d_rsp_cookie(m_d_rsp_cookie),
.d_rsp_flags(m_d_rsp_flags),
.d_rsp_count(m_d_rsp_count),
.d_rsp_mask(m_d_rsp_mask),
.d_fault(d_fault||arb_d_fault)
);
 access_service #(.TOKEN_BITS(TOKEN_BITS)) access(
.clk(clk),
.rst(rst),
.abort(abort||stopped),
.enable(operation_pending),
.active(p_active),
.active_query(p_active_query),
.active_price(p_active_price),
.req_valid(a_req_valid),
.req_ready(a_req_ready),
.req_config(a_req_config),
.req_cookie(a_req_cookie),
.req_parent(a_req_parent),
.req_child(a_req_child),
.req_sink(a_req_sink),
.req_net(a_req_net),
.req_query(a_req_query),
.req_price(a_req_price),
.rsp_valid(a_rsp_valid),
.rsp_ready(a_rsp_ready),
.rsp_status(a_rsp_status),
.rsp_cookie(a_rsp_cookie),
.rsp_parent(a_rsp_parent),
.rsp_child(a_rsp_child),
.rsp_sink(a_rsp_sink),
.rsp_net(a_rsp_net),
.rsp_bits(a_rsp_bits),
.rsp_action(a_rsp_action),
.rsp_steps(a_rsp_steps),
.rsp_services(a_rsp_services),
.rsp_query(a_rsp_query),
.rsp_price(a_rsp_price),
.busy(a_busy),
.fault(a_fault),
.svc_valid(s_req_valid),
.svc_ready(s_req_ready),
.svc_kind(s_req_kind),
.svc_phase(s_req_phase),
.svc_node(s_req_node),
.svc_net(s_req_net),
.svc_cookie(s_req_cookie),
.svc_query(s_req_query),
.svc_price(s_req_price),
.svc_rsp_valid(s_rsp_valid),
.svc_rsp_ready(s_rsp_ready),
.svc_rsp_status(s_rsp_status),
.svc_rsp_kind(s_rsp_kind),
.svc_rsp_phase(s_rsp_phase),
.svc_rsp_node(s_rsp_node),
.svc_rsp_net(s_rsp_net),
.svc_rsp_cookie(s_rsp_cookie),
.svc_rsp_value(s_rsp_value),
.svc_rsp_query(s_rsp_query),
.svc_rsp_price(s_rsp_price),
.svc_fault(s_fault)
);
 access_dispatch #(.MAX_CYCLES((1<<HASH_BITS)+262144)) dispatch(
.clk(clk),
.rst(rst),
.abort(abort||stopped),
.active(p_active),
.active_query(p_active_query),
.active_price(p_active_price),
.req_valid(s_req_valid),
.req_ready(s_req_ready),
.req_kind(s_req_kind),
.req_phase(s_req_phase),
.req_node(s_req_node),
.req_net(s_req_net),
.req_cookie(s_req_cookie),
.req_query(s_req_query),
.req_price(s_req_price),
.rsp_valid(s_rsp_valid),
.rsp_ready(s_rsp_ready),
.rsp_status(s_rsp_status),
.rsp_kind(s_rsp_kind),
.rsp_phase(s_rsp_phase),
.rsp_node(s_rsp_node),
.rsp_net(s_rsp_net),
.rsp_cookie(s_rsp_cookie),
.rsp_value(s_rsp_value),
.rsp_query(s_rsp_query),
.rsp_price(s_rsp_price),
.fault(s_fault),
.l_valid(s_l_valid),
.l_ready(s_l_ready),
.l_write(s_l_write),
.l_node(s_l_node),
.l_value(s_l_value),
.l_field(s_l_field),
.l_rsp_valid(s_l_rsp_valid),
.l_rsp_ready(s_l_rsp_ready),
.l_status(s_l_status),
.l_payload(s_l_payload),
.l_present(s_l_present),
.c_req_valid(c_req_valid),
.c_req_ready(c_req_ready),
.c_req_op(c_req_op),
.c_req_query(c_req_query),
.c_req_price(c_req_price),
.c_req_cookie(c_req_cookie),
.c_req_node(c_req_node),
.c_rsp_valid(c_rsp_valid),
.c_rsp_ready(c_rsp_ready),
.c_rsp_status(c_rsp_status),
.c_rsp_op(c_rsp_op),
.c_rsp_query(c_rsp_query),
.c_rsp_price(c_rsp_price),
.c_rsp_cookie(c_rsp_cookie),
.c_rsp_node(c_rsp_node),
.c_rsp_y(c_rsp_y),
.c_rsp_slr(c_rsp_slr),
.c_rsp_attrs(c_rsp_attrs),
.c_fault(c_fault),
.o_req_valid(o_req_valid),
.o_req_ready(o_req_ready),
.o_req_kind(o_req_kind),
.o_req_phase(o_req_phase),
.o_req_node(o_req_node),
.o_req_net(o_req_net),
.o_req_cookie(o_req_cookie),
.o_req_query(o_req_query),
.o_req_price(o_req_price),
.o_rsp_valid(o_rsp_valid),
.o_rsp_ready(o_rsp_ready),
.o_rsp_status(o_rsp_status),
.o_rsp_kind(o_rsp_kind),
.o_rsp_phase(o_rsp_phase),
.o_rsp_node(o_rsp_node),
.o_rsp_net(o_rsp_net),
.o_rsp_cookie(o_rsp_cookie),
.o_rsp_value(o_rsp_value),
.o_rsp_query(o_rsp_query),
.o_rsp_price(o_rsp_price),
.o_fault(o_fault)
);
 wire mc_req_valid,mc_req_ready;
 wire [1:0] mc_req_op;
 wire [1:0] mc_req_query;
 wire [3:0] mc_req_price;
 wire [31:0] mc_req_cookie;
 wire [31:0] mc_req_node;
 wire mc_rsp_valid,mc_rsp_ready;
 wire [3:0] mc_rsp_status;
 wire [1:0] mc_rsp_op;
 wire [1:0] mc_rsp_query;
 wire [3:0] mc_rsp_price;
 wire [31:0] mc_rsp_cookie;
 wire [31:0] mc_rsp_node;
 wire [31:0] mc_rsp_y;
 wire [31:0] mc_rsp_slr;
 wire [31:0] mc_rsp_next;
 wire [31:0] mc_rsp_prev_column;
 wire [31:0] mc_rsp_label_prev;
 wire [0:0] mc_rsp_north;
 wire [0:0] mc_rsp_prev_read;
 wire [0:0] mc_rsp_prev_present;
 wire [255:0] mc_rsp_attrs;
 wire [31:0] post_c_rsp_slr;
 wire [31:0] post_c_rsp_next;
 wire [31:0] post_c_rsp_prev_column;
 wire post_c_rsp_north,post_c_rsp_prev_present;
 wire [2:0] pc_rv,pc_rr,pc_sv,pc_sr;wire [215:0] pc_rd;wire [1484:0] pc_sd;wire [71:0] pc_bd;wire [494:0] pc_bs;
 assign pc_rv={cost_c_req_valid,post_c_req_valid,c_req_valid};assign {cost_c_req_ready,post_c_req_ready,c_req_ready}=pc_rr;
 assign pc_rd[0+:72]={c_req_op,c_req_query,c_req_price,c_req_cookie,c_req_node};
 assign pc_rd[72+:72]={2'd0,post_c_req_query,post_c_req_price,post_c_req_cookie,post_c_req_node};
 assign {cost_c_rsp_valid,post_c_rsp_valid,c_rsp_valid}=pc_sv;assign pc_sr={cost_c_rsp_ready,post_c_rsp_ready,c_rsp_ready};
 assign {c_rsp_status,c_rsp_op,c_rsp_query,c_rsp_price,c_rsp_cookie,c_rsp_node,c_rsp_y,c_rsp_slr,c_rsp_next,c_rsp_prev_column,c_rsp_label_prev,c_rsp_north,c_rsp_prev_read,c_rsp_prev_present,c_rsp_attrs}=pc_sd[0+:495];
 assign {post_c_rsp_status,post_c_rsp_op,post_c_rsp_query,post_c_rsp_price,post_c_rsp_cookie,post_c_rsp_node,post_c_rsp_y,post_c_rsp_slr,post_c_rsp_next,post_c_rsp_prev_column,post_c_rsp_label_prev,post_c_rsp_north,post_c_rsp_prev_read,post_c_rsp_prev_present,post_c_rsp_attrs}=pc_sd[495+:495];
 wire [31:0] cost_c_rsp_label_prev;wire cost_c_rsp_north,cost_c_rsp_prev_read,cost_c_rsp_prev_present;
 assign pc_rd[144+:72]={cost_c_req_op,cost_c_req_query,cost_c_req_price,cost_c_req_cookie,cost_c_req_node};
 assign {cost_c_rsp_status,cost_c_rsp_op,cost_c_rsp_query,cost_c_rsp_price,cost_c_rsp_cookie,cost_c_rsp_node,cost_c_rsp_y,cost_c_rsp_slr,cost_c_rsp_next,cost_c_rsp_prev_column,cost_c_rsp_label_prev,cost_c_rsp_north,cost_c_rsp_prev_read,cost_c_rsp_prev_present,cost_c_rsp_attrs}=pc_sd[990+:495];
 assign {mc_req_op,mc_req_query,mc_req_price,mc_req_cookie,mc_req_node}=pc_bd;
 assign pc_bs={mc_rsp_status,mc_rsp_op,mc_rsp_query,mc_rsp_price,mc_rsp_cookie,mc_rsp_node,mc_rsp_y,mc_rsp_slr,mc_rsp_next,mc_rsp_prev_column,mc_rsp_label_prev,mc_rsp_north,mc_rsp_prev_read,mc_rsp_prev_present,mc_rsp_attrs};
 service_arbiter #(.CLIENTS(3),.REQUEST_BITS(72),.RESPONSE_BITS(495))post_coordinate_arb(
 .clk(clk),.rst(rst),.c_req_valid(pc_rv),.c_req_ready(pc_rr),.c_req_data(pc_rd),.c_rsp_valid(pc_sv),.c_rsp_ready(pc_sr),.c_rsp_data(pc_sd),
 .b_req_valid(mc_req_valid),.b_req_ready(mc_req_ready),.b_req_data(pc_bd),.b_rsp_valid(mc_rsp_valid),.b_rsp_ready(mc_rsp_ready),.b_rsp_data(pc_bs),.busy(pc_arb_busy),.fault(pc_arb_fault));
 coordinate_controller #(.TOKEN_BITS(TOKEN_BITS),.MAX_CYCLES((1<<HASH_BITS)+262144)) coordinates(
.clk(clk),
.rst(rst),
.enable(operation_pending),
.abort(abort||stopped),
.nodes(held_g_nodes),
.table_rows(held_t_rows),
.table_columns(held_t_columns),
.active(p_active),
.active_query(p_active_query),
.active_price(p_active_price),
.req_valid(mc_req_valid),
.req_ready(mc_req_ready),
.req_op(mc_req_op),
.req_query(mc_req_query),
.req_price(mc_req_price),
.req_cookie(mc_req_cookie),
.req_node(mc_req_node),
.rsp_valid(mc_rsp_valid),
.rsp_ready(mc_rsp_ready),
.rsp_status(mc_rsp_status),
.rsp_op(mc_rsp_op),
.rsp_query(mc_rsp_query),
.rsp_price(mc_rsp_price),
.rsp_cookie(mc_rsp_cookie),
.rsp_node(mc_rsp_node),
.rsp_y(mc_rsp_y),
.rsp_slr(mc_rsp_slr),
.rsp_next(mc_rsp_next),
.rsp_prev_column(mc_rsp_prev_column),
.rsp_label_prev(mc_rsp_label_prev),
.rsp_north(mc_rsp_north),
.rsp_prev_read(mc_rsp_prev_read),
.rsp_prev_present(mc_rsp_prev_present),
.rsp_attrs(mc_rsp_attrs),
.busy(c_busy),
.fault(c_fault),
.g_req_valid(c_g_req_valid),
.g_req_ready(c_g_req_ready),
.g_req_op(c_g_req_op),
.g_req_cookie(c_g_req_cookie),
.g_req_node(c_g_req_node),
.g_req_index(c_g_req_index),
.g_rsp_valid(c_g_rsp_valid),
.g_rsp_ready(c_g_rsp_ready),
.g_rsp_status(c_g_rsp_status),
.g_rsp_cookie(c_g_rsp_cookie),
.g_rsp_parent(c_g_rsp_parent),
.g_rsp_index(c_g_rsp_index),
.g_rsp_node(c_g_rsp_node),
.g_rsp_start(c_g_rsp_start),
.g_rsp_count(c_g_rsp_count),
.g_rsp_attrs(c_g_rsp_attrs),
.g_fault(g_fault||arb_g_fault),
.t_req_valid(t_req_valid),
.t_req_ready(t_req_ready),
.t_req_op(t_req_op),
.t_req_cookie(t_req_cookie),
.t_req_index(t_req_index),
.t_rsp_valid(t_rsp_valid),
.t_rsp_ready(t_rsp_ready),
.t_rsp_status(t_rsp_status),
.t_rsp_op(t_rsp_op),
.t_rsp_index(t_rsp_index),
.t_rsp_cookie(t_rsp_cookie),
.t_rsp_a(t_rsp_a),
.t_rsp_b(t_rsp_b),
.t_fault(t_fault),
.p_io_valid(c_p_io_valid),
.p_io_ready(c_p_io_ready),
.p_io_write(c_p_io_write),
.p_io_node(c_p_io_node),
.p_io_value(c_p_io_value),
.p_io_field(c_p_io_field),
.p_io_rsp_valid(c_p_io_rsp_valid),
.p_io_rsp_ready(c_p_io_rsp_ready),
.p_io_status(c_p_io_status),
.p_io_payload(c_p_io_payload),
.p_io_present(c_p_io_present),
.p_fault(p_fault||arb_io_fault)
);
 geometry_table_reader t(
.clk(clk),
.rst(rst),
.cfg_valid(t_cfg_valid),
.cfg_ready(t_cfg_ready),
.cfg_rows_base(t_cfg_rows_base),
.cfg_columns_base(t_cfg_columns_base),
.cfg_rows(t_cfg_rows),
.cfg_columns(t_cfg_columns),
.cfg_rsp_valid(t_cfg_rsp_valid),
.cfg_rsp_ready(t_cfg_rsp_ready),
.cfg_status(t_cfg_status),
.configured(t_configured),
.req_valid(t_req_valid),
.req_ready(t_req_ready),
.req_op(t_req_op),
.req_index(t_req_index),
.req_cookie(t_req_cookie),
.rsp_valid(t_rsp_valid),
.rsp_ready(t_rsp_ready),
.rsp_status(t_rsp_status),
.rsp_op(t_rsp_op),
.rsp_index(t_rsp_index),
.rsp_cookie(t_rsp_cookie),
.rsp_a(t_rsp_a),
.rsp_b(t_rsp_b),
.fault(t_fault),
.m_araddr(t_m_araddr),
.m_arlen(t_m_arlen),
.m_arsize(t_m_arsize),
.m_arburst(t_m_arburst),
.m_arid(t_m_arid),
.m_arvalid(t_m_arvalid),
.m_arready(t_m_arready),
.m_rdata(t_m_rdata),
.m_rid(t_m_rid),
.m_rresp(t_m_rresp),
.m_rlast(t_m_rlast),
.m_rvalid(t_m_rvalid),
.m_rready(t_m_rready)
);
 owner_bridge owners(
.clk(clk),
.rst(rst),
.abort(abort||stopped),
.decision_lock(operation_pending),
.active(p_active),
.active_query(p_active_query),
.active_price(p_active_price),
.s_req_valid(o_req_valid),
.s_req_ready(o_req_ready),
.s_req_kind(o_req_kind),
.s_req_phase(o_req_phase),
.s_req_node(o_req_node),
.s_req_net(o_req_net),
.s_req_cookie(o_req_cookie),
.s_req_query(o_req_query),
.s_req_price(o_req_price),
.s_rsp_valid(o_rsp_valid),
.s_rsp_ready(o_rsp_ready),
.s_rsp_status(o_rsp_status),
.s_rsp_kind(o_rsp_kind),
.s_rsp_phase(o_rsp_phase),
.s_rsp_node(o_rsp_node),
.s_rsp_net(o_rsp_net),
.s_rsp_cookie(o_rsp_cookie),
.s_rsp_value(o_rsp_value),
.s_rsp_query(o_rsp_query),
.s_rsp_price(o_rsp_price),
.h_req_valid(host_owner_req_valid),
.h_req_ready(host_owner_req_ready),
.h_req_op(host_owner_req_op),
.h_req_cookie(host_owner_req_cookie),
.h_req_node(host_owner_req_node),
.h_req_net(host_owner_req_net),
.h_rsp_valid(host_owner_rsp_valid),
.h_rsp_ready(host_owner_rsp_ready),
.h_rsp_status(host_owner_rsp_status),
.h_rsp_cookie(host_owner_rsp_cookie),
.h_rsp_count(host_owner_rsp_count),
.h_rsp_occupancy(host_owner_rsp_occupancy),
.h_rsp_will_overuse(host_owner_rsp_will_overuse),
.b_req_valid(o_b_req_valid),
.b_req_ready(o_b_req_ready),
.b_req_op(o_b_req_op),
.b_req_cookie(o_b_req_cookie),
.b_req_node(o_b_req_node),
.b_req_net(o_b_req_net),
.b_rsp_valid(o_b_rsp_valid),
.b_rsp_ready(o_b_rsp_ready),
.b_rsp_status(o_b_rsp_status),
.b_rsp_cookie(o_b_rsp_cookie),
.b_rsp_count(o_b_rsp_count),
.b_rsp_occupancy(o_b_rsp_occupancy),
.b_rsp_will_overuse(o_b_rsp_will_overuse),
.b_fault(o_b_fault),
.host_pending(o_host_pending),
.busy(o_busy),
.fault(o_fault)
);
 // One accepted backend operation at a time; access bridge wins arbitration.
 reg owner_mux_pending,owner_mux_prefetch;
 wire mux_req_valid,mux_req_ready,mux_rsp_valid,mux_rsp_ready,mux_rsp_will_overuse;
 wire [2:0] mux_req_op;
 wire [31:0] mux_req_cookie,mux_req_node,mux_req_net,mux_rsp_cookie,mux_rsp_count,mux_rsp_occupancy;
 wire [3:0] mux_rsp_status;
 assign mux_req_valid=!owner_mux_pending&&(o_b_req_valid||p_o_req_valid);
 assign mux_req_op=o_b_req_valid?o_b_req_op:3'd0;
 assign mux_req_cookie=o_b_req_valid?o_b_req_cookie:p_o_req_cookie;
 assign mux_req_node=o_b_req_valid?o_b_req_node:p_o_req_node;
 assign mux_req_net=o_b_req_valid?o_b_req_net:p_o_req_net;
 assign o_b_req_ready=!owner_mux_pending&&mux_req_ready;
 assign p_o_req_ready=!owner_mux_pending&&!o_b_req_valid&&mux_req_ready;
 assign o_b_rsp_valid=owner_mux_pending&&!owner_mux_prefetch&&mux_rsp_valid;
 assign p_o_rsp_valid=owner_mux_pending&&owner_mux_prefetch&&mux_rsp_valid;
 assign mux_rsp_ready=owner_mux_pending&&(owner_mux_prefetch?p_o_rsp_ready:o_b_rsp_ready);
 assign o_b_rsp_status=mux_rsp_status;assign p_o_rsp_status=mux_rsp_status;
 assign o_b_rsp_cookie=mux_rsp_cookie;assign p_o_rsp_cookie=mux_rsp_cookie;
 assign o_b_rsp_count=mux_rsp_count;assign p_o_rsp_count=mux_rsp_count;
 assign o_b_rsp_occupancy=mux_rsp_occupancy;assign p_o_rsp_occupancy=mux_rsp_occupancy;
 assign o_b_rsp_will_overuse=mux_rsp_will_overuse;
 always @(posedge clk)begin
  if(rst)begin owner_mux_pending<=0;owner_mux_prefetch<=0;end
  else begin
   if(mux_rsp_valid&&mux_rsp_ready)owner_mux_pending<=0;
   if(mux_req_valid&&mux_req_ready)begin owner_mux_pending<=1;owner_mux_prefetch<=!o_b_req_valid;end
  end
 end
 owner_state_store owner_store(
.clk(clk),
.rst(rst),
.abort(abort||stopped),
.cfg_valid(owner_cfg_valid&&!operation_pending&&!o_host_pending),
.cfg_ready(owner_raw_cfg_ready),
.cfg_primary(owner_cfg_primary),
.cfg_pool(owner_cfg_pool),
.cfg_allocator(owner_cfg_allocator),
.cfg_nodes(owner_cfg_nodes),
.cfg_capacity(owner_cfg_capacity),
.cfg_rsp_valid(owner_cfg_rsp_valid),
.cfg_rsp_ready(owner_cfg_rsp_ready),
.cfg_status(owner_cfg_status),
.configured(owner_configured),
.req_valid(mux_req_valid),
.req_ready(mux_req_ready),
.req_op(mux_req_op),
.req_cookie(mux_req_cookie),
.req_node(mux_req_node),
.req_net(mux_req_net),
.rsp_valid(mux_rsp_valid),
.rsp_ready(mux_rsp_ready),
.rsp_status(mux_rsp_status),
.rsp_cookie(mux_rsp_cookie),
.rsp_count(mux_rsp_count),
.rsp_occupancy(mux_rsp_occupancy),
.rsp_will_overuse(mux_rsp_will_overuse),
.fault(o_b_fault),
.busy(u_busy),
.m_araddr(owner_m_araddr),
.m_arlen(owner_m_arlen),
.m_arsize(owner_m_arsize),
.m_arburst(owner_m_arburst),
.m_arid(owner_m_arid),
.m_arvalid(owner_m_arvalid),
.m_arready(owner_m_arready),
.m_rdata(owner_m_rdata),
.m_rid(owner_m_rid),
.m_rresp(owner_m_rresp),
.m_rlast(owner_m_rlast),
.m_rvalid(owner_m_rvalid),
.m_rready(owner_m_rready),
.m_awaddr(owner_m_awaddr),
.m_awlen(owner_m_awlen),
.m_awsize(owner_m_awsize),
.m_awburst(owner_m_awburst),
.m_awid(owner_m_awid),
.m_awvalid(owner_m_awvalid),
.m_awready(owner_m_awready),
.m_wdata(owner_m_wdata),
.m_wstrb(owner_m_wstrb),
.m_wlast(owner_m_wlast),
.m_wvalid(owner_m_wvalid),
.m_wready(owner_m_wready),
.m_bid(owner_m_bid),
.m_bresp(owner_m_bresp),
.m_bvalid(owner_m_bvalid),
.m_bready(owner_m_bready)
);
 recursive_candidate_controller #(.MAX_CYCLES(MAX_CYCLES)) controller(
.active_version(frame_version),.active_design(frame_design),.e_context(captured_context),.e_depth(capture_depth),.e_expand_context(controller_expand_context),.out_parent(current_parent),.out_root_cookie(current_root_cookie),
.clk(clk),
.rst(rst),
.enable(can_start),
.abort(abort),
.subsystem_fault(subsystem_fault),
.nodes(held_g_nodes),
.active(p_active),
.active_query(p_active_query),
.active_price(p_active_price),
.expand_valid(expand_valid),
.expand_ready(expand_ready),
.expand_cookie(expand_cookie),
.expand_parent(expand_parent),
.expand_prune(expand_prune),
.expand_has_laguna(expand_has_laguna),
.expand_sink(expand_sink),
.expand_net(expand_net),
.expand_sequence(expand_sequence),
.expand_flags(expand_flags),
.expand_xmin(expand_xmin),
.expand_xmax(expand_xmax),
.expand_ymin(expand_ymin),
.expand_ymax(expand_ymax),
.out_valid(out_valid),
.out_ready(out_ready),
.out_cookie(out_cookie),
.out_node(out_node),
.out_position(out_position),
.out_sequence(out_sequence),
.out_bits(out_bits),
.out_action(out_action),
.out_steps(out_steps),
.out_services(out_services),
.out_attrs(out_attrs),
.out_config(out_config),
.result_valid(result_valid),
.result_ready(result_ready),
.result_status(result_status),
.result_cookie(result_cookie),
.result_count(result_count),
.result_expanded_count(result_expanded_count),
.result_raw_count(result_raw_count),
.result_mask(result_mask),
.result_hit(result_hit),
.result_early(result_early),
.operation_pending(operation_pending),
.stopped(stopped),
.e_expand_valid(e_expand_valid),
.e_expand_ready(e_expand_ready),
.e_expand_cookie(e_expand_cookie),
.e_expand_parent(e_expand_parent),
.e_expand_prune(e_expand_prune),
.e_expand_has_laguna(e_expand_has_laguna),
.e_out_valid(e_out_valid),
.e_out_ready(e_out_ready),
.e_out_node(e_out_node),
.e_out_position(e_out_position),
.e_out_sequence(e_out_sequence),
.e_out_attrs(e_out_attrs),
.e_result_valid(e_result_valid),
.e_result_ready(e_result_ready),
.e_result_status(e_result_status),
.e_result_cookie(e_result_cookie),
.e_result_count(e_result_count),
.e_result_raw_count(e_result_raw_count),
.e_result_mask(e_result_mask),
.e_result_hit(e_result_hit),
.m_req_valid(m_req_valid),
.m_req_ready(m_req_ready),
.m_req_cookie(m_req_cookie),
.m_req_parent(m_req_parent),
.m_req_child(m_req_child),
.m_req_sink(m_req_sink),
.m_req_net(m_req_net),
.m_req_sequence(m_req_sequence),
.m_req_flags(m_req_flags),
.m_req_xmin(m_req_xmin),
.m_req_xmax(m_req_xmax),
.m_req_ymin(m_req_ymin),
.m_req_ymax(m_req_ymax),
.m_req_query(m_req_query),
.m_req_price(m_req_price),
.m_rsp_valid(m_rsp_valid),
.m_rsp_ready(m_rsp_ready),
.m_rsp_status(m_rsp_status),
.m_rsp_cookie(m_rsp_cookie),
.m_rsp_parent(m_rsp_parent),
.m_rsp_child(m_rsp_child),
.m_rsp_sink(m_rsp_sink),
.m_rsp_net(m_rsp_net),
.m_rsp_query(m_rsp_query),
.m_rsp_price(m_rsp_price),
.m_rsp_config(m_rsp_config),
.m_rsp_created(m_rsp_created),
.a_req_valid(a_req_valid),
.a_req_ready(a_req_ready),
.a_req_cookie(a_req_cookie),
.a_req_parent(a_req_parent),
.a_req_child(a_req_child),
.a_req_sink(a_req_sink),
.a_req_net(a_req_net),
.a_req_query(a_req_query),
.a_req_price(a_req_price),
.a_req_config(a_req_config),
.a_rsp_valid(a_rsp_valid),
.a_rsp_ready(a_rsp_ready),
.a_rsp_status(a_rsp_status),
.a_rsp_cookie(a_rsp_cookie),
.a_rsp_parent(a_rsp_parent),
.a_rsp_child(a_rsp_child),
.a_rsp_sink(a_rsp_sink),
.a_rsp_net(a_rsp_net),
.a_rsp_bits(a_rsp_bits),
.a_rsp_action(a_rsp_action),
.a_rsp_steps(a_rsp_steps),
.a_rsp_services(a_rsp_services),
.a_rsp_query(a_rsp_query),
.a_rsp_price(a_rsp_price)
);
endmodule
