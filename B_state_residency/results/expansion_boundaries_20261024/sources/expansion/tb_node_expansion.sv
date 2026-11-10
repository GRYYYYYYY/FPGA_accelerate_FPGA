`timescale 1ns/1ps
module tb_node_expansion;
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
 reg  expand_valid=0;
 wire  expand_ready;
 reg [31:0] expand_cookie=0;
 reg [31:0] expand_parent=0;
 reg [31:0] expand_prune=0;
 reg [31:0] expand_has_laguna=0;
 wire  out_valid;
 reg  out_ready=0;
 wire [31:0] out_node;
 wire [31:0] out_position;
 wire [31:0] out_sequence;
 wire [255:0] out_attrs;
 wire  result_valid;
 reg  result_ready=0;
 wire [3:0] result_status;
 wire [31:0] result_detail;
 wire [31:0] result_cookie;
 wire [31:0] result_count;
 wire [31:0] result_raw_count;
 wire [31:0] result_mask;
 wire  result_hit;
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
 node_expansion_engine #(.SLOTS(SLOTS),.TX_BITS(TX_BITS),.GEN_BITS(GEN_BITS),.FRAMES(256),.INDEX_BITS(8),.HASH_BITS(8)) dut(.*);
 reg inject_graph=0,inject_design=0,inject_design_b=0,inject_pager=0,inject_pager_b=0;
 integer g_reads,g_writes,g_rbeats,g_wbeats,g_bs;
 axi_file_memory #(.ADDR_BITS(64),.READ_ONLY(1),.MAX_BEATS(1),.TAG("graph")) mem_g(
  .clk(clk),
  .rst(rst),
  .base0(g_cfg_offsets_base),
  .base1(g_cfg_edges_base),
  .base2(g_cfg_attrs_base),
  .size0(64'd36356096),
  .size1(64'd161878144),
  .size2(64'd290848320),
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
 axi_file_memory #(.ADDR_BITS(64),.READ_ONLY(0),.MAX_BEATS(1),.TAG("design")) mem_d(
  .clk(clk),
  .rst(rst),
  .base0(d_cfg_base),
  .base1(64'd0),
  .base2(64'd0),
  .size0(64'd145424192),
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
 integer p_reads,p_writes,p_rbeats,p_wbeats,p_bs;
 axi_file_memory #(.ADDR_BITS(32),.READ_ONLY(0),.MAX_BEATS(3),.TAG("labels")) mem_p(
  .clk(clk),
  .rst(rst),
  .base0(64'd0),
  .base1(64'd0),
  .base2(64'd0),
  .size0(64'd49152),
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
 integer fd_vec,fd_out,fd_attrs,rc,k,j,nread,cycles=0,expansions=0,children=0,hits=0,host_blocks=0,native_reads=0,services=0,builds=0,checkpoints=0;
 integer golden_count=0;reg[31:0]golden_node[0:1023];reg[159:0]golden_value[0:1023];
 reg[20:0]bound_page[0:31];reg[31:0]bound_valid=0;reg native_pending=0;integer pending_op,pending_slot,pending_node;reg[159:0]pending_value;reg pending_present;
 string vecpath,outpath,attrpath,command;
 reg[7:0]attrbytes[0:31];reg[255:0]expected_attrs;
 integer cookie,parent,prune,laguna,hit,raw_count,nchildren,position,node,control_op,control_query,control_price,field,limit=0;
 reg[31:0]mask,value;reg[164:0]held_result;reg[351:0]held_child;
 function integer lookup(input[31:0]id);integer i;begin lookup=-1;for(i=0;i<golden_count;i=i+1)if(golden_node[i]==id)lookup=i;end endfunction
 always @(posedge clk)begin
  cycles<=cycles+1;if(cycles>100000000)$fatal(1,"watchdog");
  if(rst)begin native_pending<=0;bound_valid<=0;end
  else begin
   if(fault)$fatal(1,"unexpected expansion fault cookie=%0d state=%0d action=%0d status=%0d detail=%0d gf=%b df=%b pf=%b bf=%b unexpected=%b",expand_cookie,dut.controller.state,dut.controller.action,result_status,result_detail,dut.g_fault,dut.d_fault,dut.p_fault,dut.b_fault,dut.controller.unexpected);
   if(busy)begin
    if(host_ctrl_ready||host_io_ready||expand_ready)$fatal(1,"host admitted during expansion");
    if(host_ctrl_valid&&host_io_valid)host_blocks=host_blocks+1;
   end
   if(dut.b_build_valid&&dut.b_build_ready)builds=builds+1;
   if(dut.b_svc_valid&&dut.b_svc_ready)begin services=services+1;$fdisplay(fd_out,"S %0d %0d %0d %0d %0d",dut.b_svc_generation,dut.b_svc_parent,dut.b_svc_position,dut.b_svc_phase,dut.b_svc_node);end
   if(dut.b_svc_reply_valid&&dut.b_svc_reply_ready)$fdisplay(fd_out,"T %0d %0d %0d %0d %0d %0d %0d",dut.b_svc_reply_generation,dut.b_svc_reply_parent,dut.b_svc_reply_position,dut.b_svc_reply_phase,dut.b_svc_reply_node,dut.b_svc_value,dut.b_svc_aux);
   if(dut.pager.native_cmd_valid&&dut.pager.native_cmd_ready)begin
    if(native_pending)$fatal(1,"native overlap");native_pending<=1;pending_op=dut.pager.native_cmd_op;pending_slot=dut.pager.native_cmd_slot;
    if(pending_op==2)begin
     if(!bound_valid[pending_slot])$fatal(1,"native read unbound");pending_node=bound_page[pending_slot]*8+dut.pager.native_cmd_offset;j=lookup(pending_node);
     pending_present=j>=0;pending_value=j>=0?golden_value[j]:160'b0;
    end
    if(pending_op==1)bound_page[pending_slot]<=dut.pager.native_cmd_page;
   end
   if(dut.pager.native_rsp_valid&&dut.pager.native_rsp_ready)begin
    if(!native_pending)$fatal(1,"native unowned");native_pending<=0;
    if(dut.pager.native_rsp_status==0)begin
     if(pending_op==1)bound_valid[pending_slot]<=1;
     if(pending_op==4)bound_valid[pending_slot]<=0;
     if(pending_op==12)begin if(bound_valid!=0)$fatal(1,"checkpoint bound slots");checkpoints=checkpoints+1;end
    end
    if(pending_op==2)begin
     if(dut.pager.native_rsp_status!=0||dut.pager.native_rsp_payload!==pending_value||dut.pager.native_rsp_present!==pending_present)$fatal(1,"native label mismatch node=%0d expected=%h got=%h present=%b/%b",pending_node,pending_value,dut.pager.native_rsp_payload,pending_present,dut.pager.native_rsp_present);
     native_reads=native_reads+1;
    end
   end
  end
 end
 task control(input integer op,q,p);
  begin
   @(negedge clk);host_ctrl_op=op;host_ctrl_query=q;host_ctrl_price=p;host_ctrl_valid=1;
   wait(host_ctrl_ready);@(posedge clk);@(negedge clk);host_ctrl_valid=0;wait(host_ctrl_rsp_valid);@(negedge clk);
   if(host_ctrl_status!=0)$fatal(1,"control %d/%d",op,host_ctrl_status);
   repeat(2)@(negedge clk);host_ctrl_rsp_ready=1;@(negedge clk);host_ctrl_rsp_ready=0;
   if(op==0)golden_count=0;
   $fdisplay(fd_out,"Q %0d %0d %0d",op,q,p);
  end
 endtask
 task write_label(input integer n,f,input[31:0]v);
  integer gi;
  begin
   @(negedge clk);host_io_write=1;host_io_node=n;host_io_field=f;host_io_value=v;host_io_valid=1;
   wait(host_io_ready);@(posedge clk);@(negedge clk);host_io_valid=0;wait(host_io_rsp_valid);@(negedge clk);
   if(host_io_status!=0)$fatal(1,"label write");host_io_rsp_ready=1;@(negedge clk);host_io_rsp_ready=0;
   gi=lookup(n);if(gi<0)begin gi=golden_count;golden_count=golden_count+1;if(golden_count>1024)$fatal(1,"golden capacity");golden_node[gi]=n;golden_value[gi]=0;end
   golden_value[gi][f*32+:32]=v;$fdisplay(fd_out,"L %0d %0d %0d",n,f,v);
  end
 endtask
 initial begin
  if(!$value$plusargs("vectors=%s",vecpath)||!$value$plusargs("output=%s",outpath)||!$value$plusargs("attrs=%s",attrpath))$fatal(1,"TB paths");rc=$value$plusargs("limit=%d",limit);
  fd_vec=$fopen(vecpath,"r");fd_out=$fopen(outpath,"w");fd_attrs=$fopen(attrpath,"rb");if(!fd_vec||!fd_out||!fd_attrs)$fatal(1,"TB opens");
  rst=1;repeat(5)@(negedge clk);rst=0;
  g_cfg_offsets_base=64'h1fffff000;g_cfg_edges_base=64'h10fffff000;g_cfg_attrs_base=64'h20fffff000;g_cfg_nodes=9089009;g_cfg_edges=40469536;
  d_cfg_base=64'h31fffff000;d_cfg_nodes=9089009;
  @(negedge clk);g_cfg_valid=1;d_cfg_valid=1;wait(g_cfg_ready&&d_cfg_ready);@(posedge clk);@(negedge clk);g_cfg_valid=0;d_cfg_valid=0;
  wait(g_cfg_rsp_valid&&d_cfg_rsp_valid);@(negedge clk);if(g_cfg_status||d_cfg_status)$fatal(1,"configure");g_cfg_rsp_ready=1;d_cfg_rsp_ready=1;@(negedge clk);g_cfg_rsp_ready=0;d_cfg_rsp_ready=0;
  while(!$feof(fd_vec)&&(limit==0||expansions<limit))begin
   rc=$fscanf(fd_vec,"%s",command);if(rc!=1)$fatal(1,"command parse");
   if(command=="Q")begin rc=$fscanf(fd_vec,"%d %d %d\n",control_op,control_query,control_price);if(rc!=3)$fatal(1,"Q parse");control(control_op,control_query,control_price);end
   else if(command=="L")begin rc=$fscanf(fd_vec,"%d %d %d\n",node,field,value);if(rc!=3)$fatal(1,"L parse");write_label(node,field,value);end
   else if(command=="E")begin
    rc=$fscanf(fd_vec,"%d %d %d %d %d %d %d %d\n",cookie,parent,prune,laguna,hit,raw_count,mask,nchildren);if(rc!=8)$fatal(1,"E parse");
    @(negedge clk);expand_cookie=cookie;expand_parent=parent;expand_prune=prune;expand_has_laguna=laguna;expand_valid=1;
    wait(expand_ready);@(posedge clk);@(negedge clk);expand_valid=0;
    // Attempt both forbidden host paths throughout META/CLAIM/build/replay/result.
    host_ctrl_valid=1;host_ctrl_op=2;host_ctrl_query=p_active_query;host_ctrl_price=p_active_price;
    host_io_valid=1;host_io_node=parent;host_io_field=2;host_io_value=32'hbadabcde;host_io_write=1;
    for(k=0;k<nchildren;k=k+1)begin
     rc=$fscanf(fd_vec,"%s %d %d\n",command,position,node);if(rc!=3||command!="C")$fatal(1,"C parse");
     rc=$fseek(fd_attrs,node*32,0);if(rc!=0)$fatal(1,"attr seek");nread=$fread(attrbytes,fd_attrs);if(nread!=32)$fatal(1,"attr read");expected_attrs=0;for(j=0;j<32;j=j+1)expected_attrs[j*8+:8]=attrbytes[j];
     wait(out_valid);@(negedge clk);
     if(out_node!=node||out_position!=position||out_sequence!=k||out_attrs!==expected_attrs)$fatal(1,"child cookie=%0d seq=%0d node=%0d/%0d pos=%0d/%0d",cookie,k,out_node,node,out_position,position);
     held_child={out_node,out_position,out_sequence,out_attrs};repeat(3)begin @(negedge clk);if(!out_valid||{out_node,out_position,out_sequence,out_attrs}!==held_child)$fatal(1,"out unstable");end
     $fdisplay(fd_out,"C %0d %0d %0d %064h",cookie,position,node,out_attrs);out_ready=1;@(negedge clk);out_ready=0;children=children+1;
    end
    wait(result_valid);@(negedge clk);
    if(result_status||result_cookie!=cookie||result_raw_count!=raw_count||result_mask!=mask||result_count!=nchildren||result_hit!=hit)$fatal(1,"result cookie=%0d st=%0d count=%0d/%0d raw=%0d/%0d mask=%h/%h hit=%b/%0d",cookie,result_status,result_count,nchildren,result_raw_count,raw_count,result_mask,mask,result_hit,hit);
    held_result={result_status,result_detail,result_cookie,result_count,result_raw_count,result_mask,result_hit};repeat(3)begin @(negedge clk);if(!result_valid||{result_status,result_detail,result_cookie,result_count,result_raw_count,result_mask,result_hit}!==held_result)$fatal(1,"result unstable");end
    $fdisplay(fd_out,"E %0d %0d %0d %0d %0d",cookie,parent,result_hit,result_mask,result_count);result_ready=1;@(negedge clk);result_ready=0;host_ctrl_valid=0;host_io_valid=0;expansions=expansions+1;hits=hits+hit;
   end else $fatal(1,"unknown command %s",command);
  end
  if(g_reads!=g_rbeats||d_reads!=d_rbeats||d_writes!=d_bs||p_writes!=p_bs||page_leases_dummy())$fatal(1,"outstanding memory");
  $fflush(fd_out);$fclose(fd_out);
  $display("EXPANSION_PASS expansions=%0d hits=%0d children=%0d builds=%0d services=%0d native_reads=%0d checkpoints=%0d host_blocks=%0d graph_reads=%0d design_reads=%0d design_writes=%0d label_reads=%0d label_writes=%0d cycles=%0d",expansions,hits,children,builds,services,native_reads,checkpoints,host_blocks,g_reads,d_reads,d_writes,p_reads,p_writes,cycles);$finish;
 end
 function page_leases_dummy;begin page_leases_dummy=dut.p_page_leases!=0||dut.p_memory_leases!=0||dut.d_claim_active;end endfunction

endmodule
