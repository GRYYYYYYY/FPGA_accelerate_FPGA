`timescale 1ns/1ps
module access_fabric #(parameter integer SLOTS=32,TX_BITS=16,GEN_BITS=16,FRAMES=163840,INDEX_BITS=18,HASH_BITS=18,PROBE_LIMIT=64,EPOCH_BITS=16,TOKEN_BITS=32,ACCESS_MAX_CYCLES=8388608,SERVICE_MAX_CYCLES=(1<<HASH_BITS)+262144)(
 input wire  clk,
 input wire  rst,
 input wire  abort,
 input wire  req_valid,
 output wire  req_ready,
 input wire [447:0] req_config,
 input wire [31:0] req_cookie,
 input wire [31:0] req_parent,
 input wire [31:0] req_child,
 input wire [31:0] req_sink,
 input wire [31:0] req_net,
 input wire [1:0] req_query,
 input wire [3:0] req_price,
 output wire  rsp_valid,
 input wire  rsp_ready,
 output wire [3:0] rsp_status,
 output wire [31:0] rsp_cookie,
 output wire [31:0] rsp_parent,
 output wire [31:0] rsp_child,
 output wire [31:0] rsp_sink,
 output wire [31:0] rsp_net,
 output wire [31:0] rsp_bits,
 output wire [31:0] rsp_action,
 output wire [31:0] rsp_steps,
 output wire [31:0] rsp_services,
 output wire [1:0] rsp_query,
 output wire [3:0] rsp_price,
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
 output wire  p_active,
 output wire [1:0] p_active_query,
 output wire [3:0] p_active_price,
 input wire  host_ctrl_valid,
 output wire  host_ctrl_ready,
 input wire [1:0] host_ctrl_op,
 input wire [1:0] host_ctrl_query,
 input wire [3:0] host_ctrl_price,
 output wire  host_ctrl_rsp_valid,
 input wire  host_ctrl_rsp_ready,
 output wire [3:0] host_ctrl_status,
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
 output wire  busy,
 output wire  fault,
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
 output wire  host_owner_rsp_will_overuse
);
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
 wire  bridge_h_ready;
 wire  bridge_b_req_valid;
 wire  bridge_b_req_ready;
 wire [2:0] bridge_b_req_op;
 wire [31:0] bridge_b_req_cookie;
 wire [31:0] bridge_b_req_node;
 wire [31:0] bridge_b_req_net;
 wire  bridge_b_rsp_valid;
 wire  bridge_b_rsp_ready;
 wire [3:0] bridge_b_rsp_status;
 wire [31:0] bridge_b_rsp_cookie;
 wire [31:0] bridge_b_rsp_count;
 wire [31:0] bridge_b_rsp_occupancy;
 wire  bridge_b_rsp_will_overuse;
 wire  bridge_b_fault;
 wire  bridge_host_pending;
 wire  bridge_busy;
 wire  raw_cfg_ready;
 wire  raw_busy;
 assign owner_cfg_ready=raw_cfg_ready&&!access_pending&&!bridge_busy&&!host_owner_req_valid;
 assign host_owner_req_ready=bridge_h_ready&&!owner_cfg_valid&&!owner_cfg_rsp_valid;

 wire  a_enable;
 wire  a_busy;
 wire  a_fault;
 wire  a_svc_valid;
 wire  a_svc_ready;
 wire [3:0] a_svc_kind;
 wire [4:0] a_svc_phase;
 wire [31:0] a_svc_node;
 wire [31:0] a_svc_net;
 wire [31:0] a_svc_cookie;
 wire [1:0] a_svc_query;
 wire [3:0] a_svc_price;
 wire  a_svc_rsp_valid;
 wire  a_svc_rsp_ready;
 wire [3:0] a_svc_rsp_status;
 wire [3:0] a_svc_rsp_kind;
 wire [4:0] a_svc_rsp_phase;
 wire [31:0] a_svc_rsp_node;
 wire [31:0] a_svc_rsp_net;
 wire [31:0] a_svc_rsp_cookie;
 wire [31:0] a_svc_rsp_value;
 wire [1:0] a_svc_rsp_query;
 wire [3:0] a_svc_rsp_price;
 wire  a_svc_fault;
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
 wire [31:0] c_rsp_next;
 wire [31:0] c_rsp_prev_column;
 wire [31:0] c_rsp_label_prev;
 wire  c_rsp_north;
 wire  c_rsp_prev_read;
 wire  c_rsp_prev_present;
 wire [255:0] c_rsp_attrs;
 wire  c_busy;
 wire  c_fault;
 wire  c_host_ctrl_valid;
 wire  c_host_ctrl_ready;
 wire [1:0] c_host_ctrl_op;
 wire [1:0] c_host_ctrl_query;
 wire [3:0] c_host_ctrl_price;
 wire  c_host_ctrl_rsp_valid;
 wire  c_host_ctrl_rsp_ready;
 wire [3:0] c_host_ctrl_status;
 wire  c_host_io_valid;
 wire  c_host_io_ready;
 wire  c_host_io_write;
 wire [31:0] c_host_io_node;
 wire [31:0] c_host_io_value;
 wire [2:0] c_host_io_field;
 wire  c_host_io_rsp_valid;
 wire  c_host_io_rsp_ready;
 wire [3:0] c_host_io_status;
 wire [159:0] c_host_io_payload;
 wire  c_host_io_present;
 wire  d_fault;
 wire  d_l_valid;
 wire  d_l_ready;
 wire  d_l_write;
 wire [31:0] d_l_node;
 wire [31:0] d_l_value;
 wire [2:0] d_l_field;
 wire  d_l_rsp_valid;
 wire  d_l_rsp_ready;
 wire [3:0] d_l_status;
 wire [159:0] d_l_payload;
 wire  d_l_present;
 reg host_pending,access_pending;
 wire permit_host=!rst&&!access_pending&&!fault&&!host_pending;
 assign busy=access_pending||host_pending||fault;
 assign fault=a_fault||d_fault||c_fault||o_fault;
 assign a_svc_fault=d_fault||c_fault;
 assign a_enable=g_configured&&t_configured&&owner_configured&&!host_pending&&!host_ctrl_valid&&!host_io_valid&&!bridge_host_pending&&!host_owner_req_valid&&!owner_cfg_valid&&!owner_cfg_rsp_valid;
 always @(posedge clk)begin
  if(rst)begin host_pending<=0;access_pending<=0;end
  else begin
   if(req_valid&&req_ready)access_pending<=1;
   if(rsp_valid&&rsp_ready)access_pending<=0;
   if((host_ctrl_valid&&host_ctrl_ready)||(host_io_valid&&host_io_ready))host_pending<=1;
   if((host_ctrl_rsp_valid&&host_ctrl_rsp_ready)||(host_io_rsp_valid&&host_io_rsp_ready))host_pending<=0;
  end
 end
 assign c_host_ctrl_valid=host_ctrl_valid&&permit_host;
 assign host_ctrl_ready=c_host_ctrl_ready&&permit_host;
 assign c_host_ctrl_op=host_ctrl_op;
 assign c_host_ctrl_query=host_ctrl_query;
 assign c_host_ctrl_price=host_ctrl_price;
 assign host_ctrl_rsp_valid=c_host_ctrl_rsp_valid&&host_pending;
 assign c_host_ctrl_rsp_ready=host_ctrl_rsp_ready;
 assign host_ctrl_status=c_host_ctrl_status;
 assign c_host_io_valid=access_pending?d_l_valid:(host_io_valid&&permit_host&&!host_ctrl_valid);
 assign d_l_ready=c_host_io_ready&&access_pending;
 assign host_io_ready=c_host_io_ready&&permit_host&&!host_ctrl_valid;
 assign c_host_io_write=access_pending?d_l_write:host_io_write;
 assign c_host_io_node=access_pending?d_l_node:host_io_node;
 assign c_host_io_value=access_pending?d_l_value:host_io_value;
 assign c_host_io_field=access_pending?d_l_field:host_io_field;
 assign d_l_rsp_valid=c_host_io_rsp_valid&&access_pending&&!host_pending;
 assign host_io_rsp_valid=c_host_io_rsp_valid&&host_pending;
 assign c_host_io_rsp_ready=host_pending?host_io_rsp_ready:d_l_rsp_ready;
 assign d_l_status=c_host_io_status;
 assign host_io_status=c_host_io_status;
 assign d_l_payload=c_host_io_payload;
 assign host_io_payload=c_host_io_payload;
 assign d_l_present=c_host_io_present;
 assign host_io_present=c_host_io_present;
 access_service #(.TOKEN_BITS(TOKEN_BITS),.MAX_CYCLES(ACCESS_MAX_CYCLES)) access(
.clk(clk),
.rst(rst),
.abort(abort),
.enable(a_enable),
.active(p_active),
.active_query(p_active_query),
.active_price(p_active_price),
.req_valid(req_valid),
.req_ready(req_ready),
.req_config(req_config),
.req_cookie(req_cookie),
.req_parent(req_parent),
.req_child(req_child),
.req_sink(req_sink),
.req_net(req_net),
.req_query(req_query),
.req_price(req_price),
.rsp_valid(rsp_valid),
.rsp_ready(rsp_ready),
.rsp_status(rsp_status),
.rsp_cookie(rsp_cookie),
.rsp_parent(rsp_parent),
.rsp_child(rsp_child),
.rsp_sink(rsp_sink),
.rsp_net(rsp_net),
.rsp_bits(rsp_bits),
.rsp_action(rsp_action),
.rsp_steps(rsp_steps),
.rsp_services(rsp_services),
.rsp_query(rsp_query),
.rsp_price(rsp_price),
.busy(a_busy),
.fault(a_fault),
.svc_valid(a_svc_valid),
.svc_ready(a_svc_ready),
.svc_kind(a_svc_kind),
.svc_phase(a_svc_phase),
.svc_node(a_svc_node),
.svc_net(a_svc_net),
.svc_cookie(a_svc_cookie),
.svc_query(a_svc_query),
.svc_price(a_svc_price),
.svc_rsp_valid(a_svc_rsp_valid),
.svc_rsp_ready(a_svc_rsp_ready),
.svc_rsp_status(a_svc_rsp_status),
.svc_rsp_kind(a_svc_rsp_kind),
.svc_rsp_phase(a_svc_rsp_phase),
.svc_rsp_node(a_svc_rsp_node),
.svc_rsp_net(a_svc_rsp_net),
.svc_rsp_cookie(a_svc_rsp_cookie),
.svc_rsp_value(a_svc_rsp_value),
.svc_rsp_query(a_svc_rsp_query),
.svc_rsp_price(a_svc_rsp_price),
.svc_fault(a_svc_fault)
);
 coordinate_service #(.SLOTS(SLOTS),.TX_BITS(TX_BITS),.GEN_BITS(GEN_BITS),.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS),.PROBE_LIMIT(PROBE_LIMIT),.EPOCH_BITS(EPOCH_BITS),.MAX_CYCLES(SERVICE_MAX_CYCLES)) coordinates(
.clk(clk),
.rst(rst),
.g_cfg_valid(g_cfg_valid),
.g_cfg_ready(g_cfg_ready),
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
.t_cfg_valid(t_cfg_valid),
.t_cfg_ready(t_cfg_ready),
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
.abort(abort),
.req_valid(c_req_valid),
.req_ready(c_req_ready),
.req_op(c_req_op),
.req_query(c_req_query),
.req_price(c_req_price),
.req_cookie(c_req_cookie),
.req_node(c_req_node),
.rsp_valid(c_rsp_valid),
.rsp_ready(c_rsp_ready),
.rsp_status(c_rsp_status),
.rsp_op(c_rsp_op),
.rsp_query(c_rsp_query),
.rsp_price(c_rsp_price),
.rsp_cookie(c_rsp_cookie),
.rsp_node(c_rsp_node),
.rsp_y(c_rsp_y),
.rsp_slr(c_rsp_slr),
.rsp_next(c_rsp_next),
.rsp_prev_column(c_rsp_prev_column),
.rsp_label_prev(c_rsp_label_prev),
.rsp_north(c_rsp_north),
.rsp_prev_read(c_rsp_prev_read),
.rsp_prev_present(c_rsp_prev_present),
.rsp_attrs(c_rsp_attrs),
.busy(c_busy),
.fault(c_fault),
.host_ctrl_valid(c_host_ctrl_valid),
.host_ctrl_ready(c_host_ctrl_ready),
.host_ctrl_op(c_host_ctrl_op),
.host_ctrl_query(c_host_ctrl_query),
.host_ctrl_price(c_host_ctrl_price),
.host_ctrl_rsp_valid(c_host_ctrl_rsp_valid),
.host_ctrl_rsp_ready(c_host_ctrl_rsp_ready),
.host_ctrl_status(c_host_ctrl_status),
.host_io_valid(c_host_io_valid),
.host_io_ready(c_host_io_ready),
.host_io_write(c_host_io_write),
.host_io_node(c_host_io_node),
.host_io_value(c_host_io_value),
.host_io_field(c_host_io_field),
.host_io_rsp_valid(c_host_io_rsp_valid),
.host_io_rsp_ready(c_host_io_rsp_ready),
.host_io_status(c_host_io_status),
.host_io_payload(c_host_io_payload),
.host_io_present(c_host_io_present),
.p_active(p_active),
.p_active_query(p_active_query),
.p_active_price(p_active_price)
);
 access_dispatch #(.MAX_CYCLES(SERVICE_MAX_CYCLES)) dispatch(
.clk(clk),
.rst(rst),
.abort(abort),
.active(p_active),
.active_query(p_active_query),
.active_price(p_active_price),
.req_valid(a_svc_valid),
.req_ready(a_svc_ready),
.req_kind(a_svc_kind),
.req_phase(a_svc_phase),
.req_node(a_svc_node),
.req_net(a_svc_net),
.req_cookie(a_svc_cookie),
.req_query(a_svc_query),
.req_price(a_svc_price),
.rsp_valid(a_svc_rsp_valid),
.rsp_ready(a_svc_rsp_ready),
.rsp_status(a_svc_rsp_status),
.rsp_kind(a_svc_rsp_kind),
.rsp_phase(a_svc_rsp_phase),
.rsp_node(a_svc_rsp_node),
.rsp_net(a_svc_rsp_net),
.rsp_cookie(a_svc_rsp_cookie),
.rsp_value(a_svc_rsp_value),
.rsp_query(a_svc_rsp_query),
.rsp_price(a_svc_rsp_price),
.fault(d_fault),
.l_valid(d_l_valid),
.l_ready(d_l_ready),
.l_write(d_l_write),
.l_node(d_l_node),
.l_value(d_l_value),
.l_field(d_l_field),
.l_rsp_valid(d_l_rsp_valid),
.l_rsp_ready(d_l_rsp_ready),
.l_status(d_l_status),
.l_payload(d_l_payload),
.l_present(d_l_present),
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

 owner_bridge owners(
.clk(clk),
.rst(rst),
.abort(abort),
.decision_lock(access_pending),
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
.h_req_valid(host_owner_req_valid&&!owner_cfg_valid&&!owner_cfg_rsp_valid),
.h_req_ready(bridge_h_ready),
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
.b_req_valid(bridge_b_req_valid),
.b_req_ready(bridge_b_req_ready),
.b_req_op(bridge_b_req_op),
.b_req_cookie(bridge_b_req_cookie),
.b_req_node(bridge_b_req_node),
.b_req_net(bridge_b_req_net),
.b_rsp_valid(bridge_b_rsp_valid),
.b_rsp_ready(bridge_b_rsp_ready),
.b_rsp_status(bridge_b_rsp_status),
.b_rsp_cookie(bridge_b_rsp_cookie),
.b_rsp_count(bridge_b_rsp_count),
.b_rsp_occupancy(bridge_b_rsp_occupancy),
.b_rsp_will_overuse(bridge_b_rsp_will_overuse),
.b_fault(bridge_b_fault),
.host_pending(bridge_host_pending),
.busy(bridge_busy),
.fault(o_fault)
);
 owner_state_store owner_store(
.clk(clk),
.rst(rst),
.abort(abort),
.cfg_valid(owner_cfg_valid&&!access_pending&&!bridge_busy&&!host_owner_req_valid),
.cfg_ready(raw_cfg_ready),
.cfg_primary(owner_cfg_primary),
.cfg_pool(owner_cfg_pool),
.cfg_allocator(owner_cfg_allocator),
.cfg_nodes(owner_cfg_nodes),
.cfg_capacity(owner_cfg_capacity),
.cfg_rsp_valid(owner_cfg_rsp_valid),
.cfg_rsp_ready(owner_cfg_rsp_ready),
.cfg_status(owner_cfg_status),
.configured(owner_configured),
.req_valid(bridge_b_req_valid),
.req_ready(bridge_b_req_ready),
.req_op(bridge_b_req_op),
.req_cookie(bridge_b_req_cookie),
.req_node(bridge_b_req_node),
.req_net(bridge_b_req_net),
.rsp_valid(bridge_b_rsp_valid),
.rsp_ready(bridge_b_rsp_ready),
.rsp_status(bridge_b_rsp_status),
.rsp_cookie(bridge_b_rsp_cookie),
.rsp_count(bridge_b_rsp_count),
.rsp_occupancy(bridge_b_rsp_occupancy),
.rsp_will_overuse(bridge_b_rsp_will_overuse),
.fault(bridge_b_fault),
.busy(raw_busy),
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
endmodule
