`timescale 1ns/1ps
module coordinate_service #(parameter integer SLOTS=32,TX_BITS=16,GEN_BITS=16,FRAMES=163840,INDEX_BITS=18,HASH_BITS=18,PROBE_LIMIT=64,EPOCH_BITS=16,TOKEN_BITS=32,MAX_CYCLES=262144)(
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
 input wire  abort,
 input wire  req_valid,
 output wire  req_ready,
 input wire [1:0] req_op,
 input wire [1:0] req_query,
 input wire [3:0] req_price,
 input wire [31:0] req_cookie,
 input wire [31:0] req_node,
 output wire  rsp_valid,
 input wire  rsp_ready,
 output wire [3:0] rsp_status,
 output wire [1:0] rsp_op,
 output wire [1:0] rsp_query,
 output wire [3:0] rsp_price,
 output wire [31:0] rsp_cookie,
 output wire [31:0] rsp_node,
 output wire [31:0] rsp_y,
 output wire [31:0] rsp_slr,
 output wire [31:0] rsp_next,
 output wire [31:0] rsp_prev_column,
 output wire [31:0] rsp_label_prev,
 output wire  rsp_north,
 output wire  rsp_prev_read,
 output wire  rsp_prev_present,
 output wire [255:0] rsp_attrs,
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
 wire  t_req_valid;
 wire  t_req_ready;
 wire  t_req_op;
 wire [31:0] t_req_index;
 wire [31:0] t_req_cookie;
 wire  t_rsp_valid;
 wire  t_rsp_ready;
 wire [3:0] t_rsp_status;
 wire  t_rsp_op;
 wire [31:0] t_rsp_index;
 wire [31:0] t_rsp_cookie;
 wire [31:0] t_rsp_a;
 wire [31:0] t_rsp_b;
 wire  t_fault;
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
 wire [31:0] nodes;
 wire [31:0] table_rows;
 wire [31:0] table_columns;
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
 reg host_pending;reg [31:0]held_nodes,held_rows,held_columns;
 wire permit_host=!rst&&!busy&&!fault&&!host_pending;
 assign enable=!host_pending&&!host_ctrl_valid&&!host_io_valid&&g_configured&&t_configured;
 assign nodes=held_nodes;assign table_rows=held_rows;assign table_columns=held_columns;
 always @(posedge clk)begin
  if(rst)begin host_pending<=0;held_nodes<=0;held_rows<=0;held_columns<=0;end
  else begin
   if(g_cfg_valid&&g_cfg_ready)held_nodes<=g_cfg_nodes;
   if(t_cfg_valid&&t_cfg_ready)begin held_rows<=t_cfg_rows;held_columns<=t_cfg_columns;end
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
 assign p_io_valid=busy?c_p_io_valid:(host_io_valid&&permit_host&&!host_ctrl_valid);
 assign c_p_io_ready=p_io_ready&&busy;
 assign host_io_ready=p_io_ready&&permit_host&&!host_ctrl_valid;
 assign p_io_write=busy?c_p_io_write:host_io_write;
 assign p_io_node=busy?c_p_io_node:host_io_node;
 assign p_io_value=busy?c_p_io_value:host_io_value;
 assign p_io_field=busy?c_p_io_field:host_io_field;
 assign c_p_io_rsp_valid=p_io_rsp_valid&&!host_pending;
 assign host_io_rsp_valid=p_io_rsp_valid&&host_pending;
 assign p_io_rsp_ready=host_pending?host_io_rsp_ready:c_p_io_rsp_ready;
 assign c_p_io_status=p_io_status;
 assign host_io_status=p_io_status;
 assign c_p_io_payload=p_io_payload;
 assign host_io_payload=p_io_payload;
 assign c_p_io_present=p_io_present;
 assign host_io_present=p_io_present;
 assign p_edge_valid=0;
 assign p_edge_cookie=0;
 assign p_edge_parent=0;
 assign p_edge_child=0;
 assign p_edge_flags=0;
 assign p_edge_created=0;
 assign p_edge_has_laguna=0;
 assign p_result_ready=1;
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
 geometry_table_reader tables(
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
 coordinate_controller #(.TOKEN_BITS(TOKEN_BITS),.MAX_CYCLES(MAX_CYCLES)) controller(
 .clk(clk),
 .rst(rst),
 .enable(enable),
 .abort(abort),
 .nodes(nodes),
 .table_rows(table_rows),
 .table_columns(table_columns),
 .active(p_active),
 .active_query(p_active_query),
 .active_price(p_active_price),
 .req_valid(req_valid),
 .req_ready(req_ready),
 .req_op(req_op),
 .req_query(req_query),
 .req_price(req_price),
 .req_cookie(req_cookie),
 .req_node(req_node),
 .rsp_valid(rsp_valid),
 .rsp_ready(rsp_ready),
 .rsp_status(rsp_status),
 .rsp_op(rsp_op),
 .rsp_query(rsp_query),
 .rsp_price(rsp_price),
 .rsp_cookie(rsp_cookie),
 .rsp_node(rsp_node),
 .rsp_y(rsp_y),
 .rsp_slr(rsp_slr),
 .rsp_next(rsp_next),
 .rsp_prev_column(rsp_prev_column),
 .rsp_label_prev(rsp_label_prev),
 .rsp_north(rsp_north),
 .rsp_prev_read(rsp_prev_read),
 .rsp_prev_present(rsp_prev_present),
 .rsp_attrs(rsp_attrs),
 .busy(busy),
 .fault(fault),
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
 .p_fault(p_fault)
 );
endmodule
