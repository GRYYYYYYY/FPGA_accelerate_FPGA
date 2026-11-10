`timescale 1ns/1ps
`default_nettype none
module tb_candidate_offer;
`ifdef RESTORE_SEED_BYPASS
localparam SEED_BYPASS=1;
`else
localparam SEED_BYPASS=0;
`endif

reg snap_cmd=0,snap_rsp_ready=0;wire snap_ready,snap_busy,snap_rsp,snap_receipt,raw_pc_release_ready,snap_root_release_valid,snap_manifest;wire[3:0]snap_status;wire[31:0]snap_cookie,snap_dirty,snap_verified;
wire[63:0]copy_araddr,copy_awaddr;wire copy_arvalid,copy_arready,copy_rvalid,copy_rready,copy_rlast,copy_awvalid,copy_awready,copy_wvalid,copy_wready,copy_bvalid,copy_bready;wire[511:0]copy_rdata,copy_wdata;wire[3:0]copy_rid,copy_bid;wire[1:0]copy_rresp,copy_bresp;
reg[31:0]warm_fault_node=263946;
initial begin if($value$plusargs("warmfaultnode=%d",warm_fault_node))begin end if(warm_fault_node!=263946&&warm_fault_node!=554512)$fatal(1,"unsupported shared fault node");end

reg cancel_started=0;reg[31:0]retry_cookie=32'hc0010001;reg retry_started=0;
reg g4_warm_mode=0;
reg seed_start_consumed=0;
wire seed_enable=SEED_BYPASS&&g4_warm_mode&&!seed_start_consumed;
integer seed_log,seed_requests=0;
initial seed_log=$fopen("restore_seed_trace.txt","w");reg g3_warm_mode=0;reg wm_enable=0;wire wm_owned,wm_fault,wm_joined;wire[2:0]wm_receipts;
reg warm_psv=0,warm_plast=0;reg[31:0]warm_pi=0,warm_pd=0;reg[31:0]warm_pcrc,warm_qcrc;
reg warm_running=0;integer warm_fd,warm_rc;string warm_path;reg[31:0]warm_word;reg[31:0]warm_nodes[0:327];reg[159:0]warm_values[0:327];

reg ap_valid=0,ap_rsp_ready=0;wire ap_ready,ap_rsp_valid;wire[3:0]ap_status;wire[31:0]ap_refs,ap_occ,ap_rsp_cookie,ap_rsp_checkpoint;wire[63:0]ap_rsp_generation,ap_rsp_design;
reg[31:0]ap_node=0,ap_net=0,ap_cookie=0;reg[63:0]ap_generation=64'h100000002;
reg g4_phase=0;reg g3_phase=0,g3_arm=0;integer g3_negative=0;wire g3_bundle_owned,g3_bundle_fault,g3_bundle_manifest;wire[2:0]g3_export_receipts;wire[31:0]g3_lcount,g3_lcrc,g3_pcrc,g3_qcrc;
reg jp_start=0,jp_commit=0,jp_cancel=0,jp_done_ready=0,jp_authority_stage=0;integer joint_pulses=0,joint_watch=0;reg joint_started=0;
reg[1:0]jp_load=0,jp_ack=0;
wire jp_start_ready,jp_commit_ready,jp_cancel_ready,jp_owned,jp_done;
wire[1:0]jp_result,jp_ready,jp_reply,jp_status;

integer fi_cycle=0,fault_after=0,eligible_responses=0;reg replayed=0;
initial begin if($value$plusargs("faultafter=%d",fault_after))begin if(fault_after<0)$fatal(1,"negative fault ordinal");end end

reg qc_cmd_valid=0;
wire qc_cmd_ready;
reg[1:0]qc_cmd_slot=0;
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
reg bad_crc=0,crc_pin_flip=0;wire[31:0]lr_source_crc;wire[31:0]crc_input;
initial begin if($value$plusargs("badcrc=%d",bad_crc))begin end end


reg ls_cmd=0,ls_ack=0;wire ls_ready,ls_busy,ls_rsp,ls_receipt,label_root_release,label_gate_ready,label_manifest;wire[3:0]ls_status;wire[31:0]ls_cookie,ls_count,ls_crc,ls_pages;
wire scan_v,scan_r,scan_rv,scan_rr,scan_pub;wire[INDEX_BITS-1:0]scan_f,scan_rf;wire[2:0]scan_st;wire[26:0]scan_o;
wire[31:0]ls_ar;wire ls_av,ls_aq,ls_rv,ls_rr,ls_rl,ls_v;reg ls_r=0;wire[511:0]ls_data;wire[3:0]ls_id;wire[1:0]ls_resp;wire[31:0]ls_node;wire[159:0]ls_payload;integer ls_fd,ls_emitted=0;

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
reg rc_req_valid=0,rc_req_op=0,rc_rsp_ready=0;reg[1:0]rc_req_slot=0;reg[31:0]rc_req_cookie=0,rc_req_sink=0,rc_req_sequence=0;wire rc_req_ready,rc_rsp_valid,rc_block,rc_fault,rc_busy;wire[3:0]rc_rsp_status;wire[31:0]rc_rsp_cookie,rc_rsp_nodes,rc_rsp_acked;wire[3:0]rc_slots;
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
wire k_a_valid,k_a_rsp_ready;wire k_a_ready,k_a_rsp_valid;wire[31:0]k_a_node,k_a_net,k_a_cookie,k_a_checkpoint;wire[63:0]k_a_design;
wire[31:0]k_a_rsp_cookie,k_a_rsp_checkpoint,k_a_refs,k_a_occ;wire[63:0]k_a_rsp_design;wire[3:0]k_a_status;
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
.inject_r(armed&&!injection_seen&&fault_case==1&&qc_phase==2&&system.controller.operation==0),
.inject_b(armed&&!injection_seen&&((fault_case==2&&qc_phase==2&&system.controller.operation>=1&&system.controller.operation<=4)||(fault_case==6&&qc_phase==2&&system.controller.operation==6))),
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
.size0(64'd146284032),
.size1(64'd0),
.size2(64'd0),
.inject_r(1'b0),
.inject_b(armed&&!injection_seen&&fault_case==5&&qc_phase==6&&(!wm_enable||b_o_node==warm_fault_node)),
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
 cycles<=cycles+1;if(cycles>8000000)$fatal(1,"watchdog");
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
reg[31:0]saved1[0:31],saved2[0:31];integer count1=0,count2=0,stage_no,pi,pj,expected_refs,probe_node;reg[31:0]route_node;reg[31:0]selected_sink=204279,selected_connection=170782,selected_sequence=180327;
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
 @(negedge clk);host_owner_req_op=op;host_owner_req_cookie=32'he0000000+node;host_owner_req_node=node;host_owner_req_net=26422;host_owner_req_valid=1;
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

wire[1:0]actual_route_slot=system.inner.backend.f_broute_payload[2:1];
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
   else if(actual_route_slot==1)begin saved2[count2]<=system.inner.backend.route_join.o_node;count2<=count2+1;end
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
 wire as_cfg_valid;wire as_cfg_ready;wire[63:0]as_cfg_design,as_cfg_generation,as_cfg_primary,as_cfg_pool,as_cfg_allocator;
 wire[31:0]as_cfg_checkpoint,as_cfg_nodes,as_cfg_nets,as_cfg_capacity;
 wire as_configured;wire[63:0]as_bound_design,as_bound_generation;wire[31:0]as_bound_checkpoint;
 wire[63:0]as_m_araddr;wire[7:0]as_m_arlen;wire[2:0]as_m_arsize;wire[1:0]as_m_arburst;wire[3:0]as_m_arid;
 wire as_m_arvalid;wire as_m_arready;wire[511:0]as_m_rdata;wire[3:0]as_m_rid;wire[1:0]as_m_rresp;wire as_m_rlast,as_m_rvalid;wire as_m_rready;
 wire[63:0]as_m_awaddr;wire[7:0]as_m_awlen;wire[2:0]as_m_awsize;wire[1:0]as_m_awburst;wire[3:0]as_m_awid;
 wire as_m_awvalid;wire as_m_awready;wire[511:0]as_m_wdata;wire[63:0]as_m_wstrb;wire as_m_wlast,as_m_wvalid;wire as_m_wready;
 wire[3:0]as_m_bid;wire[1:0]as_m_bresp;wire as_m_bvalid;wire as_m_bready;
wire as_cfg_rsp_valid;wire as_cfg_rsp_ready;wire[2:0]as_cfg_status;
wire as_busy,as_fault,as_drained,as_retired;wire[63:0]as_rsp_generation;
reg authority_bind=0,authority_ack=0,as_inject=0;integer as_fault_mode=0;reg[31:0]as_recover_version=4;reg[1:0]as_recover_query=2;integer as_reads,as_writes,as_rbeats,as_wbeats,as_bresponses;
axi_file_memory #(.ADDR_BITS(64),.READ_ONLY(1),.MAX_BEATS(1),.TAG("snapshot")) authority_memory(
.clk(clk),.rst(k_cold_rst),.base0(64'h91fffff000),.base1(64'ha000000000),.base2(64'hc000000000),.size0(64'd146284032),.size1(64'd146284032),.size2(64'd146284032),
.araddr(as_m_araddr),.arlen(as_m_arlen),.arsize(as_m_arsize),.arburst(as_m_arburst),.arid(as_m_arid),.arvalid(as_m_arvalid),.arready(as_m_arready),.rdata(as_m_rdata),.rid(as_m_rid),.rresp(as_m_rresp),.rlast(as_m_rlast),.rvalid(as_m_rvalid),.rready(as_m_rready),.awaddr(as_m_awaddr),.awlen(as_m_awlen),.awsize(as_m_awsize),.awburst(as_m_awburst),.awid(as_m_awid),.awvalid(as_m_awvalid),.awready(as_m_awready),.wdata(as_m_wdata),.wstrb(as_m_wstrb),.wlast(as_m_wlast),.wvalid(as_m_wvalid),.wready(as_m_wready),.bid(as_m_bid),.bresp(as_m_bresp),.bvalid(as_m_bvalid),.bready(as_m_bready),.inject_r(as_inject),.inject_b(1'b0),.reads(as_reads),.writes(as_writes),.rbeats(as_rbeats),.wbeats(as_wbeats),.bresponses(as_bresponses));
 always @(posedge clk)if(!k_cold_rst)begin
  if(system.as_attempt_reset)$fdisplay(trace,"AS_REARM %0d %016h",cycles,as_bound_generation);
  if(as_m_awvalid||as_m_wvalid||as_writes||as_bresponses)$fatal(1,"snapshot authority write");
  if(k_target_reset&&(!as_drained||!as_retired))$fatal(1,"system target reset before authority retired");
 end
 task install_authority;begin
  @(negedge clk);authority_bind=1;do @(posedge clk);while(!as_cfg_ready);@(negedge clk);authority_bind=0;
  wait(as_cfg_rsp_valid);@(negedge clk);if(as_cfg_status||!as_configured||as_bound_generation!=64'h100000001)$fatal(1,"authority install");
  repeat(5)begin @(negedge clk);if(!as_cfg_rsp_valid||qc_cmd_ready||rc_req_ready)$fatal(1,"authority config lease");end
  $fdisplay(trace,"AS_BIND %0d %016h %0d %016h",cycles,as_bound_design,as_bound_checkpoint,as_bound_generation);
  authority_ack=1;@(negedge clk);authority_ack=0;wait(!as_busy&&!system.as_cfg_lease);
 end endtask


`ifdef QC_NO_LOSS
localparam DIAG_ENABLED=0;
`else
localparam DIAG_ENABLED=1;
`endif
`ifdef QCP_BYPASS
localparam JOIN_ENABLED=0;
`else
localparam JOIN_ENABLED=1;
`endif
reg pc_acquire_valid=0,pc_release_valid=0;wire pc_acquire_ready,pc_release_ready,pc_owned;
reg qc_cp_valid=0,qc_cp_restore=0,qc_cp_rsp_ready=0,qc_cp_s_valid=0,qc_cp_s_last=0,qc_cp_m_ready=0,qc_cp_test_reset=0;
wire qc_cp_ready,qc_cp_busy,qc_cp_rsp_valid,qc_cp_s_ready,qc_cp_m_valid,qc_cp_m_last,qc_restore_pending;
reg[31:0]qc_cp_expected_crc=0,qc_cp_s_index=0,qc_cp_s_data=0;wire[31:0]qc_cp_crc,qc_cp_m_index,qc_cp_m_data;wire[3:0]qc_cp_status;
reg[31:0]qcp_image[0:9],qcp_crc;integer qcp_checks=0,qcp_rejected=0,qcp_pending_cycles=0;reg qcp_active=0;
reg[2303:0]qcp_descriptor;reg[31:0]qcp_journal;reg[3:0]qcp_slots;
always @(posedge clk)if(!k_cold_rst)begin
 if(qc_cp_s_valid&&qc_cp_s_ready)$fdisplay(trace,"QCS %0d %0d %08h %0d",qcp_checks,qc_cp_s_index,qc_cp_s_data,qc_cp_s_last);
 if(qc_cp_m_valid&&qc_cp_m_ready)$fdisplay(trace,"QCM %0d %0d %08h %0d",qcp_checks,qc_cp_m_index,qc_cp_m_data,qc_cp_m_last);
 if(qc_restore_pending)begin
  qcp_pending_cycles<=qcp_pending_cycles+1;
  if(pc_release_ready||qc_cmd_ready||rc_req_ready||expand_ready||seed_ready)$fatal(1,"partial query restore released work");
 end
end
function automatic[31:0]qcp_sum;reg[31:0]v;begin v=32'hffffffff;for(integer x=0;x<10;x=x+1)begin v=v^qcp_image[x];for(integer b=0;b<32;b=b+1)v=v[0]?(v>>1)^32'hedb88320:v>>1;end qcp_sum=~v;end endfunction
 task qcp_result(input integer expected);reg[35:0]hold;begin
 wait(qc_cp_rsp_valid);@(negedge clk);if(qc_cp_status!=expected)$fatal(1,"query checkpoint result %d/%d",qc_cp_status,expected);hold={qc_cp_status,qc_cp_crc};
 pc_release_valid=1;
 repeat(6)begin @(negedge clk);if(!qc_cp_rsp_valid||{qc_cp_status,qc_cp_crc}!==hold||pc_release_ready||!pc_owned)$fatal(1,"held query checkpoint released lease");end
 pc_release_valid=0;$fdisplay(trace,"QCP %0d %0d %08h %0d %0d",qcp_checks,qc_cp_status,qc_cp_crc,qc_restore_pending,system.controller.last_sequence);qcp_checks=qcp_checks+1;
 qc_cp_rsp_ready=1;@(negedge clk);qc_cp_rsp_ready=0;wait(!qc_cp_busy);
end endtask
task qcp_start(input integer restore);begin
 @(negedge clk);qc_cp_restore=restore;qc_cp_valid=1;do @(posedge clk);while(!qc_cp_ready);@(negedge clk);qc_cp_valid=0;
end endtask
task qcp_load(input integer expected);begin
 qcp_start(1);
 for(integer x=0;x<10;x=x+1)begin
  @(negedge clk);qc_cp_s_valid=1;qc_cp_s_index=x;qc_cp_s_data=qcp_image[x];qc_cp_s_last=x==9;do @(posedge clk);while(!qc_cp_s_ready);@(negedge clk);qc_cp_s_valid=0;
 end
 qcp_result(expected);
end endtask
task query_checkpoint_join;begin
 qcp_active=1;qcp_descriptor=system.inner.backend.config_restore.descriptor;qcp_journal=k_count;qcp_slots=rc_slots;
 @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;if(!pc_owned)$fatal(1,"query checkpoint no lease");
 qcp_start(0);
 for(integer x=0;x<10;x=x+1)begin
  wait(qc_cp_m_valid);@(negedge clk);if(qc_cp_m_index!=x||qc_cp_m_last!=(x==9))$fatal(1,"query export boundary");qcp_image[x]=qc_cp_m_data;repeat(2)@(negedge clk);qc_cp_m_ready=1;@(negedge clk);qc_cp_m_ready=0;
 end
 qcp_result(0);qcp_crc=qc_cp_crc;
 if(qcp_image[8]!=1||!qcp_image[7][6])$fatal(1,"query ledger did not capture consumed sequence");
 if(DIAG_ENABLED)begin
 @(negedge clk);qc_cp_test_reset=1;repeat(3)@(negedge clk);qc_cp_test_reset=0;repeat(3)@(negedge clk);
 if(!qc_restore_pending||system.controller.last_sequence!=0||system.controller.sequence_seen)$fatal(1,"query diagnostic loss");
 pc_release_valid=1;repeat(9)begin @(negedge clk);if(pc_release_ready||!pc_owned)$fatal(1,"unrestored query released lease");end pc_release_valid=0;
 end
 qc_cp_expected_crc=qcp_crc^1;qcp_load(1);if(!qc_restore_pending||system.controller.last_sequence!=(DIAG_ENABLED?0:1))$fatal(1,"bad CRC opened recovery gate");
 qcp_image[5]=qcp_image[5]^1;qc_cp_expected_crc=qcp_sum();qcp_load(1);if(!qc_restore_pending||system.controller.last_sequence!=(DIAG_ENABLED?0:1))$fatal(1,"wrong generation opened recovery gate");qcp_image[5]=qcp_image[5]^1;
 qc_cp_expected_crc=qcp_crc;qcp_load(0);if(qc_restore_pending||system.controller.last_sequence!=1)$fatal(1,"query ledger recovery missing");
 if(system.inner.backend.config_restore.descriptor!==qcp_descriptor||k_count!=qcp_journal||rc_slots!=qcp_slots||system.as_bound_generation!=64'h100000001)$fatal(1,"query reset changed retained services");
 @(negedge clk);pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;wait(!pc_owned);
 // A free slot and valid context ensure this is a sequence rejection.
 @(negedge clk);qc_cmd_slot=1;qc_cmd_cookie=32'hce000001;qc_cmd_source=66893;qc_cmd_key=0;qc_cmd_nodes=9089009;qc_cmd_max_polls=65536;qc_cmd_design=design_id;qc_cmd_query=restore_epoch;qc_cmd_price=restore_version[3:0];qc_cmd_expand={restore_version,32'd291,32'd279,32'd31,32'd23,32'd260,32'd1,32'd26422,selected_sink,32'd0,32'd0,32'd0,32'd100,selected_connection};
 if(rc_slots[1]||system.controller.label_state_dirty||qc_cmd_query!=p_active_query||qc_cmd_price!=p_active_price||qc_cmd_expand[447:416]!=query_version||!system.controller.sequence_seen)$fatal(1,"invalid sequence probe context");
 qc_cmd_valid=1;do @(posedge clk);while(!qc_cmd_ready);@(negedge clk);qc_cmd_valid=0;
 wait(qc_rsp_valid);@(negedge clk);if(qc_rsp_status!=1||qc_rsp_committed||qc_prepare_acked||qc_cleanup_acked||qc_fault||ss_busy||rc_slots!=qcp_slots)$fatal(1,"restored sequence replay admitted");
 $fdisplay(trace,"QCP_REJECT %0d %0d %0d %0d",cycles,qc_rsp_status,qc_prepare_acked,qc_rsp_committed);qcp_rejected=qcp_rejected+1;
 qc_rsp_ready=1;@(negedge clk);qc_rsp_ready=0;wait(!qc_busy);
 $fdisplay(trace,"QCP_JOIN %0d %0d %0d %0d %0d",cycles,qcp_checks,qcp_rejected,qcp_pending_cycles,system.controller.last_sequence);
end endtask


reg[63:0]qc_cp_generation=0;reg[31:0]bundle_query_crc;
reg cap_path_valid=0,cap_path_restore=0,cap_path_rsp_ready=0,cap_path_m_ready=0;
wire cap_path_ready,cap_path_busy,cap_path_rsp_valid,cap_path_m_valid,cap_path_m_last;wire[3:0]cap_path_status;wire[31:0]cap_path_crc,cap_path_m_index,cap_path_m_data;
reg[31:0]cap_path_image[0:155];
always @(posedge clk)if(!k_cold_rst&&cap_path_m_valid&&cap_path_m_ready)$fdisplay(trace,"BPATH %0d %08h %0d",cap_path_m_index,cap_path_m_data,cap_path_m_last);
task bundle_capture;begin
 qcp_active=1;
 @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;
 if(!pc_owned||!system.pc_safe||system.inner.backend.dut.frontier_size!=0||qc_busy||ss_busy||rc_busy||!f_all_drained||!f_backend_idle||!f_normal_retired)$fatal(1,"bundle capture not quiescent");
 joint_cancel_check;
 // Reject decreasing generation; capture the later transaction from its handshake.
 qc_cp_generation=1;qcp_start(0);qcp_result(1);
 qc_cp_generation=64'h100000002;qcp_start(0);qc_cp_generation=~qc_cp_generation;
 for(integer x=0;x<10;x=x+1)begin
  wait(qc_cp_m_valid);@(negedge clk);if(qc_cp_m_index!=x||qc_cp_m_last!=(x==9))$fatal(1,"bundle query boundary");qcp_image[x]=qc_cp_m_data;repeat(2)@(negedge clk);qc_cp_m_ready=1;@(negedge clk);qc_cp_m_ready=0;
 end
 qcp_result(0);bundle_query_crc=qc_cp_crc;if({qcp_image[5],qcp_image[4]}!==64'h100000002||qcp_image[8]!=1)$fatal(1,"pending capture identity not held");
 // Capturing a future identity does not activate it for a running import.
 qc_cp_expected_crc=bundle_query_crc;qcp_load(1);if(!qc_restore_pending||system.controller.last_sequence!=1)$fatal(1,"future generation silently activated");
 // The default export remains bound to the running authority; re-import it to
 // retire the deliberately failed restore before freezing the healthy bundle.
 qc_cp_generation=0;qcp_start(0);
 for(integer x=0;x<10;x=x+1)begin
  wait(qc_cp_m_valid);@(negedge clk);if(qc_cp_m_index!=x)$fatal(1,"current generation boundary");qcp_image[x]=qc_cp_m_data;repeat(2)@(negedge clk);qc_cp_m_ready=1;@(negedge clk);qc_cp_m_ready=0;
 end
 qcp_result(0);if({qcp_image[5],qcp_image[4]}!==64'h100000001)$fatal(1,"default export changed identity");qc_cp_expected_crc=qc_cp_crc;qcp_load(0);

 @(negedge clk);cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<156;x=x+1)begin
  wait(cap_path_m_valid);@(negedge clk);if(cap_path_m_index!=x||cap_path_m_last!=(x==155))$fatal(1,"bundle path boundary");cap_path_image[x]=cap_path_m_data;repeat(2)@(negedge clk);cap_path_m_ready=1;@(negedge clk);cap_path_m_ready=0;
 end
 wait(cap_path_rsp_valid);@(negedge clk);if(cap_path_status)$fatal(1,"bundle path status");repeat(6)@(negedge clk);cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;wait(!cap_path_busy);
 if(system.as_bound_generation!==64'h100000001||system.controller.last_sequence!=1||qc_restore_pending||!pc_owned||!system.pc_safe||f_phase!=0||!f_all_drained||!f_backend_idle||!f_normal_retired)$fatal(1,"capture changed active binding/work state");
 $fdisplay(trace,"BCFG %0576h",system.inner.backend.config_restore.descriptor);
 $fdisplay(trace,"BCONTEXT %016h %016h %0d %0d %0d %0d %0d %0d %0d",design_id,64'h100000002,k_saved_checkpoint,query_version,p_active_query,p_active_price,cs_published_version,system.controller.last_sequence,rc_slots);
 $fdisplay(trace,"BFLOORS %0d %0d %0d %0d %0d",system.inner.backend.recovery_ctl.current_version,system.inner.backend.recovery_ctl.current_query,system.inner.backend.recovery_ctl.current_price,system.inner.backend.recovery_ctl.attempt_version,system.inner.backend.recovery_ctl.attempt_query);
 for(integer x=0;x<k_count;x=x+1)$fdisplay(trace,"BJ %0d %0d %0d",x,system.inner.backend.recovery_ctl.nodes[x],system.inner.backend.recovery_ctl.nets[x]);
 $fdisplay(trace,"BREADY %0d %08h %08h %0d %0d %0d %0d",cycles,bundle_query_crc,cap_path_crc,k_count,pc_owned,system.inner.backend.dut.frontier_size,f_phase);
end endtask

reg last_k_reset=0,prior_drained=0;integer last_j_cycle=0;reg[31:0]last_j_node=0;
always @(posedge clk)begin
 if(k_cold_rst)begin k_normal_retired<=1;last_k_reset<=0;prior_drained<=0;end
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
  if(k_a_valid&&k_a_ready)$fdisplay(trace,"KA %0d %0d %0d %0d %0d",cycles,k_a_checkpoint,k_a_node,k_a_net,k_a_cookie);
  if(k_a_rsp_valid&&k_a_rsp_ready)$fdisplay(trace,"AS_REPLY %0d %0d %0d %0d %016h",cycles,k_a_status,k_a_refs,k_a_occ,as_rsp_generation);
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






assign f_route_payload={29'd0,rc_req_sequence,32'd26422,rc_req_sink,32'd66893,rc_req_cookie,rc_req_slot,rc_req_op};


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
 if(op<0||op>1)$fatal(1,"invalid route operation");
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
 if(rc_rsp_status||rc_rsp_cookie!=32'hf0000000+route_commands||rc_rsp_nodes!=3||rc_rsp_acked!=3||rc_fault)$fatal(1,"route controller result");
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

reg cancel_hold_release=0,cancel_active=0;integer cancel_r_count=0,cancel_front_count=0,cancel_wait_count=0;
wire cancel_hold=!retry_started&&!cancel_hold_release&&((wm_owned&&k_labels_valid&&lr_written==20)||cancel_active);
reg bcfg_valid=0,bcfg_ready=0;wire bcfg_accept,bcfg_reply;wire[3:0]bcfg_status;wire baseline_idle,baseline_configured;
`ifdef BASE_ABORT_DELAY
localparam BASELINE_DELAY=48;
`else
localparam BASELINE_DELAY=0;
`endif
wire baseline_retired,baseline_physical,baseline_owned,baseline_guard_fault;
wire baseline_req_valid,baseline_req_ready,baseline_rsp_valid,baseline_rsp_ready;
wire[31:0]baseline_req_node,baseline_rsp_node;wire[63:0]baseline_req_epoch,baseline_rsp_epoch;wire[3:0]baseline_rsp_status;wire[159:0]baseline_rsp_payload;
wire[63:0]ba;wire[7:0]bl;wire[2:0]bz;wire[1:0]bb;wire[3:0]bi;wire bv,by,brv,brr,brlast;wire[511:0]bd;wire[3:0]brid;wire[1:0]bresp;

baseline_retirement_guard retirement(.clk(clk),.cold_rst(bench_rst),.reader_idle(baseline_idle),.cfg_valid(bcfg_valid),.req_valid(baseline_req_valid),.req_ready(baseline_req_ready),.rsp_valid(baseline_rsp_valid),.rsp_ready(baseline_rsp_ready),.arvalid(bv),.arready(by),.arlen(bl),.rvalid(brv),.rready(brr),.rlast(brlast),.retired(baseline_retired),.physical_drained(baseline_physical),.owned(baseline_owned),.fault(baseline_guard_fault));
label_baseline_reader baseline(.clk(clk),.rst(bench_rst),.cfg_valid(bcfg_valid),.cfg_ready(bcfg_accept),.cfg_permit(1'b1),.cfg_base(64'hb000000000),.cfg_epoch(64'h300010003),.cfg_count(32'd9089009),.cfg_rsp_valid(bcfg_reply),.cfg_rsp_ready(bcfg_ready),.cfg_status(bcfg_status),.req_valid(baseline_req_valid),.req_ready(baseline_req_ready),.req_node(baseline_req_node),.req_epoch(baseline_req_epoch),.rsp_valid(baseline_rsp_valid),.rsp_ready(baseline_rsp_ready),.rsp_status(baseline_rsp_status),.rsp_node(baseline_rsp_node),.rsp_epoch(baseline_rsp_epoch),.rsp_payload(baseline_rsp_payload),.idle(baseline_idle),.configured(baseline_configured),.araddr(ba),.arlen(bl),.arsize(bz),.arburst(bb),.arid(bi),.arvalid(bv),.arready(by),.rdata(bd),.rid(brid),.rresp(bresp),.rlast(brlast),.rvalid(brv),.rready(brr));
axi_file_memory #(.READ_ONLY(1),.READ_DELAY(BASELINE_DELAY),.TAG("baseline")) baseline_mem(.hold_r(cancel_hold),.clk(clk),.rst(bench_rst),.base0(64'hb000000000),.size0(64'd290848320),.base1(64'b0),.size1(64'b0),.base2(64'b0),.size2(64'b0),.araddr(ba),.arlen(bl),.arsize(bz),.arburst(bb),.arid(bi),.arvalid(bv),.arready(by),.rdata(bd),.rid(brid),.rresp(bresp),.rlast(brlast),.rvalid(brv),.rready(brr),.awaddr(64'b0),.awlen(8'b0),.awsize(3'd6),.awburst(2'd1),.awid(4'b0),.awvalid(1'b0),.wdata(512'b0),.wstrb(64'b0),.wlast(1'b0),.wvalid(1'b0),.bready(1'b1),.inject_r(1'b0),.inject_b(1'b0));
task baseline_configure;begin
 @(negedge clk);bcfg_valid=1;do @(posedge clk);while(!bcfg_accept);@(negedge clk);bcfg_valid=0;
 wait(bcfg_reply);@(negedge clk);if(bcfg_status)$fatal(1,"baseline config");bcfg_ready=1;@(negedge clk);bcfg_ready=0;
end endtask
always @(posedge clk)if(!bench_rst)begin
 if(baseline_req_valid&&baseline_req_ready)$fdisplay(trace,"BM %0d %0d %h",cycles,baseline_req_node,baseline_req_epoch);
 if(baseline_rsp_valid&&baseline_rsp_ready)$fdisplay(trace,"BR %0d %0d %0d %040h",cycles,baseline_rsp_node,baseline_rsp_status,baseline_rsp_payload);
end
always @(posedge clk)if(!bench_rst)begin
 if(system.inner.backend.dut.core.p.native_cmd_valid&&system.inner.backend.dut.core.p.native_cmd_ready)$fdisplay(trace,"NB %0d %0d %0d %0d %0d %0d %0d %08h %0d %0d",cycles,system.inner.backend.dut.core.p.native_cmd_op,system.inner.backend.dut.core.p.native_cmd_slot,system.inner.backend.dut.core.p.native_cmd_page,system.inner.backend.dut.core.p.native_cmd_generation,system.inner.backend.dut.core.p.native_cmd_offset,system.inner.backend.dut.core.p.native_cmd_field,system.inner.backend.dut.core.p.native_cmd_value,system.inner.backend.dut.core.p.native_cmd_query,system.inner.backend.dut.core.p.native_cmd_price);
 if(system.inner.backend.dut.core.p.native_rsp_valid&&system.inner.backend.dut.core.p.native_rsp_ready)$fdisplay(trace,"NR %0d %0d %0d %040h",cycles,system.inner.backend.dut.core.p.native_rsp_status,system.inner.backend.dut.core.p.native_rsp_present,system.inner.backend.dut.core.p.native_rsp_payload);
end


query_residency_system #(.ENABLE_RESTORE_SEED_BYPASS(SEED_BYPASS),.PATH_SLOTS(4),.ENABLE_BASELINE(1),.SLOTS(SLOTS),.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS),.ENABLE_TEST_INJECTION(DIAG_ENABLED),.ENABLE_WARM_RECOVERY(1),.RESTORE_RECORDS(1024),.ENABLE_FRAME_SCAN(1),.CHECK_LABEL_CRC(1))system(.restore_seed_enable(seed_enable),.baseline_permit(1'b1),.baseline_epoch(64'h300010003),.baseline_retired(baseline_retired),.baseline_req_valid(baseline_req_valid),.baseline_req_ready(baseline_req_ready),.baseline_req_node(baseline_req_node),.baseline_req_epoch(baseline_req_epoch),.baseline_rsp_valid(baseline_rsp_valid),.baseline_rsp_ready(baseline_rsp_ready),.baseline_rsp_status(baseline_rsp_status),.baseline_rsp_node(baseline_rsp_node),.baseline_rsp_epoch(baseline_rsp_epoch),.baseline_rsp_payload(baseline_rsp_payload),.snapshot_label_crc(crc_input),.lr_source_crc(lr_source_crc),.scan_valid(scan_v),.scan_ready(scan_r),.scan_permit(1'b1),.scan_frame(scan_f),.scan_rsp_valid(scan_rv),.scan_rsp_ready(scan_rr),.scan_status(scan_st),.scan_result_frame(scan_rf),.scan_owner(scan_o),.scan_published(scan_pub),.wm_enable(wm_enable),.wm_source_version(g4_warm_mode?32'd6:(g3_warm_mode?32'd5:32'd3)),.wm_source_query(g4_warm_mode?2'd0:(g3_warm_mode?2'd3:2'd1)),.wm_source_price(g4_warm_mode?4'd6:(g3_warm_mode?4'd5:4'd3)),.wm_path_crc(warm_pcrc),.wm_query_crc(warm_qcrc),.wm_owned(wm_owned),.wm_fault(wm_fault),.wm_joined(wm_joined),.wm_receipts(wm_receipts),.boot_required(1'b0),.boot_cfg_valid(1'b0),.boot_verify_valid(1'b0),.boot_rsp_ready(1'b0),.boot_design(64'd0),.boot_generation(64'd0),.boot_checkpoint(32'd0),.boot_version(32'd0),.boot_nodes(32'd0),.boot_label_count(32'd0),.boot_label_crc(32'd0),.boot_path_crc(32'd0),.boot_query_crc(32'd0),.boot_query(2'd0),.boot_slots(4'd0),.boot_price(4'd0),.boot_payload(2304'd0),.jp_start(jp_start),.jp_start_ready(jp_start_ready),.jp_commit(jp_commit),.jp_commit_ready(jp_commit_ready),.jp_cancel(jp_cancel),.jp_cancel_ready(jp_cancel_ready),.jp_owned(jp_owned),.jp_done(jp_done),.jp_done_ready(jp_done_ready),.jp_result(jp_result),.jp_manifest_ready(g3_phase ? g3_bundle_manifest : snap_manifest&&label_manifest),.jp_generation(g4_phase ? 64'h100000004 : (g3_phase ? 64'h100000003 : 64'h100000002)),.jp_design(design_id),.jp_checkpoint(g4_phase ? 32'd20 : (g3_phase ? 32'd19 : 32'd18)),.jp_version(query_version),.jp_query(p_active_query),.jp_price(p_active_price),.jp_load(jp_load),.jp_ack(jp_ack),.jp_ready(jp_ready),.jp_reply(jp_reply),.jp_status(jp_status),.jp_authority_stage(jp_authority_stage),.ap_valid(ap_valid),.ap_ready(ap_ready),.ap_rsp_valid(ap_rsp_valid),.ap_rsp_ready(ap_rsp_ready),.ap_status(ap_status),.ap_refs(ap_refs),.ap_occ(ap_occ),.ap_rsp_cookie(ap_rsp_cookie),.ap_rsp_checkpoint(ap_rsp_checkpoint),.ap_rsp_generation(ap_rsp_generation),.ap_rsp_design(ap_rsp_design),.ap_node(ap_node),.ap_net(ap_net),.ap_cookie(ap_cookie),.ap_generation(ap_generation),.ap_design(design_id),.ap_checkpoint(k_saved_checkpoint),.cp_ready(cap_path_ready),.cp_busy(cap_path_busy),.cp_rsp_valid(cap_path_rsp_valid),.cp_status(cap_path_status),.cp_crc(cap_path_crc),.cp_m_valid(cap_path_m_valid),.cp_m_index(cap_path_m_index),.cp_m_data(cap_path_m_data),.cp_m_last(cap_path_m_last),.qc_cp_generation(qc_cp_generation),.pc_acquire_ready(pc_acquire_ready),.pc_release_ready(raw_pc_release_ready),.pc_owned(pc_owned),.qc_cp_valid(qc_cp_valid),.qc_cp_restore(qc_cp_restore),.qc_cp_rsp_ready(qc_cp_rsp_ready),.qc_cp_s_valid(qc_cp_s_valid),.qc_cp_s_last(qc_cp_s_last),.qc_cp_m_ready(qc_cp_m_ready),.qc_cp_test_reset(qc_cp_test_reset),.qc_cp_ready(qc_cp_ready),.qc_cp_busy(qc_cp_busy),.qc_cp_rsp_valid(qc_cp_rsp_valid),.qc_cp_s_ready(qc_cp_s_ready),.qc_cp_m_valid(qc_cp_m_valid),.qc_cp_m_last(qc_cp_m_last),.qc_restore_pending(qc_restore_pending),.qc_cp_expected_crc(qc_cp_expected_crc),.qc_cp_s_index(qc_cp_s_index),.qc_cp_s_data(qc_cp_s_data),.qc_cp_crc(qc_cp_crc),.qc_cp_m_index(qc_cp_m_index),.qc_cp_m_data(qc_cp_m_data),.qc_cp_status(qc_cp_status),.as_cfg_valid(authority_bind),.as_cfg_ready(as_cfg_ready),.as_cfg_design(design_id),.as_cfg_generation(jp_authority_stage ? (g4_phase ? 64'h100000004 : (g3_phase ? 64'h100000003 : 64'h100000002)) : 64'h100000001),.as_cfg_primary(jp_authority_stage ? (g3_phase&&!g4_phase ? 64'hc000000000 : 64'ha000000000) : 64'h91fffff000),.as_cfg_pool(jp_authority_stage ? (g3_phase&&!g4_phase ? 64'hc008aaff40 : 64'ha008aaff40) : 64'h9208aaef40),.as_cfg_allocator(jp_authority_stage ? (g3_phase&&!g4_phase ? 64'hc008b81dc0 : 64'ha008b81dc0) : 64'h9208b80dc0),.as_cfg_checkpoint(jp_authority_stage ? (g4_phase ? 32'd20 : (g3_phase ? 32'd19 : 32'd18)) : 32'd17),.as_cfg_nodes(32'd9089009),.as_cfg_nets(32'd27960),.as_cfg_capacity(32'd53734),.as_configured(as_configured),.as_bound_design(as_bound_design),.as_bound_generation(as_bound_generation),.as_bound_checkpoint(as_bound_checkpoint),.as_m_araddr(as_m_araddr),.as_m_arlen(as_m_arlen),.as_m_arsize(as_m_arsize),.as_m_arburst(as_m_arburst),.as_m_arid(as_m_arid),.as_m_arvalid(as_m_arvalid),.as_m_arready(as_m_arready),.as_m_rdata(as_m_rdata),.as_m_rid(as_m_rid),.as_m_rresp(as_m_rresp),.as_m_rlast(as_m_rlast),.as_m_rvalid(as_m_rvalid),.as_m_rready(as_m_rready),.as_m_awaddr(as_m_awaddr),.as_m_awlen(as_m_awlen),.as_m_awsize(as_m_awsize),.as_m_awburst(as_m_awburst),.as_m_awid(as_m_awid),.as_m_awvalid(as_m_awvalid),.as_m_awready(as_m_awready),.as_m_wdata(as_m_wdata),.as_m_wstrb(as_m_wstrb),.as_m_wlast(as_m_wlast),.as_m_wvalid(as_m_wvalid),.as_m_wready(as_m_wready),.as_m_bid(as_m_bid),.as_m_bresp(as_m_bresp),.as_m_bvalid(as_m_bvalid),.as_m_bready(as_m_bready),.as_cfg_rsp_valid(as_cfg_rsp_valid),.as_cfg_rsp_ready(authority_ack),.as_cfg_status(as_cfg_status),.as_busy(as_busy),.as_fault(as_fault),.as_drained(as_drained),.as_retired(as_retired),.as_rsp_generation(as_rsp_generation),.pc_acquire_valid(pc_acquire_valid),.pc_release_valid(label_root_release),.cp_valid(cap_path_valid),.cp_restore(cap_path_restore),.cp_rsp_ready(cap_path_rsp_ready),.cp_s_valid(warm_psv),.cp_s_last(warm_plast),.cp_m_ready(cap_path_m_ready),.cp_test_reset(1'b0),.cp_nodes(32'd9089009),.cp_nets(32'd27960),.cp_expected_crc(warm_pcrc),.cp_s_index(warm_pi),.cp_s_data(warm_pd),.cp_design(design_id),.qc_cmd_valid(qc_cmd_valid),.qc_cmd_ready(qc_cmd_ready),.qc_cmd_slot(qc_cmd_slot),.qc_cmd_cookie(qc_cmd_cookie),.qc_cmd_route_cookie(qc_cmd_route_cookie),.qc_cmd_source(qc_cmd_source),.qc_cmd_key(qc_cmd_key),.qc_cmd_nodes(qc_cmd_nodes),.qc_cmd_max_polls(qc_cmd_max_polls),.qc_cmd_poll_cookie(qc_cmd_poll_cookie),.qc_cmd_design(qc_cmd_design),.qc_cmd_query(qc_cmd_query),.qc_cmd_price(qc_cmd_price),.qc_cmd_expand(qc_cmd_expand),.qc_rsp_valid(qc_rsp_valid),.qc_rsp_ready(qc_rsp_ready),.qc_rsp_status(qc_rsp_status),.qc_rsp_detail(qc_rsp_detail),.qc_rsp_cookie(qc_rsp_cookie),.qc_rsp_nodes(qc_rsp_nodes),.qc_rsp_acked(qc_rsp_acked),.qc_rsp_committed(qc_rsp_committed),.qc_abort(qc_abort),.qc_busy(qc_busy),.qc_fault(qc_fault),.qc_phase(qc_phase),.qc_prepared_event(qc_prepared_event),.qc_prepare_acked(qc_prepare_acked),.qc_cleanup_acked(qc_cleanup_acked),.ss_start_ready(ss_start_ready),.ss_rsp_valid(ss_rsp_valid),.ss_rsp_status(ss_rsp_status),.ss_rsp_cookie(ss_rsp_cookie),.ss_polls(ss_polls),.ss_expands(ss_expands),.ss_candidates(ss_candidates),.ss_result_node(ss_result_node),.ss_result_key(ss_result_key),.ss_busy(ss_busy),.ss_fault(ss_fault),.ss_phase(ss_phase),.ss_poll_event(ss_poll_event),.ss_poll_node(ss_poll_node),.ss_poll_key(ss_poll_key),.ss_poll_size(ss_poll_size),.abort(abort),.busy(busy),.cc_busy(cc_busy),.cc_fault(cc_fault),.cf_fault(cf_fault),.clk(clk),.cost_lease(cost_lease),.cs_busy(cs_busy),.cs_configured(cs_configured),.cs_design_id(cs_design_id),.cs_editing(cs_editing),.cs_fault(cs_fault),.cs_m_araddr(cs_m_araddr),.cs_m_arburst(cs_m_arburst),.cs_m_arid(cs_m_arid),.cs_m_arlen(cs_m_arlen),.cs_m_arready(cs_m_arready),.cs_m_arsize(cs_m_arsize),.cs_m_arvalid(cs_m_arvalid),.cs_m_awaddr(cs_m_awaddr),.cs_m_awburst(cs_m_awburst),.cs_m_awid(cs_m_awid),.cs_m_awlen(cs_m_awlen),.cs_m_awready(cs_m_awready),.cs_m_awsize(cs_m_awsize),.cs_m_awvalid(cs_m_awvalid),.cs_m_bid(cs_m_bid),.cs_m_bready(cs_m_bready),.cs_m_bresp(cs_m_bresp),.cs_m_bvalid(cs_m_bvalid),.cs_m_rdata(cs_m_rdata),.cs_m_rid(cs_m_rid),.cs_m_rlast(cs_m_rlast),.cs_m_rready(cs_m_rready),.cs_m_rresp(cs_m_rresp),.cs_m_rvalid(cs_m_rvalid),.cs_m_wdata(cs_m_wdata),.cs_m_wlast(cs_m_wlast),.cs_m_wready(cs_m_wready),.cs_m_wstrb(cs_m_wstrb),.cs_m_wvalid(cs_m_wvalid),.cs_published_version(cs_published_version),.cs_ready_for_query(cs_ready_for_query),.d_configured(d_configured),.d_m_araddr(d_m_araddr),.d_m_arburst(d_m_arburst),.d_m_arid(d_m_arid),.d_m_arlen(d_m_arlen),.d_m_arready(d_m_arready),.d_m_arsize(d_m_arsize),.d_m_arvalid(d_m_arvalid),.d_m_awaddr(d_m_awaddr),.d_m_awburst(d_m_awburst),.d_m_awid(d_m_awid),.d_m_awlen(d_m_awlen),.d_m_awready(d_m_awready),.d_m_awsize(d_m_awsize),.d_m_awvalid(d_m_awvalid),.d_m_bid(d_m_bid),.d_m_bready(d_m_bready),.d_m_bresp(d_m_bresp),.d_m_bvalid(d_m_bvalid),.d_m_rdata(d_m_rdata),.d_m_rid(d_m_rid),.d_m_rlast(d_m_rlast),.d_m_rready(d_m_rready),.d_m_rresp(d_m_rresp),.d_m_rvalid(d_m_rvalid),.d_m_wdata(d_m_wdata),.d_m_wlast(d_m_wlast),.d_m_wready(d_m_wready),.d_m_wstrb(d_m_wstrb),.d_m_wvalid(d_m_wvalid),.design_id(design_id),.f_all_drained(f_all_drained),.f_backend_idle(f_backend_idle),.f_fault(f_fault),.f_normal_retired(f_normal_retired),.f_phase(f_phase),.f_recovery_owned(f_recovery_owned),.f_route_payload(f_route_payload),.f_sp(f_sp),.f_sr(f_sr),.f_srp(f_srp),.f_srr(f_srr),.f_srv(f_srv),.f_sv(f_sv),.fault(fault),.g_configured(g_configured),.g_m_araddr(g_m_araddr),.g_m_arburst(g_m_arburst),.g_m_arid(g_m_arid),.g_m_arlen(g_m_arlen),.g_m_arready(g_m_arready),.g_m_arsize(g_m_arsize),.g_m_arvalid(g_m_arvalid),.g_m_rdata(g_m_rdata),.g_m_rid(g_m_rid),.g_m_rlast(g_m_rlast),.g_m_rready(g_m_rready),.g_m_rresp(g_m_rresp),.g_m_rvalid(g_m_rvalid),.k_a_checkpoint(k_a_checkpoint),.k_a_cookie(k_a_cookie),.k_a_design(k_a_design),.k_a_net(k_a_net),.k_a_node(k_a_node),.k_a_occ(k_a_occ),.k_a_ready(k_a_ready),.k_a_refs(k_a_refs),.k_a_rsp_checkpoint(k_a_rsp_checkpoint),.k_a_rsp_cookie(k_a_rsp_cookie),.k_a_rsp_design(k_a_rsp_design),.k_a_rsp_ready(k_a_rsp_ready),.k_a_rsp_valid(k_a_rsp_valid),.k_a_status(k_a_status),.k_a_valid(k_a_valid),.k_busy(k_busy),.k_cold_rst(k_cold_rst),.k_corrected(k_corrected),.k_count(k_count),.k_fault(k_fault),.k_full(k_full),.k_permit(k_permit),.k_rec_ready(k_rec_ready),.k_rec_valid(k_rec_valid),.k_rsp_cookie(k_rsp_cookie),.k_rsp_ready(k_rsp_ready),.k_rsp_status(k_rsp_status),.k_rsp_valid(k_rsp_valid),.k_saved_checkpoint(k_saved_checkpoint),.k_saved_design(k_saved_design),.k_target_reset(k_target_reset),.lr_fault(lr_fault),.lr_rsp_status(lr_rsp_status),.lr_s_cookie(32'he0010001),.lr_s_last(lr_s_last),.lr_s_node(lr_s_node),.lr_s_payload(lr_s_payload),.lr_s_ready(lr_s_ready),.lr_s_valid(lr_s_valid),.lr_verified(lr_verified),.lr_written(lr_written),.operation_pending(operation_pending),.out_action(out_action),.out_attrs(out_attrs),.out_bits(out_bits),.out_commit_acked(out_commit_acked),.out_commit_payload(out_commit_payload),.out_commit_status(out_commit_status),.out_commit_valid(out_commit_valid),.out_config(out_config),.out_connection(out_connection),.out_cookie(out_cookie),.out_cost_geometry(out_cost_geometry),.out_cost_geometry_result(out_cost_geometry_result),.out_cost_packet(out_cost_packet),.out_cost_status(out_cost_status),.out_cost_valid(out_cost_valid),.out_cost_words(out_cost_words),.out_node(out_node),.out_offer_before(out_offer_before),.out_offer_key(out_offer_key),.out_offer_node(out_offer_node),.out_offer_size(out_offer_size),.out_offer_status(out_offer_status),.out_offer_valid(out_offer_valid),.out_params(out_params),.out_params_valid(out_params_valid),.out_position(out_position),.out_post_attrs(out_post_attrs),.out_post_distance(out_post_distance),.out_post_prev_read(out_post_prev_read),.out_post_status(out_post_status),.out_post_upstream(out_post_upstream),.out_post_valid(out_post_valid),.out_post_x(out_post_x),.out_post_y(out_post_y),.out_prep_count(out_prep_count),.out_prep_history(out_prep_history),.out_prep_net_data(out_prep_net_data),.out_prep_occupancy(out_prep_occupancy),.out_prep_price_index(out_prep_price_index),.out_prep_price_value(out_prep_price_value),.out_prep_status(out_prep_status),.out_prep_valid(out_prep_valid),.out_profile_revision(out_profile_revision),.out_ready(out_ready),.out_sequence(out_sequence),.out_services(out_services),.out_steps(out_steps),.out_valid(out_valid),.owner_configured(owner_configured),.owner_m_araddr(owner_m_araddr),.owner_m_arburst(owner_m_arburst),.owner_m_arid(owner_m_arid),.owner_m_arlen(owner_m_arlen),.owner_m_arready(owner_m_arready),.owner_m_arsize(owner_m_arsize),.owner_m_arvalid(owner_m_arvalid),.owner_m_awaddr(owner_m_awaddr),.owner_m_awburst(owner_m_awburst),.owner_m_awid(owner_m_awid),.owner_m_awlen(owner_m_awlen),.owner_m_awready(owner_m_awready),.owner_m_awsize(owner_m_awsize),.owner_m_awvalid(owner_m_awvalid),.owner_m_bid(owner_m_bid),.owner_m_bready(owner_m_bready),.owner_m_bresp(owner_m_bresp),.owner_m_bvalid(owner_m_bvalid),.owner_m_rdata(owner_m_rdata),.owner_m_rid(owner_m_rid),.owner_m_rlast(owner_m_rlast),.owner_m_rready(owner_m_rready),.owner_m_rresp(owner_m_rresp),.owner_m_rvalid(owner_m_rvalid),.owner_m_wdata(owner_m_wdata),.owner_m_wlast(owner_m_wlast),.owner_m_wready(owner_m_wready),.owner_m_wstrb(owner_m_wstrb),.owner_m_wvalid(owner_m_wvalid),.p_active(p_active),.p_active_price(p_active_price),.p_active_query(p_active_query),.p_m_araddr(p_m_araddr),.p_m_arburst(p_m_arburst),.p_m_arid(p_m_arid),.p_m_arlen(p_m_arlen),.p_m_arready(p_m_arready),.p_m_arsize(p_m_arsize),.p_m_arvalid(p_m_arvalid),.p_m_awaddr(p_m_awaddr),.p_m_awburst(p_m_awburst),.p_m_awid(p_m_awid),.p_m_awlen(p_m_awlen),.p_m_awready(p_m_awready),.p_m_awsize(p_m_awsize),.p_m_awvalid(p_m_awvalid),.p_m_bid(p_m_bid),.p_m_bready(p_m_bready),.p_m_bresp(p_m_bresp),.p_m_bvalid(p_m_bvalid),.p_m_rdata(p_m_rdata),.p_m_rid(p_m_rid),.p_m_rlast(p_m_rlast),.p_m_rready(p_m_rready),.p_m_rresp(p_m_rresp),.p_m_rvalid(p_m_rvalid),.p_m_wdata(p_m_wdata),.p_m_wlast(p_m_wlast),.p_m_wready(p_m_wready),.p_m_wstrb(p_m_wstrb),.p_m_wvalid(p_m_wvalid),.q_busy(q_busy),.q_configured(q_configured),.q_fault(q_fault),.q_m_araddr(q_m_araddr),.q_m_arburst(q_m_arburst),.q_m_arid(q_m_arid),.q_m_arlen(q_m_arlen),.q_m_arready(q_m_arready),.q_m_arsize(q_m_arsize),.q_m_arvalid(q_m_arvalid),.q_m_rdata(q_m_rdata),.q_m_rid(q_m_rid),.q_m_rlast(q_m_rlast),.q_m_rready(q_m_rready),.q_m_rresp(q_m_rresp),.q_m_rvalid(q_m_rvalid),.query_ready(query_ready),.query_version(query_version),.rc_block(rc_block),.rc_busy(rc_busy),.rc_fault(rc_fault),.rc_req_ready(rc_req_ready),.rc_req_valid(rc_req_valid),.rc_rsp_acked(rc_rsp_acked),.rc_rsp_cookie(rc_rsp_cookie),.rc_rsp_nodes(rc_rsp_nodes),.rc_rsp_ready(rc_rsp_ready),.rc_rsp_status(rc_rsp_status),.rc_rsp_valid(rc_rsp_valid),.rc_slots(rc_slots),.recover_checkpoint(g4_warm_mode?32'd20:(g3_warm_mode?32'd19:(wm_enable?32'd18:32'd17))),.recover_cookie(retry_cookie),.recover_design(design_id),.recover_price(as_recover_version[3:0]),.recover_query(as_recover_query),.recover_version(as_recover_version),.rst(rst),.snapshot_checkpoint(g4_warm_mode?32'd20:(g3_warm_mode?32'd19:(wm_enable?32'd18:32'd17))),.snapshot_cookie(32'he0010001),.snapshot_count(ls_count),.snapshot_design(design_id),.snapshot_nodes(32'd9089009),.snapshot_probe(32'd204279),.t_configured(t_configured),.t_m_araddr(t_m_araddr),.t_m_arburst(t_m_arburst),.t_m_arid(t_m_arid),.t_m_arlen(t_m_arlen),.t_m_arready(t_m_arready),.t_m_arsize(t_m_arsize),.t_m_arvalid(t_m_arvalid),.t_m_rdata(t_m_rdata),.t_m_rid(t_m_rid),.t_m_rlast(t_m_rlast),.t_m_rready(t_m_rready),.t_m_rresp(t_m_rresp),.t_m_rvalid(t_m_rvalid),.test_route_abort(injected_abort),.test_route_version_flip(injected_drift));

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
     if(!out_params_valid||out_connection!=selected_connection||out_params[127:96]!=selected_sink||out_config[31:0]!=selected_sequence||out_config[351:320]!=23||out_config[383:352]!=31||out_config[415:384]!=279||out_config[447:416]!=291)$fatal(1,"natural State/config");
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
  if(system.inner.c_rsp_payload[3:0]||system.inner.c_rsp_payload[35:4]!=100+expand_i)$fatal(1,"autonomous expand identity status=%0d cookie=%0d wanted=%0d payload=%h",system.inner.c_rsp_payload[3:0],system.inner.c_rsp_payload[35:4],100+expand_i,system.inner.c_rsp_payload);
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
  if((!injection_seen||replayed)&&(rc_rsp_status||rc_rsp_nodes!=3||rc_rsp_acked!=3))$fatal(1,"native route completion");
  $fdisplay(trace,"RC %0d %0d %0d %0d %0d",cycles,system.inner.backend.f_broute_payload[0],actual_route_slot,rc_rsp_nodes,rc_rsp_acked);route_commands<=route_commands+1;
 end
end
task fault_query;begin
 @(negedge clk);qc_cmd_cookie=32'h50000000+query_index;qc_cmd_source=66893;qc_cmd_key=0;qc_cmd_nodes=9089009;qc_cmd_max_polls=65536;
 qc_cmd_poll_cookie=32'hc0000000+poll_i;qc_cmd_design=design_id;qc_cmd_query=restore_epoch;qc_cmd_price=restore_version[3:0];
 qc_cmd_expand={restore_version,32'd291,32'd279,32'd31,32'd23,32'd260,selected_sequence,32'd26422,selected_sink,32'd0,32'd0,32'd0,32'(100+expand_i),selected_connection};
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
 @(negedge clk);qc_cmd_cookie=32'h50000000+query_index;qc_cmd_source=66893;qc_cmd_key=0;qc_cmd_nodes=9089009;qc_cmd_max_polls=65536;
 qc_cmd_poll_cookie=32'hc0000000+poll_i;qc_cmd_design=design_id;qc_cmd_query=restore_epoch;qc_cmd_price=restore_version[3:0];
 qc_cmd_expand={restore_version,32'd291,32'd279,32'd31,32'd23,32'd260,selected_sequence,32'd26422,selected_sink,32'd0,32'd0,32'd0,32'(100+expand_i),selected_connection};
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
 if(qc_rsp_status||!qc_rsp_committed||qc_prepare_acked!=4||qc_cleanup_acked!=1||qc_rsp_nodes!=3||qc_rsp_acked!=3||qc_rsp_cookie!=32'h50000000+query_index||ss_result_node!=selected_sink||qc_fault||ss_fault||ss_polls!=(query_index==0?171:(query_index==3?83:114))||ss_expands!=(query_index==0?170:(query_index==3?82:113))||ss_candidates!=(query_index==0?849:(query_index==1?564:(query_index==3?402:565))))$fatal(1,"autonomous query result status=%0d polls=%0d expands=%0d candidates=%0d",ss_rsp_status,ss_polls,ss_expands,ss_candidates);
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
always @(posedge clk)if(!rst&&qc_rsp_valid&&!qcp_active)begin
 if(system.inner.backend.dut.core.arb_g_busy||system.inner.backend.dut.core.arb_d_busy||system.inner.backend.dut.core.arb_io_busy||system.inner.backend.dut.core.pc_arb_busy||system.inner.backend.dut.core.capture_depth!=0||system.inner.backend.dut.core.g_rsp_valid||system.inner.backend.dut.core.d_rsp_valid||system.inner.backend.dut.core.b_result_valid||system.inner.backend.dut.core.ce_result_valid)$fatal(1,"query completed with internal ownership");
end
always @(posedge clk)if(!rst&&armed&&!injection_seen&&((g_m_rvalid&&g_m_rready&&g_m_rresp!=0)||(cs_m_rvalid&&cs_m_rready&&cs_m_rresp!=0)))
 $fdisplay(trace,"FAULT_OWNER %0d %0d %0d expand=%0d metadata=%0d coordinate=%0d controller=%0d",cycles,fault_case,eligible_responses,system.inner.backend.dut.core.expansion.state,system.inner.backend.dut.core.metadata.state,system.inner.backend.dut.core.coordinates.state,system.inner.backend.dut.core.controller.state);

initial begin
 trace=$fopen("natural_trace.txt","w");if(!trace)$fatal(1,"trace open");
 if(!$value$plusargs("costvectors=%s",path))$fatal(1,"cost path");fd_gold=$fopen(path,"r");
 if(!$value$plusargs("finallabels=%s",path))$fatal(1,"final path");finals_fd=$fopen(path,"r");

 if(!$value$plusargs("candidates=%s",path))$fatal(1,"candidate path");candidates_fd=$fopen(path,"r");
 if(!$value$plusargs("polls=%s",path))$fatal(1,"poll path");polls_fd=$fopen(path,"r");
 if(!fd_gold||!finals_fd||!candidates_fd||!polls_fd)$fatal(1,"oracle open");
 bench_rst=1;k_cold_rst=1;design_id=64'h123456789abcdef0;
 g_cfg_offsets_base=64'h1fffff000;g_cfg_edges_base=64'h10fffff000;g_cfg_attrs_base=64'h20fffff000;g_cfg_nodes=9089009;g_cfg_edges=40469536;
 d_cfg_base=64'h31fffff000;d_cfg_nodes=9089009;t_cfg_rows_base=64'h41fffff000;t_cfg_columns_base=64'h51fffff000;t_cfg_rows=311;t_cfg_columns=0;
 owner_cfg_primary=64'h61fffff000;owner_cfg_nodes=9089009;owner_cfg_capacity=53734;owner_cfg_pool=owner_cfg_primary+145424192;owner_cfg_allocator=owner_cfg_pool+859776;
 cs_cfg_history=64'h71fffff000;cs_cfg_prices=cs_cfg_history+36356096;cs_cfg_nets=cs_cfg_history+36357120;cs_cfg_nodes=9089009;cs_cfg_net_count=27960;cs_cfg_version=3;cs_cfg_design_id=design_id;
 q_cfg_base=64'h81fffff000;q_cfg_design=design_id;q_cfg_connections=180326;q_cfg_nodes=9089009;q_cfg_nets=27960;q_cfg_revision=1;
 repeat(5)@(negedge clk);bench_rst=0;k_cold_rst=0;
 as_fault_mode=$value$plusargs("authorityfault=%d",as_fault_mode);install_authority;install_checkpoint;install_config_snapshot;
 @(negedge clk);q_cfg_valid=1;do @(posedge clk);while(!q_cfg_ready);@(negedge clk);q_cfg_valid=0;wait(q_cfg_rsp_valid);@(negedge clk);if(q_cfg_status)$fatal(1,"boot config");q_cfg_rsp_ready=1;@(negedge clk);q_cfg_rsp_ready=0;
 @(negedge clk);g_cfg_valid=1;do @(posedge clk);while(!g_cfg_ready);@(negedge clk);g_cfg_valid=0;wait(g_cfg_rsp_valid);@(negedge clk);if(g_cfg_status)$fatal(1,"boot config");g_cfg_rsp_ready=1;@(negedge clk);g_cfg_rsp_ready=0;
 @(negedge clk);d_cfg_valid=1;do @(posedge clk);while(!d_cfg_ready);@(negedge clk);d_cfg_valid=0;wait(d_cfg_rsp_valid);@(negedge clk);if(d_cfg_status)$fatal(1,"boot config");d_cfg_rsp_ready=1;@(negedge clk);d_cfg_rsp_ready=0;
 @(negedge clk);t_cfg_valid=1;do @(posedge clk);while(!t_cfg_ready);@(negedge clk);t_cfg_valid=0;wait(t_cfg_rsp_valid);@(negedge clk);if(t_cfg_status)$fatal(1,"boot config");t_cfg_rsp_ready=1;@(negedge clk);t_cfg_rsp_ready=0;
 @(negedge clk);owner_cfg_valid=1;do @(posedge clk);while(!owner_cfg_ready);@(negedge clk);owner_cfg_valid=0;wait(owner_cfg_rsp_valid);@(negedge clk);if(owner_cfg_status)$fatal(1,"boot config");owner_cfg_rsp_ready=1;@(negedge clk);owner_cfg_rsp_ready=0;
 @(negedge clk);cs_cfg_valid=1;do @(posedge clk);while(!cs_cfg_ready);@(negedge clk);cs_cfg_valid=0;wait(cs_cfg_rsp_valid);@(negedge clk);if(cs_cfg_status)$fatal(1,"boot config");cs_cfg_rsp_ready=1;@(negedge clk);cs_cfg_rsp_ready=0;
 baseline_configure;control(0);
 $fdisplay(trace,"BASELINE_NO_PRELOAD %0d",cycles);



 control(1);
 @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;
 ap_get(208292,6632,64'h100000001,0,1,2);ap_get(208292,17601,64'h100000001,0,2,2);ap_get(558358,23916,64'h100000001,0,1,2);
 @(negedge clk);pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;wait(!pc_owned);
 query_index=0;replayed=1;armed=0;
 autonomous_query;
 if(commits!=421||candidate_i!=849||expand_i!=170||poll_i!=171||count1!=3||k_count!=3||rc_slots!=1)$fatal(1,"iter2 query aggregate");
 stage_no=0;owner_op(0,339193,1,1);owner_op(0,558358,4,2);owner_op(0,265324,5,1);
 iter2_foreign_probe;
 iter2_prepare_continuous;
 iter2_publish_g2;
 iter2_next_query;control(1);
 $fdisplay(trace,"BASELINE_WARM_DONE %0d",cycles);
 cumulative_g3_copy;
 publish_g3;
 third_query;
 cumulative_g4_copy;
 publish_g4;
 fourth_query;
 $fdisplay(trace,"ITER2_CONTINUOUS_PREP_PASS %0d",cycles);$fflush(trace);$fclose(trace);$display("ITER2_CONTINUOUS_PREP_PASS");$finish;

end

task ap_get(input[31:0]node,net,input[63:0]generation,input[3:0]status,input[31:0]refs,occ);begin
 @(negedge clk);ap_node=node;ap_net=net;ap_generation=generation;ap_cookie=ap_cookie+1;ap_valid=1;
 do @(posedge clk);while(!ap_ready);@(negedge clk);ap_valid=0;
 wait(ap_rsp_valid);repeat(8)begin @(negedge clk);if(!ap_rsp_valid||ap_status!=status||ap_refs!=refs||ap_occ!=occ||ap_rsp_cookie!=ap_cookie||ap_rsp_checkpoint!=k_saved_checkpoint||ap_rsp_generation!=as_bound_generation||ap_rsp_design!=design_id||pc_release_ready||!pc_owned)$fatal(1,"native authority inspection");end
 ap_rsp_ready=1;@(negedge clk);ap_rsp_ready=0;
end endtask
always @(posedge clk)if(!rst&&!k_cold_rst)begin
 if(ap_valid&&ap_ready)$fdisplay(trace,"APQ %0d %0d %0d %016h %0d",cycles,ap_node,ap_net,ap_generation,ap_cookie);
 if(ap_rsp_valid&&ap_rsp_ready)$fdisplay(trace,"APR %0d %0d %0d %0d %016h %0d",cycles,ap_status,ap_refs,ap_occ,ap_rsp_generation,ap_rsp_cookie);
end

task joint_commit_check;reg[1:0]accepted;begin
 joint_started=1;
 @(negedge clk);jp_start=1;do @(posedge clk);while(!jp_start_ready);@(negedge clk);jp_start=0;
 jp_authority_stage=1;authority_bind=1;do @(posedge clk);while(!as_cfg_ready);@(negedge clk);authority_bind=0;
 wait(as_cfg_rsp_valid);repeat(8)begin @(negedge clk);if(as_cfg_status||system.jp_ap||as_bound_generation!=64'h100000001||k_count!=6||pc_release_ready)$fatal(1,"held authority candidate");end
 authority_ack=1;@(negedge clk);authority_ack=0;wait(system.jp_ap);
 jp_load=3;while(jp_load!=0)begin @(posedge clk);accepted=jp_load&jp_ready;@(negedge clk);jp_load=jp_load&~accepted;end
 wait(jp_reply==3);repeat(8)begin @(negedge clk);if(jp_status||pc_release_ready||system.jp_prepared||k_count!=6||k_saved_checkpoint!=17)$fatal(1,"held commit stage reply");end
 jp_ack=3;@(negedge clk);jp_ack=0;wait(system.jp_prepared==3);
 if(as_bound_generation!=64'h100000001||k_count!=6||k_saved_checkpoint!=17||system.jp_ccp!=17)$fatal(1,"prepared metadata changed baseline");
 jp_commit=1;do @(posedge clk);while(!jp_commit_ready);@(negedge clk);jp_commit=0;
 wait(jp_done);repeat(8)begin @(negedge clk);if(jp_result||pc_release_ready||k_count||k_saved_checkpoint!=18||system.jp_ccp!=18||as_bound_generation!=64'h100000002||joint_pulses!=1)$fatal(1,"joint publication mismatch");end
 jp_done_ready=1;@(negedge clk);jp_done_ready=0;wait(!jp_owned);jp_authority_stage=0;
 if(!k_permit||!system.pc_safe||rc_slots!=1||system.controller.last_sequence!=1)$fatal(1,"publication lost working state");
 ap_get(0,4754,64'h100000001,1,0,0);
 for(integer x=0;x<6;x=x+1)ap_get(cap_path_image[7+x],2717,64'h100000002,0,1,1);
 ap_get(0,4754,64'h100000002,0,1,1);
 // Old-generation ledger cannot be imported under newly active authority.
 qc_cp_expected_crc=qc_cp_crc;qcp_load(1);if(!qc_restore_pending||system.controller.last_sequence!=1)$fatal(1,"stale ledger accepted");
 qc_cp_generation=0;qcp_start(0);
 for(integer x=0;x<10;x=x+1)begin
  wait(qc_cp_m_valid);@(negedge clk);if(qc_cp_m_index!=x||qc_cp_m_last!=(x==9))$fatal(1,"new ledger boundary");qcp_image[x]=qc_cp_m_data;qc_cp_m_ready=1;@(negedge clk);qc_cp_m_ready=0;
 end
 qcp_result(0);if({qcp_image[5],qcp_image[4]}!=64'h100000002||qcp_image[8]!=1)$fatal(1,"new ledger identity");
 qc_cp_expected_crc=qc_cp_crc;qcp_load(0);if(qc_restore_pending||system.controller.last_sequence!=1)$fatal(1,"new ledger restore");
 @(negedge clk);pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;wait(!pc_owned);
 $fdisplay(trace,"JOINT_SYSTEM_COMMIT %0d %0d %0d %016h",cycles,k_saved_checkpoint,k_count,as_bound_generation);$fflush(trace);$display("JOINT_PUBLICATION_OBSERVED checkpoint=%0d",k_saved_checkpoint);
 // Continue from the restored first branch using the existing independent q2 oracle.
 count1=6;for(integer x=0;x<6;x=x+1)saved1[x]=cap_path_image[7+x];stage_no=0;probe_owners;
 $fclose(fd_gold);$fclose(candidates_fd);$fclose(polls_fd);$fclose(finals_fd);
 if(!$value$plusargs("cost2=%s",path))$fatal(1,"cost2");fd_gold=$fopen(path,"r");
 if(!$value$plusargs("candidates2=%s",path))$fatal(1,"candidates2");candidates_fd=$fopen(path,"r");
 if(!$value$plusargs("polls2=%s",path))$fatal(1,"polls2");polls_fd=$fopen(path,"r");
 if(!$value$plusargs("finals2=%s",path))$fatal(1,"finals2");finals_fd=$fopen(path,"r");
 if(!fd_gold||!candidates_fd||!polls_fd||!finals_fd)$fatal(1,"q2 oracle open");
 poll_i=0;expand_i=0;candidate_i=0;commits=0;offers=0;outputs=0;physical_expands=0;metadata_calls=0;visited_reads=0;
 query_index=1;selected_sink=128009;selected_connection=16497;selected_sequence=2;stopped=0;
 warm_fault_and_restore;
 autonomous_query;
 for(final_index=0;final_index<328;final_index=final_index+1)begin
  rc=$fscanf(finals_fd,"%d",final_node_id);if(rc!=1)$fatal(1,"final node");
  for(j=0;j<5;j=j+1)begin rc=$fscanf(finals_fd,"%h",word);if(rc!=1)$fatal(1,"final word");gold_final[j*32+:32]=word;end
  if(final_node_id==selected_sink)gold_final[159:128]=0;
  label_read(final_node_id);if(host_record!==gold_final)$fatal(1,"q2 final label %0d",final_node_id);
 end
 stage_no=1;probe_owners;
 stage_no=2;route_command(1,0,150697,1);probe_owners;
 stage_no=3;route_command(1,1,128009,2);probe_owners;
 if(rc_slots!=0||count1!=6||count2!=6||rc_fault||poll_i!=43||expand_i!=42||candidate_i!=176)$fatal(1,"cold q2 final totals");
 control(1);control(2);wait(f_normal_retired&&f_backend_idle&&f_all_drained&&f_phase==0);
 $fdisplay(trace,"JOINT_SYSTEM_Q2_PASS %0d %0d %0d %0d",cycles,poll_i,expand_i,candidate_i);$display("JOINT_SYSTEM_COMMIT_PASS reads=%0d polls=%0d expands=%0d candidates=%0d",as_rbeats,poll_i,expand_i,candidate_i);
end endtask

task joint_cancel_check;reg[1:0]accepted;begin
 if(!pc_owned||k_count!=6||k_saved_checkpoint!=17)$fatal(1,"joint baseline");
 @(negedge clk);jp_start=1;do @(posedge clk);while(!jp_start_ready);@(negedge clk);jp_start=0;
 if(!jp_owned)$fatal(1,"joint ownership");
 @(negedge clk);jp_load=3;
 while(jp_load!=0)begin @(posedge clk);accepted=jp_load&jp_ready;@(negedge clk);jp_load=jp_load&~accepted;end
 wait(jp_reply==3);repeat(8)begin @(negedge clk);if(jp_status||pc_release_ready||system.jp_prepared||k_count!=6||k_saved_checkpoint!=17)$fatal(1,"held stage reply");end
 jp_ack=3;@(negedge clk);jp_ack=0;
 wait(system.jp_prepared==3);
 if(k_permit||pc_release_ready||!pc_owned||system.jp_commit_ready)$fatal(1,"stage admission");
 // Native stream request must remain unaccepted while metadata transaction owns lease.
 cap_path_valid=1;qc_cp_valid=1;
 repeat(8)begin @(negedge clk);if(cap_path_ready||qc_cp_ready||cap_path_busy||qc_cp_busy)$fatal(1,"stream overlap accepted");end
 cap_path_valid=0;qc_cp_valid=0;
 jp_cancel=1;do @(posedge clk);while(!jp_cancel_ready);@(negedge clk);jp_cancel=0;
 wait(jp_done);repeat(8)begin @(negedge clk);if(jp_result!=2||pc_release_ready||k_count!=6||k_saved_checkpoint!=17||system.jp_prepared||system.as_bound_generation!=64'h100000001)$fatal(1,"cancel did not preserve state");end
 jp_done_ready=1;@(negedge clk);jp_done_ready=0;
 wait(!jp_owned);if(!k_permit||!system.pc_safe)$fatal(1,"cancel work permission not restored");
 $fdisplay(trace,"JOINT_SYSTEM_CANCEL %0d %0d %0d",cycles,k_count,k_saved_checkpoint);
 $display("JOINT_SYSTEM_CANCEL_PASS journal=%0d checkpoint=%0d",k_count,k_saved_checkpoint);
end endtask

always @(posedge clk)if(!rst&&!k_cold_rst)begin
 if(joint_started)begin joint_watch=joint_watch+1;if(joint_watch>1800000)$fatal(1,"joint watchdog state=%0d cp=%0d j=%0d prepared=%b ready=%b lease=%b",system.publication.state,k_saved_checkpoint,k_count,{system.jp_prepared,system.jp_ap},{system.jp_pubready,system.jp_apr},pc_owned);end
 if(jp_start&&jp_start_ready)$fdisplay(trace,"JS %0d %0d %0d %0d %0d %0d",cycles,k_saved_checkpoint,k_count,query_version,system.jp_cver,pc_owned);
 if(system.jp_prepare&&system.jp_load[0]&&system.inner.backend.jp_kr)$fdisplay(trace,"JK %0d %0d %0d",cycles,system.jp_checkpoint,system.jp_version);
 if(system.jp_prepare&&system.jp_load[1]&&system.inner.backend.jp_cr)$fdisplay(trace,"JC %0d %0d %0d",cycles,system.jp_checkpoint,system.jp_version);
 if(jp_reply[0]&&jp_ack[0])$fdisplay(trace,"JKR %0d %0d %0d %0d",cycles,jp_status[0],k_saved_checkpoint,k_count);
 if(jp_reply[1]&&jp_ack[1])$fdisplay(trace,"JCR %0d %0d %0d",cycles,jp_status[1],system.jp_ccp);
 if(jp_cancel&&jp_cancel_ready)$fdisplay(trace,"JX %0d %0d",cycles,system.jp_prepared);
 if(|system.jp_dv)$fdisplay(trace,"JD %0d %0d %0d",cycles,system.jp_dv,{system.jp_dropready,system.jp_adr});
 if(|system.jp_pv)begin joint_pulses=joint_pulses+1;$fdisplay(trace,"JP %0d %0d %0d %0d %0d %016h",cycles,system.jp_pv,k_saved_checkpoint,system.jp_ccp,k_count,as_bound_generation);end
 if(authority_bind&&as_cfg_ready)$fdisplay(trace,"JAS %0d %0d %016h %0d",cycles,jp_authority_stage,system.as_cfg_generation,system.as_cfg_checkpoint);
 if(as_cfg_rsp_valid&&authority_ack)$fdisplay(trace,"JAR %0d %0d %016h",cycles,as_cfg_status,as_bound_generation);
 if(jp_done&&jp_done_ready)$fdisplay(trace,"JE %0d %0d %0d %0d %0d %0d",cycles,jp_result,k_saved_checkpoint,k_count,system.jp_ccp,pc_owned);
 if(jp_owned&&(!pc_owned||pc_release_ready))$fatal(1,"unexpected publication or lost lease in cancel case");
end

always @(posedge clk)if(!k_cold_rst&&!rst)begin if(system.boot_pending||system.boot_rsp_valid)$fatal(1,"normal start entered bootstrap");end

task warm_fault_and_restore;begin
 wm_enable=1;as_recover_version=5;as_recover_query=3;recovering=0;replayed=0;injection_seen=0;armed=1;warm_running=1;
 $fdisplay(trace,"WARM_FAULT_START %0d %0d %0d",cycles,k_saved_checkpoint,k_count);
 fault_query;
 q_cfg_valid=0;g_cfg_valid=0;d_cfg_valid=0;t_cfg_valid=0;owner_cfg_valid=0;cs_cfg_valid=0;host_ctrl_valid=0;host_design_req_valid=0;host_io_valid=0;host_owner_req_valid=0;cc_req_valid=0;expand_valid=0;seed_valid=0;cs_req_valid=0;k_cfg_valid=0;cf_load_valid=0;rc_req_valid=0;
 recovering=1;armed=0;injected_abort=0;injected_drift=0;as_inject=0;k_rec_valid=1;
 do @(posedge clk);while(!k_rec_ready);@(negedge clk);k_rec_valid=0;
 wait(k_rcfg_valid);@(negedge clk);restore_epoch=k_new_query;restore_version=k_new_version;
 wait(k_labels_valid);@(negedge clk);if(k_saved_checkpoint!=18||as_bound_generation!=64'h100000002||!wm_owned||wm_fault||pc_owned)$fatal(1,"warm repair binding");
 $fdisplay(trace,"WARM_OWNER_REPAIRED %0d %0d %0d",cycles,k_corrected,k_count);
 for(integer x=0;x<328;x=x+1)begin
  @(negedge clk);lr_s_valid=1;lr_s_node=warm_nodes[x];lr_s_payload=warm_values[x];lr_s_last=x==327;do @(posedge clk);while(!lr_s_ready);@(negedge clk);lr_s_valid=0;
 end
 wait(wm_receipts[0]);repeat(12)begin @(negedge clk);if(wm_joined||k_rsp_valid||k_permit||!wm_owned||wm_fault||lr_busy)$fatal(1,"label-only completion admitted work");end
 cap_path_restore=1;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<156;x=x+1)begin
  @(negedge clk);warm_pi=x;warm_pd=cap_path_image[x];warm_plast=x==155;warm_psv=1;do @(posedge clk);while(!system.cp_s_ready);@(negedge clk);warm_psv=0;
 end
 wait(cap_path_rsp_valid);repeat(8)begin @(negedge clk);if(cap_path_status||wm_receipts!=1||wm_joined||k_rsp_valid||pc_owned)$fatal(1,"warm path held");end cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
 qc_cp_restore=1;qc_cp_expected_crc=warm_qcrc;qc_cp_valid=1;do @(posedge clk);while(!qc_cp_ready);@(negedge clk);qc_cp_valid=0;
 for(integer x=0;x<9;x=x+1)begin
  @(negedge clk);qc_cp_s_index=x;qc_cp_s_data=qcp_image[x];qc_cp_s_last=x==9;qc_cp_s_valid=1;do @(posedge clk);while(!qc_cp_s_ready);@(negedge clk);qc_cp_s_valid=0;
 end
 cancel_started=1;@(negedge clk);abort=1;
 wait(qc_cp_rsp_valid);repeat(8)begin @(negedge clk);
  $fdisplay(trace,"CANCEL_HELD %0d %0d %0d %0d %0d %0d",cycles,qc_cp_status,k_rsp_valid,k_rsp_status,wm_owned,wm_fault);
  if(qc_cp_status!=2||!wm_owned||!wm_fault||k_rsp_valid||qc_cmd_ready||rc_req_ready||pc_acquire_ready)$fatal(1,"warm failure completed before query reply retirement");
 end
 qc_cp_rsp_ready=1;@(negedge clk);qc_cp_rsp_ready=0;
 for(integer waited=0;waited<2048&&!k_rsp_valid;waited=waited+1)@(negedge clk);
 if(!k_rsp_valid)begin $fflush(trace);$fatal(1,"cancel completion stuck coordinator=%0d wm_retired=%0d query_busy=%0d",system.inner.backend.recovery_ctl.state,system.wm_retired,qc_cp_busy);end
 repeat(8)begin @(negedge clk);if(k_rsp_status==0||!wm_owned||!wm_fault||recover_open||!system.wm_retired)$fatal(1,"cancel completion quarantine");end
 $fdisplay(trace,"CANCEL_COMPLETE %0d %0d %0d %0d",cycles,k_rsp_status,k_count,k_saved_checkpoint);
 k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;abort=0;repeat(8)begin @(negedge clk);if(!wm_owned||!wm_fault||recover_open||qc_cmd_ready||rc_req_ready||pc_acquire_ready)$fatal(1,"cancel opened work");end
 // Reject the already-used attempt through the real native reply path.
 retry_started=1;retry_cookie=32'hc0020000;k_rec_valid=1;
 do @(posedge clk);while(!k_rec_ready);@(negedge clk);k_rec_valid=0;
 wait(k_rsp_valid);repeat(8)begin @(negedge clk);if(k_rsp_status!=1||k_rsp_cookie!=retry_cookie||k_count!=6||!wm_owned||!wm_fault)$fatal(1,"same-attempt native rejection");end
 $fdisplay(trace,"RETRY_REJECT %0d %0d %0d %08h",cycles,k_rsp_status,k_count,k_rsp_cookie);
 k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;repeat(8)@(negedge clk);
 as_recover_version=6;as_recover_query=0;retry_cookie=32'hc0020001;
 $fdisplay(trace,"RETRY_START %0d %0d %0d %08h",cycles,as_recover_version,k_count,retry_cookie);
 recovering=1;armed=0;injected_abort=0;injected_drift=0;as_inject=0;k_rec_valid=1;
 do @(posedge clk);while(!k_rec_ready);@(negedge clk);k_rec_valid=0;
 wait(k_rcfg_valid);@(negedge clk);restore_epoch=k_new_query;restore_version=k_new_version;
 wait(k_labels_valid);@(negedge clk);if(k_saved_checkpoint!=18||as_bound_generation!=64'h100000002||!wm_owned||wm_fault||pc_owned)$fatal(1,"warm repair binding");
 $fdisplay(trace,"WARM_OWNER_REPAIRED %0d %0d %0d",cycles,k_corrected,k_count);
 for(integer x=0;x<328;x=x+1)begin
  @(negedge clk);lr_s_valid=1;lr_s_node=warm_nodes[x];lr_s_payload=warm_values[x];lr_s_last=x==327;do @(posedge clk);while(!lr_s_ready);@(negedge clk);lr_s_valid=0;
 end
 wait(wm_receipts[0]);repeat(12)begin @(negedge clk);if(wm_joined||k_rsp_valid||k_permit||!wm_owned||wm_fault||lr_busy)$fatal(1,"label-only completion admitted work");end
 cap_path_restore=1;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<156;x=x+1)begin
  @(negedge clk);warm_pi=x;warm_pd=cap_path_image[x];warm_plast=x==155;warm_psv=1;do @(posedge clk);while(!system.cp_s_ready);@(negedge clk);warm_psv=0;
 end
 wait(cap_path_rsp_valid);repeat(8)begin @(negedge clk);if(cap_path_status||wm_receipts!=1||wm_joined||k_rsp_valid||pc_owned)$fatal(1,"warm path held");end cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
 qc_cp_restore=1;qc_cp_expected_crc=warm_qcrc;qc_cp_valid=1;do @(posedge clk);while(!qc_cp_ready);@(negedge clk);qc_cp_valid=0;
 for(integer x=0;x<10;x=x+1)begin
  @(negedge clk);qc_cp_s_index=x;qc_cp_s_data=qcp_image[x];qc_cp_s_last=x==9;qc_cp_s_valid=1;do @(posedge clk);while(!qc_cp_s_ready);@(negedge clk);qc_cp_s_valid=0;
 end
 wait(qc_cp_rsp_valid);repeat(8)begin @(negedge clk);if(qc_cp_status||wm_receipts!=3||wm_joined||k_rsp_valid||pc_owned)$fatal(1,"warm query held");end qc_cp_rsp_ready=1;@(negedge clk);qc_cp_rsp_ready=0;
 wait(k_rsp_valid);repeat(8)begin @(negedge clk);if(k_rsp_status||k_rsp_cookie!=retry_cookie||k_corrected!=0||k_count||!wm_joined||!wm_owned||wm_fault||recover_open||rc_slots!=1||system.controller.last_sequence!=1||system.controller.last_version!=6)$fatal(1,"warm complete join");end
 $fdisplay(trace,"WARM_COMPLETE %0d %0d %0d %0d %0d",cycles,k_rsp_status,k_corrected,rc_slots,system.controller.last_sequence);
 k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;wait(recover_open);if(wm_owned||wm_fault||!k_permit||query_version!=6||p_active_query!=0||p_active_price!=6)$fatal(1,"warm release");
 // Restore only verification cursors, never DUT path/owner state.
 count1=6;count2=0;for(integer x=0;x<6;x=x+1)saved1[x]=cap_path_image[7+x];
 rc=$fseek(polls_fd,0,0);if(rc)$fatal(1,"poll rewind");rc=$fseek(candidates_fd,0,0);if(rc)$fatal(1,"candidate rewind");rc=$fseek(fd_gold,0,0);if(rc)$fatal(1,"cost rewind");rc=$fseek(finals_fd,0,0);if(rc)$fatal(1,"final rewind");
 poll_i=0;expand_i=0;candidate_i=0;commits=0;outputs=0;offers=0;physical_expands=0;metadata_calls=0;visited_reads=0;stopped=0;replayed=1;warm_running=0;
 $fdisplay(trace,"WARM_RETRY %0d %0d %0d",cycles,restore_epoch,restore_version);$fflush(trace);$display("WARM_RESTORE_OBSERVED checkpoint=%0d",k_saved_checkpoint);
end endtask
always @(posedge clk)if(!k_cold_rst)begin
 if(system.wm_rec_accept&&wm_enable)$fdisplay(trace,"WA %0d %0d %0d",cycles,system.wm_on,pc_owned);
 if(system.wm_label_done&&wm_owned)$fdisplay(trace,"WL %0d %0d %0d %0d",cycles,lr_rsp_status,lr_written,lr_verified);
 if(wm_owned&&((wm_fault&&!cancel_started&&!bad_crc)||qc_cmd_ready||rc_req_ready||pc_acquire_ready))$fatal(1,"warm exclusive owner");
 if(wm_owned&&cap_path_valid&&cap_path_ready)$fdisplay(trace,"WP %0d",cycles);
 if(wm_owned&&cap_path_rsp_valid&&cap_path_rsp_ready)$fdisplay(trace,"WPR %0d %0d %08h",cycles,cap_path_status,cap_path_crc);
 if(wm_owned&&qc_cp_valid&&qc_cp_ready)$fdisplay(trace,"WQ %0d",cycles);
 if(wm_owned&&qc_cp_rsp_valid&&qc_cp_rsp_ready)$fdisplay(trace,"WQR %0d %0d %08h",cycles,qc_cp_status,qc_cp_crc);
end


always @(posedge clk)if(!rst&&wm_enable&&armed&&!injection_seen&&owner_m_bvalid&&owner_m_bready)
 $fdisplay(trace,"SHARED_B %0d %0d %0d %0d",cycles,b_o_node,owner_m_bresp,k_count);
always @(posedge clk)if(retry_started&&(k_cold_rst||bench_rst))$fatal(1,"retry performed cold reset");
task iter2_foreign_probe;begin
 @(negedge clk);host_owner_req_op=0;host_owner_req_node=558358;host_owner_req_net=23916;host_owner_req_cookie=32'hef000001;host_owner_req_valid=1;
 do @(posedge clk);while(!host_owner_req_ready);@(negedge clk);host_owner_req_valid=0;
 wait(host_owner_rsp_valid);@(negedge clk);if(host_owner_rsp_status||host_owner_rsp_count!=1||host_owner_rsp_occupancy!=2)$fatal(1,"foreign net damaged");
 $fdisplay(trace,"ITER2_FOREIGN %0d %0d %0d",cycles,host_owner_rsp_count,host_owner_rsp_occupancy);host_owner_rsp_ready=1;@(negedge clk);host_owner_rsp_ready=0;
end endtask
task iter2_sequence_reject;begin
 @(negedge clk);qc_cmd_cookie=32'hce000002;qc_cmd_source=66893;qc_cmd_key=0;qc_cmd_nodes=9089009;qc_cmd_max_polls=65536;qc_cmd_poll_cookie=32'hcf000002;qc_cmd_design=design_id;qc_cmd_query=1;qc_cmd_price=3;
 qc_cmd_expand={32'd3,32'd291,32'd279,32'd31,32'd23,32'd260,32'd180327,32'd26422,32'd204279,32'd0,32'd0,32'd0,32'd100,32'd170782};qc_cmd_slot=0;qc_cmd_route_cookie=32'hcf000003;
 qc_cmd_valid=1;do @(posedge clk);while(!qc_cmd_ready);@(negedge clk);qc_cmd_valid=0;
 wait(qc_rsp_valid);repeat(8)begin @(negedge clk);if(qc_rsp_status!=1||qc_rsp_committed||qc_prepare_acked||qc_cleanup_acked||qc_fault||ss_busy||rc_slots||k_count!=3)$fatal(1,"iter2 duplicate sequence admitted");end
 $fdisplay(trace,"ITER2_SEQUENCE_REJECT %0d %0d %0d %0d",cycles,qc_rsp_status,qc_prepare_acked,system.controller.last_sequence);
 qc_rsp_ready=1;@(negedge clk);qc_rsp_ready=0;wait(!qc_busy);
end endtask
function [31:0] prep_crc_word(input [31:0] crc,data);reg[31:0] c;integer b;begin c=crc;for(b=0;b<32;b=b+1)begin if(c[0]^data[b])c=(c>>1)^32'hedb88320;else c=c>>1;end prep_crc_word=c;end endfunction
reg[31:0]prep_crc;
task iter2_prepare_continuous;begin
 @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;
 cap_path_restore=0;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<156;x=x+1)begin
  wait(cap_path_m_valid);@(negedge clk);if(cap_path_m_index!=x||cap_path_m_last!=(x==155))$fatal(1,"prep export boundary");cap_path_image[x]=cap_path_m_data;cap_path_m_ready=1;@(negedge clk);cap_path_m_ready=0;
 end
 wait(cap_path_rsp_valid);@(negedge clk);if(cap_path_status||cap_path_image[0]!=1||cap_path_image[1]!=3||cap_path_image[39]!=0)$fatal(1,"prep initial slots");cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
 // Slot0 comes unmodified from the real committed-path export. Slot1 is the observed historical path.
 cap_path_image[39]=1;cap_path_image[40]=3;cap_path_image[41]=26422;cap_path_image[42]=66893;cap_path_image[43]=67922;cap_path_image[44]=design_id[31:0];cap_path_image[45]=design_id[63:32];
 cap_path_image[46]=990179;cap_path_image[47]=558358;cap_path_image[48]=265324;
 prep_crc=32'hffffffff;for(integer x=0;x<156;x=x+1)prep_crc=prep_crc_word(prep_crc,cap_path_image[x]);warm_pcrc=~prep_crc;
 cap_path_restore=1;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<156;x=x+1)begin
  @(negedge clk);warm_pi=x;warm_pd=cap_path_image[x];warm_plast=x==155;warm_psv=1;do @(posedge clk);while(!system.cp_s_ready);@(negedge clk);warm_psv=0;
  $fdisplay(trace,"PREP_PATH_IMPORT %0d %08h",x,cap_path_image[x]);
 end
 wait(cap_path_rsp_valid);@(negedge clk);if(cap_path_status||cap_path_crc!=warm_pcrc||rc_slots!=3)$fatal(1,"prep historical import");cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
 pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;wait(!pc_owned);
 stage_no=4;owner_op(0,990179,2,2);route_command(1,1,67922,180328);
 owner_op(0,990179,1,2);owner_op(0,339193,1,1);owner_op(0,558358,3,2);owner_op(0,265324,4,1);iter2_foreign_probe;
 if(rc_slots!=1||system.controller.last_sequence!=180327||fault||rc_fault||k_fault||!f_all_drained||!f_backend_idle)$fatal(1,"prep continuous state");
 $fdisplay(trace,"PREP_CONTINUITY %0d %0d %0d %0d",cycles,rc_slots,k_count,system.controller.last_sequence);
end endtask

task iter2_next_query;begin
 $fdisplay(trace,"ITER2_NEXT_BEGIN %0d",cycles);
 $fclose(fd_gold);$fclose(candidates_fd);$fclose(polls_fd);$fclose(finals_fd);
 if(!$value$plusargs("cost2=%s",path))$fatal(1,"cost2");fd_gold=$fopen(path,"r");
 if(!$value$plusargs("candidates2=%s",path))$fatal(1,"candidates2");candidates_fd=$fopen(path,"r");
 if(!$value$plusargs("polls2=%s",path))$fatal(1,"polls2");polls_fd=$fopen(path,"r");
 if(!$value$plusargs("finals2=%s",path))$fatal(1,"finals2");finals_fd=$fopen(path,"r");
 if(!fd_gold||!candidates_fd||!polls_fd||!finals_fd)$fatal(1,"next oracle open");
 poll_i=0;expand_i=0;candidate_i=0;commits=0;offers=0;outputs=0;physical_expands=0;metadata_calls=0;visited_reads=0;
 query_index=1;selected_sink=67922;selected_connection=170996;selected_sequence=180328;stopped=0;
 replayed=0;armed=1;injection_seen=0;fault_case=5;wm_enable=1;warm_fault_node=558358;warm_running=1;
 fault_query;
 iter2_g2_warm_restore;
 autonomous_query;
 if(commits!=302||candidate_i!=564||expand_i!=113||poll_i!=114||rc_slots!=3||system.controller.last_sequence!=180328||system.controller.last_version!=5||p_active_query!=3||p_active_price!=5)$fatal(1,"next aggregate/context");
 stage_no=5;owner_op(0,339193,1,1);owner_op(0,990179,2,2);owner_op(0,558358,4,2);owner_op(0,265324,5,1);iter2_foreign_probe;
 $fdisplay(trace,"ITER2_PAIR_PASS %0d %0d %0d %0d %0d",cycles,poll_i,expand_i,candidate_i,commits);$display("ITER2_PAIR_PASS polls=114 expands=113 candidates=564 costs=302");
end endtask

task iter2_export_query;begin
 qcp_start(0);
 for(integer x=0;x<10;x=x+1)begin
  wait(qc_cp_m_valid);@(negedge clk);if(qc_cp_m_index!=x||qc_cp_m_last!=(x==9))$fatal(1,"g2 ledger boundary");qcp_image[x]=qc_cp_m_data;qc_cp_m_ready=1;@(negedge clk);qc_cp_m_ready=0;
 end
 qcp_result(0);if(qcp_image[8]!=(g4_phase ? 180329 : (g3_phase ? 180328 : 180327)))$fatal(1,"ledger floor");
end endtask
task iter2_publish_g2;reg[1:0]accepted;begin
 $fdisplay(trace,"DEMAND_LABEL_SOURCE %0d",cycles);
 control(1);
 @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;
 runtime_owner_snapshot;
 runtime_label_snapshot;
 cap_path_restore=0;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<156;x=x+1)begin
  wait(cap_path_m_valid);@(negedge clk);if(cap_path_m_index!=x||cap_path_m_last!=(x==155))$fatal(1,"g2 path export");cap_path_image[x]=cap_path_m_data;cap_path_m_ready=1;@(negedge clk);cap_path_m_ready=0;
 end
 wait(cap_path_rsp_valid);@(negedge clk);if(cap_path_status||cap_path_image[0]!=1||cap_path_image[39]!=0)$fatal(1,"g2 path export status");warm_pcrc=cap_path_crc;cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
 qc_cp_generation=64'h100000002;iter2_export_query;warm_qcrc=qc_cp_crc;
 if({qcp_image[5],qcp_image[4]}!=64'h100000002||system.as_bound_generation!=64'h100000001||k_count!=4)$fatal(1,"g2 source capture identity");
 $fdisplay(trace,"G2_CAPTURE %0d %08h %08h %0d",cycles,warm_pcrc,warm_qcrc,system.controller.last_sequence);
 joint_started=1;
 @(negedge clk);jp_start=1;do @(posedge clk);while(!jp_start_ready);@(negedge clk);jp_start=0;
 jp_authority_stage=1;authority_bind=1;do @(posedge clk);while(!as_cfg_ready);@(negedge clk);authority_bind=0;
 wait(as_cfg_rsp_valid);repeat(8)begin @(negedge clk);if(as_cfg_status||system.jp_ap||as_bound_generation!=64'h100000001||k_count!=4||pc_release_ready)$fatal(1,"held authority candidate");end
 authority_ack=1;@(negedge clk);authority_ack=0;wait(system.jp_ap);
 jp_load=3;while(jp_load!=0)begin @(posedge clk);accepted=jp_load&jp_ready;@(negedge clk);jp_load=jp_load&~accepted;end
 wait(jp_reply==3);repeat(8)begin @(negedge clk);if(jp_status||pc_release_ready||system.jp_prepared||k_count!=4||k_saved_checkpoint!=17)$fatal(1,"held commit stage reply");end
 jp_ack=3;@(negedge clk);jp_ack=0;wait(system.jp_prepared==3);
 if(as_bound_generation!=64'h100000001||k_count!=4||k_saved_checkpoint!=17||system.jp_ccp!=17)$fatal(1,"prepared metadata changed baseline");
 jp_commit=1;do @(posedge clk);while(!jp_commit_ready);@(negedge clk);jp_commit=0;
 wait(jp_done);repeat(8)begin @(negedge clk);if(jp_result||pc_release_ready||k_count||k_saved_checkpoint!=18||system.jp_ccp!=18||as_bound_generation!=64'h100000002||joint_pulses!=1)$fatal(1,"joint publication mismatch");end
 jp_done_ready=1;@(negedge clk);jp_done_ready=0;wait(!jp_owned);jp_authority_stage=0;
 if(!k_permit||!system.pc_safe||rc_slots!=1||system.controller.last_sequence!=180327)$fatal(1,"publication lost working state");

 ap_get(339193,26422,64'h100000001,1,0,0);
 ap_get(339193,26422,64'h100000002,0,1,1);ap_get(990179,26422,64'h100000002,0,1,2);ap_get(558358,26422,64'h100000002,0,3,2);ap_get(265324,26422,64'h100000002,0,4,1);
 qc_cp_generation=0;iter2_export_query;if({qcp_image[5],qcp_image[4]}!=64'h100000002||qc_cp_crc!=warm_qcrc)$fatal(1,"g2 active export differs candidate");
 qc_cp_expected_crc=qc_cp_crc;qcp_load(0);if(qc_restore_pending||system.controller.last_sequence!=180327)$fatal(1,"g2 active ledger import");
 pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;wait(!pc_owned);
 $fdisplay(trace,"ITER2_G2_PUBLISHED %0d %0d %0d %016h",cycles,k_saved_checkpoint,k_count,as_bound_generation);
end endtask
task iter2_g2_warm_restore;begin: crc_initial_attempt
 q_cfg_valid=0;g_cfg_valid=0;d_cfg_valid=0;t_cfg_valid=0;owner_cfg_valid=0;cs_cfg_valid=0;host_ctrl_valid=0;host_design_req_valid=0;host_io_valid=0;host_owner_req_valid=0;cc_req_valid=0;expand_valid=0;seed_valid=0;cs_req_valid=0;k_cfg_valid=0;cf_load_valid=0;rc_req_valid=0;
 recovering=1;armed=0;as_recover_version=4;as_recover_query=2;k_rec_valid=1;
 do @(posedge clk);while(!k_rec_ready);@(negedge clk);k_rec_valid=0;
 wait(k_rcfg_valid);@(negedge clk);restore_epoch=k_new_query;restore_version=k_new_version;crc_pin_flip=1;$fdisplay(trace,"CRC_PIN_CHANGED %0d %08h",cycles,crc_input);
 wait(k_labels_valid);@(negedge clk);if(k_count!=2||k_corrected!=2||!wm_owned||wm_fault||as_bound_generation!=64'h100000002)$fatal(1,"iter2 warm owner repair");
 $fdisplay(trace,"ITER2_OWNER_REPAIRED %0d %0d %0d",cycles,k_corrected,k_count);
 if(!$value$plusargs("warmimports=%s",warm_path))$fatal(1,"warm source labels");warm_fd=$fopen(warm_path,"r");if(!warm_fd)$fatal(1,"warm source open");
 begin : cancel_stream
 for(integer x=0;x<ls_count;x=x+1)begin
  rc=$fscanf(warm_fd,"%d",import_node);if(rc!=1)$fatal(1,"warm import node");
  for(integer f=0;f<5;f=f+1)begin rc=$fscanf(warm_fd,"%h",word);if(rc!=1)$fatal(1,"warm import field");import_record[f*32+:32]=word;end
  @(negedge clk);lr_s_valid=1;lr_s_node=import_node;lr_s_payload=import_record;lr_s_last=x+1==ls_count;do @(posedge clk);while(!lr_s_ready);@(negedge clk);lr_s_valid=0;
  if(x==20)begin wait(cancel_started);disable cancel_stream;end
 end
 end
 if(cancel_started)begin
  wait(k_rsp_valid);repeat(8)begin @(negedge clk);if(k_rsp_status!=6||k_count!=2||!wm_owned||!wm_fault||recover_open||wm_receipts||lr_written!=20||lr_verified||cancel_r_count!=1||cancel_front_count!=1||!baseline_retired)$fatal(1,"cancel recovery quarantine");end
  $fdisplay(trace,"BASELINE_CANCEL_FAILURE %0d %0d %0d %0d %0d",cycles,k_rsp_status,k_count,lr_written,lr_verified);
  k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;abort=0;cancel_active=0;
  repeat(8)begin @(negedge clk);if(!wm_owned||!wm_fault||recover_open||qc_cmd_ready||rc_req_ready||pc_acquire_ready)$fatal(1,"cancel failure opened work");end
  cancel_retry_restore;disable crc_initial_attempt;
 end
 wait(wm_receipts[0]);if(lr_source_crc!=ls_crc)$fatal(1,"source CRC binding");if(lr_written!=ls_count||lr_verified!=ls_count||wm_joined||k_rsp_valid)$fatal(1,"iter2 label receipt");
 cap_path_restore=1;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<156;x=x+1)begin @(negedge clk);warm_pi=x;warm_pd=cap_path_image[x];warm_plast=x==155;warm_psv=1;do @(posedge clk);while(!system.cp_s_ready);@(negedge clk);warm_psv=0;end
 wait(cap_path_rsp_valid);repeat(8)begin @(negedge clk);if(cap_path_status||wm_receipts!=1||wm_joined||k_rsp_valid)$fatal(1,"iter2 path held");end cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
 qc_cp_restore=1;qc_cp_expected_crc=warm_qcrc;qc_cp_valid=1;do @(posedge clk);while(!qc_cp_ready);@(negedge clk);qc_cp_valid=0;
 for(integer x=0;x<10;x=x+1)begin @(negedge clk);qc_cp_s_index=x;qc_cp_s_data=qcp_image[x];qc_cp_s_last=x==9;qc_cp_s_valid=1;do @(posedge clk);while(!qc_cp_s_ready);@(negedge clk);qc_cp_s_valid=0;end
 wait(qc_cp_rsp_valid);repeat(8)begin @(negedge clk);if(qc_cp_status||wm_receipts!=3||wm_joined||k_rsp_valid)$fatal(1,"iter2 query held");end qc_cp_rsp_ready=1;@(negedge clk);qc_cp_rsp_ready=0;
 wait(k_rsp_valid);repeat(8)begin @(negedge clk);if(k_rsp_status||k_count||!wm_owned||!wm_joined||wm_fault||recover_open)$fatal(1,"iter2 warm complete");end
 $fdisplay(trace,"ITER2_WARM_COMPLETE %0d %0d %0d %0d %0d",cycles,k_rsp_status,k_corrected,rc_slots,system.controller.last_sequence);
 k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;wait(recover_open);
 if(wm_owned||query_version!=4||p_active_query!=2||p_active_price!=4||rc_slots!=1||system.controller.last_sequence!=180327)$fatal(1,"iter2 warm release");
 rc=$fseek(polls_fd,0,0);if(rc)$fatal(1,"poll rewind");rc=$fseek(candidates_fd,0,0);if(rc)$fatal(1,"candidate rewind");rc=$fseek(fd_gold,0,0);if(rc)$fatal(1,"cost rewind");
 poll_i=0;expand_i=0;candidate_i=0;commits=0;outputs=0;offers=0;count2=0;physical_expands=0;metadata_calls=0;visited_reads=0;replayed=1;warm_running=0;retry_started=1;
 $fdisplay(trace,"ITER2_RETRY %0d %0d %0d",cycles,restore_epoch,restore_version);
end endtask

wire pre_g3_pc_release_ready,g3_block;
owner_snapshot_checkpoint_adapter #(.MAX_DIRTY(64)) snapshot_writer(
 .host_release_valid(pc_release_valid&&!g3_block),.root_release_ready(label_gate_ready),.host_release_ready(pre_g3_pc_release_ready),.root_release_valid(snap_root_release_valid),.manifest_ready(snap_manifest),
 .clk(clk),.rst(k_cold_rst),.lease(pc_owned),.source_drained(f_all_drained&&f_backend_idle&&f_normal_retired),
 .obs_awvalid(owner_m_awvalid),.obs_awready(owner_m_awready),.obs_awaddr(owner_m_awaddr),.obs_awlen(owner_m_awlen),.obs_bvalid(owner_m_bvalid),.obs_bready(owner_m_bready),.obs_bresp(owner_m_bresp),
 .cmd_valid(snap_cmd),.cmd_ready(snap_ready),.source_base(64'h61fffff000),.destination_base(64'ha000000000),.span_bytes(64'd146284032),.cmd_cookie(32'h5a000018),.busy(snap_busy),.rsp_valid(snap_rsp),.rsp_ready(snap_rsp_ready),.status(snap_status),.rsp_cookie(snap_cookie),.receipt_valid(snap_receipt),.dirty_count(snap_dirty),.verified_count(snap_verified),
 .m_araddr(copy_araddr),.m_arvalid(copy_arvalid),.m_arready(copy_arready),.m_rdata(copy_rdata),.m_rid(copy_rid),.m_rresp(copy_rresp),.m_rlast(copy_rlast),.m_rvalid(copy_rvalid),.m_rready(copy_rready),
 .m_awaddr(copy_awaddr),.m_awvalid(copy_awvalid),.m_awready(copy_awready),.m_wdata(copy_wdata),.m_wvalid(copy_wvalid),.m_wready(copy_wready),.m_bid(copy_bid),.m_bresp(copy_bresp),.m_bvalid(copy_bvalid),.m_bready(copy_bready));
axi_file_memory #(.ADDR_BITS(64),.READ_ONLY(0),.MAX_BEATS(1),.SECONDARY_WRITABLE(1),.TAG("copy")) snapshot_copy_memory(
 .clk(clk),.rst(k_cold_rst),.base0(64'h61fffff000),.base1(64'ha000000000),.base2(64'd0),.size0(64'd146284032),.size1(64'd146284032),.size2(64'd0),.inject_r(1'b0),.inject_b(1'b0),
 .araddr(copy_araddr),.arlen(8'd0),.arsize(3'd6),.arburst(2'd1),.arid(4'd0),.arvalid(copy_arvalid),.arready(copy_arready),.rdata(copy_rdata),.rid(copy_rid),.rresp(copy_rresp),.rlast(copy_rlast),.rvalid(copy_rvalid),.rready(copy_rready),
 .awaddr(copy_awaddr),.awlen(8'd0),.awsize(3'd6),.awburst(2'd1),.awid(4'd0),.awvalid(copy_awvalid),.awready(copy_awready),.wdata(copy_wdata),.wstrb(64'hffffffffffffffff),.wlast(1'b1),.wvalid(copy_wvalid),.wready(copy_wready),.bid(copy_bid),.bresp(copy_bresp),.bvalid(copy_bvalid),.bready(copy_bready));
task runtime_owner_snapshot;begin
 if(!pc_owned||snap_receipt||snap_dirty!=4)$fatal(1,"runtime snapshot prefix");
 $fdisplay(trace,"RUNTIME_OWNER_START %0d %0d",cycles,snap_dirty);
 snap_cmd=1;do @(posedge clk);while(!snap_ready);@(negedge clk);snap_cmd=0;
 wait(snap_rsp);repeat(8)begin @(negedge clk);if(snap_status||snap_cookie!=32'h5a000018||snap_verified!=4||snap_dirty!=4||!snap_receipt||pc_release_ready||!pc_owned)$fatal(1,"runtime snapshot held completion");end
 $fdisplay(trace,"RUNTIME_OWNER_COPIED %0d %0d %0d",cycles,snap_dirty,snap_verified);
 snap_rsp_ready=1;@(negedge clk);snap_rsp_ready=0;wait(!snap_busy);
end endtask
always @(posedge clk)if(!k_cold_rst)begin
 if(snap_busy&&(!pc_owned||pc_release_ready||owner_m_awvalid))$fatal(1,"runtime snapshot source lease");
 if(snap_cmd&&snap_ready)$fdisplay(trace,"RUNTIME_OWNER_ACCEPT %0d %0d",cycles,snap_dirty);
end

label_snapshot_checkpoint_adapter #(.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS)) label_snapshot(
 .host_release_valid(snap_root_release_valid),.root_release_ready(raw_pc_release_ready),.host_release_ready(label_gate_ready),.root_release_valid(label_root_release),.manifest_ready(label_manifest),
 .clk(clk),.rst(k_cold_rst),.lease(pc_owned),.source_drained(f_all_drained&&f_backend_idle&&f_normal_retired),.cmd_valid(ls_cmd),.cmd_ready(ls_ready),.cmd_query(g3_phase ? p_active_query : 2'd1),.cmd_price(g3_phase ? p_active_price : 4'd3),.cmd_nodes(32'd9089009),.cmd_cookie(32'h1abe0018),.busy(ls_busy),.rsp_valid(ls_rsp),.rsp_ready(ls_ack),.status(ls_status),.rsp_cookie(ls_cookie),.record_count(ls_count),.record_crc(ls_crc),.page_count(ls_pages),.receipt_valid(ls_receipt),
 .scan_valid(scan_v),.scan_ready(scan_r),.scan_frame(scan_f),.scan_rsp_valid(scan_rv),.scan_rsp_ready(scan_rr),.scan_status(scan_st),.scan_result_frame(scan_rf),.scan_owner(scan_o),.scan_published(scan_pub),
 .m_araddr(ls_ar),.m_arvalid(ls_av),.m_arready(ls_aq),.m_rdata(ls_data),.m_rid(ls_id),.m_rresp(ls_resp),.m_rlast(ls_rl),.m_rvalid(ls_rv),.m_rready(ls_rr),.record_valid(ls_v),.record_ready(ls_r),.record_node(ls_node),.record_payload(ls_payload));
axi_file_memory #(.ADDR_BITS(32),.READ_ONLY(1),.MAX_BEATS(1),.TAG("labelsnap")) label_snapshot_memory(
 .clk(clk),.rst(k_cold_rst),.base0(64'd0),.base1(64'd0),.base2(64'd0),.size0(64'd3145728),.size1(64'd0),.size2(64'd0),.inject_r(1'b0),.inject_b(1'b0),
 .araddr(ls_ar),.arlen(8'd0),.arsize(3'd6),.arburst(2'd1),.arid(4'd0),.arvalid(ls_av),.arready(ls_aq),.rdata(ls_data),.rid(ls_id),.rresp(ls_resp),.rlast(ls_rl),.rvalid(ls_rv),.rready(ls_rr),
 .awaddr(32'd0),.awlen(8'd0),.awsize(3'd6),.awburst(2'd1),.awid(4'd0),.awvalid(1'b0),.wdata(512'd0),.wstrb(64'd0),.wlast(1'b0),.wvalid(1'b0),.bready(1'b0));
task runtime_label_reject_unflushed;begin
 @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;
 $fdisplay(trace,"LABEL_UNFLUSHED_BEGIN %0d",cycles);
 ls_cmd=1;do @(posedge clk);while(!ls_ready);@(negedge clk);ls_cmd=0;ls_r=1;
 wait(ls_rsp);ls_r=0;repeat(6)begin @(negedge clk);if(ls_status!=3||ls_count||ls_pages||ls_receipt||pc_release_ready||!pc_owned)$fatal(1,"unflushed label snapshot admitted");end
 $fdisplay(trace,"LABEL_UNFLUSHED_REJECT %0d %0d",cycles,ls_status);
 ls_ack=1;@(negedge clk);ls_ack=0;wait(!ls_busy);
 pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;wait(!pc_owned);
end endtask
task runtime_label_snapshot;begin
 if(g4_phase)begin if(!$value$plusargs("g4imports=%s",warm_path))$fatal(1,"G4 label output path");end else if(g3_phase)begin if(!$value$plusargs("g3imports=%s",warm_path))$fatal(1,"g3 label output path");end else if(!$value$plusargs("warmimports=%s",warm_path))$fatal(1,"runtime label output path");ls_fd=$fopen(warm_path,"w");if(!ls_fd)$fatal(1,"runtime label output");
 begin if(g4_phase)$fdisplay(trace,"G4_LABEL_BEGIN %0d",cycles);else if(g3_phase)$fdisplay(trace,"G3_LABEL_BEGIN %0d",cycles);else $fdisplay(trace,"LABEL_SNAPSHOT_BEGIN %0d",cycles);end;
 ls_cmd=1;do @(posedge clk);while(!ls_ready);@(negedge clk);ls_cmd=0;ls_r=1;
 wait(ls_rsp);ls_r=0;
 repeat(8)begin @(negedge clk);if(ls_status||ls_cookie!=32'h1abe0018||ls_count==0||ls_pages==0||ls_emitted!=ls_count||!ls_receipt||pc_release_ready||!pc_owned)$fatal(1,"runtime label snapshot status=%0d rows=%0d pages=%0d emitted=%0d",ls_status,ls_count,ls_pages,ls_emitted);end
 begin if(g4_phase)$fdisplay(trace,"G4_LABEL_DONE %0d %0d %0d %08h",cycles,ls_count,ls_pages,ls_crc);else if(g3_phase)$fdisplay(trace,"G3_LABEL_DONE %0d %0d %0d %08h",cycles,ls_count,ls_pages,ls_crc);else $fdisplay(trace,"LABEL_SNAPSHOT_DONE %0d %0d %0d %08h",cycles,ls_count,ls_pages,ls_crc);end;$fflush(ls_fd);$fclose(ls_fd);
 ls_ack=1;@(negedge clk);ls_ack=0;wait(!ls_busy);
end endtask
always @(posedge clk)if(!k_cold_rst)begin
 if(scan_v&&scan_r)begin if(g4_phase)$fdisplay(trace,"G4_FRAME_REQUEST %0d %0d",cycles,scan_f);else if(g3_phase)$fdisplay(trace,"G3_FRAME_REQUEST %0d %0d",cycles,scan_f);else $fdisplay(trace,"FRAME_SCAN_REQUEST %0d %0d",cycles,scan_f);end;
 if(scan_rv&&scan_rr)begin if(g4_phase)$fdisplay(trace,"G4_FRAME_REPLY %0d %0d %0d %07h %0d",cycles,scan_st,scan_rf,scan_o,scan_pub);else if(g3_phase)$fdisplay(trace,"G3_FRAME_REPLY %0d %0d %0d %07h %0d",cycles,scan_st,scan_rf,scan_o,scan_pub);else $fdisplay(trace,"FRAME_SCAN_REPLY %0d %0d %0d %07h %0d",cycles,scan_st,scan_rf,scan_o,scan_pub);end;
 if(ls_v&&ls_r)begin
  $fwrite(ls_fd,"%0d",ls_node);for(integer f=0;f<5;f=f+1)$fwrite(ls_fd," %08h",ls_payload[f*32+:32]);$fwrite(ls_fd,"\n");
  begin if(g4_phase)$fdisplay(trace,"G4_LABEL_RECORD %0d %0d %040h",cycles,ls_node,ls_payload);else if(g3_phase)$fdisplay(trace,"G3_LABEL_RECORD %0d %0d %040h",cycles,ls_node,ls_payload);else $fdisplay(trace,"LABEL_SNAPSHOT_RECORD %0d %0d %040h",cycles,ls_node,ls_payload);end;ls_emitted<=ls_emitted+1;
 end
 if(ls_busy&&(!pc_owned||pc_release_ready||host_io_ready))$fatal(1,"runtime label lease");
end

assign crc_input=ls_crc^(bad_crc?32'd1:32'd0)^(crc_pin_flip?32'h100:32'd0);
always @(posedge clk)if(!k_cold_rst)begin
 if(k_rec_valid&&k_rec_ready)$fdisplay(trace,"LABEL_CRC_DESCRIPTOR %0d %08h %08h",cycles,crc_input,ls_crc);
 if(lr_rsp_valid&&lr_rsp_ready)$fdisplay(trace,"LABEL_CRC_RESULT %0d %0d %0d %0d %08h",cycles,lr_rsp_status,lr_written,lr_verified,lr_source_crc);
end

always @(posedge clk)if(!bench_rst)begin
 if(baseline_guard_fault)$fatal(1,"baseline guard fault");
 if(k_target_reset&&!baseline_retired)$fatal(1,"reset before baseline retirement");
 if(k_target_reset)$fdisplay(trace,"BASELINE_TARGET_RESET %0d %0d %0d %0d",cycles,baseline_retired,baseline_physical,baseline_owned);
 if(!baseline_retired&&(f_all_drained||f_backend_idle))$fatal(1,"baseline missing from full warm fence");
end
task cancel_retry_restore;begin
 cancel_started=1;retry_started=1;bad_crc=0;crc_pin_flip=0;retry_cookie=32'hc0020000;
 k_rec_valid=1;do @(posedge clk);while(!k_rec_ready);@(negedge clk);k_rec_valid=0;
 wait(k_rsp_valid);repeat(8)begin @(negedge clk);if(k_rsp_status!=1||k_rsp_cookie!=retry_cookie||k_count!=2||!wm_owned||!wm_fault||recover_open)$fatal(1,"CRC same attempt admitted");end
 $fdisplay(trace,"CANCEL_RETRY_REJECT %0d %0d %0d %08h",cycles,k_rsp_status,k_count,k_rsp_cookie);
 k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;repeat(8)@(negedge clk);
 retry_cookie=32'hc0020001;
 $fdisplay(trace,"CANCEL_HIGHER_ATTEMPT %0d",cycles);
 q_cfg_valid=0;g_cfg_valid=0;d_cfg_valid=0;t_cfg_valid=0;owner_cfg_valid=0;cs_cfg_valid=0;host_ctrl_valid=0;host_design_req_valid=0;host_io_valid=0;host_owner_req_valid=0;cc_req_valid=0;expand_valid=0;seed_valid=0;cs_req_valid=0;k_cfg_valid=0;cf_load_valid=0;rc_req_valid=0;
 recovering=1;armed=0;as_recover_version=5;as_recover_query=3;k_rec_valid=1;
 do @(posedge clk);while(!k_rec_ready);@(negedge clk);k_rec_valid=0;
 wait(k_rcfg_valid);@(negedge clk);restore_epoch=k_new_query;restore_version=k_new_version;crc_pin_flip=1;$fdisplay(trace,"CRC_PIN_CHANGED %0d %08h",cycles,crc_input);
 wait(k_labels_valid);@(negedge clk);if(k_count!=2||k_corrected!=0||!wm_owned||wm_fault||as_bound_generation!=64'h100000002)$fatal(1,"iter2 warm owner repair");
 $fdisplay(trace,"CANCEL_RETRY_OWNER_VERIFIED %0d %0d %0d",cycles,k_corrected,k_count);
 if(!$value$plusargs("warmimports=%s",warm_path))$fatal(1,"warm source labels");warm_fd=$fopen(warm_path,"r");if(!warm_fd)$fatal(1,"warm source open");
 for(integer x=0;x<ls_count;x=x+1)begin
  rc=$fscanf(warm_fd,"%d",import_node);if(rc!=1)$fatal(1,"warm import node");
  for(integer f=0;f<5;f=f+1)begin rc=$fscanf(warm_fd,"%h",word);if(rc!=1)$fatal(1,"warm import field");import_record[f*32+:32]=word;end
  @(negedge clk);lr_s_valid=1;lr_s_node=import_node;lr_s_payload=import_record;lr_s_last=x+1==ls_count;do @(posedge clk);while(!lr_s_ready);@(negedge clk);lr_s_valid=0;
 end
 wait(wm_receipts[0]);if(lr_source_crc!=ls_crc)$fatal(1,"source CRC binding");if(lr_written!=ls_count||lr_verified!=ls_count||wm_joined||k_rsp_valid)$fatal(1,"iter2 label receipt");
 cap_path_restore=1;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<156;x=x+1)begin @(negedge clk);warm_pi=x;warm_pd=cap_path_image[x];warm_plast=x==155;warm_psv=1;do @(posedge clk);while(!system.cp_s_ready);@(negedge clk);warm_psv=0;end
 wait(cap_path_rsp_valid);repeat(8)begin @(negedge clk);if(cap_path_status||wm_receipts!=1||wm_joined||k_rsp_valid)$fatal(1,"iter2 path held");end cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
 qc_cp_restore=1;qc_cp_expected_crc=warm_qcrc;qc_cp_valid=1;do @(posedge clk);while(!qc_cp_ready);@(negedge clk);qc_cp_valid=0;
 for(integer x=0;x<10;x=x+1)begin @(negedge clk);qc_cp_s_index=x;qc_cp_s_data=qcp_image[x];qc_cp_s_last=x==9;qc_cp_s_valid=1;do @(posedge clk);while(!qc_cp_s_ready);@(negedge clk);qc_cp_s_valid=0;end
 wait(qc_cp_rsp_valid);repeat(8)begin @(negedge clk);if(qc_cp_status||wm_receipts!=3||wm_joined||k_rsp_valid)$fatal(1,"iter2 query held");end qc_cp_rsp_ready=1;@(negedge clk);qc_cp_rsp_ready=0;
 wait(k_rsp_valid);repeat(8)begin @(negedge clk);if(k_rsp_status||k_count||!wm_owned||!wm_joined||wm_fault||recover_open)$fatal(1,"iter2 warm complete");end
 $fdisplay(trace,"ITER2_WARM_COMPLETE %0d %0d %0d %0d %0d",cycles,k_rsp_status,k_corrected,rc_slots,system.controller.last_sequence);
 k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;wait(recover_open);
 if(wm_owned||query_version!=5||p_active_query!=3||p_active_price!=5||rc_slots!=1||system.controller.last_sequence!=180327)$fatal(1,"iter2 warm release");
 rc=$fseek(polls_fd,0,0);if(rc)$fatal(1,"poll rewind");rc=$fseek(candidates_fd,0,0);if(rc)$fatal(1,"candidate rewind");rc=$fseek(fd_gold,0,0);if(rc)$fatal(1,"cost rewind");
 poll_i=0;expand_i=0;candidate_i=0;commits=0;outputs=0;offers=0;count2=0;physical_expands=0;metadata_calls=0;visited_reads=0;replayed=1;warm_running=0;retry_started=1;
 $fdisplay(trace,"ITER2_RETRY %0d %0d %0d",cycles,restore_epoch,restore_version);
end endtask
initial begin
 @(negedge bench_rst);
 do @(posedge clk);while(!(bv&&by&&wm_owned&&k_labels_valid&&lr_written==20&&!retry_started));
 @(negedge clk);cancel_started=1;cancel_active=1;abort=1;
 $fdisplay(trace,"BASELINE_CANCEL_AR %0d %016h",cycles,ba);
 repeat(64)begin
  @(negedge clk);cancel_wait_count=cancel_wait_count+1;
  if(baseline_retired||baseline_physical||!baseline_owned||k_rsp_valid||k_target_reset||!wm_owned||recover_open||!lr_busy||cancel_r_count||f_all_drained||f_backend_idle)$fatal(1,"baseline cancel premature completion");
  $fdisplay(trace,"BASELINE_CANCEL_WAIT %0d %0d %0d %0d %0d %0d",cycles,baseline_retired,baseline_physical,baseline_owned,k_rsp_valid,lr_busy);
 end
 cancel_hold_release=1;$fdisplay(trace,"BASELINE_CANCEL_RELEASE %0d",cycles);
end
always @(posedge clk)if(!bench_rst&&cancel_active)begin
 if(brv&&brr)begin cancel_r_count=cancel_r_count+1;$fdisplay(trace,"BASELINE_CANCEL_R %0d",cycles);end
 if(baseline_rsp_valid&&baseline_rsp_ready)begin cancel_front_count=cancel_front_count+1;$fdisplay(trace,"BASELINE_CANCEL_FRONT %0d",cycles);end
end

assign pc_release_ready=pre_g3_pc_release_ready&&!g3_block&&!g3_bundle_owned;
reg g3_cmd=0,g3_ack=0;reg[1:0]g3_op=0;
wire g3_ready,g3_busy,g3_rsp,g3_receipt,g3_bound,g3_data_error,g3_coverage_error,g3_manifest;
wire[3:0]g3_status;wire[31:0]g3_cookie,g3_dirty,g3_verified;
wire[63:0]g3_floor,g3_cpfloor,g3_rd,g3_rb,g3_rg,g3_rc,g3_rdst;
wire[63:0]g3_ar,g3_aw;wire g3_av,g3_aq,g3_rv,g3_rr,g3_rl,g3_wav,g3_waq,g3_wv,g3_wq,g3_bv,g3_bq;
wire[511:0]g3_data,g3_wdata;wire[3:0]g3_rid,g3_bid;wire[1:0]g3_rresp,g3_bresp;
wire g3_healthy=system.pc_safe&&!wm_owned&&!wm_fault&&recover_open&&!qc_busy&&!rc_busy&&!f_fault;
cumulative_owner_snapshot #(.MAX_DIRTY(64),.KEEP_RECEIPT_ON_BUSY(1)) g3_writer(
 .clk(clk),.rst(k_cold_rst),.lease(pc_owned),.source_drained(f_all_drained&&f_backend_idle&&f_normal_retired&&owner_drained),.source_healthy(g3_healthy),.publication_retired(owner_drained&&f_all_drained&&f_backend_idle&&f_normal_retired&&!qc_busy&&!ss_busy&&!rc_busy&&!as_busy&&!system.as_cfg_lease&&!system.as_core_cfg_valid&&!k_busy&&!(|jp_reply)&&!qc_cp_busy&&!cap_path_busy),.source_protocol_ok(!owner_watch_fault),.source_integrity_fault(abort||owner_watch_fault||f_fault||fault||rc_fault||k_fault||cf_fault||lr_fault||qc_fault||ss_fault),
 .cmd_op(g3_op),.cmd_design(design_id),.cmd_baseline(64'h100000001),.cmd_generation(g4_phase ? 64'h100000004 : 64'h100000003),.cmd_checkpoint(g3_op==0 ? 64'd17 : (g4_phase ? 64'd20 : 64'd19)),
 .bank0_base(64'ha000000000),.bank1_base(64'hc000000000),.active_destination(as_bound_generation==64'h100000001 ? 64'h91fffff000 : ((as_bound_generation==64'h100000002||as_bound_generation==64'h100000004) ? 64'ha000000000 : 64'hc000000000)),.active_generation(as_bound_generation),
 .obs_bid(owner_m_bid),.obs_awid(owner_m_awid),.obs_awsize(owner_m_awsize),.obs_awburst(owner_m_awburst),
 .bound(g3_bound),.data_error(g3_data_error),.coverage_error(g3_coverage_error),.generation_floor(g3_floor),.checkpoint_floor(g3_cpfloor),
 .receipt_design(g3_rd),.receipt_baseline(g3_rb),.receipt_generation(g3_rg),.receipt_checkpoint(g3_rc),.receipt_destination(g3_rdst),
 .publish_design(design_id),.publish_baseline(64'h100000001),.publish_generation(g4_phase ? 64'h100000004 : 64'h100000003),.publish_checkpoint(g4_phase ? 64'd20 : 64'd19),.publish_destination(g4_phase ? 64'ha000000000 : 64'hc000000000),.manifest_ready(g3_manifest),.release_blocked(g3_block),
 .obs_awvalid(owner_m_awvalid),.obs_awready(owner_m_awready),.obs_awaddr(owner_m_awaddr),.obs_awlen(owner_m_awlen),.obs_bvalid(owner_m_bvalid),.obs_bready(owner_m_bready),.obs_bresp(owner_m_bresp),
 .cmd_valid(g3_cmd),.cmd_ready(g3_ready),.source_base(64'h61fffff000),.destination_base(g4_phase ? 64'ha000000000 : 64'hc000000000),.span_bytes(64'd146284032),.cmd_cookie(32'h5a000019),
 .busy(g3_busy),.rsp_valid(g3_rsp),.rsp_ready(g3_ack),.status(g3_status),.rsp_cookie(g3_cookie),.receipt_valid(g3_receipt),.dirty_count(g3_dirty),.verified_count(g3_verified),
 .m_araddr(g3_ar),.m_arvalid(g3_av),.m_arready(g3_aq),.m_rdata(g3_data),.m_rid(g3_rid),.m_rresp(g3_rresp),.m_rlast(g3_rl),.m_rvalid(g3_rv),.m_rready(g3_rr),
 .m_awaddr(g3_aw),.m_awvalid(g3_wav),.m_awready(g3_waq),.m_wdata(g3_wdata),.m_wvalid(g3_wv),.m_wready(g3_wq),.m_bid(g3_bid),.m_bresp(g3_bresp),.m_bvalid(g3_bv),.m_bready(g3_bq));
axi_file_memory #(.READ_ONLY(0),.MAX_BEATS(1),.SECONDARY_WRITABLE(1),.TERTIARY_WRITABLE(1),.TAG("g3copy")) g3_memory(
 .clk(clk),.rst(k_cold_rst),.base0(64'h61fffff000),.base1(64'ha000000000),.base2(64'hc000000000),.size0(64'd146284032),.size1(64'd146284032),.size2(64'd146284032),.inject_r(1'b0),.inject_b(1'b0),.hold_r(1'b0),
 .araddr(g3_ar),.arlen(8'd0),.arsize(3'd6),.arburst(2'd1),.arid(4'd0),.arvalid(g3_av),.arready(g3_aq),.rdata(g3_data),.rid(g3_rid),.rresp(g3_rresp),.rlast(g3_rl),.rvalid(g3_rv),.rready(g3_rr),
 .awaddr(g3_aw),.awlen(8'd0),.awsize(3'd6),.awburst(2'd1),.awid(4'd0),.awvalid(g3_wav),.awready(g3_waq),.wdata(g3_wdata),.wstrb(64'hffffffffffffffff),.wlast(1'b1),.wvalid(g3_wv),.wready(g3_wq),.bid(g3_bid),.bresp(g3_bresp),.bvalid(g3_bv),.bready(g3_bq));
task cumulative_command(input integer op);begin
 @(negedge clk);g3_op=op;g3_cmd=1;do @(posedge clk);while(!g3_ready);@(negedge clk);g3_cmd=0;
end endtask
task cumulative_result(input integer op,expected,n);begin
 wait(g3_rsp);repeat(8)begin @(negedge clk);
  if(g3_status!=expected||g3_cookie!=32'h5a000019||g3_verified!=n||!pc_owned||pc_release_ready||g3_manifest)$fatal(1,"cumulative held response op=%0d status=%0d",op,g3_status);
 end
 $fdisplay(trace,"CUMULATIVE_RESULT %0d %0d %0d %0d %0d %0d %0d %016h %0d",cycles,op,g3_status,g3_dirty,g3_verified,g3_data_error,g3_coverage_error,g3_floor,g3_cpfloor);
 g3_ack=1;@(negedge clk);g3_ack=0;wait(!g3_busy);
end endtask
initial begin
 @(negedge bench_rst);wait(pc_owned&&g3_healthy&&f_all_drained&&f_backend_idle&&f_normal_retired&&owner_drained);
 cumulative_command(0);cumulative_result(0,0,0);
 if(!g3_bound||g3_dirty||g3_floor!=64'h100000001)$fatal(1,"pre-work cumulative bind");
end
task cumulative_g3_copy;begin
 @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;
 $fdisplay(trace,"CUMULATIVE_PRECONDITION %0d %0d %0d %0d %0d %0d %0d %016h %0d %0d %0d",cycles,pc_owned,g3_healthy,g3_bound,g3_data_error,g3_coverage_error,g3_dirty,as_bound_generation,k_saved_checkpoint,rc_slots,system.controller.last_sequence);
 if(!pc_owned||!g3_healthy||!g3_bound||!g3_data_error||g3_coverage_error||g3_dirty!=4||as_bound_generation!=64'h100000002||k_saved_checkpoint!=18||rc_slots!=3||system.controller.last_sequence!=180328)$fatal(1,"actual G3 rearm preconditions");
 $fdisplay(trace,"CUMULATIVE_REARM_SOURCE %0d %0d %0d %0d %0d %0d %0d",cycles,pc_owned,g3_healthy,owner_drained,f_all_drained,g3_data_error,g3_dirty);
 cumulative_command(1);cumulative_result(1,0,0);
 if(g3_data_error||g3_coverage_error||g3_dirty!=4)$fatal(1,"cumulative rearm lost coverage");
 cumulative_command(2);cumulative_result(2,0,4);
 if(!g3_manifest||!g3_receipt||g3_rd!=design_id||g3_rb!=64'h100000001||g3_rg!=64'h100000003||g3_rc!=19||g3_rdst!=64'hc000000000||g3_dirty!=4||as_bound_generation!=64'h100000002||k_saved_checkpoint!=18)$fatal(1,"G3 candidate descriptor/current G2");
 $fdisplay(trace,"CUMULATIVE_G3_CANDIDATE %0d %016h %0d %016h %0d",cycles,g3_rg,g3_rc,g3_rdst,g3_dirty);
end endtask
always @(posedge clk)if(!k_cold_rst)begin
 if(g3_coverage_error)$fatal(1,"real owner cumulative coverage lost");
 if(g3_busy&&(!pc_owned||pc_release_ready||owner_m_awvalid))$fatal(1,"cumulative native lease");
 if(g3_cmd&&g3_ready)$fdisplay(trace,"CUMULATIVE_ACCEPT %0d %0d %0d %0d",cycles,g3_op,g3_dirty,g3_data_error);
end

export_manifest #(.PATH_SLOTS(4)) g3_exports(.clk(clk),.rst(k_cold_rst),.lease(pc_owned),.arm(g3_arm),.abort(abort||owner_watch_fault||wm_owned||wm_fault),
 .source_write((owner_m_awvalid&&owner_m_awready)||(p_m_awvalid&&p_m_awready)),.published(g3_phase&&(&system.jp_pv)),
 .active_design(design_id),.target_generation(g4_phase ? 64'h100000004 : 64'h100000003),.target_checkpoint(g4_phase ? 32'd20 : 32'd19),.active_version(query_version),.active_sequence(system.controller.last_sequence),.active_query(p_active_query),.active_price(p_active_price),.active_slots(rc_slots),
 .selected_design(system.jp_design),.selected_generation(system.jp_generation),.selected_checkpoint(system.jp_checkpoint),.selected_version(system.jp_version),.selected_query(system.jp_query),.selected_price(system.jp_price),
 .owner_manifest(g3_manifest),.label_manifest(label_manifest),
 .label_accept(ls_cmd&&ls_ready),.label_restore(1'b0),.label_done(ls_rsp&&ls_ack),.label_query(p_active_query),.label_price(p_active_price),.label_status(ls_status),.label_count(ls_count),.label_crc(ls_crc),
 .path_accept(cap_path_valid&&cap_path_ready),.path_restore(cap_path_restore),.path_done(cap_path_rsp_valid&&cap_path_rsp_ready),.path_word(cap_path_m_valid&&cap_path_m_ready),.path_status(cap_path_status),.path_index(cap_path_m_index),.path_data(cap_path_m_data),.path_crc(cap_path_crc),.path_last(cap_path_m_last),
 .query_accept(qc_cp_valid&&qc_cp_ready),.query_restore(qc_cp_restore),.query_done(qc_cp_rsp_valid&&qc_cp_rsp_ready),.query_word(qc_cp_m_valid&&qc_cp_m_ready),.query_status(qc_cp_status),.query_index(qc_cp_m_index),.query_data(qc_cp_m_data),.query_crc(qc_cp_crc),.query_last(qc_cp_m_last),
 .owned(g3_bundle_owned),.fault(g3_bundle_fault),.receipts(g3_export_receipts),.saved_label_count(g3_lcount),.saved_label_crc(g3_lcrc),.saved_path_crc(g3_pcrc),.saved_query_crc(g3_qcrc),.manifest_ready(g3_bundle_manifest));
task publish_g3;reg[1:0]accepted;begin
 g3_phase=1;ls_emitted=0;rc=$value$plusargs("g3negative=%d",g3_negative);
 @(negedge clk);g3_arm=1;@(negedge clk);g3_arm=0;
 runtime_label_snapshot;
 if(ls_count!=781||ls_pages!=393||g3_bundle_fault)$fatal(1,"G3 native label cardinality");
 cap_path_restore=0;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<156;x=x+1)begin
  wait(cap_path_m_valid);@(negedge clk);if(cap_path_m_index!=x||cap_path_m_last!=(x==155))$fatal(1,"G3 path boundary");cap_path_image[x]=cap_path_m_data;
  $fdisplay(trace,"G3_PATH_WORD %0d %0d %08h",cycles,x,cap_path_m_data);cap_path_m_ready=1;@(negedge clk);cap_path_m_ready=0;
 end
 wait(cap_path_rsp_valid);repeat(8)begin @(negedge clk);if(cap_path_status||cap_path_image[0]!=1||cap_path_image[39]!=1||pc_release_ready||!pc_owned)$fatal(1,"G3 path held");end
 $fdisplay(trace,"G3_PATH_RESULT %0d %08h",cycles,cap_path_crc);cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
 qc_cp_generation=64'h100000003;iter2_export_query;
 if({qcp_image[5],qcp_image[4]}!=64'h100000003||qcp_image[6]!=5||qcp_image[7]!=32'h57||qcp_image[8]!=180328||g3_bundle_fault||g3_export_receipts!=7)$fatal(1,"G3 query/bundle identity");
 for(integer x=0;x<10;x=x+1)$fdisplay(trace,"G3_QUERY_WORD %0d %0d %08h",cycles,x,qcp_image[x]);
 $fdisplay(trace,"G3_BUNDLE %0d %0d %08h %08h %08h %0d %0d %0d",cycles,g3_lcount,g3_lcrc,g3_pcrc,g3_qcrc,g3_receipt,g3_manifest,g3_bundle_manifest);
 if(!g3_negative&&!g3_bundle_manifest)$fatal(1,"G3 manifest before publication");
 joint_watch=0;
 @(negedge clk);jp_start=1;do @(posedge clk);while(!jp_start_ready);@(negedge clk);jp_start=0;
 jp_authority_stage=1;authority_bind=1;do @(posedge clk);while(!as_cfg_ready);@(negedge clk);authority_bind=0;
 wait(as_cfg_rsp_valid);repeat(8)begin @(negedge clk);if(as_cfg_status||system.jp_ap||as_bound_generation!=64'h100000002||k_count!=3||pc_release_ready)$fatal(1,"G3 authority held");
  $fdisplay(trace,"G3_AUTH_HELD %0d %0d %0d %0d %0d",cycles,g3_healthy,f_backend_idle,g3_receipt,g3_manifest);
 end
 authority_ack=1;@(negedge clk);authority_ack=0;wait(system.jp_ap);
 jp_load=3;while(jp_load!=0)begin @(posedge clk);accepted=jp_load&jp_ready;@(negedge clk);jp_load=jp_load&~accepted;end
 wait(jp_reply==3);repeat(8)begin @(negedge clk);if(jp_status||pc_release_ready||system.jp_prepared||k_count!=3||k_saved_checkpoint!=18)$fatal(1,"G3 metadata held");end
 jp_ack=3;@(negedge clk);jp_ack=0;wait(system.jp_prepared==3);
 if(g3_negative)begin
  repeat(64)begin @(negedge clk);if(g3_receipt||g3_manifest||g3_bundle_manifest||jp_commit_ready||as_bound_generation!=64'h100000002||k_saved_checkpoint!=18||k_count!=3||joint_pulses!=1||pc_release_ready||g3_bundle_fault||g3_export_receipts!=7)$fatal(1,"G3 negative containment");end
  $fdisplay(trace,"G3_PUBLISH_BLOCKED %0d %0d %0d %0d %0d",cycles,g3_receipt,g3_export_receipts,k_saved_checkpoint,k_count);$fflush(trace);$display("G3_NEGATIVE_OBSERVED");$finish;
 end
 for(integer n=0;n<64&&(g3_bundle_manifest!==1'b1);n=n+1)begin
  @(negedge clk);$fdisplay(trace,"G3_RETIRE_WAIT %0d %0d %0d %0d %0d %0d",cycles,g3_receipt,g3_manifest,g3_bundle_manifest,k_permit,g3_writer.publication_retired);
 end
 if(g3_bundle_manifest!==1'b1||g3_bundle_fault||k_saved_checkpoint!=18||k_count!=3||system.jp_ccp!=18||k_permit)$fatal(1,"G3 prepared identity/retired manifest");
 $fdisplay(trace,"G3_PREPARED_PROOF %0d %0d %0d %0d %0d %0d",cycles,g3_receipt,g3_manifest,g3_bundle_manifest,k_permit,g3_writer.publication_retired);
 jp_commit=1;do @(posedge clk);while(!jp_commit_ready);@(negedge clk);jp_commit=0;
 wait(jp_done);repeat(8)begin @(negedge clk);if(jp_result||pc_release_ready||k_count||k_saved_checkpoint!=19||system.jp_ccp!=19||as_bound_generation!=64'h100000003||joint_pulses!=2||g3_bundle_owned||g3_bundle_fault)$fatal(1,"G3 publication identity");end
 jp_done_ready=1;@(negedge clk);jp_done_ready=0;wait(!jp_owned);jp_authority_stage=0;
 ap_get(339193,26422,64'h100000002,1,0,0);
 ap_get(339193,26422,64'h100000003,0,1,1);ap_get(990179,26422,64'h100000003,0,2,2);ap_get(558358,26422,64'h100000003,0,4,2);ap_get(558358,23916,64'h100000003,0,1,2);ap_get(265324,26422,64'h100000003,0,5,1);
 qc_cp_generation=0;iter2_export_query;
 if({qcp_image[5],qcp_image[4]}!=64'h100000003||qc_cp_crc!=g3_qcrc||system.controller.last_sequence!=180328)$fatal(1,"G3 published query export");
 pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;wait(!pc_owned);
 $fdisplay(trace,"G3_PUBLISHED %0d %016h %0d %0d %0d %0d",cycles,as_bound_generation,k_saved_checkpoint,query_version,rc_slots,system.controller.last_sequence);$display("G3_PUBLISH_PASS");
end endtask
always @(posedge clk)if(!k_cold_rst&&g3_phase)begin
 if($isunknown(g3_writer.publication_retired))$fatal(1,"unknown native publication retirement");
 if(g3_bundle_owned&&(!pc_owned||pc_release_ready))$fatal(1,"G3 bundle lost lease");
 if(g3_bundle_fault)$fatal(1,"G3 native export manifest fault");
end

task third_path_snapshot(input bit capture);begin
 cap_path_restore=0;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<156;x=x+1)begin
  wait(cap_path_m_valid);@(negedge clk);if(cap_path_m_index!=x||cap_path_m_last!=(x==155))$fatal(1,"third snapshot framing");
  cap_path_image[x]=cap_path_m_data;$fdisplay(trace,"THIRD_PATH_WORD %0d %0d %0d %08h",cycles,capture,x,cap_path_m_data);
  cap_path_m_ready=1;@(negedge clk);cap_path_m_ready=0;
 end
 wait(cap_path_rsp_valid);@(negedge clk);if(cap_path_status)$fatal(1,"third snapshot status");
 $fdisplay(trace,"THIRD_PATH_DONE %0d %0d %08h %0d",cycles,capture,cap_path_crc,rc_slots);
 cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
end endtask
reg[31:0]g3_saved_path[0:155],g3_saved_query[0:9];
reg[31:0]g3_saved_pcrc,g3_saved_qcrc,g3_saved_lcrc,g3_saved_count;
task third_prepare;begin
 $fdisplay(trace,"THIRD_BEGIN %0d %0d %0d %0d",cycles,rc_slots,k_count,system.controller.last_sequence);
 @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;
 third_path_snapshot(0);
 if(rc_slots!=3||cap_path_image[78]!=0||k_count)$fatal(1,"third initial paths");
 cap_path_image[78]=1;cap_path_image[79]=3;cap_path_image[80]=26422;cap_path_image[81]=66893;cap_path_image[82]=151354;
 cap_path_image[83]=design_id[31:0];cap_path_image[84]=design_id[63:32];cap_path_image[85]=990179;cap_path_image[86]=558358;cap_path_image[87]=265324;
 prep_crc=32'hffffffff;for(integer x=0;x<156;x=x+1)prep_crc=prep_crc_word(prep_crc,cap_path_image[x]);warm_pcrc=~prep_crc;
 cap_path_restore=1;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<156;x=x+1)begin
  @(negedge clk);warm_pi=x;warm_pd=cap_path_image[x];warm_plast=x==155;warm_psv=1;do @(posedge clk);while(!system.cp_s_ready);@(negedge clk);warm_psv=0;
  $fdisplay(trace,"THIRD_PATH_IMPORT %0d %08h",x,cap_path_image[x]);
 end
 wait(cap_path_rsp_valid);repeat(8)begin @(negedge clk);if(cap_path_status||cap_path_crc!=warm_pcrc||rc_slots!=7||k_count||!pc_owned)$fatal(1,"third metadata registration");end
 cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
 pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;wait(!pc_owned);
 stage_no=6;owner_op(0,990179,2,2);owner_op(0,558358,4,2);owner_op(0,265324,5,1);
 route_command(1,2,151354,180329);
 owner_op(0,990179,1,2);owner_op(0,558358,3,2);owner_op(0,265324,4,1);owner_op(0,339193,1,1);iter2_foreign_probe;
 if(rc_slots!=3||system.controller.last_sequence!=180328||k_saved_checkpoint!=19||k_count!=3||fault||rc_fault||k_fault)$fatal(1,"third preparation continuity");
 $fdisplay(trace,"THIRD_PREPARED %0d %0d %0d %0d",cycles,rc_slots,k_count,system.controller.last_sequence);
end endtask
task third_query;begin
 for(integer x=0;x<156;x=x+1)g3_saved_path[x]=cap_path_image[x];
 for(integer x=0;x<10;x=x+1)g3_saved_query[x]=qcp_image[x];
 g3_saved_pcrc=g3_pcrc;g3_saved_qcrc=g3_qcrc;g3_saved_lcrc=g3_lcrc;g3_saved_count=g3_lcount;
 third_prepare;
 $fclose(fd_gold);$fclose(candidates_fd);$fclose(polls_fd);$fclose(finals_fd);
 if(!$value$plusargs("cost3=%s",path))$fatal(1,"cost3");fd_gold=$fopen(path,"r");
 if(!$value$plusargs("candidates3=%s",path))$fatal(1,"candidates3");candidates_fd=$fopen(path,"r");
 if(!$value$plusargs("polls3=%s",path))$fatal(1,"polls3");polls_fd=$fopen(path,"r");
 if(!$value$plusargs("finals3=%s",path))$fatal(1,"finals3");finals_fd=$fopen(path,"r");
 if(!fd_gold||!candidates_fd||!polls_fd||!finals_fd)$fatal(1,"third oracle files");
 poll_i=0;expand_i=0;candidate_i=0;commits=0;offers=0;outputs=0;count2=0;physical_expands=0;metadata_calls=0;visited_reads=0;
 query_index=2;selected_sink=151354;selected_connection=170785;selected_sequence=180329;stopped=0;armed=0;replayed=1;warm_running=0;

 g3_warm_mode=1;replayed=0;armed=1;injection_seen=0;fault_case=5;wm_enable=1;warm_fault_node=558358;warm_running=1;
 // Keep recovering asserted until this task explicitly submits the new descriptor.
 recovering=1;
 $fdisplay(trace,"THIRD_FAULT_BEGIN %0d",cycles);
 fault_query;
 if(commits!=302||candidate_i!=565||expand_i!=113||poll_i!=114||qc_rsp_status!=7||qc_rsp_detail!=5||qc_rsp_committed||k_count!=3)$fatal(1,"G3 fault numerical/journal result");
 $fdisplay(trace,"THIRD_FAULT_DONE %0d %0d %0d %0d %0d",cycles,poll_i,expand_i,candidate_i,commits);
 third_warm_restore;
 third_prepare;
 rc=$fseek(polls_fd,0,0);if(rc)$fatal(1,"third poll rewind");rc=$fseek(candidates_fd,0,0);if(rc)$fatal(1,"third candidate rewind");rc=$fseek(fd_gold,0,0);if(rc)$fatal(1,"third cost rewind");
 poll_i=0;expand_i=0;candidate_i=0;commits=0;outputs=0;offers=0;count2=0;physical_expands=0;metadata_calls=0;visited_reads=0;stopped=0;replayed=1;warm_running=0;
 $fdisplay(trace,"THIRD_RETRY_BEGIN %0d",cycles);
 autonomous_query;
 if(commits!=302||candidate_i!=565||expand_i!=113||poll_i!=114||rc_slots!=7||system.controller.last_sequence!=180329||query_version!=6||p_active_query!=0||p_active_price!=6||k_count!=3||k_saved_checkpoint!=19)$fatal(1,"third aggregate/context");
 owner_op(0,339193,1,1);owner_op(0,990179,2,2);owner_op(0,558358,4,2);owner_op(0,265324,5,1);iter2_foreign_probe;
 control(1);
 @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;
 third_path_snapshot(1);
 qc_cp_generation=0;qcp_start(0);
 for(integer x=0;x<10;x=x+1)begin
  wait(qc_cp_m_valid);@(negedge clk);if(qc_cp_m_index!=x||qc_cp_m_last!=(x==9))$fatal(1,"third query export");qcp_image[x]=qc_cp_m_data;qc_cp_m_ready=1;@(negedge clk);qc_cp_m_ready=0;
 end
 qcp_result(0);if(qcp_image[8]!=180329||qcp_image[6]!=6||qcp_image[7]!=32'h58)$fatal(1,"third ledger floor");
 pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;wait(!pc_owned);
 $fdisplay(trace,"THIRD_PASS %0d %0d %0d %0d %0d %0d %0d",cycles,poll_i,expand_i,candidate_i,commits,rc_slots,system.controller.last_sequence);
 $display("THIRD_WARM_PASS polls=114 expands=113 candidates=565 costs=302");
end endtask

task third_warm_restore;begin
 q_cfg_valid=0;g_cfg_valid=0;d_cfg_valid=0;t_cfg_valid=0;owner_cfg_valid=0;cs_cfg_valid=0;host_ctrl_valid=0;host_design_req_valid=0;host_io_valid=0;host_owner_req_valid=0;cc_req_valid=0;expand_valid=0;seed_valid=0;cs_req_valid=0;k_cfg_valid=0;cf_load_valid=0;rc_req_valid=0;
 recovering=1;armed=0;as_recover_version=6;as_recover_query=0;crc_pin_flip=0;retry_cookie=32'hc0030001;
 warm_pcrc=g3_saved_pcrc;warm_qcrc=g3_saved_qcrc;
 if(g3_saved_count!=781||ls_count!=781||ls_crc!=g3_saved_lcrc||k_count!=3||k_saved_checkpoint!=19||as_bound_generation!=64'h100000003)$fatal(1,"G3 warm descriptor");
 $fdisplay(trace,"THIRD_WARM_START %0d %0d %0d %08h %08h %08h",cycles,k_count,k_saved_checkpoint,g3_saved_lcrc,warm_pcrc,warm_qcrc);
 k_rec_valid=1;do @(posedge clk);while(!k_rec_ready);@(negedge clk);k_rec_valid=0;
 wait(k_rcfg_valid);@(negedge clk);restore_epoch=k_new_query;restore_version=k_new_version;
 wait(k_labels_valid);@(negedge clk);
 if(k_count!=3||k_corrected!=1||!wm_owned||wm_fault||as_bound_generation!=64'h100000003)$fatal(1,"G3 warm owner repair corrected=%0d journal=%0d",k_corrected,k_count);
 $fdisplay(trace,"THIRD_WARM_OWNER %0d %0d %0d",cycles,k_corrected,k_count);
 if(!$value$plusargs("g3imports=%s",warm_path))$fatal(1,"G3 warm source path");warm_fd=$fopen(warm_path,"r");if(!warm_fd)$fatal(1,"G3 warm source open");
 for(integer x=0;x<g3_saved_count;x=x+1)begin
  rc=$fscanf(warm_fd,"%d",import_node);if(rc!=1)$fatal(1,"G3 import node");
  for(integer f=0;f<5;f=f+1)begin rc=$fscanf(warm_fd,"%h",word);if(rc!=1)$fatal(1,"G3 import field");import_record[f*32+:32]=word;end
  @(negedge clk);lr_s_valid=1;lr_s_node=import_node;lr_s_payload=import_record;lr_s_last=x+1==g3_saved_count;do @(posedge clk);while(!lr_s_ready);@(negedge clk);lr_s_valid=0;
 end
 $fclose(warm_fd);
 wait(wm_receipts[0]);
 if(lr_source_crc!=g3_saved_lcrc||lr_written!=781||lr_verified!=781||wm_joined||k_rsp_valid)$fatal(1,"G3 label receipt");
 $fdisplay(trace,"THIRD_WARM_LABELS %0d %0d %0d %08h",cycles,lr_written,lr_verified,lr_source_crc);
 cap_path_restore=1;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<156;x=x+1)begin
  @(negedge clk);warm_pi=x;warm_pd=g3_saved_path[x];warm_plast=x==155;warm_psv=1;do @(posedge clk);while(!system.cp_s_ready);@(negedge clk);warm_psv=0;
  $fdisplay(trace,"THIRD_WARM_PATH %0d %0d %08h",cycles,x,g3_saved_path[x]);
 end
 wait(cap_path_rsp_valid);repeat(8)begin @(negedge clk);
  if(cap_path_status||cap_path_crc!=g3_saved_pcrc||wm_receipts!=1||wm_joined||k_rsp_valid||!wm_owned||recover_open||pc_owned)$fatal(1,"G3 path held");
 end
 cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
 qc_cp_restore=1;qc_cp_expected_crc=g3_saved_qcrc;qc_cp_generation=0;qc_cp_valid=1;do @(posedge clk);while(!qc_cp_ready);@(negedge clk);qc_cp_valid=0;
 for(integer x=0;x<10;x=x+1)begin
  @(negedge clk);qc_cp_s_index=x;qc_cp_s_data=g3_saved_query[x];qc_cp_s_last=x==9;qc_cp_s_valid=1;do @(posedge clk);while(!qc_cp_s_ready);@(negedge clk);qc_cp_s_valid=0;
  $fdisplay(trace,"THIRD_WARM_QUERY %0d %0d %08h",cycles,x,g3_saved_query[x]);
 end
 wait(qc_cp_rsp_valid);repeat(8)begin @(negedge clk);
  if(qc_cp_status||qc_cp_crc!=g3_saved_qcrc||wm_receipts!=3||wm_joined||k_rsp_valid||!wm_owned||recover_open)$fatal(1,"G3 query held");
 end
 qc_cp_rsp_ready=1;@(negedge clk);qc_cp_rsp_ready=0;
 wait(k_rsp_valid);repeat(8)begin @(negedge clk);
  if(k_rsp_status||k_rsp_cookie!=32'hc0030001||k_corrected!=1||k_count||!wm_owned||!wm_joined||wm_fault||recover_open||rc_slots!=3||system.controller.last_sequence!=180328)$fatal(1,"G3 warm complete");
  $fdisplay(trace,"THIRD_WARM_HELD %0d %0d %0d %0d %0d %0d %0d",cycles,k_rsp_status,k_corrected,k_count,wm_receipts,wm_owned,recover_open);
 end
 k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;wait(recover_open);
 if(wm_owned||query_version!=6||p_active_query!=0||p_active_price!=6||rc_slots!=3||system.controller.last_sequence!=180328||k_saved_checkpoint!=19)$fatal(1,"G3 warm release");
 $fdisplay(trace,"THIRD_WARM_RELEASE %0d %0d %0d %0d %0d %0d",cycles,query_version,p_active_query,p_active_price,rc_slots,system.controller.last_sequence);
 owner_op(0,339193,1,1);owner_op(0,990179,2,2);owner_op(0,558358,4,2);owner_op(0,265324,5,1);iter2_foreign_probe;
end endtask

task cumulative_g4_copy;begin
 g4_phase=1;
 $fdisplay(trace,"G4_ROTATION_BEGIN %0d %0d %0d %0d",cycles,as_rbeats,g3_memory.rbeats,g3_memory.wbeats);
 @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;
 $fdisplay(trace,"CUMULATIVE_PRECONDITION %0d %0d %0d %0d %0d %0d %0d %016h %0d %0d %0d",cycles,pc_owned,g3_healthy,g3_bound,g3_data_error,g3_coverage_error,g3_dirty,as_bound_generation,k_saved_checkpoint,rc_slots,system.controller.last_sequence);
 if(!pc_owned||!g3_healthy||!g3_bound||!g3_data_error||g3_coverage_error||g3_dirty!=4||as_bound_generation!=64'h100000003||k_saved_checkpoint!=19||rc_slots!=7||system.controller.last_sequence!=180329)$fatal(1,"actual G4 rearm preconditions");
 $fdisplay(trace,"CUMULATIVE_REARM_SOURCE %0d %0d %0d %0d %0d %0d %0d",cycles,pc_owned,g3_healthy,owner_drained,f_all_drained,g3_data_error,g3_dirty);
 cumulative_command(1);cumulative_result(1,0,0);
 if(g3_data_error||g3_coverage_error||g3_dirty!=4)$fatal(1,"cumulative rearm lost coverage");
 cumulative_command(2);cumulative_result(2,0,4);
 if(!g3_manifest||!g3_receipt||g3_rd!=design_id||g3_rb!=64'h100000001||g3_rg!=64'h100000004||g3_rc!=20||g3_rdst!=64'ha000000000||g3_dirty!=4||as_bound_generation!=64'h100000003||k_saved_checkpoint!=19)$fatal(1,"G4 candidate descriptor/current G2");
 $fdisplay(trace,"CUMULATIVE_G4_CANDIDATE %0d %016h %0d %016h %0d",cycles,g3_rg,g3_rc,g3_rdst,g3_dirty);
$fdisplay(trace,"G4_ROTATION_COPIED %0d %0d %0d %0d",cycles,as_rbeats,g3_memory.rbeats,g3_memory.wbeats);
end endtask
task publish_g4;reg[1:0]accepted;begin
 g3_phase=1;ls_emitted=0;rc=$value$plusargs("g3negative=%d",g3_negative);
 @(negedge clk);g3_arm=1;@(negedge clk);g3_arm=0;
 runtime_label_snapshot;
 if(ls_count!=781||ls_pages!=393||g3_bundle_fault)$fatal(1,"G4 native label cardinality");
 cap_path_restore=0;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<156;x=x+1)begin
  wait(cap_path_m_valid);@(negedge clk);if(cap_path_m_index!=x||cap_path_m_last!=(x==155))$fatal(1,"G4 path boundary");cap_path_image[x]=cap_path_m_data;
  $fdisplay(trace,"G4_PATH_WORD %0d %0d %08h",cycles,x,cap_path_m_data);cap_path_m_ready=1;@(negedge clk);cap_path_m_ready=0;
 end
 wait(cap_path_rsp_valid);repeat(8)begin @(negedge clk);if(cap_path_status||cap_path_image[0]!=1||cap_path_image[39]!=1||cap_path_image[78]!=1||cap_path_image[117]!=0||pc_release_ready||!pc_owned)$fatal(1,"G4 path held");end
 $fdisplay(trace,"G4_PATH_RESULT %0d %08h",cycles,cap_path_crc);cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
 qc_cp_generation=64'h100000004;iter2_export_query;
 if({qcp_image[5],qcp_image[4]}!=64'h100000004||qcp_image[6]!=6||qcp_image[7]!=32'h58||qcp_image[8]!=180329||g3_bundle_fault||g3_export_receipts!=7)$fatal(1,"G4 query/bundle identity");
 for(integer x=0;x<10;x=x+1)$fdisplay(trace,"G4_QUERY_WORD %0d %0d %08h",cycles,x,qcp_image[x]);
 $fdisplay(trace,"G4_BUNDLE %0d %0d %08h %08h %08h %0d %0d %0d",cycles,g3_lcount,g3_lcrc,g3_pcrc,g3_qcrc,g3_receipt,g3_manifest,g3_bundle_manifest);
 if(!g3_negative&&!g3_bundle_manifest)$fatal(1,"G4 manifest before publication");
 joint_watch=0;
 @(negedge clk);jp_start=1;do @(posedge clk);while(!jp_start_ready);@(negedge clk);jp_start=0;
 jp_authority_stage=1;authority_bind=1;do @(posedge clk);while(!as_cfg_ready);@(negedge clk);authority_bind=0;
 wait(as_cfg_rsp_valid);repeat(8)begin @(negedge clk);if(as_cfg_status||system.jp_ap||as_bound_generation!=64'h100000003||k_count!=3||pc_release_ready)$fatal(1,"G4 authority held");
  $fdisplay(trace,"G4_AUTH_HELD %0d %0d %0d %0d %0d",cycles,g3_healthy,f_backend_idle,g3_receipt,g3_manifest);
 end
 authority_ack=1;@(negedge clk);authority_ack=0;wait(system.jp_ap);
 jp_load=3;while(jp_load!=0)begin @(posedge clk);accepted=jp_load&jp_ready;@(negedge clk);jp_load=jp_load&~accepted;end
 wait(jp_reply==3);repeat(8)begin @(negedge clk);if(jp_status||pc_release_ready||system.jp_prepared||k_count!=3||k_saved_checkpoint!=19)$fatal(1,"G4 metadata held");end
 jp_ack=3;@(negedge clk);jp_ack=0;wait(system.jp_prepared==3);
 if(g3_negative)begin
  repeat(64)begin @(negedge clk);if(g3_receipt||g3_manifest||g3_bundle_manifest||jp_commit_ready||as_bound_generation!=64'h100000003||k_saved_checkpoint!=19||k_count!=3||joint_pulses!=2||pc_release_ready||g3_bundle_fault||g3_export_receipts!=7)$fatal(1,"G4 negative containment");end
  $fdisplay(trace,"G4_PUBLISH_BLOCKED %0d %0d %0d %0d %0d",cycles,g3_receipt,g3_export_receipts,k_saved_checkpoint,k_count);$fflush(trace);$display("G4_NEGATIVE_OBSERVED");$finish;
 end
 for(integer n=0;n<64&&(g3_bundle_manifest!==1'b1);n=n+1)begin
  @(negedge clk);$fdisplay(trace,"G4_RETIRE_WAIT %0d %0d %0d %0d %0d %0d",cycles,g3_receipt,g3_manifest,g3_bundle_manifest,k_permit,g3_writer.publication_retired);
 end
 if(g3_bundle_manifest!==1'b1||g3_bundle_fault||k_saved_checkpoint!=19||k_count!=3||system.jp_ccp!=19||k_permit)$fatal(1,"G4 prepared identity/retired manifest");
 $fdisplay(trace,"G4_PREPARED_PROOF %0d %0d %0d %0d %0d %0d",cycles,g3_receipt,g3_manifest,g3_bundle_manifest,k_permit,g3_writer.publication_retired);
 jp_commit=1;do @(posedge clk);while(!jp_commit_ready);@(negedge clk);jp_commit=0;
 wait(jp_done);repeat(8)begin @(negedge clk);if(jp_result||pc_release_ready||k_count||k_saved_checkpoint!=20||system.jp_ccp!=20||as_bound_generation!=64'h100000004||joint_pulses!=3||g3_bundle_owned||g3_bundle_fault)$fatal(1,"G4 publication identity");end
 jp_done_ready=1;@(negedge clk);jp_done_ready=0;wait(!jp_owned);jp_authority_stage=0;
 ap_get(339193,26422,64'h100000003,1,0,0);
 ap_get(339193,26422,64'h100000004,0,1,1);ap_get(990179,26422,64'h100000004,0,2,2);ap_get(558358,26422,64'h100000004,0,4,2);ap_get(558358,23916,64'h100000004,0,1,2);ap_get(265324,26422,64'h100000004,0,5,1);
 qc_cp_generation=0;iter2_export_query;
 if({qcp_image[5],qcp_image[4]}!=64'h100000004||qc_cp_crc!=g3_qcrc||system.controller.last_sequence!=180329)$fatal(1,"G4 published query export");
 pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;wait(!pc_owned);
 $fdisplay(trace,"G4_PUBLISHED %0d %016h %0d %0d %0d %0d",cycles,as_bound_generation,k_saved_checkpoint,query_version,rc_slots,system.controller.last_sequence);$display("G4_PUBLISH_PASS");
end endtask
task fourth_path_snapshot(input integer capture);begin
 cap_path_restore=0;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<156;x=x+1)begin
  wait(cap_path_m_valid);@(negedge clk);if(cap_path_m_index!=x||cap_path_m_last!=(x==155))$fatal(1,"fourth snapshot framing");
  cap_path_image[x]=cap_path_m_data;$fdisplay(trace,"FOURTH_PATH_WORD %0d %0d %0d %08h",cycles,capture,x,cap_path_m_data);
  cap_path_m_ready=1;@(negedge clk);cap_path_m_ready=0;
 end
 wait(cap_path_rsp_valid);@(negedge clk);if(cap_path_status)$fatal(1,"fourth snapshot status");
 $fdisplay(trace,"FOURTH_PATH_DONE %0d %0d %08h %0d",cycles,capture,cap_path_crc,rc_slots);
 cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
end endtask

task fourth_prepare;begin
 $fdisplay(trace,"FOURTH_BEGIN %0d %0d %0d %0d",cycles,rc_slots,k_count,system.controller.last_sequence);
 @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;
 fourth_path_snapshot(0);
 if(rc_slots!=7||cap_path_image[117]!=0||k_count||k_saved_checkpoint!=20)$fatal(1,"fourth initial paths");
 cap_path_image[117]=1;cap_path_image[118]=3;cap_path_image[119]=26422;cap_path_image[120]=66893;cap_path_image[121]=6954;
 cap_path_image[122]=design_id[31:0];cap_path_image[123]=design_id[63:32];cap_path_image[124]=990178;cap_path_image[125]=558358;cap_path_image[126]=265324;
 prep_crc=32'hffffffff;for(integer x=0;x<156;x=x+1)prep_crc=prep_crc_word(prep_crc,cap_path_image[x]);warm_pcrc=~prep_crc;
 cap_path_restore=1;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<156;x=x+1)begin
  @(negedge clk);warm_pi=x;warm_pd=cap_path_image[x];warm_plast=x==155;warm_psv=1;do @(posedge clk);while(!system.cp_s_ready);@(negedge clk);warm_psv=0;
  $fdisplay(trace,"FOURTH_PATH_IMPORT %0d %08h",x,cap_path_image[x]);
 end
 wait(cap_path_rsp_valid);repeat(8)begin @(negedge clk);if(cap_path_status||cap_path_crc!=warm_pcrc||rc_slots!=15||k_count||!pc_owned)$fatal(1,"fourth metadata registration");end
 cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
 pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;wait(!pc_owned);
 stage_no=7;owner_op(0,990178,1,1);owner_op(0,558358,4,2);owner_op(0,265324,5,1);
 route_command(1,3,6954,180330);
 owner_op(0,990178,0,0);owner_op(0,558358,3,2);owner_op(0,265324,4,1);owner_op(0,339193,1,1);owner_op(0,990179,2,2);iter2_foreign_probe;
 if(rc_slots!=7||system.controller.last_sequence!=180329||k_saved_checkpoint!=20||k_count!=3||fault||rc_fault||k_fault)$fatal(1,"fourth preparation continuity");
 $fdisplay(trace,"FOURTH_PREPARED %0d %0d %0d %0d",cycles,rc_slots,k_count,system.controller.last_sequence);
end endtask
reg[31:0]g4_saved_path[0:155],g4_saved_query[0:9];reg[31:0]g4_saved_pcrc,g4_saved_qcrc,g4_saved_lcrc,g4_saved_count;
task fourth_query;begin
 for(integer x=0;x<156;x=x+1)g4_saved_path[x]=cap_path_image[x];
 for(integer x=0;x<10;x=x+1)g4_saved_query[x]=qcp_image[x];
 g4_saved_pcrc=g3_pcrc;g4_saved_qcrc=g3_qcrc;g4_saved_lcrc=g3_lcrc;g4_saved_count=g3_lcount;
 fourth_prepare;
 $fclose(fd_gold);$fclose(candidates_fd);$fclose(polls_fd);$fclose(finals_fd);
 if(!$value$plusargs("cost4=%s",path))$fatal(1,"cost4");fd_gold=$fopen(path,"r");
 if(!$value$plusargs("candidates4=%s",path))$fatal(1,"candidates4");candidates_fd=$fopen(path,"r");
 if(!$value$plusargs("polls4=%s",path))$fatal(1,"polls4");polls_fd=$fopen(path,"r");
 if(!$value$plusargs("finals4=%s",path))$fatal(1,"finals4");finals_fd=$fopen(path,"r");
 if(!fd_gold||!candidates_fd||!polls_fd||!finals_fd)$fatal(1,"fourth oracle files");
 poll_i=0;expand_i=0;candidate_i=0;commits=0;offers=0;outputs=0;count2=0;physical_expands=0;metadata_calls=0;visited_reads=0;
 query_index=3;selected_sink=6954;selected_connection=170791;selected_sequence=180330;stopped=0;armed=0;replayed=1;warm_running=0;
 g4_warm_mode=1;replayed=0;armed=1;injection_seen=0;eligible_responses=0;fault_after=0;fault_case=3;wm_enable=1;warm_running=1;recovering=1;
 $fdisplay(trace,"FOURTH_FAULT_BEGIN %0d %0d %0d %0d",cycles,k_count,k_saved_checkpoint,system.controller.last_sequence);
 fault_query;
 if(qc_rsp_committed||qc_rsp_nodes||qc_rsp_acked||k_count!=3||rc_slots!=7||system.controller.last_sequence!=180330)$fatal(1,"G4 failed search/consumed sequence");
 $fdisplay(trace,"FOURTH_FAULT_DONE %0d %0d %0d %0d %0d %0d %0d %0d",cycles,poll_i,expand_i,candidate_i,commits,qc_rsp_status,qc_rsp_detail,system.controller.last_sequence);
 fourth_warm_restore;
 fourth_floor_probe;
 fourth_prepare;
 rc=$fseek(polls_fd,0,0);if(rc)$fatal(1,"fourth poll rewind");rc=$fseek(candidates_fd,0,0);if(rc)$fatal(1,"fourth candidate rewind");rc=$fseek(fd_gold,0,0);if(rc)$fatal(1,"fourth cost rewind");
 poll_i=0;expand_i=0;candidate_i=0;commits=0;outputs=0;offers=0;count2=0;physical_expands=0;metadata_calls=0;visited_reads=0;stopped=0;replayed=1;warm_running=0;
 $fdisplay(trace,"FOURTH_RETRY_BEGIN %0d",cycles);
 autonomous_query;
 if(commits!=231||candidate_i!=402||expand_i!=82||poll_i!=83||rc_slots!=15||system.controller.last_sequence!=180330||query_version!=7||p_active_query!=1||p_active_price!=7||k_count!=3||k_saved_checkpoint!=20)$fatal(1,"fourth aggregate/context");
 owner_op(0,990178,1,1);owner_op(0,339193,1,1);owner_op(0,990179,2,2);owner_op(0,558358,4,2);owner_op(0,265324,5,1);iter2_foreign_probe;
 control(1);
 @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;
 fourth_path_snapshot(1);
 qc_cp_generation=0;qcp_start(0);
 for(integer x=0;x<10;x=x+1)begin
  wait(qc_cp_m_valid);@(negedge clk);if(qc_cp_m_index!=x||qc_cp_m_last!=(x==9))$fatal(1,"fourth query export");qcp_image[x]=qc_cp_m_data;
  $fdisplay(trace,"FOURTH_QUERY_WORD %0d %0d %08h",cycles,x,qc_cp_m_data);qc_cp_m_ready=1;@(negedge clk);qc_cp_m_ready=0;
 end
 qcp_result(0);if(qcp_image[8]!=180330||qcp_image[6]!=7||qcp_image[7]!=32'h5d||{qcp_image[5],qcp_image[4]}!=64'h100000004)$fatal(1,"fourth ledger floor");
 pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;wait(!pc_owned);
 $fdisplay(trace,"FOURTH_PASS %0d %0d %0d %0d %0d %0d %0d %08h",cycles,poll_i,expand_i,candidate_i,commits,rc_slots,system.controller.last_sequence,qc_cp_crc);
 $display("FOURTH_WARM_PASS polls=83 expands=82 candidates=402 costs=231");
end endtask

task fourth_warm_restore;begin
 q_cfg_valid=0;g_cfg_valid=0;d_cfg_valid=0;t_cfg_valid=0;owner_cfg_valid=0;cs_cfg_valid=0;host_ctrl_valid=0;host_design_req_valid=0;host_io_valid=0;host_owner_req_valid=0;cc_req_valid=0;expand_valid=0;seed_valid=0;cs_req_valid=0;k_cfg_valid=0;cf_load_valid=0;rc_req_valid=0;
 recovering=1;armed=0;as_recover_version=7;as_recover_query=1;crc_pin_flip=0;retry_cookie=32'hc0040001;
 warm_pcrc=g4_saved_pcrc;warm_qcrc=g4_saved_qcrc;
 if(g4_saved_count!=781||ls_count!=781||ls_crc!=g4_saved_lcrc||k_count!=3||k_saved_checkpoint!=20||as_bound_generation!=64'h100000004)$fatal(1,"G4 warm descriptor");
 $fdisplay(trace,"FOURTH_WARM_START %0d %0d %0d %08h %08h %08h",cycles,k_count,k_saved_checkpoint,g4_saved_lcrc,warm_pcrc,warm_qcrc);
 k_rec_valid=1;do @(posedge clk);while(!k_rec_ready);@(negedge clk);k_rec_valid=0;
 wait(k_rcfg_valid);@(negedge clk);restore_epoch=k_new_query;restore_version=k_new_version;
 wait(k_labels_valid);@(negedge clk);
 if(k_count!=3||k_corrected!=3||!wm_owned||wm_fault||as_bound_generation!=64'h100000004)$fatal(1,"G4 warm owner repair corrected=%0d journal=%0d",k_corrected,k_count);
 $fdisplay(trace,"FOURTH_WARM_OWNER %0d %0d %0d",cycles,k_corrected,k_count);
 if(!$value$plusargs("g4imports=%s",warm_path))$fatal(1,"G4 warm source path");warm_fd=$fopen(warm_path,"r");if(!warm_fd)$fatal(1,"G4 warm source open");
 for(integer x=0;x<g4_saved_count;x=x+1)begin
  rc=$fscanf(warm_fd,"%d",import_node);if(rc!=1)$fatal(1,"G4 import node");
  for(integer f=0;f<5;f=f+1)begin rc=$fscanf(warm_fd,"%h",word);if(rc!=1)$fatal(1,"G4 import field");import_record[f*32+:32]=word;end
  @(negedge clk);lr_s_valid=1;lr_s_node=import_node;lr_s_payload=import_record;lr_s_last=x+1==g4_saved_count;do @(posedge clk);while(!lr_s_ready);@(negedge clk);lr_s_valid=0;
 end
 $fclose(warm_fd);
 wait(wm_receipts[0]);
 if(lr_source_crc!=g4_saved_lcrc||lr_written!=781||lr_verified!=781||wm_joined||k_rsp_valid)$fatal(1,"G4 label receipt");
 $fdisplay(trace,"FOURTH_WARM_LABELS %0d %0d %0d %08h",cycles,lr_written,lr_verified,lr_source_crc);
 cap_path_restore=1;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<156;x=x+1)begin
  @(negedge clk);warm_pi=x;warm_pd=g4_saved_path[x];warm_plast=x==155;warm_psv=1;do @(posedge clk);while(!system.cp_s_ready);@(negedge clk);warm_psv=0;
  $fdisplay(trace,"FOURTH_WARM_PATH %0d %0d %08h",cycles,x,g4_saved_path[x]);
 end
 wait(cap_path_rsp_valid);repeat(8)begin @(negedge clk);
  if(cap_path_status||cap_path_crc!=g4_saved_pcrc||wm_receipts!=1||wm_joined||k_rsp_valid||!wm_owned||recover_open||pc_owned)$fatal(1,"G4 path held");
 end
 cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
 qc_cp_restore=1;qc_cp_expected_crc=g4_saved_qcrc;qc_cp_generation=0;qc_cp_valid=1;do @(posedge clk);while(!qc_cp_ready);@(negedge clk);qc_cp_valid=0;
 for(integer x=0;x<10;x=x+1)begin
  @(negedge clk);qc_cp_s_index=x;qc_cp_s_data=g4_saved_query[x];qc_cp_s_last=x==9;qc_cp_s_valid=1;do @(posedge clk);while(!qc_cp_s_ready);@(negedge clk);qc_cp_s_valid=0;
  $fdisplay(trace,"FOURTH_WARM_QUERY %0d %0d %08h",cycles,x,g4_saved_query[x]);
 end
 wait(qc_cp_rsp_valid);repeat(8)begin @(negedge clk);
  if(qc_cp_status||qc_cp_crc!=g4_saved_qcrc||wm_receipts!=3||wm_joined||k_rsp_valid||!wm_owned||recover_open)$fatal(1,"G4 query held");
 end
 qc_cp_rsp_ready=1;@(negedge clk);qc_cp_rsp_ready=0;
 wait(k_rsp_valid);repeat(8)begin @(negedge clk);
  if(k_rsp_status||k_rsp_cookie!=32'hc0040001||k_corrected!=3||k_count||!wm_owned||!wm_joined||wm_fault||recover_open||rc_slots!=7||system.controller.last_sequence!=180329)$fatal(1,"G4 warm complete");
  $fdisplay(trace,"FOURTH_WARM_HELD %0d %0d %0d %0d %0d %0d %0d",cycles,k_rsp_status,k_corrected,k_count,wm_receipts,wm_owned,recover_open);
 end
 k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;wait(recover_open);
 if(wm_owned||query_version!=7||p_active_query!=1||p_active_price!=7||rc_slots!=7||system.controller.last_sequence!=180329||k_saved_checkpoint!=20)$fatal(1,"G4 warm release");
 $fdisplay(trace,"FOURTH_WARM_RELEASE %0d %0d %0d %0d %0d %0d",cycles,query_version,p_active_query,p_active_price,rc_slots,system.controller.last_sequence);
 owner_op(0,990178,1,1);owner_op(0,339193,1,1);owner_op(0,990179,2,2);owner_op(0,558358,4,2);owner_op(0,265324,5,1);iter2_foreign_probe;
end endtask
task fourth_floor_probe;begin
 if(rc_slots!=7||k_count||system.controller.last_sequence!=180329||query_version!=7||p_active_query!=1||p_active_price!=7)$fatal(1,"G4 floor probe preconditions");
 $fdisplay(trace,"FOURTH_FLOOR_BEGIN %0d %0d %0d %0d",cycles,rc_slots,k_count,system.controller.last_sequence);
 @(negedge clk);qc_cmd_cookie=32'hce040001;qc_cmd_source=66893;qc_cmd_key=0;qc_cmd_nodes=9089009;qc_cmd_max_polls=65536;
 qc_cmd_poll_cookie=32'hc0040000;qc_cmd_design=design_id;qc_cmd_query=restore_epoch;qc_cmd_price=restore_version[3:0];
 qc_cmd_expand={restore_version,32'd291,32'd279,32'd31,32'd23,32'd260,32'd180329,32'd26422,32'd6954,32'd0,32'd0,32'd0,32'd100,32'd170791};
 qc_cmd_slot=3;qc_cmd_route_cookie=32'hf0040000;qc_cmd_valid=1;do @(posedge clk);while(!qc_cmd_ready);@(negedge clk);qc_cmd_valid=0;
 wait(qc_rsp_valid);repeat(8)begin @(negedge clk);
  if(qc_rsp_status!=1||qc_rsp_cookie!=32'hce040001||qc_rsp_committed||qc_prepare_acked||qc_cleanup_acked||qc_fault||ss_busy||k_count||rc_slots!=7||system.controller.last_sequence!=180329)$fatal(1,"G4 restored floor rejected incorrectly");
 end
 $fdisplay(trace,"FOURTH_FLOOR_REJECT %0d %0d %0d %0d %0d",cycles,qc_rsp_status,qc_prepare_acked,rc_slots,system.controller.last_sequence);
 qc_rsp_ready=1;@(negedge clk);qc_rsp_ready=0;wait(!qc_busy);
end endtask


// Observe actual downstream acceptance after the frontend queue, including WW.
`define SEED_PM system.inner.backend.dut.core.p.pager
`define SEED_LR system.inner.backend.label_restore
always @(posedge clk)if(!rst)begin
 if(lr_start_valid&&lr_start_ready&&g4_warm_mode&&SEED_BYPASS)begin
  if(!seed_enable||seed_start_consumed)$fatal(1,"seed permission not offered at start");
  seed_start_consumed<=1;
  $fdisplay(seed_log,"START %0d",cycles);
 end
 if(`SEED_PM.io_valid&&`SEED_PM.io_ready)begin
  if(`SEED_PM.baseline_restore_write)begin
   if(!SEED_BYPASS||!g4_warm_mode||!seed_start_consumed||seed_enable||
      !f_recovery_owned||!system.inner.backend.k_labels_valid||!`SEED_LR.l_import||
      !`SEED_PM.io_write||`SEED_PM.baseline_raw_probe)
       $fatal(1,"unauthorized restore seed bypass");
   seed_requests<=seed_requests+1;
   $fdisplay(seed_log,"WRITE %0d %0d %0d %08h %0d",cycles,
    `SEED_PM.io_node,`SEED_PM.io_field,`SEED_PM.io_value,`SEED_LR.state);
  end
  if(SEED_BYPASS&&g4_warm_mode&&`SEED_LR.l_import&&
     !`SEED_PM.baseline_restore_write)$fatal(1,"lost queued restore provenance");
 end
 if(SEED_BYPASS&&g4_warm_mode&&lr_rsp_ready&&system.inner.backend.lr_rsp_valid)begin
  if(lr_rsp_status!=0||lr_written!=781||lr_verified!=781||seed_requests!=3905)
   $fatal(1,"seed bypass restore completion mismatch");
  $fdisplay(seed_log,"PASS %0d %0d %0d %0d",cycles,seed_requests,lr_written,lr_verified);
 end
end
`undef SEED_PM
`undef SEED_LR

endmodule

`default_nettype wire
