`timescale 1ns/1ps
module tb_record_response_gate;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,iv=0,orr=1,en=0;reg [23:0] data=0;wire ir,ov;wire [23:0] od;wire [2:0] count;
 record_response_fallthrough_fifo dut(clk,rst,iv,ir,data,ov,orr,od,count,en);
 initial begin
  repeat(3)@(negedge clk);rst=0;iv=1;data=24'h123456;
  #1;if(ov||!ir||count!=0)$fatal(1,"control response bypassed");
  @(negedge clk);iv=0;
  #1;if(!ov||od!=24'h123456||count!=1)$fatal(1,"control response not stored");
  @(negedge clk);en=1;iv=1;data=24'h654321;
  #1;if(!ov||od!=24'h654321||count!=0)$fatal(1,"record bypass missing");
  @(negedge clk);iv=0;
  #1;if(ov||count!=0)$fatal(1,"record delivered twice");
  @(negedge clk);iv=1;data=24'habcdef;orr=0;
  #1;if(!ov||od!=24'habcdef)$fatal(1,"blocked record missing");
  @(negedge clk);iv=0;en=0;data=0;
  #1;if(!ov||od!=24'habcdef||count!=1)$fatal(1,"blocked record not captured");
  repeat(3)@(negedge clk);
  orr=1;@(negedge clk);
  #1;if(ov||count!=0)$fatal(1,"stored record not drained");
  $display("RECORD_GATE_PASS control_registered=1 record_bypass=1 blocked_capture=1");$finish;
 end
 initial begin #10000;$fatal(1,"gate watchdog");end
endmodule
