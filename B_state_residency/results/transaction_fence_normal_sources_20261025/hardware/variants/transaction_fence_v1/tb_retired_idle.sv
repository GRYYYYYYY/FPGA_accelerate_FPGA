`timescale 1ns/1ps
module tb_retired_idle;
 reg clk=0;always #5 clk=~clk;reg rst=1,abort=0,active=1,req_valid=0,rsp_ready=0;
 reg[1:0]active_query=1,req_query=1;reg[3:0]active_price=3,req_price=3;reg[31:0]active_version=3,req_version=3,req_cookie=1;reg[127:0]req_words=0;
 wire req_ready,rsp_valid,busy,fault,retired_idle,ap_start;wire[63:0]rsp_words;wire[31:0]rsp_cookie,rsp_version;wire[1:0]rsp_query,rsp_status;wire[3:0]rsp_price;
 reg ap_idle=1,ap_ready=0,ap_done=0;reg[1:0]ia0=0;reg ic0=0;wire[31:0]iq0;reg[0:0]oa0=0,oa1=1;reg oc0=0,oc1=0,ow0=0,ow1=0;reg[31:0]od0=0,od1=0;
 cost_center_memory_call #(.MAX_CALL_CYCLES(16))dut(.*);
 task init;begin @(negedge clk);rst=1;abort=0;active=1;ap_idle=1;ap_done=0;ap_ready=0;req_valid=0;rsp_ready=0;repeat(3)@(negedge clk);rst=0;@(negedge clk);end endtask
 initial begin
  init;if(!retired_idle)$fatal(1,"fresh idle");abort=1;@(negedge clk);if(!fault||!busy||!retired_idle||req_ready)$fatal(1,"idle abort must stay quiescent while fault remains sticky");
  init;active=0;req_valid=1;do @(posedge clk);while(!req_ready);@(negedge clk);req_valid=0;wait(rsp_valid);if(retired_idle)$fatal(1,"held reply counted idle");abort=1;rsp_ready=1;@(negedge clk);rsp_ready=0;if(!retired_idle||!fault||!busy)$fatal(1,"retired fault reply");
  init;req_valid=1;do @(posedge clk);while(!req_ready);@(negedge clk);req_valid=0;ap_idle=0;if(retired_idle)$fatal(1,"owned HLS RUN counted idle");abort=1;repeat(3)@(negedge clk);ap_idle=1;repeat(3)@(negedge clk);if(retired_idle||!fault||!busy)$fatal(1,"fault cannot hide an owned call even if ap_idle rises");
  $display("RETIRED_IDLE_PASS checks=5");$finish;
 end
endmodule
