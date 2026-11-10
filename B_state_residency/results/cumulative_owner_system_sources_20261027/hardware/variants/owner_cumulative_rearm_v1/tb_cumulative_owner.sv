`timescale 1ns/1ps
module tb_cumulative_owner;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,lease=1,source_drained=1,source_healthy=1,source_protocol_ok=1;
 reg obs_awvalid=0,obs_bvalid=0;wire obs_awready=1,obs_bready=1;
 reg[63:0]obs_awaddr=0;reg[7:0]obs_awlen=0;reg[1:0]obs_bresp=0;
 reg[3:0]obs_bid=0,obs_awid=0;reg[2:0]obs_awsize=6;reg[1:0]obs_awburst=1;
 reg cmd_valid=0,rsp_ready=0;wire cmd_ready,busy,rsp_valid,receipt_valid,bound,data_error,coverage_error,manifest_ready,release_blocked;
 reg[1:0]cmd_op=0;reg[63:0]source_base='h1000,destination_base='h4000,span_bytes=512;
 reg[63:0]cmd_design=7,cmd_baseline=11,cmd_generation=2,cmd_checkpoint=17,bank0_base='h4000,bank1_base='h8000;
 reg[63:0]active_destination='hc000,active_generation=1;
 wire[63:0]generation_floor,checkpoint_floor,receipt_design,receipt_baseline,receipt_generation,receipt_checkpoint,receipt_destination;
 reg[63:0]publish_design=7,publish_baseline=11,publish_generation=2,publish_checkpoint=18,publish_destination='h4000;
 reg[31:0]cmd_cookie='h12345678;wire[31:0]rsp_cookie,dirty_count,verified_count;wire[3:0]status;
 wire[63:0]m_araddr,m_awaddr;wire m_arvalid,m_arready,m_rvalid,m_rready,m_rlast,m_awvalid,m_awready,m_wvalid,m_wready,m_bvalid,m_bready;
 wire[511:0]m_rdata,m_wdata;wire[3:0]m_rid,m_bid;wire[1:0]m_rresp,m_bresp;
 reg inject_r=0,inject_b=0;integer reads,writes,rbeats,wbeats,bresponses,checks=0,before_reads,before_writes;
 integer trace,cycle=0;string tracepath;
 cumulative_owner_snapshot #(.MAX_DIRTY(4)) dut(.*);
 axi_file_memory #(.READ_ONLY(0),.MAX_BEATS(1),.SECONDARY_WRITABLE(1),.TERTIARY_WRITABLE(1),.TAG("copy")) mem(
 .clk(clk),.rst(rst),.base0(64'h1000),.base1(64'h4000),.base2(64'h8000),.size0(64'd512),.size1(64'd512),.size2(64'd512),
 .araddr(m_araddr),.arlen(8'd0),.arsize(3'd6),.arburst(2'd1),.arid(4'd0),.arvalid(m_arvalid),.arready(m_arready),.rdata(m_rdata),.rid(m_rid),.rresp(m_rresp),.rlast(m_rlast),.rvalid(m_rvalid),.rready(m_rready),
 .awaddr(m_awaddr),.awlen(8'd0),.awsize(3'd6),.awburst(2'd1),.awid(4'd0),.awvalid(m_awvalid),.awready(m_awready),.wdata(m_wdata),.wstrb(64'hffffffffffffffff),.wlast(1'b1),.wvalid(m_wvalid),.wready(m_wready),.bid(m_bid),.bresp(m_bresp),.bvalid(m_bvalid),.bready(m_bready),.inject_r(inject_r),.inject_b(inject_b),.reads(reads),.writes(writes),.rbeats(rbeats),.wbeats(wbeats),.bresponses(bresponses));
 always @(posedge clk)begin
  cycle=cycle+1;
  if(!rst)begin
   if(obs_awvalid)$fdisplay(trace,"AW %0d %h %0d",cycle,obs_awaddr,obs_awlen);
   if(obs_bvalid)$fdisplay(trace,"B %0d %0d %0d",cycle,obs_bresp,obs_bid);
   if(cmd_valid&&cmd_ready)$fdisplay(trace,"CMD %0d %0d %0d %0d %h",cycle,cmd_op,cmd_generation,cmd_checkpoint,destination_base);
   if(manifest_ready&&(!receipt_valid||busy||cmd_valid||!lease||data_error||coverage_error))$fatal(1,"manifest unsafe");
   if(release_blocked!=(busy||cmd_valid))$fatal(1,"release ownership");
  end
 end
 task check(input bit ok,input string why);begin checks=checks+1;if(!ok)$fatal(1,"check %0d: %s",checks,why);end endtask
 task reset_case;begin
  @(negedge clk);rst=1;cmd_valid=0;rsp_ready=0;obs_awvalid=0;obs_bvalid=0;obs_bid=0;obs_awid=0;obs_awsize=6;obs_awburst=1;
  lease=1;source_drained=1;source_healthy=1;source_protocol_ok=1;inject_r=0;inject_b=0;
  source_base='h1000;destination_base='h4000;span_bytes=512;bank0_base='h4000;bank1_base='h8000;
  cmd_design=7;cmd_baseline=11;cmd_generation=2;cmd_checkpoint=17;active_destination='hc000;active_generation=1;
  publish_design=7;publish_baseline=11;publish_generation=2;publish_checkpoint=18;publish_destination='h4000;
  repeat(4)@(negedge clk);rst=0;repeat(2)@(negedge clk);$fdisplay(trace,"RESET %0d",cycle);
 end endtask
 task mark(input integer off,len,resp);begin
  @(negedge clk);obs_awaddr='h1000+off;obs_awlen=len;obs_awvalid=1;
  @(negedge clk);obs_awvalid=0;repeat(len+3)@(negedge clk);obs_bresp=resp;obs_bvalid=1;
  @(negedge clk);obs_bvalid=0;repeat(2)@(negedge clk);
 end endtask
 task launch(input integer op);begin
  @(negedge clk);cmd_op=op;cmd_valid=1;do @(posedge clk);while(!cmd_ready);@(negedge clk);cmd_valid=0;
 end endtask
 task result(input integer expected,n,input bit rec);begin
  wait(rsp_valid);repeat(5)begin @(negedge clk);
   check(rsp_valid&&status==expected&&verified_count==n&&receipt_valid==rec&&rsp_cookie=='h12345678&&!cmd_ready&&!manifest_ready,"held response");
  end
  $fdisplay(trace,"RESULT %0d %0d %0d %0d %0d %0d %0d %0d %0d",cycle,status,verified_count,receipt_valid,dirty_count,data_error,coverage_error,generation_floor,checkpoint_floor);
  rsp_ready=1;@(negedge clk);rsp_ready=0;wait(!busy);
 end endtask
 task bind_ok;begin launch(0);result(0,0,0);check(bound&&generation_floor==1&&dirty_count==0,"bind once");end endtask
 initial begin
  if(!$value$plusargs("trace=%s",tracepath))$fatal(1,"trace path");trace=$fopen(tracepath,"w");
  reset_case;bind_ok;
  mark(0,1,0);mark(0,0,0);check(dirty_count==2&&!data_error&&!coverage_error,"dedup");
  cmd_checkpoint=18;launch(2);result(0,2,1);check(manifest_ready,"exact consumed receipt");
  publish_generation=3;#1;check(!manifest_ready,"wrong generation");publish_generation=2;
  publish_destination='h8000;#1;check(!manifest_ready,"wrong bank");publish_destination='h4000;
  publish_baseline=12;#1;check(!manifest_ready,"wrong baseline");publish_baseline=11;
  publish_design=8;#1;check(!manifest_ready,"wrong design");publish_design=7;
  publish_checkpoint=19;#1;check(!manifest_ready,"wrong checkpoint");publish_checkpoint=18;
  active_destination='h4000;active_generation=2;#1;check(!manifest_ready,"published bank immutable");
  mark(128,0,2);check(data_error&&!coverage_error&&dirty_count==3&&!receipt_valid,"tracked B fault");
  cmd_generation=3;cmd_checkpoint=19;destination_base='h8000;before_reads=reads;launch(2);result(3,0,0);check(reads==before_reads,"data poison blocks copy");
  source_healthy=0;launch(1);result(1,0,0);check(data_error&&dirty_count==3,"unhealthy rearm refused");source_healthy=1;
  source_drained=0;launch(1);result(1,0,0);check(data_error,"undrained rearm refused");source_drained=1;
  lease=0;launch(1);result(1,0,0);check(data_error,"no lease rearm refused");lease=1;
  launch(1);result(0,0,0);check(!data_error&&dirty_count==3&&generation_floor==2,"rearm preserves cumulative G1 dirty/floor");
  cmd_generation=2;launch(2);result(9,0,0);cmd_generation=3;
  destination_base='h4000;launch(2);result(4,0,0);destination_base='h8000;
  cmd_baseline=12;launch(2);result(4,0,0);cmd_baseline=11;
  source_base='h1040;launch(2);result(4,0,0);source_base='h1000;
  bank1_base='h9000;launch(2);result(4,0,0);bank1_base='h8000;
  cmd_checkpoint=18;launch(2);result(9,0,0);cmd_checkpoint=19;
  launch(2); // pins may change after handshake; the receipt and addresses stay latched
  cmd_design=0;cmd_baseline=0;source_base=0;span_bytes=0;destination_base=0;cmd_generation=99;cmd_checkpoint=99;
  result(0,3,1);
  check(receipt_design==7&&receipt_baseline==11&&receipt_generation==3&&receipt_checkpoint==19&&receipt_destination=='h8000,"latched receipt");
  publish_generation=3;publish_checkpoint=19;publish_destination='h8000;#1;check(manifest_ready,"G3 receipt matches");
  lease=0;@(negedge clk);check(!manifest_ready&&!receipt_valid,"lease loss revokes receipt");
  // Coverage loss cannot be cleared by rearm or by bind.
  reset_case;bind_ok;mark(0,4,0);check(coverage_error&&dirty_count==4,"capacity coverage loss");
  launch(1);result(3,0,0);check(coverage_error&&dirty_count==4,"no coverage rearm");launch(0);result(3,0,0);
  reset_case;bind_ok;obs_bvalid=1;@(negedge clk);obs_bvalid=0;launch(1);result(3,0,0);check(coverage_error,"unknown B is coverage loss");
  reset_case;bind_ok;mark(512,0,2);check(coverage_error&&data_error&&dirty_count==0,"out of span never becomes recoverable B");launch(1);result(3,0,0);
  reset_case;mark(0,0,0);launch(0);result(3,0,0);check(!bound,"writes before bind poison");
  reset_case;bank1_base='h4000;launch(0);result(4,0,0);check(!bound,"overlap bind rejected");
  reset_case;bind_ok;launch(0);result(4,0,0);check(bound,"no rebind");
  reset_case;bind_ok;source_protocol_ok=0;@(negedge clk);source_protocol_ok=1;launch(1);result(3,0,0);check(coverage_error,"external protocol coverage poison");
  reset_case;bind_ok;mark(0,0,0);cmd_checkpoint=18;launch(2);
  do @(posedge clk);while(!(m_arvalid&&m_arready));@(negedge clk);lease=0;before_writes=writes;result(2,0,0);check(writes==before_writes,"cancel drains R no new write");
  lease=1;launch(2);result(9,0,0);check(generation_floor==2,"failed copy consumes generation");
  reset_case;bind_ok;obs_awsize=5;mark(0,0,0);launch(1);result(3,0,0);check(coverage_error,"AW size coverage error");
  reset_case;bind_ok;obs_bid=1;mark(0,0,2);launch(1);result(3,0,0);check(coverage_error&&data_error,"wrong BID not rearmable");
  reset_case;bind_ok;mark(0,0,0);cmd_checkpoint=18;inject_r=1;launch(2);result(5,0,0);check(generation_floor==2,"read failure floor");
  reset_case;bind_ok;mark(0,0,0);cmd_checkpoint=18;inject_b=1;launch(2);result(6,0,0);
  reset_case;bind_ok;mark(0,0,0);cmd_checkpoint=18;launch(2);
  do @(posedge clk);while(!(m_bvalid&&m_bready));@(negedge clk);inject_r=1;result(7,0,0);
  reset_case;bind_ok;mark(0,0,0);cmd_checkpoint=18;launch(2);
  do @(posedge clk);while(!(m_awvalid&&m_awready));@(negedge clk);lease=0;before_writes=bresponses;result(2,0,0);check(bresponses==before_writes+1,"cancel accepted AW drains B");
  reset_case;bind_ok;mark(0,0,0);cmd_checkpoint=18;launch(2);result(0,1,1);
  mark(0,0,0);check(!receipt_valid&&!manifest_ready&&dirty_count==1,"later AW revokes receipt even same dirty line");
  reset_case;span_bytes=16384;bank0_base='h10000;bank1_base='h20000;bind_ok;
  mark(0,255,0);check(coverage_error&&dirty_count==0,"256 beat page crossing detected without width truncation");launch(1);result(3,0,0);
  $display("CUMULATIVE_OWNER_PASS checks=%0d",checks);$fclose(trace);$finish;
 end
 initial begin #2000000;$fatal(1,"cumulative owner watchdog");end
endmodule
