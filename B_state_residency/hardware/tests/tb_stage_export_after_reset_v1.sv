`timescale 1ns/1ps
module tb_stage_export_after_reset;

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
`ifdef NETLIST
 route_commit_controller dut(.*);
`else
 route_commit_controller #(.MAX_PATH(8),.MAX_CYCLES(256))dut(.*);
`endif

 integer cycles=0;integer accepted=0;integer output_words=0;integer x;
 reg[31:0]import_crc,zero_crc;
 function automatic[31:0]crc_word(input[31:0]old_crc,input[31:0]word);
 reg[31:0]v;begin v=old_crc^word;for(integer z=0;z<32;z=z+1)v=v[0]?(v>>1)^32'hedb88320:v>>1;crc_word=v;end endfunction
 always @(posedge clk)begin
  cycles=cycles+1;if(cycles>2000)$fatal(1,"watchdog");
  if(!rst&&cp_s_valid&&cp_s_ready)accepted=accepted+1;
 end
 task reset_controller;begin
  @(negedge clk);rst=1;repeat(4)@(negedge clk);rst=0;repeat(3)@(negedge clk);
 end endtask
 task command(input bit restore);begin
  wait(cp_ready);@(negedge clk);cp_restore=restore;cp_valid=1;
  do @(posedge clk);while(!cp_ready);
  @(negedge clk);cp_valid=0;
 end endtask
 task response;begin
  wait(cp_rsp_valid);@(negedge clk);if(cp_status!==0)$fatal(1,"CP status %0d",cp_status);
  cp_rsp_ready=1;@(negedge clk);cp_rsp_ready=0;repeat(3)@(negedge clk);
 end endtask
 initial begin
  for(x=0;x<30;x=x+1)saved[x]=0;
  saved[0]=1;saved[1]=1;saved[2]=3;saved[3]=1;saved[4]=2;
  saved[5]=active_design[31:0];saved[6]=active_design[63:32];saved[7]=4;
  import_crc=32'hffffffff;zero_crc=32'hffffffff;
  for(x=0;x<30;x=x+1)begin import_crc=crc_word(import_crc,saved[x]);zero_crc=crc_word(zero_crc,0);end
  import_crc=~import_crc;zero_crc=~zero_crc;
  reset_controller;
  cp_expected_crc=import_crc;command(1);
  for(x=0;x<30;x=x+1)begin
   @(negedge clk);cp_s_valid=1;cp_s_index=x;cp_s_data=saved[x];cp_s_last=x==29;
   do @(posedge clk);while(!cp_s_ready);
   @(negedge clk);cp_s_valid=0;
  end
  response;
  if(accepted!=30||slot_valid!==2'b01)$fatal(1,"import coverage count=%0d slots=%b",accepted,slot_valid);
  $display("PROBE_IMPORT_PASS words=%0d slots=%b",accepted,slot_valid);
  reset_controller;
  if(slot_valid!==0)$fatal(1,"reset slots");
  cp_s_valid=0;command(0);
  for(x=0;x<30;x=x+1)begin
   wait(cp_m_valid);@(negedge clk);
   if(cp_s_valid!==0||cp_m_index!==x||cp_m_last!==(x==29)||cp_m_data!==0)
    $fatal(1,"export mismatch word=%0d index=%0d data=%h last=%b",x,cp_m_index,cp_m_data,cp_m_last);
   repeat(2)begin @(negedge clk);if(!cp_m_valid||cp_m_data!==0||cp_m_index!==x)$fatal(1,"export backpressure");end
   cp_m_ready=1;@(negedge clk);cp_m_ready=0;output_words=output_words+1;
  end
  response;
  if(output_words!=30||cp_crc!==zero_crc)$fatal(1,"export CRC or coverage");
  $display("STAGE_EXPORT_AFTER_RESET_PASS imports=%0d exports=%0d crc=%08h",accepted,output_words,cp_crc);
  $finish;
 end
endmodule
