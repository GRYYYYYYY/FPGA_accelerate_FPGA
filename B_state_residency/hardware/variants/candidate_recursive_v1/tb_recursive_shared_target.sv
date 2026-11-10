`timescale 1ns/1ps
module tb_candidate_offer;
reg clk=0;always #5 clk=~clk;
wire  operation_pending;
reg  rst=0;
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
candidate_recursive_engine #(.SLOTS(SLOTS),.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS))dut(.*);
integer g_reads,g_writes,g_rbeats,g_wbeats,g_bs;
axi_file_memory #(.ADDR_BITS(64),.READ_ONLY(1),.MAX_BEATS(1),.TAG("graph"))mem_g(
.clk(clk),
.rst(rst),
.base0(g_cfg_offsets_base),
.base1(g_cfg_edges_base),
.base2(g_cfg_attrs_base),
.size0(64'd192),
.size1(64'd64),
.size2(64'd1088),
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
.size0(64'd576),
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
.size0(64'd2496),
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
.inject_r(1'b0),
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
.size0(64'd640),
.size1(64'd0),
.size2(64'd0),
.inject_r(1'b0),
.inject_b(1'b0),
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
.size0(64'd1280),
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
.size0(64'd64),
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
integer commits=0,offers=0,outputs=0,host_blocks=0,physical_expands=0,metadata_calls=0,visited_reads=0,drains=0;
reg[735:0]gold_packet;reg[159:0]gold_cost,gold_label;reg[31:0]word;integer logical_parent,logical_child;
reg[31:0]expected_parent[0:2],expected_node[0:2],expected_frame[0:2],expected_action[0:2],expected_ordinal[0:2];
reg[447:0]gold_config;reg[1855:0]held_output;
integer final_file,final_index;reg[31:0]final_node_id;reg[159:0]gold_final;
reg label_pending=0;reg[31:0]pending_label_node,pending_label_field;reg pending_label_write;
always @(posedge clk)begin
 cycles<=cycles+1;if(cycles>1000000)$fatal(1,"watchdog");
 if(!rst)begin
  if(fault)$fatal(1,"join fault controller=%0d expansion=%0d metadata=%0d access=%0d cf=%b pf=%b df=%b of=%b",dut.core.controller.state,dut.core.expansion.state,dut.core.metadata.state,dut.core.access.controller.state,dut.core.capture_fault,dut.core.p_fault,dut.core.d_fault,dut.core.o_fault);
  if(operation_pending)begin
   if(host_ctrl_ready||host_io_ready||host_design_req_ready||host_owner_req_ready||expand_ready)$fatal(1,"query lease gap");
   if(host_ctrl_valid&&host_io_valid&&host_design_req_valid&&host_owner_req_valid)host_blocks<=host_blocks+1;
  end
  if(dut.core.e_out_valid&&dut.core.e_out_ready)begin
   drains<=drains+1;$fdisplay(trace,"D %0d %0d %0d %0d %0d %0d %0d",cycles,dut.core.controller.frame_cookie,dut.core.controller.parent,dut.core.e_out_node,dut.core.e_out_sequence,dut.core.controller.early,dut.core.controller.state);
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
  if(dut.pl_valid&&dut.pl_ready)$fdisplay(trace,"P %0d %0d %0d %0d %08h",cycles,dut.pl_write,dut.pl_node,dut.pl_field,dut.pl_value);
  if(dut.pl_rsp_valid&&dut.pl_rsp_ready)$fdisplay(trace,"PR %0d %0d %0d %040h",cycles,dut.pl_status,dut.pl_present,dut.pl_payload);
  if(dut.cl_valid&&dut.cl_ready)$fdisplay(trace,"W %0d %0d %0d %08h",cycles,dut.cl_node,dut.cl_field,dut.cl_value);
  if(dut.cl_rsp_valid&&dut.cl_rsp_ready)$fdisplay(trace,"A %0d %0d %0d %040h",cycles,dut.cl_status,dut.cl_present,dut.cl_payload);
  if(dut.of_valid&&dut.of_ready)begin offers<=offers+1;$fdisplay(trace,"F %0d %0d %08h %0d",cycles,dut.of_id,dut.of_key,dut.frontier_size);end
  if(dut.frontier.fs_req_valid&&dut.frontier.fs_req_ready)$fdisplay(trace,"FQ %0d %0d %08h %0d %0d",cycles,dut.frontier.fs_req_op,dut.frontier.fs_req_key,dut.frontier.fs_req_id,dut.frontier.fs_req_cookie);
  if(dut.frontier.fs_rsp_valid&&dut.frontier.fs_rsp_ready)$fdisplay(trace,"FR %0d %0d %08h %0d %0d",cycles,dut.frontier.fs_rsp_status,dut.frontier.fs_rsp_key,dut.frontier.fs_rsp_id,dut.frontier.fs_rsp_size);
 end
end
task control(input integer op);begin
 @(negedge clk);host_ctrl_op=op;host_ctrl_query=1;host_ctrl_price=3;host_ctrl_version=3;host_ctrl_valid=1;
 do @(posedge clk);while(!host_ctrl_ready);@(negedge clk);host_ctrl_valid=0;
 wait(host_ctrl_rsp_valid);@(negedge clk);if(host_ctrl_status)$fatal(1,"control status op=%0d status=%0d",op,host_ctrl_status);
 host_ctrl_rsp_ready=1;@(negedge clk);host_ctrl_rsp_ready=0;
end endtask
task initialize_prev(input integer n);begin
 @(negedge clk);host_io_valid=1;host_io_node=n;host_io_field=2;host_io_write=1;host_io_value=32'hffffffff;
 do @(posedge clk);while(!host_io_ready);@(negedge clk);host_io_valid=0;
 wait(host_io_rsp_valid);@(negedge clk);if(host_io_status)$fatal(1,"initial label");host_io_rsp_ready=1;@(negedge clk);host_io_rsp_ready=0;
end endtask
task target_seed;begin
 @(negedge clk);host_io_valid=1;host_io_node=16;host_io_field=4;host_io_write=1;host_io_value=1;
 do @(posedge clk);while(!host_io_ready);@(negedge clk);host_io_valid=0;
 wait(host_io_rsp_valid);@(negedge clk);if(host_io_status||host_io_payload[159:128]!=1)$fatal(1,"set target");host_io_rsp_ready=1;@(negedge clk);host_io_rsp_ready=0;
 @(negedge clk);seed_valid=1;seed_op=1;seed_key=32'h3f800000;seed_id=24;seed_cookie=32'h10000000;seed_version=query_version;
 do @(posedge clk);while(!seed_ready);@(negedge clk);seed_valid=0;
 wait(seed_rsp_valid);@(negedge clk);if(seed_rsp_status||seed_rsp_size!=1)$fatal(1,"seed nonempty heap");seed_rsp_ready=1;@(negedge clk);seed_rsp_ready=0;
end endtask
task poll(input integer status,id,input[31:0]key);begin
 @(negedge clk);seed_valid=1;seed_op=2;seed_cookie=32'hc0000000+status;seed_version=query_version;
 do @(posedge clk);while(!seed_ready);@(negedge clk);seed_valid=0;
 wait(seed_rsp_valid);@(negedge clk);if(seed_rsp_status!=status||seed_rsp_size||(!status&&(seed_rsp_id!=id||seed_rsp_key!==key)))$fatal(1,"poll mismatch");
 seed_rsp_ready=1;@(negedge clk);seed_rsp_ready=0;
end endtask
initial begin
 trace=$fopen("joined_trace.txt","w");if(!trace)$fatal(1,"trace open");
 if(!$value$plusargs("costvectors=%s",path))$fatal(1,"gold cost");fd_gold=$fopen(path,"r");
 if(!$value$plusargs("finallabels=%s",path))$fatal(1,"final labels");final_file=$fopen(path,"r");if(!fd_gold||!final_file)$fatal(1,"oracle open");
 rst=1;design_id=64'h123456789abcdef0;
 g_cfg_offsets_base=64'h1fffff000;g_cfg_edges_base=64'h10fffff000;g_cfg_attrs_base=64'h20fffff000;g_cfg_nodes=33;g_cfg_edges=3;
 d_cfg_base=64'h31fffff000;d_cfg_nodes=33;t_cfg_rows_base=64'h41fffff000;t_cfg_columns_base=64'h51fffff000;t_cfg_rows=1;t_cfg_columns=0;
 owner_cfg_primary=64'h61fffff000;owner_cfg_nodes=33;owner_cfg_capacity=0;owner_cfg_pool=owner_cfg_primary+576;owner_cfg_allocator=owner_cfg_primary+576;
 cs_cfg_history=64'h71fffff000;cs_cfg_prices=cs_cfg_history+192;cs_cfg_nets=cs_cfg_history+1216;cs_cfg_nodes=33;cs_cfg_net_count=2;cs_cfg_version=3;cs_cfg_design_id=design_id;
 q_cfg_base=64'h81fffff000;q_cfg_design=design_id;q_cfg_connections=1;q_cfg_nodes=33;q_cfg_nets=2;q_cfg_revision=1;
 repeat(5)@(negedge clk);rst=0;
 @(negedge clk);q_cfg_valid=1;do @(posedge clk);while(!q_cfg_ready);@(negedge clk);q_cfg_valid=0;
 wait(q_cfg_rsp_valid);@(negedge clk);if(q_cfg_status)$fatal(1,"qconfig");q_cfg_rsp_ready=1;@(negedge clk);q_cfg_rsp_ready=0;
 @(negedge clk);g_cfg_valid=1;d_cfg_valid=1;t_cfg_valid=1;owner_cfg_valid=1;cs_cfg_valid=1;
 wait(g_cfg_ready&&d_cfg_ready&&t_cfg_ready&&owner_cfg_ready&&cs_cfg_ready);@(posedge clk);@(negedge clk);g_cfg_valid=0;d_cfg_valid=0;t_cfg_valid=0;owner_cfg_valid=0;cs_cfg_valid=0;
 wait(g_cfg_rsp_valid&&d_cfg_rsp_valid&&t_cfg_rsp_valid&&owner_cfg_rsp_valid&&cs_cfg_rsp_valid);@(negedge clk);
 if(g_cfg_status||d_cfg_status||t_cfg_status||owner_cfg_status||cs_cfg_status)$fatal(1,"config");g_cfg_rsp_ready=1;d_cfg_rsp_ready=1;t_cfg_rsp_ready=1;owner_cfg_rsp_ready=1;cs_cfg_rsp_ready=1;
 @(negedge clk);g_cfg_rsp_ready=0;d_cfg_rsp_ready=0;t_cfg_rsp_ready=0;owner_cfg_rsp_ready=0;cs_cfg_rsp_ready=0;
 control(0);for(i=0;i<5;i=i+1)initialize_prev(i*8);target_seed();
 expected_parent[0]=0;expected_parent[1]=8;expected_parent[2]=0;
 expected_node[0]=8;expected_node[1]=16;expected_node[2]=16;
 expected_frame[0]=100;expected_frame[1]=101;expected_frame[2]=100;
 expected_action[0]=2;expected_action[1]=1;expected_action[2]=0;
 expected_ordinal[0]=0;expected_ordinal[1]=0;expected_ordinal[2]=1;
 @(negedge clk);expand_cookie=100;expand_parent=0;expand_prune=0;expand_has_laguna=1;expand_sink=32;expand_net=0;expand_sequence=77;expand_flags=0;expand_connection=0;
 expand_xmin=-10;expand_xmax=10;expand_ymin=-10;expand_ymax=10;expand_version=3;expand_valid=1;
 do @(posedge clk);while(!expand_ready);@(negedge clk);expand_valid=0;
 // Queued external CLOSE must not prevent the required internal cost OFFER.
 host_ctrl_valid=1;host_ctrl_op=2;host_io_valid=1;host_design_req_valid=1;host_owner_req_valid=1;
 for(i=0;i<2;i=i+1)begin
  wait(out_valid);@(negedge clk);
  if(out_cookie!=expected_frame[i]||dut.held_parent!=expected_parent[i]||out_node!=expected_node[i]||out_action!=expected_action[i]||out_sequence!=expected_ordinal[i])$fatal(1,"candidate order i=%0d cookie=%0d parent=%0d child=%0d action=%0d",i,out_cookie,dut.held_parent,out_node,out_action);
  gold_config=0;gold_config[31:0]=77;gold_config[63:32]=expected_parent[i]==0?32:0;gold_config[95:64]=12;gold_config[127:96]=12;gold_config[159:128]=12;gold_config[191:160]=expected_node[i]/8;gold_config[223:192]=expected_node[i]/8;gold_config[255:224]=4;gold_config[287:256]=4;gold_config[319:288]=0;gold_config[351:320]=-10;gold_config[383:352]=10;gold_config[415:384]=-10;gold_config[447:416]=10;
  if(out_bits!==(i==0?32'd1:32'd6))$fatal(1,"target/EARLY bits");
  if(out_config!==gold_config||!out_params_valid||out_connection||out_params[127:96]!=32)$fatal(1,"config/State identity");
  if(i<2)begin
   if(out_prep_count!=(i==1?2:0)||out_prep_occupancy!=(i==1?1:0)||out_prep_price_index||out_prep_price_value!==32'h3f800000)$fatal(1,"same-net sharing source");
   $fdisplay(trace,"H %0d %0d %0d %0d %0d %08h",cycles,out_node,out_prep_count,out_prep_occupancy,out_prep_price_index,out_prep_price_value);
   rc=$fscanf(fd_gold,"%d %d",logical_parent,logical_child);if(rc!=2||logical_parent*8!=expected_parent[i]||logical_child*8!=expected_node[i])$fatal(1,"CPU oracle order");
   for(j=0;j<23;j=j+1)begin rc=$fscanf(fd_gold,"%h",word);if(rc!=1)$fatal(1,"packet word");gold_packet[j*32+:32]=word;end
   for(j=0;j<5;j=j+1)begin rc=$fscanf(fd_gold,"%h",word);if(rc!=1)$fatal(1,"cost word");gold_cost[j*32+:32]=word;end
   if(!out_cost_valid||out_cost_status||out_cost_packet!==gold_packet||out_cost_words!==gold_cost)$fatal(1,"CPU cost mismatch i=%0d packet=%h/%h cost=%h/%h",i,out_cost_packet,gold_packet,out_cost_words,gold_cost);
   gold_label={i==1?32'd1:32'd0,32'd77,expected_parent[i],gold_cost[95:64],gold_cost[159:128]};
   if(!out_commit_valid||out_commit_status||out_commit_acked!=7||out_commit_payload!==gold_label)$fatal(1,"actual label ACK payload");
   if(out_post_upstream!==gold_packet[8*32+:32])$fatal(1,"actual parent upstream");
   if(i==1&&(!out_offer_valid||out_offer_status||out_offer_node!=16||out_offer_key!==gold_cost[159:128]||out_offer_before||out_offer_size!=1))$fatal(1,"actual cost OFFER");
   if(i==0&&out_offer_valid)$fatal(1,"lookahead enqueued");
   commits=commits+1;
  end
  $fdisplay(trace,"O %0d %0d %0d %0d %0d %0d",cycles,out_cookie,dut.held_parent,out_node,out_action,out_sequence);
  if(i<2)$fdisplay(trace,"C %0d %0d %0184h %040h",cycles,out_node,out_cost_packet,out_cost_words);
  held_output={out_config,out_attrs,out_cost_packet,out_cost_words,out_commit_payload,out_cookie,out_node,dut.held_parent};
  repeat(4)begin @(negedge clk);if(!out_valid||{out_config,out_attrs,out_cost_packet,out_cost_words,out_commit_payload,out_cookie,out_node,dut.held_parent}!==held_output)$fatal(1,"joined reply hold");end
  out_ready=1;@(negedge clk);out_ready=0;outputs=outputs+1;
 end
 wait(result_valid);@(negedge clk);if(result_status||result_cookie!=100||result_count!=2||result_expanded_count!=3||result_raw_count!=3||result_mask!=3||!result_early||physical_expands!=2||metadata_calls!=2||drains!=3||commits!=2||offers!=1||!host_blocks)$fatal(1,"root summary status=%0d count=%0d raw=%0d physical=%0d metadata=%0d",result_status,result_count,result_raw_count,physical_expands,metadata_calls);
 result_ready=1;@(negedge clk);result_ready=0;host_ctrl_valid=0;host_io_valid=0;host_design_req_valid=0;host_owner_req_valid=0;
 control(1);
 for(final_index=0;final_index<5;final_index=final_index+1)begin
  rc=$fscanf(final_file,"%d",final_node_id);if(rc!=1)$fatal(1,"final node");
  for(j=0;j<5;j=j+1)begin rc=$fscanf(final_file,"%h",word);if(rc!=1)$fatal(1,"final word");gold_final[j*32+:32]=word;end
  @(negedge clk);host_io_valid=1;host_io_write=0;host_io_node=final_node_id;host_io_field=0;
  do @(posedge clk);while(!host_io_ready);@(negedge clk);host_io_valid=0;
  wait(host_io_rsp_valid);@(negedge clk);if(host_io_status||!host_io_present||host_io_payload!==gold_final)$fatal(1,"final native label n=%0d actual=%h expected=%h",final_node_id,host_io_payload,gold_final);
  $fdisplay(trace,"R %0d %0d %040h",cycles,final_node_id,host_io_payload);host_io_rsp_ready=1;@(negedge clk);host_io_rsp_ready=0;
 end
 poll(0,16,gold_cost[159:128]);poll(1,0,0);control(2);
 if(fault||visited_reads!=2||outputs!=2||g_reads!=g_rbeats||d_reads!=d_rbeats||d_writes!=d_bs||p_writes!=p_bs)$fatal(1,"final outstanding/visited");
 $fflush(trace);$fclose(trace);
 $display("RECURSIVE_SHARED_TARGET_PASS outputs=%0d commits=%0d offers=%0d expands=%0d visited_reads=%0d host_blocks=%0d label_reads=%0d label_writes=%0d cycles=%0d",outputs,commits,offers,physical_expands,visited_reads,host_blocks,p_reads,p_writes,cycles);$finish;
end
endmodule
