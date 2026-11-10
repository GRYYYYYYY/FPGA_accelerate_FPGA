`timescale 1ns/1ps
module node_expansion_engine #(parameter integer SLOTS=32,TX_BITS=16,GEN_BITS=16,FRAMES=163840,INDEX_BITS=18,HASH_BITS=18,PROBE_LIMIT=64,EPOCH_BITS=16,TOKEN_BITS=32,OWNER_BITS=32)(
 input wire  clk,
 input wire  rst,
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
 input wire  expand_valid,
 output wire  expand_ready,
 input wire [31:0] expand_cookie,
 input wire [31:0] expand_parent,
 input wire [31:0] expand_prune,
 input wire [31:0] expand_has_laguna,
 output wire  out_valid,
 input wire  out_ready,
 output wire [31:0] out_node,
 output wire [31:0] out_position,
 output wire [31:0] out_sequence,
 output wire [255:0] out_attrs,
 output wire  result_valid,
 input wire  result_ready,
 output wire [3:0] result_status,
 output wire [31:0] result_detail,
 output wire [31:0] result_cookie,
 output wire [31:0] result_count,
 output wire [31:0] result_raw_count,
 output wire [31:0] result_mask,
 output wire  result_hit,
 output wire  busy,
 output wire  fault,
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
 output wire  p_active,
 output wire [1:0] p_active_query,
 output wire [3:0] p_active_price
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
 wire  enable;
 wire  configuration_fault;
 reg host_pending;reg[31:0] graph_nodes,design_nodes;
 wire permit_host=!rst&&!busy&&!fault&&!host_pending;
 assign enable=!host_pending&&!host_ctrl_valid&&!host_io_valid&&p_active&&g_configured&&d_configured;
 assign configuration_fault=g_configured&&d_configured&&graph_nodes!=design_nodes;
 always @(posedge clk)begin
  if(rst)begin host_pending<=0;graph_nodes<=0;design_nodes<=0;end
  else begin
   if(g_cfg_valid&&g_cfg_ready)graph_nodes<=g_cfg_nodes;
   if(d_cfg_valid&&d_cfg_ready)design_nodes<=d_cfg_nodes;
   if((host_ctrl_valid&&host_ctrl_ready)||(host_io_valid&&host_io_ready))host_pending<=1;
   if((host_ctrl_rsp_valid&&host_ctrl_rsp_ready)||(host_io_rsp_valid&&host_io_rsp_ready))host_pending<=0;
  end
 end
 assign p_ctrl_valid=host_ctrl_valid&&permit_host;
 assign host_ctrl_ready=p_ctrl_ready&&permit_host;
 assign p_ctrl_op=host_ctrl_op;
 assign p_ctrl_query=host_ctrl_query;
 assign p_ctrl_price=host_ctrl_price;
 assign host_ctrl_rsp_valid=p_ctrl_rsp_valid;
 assign p_ctrl_rsp_ready=host_ctrl_rsp_ready;
 assign host_ctrl_status=p_ctrl_status;
 assign p_io_valid=host_io_valid&&permit_host&&!host_ctrl_valid;
 assign host_io_ready=p_io_ready&&permit_host&&!host_ctrl_valid;
 assign p_io_write=host_io_write;
 assign p_io_node=host_io_node;
 assign p_io_value=host_io_value;
 assign p_io_field=host_io_field;
 assign host_io_rsp_valid=p_io_rsp_valid;
 assign p_io_rsp_ready=host_io_rsp_ready;
 assign host_io_status=p_io_status;
 assign host_io_payload=p_io_payload;
 assign host_io_present=p_io_present;
 assign p_dispatch_enable=1;
 assign p_execute_enable=1;
 assign p_fence_service_enable=1;
 assign p_ack_receive_enable=1;
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
 children_build_engine builder(
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
 paged_exclusion_engine #(.SLOTS(SLOTS),.TX_BITS(TX_BITS),.GEN_BITS(GEN_BITS),.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS),.PROBE_LIMIT(PROBE_LIMIT),.EPOCH_BITS(EPOCH_BITS)) pager(
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
 expansion_controller #(.TOKEN_BITS(TOKEN_BITS),.OWNER_BITS(OWNER_BITS)) controller(
  .clk(clk),
  .rst(rst),
  .enable(enable),
  .configuration_fault(configuration_fault),
  .expand_valid(expand_valid),
  .expand_ready(expand_ready),
  .expand_cookie(expand_cookie),
  .expand_parent(expand_parent),
  .expand_prune(expand_prune),
  .expand_has_laguna(expand_has_laguna),
  .out_valid(out_valid),
  .out_ready(out_ready),
  .out_node(out_node),
  .out_position(out_position),
  .out_sequence(out_sequence),
  .out_attrs(out_attrs),
  .result_valid(result_valid),
  .result_ready(result_ready),
  .result_status(result_status),
  .result_detail(result_detail),
  .result_cookie(result_cookie),
  .result_count(result_count),
  .result_raw_count(result_raw_count),
  .result_mask(result_mask),
  .result_hit(result_hit),
  .busy(busy),
  .fault(fault),
  .g_fault(g_fault),
  .d_fault(d_fault),
  .p_fault(p_fault),
  .b_fault(b_fault),
  .p_active(p_active),
  .p_active_query(p_active_query),
  .p_active_price(p_active_price),
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
  .d_req_valid(d_req_valid),
  .d_req_ready(d_req_ready),
  .d_req_op(d_req_op),
  .d_req_cookie(d_req_cookie),
  .d_req_owner(d_req_owner),
  .d_req_node(d_req_node),
  .d_req_arg(d_req_arg),
  .d_rsp_valid(d_rsp_valid),
  .d_rsp_ready(d_rsp_ready),
  .d_rsp_status(d_rsp_status),
  .d_rsp_cookie(d_rsp_cookie),
  .d_rsp_flags(d_rsp_flags),
  .d_rsp_count(d_rsp_count),
  .d_rsp_mask(d_rsp_mask),
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
endmodule
