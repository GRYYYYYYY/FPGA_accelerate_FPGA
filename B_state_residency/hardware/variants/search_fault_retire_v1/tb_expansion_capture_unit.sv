`timescale 1ns/1ps
module tb_expansion_capture_unit;
reg clk=0;always #5 clk=~clk;
reg rst=1,abort=0,expand_valid=0,out_ready=0,result_ready=0;
wire expand_ready,out_valid,result_valid,busy,fault;
reg[31:0]expand_cookie=0,expand_parent=0,expand_prune=0,expand_has_laguna=0;
reg[511:0]expand_context=0;wire[511:0]out_context;
wire[31:0]out_node,out_position,out_sequence,result_detail,result_cookie,result_count,result_raw_count,result_mask,depth;
wire[255:0]out_attrs;wire[3:0]result_status;wire result_hit;
wire e_expand_valid,e_out_ready,e_result_ready;
reg e_expand_ready=0,e_out_valid=0,e_result_valid=0;
wire[31:0]e_expand_cookie,e_expand_parent,e_expand_prune,e_expand_has_laguna;
reg[31:0]e_out_node=0,e_out_position=0,e_out_sequence=0,e_result_detail=0,e_result_cookie=0,e_result_count=0,e_result_raw_count=0,e_result_mask=0;
reg[255:0]e_out_attrs=0;reg[3:0]e_result_status=0;reg e_result_hit=0;
expansion_capture #(.DEPTH(3),.CAPACITY(4))d(.*);
task tick;begin @(posedge clk);#1;end endtask
task start(input integer cookie);begin
 @(negedge clk);expand_valid=1;expand_cookie=cookie;expand_parent=cookie+1;expand_context={480'habcdef,cookie[31:0]};#1;if(!expand_ready)$fatal(1,"start blocked");tick;
 @(negedge clk);expand_valid=0;expand_cookie=999;expand_parent=888;
 repeat(3)begin tick;if(!e_expand_valid||e_expand_cookie!=cookie||e_expand_parent!=cookie+1)$fatal(1,"exposed request changed");end
 @(negedge clk);e_expand_ready=1;tick;@(negedge clk);e_expand_ready=0;
end endtask
task emit(input integer node,seq);begin
 @(negedge clk);e_out_valid=1;e_out_node=node;e_out_sequence=seq;e_out_position=seq+9;e_out_attrs={224'habcdef,node[31:0]};#1;if(!e_out_ready)$fatal(1,"stream blocked");tick;@(negedge clk);e_out_valid=0;
end endtask
task seal(input integer cookie,count);begin
 @(negedge clk);e_result_cookie=cookie;e_result_count=count;e_result_raw_count=count+5;e_result_mask=32'ha5;e_result_hit=1;e_result_detail=cookie+7;e_result_valid=1;#1;if(!e_result_ready)$fatal(1,"finish blocked");tick;@(negedge clk);e_result_valid=0;
end endtask
task item(input integer ctx,node,seq);begin
 #1;if(!out_valid||out_node!=node||out_position!=seq+9||out_sequence!=seq||out_context!=={480'habcdef,ctx[31:0]}||out_attrs!=={224'habcdef,node[31:0]})$fatal(1,"replay mismatch");
 repeat(3)begin tick;if(!out_valid||out_node!=node)$fatal(1,"item hold");end
 @(negedge clk);out_ready=1;tick;@(negedge clk);out_ready=0;$display("ITEM %0d %0d",ctx,node);
end endtask
task result(input integer cookie,count);reg[164:0]snapshot;begin
 #1;if(!result_valid||result_status||result_cookie!=cookie||result_count!=count||result_raw_count!=count+5||result_mask!=32'ha5||!result_hit||result_detail!=cookie+7)$fatal(1,"result mismatch");
 snapshot={result_status,result_detail,result_cookie,result_count,result_raw_count,result_mask,result_hit};tick;
 @(negedge clk);expand_valid=1;expand_cookie=77;
 repeat(4)begin tick;if(expand_ready||!result_valid||{result_status,result_detail,result_cookie,result_count,result_raw_count,result_mask,result_hit}!==snapshot)$fatal(1,"offered result preempted");end
 @(negedge clk);expand_valid=0;result_ready=1;tick;@(negedge clk);result_ready=0;$display("RESULT %0d %0d",cookie,count);
end endtask
task reset_case;begin
 @(negedge clk);rst=1;abort=0;expand_valid=0;out_ready=0;result_ready=0;e_expand_ready=0;e_out_valid=0;e_result_valid=0;e_result_status=0;
 repeat(3)tick;@(negedge clk);rst=0;
end endtask
task error_result(input integer cookie);reg[164:0]v;begin
 #1;if(!result_valid||result_status==0||result_cookie!=cookie||out_valid)$fatal(1,"error completion cookie=%0d actual=%0d status=%0d depth=%0d",cookie,result_cookie,result_status,depth);
 v={result_status,result_detail,result_cookie,result_count,result_raw_count,result_mask,result_hit};
 repeat(4)begin tick;if(!result_valid||{result_status,result_detail,result_cookie,result_count,result_raw_count,result_mask,result_hit}!==v)$fatal(1,"error hold");end
 @(negedge clk);result_ready=1;tick;@(negedge clk);result_ready=0;
 $display("ERROR_RETIRED %0d",cookie);
end endtask
initial begin
 repeat(3)tick;@(negedge clk);rst=0;
 start(10);emit(1,0);emit(2,1);if(out_valid)$fatal(1,"unsealed replay");seal(10,2);item(10,1,0);
 start(20);emit(3,0);seal(20,1);item(20,3,0);result(20,1);item(10,2,1);result(10,2);
 tick;if(depth||busy||fault)$fatal(1,"leaked frame");

 reset_case;start(30);emit(4,0);e_result_status=3;seal(30,1);error_result(30);if(depth||!fault)$fatal(1,"failed root leaked");
 reset_case;start(40);emit(5,0);seal(40,1); // parent item is exposed and must retire during unwind
 start(50);emit(6,0);e_result_status=3;seal(50,1);error_result(50);
 if(!out_valid||out_node!=5)$fatal(1,"parent held child lost");
 @(negedge clk);out_ready=1;tick;@(negedge clk);out_ready=0;error_result(40);if(depth)$fatal(1,"nested error leaked");
 reset_case;
 @(negedge clk);expand_valid=1;expand_cookie=60;expand_parent=61;tick;@(negedge clk);expand_valid=0;abort=1;
 repeat(4)begin tick;if(!e_expand_valid||e_expand_cookie!=60||result_valid)$fatal(1,"aborted offered command");end
 @(negedge clk);e_expand_ready=1;tick;@(negedge clk);e_expand_ready=0;
 emit(7,0);seal(60,1);error_result(60);
 reset_case;start(70);emit(8,0);@(negedge clk);abort=1;
 emit(9,1);emit(10,2);seal(70,3);error_result(70);
 reset_case;start(80);for(integer j=0;j<6;j=j+1)emit(100+j,j);seal(80,6);error_result(80);
 reset_case;start(90);seal(91,0);error_result(90);
 reset_case;start(100);emit(11,3);seal(100,1);error_result(100);
 reset_case;start(110);seal(110,0);tick;
 @(negedge clk);abort=1;
 repeat(4)begin tick;if(!result_valid||result_status||result_cookie!=110)$fatal(1,"offered success mutated by late abort");end
 @(negedge clk);result_ready=1;tick;@(negedge clk);result_ready=0;if(depth||!fault)$fatal(1,"late abort leaked");
 reset_case;start(120);emit(12,0);emit(13,1);seal(120,2);tick;
 @(negedge clk);abort=1;
 repeat(4)begin tick;if(!out_valid||out_node!=12||result_valid)$fatal(1,"offered item lost by late abort");end
 @(negedge clk);out_ready=1;tick;@(negedge clk);out_ready=0;error_result(120);
 $display("SEARCH_CAPTURE_RETIRE_PASS normal_nested=1 failures=9");$finish;
end
initial begin #100000;$fatal(1,"watchdog");end
endmodule
