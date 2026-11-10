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
`ifdef PRESSURE
localparam SLOTS=1,TX_BITS=6,GEN_BITS=3;
`else
localparam SLOTS=32,TX_BITS=16,GEN_BITS=16;
`endif
access_fabric #(.SLOTS(SLOTS),.TX_BITS(TX_BITS),.GEN_BITS(GEN_BITS),.FRAMES(16384),.INDEX_BITS(14),.HASH_BITS(15))dut(.*);
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
reg[63:0]owner_image_size=0;reg inject_owner=0,inject_owner_b=0;
integer owner_reads,owner_writes,owner_rbeats,owner_wbeats,owner_bs;
axi_file_memory #(.MAX_BEATS(1),.TAG("owners"))mem_owner(
.clk(clk),
.rst(rst),
.base0(owner_cfg_primary),
.base1(64'd0),
.base2(64'd0),
.size0(owner_image_size),
.size1(64'd0),
.size2(64'd0),
.inject_r(inject_owner),
.inject_b(inject_owner_b),
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
 integer fd,ctxfd,logfd,rc,i,row,case_id,saved_case,cases=0,steps=0,services=0,cycles=0,case_steps,case_services,j;
 integer native_reads=0,checkpoints=0,host_blocks=0,golden_count=0;
 reg[31:0]golden_node[0:1023];reg[159:0]golden_value[0:1023];
 reg[31:0]ins[0:19],outs[0:5];reg[639:0]expected_input;reg[191:0]expected_output;
 reg[31:0]parent_id,child_id,sink_id,pred_id,parent_prev,child_prev,visited,target,kind,phase,expected_node,value,final_bits,final_action;
 integer occ,uses,ctx_case,limit=0;string vecpath,ctxpath,outpath;
 reg[329:0]held_response;
 wire[329:0]response_bundle={rsp_status,rsp_cookie,rsp_parent,rsp_child,rsp_sink,rsp_net,rsp_bits,rsp_action,rsp_steps,rsp_services,rsp_query,rsp_price};
 reg owner_pending=0;integer owner_calls=0,owner_commands=0,owner_blocks=0;
 reg[110:0]owner_identity;
 always @(posedge clk)begin
  if(rst)owner_pending<=0;
  else begin
   if(dut.o_req_valid&&dut.o_req_ready)begin
    if(owner_pending||dut.o_req_node!=child_id||dut.o_req_net||!(dut.o_req_kind==4||dut.o_req_kind==6))$fatal(1,"owner request scope");
    owner_pending<=1;owner_identity<={dut.o_req_kind,dut.o_req_phase,dut.o_req_node,dut.o_req_net,dut.o_req_cookie,dut.o_req_query,dut.o_req_price};owner_calls=owner_calls+1;
   end
   if(dut.o_rsp_valid&&dut.o_rsp_ready)begin
    if(!owner_pending||{dut.o_rsp_kind,dut.o_rsp_phase,dut.o_rsp_node,dut.o_rsp_net,dut.o_rsp_cookie,dut.o_rsp_query,dut.o_rsp_price}!==owner_identity)$fatal(1,"owner identity echo");owner_pending<=0;
   end
   if(dut.access_pending)begin
    if(host_owner_req_ready||owner_cfg_ready)$fatal(1,"owner host/config admitted during decision");
    if(host_owner_req_valid)owner_blocks=owner_blocks+1;
   end
   if(dut.bridge_host_pending&&req_ready)$fatal(1,"decision admitted during owner transaction");
  end
 end
 integer old_occ=0,old_uses=0,old_child=0,nuser,branch;
 task owner_command(input integer operation,input[31:0]id,net);
  begin
   @(negedge clk);owner_commands=owner_commands+1;host_owner_req_op=operation;host_owner_req_cookie=owner_commands;host_owner_req_node=id;host_owner_req_net=net;host_owner_req_valid=1;
   wait(host_owner_req_ready);@(posedge clk);@(negedge clk);host_owner_req_valid=0;wait(host_owner_rsp_valid);@(negedge clk);
   if(fault||host_owner_rsp_status!=0||host_owner_rsp_cookie!=owner_commands)$fatal(1,"owner host response");
   $fdisplay(logfd,"O %0d %0d %0d %0d %0d %0d",operation,id,net,host_owner_rsp_count,host_owner_rsp_occupancy,host_owner_rsp_will_overuse);
   repeat(2)begin @(negedge clk);if(req_ready)$fatal(1,"decision during held host owner response");end
   host_owner_rsp_ready=1;@(negedge clk);host_owner_rsp_ready=0;
  end
 endtask
 task prepare_owner;
  begin
   for(branch=0;branch<old_uses;branch=branch+1)owner_command(2,old_child,0);
   for(nuser=1;nuser<=old_occ-(old_uses!=0);nuser=nuser+1)owner_command(2,old_child,nuser);
   for(branch=0;branch<uses;branch=branch+1)owner_command(1,child_id,0);
   for(nuser=1;nuser<=occ-(uses!=0);nuser=nuser+1)owner_command(1,child_id,nuser);
   old_child=child_id;old_occ=occ;old_uses=uses;
  end
 endtask
 reg[20:0]bound_page[0:31];reg[31:0]bound_valid=0;reg native_pending=0;integer pending_op,pending_slot,pending_node;reg[159:0]pending_value;reg pending_present;
 function integer lookup(input[31:0]id);integer i;begin lookup=-1;for(i=0;i<golden_count;i=i+1)if(golden_node[i]==id)lookup=i;end endfunction
 always @(posedge clk)begin
  cycles<=cycles+1;if(cycles>100000000)$fatal(1,"watchdog");
  if(rst)begin native_pending<=0;bound_valid<=0;end
  else begin
   if(fault)$fatal(1,"fabric fault case=%0d astate=%0d dstate=%0d ast=%0d c_fault=%b d_fault=%b",saved_case,dut.access.controller.state,dut.dispatch.state,rsp_status,dut.c_fault,dut.d_fault);
   if(dut.a_busy)begin if(host_ctrl_ready||host_io_ready||req_ready)$fatal(1,"host admitted during decision");if(host_ctrl_valid&&host_io_valid)host_blocks=host_blocks+1;end
   if(dut.host_pending&&req_ready)$fatal(1,"decision admitted during host operation");
   if(dut.access.k_req_valid&&dut.access.k_req_ready&&dut.access.k_req_words!==expected_input)$fatal(1,"resident state row=%0d",row);
   if(dut.coordinates.pager.native_cmd_valid&&dut.coordinates.pager.native_cmd_ready)begin
    if(native_pending)$fatal(1,"native overlap");native_pending<=1;pending_op=dut.coordinates.pager.native_cmd_op;pending_slot=dut.coordinates.pager.native_cmd_slot;
    if(pending_op==2)begin
     if(!bound_valid[pending_slot])$fatal(1,"native read unbound");pending_node=bound_page[pending_slot]*8+dut.coordinates.pager.native_cmd_offset;j=lookup(pending_node);
     pending_present=j>=0;pending_value=j>=0?golden_value[j]:160'b0;
    end
    if(pending_op==1)bound_page[pending_slot]<=dut.coordinates.pager.native_cmd_page;
   end
   if(dut.coordinates.pager.native_rsp_valid&&dut.coordinates.pager.native_rsp_ready)begin
    if(!native_pending)$fatal(1,"native unowned");native_pending<=0;
    if(dut.coordinates.pager.native_rsp_status==0)begin
     if(pending_op==1)bound_valid[pending_slot]<=1;
     if(pending_op==4)bound_valid[pending_slot]<=0;
     if(pending_op==12)begin if(bound_valid!=0)$fatal(1,"checkpoint bound slots");checkpoints=checkpoints+1;end
    end
    if(pending_op==2)begin
     if(dut.coordinates.pager.native_rsp_status!=0||dut.coordinates.pager.native_rsp_payload!==pending_value||dut.coordinates.pager.native_rsp_present!==pending_present)$fatal(1,"native label mismatch node=%0d expected=%h got=%h present=%b/%b",pending_node,pending_value,dut.coordinates.pager.native_rsp_payload,pending_present,dut.coordinates.pager.native_rsp_present);
     native_reads=native_reads+1;
    end
   end
  end
 end
 integer owner_writes_before_control;
 task control(input integer op,q,p);
  begin
   owner_writes_before_control=owner_writes;@(negedge clk);host_ctrl_op=op;host_ctrl_query=q;host_ctrl_price=p;host_ctrl_valid=1;
   wait(host_ctrl_ready);@(posedge clk);@(negedge clk);host_ctrl_valid=0;wait(host_ctrl_rsp_valid);@(negedge clk);
   if(host_ctrl_status!=0)$fatal(1,"control %d/%d",op,host_ctrl_status);
   repeat(2)@(negedge clk);host_ctrl_rsp_ready=1;@(negedge clk);host_ctrl_rsp_ready=0;
   if(owner_writes!=owner_writes_before_control)$fatal(1,"query control mutated design owner");
   if(op==0)golden_count=0;
    $fdisplay(logfd,"Q %0d %0d %0d",op,q,p);
  end
 endtask
 task write_label(input integer n,f,input[31:0]v);
  integer gi;
  begin
   @(negedge clk);host_io_write=1;host_io_node=n;host_io_field=f;host_io_value=v;host_io_valid=1;
   wait(host_io_ready);@(posedge clk);@(negedge clk);host_io_valid=0;wait(host_io_rsp_valid);@(negedge clk);
   if(host_io_status!=0)$fatal(1,"label write");host_io_rsp_ready=1;@(negedge clk);host_io_rsp_ready=0;
   gi=lookup(n);if(gi<0)begin gi=golden_count;golden_count=golden_count+1;if(golden_count>1024)$fatal(1,"golden capacity");golden_node[gi]=n;golden_value[gi]=0;end
   golden_value[gi][f*32+:32]=v; $fdisplay(logfd,"L %0d %0d %0d",n,f,v);
  end
 endtask
 task read_row;
 begin
  rc=$fscanf(fd,"%d %d",row,case_id);if(rc!=2)$fatal(1,"header parse");
  for(i=0;i<20;i=i+1)begin rc=$fscanf(fd,"%h",ins[i]);if(rc!=1)$fatal(1,"input parse");expected_input[i*32+:32]=ins[i];end
  for(i=0;i<6;i=i+1)begin rc=$fscanf(fd,"%h",outs[i]);if(rc!=1)$fatal(1,"output parse");expected_output[i*32+:32]=outs[i];end
  rc=$fscanf(fd,"\n");
 end endtask
 initial begin
  if(!$value$plusargs("vectors=%s",vecpath)||!$value$plusargs("contexts=%s",ctxpath)||!$value$plusargs("output=%s",outpath))$fatal(1,"paths");
  if(!$value$plusargs("nodes=%d",g_cfg_nodes)||!$value$plusargs("edges=%d",g_cfg_edges)||!$value$plusargs("rows=%d",t_cfg_rows)||!$value$plusargs("columns=%d",t_cfg_columns))$fatal(1,"sizes");rc=$value$plusargs("limit=%d",limit);
  fd=$fopen(vecpath,"r");ctxfd=$fopen(ctxpath,"r");logfd=$fopen(outpath,"w");if(!fd||!ctxfd||!logfd)$fatal(1,"open");
  g_cfg_offsets_base=64'h1fffff000;g_cfg_edges_base=64'h10fffff000;g_cfg_attrs_base=64'h20fffff000;t_cfg_rows_base=64'h31fffff000;t_cfg_columns_base=64'h41fffff000;
  graph_size0=((g_cfg_nodes+64'd1)*4+63)&~64'd63;graph_size1=(g_cfg_edges*64'd4+63)&~64'd63;graph_size2=(g_cfg_nodes*64'd32+63)&~64'd63;table_size0=(t_cfg_rows*64'd8+63)&~64'd63;table_size1=(t_cfg_columns*64'd8+63)&~64'd63;
  rst=1;repeat(5)@(negedge clk);rst=0;
  @(negedge clk);g_cfg_valid=1;t_cfg_valid=1;wait(g_cfg_ready&&t_cfg_ready);@(posedge clk);@(negedge clk);g_cfg_valid=0;t_cfg_valid=0;
  wait(g_cfg_rsp_valid&&t_cfg_rsp_valid);@(negedge clk);if(g_cfg_status||t_cfg_status)$fatal(1,"configure");g_cfg_rsp_ready=1;t_cfg_rsp_ready=1;@(negedge clk);g_cfg_rsp_ready=0;t_cfg_rsp_ready=0;
  owner_cfg_primary=64'h51fffff000;owner_cfg_nodes=g_cfg_nodes;owner_cfg_capacity=64;
  owner_cfg_pool=owner_cfg_primary+((g_cfg_nodes*64'd16+63)&~64'd63)+4096;owner_cfg_allocator=owner_cfg_pool+1024+4096;owner_image_size=owner_cfg_allocator-owner_cfg_primary+64;
  owner_cfg_valid=1;wait(owner_cfg_ready);@(posedge clk);@(negedge clk);owner_cfg_valid=0;wait(owner_cfg_rsp_valid);@(negedge clk);
  if(owner_cfg_status||!owner_configured)$fatal(1,"owner configure");owner_cfg_rsp_ready=1;@(negedge clk);owner_cfg_rsp_ready=0;
  while(!$feof(fd)&&(limit==0||cases<limit))begin
   read_row;if(ins[0]!=0)$fatal(1,"start row");saved_case=case_id;case_steps=0;case_services=0;
   rc=$fscanf(ctxfd,"%d %d %d %d %d %h %h %h %h %d %d\n",ctx_case,parent_id,child_id,sink_id,pred_id,parent_prev,child_prev,visited,target,occ,uses);if(rc!=11||ctx_case!=case_id)$fatal(1,"context parse");
   prepare_owner;control(0,1,3);
   if(parent_prev)write_label(parent_id,2,parent_prev);
   if(child_prev)write_label(child_id,2,child_prev);
   if(visited)write_label(child_id,3,visited);
   if(target)write_label(child_id,4,target);
   if(cases%50==0)control(1,1,3);
   @(negedge clk);req_valid=1;req_cookie=case_id+100;req_config=expected_input[639:192];req_parent=parent_id;req_child=child_id;req_sink=sink_id;req_net=0;req_query=1;req_price=3;
   wait(req_ready);@(posedge clk);@(negedge clk);req_valid=0;req_config=~req_config;req_cookie=32'hbad;
   host_owner_req_valid=1;host_owner_req_op=1;host_owner_req_node=child_id;host_owner_req_net=0;host_owner_req_cookie=32'hbad;owner_cfg_valid=1;
   host_ctrl_valid=1;host_ctrl_op=2;host_ctrl_query=1;host_ctrl_price=3;host_io_valid=1;host_io_write=1;host_io_node=child_id;host_io_field=2;host_io_value=32'hbadabcde;
   begin:decision
    while(1)begin
     wait(dut.access.k_rsp_valid);@(negedge clk);
     if(dut.access.k_rsp_words!==expected_output||dut.access.k_rsp_status)$fatal(1,"HLS row=%0d expected=%h actual=%h",row,expected_output,dut.access.k_rsp_words);
     $fdisplay(logfd,"K %0d %0d %048h",row,saved_case,dut.access.k_rsp_words);steps=steps+1;case_steps=case_steps+1;
     kind=outs[4];phase=outs[1];final_bits=outs[2];final_action=outs[5];expected_node=kind==8?sink_id:kind==9?parent_id:kind==10?outs[3]:child_id;
     if(kind==0)disable decision;
     read_row;if(case_id!=saved_case||ins[0]!=1)$fatal(1,"advance row");value=ins[5];
     wait(dut.a_svc_valid);@(negedge clk);
     if(dut.a_svc_kind!==kind[3:0]||dut.a_svc_phase!==phase[4:0]||dut.a_svc_node!==expected_node||dut.a_svc_net||dut.a_svc_query!=1||dut.a_svc_price!=3)$fatal(1,"dispatch request case=%0d kind=%0d node=%0d/%0d",saved_case,kind,dut.a_svc_node,expected_node);
     wait(dut.a_svc_rsp_valid);@(negedge clk);
     if(dut.a_svc_rsp_status||dut.a_svc_rsp_value!==value)$fatal(1,"physical service case=%0d kind=%0d node=%0d expected=%h actual=%h",saved_case,kind,expected_node,value,dut.a_svc_rsp_value);
     $fdisplay(logfd,"S %0d %0d %0d %0d %0d %0d %08h",saved_case,kind,phase,expected_node,0,dut.a_svc_rsp_cookie,dut.a_svc_rsp_value);
     @(posedge clk);@(negedge clk);services=services+1;case_services=case_services+1;
    end
   end
   wait(rsp_valid);@(negedge clk);
   if(rsp_status||rsp_cookie!=saved_case+100||rsp_parent!=parent_id||rsp_child!=child_id||rsp_sink!=sink_id||rsp_net||rsp_query!=1||rsp_price!=3||rsp_bits!=final_bits||rsp_action!=final_action||rsp_steps!=case_steps||rsp_services!=case_services)$fatal(1,"final case=%0d",saved_case);
   held_response=response_bundle;repeat(3)begin @(negedge clk);if(!rsp_valid||response_bundle!==held_response)$fatal(1,"result unstable");end
   $fdisplay(logfd,"D %0d %0d %0d %0d %0d",saved_case,rsp_bits,rsp_action,rsp_steps,rsp_services);
   rsp_ready=1;@(negedge clk);rsp_ready=0;host_ctrl_valid=0;host_io_valid=0;host_owner_req_valid=0;owner_cfg_valid=0;control(2,1,3);
   owner_command(0,child_id,0);if(host_owner_rsp_count!=uses||host_owner_rsp_occupancy!=occ)$fatal(1,"owner state lost on query CLOSE");
   $fdisplay(logfd,"P %0d %0d %0d %0d",saved_case,child_id,uses,occ);cases=cases+1;
  end
  if(g_reads!=g_rbeats||t_reads!=t_rbeats||p_writes!=p_bs||native_pending||dut.coordinates.p_page_leases||dut.coordinates.p_memory_leases||owner_pending||dut.bridge_busy||dut.raw_busy)$fatal(1,"outstanding");
  $fclose(logfd);$display("ACCESS_FABRIC_PASS cases=%0d steps=%0d services=%0d owner_calls=%0d native_reads=%0d checkpoints=%0d host_blocks=%0d graph_reads=%0d table_reads=%0d label_reads=%0d label_writes=%0d owner_commands=%0d owner_reads=%0d owner_writes=%0d owner_blocks=%0d cycles=%0d",cases,steps,services,owner_calls,native_reads,checkpoints,host_blocks,g_reads,t_reads,p_reads,p_writes,owner_commands,owner_reads,owner_writes,owner_blocks,cycles);$finish;
 end

endmodule
