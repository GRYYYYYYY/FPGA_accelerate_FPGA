`timescale 1ns/1ps
module tb_guard;
reg clk=0;always #5 clk=~clk;
reg cold_rst=1,reader_idle=1,cfg_valid=0,req_valid=0,req_ready=0,rsp_valid=0,rsp_ready=0;
reg arvalid=0,arready=0,rvalid=0,rready=0,rlast=1;reg[7:0]arlen=0;
wire retired,physical_drained,owned,fault;
integer checks=0,fd;
baseline_retirement_guard dut(.*);
task ck(input bit re,ph,ow,fa);begin
 #1;checks=checks+1;if({retired,physical_drained,owned,fault}!={re,ph,ow,fa})$fatal(1,"guard check%0d",checks);
 $fdisplay(fd,"CHECK %0d %b%b%b%b",checks,retired,physical_drained,owned,fault);
end endtask
task tick;begin @(posedge clk);@(negedge clk);end endtask
initial begin
 fd=$fopen("guard_trace.txt","w");tick;tick;cold_rst=0;ck(1,1,0,0);
 cfg_valid=1;ck(0,1,0,0);cfg_valid=0;ck(1,1,0,0);
 req_valid=1;repeat(3)begin tick;ck(0,1,0,0);end
 req_ready=1;tick;req_valid=0;req_ready=0;reader_idle=0;ck(0,1,1,0);
 arvalid=1;repeat(3)begin tick;ck(0,0,1,0);end
 arready=1;tick;arvalid=0;arready=0;ck(0,0,1,0);
 rvalid=1;repeat(4)begin tick;ck(0,0,1,0);end
 rready=1;tick;rvalid=0;rready=0;ck(0,1,1,0);
 // Physical R has retired, but the response is still owned/backpressured.
 rsp_valid=1;repeat(4)begin tick;ck(0,1,1,0);end
 rsp_ready=1;tick;rsp_valid=0;rsp_ready=0;reader_idle=1;ck(1,1,0,0);
 rsp_valid=1;rsp_ready=1;tick;rsp_valid=0;rsp_ready=0;ck(0,1,0,1);
 cold_rst=1;tick;cold_rst=0;ck(1,1,0,0);
 rvalid=1;rready=1;tick;rvalid=0;rready=0;ck(0,0,0,1);
 $fdisplay(fd,"PASS %0d",checks);$fclose(fd);$display("BASELINE_GUARD_UNIT_PASS %0d",checks);$finish;
end
initial begin #10000;$fatal(1,"guard timeout");end
endmodule
