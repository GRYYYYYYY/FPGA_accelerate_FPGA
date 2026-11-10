`timescale 1ns/1ps
module tb_warm_retry;
 reg clk=0;always #5 clk=~clk;
 reg cold_rst=1,abort=0,recovery_owned=1,backend_drained=1,retired=1,owner_repaired=1;
 reg arm_valid=0;wire arm_ready;
 reg[63:0]arm_design=64'h1234,arm_generation=2,bound_design=64'h1234,bound_generation=2;
 reg[31:0]arm_checkpoint=18,bound_checkpoint=18,arm_version=5,active_version=4;
 reg[1:0]arm_query=3,active_query=2;reg[3:0]arm_price=5,active_price=4;
 reg[31:0]arm_cookie=32'he001,arm_labels=328,arm_path_crc=32'h637ddbbb,arm_query_crc=32'h6d0c23ca;
 reg label_accept=0,label_done=0;reg[3:0]label_status=0;
 reg[31:0]label_cookie=32'he001,label_written=328,label_verified=328;
 reg path_accept=0,path_restore=1,path_done=0;reg[3:0]path_status=0;reg[31:0]path_crc=32'h637ddbbb;
 reg query_accept=0,query_restore=1,query_done=0;reg[3:0]query_status=0;reg[31:0]query_crc=32'h6d0c23ca;
 reg completion_consumed=0;
 wire owned,label_allow,admin_safe,path_allow,query_allow,joined,fault,retry_window;wire[2:0]receipts;
 integer checks=0;reg must_isolate=0;
 warm_restore_receipt_join dut(.*);
 task tick;begin @(posedge clk);#1;@(negedge clk);end endtask
 task ck(input bit ok,input[511:0]why);begin checks=checks+1;if(!ok)$fatal(1,"check %0d: %0s",checks,why);end endtask
 task arm;begin ck(arm_ready,"arm ready");arm_valid=1;tick();arm_valid=0;end endtask
 task consume;begin completion_consumed=1;tick();completion_consumed=0;end endtask
 task turnover;begin recovery_owned=0;tick();tick();recovery_owned=1;#1;end endtask
 task stop;begin abort=1;tick();abort=0;tick();ck(owned&&fault&&!joined&&!label_allow,"failure quarantine");end endtask
 task all_receipts;begin
  ck(label_allow,"new labels allowed");label_accept=1;tick();label_accept=0;
  active_version=arm_version;active_query=arm_query;active_price=arm_price;
  label_cookie=arm_cookie;label_done=1;tick();label_done=0;
  ck(path_allow&&query_allow,"admin import after label receipt");
  path_accept=1;query_accept=1;tick();path_accept=0;query_accept=0;
  path_done=1;query_done=1;tick();path_done=0;query_done=0;
  tick();ck(joined&&owned&&!fault&&receipts==7,"three fresh receipts joined");
 end endtask
 always @(negedge clk)if(must_isolate&&!owned)$fatal(1,"ownership dropped before success consumed");
 initial begin #10000;$fatal(1,"watchdog");end
 initial begin
  tick();cold_rst=0;tick();arm();must_isolate=1;stop();
  // A fence gap before failure consumption cannot authorize a new attempt.
  turnover();ck(!arm_ready&&!retry_window,"release before consumption rejected");
  consume();tick();ck(!arm_ready,"consumption alone insufficient");turnover();
  ck(retry_window&&arm_ready,"consumption then fence turnover");
  retired=0;#1;ck(!arm_ready,"held reply blocks rearm");retired=1;
  backend_drained=0;#1;ck(!arm_ready,"physical activity blocks rearm");backend_drained=1;
  abort=1;#1;ck(!arm_ready,"abort blocks rearm");abort=0;#1;
  // Same and lower versions cannot start any restore service.
  arm();ck(fault&&!label_allow&&!retry_window,"same attempt rejected");
  consume();turnover();arm_version=4;arm_price=4;arm();ck(fault&&!label_allow,"lower attempt rejected");
  consume();turnover();arm_version=6;arm_query=0;arm_price=6;arm_checkpoint=19;
  arm();ck(fault&&!label_allow,"wrong checkpoint rejected");arm_checkpoint=18;
  consume();turnover();arm_cookie=32'he002;arm();
  ck(owned&&!fault&&receipts==0,"higher attempt accepted with fresh receipts");
  // A stale label completion from the old cookie must fail closed.
  label_accept=1;tick();label_accept=0;label_done=1;tick();label_done=0;
  ck(fault&&!joined,"old label cookie rejected");
  consume();turnover();arm_version=7;arm_query=1;arm_price=7;arm_cookie=32'he003;arm();
  all_receipts();repeat(8)begin tick();ck(joined&&owned,"held success stays owned");end
  must_isolate=0;consume();ck(!owned&&!fault&&!joined,"success consumption releases ownership");
  // Original healthy path remains usable without any fence retry flags.
  arm_version=8;arm_query=2;arm_price=8;arm_cookie=32'he004;arm();must_isolate=1;
  all_receipts();must_isolate=0;consume();ck(!owned&&!fault,"healthy path completes");
  $display("WARM_RETRY_UNIT_PASS checks=%0d",checks);$finish;
 end
endmodule
