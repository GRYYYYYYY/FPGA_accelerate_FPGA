`timescale 1ns/1ps
module tb_access_fabric;
reg clk=0;always #5 clk=~clk;
reg  rst=0;
reg  abort=0;
reg  req_valid=0;
wire  req_ready;
reg [447:0] req_config=0;
reg [31:0] req_cookie=0;
reg [31:0] req_parent=0;
reg [31:0] req_child=0;
reg [31:0] req_sink=0;
reg [31:0] req_net=0;
reg [1:0] req_query=0;
reg [3:0] req_price=0;
wire  rsp_valid;
reg  rsp_ready=0;
wire [3:0] rsp_status;
wire [31:0] rsp_cookie;
wire [31:0] rsp_parent;
wire [31:0] rsp_child;
wire [31:0] rsp_sink;
wire [31:0] rsp_net;
wire [31:0] rsp_bits;
wire [31:0] rsp_action;
wire [31:0] rsp_steps;
wire [31:0] rsp_services;
wire [1:0] rsp_query;
wire [3:0] rsp_price;
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
wire  p_active;
wire [1:0] p_active_query;
wire [3:0] p_active_price;
wire  o_req_valid;
reg  o_req_ready=0;
wire [3:0] o_req_kind;
wire [4:0] o_req_phase;
wire [31:0] o_req_node;
wire [31:0] o_req_net;
wire [31:0] o_req_cookie;
wire [1:0] o_req_query;
wire [3:0] o_req_price;
reg  o_rsp_valid=0;
wire  o_rsp_ready;
reg [3:0] o_rsp_status=0;
reg [3:0] o_rsp_kind=0;
reg [4:0] o_rsp_phase=0;
reg [31:0] o_rsp_node=0;
reg [31:0] o_rsp_net=0;
reg [31:0] o_rsp_cookie=0;
reg [31:0] o_rsp_value=0;
reg [1:0] o_rsp_query=0;
reg [3:0] o_rsp_price=0;
reg  o_fault=0;
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
wire  busy;
wire  fault;
`ifdef PRESSURE
localparam SLOTS=1,TX_BITS=6,GEN_BITS=3;
`else
localparam SLOTS=32,TX_BITS=16,GEN_BITS=16;
`endif
access_fabric #(.SLOTS(SLOTS),.TX_BITS(TX_BITS),.GEN_BITS(GEN_BITS),.FRAMES(16384),.INDEX_BITS(14),.HASH_BITS(15),.SERVICE_MAX_CYCLES(256))dut(.*);
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
 integer cycles=0,cases=0,recoveries=0,i,j,owner_error=-1;reg auto_owner=0,owner_pending=0;integer owner_delay=0;
 reg[329:0]held;wire[329:0]bundle={rsp_status,rsp_cookie,rsp_parent,rsp_child,rsp_sink,rsp_net,rsp_bits,rsp_action,rsp_steps,rsp_services,rsp_query,rsp_price};
 always @(posedge clk)begin cycles<=cycles+1;if(cycles>2000000)$fatal(1,"watchdog");end
 always @(posedge clk)begin
  if(rst)begin owner_pending<=0;o_rsp_valid<=0;o_req_ready<=0;end
  else if(auto_owner)begin
   o_req_ready<=!owner_pending&&!o_rsp_valid;
   if(o_req_valid&&o_req_ready)begin
    owner_pending<=1;owner_delay<=2;o_rsp_kind<=o_req_kind;o_rsp_phase<=o_req_phase;o_rsp_node<=o_req_node;o_rsp_net<=o_req_net;o_rsp_cookie<=o_req_cookie;o_rsp_query<=o_req_query;o_rsp_price<=o_req_price;o_rsp_value<=0;o_rsp_status<=0;
    case(owner_error)0:o_rsp_cookie<=o_req_cookie+1;1:o_rsp_kind<=6;2:o_rsp_phase<=o_req_phase+1;3:o_rsp_node<=o_req_node+1;4:o_rsp_net<=1;5:o_rsp_query<=2;6:o_rsp_price<=4;7:o_rsp_status<=1;endcase
   end
   if(owner_pending&&!o_rsp_valid)begin if(owner_delay)owner_delay<=owner_delay-1;else o_rsp_valid<=1;end
   if(o_rsp_valid&&o_rsp_ready)begin owner_pending<=0;o_rsp_valid<=0;end
  end
 end
 task reset_case;
 begin
  @(negedge clk);rst=1;abort=0;inject_graph=0;inject_table=0;inject_pager=0;inject_pager_b=0;auto_owner=0;owner_error=-1;o_fault=0;
  req_valid=0;rsp_ready=0;host_ctrl_valid=0;host_io_valid=0;host_ctrl_rsp_ready=0;host_io_rsp_ready=0;g_cfg_valid=0;t_cfg_valid=0;g_cfg_rsp_ready=0;t_cfg_rsp_ready=0;
  repeat(5)@(negedge clk);rst=0;
  @(negedge clk);g_cfg_valid=1;t_cfg_valid=1;wait(g_cfg_ready&&t_cfg_ready);@(posedge clk);@(negedge clk);g_cfg_valid=0;t_cfg_valid=0;
  wait(g_cfg_rsp_valid&&t_cfg_rsp_valid);@(negedge clk);if(g_cfg_status||t_cfg_status)$fatal(1,"config");g_cfg_rsp_ready=1;t_cfg_rsp_ready=1;@(negedge clk);g_cfg_rsp_ready=0;t_cfg_rsp_ready=0;
  host_ctrl_op=0;host_ctrl_query=1;host_ctrl_price=3;host_ctrl_valid=1;wait(host_ctrl_ready);@(posedge clk);@(negedge clk);host_ctrl_valid=0;
  wait(host_ctrl_rsp_valid);@(negedge clk);if(host_ctrl_status||fault)$fatal(1,"open");host_ctrl_rsp_ready=1;@(negedge clk);host_ctrl_rsp_ready=0;
 end endtask
 task write_label(input integer n,f,input[31:0]v);
 begin
  @(negedge clk);host_io_valid=1;host_io_write=1;host_io_node=n;host_io_field=f;host_io_value=v;wait(host_io_ready);@(posedge clk);@(negedge clk);host_io_valid=0;
  wait(host_io_rsp_valid);@(negedge clk);if(host_io_status||fault)$fatal(1,"label setup");host_io_rsp_ready=1;@(negedge clk);host_io_rsp_ready=0;
 end endtask
 task start(input integer node,flags);
 begin
  @(negedge clk);req_config=0;req_config[31:0]=17;req_config[63:32]=flags;req_config[95:64]=node; // synthetic child ids0..17 match types
  req_config[127:96]=0;req_config[159:128]=0;req_config[191:160]=node%3;req_config[223:192]=node%5;req_config[255:224]=1;
  req_config[287:256]=0;req_config[319:288]=29;req_config[351:320]=-100;req_config[383:352]=100;req_config[415:384]=-100;req_config[447:416]=100;
  req_valid=1;req_cookie=42;req_parent=18;req_child=node;req_sink=36;req_net=0;req_query=1;req_price=3;
  wait(req_ready);@(posedge clk);@(negedge clk);req_valid=0;
 end endtask
 task retire(input integer status,input bad);
 begin
  wait(rsp_valid);@(negedge clk);if(rsp_status!=status||fault!==bad)$fatal(1,"case=%0d status=%0d/%0d fault=%b af=%b df=%b cf=%b",cases,rsp_status,status,fault,dut.a_fault,dut.d_fault,dut.c_fault);
  held=bundle;repeat(5)begin @(negedge clk);if(!rsp_valid||held!==bundle)$fatal(1,"unstable");end
  rsp_ready=1;@(negedge clk);rsp_ready=0;repeat(3)@(negedge clk);if(bad&&(!fault||req_ready||host_ctrl_ready||host_io_ready))$fatal(1,"fault not stopped");
 end endtask
 task recovery;
 begin reset_case;start(12,0);wait(rsp_valid);@(negedge clk);if(rsp_action!=1||rsp_bits||rsp_services!=2)$fatal(1,"recovery value case=%0d status=%0d action=%0d bits=%0d services=%0d fault=%b af=%b df=%b cf=%b ds=%0d",cases,rsp_status,rsp_action,rsp_bits,rsp_services,fault,dut.a_fault,dut.d_fault,dut.c_fault,dut.dispatch.rsp_status);retire(0,0);recoveries=recoveries+1;end endtask
 initial begin
  g_cfg_offsets_base=64'h1fffff000;g_cfg_edges_base=64'h10fffff000;g_cfg_attrs_base=64'h20fffff000;g_cfg_nodes=64;g_cfg_edges=0;
  t_cfg_rows_base=64'h31fffff000;t_cfg_columns_base=64'h41fffff000;t_cfg_rows=128;t_cfg_columns=64;graph_size0=320;graph_size1=0;graph_size2=2048;table_size0=1024;table_size1=512;
  for(i=0;i<6;i=i+1)begin
   reset_case;
   case(i)
    0:begin inject_graph=1;start(0,4);end
    1:begin inject_table=1;auto_owner=1;start(6,8);end
    2:begin write_label(5,2,64);start(5,4);end
    3:begin write_label(1,4,1);write_label(9,3,33);inject_pager=1;start(1,0);end
    4:begin write_label(9,3,33);inject_pager_b=1;start(1,0);end
    5:begin start(6,8);end // no owner readiness: dispatcher timeout256
   endcase
   retire(5,1);cases=cases+1;recovery;
  end
  for(i=0;i<8;i=i+1)begin reset_case;auto_owner=1;owner_error=i;start(6,8);retire(5,1);cases=cases+1;recovery;end
  // Abort at kernel work, label wait, coordinate wait, and final response.
  for(i=0;i<4;i=i+1)begin
   reset_case;start(0,4);
   case(i)0:repeat(3)@(negedge clk);1:wait(dut.dispatch.state==2);2:wait(dut.dispatch.state==4);3:begin wait(rsp_valid);@(negedge clk);held=bundle;end endcase
   @(negedge clk);abort=1;@(negedge clk);abort=0;if(i==3&&held!==bundle)$fatal(1,"late abort mutated result");retire(i==3?0:5,1);cases=cases+1;recovery;
  end
  reset_case;start(12,0);wait(rsp_valid);@(negedge clk);held=bundle;o_fault=1;@(negedge clk);if(bundle!==held)$fatal(1,"late owner fault");retire(0,1);cases=cases+1;recovery;
  $display("ACCESS_FABRIC_BOUNDARIES_PASS faults=%0d recoveries=%0d cycles=%0d",cases,recoveries,cycles);$finish;
 end

endmodule
