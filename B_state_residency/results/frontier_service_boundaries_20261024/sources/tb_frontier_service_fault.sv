`timescale 1ns/1ps
module tb_frontier_service_fault;
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
 do @(negedge clk);while(!initialized&&!fault);
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
 do @(negedge clk);while(!rsp_valid&&!fault);
 if(fault||rsp_status!==status||rsp_size!==size||rsp_cookie!==req_cookie||rsp_query!==req_query||rsp_price!==req_price)
  $fatal(1,"bad reply call=%0d op=%0d status=%0d size=%0d want=%0d/%0d fault=%b",calls,req_op,rsp_status,rsp_size,status,size,fault);
 if(heap_size!==size)$fatal(1,"size mirror mismatch");
 repeat(req_cookie%3)@(negedge clk);
 rsp_ready=1;@(negedge clk);rsp_ready=0;calls=calls+1;
end endtask
task call(input [31:0] op,input [31:0] bits,input [31:0] node,input [31:0] status,input [31:0] size);
begin launch(op,bits,node);collect(status,size);end endtask
task fault_stop(input integer tag);
begin
 do @(negedge clk);while(!fault);
 repeat(3)@(negedge clk);
 if(req_ready||rsp_valid||!busy)$fatal(1,"fault boundary %0d",tag);
 $fdisplay(fd,"FAULT %0d %0d %0d %0d",tag,active,heap_size,initialized);
end endtask
initial begin
 fd=$fopen("fault_transactions.txt","w");if(!fd)$fatal(1,"trace open");
 // Boot waits for HLS idle only for a bounded interval.
 @(negedge clk);force dut.ap_idle=0;rst=0;
 fault_stop(0);if(initialized||active)$fatal(1,"boot timeout admitted work");release dut.ap_idle;
 cold_reset;call(0,0,0,0,0);
 // A missing completion, despite actual heap mutation, must stop admission.
 force dut.hls_valid=0;force dut.ap_done=0;launch(1,32'h3f800000,99);
 fault_stop(1);if(!active||heap_size!=0)$fatal(1,"timeout committed mirror");
 release dut.hls_valid;release dut.ap_done;
 cold_reset;call(0,0,0,0,0);call(2,0,0,1,0);
 launch(1,32'h3f800000,99);wait(dut.hls_valid[0]);@(negedge clk);force dut.hls_reply[31:0]=7;
 repeat(2)@(negedge clk);release dut.hls_reply[31:0];fault_stop(2);
 if(!active||heap_size!=0)$fatal(1,"bad status committed mirror");
 cold_reset;call(0,0,0,0,0);
 launch(1,32'h3f800000,99);wait(dut.hls_valid[3]);@(negedge clk);force dut.hls_reply[127:96]=65537;
 repeat(2)@(negedge clk);release dut.hls_reply[127:96];fault_stop(3);
 if(heap_size!=0)$fatal(1,"bad size committed mirror");
 cold_reset;call(0,0,0,0,0);
 launch(1,32'h3f800000,99);wait(dut.hls_valid[1]);@(negedge clk);force dut.hls_reply[63:32]=1;
 repeat(2)@(negedge clk);release dut.hls_reply[63:32];fault_stop(4);
 cold_reset;call(0,0,0,0,0);
 launch(1,32'h3f800000,99);abort=1;fault_stop(5);abort=0;
 repeat(3)@(negedge clk);if(!fault||req_ready)$fatal(1,"abort failed to latch");
 cold_reset;call(0,0,0,0,0);call(2,0,0,1,0);
 $fclose(fd);$display("FRONTIER_SERVICE_FAULT_PASS cases=6 recovered_empty=1");$finish;
end
endmodule
