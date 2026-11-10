`timescale 1ns/1ps
module tb_candidate_offer;
integer recovery_fault=0,recovery_injected=0,recovery_fi_cycle=0;reg recovery_done=0;
wire recovery_inject;
reg[31:0]retry_cookie=32'hc0010001,retry_version=4,stream_cookie=32'he0010001;
reg[1:0]retry_query=2;reg[3:0]retry_price=4;
integer soft_resets=0,reset_cycles=0,cold_cycles=0;reg[2303:0]descriptor_before;

initial begin if(!$value$plusargs("recoveryfault=%d",recovery_fault)||recovery_fault<1||recovery_fault>5)$fatal(1,"recovery fault selector");end
integer fi_cycle=0,fault_after=0,eligible_responses=0;reg replayed=0;
initial begin if($value$plusargs("faultafter=%d",fault_after))begin if(fault_after<0)$fatal(1,"negative fault ordinal");end end

reg qc_cmd_valid=0;
wire qc_cmd_ready;
reg qc_cmd_slot=0;
reg [31:0] qc_cmd_cookie=0;
reg [31:0] qc_cmd_route_cookie=0;
reg [31:0] qc_cmd_source=0;
reg [31:0] qc_cmd_key=0;
reg [31:0] qc_cmd_nodes=0;
reg [31:0] qc_cmd_max_polls=0;
reg [31:0] qc_cmd_poll_cookie=0;
reg [63:0] qc_cmd_design=0;
reg [1:0] qc_cmd_query=0;
reg [3:0] qc_cmd_price=0;
reg [447:0] qc_cmd_expand=0;
wire qc_rsp_valid;
reg qc_rsp_ready=0;
wire [3:0] qc_rsp_status;
wire [3:0] qc_rsp_detail;
wire [31:0] qc_rsp_cookie;
wire [31:0] qc_rsp_nodes;
wire [31:0] qc_rsp_acked;
wire qc_rsp_committed;
reg qc_abort=0;
wire qc_busy;
wire qc_fault;
wire [3:0] qc_phase;
wire qc_prepared_event;
wire [31:0] qc_prepare_acked;
wire [31:0] qc_cleanup_acked;

reg ss_abort=0;
reg ss_start_valid=0;
wire ss_start_ready;
reg [31:0] ss_start_cookie=0;
reg [31:0] ss_start_source=0;
reg [31:0] ss_start_key=0;
reg [31:0] ss_start_nodes=0;
reg [31:0] ss_start_max_polls=0;
reg [31:0] ss_start_poll_cookie=0;
reg [63:0] ss_start_design=0;
reg [1:0] ss_start_query=0;
reg [3:0] ss_start_price=0;
reg [447:0] ss_start_expand=0;
wire ss_rsp_valid;
reg ss_rsp_ready=0;
wire [3:0] ss_rsp_status;
wire [31:0] ss_rsp_cookie;
wire [31:0] ss_polls;
wire [31:0] ss_expands;
wire [31:0] ss_candidates;
wire [31:0] ss_result_node;
wire [31:0] ss_result_key;
wire ss_busy;
wire ss_fault;
wire [3:0] ss_phase;
wire ss_poll_event;
wire [31:0] ss_poll_node;
wire [31:0] ss_poll_key;
wire [31:0] ss_poll_size;

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
reg bench_rst=0;wire rst;
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






reg[31:0]authority_node[0:5],authority_net[0:5],authority_refs0[0:5],authority_occ0[0:5],authority_refs1[0:5],authority_occ1[0:5];
integer auth_fd,auth_rc,auth_i,auth_match,auth_delay=0;string auth_path;
initial begin
 if(!$value$plusargs("authority=%s",auth_path))$fatal(1,"authority path");auth_fd=$fopen(auth_path,"r");if(!auth_fd)$fatal(1,"authority file");
 for(auth_i=0;auth_i<6;auth_i=auth_i+1)begin
  auth_rc=$fscanf(auth_fd,"%d %d %d %d %d %d",authority_node[auth_i],authority_net[auth_i],authority_refs0[auth_i],authority_occ0[auth_i],authority_refs1[auth_i],authority_occ1[auth_i]);if(auth_rc!=6)$fatal(1,"authority row");
 end
end

reg lr_s_valid=0;wire lr_start_valid,lr_rsp_ready;wire lr_start_ready,lr_s_ready;
reg[31:0]lr_s_node=0;reg[159:0]lr_s_payload=0;reg lr_s_last=0;wire[3:0]lr_rsp_status;wire[31:0]lr_written,lr_verified;
wire lr_c_valid,lr_c_ready,lr_c_rsp_ready;wire[1:0]lr_c_op,lr_c_query;wire[3:0]lr_c_price;wire[31:0]lr_c_version;
wire lr_l_valid,lr_l_ready,lr_l_write,lr_l_rsp_ready,lr_l_rsp_valid,mux_h_l_ready,mux_h_l_rsp_valid;
wire[31:0]lr_l_node,lr_l_value;wire[2:0]lr_l_field;







reg cf_load_valid=0,cf_load_rsp_ready=0;wire cf_load_ready,cf_load_rsp_valid,cf_load_status;
wire[5:0]cf_valid,cf_ready,cf_replies,cf_reply_ready,cf_sent,cf_retired;wire[17:0]cf_status;
wire[2303:0]cf_input,cf_payload;wire[3:0]cf_rsp_status;wire[63:0]cf_saved_design;wire[31:0]cf_saved_checkpoint;
assign cf_input[0+:384]={128'd0,q_cfg_revision,q_cfg_nets,q_cfg_nodes,q_cfg_connections,q_cfg_design,q_cfg_base};
assign cf_input[384+:384]={128'd0,g_cfg_edges,g_cfg_nodes,g_cfg_attrs_base,g_cfg_edges_base,g_cfg_offsets_base};
assign cf_input[768+:384]={288'd0,d_cfg_nodes,d_cfg_base};
assign cf_input[1152+:384]={192'd0,t_cfg_columns,t_cfg_rows,t_cfg_columns_base,t_cfg_rows_base};
assign cf_input[1536+:384]={128'd0,owner_cfg_capacity,owner_cfg_nodes,owner_cfg_allocator,owner_cfg_pool,owner_cfg_primary};
assign cf_input[1920+:384]={32'd0,k_cfg_version,cs_cfg_net_count,cs_cfg_nodes,cs_cfg_design_id,cs_cfg_nets,cs_cfg_prices,cs_cfg_history};









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
.inject_r(armed&&!injection_seen&&fault_case==3&&qc_phase==4&&eligible_responses==fault_after),
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
.inject_r(recovery_inject&&recovery_fault==5&&system.inner.backend.label_restore.state==10),
.inject_b(recovery_inject&&((recovery_fault==3&&system.inner.backend.label_restore.state==7)||(recovery_fault==4&&system.inner.backend.label_restore.state==2&&system.inner.backend.label_restore.checkpoint_phase))),
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
.inject_r(recovery_inject&&recovery_fault==1),
.inject_b((armed&&!injection_seen&&fault_case==5&&qc_phase==6)||(recovery_inject&&recovery_fault==2)),
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
.inject_r(armed&&!injection_seen&&fault_case==4&&qc_phase==4&&eligible_responses==fault_after),
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
 cycles<=cycles+1;if(cycles>3000000)$fatal(1,"watchdog");
 if(!rst)begin
  if(fault&&!armed&&(!recovering||recover_open)&&replayed)$fatal(1,"join fault controller=%0d expansion=%0d metadata=%0d access=%0d cf=%b pf=%b df=%b of=%b",system.inner.backend.dut.core.controller.state,system.inner.backend.dut.core.expansion.state,system.inner.backend.dut.core.metadata.state,system.inner.backend.dut.core.access.controller.state,system.inner.backend.dut.core.capture_fault,system.inner.backend.dut.core.p_fault,system.inner.backend.dut.core.d_fault,system.inner.backend.dut.core.o_fault);
  if(operation_pending)begin
   if(host_ctrl_ready||host_io_ready||host_design_req_ready||host_owner_req_ready||expand_ready)$fatal(1,"query lease gap");
   if(host_ctrl_valid&&host_io_valid&&host_design_req_valid&&host_owner_req_valid)host_blocks<=host_blocks+1;
  end
  if(system.inner.backend.dut.core.ce_expand_valid&&system.inner.backend.dut.core.ce_expand_ready)begin physical_expands<=physical_expands+1;$fdisplay(trace,"E %0d %0d %0d",cycles,system.inner.backend.dut.core.ce_expand_cookie,system.inner.backend.dut.core.ce_expand_parent);end
  if(system.inner.backend.dut.core.ce_result_valid&&system.inner.backend.dut.core.ce_result_ready)$fdisplay(trace,"S %0d %0d %0d",cycles,system.inner.backend.dut.core.ce_result_cookie,system.inner.backend.dut.core.ce_result_count);
  if(system.inner.backend.dut.core.m_req_valid&&system.inner.backend.dut.core.m_req_ready)begin
   metadata_calls<=metadata_calls+1;if(system.inner.backend.dut.core.expansion.state!=0||system.inner.backend.dut.core.child_capture.state!=0)$fatal(1,"metadata before seal");
   $fdisplay(trace,"M %0d %0d %0d %0d",cycles,system.inner.backend.dut.core.controller.frame_cookie,system.inner.backend.dut.core.m_req_parent,system.inner.backend.dut.core.m_req_child);
  end
  if(system.inner.backend.dut.core.s_l_valid&&system.inner.backend.dut.core.s_l_ready)begin
   label_pending<=1;pending_label_node<=system.inner.backend.dut.core.s_l_node;pending_label_field<=system.inner.backend.dut.core.s_l_field;pending_label_write<=system.inner.backend.dut.core.s_l_write;
   $fdisplay(trace,"LQ %0d %0d %0d %0d",cycles,system.inner.backend.dut.core.s_l_node,system.inner.backend.dut.core.s_l_field,system.inner.backend.dut.core.s_l_write);
  end
  if(system.inner.backend.dut.core.s_l_rsp_valid&&system.inner.backend.dut.core.s_l_rsp_ready)begin
   if(!label_pending)$fatal(1,"unowned label reply");label_pending<=0;
   if(!pending_label_write&&pending_label_field==3)begin visited_reads<=visited_reads+1;$fdisplay(trace,"V %0d %0d %0d %040h",cycles,pending_label_node,system.inner.backend.dut.core.s_l_status,system.inner.backend.dut.core.s_l_payload);end
  end
  if(system.inner.backend.dut.cl_valid&&system.inner.backend.dut.cl_ready)$fdisplay(trace,"W %0d %0d %0d %08h",cycles,system.inner.backend.dut.cl_node,system.inner.backend.dut.cl_field,system.inner.backend.dut.cl_value);
  if(system.inner.backend.dut.cl_rsp_valid&&system.inner.backend.dut.cl_rsp_ready)$fdisplay(trace,"A %0d %0d %0d %040h",cycles,system.inner.backend.dut.cl_status,system.inner.backend.dut.cl_present,system.inner.backend.dut.cl_payload);
  if(system.inner.backend.dut.of_valid&&system.inner.backend.dut.of_ready)begin offers<=offers+1;$fdisplay(trace,"F %0d %0d %08h %0d",cycles,system.inner.backend.dut.of_id,system.inner.backend.dut.of_key,system.inner.backend.dut.frontier_size);end
  if(system.inner.backend.dut.frontier.fs_req_valid&&system.inner.backend.dut.frontier.fs_req_ready)$fdisplay(trace,"FQ %0d %0d %08h %0d %0d",cycles,system.inner.backend.dut.frontier.fs_req_op,system.inner.backend.dut.frontier.fs_req_key,system.inner.backend.dut.frontier.fs_req_id,system.inner.backend.dut.frontier.fs_req_cookie);
  if(system.inner.backend.dut.frontier.fs_rsp_valid&&system.inner.backend.dut.frontier.fs_rsp_ready)$fdisplay(trace,"FR %0d %0d %08h %0d %0d",cycles,system.inner.backend.dut.frontier.fs_rsp_status,system.inner.backend.dut.frontier.fs_rsp_key,system.inner.backend.dut.frontier.fs_rsp_id,system.inner.backend.dut.frontier.fs_rsp_size);
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

wire actual_route_slot=system.inner.backend.f_broute_payload[1];
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
 if(system.inner.backend.route_join.l_valid&&system.inner.backend.route_join.l_ready)begin rc_read_node<=system.inner.backend.route_join.l_node;$fdisplay(trace,"RL %0d %0d %0d",cycles,actual_route_slot,system.inner.backend.route_join.l_node);end
 if(system.inner.backend.route_join.l_rsp_valid&&system.inner.backend.route_join.l_rsp_ready)$fdisplay(trace,"RA %0d %0d %0d %040h",cycles,actual_route_slot,rc_read_node,b_l_payload);
 if(system.inner.backend.route_join.o_valid&&system.inner.backend.route_join.o_ready)begin
  $fdisplay(trace,"RO %0d %0d %0d %0d",cycles,actual_route_slot,system.inner.backend.route_join.o_op,system.inner.backend.route_join.o_node);
  if(system.inner.backend.route_join.o_op==1)begin
   if(actual_route_slot==0)begin saved1[count1]<=system.inner.backend.route_join.o_node;count1<=count1+1;end
   else begin saved2[count2]<=system.inner.backend.route_join.o_node;count2<=count2+1;end
  end
 end
 if(system.inner.backend.route_join.o_rsp_valid&&system.inner.backend.route_join.o_rsp_ready)$fdisplay(trace,"RB %0d %0d %0d %0d %0d",cycles,actual_route_slot,b_o_status,b_o_count,b_o_occupancy);
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
  if(system.inner.backend.route_join.held&&b_o_valid&&b_o_ready)begin
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
  if(system.inner.backend.label_restore.state==4)$fdisplay(trace,"ABS %0d %040h",cycles,f_cbrp[2053+:160]);
  if(system.inner.backend.label_restore.state==10)$fdisplay(trace,"CHECK %0d %0d %040h",cycles,system.inner.backend.label_restore.row[191:160],f_cbrp[2053+:160]);
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
assign f_sp[0+:64]=q_cfg_base;
assign f_sp[64+:64]=q_cfg_design;
assign f_sp[128+:32]=q_cfg_connections;
assign f_sp[160+:32]=q_cfg_nodes;
assign f_sp[192+:32]=q_cfg_nets;
assign f_sp[224+:32]=q_cfg_revision;
assign f_sp[256+:2176]=0;
assign q_cfg_status=f_srp[0+:3];


assign f_sv[1]=g_cfg_valid;assign g_cfg_ready=f_sr[1];assign g_cfg_rsp_valid=f_srv[1];assign f_srr[1]=g_cfg_rsp_ready;
assign f_sp[2432+:64]=g_cfg_offsets_base;
assign f_sp[2496+:64]=g_cfg_edges_base;
assign f_sp[2560+:64]=g_cfg_attrs_base;
assign f_sp[2624+:32]=g_cfg_nodes;
assign f_sp[2656+:32]=g_cfg_edges;
assign f_sp[2688+:2176]=0;
assign g_cfg_status=f_srp[256+:3];


assign f_sv[2]=d_cfg_valid;assign d_cfg_ready=f_sr[2];assign d_cfg_rsp_valid=f_srv[2];assign f_srr[2]=d_cfg_rsp_ready;
assign f_sp[4864+:64]=d_cfg_base;
assign f_sp[4928+:32]=d_cfg_nodes;
assign f_sp[4960+:2336]=0;
assign d_cfg_status=f_srp[512+:3];


assign f_sv[3]=t_cfg_valid;assign t_cfg_ready=f_sr[3];assign t_cfg_rsp_valid=f_srv[3];assign f_srr[3]=t_cfg_rsp_ready;
assign f_sp[7296+:64]=t_cfg_rows_base;
assign f_sp[7360+:64]=t_cfg_columns_base;
assign f_sp[7424+:32]=t_cfg_rows;
assign f_sp[7456+:32]=t_cfg_columns;
assign f_sp[7488+:2240]=0;
assign t_cfg_status=f_srp[768+:3];


assign f_sv[4]=owner_cfg_valid;assign owner_cfg_ready=f_sr[4];assign owner_cfg_rsp_valid=f_srv[4];assign f_srr[4]=owner_cfg_rsp_ready;
assign f_sp[9728+:64]=owner_cfg_primary;
assign f_sp[9792+:64]=owner_cfg_pool;
assign f_sp[9856+:64]=owner_cfg_allocator;
assign f_sp[9920+:32]=owner_cfg_nodes;
assign f_sp[9952+:32]=owner_cfg_capacity;
assign f_sp[9984+:2176]=0;
assign owner_cfg_status=f_srp[1024+:3];


assign f_sv[5]=cs_cfg_valid;assign cs_cfg_ready=f_sr[5];assign cs_cfg_rsp_valid=f_srv[5];assign f_srr[5]=cs_cfg_rsp_ready;
assign f_sp[12160+:64]=cs_cfg_history;
assign f_sp[12224+:64]=cs_cfg_prices;
assign f_sp[12288+:64]=cs_cfg_nets;
assign f_sp[12352+:64]=cs_cfg_design_id;
assign f_sp[12416+:32]=cs_cfg_nodes;
assign f_sp[12448+:32]=cs_cfg_net_count;
assign f_sp[12480+:32]=cs_cfg_version;
assign f_sp[12512+:2080]=0;
assign cs_cfg_status=f_srp[1280+:3];


assign f_sv[6]=host_ctrl_valid;assign host_ctrl_ready=f_sr[6];assign host_ctrl_rsp_valid=f_srv[6];assign f_srr[6]=host_ctrl_rsp_ready;
assign f_sp[14592+:2]=host_ctrl_op;
assign f_sp[14594+:2]=host_ctrl_query;
assign f_sp[14596+:4]=host_ctrl_price;
assign f_sp[14600+:32]=host_ctrl_version;
assign f_sp[14632+:2392]=0;
assign host_ctrl_status=f_srp[1536+:4];


assign f_sv[7]=host_design_req_valid;assign host_design_req_ready=f_sr[7];assign host_design_rsp_valid=f_srv[7];assign f_srr[7]=host_design_rsp_ready;
assign f_sp[17024+:3]=host_design_req_op;
assign f_sp[17027+:32]=host_design_req_cookie;
assign f_sp[17059+:32]=host_design_req_owner;
assign f_sp[17091+:32]=host_design_req_node;
assign f_sp[17123+:32]=host_design_req_arg;
assign f_sp[17155+:2301]=0;
assign host_design_rsp_status=f_srp[1792+:4];
assign host_design_rsp_cookie=f_srp[1796+:32];
assign host_design_rsp_flags=f_srp[1828+:32];
assign host_design_rsp_count=f_srp[1860+:32];
assign host_design_rsp_mask=f_srp[1892+:32];


assign f_sv[8]=host_io_valid;assign host_io_ready=f_sr[8];assign host_io_rsp_valid=f_srv[8];assign f_srr[8]=host_io_rsp_ready;
assign f_sp[19456+:1]=host_io_write;
assign f_sp[19457+:32]=host_io_node;
assign f_sp[19489+:32]=host_io_value;
assign f_sp[19521+:3]=host_io_field;
assign f_sp[19524+:2364]=0;
assign host_io_status=f_srp[2048+:4];
assign host_io_present=f_srp[2052+:1];
assign host_io_payload=f_srp[2053+:160];


assign f_sv[9]=host_owner_req_valid;assign host_owner_req_ready=f_sr[9];assign host_owner_rsp_valid=f_srv[9];assign f_srr[9]=host_owner_rsp_ready;
assign f_sp[21888+:3]=host_owner_req_op;
assign f_sp[21891+:32]=host_owner_req_cookie;
assign f_sp[21923+:32]=host_owner_req_node;
assign f_sp[21955+:32]=host_owner_req_net;
assign f_sp[21987+:2333]=0;
assign host_owner_rsp_status=f_srp[2304+:4];
assign host_owner_rsp_cookie=f_srp[2308+:32];
assign host_owner_rsp_count=f_srp[2340+:32];
assign host_owner_rsp_occupancy=f_srp[2372+:32];
assign host_owner_rsp_will_overuse=f_srp[2404+:1];


assign f_sv[10]=cc_req_valid;assign cc_req_ready=f_sr[10];assign cc_rsp_valid=f_srv[10];assign f_srr[10]=cc_rsp_ready;
assign f_sp[24320+:128]=cc_req_words;
assign f_sp[24448+:32]=cc_req_cookie;
assign f_sp[24480+:32]=cc_req_version;
assign f_sp[24512+:64]=cc_req_design_id;
assign f_sp[24576+:2]=cc_req_query;
assign f_sp[24578+:4]=cc_req_price;
assign f_sp[24582+:2170]=0;
assign cc_rsp_words=f_srp[2560+:64];
assign cc_rsp_cookie=f_srp[2624+:32];
assign cc_rsp_version=f_srp[2656+:32];
assign cc_rsp_design_id=f_srp[2688+:64];
assign cc_rsp_query=f_srp[2752+:2];
assign cc_rsp_status=f_srp[2754+:2];
assign cc_rsp_price=f_srp[2756+:4];


assign f_sv[11]=expand_valid;assign expand_ready=f_sr[11];assign result_valid=f_srv[11];assign f_srr[11]=result_ready;
assign f_sp[26752+:32]=expand_connection;
assign f_sp[26784+:32]=expand_cookie;
assign f_sp[26816+:32]=expand_parent;
assign f_sp[26848+:32]=expand_prune;
assign f_sp[26880+:32]=expand_has_laguna;
assign f_sp[26912+:32]=expand_sink;
assign f_sp[26944+:32]=expand_net;
assign f_sp[26976+:32]=expand_sequence;
assign f_sp[27008+:32]=expand_flags;
assign f_sp[27040+:32]=expand_xmin;
assign f_sp[27072+:32]=expand_xmax;
assign f_sp[27104+:32]=expand_ymin;
assign f_sp[27136+:32]=expand_ymax;
assign f_sp[27168+:32]=expand_version;
assign f_sp[27200+:1984]=0;
assign result_status=f_srp[2816+:4];
assign result_cookie=f_srp[2820+:32];
assign result_count=f_srp[2852+:32];
assign result_expanded_count=f_srp[2884+:32];
assign result_raw_count=f_srp[2916+:32];
assign result_mask=f_srp[2948+:32];
assign result_hit=f_srp[2980+:1];
assign result_early=f_srp[2981+:1];


assign f_sv[12]=seed_valid;assign seed_ready=f_sr[12];assign seed_rsp_valid=f_srv[12];assign f_srr[12]=seed_rsp_ready;
assign f_sp[29184+:32]=seed_op;
assign f_sp[29216+:32]=seed_key;
assign f_sp[29248+:32]=seed_id;
assign f_sp[29280+:32]=seed_cookie;
assign f_sp[29312+:32]=seed_version;
assign f_sp[29344+:2272]=0;
assign seed_rsp_status=f_srp[3072+:32];
assign seed_rsp_cookie=f_srp[3104+:32];
assign seed_rsp_size=f_srp[3136+:32];
assign seed_rsp_key=f_srp[3168+:32];
assign seed_rsp_id=f_srp[3200+:32];


assign f_sv[13]=cs_req_valid;assign cs_req_ready=f_sr[13];assign cs_rsp_valid=f_srv[13];assign f_srr[13]=cs_rsp_ready;
assign f_sp[31616+:1]=cs_req_host;
assign f_sp[31617+:3]=cs_req_op;
assign f_sp[31620+:32]=cs_req_cookie;
assign f_sp[31652+:32]=cs_req_index;
assign f_sp[31684+:32]=cs_req_value;
assign f_sp[31716+:32]=cs_req_version;
assign f_sp[31748+:2]=cs_req_query;
assign f_sp[31750+:4]=cs_req_price;
assign f_sp[31754+:2294]=0;
assign cs_rsp_status=f_srp[3328+:4];
assign cs_rsp_cookie=f_srp[3332+:32];
assign cs_rsp_index=f_srp[3364+:32];
assign cs_rsp_version=f_srp[3396+:32];
assign cs_rsp_op=f_srp[3428+:3];
assign cs_rsp_host=f_srp[3431+:1];
assign cs_rsp_query=f_srp[3432+:2];
assign cs_rsp_price=f_srp[3434+:4];
assign cs_rsp_data=f_srp[3438+:128];


assign f_sv[14]=k_cfg_valid;assign k_cfg_ready=f_sr[14];assign k_cfg_rsp_valid=f_srv[14];assign f_srr[14]=k_cfg_rsp_ready;
assign f_sp[34048+:1]=1'b1;
assign f_sp[34049+:64]=design_id;
assign f_sp[34113+:32]=k_checkpoint;
assign f_sp[34145+:32]=k_cfg_version;
assign f_sp[34177+:2]=k_cfg_query;
assign f_sp[34179+:4]=k_cfg_price;
assign f_sp[34183+:2297]=0;
assign k_cfg_status=f_srp[3584+:1];


assign f_sv[15]=cf_load_valid;assign cf_load_ready=f_sr[15];assign cf_load_rsp_valid=f_srv[15];assign f_srr[15]=cf_load_rsp_ready;
assign f_sp[36480+:2304]=cf_input;
assign f_sp[38784+:64]=k_saved_design;
assign f_sp[38848+:32]=k_saved_checkpoint;
assign f_sp[38880+:1]=1'b1;
assign f_sp[38881+:31]=0;
assign cf_load_status=f_srp[3840+:1];











































wire[4:0]f_watch_idle,f_watch_fault;






assign f_route_payload={30'd0,rc_req_sequence,32'd2717,rc_req_sink,32'd65185,rc_req_cookie,rc_req_slot,rc_req_op};


integer f_last_progress=0;
integer f_conflict_cycles=0;
always @(posedge clk)if(!k_cold_rst)begin
 if(f_recovery_owned&&f_sv==16'hffff&&rc_req_valid)f_conflict_cycles<=f_conflict_cycles+1;
 if((|(f_dv&f_dr))||(|(f_drv&f_drr))||k_target_reset||f_broute_valid&&f_broute_ready||f_broute_rsp_valid&&f_broute_rsp_ready)f_last_progress<=cycles;
 if(!injection_seen&&cycles-f_last_progress>131072)$fatal(1,"fabric no progress phase=%0d drained=%b idle=%b center=%b prefetch=%b post=%b frontier=%b core=%b cc=%b",f_phase,f_all_drained,f_backend_idle,system.inner.backend.dut.center_retired_idle,system.inner.backend.dut.prefetch_retired_idle,system.inner.backend.dut.post_retired_idle,system.inner.backend.dut.frontier_retired_idle,system.inner.backend.dut.core_busy,cc_busy);
 if(f_fault||(|f_watch_fault))$fatal(1,"unified fabric/transport fault");
 if((f_recovery_owned||f_phase==4||f_phase==5)&&(f_sr!=0||rc_req_ready))$fatal(1,"recovery host/route admission leak");
 if(k_target_reset&&(!f_recovery_owned||!f_normal_retired))$fatal(1,"target reset outside retired ownership");
 for(integer fx=0;fx<16;fx=fx+1)begin
  if(system.inner.backend.f_sv[fx]&&system.inner.backend.f_sr[fx])$fdisplay(trace,"FS %0d %0d %0608h",cycles,fx,system.inner.backend.f_sp[fx*2432+:2432]);
  if(f_dv[fx]&&f_dr[fx])$fdisplay(trace,"FD %0d %0d %0d %0608h",cycles,f_phase,fx,f_dp[fx*2432+:2432]);
  if(f_drv[fx]&&f_drr[fx])$fdisplay(trace,"FB %0d %0d %0d",cycles,f_phase,fx);
 end
 if(system.inner.backend.rc_req_valid&&system.inner.backend.rc_req_ready)$fdisplay(trace,"FR %0d",cycles);
 if(k_rec_valid&&k_rec_ready)$fdisplay(trace,"FK %0d",cycles);
end

task route_command(input integer op,slot,sink,sequence_id);begin
 @(negedge clk);rc_req_op=op;rc_req_slot=slot;rc_req_sink=sink;rc_req_sequence=sequence_id;rc_req_cookie=32'hf0000000+route_commands;rc_req_valid=1;
 do @(posedge clk);while(!rc_req_ready);@(negedge clk);rc_req_valid=0;
 host_ctrl_valid=1;
 host_design_req_valid=1;
 expand_valid=1;
 seed_valid=1;
 q_cfg_valid=1;
 g_cfg_valid=1;
 d_cfg_valid=1;
 t_cfg_valid=1;
 owner_cfg_valid=1;
 cs_cfg_valid=1;
 host_io_valid=1;
 host_owner_req_valid=1;

 wait(rc_rsp_valid);@(negedge clk);
 if(rc_rsp_status||rc_rsp_cookie!=32'hf0000000+route_commands||rc_rsp_nodes!=6||rc_rsp_acked!=6||rc_fault)$fatal(1,"route controller result");
 repeat(5)begin @(negedge clk);if(!rc_rsp_valid||!rc_block||host_io_ready||host_owner_req_ready)$fatal(1,"route response fence");end

 host_ctrl_valid=0;
 host_design_req_valid=0;
 expand_valid=0;
 seed_valid=0;
 q_cfg_valid=0;
 g_cfg_valid=0;
 d_cfg_valid=0;
 t_cfg_valid=0;
 owner_cfg_valid=0;
 cs_cfg_valid=0;
 host_io_valid=0;
 host_owner_req_valid=0;

 rc_rsp_ready=1;@(negedge clk);rc_rsp_ready=0;wait(!rc_block);@(negedge clk);
end endtask

query_residency_system #(.SLOTS(SLOTS),.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS),.ENABLE_TEST_INJECTION(0))system(.qc_cmd_valid(qc_cmd_valid),.qc_cmd_ready(qc_cmd_ready),.qc_cmd_slot(qc_cmd_slot),.qc_cmd_cookie(qc_cmd_cookie),.qc_cmd_route_cookie(qc_cmd_route_cookie),.qc_cmd_source(qc_cmd_source),.qc_cmd_key(qc_cmd_key),.qc_cmd_nodes(qc_cmd_nodes),.qc_cmd_max_polls(qc_cmd_max_polls),.qc_cmd_poll_cookie(qc_cmd_poll_cookie),.qc_cmd_design(qc_cmd_design),.qc_cmd_query(qc_cmd_query),.qc_cmd_price(qc_cmd_price),.qc_cmd_expand(qc_cmd_expand),.qc_rsp_valid(qc_rsp_valid),.qc_rsp_ready(qc_rsp_ready),.qc_rsp_status(qc_rsp_status),.qc_rsp_detail(qc_rsp_detail),.qc_rsp_cookie(qc_rsp_cookie),.qc_rsp_nodes(qc_rsp_nodes),.qc_rsp_acked(qc_rsp_acked),.qc_rsp_committed(qc_rsp_committed),.qc_abort(qc_abort),.qc_busy(qc_busy),.qc_fault(qc_fault),.qc_phase(qc_phase),.qc_prepared_event(qc_prepared_event),.qc_prepare_acked(qc_prepare_acked),.qc_cleanup_acked(qc_cleanup_acked),.ss_start_ready(ss_start_ready),.ss_rsp_valid(ss_rsp_valid),.ss_rsp_status(ss_rsp_status),.ss_rsp_cookie(ss_rsp_cookie),.ss_polls(ss_polls),.ss_expands(ss_expands),.ss_candidates(ss_candidates),.ss_result_node(ss_result_node),.ss_result_key(ss_result_key),.ss_busy(ss_busy),.ss_fault(ss_fault),.ss_phase(ss_phase),.ss_poll_event(ss_poll_event),.ss_poll_node(ss_poll_node),.ss_poll_key(ss_poll_key),.ss_poll_size(ss_poll_size),.abort(abort),.busy(busy),.cc_busy(cc_busy),.cc_fault(cc_fault),.cf_fault(cf_fault),.clk(clk),.cost_lease(cost_lease),.cs_busy(cs_busy),.cs_configured(cs_configured),.cs_design_id(cs_design_id),.cs_editing(cs_editing),.cs_fault(cs_fault),.cs_m_araddr(cs_m_araddr),.cs_m_arburst(cs_m_arburst),.cs_m_arid(cs_m_arid),.cs_m_arlen(cs_m_arlen),.cs_m_arready(cs_m_arready),.cs_m_arsize(cs_m_arsize),.cs_m_arvalid(cs_m_arvalid),.cs_m_awaddr(cs_m_awaddr),.cs_m_awburst(cs_m_awburst),.cs_m_awid(cs_m_awid),.cs_m_awlen(cs_m_awlen),.cs_m_awready(cs_m_awready),.cs_m_awsize(cs_m_awsize),.cs_m_awvalid(cs_m_awvalid),.cs_m_bid(cs_m_bid),.cs_m_bready(cs_m_bready),.cs_m_bresp(cs_m_bresp),.cs_m_bvalid(cs_m_bvalid),.cs_m_rdata(cs_m_rdata),.cs_m_rid(cs_m_rid),.cs_m_rlast(cs_m_rlast),.cs_m_rready(cs_m_rready),.cs_m_rresp(cs_m_rresp),.cs_m_rvalid(cs_m_rvalid),.cs_m_wdata(cs_m_wdata),.cs_m_wlast(cs_m_wlast),.cs_m_wready(cs_m_wready),.cs_m_wstrb(cs_m_wstrb),.cs_m_wvalid(cs_m_wvalid),.cs_published_version(cs_published_version),.cs_ready_for_query(cs_ready_for_query),.d_configured(d_configured),.d_m_araddr(d_m_araddr),.d_m_arburst(d_m_arburst),.d_m_arid(d_m_arid),.d_m_arlen(d_m_arlen),.d_m_arready(d_m_arready),.d_m_arsize(d_m_arsize),.d_m_arvalid(d_m_arvalid),.d_m_awaddr(d_m_awaddr),.d_m_awburst(d_m_awburst),.d_m_awid(d_m_awid),.d_m_awlen(d_m_awlen),.d_m_awready(d_m_awready),.d_m_awsize(d_m_awsize),.d_m_awvalid(d_m_awvalid),.d_m_bid(d_m_bid),.d_m_bready(d_m_bready),.d_m_bresp(d_m_bresp),.d_m_bvalid(d_m_bvalid),.d_m_rdata(d_m_rdata),.d_m_rid(d_m_rid),.d_m_rlast(d_m_rlast),.d_m_rready(d_m_rready),.d_m_rresp(d_m_rresp),.d_m_rvalid(d_m_rvalid),.d_m_wdata(d_m_wdata),.d_m_wlast(d_m_wlast),.d_m_wready(d_m_wready),.d_m_wstrb(d_m_wstrb),.d_m_wvalid(d_m_wvalid),.design_id(design_id),.f_all_drained(f_all_drained),.f_backend_idle(f_backend_idle),.f_fault(f_fault),.f_normal_retired(f_normal_retired),.f_phase(f_phase),.f_recovery_owned(f_recovery_owned),.f_route_payload(f_route_payload),.f_sp(f_sp),.f_sr(f_sr),.f_srp(f_srp),.f_srr(f_srr),.f_srv(f_srv),.f_sv(f_sv),.fault(fault),.g_configured(g_configured),.g_m_araddr(g_m_araddr),.g_m_arburst(g_m_arburst),.g_m_arid(g_m_arid),.g_m_arlen(g_m_arlen),.g_m_arready(g_m_arready),.g_m_arsize(g_m_arsize),.g_m_arvalid(g_m_arvalid),.g_m_rdata(g_m_rdata),.g_m_rid(g_m_rid),.g_m_rlast(g_m_rlast),.g_m_rready(g_m_rready),.g_m_rresp(g_m_rresp),.g_m_rvalid(g_m_rvalid),.k_a_checkpoint(k_a_checkpoint),.k_a_cookie(k_a_cookie),.k_a_design(k_a_design),.k_a_net(k_a_net),.k_a_node(k_a_node),.k_a_occ(k_a_occ),.k_a_ready(k_a_ready),.k_a_refs(k_a_refs),.k_a_rsp_checkpoint(k_a_rsp_checkpoint),.k_a_rsp_cookie(k_a_rsp_cookie),.k_a_rsp_design(k_a_rsp_design),.k_a_rsp_ready(k_a_rsp_ready),.k_a_rsp_valid(k_a_rsp_valid),.k_a_status(k_a_status),.k_a_valid(k_a_valid),.k_busy(k_busy),.k_cold_rst(k_cold_rst),.k_corrected(k_corrected),.k_count(k_count),.k_fault(k_fault),.k_full(k_full),.k_permit(k_permit),.k_rec_ready(k_rec_ready),.k_rec_valid(k_rec_valid),.k_rsp_cookie(k_rsp_cookie),.k_rsp_ready(k_rsp_ready),.k_rsp_status(k_rsp_status),.k_rsp_valid(k_rsp_valid),.k_saved_checkpoint(k_saved_checkpoint),.k_saved_design(k_saved_design),.k_target_reset(k_target_reset),.lr_fault(lr_fault),.lr_rsp_status(lr_rsp_status),.lr_s_cookie(stream_cookie),.lr_s_last(lr_s_last),.lr_s_node(lr_s_node),.lr_s_payload(lr_s_payload),.lr_s_ready(lr_s_ready),.lr_s_valid(lr_s_valid),.lr_verified(lr_verified),.lr_written(lr_written),.operation_pending(operation_pending),.out_action(out_action),.out_attrs(out_attrs),.out_bits(out_bits),.out_commit_acked(out_commit_acked),.out_commit_payload(out_commit_payload),.out_commit_status(out_commit_status),.out_commit_valid(out_commit_valid),.out_config(out_config),.out_connection(out_connection),.out_cookie(out_cookie),.out_cost_geometry(out_cost_geometry),.out_cost_geometry_result(out_cost_geometry_result),.out_cost_packet(out_cost_packet),.out_cost_status(out_cost_status),.out_cost_valid(out_cost_valid),.out_cost_words(out_cost_words),.out_node(out_node),.out_offer_before(out_offer_before),.out_offer_key(out_offer_key),.out_offer_node(out_offer_node),.out_offer_size(out_offer_size),.out_offer_status(out_offer_status),.out_offer_valid(out_offer_valid),.out_params(out_params),.out_params_valid(out_params_valid),.out_position(out_position),.out_post_attrs(out_post_attrs),.out_post_distance(out_post_distance),.out_post_prev_read(out_post_prev_read),.out_post_status(out_post_status),.out_post_upstream(out_post_upstream),.out_post_valid(out_post_valid),.out_post_x(out_post_x),.out_post_y(out_post_y),.out_prep_count(out_prep_count),.out_prep_history(out_prep_history),.out_prep_net_data(out_prep_net_data),.out_prep_occupancy(out_prep_occupancy),.out_prep_price_index(out_prep_price_index),.out_prep_price_value(out_prep_price_value),.out_prep_status(out_prep_status),.out_prep_valid(out_prep_valid),.out_profile_revision(out_profile_revision),.out_ready(out_ready),.out_sequence(out_sequence),.out_services(out_services),.out_steps(out_steps),.out_valid(out_valid),.owner_configured(owner_configured),.owner_m_araddr(owner_m_araddr),.owner_m_arburst(owner_m_arburst),.owner_m_arid(owner_m_arid),.owner_m_arlen(owner_m_arlen),.owner_m_arready(owner_m_arready),.owner_m_arsize(owner_m_arsize),.owner_m_arvalid(owner_m_arvalid),.owner_m_awaddr(owner_m_awaddr),.owner_m_awburst(owner_m_awburst),.owner_m_awid(owner_m_awid),.owner_m_awlen(owner_m_awlen),.owner_m_awready(owner_m_awready),.owner_m_awsize(owner_m_awsize),.owner_m_awvalid(owner_m_awvalid),.owner_m_bid(owner_m_bid),.owner_m_bready(owner_m_bready),.owner_m_bresp(owner_m_bresp),.owner_m_bvalid(owner_m_bvalid),.owner_m_rdata(owner_m_rdata),.owner_m_rid(owner_m_rid),.owner_m_rlast(owner_m_rlast),.owner_m_rready(owner_m_rready),.owner_m_rresp(owner_m_rresp),.owner_m_rvalid(owner_m_rvalid),.owner_m_wdata(owner_m_wdata),.owner_m_wlast(owner_m_wlast),.owner_m_wready(owner_m_wready),.owner_m_wstrb(owner_m_wstrb),.owner_m_wvalid(owner_m_wvalid),.p_active(p_active),.p_active_price(p_active_price),.p_active_query(p_active_query),.p_m_araddr(p_m_araddr),.p_m_arburst(p_m_arburst),.p_m_arid(p_m_arid),.p_m_arlen(p_m_arlen),.p_m_arready(p_m_arready),.p_m_arsize(p_m_arsize),.p_m_arvalid(p_m_arvalid),.p_m_awaddr(p_m_awaddr),.p_m_awburst(p_m_awburst),.p_m_awid(p_m_awid),.p_m_awlen(p_m_awlen),.p_m_awready(p_m_awready),.p_m_awsize(p_m_awsize),.p_m_awvalid(p_m_awvalid),.p_m_bid(p_m_bid),.p_m_bready(p_m_bready),.p_m_bresp(p_m_bresp),.p_m_bvalid(p_m_bvalid),.p_m_rdata(p_m_rdata),.p_m_rid(p_m_rid),.p_m_rlast(p_m_rlast),.p_m_rready(p_m_rready),.p_m_rresp(p_m_rresp),.p_m_rvalid(p_m_rvalid),.p_m_wdata(p_m_wdata),.p_m_wlast(p_m_wlast),.p_m_wready(p_m_wready),.p_m_wstrb(p_m_wstrb),.p_m_wvalid(p_m_wvalid),.q_busy(q_busy),.q_configured(q_configured),.q_fault(q_fault),.q_m_araddr(q_m_araddr),.q_m_arburst(q_m_arburst),.q_m_arid(q_m_arid),.q_m_arlen(q_m_arlen),.q_m_arready(q_m_arready),.q_m_arsize(q_m_arsize),.q_m_arvalid(q_m_arvalid),.q_m_rdata(q_m_rdata),.q_m_rid(q_m_rid),.q_m_rlast(q_m_rlast),.q_m_rready(q_m_rready),.q_m_rresp(q_m_rresp),.q_m_rvalid(q_m_rvalid),.query_ready(query_ready),.query_version(query_version),.rc_block(rc_block),.rc_busy(rc_busy),.rc_fault(rc_fault),.rc_req_ready(rc_req_ready),.rc_req_valid(rc_req_valid),.rc_rsp_acked(rc_rsp_acked),.rc_rsp_cookie(rc_rsp_cookie),.rc_rsp_nodes(rc_rsp_nodes),.rc_rsp_ready(rc_rsp_ready),.rc_rsp_status(rc_rsp_status),.rc_rsp_valid(rc_rsp_valid),.rc_slots(rc_slots),.recover_checkpoint(32'd17),.recover_cookie(retry_cookie),.recover_design(design_id),.recover_price(retry_price),.recover_query(retry_query),.recover_version(retry_version),.rst(rst),.snapshot_checkpoint(32'd17),.snapshot_cookie(stream_cookie),.snapshot_count(32'd328),.snapshot_design(design_id),.snapshot_nodes(32'd9089009),.snapshot_probe(32'd150697),.t_configured(t_configured),.t_m_araddr(t_m_araddr),.t_m_arburst(t_m_arburst),.t_m_arid(t_m_arid),.t_m_arlen(t_m_arlen),.t_m_arready(t_m_arready),.t_m_arsize(t_m_arsize),.t_m_arvalid(t_m_arvalid),.t_m_rdata(t_m_rdata),.t_m_rid(t_m_rid),.t_m_rlast(t_m_rlast),.t_m_rready(t_m_rready),.t_m_rresp(t_m_rresp),.t_m_rvalid(t_m_rvalid),.test_route_abort(injected_abort),.test_route_version_flip(injected_drift));

assign b_l_field=system.inner.backend.b_l_field;
assign b_l_node=system.inner.backend.b_l_node;
assign b_l_payload=system.inner.backend.b_l_payload;
assign b_l_present=system.inner.backend.b_l_present;
assign b_l_ready=system.inner.backend.b_l_ready;
assign b_l_rsp_ready=system.inner.backend.b_l_rsp_ready;
assign b_l_rsp_valid=system.inner.backend.b_l_rsp_valid;
assign b_l_status=system.inner.backend.b_l_status;
assign b_l_valid=system.inner.backend.b_l_valid;
assign b_l_value=system.inner.backend.b_l_value;
assign b_l_write=system.inner.backend.b_l_write;
assign b_o_cookie=system.inner.backend.b_o_cookie;
assign b_o_count=system.inner.backend.b_o_count;
assign b_o_net=system.inner.backend.b_o_net;
assign b_o_node=system.inner.backend.b_o_node;
assign b_o_occupancy=system.inner.backend.b_o_occupancy;
assign b_o_op=system.inner.backend.b_o_op;
assign b_o_ready=system.inner.backend.b_o_ready;
assign b_o_rsp_cookie=system.inner.backend.b_o_rsp_cookie;
assign b_o_rsp_ready=system.inner.backend.b_o_rsp_ready;
assign b_o_rsp_valid=system.inner.backend.b_o_rsp_valid;
assign b_o_status=system.inner.backend.b_o_status;
assign b_o_valid=system.inner.backend.b_o_valid;
assign b_o_will_overuse=system.inner.backend.b_o_will_overuse;
assign cf_busy=system.inner.backend.cf_busy;
assign cf_payload=system.inner.backend.cf_payload;
assign cf_ready=system.inner.backend.cf_ready;
assign cf_replies=system.inner.backend.cf_replies;
assign cf_reply_ready=system.inner.backend.cf_reply_ready;
assign cf_retired=system.inner.backend.cf_retired;
assign cf_rsp_cookie=system.inner.backend.cf_rsp_cookie;
assign cf_rsp_status=system.inner.backend.cf_rsp_status;
assign cf_rsp_valid=system.inner.backend.cf_rsp_valid;
assign cf_saved_checkpoint=system.inner.backend.cf_saved_checkpoint;
assign cf_saved_design=system.inner.backend.cf_saved_design;
assign cf_sent=system.inner.backend.cf_sent;
assign cf_status=system.inner.backend.cf_status;
assign cf_valid=system.inner.backend.cf_valid;
assign f_brecover_ready=system.inner.backend.f_brecover_ready;
assign f_brecover_rsp_ready=system.inner.backend.f_brecover_rsp_ready;
assign f_brecover_rsp_valid=system.inner.backend.f_brecover_rsp_valid;
assign f_brecover_valid=system.inner.backend.f_brecover_valid;
assign f_broute_payload=system.inner.backend.f_broute_payload;
assign f_broute_ready=system.inner.backend.f_broute_ready;
assign f_broute_rsp_ready=system.inner.backend.f_broute_rsp_ready;
assign f_broute_rsp_valid=system.inner.backend.f_broute_rsp_valid;
assign f_broute_valid=system.inner.backend.f_broute_valid;
assign f_cbp=system.inner.backend.f_cbp;
assign f_cbr=system.inner.backend.f_cbr;
assign f_cbrp=system.inner.backend.f_cbrp;
assign f_cbrr=system.inner.backend.f_cbrr;
assign f_cbrv=system.inner.backend.f_cbrv;
assign f_cbv=system.inner.backend.f_cbv;
assign f_dp=system.inner.backend.f_dp;
assign f_dr=system.inner.backend.f_dr;
assign f_drp=system.inner.backend.f_drp;
assign f_drr=system.inner.backend.f_drr;
assign f_drv=system.inner.backend.f_drv;
assign f_dv=system.inner.backend.f_dv;
assign f_pending=system.inner.backend.f_pending;
assign f_watch_fault=system.inner.backend.f_watch_fault;
assign f_watch_idle=system.inner.backend.f_watch_idle;
assign fd_cc_req_cookie=system.inner.backend.fd_cc_req_cookie;
assign fd_cc_req_design_id=system.inner.backend.fd_cc_req_design_id;
assign fd_cc_req_price=system.inner.backend.fd_cc_req_price;
assign fd_cc_req_query=system.inner.backend.fd_cc_req_query;
assign fd_cc_req_ready=system.inner.backend.fd_cc_req_ready;
assign fd_cc_req_valid=system.inner.backend.fd_cc_req_valid;
assign fd_cc_req_version=system.inner.backend.fd_cc_req_version;
assign fd_cc_req_words=system.inner.backend.fd_cc_req_words;
assign fd_cc_rsp_cookie=system.inner.backend.fd_cc_rsp_cookie;
assign fd_cc_rsp_design_id=system.inner.backend.fd_cc_rsp_design_id;
assign fd_cc_rsp_price=system.inner.backend.fd_cc_rsp_price;
assign fd_cc_rsp_query=system.inner.backend.fd_cc_rsp_query;
assign fd_cc_rsp_ready=system.inner.backend.fd_cc_rsp_ready;
assign fd_cc_rsp_status=system.inner.backend.fd_cc_rsp_status;
assign fd_cc_rsp_valid=system.inner.backend.fd_cc_rsp_valid;
assign fd_cc_rsp_version=system.inner.backend.fd_cc_rsp_version;
assign fd_cc_rsp_words=system.inner.backend.fd_cc_rsp_words;
assign fd_cf_load_ready=system.inner.backend.fd_cf_load_ready;
assign fd_cf_load_rsp_ready=system.inner.backend.fd_cf_load_rsp_ready;
assign fd_cf_load_rsp_valid=system.inner.backend.fd_cf_load_rsp_valid;
assign fd_cf_load_status=system.inner.backend.fd_cf_load_status;
assign fd_cf_load_valid=system.inner.backend.fd_cf_load_valid;
assign fd_cs_cfg_design_id=system.inner.backend.fd_cs_cfg_design_id;
assign fd_cs_cfg_history=system.inner.backend.fd_cs_cfg_history;
assign fd_cs_cfg_net_count=system.inner.backend.fd_cs_cfg_net_count;
assign fd_cs_cfg_nets=system.inner.backend.fd_cs_cfg_nets;
assign fd_cs_cfg_nodes=system.inner.backend.fd_cs_cfg_nodes;
assign fd_cs_cfg_prices=system.inner.backend.fd_cs_cfg_prices;
assign fd_cs_cfg_ready=system.inner.backend.fd_cs_cfg_ready;
assign fd_cs_cfg_rsp_ready=system.inner.backend.fd_cs_cfg_rsp_ready;
assign fd_cs_cfg_rsp_valid=system.inner.backend.fd_cs_cfg_rsp_valid;
assign fd_cs_cfg_status=system.inner.backend.fd_cs_cfg_status;
assign fd_cs_cfg_valid=system.inner.backend.fd_cs_cfg_valid;
assign fd_cs_cfg_version=system.inner.backend.fd_cs_cfg_version;
assign fd_cs_req_cookie=system.inner.backend.fd_cs_req_cookie;
assign fd_cs_req_host=system.inner.backend.fd_cs_req_host;
assign fd_cs_req_index=system.inner.backend.fd_cs_req_index;
assign fd_cs_req_op=system.inner.backend.fd_cs_req_op;
assign fd_cs_req_price=system.inner.backend.fd_cs_req_price;
assign fd_cs_req_query=system.inner.backend.fd_cs_req_query;
assign fd_cs_req_ready=system.inner.backend.fd_cs_req_ready;
assign fd_cs_req_valid=system.inner.backend.fd_cs_req_valid;
assign fd_cs_req_value=system.inner.backend.fd_cs_req_value;
assign fd_cs_req_version=system.inner.backend.fd_cs_req_version;
assign fd_cs_rsp_cookie=system.inner.backend.fd_cs_rsp_cookie;
assign fd_cs_rsp_data=system.inner.backend.fd_cs_rsp_data;
assign fd_cs_rsp_host=system.inner.backend.fd_cs_rsp_host;
assign fd_cs_rsp_index=system.inner.backend.fd_cs_rsp_index;
assign fd_cs_rsp_op=system.inner.backend.fd_cs_rsp_op;
assign fd_cs_rsp_price=system.inner.backend.fd_cs_rsp_price;
assign fd_cs_rsp_query=system.inner.backend.fd_cs_rsp_query;
assign fd_cs_rsp_ready=system.inner.backend.fd_cs_rsp_ready;
assign fd_cs_rsp_status=system.inner.backend.fd_cs_rsp_status;
assign fd_cs_rsp_valid=system.inner.backend.fd_cs_rsp_valid;
assign fd_cs_rsp_version=system.inner.backend.fd_cs_rsp_version;
assign fd_d_cfg_base=system.inner.backend.fd_d_cfg_base;
assign fd_d_cfg_nodes=system.inner.backend.fd_d_cfg_nodes;
assign fd_d_cfg_ready=system.inner.backend.fd_d_cfg_ready;
assign fd_d_cfg_rsp_ready=system.inner.backend.fd_d_cfg_rsp_ready;
assign fd_d_cfg_rsp_valid=system.inner.backend.fd_d_cfg_rsp_valid;
assign fd_d_cfg_status=system.inner.backend.fd_d_cfg_status;
assign fd_d_cfg_valid=system.inner.backend.fd_d_cfg_valid;
assign fd_expand_connection=system.inner.backend.fd_expand_connection;
assign fd_expand_cookie=system.inner.backend.fd_expand_cookie;
assign fd_expand_flags=system.inner.backend.fd_expand_flags;
assign fd_expand_has_laguna=system.inner.backend.fd_expand_has_laguna;
assign fd_expand_net=system.inner.backend.fd_expand_net;
assign fd_expand_parent=system.inner.backend.fd_expand_parent;
assign fd_expand_prune=system.inner.backend.fd_expand_prune;
assign fd_expand_ready=system.inner.backend.fd_expand_ready;
assign fd_expand_sequence=system.inner.backend.fd_expand_sequence;
assign fd_expand_sink=system.inner.backend.fd_expand_sink;
assign fd_expand_valid=system.inner.backend.fd_expand_valid;
assign fd_expand_version=system.inner.backend.fd_expand_version;
assign fd_expand_xmax=system.inner.backend.fd_expand_xmax;
assign fd_expand_xmin=system.inner.backend.fd_expand_xmin;
assign fd_expand_ymax=system.inner.backend.fd_expand_ymax;
assign fd_expand_ymin=system.inner.backend.fd_expand_ymin;
assign fd_fa_authoritative=system.inner.backend.fd_fa_authoritative;
assign fd_fa_checkpoint=system.inner.backend.fd_fa_checkpoint;
assign fd_fa_design=system.inner.backend.fd_fa_design;
assign fd_fa_price=system.inner.backend.fd_fa_price;
assign fd_fa_query=system.inner.backend.fd_fa_query;
assign fd_fa_version=system.inner.backend.fd_fa_version;
assign fd_fc_authoritative=system.inner.backend.fd_fc_authoritative;
assign fd_fc_checkpoint=system.inner.backend.fd_fc_checkpoint;
assign fd_fc_design=system.inner.backend.fd_fc_design;
assign fd_fc_payload=system.inner.backend.fd_fc_payload;
assign fd_g_cfg_attrs_base=system.inner.backend.fd_g_cfg_attrs_base;
assign fd_g_cfg_edges=system.inner.backend.fd_g_cfg_edges;
assign fd_g_cfg_edges_base=system.inner.backend.fd_g_cfg_edges_base;
assign fd_g_cfg_nodes=system.inner.backend.fd_g_cfg_nodes;
assign fd_g_cfg_offsets_base=system.inner.backend.fd_g_cfg_offsets_base;
assign fd_g_cfg_ready=system.inner.backend.fd_g_cfg_ready;
assign fd_g_cfg_rsp_ready=system.inner.backend.fd_g_cfg_rsp_ready;
assign fd_g_cfg_rsp_valid=system.inner.backend.fd_g_cfg_rsp_valid;
assign fd_g_cfg_status=system.inner.backend.fd_g_cfg_status;
assign fd_g_cfg_valid=system.inner.backend.fd_g_cfg_valid;
assign fd_host_ctrl_op=system.inner.backend.fd_host_ctrl_op;
assign fd_host_ctrl_price=system.inner.backend.fd_host_ctrl_price;
assign fd_host_ctrl_query=system.inner.backend.fd_host_ctrl_query;
assign fd_host_ctrl_ready=system.inner.backend.fd_host_ctrl_ready;
assign fd_host_ctrl_rsp_ready=system.inner.backend.fd_host_ctrl_rsp_ready;
assign fd_host_ctrl_rsp_valid=system.inner.backend.fd_host_ctrl_rsp_valid;
assign fd_host_ctrl_status=system.inner.backend.fd_host_ctrl_status;
assign fd_host_ctrl_valid=system.inner.backend.fd_host_ctrl_valid;
assign fd_host_ctrl_version=system.inner.backend.fd_host_ctrl_version;
assign fd_host_design_req_arg=system.inner.backend.fd_host_design_req_arg;
assign fd_host_design_req_cookie=system.inner.backend.fd_host_design_req_cookie;
assign fd_host_design_req_node=system.inner.backend.fd_host_design_req_node;
assign fd_host_design_req_op=system.inner.backend.fd_host_design_req_op;
assign fd_host_design_req_owner=system.inner.backend.fd_host_design_req_owner;
assign fd_host_design_req_ready=system.inner.backend.fd_host_design_req_ready;
assign fd_host_design_req_valid=system.inner.backend.fd_host_design_req_valid;
assign fd_host_design_rsp_cookie=system.inner.backend.fd_host_design_rsp_cookie;
assign fd_host_design_rsp_count=system.inner.backend.fd_host_design_rsp_count;
assign fd_host_design_rsp_flags=system.inner.backend.fd_host_design_rsp_flags;
assign fd_host_design_rsp_mask=system.inner.backend.fd_host_design_rsp_mask;
assign fd_host_design_rsp_ready=system.inner.backend.fd_host_design_rsp_ready;
assign fd_host_design_rsp_status=system.inner.backend.fd_host_design_rsp_status;
assign fd_host_design_rsp_valid=system.inner.backend.fd_host_design_rsp_valid;
assign fd_host_io_field=system.inner.backend.fd_host_io_field;
assign fd_host_io_node=system.inner.backend.fd_host_io_node;
assign fd_host_io_payload=system.inner.backend.fd_host_io_payload;
assign fd_host_io_present=system.inner.backend.fd_host_io_present;
assign fd_host_io_ready=system.inner.backend.fd_host_io_ready;
assign fd_host_io_rsp_ready=system.inner.backend.fd_host_io_rsp_ready;
assign fd_host_io_rsp_valid=system.inner.backend.fd_host_io_rsp_valid;
assign fd_host_io_status=system.inner.backend.fd_host_io_status;
assign fd_host_io_valid=system.inner.backend.fd_host_io_valid;
assign fd_host_io_value=system.inner.backend.fd_host_io_value;
assign fd_host_io_write=system.inner.backend.fd_host_io_write;
assign fd_host_owner_req_cookie=system.inner.backend.fd_host_owner_req_cookie;
assign fd_host_owner_req_net=system.inner.backend.fd_host_owner_req_net;
assign fd_host_owner_req_node=system.inner.backend.fd_host_owner_req_node;
assign fd_host_owner_req_op=system.inner.backend.fd_host_owner_req_op;
assign fd_host_owner_req_ready=system.inner.backend.fd_host_owner_req_ready;
assign fd_host_owner_req_valid=system.inner.backend.fd_host_owner_req_valid;
assign fd_host_owner_rsp_cookie=system.inner.backend.fd_host_owner_rsp_cookie;
assign fd_host_owner_rsp_count=system.inner.backend.fd_host_owner_rsp_count;
assign fd_host_owner_rsp_occupancy=system.inner.backend.fd_host_owner_rsp_occupancy;
assign fd_host_owner_rsp_ready=system.inner.backend.fd_host_owner_rsp_ready;
assign fd_host_owner_rsp_status=system.inner.backend.fd_host_owner_rsp_status;
assign fd_host_owner_rsp_valid=system.inner.backend.fd_host_owner_rsp_valid;
assign fd_host_owner_rsp_will_overuse=system.inner.backend.fd_host_owner_rsp_will_overuse;
assign fd_k_cfg_ready=system.inner.backend.fd_k_cfg_ready;
assign fd_k_cfg_rsp_ready=system.inner.backend.fd_k_cfg_rsp_ready;
assign fd_k_cfg_rsp_valid=system.inner.backend.fd_k_cfg_rsp_valid;
assign fd_k_cfg_status=system.inner.backend.fd_k_cfg_status;
assign fd_k_cfg_valid=system.inner.backend.fd_k_cfg_valid;
assign fd_owner_cfg_allocator=system.inner.backend.fd_owner_cfg_allocator;
assign fd_owner_cfg_capacity=system.inner.backend.fd_owner_cfg_capacity;
assign fd_owner_cfg_nodes=system.inner.backend.fd_owner_cfg_nodes;
assign fd_owner_cfg_pool=system.inner.backend.fd_owner_cfg_pool;
assign fd_owner_cfg_primary=system.inner.backend.fd_owner_cfg_primary;
assign fd_owner_cfg_ready=system.inner.backend.fd_owner_cfg_ready;
assign fd_owner_cfg_rsp_ready=system.inner.backend.fd_owner_cfg_rsp_ready;
assign fd_owner_cfg_rsp_valid=system.inner.backend.fd_owner_cfg_rsp_valid;
assign fd_owner_cfg_status=system.inner.backend.fd_owner_cfg_status;
assign fd_owner_cfg_valid=system.inner.backend.fd_owner_cfg_valid;
assign fd_q_cfg_base=system.inner.backend.fd_q_cfg_base;
assign fd_q_cfg_connections=system.inner.backend.fd_q_cfg_connections;
assign fd_q_cfg_design=system.inner.backend.fd_q_cfg_design;
assign fd_q_cfg_nets=system.inner.backend.fd_q_cfg_nets;
assign fd_q_cfg_nodes=system.inner.backend.fd_q_cfg_nodes;
assign fd_q_cfg_ready=system.inner.backend.fd_q_cfg_ready;
assign fd_q_cfg_revision=system.inner.backend.fd_q_cfg_revision;
assign fd_q_cfg_rsp_ready=system.inner.backend.fd_q_cfg_rsp_ready;
assign fd_q_cfg_rsp_valid=system.inner.backend.fd_q_cfg_rsp_valid;
assign fd_q_cfg_status=system.inner.backend.fd_q_cfg_status;
assign fd_q_cfg_valid=system.inner.backend.fd_q_cfg_valid;
assign fd_result_cookie=system.inner.backend.fd_result_cookie;
assign fd_result_count=system.inner.backend.fd_result_count;
assign fd_result_early=system.inner.backend.fd_result_early;
assign fd_result_expanded_count=system.inner.backend.fd_result_expanded_count;
assign fd_result_hit=system.inner.backend.fd_result_hit;
assign fd_result_mask=system.inner.backend.fd_result_mask;
assign fd_result_raw_count=system.inner.backend.fd_result_raw_count;
assign fd_result_ready=system.inner.backend.fd_result_ready;
assign fd_result_status=system.inner.backend.fd_result_status;
assign fd_result_valid=system.inner.backend.fd_result_valid;
assign fd_seed_cookie=system.inner.backend.fd_seed_cookie;
assign fd_seed_id=system.inner.backend.fd_seed_id;
assign fd_seed_key=system.inner.backend.fd_seed_key;
assign fd_seed_op=system.inner.backend.fd_seed_op;
assign fd_seed_ready=system.inner.backend.fd_seed_ready;
assign fd_seed_rsp_cookie=system.inner.backend.fd_seed_rsp_cookie;
assign fd_seed_rsp_id=system.inner.backend.fd_seed_rsp_id;
assign fd_seed_rsp_key=system.inner.backend.fd_seed_rsp_key;
assign fd_seed_rsp_ready=system.inner.backend.fd_seed_rsp_ready;
assign fd_seed_rsp_size=system.inner.backend.fd_seed_rsp_size;
assign fd_seed_rsp_status=system.inner.backend.fd_seed_rsp_status;
assign fd_seed_rsp_valid=system.inner.backend.fd_seed_rsp_valid;
assign fd_seed_valid=system.inner.backend.fd_seed_valid;
assign fd_seed_version=system.inner.backend.fd_seed_version;
assign fd_t_cfg_columns=system.inner.backend.fd_t_cfg_columns;
assign fd_t_cfg_columns_base=system.inner.backend.fd_t_cfg_columns_base;
assign fd_t_cfg_ready=system.inner.backend.fd_t_cfg_ready;
assign fd_t_cfg_rows=system.inner.backend.fd_t_cfg_rows;
assign fd_t_cfg_rows_base=system.inner.backend.fd_t_cfg_rows_base;
assign fd_t_cfg_rsp_ready=system.inner.backend.fd_t_cfg_rsp_ready;
assign fd_t_cfg_rsp_valid=system.inner.backend.fd_t_cfg_rsp_valid;
assign fd_t_cfg_status=system.inner.backend.fd_t_cfg_status;
assign fd_t_cfg_valid=system.inner.backend.fd_t_cfg_valid;
assign k_j_net=system.inner.backend.k_j_net;
assign k_j_node=system.inner.backend.k_j_node;
assign k_j_op=system.inner.backend.k_j_op;
assign k_j_ready=system.inner.backend.k_j_ready;
assign k_j_valid=system.inner.backend.k_j_valid;
assign k_labels_done=system.inner.backend.k_labels_done;
assign k_labels_valid=system.inner.backend.k_labels_valid;
assign k_new_price=system.inner.backend.k_new_price;
assign k_new_query=system.inner.backend.k_new_query;
assign k_new_version=system.inner.backend.k_new_version;
assign k_o_cookie=system.inner.backend.k_o_cookie;
assign k_o_net=system.inner.backend.k_o_net;
assign k_o_node=system.inner.backend.k_o_node;
assign k_o_op=system.inner.backend.k_o_op;
assign k_o_ready=system.inner.backend.k_o_ready;
assign k_o_rsp_ready=system.inner.backend.k_o_rsp_ready;
assign k_o_rsp_valid=system.inner.backend.k_o_rsp_valid;
assign k_o_valid=system.inner.backend.k_o_valid;
assign k_rcfg_done=system.inner.backend.k_rcfg_done;
assign k_rcfg_valid=system.inner.backend.k_rcfg_valid;
assign label_drained=system.inner.backend.label_drained;
assign label_watch_fault=system.inner.backend.label_watch_fault;
assign lr_busy=system.inner.backend.lr_busy;
assign lr_c_op=system.inner.backend.lr_c_op;
assign lr_c_price=system.inner.backend.lr_c_price;
assign lr_c_query=system.inner.backend.lr_c_query;
assign lr_c_ready=system.inner.backend.lr_c_ready;
assign lr_c_rsp_ready=system.inner.backend.lr_c_rsp_ready;
assign lr_c_valid=system.inner.backend.lr_c_valid;
assign lr_c_version=system.inner.backend.lr_c_version;
assign lr_l_field=system.inner.backend.lr_l_field;
assign lr_l_node=system.inner.backend.lr_l_node;
assign lr_l_ready=system.inner.backend.lr_l_ready;
assign lr_l_rsp_ready=system.inner.backend.lr_l_rsp_ready;
assign lr_l_rsp_valid=system.inner.backend.lr_l_rsp_valid;
assign lr_l_valid=system.inner.backend.lr_l_valid;
assign lr_l_value=system.inner.backend.lr_l_value;
assign lr_l_write=system.inner.backend.lr_l_write;
assign lr_rsp_cookie=system.inner.backend.lr_rsp_cookie;
assign lr_rsp_ready=system.inner.backend.lr_rsp_ready;
assign lr_rsp_valid=system.inner.backend.lr_rsp_valid;
assign lr_start_ready=system.inner.backend.lr_start_ready;
assign lr_start_valid=system.inner.backend.lr_start_valid;
assign owner_drained=system.inner.backend.owner_drained;
assign owner_watch_fault=system.inner.backend.owner_watch_fault;
assign recover_open=system.inner.backend.recover_open;
always @(posedge clk)if(!rst&&ss_busy&&(!injection_seen||replayed))begin
 if(f_sr!=0||rc_req_ready||k_rec_ready)$fatal(1,"search host lease gap");
 if(ss_poll_event)begin
  poll_node=ss_poll_node;poll_key=ss_poll_key;poll_size=ss_poll_size;
  rc=$fscanf(polls_fd,"%d %d %d",cp_pnode,cp_pkey,cp_psize);
  if(rc!=3||poll_node!=cp_pnode||poll_key!==cp_pkey||poll_size!=cp_psize)$fatal(1,"autonomous poll CPU mismatch");
  $fdisplay(trace,"P %0d %0d %08h %0d",cycles,poll_node,poll_key,poll_size);poll_i=poll_i+1;
 end
 if(out_valid&&system.inner.b_out_ready)begin
     rc=$fscanf(candidates_fd,"%d %d %d %d %d",cp_parent,cp_child,cp_pos,cp_action,cp_target);
     if(rc!=5||system.inner.backend.dut.held_parent!=poll_node||cp_parent!=poll_node||out_node!=cp_child||out_action!=cp_action||out_sequence!=cp_pos||out_cookie!=100+expand_i)$fatal(1,"candidate mismatch index=%0d parent=%0d child=%0d action=%0d seq=%0d expected=%0d %0d %0d %0d",candidate_i,system.inner.backend.dut.held_parent,out_node,out_action,out_sequence,cp_parent,cp_child,cp_action,cp_pos);
     if(!out_params_valid||out_connection!=selected_connection||out_params[127:96]!=selected_sink||out_config[31:0]!=selected_sequence||out_config[351:320]!=38||out_config[383:352]!=46||out_config[415:384]!=283||out_config[447:416]!=295)$fatal(1,"natural State/config");
     if(out_action==1)begin
      rc=$fscanf(fd_gold,"%d %d",logical_parent,logical_child);if(rc!=2||logical_parent!=poll_node||logical_child!=out_node)$fatal(1,"cost identity");
      for(j=0;j<23;j=j+1)begin rc=$fscanf(fd_gold,"%h",word);if(rc!=1)$fatal(1,"packet word");gold_packet[j*32+:32]=word;end
      for(j=0;j<5;j=j+1)begin rc=$fscanf(fd_gold,"%h",word);if(rc!=1)$fatal(1,"cost word");gold_cost[j*32+:32]=word;end
      if(!out_cost_valid||out_cost_status||out_cost_packet!==gold_packet||out_cost_words!==gold_cost)$fatal(1,"natural cost index=%0d packet=%h expected=%h cost=%h expected=%h",candidate_i,out_cost_packet,gold_packet,out_cost_words,gold_cost);
      gold_label={32'(cp_target),selected_sequence,32'(poll_node),gold_cost[95:64],gold_cost[159:128]};
      if(!out_commit_valid||out_commit_status||out_commit_acked!=7||out_commit_payload!==gold_label)$fatal(1,"label ACK payload index=%0d",candidate_i);
      if(!out_offer_valid||out_offer_status||out_offer_node!=out_node||out_offer_key!==gold_cost[159:128])$fatal(1,"actual OFFER");commits=commits+1;
      $fdisplay(trace,"C %0d %0d %0184h %040h",cycles,out_node,out_cost_packet,out_cost_words);
     end else if(out_cost_valid||out_commit_valid||out_offer_valid)$fatal(1,"skip changed state");
     $fdisplay(trace,"O %0d %0d %0d %0d %0d %0d",cycles,out_cookie,system.inner.backend.dut.held_parent,out_node,out_action,out_sequence);

  outputs=outputs+1;candidate_i=candidate_i+1;
 end
 if(system.inner.c_rsp_valid&&system.inner.c_rsp_ready&&system.inner.c_lane==11)begin
  if(system.inner.c_rsp_payload[3:0]||system.inner.c_rsp_payload[35:4]!=100+expand_i)$fatal(1,"autonomous expand identity");
  $fdisplay(trace,"Q %0d %0d %0d %0d %0d %0d",cycles,system.inner.c_rsp_payload[35:4],system.inner.c_rsp_payload[67:36],system.inner.c_rsp_payload[99:68],system.inner.c_rsp_payload[131:100],system.inner.c_rsp_payload[165]);expand_i=expand_i+1;
 end
end
always @(posedge clk)if(!rst)begin
 if(qc_busy&&(f_sr!=0||rc_req_ready||k_rec_ready))$fatal(1,"lifecycle lease gap");
 if(system.c_service_valid&&system.c_service_ready)$fdisplay(trace,"LI %0d %0d %0d %0112h",cycles,query_index,system.c_service_lane,system.c_service_payload);
 if(system.c_service_rsp_valid&&system.c_service_rsp_ready)$fdisplay(trace,"LA %0d %0d %0d %064h",cycles,query_index,system.c_service_lane,system.c_service_rsp_payload);
 if(qc_prepared_event)$fdisplay(trace,"LP %0d %0d %0d",cycles,query_index,qc_prepare_acked);
 if(ss_rsp_valid&&system.inner.ss_rsp_ready)$fdisplay(trace,"SEARCH %0d %0d %0d %0d %0d %0d",cycles,query_index,ss_rsp_status,ss_polls,ss_expands,ss_candidates);
 if(system.inner.backend.rc_rsp_valid&&system.inner.backend.rc_rsp_ready)begin
  if((!injection_seen||replayed)&&(rc_rsp_status||rc_rsp_nodes!=6||rc_rsp_acked!=6))$fatal(1,"native route completion");
  $fdisplay(trace,"RC %0d %0d %0d %0d %0d",cycles,system.inner.backend.f_broute_payload[0],actual_route_slot,rc_rsp_nodes,rc_rsp_acked);route_commands<=route_commands+1;
 end
end
task fault_query;begin
 @(negedge clk);qc_cmd_cookie=32'h50000000+query_index;qc_cmd_source=65185;qc_cmd_key=0;qc_cmd_nodes=9089009;qc_cmd_max_polls=65536;
 qc_cmd_poll_cookie=32'hc0000000+poll_i;qc_cmd_design=design_id;qc_cmd_query=restore_epoch;qc_cmd_price=restore_version[3:0];
 qc_cmd_expand={restore_version,32'd295,32'd283,32'd46,32'd38,32'd260,selected_sequence,32'd2717,selected_sink,32'd0,32'd0,32'd0,32'(100+expand_i),selected_connection};
 qc_cmd_slot=query_index;qc_cmd_route_cookie=32'hf0000000+query_index;
 qc_cmd_valid=1;do @(posedge clk);while(!qc_cmd_ready);@(negedge clk);qc_cmd_valid=0;qc_cmd_source=~qc_cmd_source;qc_cmd_expand=~qc_cmd_expand;qc_cmd_slot=~qc_cmd_slot;qc_cmd_route_cookie=~qc_cmd_route_cookie;
q_cfg_valid=1;
g_cfg_valid=1;
d_cfg_valid=1;
t_cfg_valid=1;
owner_cfg_valid=1;
cs_cfg_valid=1;
host_ctrl_valid=1;
host_design_req_valid=1;
host_io_valid=1;
host_owner_req_valid=1;
cc_req_valid=1;
expand_valid=1;
seed_valid=1;
cs_req_valid=1;
k_cfg_valid=1;
cf_load_valid=1;
rc_req_valid=1;


 wait(qc_rsp_valid);@(negedge clk);
 if(!injection_seen||!qc_rsp_status||!qc_fault||!f_all_drained||!f_backend_idle||!f_normal_retired)$fatal(1,"fault completion not drained");
 $fdisplay(trace,"FAILED_QUERY %0d %0d %0d %0d %0d %0d %0d",cycles,fault_case,qc_rsp_status,qc_rsp_detail,qc_rsp_committed,qc_rsp_acked,k_count);
 repeat(5)begin @(negedge clk);if(!qc_rsp_valid||!qc_busy||f_sr||rc_req_ready||k_rec_ready)$fatal(1,"fault completion lease");end
 qc_rsp_ready=1;@(negedge clk);qc_rsp_ready=0;
end endtask
always @(posedge clk)if(!rst&&armed&&!injection_seen)begin
 if((p_m_rvalid&&p_m_rready&&p_m_rresp!=0)||(p_m_bvalid&&p_m_bready&&p_m_bresp!=0)||
    (g_m_rvalid&&g_m_rready&&g_m_rresp!=0)||(cs_m_rvalid&&cs_m_rready&&cs_m_rresp!=0)||
    (owner_m_bvalid&&owner_m_bready&&owner_m_bresp!=0))begin
  injection_seen<=1;fi_cycle<=cycles;
  $fdisplay(trace,"FI %0d %0d %0d %0d",cycles,fault_case,qc_phase,system.controller.operation);
 end
end
always @(negedge clk)if(injection_seen&&!recovering)k_rec_valid=1;
always @(negedge clk)if(injection_seen&&!recovering&&!qc_rsp_valid&&cycles-fi_cycle>32768)begin
 $fdisplay(trace,"STALLED %0d %0d qc=%0d ss=%0d fence=%0d drained=%b idle=%b retired=%b pending=%h",cycles,fault_case,qc_phase,ss_phase,f_phase,f_all_drained,f_backend_idle,f_normal_retired,system.inner.backend.f_pending);
 $fdisplay(trace,"OWNED core=%b center=%b prefetch=%b post=%b frontier=%b cost=%b commit=%b offer=%b op=%b lease=%b qlease=%b",system.inner.backend.dut.core_busy,system.inner.backend.dut.center_retired_idle,system.inner.backend.dut.prefetch_retired_idle,system.inner.backend.dut.post_retired_idle,system.inner.backend.dut.frontier_retired_idle,system.inner.backend.dut.k_retired_idle,system.inner.backend.dut.commit_busy,system.inner.backend.dut.offer_busy,system.inner.backend.dut.operation_pending,system.inner.backend.dut.cost_lease,system.inner.backend.dut.q_lease);
 $fdisplay(trace,"LABEL_RETIRE memory_leases=%0d page_leases=%0d draining=%b b_retired=%b p_result=%b",system.inner.backend.dut.core.p_memory_leases,system.inner.backend.dut.core.p_page_leases,system.inner.backend.dut.core.p_draining,system.inner.backend.dut.core.b_retired_idle,system.inner.backend.dut.core.p_result_valid);
 $fdisplay(trace,"DETAIL arb_g=%b arb_d=%b arb_io=%b pc_arb=%b capture=%0d capstate=%0d framefault=%b expand=%0d controller=%0d gvalid=%b gready=%b prefetch=%0d post=%0d",system.inner.backend.dut.core.arb_g_busy,system.inner.backend.dut.core.arb_d_busy,system.inner.backend.dut.core.arb_io_busy,system.inner.backend.dut.core.pc_arb_busy,system.inner.backend.dut.core.capture_depth,system.inner.backend.dut.core.child_capture.state,system.inner.backend.dut.core.child_capture.frame_fault,system.inner.backend.dut.core.expansion.state,system.inner.backend.dut.core.controller.state,system.inner.backend.dut.core.g_rsp_valid,system.inner.backend.dut.core.g_rsp_ready,system.inner.backend.dut.prefetch.state,system.inner.backend.dut.post_inputs.state);
 $fflush(trace);$display("QUERY_FAULT_OBSERVED case=%0d outcome=stalled cycles=%0d",fault_case,cycles);$finish;
end
task autonomous_query;begin
 @(negedge clk);qc_cmd_cookie=32'h50000000+query_index;qc_cmd_source=65185;qc_cmd_key=0;qc_cmd_nodes=9089009;qc_cmd_max_polls=65536;
 qc_cmd_poll_cookie=32'hc0000000+poll_i;qc_cmd_design=design_id;qc_cmd_query=restore_epoch;qc_cmd_price=restore_version[3:0];
 qc_cmd_expand={restore_version,32'd295,32'd283,32'd46,32'd38,32'd260,selected_sequence,32'd2717,selected_sink,32'd0,32'd0,32'd0,32'(100+expand_i),selected_connection};
 qc_cmd_slot=query_index;qc_cmd_route_cookie=32'hf0000000+query_index;
 qc_cmd_valid=1;do @(posedge clk);while(!qc_cmd_ready);@(negedge clk);qc_cmd_valid=0;qc_cmd_source=~qc_cmd_source;qc_cmd_expand=~qc_cmd_expand;qc_cmd_slot=~qc_cmd_slot;qc_cmd_route_cookie=~qc_cmd_route_cookie;
q_cfg_valid=1;
g_cfg_valid=1;
d_cfg_valid=1;
t_cfg_valid=1;
owner_cfg_valid=1;
cs_cfg_valid=1;
host_ctrl_valid=1;
host_design_req_valid=1;
host_io_valid=1;
host_owner_req_valid=1;
cc_req_valid=1;
expand_valid=1;
seed_valid=1;
cs_req_valid=1;
k_cfg_valid=1;
cf_load_valid=1;
rc_req_valid=1;

 wait(qc_rsp_valid);@(negedge clk);
 if(qc_rsp_status||!qc_rsp_committed||qc_prepare_acked!=4||qc_cleanup_acked!=1||qc_rsp_nodes!=6||qc_rsp_acked!=6||qc_rsp_cookie!=32'h50000000+query_index||ss_result_node!=selected_sink||qc_fault||ss_fault||ss_polls!=(query_index==0?73:43)||ss_expands!=(query_index==0?72:42)||ss_candidates!=(query_index==0?271:176))$fatal(1,"autonomous query result status=%0d polls=%0d expands=%0d candidates=%0d",ss_rsp_status,ss_polls,ss_expands,ss_candidates);
 repeat(5)begin @(negedge clk);if(!qc_rsp_valid||!qc_busy||f_sr!=0||rc_req_ready||k_rec_ready||!f_all_drained||!f_backend_idle)$fatal(1,"autonomous held/drain response");end
 $fdisplay(trace,"LIFECYCLE %0d %0d %0d %0d %0d %0d %0d %0d",cycles,query_index,qc_rsp_status,qc_rsp_committed,qc_prepare_acked,qc_cleanup_acked,qc_rsp_nodes,qc_rsp_acked);
q_cfg_valid=0;
g_cfg_valid=0;
d_cfg_valid=0;
t_cfg_valid=0;
owner_cfg_valid=0;
cs_cfg_valid=0;
host_ctrl_valid=0;
host_design_req_valid=0;
host_io_valid=0;
host_owner_req_valid=0;
cc_req_valid=0;
expand_valid=0;
seed_valid=0;
cs_req_valid=0;
k_cfg_valid=0;
cf_load_valid=0;
rc_req_valid=0;

 qc_rsp_ready=1;@(negedge clk);qc_rsp_ready=0;
end endtask


always @(posedge clk)if(!rst&&armed&&!injection_seen&&qc_phase==4)begin
 if((fault_case==3&&g_m_rvalid&&g_m_rready)||(fault_case==4&&cs_m_rvalid&&cs_m_rready))eligible_responses<=eligible_responses+1;
end
always @(posedge clk)if(!rst&&qc_rsp_valid)begin
 if(system.inner.backend.dut.core.arb_g_busy||system.inner.backend.dut.core.arb_d_busy||system.inner.backend.dut.core.arb_io_busy||system.inner.backend.dut.core.pc_arb_busy||system.inner.backend.dut.core.capture_depth!=0||system.inner.backend.dut.core.g_rsp_valid||system.inner.backend.dut.core.d_rsp_valid||system.inner.backend.dut.core.b_result_valid||system.inner.backend.dut.core.ce_result_valid)$fatal(1,"query completed with internal ownership");
end
always @(posedge clk)if(!rst&&armed&&!injection_seen&&((g_m_rvalid&&g_m_rready&&g_m_rresp!=0)||(cs_m_rvalid&&cs_m_rready&&cs_m_rresp!=0)))
 $fdisplay(trace,"FAULT_OWNER %0d %0d %0d expand=%0d metadata=%0d coordinate=%0d controller=%0d",cycles,fault_case,eligible_responses,system.inner.backend.dut.core.expansion.state,system.inner.backend.dut.core.metadata.state,system.inner.backend.dut.core.coordinates.state,system.inner.backend.dut.core.controller.state);

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


 control(1);
 if(!$value$plusargs("faultcase=%d",fault_case)||fault_case<1||fault_case>6)$fatal(1,"faultcase");
 query_index=0;armed=1;
 fault_query;
 cc_req_valid=0;cs_req_valid=0;k_cfg_valid=0;cf_load_valid=0;rc_req_valid=0;
 k_rec_valid=1;recovering=1;armed=0;injected_abort=0;injected_drift=0;
 host_ctrl_valid=0;host_io_valid=0;host_owner_req_valid=0;host_design_req_valid=0;expand_valid=0;seed_valid=0;
 q_cfg_valid=0;g_cfg_valid=0;d_cfg_valid=0;t_cfg_valid=0;owner_cfg_valid=0;cs_cfg_valid=0;
 do @(posedge clk);while(!k_rec_ready);@(negedge clk);k_rec_valid=0;
 wait(k_rcfg_valid);@(negedge clk);
 restore_epoch=k_new_query;restore_version=k_new_version;
 rc_req_valid=1;expand_valid=1;seed_valid=1;q_cfg_valid=1;g_cfg_valid=1;d_cfg_valid=1;t_cfg_valid=1;owner_cfg_valid=1;cs_cfg_valid=1;host_ctrl_valid=1;host_io_valid=1;host_owner_req_valid=1;host_design_req_valid=1;cc_req_valid=1;cs_req_valid=1;k_cfg_valid=1;cf_load_valid=1;
 wait(!k_rcfg_valid);
 wait(k_rsp_valid);@(negedge clk);
 if(!recovery_injected||!k_rsp_status||!k_fault||k_count!=1||k_saved_checkpoint!=17||k_saved_design!=design_id||k_rsp_cookie!=32'hc0010001||!f_all_drained||!f_normal_retired||f_pending!=0)$fatal(1,"recovery error completion contract");
 $fdisplay(trace,"RF_DONE %0d %0d %0d %0d %0d %0d %0d",cycles,recovery_fault,k_rsp_status,k_corrected,k_count,lr_written,lr_verified);
 repeat(9)begin @(negedge clk);if(!k_rsp_valid||!k_rsp_status||recover_open||k_permit||f_sr!=0||rc_req_ready||qc_cmd_ready||!f_all_drained||f_pending!=0)$fatal(1,"held recovery error admission");end
 $fdisplay(trace,"RF_HELD %0d %0d",cycles,k_rsp_status);
 k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;
 recovery_done=1;disable first_stream;lr_s_valid=0;
 descriptor_before=system.inner.backend.config_restore.descriptor;
 repeat(16)begin @(negedge clk);if(recover_open||k_permit||f_sr!=0||rc_req_ready||qc_cmd_ready||k_target_reset||!k_fault||k_count!=1||!f_all_drained||f_pending!=0)$fatal(1,"failed recovery reopened or dropped journal");end
 $fdisplay(trace,"RF_CLOSED %0d %0d %0d",cycles,k_count,f_phase);
 retry_cookie=32'hc0020001;retry_version=5;retry_query=3;retry_price=5;stream_cookie=32'he0020001;
 k_rec_valid=1;do @(posedge clk);while(!k_rec_ready);@(negedge clk);k_rec_valid=0;
 wait(k_rcfg_valid);@(negedge clk);restore_epoch=k_new_query;restore_version=k_new_version;
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
 if(lr_rsp_status||lr_rsp_cookie!=32'he0020001||lr_fault||lr_written!=328||lr_verified!=328)$fatal(1,"hardware label restore result");
 $fdisplay(trace,"LD %0d %0d %0d %0d",cycles,lr_rsp_status,lr_written,lr_verified);
 wait(!lr_busy);
 if(rc_req_ready||expand_ready||seed_ready||rc_slots!=0||rc_fault)$fatal(1,"recovery admission gate");
 $fdisplay(trace,"FG %0d %0d",cycles,f_conflict_cycles);rc_req_valid=0;expand_valid=0;seed_valid=0;q_cfg_valid=0;g_cfg_valid=0;d_cfg_valid=0;t_cfg_valid=0;owner_cfg_valid=0;cs_cfg_valid=0;host_ctrl_valid=0;host_io_valid=0;host_owner_req_valid=0;host_design_req_valid=0;cc_req_valid=0;cs_req_valid=0;k_cfg_valid=0;cf_load_valid=0;
 wait(k_rsp_valid);@(negedge clk);if(k_rsp_status||k_rsp_cookie!=32'hc0020001||k_fault||k_count!=0)$fatal(1,"coordinator recovery result");
 repeat(5)begin @(negedge clk);if(recover_open||!k_rsp_valid)$fatal(1,"coordinator response gate");end
 $fdisplay(trace,"KD %0d %0d %0d",cycles,k_rsp_status,k_corrected);
 k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;wait(recover_open);

 if(soft_resets!=1||reset_cycles!=10||cold_cycles!=5||system.inner.backend.config_restore.descriptor!==descriptor_before||k_new_query!=3||k_new_version!=5)$fatal(1,"retry reset/config identity");

 replayed=1;query_index=0;poll_i=0;expand_i=0;candidate_i=0;commits=0;outputs=0;offers=0;physical_expands=0;metadata_calls=0;
 rc=$fseek(polls_fd,0,0);if(rc)$fatal(1,"poll rewind");
 rc=$fseek(candidates_fd,0,0);if(rc)$fatal(1,"candidate rewind");
 rc=$fseek(fd_gold,0,0);if(rc)$fatal(1,"cost rewind");
 $fdisplay(trace,"RETRY %0d %0d %0d",cycles,restore_epoch,restore_version);
 autonomous_query;
 for(final_index=0;final_index<328;final_index=final_index+1)begin
  rc=$fscanf(finals_fd,"%d",final_node_id);if(rc!=1)$fatal(1,"final node");
  for(j=0;j<5;j=j+1)begin rc=$fscanf(finals_fd,"%h",word);if(rc!=1)$fatal(1,"final word");gold_final[j*32+:32]=word;end
  if(final_node_id==selected_sink)gold_final[159:128]=0;
  label_read(final_node_id);if(host_record!==gold_final)$fatal(1,"retry final labels node=%0d",final_node_id);
  $fdisplay(trace,"Z %0d %0d %040h",cycles,final_node_id,host_record);
 end
 stage_no=0;probe_owners;
 if(fault||qc_fault||ss_fault||k_fault||cf_fault||lr_fault||!f_all_drained||!f_backend_idle||ss_polls!=73||ss_expands!=72||ss_candidates!=271||commits!=171||offers!=171)$fatal(1,"retry final state");
 $fflush(trace);$fclose(trace);
 $display("RECOVERY_RETRY_OBSERVED case=%0d outcome=recovered_retry cycles=%0d repairs=%0d",recovery_fault,cycles,k_corrected);$finish;
end

assign recovery_inject=recovering&&!recovery_injected;
initial begin:first_stream wait(recovering);
 wait(k_labels_valid);@(negedge clk);repairs=k_corrected;$fdisplay(trace,"AUTH %0d %0d",cycles,k_corrected);
 // labels_valid automatically starts the hardware service; TB supplies records only.
 rc=$fseek(imports_fd,0,0);if(rc)$fatal(1,"label stream rewind");
 for(import_i=0;import_i<328;import_i=import_i+1)begin
  rc=$fscanf(imports_fd,"%d",import_node);if(rc!=1)$fatal(1,"stream node");
  for(field_i=0;field_i<5;field_i=field_i+1)begin rc=$fscanf(imports_fd,"%h",word);if(rc!=1)$fatal(1,"stream field");import_record[field_i*32+:32]=word;end
  @(negedge clk);lr_s_valid=1;lr_s_node=import_node;lr_s_payload=import_record;lr_s_last=import_i==327;
  do @(posedge clk);while(!lr_s_ready);@(negedge clk);lr_s_valid=0;
 end
end
always @(posedge clk)if(!rst&&recovery_inject)begin
 if((owner_m_rvalid&&owner_m_rready&&owner_m_rresp!=0)||(owner_m_bvalid&&owner_m_bready&&owner_m_bresp!=0)||(p_m_rvalid&&p_m_rready&&p_m_rresp!=0)||(p_m_bvalid&&p_m_bready&&p_m_bresp!=0))begin
  recovery_injected<=1;recovery_fi_cycle<=cycles;
  $fdisplay(trace,"RFI %0d %0d ctl=%0d label=%0d owner_op=%0d checkpoint=%b",cycles,recovery_fault,system.inner.backend.recovery_ctl.state,system.inner.backend.label_restore.state,k_o_op,system.inner.backend.label_restore.checkpoint_phase);
 end
end
always @(negedge clk)if(recovery_injected&&!recovery_done&&cycles-recovery_fi_cycle>32768)begin
 $fdisplay(trace,"RF_STALLED %0d %0d ctl=%0d label=%0d pending=%h drained=%b idle=%b rsp=%b",cycles,recovery_fault,system.inner.backend.recovery_ctl.state,system.inner.backend.label_restore.state,f_pending,f_all_drained,f_backend_idle,k_rsp_valid);
 $fflush(trace);$display("RECOVERY_FAULT_OBSERVED case=%0d outcome=stalled cycles=%0d",recovery_fault,cycles);$finish;
end

always @(posedge clk)begin
 if(k_cold_rst)cold_cycles<=cold_cycles+1;
 if(k_target_reset)reset_cycles<=reset_cycles+1;
 if(system.inner.backend.k_attempt_reset)begin
  soft_resets<=soft_resets+1;
  if(k_count!=1||!f_all_drained||!f_backend_idle||!f_normal_retired||f_pending!=0||lr_busy||cf_busy||lr_rsp_valid||cf_rsp_valid||system.inner.backend.config_restore.descriptor!==descriptor_before)$fatal(1,"unsafe retry transient reset");
  $fdisplay(trace,"SOFT %0d %0d %0d %0d",cycles,k_count,k_new_query,k_new_version);
 end
end

endmodule
