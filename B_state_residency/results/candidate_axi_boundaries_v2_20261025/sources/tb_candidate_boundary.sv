`timescale 1ns/1ps
module tb_candidate_boundary;
 reg hold_graph_ar=0,inject_graph_r=0;wire graph_mem_arready;integer mode=0;reg[80:0]held_ar;
 assign g_m_arready=graph_mem_arready&&!hold_graph_ar;
reg clk=0;always #5 clk=~clk;
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
candidate_engine #(.SLOTS(SLOTS),.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS))dut(.*);
integer g_reads,g_writes,g_rbeats,g_wbeats,g_bs;
axi_file_memory #(.ADDR_BITS(64),.READ_ONLY(1),.MAX_BEATS(1),.TAG("graph"))mem_g(
.clk(clk),
.rst(rst),
.base0(g_cfg_offsets_base),
.base1(g_cfg_edges_base),
.base2(g_cfg_attrs_base),
.size0(64'd36356096),
.size1(64'd161878144),
.size2(64'd290848320),
.inject_r(inject_graph_r),
.inject_b(1'b0),
.araddr(g_m_araddr),
.arlen(g_m_arlen),
.arsize(g_m_arsize),
.arburst(g_m_arburst),
.arid(g_m_arid),
.arvalid(g_m_arvalid&&!hold_graph_ar),
.arready(graph_mem_arready),
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
.size0(64'd145433472),
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
 integer fd,rc,i,j,k,cycles=0,expansions=0,decisions=0,early_count=0,raw_seen=0,host_blocks=0,limit=0;
 integer cookie,parent,prune,laguna,hit,raw_count,nchildren,ci,sink,net,seq,flags,xmin,xmax,ymin,ymax;
 integer cn[0:31],cp[0:31],an[0:31],ab[0:31],aa[0:31],asvc[0:31];reg[447:0]acfg[0:31];
 integer acount,allowed,early,pruned,ordinal,child,bits,action,services,op,q,price,node,field;reg[31:0]mask,value,word_value;
 string path,output_path,command;integer output_fd;
 reg[767:0]held_out;reg[196:0]held_final;
 always @(posedge clk)begin
  cycles<=cycles+1;if(cycles>100000000)$fatal(1,"watchdog");
  if(!rst)begin
   // Fault is expected in this separate boundary harness.
   if(dut.operation_pending)begin
    if(host_ctrl_ready||host_io_ready||host_design_req_ready||host_owner_req_ready||expand_ready)$fatal(1,"host lock gap");
    if(host_ctrl_valid&&host_io_valid&&host_design_req_valid&&host_owner_req_valid)host_blocks<=host_blocks+1;
   end
   if(dut.e_out_valid&&dut.e_out_ready)begin
    if(raw_seen>=nchildren||dut.e_out_node!==cn[raw_seen]||dut.e_out_position!==cp[raw_seen]||dut.e_out_sequence!==raw_seen)$fatal(1,"expanded child mismatch");
    raw_seen<=raw_seen+1;
   end
  end
 end
 task control(input integer operation,query,version);
  begin
   @(negedge clk);host_ctrl_op=operation;host_ctrl_query=query;host_ctrl_price=version;host_ctrl_valid=1;
   wait(host_ctrl_ready);@(posedge clk);@(negedge clk);host_ctrl_valid=0;wait(host_ctrl_rsp_valid);@(negedge clk);
   if(host_ctrl_status)$fatal(1,"control");host_ctrl_rsp_ready=1;@(negedge clk);host_ctrl_rsp_ready=0;
  end
 endtask
 task label_write(input integer n,f,input[31:0]v);
  begin
   @(negedge clk);host_io_write=1;host_io_node=n;host_io_field=f;host_io_value=v;host_io_valid=1;
   wait(host_io_ready);@(posedge clk);@(negedge clk);host_io_valid=0;wait(host_io_rsp_valid);@(negedge clk);
   if(host_io_status)$fatal(1,"label write");host_io_rsp_ready=1;@(negedge clk);host_io_rsp_ready=0;
  end
 endtask
 initial begin
  rst=1;rc=$value$plusargs("mode=%d",mode);
  if(!$value$plusargs("vectors=%s",path)||!$value$plusargs("output=%s",output_path))$fatal(1,"paths");rc=$value$plusargs("limit=%d",limit);
  fd=$fopen(path,"r");output_fd=$fopen(output_path,"w");if(!fd||!output_fd)$fatal(1,"open");
  g_cfg_offsets_base=64'h1fffff000;g_cfg_edges_base=64'h10fffff000;g_cfg_attrs_base=64'h20fffff000;g_cfg_nodes=9089009;g_cfg_edges=40469536;
  d_cfg_base=64'h31fffff000;d_cfg_nodes=9089009;t_cfg_rows_base=64'h41fffff000;t_cfg_columns_base=64'h51fffff000;t_cfg_rows=311;t_cfg_columns=0;
  owner_cfg_primary=64'h61fffff000;owner_cfg_nodes=9089009;owner_cfg_capacity=64;owner_cfg_pool=owner_cfg_primary+145428288;owner_cfg_allocator=owner_cfg_primary+145433408;
  repeat(5)@(negedge clk);rst=0;
  @(negedge clk);g_cfg_valid=1;d_cfg_valid=1;t_cfg_valid=1;owner_cfg_valid=1;
  wait(g_cfg_ready&&d_cfg_ready&&t_cfg_ready&&owner_cfg_ready);@(posedge clk);@(negedge clk);g_cfg_valid=0;d_cfg_valid=0;t_cfg_valid=0;owner_cfg_valid=0;
  wait(g_cfg_rsp_valid&&d_cfg_rsp_valid&&t_cfg_rsp_valid&&owner_cfg_rsp_valid);@(negedge clk);
  if(g_cfg_status||d_cfg_status||t_cfg_status||owner_cfg_status)$fatal(1,"config");g_cfg_rsp_ready=1;d_cfg_rsp_ready=1;t_cfg_rsp_ready=1;owner_cfg_rsp_ready=1;
  @(negedge clk);g_cfg_rsp_ready=0;d_cfg_rsp_ready=0;t_cfg_rsp_ready=0;owner_cfg_rsp_ready=0;
  while(!$feof(fd)&&(limit==0||expansions<limit))begin
   rc=$fscanf(fd,"%s",command);if(rc!=1)$fatal(1,"parse");
   if(command=="Q")begin rc=$fscanf(fd,"%d %d %d\n",op,q,price);if(rc!=3)$fatal(1,"Q");control(op,q,price);end
   else if(command=="L")begin rc=$fscanf(fd,"%d %d %d\n",node,field,value);if(rc!=3)$fatal(1,"L");label_write(node,field,value);end
   else if(command=="E")begin
    rc=$fscanf(fd,"%d %d %d %d %d %d %d %d\n",cookie,parent,prune,laguna,hit,raw_count,mask,nchildren);if(rc!=8)$fatal(1,"E");
    for(i=0;i<nchildren;i=i+1)begin rc=$fscanf(fd,"%s %d %d\n",command,cp[i],cn[i]);if(rc!=3||command!="C")$fatal(1,"C");end
    rc=$fscanf(fd,"%s %d %d %d %d %d %d %d %d %d\n",command,ci,sink,net,seq,flags,xmin,xmax,ymin,ymax);if(rc!=10||command!="D")$fatal(1,"D");
    acount=0;command="";
    while(command!="Z")begin
     rc=$fscanf(fd,"%s",command);if(rc!=1)$fatal(1,"decision parse");
     if(command=="L")begin rc=$fscanf(fd,"%d %d %d\n",node,field,value);if(rc!=3)$fatal(1,"target L");label_write(node,field,value);end
     else if(command=="A")begin
      rc=$fscanf(fd,"%d %d %d %d %d",ordinal,child,bits,action,services);if(rc!=5||ordinal!=acount)$fatal(1,"A");
      an[acount]=child;ab[acount]=bits;aa[acount]=action;asvc[acount]=services;
      for(j=0;j<14;j=j+1)begin rc=$fscanf(fd,"%d",word_value);if(rc!=1)$fatal(1,"Config");acfg[acount][j*32+:32]=word_value;end
      acount=acount+1;
     end else if(command=="Z")begin rc=$fscanf(fd,"%d %d %d\n",allowed,early,pruned);if(rc!=3)$fatal(1,"Z");end
     else $fatal(1,"unknown decision");
    end
    @(negedge clk);raw_seen=0;expand_cookie=cookie;expand_parent=parent;expand_prune=prune;expand_has_laguna=laguna;expand_sink=sink;expand_net=net;expand_sequence=seq;expand_flags=flags&32'h11c;
    expand_xmin=xmin;expand_xmax=xmax;expand_ymin=ymin;expand_ymax=ymax;expand_valid=1;
    wait(expand_ready);@(posedge clk);@(negedge clk);expand_valid=0;
    host_ctrl_valid=1;host_io_valid=1;host_design_req_valid=1;host_owner_req_valid=1;
    if(nchildren>0)begin
     // Gate the actual shared graph AXI AR before metadata's first graph fetch.
     hold_graph_ar=1;wait(dut.controller.m_pending);wait(g_m_arvalid);@(negedge clk);
     held_ar={g_m_araddr,g_m_arlen,g_m_arsize,g_m_arburst,g_m_arid};
     if(mode==0)begin
      abort=1;
      repeat(4)begin @(negedge clk);if(!g_m_arvalid||{g_m_araddr,g_m_arlen,g_m_arsize,g_m_arburst,g_m_arid}!==held_ar||g_m_arready)$fatal(1,"AR withdrawn/changed on abort");end
     end else inject_graph_r=1;
     hold_graph_ar=0;
     wait(result_valid);@(negedge clk);
     if(result_status!=4||!dut.stopped||!dut.operation_pending)$fatal(1,"boundary error result");
     held_final={result_status,result_cookie,result_count,result_expanded_count,result_raw_count,result_mask,result_hit,result_early};
     wait(!dut.metadata.g_pending&&!dut.metadata.d_pending&&!dut.arb_g_busy&&!mem_g.rp&&!g_m_rvalid&&!g_m_arvalid);
     repeat(4)begin @(negedge clk);if(!result_valid||{result_status,result_cookie,result_count,result_expanded_count,result_raw_count,result_mask,result_hit,result_early}!==held_final||!dut.operation_pending)$fatal(1,"boundary result/lock stability");end
     if(mode==1&&!dut.g_fault)$fatal(1,"actual R error not latched");
     result_ready=1;@(negedge clk);result_ready=0;host_ctrl_valid=0;host_io_valid=0;host_design_req_valid=0;host_owner_req_valid=0;abort=0;inject_graph_r=0;
     repeat(3)@(negedge clk);
     if(dut.operation_pending||expand_ready||host_ctrl_ready||host_io_ready||host_design_req_ready||host_owner_req_ready||owner_writes)$fatal(1,"stopped admission or owner corruption");
     $display("CANDIDATE_BOUNDARY_PASS mode=%0d cookie=%0d graph_reads=%0d owner_writes=%0d cycles=%0d",mode,cookie,g_reads,owner_writes,cycles);$finish;
    end
    for(k=0;k<acount;k=k+1)begin
     wait(out_valid);@(negedge clk);
     if(out_cookie!==cookie||out_node!==an[k]||out_sequence!==k||out_position!==cp[k]||out_bits!==ab[k]||out_action!==aa[k]||out_services!==asvc[k]||out_config!==acfg[k])$fatal(1,"decision mismatch cookie=%d ordinal=%d bits=%d/%d action=%d/%d svc=%d/%d config=%h/%h",cookie,k,out_bits,ab[k],out_action,aa[k],out_services,asvc[k],out_config,acfg[k]);
     held_out={out_config,out_attrs,out_bits,out_action};repeat(2)begin @(negedge clk);if(!out_valid||{out_config,out_attrs,out_bits,out_action}!==held_out)$fatal(1,"out stability");end
     $fdisplay(output_fd,"A %0d %0d %0d %0d %0d %0112h",cookie,k,out_node,out_bits,out_action,out_config);
     out_ready=1;@(negedge clk);out_ready=0;decisions=decisions+1;
    end
    wait(result_valid);@(negedge clk);
    if(result_status||result_cookie!==cookie||result_count!==acount||result_expanded_count!==nchildren||result_raw_count!==raw_count||result_mask!==mask||result_hit!==hit[0]||result_early!==early[0]||raw_seen!=nchildren)$fatal(1,"final mismatch cookie=%d status=%d counts=%d/%d expanded=%d/%d rawseen=%d",cookie,result_status,result_count,acount,result_expanded_count,nchildren,raw_seen);
    repeat(3)@(negedge clk);result_ready=1;@(negedge clk);result_ready=0;host_ctrl_valid=0;host_io_valid=0;host_design_req_valid=0;host_owner_req_valid=0;
    expansions=expansions+1;early_count=early_count+early;
   end else $fatal(1,"unknown command %s",command);
  end
  $fclose(fd);$fclose(output_fd);
  if(owner_writes!=0)$fatal(1,"readonly candidate mutated ownership");
  $display("CANDIDATE_PASS expansions=%0d decisions=%0d early=%0d host_blocks=%0d graph_reads=%0d design_reads=%0d design_writes=%0d owner_reads=%0d cycles=%0d",expansions,decisions,early_count,host_blocks,g_reads,d_reads,d_writes,owner_reads,cycles);$finish;
 end

endmodule
