`timescale 1ns/1ps
module tb_cost_inputs_prefetch;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,abort=0,active=1,decision_lock=1,req_valid=0,rsp_ready=0;
 reg [1:0] active_query=2;reg [3:0] active_price=3;
 reg [31:0] active_version=19;reg [63:0] active_design=64'h123456789abcdef0;
 reg [31:0] req_cookie=9,req_node=7,req_net=11;
 wire req_ready,rsp_valid,busy,fault;
 wire [31:0] rsp_cookie,rsp_node,rsp_net,rsp_count,rsp_occupancy,rsp_price_index,rsp_history,rsp_price_value,rsp_version;
 wire [127:0] rsp_net_data;wire [63:0] rsp_design;wire [1:0] rsp_query;wire [3:0] rsp_price,rsp_status;
 wire o_req_valid,o_rsp_ready;reg o_req_ready=0,o_rsp_valid=0;
 wire [31:0] o_req_cookie,o_req_node,o_req_net;
 reg [31:0] o_rsp_cookie=9,o_rsp_count=0,o_rsp_occupancy=0;reg [3:0] o_rsp_status=0;
 wire c_req_valid,c_rsp_ready;reg c_req_ready=0,c_rsp_valid=0;
 wire [2:0] c_req_op;wire [31:0] c_req_cookie,c_req_index,c_req_version;
 wire [1:0] c_req_query;wire [3:0] c_req_price;
 reg [3:0] c_rsp_status=0,c_rsp_price=3;reg [31:0] c_rsp_cookie=9,c_rsp_index=0,c_rsp_version=19;
 reg [2:0] c_rsp_op=0;reg c_rsp_host=0;reg [1:0] c_rsp_query=2;reg [127:0] c_rsp_data=0;
 cost_inputs_prefetch #(.MAX_CYCLES(64)) dut(.*);
 integer r,o,j,refs,index,valid_cases=0,invalid_cases=0,fault_cases=0,mode;
 reg [127:0] net_expected=128'h11112222333344445555666677778888;
 reg [387:0] held;
 initial begin #50000000;$fatal(1,"watchdog");end
 task boot;
 begin @(negedge clk);rst=1;abort=0;active=1;decision_lock=1;active_query=2;active_price=3;active_version=19;active_design=64'h123456789abcdef0;
 req_valid=0;rsp_ready=0;req_cookie=9;req_node=7;req_net=11;
 o_req_ready=0;o_rsp_valid=0;o_rsp_cookie=9;o_rsp_status=0;c_req_ready=0;c_rsp_valid=0;c_rsp_status=0;c_rsp_host=0;c_rsp_version=19;c_rsp_query=2;c_rsp_price=3;c_rsp_cookie=9;
 repeat(3)@(negedge clk);rst=0;end endtask
 task start;
 begin req_valid=1;@(negedge clk);req_valid=0;req_node=999;req_net=999;req_cookie=999;
 if(!o_req_valid||o_req_cookie!=9||o_req_node!=7||o_req_net!=11)$fatal(1,"owner snapshot");end endtask
 task owner_reply(input integer cnt,occ);
 begin repeat(2)begin @(negedge clk);if(!o_req_valid||o_req_node!=7||o_req_net!=11)$fatal(1,"owner request backpressure");end
 o_req_ready=1;@(negedge clk);o_req_ready=0;o_rsp_count=cnt;o_rsp_occupancy=occ;o_rsp_valid=1;
 @(negedge clk);o_rsp_valid=0;#1;end endtask
 task cost_reply(input integer st,idx,bad);
 begin
 while(!c_req_valid)@(negedge clk);
 if(c_req_op!==(st==0?3'd0:st==1?3'd2:3'd6)||c_req_index!==idx||c_req_cookie!=9||c_req_version!=19||c_req_query!=2||c_req_price!=3)$fatal(1,"internal selector stage=%0d index=%0d/%0d",st,c_req_index,idx);
 repeat(2)@(negedge clk);c_req_ready=1;@(negedge clk);c_req_ready=0;
 c_rsp_index=idx;c_rsp_op=c_req_op;c_rsp_data=st==0?128'h3f900000:st==1?(128'h3f000000+index):net_expected;
 if(bad==1)c_rsp_version=35;if(bad==2)c_rsp_host=1;if(bad==3)c_rsp_index=idx+1;if(bad==4)c_rsp_cookie=10;
 c_rsp_valid=1;@(negedge clk);c_rsp_valid=0;#1;
 end endtask
 task assert_stopped;
 begin #1;if(!fault||!busy||req_ready)$fatal(1,"missing stop mode=%0d",mode);
 repeat(3)@(negedge clk);if(!fault||req_ready)$fatal(1,"stop not sticky");fault_cases=fault_cases+1;end endtask
 initial begin
 for(r=0;r<4;r=r+1)for(o=0;o<=258;o=o+1)begin
  refs=r==0?0:r==1?1:r==2?7:65535;index=o-(refs!=0);
  boot();start();owner_reply(refs,o);
  if(index<0||index>255)begin
   if(!rsp_valid||rsp_status!==1||!fault||c_req_valid)$fatal(1,"invalid owner index refs=%0d occ=%0d",refs,o);
   invalid_cases=invalid_cases+1;
  end else begin
   cost_reply(0,7,0);cost_reply(1,index,0);cost_reply(2,11,0);
   if(!rsp_valid||fault||rsp_status||rsp_count!==refs||rsp_occupancy!==o||rsp_price_index!==index||rsp_history!==32'h3f900000||rsp_price_value!==(32'h3f000000+index)||rsp_net_data!==net_expected||rsp_cookie!=9||rsp_node!=7||rsp_net!=11||rsp_version!=19||rsp_design!=64'h123456789abcdef0)$fatal(1,"inputs packet refs=%0d occ=%0d",refs,o);
   held={rsp_status,rsp_count,rsp_occupancy,rsp_price_index,rsp_history,rsp_price_value,rsp_net_data,rsp_version,rsp_design};
   repeat(3)begin @(negedge clk);if(!rsp_valid||req_ready||!busy||{rsp_status,rsp_count,rsp_occupancy,rsp_price_index,rsp_history,rsp_price_value,rsp_net_data,rsp_version,rsp_design}!==held)$fatal(1,"packet backpressure");end
   rsp_ready=1;@(negedge clk);rsp_ready=0;if(busy)$fatal(1,"retire");valid_cases=valid_cases+1;
  end
 end
 for(mode=0;mode<12;mode=mode+1)begin
  boot();start();index=1;
  case(mode)
   0:begin o_rsp_cookie=10;owner_reply(0,1);end
   1:begin o_rsp_status=4;owner_reply(0,1);end
   2,3,4,5:begin owner_reply(0,1);cost_reply(0,7,mode-1);end
   6:active_version=35;
   7:active_design=64'hffffffffffffffff;
   8:active_query=1;
   9:decision_lock=0;
   10:abort=1;
   11:begin repeat(64)@(negedge clk);if(!o_req_valid||o_req_node!=7||o_req_net!=11)$fatal(1,"timeout withdrew request");end
  endcase
  assert_stopped();
 end
 boot();o_rsp_valid=1;assert_stopped();
 if(valid_cases!=1024||invalid_cases!=12||fault_cases!=13)$fatal(1,"coverage count");
 $display("COST_INPUTS_PREFETCH_PASS valid=1024 invalid=12 fault_cases=13");$finish;
 end
endmodule
