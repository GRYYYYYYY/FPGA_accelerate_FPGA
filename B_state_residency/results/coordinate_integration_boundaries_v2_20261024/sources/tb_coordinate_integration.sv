`timescale 1ns/1ps
module tb_coordinate_service;
reg clk=0;always #5 clk=~clk;
reg  rst=0;
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
reg  abort=0;
reg  req_valid=0;
wire  req_ready;
reg [1:0] req_op=0;
reg [1:0] req_query=0;
reg [3:0] req_price=0;
reg [31:0] req_cookie=0;
reg [31:0] req_node=0;
wire  rsp_valid;
reg  rsp_ready=0;
wire [3:0] rsp_status;
wire [1:0] rsp_op;
wire [1:0] rsp_query;
wire [3:0] rsp_price;
wire [31:0] rsp_cookie;
wire [31:0] rsp_node;
wire [31:0] rsp_y;
wire [31:0] rsp_slr;
wire [31:0] rsp_next;
wire [31:0] rsp_prev_column;
wire [31:0] rsp_label_prev;
wire  rsp_north;
wire  rsp_prev_read;
wire  rsp_prev_present;
wire [255:0] rsp_attrs;
wire  busy;
wire  fault;
reg  host_ctrl_valid=0;
wire  host_ctrl_ready;
reg [1:0] host_ctrl_op=0;
reg [1:0] host_ctrl_query=0;
reg [3:0] host_ctrl_price=0;
wire  host_ctrl_rsp_valid;
reg  host_ctrl_rsp_ready=0;
wire [3:0] host_ctrl_status;
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
wire  p_active;
wire [1:0] p_active_query;
wire [3:0] p_active_price;
`ifdef PRESSURE
localparam SLOTS=1,TX_BITS=6,GEN_BITS=3;
`else
localparam SLOTS=32,TX_BITS=16,GEN_BITS=16;
`endif
coordinate_service #(.SLOTS(SLOTS),.TX_BITS(TX_BITS),.GEN_BITS(GEN_BITS),.FRAMES(16384),.INDEX_BITS(14),.HASH_BITS(15))dut(.*);
reg inject_graph=0,inject_table=0,inject_pager=0,inject_pager_b=0;
reg[63:0]graph_size0=0,graph_size1=0,graph_size2=0,table_size0=0,table_size1=0;
integer g_reads,g_writes,g_rbeats,g_wbeats,g_bs;
axi_file_memory #(.ADDR_BITS(64),.READ_ONLY(1),.MAX_BEATS(1),.TAG("graph"))mem_g(
.clk(clk),
.rst(rst),
.base0(g_cfg_offsets_base),
.base1(g_cfg_edges_base),
.base2(g_cfg_attrs_base),
.size0(graph_size0),
.size1(graph_size1),
.size2(graph_size2),
.inject_r(inject_graph),
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
integer t_reads,t_writes,t_rbeats,t_wbeats,t_bs;
axi_file_memory #(.ADDR_BITS(64),.READ_ONLY(1),.MAX_BEATS(1),.TAG("tables"))mem_t(
.clk(clk),
.rst(rst),
.base0(t_cfg_rows_base),
.base1(t_cfg_columns_base),
.base2(64'd0),
.size0(table_size0),
.size1(table_size1),
.size2(64'd0),
.inject_r(inject_table),
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
.size0(64'd3145728),
.size1(64'd0),
.size2(64'd0),
.inject_r(inject_pager),
.inject_b(inject_pager_b),
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
 integer cases=0,cycles=0,i;reg[494:0]held;
 wire[494:0]bundle={rsp_status,rsp_op,rsp_query,rsp_price,rsp_cookie,rsp_node,rsp_y,rsp_slr,rsp_next,rsp_prev_column,rsp_label_prev,rsp_north,rsp_prev_read,rsp_prev_present,rsp_attrs};
 always @(posedge clk)begin cycles<=cycles+1;if(cycles>2000000)$fatal(1,"integration watchdog");end
 task reset_case;
 begin
  @(negedge clk);rst=1;abort=0;inject_graph=0;inject_table=0;inject_pager=0;inject_pager_b=0;
  req_valid=0;rsp_ready=0;host_ctrl_valid=0;host_io_valid=0;host_ctrl_rsp_ready=0;host_io_rsp_ready=0;g_cfg_valid=0;t_cfg_valid=0;g_cfg_rsp_ready=0;t_cfg_rsp_ready=0;
  repeat(5)@(negedge clk);rst=0;
  @(negedge clk);g_cfg_valid=1;t_cfg_valid=1;wait(g_cfg_ready&&t_cfg_ready);@(posedge clk);@(negedge clk);g_cfg_valid=0;t_cfg_valid=0;
  wait(g_cfg_rsp_valid&&t_cfg_rsp_valid);@(negedge clk);if(g_cfg_status||t_cfg_status)$fatal(1,"config");g_cfg_rsp_ready=1;t_cfg_rsp_ready=1;@(negedge clk);g_cfg_rsp_ready=0;t_cfg_rsp_ready=0;
  host_ctrl_op=0;host_ctrl_query=1;host_ctrl_price=3;host_ctrl_valid=1;wait(host_ctrl_ready);@(posedge clk);@(negedge clk);host_ctrl_valid=0;
  wait(host_ctrl_rsp_valid);@(negedge clk);if(host_ctrl_status||fault)$fatal(1,"open");host_ctrl_rsp_ready=1;@(negedge clk);host_ctrl_rsp_ready=0;
 end endtask
 task write_prev(input integer n,input[31:0]v);
 begin
  @(negedge clk);host_io_valid=1;host_io_write=1;host_io_node=n;host_io_field=2;host_io_value=v;
  wait(host_io_ready);@(posedge clk);@(negedge clk);host_io_valid=0;
  wait(host_io_rsp_valid);@(negedge clk);if(host_io_status||fault)$fatal(1,"write_prev");host_io_rsp_ready=1;@(negedge clk);host_io_rsp_ready=0;
 end endtask
 task start(input integer op,n);
 begin
  @(negedge clk);req_valid=1;req_op=op;req_query=1;req_price=3;req_cookie=42;req_node=n;
  wait(req_ready);@(posedge clk);@(negedge clk);req_valid=0;
 end endtask
 task retire(input integer status,input bad);
 begin
  wait(rsp_valid);@(negedge clk);if(rsp_status!=status||fault!==bad)$fatal(1,"integration case=%0d status=%0d/%0d fault=%b gf=%b tf=%b pf=%b",cases,rsp_status,status,fault,dut.g_fault,dut.t_fault,dut.p_fault);
  held=bundle;repeat(5)begin @(negedge clk);if(!rsp_valid||held!==bundle)$fatal(1,"integration unstable");end
  rsp_ready=1;@(negedge clk);rsp_ready=0;repeat(3)@(negedge clk);
  if(bad&&(!fault||req_ready||host_ctrl_ready||host_io_ready))$fatal(1,"integration fault not stopped");
 end endtask
 initial begin
  g_cfg_offsets_base=64'h1fffff000;g_cfg_edges_base=64'h10fffff000;g_cfg_attrs_base=64'h20fffff000;g_cfg_nodes=64;g_cfg_edges=0;
  t_cfg_rows_base=64'h31fffff000;t_cfg_columns_base=64'h41fffff000;t_cfg_rows=128;t_cfg_columns=64;
  graph_size0=320;graph_size1=0;graph_size2=2048;table_size0=1024;table_size1=512;
  for(i=0;i<7;i=i+1)begin
   reset_case;
   case(i)
    0:begin inject_graph=1;start(0,0);retire(5,1);end
    1:begin inject_table=1;start(1,0);retire(5,1);end
    2:begin write_prev(1,64);start(0,1);retire(7,1);end
    3:begin write_prev(1,32'hffffffff);write_prev(9,32'hffffffff);inject_pager=1;start(0,1);retire(5,1);end
    4:begin write_prev(1,32'hffffffff);inject_pager_b=1;start(0,9);retire(5,1);end
    5:begin start(0,1);abort=1;@(negedge clk);abort=0;retire(5,1);end
    6:begin start(0,0);wait(rsp_valid);@(negedge clk);held=bundle;abort=1;@(negedge clk);abort=0;if(held!==bundle)$fatal(1,"integration late fault");retire(0,1);end
   endcase
   cases=cases+1;
   // Coordinated cold reset flushes all mocked fabric transactions.
   reset_case;start(0,0);wait(rsp_valid);@(negedge clk);if(rsp_y!=70)$fatal(1,"recovery coordinate");retire(0,0);
  end
  $display("INTEGRATED_BOUNDARIES_PASS faults=%0d recoveries=%0d cycles=%0d",cases,cases,cycles);$finish;
 end

endmodule
