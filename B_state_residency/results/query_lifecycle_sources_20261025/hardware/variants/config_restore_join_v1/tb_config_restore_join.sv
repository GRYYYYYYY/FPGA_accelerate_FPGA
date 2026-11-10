`timescale 1ns/1ps
module tb_candidate_offer;
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
assign host_ctrl_ready=!lr_busy&&!rc_block&&raw_host_ctrl_ready;
wire raw_host_design_req_ready;
assign host_design_req_ready=!rc_block&&raw_host_design_req_ready;
wire raw_expand_ready;
assign expand_ready=!rc_block&&recover_open&&raw_expand_ready;
wire raw_seed_ready;
assign seed_ready=!rc_block&&recover_open&&raw_seed_ready;
wire raw_q_cfg_ready;
assign q_cfg_ready=!cf_busy&&!rc_block&&raw_q_cfg_ready;
wire raw_g_cfg_ready;
assign g_cfg_ready=!cf_busy&&!rc_block&&raw_g_cfg_ready;
wire raw_d_cfg_ready;
assign d_cfg_ready=!cf_busy&&!rc_block&&raw_d_cfg_ready;
wire raw_t_cfg_ready;
assign t_cfg_ready=!cf_busy&&!rc_block&&raw_t_cfg_ready;
wire raw_owner_cfg_ready;
assign owner_cfg_ready=!cf_busy&&!rc_block&&raw_owner_cfg_ready;
wire raw_cs_cfg_ready;
assign cs_cfg_ready=!cf_busy&&!rc_block&&raw_cs_cfg_ready;
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
assign recover_open=k_permit;
assign host_owner_req_ready=!k_busy&&mux_h_o_ready;
assign host_owner_rsp_valid=!k_busy&&mux_h_o_rsp_valid;
assign k_o_ready=k_busy&&mux_h_o_ready;
assign k_o_rsp_valid=k_busy&&mux_h_o_rsp_valid;
recovery_coordinator #(.ENTRIES(32),.RESET_HOLD(5),.MAX_CYCLES(1048576)) recovery_ctl(
 .clk(clk),.cold_rst(k_cold_rst),.abort(cf_fault||(cf_rsp_valid&&cf_rsp_cookie!=32'hf0010001)||lr_fault||(lr_rsp_valid&&lr_rsp_cookie!=32'he0010001)),.backend_drained(label_drained&&owner_drained),.normal_retired(k_normal_retired),
 .cfg_valid(k_cfg_valid),.cfg_ready(k_cfg_ready),.cfg_authoritative(1'b1),.cfg_design(design_id),.cfg_checkpoint(k_checkpoint),.cfg_version(k_cfg_version),.cfg_query(k_cfg_query),.cfg_price(k_cfg_price),
 .cfg_rsp_valid(k_cfg_rsp_valid),.cfg_rsp_ready(k_cfg_rsp_ready),.cfg_status(k_cfg_status),
 .j_valid(k_j_valid),.j_ready(k_j_ready),.j_node(k_j_node),.j_net(k_j_net),.j_op(k_j_op),.journal_count(k_count),.journal_full(k_full),.permit_work(k_permit),
 .recover_valid(k_rec_valid),.recover_ready(k_rec_ready),.recover_cookie(32'hc0010001),.recover_checkpoint(32'd17),.recover_version(32'd4),.recover_design(design_id),.recover_query(2'd2),.recover_price(4'd4),
 .target_reset(k_target_reset),.reconfigure_valid(k_rcfg_valid),.reconfigure_done(k_rcfg_done),.labels_valid(k_labels_valid),.labels_done(k_labels_done),
 .saved_design(k_saved_design),.saved_checkpoint(k_saved_checkpoint),.new_version(k_new_version),.new_query(k_new_query),.new_price(k_new_price),
 .rsp_valid(k_rsp_valid),.rsp_ready(k_rsp_ready),.rsp_status(k_rsp_status),.rsp_cookie(k_rsp_cookie),.rsp_corrected(k_corrected),.busy(k_busy),.fault(k_fault),
 .a_valid(k_a_valid),.a_ready(k_a_ready),.a_node(k_a_node),.a_net(k_a_net),.a_cookie(k_a_cookie),.a_checkpoint(k_a_checkpoint),.a_design(k_a_design),
 .a_rsp_valid(k_a_rsp_valid),.a_rsp_ready(k_a_rsp_ready),.a_status(k_a_status),.a_rsp_cookie(k_a_rsp_cookie),.a_rsp_checkpoint(k_a_rsp_checkpoint),.a_rsp_design(k_a_rsp_design),.a_refs(k_a_refs),.a_occupancy(k_a_occ),
 .o_valid(k_o_valid),.o_ready(k_o_ready),.o_op(k_o_op),.o_node(k_o_node),.o_net(k_o_net),.o_cookie(k_o_cookie),
 .o_rsp_valid(k_o_rsp_valid),.o_rsp_ready(k_o_rsp_ready),.o_status(host_owner_rsp_status),.o_rsp_cookie(host_owner_rsp_cookie),.o_count(host_owner_rsp_count),.o_occupancy(host_owner_rsp_occupancy));
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
assign lr_c_ready=lr_busy&&!rc_block&&raw_host_ctrl_ready;
assign lr_l_ready=lr_busy&&mux_h_l_ready;assign lr_l_rsp_valid=lr_busy&&mux_h_l_rsp_valid;
assign host_io_ready=!lr_busy&&mux_h_l_ready;assign host_io_rsp_valid=!lr_busy&&mux_h_l_rsp_valid;
label_restore_controller #(.MAX_RECORDS(512),.MAX_CYCLES(1048576))label_restore(
 .clk(clk),.rst(k_cold_rst),.abort(1'b0),.backend_drained(label_drained&&owner_drained),
 .start_valid(lr_start_valid),.start_ready(lr_start_ready),.start_design(k_saved_design),.expected_design(design_id),.start_checkpoint(k_saved_checkpoint),.expected_checkpoint(32'd17),
 .start_cookie(32'he0010001),.start_count(32'd328),.start_nodes(32'd9089009),.start_probe(32'd150697),.start_version(k_new_version),.start_query(k_new_query),.start_price(k_new_price),
 .s_valid(lr_s_valid),.s_ready(lr_s_ready),.s_node(lr_s_node),.s_cookie(32'he0010001),.s_payload(lr_s_payload),.s_last(lr_s_last),
 .rsp_valid(lr_rsp_valid),.rsp_ready(lr_rsp_ready),.rsp_status(lr_rsp_status),.rsp_cookie(lr_rsp_cookie),.written(lr_written),.verified(lr_verified),.busy(lr_busy),.fault(lr_fault),
 .c_valid(lr_c_valid),.c_ready(lr_c_ready),.c_op(lr_c_op),.c_query(lr_c_query),.c_price(lr_c_price),.c_version(lr_c_version),.c_rsp_valid(host_ctrl_rsp_valid&&lr_busy),.c_rsp_ready(lr_c_rsp_ready),.c_status(host_ctrl_status),
 .l_valid(lr_l_valid),.l_ready(lr_l_ready),.l_write(lr_l_write),.l_node(lr_l_node),.l_value(lr_l_value),.l_field(lr_l_field),.l_rsp_valid(lr_l_rsp_valid),.l_rsp_ready(lr_l_rsp_ready),.l_status(host_io_status),.l_present(host_io_present),.l_payload(host_io_payload));

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
assign cf_ready={raw_cs_cfg_ready,raw_owner_cfg_ready,raw_t_cfg_ready,raw_d_cfg_ready,raw_g_cfg_ready,raw_q_cfg_ready}&{6{!rc_block}};
assign cf_replies={cs_cfg_rsp_valid,owner_cfg_rsp_valid,t_cfg_rsp_valid,d_cfg_rsp_valid,g_cfg_rsp_valid,q_cfg_rsp_valid};
assign cf_status={cs_cfg_status,owner_cfg_status,t_cfg_status,d_cfg_status,g_cfg_status,q_cfg_status};
config_restore_controller #(.MAX_CYCLES(1048576))config_restore(
 .clk(clk),.rst(k_cold_rst),.abort(1'b0),.backend_drained(label_drained&&owner_drained),.normal_retired(k_normal_retired),
 .load_valid(cf_load_valid),.load_ready(cf_load_ready),.load_authoritative(1'b1),.load_payload(cf_input),.load_design(k_saved_design),.load_checkpoint(k_saved_checkpoint),.load_rsp_valid(cf_load_rsp_valid),.load_rsp_ready(cf_load_rsp_ready),.load_status(cf_load_status),
 .start_valid(k_rcfg_valid),.start_ready(),.start_design(k_saved_design),.start_checkpoint(k_saved_checkpoint),.start_cookie(32'hf0010001),.start_version(k_new_version),.start_price(k_new_price),
 .cfg_valid(cf_valid),.cfg_ready(cf_ready),.cfg_payload(cf_payload),.cfg_rsp_valid(cf_replies),.cfg_rsp_ready(cf_reply_ready),.cfg_status(cf_status),
 .rsp_valid(cf_rsp_valid),.rsp_ready(!k_rcfg_valid),.rsp_status(cf_rsp_status),.rsp_cookie(cf_rsp_cookie),.busy(cf_busy),.fault(cf_fault),.sent(cf_sent),.retired(cf_retired),.saved_design(cf_saved_design),.saved_checkpoint(cf_saved_checkpoint));
assign k_rcfg_done=cf_rsp_valid;

route_commit_host_adapter #(.MAX_PATH(32)) route_join(.clk(clk),.rst(rst),.abort(injected_abort),.active(p_active),.backend_drained(label_drained&&owner_drained),.j_valid(k_j_valid),.j_ready(k_j_ready),.j_node(k_j_node),.j_net(k_j_net),.j_op(k_j_op),.admit(!fault&&!busy&&!host_ctrl_valid&&!host_design_req_valid&&!expand_valid&&!seed_valid&&!q_cfg_valid&&!g_cfg_valid&&!d_cfg_valid&&!t_cfg_valid&&!owner_cfg_valid&&!cs_cfg_valid&&!host_io_valid&&!host_owner_req_valid&&!b_l_rsp_valid&&!b_o_rsp_valid&&!host_ctrl_rsp_valid&&!host_design_rsp_valid&&!seed_rsp_valid&&!result_valid&&!q_cfg_rsp_valid&&!g_cfg_rsp_valid&&!d_cfg_rsp_valid&&!t_cfg_rsp_valid&&!owner_cfg_rsp_valid&&!cs_cfg_rsp_valid),.active_query(p_active_query),.active_price(p_active_price),.active_version(query_version^(injected_drift?32'd1:32'd0)),.active_design(design_id),.req_valid(rc_req_valid&&recover_open),.req_ready(raw_recovery_ready),.req_op(rc_req_op),.req_slot(rc_req_slot),.req_cookie(rc_req_cookie),.req_source(32'd65185),.req_sink(rc_req_sink),.req_net(32'd2717),.req_sequence(rc_req_sequence),.rsp_valid(rc_rsp_valid),.rsp_ready(rc_rsp_ready),.rsp_status(rc_rsp_status),.rsp_cookie(rc_rsp_cookie),.rsp_nodes(rc_rsp_nodes),.rsp_acked(rc_rsp_acked),.busy(rc_busy),.fault(rc_fault),.block_external(rc_block),.slot_valid(rc_slots),.h_l_valid(lr_busy?lr_l_valid:host_io_valid),.b_l_valid(b_l_valid),.h_l_ready(mux_h_l_ready),.b_l_ready(b_l_ready),.h_l_write(lr_busy?lr_l_write:host_io_write),.b_l_write(b_l_write),.h_l_node(lr_busy?lr_l_node:host_io_node),.b_l_node(b_l_node),.h_l_value(lr_busy?lr_l_value:host_io_value),.b_l_value(b_l_value),.h_l_field(lr_busy?lr_l_field:host_io_field),.b_l_field(b_l_field),.h_l_rsp_valid(mux_h_l_rsp_valid),.b_l_rsp_valid(b_l_rsp_valid),.h_l_rsp_ready(lr_busy?lr_l_rsp_ready:host_io_rsp_ready),.b_l_rsp_ready(b_l_rsp_ready),.h_l_status(host_io_status),.b_l_status(b_l_status),.h_l_present(host_io_present),.b_l_present(b_l_present),.h_l_payload(host_io_payload),.b_l_payload(b_l_payload),.h_o_valid(k_busy?k_o_valid:host_owner_req_valid),.b_o_valid(b_o_valid),.h_o_ready(mux_h_o_ready),.b_o_ready(b_o_ready),.h_o_op(k_busy?k_o_op:host_owner_req_op),.b_o_op(b_o_op),.h_o_node(k_busy?k_o_node:host_owner_req_node),.b_o_node(b_o_node),.h_o_net(k_busy?k_o_net:host_owner_req_net),.b_o_net(b_o_net),.h_o_cookie(k_busy?k_o_cookie:host_owner_req_cookie),.b_o_cookie(b_o_cookie),.h_o_rsp_valid(mux_h_o_rsp_valid),.b_o_rsp_valid(b_o_rsp_valid),.h_o_rsp_ready(k_busy?k_o_rsp_ready:host_owner_rsp_ready),.b_o_rsp_ready(b_o_rsp_ready),.h_o_status(host_owner_rsp_status),.b_o_status(b_o_status),.h_o_rsp_cookie(host_owner_rsp_cookie),.b_o_rsp_cookie(b_o_rsp_cookie),.h_o_count(host_owner_rsp_count),.b_o_count(b_o_count),.h_o_occupancy(host_owner_rsp_occupancy),.b_o_occupancy(b_o_occupancy),.h_o_will_overuse(host_owner_rsp_will_overuse),.b_o_will_overuse(b_o_will_overuse));
assign rc_req_ready=raw_recovery_ready&&recover_open;
candidate_recursive_engine #(.SLOTS(SLOTS),.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS))dut(.host_io_valid(b_l_valid),.host_io_ready(b_l_ready),.host_io_write(b_l_write),.host_io_node(b_l_node),.host_io_value(b_l_value),.host_io_field(b_l_field),.host_io_rsp_valid(b_l_rsp_valid),.host_io_rsp_ready(b_l_rsp_ready),.host_io_status(b_l_status),.host_io_present(b_l_present),.host_io_payload(b_l_payload),.host_owner_req_valid(b_o_valid),.host_owner_req_ready(b_o_ready),.host_owner_req_op(b_o_op),.host_owner_req_node(b_o_node),.host_owner_req_net(b_o_net),.host_owner_req_cookie(b_o_cookie),.host_owner_rsp_valid(b_o_rsp_valid),.host_owner_rsp_ready(b_o_rsp_ready),.host_owner_rsp_status(b_o_status),.host_owner_rsp_cookie(b_o_rsp_cookie),.host_owner_rsp_count(b_o_count),.host_owner_rsp_occupancy(b_o_occupancy),.host_owner_rsp_will_overuse(b_o_will_overuse),.host_ctrl_valid(((lr_busy?lr_c_valid:host_ctrl_valid)&&!rc_block)),.host_ctrl_op(lr_busy?lr_c_op:host_ctrl_op),.host_ctrl_query(lr_busy?lr_c_query:host_ctrl_query),.host_ctrl_price(lr_busy?lr_c_price:host_ctrl_price),.host_ctrl_version(lr_busy?lr_c_version:host_ctrl_version),.host_ctrl_rsp_ready(lr_busy?lr_c_rsp_ready:host_ctrl_rsp_ready),.host_ctrl_ready(raw_host_ctrl_ready),.host_design_req_valid((host_design_req_valid&&!rc_block)),.host_design_req_ready(raw_host_design_req_ready),.expand_valid((expand_valid&&!rc_block&&recover_open)),.expand_ready(raw_expand_ready),.seed_valid((seed_valid&&!rc_block&&recover_open)),.seed_ready(raw_seed_ready),.q_cfg_valid(((cf_busy?cf_valid[0]:q_cfg_valid)&&!rc_block)),.q_cfg_ready(raw_q_cfg_ready),.g_cfg_valid(((cf_busy?cf_valid[1]:g_cfg_valid)&&!rc_block)),.g_cfg_ready(raw_g_cfg_ready),.d_cfg_valid(((cf_busy?cf_valid[2]:d_cfg_valid)&&!rc_block)),.d_cfg_ready(raw_d_cfg_ready),.t_cfg_valid(((cf_busy?cf_valid[3]:t_cfg_valid)&&!rc_block)),.t_cfg_ready(raw_t_cfg_ready),.owner_cfg_valid(((cf_busy?cf_valid[4]:owner_cfg_valid)&&!rc_block)),.owner_cfg_ready(raw_owner_cfg_ready),.cs_cfg_valid(((cf_busy?cf_valid[5]:cs_cfg_valid)&&!rc_block)),.cs_cfg_ready(raw_cs_cfg_ready),.q_cfg_rsp_ready(cf_busy?cf_reply_ready[0]:q_cfg_rsp_ready),.q_cfg_base(cf_busy?cf_payload[0+:64]:q_cfg_base),.q_cfg_design(cf_busy?cf_payload[64+:64]:q_cfg_design),.q_cfg_connections(cf_busy?cf_payload[128+:32]:q_cfg_connections),.q_cfg_nodes(cf_busy?cf_payload[160+:32]:q_cfg_nodes),.q_cfg_nets(cf_busy?cf_payload[192+:32]:q_cfg_nets),.q_cfg_revision(cf_busy?cf_payload[224+:32]:q_cfg_revision),.g_cfg_rsp_ready(cf_busy?cf_reply_ready[1]:g_cfg_rsp_ready),.g_cfg_offsets_base(cf_busy?cf_payload[384+:64]:g_cfg_offsets_base),.g_cfg_edges_base(cf_busy?cf_payload[448+:64]:g_cfg_edges_base),.g_cfg_attrs_base(cf_busy?cf_payload[512+:64]:g_cfg_attrs_base),.g_cfg_nodes(cf_busy?cf_payload[576+:32]:g_cfg_nodes),.g_cfg_edges(cf_busy?cf_payload[608+:32]:g_cfg_edges),.d_cfg_rsp_ready(cf_busy?cf_reply_ready[2]:d_cfg_rsp_ready),.d_cfg_base(cf_busy?cf_payload[768+:64]:d_cfg_base),.d_cfg_nodes(cf_busy?cf_payload[832+:32]:d_cfg_nodes),.t_cfg_rsp_ready(cf_busy?cf_reply_ready[3]:t_cfg_rsp_ready),.t_cfg_rows_base(cf_busy?cf_payload[1152+:64]:t_cfg_rows_base),.t_cfg_columns_base(cf_busy?cf_payload[1216+:64]:t_cfg_columns_base),.t_cfg_rows(cf_busy?cf_payload[1280+:32]:t_cfg_rows),.t_cfg_columns(cf_busy?cf_payload[1312+:32]:t_cfg_columns),.owner_cfg_rsp_ready(cf_busy?cf_reply_ready[4]:owner_cfg_rsp_ready),.owner_cfg_primary(cf_busy?cf_payload[1536+:64]:owner_cfg_primary),.owner_cfg_pool(cf_busy?cf_payload[1600+:64]:owner_cfg_pool),.owner_cfg_allocator(cf_busy?cf_payload[1664+:64]:owner_cfg_allocator),.owner_cfg_nodes(cf_busy?cf_payload[1728+:32]:owner_cfg_nodes),.owner_cfg_capacity(cf_busy?cf_payload[1760+:32]:owner_cfg_capacity),.cs_cfg_rsp_ready(cf_busy?cf_reply_ready[5]:cs_cfg_rsp_ready),.cs_cfg_history(cf_busy?cf_payload[1920+:64]:cs_cfg_history),.cs_cfg_prices(cf_busy?cf_payload[1984+:64]:cs_cfg_prices),.cs_cfg_nets(cf_busy?cf_payload[2048+:64]:cs_cfg_nets),.cs_cfg_design_id(cf_busy?cf_payload[2112+:64]:cs_cfg_design_id),.cs_cfg_nodes(cf_busy?cf_payload[2176+:32]:cs_cfg_nodes),.cs_cfg_net_count(cf_busy?cf_payload[2208+:32]:cs_cfg_net_count),.cs_cfg_version(cf_busy?cf_payload[2240+:32]:cs_cfg_version),.*);
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
 cycles<=cycles+1;if(cycles>3000000)$fatal(1,"watchdog");
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
  prior_drained<=label_drained&&owner_drained;last_k_reset<=k_target_reset;
  if(rc_req_valid&&rc_req_ready)k_normal_retired<=0;
  if(rc_rsp_valid&&rc_rsp_ready)k_normal_retired<=1;
  if(k_target_reset&&!last_k_reset)begin
   if(!prior_drained||!k_normal_retired)$fatal(1,"RTL reset before drain/retire");$fdisplay(trace,"RESET %0d %0d",cycles,k_count);
  end
  if(k_j_valid&&k_j_ready)begin last_j_cycle<=cycles;last_j_node<=k_j_node;$fdisplay(trace,"J %0d %0d %0d %0d",cycles,k_j_node,k_j_net,k_j_op);end
  if(route_join.held&&b_o_valid&&b_o_ready)begin
   if(cycles<=last_j_cycle||b_o_node!=last_j_node)$fatal(1,"owner forwarded before journal");$fdisplay(trace,"BF %0d %0d %0d",cycles,b_o_op,b_o_node);
  end
  if(k_o_valid&&k_o_ready)$fdisplay(trace,"KO %0d %0d %0d %0d",cycles,k_o_op,k_o_node,k_o_cookie);
  if(k_o_rsp_valid&&k_o_rsp_ready)$fdisplay(trace,"KR %0d %0d %0d %0d",cycles,host_owner_rsp_status,host_owner_rsp_count,host_owner_rsp_occupancy);
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
  $fdisplay(trace,"LX %0d %0d %0d %040h",cycles,host_io_status,host_io_present,host_io_payload);
  if(label_restore.state==4)$fdisplay(trace,"ABS %0d %040h",cycles,host_io_payload);
  if(label_restore.state==10)$fdisplay(trace,"CHECK %0d %0d %040h",cycles,label_restore.row[191:160],host_io_payload);
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
 @(negedge clk);q_cfg_valid=1;do @(posedge clk);while(!q_cfg_ready);@(negedge clk);q_cfg_valid=0;
 wait(q_cfg_rsp_valid);@(negedge clk);if(q_cfg_status)$fatal(1,"qconfig");q_cfg_rsp_ready=1;@(negedge clk);q_cfg_rsp_ready=0;
 @(negedge clk);g_cfg_valid=1;d_cfg_valid=1;t_cfg_valid=1;owner_cfg_valid=1;cs_cfg_valid=1;
 wait(g_cfg_ready&&d_cfg_ready&&t_cfg_ready&&owner_cfg_ready&&cs_cfg_ready);@(posedge clk);@(negedge clk);g_cfg_valid=0;d_cfg_valid=0;t_cfg_valid=0;owner_cfg_valid=0;cs_cfg_valid=0;
 wait(g_cfg_rsp_valid&&d_cfg_rsp_valid&&t_cfg_rsp_valid&&owner_cfg_rsp_valid&&cs_cfg_rsp_valid);@(negedge clk);
 if(g_cfg_status||d_cfg_status||t_cfg_status||owner_cfg_status||cs_cfg_status)$fatal(1,"config g=%0d d=%0d t=%0d o=%0d c=%0d",g_cfg_status,d_cfg_status,t_cfg_status,owner_cfg_status,cs_cfg_status);
 g_cfg_rsp_ready=1;d_cfg_rsp_ready=1;t_cfg_rsp_ready=1;owner_cfg_rsp_ready=1;cs_cfg_rsp_ready=1;
 @(negedge clk);g_cfg_rsp_ready=0;d_cfg_rsp_ready=0;t_cfg_rsp_ready=0;owner_cfg_rsp_ready=0;cs_cfg_rsp_ready=0;
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
 $fflush(trace);$fclose(trace);$display("CONFIG_RESTORE_JOIN_PASS case=%0d journal=%0d repairs=%0d epoch=%0d version=%0d cycles=%0d",fault_case,journal_count,repairs,restore_epoch,restore_version,cycles);$finish;
end
endmodule
