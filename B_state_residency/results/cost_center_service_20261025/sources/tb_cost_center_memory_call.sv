`timescale 1ns/1ps
module tb_cost_center_memory_call;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,abort=0,active=1,req_valid=0,rsp_ready=0;
 reg [1:0] active_query=2,req_query=2;
 reg [3:0] active_price=3,req_price=3;
 reg [31:0] active_version=19,req_version=19,req_cookie=7;
 reg [127:0] req_words=128'h44444444333333332222222211111111;
 wire req_ready,rsp_valid,busy,fault,ap_start;
 wire [63:0] rsp_words;wire [31:0] rsp_cookie,rsp_version;
 wire [1:0] rsp_query,rsp_status;wire [3:0] rsp_price;
 reg ap_idle=1,ap_ready=0,ap_done=0;
 reg [1:0] ia0=0;reg ic0=0;wire [31:0] iq0;
 reg [0:0] oa0=0,oa1=0;reg oc0=0,oc1=0,ow0=0,ow1=0;
 reg [31:0] od0=0,od1=0;
 cost_center_memory_call #(.MAX_CALL_CYCLES(16)) dut(.*);
 integer mode,i,cases=0;
 initial begin #1000000;$fatal(1,"watchdog");end
 task reset_all;
 begin @(negedge clk);rst=1;abort=0;active=1;active_query=2;active_price=3;active_version=19;
 req_valid=0;rsp_ready=0;ap_idle=1;ap_ready=0;ap_done=0;ic0=0;oc0=0;oc1=0;ow0=0;ow1=0;
 req_words=128'h44444444333333332222222211111111;
 repeat(3)@(negedge clk);rst=0;end endtask
 task start;
 begin req_valid=1;@(negedge clk);req_valid=0;req_words=0;if(!ap_start)$fatal(1,"start");end endtask
 task writes;
 begin oc0=1;ow0=1;oa0=1;od0=32'hdeadbeef;oc1=1;ow1=1;oa1=0;od1=0;end endtask
 task expect_fault;
 begin #1;if(!fault||req_ready||!busy)$fatal(1,"expected fault mode=%0d",mode);
 @(negedge clk);ap_done=0;ap_ready=0;oc0=0;oc1=0;ow0=0;ow1=0;ic0=0;abort=0;active=1;active_query=2;active_price=3;active_version=19;
 @(negedge clk);if(!fault||req_ready)$fatal(1,"not sticky");cases=cases+1;end endtask
 initial begin
 // All four input addresses return latched words despite request mutation.
 reset_all();start();for(i=0;i<4;i=i+1)begin ic0=1;ia0=i;@(negedge clk);
 if(iq0!==32'h11111111*(i+1))$fatal(1,"snapshot address %0d",i);end ic0=0;
 // Reversed physical ports, both final writes on done edge.
 writes();ap_done=1;ap_ready=1;@(negedge clk);oc0=0;oc1=0;ow0=0;ow1=0;ap_done=0;ap_ready=0;
 if(!rsp_valid||rsp_words!==64'hdeadbeef00000000||fault)$fatal(1,"done writes");
 repeat(4)begin @(negedge clk);if(!busy||req_ready||!rsp_valid||rsp_words!==64'hdeadbeef00000000)$fatal(1,"hold");end
 rsp_ready=1;@(negedge clk);rsp_ready=0;if(busy)$fatal(1,"retire");cases=cases+1;
 // Separate early output writes, then done without a write.
 reset_all();start();oc0=1;ow0=1;oa0=0;od0=0;@(negedge clk);oa0=1;od0=7;
 @(negedge clk);oc0=0;ow0=0;ap_done=1;ap_ready=1;@(negedge clk);
 ap_done=0;ap_ready=0;if(!rsp_valid||rsp_words!==64'h0000000700000000||fault)$fatal(1,"early writes");cases=cases+1;
 for(mode=0;mode<12;mode=mode+1)begin
 reset_all();start();
 case(mode)
 0:begin writes();oa1=1;end // simultaneous duplicate
 1:begin writes();oc1=0;ap_done=1;ap_ready=1;end // missing output
 2:ap_done=1;
 3:ap_ready=1;
 4:begin oc0=1;ow0=1;oa0=0;@(negedge clk);end // repeated write
 5:active=0;
 6:active_query=1;
 7:active_price=4;
 8:active_version=35; // same low tag
 9:abort=1;
 10:repeat(15)@(negedge clk); // timeout last allowed edge
 11:begin writes();ap_done=1;ap_ready=1;@(negedge clk);
 ap_done=0;ap_ready=0;oc0=0;oc1=0;ow0=0;ow1=0;active_version=35;end
 endcase
 expect_fault();end
 // Exact timeout boundary: complete on cycle16 is legal.
 reset_all();start();repeat(15)@(negedge clk);writes();ap_done=1;ap_ready=1;
 #1;if(fault)$fatal(1,"completion precedence");@(negedge clk);
 ap_done=0;ap_ready=0;oc0=0;oc1=0;ow0=0;ow1=0;
 if(!rsp_valid||fault)$fatal(1,"boundary completion");cases=cases+1;
 reset_all();ic0=1;expect_fault(); // stray event in idle
 $display("COST_CENTER_MEMORY_CALL_PASS cases=%0d",cases);$finish;
 end
endmodule
