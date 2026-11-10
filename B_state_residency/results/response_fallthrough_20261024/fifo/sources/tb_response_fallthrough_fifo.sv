`timescale 1ns/1ps
module fifo_scoreboard #(parameter DEPTH=4)(input wire clk,output reg done=0);
 reg rst=1,iv=0,orr=0;reg [31:0] data=0;
 wire ir,ov;wire [31:0] od;wire [$clog2(DEPTH+1)-1:0] count;
 response_fallthrough_fifo #(.WIDTH(32),.DEPTH(DEPTH)) dut(clk,rst,iv,ir,data,ov,orr,od,count);
 reg [31:0] expected[0:65535];integer head=0,tail=0,i;
 integer accepted=0,consumed=0,empty_pass=0,full_stall=0,captured=0,simultaneous=0;
 reg [31:0] random_state=32'hbeef1234;reg held=0;reg [31:0] held_data;
 always @(posedge clk)begin
  if(rst)begin head=0;tail=0;held=0;end
  else begin
   if(count!=tail-head)$fatal(1,"occupancy depth=%0d got=%0d expected=%0d",DEPTH,count,tail-head);
   if(held && (!ov || od!==held_data))$fatal(1,"unstable stalled output");
   if(iv&&ir)begin expected[tail]=data;tail=tail+1;accepted=accepted+1;end
   if(ov&&orr)begin
    if(head==tail || od!==expected[head])$fatal(1,"order/data depth=%0d",DEPTH);
    head=head+1;consumed=consumed+1;
   end
   if(count==0&&iv&&ir&&orr)empty_pass=empty_pass+1;
   if(count==0&&iv&&ir&&!orr)captured=captured+1;
   if(count==DEPTH&&iv&&!ir)full_stall=full_stall+1;
   if(count!=0&&iv&&ir&&ov&&orr)simultaneous=simultaneous+1;
   held=ov&&!orr;held_data=od;
  end
 end
 task drive(input bit v,input bit r);
  begin @(negedge clk);iv=v;orr=r;data=data+1;end
 endtask
 initial begin
  repeat(3)@(negedge clk);rst=0;
  repeat(12)drive(1,1);
  repeat(DEPTH+4)drive(1,0);
  repeat(12)drive(1,1);
  repeat(DEPTH+4)drive(0,1);
  for(i=0;i<4000;i=i+1)begin
   random_state=random_state^(random_state<<13);random_state=random_state^(random_state>>17);random_state=random_state^(random_state<<5);
   // Producer retains a pending item until accepted.
   @(negedge clk);
   if(!iv||ir)begin iv=random_state[0];data=data+1;end
   orr=random_state[1];
  end
  // Reset a deliberately occupied queue; stale records must disappear.
  repeat(DEPTH+2)drive(1,0);
  @(negedge clk);rst=1;iv=0;orr=0;
  repeat(2)@(negedge clk);rst=0;
  repeat(DEPTH+2)drive(0,1);
  repeat(12)drive(1,1);
  repeat(DEPTH+2)drive(0,1);
  @(negedge clk);
  if(head!=tail||count!=0||empty_pass==0||captured==0||full_stall==0||(DEPTH>1&&simultaneous==0))$fatal(1,"coverage/drain depth=%0d",DEPTH);
  $display("FIFO_SCOREBOARD_PASS depth=%0d accepted=%0d consumed=%0d bypass=%0d captured=%0d full=%0d simultaneous=%0d",DEPTH,accepted,consumed,empty_pass,captured,full_stall,simultaneous);done=1;
 end
endmodule
module tb_response_fallthrough_fifo;
 reg clk=0;always #5 clk=~clk;wire a,b,c;
 fifo_scoreboard #(.DEPTH(1)) d1(clk,a);
 fifo_scoreboard #(.DEPTH(3)) d3(clk,b);
 fifo_scoreboard #(.DEPTH(4)) d4(clk,c);
 initial begin wait(a&&b&&c);$display("RESPONSE_FIFO_PASS depths=1,3,4");$finish;end
 initial begin #1000000;$fatal(1,"watchdog");end
endmodule
