`timescale 1ns/1ps
module tb_checkpoint_lease_guard;
reg clk=0;always #5 clk=~clk;
reg rst=1,acquire_valid=0,release_valid=0,healthy=0,retired=0,no_offers=0,route_retired=0,command_busy=0,command_valid=0,test_reset=0;
wire acquire_ready,release_ready,safe,owned;
checkpoint_lease_guard dut(.*);
integer checks=0,fd;string path;
task check(input integer ar,rr,ss,oo);begin
 #1;if({acquire_ready,release_ready,safe,owned}!=={1'(ar),1'(rr),1'(ss),1'(oo)})$fatal(1,"lease guard check %0d actual=%b%b%b%b expected=%0d%0d%0d%0d",checks,acquire_ready,release_ready,safe,owned,ar,rr,ss,oo);
 $fdisplay(fd,"G %0d %0d%0d%0d%0d %b%b%b%b%b%b%b%b%b%b",checks,ar,rr,ss,oo,rst,acquire_valid,release_valid,healthy,retired,no_offers,route_retired,command_busy,command_valid,test_reset);checks=checks+1;@(negedge clk);
end endtask
initial begin
 if(!$value$plusargs("events=%s",path))$fatal(1,"events path");fd=$fopen(path,"w");
 repeat(3)@(negedge clk);check(0,0,0,0);rst=0;acquire_valid=1;check(0,0,0,0);
 healthy=1;check(0,0,0,0);no_offers=1;check(0,0,0,0);route_retired=1;command_busy=1;check(0,0,0,0);
 command_busy=0;test_reset=1;check(0,0,0,0);test_reset=0;check(1,0,0,0);
 acquire_valid=0;check(0,0,1,1);
 no_offers=0;check(0,0,1,1);healthy=0;check(0,0,0,1);release_valid=1;
 retired=1;command_busy=1;check(0,0,0,1);command_busy=0;route_retired=0;check(0,0,0,1);
 route_retired=1;retired=0;check(0,0,0,1);retired=1;command_valid=1;check(0,0,0,1);
 command_valid=0;test_reset=1;check(0,0,0,1);test_reset=0;check(0,1,0,1);
 release_valid=0;check(0,0,0,0);healthy=1;no_offers=1;command_valid=1;check(1,0,0,0);
 acquire_valid=1;check(1,0,0,0);acquire_valid=0;check(0,0,1,1);command_valid=0;check(0,1,1,1);
 rst=1;check(0,0,0,1);check(0,0,0,0);rst=0;acquire_valid=1;release_valid=1;check(1,0,0,0);
 acquire_valid=0;check(0,1,1,1);release_valid=0;check(1,0,0,0);
 $fflush(fd);$fclose(fd);$display("CHECKPOINT_LEASE_GUARD_PASS checks=%0d",checks);$finish;
end
endmodule
