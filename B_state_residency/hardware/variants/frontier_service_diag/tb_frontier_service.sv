`timescale 1ns/1ps
module tb_frontier_service;
reg clk=0;always #5 clk=~clk;
reg rst=1,abort=0,req_valid=0,rsp_ready=0;
reg [31:0] req_op=0,req_key_bits=0,req_id=0,req_cookie=0;
reg [1:0] req_query=1;reg [3:0] req_price=3;
wire req_ready,rsp_valid,initialized,active,busy,fault;
wire [31:0] rsp_status,rsp_key_bits,rsp_id,rsp_size,rsp_cookie,heap_size;
wire [1:0] rsp_query,owner_query;wire [3:0] rsp_price,owner_price;
frontier_service dut(.*);
integer calls=0,resets=0,i,j,delay_cycles,fd,accepted=0,responded=0,hls_calls=0,cycles=0;
reg held=0;reg [165:0] packet;
wire [165:0] live_packet={rsp_price,rsp_query,rsp_cookie,rsp_size,rsp_id,rsp_key_bits,rsp_status};
reg [31:0] special[0:9];
always @(posedge clk)begin
 cycles<=cycles+1;
 if($time<300) $display("DIAG t=%0t rst=%b svc=%d cstate=%d accepted=%b done_seen=%b seen=%h start=%b ready=%b done=%b idle=%b valid=%h fault=%b stopped=%b bad=%b data=%h",$time,rst,dut.state,dut.collector.state,dut.collector.accepted,dut.collector.done_seen,dut.collector.seen,dut.ap_start,dut.ap_ready,dut.ap_done,dut.ap_idle,dut.hls_valid,fault,dut.stopped,dut.bad_reply,dut.reply_data);
 if(rst)held<=0;
 else begin
  if(held&&(!rsp_valid||live_packet!==packet))$fatal(1,"unstable stalled reply");
  held<=rsp_valid&&!rsp_ready;packet<=live_packet;
  if(!initialized&&(req_ready||rsp_valid||active))$fatal(1,"admission before boot clear");
  if(dut.ap_start&&dut.ap_ready)hls_calls=hls_calls+1;
  if(req_valid&&req_ready)begin
   accepted=accepted+1;
   $fdisplay(fd,"Q %08x %08x %08x %08x %0d %0d",req_op,req_key_bits,req_id,req_cookie,req_query,req_price);
  end
  if(rsp_valid&&rsp_ready)begin
   responded=responded+1;
   $fdisplay(fd,"R %08x %08x %08x %08x %08x %0d %0d",rsp_status,rsp_key_bits,rsp_id,rsp_size,rsp_cookie,rsp_query,rsp_price);
  end
 end
end
initial begin #200000000;$fatal(1,"service watchdog");end
task cold_reset;
begin
 @(negedge clk);rst=1;abort=0;req_valid=0;rsp_ready=0;$fdisplay(fd,"RESET");
 repeat(6)@(negedge clk);rst=0;resets=resets+1;
 wait(initialized||fault);@(negedge clk);
 if(fault||active||heap_size!=0||!req_ready)$fatal(1,"boot clear failed");
 $fdisplay(fd,"BOOT %0d",hls_calls);
 req_query=1;req_price=3;
end endtask
task launch(input [31:0] op,input [31:0] bits,input [31:0] node);
begin
 @(negedge clk);req_op=op;req_key_bits=bits;req_id=node;req_cookie=req_cookie+1;req_valid=1;
 do @(posedge clk);while(!req_ready);
 @(negedge clk);req_valid=0;
end endtask
task collect(input [31:0] status,input [31:0] size);
begin
 wait(rsp_valid||fault);@(negedge clk);
 if(fault||rsp_status!==status||rsp_size!==size||rsp_cookie!==req_cookie||rsp_query!==req_query||rsp_price!==req_price)
  $fatal(1,"bad reply call=%0d op=%0d status=%0d size=%0d want=%0d/%0d fault=%b",calls,req_op,rsp_status,rsp_size,status,size,fault);
 if(heap_size!==size)$fatal(1,"size mirror mismatch");
 repeat(req_cookie%3)@(negedge clk);
 rsp_ready=1;@(negedge clk);rsp_ready=0;calls=calls+1;
end endtask
task call(input [31:0] op,input [31:0] bits,input [31:0] node,input [31:0] status,input [31:0] size);
begin launch(op,bits,node);collect(status,size);end endtask
initial begin
 fd=$fopen("transactions.txt","w");if(!fd)$fatal(1,"trace open");
 special[0]=32'h00000000;special[1]=32'h80000000;special[2]=32'h00000001;special[3]=32'h80000001;
 special[4]=32'h7f800000;special[5]=32'hff800000;special[6]=32'h7fc12345;special[7]=32'hffc54321;
 special[8]=32'h3f800000;special[9]=32'hbf800000;
 cold_reset;
 call(2,0,0,4,0);call(99,0,0,3,0);call(0,0,0,0,0);
 if(!active||owner_query!=1||owner_price!=3)$fatal(1,"owner missing");
 call(0,0,0,6,0);call(2,0,0,1,0);
 req_query=2;call(1,1,1,5,0);req_query=1;req_price=4;call(4,0,0,5,0);req_price=3;
 for(i=0;i<10;i=i+1)begin
  call(1,special[i],32'hf0000000+i,0,1);call(2,0,0,0,0);
  if(rsp_key_bits!==special[i]||rsp_id!==32'hf0000000+i)$fatal(1,"raw payload changed");
 end
 // Actual 65536-entry capacity, decreasing unique positive IEEE keys.
 for(i=0;i<65536;i=i+1)call(1,32'h47800000-i,i,0,i+1);
 call(1,0,32'hffffffff,2,65536);call(3,0,0,0,65536);
 for(i=65535;i>=0;i=i-1)begin
  call(2,0,0,0,i);
  if(rsp_key_bits!==32'h47800000-i||rsp_id!==i)$fatal(1,"heap ordering at %0d",i);
 end
 call(2,0,0,1,0);
 call(1,32'hdeadbeef,55,0,1);call(4,0,0,0,0);
 if(active)$fatal(1,"close did not release");
 req_query=2;req_price=7;call(0,0,0,0,0);call(2,0,0,1,0);call(4,0,0,0,0);
 // Coordinated reset at every cycle offset through OFFER/POLL and held reply.
 for(j=0;j<2;j=j+1)for(delay_cycles=0;delay_cycles<96;delay_cycles=delay_cycles+1)begin
  cold_reset;call(0,0,0,0,0);
  for(i=0;i<16;i=i+1)call(1,32'h40000000-i,i,0,i+1);
  launch(j==0?1:2,32'h3f800000,32'hbadbad00);
  repeat(delay_cycles)@(negedge clk);
  cold_reset;call(0,0,0,0,0);call(2,0,0,1,0);call(1,32'h3f800000,42,0,1);call(2,0,0,0,0);
  if(rsp_id!=42)$fatal(1,"stale result after reset");
 end
 // Nonempty completed heap, close response held, and boot itself interrupted.
 cold_reset;call(0,0,0,0,0);call(1,0,123,0,1);cold_reset;call(0,0,0,0,0);call(2,0,0,1,0);
 call(1,0,123,0,1);launch(4,0,0);wait(rsp_valid);cold_reset;call(0,0,0,0,0);call(2,0,0,1,0);
 @(negedge clk);rst=1;$fdisplay(fd,"RESET");repeat(6)@(negedge clk);rst=0;repeat(4)@(negedge clk);cold_reset;
 // Late abort preserves offered packet; future commands blocked until cold reset.
 call(0,0,0,0,0);launch(1,0,99);wait(rsp_valid);@(negedge clk);abort=1;$fdisplay(fd,"ABORT");
 repeat(4)@(negedge clk);
 if(!fault||req_ready||!rsp_valid||rsp_status!=0||rsp_size!=1)$fatal(1,"late abort contract");
 rsp_ready=1;@(negedge clk);rsp_ready=0;abort=0;
 repeat(4)@(negedge clk);if(!fault||req_ready)$fatal(1,"fault not latched");
 cold_reset;call(0,0,0,0,0);call(2,0,0,1,0);
 $fdisplay(fd,"END %0d %0d %0d %0d",accepted,responded,resets,hls_calls);$fclose(fd);
 $display("FRONTIER_SERVICE_PASS calls=%0d resets=%0d accepted=%0d responded=%0d hls_calls=%0d cycles=%0d capacity=65536 interrupted_offsets=192",calls,resets,accepted,responded,hls_calls,cycles);$finish;
end
endmodule
