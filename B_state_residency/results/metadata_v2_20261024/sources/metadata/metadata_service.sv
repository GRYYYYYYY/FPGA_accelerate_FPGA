`timescale 1ns/1ps
module metadata_service #(parameter integer TOKEN_BITS=32,MAX_CYCLES=262144)(
 input wire  clk,
 input wire  rst,
 input wire  abort,
 input wire  owner_configured,
 input wire [31:0] owner_nodes,
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
 input wire  active,
 input wire [1:0] active_query,
 input wire [3:0] active_price,
 input wire  req_valid,
 output wire  req_ready,
 input wire [31:0] req_cookie,
 input wire [31:0] req_parent,
 input wire [31:0] req_child,
 input wire [31:0] req_sink,
 input wire [31:0] req_net,
 input wire [31:0] req_sequence,
 input wire [31:0] req_flags,
 input wire [31:0] req_xmin,
 input wire [31:0] req_xmax,
 input wire [31:0] req_ymin,
 input wire [31:0] req_ymax,
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
 output wire [1:0] rsp_query,
 output wire [3:0] rsp_price,
 output wire [447:0] rsp_config,
 output wire  rsp_created,
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
 output wire  busy,
 output wire  fault,
 output wire  design_claim_active
);
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
 wire  c_enable;
 wire  c_busy;
 wire  c_fault;
 wire  c_d_req_valid;
 wire  c_d_req_ready;
 wire [2:0] c_d_req_op;
 wire [31:0] c_d_req_cookie;
 wire [31:0] c_d_req_owner;
 wire [31:0] c_d_req_node;
 wire [31:0] c_d_req_arg;
 wire  c_d_rsp_valid;
 wire  c_d_rsp_ready;
 wire [3:0] c_d_rsp_status;
 wire [31:0] c_d_rsp_cookie;
 wire [31:0] c_d_rsp_flags;
 wire [31:0] c_d_rsp_count;
 wire [31:0] c_d_rsp_mask;
 reg[31:0]held_g_nodes,held_d_nodes;reg meta_pending,host_pending;
 wire config_fault=g_configured&&d_configured&&owner_configured&&(held_g_nodes!=held_d_nodes||held_g_nodes!=owner_nodes);
 wire owner_lost=meta_pending&&!owner_configured;
 wire permit_host=!rst&&!fault&&!meta_pending&&!host_pending;
 assign fault=c_fault||g_fault||d_fault||config_fault||owner_lost;
 assign busy=meta_pending||host_pending;
 assign design_claim_active=d_claim_active;
 assign c_enable=g_configured&&d_configured&&owner_configured&&!g_cfg_rsp_valid&&!d_cfg_rsp_valid&&!host_pending&&!host_design_req_valid;
 always @(posedge clk)begin
  if(rst)begin held_g_nodes<=0;held_d_nodes<=0;meta_pending<=0;host_pending<=0;end
  else begin
   if(g_cfg_valid&&g_cfg_ready)held_g_nodes<=g_cfg_nodes;
   if(d_cfg_valid&&d_cfg_ready)held_d_nodes<=d_cfg_nodes;
   if(req_valid&&req_ready)meta_pending<=1;
   if(rsp_valid&&rsp_ready)meta_pending<=0;
   if(host_design_req_valid&&host_design_req_ready)host_pending<=1;
   if(host_design_rsp_valid&&host_design_rsp_ready)host_pending<=0;
  end
 end
 assign d_req_valid=meta_pending?c_d_req_valid:(host_design_req_valid&&permit_host);
 assign c_d_req_ready=d_req_ready&&meta_pending;
 assign host_design_req_ready=d_req_ready&&permit_host;
 assign d_req_op=meta_pending?c_d_req_op:host_design_req_op;
 assign d_req_cookie=meta_pending?c_d_req_cookie:host_design_req_cookie;
 assign d_req_owner=meta_pending?c_d_req_owner:host_design_req_owner;
 assign d_req_node=meta_pending?c_d_req_node:host_design_req_node;
 assign d_req_arg=meta_pending?c_d_req_arg:host_design_req_arg;
 assign c_d_rsp_valid=d_rsp_valid&&!host_pending;
 assign host_design_rsp_valid=d_rsp_valid&&host_pending;
 assign d_rsp_ready=host_pending?host_design_rsp_ready:c_d_rsp_ready;
 assign c_d_rsp_status=d_rsp_status;
 assign host_design_rsp_status=d_rsp_status;
 assign c_d_rsp_cookie=d_rsp_cookie;
 assign host_design_rsp_cookie=d_rsp_cookie;
 assign c_d_rsp_flags=d_rsp_flags;
 assign host_design_rsp_flags=d_rsp_flags;
 assign c_d_rsp_count=d_rsp_count;
 assign host_design_rsp_count=d_rsp_count;
 assign c_d_rsp_mask=d_rsp_mask;
 assign host_design_rsp_mask=d_rsp_mask;
 graph_static_reader graph(
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
 design_state_store design_store(
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
 metadata_controller #(.TOKEN_BITS(TOKEN_BITS),.MAX_CYCLES(MAX_CYCLES)) controller(
.clk(clk),
.rst(rst),
.enable(c_enable),
.abort(abort||config_fault||owner_lost),
.active(active),
.active_query(active_query),
.active_price(active_price),
.nodes(held_g_nodes),
.claim_active(d_claim_active),
.req_valid(req_valid),
.req_ready(req_ready),
.req_cookie(req_cookie),
.req_parent(req_parent),
.req_child(req_child),
.req_sink(req_sink),
.req_net(req_net),
.req_sequence(req_sequence),
.req_flags(req_flags),
.req_xmin(req_xmin),
.req_xmax(req_xmax),
.req_ymin(req_ymin),
.req_ymax(req_ymax),
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
.rsp_query(rsp_query),
.rsp_price(rsp_price),
.rsp_config(rsp_config),
.rsp_created(rsp_created),
.busy(c_busy),
.fault(c_fault),
.g_req_valid(g_req_valid),
.g_req_ready(g_req_ready),
.g_req_op(g_req_op),
.g_req_cookie(g_req_cookie),
.g_req_node(g_req_node),
.g_req_index(g_req_index),
.g_rsp_valid(g_rsp_valid),
.g_rsp_ready(g_rsp_ready),
.g_rsp_status(g_rsp_status),
.g_rsp_cookie(g_rsp_cookie),
.g_rsp_parent(g_rsp_parent),
.g_rsp_index(g_rsp_index),
.g_rsp_node(g_rsp_node),
.g_rsp_start(g_rsp_start),
.g_rsp_count(g_rsp_count),
.g_rsp_attrs(g_rsp_attrs),
.g_fault(g_fault),
.d_req_valid(c_d_req_valid),
.d_req_ready(c_d_req_ready),
.d_req_op(c_d_req_op),
.d_req_cookie(c_d_req_cookie),
.d_req_owner(c_d_req_owner),
.d_req_node(c_d_req_node),
.d_req_arg(c_d_req_arg),
.d_rsp_valid(c_d_rsp_valid),
.d_rsp_ready(c_d_rsp_ready),
.d_rsp_status(c_d_rsp_status),
.d_rsp_cookie(c_d_rsp_cookie),
.d_rsp_flags(c_d_rsp_flags),
.d_rsp_count(c_d_rsp_count),
.d_rsp_mask(c_d_rsp_mask),
.d_fault(d_fault)
);
endmodule
