`timescale 1ns/1ps
module tb_recursive_candidate_controller;
reg [31:0] active_version=0;
reg [63:0] active_design=0;
wire [511:0] e_context;
wire [31:0] e_depth;
wire [511:0] e_expand_context;
wire [31:0] out_parent;
wire [31:0] out_root_cookie;
reg  clk=0;
reg  rst=0;
reg  enable=0;
reg  abort=0;
reg  subsystem_fault=0;
reg [31:0] nodes=0;
reg  active=0;
reg [1:0] active_query=0;
reg [3:0] active_price=0;
reg  expand_valid=0;
wire  expand_ready;
reg [31:0] expand_cookie=0;
reg [31:0] expand_parent=0;
reg [31:0] expand_prune=0;
reg [31:0] expand_has_laguna=0;
reg [31:0] expand_sink=0;
reg [31:0] expand_net=0;
reg [31:0] expand_sequence=0;
reg [31:0] expand_flags=0;
reg [31:0] expand_xmin=0;
reg [31:0] expand_xmax=0;
reg [31:0] expand_ymin=0;
reg [31:0] expand_ymax=0;
wire  out_valid;
reg  out_ready=0;
wire [31:0] out_cookie;
wire [31:0] out_node;
wire [31:0] out_position;
wire [31:0] out_sequence;
wire [31:0] out_bits;
wire [31:0] out_action;
wire [31:0] out_steps;
wire [31:0] out_services;
wire [255:0] out_attrs;
wire [447:0] out_config;
wire  result_valid;
reg  result_ready=0;
wire [3:0] result_status;
wire [31:0] result_cookie;
wire [31:0] result_count;
wire [31:0] result_expanded_count;
wire [31:0] result_raw_count;
wire [31:0] result_mask;
wire  result_hit;
wire  result_early;
wire  operation_pending;
wire  stopped;
wire  e_expand_valid;
wire  e_expand_ready;
wire [31:0] e_expand_cookie;
wire [31:0] e_expand_parent;
wire [31:0] e_expand_prune;
wire [31:0] e_expand_has_laguna;
wire  e_out_valid;
wire  e_out_ready;
wire [31:0] e_out_node;
wire [31:0] e_out_position;
wire [31:0] e_out_sequence;
wire [255:0] e_out_attrs;
wire  e_result_valid;
wire  e_result_ready;
wire [3:0] e_result_status;
wire [31:0] e_result_cookie;
wire [31:0] e_result_count;
wire [31:0] e_result_raw_count;
wire [31:0] e_result_mask;
wire  e_result_hit;
wire  m_req_valid;
reg  m_req_ready=0;
wire [31:0] m_req_cookie;
wire [31:0] m_req_parent;
wire [31:0] m_req_child;
wire [31:0] m_req_sink;
wire [31:0] m_req_net;
wire [31:0] m_req_sequence;
wire [31:0] m_req_flags;
wire [31:0] m_req_xmin;
wire [31:0] m_req_xmax;
wire [31:0] m_req_ymin;
wire [31:0] m_req_ymax;
wire [1:0] m_req_query;
wire [3:0] m_req_price;
reg  m_rsp_valid=0;
wire  m_rsp_ready;
reg [3:0] m_rsp_status=0;
reg [31:0] m_rsp_cookie=0;
reg [31:0] m_rsp_parent=0;
reg [31:0] m_rsp_child=0;
reg [31:0] m_rsp_sink=0;
reg [31:0] m_rsp_net=0;
reg [1:0] m_rsp_query=0;
reg [3:0] m_rsp_price=0;
reg [447:0] m_rsp_config=0;
reg  m_rsp_created=0;
wire  a_req_valid;
reg  a_req_ready=0;
wire [31:0] a_req_cookie;
wire [31:0] a_req_parent;
wire [31:0] a_req_child;
wire [31:0] a_req_sink;
wire [31:0] a_req_net;
wire [1:0] a_req_query;
wire [3:0] a_req_price;
wire [447:0] a_req_config;
reg  a_rsp_valid=0;
wire  a_rsp_ready;
reg [3:0] a_rsp_status=0;
reg [31:0] a_rsp_cookie=0;
reg [31:0] a_rsp_parent=0;
reg [31:0] a_rsp_child=0;
reg [31:0] a_rsp_sink=0;
reg [31:0] a_rsp_net=0;
reg [31:0] a_rsp_bits=0;
reg [31:0] a_rsp_action=0;
reg [31:0] a_rsp_steps=0;
reg [31:0] a_rsp_services=0;
reg [1:0] a_rsp_query=0;
reg [3:0] a_rsp_price=0;
always #5 clk=~clk;
recursive_candidate_controller #(.MAX_CYCLES(10000)) d(.*);
wire b_expand_valid;
wire b_expand_ready;
wire [31:0] b_expand_cookie;
wire [31:0] b_expand_parent;
wire [31:0] b_expand_prune;
wire [31:0] b_expand_has_laguna;
wire b_out_valid;
wire b_out_ready;
wire [31:0] b_out_node;
wire [31:0] b_out_position;
wire [31:0] b_out_sequence;
wire [255:0] b_out_attrs;
wire b_result_valid;
wire b_result_ready;
wire [3:0] b_result_status;
wire [31:0] b_result_detail;
wire [31:0] b_result_cookie;
wire [31:0] b_result_count;
wire [31:0] b_result_raw_count;
wire [31:0] b_result_mask;
wire b_result_hit;
wire cap_fault,cap_busy;wire[31:0]e_result_detail;
expansion_capture #(.DEPTH(16),.CAPACITY(4)) capture(
.clk(clk),.rst(rst),.abort(abort),.expand_context(e_expand_context),.out_context(e_context),.busy(cap_busy),.fault(cap_fault),.depth(e_depth),
.expand_valid(e_expand_valid),
.expand_ready(e_expand_ready),
.expand_cookie(e_expand_cookie),
.expand_parent(e_expand_parent),
.expand_prune(e_expand_prune),
.expand_has_laguna(e_expand_has_laguna),
.out_valid(e_out_valid),
.out_ready(e_out_ready),
.out_node(e_out_node),
.out_position(e_out_position),
.out_sequence(e_out_sequence),
.out_attrs(e_out_attrs),
.result_valid(e_result_valid),
.result_ready(e_result_ready),
.result_status(e_result_status),
.result_detail(e_result_detail),
.result_cookie(e_result_cookie),
.result_count(e_result_count),
.result_raw_count(e_result_raw_count),
.result_mask(e_result_mask),
.result_hit(e_result_hit),
.e_expand_valid(b_expand_valid),
.e_expand_ready(b_expand_ready),
.e_expand_cookie(b_expand_cookie),
.e_expand_parent(b_expand_parent),
.e_expand_prune(b_expand_prune),
.e_expand_has_laguna(b_expand_has_laguna),
.e_out_valid(b_out_valid),
.e_out_ready(b_out_ready),
.e_out_node(b_out_node),
.e_out_position(b_out_position),
.e_out_sequence(b_out_sequence),
.e_out_attrs(b_out_attrs),
.e_result_valid(b_result_valid),
.e_result_ready(b_result_ready),
.e_result_status(b_result_status),
.e_result_detail(b_result_detail),
.e_result_cookie(b_result_cookie),
.e_result_count(b_result_count),
.e_result_raw_count(b_result_raw_count),
.e_result_mask(b_result_mask),
.e_result_hit(b_result_hit));
integer scenario=0,cycles=0,pstate=0,pparent=0,pcookie=0,pindex=0,pcount=0,pdelay=0;
integer decisions=0,reads=0,expansions=0,max_depth=0;reg[15:0]visited=0;
function integer degree(input integer node);begin
 if(scenario==4)degree=0;
 else if(scenario==3)degree=node<8?1:0;
 else if(node==0)degree=2;
 else if(node==1)degree=1;
 else if(scenario==1&&node==3)degree=1;
 else degree=0;
end endfunction
function integer kid(input integer node,index);begin
 if(scenario==3)kid=node+1;
 else if(node==0)kid=index+1;
 else if(scenario==1&&node==1)kid=3;
 else kid=2;
end endfunction
assign b_expand_ready=pstate==0;
assign b_out_valid=pstate==2;
assign b_out_node=kid(pparent,pindex);
assign b_out_position=pindex;
assign b_out_sequence=pindex;
assign b_out_attrs={224'habcdef,b_out_node};
assign b_result_valid=pstate==3;
assign b_result_status=0;assign b_result_detail=0;assign b_result_cookie=pcookie;
assign b_result_count=pcount;assign b_result_raw_count=pcount;assign b_result_mask=(1<<pcount)-1;assign b_result_hit=0;
always @(posedge clk)begin
 cycles<=cycles+1;
 if(rst)begin pstate<=0;visited<=0;m_rsp_valid<=0;a_rsp_valid<=0;decisions<=0;reads<=0;expansions<=0;max_depth<=0;end
 else begin
  if(cap_fault||(stopped&&scenario<5))$fatal(1,"unexpected fault scenario=%0d state=%0d depth=%0d cf=%b",scenario,d.state,e_depth,cap_fault);
  if(e_depth>max_depth)max_depth<=e_depth;
  if(pstate==0&&b_expand_valid&&b_expand_ready)begin
   pparent<=b_expand_parent;pcookie<=b_expand_cookie;pcount<=degree(b_expand_parent);pindex<=0;pdelay<=3;pstate<=1;expansions<=expansions+1;
   $display("E %0d %0d %0d",scenario,b_expand_cookie,b_expand_parent);
  end
  if(pstate==1)begin if(pdelay==0)pstate<=pcount==0?3:2;else pdelay<=pdelay-1;end
  if(b_out_valid&&b_out_ready)begin if(pindex+1==pcount)pstate<=3;else pindex<=pindex+1;end
  if(b_result_valid&&b_result_ready)pstate<=0;
  if(m_rsp_valid&&m_rsp_ready)m_rsp_valid<=0;
  if(m_req_valid&&m_req_ready)begin
   if(m_rsp_valid)$fatal(1,"metadata overlap");
   if(m_req_parent!=out_parent||m_req_net!=5||m_req_sink!=15||m_req_sequence!=77||m_req_flags!=4||m_req_xmin!=1||m_req_xmax!=20||m_req_ymin!=2||m_req_ymax!=30||m_req_query!=2||m_req_price!=3)$fatal(1,"restored metadata context");
   m_rsp_valid<=1;m_rsp_status<=0;m_rsp_created<=1;m_rsp_cookie<=m_req_cookie;m_rsp_parent<=m_req_parent;m_rsp_child<=m_req_child;m_rsp_sink<=m_req_sink;m_rsp_net<=m_req_net;m_rsp_query<=m_req_query;m_rsp_price<=m_req_price;m_rsp_config<={384'habcdef,32'h12345678,32'd77};
   $display("M %0d %0d %0d %0d",scenario,d.frame_cookie,m_req_parent,m_req_child);
  end
  if(a_rsp_valid&&a_rsp_ready)a_rsp_valid<=0;
  if(a_req_valid&&a_req_ready)begin
   if(a_rsp_valid)$fatal(1,"access overlap");
   reads<=reads+1;a_rsp_valid<=1;a_rsp_status<=0;a_rsp_cookie<=a_req_cookie;a_rsp_parent<=a_req_parent;a_rsp_child<=a_req_child;a_rsp_sink<=a_req_sink;a_rsp_net<=a_req_net;a_rsp_query<=a_req_query;a_rsp_price<=a_req_price;a_rsp_steps<=1;a_rsp_services<=1;
   if(visited[a_req_child])begin a_rsp_action<=0;a_rsp_bits<=0;end
   else if(scenario==2&&a_req_child==2)begin a_rsp_action<=1;a_rsp_bits<=4;end
   else begin a_rsp_action<=(scenario==3||a_req_parent==0||(scenario==1&&a_req_child==3))?2:1;a_rsp_bits<=0;end
   $display("R %0d %0d %0d %0d",scenario,a_req_parent,a_req_child,visited[a_req_child]);
  end
  if(out_valid&&out_ready)begin
   decisions<=decisions+1;
   if(out_action!=0)visited[out_node]<=1;
   if(out_config!=={384'habcdef,32'h12345678,32'd77})$fatal(1,"config altered");
   $display("O %0d %0d %0d %0d %0d",scenario,out_cookie,out_parent,out_node,out_action);
  end
 end
end
reg[543:0]held;reg holding=0;
always @(negedge clk)begin
 if(rst)holding=0;
 else begin
  if(holding&&(!out_valid||{out_parent,out_cookie,out_node,out_position,out_sequence,out_bits,out_action,out_steps,out_services,out_attrs}!==held))$fatal(1,"output/parent changed during backpressure");
  out_ready=cycles%5==0;
  holding=out_valid&&!out_ready;held={out_parent,out_cookie,out_node,out_position,out_sequence,out_bits,out_action,out_steps,out_services,out_attrs};
 end
end
task tick;begin @(posedge clk);#1;end endtask
task run_case(input integer mode,expected_decisions,expected_expansions,expected_depth,expected_early);reg[196:0]r;begin
 @(negedge clk);scenario=mode;rst=1;expand_valid=0;result_ready=0;repeat(3)tick;
 @(negedge clk);rst=0;enable=1;nodes=16;active=1;active_query=2;active_price=3;active_version=32'h12340009;active_design=64'habcdef0198765432;m_req_ready=1;a_req_ready=1;
 expand_cookie=100;expand_parent=0;expand_prune=0;expand_has_laguna=1;expand_sink=15;expand_net=5;expand_sequence=77;expand_flags=4;expand_xmin=1;expand_xmax=20;expand_ymin=2;expand_ymax=30;expand_valid=1;
 #1;if(!expand_ready)$fatal(1,"root not ready");tick;@(negedge clk);expand_valid=0;expand_parent=99;expand_net=99;
 wait(result_valid);@(negedge clk);
 if(result_status||result_cookie!=100||result_count!=expected_decisions||decisions!=expected_decisions||reads!=expected_decisions||expansions!=expected_expansions||max_depth!=expected_depth||result_early!=expected_early||out_root_cookie!=100||out_parent!=0||result_expanded_count!=(mode==2?3:expected_decisions)||result_raw_count!=(mode==2?3:expected_decisions)||result_mask!=((1<<degree(0))-1))$fatal(1,"case summary mode=%0d st=%0d decisions=%0d reads=%0d expands=%0d depth=%0d early=%0d",mode,result_status,decisions,reads,expansions,max_depth,result_early);
 r={result_status,32'b0,result_cookie,result_count,result_expanded_count,result_raw_count,result_mask,result_hit};
 repeat(3)begin tick;if(!result_valid||{result_status,32'b0,result_cookie,result_count,result_expanded_count,result_raw_count,result_mask,result_hit}!==r)$fatal(1,"final hold");end
 @(negedge clk);result_ready=1;tick;@(negedge clk);result_ready=0;tick;if(operation_pending||cap_busy||e_depth)$fatal(1,"ownership leak");
 $display("CASE %0d PASS decisions=%0d expansions=%0d depth=%0d early=%0d",mode,decisions,expansions,max_depth,result_early);
end endtask
task run_stop(input integer mode);begin
 @(negedge clk);scenario=mode;rst=1;expand_valid=0;result_ready=0;repeat(3)tick;
 @(negedge clk);rst=0;enable=1;nodes=16;active=1;active_query=2;active_price=3;active_version=32'h12340009;active_design=64'habcdef0198765432;m_req_ready=1;a_req_ready=1;
 expand_cookie=mode==5?32'hffffffff:100;expand_parent=0;expand_prune=0;expand_has_laguna=1;expand_sink=15;expand_net=5;expand_sequence=77;expand_flags=4;expand_xmin=1;expand_xmax=20;expand_ymin=2;expand_ymax=30;expand_valid=1;
 tick;@(negedge clk);expand_valid=0;
 if(mode==6)begin wait(out_valid);@(negedge clk);active_version=32'h22340009;end
 wait(result_valid);@(negedge clk);
 if(!stopped||result_status!=4||decisions!=1||reads!=1||expansions!=1||e_depth||cap_busy||d.cookie_counter!=(mode==5?32'hffffffff:100))$fatal(1,"stop boundary mode=%0d status=%0d decisions=%0d reads=%0d expansions=%0d depth=%0d",mode,result_status,decisions,reads,expansions,e_depth);
 repeat(3)begin tick;if(!result_valid||result_status!=4||expand_ready)$fatal(1,"terminal hold");end
 @(negedge clk);result_ready=1;tick;@(negedge clk);result_ready=0;tick;if(operation_pending||expand_ready)$fatal(1,"stop reopened");
 $display("STOP %0d PASS status=4 decisions=1 expansions=1",mode);
end endtask
initial begin
 run_case(0,3,2,2,0);run_case(1,4,3,3,0);run_case(2,2,2,2,1);run_case(3,8,9,9,0);run_case(4,0,1,1,0);
 run_stop(5);run_stop(6);
 $display("RECURSIVE_CONTROLLER_PASS cases=7");$finish;
end
initial begin #1000000;$fatal(1,"watchdog");end
endmodule
