`timescale 1ns/1ps
module tb_candidate_control;
reg clk=0;always #5 clk=~clk;
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
reg  e_expand_ready=0;
wire [31:0] e_expand_cookie;
wire [31:0] e_expand_parent;
wire [31:0] e_expand_prune;
wire [31:0] e_expand_has_laguna;
reg  e_out_valid=0;
wire  e_out_ready;
reg [31:0] e_out_node=0;
reg [31:0] e_out_position=0;
reg [31:0] e_out_sequence=0;
reg [255:0] e_out_attrs=0;
reg  e_result_valid=0;
wire  e_result_ready;
reg [3:0] e_result_status=0;
reg [31:0] e_result_cookie=0;
reg [31:0] e_result_count=0;
reg [31:0] e_result_raw_count=0;
reg [31:0] e_result_mask=0;
reg  e_result_hit=0;
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
candidate_controller #(.MAX_CYCLES(32))dut(.*);
 integer checks=0,cycles=0;
 always @(posedge clk)begin cycles<=cycles+1;if(cycles>10000)$fatal(1,"watchdog");end
 task tick;begin @(posedge clk);#1;end endtask
 task expect_true(input bit value,input string message);begin if(!value)$fatal(1,"%s state=%0d",message,dut.state);checks=checks+1;end endtask
 task reset_case;
  begin
   @(negedge clk);rst=1;abort=0;subsystem_fault=0;active=1;active_query=2;active_price=4;enable=1;nodes=100;
   expand_valid=0;out_ready=0;result_ready=0;e_expand_ready=1;e_out_valid=0;e_result_valid=0;m_req_ready=0;m_rsp_valid=0;a_req_ready=0;a_rsp_valid=0;
   expand_parent=1;expand_sink=3;expand_net=7;expand_sequence=17;expand_cookie=91;expand_flags=0;expand_prune=0;expand_has_laguna=0;
   e_result_status=0;e_result_cookie=91;e_result_count=1;e_result_raw_count=1;e_result_mask=1;e_result_hit=0;
   m_rsp_status=0;m_rsp_created=1;m_rsp_cookie=0;m_rsp_parent=1;m_rsp_child=2;m_rsp_sink=3;m_rsp_net=7;m_rsp_query=2;m_rsp_price=4;m_rsp_config=448'h1234;
   a_rsp_status=0;a_rsp_cookie=0;a_rsp_parent=1;a_rsp_child=2;a_rsp_sink=3;a_rsp_net=7;a_rsp_query=2;a_rsp_price=4;a_rsp_bits=0;a_rsp_action=1;a_rsp_steps=4;a_rsp_services=3;
   tick();@(negedge clk);rst=0;tick();
  end
 endtask
 task start_operation;
  begin @(negedge clk);expand_valid=1;#1;expect_true(expand_ready&&e_expand_valid,"expansion handshake");tick();@(negedge clk);expand_valid=0;expect_true(operation_pending,"operation lock");end
 endtask
 task start_metadata;
  begin start_operation();e_out_valid=1;e_out_node=2;e_out_position=0;e_out_sequence=0;e_out_attrs=256'h5678;m_req_ready=1;tick();@(negedge clk);m_req_ready=0;expect_true(dut.state==2,"metadata waiting");end
 endtask
 initial begin
  reset_case();start_metadata();abort=1;tick();@(negedge clk);abort=0;e_out_valid=0;e_result_valid=1;tick();@(negedge clk);e_result_valid=0;
  repeat(3)begin tick();expect_true(operation_pending&&!result_valid,"final must await accepted metadata reply drain");end
  @(negedge clk);m_rsp_valid=1;#1;expect_true(m_rsp_ready,"drain metadata reply");tick();@(negedge clk);m_rsp_valid=0;
  repeat(2)tick();expect_true(result_valid&&result_status==4&&operation_pending,"error after drain");
  @(negedge clk);result_ready=1;tick();expect_true(!operation_pending&&stopped&&!expand_ready,"stopped after error retirement");
  $display("CANDIDATE_CONTROL_PASS checks=%0d cycles=%0d",checks,cycles);$finish;
 end

endmodule
