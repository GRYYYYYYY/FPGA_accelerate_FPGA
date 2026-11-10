`timescale 1ns/1ps
module tb_cost_service;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,abort=0,active=1,req_valid=0,rsp_ready=0;
 reg [1:0] active_query=0,req_query=0;reg [3:0] active_price=0,req_price=0;
 reg [735:0] req_words=0;reg [31:0] req_cookie=0;
 wire req_ready,rsp_valid,busy,fault;wire [159:0] rsp_words;
 wire [31:0] rsp_cookie;wire [1:0] rsp_query,rsp_status;wire [3:0] rsp_price;
 cost_service dut(.*);
 reg [735:0] inputs[0:21575];reg [159:0] golden[0:21575];integer groups[0:21575];
 integer f,trace,rc,i,j,k,idx=0,serial=0,accepted=0,responded=0,resets=0;
 integer cycles=0,start_cycle,max_latency=0,max_index=0,latency;
 integer early_writes=0,all_writes=0,completions=0;
 reg [31:0] held_cookie;reg [1:0] held_query;reg [3:0] held_price;
 reg [159:0] held_words;
 always @(posedge clk)begin
  cycles=cycles+1;
  if(cycles>18000000)$fatal(1,"watchdog");
  if(!rst)begin
   if(req_valid&&req_ready)begin
    accepted=accepted+1;
    $fdisplay(trace,"Q %0d %0d %0d %0d %0d",req_cookie,idx,req_query,req_price,active);
   end
   if(rsp_valid&&rsp_ready)begin
    responded=responded+1;
    $fdisplay(trace,"R %0d %0d %0d %0d %08x %08x %08x %08x %08x",
     rsp_cookie,rsp_query,rsp_price,rsp_status,rsp_words[31:0],rsp_words[63:32],
     rsp_words[95:64],rsp_words[127:96],rsp_words[159:128]);
   end
   if(dut.ap_done)completions=completions+1;
   if(dut.oc0&&dut.ow0)begin all_writes=all_writes+1;if(!dut.ap_ready)early_writes=early_writes+1;end
   if(dut.oc1&&dut.ow1)begin all_writes=all_writes+1;if(!dut.ap_ready)early_writes=early_writes+1;end
  end
 end
 task cold_reset;
 begin
  @(negedge clk);rst=1;abort=0;req_valid=0;rsp_ready=0;active=1;
  resets=resets+1;$fdisplay(trace,"RESET");
  repeat(2)@(posedge clk);
  @(negedge clk);rst=0;
  repeat(3)begin @(negedge clk);if(fault||rsp_valid)$fatal(1,"stale after reset");end
  if(!req_ready)$fatal(1,"not idle after reset");
 end endtask
 task send(input integer n);
 begin
  @(negedge clk);while(!req_ready)@(negedge clk);
  if(fault)$fatal(1,"fault before send %0d",n);
  idx=n;serial=serial+1;req_cookie=serial;req_words=inputs[n];
  req_query=active_query;req_price=active_price;req_valid=1;
  held_cookie=req_cookie;held_query=req_query;held_price=req_price;start_cycle=cycles;
  @(posedge clk);#1;req_valid=0;
  // Deliberately destroy live buses after handshake: only the snapshot is valid.
  req_words=~req_words;req_cookie=~req_cookie;req_query=~req_query;req_price=~req_price;
 end endtask
 task receive(input integer n,input integer stall,input integer status);
 begin
  @(negedge clk);while(!rsp_valid)begin if(fault)$fatal(1,"fault case=%0d cycle=%0d",n,cycles);@(negedge clk);end
  latency=cycles-start_cycle;
  if(status==0&&latency>max_latency)begin max_latency=latency;max_index=n;end
  if(fault||rsp_cookie!==held_cookie||rsp_query!==held_query||rsp_price!==held_price||rsp_status!==status)
   $fatal(1,"response ownership/status case=%0d",n);
  if(status==0&&rsp_words!==golden[n])$fatal(1,"numerical case=%0d expected=%040x got=%040x",n,golden[n],rsp_words);
  if(status!=0&&rsp_words!==0)$fatal(1,"rejection payload");
  held_words=rsp_words;
  repeat(stall)begin
   @(negedge clk);
   if(!rsp_valid||rsp_words!==held_words||rsp_cookie!==held_cookie||rsp_query!==held_query||
      rsp_price!==held_price||rsp_status!==status||req_ready||fault)$fatal(1,"stalled reply changed");
  end
  rsp_ready=1;@(posedge clk);#1;rsp_ready=0;
 end endtask
 initial begin
  f=$fopen("vectors.txt","r");trace=$fopen("transactions.txt","w");
  if(!f||!trace)$fatal(1,"open inputs/log");
  for(i=0;i<21576;i=i+1)begin
   rc=$fscanf(f,"%d",groups[i]);if(rc!=1)$fatal(1,"group parse");
   for(j=0;j<23;j=j+1)begin rc=$fscanf(f,"%h",inputs[i][j*32+:32]);if(rc!=1)$fatal(1,"input parse");end
   for(j=0;j<5;j=j+1)begin rc=$fscanf(f,"%h",golden[i][j*32+:32]);if(rc!=1)$fatal(1,"golden parse");end
  end
  $fclose(f);cold_reset();
  for(i=0;i<21576;i=i+1)begin
   active_query=i%4;active_price=(i/4)%16;send(i);receive(i,i%7,0);
   if(i%4096==0)$display("COST_PROGRESS %0d",i);
  end
  // Inactive and wrong-owner requests must not launch arithmetic.
  active=0;send(0);receive(0,4,1);active=1;
  @(negedge clk);req_cookie=serial+1;serial=serial+1;req_query=active_query^1;
  req_price=active_price;req_words=inputs[0];req_valid=1;idx=0;
  held_cookie=req_cookie;held_query=req_query;held_price=req_price;start_cycle=cycles;
  @(posedge clk);#1;req_valid=0;receive(0,4,2);
  $display("COST_MAX latency=%0d index=%0d",max_latency,max_index);
  // Every cycle through the longest observed call, plus pending-response interval.
  k=max_index;
  for(i=0;i<720;i=i+1)begin
   send(k);repeat(i)@(posedge clk);cold_reset();send((i*31)%21576);receive((i*31)%21576,2,0);
  end
  // Backpressure can exceed computation timeout without triggering a timeout.
  send(0);receive(0,1100,0);
  $fdisplay(trace,"END %0d %0d %0d",accepted,responded,resets);$fclose(trace);
  if(early_writes<21576*4)$fatal(1,"early writes not observed");
  $display("COST_SERVICE_PASS vectors=21576 reset_offsets=720 accepted=%0d responded=%0d resets=%0d early_writes=%0d all_writes=%0d completions=%0d cycles=%0d",accepted,responded,resets,early_writes,all_writes,completions,cycles);
  $finish;
 end
endmodule
