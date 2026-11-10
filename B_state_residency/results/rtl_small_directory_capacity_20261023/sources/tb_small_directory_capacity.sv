`timescale 1ns/1ps
module tb_small_directory_capacity;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,cmd_valid=0,rsp_ready=0,memory_success=0,fence_retired=0;
 reg [2:0] cmd_op=0;reg [26:0] cmd_owner=0;reg [17:0] cmd_frame=0;reg [71:0] cmd_cookie=0;
 wire cmd_ready,rsp_valid,rsp_published,any_fault;wire [2:0] rsp_status;wire [17:0] rsp_frame;
 wire [31:0] rsp_address,leased;wire [18:0] allocated;
 backing_frame_directory_small dut(.*);
 integer checks=0,n,f;reg [71:0] token;
 function automatic [26:0] owner(input integer n);begin owner=27'h7000000+n;end endfunction
 function automatic [71:0] cookie(input integer frame,tx,kind);begin
  cookie=0;cookie[4:0]=31;cookie[31:5]=owner(frame);cookie[47:32]=16'hffff;cookie[63:48]=tx;cookie[64]=kind;
 end endfunction
 task request(input integer op,input reg[26:0] own,input integer frame,input reg[71:0] tok,input bit success,fence,input integer status,expected_frame,input bit pub);
 integer d;begin
  @(negedge clk);cmd_valid=1;cmd_op=op;cmd_owner=own;cmd_frame=frame;cmd_cookie=tok;memory_success=success;fence_retired=fence;
  d=0;@(posedge clk);while(!cmd_ready)begin @(posedge clk);d=d+1;if(d>300000)$fatal(1,"command timeout");end
  @(negedge clk);cmd_valid=0;memory_success=0;fence_retired=0;
  d=0;while(!rsp_valid)begin @(negedge clk);d=d+1;if(d>400000)$fatal(1,"response timeout");end
  if(rsp_status!==status[2:0] || rsp_frame!==expected_frame[17:0] || rsp_address!==32'(expected_frame*192) || rsp_published!==pub)$fatal(1,"capacity mismatch check=%0d status=%0d frame=%0d expected=%0d",checks,rsp_status,rsp_frame,expected_frame);
  rsp_ready=1;@(posedge clk);@(negedge clk);rsp_ready=0;checks=checks+1;
 end endtask
 initial begin #64'd100000000000;$fatal(1,"watchdog");end
 initial begin
  repeat(3)@(negedge clk);rst=0;
  for(n=0;n<163840;n=n+1)begin
   request(0,owner(n),0,0,0,0,0,n,0);
   if((n+1)%32768==0)$display("CAPACITY_ALLOCATED frames=%0d",n+1);
  end
  if(allocated!=163840 || rsp_address!=31457088)$fatal(1,"capacity or final address");
  request(0,27'h7ffffff,0,0,0,0,4,0,0);request(5,27'h7ffffff,0,0,0,0,6,0,0);
  for(n=0;n<163840;n=n+1)begin
   request(5,owner(n),0,0,0,0,0,n,0);
   if((n+1)%32768==0)$display("CAPACITY_LOOKED_UP frames=%0d",n+1);
  end
  for(n=0;n<3;n=n+1)begin
   f=n==0?65535:(n==1?65536:163839);token=cookie(f,n,0);
   request(1,0,f,token,0,0,0,f,0);request(2,0,f,token,1,0,0,f,1);request(3,0,f,token,0,0,0,f,1);
  end
  request(6,0,0,0,0,1,0,0,0);if(allocated!=163840)$fatal(1,"checkpoint capacity loss");
  for(n=0;n<3;n=n+1)begin
   f=n==0?65535:(n==1?65536:163839);token=cookie(f,n,1);
   request(1,0,f,token,0,0,0,f,1);request(2,0,f,token,1,0,0,f,1);request(3,0,f,token,0,0,0,f,1);
  end
  request(4,0,0,0,0,1,0,0,0);request(5,owner(163839),0,0,0,0,6,0,0);
  if(allocated!=0 || leased!=0 || any_fault)$fatal(1,"final reset domain");
  $display("SMALL_DIRECTORY_CAPACITY_PASS checks=%0d frames=163840",checks);$finish;
 end
endmodule
