`timescale 1ns/1ps
module tb_baseline;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,cv=0,cp=1,cr=0,qv=0,rr=0,inject=0,badpad=0;
 reg[63:0]cb=64'hb000000000,ce=64'h300010003,qe=64'h300010003;
 reg[31:0]cn=9089009,qn=0;
 wire cy,crv,qy,rv,idle,configured;wire[3:0]cs,rs;wire[31:0]rn;wire[63:0]re;wire[159:0]payload;
 wire[63:0]aa;wire[7:0]al;wire[2:0]az;wire[1:0]ab;wire[3:0]ai;wire av,ay;
 wire[511:0]rd;wire[3:0]ri;wire[1:0]resp;wire last,rvalid,ry;
 integer reads,writes,rbeats,wbeats,breplies,checks=0,holds=0,fd,tf,rc,node,phase=0;reg[159:0]expected;
 string vectors,trace;
 label_baseline_reader dut(.clk(clk),.rst(rst),.cfg_valid(cv),.cfg_ready(cy),.cfg_permit(cp),.cfg_base(cb),.cfg_epoch(ce),.cfg_count(cn),.cfg_rsp_valid(crv),.cfg_rsp_ready(cr),.cfg_status(cs),.req_valid(qv),.req_ready(qy),.req_node(qn),.req_epoch(qe),.rsp_valid(rv),.rsp_ready(rr),.rsp_status(rs),.rsp_node(rn),.rsp_epoch(re),.rsp_payload(payload),.idle(idle),.configured(configured),.araddr(aa),.arlen(al),.arsize(az),.arburst(ab),.arid(ai),.arvalid(av),.arready(ay),.rdata(rd^(badpad?(512'b1<<160):512'b0)),.rresp(resp),.rid(ri),.rlast(last),.rvalid(rvalid),.rready(ry));
 axi_file_memory #(.READ_ONLY(1),.TAG("baseline")) mem(.clk(clk),.rst(rst),.base0(64'hb000000000),.base1(64'b0),.base2(64'b0),.size0(64'd290848320),.size1(64'b0),.size2(64'b0),.araddr(aa),.arlen(al),.arsize(az),.arburst(ab),.arid(ai),.arvalid(av),.arready(ay),.rdata(rd),.rid(ri),.rresp(resp),.rlast(last),.rvalid(rvalid),.rready(ry),.awaddr(64'b0),.awlen(8'b0),.awsize(3'd6),.awburst(2'd1),.awid(4'b0),.awvalid(1'b0),.wdata(512'b0),.wstrb(64'b0),.wlast(1'b0),.wvalid(1'b0),.bready(1'b1),.inject_r(inject),.inject_b(1'b0),.reads(reads),.writes(writes),.rbeats(rbeats),.wbeats(wbeats),.bresponses(breplies));
 task check(input bit ok);begin checks=checks+1;if(!ok)$fatal(1,"baseline check %0d phase%0d",checks,phase);end endtask
 task configure(input integer status);
 begin
  @(negedge clk);cv=1;do @(posedge clk);while(!cy);
  @(negedge clk);cv=0;wait(crv);#1;check(cs==status);
  repeat(4)begin @(posedge clk);#1;check(crv&&cs==status&&!qy&&!cy);holds=holds+1;end
  @(negedge clk);cr=1;@(posedge clk);@(negedge clk);cr=0;
 end endtask
 task query(input integer n,input[63:0]epoch,input integer status,input[159:0]want);
 reg[63:0]saved;integer before_reads;
 begin
  before_reads=reads;@(negedge clk);qn=n;qe=epoch;qv=1;
  do @(posedge clk);while(!qy);
  @(negedge clk);qv=0;qn=32'hffffffff;qe=0;
  // Offer a conflicting configuration while the request is in flight.
  cv=1;cb=64'hc000000000;cn=2;ce=77;
  while(!rv)begin @(posedge clk);#1;check(!cy);end
  check(rs==status&&rn==n&&re==epoch&&payload==want);
  repeat(5)begin @(posedge clk);#1;check(rv&&rs==status&&payload==want&&!cy&&!qy);holds=holds+1;end
  $fdisplay(tf,"Q %0d %h %0d %040h %0d",n,epoch,status,payload,reads-before_reads);
  @(negedge clk);cv=0;cb=64'hb000000000;cn=9089009;ce=64'h300010003;rr=1;
  @(posedge clk);@(negedge clk);rr=0;
 end endtask
 initial begin
  if(!$value$plusargs("vectors=%s",vectors)||!$value$plusargs("trace=%s",trace))$fatal(1,"paths");
  fd=$fopen(vectors,"r");tf=$fopen(trace,"w");if(!fd||!tf)$fatal(1,"open");
  repeat(5)@(posedge clk);@(negedge clk);rst=0;
  query(0,64'h300010003,5,0);check(reads==0);
  phase=1;cp=0;configure(5);check(!configured);cp=1;
  cb=64'hb000000020;configure(2);check(!configured);cb=64'hb000000000;
  cn=0;configure(2);cn=9089009;
  cb=64'hffffffffffffffc0;configure(2);cb=64'hb000000000;
  ce=0;configure(2);ce=64'h300010003;
  phase=2;configure(0);check(configured);
  while(!$feof(fd))begin
   rc=$fscanf(fd,"%d %h\n",node,expected);
   if(rc==2)query(node,64'h300010003,0,expected);
   else if(!$feof(fd))$fatal(1,"vector syntax");
  end
  phase=3;query(9089009,64'h300010003,1,0);query(0,64'h300010004,5,0);
  cp=0;configure(5);cp=1; // rejected configuration preserves the old immutable binding
  query(0,64'h300010003,0,160'h000000007f800000ffffffff000000007f800000); // replaced by runner using real CPU words
  phase=4;inject=1;query(0,64'h300010003,3,0);inject=0;
  badpad=1;query(0,64'h300010003,4,0);badpad=0;
  check(writes==0&&wbeats==0&&breplies==0&&reads==rbeats);
  $fdisplay(tf,"PASS %0d %0d %0d",checks,holds,reads);$fclose(tf);
  $display("LABEL_BASELINE_PASS checks=%0d holds=%0d reads=%0d",checks,holds,reads);$finish;
 end
 initial begin #2000000;$fatal(1,"watchdog phase%0d",phase);end
endmodule
