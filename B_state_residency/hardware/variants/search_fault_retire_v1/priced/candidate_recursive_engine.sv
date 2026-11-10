`timescale 1ns/1ps
module candidate_recursive_engine #(parameter integer SLOTS=32,TX_BITS=16,GEN_BITS=16,FRAMES=163840,INDEX_BITS=18,HASH_BITS=18,PROBE_LIMIT=64,EPOCH_BITS=16,TOKEN_BITS=32,OWNER_BITS=32,MAX_CYCLES=33554432)(
output wire out_offer_valid,output wire [3:0] out_offer_status,output wire [31:0] out_offer_key,out_offer_node,out_offer_before,out_offer_size,
output wire [31:0] seed_rsp_key,seed_rsp_id,
output wire out_commit_valid,output wire [3:0] out_commit_status,output wire [2:0] out_commit_acked,output wire [159:0] out_commit_payload,
output wire out_cost_valid,output wire [3:0] out_cost_status,output wire [159:0] out_cost_words,output wire [735:0] out_cost_packet,
output wire [415:0] out_cost_geometry,output wire [127:0] out_cost_geometry_result,
input wire [31:0] expand_connection,
input wire q_cfg_valid,output wire q_cfg_ready,input wire [63:0] q_cfg_base,q_cfg_design,
input wire [31:0] q_cfg_connections,q_cfg_nodes,q_cfg_nets,q_cfg_revision,
output wire q_cfg_rsp_valid,input wire q_cfg_rsp_ready,output wire [2:0] q_cfg_status,output wire q_configured,
output wire out_params_valid,output wire [511:0] out_params,output wire [31:0] out_connection,out_profile_revision,
output wire q_busy,q_fault,
output wire [63:0] q_m_araddr,output wire [7:0] q_m_arlen,output wire [2:0] q_m_arsize,output wire [1:0] q_m_arburst,output wire [3:0] q_m_arid,
output wire q_m_arvalid,input wire q_m_arready,input wire [511:0] q_m_rdata,input wire [3:0] q_m_rid,input wire [1:0] q_m_rresp,input wire q_m_rlast,q_m_rvalid,output wire q_m_rready,
output wire out_post_valid,output wire [3:0] out_post_status,
output wire [31:0] out_post_x,out_post_y,out_post_upstream,out_post_distance,
output wire [255:0] out_post_attrs,output wire out_post_prev_read,
input wire seed_valid,output wire seed_ready,input wire [31:0] seed_op,seed_key,seed_id,seed_cookie,seed_version,
output wire seed_rsp_valid,input wire seed_rsp_ready,output wire [31:0] seed_rsp_status,seed_rsp_cookie,seed_rsp_size,
output wire out_prep_valid,
output wire [31:0] out_prep_count,out_prep_occupancy,out_prep_price_index,out_prep_history,out_prep_price_value,
output wire [127:0] out_prep_net_data,
output wire [3:0] out_prep_status,
input wire cc_req_valid,
output wire cc_req_ready,
input wire [127:0] cc_req_words,
input wire [31:0] cc_req_cookie,cc_req_version,
input wire [63:0] cc_req_design_id,
input wire [1:0] cc_req_query,
input wire [3:0] cc_req_price,
output wire cc_rsp_valid,
input wire cc_rsp_ready,
output wire [63:0] cc_rsp_words,
output wire [31:0] cc_rsp_cookie,cc_rsp_version,
output reg [63:0] cc_rsp_design_id,
output wire [1:0] cc_rsp_query,cc_rsp_status,
output wire [3:0] cc_rsp_price,
output wire cc_busy,cc_fault,
output wire  operation_pending,
output wire retired_idle,
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
output wire  busy,
input wire [63:0] design_id,
input wire [31:0] host_ctrl_version,
input wire [31:0] expand_version,
output reg [31:0] query_version,
output wire  query_ready,
output reg  cost_lease,
input wire  cs_cfg_valid,
output wire  cs_cfg_ready,
input wire [63:0] cs_cfg_history,
input wire [63:0] cs_cfg_prices,
input wire [63:0] cs_cfg_nets,
input wire [63:0] cs_cfg_design_id,
input wire [31:0] cs_cfg_nodes,
input wire [31:0] cs_cfg_net_count,
input wire [31:0] cs_cfg_version,
output wire  cs_cfg_rsp_valid,
input wire  cs_cfg_rsp_ready,
output wire [2:0] cs_cfg_status,
output wire  cs_configured,
output wire  cs_ready_for_query,
output wire  cs_editing,
output wire [31:0] cs_published_version,
output wire [63:0] cs_design_id,
input wire  cs_req_valid,
output wire  cs_req_ready,
input wire  cs_req_host,
input wire [2:0] cs_req_op,
input wire [31:0] cs_req_cookie,
input wire [31:0] cs_req_index,
input wire [31:0] cs_req_value,
input wire [31:0] cs_req_version,
input wire [1:0] cs_req_query,
input wire [3:0] cs_req_price,
output wire  cs_rsp_valid,
input wire  cs_rsp_ready,
output wire [3:0] cs_rsp_status,
output wire [31:0] cs_rsp_cookie,
output wire [31:0] cs_rsp_index,
output wire [31:0] cs_rsp_version,
output wire [2:0] cs_rsp_op,
output wire  cs_rsp_host,
output wire [1:0] cs_rsp_query,
output wire [3:0] cs_rsp_price,
output wire [127:0] cs_rsp_data,
output wire  cs_busy,
output wire  cs_fault,
output wire [63:0] cs_m_araddr,
output wire [7:0] cs_m_arlen,
output wire [2:0] cs_m_arsize,
output wire [1:0] cs_m_arburst,
output wire [3:0] cs_m_arid,
output wire  cs_m_arvalid,
input wire  cs_m_arready,
input wire [511:0] cs_m_rdata,
input wire [3:0] cs_m_rid,
input wire [1:0] cs_m_rresp,
input wire  cs_m_rlast,
input wire  cs_m_rvalid,
output wire  cs_m_rready,
output wire [63:0] cs_m_awaddr,
output wire [7:0] cs_m_awlen,
output wire [2:0] cs_m_awsize,
output wire [1:0] cs_m_awburst,
output wire [3:0] cs_m_awid,
output wire  cs_m_awvalid,
input wire  cs_m_awready,
output wire [511:0] cs_m_wdata,
output wire [63:0] cs_m_wstrb,
output wire  cs_m_wlast,
output wire  cs_m_wvalid,
input wire  cs_m_wready,
input wire [3:0] cs_m_bid,
input wire [1:0] cs_m_bresp,
input wire  cs_m_bvalid,
output wire  cs_m_bready
);
wire center_retired_idle,prefetch_retired_idle,post_retired_idle,frontier_retired_idle,k_retired_idle;
wire offer_busy,offer_fault,offer_ready,offer_req_valid;reg offer_started;
wire [31:0] offer_cookie,offer_version,offer_backend_status;wire [1:0] offer_query;wire [3:0] offer_price;wire [63:0] offer_design;
wire of_valid,of_ready,of_rsp_valid,of_rsp_ready;wire [31:0] of_key,of_id,of_cookie,of_version,of_rsp_status,of_rsp_cookie,of_rsp_size,of_rsp_version;wire [63:0] of_design,of_rsp_design;wire [1:0] of_query,of_rsp_query;wire [3:0] of_price,of_rsp_price;
wire offer_identity_error;
wire k_reply_error=out_cost_valid&&out_cost_status!=0;
wire commit_busy,commit_fault,commit_ready,commit_req_valid;reg commit_started;
wire [31:0] commit_cookie,commit_parent,commit_child,commit_sequence,commit_version;wire [1:0] commit_query;wire [3:0] commit_price;wire [63:0] commit_design;
wire cl_valid,cl_ready,cl_write,cl_rsp_valid,cl_rsp_ready,cl_present;wire [31:0] cl_node,cl_value;wire [2:0] cl_field;wire [3:0] cl_status;wire [159:0] cl_payload;
wire commit_identity_error;
wire k_busy,k_fault,k_ready,k_req_valid;reg k_started;
wire [31:0] k_cookie,k_child,k_version;wire [1:0] k_query;wire [3:0] k_price;wire [63:0] k_design;
wire kc_valid,kc_ready,kc_rsp_valid,kc_rsp_ready;wire [31:0] kc_cookie,kc_node,kc_rsp_cookie,kc_rsp_node,kc_y,kc_slr,kc_next,kc_prev;
wire [1:0] kc_query,kc_op,kc_rsp_op,kc_rsp_query;wire [3:0] kc_price,kc_status,kc_rsp_price;wire [255:0] kc_attrs;
wire k_identity_error;
wire q_req_ready,q_rsp_valid,q_cfg_raw_ready,raw_result_valid,raw_result_ready;
wire [3:0] q_rsp_status;wire [511:0] q_rsp_data;
wire [31:0] q_rsp_cookie,q_rsp_connection,q_rsp_net,q_rsp_sink,q_rsp_cross,q_rsp_version,q_rsp_revision;
wire [1:0] q_rsp_query;wire [3:0] q_rsp_price;wire [63:0] q_rsp_design,q_design;
wire [31:0] q_nodes,q_nets,q_connections,q_revision;
reg q_pending,q_meta_valid,q_stopped,q_started,q_result_failed;wire[3:0]raw_result_status;reg [511:0] q_meta;
reg [31:0] q_cookie,q_connection,q_net,q_sink,q_cross,q_version,q_profile,cost_nets;
reg [1:0] q_query;reg [3:0] q_price;reg [63:0] q_design_held;
wire q_lease=q_pending||q_busy;
wire q_identity_error;
wire raw_cs_req_valid,raw_cs_req_ready;
wire core_busy,core_retired_idle,state_lease;
reg query_owned,fence_stopped;
wire prefetch_busy,prefetch_fault,raw_out_valid,raw_out_ready,prefetch_ready;
wire po_req_valid,po_req_ready,po_rsp_valid,po_rsp_ready;
wire [31:0] po_req_cookie,po_req_node,po_req_net,po_rsp_cookie,po_rsp_count,po_rsp_occupancy;
wire [3:0] po_rsp_status;
wire pc_req_valid,pc_req_ready,pc_rsp_valid,pc_rsp_ready,pc_rsp_host;
wire [2:0] pc_req_op,pc_rsp_op;
wire [31:0] pc_req_cookie,pc_req_index,pc_req_version,pc_rsp_cookie,pc_rsp_index,pc_rsp_version;
wire [1:0] pc_req_query,pc_rsp_query;wire [3:0] pc_req_price,pc_rsp_price,pc_rsp_status;
wire [127:0] pc_rsp_data;
wire [31:0] prep_cookie,prep_node,prep_net,prep_version;wire [63:0] prep_design;
wire [1:0] prep_query;wire [3:0] prep_price;
reg prep_started,raw_seen,post_started;reg [31:0] held_net;wire[31:0]held_parent,held_root_cookie;

wire post_busy,post_fault,post_req_ready,post_req_valid;
wire frontier_expand_ready,frontier_close_ready,frontier_initialized,frontier_busy,frontier_fault;
wire [31:0] frontier_size;
wire pf_valid,pf_ready,pf_rsp_valid,pf_rsp_ready;wire [31:0] pf_cookie,pf_rsp_status,pf_rsp_cookie,pf_rsp_size;
wire [1:0] pf_query,pf_rsp_query;wire [3:0] pf_price,pf_rsp_price;
wire pl_valid,pl_ready,pl_write,pl_rsp_valid,pl_rsp_ready,pl_present;
wire [31:0] pl_node,pl_value;wire [2:0] pl_field;wire [3:0] pl_status;wire [159:0] pl_payload;
wire pc2_valid,pc2_ready,pc2_rsp_valid,pc2_rsp_ready,pc2_prev_read;
wire [31:0] pc2_cookie,pc2_node,pc2_rsp_cookie,pc2_rsp_node,pc2_y,pc2_label_prev;
wire [1:0] pc2_query,pc2_rsp_query,pc2_rsp_op;wire [3:0] pc2_price,pc2_rsp_price,pc2_status;wire [255:0] pc2_attrs;
wire [31:0] post_cookie,post_parent,post_child,post_version;wire [63:0] post_design;wire [1:0] post_query;wire [3:0] post_price;
wire post_identity_error=out_post_valid&&(post_cookie!=out_sequence||post_parent!=held_parent||post_child!=out_node||post_query!=p_active_query||post_price!=p_active_price||post_version!=query_version||post_design!=design_id);

postprev_inputs post_inputs(
 .clk(clk),.rst(rst),.abort((abort||fence_stopped)&&post_started),.active(p_active),.decision_lock(operation_pending),.active_query(p_active_query),.active_price(p_active_price),.active_version(query_version),.active_design(design_id),
 .req_valid(post_req_valid),.req_ready(post_req_ready),.req_early(out_bits[2]),.req_cookie(out_sequence),.req_parent(held_parent),.req_child(out_node),.req_centers(out_prep_net_data[63:0]),
 .rsp_valid(out_post_valid),.rsp_ready(raw_out_valid&&raw_out_ready&&out_action!=0),.rsp_status(out_post_status),.rsp_cookie(post_cookie),.rsp_parent(post_parent),.rsp_child(post_child),
 .rsp_x(out_post_x),.rsp_y(out_post_y),.rsp_upstream(out_post_upstream),.rsp_distance(out_post_distance),.rsp_attrs(out_post_attrs),.rsp_prev_read(out_post_prev_read),.rsp_query(post_query),.rsp_price(post_price),.rsp_version(post_version),.rsp_design(post_design),.busy(post_busy),.fault(post_fault),.retired_idle(post_retired_idle),
 .f_req_valid(pf_valid),.f_req_ready(pf_ready),.f_req_cookie(pf_cookie),.f_req_query(pf_query),.f_req_price(pf_price),.f_rsp_valid(pf_rsp_valid),.f_rsp_ready(pf_rsp_ready),.f_rsp_status(pf_rsp_status),.f_rsp_cookie(pf_rsp_cookie),.f_rsp_size(pf_rsp_size),.f_rsp_query(pf_rsp_query),.f_rsp_price(pf_rsp_price),
 .l_valid(pl_valid),.l_ready(pl_ready),.l_write(pl_write),.l_node(pl_node),.l_value(pl_value),.l_field(pl_field),.l_rsp_valid(pl_rsp_valid),.l_rsp_ready(pl_rsp_ready),.l_status(pl_status),.l_payload(pl_payload),.l_present(pl_present),
 .c_req_valid(pc2_valid),.c_req_ready(pc2_ready),.c_req_cookie(pc2_cookie),.c_req_node(pc2_node),.c_req_query(pc2_query),.c_req_price(pc2_price),.c_rsp_valid(pc2_rsp_valid),.c_rsp_ready(pc2_rsp_ready),.c_rsp_status(pc2_status),.c_rsp_cookie(pc2_rsp_cookie),.c_rsp_node(pc2_rsp_node),.c_rsp_y(pc2_y),.c_rsp_label_prev(pc2_label_prev),.c_rsp_attrs(pc2_attrs),.c_rsp_op(pc2_rsp_op),.c_rsp_query(pc2_rsp_query),.c_rsp_price(pc2_rsp_price),.c_rsp_prev_read(pc2_prev_read));
query_frontier_offer frontier(
 .design_id(design_id),.offer_valid(of_valid),.offer_ready(of_ready),.offer_key(of_key),.offer_id(of_id),.offer_cookie(of_cookie),.offer_version(of_version),.offer_design(of_design),.offer_query(of_query),.offer_price(of_price),
 .offer_rsp_valid(of_rsp_valid),.offer_rsp_ready(of_rsp_ready),.offer_rsp_status(of_rsp_status),.offer_rsp_cookie(of_rsp_cookie),.offer_rsp_size(of_rsp_size),.offer_rsp_version(of_rsp_version),.offer_rsp_design(of_rsp_design),.offer_rsp_query(of_rsp_query),.offer_rsp_price(of_rsp_price),.seed_rsp_key(seed_rsp_key),.seed_rsp_id(seed_rsp_id),
 .clk(clk),.rst(rst),.abort(abort||fence_stopped),.query_active(p_active),.query_owned(query_owned),.decision_lock(operation_pending),.close_requested(host_ctrl_valid&&host_ctrl_op==2),.may_close(!core_busy&&!state_lease),
 .query_id(p_active_query),.price(p_active_price),.version(query_version),.ready_for_expand(frontier_expand_ready),.ready_for_close(frontier_close_ready),.initialized(frontier_initialized),.busy(frontier_busy),.fault(frontier_fault),.retired_idle(frontier_retired_idle),
 .clear_valid(pf_valid),.clear_ready(pf_ready),.clear_cookie(pf_cookie),.clear_query(pf_query),.clear_price(pf_price),.clear_rsp_valid(pf_rsp_valid),.clear_rsp_ready(pf_rsp_ready),.clear_rsp_status(pf_rsp_status),.clear_rsp_cookie(pf_rsp_cookie),.clear_rsp_size(pf_rsp_size),.clear_rsp_query(pf_rsp_query),.clear_rsp_price(pf_rsp_price),
 .seed_valid(seed_valid),.seed_ready(seed_ready),.seed_op(seed_op),.seed_key(seed_key),.seed_id(seed_id),.seed_cookie(seed_cookie),.seed_version(seed_version),.seed_rsp_valid(seed_rsp_valid),.seed_rsp_ready(seed_rsp_ready),.seed_rsp_status(seed_rsp_status),.seed_rsp_cookie(seed_rsp_cookie),.seed_rsp_size(seed_rsp_size),.heap_size(frontier_size));

wire prep_req_valid;
reg prep_offered;
 assign prep_req_valid=!rst&&(prep_offered||(!fault&&!abort&&(raw_seen&&raw_out_valid&&out_action!=0&&!prep_started)));
 always @(posedge clk)begin
  if(rst)prep_offered<=0;
  else if(prep_req_valid)prep_offered<=!prefetch_ready;
 end
reg post_offered;
 assign post_req_valid=!rst&&(post_offered||(!fault&&!abort&&(q_meta_valid&&raw_seen&&raw_out_valid&&out_action!=0&&out_prep_valid&&!post_started)));
 always @(posedge clk)begin
  if(rst)post_offered<=0;
  else if(post_req_valid)post_offered<=!post_req_ready;
 end
reg k_offered;
 assign k_req_valid=!rst&&(k_offered||(!fault&&!abort&&(q_meta_valid&&raw_seen&&raw_out_valid&&out_action!=0&&out_prep_valid&&out_post_valid&&!k_started)));
 always @(posedge clk)begin
  if(rst)k_offered<=0;
  else if(k_req_valid)k_offered<=!k_ready;
 end
reg commit_offered;
 assign commit_req_valid=!rst&&(commit_offered||(!fault&&!abort&&(!fault&&out_cost_status==0&&q_meta_valid&&raw_seen&&raw_out_valid&&out_action!=0&&out_cost_valid&&!commit_started)));
 always @(posedge clk)begin
  if(rst)commit_offered<=0;
  else if(commit_req_valid)commit_offered<=!commit_ready;
 end
reg offer_offered;
 assign offer_req_valid=!rst&&(offer_offered||(!fault&&!abort&&(!fault&&q_meta_valid&&raw_seen&&raw_out_valid&&out_action==1&&out_cost_valid&&out_cost_status==0&&out_commit_valid&&out_commit_status==0&&out_commit_acked==7&&!offer_started)));
 always @(posedge clk)begin
  if(rst)offer_offered<=0;
  else if(offer_req_valid)offer_offered<=!offer_ready;
 end
wire failed_candidate_retired=fault&&
 !prep_req_valid&&(!prep_started||out_prep_valid)&&
 !post_req_valid&&(!post_started||out_post_valid)&&
 !k_req_valid&&(!k_started||out_cost_valid)&&
 !commit_req_valid&&(!commit_started||out_commit_valid)&&
 !offer_req_valid&&(!offer_started||out_offer_valid);
assign out_valid=(q_meta_valid||(q_result_failed&&!q_lease))&&raw_seen&&raw_out_valid&&(failed_candidate_retired||out_action==0||(out_prep_valid&&out_post_valid&&out_cost_valid&&out_commit_valid&&(out_action==2||(out_offer_valid&&out_offer_status==0))));
assign raw_out_ready=out_ready&&out_valid;
always @(posedge clk)begin
 if(rst)begin prep_started<=0;raw_seen<=0;held_net<=0;post_started<=0;end
 else begin
  if(raw_out_valid)raw_seen<=1;
  if(raw_out_valid&&raw_out_ready)raw_seen<=0;
  if(expand_valid&&expand_ready)begin held_net<=expand_net;end
  if(raw_out_valid&&raw_out_ready)post_started<=0;
  else if(post_req_valid&&post_req_ready)post_started<=1;
  if(raw_out_valid&&raw_out_ready)prep_started<=0;
  else if(prep_req_valid&&prefetch_ready)prep_started<=1;
 end
end
cost_inputs_prefetch prefetch(
 .clk(clk),.rst(rst),.abort((abort||fence_stopped)&&prep_started),.active(p_active),.decision_lock(operation_pending),
 .active_query(p_active_query),.active_price(p_active_price),.active_version(query_version),.active_design(design_id),
 .req_valid(prep_req_valid),.req_ready(prefetch_ready),.req_cookie(out_sequence),.req_node(out_node),.req_net(held_net),
 .rsp_valid(out_prep_valid),.rsp_ready(raw_out_valid&&raw_out_ready&&out_action!=0),
 .rsp_cookie(prep_cookie),.rsp_node(prep_node),.rsp_net(prep_net),.rsp_count(out_prep_count),.rsp_occupancy(out_prep_occupancy),.rsp_price_index(out_prep_price_index),
 .rsp_history(out_prep_history),.rsp_price_value(out_prep_price_value),.rsp_net_data(out_prep_net_data),
 .rsp_query(prep_query),.rsp_price(prep_price),.rsp_status(out_prep_status),.rsp_version(prep_version),.rsp_design(prep_design),.busy(prefetch_busy),.fault(prefetch_fault),.retired_idle(prefetch_retired_idle),
 .o_req_valid(po_req_valid),.o_req_ready(po_req_ready),.o_req_cookie(po_req_cookie),.o_req_node(po_req_node),.o_req_net(po_req_net),
 .o_rsp_valid(po_rsp_valid),.o_rsp_ready(po_rsp_ready),.o_rsp_cookie(po_rsp_cookie),.o_rsp_count(po_rsp_count),.o_rsp_occupancy(po_rsp_occupancy),.o_rsp_status(po_rsp_status),
 .c_req_valid(pc_req_valid),.c_req_ready(pc_req_ready),.c_req_op(pc_req_op),.c_req_cookie(pc_req_cookie),.c_req_index(pc_req_index),.c_req_version(pc_req_version),.c_req_query(pc_req_query),.c_req_price(pc_req_price),
 .c_rsp_valid(pc_rsp_valid),.c_rsp_ready(pc_rsp_ready),.c_rsp_status(pc_rsp_status),.c_rsp_cookie(pc_rsp_cookie),.c_rsp_index(pc_rsp_index),.c_rsp_version(pc_rsp_version),
 .c_rsp_op(pc_rsp_op),.c_rsp_host(pc_rsp_host),.c_rsp_query(pc_rsp_query),.c_rsp_price(pc_rsp_price),.c_rsp_data(pc_rsp_data));
// Response ownership is latched at request acceptance, never inferred from current VALID.
reg cs_mux_pending,cs_mux_prefetch;
wire mux_c_req_valid,mux_c_req_ready,mux_c_rsp_valid,mux_c_rsp_ready;
wire [3:0] mux_c_rsp_status,mux_c_rsp_price;wire [2:0] mux_c_rsp_op;
wire mux_c_rsp_host;wire [1:0] mux_c_rsp_query;
wire [31:0] mux_c_rsp_cookie,mux_c_rsp_index,mux_c_rsp_version;wire [127:0] mux_c_rsp_data;
assign mux_c_req_valid=!cs_mux_pending&&(pc_req_valid||raw_cs_req_valid);
assign pc_req_ready=!cs_mux_pending&&mux_c_req_ready;
assign raw_cs_req_ready=!cs_mux_pending&&!pc_req_valid&&mux_c_req_ready;
assign pc_rsp_valid=cs_mux_pending&&cs_mux_prefetch&&mux_c_rsp_valid;
assign cs_rsp_valid=cs_mux_pending&&!cs_mux_prefetch&&mux_c_rsp_valid;
assign mux_c_rsp_ready=cs_mux_pending&&(cs_mux_prefetch?pc_rsp_ready:cs_rsp_ready);
assign {pc_rsp_status,pc_rsp_cookie,pc_rsp_index,pc_rsp_version,pc_rsp_op,pc_rsp_host,pc_rsp_query,pc_rsp_price,pc_rsp_data}=
 {mux_c_rsp_status,mux_c_rsp_cookie,mux_c_rsp_index,mux_c_rsp_version,mux_c_rsp_op,mux_c_rsp_host,mux_c_rsp_query,mux_c_rsp_price,mux_c_rsp_data};
assign {cs_rsp_status,cs_rsp_cookie,cs_rsp_index,cs_rsp_version,cs_rsp_op,cs_rsp_host,cs_rsp_query,cs_rsp_price,cs_rsp_data}=
 {mux_c_rsp_status,mux_c_rsp_cookie,mux_c_rsp_index,mux_c_rsp_version,mux_c_rsp_op,mux_c_rsp_host,mux_c_rsp_query,mux_c_rsp_price,mux_c_rsp_data};
always @(posedge clk)begin
 if(rst)begin cs_mux_pending<=0;cs_mux_prefetch<=0;end
 else begin
  if(mux_c_rsp_valid&&mux_c_rsp_ready)cs_mux_pending<=0;
  if(mux_c_req_valid&&mux_c_req_ready)begin cs_mux_pending<=1;cs_mux_prefetch<=pc_req_valid;end
 end
end

// Arithmetic owns the same mutation fence even after the candidate core retires.
assign state_lease=cost_lease||cc_busy||prefetch_busy||post_busy||q_lease||k_busy||commit_busy||offer_busy;
wire center_permit=operation_pending&&query_owned&&p_active&&!fault;
wire center_raw_valid=cc_req_valid&&center_permit;
wire center_raw_ready;
reg center_owned;
wire center_identity_error=(center_owned&&cc_rsp_design_id!=design_id)||
 (cc_req_valid&&operation_pending&&query_owned&&cc_req_design_id!=design_id);
assign cc_req_ready=center_raw_ready&&center_permit;
always @(posedge clk) begin
 if(rst)begin center_owned<=0;cc_rsp_design_id<=0;end
 else begin
  if(cc_rsp_valid&&cc_rsp_ready)center_owned<=0;
  if(cc_req_valid&&cc_req_ready)begin center_owned<=1;cc_rsp_design_id<=cc_req_design_id;end
 end
end
cost_center_service center(
 .clk(clk),.rst(rst),.abort(abort||fence_stopped||center_identity_error),
 .active(p_active&&query_owned),.active_query(p_active_query),.active_price(p_active_price),.active_version(query_version),
 .req_valid(center_raw_valid),.req_ready(center_raw_ready),.req_words(cc_req_words),
 .req_cookie(cc_req_cookie),.req_version(cc_req_version),.req_query(cc_req_query),.req_price(cc_req_price),
 .rsp_valid(cc_rsp_valid),.rsp_ready(cc_rsp_ready),.rsp_words(cc_rsp_words),.rsp_cookie(cc_rsp_cookie),
 .rsp_version(cc_rsp_version),.rsp_query(cc_rsp_query),.rsp_price(cc_rsp_price),.rsp_status(cc_rsp_status),
 .busy(cc_busy),.fault(cc_fault),.retired_idle(center_retired_idle));
wire center_g_cfg_ready;
assign g_cfg_ready=center_g_cfg_ready&&!(cc_busy||prefetch_busy||post_busy||q_lease||k_busy||commit_busy||offer_busy);
wire center_d_cfg_ready;
assign d_cfg_ready=center_d_cfg_ready&&!(cc_busy||prefetch_busy||post_busy||q_lease||k_busy||commit_busy||offer_busy);
wire center_t_cfg_ready;
assign t_cfg_ready=center_t_cfg_ready&&!(cc_busy||prefetch_busy||post_busy||q_lease||k_busy||commit_busy||offer_busy);
wire center_owner_cfg_ready;
assign owner_cfg_ready=center_owner_cfg_ready&&!(cc_busy||prefetch_busy||post_busy||q_lease||k_busy||commit_busy||offer_busy);
wire center_cs_cfg_ready;
assign cs_cfg_ready=center_cs_cfg_ready&&!(cc_busy||prefetch_busy||post_busy||q_lease||k_busy||commit_busy||offer_busy);
reg[31:0]g_nodes,d_nodes,owner_nodes,cost_nodes;
wire  core_host_ctrl_valid;
wire  core_host_ctrl_ready;
wire  core_host_owner_req_valid;
wire  core_host_owner_req_ready;
wire  core_expand_valid;
wire  core_expand_ready;
wire  core_host_design_req_valid;
wire  core_host_design_req_ready;
wire  core_host_io_valid;
wire  core_host_io_ready;
wire  core_fault;



wire  all_configured;
wire  configuration_fault;
wire  permit_open;
wire  permit_control;
wire  permit_expand;
wire  permit_cs_request;
wire  query_drift;
wire  bad_control_identity;
wire  bad_expand_identity;
wire  internal_fire;
assign q_cfg_ready=q_cfg_raw_ready&&!state_lease&&!fault;
assign out_params_valid=q_meta_valid&&operation_pending;
assign out_params=q_meta;assign out_connection=q_connection;assign out_profile_revision=q_profile;
wire q_completion_ready=q_meta_valid||(q_result_failed&&!q_lease);
assign result_valid=raw_result_valid&&q_completion_ready;
assign result_status=q_result_failed?4'd4:raw_result_status;
assign raw_result_ready=result_ready&&q_completion_ready;
assign q_identity_error=q_meta_valid&&operation_pending&&(!p_active||p_active_query!=q_query||p_active_price!=q_price||query_version!=q_version||design_id!=q_design_held);
always @(posedge clk)begin
 if(rst)begin q_pending<=0;q_meta_valid<=0;q_stopped<=0;q_started<=0;q_result_failed<=0;q_meta<=0;q_cookie<=0;q_connection<=0;q_net<=0;q_sink<=0;q_cross<=0;q_version<=0;q_profile<=0;q_query<=0;q_price<=0;q_design_held<=0;cost_nets<=0;end
 else begin
  if(cs_cfg_valid&&cs_cfg_ready)cost_nets<=cs_cfg_net_count;
  if(q_pending&&q_req_ready)begin q_pending<=0;q_started<=1;end
  if(expand_valid&&expand_ready)begin
   q_pending<=1;q_meta_valid<=0;q_started<=0;q_result_failed<=0;q_cookie<=expand_cookie;q_connection<=expand_connection;q_net<=expand_net;q_sink<=expand_sink;q_cross<=expand_flags&32'h18;
   q_version<=query_version;q_query<=p_active_query;q_price<=p_active_price;q_design_held<=design_id;q_profile<=q_revision;
  end
  if(q_rsp_valid)begin
   if(q_rsp_status!=0||q_rsp_cookie!=q_cookie||q_rsp_connection!=q_connection||q_rsp_net!=q_net||q_rsp_sink!=q_sink||q_rsp_cross!=q_cross||q_rsp_query!=q_query||q_rsp_price!=q_price||q_rsp_version!=q_version||q_rsp_design!=q_design_held||q_rsp_revision!=q_profile)begin q_stopped<=1;if(!q_meta_valid)q_result_failed<=1;end
   else begin q_meta<=q_rsp_data;q_meta_valid<=1;end
  end
 end
end
connection_state_reader #(.MAX_CYCLES(MAX_CYCLES)) params_reader(
 .clk(clk),.rst(rst),.abort((abort||fence_stopped)&&q_started),
 .cfg_valid(q_cfg_valid&&!state_lease&&!fault),.cfg_ready(q_cfg_raw_ready),.cfg_base(q_cfg_base),.cfg_design(q_cfg_design),.cfg_connections(q_cfg_connections),.cfg_nodes(q_cfg_nodes),.cfg_nets(q_cfg_nets),.cfg_revision(q_cfg_revision),.cfg_rsp_valid(q_cfg_rsp_valid),.cfg_rsp_ready(q_cfg_rsp_ready),.cfg_status(q_cfg_status),.configured(q_configured),.design_id(q_design),.nodes(q_nodes),.nets(q_nets),.connections(q_connections),.revision(q_revision),
 .query_active(p_active),.decision_lock(operation_pending),.active_query(p_active_query),.active_price(p_active_price),.active_version(query_version),.active_design(design_id),
 .req_valid(q_pending),.req_ready(q_req_ready),.req_cookie(q_cookie),.req_connection(q_connection),.req_net(q_net),.req_sink(q_sink),.req_cross(q_cross),.req_version(q_version),.req_query(q_query),.req_price(q_price),.req_design(q_design_held),
 .rsp_valid(q_rsp_valid),.rsp_ready(1'b1),.rsp_status(q_rsp_status),.rsp_cookie(q_rsp_cookie),.rsp_connection(q_rsp_connection),.rsp_net(q_rsp_net),.rsp_sink(q_rsp_sink),.rsp_cross(q_rsp_cross),.rsp_version(q_rsp_version),.rsp_revision(q_rsp_revision),.rsp_query(q_rsp_query),.rsp_price(q_rsp_price),.rsp_design(q_rsp_design),.rsp_data(q_rsp_data),.busy(q_busy),.fault(q_fault),
 .m_araddr(q_m_araddr),.m_arlen(q_m_arlen),.m_arsize(q_m_arsize),.m_arburst(q_m_arburst),.m_arid(q_m_arid),.m_arvalid(q_m_arvalid),.m_arready(q_m_arready),.m_rdata(q_m_rdata),.m_rid(q_m_rid),.m_rresp(q_m_rresp),.m_rlast(q_m_rlast),.m_rvalid(q_m_rvalid),.m_rready(q_m_rready));
assign k_identity_error=out_cost_valid&&(k_cookie!=out_sequence||k_child!=out_node||k_query!=p_active_query||k_price!=p_active_price||k_version!=query_version||k_design!=design_id);

always @(posedge clk)begin
 if(rst)k_started<=0;
 else if(raw_out_valid&&raw_out_ready)k_started<=0;
 else if(k_req_valid&&k_ready)k_started<=1;
end
cost23_inputs cost_inputs(.clk(clk),.rst(rst),.abort((abort||fence_stopped)&&k_started),.active(p_active),.decision_lock(operation_pending),.active_query(p_active_query),.active_price(p_active_price),.active_version(query_version),.active_design(design_id),
 .req_valid(k_req_valid),.req_ready(k_ready),.req_cookie(out_sequence),.req_child(out_node),.req_sink(q_sink),.req_params(q_meta),.req_config(out_config),.req_attrs(out_post_attrs),
 .req_count(out_prep_count),.req_history(out_prep_history),.req_price_value(out_prep_price_value),.req_x(out_post_x),.req_y(out_post_y),.req_upstream(out_post_upstream),.req_center(out_post_distance),.req_net(out_prep_net_data),
 .rsp_valid(out_cost_valid),.rsp_ready(raw_out_valid&&raw_out_ready&&out_action!=0),.rsp_status(out_cost_status),.rsp_cookie(k_cookie),.rsp_child(k_child),.rsp_version(k_version),.rsp_query(k_query),.rsp_price(k_price),.rsp_design(k_design),.rsp_packet(out_cost_packet),.rsp_cost(out_cost_words),.rsp_geometry(out_cost_geometry),.rsp_geometry_result(out_cost_geometry_result),.busy(k_busy),.fault(k_fault),.retired_idle(k_retired_idle),
 .c_req_valid(kc_valid),.c_req_ready(kc_ready),.c_req_cookie(kc_cookie),.c_req_node(kc_node),.c_req_query(kc_query),.c_req_op(kc_op),.c_req_price(kc_price),
 .c_rsp_valid(kc_rsp_valid),.c_rsp_ready(kc_rsp_ready),.c_rsp_status(kc_status),.c_rsp_cookie(kc_rsp_cookie),.c_rsp_node(kc_rsp_node),.c_rsp_y(kc_y),.c_rsp_slr(kc_slr),.c_rsp_next(kc_next),.c_rsp_prev_column(kc_prev),.c_rsp_attrs(kc_attrs),.c_rsp_op(kc_rsp_op),.c_rsp_query(kc_rsp_query),.c_rsp_price(kc_rsp_price));
assign commit_identity_error=out_commit_valid&&(commit_cookie!=out_sequence||commit_parent!=held_parent||commit_child!=out_node||commit_sequence!=out_config[31:0]||commit_query!=p_active_query||commit_price!=p_active_price||commit_version!=query_version||commit_design!=design_id);

always @(posedge clk)begin
 if(rst)commit_started<=0;
 else if(raw_out_valid&&raw_out_ready)commit_started<=0;
 else if(commit_req_valid&&commit_ready)commit_started<=1;
end
cost_label_commit commit_inputs(.clk(clk),.rst(rst),.abort((abort||fence_stopped)&&commit_started),.active(p_active),.decision_lock(operation_pending),.active_query(p_active_query),.active_price(p_active_price),.active_version(query_version),.active_design(design_id),
 .req_valid(commit_req_valid),.req_ready(commit_ready),.req_cookie(out_sequence),.req_parent(held_parent),.req_child(out_node),.req_sequence(out_config[31:0]),.req_partial(out_cost_words[95:64]),.req_total(out_cost_words[159:128]),
 .rsp_valid(out_commit_valid),.rsp_ready(raw_out_valid&&raw_out_ready&&out_action!=0),.rsp_status(out_commit_status),.rsp_acked(out_commit_acked),.rsp_cookie(commit_cookie),.rsp_parent(commit_parent),.rsp_child(commit_child),.rsp_sequence(commit_sequence),.rsp_version(commit_version),.rsp_query(commit_query),.rsp_price(commit_price),.rsp_design(commit_design),.rsp_payload(out_commit_payload),.busy(commit_busy),.fault(commit_fault),
 .l_valid(cl_valid),.l_ready(cl_ready),.l_write(cl_write),.l_node(cl_node),.l_value(cl_value),.l_field(cl_field),.l_rsp_valid(cl_rsp_valid),.l_rsp_ready(cl_rsp_ready),.l_status(cl_status),.l_payload(cl_payload),.l_present(cl_present));
assign offer_identity_error=out_offer_valid&&(offer_cookie!=out_sequence||out_offer_node!=out_node||out_offer_key!=out_cost_words[159:128]||offer_query!=p_active_query||offer_price!=p_active_price||offer_version!=query_version||offer_design!=design_id);

always @(posedge clk)begin
 if(rst)offer_started<=0;
 else if(raw_out_valid&&raw_out_ready)offer_started<=0;
 else if(offer_req_valid&&offer_ready)offer_started<=1;
end
cost_offer offer_inputs(.clk(clk),.rst(rst),.abort((abort||fence_stopped)&&offer_started),.active(p_active),.decision_lock(operation_pending),.active_query(p_active_query),.active_price(p_active_price),.active_version(query_version),.active_design(design_id),
 .req_valid(offer_req_valid),.req_ready(offer_ready),.req_cookie(out_sequence),.req_node(out_node),.req_key(out_cost_words[159:128]),.req_before(frontier_size),
 .rsp_valid(out_offer_valid),.rsp_ready(raw_out_valid&&raw_out_ready&&out_action==1),.rsp_status(out_offer_status),.rsp_cookie(offer_cookie),.rsp_node(out_offer_node),.rsp_key(out_offer_key),.rsp_before(out_offer_before),.rsp_size(out_offer_size),.rsp_version(offer_version),.rsp_backend_status(offer_backend_status),.rsp_query(offer_query),.rsp_price(offer_price),.rsp_design(offer_design),.busy(offer_busy),.fault(offer_fault),
 .f_valid(of_valid),.f_ready(of_ready),.f_key(of_key),.f_id(of_id),.f_cookie(of_cookie),.f_version(of_version),.f_design(of_design),.f_query(of_query),.f_price(of_price),
 .f_rsp_valid(of_rsp_valid),.f_rsp_ready(of_rsp_ready),.f_rsp_status(of_rsp_status),.f_rsp_cookie(of_rsp_cookie),.f_rsp_size(of_rsp_size),.f_rsp_version(of_rsp_version),.f_rsp_design(of_rsp_design),.f_rsp_query(of_rsp_query),.f_rsp_price(of_rsp_price));
assign all_configured=q_configured&&!q_cfg_rsp_valid&&g_configured&&d_configured&&owner_configured&&t_configured&&cs_configured&&!g_cfg_rsp_valid&&!d_cfg_rsp_valid&&!owner_cfg_rsp_valid&&!t_cfg_rsp_valid&&!cs_cfg_rsp_valid;
assign configuration_fault=(q_configured&&g_configured&&cs_configured&&(q_nodes!=g_nodes||q_nets!=cost_nets||q_design!=design_id))||g_configured&&d_configured&&owner_configured&&cs_configured&&(g_nodes!=d_nodes||g_nodes!=owner_nodes||g_nodes!=cost_nodes||cs_design_id!=design_id);
assign query_drift=query_owned&&p_active&&(query_version!=cs_published_version||p_active_price!=query_version[3:0]||cs_editing);
assign query_ready=frontier_initialized&&!frontier_busy&&all_configured&&cs_ready_for_query&&!core_busy&&!state_lease&&!fault;
assign permit_open=query_ready&&host_ctrl_version==cs_published_version&&host_ctrl_price==cs_published_version[3:0];
assign permit_control=(host_ctrl_op!=2||frontier_close_ready)&&!frontier_busy&&!state_lease&&!cs_busy&&!fault&&(host_ctrl_op==0?permit_open:(query_owned&&host_ctrl_version==query_version&&host_ctrl_query==p_active_query&&host_ctrl_price==p_active_price));
assign core_host_ctrl_valid=host_ctrl_valid&&permit_control;
assign host_ctrl_ready=core_host_ctrl_ready&&permit_control;
assign permit_expand=frontier_expand_ready&&!state_lease&&cs_ready_for_query&&query_owned&&!fault&&expand_version==query_version&&cs_published_version==query_version;
assign core_expand_valid=expand_valid&&permit_expand;
assign expand_ready=core_expand_ready&&permit_expand;
assign permit_cs_request=!fault&&(cs_req_host?(!core_busy&&!state_lease&&(cs_editing||(!host_ctrl_valid&&!expand_valid))):(operation_pending&&query_owned));
assign raw_cs_req_valid=cs_req_valid&&permit_cs_request&&!prefetch_busy;
assign cs_req_ready=raw_cs_req_ready&&permit_cs_request&&!prefetch_busy;
assign internal_fire=raw_cs_req_valid&&raw_cs_req_ready&&!cs_req_host;
assign bad_control_identity=host_ctrl_valid&&query_ready&&(host_ctrl_op==0?(host_ctrl_version!=cs_published_version||host_ctrl_price!=cs_published_version[3:0]):(!query_owned||host_ctrl_version!=query_version||host_ctrl_query!=p_active_query||host_ctrl_price!=p_active_price));
assign bad_expand_identity=expand_valid&&!core_busy&&!state_lease&&p_active&&cs_ready_for_query&&query_owned&&(expand_version!=query_version);
assign fault=offer_fault||offer_identity_error||k_reply_error||commit_fault||commit_identity_error||k_fault||k_identity_error||q_fault||q_stopped||q_identity_error||post_fault||post_identity_error||frontier_fault||prefetch_fault||core_fault||cs_fault||cc_fault||center_identity_error||fence_stopped||configuration_fault||query_drift;
assign busy=core_busy||cs_busy||state_lease||frontier_busy;
assign retired_idle=core_retired_idle&&!core_busy&&!cs_busy&&frontier_retired_idle&&!operation_pending&&!cost_lease&&prefetch_retired_idle&&post_retired_idle&&!q_lease&&k_retired_idle&&!commit_busy&&!offer_busy&&!center_owned&&center_retired_idle;
assign core_host_io_valid=host_io_valid&&!state_lease&&!fault;
assign host_io_ready=core_host_io_ready&&!state_lease&&!fault;
assign core_host_design_req_valid=host_design_req_valid&&!state_lease&&!fault;
assign host_design_req_ready=core_host_design_req_ready&&!state_lease&&!fault;
assign core_host_owner_req_valid=host_owner_req_valid&&!state_lease&&!fault;
assign host_owner_req_ready=core_host_owner_req_ready&&!state_lease&&!fault;
always @(posedge clk)begin
 if(rst)begin cost_lease<=0;query_owned<=0;query_version<=0;fence_stopped<=0;g_nodes<=0;d_nodes<=0;owner_nodes<=0;cost_nodes<=0;end
 else begin
  if(g_cfg_valid&&g_cfg_ready)g_nodes<=g_cfg_nodes;
  if(d_cfg_valid&&d_cfg_ready)d_nodes<=d_cfg_nodes;
  if(owner_cfg_valid&&owner_cfg_ready)owner_nodes<=owner_cfg_nodes;
  if(cs_cfg_valid&&cs_cfg_ready)cost_nodes<=cs_cfg_nodes;
  if(cost_lease&&!cs_busy)cost_lease<=0;
  if(internal_fire||(pc_req_valid&&pc_req_ready))cost_lease<=1;
  if(host_ctrl_valid&&host_ctrl_ready&&host_ctrl_op==0)begin query_owned<=1;query_version<=host_ctrl_version;end
  else if(!p_active&&!core_busy)query_owned<=0;
  if(host_ctrl_rsp_valid&&host_ctrl_rsp_ready&&host_ctrl_status!=0)query_owned<=0;
  if(offer_fault||offer_identity_error||k_reply_error||commit_fault||commit_identity_error||k_fault||k_identity_error||q_fault||q_stopped||q_identity_error||post_fault||post_identity_error||frontier_fault||prefetch_fault||core_fault||cs_fault||cc_fault||center_identity_error||configuration_fault||query_drift||bad_control_identity||bad_expand_identity)fence_stopped<=1;
 end
end
candidate_recursive_query_core #(.SLOTS(SLOTS),.TX_BITS(TX_BITS),.GEN_BITS(GEN_BITS),.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS),.PROBE_LIMIT(PROBE_LIMIT),.EPOCH_BITS(EPOCH_BITS),.TOKEN_BITS(TOKEN_BITS),.OWNER_BITS(OWNER_BITS),.MAX_CYCLES(MAX_CYCLES)) core(
.current_parent(held_parent),.current_root_cookie(held_root_cookie),
.frame_version(query_version),.frame_design(design_id),
.commit_l_valid(cl_valid),.commit_l_ready(cl_ready),.commit_l_write(cl_write),.commit_l_node(cl_node),.commit_l_value(cl_value),.commit_l_field(cl_field),.commit_l_rsp_valid(cl_rsp_valid),.commit_l_rsp_ready(cl_rsp_ready),.commit_l_status(cl_status),.commit_l_payload(cl_payload),.commit_l_present(cl_present),
.cost_c_req_valid(kc_valid),.cost_c_req_ready(kc_ready),.cost_c_req_cookie(kc_cookie),.cost_c_req_node(kc_node),.cost_c_req_query(kc_query),.cost_c_req_op(kc_op),.cost_c_req_price(kc_price),
.cost_c_rsp_valid(kc_rsp_valid),.cost_c_rsp_ready(kc_rsp_ready),.cost_c_rsp_status(kc_status),.cost_c_rsp_cookie(kc_rsp_cookie),.cost_c_rsp_node(kc_rsp_node),.cost_c_rsp_y(kc_y),.cost_c_rsp_slr(kc_slr),.cost_c_rsp_next(kc_next),.cost_c_rsp_prev_column(kc_prev),.cost_c_rsp_attrs(kc_attrs),.cost_c_rsp_op(kc_rsp_op),.cost_c_rsp_query(kc_rsp_query),.cost_c_rsp_price(kc_rsp_price),
.post_l_valid(pl_valid),
.post_l_ready(pl_ready),
.post_l_write(pl_write),
.post_l_node(pl_node),
.post_l_value(pl_value),
.post_l_field(pl_field),
.post_l_rsp_valid(pl_rsp_valid),
.post_l_rsp_ready(pl_rsp_ready),
.post_l_status(pl_status),
.post_l_payload(pl_payload),
.post_l_present(pl_present),
.post_c_req_valid(pc2_valid),
.post_c_req_ready(pc2_ready),
.post_c_req_cookie(pc2_cookie),
.post_c_req_node(pc2_node),
.post_c_req_query(pc2_query),
.post_c_req_price(pc2_price),
.post_c_rsp_valid(pc2_rsp_valid),
.post_c_rsp_ready(pc2_rsp_ready),
.post_c_rsp_status(pc2_status),
.post_c_rsp_cookie(pc2_rsp_cookie),
.post_c_rsp_node(pc2_rsp_node),
.post_c_rsp_y(pc2_y),
.post_c_rsp_label_prev(pc2_label_prev),
.post_c_rsp_attrs(pc2_attrs),
.post_c_rsp_op(pc2_rsp_op),
.post_c_rsp_query(pc2_rsp_query),
.post_c_rsp_price(pc2_rsp_price),
.post_c_rsp_prev_read(pc2_prev_read),
.p_o_req_valid(po_req_valid),.p_o_req_ready(po_req_ready),.p_o_req_cookie(po_req_cookie),.p_o_req_node(po_req_node),.p_o_req_net(po_req_net),
.p_o_rsp_valid(po_rsp_valid),.p_o_rsp_ready(po_rsp_ready),.p_o_rsp_cookie(po_rsp_cookie),.p_o_rsp_count(po_rsp_count),.p_o_rsp_occupancy(po_rsp_occupancy),.p_o_rsp_status(po_rsp_status),
.operation_pending(operation_pending),
.clk(clk),
.rst(rst),
.abort(abort||fence_stopped),
.g_cfg_valid(g_cfg_valid&&!(cc_busy||prefetch_busy||post_busy||q_lease||k_busy||commit_busy||offer_busy)),
.g_cfg_ready(center_g_cfg_ready),
.g_cfg_offsets_base(g_cfg_offsets_base),
.g_cfg_edges_base(g_cfg_edges_base),
.g_cfg_attrs_base(g_cfg_attrs_base),
.g_cfg_nodes(g_cfg_nodes),
.g_cfg_edges(g_cfg_edges),
.g_cfg_rsp_valid(g_cfg_rsp_valid),
.g_cfg_rsp_ready(g_cfg_rsp_ready),
.g_cfg_status(g_cfg_status),
.g_configured(g_configured),
.g_m_araddr(g_m_araddr),
.g_m_arlen(g_m_arlen),
.g_m_arsize(g_m_arsize),
.g_m_arburst(g_m_arburst),
.g_m_arid(g_m_arid),
.g_m_arvalid(g_m_arvalid),
.g_m_arready(g_m_arready),
.g_m_rdata(g_m_rdata),
.g_m_rid(g_m_rid),
.g_m_rresp(g_m_rresp),
.g_m_rlast(g_m_rlast),
.g_m_rvalid(g_m_rvalid),
.g_m_rready(g_m_rready),
.d_cfg_valid(d_cfg_valid&&!(cc_busy||prefetch_busy||post_busy||q_lease||k_busy||commit_busy||offer_busy)),
.d_cfg_ready(center_d_cfg_ready),
.d_cfg_base(d_cfg_base),
.d_cfg_nodes(d_cfg_nodes),
.d_cfg_rsp_valid(d_cfg_rsp_valid),
.d_cfg_rsp_ready(d_cfg_rsp_ready),
.d_cfg_status(d_cfg_status),
.d_configured(d_configured),
.d_m_araddr(d_m_araddr),
.d_m_arlen(d_m_arlen),
.d_m_arsize(d_m_arsize),
.d_m_arburst(d_m_arburst),
.d_m_arid(d_m_arid),
.d_m_arvalid(d_m_arvalid),
.d_m_arready(d_m_arready),
.d_m_rdata(d_m_rdata),
.d_m_rid(d_m_rid),
.d_m_rresp(d_m_rresp),
.d_m_rlast(d_m_rlast),
.d_m_rvalid(d_m_rvalid),
.d_m_rready(d_m_rready),
.d_m_awaddr(d_m_awaddr),
.d_m_awlen(d_m_awlen),
.d_m_awsize(d_m_awsize),
.d_m_awburst(d_m_awburst),
.d_m_awid(d_m_awid),
.d_m_awvalid(d_m_awvalid),
.d_m_awready(d_m_awready),
.d_m_wdata(d_m_wdata),
.d_m_wstrb(d_m_wstrb),
.d_m_wlast(d_m_wlast),
.d_m_wvalid(d_m_wvalid),
.d_m_wready(d_m_wready),
.d_m_bid(d_m_bid),
.d_m_bresp(d_m_bresp),
.d_m_bvalid(d_m_bvalid),
.d_m_bready(d_m_bready),
.host_ctrl_valid(core_host_ctrl_valid),
.host_ctrl_ready(core_host_ctrl_ready),
.host_ctrl_op(host_ctrl_op),
.host_ctrl_query(host_ctrl_query),
.host_ctrl_price(host_ctrl_price),
.host_ctrl_rsp_valid(host_ctrl_rsp_valid),
.host_ctrl_rsp_ready(host_ctrl_rsp_ready),
.host_ctrl_status(host_ctrl_status),
.p_active(p_active),
.p_active_query(p_active_query),
.p_active_price(p_active_price),
.p_m_awaddr(p_m_awaddr),
.p_m_awlen(p_m_awlen),
.p_m_awsize(p_m_awsize),
.p_m_awburst(p_m_awburst),
.p_m_awid(p_m_awid),
.p_m_awvalid(p_m_awvalid),
.p_m_awready(p_m_awready),
.p_m_wdata(p_m_wdata),
.p_m_wstrb(p_m_wstrb),
.p_m_wlast(p_m_wlast),
.p_m_wvalid(p_m_wvalid),
.p_m_wready(p_m_wready),
.p_m_bid(p_m_bid),
.p_m_bresp(p_m_bresp),
.p_m_bvalid(p_m_bvalid),
.p_m_bready(p_m_bready),
.p_m_araddr(p_m_araddr),
.p_m_arlen(p_m_arlen),
.p_m_arsize(p_m_arsize),
.p_m_arburst(p_m_arburst),
.p_m_arid(p_m_arid),
.p_m_arvalid(p_m_arvalid),
.p_m_arready(p_m_arready),
.p_m_rdata(p_m_rdata),
.p_m_rid(p_m_rid),
.p_m_rresp(p_m_rresp),
.p_m_rlast(p_m_rlast),
.p_m_rvalid(p_m_rvalid),
.p_m_rready(p_m_rready),
.t_cfg_valid(t_cfg_valid&&!(cc_busy||prefetch_busy||post_busy||q_lease||k_busy||commit_busy||offer_busy)),
.t_cfg_ready(center_t_cfg_ready),
.t_cfg_rows_base(t_cfg_rows_base),
.t_cfg_columns_base(t_cfg_columns_base),
.t_cfg_rows(t_cfg_rows),
.t_cfg_columns(t_cfg_columns),
.t_cfg_rsp_valid(t_cfg_rsp_valid),
.t_cfg_rsp_ready(t_cfg_rsp_ready),
.t_cfg_status(t_cfg_status),
.t_configured(t_configured),
.t_m_araddr(t_m_araddr),
.t_m_arlen(t_m_arlen),
.t_m_arsize(t_m_arsize),
.t_m_arburst(t_m_arburst),
.t_m_arid(t_m_arid),
.t_m_arvalid(t_m_arvalid),
.t_m_arready(t_m_arready),
.t_m_rdata(t_m_rdata),
.t_m_rid(t_m_rid),
.t_m_rresp(t_m_rresp),
.t_m_rlast(t_m_rlast),
.t_m_rvalid(t_m_rvalid),
.t_m_rready(t_m_rready),
.host_owner_req_valid(core_host_owner_req_valid),
.host_owner_req_ready(core_host_owner_req_ready),
.host_owner_req_op(host_owner_req_op),
.host_owner_req_cookie(host_owner_req_cookie),
.host_owner_req_node(host_owner_req_node),
.host_owner_req_net(host_owner_req_net),
.host_owner_rsp_valid(host_owner_rsp_valid),
.host_owner_rsp_ready(host_owner_rsp_ready),
.host_owner_rsp_status(host_owner_rsp_status),
.host_owner_rsp_cookie(host_owner_rsp_cookie),
.host_owner_rsp_count(host_owner_rsp_count),
.host_owner_rsp_occupancy(host_owner_rsp_occupancy),
.host_owner_rsp_will_overuse(host_owner_rsp_will_overuse),
.owner_cfg_valid(owner_cfg_valid&&!(cc_busy||prefetch_busy||post_busy||q_lease||k_busy||commit_busy||offer_busy)),
.owner_cfg_ready(center_owner_cfg_ready),
.owner_cfg_primary(owner_cfg_primary),
.owner_cfg_pool(owner_cfg_pool),
.owner_cfg_allocator(owner_cfg_allocator),
.owner_cfg_nodes(owner_cfg_nodes),
.owner_cfg_capacity(owner_cfg_capacity),
.owner_cfg_rsp_valid(owner_cfg_rsp_valid),
.owner_cfg_rsp_ready(owner_cfg_rsp_ready),
.owner_cfg_status(owner_cfg_status),
.owner_configured(owner_configured),
.owner_m_araddr(owner_m_araddr),
.owner_m_arlen(owner_m_arlen),
.owner_m_arsize(owner_m_arsize),
.owner_m_arburst(owner_m_arburst),
.owner_m_arid(owner_m_arid),
.owner_m_arvalid(owner_m_arvalid),
.owner_m_arready(owner_m_arready),
.owner_m_rdata(owner_m_rdata),
.owner_m_rid(owner_m_rid),
.owner_m_rresp(owner_m_rresp),
.owner_m_rlast(owner_m_rlast),
.owner_m_rvalid(owner_m_rvalid),
.owner_m_rready(owner_m_rready),
.owner_m_awaddr(owner_m_awaddr),
.owner_m_awlen(owner_m_awlen),
.owner_m_awsize(owner_m_awsize),
.owner_m_awburst(owner_m_awburst),
.owner_m_awid(owner_m_awid),
.owner_m_awvalid(owner_m_awvalid),
.owner_m_awready(owner_m_awready),
.owner_m_wdata(owner_m_wdata),
.owner_m_wstrb(owner_m_wstrb),
.owner_m_wlast(owner_m_wlast),
.owner_m_wvalid(owner_m_wvalid),
.owner_m_wready(owner_m_wready),
.owner_m_bid(owner_m_bid),
.owner_m_bresp(owner_m_bresp),
.owner_m_bvalid(owner_m_bvalid),
.owner_m_bready(owner_m_bready),
.expand_valid(core_expand_valid),
.expand_ready(core_expand_ready),
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
.out_valid(raw_out_valid),
.out_ready(raw_out_ready),
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
.result_valid(raw_result_valid),
.result_ready(raw_result_ready),
.result_status(raw_result_status),
.result_cookie(result_cookie),
.result_count(result_count),
.result_expanded_count(result_expanded_count),
.result_raw_count(result_raw_count),
.result_mask(result_mask),
.result_hit(result_hit),
.result_early(result_early),
.host_design_req_valid(core_host_design_req_valid),
.host_design_req_ready(core_host_design_req_ready),
.host_design_req_op(host_design_req_op),
.host_design_req_cookie(host_design_req_cookie),
.host_design_req_owner(host_design_req_owner),
.host_design_req_node(host_design_req_node),
.host_design_req_arg(host_design_req_arg),
.host_design_rsp_valid(host_design_rsp_valid),
.host_design_rsp_ready(host_design_rsp_ready),
.host_design_rsp_status(host_design_rsp_status),
.host_design_rsp_cookie(host_design_rsp_cookie),
.host_design_rsp_flags(host_design_rsp_flags),
.host_design_rsp_count(host_design_rsp_count),
.host_design_rsp_mask(host_design_rsp_mask),
.host_io_valid(core_host_io_valid),
.host_io_ready(core_host_io_ready),
.host_io_write(host_io_write),
.host_io_node(host_io_node),
.host_io_value(host_io_value),
.host_io_field(host_io_field),
.host_io_rsp_valid(host_io_rsp_valid),
.host_io_rsp_ready(host_io_rsp_ready),
.host_io_status(host_io_status),
.host_io_payload(host_io_payload),
.host_io_present(host_io_present),
.fault(core_fault),
.busy(core_busy),.retired_idle(core_retired_idle)
);
cost_state_store store(
.clk(clk),
.rst(rst),
.abort(abort||fence_stopped),
.cfg_valid(cs_cfg_valid&&!(cc_busy||prefetch_busy||post_busy||q_lease||k_busy||commit_busy||offer_busy)),
.cfg_ready(center_cs_cfg_ready),
.cfg_history(cs_cfg_history),
.cfg_prices(cs_cfg_prices),
.cfg_nets(cs_cfg_nets),
.cfg_design_id(cs_cfg_design_id),
.cfg_nodes(cs_cfg_nodes),
.cfg_net_count(cs_cfg_net_count),
.cfg_version(cs_cfg_version),
.cfg_rsp_valid(cs_cfg_rsp_valid),
.cfg_rsp_ready(cs_cfg_rsp_ready),
.cfg_status(cs_cfg_status),
.configured(cs_configured),
.query_active(p_active),
.decision_lock(operation_pending||state_lease),
.active_query(p_active_query),
.active_price(p_active_price),
.ready_for_query(cs_ready_for_query),
.editing(cs_editing),
.published_version(cs_published_version),
.design_id(cs_design_id),
.req_valid(mux_c_req_valid),
.req_ready(mux_c_req_ready),
.req_host(pc_req_valid?1'b0:cs_req_host),
.req_op(pc_req_valid?pc_req_op:cs_req_op),
.req_cookie(pc_req_valid?pc_req_cookie:cs_req_cookie),
.req_index(pc_req_valid?pc_req_index:cs_req_index),
.req_value(pc_req_valid?32'b0:cs_req_value),
.req_version(pc_req_valid?pc_req_version:cs_req_version),
.req_query(pc_req_valid?pc_req_query:cs_req_query),
.req_price(pc_req_valid?pc_req_price:cs_req_price),
.rsp_valid(mux_c_rsp_valid),
.rsp_ready(mux_c_rsp_ready),
.rsp_status(mux_c_rsp_status),
.rsp_cookie(mux_c_rsp_cookie),
.rsp_index(mux_c_rsp_index),
.rsp_version(mux_c_rsp_version),
.rsp_op(mux_c_rsp_op),
.rsp_host(mux_c_rsp_host),
.rsp_query(mux_c_rsp_query),
.rsp_price(mux_c_rsp_price),
.rsp_data(mux_c_rsp_data),
.busy(cs_busy),
.fault(cs_fault),
.m_araddr(cs_m_araddr),
.m_arlen(cs_m_arlen),
.m_arsize(cs_m_arsize),
.m_arburst(cs_m_arburst),
.m_arid(cs_m_arid),
.m_arvalid(cs_m_arvalid),
.m_arready(cs_m_arready),
.m_rdata(cs_m_rdata),
.m_rid(cs_m_rid),
.m_rresp(cs_m_rresp),
.m_rlast(cs_m_rlast),
.m_rvalid(cs_m_rvalid),
.m_rready(cs_m_rready),
.m_awaddr(cs_m_awaddr),
.m_awlen(cs_m_awlen),
.m_awsize(cs_m_awsize),
.m_awburst(cs_m_awburst),
.m_awid(cs_m_awid),
.m_awvalid(cs_m_awvalid),
.m_awready(cs_m_awready),
.m_wdata(cs_m_wdata),
.m_wstrb(cs_m_wstrb),
.m_wlast(cs_m_wlast),
.m_wvalid(cs_m_wvalid),
.m_wready(cs_m_wready),
.m_bid(cs_m_bid),
.m_bresp(cs_m_bresp),
.m_bvalid(cs_m_bvalid),
.m_bready(cs_m_bready)
);
endmodule
