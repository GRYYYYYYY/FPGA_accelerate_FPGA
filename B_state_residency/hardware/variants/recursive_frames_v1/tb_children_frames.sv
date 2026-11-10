`timescale 1ns/1ps
module tb_children_frames;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,abort=0,begin_valid=0,child_valid=0,finish_valid=0,item_ready=0,pop_valid=0;
 reg[511:0]begin_context=0;reg[351:0]child_record=0;reg[3:0]finish_status=0;reg[31:0]finish_count=0;
 wire begin_ready,child_ready,finish_ready,capture_active,fault,frame_valid,item_valid,frame_done,pop_ready;
 wire[3:0]error_code;wire[31:0]depth;wire[511:0]frame_context;wire[351:0]item_record;
 children_frames #(.DEPTH(3),.CAPACITY(3))d(.*);
 task tick;begin @(posedge clk);#1;end endtask
 task reset;begin @(negedge clk);rst=1;abort=0;begin_valid=0;child_valid=0;finish_valid=0;item_ready=0;pop_valid=0;finish_status=0;tick;@(negedge clk);rst=0;tick;end endtask
 task start(input integer id);begin @(negedge clk);begin_context={448'h0123456789abcdef0123456789abcdef,32'hfedcba98,id[31:0]};begin_valid=1;#1;if(!begin_ready)$fatal(1,"begin not ready");tick;@(negedge clk);begin_valid=0;end endtask
 task child(input integer id);begin @(negedge clk);child_record={320'h123456789abcdef0123456789abcdef,id[31:0]};child_valid=1;#1;if(!child_ready)$fatal(1,"capture blocked");tick;@(negedge clk);child_valid=0;end endtask
 task finish(input integer count);begin @(negedge clk);finish_count=count;finish_valid=1;#1;if(!finish_ready)$fatal(1,"finish blocked");tick;@(negedge clk);finish_valid=0;tick;end endtask
 task consume(input integer ctx,input integer id);reg[351:0]held;begin
  #1;if(!item_valid||frame_context!=={448'h0123456789abcdef0123456789abcdef,32'hfedcba98,ctx[31:0]}||item_record!=={320'h123456789abcdef0123456789abcdef,id[31:0]})$fatal(1,"item/context mismatch");held=item_record;
  repeat(4)begin tick;if(!item_valid||item_record!==held)$fatal(1,"backpressure changed");end
  @(negedge clk);item_ready=1;tick;@(negedge clk);item_ready=0;
  $display("ITEM %0d %0d",ctx,id);
 end endtask
 task pop;begin #1;if(!frame_done||!pop_ready)$fatal(1,"not done");@(negedge clk);pop_valid=1;tick;@(negedge clk);pop_valid=0;tick;end endtask
 initial begin
  reset;start(10);child(1);child(2);if(item_valid)$fatal(1,"unsealed visible");finish(2);consume(10,1);
  start(20);child(3);finish(1);consume(20,3);
  start(30);finish(0);pop;pop;consume(10,2);pop;
  if(depth!=0||fault||item_valid)$fatal(1,"normal state");$display("CASE 1 resume_ok");
  // Reuse physical frame bank; no old tail may become visible.
  start(40);child(4);finish(1);consume(40,4);pop;if(item_valid)$fatal(1,"stale item");$display("CASE 2 reuse_ok");
  reset;start(1);finish(0);start(2);finish(0);start(3);finish(0);start(4);tick;
  if(!fault||error_code!=1||capture_active||item_valid)$fatal(1,"depth overflow");$display("CASE 3 depth_stop");
  reset;start(1);child(1);child(2);child(3);child(4);child(5);finish(5);
  if(!fault||error_code!=2||capture_active||item_valid)$fatal(1,"capacity/drain");$display("CASE 4 capacity_drain");
  reset;start(1);child(1);finish(2);if(!fault||error_code!=3||item_valid)$fatal(1,"count mismatch");$display("CASE 5 count_stop");
  reset;start(1);child(1);@(negedge clk);abort=1;tick;@(negedge clk);abort=0;child(2);finish(2);
  if(!fault||error_code!=4||capture_active||item_valid||begin_ready)$fatal(1,"abort drain");$display("CASE 6 abort_drain");
  reset;start(1);child(1);finish_status=7;finish(1);if(!fault||error_code!=3||item_valid)$fatal(1,"bad producer");$display("CASE 7 producer_stop");
  reset;start(1);finish(0);pop;if(fault||frame_valid)$fatal(1,"reset stale");$display("CASE 8 reset_empty");
  start(8);child(8);finish(1);@(negedge clk);abort=1;item_ready=1;#1;
  if(item_valid||begin_ready)$fatal(1,"abort admission");tick;@(negedge clk);abort=0;item_ready=0;
  if(!fault||error_code!=4||item_valid)$fatal(1,"abort hidden");$display("CASE 9 abort_admission");
  $display("CHILDREN_FRAMES_PASS cases=9 items=4");$finish;
 end
 initial begin #100000;$fatal(1,"watchdog");end
endmodule
