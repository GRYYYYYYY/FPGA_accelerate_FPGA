`timescale 1ns/1ps
module tb_service_arbiter;
 reg clk=0;always #5 clk=~clk;
 reg rst=1;reg[2:0]cv=0,cr=0;wire[2:0]cq,rv;reg[23:0]cd=0;wire[23:0]rd;
 wire bv,br;reg bq=0,vr=0;wire[7:0]bd;reg[7:0]dr=0;wire fault,busy;
 service_arbiter #(.CLIENTS(3),.REQUEST_BITS(8),.RESPONSE_BITS(8))dut(clk,rst,cv,cq,cd,rv,cr,rd,bv,bq,bd,vr,br,dr,fault,busy);
 task tick;begin @(posedge clk);#1;end endtask
 task check(input bit ok,input string message);begin if(!ok)$fatal(1,"%s",message);end endtask
 initial begin
  repeat(2)tick();@(negedge clk);rst=0;cv=7;cd=24'hc3b2a1;#1;check(cq==1,"lowest index priority");tick();
  @(negedge clk);cv=6;cd=24'hc3b2ff;
  repeat(4)begin tick();check(bv&&bd==8'ha1&&cq==0&&busy,"captured request stable under backend stall");end
  @(negedge clk);bq=1;tick();@(negedge clk);bq=0;vr=1;dr=8'h51;#1;
  check(rv==1&&rd[7:0]==8'h51&&!br,"reply belongs to captured client");
  repeat(3)begin tick();check(cq==0&&rv==1&&!br,"no new client before reply retirement");end
  @(negedge clk);cr=1;tick();@(negedge clk);vr=0;cr=0;#1;check(cq==2,"second client priority");tick();
  @(negedge clk);cv=4;bq=1;#1;check(bv&&bd==8'hb2,"second payload");tick();
  @(negedge clk);bq=0;vr=1;dr=8'h62;cr=2;#1;check(rv==2&&br,"second response route");tick();
  @(negedge clk);vr=0;cr=0;tick();@(negedge clk);cv=0;bq=1;#1;check(bv&&bd==8'hc3,"third payload");tick();
  @(negedge clk);bq=0;vr=1;cr=4;#1;check(rv==4&&br,"third response route");tick();
  @(negedge clk);vr=0;cr=0;tick();check(!fault&&!busy,"normal idle");
  @(negedge clk);vr=1;tick();check(fault,"unowned response faults");
  @(negedge clk);vr=0;cv=7;tick();check(cq==0&&!bv,"fault blocks new requests");
  @(negedge clk);rst=1;tick();@(negedge clk);rst=0;cv=0;tick();check(!fault&&!busy,"coordinated reset recovers");
  $display("SERVICE_ARBITER_PASS clients=3 stalled_request=4 stalled_reply=3 unowned=1 reset=1");$finish;
 end
 initial begin #10000;$fatal(1,"timeout");end
endmodule
