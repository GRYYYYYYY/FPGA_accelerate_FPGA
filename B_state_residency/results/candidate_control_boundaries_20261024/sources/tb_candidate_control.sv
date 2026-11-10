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
 integer checks=0,cycles=0,errors=0,test_index;reg[767:0]held;reg[165:0]final_held;
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
 task start_access;
  begin start_metadata();m_rsp_valid=1;a_req_ready=1;tick();@(negedge clk);m_rsp_valid=0;a_req_ready=0;expect_true(dut.state==3,"access waiting");end
 endtask
 task finish_error;
  begin
   @(negedge clk);e_out_valid=0;out_ready=1;
   while(!result_valid)begin
    m_rsp_valid=dut.m_pending;a_rsp_valid=dut.a_pending;e_result_valid=dut.e_pending;
    tick();@(negedge clk);
   end
   m_rsp_valid=0;a_rsp_valid=0;e_result_valid=0;out_ready=0;
   expect_true(result_status==4&&operation_pending&&stopped,"error completion after drains");
   final_held={result_status,result_cookie,result_count,result_expanded_count,result_raw_count,result_mask,result_hit,result_early};
   abort=1;repeat(3)begin tick();expect_true(result_valid&&{result_status,result_cookie,result_count,result_expanded_count,result_raw_count,result_mask,result_hit,result_early}===final_held,"exposed error stable");end
   @(negedge clk);abort=0;result_ready=1;tick();expect_true(!operation_pending&&stopped&&!expand_ready,"error retirement stops admission");errors=errors+1;
  end
 endtask
 initial begin
  reset_case();start_metadata();abort=1;tick();@(negedge clk);abort=0;e_out_valid=0;e_result_valid=1;tick();@(negedge clk);e_result_valid=0;
  repeat(3)begin tick();expect_true(operation_pending&&!result_valid,"final must await accepted metadata reply drain");end
  @(negedge clk);m_rsp_valid=1;#1;expect_true(m_rsp_ready,"drain metadata reply");tick();@(negedge clk);m_rsp_valid=0;
  repeat(2)tick();expect_true(result_valid&&result_status==4&&operation_pending,"error after drain");
  @(negedge clk);result_ready=1;tick();expect_true(!operation_pending&&stopped&&!expand_ready,"stopped after error retirement");
  errors=errors+1;
  // An accepted access reply must also drain after the expansion has finished.
  reset_case();start_access();abort=1;tick();@(negedge clk);abort=0;e_out_valid=0;e_result_valid=1;tick();@(negedge clk);e_result_valid=0;
  repeat(3)begin tick();expect_true(operation_pending&&!result_valid,"final awaits access drain");end
  finish_error();
  // Metadata status/created and all identity fields.
  for(test_index=0;test_index<9;test_index=test_index+1)begin
   reset_case();start_metadata();
   case(test_index)
    0:m_rsp_status=1;1:m_rsp_created=0;2:m_rsp_cookie=9;3:m_rsp_parent=9;4:m_rsp_child=9;5:m_rsp_sink=9;6:m_rsp_net=9;7:m_rsp_query=1;8:m_rsp_price=1;
   endcase
   m_rsp_valid=1;tick();@(negedge clk);m_rsp_valid=0;expect_true(stopped&&!a_req_valid,"bad metadata does not start access");finish_error();
  end
  // Access status and complete identity echo.
  for(test_index=0;test_index<8;test_index=test_index+1)begin
   reset_case();start_access();
   case(test_index)
    0:a_rsp_status=1;1:a_rsp_cookie=9;2:a_rsp_parent=9;3:a_rsp_child=9;4:a_rsp_sink=9;5:a_rsp_net=9;6:a_rsp_query=1;7:a_rsp_price=1;
   endcase
   a_rsp_valid=1;tick();@(negedge clk);expect_true(stopped&&!out_valid,"bad access does not expose child");finish_error();
  end
  // Active/query/price drift with metadata outstanding.
  for(test_index=0;test_index<3;test_index=test_index+1)begin
   reset_case();start_metadata();case(test_index)0:active=0;1:active_query=1;2:active_price=1;endcase
   tick();expect_true(stopped,"context drift");finish_error();
  end
  reset_case();start_metadata();repeat(34)tick();expect_true(stopped&&!result_valid&&operation_pending,"timeout retains pending lock");finish_error();
  // Late abort cannot change a child already exposed under backpressure.
  reset_case();start_access();a_rsp_valid=1;tick();@(negedge clk);expect_true(out_valid,"child exposed");held={out_config,out_attrs,out_bits,out_action};abort=1;
  repeat(4)begin tick();expect_true(out_valid&&{out_config,out_attrs,out_bits,out_action}===held&&operation_pending,"late abort child stable");end
  finish_error();
  // Global error coincident with final expansion handshake must terminate.
  reset_case();start_operation();e_result_valid=1;abort=1;tick();@(negedge clk);e_result_valid=0;abort=0;finish_error();
  reset_case();start_operation();e_result_valid=1;e_result_cookie=99;tick();@(negedge clk);e_result_valid=0;finish_error();
  // Idle replies without request ownership cannot fabricate a response.
  for(test_index=0;test_index<3;test_index=test_index+1)begin
   reset_case();case(test_index)0:m_rsp_valid=1;1:a_rsp_valid=1;2:e_result_valid=1;endcase
   tick();expect_true(stopped&&!operation_pending&&!result_valid&&!expand_ready,"unowned idle reply");
  end
  // Invalid descriptors are nonfatal and cause no expansion side effect.
  reset_case();@(negedge clk);expand_parent=100;expand_valid=1;#1;expect_true(expand_ready&&!e_expand_valid,"invalid descriptor no backend");tick();@(negedge clk);expand_valid=0;
  expect_true(result_valid&&result_status==1&&!stopped,"invalid descriptor response");result_ready=1;tick();expect_true(!operation_pending&&!stopped,"invalid descriptor recovers");
  // Normal exposed final remains stable after a late subsystem fault.
  reset_case();start_operation();e_out_valid=0;e_result_valid=1;tick();@(negedge clk);e_result_valid=0;expect_true(result_valid&&result_status==0,"normal final");
  subsystem_fault=1;repeat(3)begin tick();expect_true(result_valid&&result_status==0&&operation_pending,"late final fault stability");end
  $display("CANDIDATE_CONTROL_PASS checks=%0d errors=%0d cycles=%0d",checks,errors,cycles);$finish;
 end

endmodule
