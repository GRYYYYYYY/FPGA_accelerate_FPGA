`timescale 1ns/1ps
module tb_metadata;
reg clk=0;always #5 clk=~clk;
reg  rst=0;
reg  abort=0;
reg  owner_configured=0;
reg [31:0] owner_nodes=0;
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
reg  active=0;
reg [1:0] active_query=0;
reg [3:0] active_price=0;
reg  req_valid=0;
wire  req_ready;
reg [31:0] req_cookie=0;
reg [31:0] req_parent=0;
reg [31:0] req_child=0;
reg [31:0] req_sink=0;
reg [31:0] req_net=0;
reg [31:0] req_sequence=0;
reg [31:0] req_flags=0;
reg [31:0] req_xmin=0;
reg [31:0] req_xmax=0;
reg [31:0] req_ymin=0;
reg [31:0] req_ymax=0;
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
wire [1:0] rsp_query;
wire [3:0] rsp_price;
wire [447:0] rsp_config;
wire  rsp_created;
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
wire  busy;
wire  fault;
wire  design_claim_active;
metadata_service dut(.*);
reg[63:0]graph_size0=0,graph_size1=0,graph_size2=0,design_size=0;
reg inject_graph=0,inject_design=0,inject_design_b=0;
integer g_reads,g_writes,g_rbeats,g_wbeats,g_bs;
axi_file_memory #(.MAX_BEATS(1),.READ_ONLY(1),.TAG("graph"))mem_g(
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
integer d_reads,d_writes,d_rbeats,d_wbeats,d_bs;
axi_file_memory #(.MAX_BEATS(1),.READ_ONLY(0),.TAG("design"))mem_d(
.clk(clk),
.rst(rst),
.base0(d_cfg_base),
.base1(64'd0),
.base2(64'd0),
.size0(design_size),
.size1(64'd0),
.size2(64'd0),
.inject_r(inject_design),
.inject_b(inject_design_b),
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
 integer fd,logfd,rc,cid,parent,child,sink,dead,cases=0,cycles=0,host_commands=0,host_blocks=0,write_before;
 reg[31:0]seq_word,flags,xmin_word,xmax_word,ymin_word,ymax_word;reg[447:0]expected;
 reg[618:0]held;string path;
 always @(posedge clk)begin
  cycles=cycles+1;if(cycles>10000000)$fatal(1,"metadata watchdog case=%0d state=%0d",cid,dut.controller.state);
  if(!rst)begin
   if(fault)$fatal(1,"metadata fault case=%0d state=%0d token=%0d",cid,dut.controller.state,dut.controller.token);
   if(dut.meta_pending)begin if(host_design_req_ready||req_ready)$fatal(1,"host/second request admitted during metadata");if(host_design_req_valid)host_blocks=host_blocks+1;end
   if(dut.host_pending&&req_ready)$fatal(1,"metadata accepted during host reply");
  end
 end
 task host_command(input integer op,node,owner,arg);
  begin
   @(negedge clk);host_commands=host_commands+1;host_design_req_op=op;host_design_req_node=node;host_design_req_owner=owner;host_design_req_arg=arg;host_design_req_cookie=host_commands;host_design_req_valid=1;
   wait(host_design_req_ready);@(posedge clk);@(negedge clk);host_design_req_valid=0;wait(host_design_rsp_valid);@(negedge clk);
   if(host_design_rsp_status||host_design_rsp_cookie!=host_commands)$fatal(1,"design host response op=%0d",op);
   $fdisplay(logfd,"H %0d %0d %0d %0d %0d %0d %0d",op,node,owner,arg,host_design_rsp_flags,host_design_rsp_count,host_design_rsp_mask);
   repeat(2)@(negedge clk);host_design_rsp_ready=1;@(negedge clk);host_design_rsp_ready=0;
  end
 endtask
 initial begin
  rst=1;
  if(!$value$plusargs("commands=%s",path))$fatal(1,"commands");fd=$fopen(path,"r");
  if(!$value$plusargs("observed=%s",path))$fatal(1,"observed");logfd=$fopen(path,"w");
  if(!$value$plusargs("nodes=%d",g_cfg_nodes)||!$value$plusargs("edges=%d",g_cfg_edges))$fatal(1,"sizes");
  if(!fd||!logfd)$fatal(1,"open metadata inputs");
  d_cfg_nodes=g_cfg_nodes;owner_nodes=g_cfg_nodes;owner_configured=1;active=1;active_query=1;active_price=3;
  g_cfg_offsets_base=64'h1fffff000;g_cfg_edges_base=64'h10fffff000;g_cfg_attrs_base=64'h20fffff000;d_cfg_base=64'h61fffff000;
  graph_size0=((g_cfg_nodes+64'd1)*4+63)&~64'd63;graph_size1=(g_cfg_edges*64'd4+63)&~64'd63;graph_size2=(g_cfg_nodes*64'd32+63)&~64'd63;design_size=(g_cfg_nodes*64'd16+63)&~64'd63;
  repeat(4)@(negedge clk);rst=0;
  g_cfg_valid=1;d_cfg_valid=1;wait(g_cfg_ready&&d_cfg_ready);@(posedge clk);@(negedge clk);g_cfg_valid=0;d_cfg_valid=0;
  wait(g_cfg_rsp_valid&&d_cfg_rsp_valid);@(negedge clk);if(g_cfg_status||d_cfg_status)$fatal(1,"configuration");g_cfg_rsp_ready=1;d_cfg_rsp_ready=1;@(negedge clk);g_cfg_rsp_ready=0;d_cfg_rsp_ready=0;
  while(!$feof(fd))begin
   rc=$fscanf(fd,"%d %d %d %d %d %h %h %h %h %h %h %h\n",cid,parent,child,sink,dead,seq_word,flags,xmin_word,xmax_word,ymin_word,ymax_word,expected);
   if(rc!=12)$fatal(1,"command format %0d",rc);
   host_command(2,child,0,0);if(dead)host_command(3,child,0,0);
   if(cases==0&&g_cfg_edges==0)begin
    host_command(1,parent,1,0);if(!design_claim_active||req_ready)$fatal(1,"metadata admitted before cache publication");
    repeat(3)@(negedge clk);host_command(5,parent,1,0);if(design_claim_active)$fatal(1,"cache claim not released");
   end
   write_before=d_writes;
   @(negedge clk);req_parent=parent;req_child=child;req_sink=sink;req_net=0;req_cookie=cid+100;req_sequence=seq_word;req_flags=flags;req_xmin=xmin_word;req_xmax=xmax_word;req_ymin=ymin_word;req_ymax=ymax_word;req_query=1;req_price=3;req_valid=1;
   wait(req_ready);@(posedge clk);@(negedge clk);req_valid=0;
   req_parent=32'hbad;req_child=32'hbad;req_sink=32'hbad;req_flags=32'hffffffff;req_sequence=0;req_cookie=0;req_xmin=0;req_xmax=0;req_ymin=0;req_ymax=0;
   host_design_req_valid=1;host_design_req_op=3;host_design_req_node=child;
   wait(rsp_valid);@(negedge clk);
   if(fault||rsp_status||!rsp_created||rsp_config!==expected||rsp_cookie!=cid+100||rsp_parent!=parent||rsp_child!=child||rsp_sink!=sink||rsp_net||rsp_query!=1||rsp_price!=3)$fatal(1,"metadata case=%0d expected=%h actual=%h status=%0d",cid,expected,rsp_config,rsp_status);
   if(d_writes!=write_before)$fatal(1,"metadata request mutated persistent state");
   held={rsp_status,rsp_cookie,rsp_parent,rsp_child,rsp_sink,rsp_net,rsp_query,rsp_price,rsp_config,rsp_created};
   repeat(3)begin @(negedge clk);if(!rsp_valid||{rsp_status,rsp_cookie,rsp_parent,rsp_child,rsp_sink,rsp_net,rsp_query,rsp_price,rsp_config,rsp_created}!==held)$fatal(1,"metadata response changed");end
   $fdisplay(logfd,"M %0d %0112h",cid,rsp_config);rsp_ready=1;@(negedge clk);rsp_ready=0;host_design_req_valid=0;cases=cases+1;
  end
  if(d_writes!=d_bs||dut.controller.g_pending||dut.controller.d_pending||dut.host_pending||dut.meta_pending)$fatal(1,"outstanding metadata traffic");
  $fclose(logfd);$display("METADATA_PASS cases=%0d host_commands=%0d host_blocks=%0d graph_reads=%0d design_reads=%0d design_writes=%0d cycles=%0d",cases,host_commands,host_blocks,g_reads,d_reads,d_writes,cycles);$finish;
 end

endmodule
