`timescale 1ns/1ps
module tb_route_commit;

 integer bank_fd,bank_cycle=0;reg bank_seen=0;string bank_path;
 reg[31:0]bank_previous[0:1][0:7];

 wire idle_fault;
 localparam CP_CAPACITY=8;
 reg cp_valid=0,cp_restore=0,cp_safe=1,cp_rsp_ready=0,cp_s_valid=0,cp_s_last=0,cp_m_ready=0;
 wire cp_ready,cp_busy,cp_rsp_valid,cp_s_ready,cp_m_valid,cp_m_last;
 reg[63:0]cp_design=64'h123456789abcdef0;reg[31:0]cp_nodes=9089009,cp_nets=27960,cp_expected_crc=0,cp_s_index=0,cp_s_data=0;
 wire[3:0]cp_status;wire[31:0]cp_crc,cp_m_index,cp_m_data;
 reg[31:0]saved[0:29],pristine[0:29];reg[31:0]saved_crc;integer cp_checks=0;
 reg preserve_owner=0;

 reg clk=0;always #5 clk=~clk;
 reg rst=1,abort=0,active=1,lease=1;reg[1:0]active_query=1;reg[3:0]active_price=3;reg[31:0]active_version=3;reg[63:0]active_design=64'h123456789abcdef0;
 reg req_valid=0,req_op=0,req_slot=0,rsp_ready=0;wire req_ready,rsp_valid,busy,fault;reg[31:0]req_cookie=0,req_source=65185,req_sink=150697,req_net=2717,req_sequence=1;
 wire[3:0]rsp_status;wire[31:0]rsp_cookie,rsp_nodes,rsp_acked;wire[1:0]slot_valid;
 wire l_valid,l_rsp_ready,o_valid,o_rsp_ready;reg l_ready=0,l_rsp_valid=0,l_present=1,o_ready=0,o_rsp_valid=0;wire[31:0]l_node,o_node,o_net,o_cookie;wire[2:0]o_op;reg[3:0]l_status=0,o_status=0;reg[159:0]l_payload=0;reg[31:0]o_rsp_cookie=0;
 route_commit_controller #(.FACTORED_PATH_WRITES(1),.MAX_PATH(8),.MAX_CYCLES(256))dut(.*);

 integer events,ticks=0;string path;
 always @(posedge clk)begin ticks=ticks+1;if(ticks>200)$fatal(1,"overlap watchdog");end
 initial begin
  if(!$value$plusargs("events=%s",path))$fatal(1,"events path");events=$fopen(path,"w");
  repeat(3)@(negedge clk);rst=0;
  @(negedge clk);req_valid=1;
  do @(posedge clk);while(!req_ready);
  @(negedge clk);req_valid=0;
  wait(l_valid);@(negedge clk);l_ready=1;l_rsp_valid=1;
  #1;
  if(dut.state!=1||dut.unexpected!=0||fault!=0)$fatal(1,"generic overlap contract mismatch");
  $fdisplay(events,"OVERLAP %0d %0d %0d",dut.state,dut.unexpected,fault);
  $fflush(events);$fclose(events);
  $display("ROUTE_PATH_OVERLAP_PASS specialized=0 unexpected=%0d",dut.unexpected);
  $finish;
 end
 initial begin
  if(!$value$plusargs("bank_events=%s",bank_path))$fatal(1,"bank events path");
  bank_fd=$fopen(bank_path,"w");if(!bank_fd)$fatal(1,"bank events open");
 end
 always @(negedge clk)begin
  bank_cycle=bank_cycle+1;
  for(integer bank_slot=0;bank_slot<2;bank_slot=bank_slot+1)
   for(integer bank_word=0;bank_word<8;bank_word=bank_word+1)begin
    if(!bank_seen||dut.path[bank_slot][bank_word]!==bank_previous[bank_slot][bank_word])
     $fdisplay(bank_fd,"BANK %0d %0d %0d %08h",bank_cycle,bank_slot,bank_word,dut.path[bank_slot][bank_word]);
    bank_previous[bank_slot][bank_word]=dut.path[bank_slot][bank_word];
   end
  bank_seen=1;$fflush(bank_fd);
 end

endmodule
