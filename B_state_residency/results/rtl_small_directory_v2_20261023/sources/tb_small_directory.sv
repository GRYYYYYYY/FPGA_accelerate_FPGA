`timescale 1ns/1ps
module tb_small_directory;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,cmd_valid=0,rsp_ready=0,memory_success=0,fence_retired=0;
 reg [2:0] cmd_op=0;reg [26:0] cmd_owner=0;reg [5:0] cmd_frame=0;reg [71:0] cmd_cookie=0;
 wire cmd_ready,rsp_valid,rsp_published,any_fault;wire [2:0] rsp_status;wire [5:0] rsp_frame;
 wire [31:0] rsp_address,leased;wire [6:0] allocated;
 backing_frame_directory_small #(.FRAMES(40),.INDEX_BITS(6),.HASH_BITS(3),.PROBE_LIMIT(1),.EPOCH_BITS(2)) dut(.*);
 integer checks=0,n,e;reg [71:0] token;reg [31:0] expected_mask;
 function automatic [26:0] owner(input integer n);begin owner=((n%8)<<24)+(n/8)+1;end endfunction
 function automatic [71:0] cookie(input reg[26:0] own,input integer slot,tx,kind);begin
  cookie=0;cookie[4:0]=slot;cookie[31:5]=own;cookie[47:32]=16'hfedc;cookie[63:48]=tx;cookie[64]=kind;
 end endfunction
 task request(input integer op,input reg[26:0] own,input integer frame,input reg[71:0] tok,input bit success,fence,input integer status,expected_frame,input bit pub);
 integer deadline,h;begin
  @(negedge clk);cmd_valid=1;cmd_op=op;cmd_owner=own;cmd_frame=frame;cmd_cookie=tok;memory_success=success;fence_retired=fence;
  deadline=0;@(posedge clk);while(!cmd_ready)begin @(posedge clk);deadline=deadline+1;if(deadline>1000)$fatal(1,"command timeout");end
  @(negedge clk);cmd_valid=0;cmd_owner='1;cmd_cookie='1;memory_success=0;fence_retired=0;
  deadline=0;while(!rsp_valid)begin @(negedge clk);deadline=deadline+1;if(deadline>1000)$fatal(1,"response timeout");end
  repeat(3)begin
   if(!rsp_valid || rsp_status!==status[2:0] || rsp_frame!==expected_frame[5:0] || rsp_address!==32'(expected_frame*192) || rsp_published!==pub || cmd_ready)$fatal(1,"response check=%0d got=%0d frame=%0d pub=%b expected=%0d/%0d/%b",checks,rsp_status,rsp_frame,rsp_published,status,expected_frame,pub);
   @(negedge clk);
  end
  rsp_ready=1;@(posedge clk);@(negedge clk);rsp_ready=0;checks=checks+1;
 end endtask
 initial begin #10000000;$fatal(1,"watchdog");end
 initial begin
  repeat(3)@(negedge clk);rst=0;
  for(n=0;n<32;n=n+1)begin
   request(0,owner(n),0,0,0,0,0,n,0);request(5,owner(n),0,0,0,0,0,n,0);
  end
  if(allocated!=32)$fatal(1,"owner truncation or allocation mismatch");
  for(n=0;n<32;n=n+1)begin
   request(1,0,n,cookie(owner(n),n,n,0),0,0,0,n,0);
   expected_mask=32'hffffffff>>(31-n);if(leased!==expected_mask)$fatal(1,"lease slot alias");
  end
  request(6,0,0,0,0,1,2,0,0);
  for(n=0;n<32;n=n+1)request(2,0,n,cookie(owner(n),n,n,0),1,0,0,n,1);
  request(6,0,0,0,0,1,2,0,0);
  for(n=31;n>=0;n=n-1)begin
   request(3,0,n,cookie(owner(n),n,n,0),0,0,0,n,1);
   expected_mask=n==0?0:32'hffffffff>>(32-n);if(leased!==expected_mask)$fatal(1,"retire alias");
  end
  request(6,0,0,0,0,0,2,0,0);request(6,0,0,0,0,1,0,0,0);
  if(allocated!=32)$fatal(1,"checkpoint lost allocation");
  for(n=0;n<32;n=n+1)begin
   token=cookie(owner(n),31-n,n,1);
   request(1,0,n,token,0,0,0,n,1);request(2,0,n,token,1,0,0,n,1);request(3,0,n,token,0,0,0,n,1);
  end
  request(1,0,0,cookie(owner(0),0,0,1),0,0,5,0,0);
  request(1,0,0,cookie(owner(0)^(27'b1<<24),31,32,1),0,0,1,0,0);
  token=cookie(owner(0),31,32,1);
  request(1,0,0,token,0,0,0,0,1);request(2,0,0,token,1,0,0,0,1);request(3,0,0,token,0,0,0,0,1);
  for(n=32;n<40;n=n+1)request(0,owner(n),0,0,0,0,0,n,0);
  request(0,27'h7ffffff,0,0,0,0,4,0,0);request(5,27'h7ffffff,0,0,0,0,6,0,0);
  for(e=0;e<8;e=e+1)begin
   request(4,0,0,0,0,1,0,0,0);request(5,owner(0),0,0,0,0,6,0,0);
   request(0,27'h7000100+e,0,0,0,0,0,0,0);
   request(5,27'h6000100+e,0,0,0,0,6,0,0);
   request(6,0,0,0,0,1,0,0,0);request(5,27'h7000100+e,0,0,0,0,0,0,0);
  end
  token=cookie(27'h7000107,31,0,0);
  request(1,0,0,token|(72'b1<<65),0,0,3,0,0);
  request(1,0,0,token,0,0,0,0,0);request(2,0,0,token,0,0,7,0,0);
  if(!any_fault || leased!==32'h80000000)$fatal(1,"failed high slot missing");
  request(6,0,0,0,0,1,2,0,0);request(3,0,0,token,0,0,6,0,0);
  $display("SMALL_DIRECTORY_PASS checks=%0d slots=32 owners=40 full_recycles=8",checks);$finish;
 end
endmodule
