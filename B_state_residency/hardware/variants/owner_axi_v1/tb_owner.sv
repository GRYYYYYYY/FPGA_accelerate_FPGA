`timescale 1ns/1ps
module tb_owner;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,abort=0,cfg_valid=0,cfg_rsp_ready=1,req_valid=0,rsp_ready=0;
 wire cfg_ready,cfg_rsp_valid,configured,req_ready,rsp_valid,fault,busy;
 wire[2:0]cfg_status;wire[3:0]rsp_status;
 reg[2:0]req_op=0;reg[31:0]req_cookie=0,req_node=0,req_net=0;
 wire[31:0]rsp_cookie,rsp_count,rsp_occupancy;wire rsp_will_overuse;
 wire[63:0]m_araddr,m_awaddr;wire[7:0]m_arlen,m_awlen;wire[2:0]m_arsize,m_awsize;wire[1:0]m_arburst,m_awburst;wire[3:0]m_arid,m_awid,m_rid,m_bid;
 wire m_arvalid,m_arready,m_rvalid,m_rready,m_rlast,m_awvalid,m_awready,m_wvalid,m_wready,m_wlast,m_bvalid,m_bready;
 wire[511:0]m_rdata,m_wdata;wire[63:0]m_wstrb;wire[1:0]m_rresp,m_bresp;
 integer reads,writes,rbeats,wbeats,bresponses;
 localparam[63:0]BASE=64'h1fffff000;
 owner_state_store dut(.clk(clk),.rst(rst),.abort(abort),.cfg_valid(cfg_valid),.cfg_ready(cfg_ready),.cfg_primary(BASE),.cfg_pool(BASE+4096),.cfg_allocator(BASE+12288),.cfg_nodes(32'd128),.cfg_capacity(32'd256),.*);
 axi_file_memory #(.MAX_BEATS(1),.TAG("owner")) memory(.clk(clk),.rst(rst),.base0(BASE),.base1(64'd0),.base2(64'd0),.size0(64'd16384),.size1(64'd0),.size2(64'd0),
  .araddr(m_araddr),.arlen(m_arlen),.arsize(m_arsize),.arburst(m_arburst),.arid(m_arid),.arvalid(m_arvalid),.arready(m_arready),.rdata(m_rdata),.rid(m_rid),.rresp(m_rresp),.rlast(m_rlast),.rvalid(m_rvalid),.rready(m_rready),
  .awaddr(m_awaddr),.awlen(m_awlen),.awsize(m_awsize),.awburst(m_awburst),.awid(m_awid),.awvalid(m_awvalid),.awready(m_awready),.wdata(m_wdata),.wstrb(m_wstrb),.wlast(m_wlast),.wvalid(m_wvalid),.wready(m_wready),.bid(m_bid),.bresp(m_bresp),.bvalid(m_bvalid),.bready(m_bready),
  .inject_r(1'b0),.inject_b(1'b0),.*);
 integer fd,rc,seq,operation,status,count,occ,overuse,record_writes,n,initial_b,delay,case_count=0,cycles=0;
 reg[31:0]node,net;reg[100:0]held_response;
 string vectors;integer observed;
 reg stalled_ar=0,stalled_aw=0,stalled_w=0;reg[63:0]held_ar,held_aw,held_strb;reg[511:0]held_w;
 always @(posedge clk)begin
  cycles=cycles+1;
  if(cycles>20000000)$fatal(1,"watchdog case=%0d state=%0d",case_count,dut.state);
  if(!rst)begin
   if(stalled_ar&&(!m_arvalid||m_araddr!==held_ar))$fatal(1,"AR stability");
   if(stalled_aw&&(!m_awvalid||m_awaddr!==held_aw))$fatal(1,"AW stability");
   if(stalled_w&&(!m_wvalid||m_wdata!==held_w||m_wstrb!==held_strb))$fatal(1,"W stability");
  end
  stalled_ar=!rst&&m_arvalid&&!m_arready;held_ar=m_araddr;
  stalled_aw=!rst&&m_awvalid&&!m_awready;held_aw=m_awaddr;
  stalled_w=!rst&&m_wvalid&&!m_wready;held_w=m_wdata;held_strb=m_wstrb;
 end
 initial begin
  if(!$value$plusargs("vectors=%s",vectors))$fatal(1,"vectors");fd=$fopen(vectors,"r");
  if(!$value$plusargs("observed=%s",vectors))$fatal(1,"observed");observed=$fopen(vectors,"w");
  if(!fd||!observed)$fatal(1,"open vectors");
  repeat(4)@(negedge clk);rst=0;
  @(negedge clk);cfg_valid=1;while(!cfg_ready)@(negedge clk);
  @(negedge clk);cfg_valid=0;while(!cfg_rsp_valid)@(negedge clk);
  if(cfg_status!=0||!configured)$fatal(1,"configuration");
  @(negedge clk);
  while(!$feof(fd))begin
   rc=$fscanf(fd,"%d %d %h %h %d %d %d %d %d\n",seq,operation,node,net,status,count,occ,overuse,record_writes);
   if(rc!=9)$fatal(1,"vector format %0d",rc);
   initial_b=bresponses;req_cookie=seq;req_node=node;req_net=net;req_op=operation;req_valid=1;
   while(!req_ready)@(negedge clk);
   @(negedge clk);req_valid=0;
   while(!rsp_valid)begin @(negedge clk);if(fault)$fatal(1,"fault case=%0d state=%0d",seq,dut.state);end
   if(fault||rsp_status!==status||rsp_cookie!==seq||rsp_count!==count||rsp_occupancy!==occ||rsp_will_overuse!==overuse[0])$fatal(1,"result case=%0d status=%0d/%0d count=%0d/%0d occ=%0d/%0d",seq,rsp_status,status,rsp_count,count,rsp_occupancy,occ);
   if(bresponses-initial_b!=record_writes)$fatal(1,"early/incorrect B case=%0d got=%0d expected=%0d",seq,bresponses-initial_b,record_writes);
   held_response={rsp_status,rsp_cookie,rsp_count,rsp_occupancy,rsp_will_overuse};delay=seq%7;
   repeat(delay)begin @(negedge clk);if(!rsp_valid||req_ready||{rsp_status,rsp_cookie,rsp_count,rsp_occupancy,rsp_will_overuse}!==held_response)$fatal(1,"response stability");end
   $fdisplay(observed,"%0d %0d %0d %0d %0d %0d",seq,rsp_status,rsp_count,rsp_occupancy,rsp_will_overuse,bresponses-initial_b);
   rsp_ready=1;@(negedge clk);rsp_ready=0;case_count=case_count+1;
  end
  $fclose(observed);$display("OWNER_AXI_PASS commands=%0d reads=%0d writes=%0d bresponses=%0d cycles=%0d",case_count,reads,writes,bresponses,cycles);$finish;
 end
endmodule
