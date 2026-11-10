`timescale 1ns/1ps
module tb_backing_base_config;
 reg clk=0;always #5 clk=~clk;reg rst=1,cfg_base_valid=0,cfg_rsp_ready=0;
 reg [63:0] cfg_base_address=0;wire cfg_base_ready,cfg_rsp_valid,configured;
 wire [1:0] cfg_rsp_status;wire [63:0] backing_base;integer cases=0;
 backing_base_config #(.FRAMES(64)) dut(.*);
 task send(input [63:0] value,input [1:0] expected);
  begin
   @(negedge clk);cfg_base_address=value;cfg_base_valid=1;
   @(posedge clk);if(!cfg_base_ready)$fatal(1,"configuration not ready");
   @(negedge clk);cfg_base_valid=0;cfg_base_address='1;
   repeat(4)begin
    if(!cfg_rsp_valid || cfg_rsp_status!==expected || cfg_base_ready)$fatal(1,"configuration response changed");
    if(expected==0)begin if(!configured || backing_base!==value)$fatal(1,"base not latched");end
    else if(configured || backing_base!=0)$fatal(1,"invalid base enabled traffic");
    @(negedge clk);
   end
   cfg_rsp_ready=1;@(negedge clk);cfg_rsp_ready=0;cases=cases+1;
  end
 endtask
 initial begin
  repeat(3)@(negedge clk);rst=0;
  send(64'h12345001,1);
  send(64'hfffffffffffff000,2);
  send(64'h0000001234567000,0);
  @(negedge clk);cfg_base_valid=1;cfg_base_address=0;
  repeat(5)begin @(negedge clk);if(cfg_base_ready || backing_base!=64'h0000001234567000 || !configured || cfg_rsp_valid)$fatal(1,"live reconfiguration accepted");end
  rst=1;cfg_base_valid=0;repeat(3)@(negedge clk);rst=0;
  if(configured)$fatal(1,"reset retained old base");
  send(64'hffffffffffffd000,0);
  if(cases!=4)$fatal(1,"missing config cases");
  $display("BASE_CONFIG_PASS cases=4 invalid_alignment=1 overflow=1 high_address=1 exact_end=1 locked=1 reset=1");$finish;
 end
 initial begin #100000;$fatal(1,"config watchdog");end
endmodule
