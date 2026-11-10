`timescale 1ns/1ps
module tb_candidate_offer;
wire f_normal_retired,f_recovery_owned,f_fault;wire[3:0]f_phase;wire f_all_drained,f_backend_idle;
wire fd_q_cfg_valid;
wire fd_q_cfg_ready;
wire fd_q_cfg_rsp_valid;
wire fd_q_cfg_rsp_ready;
wire [63:0]fd_q_cfg_base;
wire [63:0]fd_q_cfg_design;
wire [31:0]fd_q_cfg_connections;
wire [31:0]fd_q_cfg_nodes;
wire [31:0]fd_q_cfg_nets;
wire [31:0]fd_q_cfg_revision;
wire [2:0]fd_q_cfg_status;
wire fd_g_cfg_valid;
wire fd_g_cfg_ready;
wire fd_g_cfg_rsp_valid;
wire fd_g_cfg_rsp_ready;
wire [63:0]fd_g_cfg_offsets_base;
wire [63:0]fd_g_cfg_edges_base;
wire [63:0]fd_g_cfg_attrs_base;
wire [31:0]fd_g_cfg_nodes;
wire [31:0]fd_g_cfg_edges;
wire [2:0]fd_g_cfg_status;
wire fd_d_cfg_valid;
wire fd_d_cfg_ready;
wire fd_d_cfg_rsp_valid;
wire fd_d_cfg_rsp_ready;
wire [63:0]fd_d_cfg_base;
wire [31:0]fd_d_cfg_nodes;
wire [2:0]fd_d_cfg_status;
wire fd_t_cfg_valid;
wire fd_t_cfg_ready;
wire fd_t_cfg_rsp_valid;
wire fd_t_cfg_rsp_ready;
wire [63:0]fd_t_cfg_rows_base;
wire [63:0]fd_t_cfg_columns_base;
wire [31:0]fd_t_cfg_rows;
wire [31:0]fd_t_cfg_columns;
wire [2:0]fd_t_cfg_status;
wire fd_owner_cfg_valid;
wire fd_owner_cfg_ready;
wire fd_owner_cfg_rsp_valid;
wire fd_owner_cfg_rsp_ready;
wire [63:0]fd_owner_cfg_primary;
wire [63:0]fd_owner_cfg_pool;
wire [63:0]fd_owner_cfg_allocator;
wire [31:0]fd_owner_cfg_nodes;
wire [31:0]fd_owner_cfg_capacity;
wire [2:0]fd_owner_cfg_status;
wire fd_cs_cfg_valid;
wire fd_cs_cfg_ready;
wire fd_cs_cfg_rsp_valid;
wire fd_cs_cfg_rsp_ready;
wire [63:0]fd_cs_cfg_history;
wire [63:0]fd_cs_cfg_prices;
wire [63:0]fd_cs_cfg_nets;
wire [63:0]fd_cs_cfg_design_id;
wire [31:0]fd_cs_cfg_nodes;
wire [31:0]fd_cs_cfg_net_count;
wire [31:0]fd_cs_cfg_version;
wire [2:0]fd_cs_cfg_status;
wire fd_host_ctrl_valid;
wire fd_host_ctrl_ready;
wire fd_host_ctrl_rsp_valid;
wire fd_host_ctrl_rsp_ready;
wire [1:0]fd_host_ctrl_op;
wire [1:0]fd_host_ctrl_query;
wire [3:0]fd_host_ctrl_price;
wire [31:0]fd_host_ctrl_version;
wire [3:0]fd_host_ctrl_status;
wire fd_host_design_req_valid;
wire fd_host_design_req_ready;
wire fd_host_design_rsp_valid;
wire fd_host_design_rsp_ready;
wire [2:0]fd_host_design_req_op;
wire [31:0]fd_host_design_req_cookie;
wire [31:0]fd_host_design_req_owner;
wire [31:0]fd_host_design_req_node;
wire [31:0]fd_host_design_req_arg;
wire [3:0]fd_host_design_rsp_status;
wire [31:0]fd_host_design_rsp_cookie;
wire [31:0]fd_host_design_rsp_flags;
wire [31:0]fd_host_design_rsp_count;
wire [31:0]fd_host_design_rsp_mask;
wire fd_host_io_valid;
wire fd_host_io_ready;
wire fd_host_io_rsp_valid;
wire fd_host_io_rsp_ready;
wire [0:0]fd_host_io_write;
wire [31:0]fd_host_io_node;
wire [31:0]fd_host_io_value;
wire [2:0]fd_host_io_field;
wire [3:0]fd_host_io_status;
wire [0:0]fd_host_io_present;
wire [159:0]fd_host_io_payload;
wire fd_host_owner_req_valid;
wire fd_host_owner_req_ready;
wire fd_host_owner_rsp_valid;
wire fd_host_owner_rsp_ready;
wire [2:0]fd_host_owner_req_op;
wire [31:0]fd_host_owner_req_cookie;
wire [31:0]fd_host_owner_req_node;
wire [31:0]fd_host_owner_req_net;
wire [3:0]fd_host_owner_rsp_status;
wire [31:0]fd_host_owner_rsp_cookie;
wire [31:0]fd_host_owner_rsp_count;
wire [31:0]fd_host_owner_rsp_occupancy;
wire [0:0]fd_host_owner_rsp_will_overuse;
wire fd_cc_req_valid;
wire fd_cc_req_ready;
wire fd_cc_rsp_valid;
wire fd_cc_rsp_ready;
wire [127:0]fd_cc_req_words;
wire [31:0]fd_cc_req_cookie;
wire [31:0]fd_cc_req_version;
wire [63:0]fd_cc_req_design_id;
wire [1:0]fd_cc_req_query;
wire [3:0]fd_cc_req_price;
wire [63:0]fd_cc_rsp_words;
wire [31:0]fd_cc_rsp_cookie;
wire [31:0]fd_cc_rsp_version;
wire [63:0]fd_cc_rsp_design_id;
wire [1:0]fd_cc_rsp_query;
wire [1:0]fd_cc_rsp_status;
wire [3:0]fd_cc_rsp_price;
wire fd_expand_valid;
wire fd_expand_ready;
wire fd_result_valid;
wire fd_result_ready;
wire [31:0]fd_expand_connection;
wire [31:0]fd_expand_cookie;
wire [31:0]fd_expand_parent;
wire [31:0]fd_expand_prune;
wire [31:0]fd_expand_has_laguna;
wire [31:0]fd_expand_sink;
wire [31:0]fd_expand_net;
wire [31:0]fd_expand_sequence;
wire [31:0]fd_expand_flags;
wire [31:0]fd_expand_xmin;
wire [31:0]fd_expand_xmax;
wire [31:0]fd_expand_ymin;
wire [31:0]fd_expand_ymax;
wire [31:0]fd_expand_version;
wire [3:0]fd_result_status;
wire [31:0]fd_result_cookie;
wire [31:0]fd_result_count;
wire [31:0]fd_result_expanded_count;
wire [31:0]fd_result_raw_count;
wire [31:0]fd_result_mask;
wire [0:0]fd_result_hit;
wire [0:0]fd_result_early;
wire fd_seed_valid;
wire fd_seed_ready;
wire fd_seed_rsp_valid;
wire fd_seed_rsp_ready;
wire [31:0]fd_seed_op;
wire [31:0]fd_seed_key;
wire [31:0]fd_seed_id;
wire [31:0]fd_seed_cookie;
wire [31:0]fd_seed_version;
wire [31:0]fd_seed_rsp_status;
wire [31:0]fd_seed_rsp_cookie;
wire [31:0]fd_seed_rsp_size;
wire [31:0]fd_seed_rsp_key;
wire [31:0]fd_seed_rsp_id;
wire fd_cs_req_valid;
wire fd_cs_req_ready;
wire fd_cs_rsp_valid;
wire fd_cs_rsp_ready;
wire [0:0]fd_cs_req_host;
wire [2:0]fd_cs_req_op;
wire [31:0]fd_cs_req_cookie;
wire [31:0]fd_cs_req_index;
wire [31:0]fd_cs_req_value;
wire [31:0]fd_cs_req_version;
wire [1:0]fd_cs_req_query;
wire [3:0]fd_cs_req_price;
wire [3:0]fd_cs_rsp_status;
wire [31:0]fd_cs_rsp_cookie;
wire [31:0]fd_cs_rsp_index;
wire [31:0]fd_cs_rsp_version;
wire [2:0]fd_cs_rsp_op;
wire [0:0]fd_cs_rsp_host;
wire [1:0]fd_cs_rsp_query;
wire [3:0]fd_cs_rsp_price;
wire [127:0]fd_cs_rsp_data;
wire fd_k_cfg_valid;
wire fd_k_cfg_ready;
wire fd_k_cfg_rsp_valid;
wire fd_k_cfg_rsp_ready;
wire [0:0]fd_fa_authoritative;
wire [63:0]fd_fa_design;
wire [31:0]fd_fa_checkpoint;
wire [31:0]fd_fa_version;
wire [1:0]fd_fa_query;
wire [3:0]fd_fa_price;
wire [0:0]fd_k_cfg_status;
wire fd_cf_load_valid;
wire fd_cf_load_ready;
wire fd_cf_load_rsp_valid;
wire fd_cf_load_rsp_ready;
wire [2303:0]fd_fc_payload;
wire [63:0]fd_fc_design;
wire [31:0]fd_fc_checkpoint;
wire [0:0]fd_fc_authoritative;
wire [0:0]fd_cf_load_status;
wire[15:0]f_sv,f_sr,f_srv,f_srr,f_cbv,f_cbr,f_cbrv,f_cbrr,f_dv,f_dr,f_drv,f_drr,f_pending;
wire[38911:0]f_sp,f_cbp,f_dp;wire[4095:0]f_srp,f_cbrp,f_drp;
wire f_broute_valid,f_broute_ready,f_broute_rsp_valid,f_broute_rsp_ready;
wire[191:0]f_route_payload,f_broute_payload;
wire f_brecover_valid,f_brecover_ready,f_brecover_rsp_valid,f_brecover_rsp_ready;

wire cf_busy,cf_fault,cf_rsp_valid;wire[31:0]cf_rsp_cookie;
wire lr_busy,lr_fault,lr_rsp_valid;wire[31:0]lr_rsp_cookie;
integer fault_case=0,armed=0,injection_seen=0,owner_b_start=0,owner_r_start=0,label_r_start=0;reg injected_abort=0,injected_drift=0;wire recover_open;reg recovering=0;reg k_cold_rst=1,k_normal_retired=1;wire k_target_reset;reg[1:0]restore_epoch=1;reg[31:0]restore_version=3;wire raw_recovery_ready;integer repairs=0;wire label_drained,owner_drained,label_watch_fault,owner_watch_fault;
reg clk=0;always #5 clk=~clk;
wire  operation_pending;
reg bench_rst=0;wire rst=bench_rst||k_target_reset;
reg  abort=0;
reg  g_cfg_valid=0;
wire  g_cfg_ready;
reg [63:0] g_cfg_offsets_base=0;
reg [63:0] g_cfg_edges_base=0;
reg [63:0] g_cfg_attrs_base=0;
reg [31:0] g_cfg_nodes=0;
reg [31:0] g_cfg_edges=0;
wire  g_cfg_rsp_valid;
reg  g_cfg_rsp_ready=0;
wire [2:0] g_cfg_status;
wire  g_configured;
wire [63:0] g_m_araddr;
wire [7:0] g_m_arlen;
wire [2:0] g_m_arsize;
wire [1:0] g_m_arburst;
wire [3:0] g_m_arid;
wire  g_m_arvalid;
wire  g_m_arready;
wire [511:0] g_m_rdata;
wire [3:0] g_m_rid;
wire [1:0] g_m_rresp;
wire  g_m_rlast;
wire  g_m_rvalid;
wire  g_m_rready;
reg  d_cfg_valid=0;
wire  d_cfg_ready;
reg [63:0] d_cfg_base=0;
reg [31:0] d_cfg_nodes=0;
wire  d_cfg_rsp_valid;
reg  d_cfg_rsp_ready=0;
wire [2:0] d_cfg_status;
wire  d_configured;
wire [63:0] d_m_araddr;
wire [7:0] d_m_arlen;
wire [2:0] d_m_arsize;
wire [1:0] d_m_arburst;
wire [3:0] d_m_arid;
wire  d_m_arvalid;
wire  d_m_arready;
wire [511:0] d_m_rdata;
wire [3:0] d_m_rid;
wire [1:0] d_m_rresp;
wire  d_m_rlast;
wire  d_m_rvalid;
wire  d_m_rready;
wire [63:0] d_m_awaddr;
wire [7:0] d_m_awlen;
wire [2:0] d_m_awsize;
wire [1:0] d_m_awburst;
wire [3:0] d_m_awid;
wire  d_m_awvalid;
wire  d_m_awready;
wire [511:0] d_m_wdata;
wire [63:0] d_m_wstrb;
wire  d_m_wlast;
wire  d_m_wvalid;
wire  d_m_wready;
wire [3:0] d_m_bid;
wire [1:0] d_m_bresp;
wire  d_m_bvalid;
wire  d_m_bready;
reg  host_ctrl_valid=0;
wire  host_ctrl_ready;
reg [1:0] host_ctrl_op=0;
reg [1:0] host_ctrl_query=0;
reg [3:0] host_ctrl_price=0;
wire  host_ctrl_rsp_valid;
reg  host_ctrl_rsp_ready=0;
wire [3:0] host_ctrl_status;
wire  p_active;
wire [1:0] p_active_query;
wire [3:0] p_active_price;
wire [31:0] p_m_awaddr;
wire [7:0] p_m_awlen;
wire [2:0] p_m_awsize;
wire [1:0] p_m_awburst;
wire [3:0] p_m_awid;
wire  p_m_awvalid;
wire  p_m_awready;
wire [511:0] p_m_wdata;
wire [63:0] p_m_wstrb;
wire  p_m_wlast;
wire  p_m_wvalid;
wire  p_m_wready;
wire [3:0] p_m_bid;
wire [1:0] p_m_bresp;
wire  p_m_bvalid;
wire  p_m_bready;
wire [31:0] p_m_araddr;
wire [7:0] p_m_arlen;
wire [2:0] p_m_arsize;
wire [1:0] p_m_arburst;
wire [3:0] p_m_arid;
wire  p_m_arvalid;
wire  p_m_arready;
wire [511:0] p_m_rdata;
wire [3:0] p_m_rid;
wire [1:0] p_m_rresp;
wire  p_m_rlast;
wire  p_m_rvalid;
wire  p_m_rready;
reg  t_cfg_valid=0;
wire  t_cfg_ready;
reg [63:0] t_cfg_rows_base=0;
reg [63:0] t_cfg_columns_base=0;
reg [31:0] t_cfg_rows=0;
reg [31:0] t_cfg_columns=0;
wire  t_cfg_rsp_valid;
reg  t_cfg_rsp_ready=0;
wire [2:0] t_cfg_status;
wire  t_configured;
wire [63:0] t_m_araddr;
wire [7:0] t_m_arlen;
wire [2:0] t_m_arsize;
wire [1:0] t_m_arburst;
wire [3:0] t_m_arid;
wire  t_m_arvalid;
wire  t_m_arready;
wire [511:0] t_m_rdata;
wire [3:0] t_m_rid;
wire [1:0] t_m_rresp;
wire  t_m_rlast;
wire  t_m_rvalid;
wire  t_m_rready;
reg  host_owner_req_valid=0;
wire  host_owner_req_ready;
reg [2:0] host_owner_req_op=0;
reg [31:0] host_owner_req_cookie=0;
reg [31:0] host_owner_req_node=0;
reg [31:0] host_owner_req_net=0;
wire  host_owner_rsp_valid;
reg  host_owner_rsp_ready=0;
wire [3:0] host_owner_rsp_status;
wire [31:0] host_owner_rsp_cookie;
wire [31:0] host_owner_rsp_count;
wire [31:0] host_owner_rsp_occupancy;
wire  host_owner_rsp_will_overuse;
reg  owner_cfg_valid=0;
wire  owner_cfg_ready;
reg [63:0] owner_cfg_primary=0;
reg [63:0] owner_cfg_pool=0;
reg [63:0] owner_cfg_allocator=0;
reg [31:0] owner_cfg_nodes=0;
reg [31:0] owner_cfg_capacity=0;
wire  owner_cfg_rsp_valid;
reg  owner_cfg_rsp_ready=0;
wire [2:0] owner_cfg_status;
wire  owner_configured;
wire [63:0] owner_m_araddr;
wire [7:0] owner_m_arlen;
wire [2:0] owner_m_arsize;
wire [1:0] owner_m_arburst;
wire [3:0] owner_m_arid;
wire  owner_m_arvalid;
wire  owner_m_arready;
wire [511:0] owner_m_rdata;
wire [3:0] owner_m_rid;
wire [1:0] owner_m_rresp;
wire  owner_m_rlast;
wire  owner_m_rvalid;
wire  owner_m_rready;
wire [63:0] owner_m_awaddr;
wire [7:0] owner_m_awlen;
wire [2:0] owner_m_awsize;
wire [1:0] owner_m_awburst;
wire [3:0] owner_m_awid;
wire  owner_m_awvalid;
wire  owner_m_awready;
wire [511:0] owner_m_wdata;
wire [63:0] owner_m_wstrb;
wire  owner_m_wlast;
wire  owner_m_wvalid;
wire  owner_m_wready;
wire [3:0] owner_m_bid;
wire [1:0] owner_m_bresp;
wire  owner_m_bvalid;
wire  owner_m_bready;
reg  expand_valid=0;
wire  expand_ready;
reg [31:0] expand_cookie=0;
reg [31:0] expand_parent=0;
reg [31:0] expand_prune=0;
reg [31:0] expand_has_laguna=0;
reg [31:0] expand_sink=0;
reg [31:0] expand_net=0;
reg [31:0] expand_sequence=0;
reg [31:0] expand_flags=0;
reg [31:0] expand_xmin=0;
reg [31:0] expand_xmax=0;
reg [31:0] expand_ymin=0;
reg [31:0] expand_ymax=0;
wire  out_valid;
reg  out_ready=0;
wire [31:0] out_cookie;
wire [31:0] out_node;
wire [31:0] out_position;
wire [31:0] out_sequence;
wire [31:0] out_bits;
wire [31:0] out_action;
wire [31:0] out_steps;
wire [31:0] out_services;
wire [255:0] out_attrs;
wire [447:0] out_config;
wire  result_valid;
reg  result_ready=0;
wire [3:0] result_status;
wire [31:0] result_cookie;
wire [31:0] result_count;
wire [31:0] result_expanded_count;
wire [31:0] result_raw_count;
wire [31:0] result_mask;
wire  result_hit;
wire  result_early;
reg  host_design_req_valid=0;
wire  host_design_req_ready;
reg [2:0] host_design_req_op=0;
reg [31:0] host_design_req_cookie=0;
reg [31:0] host_design_req_owner=0;
reg [31:0] host_design_req_node=0;
reg [31:0] host_design_req_arg=0;
wire  host_design_rsp_valid;
reg  host_design_rsp_ready=0;
wire [3:0] host_design_rsp_status;
wire [31:0] host_design_rsp_cookie;
wire [31:0] host_design_rsp_flags;
wire [31:0] host_design_rsp_count;
wire [31:0] host_design_rsp_mask;
reg  host_io_valid=0;
wire  host_io_ready;
reg  host_io_write=0;
reg [31:0] host_io_node=0;
reg [31:0] host_io_value=0;
reg [2:0] host_io_field=0;
wire  host_io_rsp_valid;
reg  host_io_rsp_ready=0;
wire [3:0] host_io_status;
wire [159:0] host_io_payload;
wire  host_io_present;
wire  fault;
wire  busy;
reg [63:0] design_id=0;
reg [31:0] host_ctrl_version=0;
reg [31:0] expand_version=0;
wire [31:0] query_version;
wire  query_ready;
wire  cost_lease;
reg  cs_cfg_valid=0;
wire  cs_cfg_ready;
reg [63:0] cs_cfg_history=0;
reg [63:0] cs_cfg_prices=0;
reg [63:0] cs_cfg_nets=0;
reg [63:0] cs_cfg_design_id=0;
reg [31:0] cs_cfg_nodes=0;
reg [31:0] cs_cfg_net_count=0;
reg [31:0] cs_cfg_version=0;
wire  cs_cfg_rsp_valid;
reg  cs_cfg_rsp_ready=0;
wire [2:0] cs_cfg_status;
wire  cs_configured;
wire  cs_ready_for_query;
wire  cs_editing;
wire [31:0] cs_published_version;
wire [63:0] cs_design_id;
reg  cs_req_valid=0;
wire  cs_req_ready;
reg  cs_req_host=0;
reg [2:0] cs_req_op=0;
reg [31:0] cs_req_cookie=0;
reg [31:0] cs_req_index=0;
reg [31:0] cs_req_value=0;
reg [31:0] cs_req_version=0;
reg [1:0] cs_req_query=0;
reg [3:0] cs_req_price=0;
wire  cs_rsp_valid;
reg  cs_rsp_ready=0;
wire [3:0] cs_rsp_status;
wire [31:0] cs_rsp_cookie;
wire [31:0] cs_rsp_index;
wire [31:0] cs_rsp_version;
wire [2:0] cs_rsp_op;
wire  cs_rsp_host;
wire [1:0] cs_rsp_query;
wire [3:0] cs_rsp_price;
wire [127:0] cs_rsp_data;
wire  cs_busy;
wire  cs_fault;
wire [63:0] cs_m_araddr;
wire [7:0] cs_m_arlen;
wire [2:0] cs_m_arsize;
wire [1:0] cs_m_arburst;
wire [3:0] cs_m_arid;
wire  cs_m_arvalid;
wire  cs_m_arready;
wire [511:0] cs_m_rdata;
wire [3:0] cs_m_rid;
wire [1:0] cs_m_rresp;
wire  cs_m_rlast;
wire  cs_m_rvalid;
wire  cs_m_rready;
wire [63:0] cs_m_awaddr;
wire [7:0] cs_m_awlen;
wire [2:0] cs_m_awsize;
wire [1:0] cs_m_awburst;
wire [3:0] cs_m_awid;
wire  cs_m_awvalid;
wire  cs_m_awready;
wire [511:0] cs_m_wdata;
wire [63:0] cs_m_wstrb;
wire  cs_m_wlast;
wire  cs_m_wvalid;
wire  cs_m_wready;
wire [3:0] cs_m_bid;
wire [1:0] cs_m_bresp;
wire  cs_m_bvalid;
wire  cs_m_bready;
`ifdef PRESSURE
localparam SLOTS=1;
`else
localparam SLOTS=32;
`endif
`ifdef DEFAULT_DIRECTORY
localparam FRAMES=163840,INDEX_BITS=18,HASH_BITS=18;
`else
localparam FRAMES=16384,INDEX_BITS=14,HASH_BITS=15;
`endif
reg cc_req_valid=0,cc_rsp_ready=0;
wire cc_req_ready,cc_rsp_valid,cc_busy,cc_fault;
reg [127:0] cc_req_words=0;
reg [31:0] cc_req_cookie=0,cc_req_version=0;
reg [63:0] cc_req_design_id=0;
reg [1:0] cc_req_query=0;
reg [3:0] cc_req_price=0;
wire [63:0] cc_rsp_words,cc_rsp_design_id;
wire [31:0] cc_rsp_cookie,cc_rsp_version;
wire [1:0] cc_rsp_query,cc_rsp_status;
wire [3:0] cc_rsp_price;
integer center_calls=0,center_retired_checks=0,center_fd;
wire out_prep_valid;wire [31:0] out_prep_count,out_prep_occupancy,out_prep_price_index,out_prep_history,out_prep_price_value;
wire [127:0] out_prep_net_data;wire [3:0] out_prep_status;
integer prep_fd,prep_calls=0;
reg [291:0] held_prep;
wire out_post_valid;wire [3:0] out_post_status;wire [31:0] out_post_x,out_post_y,out_post_upstream,out_post_distance;wire [255:0] out_post_attrs;wire out_post_prev_read;
reg seed_valid=0,seed_rsp_ready=0;wire seed_ready,seed_rsp_valid;
reg [31:0] seed_op=1,seed_key=0,seed_id=0,seed_cookie=0,seed_version=0;wire [31:0] seed_rsp_status,seed_rsp_cookie,seed_rsp_size;
integer post_fd,post_out,order_fd,post_rc,post_calls=0,seed_calls=0,p_cookie,p_ordinal,p_parent,p_child,p_old,p_early;
reg [31:0] px,py,pu,pd;reg [388:0] held_post;string post_path;
reg guard_test=0;integer guard_mode=0,guard_commits=0;
wire out_offer_valid;wire [3:0] out_offer_status;wire [31:0] out_offer_key,out_offer_node,out_offer_before,out_offer_size,seed_rsp_key,seed_rsp_id;
integer queue_fd,queue_log,offer_log,offer_order,queue_rc,queue_i,queue_seen=0,queue_replies=0,queue_count=0,observer_calls=0,observer_polls=0,offer_calls=0,seed_initial;
reg queue_pending=0;reg [31:0] expected_queue[0:9];reg [31:0] observer_status,observer_size;reg [127:0] held_offer;reg [31:0] seed_cookie_held;string queue_path;
wire out_commit_valid;wire [3:0] out_commit_status;wire [2:0] out_commit_acked;wire [159:0] out_commit_payload;
integer commit_out,commit_order,commit_calls=0,final_fd,final_out,final_node,final_rc,final_i,final_count=0;
reg [159:0] held_commit,final_expected;reg [31:0] final_word;string final_path;
wire out_cost_valid;wire [3:0] out_cost_status;wire [159:0] out_cost_words;wire [735:0] out_cost_packet;wire [415:0] out_cost_geometry;wire [127:0] out_cost_geometry_result;
integer cost23_fd,cost23_out,cost23_order,cost23_rc,cost23_cookie,cost23_ordinal,cost23_i,cost23_calls=0;
reg [31:0] cost23_word;reg [735:0] expected_packet,held_packet;reg [159:0] expected_cost23,held_cost;reg [415:0] held_geom;reg [127:0] held_gresult;string cost23_path;
reg [31:0] expand_connection=0;
reg  q_cfg_valid=0;
wire  q_cfg_ready;
reg [63:0] q_cfg_base=0;
reg [63:0] q_cfg_design=0;
reg [31:0] q_cfg_connections=0;
reg [31:0] q_cfg_nodes=0;
reg [31:0] q_cfg_nets=0;
reg [31:0] q_cfg_revision=0;
wire  q_cfg_rsp_valid;
reg  q_cfg_rsp_ready=0;
wire [2:0] q_cfg_status;
wire  q_configured;
wire  out_params_valid;
wire [511:0] out_params;
wire [31:0] out_connection;
wire [31:0] out_profile_revision;
wire  q_busy;
wire  q_fault;
wire [63:0] q_m_araddr;
wire [7:0] q_m_arlen;
wire [2:0] q_m_arsize;
wire [1:0] q_m_arburst;
wire [3:0] q_m_arid;
wire  q_m_arvalid;
wire  q_m_arready;
wire [511:0] q_m_rdata;
wire [3:0] q_m_rid;
wire [1:0] q_m_rresp;
wire  q_m_rlast;
wire  q_m_rvalid;
wire  q_m_rready;
integer cycles=0;
integer q_reads,q_writes,q_rbeats,q_wbeats,q_bs,q_log;reg[511:0] held_params;
reg rc_req_valid=0,rc_req_op=0,rc_req_slot=0,rc_rsp_ready=0;reg[31:0]rc_req_cookie=0,rc_req_sink=0,rc_req_sequence=0;wire rc_req_ready,rc_rsp_valid,rc_block,rc_fault,rc_busy;wire[3:0]rc_rsp_status;wire[31:0]rc_rsp_cookie,rc_rsp_nodes,rc_rsp_acked;wire[1:0]rc_slots;
wire b_l_valid;
wire b_l_ready;
wire b_l_write;
wire [31:0] b_l_node;
wire [31:0] b_l_value;
wire [2:0] b_l_field;
wire b_l_rsp_valid;
wire b_l_rsp_ready;
wire [3:0] b_l_status;
wire b_l_present;
wire [159:0] b_l_payload;
wire b_o_valid;
wire b_o_ready;
wire [2:0] b_o_op;
wire [31:0] b_o_node;
wire [31:0] b_o_net;
wire [31:0] b_o_cookie;
wire b_o_rsp_valid;
wire b_o_rsp_ready;
wire [3:0] b_o_status;
wire [31:0] b_o_rsp_cookie;
wire [31:0] b_o_count;
wire [31:0] b_o_occupancy;
wire b_o_will_overuse;
wire raw_host_ctrl_ready;

wire raw_host_design_req_ready;

wire raw_expand_ready;

wire raw_seed_ready;

wire raw_q_cfg_ready;

wire raw_g_cfg_ready;

wire raw_d_cfg_ready;

wire raw_t_cfg_ready;

wire raw_owner_cfg_ready;

wire raw_cs_cfg_ready;

axi_drain_watch label_watch(.clk(clk),.rst(rst),.arvalid(p_m_arvalid),.arready(p_m_arready),.arlen(p_m_arlen),.rvalid(p_m_rvalid),.rready(p_m_rready),.rlast(p_m_rlast),.awvalid(p_m_awvalid),.awready(p_m_awready),.awlen(p_m_awlen),.wvalid(p_m_wvalid),.wready(p_m_wready),.wlast(p_m_wlast),.bvalid(p_m_bvalid),.bready(p_m_bready),.drained(label_drained),.fault(label_watch_fault));
axi_drain_watch owner_watch(.clk(clk),.rst(rst),.arvalid(owner_m_arvalid),.arready(owner_m_arready),.arlen(owner_m_arlen),.rvalid(owner_m_rvalid),.rready(owner_m_rready),.rlast(owner_m_rlast),.awvalid(owner_m_awvalid),.awready(owner_m_awready),.awlen(owner_m_awlen),.wvalid(owner_m_wvalid),.wready(owner_m_wready),.wlast(owner_m_wlast),.bvalid(owner_m_bvalid),.bready(owner_m_bready),.drained(owner_drained),.fault(owner_watch_fault));
reg k_cfg_valid=0,k_cfg_rsp_ready=0,k_rec_valid=0,k_rsp_ready=0;wire k_rcfg_done;wire k_labels_done;
wire k_cfg_ready,k_cfg_rsp_valid,k_cfg_status,k_rec_ready,k_rsp_valid,k_fault,k_busy,k_permit;
reg[31:0]k_checkpoint=17,k_cfg_version=3;reg[1:0]k_cfg_query=1;reg[3:0]k_cfg_price=3;
wire[3:0]k_rsp_status;wire[31:0]k_rsp_cookie,k_corrected,k_count,k_new_version,k_saved_checkpoint;wire[63:0]k_saved_design;wire[1:0]k_new_query;wire[3:0]k_new_price;
wire k_rcfg_valid,k_labels_valid,k_full,k_j_valid,k_j_ready;wire[31:0]k_j_node,k_j_net;wire[2:0]k_j_op;
wire k_a_valid,k_a_rsp_ready;reg k_a_ready=0,k_a_rsp_valid=0;wire[31:0]k_a_node,k_a_net,k_a_cookie,k_a_checkpoint;wire[63:0]k_a_design;
reg[31:0]k_a_rsp_cookie=0,k_a_rsp_checkpoint=0,k_a_refs=0,k_a_occ=0;reg[63:0]k_a_rsp_design=0;reg[3:0]k_a_status=0;
wire k_o_valid,k_o_ready,k_o_rsp_valid,k_o_rsp_ready;wire[2:0]k_o_op;wire[31:0]k_o_node,k_o_net,k_o_cookie;
wire mux_h_o_ready,mux_h_o_rsp_valid;
wire[31:0]journal_count=k_count;
assign recover_open=k_permit&&!f_recovery_owned&&!k_rec_valid;




recovery_coordinator #(.ENTRIES(32),.RESET_HOLD(5),.MAX_CYCLES(1048576)) recovery_ctl(.clk(clk),.cold_rst(k_cold_rst),.abort(f_fault||cf_fault||(cf_rsp_valid&&cf_rsp_cookie!=32'hf0010001)||lr_fault||(lr_rsp_valid&&lr_rsp_cookie!=32'he0010001)),.backend_drained(f_all_drained),.normal_retired(f_normal_retired),.cfg_valid(fd_k_cfg_valid),.cfg_ready(fd_k_cfg_ready),.cfg_authoritative(fd_fa_authoritative),.cfg_design(fd_fa_design),.cfg_checkpoint(fd_fa_checkpoint),.cfg_version(fd_fa_version),.cfg_query(fd_fa_query),.cfg_price(fd_fa_price),.cfg_rsp_valid(fd_k_cfg_rsp_valid),.cfg_rsp_ready(fd_k_cfg_rsp_ready),.cfg_status(fd_k_cfg_status),.j_valid(k_j_valid),.j_ready(k_j_ready),.j_node(k_j_node),.j_net(k_j_net),.j_op(k_j_op),.journal_count(k_count),.journal_full(k_full),.permit_work(k_permit),.recover_valid(f_brecover_valid),.recover_ready(f_brecover_ready),.recover_cookie(32'hc0010001),.recover_checkpoint(32'd17),.recover_version(32'd4),.recover_design(design_id),.recover_query(2'd2),.recover_price(4'd4),.target_reset(k_target_reset),.reconfigure_valid(k_rcfg_valid),.reconfigure_done(k_rcfg_done),.labels_valid(k_labels_valid),.labels_done(k_labels_done),.saved_design(k_saved_design),.saved_checkpoint(k_saved_checkpoint),.new_version(k_new_version),.new_query(k_new_query),.new_price(k_new_price),.rsp_valid(f_brecover_rsp_valid),.rsp_ready(f_brecover_rsp_ready),.rsp_status(k_rsp_status),.rsp_cookie(k_rsp_cookie),.rsp_corrected(k_corrected),.busy(k_busy),.fault(k_fault),.a_valid(k_a_valid),.a_ready(k_a_ready),.a_node(k_a_node),.a_net(k_a_net),.a_cookie(k_a_cookie),.a_checkpoint(k_a_checkpoint),.a_design(k_a_design),.a_rsp_valid(k_a_rsp_valid),.a_rsp_ready(k_a_rsp_ready),.a_status(k_a_status),.a_rsp_cookie(k_a_rsp_cookie),.a_rsp_checkpoint(k_a_rsp_checkpoint),.a_rsp_design(k_a_rsp_design),.a_refs(k_a_refs),.a_occupancy(k_a_occ),.o_valid(k_o_valid),.o_ready(k_o_ready),.o_op(k_o_op),.o_node(k_o_node),.o_net(k_o_net),.o_cookie(k_o_cookie),.o_rsp_valid(k_o_rsp_valid),.o_rsp_ready(k_o_rsp_ready),.o_status(f_cbrp[2304+:4]),.o_rsp_cookie(f_cbrp[2308+:32]),.o_count(f_cbrp[2340+:32]),.o_occupancy(f_cbrp[2372+:32]));
reg[31:0]authority_node[0:5],authority_net[0:5],authority_refs0[0:5],authority_occ0[0:5],authority_refs1[0:5],authority_occ1[0:5];
integer auth_fd,auth_rc,auth_i,auth_match,auth_delay=0;string auth_path;
initial begin
 if(!$value$plusargs("authority=%s",auth_path))$fatal(1,"authority path");auth_fd=$fopen(auth_path,"r");if(!auth_fd)$fatal(1,"authority file");
 for(auth_i=0;auth_i<6;auth_i=auth_i+1)begin
  auth_rc=$fscanf(auth_fd,"%d %d %d %d %d %d",authority_node[auth_i],authority_net[auth_i],authority_refs0[auth_i],authority_occ0[auth_i],authority_refs1[auth_i],authority_occ1[auth_i]);if(auth_rc!=6)$fatal(1,"authority row");
 end
end

reg lr_s_valid=0;wire lr_start_valid=k_labels_valid,lr_rsp_ready=!k_labels_valid;wire lr_start_ready,lr_s_ready;
reg[31:0]lr_s_node=0;reg[159:0]lr_s_payload=0;reg lr_s_last=0;wire[3:0]lr_rsp_status;wire[31:0]lr_written,lr_verified;
wire lr_c_valid,lr_c_ready,lr_c_rsp_ready;wire[1:0]lr_c_op,lr_c_query;wire[3:0]lr_c_price;wire[31:0]lr_c_version;
wire lr_l_valid,lr_l_ready,lr_l_write,lr_l_rsp_ready,lr_l_rsp_valid,mux_h_l_ready,mux_h_l_rsp_valid;
wire[31:0]lr_l_node,lr_l_value;wire[2:0]lr_l_field;



label_restore_controller #(.MAX_RECORDS(512),.MAX_CYCLES(1048576))label_restore(.clk(clk),.rst(k_cold_rst),.abort(1'b0),.backend_drained(f_all_drained),.start_valid(lr_start_valid),.start_ready(lr_start_ready),.start_design(k_saved_design),.expected_design(design_id),.start_checkpoint(k_saved_checkpoint),.expected_checkpoint(32'd17),.start_cookie(32'he0010001),.start_count(32'd328),.start_nodes(32'd9089009),.start_probe(32'd150697),.start_version(k_new_version),.start_query(k_new_query),.start_price(k_new_price),.s_valid(lr_s_valid),.s_ready(lr_s_ready),.s_node(lr_s_node),.s_cookie(32'he0010001),.s_payload(lr_s_payload),.s_last(lr_s_last),.rsp_valid(lr_rsp_valid),.rsp_ready(lr_rsp_ready),.rsp_status(lr_rsp_status),.rsp_cookie(lr_rsp_cookie),.written(lr_written),.verified(lr_verified),.busy(lr_busy),.fault(lr_fault),.c_valid(lr_c_valid),.c_ready(lr_c_ready),.c_op(lr_c_op),.c_query(lr_c_query),.c_price(lr_c_price),.c_version(lr_c_version),.c_rsp_valid(f_cbrv[6]),.c_rsp_ready(lr_c_rsp_ready),.c_status(f_cbrp[1536+:4]),.l_valid(lr_l_valid),.l_ready(lr_l_ready),.l_write(lr_l_write),.l_node(lr_l_node),.l_value(lr_l_value),.l_field(lr_l_field),.l_rsp_valid(lr_l_rsp_valid),.l_rsp_ready(lr_l_rsp_ready),.l_status(f_cbrp[2048+:4]),.l_present(f_cbrp[2052]),.l_payload(f_cbrp[2053+:160]));

assign k_labels_done=lr_rsp_valid;

reg cf_load_valid=0,cf_load_rsp_ready=0;wire cf_load_ready,cf_load_rsp_valid,cf_load_status;
wire[5:0]cf_valid,cf_ready,cf_replies,cf_reply_ready,cf_sent,cf_retired;wire[17:0]cf_status;
wire[2303:0]cf_input,cf_payload;wire[3:0]cf_rsp_status;wire[63:0]cf_saved_design;wire[31:0]cf_saved_checkpoint;
assign cf_input[0+:384]={128'd0,q_cfg_revision,q_cfg_nets,q_cfg_nodes,q_cfg_connections,q_cfg_design,q_cfg_base};
assign cf_input[384+:384]={128'd0,g_cfg_edges,g_cfg_nodes,g_cfg_attrs_base,g_cfg_edges_base,g_cfg_offsets_base};
assign cf_input[768+:384]={288'd0,d_cfg_nodes,d_cfg_base};
assign cf_input[1152+:384]={192'd0,t_cfg_columns,t_cfg_rows,t_cfg_columns_base,t_cfg_rows_base};
assign cf_input[1536+:384]={128'd0,owner_cfg_capacity,owner_cfg_nodes,owner_cfg_allocator,owner_cfg_pool,owner_cfg_primary};
assign cf_input[1920+:384]={32'd0,k_cfg_version,cs_cfg_net_count,cs_cfg_nodes,cs_cfg_design_id,cs_cfg_nets,cs_cfg_prices,cs_cfg_history};



config_restore_controller #(.MAX_CYCLES(1048576))config_restore(.clk(clk),.rst(k_cold_rst),.abort(1'b0),.backend_drained(f_all_drained),.normal_retired(f_normal_retired),.load_valid(fd_cf_load_valid),.load_ready(fd_cf_load_ready),.load_authoritative(fd_fc_authoritative),.load_payload(fd_fc_payload),.load_design(fd_fc_design),.load_checkpoint(fd_fc_checkpoint),.load_rsp_valid(fd_cf_load_rsp_valid),.load_rsp_ready(fd_cf_load_rsp_ready),.load_status(fd_cf_load_status),.start_valid(k_rcfg_valid),.start_ready(),.start_design(k_saved_design),.start_checkpoint(k_saved_checkpoint),.start_cookie(32'hf0010001),.start_version(k_new_version),.start_price(k_new_price),.cfg_valid(cf_valid),.cfg_ready(cf_ready),.cfg_payload(cf_payload),.cfg_rsp_valid(cf_replies),.cfg_rsp_ready(cf_reply_ready),.cfg_status(cf_status),.rsp_valid(cf_rsp_valid),.rsp_ready(!k_rcfg_valid),.rsp_status(cf_rsp_status),.rsp_cookie(cf_rsp_cookie),.busy(cf_busy),.fault(cf_fault),.sent(cf_sent),.retired(cf_retired),.saved_design(cf_saved_design),.saved_checkpoint(cf_saved_checkpoint));
assign k_rcfg_done=cf_rsp_valid;

route_commit_host_adapter #(.MAX_PATH(32)) route_join(.clk(clk),.rst(rst),.abort(injected_abort),.active(p_active),.backend_drained(f_all_drained),.j_valid(k_j_valid),.j_ready(k_j_ready),.j_node(k_j_node),.j_net(k_j_net),.j_op(k_j_op),.admit(!fault&&!busy),.active_query(p_active_query),.active_price(p_active_price),.active_version(query_version^(injected_drift?32'd1:32'd0)),.active_design(design_id),.req_valid(f_broute_valid),.req_ready(f_broute_ready),.req_op(f_broute_payload[0+:1]),.req_slot(f_broute_payload[1+:1]),.req_cookie(f_broute_payload[2+:32]),.req_source(f_broute_payload[34+:32]),.req_sink(f_broute_payload[66+:32]),.req_net(f_broute_payload[98+:32]),.req_sequence(f_broute_payload[130+:32]),.rsp_valid(f_broute_rsp_valid),.rsp_ready(f_broute_rsp_ready),.rsp_status(rc_rsp_status),.rsp_cookie(rc_rsp_cookie),.rsp_nodes(rc_rsp_nodes),.rsp_acked(rc_rsp_acked),.busy(rc_busy),.fault(rc_fault),.block_external(rc_block),.slot_valid(rc_slots),.h_l_valid(fd_host_io_valid),.b_l_valid(b_l_valid),.h_l_ready(fd_host_io_ready),.b_l_ready(b_l_ready),.h_l_write(fd_host_io_write),.b_l_write(b_l_write),.h_l_node(fd_host_io_node),.b_l_node(b_l_node),.h_l_value(fd_host_io_value),.b_l_value(b_l_value),.h_l_field(fd_host_io_field),.b_l_field(b_l_field),.h_l_rsp_valid(fd_host_io_rsp_valid),.b_l_rsp_valid(b_l_rsp_valid),.h_l_rsp_ready(fd_host_io_rsp_ready),.b_l_rsp_ready(b_l_rsp_ready),.h_l_status(fd_host_io_status),.b_l_status(b_l_status),.h_l_present(fd_host_io_present),.b_l_present(b_l_present),.h_l_payload(fd_host_io_payload),.b_l_payload(b_l_payload),.h_o_valid(fd_host_owner_req_valid),.b_o_valid(b_o_valid),.h_o_ready(fd_host_owner_req_ready),.b_o_ready(b_o_ready),.h_o_op(fd_host_owner_req_op),.b_o_op(b_o_op),.h_o_node(fd_host_owner_req_node),.b_o_node(b_o_node),.h_o_net(fd_host_owner_req_net),.b_o_net(b_o_net),.h_o_cookie(fd_host_owner_req_cookie),.b_o_cookie(b_o_cookie),.h_o_rsp_valid(fd_host_owner_rsp_valid),.b_o_rsp_valid(b_o_rsp_valid),.h_o_rsp_ready(fd_host_owner_rsp_ready),.b_o_rsp_ready(b_o_rsp_ready),.h_o_status(fd_host_owner_rsp_status),.b_o_status(b_o_status),.h_o_rsp_cookie(fd_host_owner_rsp_cookie),.b_o_rsp_cookie(b_o_rsp_cookie),.h_o_count(fd_host_owner_rsp_count),.b_o_count(b_o_count),.h_o_occupancy(fd_host_owner_rsp_occupancy),.b_o_occupancy(b_o_occupancy),.h_o_will_overuse(fd_host_owner_rsp_will_overuse),.b_o_will_overuse(b_o_will_overuse));

candidate_recursive_engine #(.SLOTS(SLOTS),.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS))dut(.q_cfg_valid(fd_q_cfg_valid),.q_cfg_ready(fd_q_cfg_ready),.q_cfg_rsp_valid(fd_q_cfg_rsp_valid),.q_cfg_rsp_ready(fd_q_cfg_rsp_ready),.q_cfg_base(fd_q_cfg_base),.q_cfg_design(fd_q_cfg_design),.q_cfg_connections(fd_q_cfg_connections),.q_cfg_nodes(fd_q_cfg_nodes),.q_cfg_nets(fd_q_cfg_nets),.q_cfg_revision(fd_q_cfg_revision),.q_cfg_status(fd_q_cfg_status),.g_cfg_valid(fd_g_cfg_valid),.g_cfg_ready(fd_g_cfg_ready),.g_cfg_rsp_valid(fd_g_cfg_rsp_valid),.g_cfg_rsp_ready(fd_g_cfg_rsp_ready),.g_cfg_offsets_base(fd_g_cfg_offsets_base),.g_cfg_edges_base(fd_g_cfg_edges_base),.g_cfg_attrs_base(fd_g_cfg_attrs_base),.g_cfg_nodes(fd_g_cfg_nodes),.g_cfg_edges(fd_g_cfg_edges),.g_cfg_status(fd_g_cfg_status),.d_cfg_valid(fd_d_cfg_valid),.d_cfg_ready(fd_d_cfg_ready),.d_cfg_rsp_valid(fd_d_cfg_rsp_valid),.d_cfg_rsp_ready(fd_d_cfg_rsp_ready),.d_cfg_base(fd_d_cfg_base),.d_cfg_nodes(fd_d_cfg_nodes),.d_cfg_status(fd_d_cfg_status),.t_cfg_valid(fd_t_cfg_valid),.t_cfg_ready(fd_t_cfg_ready),.t_cfg_rsp_valid(fd_t_cfg_rsp_valid),.t_cfg_rsp_ready(fd_t_cfg_rsp_ready),.t_cfg_rows_base(fd_t_cfg_rows_base),.t_cfg_columns_base(fd_t_cfg_columns_base),.t_cfg_rows(fd_t_cfg_rows),.t_cfg_columns(fd_t_cfg_columns),.t_cfg_status(fd_t_cfg_status),.owner_cfg_valid(fd_owner_cfg_valid),.owner_cfg_ready(fd_owner_cfg_ready),.owner_cfg_rsp_valid(fd_owner_cfg_rsp_valid),.owner_cfg_rsp_ready(fd_owner_cfg_rsp_ready),.owner_cfg_primary(fd_owner_cfg_primary),.owner_cfg_pool(fd_owner_cfg_pool),.owner_cfg_allocator(fd_owner_cfg_allocator),.owner_cfg_nodes(fd_owner_cfg_nodes),.owner_cfg_capacity(fd_owner_cfg_capacity),.owner_cfg_status(fd_owner_cfg_status),.cs_cfg_valid(fd_cs_cfg_valid),.cs_cfg_ready(fd_cs_cfg_ready),.cs_cfg_rsp_valid(fd_cs_cfg_rsp_valid),.cs_cfg_rsp_ready(fd_cs_cfg_rsp_ready),.cs_cfg_history(fd_cs_cfg_history),.cs_cfg_prices(fd_cs_cfg_prices),.cs_cfg_nets(fd_cs_cfg_nets),.cs_cfg_design_id(fd_cs_cfg_design_id),.cs_cfg_nodes(fd_cs_cfg_nodes),.cs_cfg_net_count(fd_cs_cfg_net_count),.cs_cfg_version(fd_cs_cfg_version),.cs_cfg_status(fd_cs_cfg_status),.host_ctrl_valid(fd_host_ctrl_valid),.host_ctrl_ready(fd_host_ctrl_ready),.host_ctrl_rsp_valid(fd_host_ctrl_rsp_valid),.host_ctrl_rsp_ready(fd_host_ctrl_rsp_ready),.host_ctrl_op(fd_host_ctrl_op),.host_ctrl_query(fd_host_ctrl_query),.host_ctrl_price(fd_host_ctrl_price),.host_ctrl_version(fd_host_ctrl_version),.host_ctrl_status(fd_host_ctrl_status),.host_design_req_valid(fd_host_design_req_valid),.host_design_req_ready(fd_host_design_req_ready),.host_design_rsp_valid(fd_host_design_rsp_valid),.host_design_rsp_ready(fd_host_design_rsp_ready),.host_design_req_op(fd_host_design_req_op),.host_design_req_cookie(fd_host_design_req_cookie),.host_design_req_owner(fd_host_design_req_owner),.host_design_req_node(fd_host_design_req_node),.host_design_req_arg(fd_host_design_req_arg),.host_design_rsp_status(fd_host_design_rsp_status),.host_design_rsp_cookie(fd_host_design_rsp_cookie),.host_design_rsp_flags(fd_host_design_rsp_flags),.host_design_rsp_count(fd_host_design_rsp_count),.host_design_rsp_mask(fd_host_design_rsp_mask),.cc_req_valid(fd_cc_req_valid),.cc_req_ready(fd_cc_req_ready),.cc_rsp_valid(fd_cc_rsp_valid),.cc_rsp_ready(fd_cc_rsp_ready),.cc_req_words(fd_cc_req_words),.cc_req_cookie(fd_cc_req_cookie),.cc_req_version(fd_cc_req_version),.cc_req_design_id(fd_cc_req_design_id),.cc_req_query(fd_cc_req_query),.cc_req_price(fd_cc_req_price),.cc_rsp_words(fd_cc_rsp_words),.cc_rsp_cookie(fd_cc_rsp_cookie),.cc_rsp_version(fd_cc_rsp_version),.cc_rsp_design_id(fd_cc_rsp_design_id),.cc_rsp_query(fd_cc_rsp_query),.cc_rsp_status(fd_cc_rsp_status),.cc_rsp_price(fd_cc_rsp_price),.expand_valid(fd_expand_valid),.expand_ready(fd_expand_ready),.result_valid(fd_result_valid),.result_ready(fd_result_ready),.expand_connection(fd_expand_connection),.expand_cookie(fd_expand_cookie),.expand_parent(fd_expand_parent),.expand_prune(fd_expand_prune),.expand_has_laguna(fd_expand_has_laguna),.expand_sink(fd_expand_sink),.expand_net(fd_expand_net),.expand_sequence(fd_expand_sequence),.expand_flags(fd_expand_flags),.expand_xmin(fd_expand_xmin),.expand_xmax(fd_expand_xmax),.expand_ymin(fd_expand_ymin),.expand_ymax(fd_expand_ymax),.expand_version(fd_expand_version),.result_status(fd_result_status),.result_cookie(fd_result_cookie),.result_count(fd_result_count),.result_expanded_count(fd_result_expanded_count),.result_raw_count(fd_result_raw_count),.result_mask(fd_result_mask),.result_hit(fd_result_hit),.result_early(fd_result_early),.seed_valid(fd_seed_valid),.seed_ready(fd_seed_ready),.seed_rsp_valid(fd_seed_rsp_valid),.seed_rsp_ready(fd_seed_rsp_ready),.seed_op(fd_seed_op),.seed_key(fd_seed_key),.seed_id(fd_seed_id),.seed_cookie(fd_seed_cookie),.seed_version(fd_seed_version),.seed_rsp_status(fd_seed_rsp_status),.seed_rsp_cookie(fd_seed_rsp_cookie),.seed_rsp_size(fd_seed_rsp_size),.seed_rsp_key(fd_seed_rsp_key),.seed_rsp_id(fd_seed_rsp_id),.cs_req_valid(fd_cs_req_valid),.cs_req_ready(fd_cs_req_ready),.cs_rsp_valid(fd_cs_rsp_valid),.cs_rsp_ready(fd_cs_rsp_ready),.cs_req_host(fd_cs_req_host),.cs_req_op(fd_cs_req_op),.cs_req_cookie(fd_cs_req_cookie),.cs_req_index(fd_cs_req_index),.cs_req_value(fd_cs_req_value),.cs_req_version(fd_cs_req_version),.cs_req_query(fd_cs_req_query),.cs_req_price(fd_cs_req_price),.cs_rsp_status(fd_cs_rsp_status),.cs_rsp_cookie(fd_cs_rsp_cookie),.cs_rsp_index(fd_cs_rsp_index),.cs_rsp_version(fd_cs_rsp_version),.cs_rsp_op(fd_cs_rsp_op),.cs_rsp_host(fd_cs_rsp_host),.cs_rsp_query(fd_cs_rsp_query),.cs_rsp_price(fd_cs_rsp_price),.cs_rsp_data(fd_cs_rsp_data),.host_io_valid(b_l_valid),.host_io_ready(b_l_ready),.host_io_write(b_l_write),.host_io_node(b_l_node),.host_io_value(b_l_value),.host_io_field(b_l_field),.host_io_rsp_valid(b_l_rsp_valid),.host_io_rsp_ready(b_l_rsp_ready),.host_io_status(b_l_status),.host_io_present(b_l_present),.host_io_payload(b_l_payload),.host_owner_req_valid(b_o_valid),.host_owner_req_ready(b_o_ready),.host_owner_req_op(b_o_op),.host_owner_req_node(b_o_node),.host_owner_req_net(b_o_net),.host_owner_req_cookie(b_o_cookie),.host_owner_rsp_valid(b_o_rsp_valid),.host_owner_rsp_ready(b_o_rsp_ready),.host_owner_rsp_status(b_o_status),.host_owner_rsp_cookie(b_o_rsp_cookie),.host_owner_rsp_count(b_o_count),.host_owner_rsp_occupancy(b_o_occupancy),.host_owner_rsp_will_overuse(b_o_will_overuse),.*);
integer g_reads,g_writes,g_rbeats,g_wbeats,g_bs;
axi_file_memory #(.ADDR_BITS(64),.READ_ONLY(1),.MAX_BEATS(1),.TAG("graph"))mem_g(
.clk(clk),
.rst(rst),
.base0(g_cfg_offsets_base),
.base1(g_cfg_edges_base),
.base2(g_cfg_attrs_base),
.size0(64'd36356040),
.size1(64'd161878144),
.size2(64'd290848288),
.inject_r(1'b0),
.inject_b(1'b0),
.araddr(g_m_araddr),
.arlen(g_m_arlen),
.arsize(g_m_arsize),
.arburst(g_m_arburst),
.arid(g_m_arid),
.arvalid(g_m_arvalid),
.arready(g_m_arready),
.rdata(g_m_rdata),
.rid(g_m_rid),
.rresp(g_m_rresp),
.rlast(g_m_rlast),
.rvalid(g_m_rvalid),
.rready(g_m_rready),
.awaddr('0),
.awlen('0),
.awsize('0),
.awburst('0),
.awid('0),
.awvalid('0),
.awready(),
.wdata('0),
.wstrb('0),
.wlast('0),
.wvalid('0),
.wready(),
.bid(),
.bresp(),
.bvalid(),
.bready('0),
.reads(g_reads),
.writes(g_writes),
.rbeats(g_rbeats),
.wbeats(g_wbeats),
.bresponses(g_bs)
);
integer d_reads,d_writes,d_rbeats,d_wbeats,d_bs;
axi_file_memory #(.ADDR_BITS(64),.READ_ONLY(0),.MAX_BEATS(1),.TAG("design"))mem_d(
.clk(clk),
.rst(rst),
.base0(d_cfg_base),
.base1(64'd0),
.base2(64'd0),
.size0(64'd145424192),
.size1(64'd0),
.size2(64'd0),
.inject_r(1'b0),
.inject_b(1'b0),
.araddr(d_m_araddr),
.arlen(d_m_arlen),
.arsize(d_m_arsize),
.arburst(d_m_arburst),
.arid(d_m_arid),
.arvalid(d_m_arvalid),
.arready(d_m_arready),
.rdata(d_m_rdata),
.rid(d_m_rid),
.rresp(d_m_rresp),
.rlast(d_m_rlast),
.rvalid(d_m_rvalid),
.rready(d_m_rready),
.awaddr(d_m_awaddr),
.awlen(d_m_awlen),
.awsize(d_m_awsize),
.awburst(d_m_awburst),
.awid(d_m_awid),
.awvalid(d_m_awvalid),
.awready(d_m_awready),
.wdata(d_m_wdata),
.wstrb(d_m_wstrb),
.wlast(d_m_wlast),
.wvalid(d_m_wvalid),
.wready(d_m_wready),
.bid(d_m_bid),
.bresp(d_m_bresp),
.bvalid(d_m_bvalid),
.bready(d_m_bready),
.reads(d_reads),
.writes(d_writes),
.rbeats(d_rbeats),
.wbeats(d_wbeats),
.bresponses(d_bs)
);
integer t_reads,t_writes,t_rbeats,t_wbeats,t_bs;
axi_file_memory #(.ADDR_BITS(64),.READ_ONLY(1),.MAX_BEATS(1),.TAG("tables"))mem_t(
.clk(clk),
.rst(rst),
.base0(t_cfg_rows_base),
.base1(t_cfg_columns_base),
.base2(64'd0),
.size0(64'd1280),
.size1(64'd0),
.size2(64'd0),
.inject_r(1'b0),
.inject_b(1'b0),
.araddr(t_m_araddr),
.arlen(t_m_arlen),
.arsize(t_m_arsize),
.arburst(t_m_arburst),
.arid(t_m_arid),
.arvalid(t_m_arvalid),
.arready(t_m_arready),
.rdata(t_m_rdata),
.rid(t_m_rid),
.rresp(t_m_rresp),
.rlast(t_m_rlast),
.rvalid(t_m_rvalid),
.rready(t_m_rready),
.awaddr('0),
.awlen('0),
.awsize('0),
.awburst('0),
.awid('0),
.awvalid('0),
.awready(),
.wdata('0),
.wstrb('0),
.wlast('0),
.wvalid('0),
.wready(),
.bid(),
.bresp(),
.bvalid(),
.bready('0),
.reads(t_reads),
.writes(t_writes),
.rbeats(t_rbeats),
.wbeats(t_wbeats),
.bresponses(t_bs)
);
integer p_reads,p_writes,p_rbeats,p_wbeats,p_bs;
axi_file_memory #(.ADDR_BITS(32),.READ_ONLY(0),.MAX_BEATS(3),.TAG("labels"))mem_p(
.clk(clk),
.rst(rst),
.base0(64'd0),
.base1(64'd0),
.base2(64'd0),
.size0((FRAMES==163840?64'd31457280:64'd3145728)),
.size1(64'd0),
.size2(64'd0),
.inject_r(armed&&fault_case==2),
.inject_b(1'b0),
.araddr(p_m_araddr),
.arlen(p_m_arlen),
.arsize(p_m_arsize),
.arburst(p_m_arburst),
.arid(p_m_arid),
.arvalid(p_m_arvalid),
.arready(p_m_arready),
.rdata(p_m_rdata),
.rid(p_m_rid),
.rresp(p_m_rresp),
.rlast(p_m_rlast),
.rvalid(p_m_rvalid),
.rready(p_m_rready),
.awaddr(p_m_awaddr),
.awlen(p_m_awlen),
.awsize(p_m_awsize),
.awburst(p_m_awburst),
.awid(p_m_awid),
.awvalid(p_m_awvalid),
.awready(p_m_awready),
.wdata(p_m_wdata),
.wstrb(p_m_wstrb),
.wlast(p_m_wlast),
.wvalid(p_m_wvalid),
.wready(p_m_wready),
.bid(p_m_bid),
.bresp(p_m_bresp),
.bvalid(p_m_bvalid),
.bready(p_m_bready),
.reads(p_reads),
.writes(p_writes),
.rbeats(p_rbeats),
.wbeats(p_wbeats),
.bresponses(p_bs)
);
integer owner_reads,owner_writes,owner_rbeats,owner_wbeats,owner_bs;
axi_file_memory #(.ADDR_BITS(64),.READ_ONLY(0),.MAX_BEATS(1),.TAG("owners"))mem_owner(
.clk(clk),
.rst(rst),
.base0(owner_cfg_primary),
.base1(64'd0),
.base2(64'd0),
.size0(64'd145424256),
.size1(64'd0),
.size2(64'd0),
.inject_r(armed&&fault_case==5),
.inject_b(armed&&fault_case==1),
.araddr(owner_m_araddr),
.arlen(owner_m_arlen),
.arsize(owner_m_arsize),
.arburst(owner_m_arburst),
.arid(owner_m_arid),
.arvalid(owner_m_arvalid),
.arready(owner_m_arready),
.rdata(owner_m_rdata),
.rid(owner_m_rid),
.rresp(owner_m_rresp),
.rlast(owner_m_rlast),
.rvalid(owner_m_rvalid),
.rready(owner_m_rready),
.awaddr(owner_m_awaddr),
.awlen(owner_m_awlen),
.awsize(owner_m_awsize),
.awburst(owner_m_awburst),
.awid(owner_m_awid),
.awvalid(owner_m_awvalid),
.awready(owner_m_awready),
.wdata(owner_m_wdata),
.wstrb(owner_m_wstrb),
.wlast(owner_m_wlast),
.wvalid(owner_m_wvalid),
.wready(owner_m_wready),
.bid(owner_m_bid),
.bresp(owner_m_bresp),
.bvalid(owner_m_bvalid),
.bready(owner_m_bready),
.reads(owner_reads),
.writes(owner_writes),
.rbeats(owner_rbeats),
.wbeats(owner_wbeats),
.bresponses(owner_bs)
);
integer cs_reads,cs_writes,cs_rbeats,cs_wbeats,cs_bs;
axi_file_memory #(.ADDR_BITS(64),.READ_ONLY(0),.MAX_BEATS(1),.TAG("cost"))mem_cs(
.clk(clk),
.rst(rst),
.base0(cs_cfg_history),
.base1(64'd0),
.base2(64'd0),
.size0(64'd36804480),
.size1(64'd0),
.size2(64'd0),
.inject_r(1'b0),
.inject_b(1'b0),
.araddr(cs_m_araddr),
.arlen(cs_m_arlen),
.arsize(cs_m_arsize),
.arburst(cs_m_arburst),
.arid(cs_m_arid),
.arvalid(cs_m_arvalid),
.arready(cs_m_arready),
.rdata(cs_m_rdata),
.rid(cs_m_rid),
.rresp(cs_m_rresp),
.rlast(cs_m_rlast),
.rvalid(cs_m_rvalid),
.rready(cs_m_rready),
.awaddr(cs_m_awaddr),
.awlen(cs_m_awlen),
.awsize(cs_m_awsize),
.awburst(cs_m_awburst),
.awid(cs_m_awid),
.awvalid(cs_m_awvalid),
.awready(cs_m_awready),
.wdata(cs_m_wdata),
.wstrb(cs_m_wstrb),
.wlast(cs_m_wlast),
.wvalid(cs_m_wvalid),
.wready(cs_m_wready),
.bid(cs_m_bid),
.bresp(cs_m_bresp),
.bvalid(cs_m_bvalid),
.bready(cs_m_bready),
.reads(cs_reads),
.writes(cs_writes),
.rbeats(cs_rbeats),
.wbeats(cs_wbeats),
.bresponses(cs_bs)
);
axi_file_memory #(.ADDR_BITS(64),.READ_ONLY(1),.MAX_BEATS(1),.TAG("qstate"))mem_q(
.clk(clk),
.rst(rst),
.base0(q_cfg_base),
.base1(64'd0),
.base2(64'd0),
.size0(64'd11540864),
.size1(64'd0),
.size2(64'd0),
.inject_r(1'b0),
.inject_b(1'b0),
.araddr(q_m_araddr),
.arlen(q_m_arlen),
.arsize(q_m_arsize),
.arburst(q_m_arburst),
.arid(q_m_arid),
.arvalid(q_m_arvalid),
.arready(q_m_arready),
.rdata(q_m_rdata),
.rid(q_m_rid),
.rresp(q_m_rresp),
.rlast(q_m_rlast),
.rvalid(q_m_rvalid),
.rready(q_m_rready),
.awaddr(64'd0),
.awlen(8'd0),
.awsize(3'd6),
.awburst(2'd1),
.awid(4'd0),
.awvalid(1'b0),
.awready(),
.wdata(512'd0),
.wstrb(64'd0),
.wlast(1'b0),
.wvalid(1'b0),
.wready(),
.bid(),
.bresp(),
.bvalid(),
.bready(1'b1),
.reads(q_reads),
.writes(q_writes),
.rbeats(q_rbeats),
.wbeats(q_wbeats),
.bresponses(q_bs)
);

integer trace,fd_gold,rc,i,j,node_id;string path;
integer commits=0,offers=0,outputs=0,host_blocks=0,physical_expands=0,metadata_calls=0,visited_reads=0;
reg[735:0]gold_packet;reg[159:0]gold_cost,gold_label;reg[31:0]word;integer logical_parent,logical_child;
reg[31:0]expected_parent[0:2],expected_node[0:2],expected_frame[0:2],expected_action[0:2],expected_ordinal[0:2];
reg[447:0]gold_config;reg[1855:0]held_output;
integer final_file,final_index;reg[31:0]final_node_id;reg[159:0]gold_final;
reg label_pending=0;reg[31:0]pending_label_node,pending_label_field;reg pending_label_write;
always @(posedge clk)begin
 cycles<=cycles+1;if(cycles==106000)begin $display("FENCE_DEBUG phase=%0d drained=%b idle=%b busy=%b op=%b cc=%b cs=%b q=%b route_started=%b route_send=%b route_failed=%b rec=%b rawrv=%b rawrr=%b fault=%b",f_phase,f_all_drained,f_backend_idle,busy,operation_pending,cc_busy,cs_busy,q_busy,fence.route_started,fence.route_send,fence.route_failed,k_rec_valid,f_brecover_valid,f_brecover_ready,fault);$fatal(1,"debug stop");endif(cycles>3000000)$fatal(1,"watchdog");
 if(!rst)begin
  if(fault&&!armed&&(!recovering||recover_open))$fatal(1,"join fault controller=%0d expansion=%0d metadata=%0d access=%0d cf=%b pf=%b df=%b of=%b",dut.core.controller.state,dut.core.expansion.state,dut.core.metadata.state,dut.core.access.controller.state,dut.core.capture_fault,dut.core.p_fault,dut.core.d_fault,dut.core.o_fault);
  if(operation_pending)begin
   if(host_ctrl_ready||host_io_ready||host_design_req_ready||host_owner_req_ready||expand_ready)$fatal(1,"query lease gap");
   if(host_ctrl_valid&&host_io_valid&&host_design_req_valid&&host_owner_req_valid)host_blocks<=host_blocks+1;
  end
  if(dut.core.ce_expand_valid&&dut.core.ce_expand_ready)begin physical_expands<=physical_expands+1;$fdisplay(trace,"E %0d %0d %0d",cycles,dut.core.ce_expand_cookie,dut.core.ce_expand_parent);end
  if(dut.core.ce_result_valid&&dut.core.ce_result_ready)$fdisplay(trace,"S %0d %0d %0d",cycles,dut.core.ce_result_cookie,dut.core.ce_result_count);
  if(dut.core.m_req_valid&&dut.core.m_req_ready)begin
   metadata_calls<=metadata_calls+1;if(dut.core.expansion.state!=0||dut.core.child_capture.state!=0)$fatal(1,"metadata before seal");
   $fdisplay(trace,"M %0d %0d %0d %0d",cycles,dut.core.controller.frame_cookie,dut.core.m_req_parent,dut.core.m_req_child);
  end
  if(dut.core.s_l_valid&&dut.core.s_l_ready)begin
   label_pending<=1;pending_label_node<=dut.core.s_l_node;pending_label_field<=dut.core.s_l_field;pending_label_write<=dut.core.s_l_write;
   $fdisplay(trace,"LQ %0d %0d %0d %0d",cycles,dut.core.s_l_node,dut.core.s_l_field,dut.core.s_l_write);
  end
  if(dut.core.s_l_rsp_valid&&dut.core.s_l_rsp_ready)begin
   if(!label_pending)$fatal(1,"unowned label reply");label_pending<=0;
   if(!pending_label_write&&pending_label_field==3)begin visited_reads<=visited_reads+1;$fdisplay(trace,"V %0d %0d %0d %040h",cycles,pending_label_node,dut.core.s_l_status,dut.core.s_l_payload);end
  end
  if(dut.cl_valid&&dut.cl_ready)$fdisplay(trace,"W %0d %0d %0d %08h",cycles,dut.cl_node,dut.cl_field,dut.cl_value);
  if(dut.cl_rsp_valid&&dut.cl_rsp_ready)$fdisplay(trace,"A %0d %0d %0d %040h",cycles,dut.cl_status,dut.cl_present,dut.cl_payload);
  if(dut.of_valid&&dut.of_ready)begin offers<=offers+1;$fdisplay(trace,"F %0d %0d %08h %0d",cycles,dut.of_id,dut.of_key,dut.frontier_size);end
  if(dut.frontier.fs_req_valid&&dut.frontier.fs_req_ready)$fdisplay(trace,"FQ %0d %0d %08h %0d %0d",cycles,dut.frontier.fs_req_op,dut.frontier.fs_req_key,dut.frontier.fs_req_id,dut.frontier.fs_req_cookie);
  if(dut.frontier.fs_rsp_valid&&dut.frontier.fs_rsp_ready)$fdisplay(trace,"FR %0d %0d %08h %0d %0d",cycles,dut.frontier.fs_rsp_status,dut.frontier.fs_rsp_key,dut.frontier.fs_rsp_id,dut.frontier.fs_rsp_size);
 end
end
task control(input integer op);begin
 @(negedge clk);host_ctrl_op=op;host_ctrl_query=restore_epoch;host_ctrl_price=restore_version[3:0];host_ctrl_version=restore_version;host_ctrl_valid=1;
 do @(posedge clk);while(!host_ctrl_ready);@(negedge clk);host_ctrl_valid=0;
 wait(host_ctrl_rsp_valid);@(negedge clk);if(host_ctrl_status)$fatal(1,"control status op=%0d status=%0d",op,host_ctrl_status);
 host_ctrl_rsp_ready=1;@(negedge clk);host_ctrl_rsp_ready=0;
end endtask

integer imports_fd,candidates_fd,polls_fd,finals_fd,prepared_fd;
integer query_index,next_node,path_steps;
reg[31:0]saved1[0:31],saved2[0:31];integer count1=0,count2=0,stage_no,pi,pj,expected_refs,probe_node;reg[31:0]route_node;reg[31:0]selected_sink=150697,selected_connection=16506,selected_sequence=1;
integer import_i,field_i,candidate_i=0,poll_i=0,expand_i=0,stopped=0;
integer cp_parent,cp_child,cp_pos,cp_action,cp_target,cp_pnode,cp_psize,cp_pkey;
integer poll_node,poll_key,poll_size,host_reads=0;
reg[159:0]host_record;reg[159:0]import_record;reg[31:0]import_node;
string natural_path;
task label_write(input[31:0]n,input integer field,input[31:0]value);begin
 @(negedge clk);host_io_valid=1;host_io_node=n;host_io_field=field;host_io_write=1;host_io_value=value;
 do @(posedge clk);while(!host_io_ready);@(negedge clk);host_io_valid=0;
 wait(host_io_rsp_valid);@(negedge clk);if(host_io_status)$fatal(1,"label import n=%0d f=%0d",n,field);host_io_rsp_ready=1;@(negedge clk);host_io_rsp_ready=0;
end endtask
task label_read(input[31:0]n);begin
 @(negedge clk);host_io_valid=1;host_io_node=n;host_io_field=0;host_io_write=0;
 do @(posedge clk);while(!host_io_ready);@(negedge clk);host_io_valid=0;
 wait(host_io_rsp_valid);@(negedge clk);if(host_io_status||!host_io_present)$fatal(1,"label read n=%0d",n);host_record=host_io_payload;
 host_io_rsp_ready=1;@(negedge clk);host_io_rsp_ready=0;host_reads=host_reads+1;
end endtask
task frontier_command(input[31:0]op,key,id);begin
 @(negedge clk);seed_valid=1;seed_op=op;seed_key=key;seed_id=id;seed_cookie=32'hc0000000+poll_i;seed_version=query_version;
 do @(posedge clk);while(!seed_ready);@(negedge clk);seed_valid=0;
 wait(seed_rsp_valid);@(negedge clk);if(seed_rsp_status)$fatal(1,"heap op=%0d status=%0d",op,seed_rsp_status);
 poll_node=seed_rsp_id;poll_key=seed_rsp_key;poll_size=seed_rsp_size;
 seed_rsp_ready=1;@(negedge clk);seed_rsp_ready=0;
end endtask

task owner_op(input integer op,input[31:0]node,input integer want_refs,input integer want_occ);begin
 @(negedge clk);host_owner_req_op=op;host_owner_req_cookie=32'he0000000+node;host_owner_req_node=node;host_owner_req_net=2717;host_owner_req_valid=1;
 do @(posedge clk);while(!host_owner_req_ready);@(negedge clk);host_owner_req_valid=0;
 wait(host_owner_rsp_valid);@(negedge clk);
 if(host_owner_rsp_status||host_owner_rsp_cookie!=32'he0000000+node||host_owner_rsp_count!=want_refs||host_owner_rsp_occupancy!=want_occ)$fatal(1,"owner stage=%0d op=%0d node=%0d refs=%0d occ=%0d expected=%0d %0d",stage_no,op,node,host_owner_rsp_count,host_owner_rsp_occupancy,want_refs,want_occ);
 $fdisplay(trace,"SO %0d %0d %0d %0d %0d %0d",cycles,stage_no,op,node,host_owner_rsp_count,host_owner_rsp_occupancy);
 host_owner_rsp_ready=1;@(negedge clk);host_owner_rsp_ready=0;
end endtask
function integer in_first(input[31:0]node);integer k;begin in_first=0;for(k=0;k<count1;k=k+1)if(saved1[k]==node)in_first=1;end endfunction
function integer in_second(input[31:0]node);integer k;begin in_second=0;for(k=0;k<count2;k=k+1)if(saved2[k]==node)in_second=1;end endfunction
task probe_owners;integer k,node,refs;begin
 for(k=0;k<count1+count2;k=k+1)begin
  node=k<count1?saved1[k]:saved2[k-count1];
  refs=stage_no==0?in_first(node):stage_no==1?in_first(node)+in_second(node):stage_no==2?in_second(node):0;
  owner_op(0,node,refs,refs!=0);
 end
 $fdisplay(trace,"ST %0d %0d",cycles,stage_no);
end endtask

reg[31:0]rc_read_node;integer route_commands=0;
always @(posedge clk)if(!rst)begin
 if(recovering&&!recover_open&&(rc_req_ready||expand_ready||seed_ready))$fatal(1,"work admitted during authority restore");
 if(rc_block)begin
 if(host_ctrl_valid&&host_ctrl_ready)$fatal(1,"route fence host_ctrl_valid");
 if(host_design_req_valid&&host_design_req_ready)$fatal(1,"route fence host_design_req_valid");
 if(expand_valid&&expand_ready)$fatal(1,"route fence expand_valid");
 if(seed_valid&&seed_ready)$fatal(1,"route fence seed_valid");
 if(q_cfg_valid&&q_cfg_ready)$fatal(1,"route fence q_cfg_valid");
 if(g_cfg_valid&&g_cfg_ready)$fatal(1,"route fence g_cfg_valid");
 if(d_cfg_valid&&d_cfg_ready)$fatal(1,"route fence d_cfg_valid");
 if(t_cfg_valid&&t_cfg_ready)$fatal(1,"route fence t_cfg_valid");
 if(owner_cfg_valid&&owner_cfg_ready)$fatal(1,"route fence owner_cfg_valid");
 if(cs_cfg_valid&&cs_cfg_ready)$fatal(1,"route fence cs_cfg_valid");

 end
 if(route_join.l_valid&&route_join.l_ready)begin rc_read_node<=route_join.l_node;$fdisplay(trace,"RL %0d %0d %0d",cycles,rc_req_slot,route_join.l_node);end
 if(route_join.l_rsp_valid&&route_join.l_rsp_ready)$fdisplay(trace,"RA %0d %0d %0d %040h",cycles,rc_req_slot,rc_read_node,b_l_payload);
 if(route_join.o_valid&&route_join.o_ready)begin
  $fdisplay(trace,"RO %0d %0d %0d %0d",cycles,rc_req_slot,route_join.o_op,route_join.o_node);
  if(route_join.o_op==1)begin
   if(rc_req_slot==0)begin saved1[count1]<=route_join.o_node;count1<=count1+1;end
   else begin saved2[count2]<=route_join.o_node;count2<=count2+1;end
  end
 end
 if(route_join.o_rsp_valid&&route_join.o_rsp_ready)$fdisplay(trace,"RB %0d %0d %0d %0d %0d",cycles,rc_req_slot,b_o_status,b_o_count,b_o_occupancy);
end

always @(posedge clk)if(!rst&&armed)begin
 if((fault_case==3||fault_case==4)&&!injection_seen&&((owner_m_awvalid&&owner_m_awready)||(owner_m_wvalid&&owner_m_wready)))begin
  injection_seen<=1;if(fault_case==3)injected_abort<=1;else injected_drift<=1;
  $fdisplay(trace,"FI %0d %0d",cycles,fault_case);
 end
 if((fault_case==1&&owner_m_bvalid&&owner_m_bready)||(fault_case==5&&owner_m_rvalid&&owner_m_rready)||(fault_case==2&&p_m_rvalid&&p_m_rready))begin
  injection_seen<=1;$fdisplay(trace,"FI %0d %0d",cycles,fault_case);
 end
end

task install_config_snapshot;begin
 @(negedge clk);cf_load_valid=1;do @(posedge clk);while(!cf_load_ready);@(negedge clk);cf_load_valid=0;
 wait(cf_load_rsp_valid);@(negedge clk);if(cf_load_status)$fatal(1,"resident config install");
 $fdisplay(trace,"CL %0d %0d %0d",cycles,cf_saved_checkpoint,cf_load_status);
 cf_load_rsp_ready=1;@(negedge clk);cf_load_rsp_ready=0;
end endtask
task install_checkpoint;begin
 @(negedge clk);k_cfg_valid=1;do @(posedge clk);while(!k_cfg_ready);@(negedge clk);k_cfg_valid=0;
 wait(k_cfg_rsp_valid);@(negedge clk);if(k_cfg_status)$fatal(1,"checkpoint install");k_cfg_rsp_ready=1;@(negedge clk);k_cfg_rsp_ready=0;
 $fdisplay(trace,"KC %0d %0d",cycles,k_saved_checkpoint);
end endtask
reg last_k_reset=0,prior_drained=0;integer last_j_cycle=0;reg[31:0]last_j_node=0;
always @(posedge clk)begin
 if(k_cold_rst)begin k_normal_retired<=1;last_k_reset<=0;prior_drained<=0;k_a_ready<=0;k_a_rsp_valid<=0;auth_delay<=0;end
 else begin
  prior_drained<=f_all_drained;last_k_reset<=k_target_reset;
  if(rc_req_valid&&rc_req_ready)k_normal_retired<=0;
  if(rc_rsp_valid&&rc_rsp_ready)k_normal_retired<=1;
  if(k_target_reset&&!last_k_reset)begin
   if(!prior_drained||!f_normal_retired)$fatal(1,"RTL reset before drain/retire");$fdisplay(trace,"RESET %0d %0d",cycles,k_count);
  end
  if(k_j_valid&&k_j_ready)begin last_j_cycle<=cycles;last_j_node<=k_j_node;$fdisplay(trace,"J %0d %0d %0d %0d",cycles,k_j_node,k_j_net,k_j_op);end
  if(route_join.held&&b_o_valid&&b_o_ready)begin
   if(cycles<=last_j_cycle||b_o_node!=last_j_node)$fatal(1,"owner forwarded before journal");$fdisplay(trace,"BF %0d %0d %0d",cycles,b_o_op,b_o_node);
  end
  if(k_o_valid&&k_o_ready)$fdisplay(trace,"KO %0d %0d %0d %0d",cycles,k_o_op,k_o_node,k_o_cookie);
  if(k_o_rsp_valid&&k_o_rsp_ready)$fdisplay(trace,"KR %0d %0d %0d %0d",cycles,f_cbrp[2304+:4],f_cbrp[2340+:32],f_cbrp[2372+:32]);
  if(!recover_open&&k_busy&&(rc_req_ready||expand_ready||seed_ready))$fatal(1,"coordinator gate leak");
  k_a_ready<=cycles%4==0;
  if(k_a_valid&&k_a_ready)begin
   if(auth_delay||k_a_rsp_valid)$fatal(1,"authority overlap");auth_match=-1;
   for(integer ax=0;ax<6;ax=ax+1)if(authority_node[ax]==k_a_node&&authority_net[ax]==k_a_net)auth_match=ax;
   if(auth_match<0||k_a_design!=design_id||(k_a_checkpoint!=17&&k_a_checkpoint!=18))$fatal(1,"authority key binding");
   k_a_rsp_cookie<=k_a_cookie;k_a_rsp_checkpoint<=k_a_checkpoint;k_a_rsp_design<=k_a_design;k_a_status<=0;
   k_a_refs<=k_a_checkpoint==17?authority_refs0[auth_match]:authority_refs1[auth_match];k_a_occ<=k_a_checkpoint==17?authority_occ0[auth_match]:authority_occ1[auth_match];auth_delay<=3;
   $fdisplay(trace,"KA %0d %0d %0d %0d %0d",cycles,k_a_checkpoint,k_a_node,k_a_net,k_a_cookie);
  end
  if(auth_delay>0)begin auth_delay<=auth_delay-1;if(auth_delay==1)k_a_rsp_valid<=1;end
  if(k_a_rsp_valid&&k_a_rsp_ready)k_a_rsp_valid<=0;
 end
end

always @(posedge clk)if(!k_cold_rst)begin
 if(lr_c_valid&&lr_c_ready)$fdisplay(trace,"LC %0d %0d",cycles,lr_c_op);
 if(lr_l_valid&&lr_l_ready)$fdisplay(trace,"LL %0d %0d %0d %0d %08h",cycles,lr_l_write,lr_l_node,lr_l_field,lr_l_value);
 if(lr_l_rsp_valid&&lr_l_rsp_ready)begin
  $fdisplay(trace,"LX %0d %0d %0d %040h",cycles,f_cbrp[2048+:4],f_cbrp[2052],f_cbrp[2053+:160]);
  if(label_restore.state==4)$fdisplay(trace,"ABS %0d %040h",cycles,f_cbrp[2053+:160]);
  if(label_restore.state==10)$fdisplay(trace,"CHECK %0d %0d %040h",cycles,label_restore.row[191:160],f_cbrp[2053+:160]);
 end
 if(lr_s_valid&&lr_s_ready)$fdisplay(trace,"RELOAD %0d %0d %040h",cycles,lr_s_node,lr_s_payload);
 if(lr_busy&&(host_ctrl_ready||host_io_ready))$fatal(1,"label restore exclusive host lease");
end

reg cf_last_rsp=0;
always @(posedge clk)begin
 if(k_cold_rst)cf_last_rsp<=0;
 else begin
  cf_last_rsp<=cf_rsp_valid;
  for(integer cx=0;cx<6;cx=cx+1)begin
   if(cf_valid[cx]&&cf_ready[cx])$fdisplay(trace,"CQ %0d %0d %096h",cycles,cx,cf_payload[cx*384+:384]);
   if(cf_replies[cx]&&cf_reply_ready[cx])$fdisplay(trace,"CP %0d %0d %0d",cycles,cx,cf_status[cx*3+:3]);
  end
  if(cf_rsp_valid&&!cf_last_rsp)begin
   if(cf_rsp_status||cf_sent!=63||cf_retired!=63||cf_fault)$fatal(1,"hardware config restore result");
   $fdisplay(trace,"CD %0d %0d %0d %0d",cycles,cf_rsp_status,cf_sent,cf_retired);
  end
  if(cf_busy&&(q_cfg_ready||g_cfg_ready||d_cfg_ready||t_cfg_ready||owner_cfg_ready||cs_cfg_ready))$fatal(1,"config restore host lease");
 end
end

assign f_sv[0]=q_cfg_valid;assign q_cfg_ready=f_sr[0];assign q_cfg_rsp_valid=f_srv[0];assign f_srr[0]=q_cfg_rsp_ready;
assign f_sp[0+:64]=q_cfg_base;assign fd_q_cfg_base=f_dp[0+:64];
assign f_sp[64+:64]=q_cfg_design;assign fd_q_cfg_design=f_dp[64+:64];
assign f_sp[128+:32]=q_cfg_connections;assign fd_q_cfg_connections=f_dp[128+:32];
assign f_sp[160+:32]=q_cfg_nodes;assign fd_q_cfg_nodes=f_dp[160+:32];
assign f_sp[192+:32]=q_cfg_nets;assign fd_q_cfg_nets=f_dp[192+:32];
assign f_sp[224+:32]=q_cfg_revision;assign fd_q_cfg_revision=f_dp[224+:32];
assign f_sp[256+:2176]=0;
assign f_drp[0+:3]=fd_q_cfg_status;assign q_cfg_status=f_srp[0+:3];
assign f_drp[3+:253]=0;
assign fd_q_cfg_valid=f_dv[0];assign f_dr[0]=fd_q_cfg_ready;assign f_drv[0]=fd_q_cfg_rsp_valid;assign fd_q_cfg_rsp_ready=f_drr[0];
assign f_sv[1]=g_cfg_valid;assign g_cfg_ready=f_sr[1];assign g_cfg_rsp_valid=f_srv[1];assign f_srr[1]=g_cfg_rsp_ready;
assign f_sp[2432+:64]=g_cfg_offsets_base;assign fd_g_cfg_offsets_base=f_dp[2432+:64];
assign f_sp[2496+:64]=g_cfg_edges_base;assign fd_g_cfg_edges_base=f_dp[2496+:64];
assign f_sp[2560+:64]=g_cfg_attrs_base;assign fd_g_cfg_attrs_base=f_dp[2560+:64];
assign f_sp[2624+:32]=g_cfg_nodes;assign fd_g_cfg_nodes=f_dp[2624+:32];
assign f_sp[2656+:32]=g_cfg_edges;assign fd_g_cfg_edges=f_dp[2656+:32];
assign f_sp[2688+:2176]=0;
assign f_drp[256+:3]=fd_g_cfg_status;assign g_cfg_status=f_srp[256+:3];
assign f_drp[259+:253]=0;
assign fd_g_cfg_valid=f_dv[1];assign f_dr[1]=fd_g_cfg_ready;assign f_drv[1]=fd_g_cfg_rsp_valid;assign fd_g_cfg_rsp_ready=f_drr[1];
assign f_sv[2]=d_cfg_valid;assign d_cfg_ready=f_sr[2];assign d_cfg_rsp_valid=f_srv[2];assign f_srr[2]=d_cfg_rsp_ready;
assign f_sp[4864+:64]=d_cfg_base;assign fd_d_cfg_base=f_dp[4864+:64];
assign f_sp[4928+:32]=d_cfg_nodes;assign fd_d_cfg_nodes=f_dp[4928+:32];
assign f_sp[4960+:2336]=0;
assign f_drp[512+:3]=fd_d_cfg_status;assign d_cfg_status=f_srp[512+:3];
assign f_drp[515+:253]=0;
assign fd_d_cfg_valid=f_dv[2];assign f_dr[2]=fd_d_cfg_ready;assign f_drv[2]=fd_d_cfg_rsp_valid;assign fd_d_cfg_rsp_ready=f_drr[2];
assign f_sv[3]=t_cfg_valid;assign t_cfg_ready=f_sr[3];assign t_cfg_rsp_valid=f_srv[3];assign f_srr[3]=t_cfg_rsp_ready;
assign f_sp[7296+:64]=t_cfg_rows_base;assign fd_t_cfg_rows_base=f_dp[7296+:64];
assign f_sp[7360+:64]=t_cfg_columns_base;assign fd_t_cfg_columns_base=f_dp[7360+:64];
assign f_sp[7424+:32]=t_cfg_rows;assign fd_t_cfg_rows=f_dp[7424+:32];
assign f_sp[7456+:32]=t_cfg_columns;assign fd_t_cfg_columns=f_dp[7456+:32];
assign f_sp[7488+:2240]=0;
assign f_drp[768+:3]=fd_t_cfg_status;assign t_cfg_status=f_srp[768+:3];
assign f_drp[771+:253]=0;
assign fd_t_cfg_valid=f_dv[3];assign f_dr[3]=fd_t_cfg_ready;assign f_drv[3]=fd_t_cfg_rsp_valid;assign fd_t_cfg_rsp_ready=f_drr[3];
assign f_sv[4]=owner_cfg_valid;assign owner_cfg_ready=f_sr[4];assign owner_cfg_rsp_valid=f_srv[4];assign f_srr[4]=owner_cfg_rsp_ready;
assign f_sp[9728+:64]=owner_cfg_primary;assign fd_owner_cfg_primary=f_dp[9728+:64];
assign f_sp[9792+:64]=owner_cfg_pool;assign fd_owner_cfg_pool=f_dp[9792+:64];
assign f_sp[9856+:64]=owner_cfg_allocator;assign fd_owner_cfg_allocator=f_dp[9856+:64];
assign f_sp[9920+:32]=owner_cfg_nodes;assign fd_owner_cfg_nodes=f_dp[9920+:32];
assign f_sp[9952+:32]=owner_cfg_capacity;assign fd_owner_cfg_capacity=f_dp[9952+:32];
assign f_sp[9984+:2176]=0;
assign f_drp[1024+:3]=fd_owner_cfg_status;assign owner_cfg_status=f_srp[1024+:3];
assign f_drp[1027+:253]=0;
assign fd_owner_cfg_valid=f_dv[4];assign f_dr[4]=fd_owner_cfg_ready;assign f_drv[4]=fd_owner_cfg_rsp_valid;assign fd_owner_cfg_rsp_ready=f_drr[4];
assign f_sv[5]=cs_cfg_valid;assign cs_cfg_ready=f_sr[5];assign cs_cfg_rsp_valid=f_srv[5];assign f_srr[5]=cs_cfg_rsp_ready;
assign f_sp[12160+:64]=cs_cfg_history;assign fd_cs_cfg_history=f_dp[12160+:64];
assign f_sp[12224+:64]=cs_cfg_prices;assign fd_cs_cfg_prices=f_dp[12224+:64];
assign f_sp[12288+:64]=cs_cfg_nets;assign fd_cs_cfg_nets=f_dp[12288+:64];
assign f_sp[12352+:64]=cs_cfg_design_id;assign fd_cs_cfg_design_id=f_dp[12352+:64];
assign f_sp[12416+:32]=cs_cfg_nodes;assign fd_cs_cfg_nodes=f_dp[12416+:32];
assign f_sp[12448+:32]=cs_cfg_net_count;assign fd_cs_cfg_net_count=f_dp[12448+:32];
assign f_sp[12480+:32]=cs_cfg_version;assign fd_cs_cfg_version=f_dp[12480+:32];
assign f_sp[12512+:2080]=0;
assign f_drp[1280+:3]=fd_cs_cfg_status;assign cs_cfg_status=f_srp[1280+:3];
assign f_drp[1283+:253]=0;
assign fd_cs_cfg_valid=f_dv[5];assign f_dr[5]=fd_cs_cfg_ready;assign f_drv[5]=fd_cs_cfg_rsp_valid;assign fd_cs_cfg_rsp_ready=f_drr[5];
assign f_sv[6]=host_ctrl_valid;assign host_ctrl_ready=f_sr[6];assign host_ctrl_rsp_valid=f_srv[6];assign f_srr[6]=host_ctrl_rsp_ready;
assign f_sp[14592+:2]=host_ctrl_op;assign fd_host_ctrl_op=f_dp[14592+:2];
assign f_sp[14594+:2]=host_ctrl_query;assign fd_host_ctrl_query=f_dp[14594+:2];
assign f_sp[14596+:4]=host_ctrl_price;assign fd_host_ctrl_price=f_dp[14596+:4];
assign f_sp[14600+:32]=host_ctrl_version;assign fd_host_ctrl_version=f_dp[14600+:32];
assign f_sp[14632+:2392]=0;
assign f_drp[1536+:4]=fd_host_ctrl_status;assign host_ctrl_status=f_srp[1536+:4];
assign f_drp[1540+:252]=0;
assign fd_host_ctrl_valid=f_dv[6];assign f_dr[6]=fd_host_ctrl_ready;assign f_drv[6]=fd_host_ctrl_rsp_valid;assign fd_host_ctrl_rsp_ready=f_drr[6];
assign f_sv[7]=host_design_req_valid;assign host_design_req_ready=f_sr[7];assign host_design_rsp_valid=f_srv[7];assign f_srr[7]=host_design_rsp_ready;
assign f_sp[17024+:3]=host_design_req_op;assign fd_host_design_req_op=f_dp[17024+:3];
assign f_sp[17027+:32]=host_design_req_cookie;assign fd_host_design_req_cookie=f_dp[17027+:32];
assign f_sp[17059+:32]=host_design_req_owner;assign fd_host_design_req_owner=f_dp[17059+:32];
assign f_sp[17091+:32]=host_design_req_node;assign fd_host_design_req_node=f_dp[17091+:32];
assign f_sp[17123+:32]=host_design_req_arg;assign fd_host_design_req_arg=f_dp[17123+:32];
assign f_sp[17155+:2301]=0;
assign f_drp[1792+:4]=fd_host_design_rsp_status;assign host_design_rsp_status=f_srp[1792+:4];
assign f_drp[1796+:32]=fd_host_design_rsp_cookie;assign host_design_rsp_cookie=f_srp[1796+:32];
assign f_drp[1828+:32]=fd_host_design_rsp_flags;assign host_design_rsp_flags=f_srp[1828+:32];
assign f_drp[1860+:32]=fd_host_design_rsp_count;assign host_design_rsp_count=f_srp[1860+:32];
assign f_drp[1892+:32]=fd_host_design_rsp_mask;assign host_design_rsp_mask=f_srp[1892+:32];
assign f_drp[1924+:124]=0;
assign fd_host_design_req_valid=f_dv[7];assign f_dr[7]=fd_host_design_req_ready;assign f_drv[7]=fd_host_design_rsp_valid;assign fd_host_design_rsp_ready=f_drr[7];
assign f_sv[8]=host_io_valid;assign host_io_ready=f_sr[8];assign host_io_rsp_valid=f_srv[8];assign f_srr[8]=host_io_rsp_ready;
assign f_sp[19456+:1]=host_io_write;assign fd_host_io_write=f_dp[19456+:1];
assign f_sp[19457+:32]=host_io_node;assign fd_host_io_node=f_dp[19457+:32];
assign f_sp[19489+:32]=host_io_value;assign fd_host_io_value=f_dp[19489+:32];
assign f_sp[19521+:3]=host_io_field;assign fd_host_io_field=f_dp[19521+:3];
assign f_sp[19524+:2364]=0;
assign f_drp[2048+:4]=fd_host_io_status;assign host_io_status=f_srp[2048+:4];
assign f_drp[2052+:1]=fd_host_io_present;assign host_io_present=f_srp[2052+:1];
assign f_drp[2053+:160]=fd_host_io_payload;assign host_io_payload=f_srp[2053+:160];
assign f_drp[2213+:91]=0;
assign fd_host_io_valid=f_dv[8];assign f_dr[8]=fd_host_io_ready;assign f_drv[8]=fd_host_io_rsp_valid;assign fd_host_io_rsp_ready=f_drr[8];
assign f_sv[9]=host_owner_req_valid;assign host_owner_req_ready=f_sr[9];assign host_owner_rsp_valid=f_srv[9];assign f_srr[9]=host_owner_rsp_ready;
assign f_sp[21888+:3]=host_owner_req_op;assign fd_host_owner_req_op=f_dp[21888+:3];
assign f_sp[21891+:32]=host_owner_req_cookie;assign fd_host_owner_req_cookie=f_dp[21891+:32];
assign f_sp[21923+:32]=host_owner_req_node;assign fd_host_owner_req_node=f_dp[21923+:32];
assign f_sp[21955+:32]=host_owner_req_net;assign fd_host_owner_req_net=f_dp[21955+:32];
assign f_sp[21987+:2333]=0;
assign f_drp[2304+:4]=fd_host_owner_rsp_status;assign host_owner_rsp_status=f_srp[2304+:4];
assign f_drp[2308+:32]=fd_host_owner_rsp_cookie;assign host_owner_rsp_cookie=f_srp[2308+:32];
assign f_drp[2340+:32]=fd_host_owner_rsp_count;assign host_owner_rsp_count=f_srp[2340+:32];
assign f_drp[2372+:32]=fd_host_owner_rsp_occupancy;assign host_owner_rsp_occupancy=f_srp[2372+:32];
assign f_drp[2404+:1]=fd_host_owner_rsp_will_overuse;assign host_owner_rsp_will_overuse=f_srp[2404+:1];
assign f_drp[2405+:155]=0;
assign fd_host_owner_req_valid=f_dv[9];assign f_dr[9]=fd_host_owner_req_ready;assign f_drv[9]=fd_host_owner_rsp_valid;assign fd_host_owner_rsp_ready=f_drr[9];
assign f_sv[10]=cc_req_valid;assign cc_req_ready=f_sr[10];assign cc_rsp_valid=f_srv[10];assign f_srr[10]=cc_rsp_ready;
assign f_sp[24320+:128]=cc_req_words;assign fd_cc_req_words=f_dp[24320+:128];
assign f_sp[24448+:32]=cc_req_cookie;assign fd_cc_req_cookie=f_dp[24448+:32];
assign f_sp[24480+:32]=cc_req_version;assign fd_cc_req_version=f_dp[24480+:32];
assign f_sp[24512+:64]=cc_req_design_id;assign fd_cc_req_design_id=f_dp[24512+:64];
assign f_sp[24576+:2]=cc_req_query;assign fd_cc_req_query=f_dp[24576+:2];
assign f_sp[24578+:4]=cc_req_price;assign fd_cc_req_price=f_dp[24578+:4];
assign f_sp[24582+:2170]=0;
assign f_drp[2560+:64]=fd_cc_rsp_words;assign cc_rsp_words=f_srp[2560+:64];
assign f_drp[2624+:32]=fd_cc_rsp_cookie;assign cc_rsp_cookie=f_srp[2624+:32];
assign f_drp[2656+:32]=fd_cc_rsp_version;assign cc_rsp_version=f_srp[2656+:32];
assign f_drp[2688+:64]=fd_cc_rsp_design_id;assign cc_rsp_design_id=f_srp[2688+:64];
assign f_drp[2752+:2]=fd_cc_rsp_query;assign cc_rsp_query=f_srp[2752+:2];
assign f_drp[2754+:2]=fd_cc_rsp_status;assign cc_rsp_status=f_srp[2754+:2];
assign f_drp[2756+:4]=fd_cc_rsp_price;assign cc_rsp_price=f_srp[2756+:4];
assign f_drp[2760+:56]=0;
assign fd_cc_req_valid=f_dv[10];assign f_dr[10]=fd_cc_req_ready;assign f_drv[10]=fd_cc_rsp_valid;assign fd_cc_rsp_ready=f_drr[10];
assign f_sv[11]=expand_valid;assign expand_ready=f_sr[11];assign result_valid=f_srv[11];assign f_srr[11]=result_ready;
assign f_sp[26752+:32]=expand_connection;assign fd_expand_connection=f_dp[26752+:32];
assign f_sp[26784+:32]=expand_cookie;assign fd_expand_cookie=f_dp[26784+:32];
assign f_sp[26816+:32]=expand_parent;assign fd_expand_parent=f_dp[26816+:32];
assign f_sp[26848+:32]=expand_prune;assign fd_expand_prune=f_dp[26848+:32];
assign f_sp[26880+:32]=expand_has_laguna;assign fd_expand_has_laguna=f_dp[26880+:32];
assign f_sp[26912+:32]=expand_sink;assign fd_expand_sink=f_dp[26912+:32];
assign f_sp[26944+:32]=expand_net;assign fd_expand_net=f_dp[26944+:32];
assign f_sp[26976+:32]=expand_sequence;assign fd_expand_sequence=f_dp[26976+:32];
assign f_sp[27008+:32]=expand_flags;assign fd_expand_flags=f_dp[27008+:32];
assign f_sp[27040+:32]=expand_xmin;assign fd_expand_xmin=f_dp[27040+:32];
assign f_sp[27072+:32]=expand_xmax;assign fd_expand_xmax=f_dp[27072+:32];
assign f_sp[27104+:32]=expand_ymin;assign fd_expand_ymin=f_dp[27104+:32];
assign f_sp[27136+:32]=expand_ymax;assign fd_expand_ymax=f_dp[27136+:32];
assign f_sp[27168+:32]=expand_version;assign fd_expand_version=f_dp[27168+:32];
assign f_sp[27200+:1984]=0;
assign f_drp[2816+:4]=fd_result_status;assign result_status=f_srp[2816+:4];
assign f_drp[2820+:32]=fd_result_cookie;assign result_cookie=f_srp[2820+:32];
assign f_drp[2852+:32]=fd_result_count;assign result_count=f_srp[2852+:32];
assign f_drp[2884+:32]=fd_result_expanded_count;assign result_expanded_count=f_srp[2884+:32];
assign f_drp[2916+:32]=fd_result_raw_count;assign result_raw_count=f_srp[2916+:32];
assign f_drp[2948+:32]=fd_result_mask;assign result_mask=f_srp[2948+:32];
assign f_drp[2980+:1]=fd_result_hit;assign result_hit=f_srp[2980+:1];
assign f_drp[2981+:1]=fd_result_early;assign result_early=f_srp[2981+:1];
assign f_drp[2982+:90]=0;
assign fd_expand_valid=f_dv[11];assign f_dr[11]=fd_expand_ready;assign f_drv[11]=fd_result_valid;assign fd_result_ready=f_drr[11];
assign f_sv[12]=seed_valid;assign seed_ready=f_sr[12];assign seed_rsp_valid=f_srv[12];assign f_srr[12]=seed_rsp_ready;
assign f_sp[29184+:32]=seed_op;assign fd_seed_op=f_dp[29184+:32];
assign f_sp[29216+:32]=seed_key;assign fd_seed_key=f_dp[29216+:32];
assign f_sp[29248+:32]=seed_id;assign fd_seed_id=f_dp[29248+:32];
assign f_sp[29280+:32]=seed_cookie;assign fd_seed_cookie=f_dp[29280+:32];
assign f_sp[29312+:32]=seed_version;assign fd_seed_version=f_dp[29312+:32];
assign f_sp[29344+:2272]=0;
assign f_drp[3072+:32]=fd_seed_rsp_status;assign seed_rsp_status=f_srp[3072+:32];
assign f_drp[3104+:32]=fd_seed_rsp_cookie;assign seed_rsp_cookie=f_srp[3104+:32];
assign f_drp[3136+:32]=fd_seed_rsp_size;assign seed_rsp_size=f_srp[3136+:32];
assign f_drp[3168+:32]=fd_seed_rsp_key;assign seed_rsp_key=f_srp[3168+:32];
assign f_drp[3200+:32]=fd_seed_rsp_id;assign seed_rsp_id=f_srp[3200+:32];
assign f_drp[3232+:96]=0;
assign fd_seed_valid=f_dv[12];assign f_dr[12]=fd_seed_ready;assign f_drv[12]=fd_seed_rsp_valid;assign fd_seed_rsp_ready=f_drr[12];
assign f_sv[13]=cs_req_valid;assign cs_req_ready=f_sr[13];assign cs_rsp_valid=f_srv[13];assign f_srr[13]=cs_rsp_ready;
assign f_sp[31616+:1]=cs_req_host;assign fd_cs_req_host=f_dp[31616+:1];
assign f_sp[31617+:3]=cs_req_op;assign fd_cs_req_op=f_dp[31617+:3];
assign f_sp[31620+:32]=cs_req_cookie;assign fd_cs_req_cookie=f_dp[31620+:32];
assign f_sp[31652+:32]=cs_req_index;assign fd_cs_req_index=f_dp[31652+:32];
assign f_sp[31684+:32]=cs_req_value;assign fd_cs_req_value=f_dp[31684+:32];
assign f_sp[31716+:32]=cs_req_version;assign fd_cs_req_version=f_dp[31716+:32];
assign f_sp[31748+:2]=cs_req_query;assign fd_cs_req_query=f_dp[31748+:2];
assign f_sp[31750+:4]=cs_req_price;assign fd_cs_req_price=f_dp[31750+:4];
assign f_sp[31754+:2294]=0;
assign f_drp[3328+:4]=fd_cs_rsp_status;assign cs_rsp_status=f_srp[3328+:4];
assign f_drp[3332+:32]=fd_cs_rsp_cookie;assign cs_rsp_cookie=f_srp[3332+:32];
assign f_drp[3364+:32]=fd_cs_rsp_index;assign cs_rsp_index=f_srp[3364+:32];
assign f_drp[3396+:32]=fd_cs_rsp_version;assign cs_rsp_version=f_srp[3396+:32];
assign f_drp[3428+:3]=fd_cs_rsp_op;assign cs_rsp_op=f_srp[3428+:3];
assign f_drp[3431+:1]=fd_cs_rsp_host;assign cs_rsp_host=f_srp[3431+:1];
assign f_drp[3432+:2]=fd_cs_rsp_query;assign cs_rsp_query=f_srp[3432+:2];
assign f_drp[3434+:4]=fd_cs_rsp_price;assign cs_rsp_price=f_srp[3434+:4];
assign f_drp[3438+:128]=fd_cs_rsp_data;assign cs_rsp_data=f_srp[3438+:128];
assign f_drp[3566+:18]=0;
assign fd_cs_req_valid=f_dv[13];assign f_dr[13]=fd_cs_req_ready;assign f_drv[13]=fd_cs_rsp_valid;assign fd_cs_rsp_ready=f_drr[13];
assign f_sv[14]=k_cfg_valid;assign k_cfg_ready=f_sr[14];assign k_cfg_rsp_valid=f_srv[14];assign f_srr[14]=k_cfg_rsp_ready;
assign f_sp[34048+:1]=1'b1;assign fd_fa_authoritative=f_dp[34048+:1];
assign f_sp[34049+:64]=design_id;assign fd_fa_design=f_dp[34049+:64];
assign f_sp[34113+:32]=k_checkpoint;assign fd_fa_checkpoint=f_dp[34113+:32];
assign f_sp[34145+:32]=k_cfg_version;assign fd_fa_version=f_dp[34145+:32];
assign f_sp[34177+:2]=k_cfg_query;assign fd_fa_query=f_dp[34177+:2];
assign f_sp[34179+:4]=k_cfg_price;assign fd_fa_price=f_dp[34179+:4];
assign f_sp[34183+:2297]=0;
assign f_drp[3584+:1]=fd_k_cfg_status;assign k_cfg_status=f_srp[3584+:1];
assign f_drp[3585+:255]=0;
assign fd_k_cfg_valid=f_dv[14];assign f_dr[14]=fd_k_cfg_ready;assign f_drv[14]=fd_k_cfg_rsp_valid;assign fd_k_cfg_rsp_ready=f_drr[14];
assign f_sv[15]=cf_load_valid;assign cf_load_ready=f_sr[15];assign cf_load_rsp_valid=f_srv[15];assign f_srr[15]=cf_load_rsp_ready;
assign f_sp[36480+:2304]=cf_input;assign fd_fc_payload=f_dp[36480+:2304];
assign f_sp[38784+:64]=k_saved_design;assign fd_fc_design=f_dp[38784+:64];
assign f_sp[38848+:32]=k_saved_checkpoint;assign fd_fc_checkpoint=f_dp[38848+:32];
assign f_sp[38880+:1]=1'b1;assign fd_fc_authoritative=f_dp[38880+:1];
assign f_sp[38881+:31]=0;
assign f_drp[3840+:1]=fd_cf_load_status;assign cf_load_status=f_srp[3840+:1];
assign f_drp[3841+:255]=0;
assign fd_cf_load_valid=f_dv[15];assign f_dr[15]=fd_cf_load_ready;assign f_drv[15]=fd_cf_load_rsp_valid;assign fd_cf_load_rsp_ready=f_drr[15];
assign f_cbv={6'd0,k_o_valid,lr_l_valid,1'b0,lr_c_valid,cf_valid};
assign cf_ready=f_cbr[5:0];assign cf_replies=f_cbrv[5:0];
assign f_cbp[0+:384]=cf_payload[0+:384];assign f_cbp[384+:2048]=0;assign cf_status[0+:3]=f_cbrp[0+:3];assign f_cbrr[0]=cf_reply_ready[0];
assign f_cbp[2432+:384]=cf_payload[384+:384];assign f_cbp[2816+:2048]=0;assign cf_status[3+:3]=f_cbrp[256+:3];assign f_cbrr[1]=cf_reply_ready[1];
assign f_cbp[4864+:384]=cf_payload[768+:384];assign f_cbp[5248+:2048]=0;assign cf_status[6+:3]=f_cbrp[512+:3];assign f_cbrr[2]=cf_reply_ready[2];
assign f_cbp[7296+:384]=cf_payload[1152+:384];assign f_cbp[7680+:2048]=0;assign cf_status[9+:3]=f_cbrp[768+:3];assign f_cbrr[3]=cf_reply_ready[3];
assign f_cbp[9728+:384]=cf_payload[1536+:384];assign f_cbp[10112+:2048]=0;assign cf_status[12+:3]=f_cbrp[1024+:3];assign f_cbrr[4]=cf_reply_ready[4];
assign f_cbp[12160+:384]=cf_payload[1920+:384];assign f_cbp[12544+:2048]=0;assign cf_status[15+:3]=f_cbrp[1280+:3];assign f_cbrr[5]=cf_reply_ready[5];
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
assign lr_c_ready=f_cbr[6];assign lr_l_ready=f_cbr[8];assign lr_l_rsp_valid=f_cbrv[8];assign k_o_ready=f_cbr[9];assign k_o_rsp_valid=f_cbrv[9];
wire[4:0]f_watch_idle,f_watch_fault;
axi_drain_watch f_watch_g(.clk(clk),.rst(rst),.arvalid(g_m_arvalid),.arready(g_m_arready),.arlen(g_m_arlen),.rvalid(g_m_rvalid),.rready(g_m_rready),.rlast(g_m_rlast),.awvalid(1'b0),.awready(1'b0),.awlen(8'd0),.wvalid(1'b0),.wready(1'b0),.wlast(1'b0),.bvalid(1'b0),.bready(1'b0),.drained(f_watch_idle[0]),.fault(f_watch_fault[0]));
axi_drain_watch f_watch_d(.clk(clk),.rst(rst),.arvalid(d_m_arvalid),.arready(d_m_arready),.arlen(d_m_arlen),.rvalid(d_m_rvalid),.rready(d_m_rready),.rlast(d_m_rlast),.awvalid(d_m_awvalid),.awready(d_m_awready),.awlen(d_m_awlen),.wvalid(d_m_wvalid),.wready(d_m_wready),.wlast(d_m_wlast),.bvalid(d_m_bvalid),.bready(d_m_bready),.drained(f_watch_idle[1]),.fault(f_watch_fault[1]));
axi_drain_watch f_watch_t(.clk(clk),.rst(rst),.arvalid(t_m_arvalid),.arready(t_m_arready),.arlen(t_m_arlen),.rvalid(t_m_rvalid),.rready(t_m_rready),.rlast(t_m_rlast),.awvalid(1'b0),.awready(1'b0),.awlen(8'd0),.wvalid(1'b0),.wready(1'b0),.wlast(1'b0),.bvalid(1'b0),.bready(1'b0),.drained(f_watch_idle[2]),.fault(f_watch_fault[2]));
axi_drain_watch f_watch_cs(.clk(clk),.rst(rst),.arvalid(cs_m_arvalid),.arready(cs_m_arready),.arlen(cs_m_arlen),.rvalid(cs_m_rvalid),.rready(cs_m_rready),.rlast(cs_m_rlast),.awvalid(cs_m_awvalid),.awready(cs_m_awready),.awlen(cs_m_awlen),.wvalid(cs_m_wvalid),.wready(cs_m_wready),.wlast(cs_m_wlast),.bvalid(cs_m_bvalid),.bready(cs_m_bready),.drained(f_watch_idle[3]),.fault(f_watch_fault[3]));
axi_drain_watch f_watch_q(.clk(clk),.rst(rst),.arvalid(q_m_arvalid),.arready(q_m_arready),.arlen(q_m_arlen),.rvalid(q_m_rvalid),.rready(q_m_rready),.rlast(q_m_rlast),.awvalid(1'b0),.awready(1'b0),.awlen(8'd0),.wvalid(1'b0),.wready(1'b0),.wlast(1'b0),.bvalid(1'b0),.bready(1'b0),.drained(f_watch_idle[4]),.fault(f_watch_fault[4]));
assign f_all_drained=label_drained&&owner_drained&&(&f_watch_idle)&&!(|f_watch_fault);assign f_backend_idle=!busy&&!operation_pending&&!cc_busy&&!cs_busy&&!q_busy;
assign f_route_payload={30'd0,rc_req_sequence,32'd2717,rc_req_sink,32'd65185,rc_req_cookie,rc_req_slot,rc_req_op};
transaction_fence #(.LANES(16),.REQ_BITS(2432),.RSP_BITS(256),.ADMIN_FIRST(14),.CALLBACK_MASK(16'h037f))fence(
 .clk(clk),.rst(k_cold_rst),.work_permit(k_permit),.normal_fault(fault||rc_fault||k_fault||cf_fault||lr_fault),.backend_drained(f_all_drained),.backend_idle(f_backend_idle),.route_block(rc_block),
 .s_valid(f_sv),.s_ready(f_sr),.s_payload(f_sp),.s_rsp_valid(f_srv),.s_rsp_ready(f_srr),.s_rsp_payload(f_srp),
 .cb_valid(f_cbv),.cb_ready(f_cbr),.cb_payload(f_cbp),.cb_rsp_valid(f_cbrv),.cb_rsp_ready(f_cbrr),.cb_rsp_payload(f_cbrp),
 .d_valid(f_dv),.d_ready(f_dr),.d_payload(f_dp),.d_rsp_valid(f_drv),.d_rsp_ready(f_drr),.d_rsp_payload(f_drp),
 .route_valid(rc_req_valid),.route_ready(rc_req_ready),.route_payload(f_route_payload),.route_rsp_valid(rc_rsp_valid),.route_rsp_ready(rc_rsp_ready),
 .backend_route_valid(f_broute_valid),.backend_route_ready(f_broute_ready),.backend_route_payload(f_broute_payload),.backend_route_rsp_valid(f_broute_rsp_valid),.backend_route_rsp_ready(f_broute_rsp_ready),.route_error(rc_rsp_status!=0),
 .recover_valid(k_rec_valid),.recover_ready(k_rec_ready),.backend_recover_valid(f_brecover_valid),.backend_recover_ready(f_brecover_ready),
 .recover_rsp_valid(k_rsp_valid),.recover_rsp_ready(k_rsp_ready),.backend_recover_rsp_valid(f_brecover_rsp_valid),.backend_recover_rsp_ready(f_brecover_rsp_ready),.recover_error(k_rsp_status!=0),
 .normal_retired(f_normal_retired),.recovery_owned(f_recovery_owned),.fault(f_fault),.phase(f_phase),.callback_pending(f_pending));

always @(posedge clk)if(!k_cold_rst)begin
 if(f_fault||(|f_watch_fault))$fatal(1,"unified fabric/transport fault");
 if(f_recovery_owned&&(f_sr!=0||rc_req_ready))$fatal(1,"recovery host/route admission leak");
 if(k_target_reset&&(!f_recovery_owned||!f_normal_retired))$fatal(1,"target reset outside retired ownership");
 for(integer fx=0;fx<16;fx=fx+1)begin
  if(f_sv[fx]&&f_sr[fx])$fdisplay(trace,"FS %0d %0d",cycles,fx);
  if(f_dv[fx]&&f_dr[fx])$fdisplay(trace,"FD %0d %0d %0d",cycles,f_phase,fx);
  if(f_drv[fx]&&f_drr[fx])$fdisplay(trace,"FB %0d %0d %0d",cycles,f_phase,fx);
 end
 if(rc_req_valid&&rc_req_ready)$fdisplay(trace,"FR %0d",cycles);
 if(k_rec_valid&&k_rec_ready)$fdisplay(trace,"FK %0d",cycles);
end

initial begin
 trace=$fopen("natural_trace.txt","w");if(!trace)$fatal(1,"trace open");
 if(!$value$plusargs("costvectors=%s",path))$fatal(1,"cost path");fd_gold=$fopen(path,"r");
 if(!$value$plusargs("finallabels=%s",path))$fatal(1,"final path");finals_fd=$fopen(path,"r");
 if(!$value$plusargs("imports=%s",path))$fatal(1,"import path");imports_fd=$fopen(path,"r");
 if(!$value$plusargs("candidates=%s",path))$fatal(1,"candidate path");candidates_fd=$fopen(path,"r");
 if(!$value$plusargs("polls=%s",path))$fatal(1,"poll path");polls_fd=$fopen(path,"r");
 if(!fd_gold||!finals_fd||!imports_fd||!candidates_fd||!polls_fd)$fatal(1,"oracle open");
 bench_rst=1;k_cold_rst=1;design_id=64'h123456789abcdef0;
 g_cfg_offsets_base=64'h1fffff000;g_cfg_edges_base=64'h10fffff000;g_cfg_attrs_base=64'h20fffff000;g_cfg_nodes=9089009;g_cfg_edges=40469536;
 d_cfg_base=64'h31fffff000;d_cfg_nodes=9089009;t_cfg_rows_base=64'h41fffff000;t_cfg_columns_base=64'h51fffff000;t_cfg_rows=311;t_cfg_columns=0;
 owner_cfg_primary=64'h61fffff000;owner_cfg_nodes=9089009;owner_cfg_capacity=0;owner_cfg_pool=owner_cfg_primary+145424192;owner_cfg_allocator=owner_cfg_pool;
 cs_cfg_history=64'h71fffff000;cs_cfg_prices=cs_cfg_history+36356096;cs_cfg_nets=cs_cfg_history+36357120;cs_cfg_nodes=9089009;cs_cfg_net_count=27960;cs_cfg_version=3;cs_cfg_design_id=design_id;
 q_cfg_base=64'h81fffff000;q_cfg_design=design_id;q_cfg_connections=180326;q_cfg_nodes=9089009;q_cfg_nets=27960;q_cfg_revision=1;
 repeat(5)@(negedge clk);bench_rst=0;k_cold_rst=0;
 install_checkpoint;install_config_snapshot;
 @(negedge clk);q_cfg_valid=1;do @(posedge clk);while(!q_cfg_ready);@(negedge clk);q_cfg_valid=0;wait(q_cfg_rsp_valid);@(negedge clk);if(q_cfg_status)$fatal(1,"boot config");q_cfg_rsp_ready=1;@(negedge clk);q_cfg_rsp_ready=0;
 @(negedge clk);g_cfg_valid=1;do @(posedge clk);while(!g_cfg_ready);@(negedge clk);g_cfg_valid=0;wait(g_cfg_rsp_valid);@(negedge clk);if(g_cfg_status)$fatal(1,"boot config");g_cfg_rsp_ready=1;@(negedge clk);g_cfg_rsp_ready=0;
 @(negedge clk);d_cfg_valid=1;do @(posedge clk);while(!d_cfg_ready);@(negedge clk);d_cfg_valid=0;wait(d_cfg_rsp_valid);@(negedge clk);if(d_cfg_status)$fatal(1,"boot config");d_cfg_rsp_ready=1;@(negedge clk);d_cfg_rsp_ready=0;
 @(negedge clk);t_cfg_valid=1;do @(posedge clk);while(!t_cfg_ready);@(negedge clk);t_cfg_valid=0;wait(t_cfg_rsp_valid);@(negedge clk);if(t_cfg_status)$fatal(1,"boot config");t_cfg_rsp_ready=1;@(negedge clk);t_cfg_rsp_ready=0;
 @(negedge clk);owner_cfg_valid=1;do @(posedge clk);while(!owner_cfg_ready);@(negedge clk);owner_cfg_valid=0;wait(owner_cfg_rsp_valid);@(negedge clk);if(owner_cfg_status)$fatal(1,"boot config");owner_cfg_rsp_ready=1;@(negedge clk);owner_cfg_rsp_ready=0;
 @(negedge clk);cs_cfg_valid=1;do @(posedge clk);while(!cs_cfg_ready);@(negedge clk);cs_cfg_valid=0;wait(cs_cfg_rsp_valid);@(negedge clk);if(cs_cfg_status)$fatal(1,"boot config");cs_cfg_rsp_ready=1;@(negedge clk);cs_cfg_rsp_ready=0;
 control(0);
 for(import_i=0;import_i<328;import_i=import_i+1)begin
  rc=$fscanf(imports_fd,"%d",import_node);if(rc!=1)$fatal(1,"import node");
  for(field_i=0;field_i<5;field_i=field_i+1)begin rc=$fscanf(imports_fd,"%h",word);if(rc!=1)$fatal(1,"import word");import_record[field_i*32+:32]=word;end
  for(field_i=0;field_i<5;field_i=field_i+1)label_write(import_node,field_i,import_record[field_i*32+:32]);
  $fdisplay(trace,"I %0d %0d %040h",cycles,import_node,import_record);
 end

 control(1); // Durable import complete before arming any fault.
 if(!$value$plusargs("faultcase=%d",fault_case)||fault_case<1||fault_case>5)$fatal(1,"faultcase");
 owner_b_start=mem_owner.bresponses;owner_r_start=mem_owner.rbeats;label_r_start=mem_p.rbeats;armed=1;
 @(negedge clk);rc_req_op=0;rc_req_slot=0;rc_req_sink=150697;rc_req_sequence=1;rc_req_cookie=32'hfabcd001;rc_req_valid=1;
 do @(posedge clk);while(!rc_req_ready);@(negedge clk);rc_req_valid=0;
 host_ctrl_valid=1;host_io_valid=1;host_owner_req_valid=1;host_design_req_valid=1;expand_valid=1;seed_valid=1;
 q_cfg_valid=1;g_cfg_valid=1;d_cfg_valid=1;t_cfg_valid=1;owner_cfg_valid=1;cs_cfg_valid=1;
 wait(rc_rsp_valid);@(negedge clk);
 if(!injection_seen||!rc_fault||!rc_block||rc_slots!=0||label_watch_fault||owner_watch_fault)$fatal(1,"fault not contained");
 if(rc_rsp_cookie!=32'hfabcd001||rc_rsp_status!=(fault_case==2?4:(fault_case==3||fault_case==4)?6:5)||rc_rsp_acked!=((fault_case==3||fault_case==4)?1:0))$fatal(1,"fault result status=%0d ack=%0d",rc_rsp_status,rc_rsp_acked);
 if(mem_owner.rp||mem_owner.wp||mem_owner.rvalid||mem_owner.bvalid||mem_p.rp||mem_p.wp||mem_p.rvalid||mem_p.bvalid||route_join.l_valid||route_join.o_valid||b_l_rsp_valid||b_o_rsp_valid)$fatal(1,"completion before physical drain");
 $fdisplay(trace,"FC %0d %0d %0d %0d %0d %0d %0d",cycles,fault_case,rc_rsp_status,rc_rsp_acked,mem_owner.bresponses-owner_b_start,mem_owner.rbeats-owner_r_start,mem_p.rbeats-label_r_start);
 repeat(7)begin @(negedge clk);if(!rc_rsp_valid||!rc_block||rc_req_ready||rc_rsp_status!=(fault_case==2?4:(fault_case==3||fault_case==4)?6:5))$fatal(1,"held fault response");end
 rc_rsp_ready=1;@(negedge clk);rc_rsp_ready=0;
 repeat(32)begin @(negedge clk);if(!rc_block||!rc_fault||rc_req_ready||host_io_ready||host_owner_req_ready||host_ctrl_ready||expand_ready||seed_ready)$fatal(1,"fault fence released");end

 k_rec_valid=1;recovering=1;armed=0;injected_abort=0;injected_drift=0;
 host_ctrl_valid=0;host_io_valid=0;host_owner_req_valid=0;host_design_req_valid=0;expand_valid=0;seed_valid=0;
 q_cfg_valid=0;g_cfg_valid=0;d_cfg_valid=0;t_cfg_valid=0;owner_cfg_valid=0;cs_cfg_valid=0;
 do @(posedge clk);while(!k_rec_ready);@(negedge clk);k_rec_valid=0;
 wait(k_rcfg_valid);@(negedge clk);
 restore_epoch=k_new_query;restore_version=k_new_version;
 rc_req_valid=1;expand_valid=1;seed_valid=1;
 wait(!k_rcfg_valid);
 wait(k_labels_valid);@(negedge clk);repairs=k_corrected;$fdisplay(trace,"AUTH %0d %0d",cycles,k_corrected);
 // labels_valid automatically starts the hardware service; TB supplies records only.
 rc=$fseek(imports_fd,0,0);if(rc)$fatal(1,"label stream rewind");
 for(import_i=0;import_i<328;import_i=import_i+1)begin
  rc=$fscanf(imports_fd,"%d",import_node);if(rc!=1)$fatal(1,"stream node");
  for(field_i=0;field_i<5;field_i=field_i+1)begin rc=$fscanf(imports_fd,"%h",word);if(rc!=1)$fatal(1,"stream field");import_record[field_i*32+:32]=word;end
  @(negedge clk);lr_s_valid=1;lr_s_node=import_node;lr_s_payload=import_record;lr_s_last=import_i==327;
  do @(posedge clk);while(!lr_s_ready);@(negedge clk);lr_s_valid=0;
 end
 wait(lr_rsp_valid);@(negedge clk);
 if(lr_rsp_status||lr_rsp_cookie!=32'he0010001||lr_fault||lr_written!=328||lr_verified!=328)$fatal(1,"hardware label restore result");
 $fdisplay(trace,"LD %0d %0d %0d %0d",cycles,lr_rsp_status,lr_written,lr_verified);
 wait(!lr_busy);
 if(rc_req_ready||expand_ready||seed_ready||rc_slots!=0||rc_fault)$fatal(1,"recovery admission gate");
 rc_req_valid=0;expand_valid=0;seed_valid=0;
 wait(k_rsp_valid);@(negedge clk);if(k_rsp_status||k_rsp_cookie!=32'hc0010001||k_fault||k_count!=0)$fatal(1,"coordinator recovery result");
 repeat(5)begin @(negedge clk);if(recover_open||!k_rsp_valid)$fatal(1,"coordinator response gate");end
 $fdisplay(trace,"KD %0d %0d %0d",cycles,k_rsp_status,k_corrected);
 k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;wait(recover_open);
 @(negedge clk);rc_req_op=0;rc_req_slot=0;rc_req_sink=150697;rc_req_sequence=1;rc_req_cookie=32'hfabcd002;rc_req_valid=1;
 do @(posedge clk);while(!rc_req_ready);@(negedge clk);rc_req_valid=0;
 wait(rc_rsp_valid);@(negedge clk);if(rc_rsp_status||rc_rsp_acked!=6||rc_rsp_nodes!=6||rc_slots!=1||rc_fault||!label_drained||!owner_drained)$fatal(1,"recovered commit");
 $fdisplay(trace,"RECOVERED %0d %0d %0d %0d",cycles,rc_rsp_status,rc_rsp_nodes,rc_rsp_acked);
 rc_rsp_ready=1;@(negedge clk);rc_rsp_ready=0;wait(!rc_block);
 k_checkpoint=18;k_cfg_version=restore_version;k_cfg_query=restore_epoch;k_cfg_price=restore_version[3:0];install_checkpoint;install_config_snapshot;
 if(k_count||k_fault)$fatal(1,"committed checkpoint publication");
 control(1);control(2);
 if(fault||rc_fault||repairs!=((fault_case==1||fault_case==3||fault_case==4)?1:0))$fatal(1,"recovery final");
 $fflush(trace);$fclose(trace);$display("TRANSACTION_FENCE_JOIN_PASS case=%0d journal=%0d repairs=%0d epoch=%0d version=%0d cycles=%0d",fault_case,journal_count,repairs,restore_epoch,restore_version,cycles);$finish;
end
endmodule
