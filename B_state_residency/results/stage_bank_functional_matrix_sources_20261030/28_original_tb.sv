`timescale 1ns/1ps
module tb_stage_bank_matrix;

 localparam CP_CAPACITY=8;
 reg cp_valid=0,cp_restore=0,cp_safe=1,cp_rsp_ready=0,cp_s_valid=0,cp_s_last=0,cp_m_ready=0;
 wire idle_fault;
 wire cp_ready,cp_busy,cp_rsp_valid,cp_s_ready,cp_m_valid,cp_m_last;
 reg[63:0]cp_design=64'h123456789abcdef0;reg[31:0]cp_nodes=9089009,cp_nets=27960,cp_expected_crc=0,cp_s_index=0,cp_s_data=0;
 wire[3:0]cp_status;wire[31:0]cp_crc,cp_m_index,cp_m_data;
 reg[31:0]saved[0:155],pristine[0:155];reg[31:0]saved_crc;integer cp_checks=0;
 reg preserve_owner=0;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,abort=0,active=1,lease=1;reg[1:0]active_query=1;reg[3:0]active_price=3;reg[31:0]active_version=3;reg[63:0]active_design=64'h123456789abcdef0;
 reg req_valid=0,req_op=0,rsp_ready=0;reg[1:0]req_slot=0;wire req_ready,rsp_valid,busy,fault;reg[31:0]req_cookie=0,req_source=65185,req_sink=150697,req_net=2717,req_sequence=1;
 wire[3:0]rsp_status;wire[31:0]rsp_cookie,rsp_nodes,rsp_acked;wire[3:0]slot_valid;
 wire l_valid,l_rsp_ready,o_valid,o_rsp_ready;reg l_ready=0,l_rsp_valid=0,l_present=1,o_ready=0,o_rsp_valid=0;wire[31:0]l_node,o_node,o_net,o_cookie;wire[2:0]o_op;reg[3:0]l_status=0,o_status=0;reg[159:0]l_payload=0;reg[31:0]o_rsp_cookie=0;
`ifdef NETLIST
 route_commit_controller dut(.*);
`elsif ORIGINAL
 route_commit_controller #(.PATH_SLOTS(4),.PATH_SLOT_BITS(2),.MAX_PATH(32),.MAX_CYCLES(256))dut(.*);
`elsif STAGE_ON
 route_commit_controller #(.STATIC_STAGE_WRITES(1),.PATH_SLOTS(4),.PATH_SLOT_BITS(2),.MAX_PATH(32),.MAX_CYCLES(256))dut(.*);
`else
 route_commit_controller #(.STATIC_STAGE_WRITES(0),.PATH_SLOTS(4),.PATH_SLOT_BITS(2),.MAX_PATH(32),.MAX_CYCLES(256))dut(.*);
`endif

 integer cycles=0,commands=0,imports=0,exports=0,responses=0,checks=0;
 integer x,y,s;
 reg[31:0]expected_crc;
 function automatic[31:0]crc_word(input[31:0]old_crc,input[31:0]word);
 reg[31:0]v;begin v=old_crc^word;for(integer z=0;z<32;z=z+1)v=v[0]?(v>>1)^32'hedb88320:v>>1;crc_word=v;end endfunction
 function automatic[31:0]image_crc(input bit zero_image);
 reg[31:0]v;begin v=32'hffffffff;for(integer z=0;z<156;z=z+1)v=crc_word(v,zero_image?32'b0:pristine[z]);image_crc=~v;end endfunction
 always @(posedge clk)begin
  cycles=cycles+1;if(cycles>100000)$fatal(1,"watchdog");
  if(!rst&&cp_s_valid&&cp_s_ready)begin imports=imports+1;$display("EVT I %0d %0d %08h %0d",cycles,cp_s_index,cp_s_data,cp_s_last);end
 end
 task reset_controller;begin
  @(negedge clk);rst=1;repeat(4)@(negedge clk);rst=0;repeat(3)@(negedge clk);
 end endtask
 task command(input bit restore);begin
  wait(cp_ready);@(negedge clk);cp_restore=restore;cp_valid=1;
  do @(posedge clk);while(!cp_ready);
  $display("EVT C %0d %0d %0d",cycles,commands,restore);commands=commands+1;
  @(negedge clk);cp_valid=0;
 end endtask
 task response(input integer expected);begin
  wait(cp_rsp_valid);@(negedge clk);if(cp_status!==expected)$fatal(1,"CP status got=%0d expected=%0d",cp_status,expected);
  $display("EVT R %0d %0d %0d %08h %b",cycles,responses,cp_status,cp_crc,slot_valid);responses=responses+1;
  cp_rsp_ready=1;@(negedge clk);cp_rsp_ready=0;repeat(3)@(negedge clk);
 end endtask
 task load(input integer mode);integer count;begin
  for(integer z=0;z<156;z=z+1)saved[z]=pristine[z];
  if(mode==1)saved[7]=777;
  if(mode==2)saved[38]=saved[37];
  cp_expected_crc=32'hffffffff;
  for(integer z=0;z<156;z=z+1)cp_expected_crc=crc_word(cp_expected_crc,saved[z]);
  cp_expected_crc=~cp_expected_crc;if(mode==1)cp_expected_crc=cp_expected_crc^1;
  command(1);count=mode==3?5:mode==4?4:156;
  for(integer z=0;z<count;z=z+1)begin
   @(negedge clk);cp_s_valid=1;cp_s_index=(mode==4&&z==3)?4:z;cp_s_data=saved[z];cp_s_last=z==155;
   do @(posedge clk);while(!cp_s_ready);
   @(negedge clk);cp_s_valid=0;
  end
  if(mode==3)begin @(negedge clk);cp_safe=0;repeat(2)@(negedge clk);cp_safe=1;end
  response(mode==0?0:mode==3?2:1);
  if(slot_valid!==4'b1111)$fatal(1,"failed import changed slots");
  checks=checks+1;$display("CASE IMPORT %0d PASS",mode);
 end endtask
 task save_image(input bit zero_image);reg[64:0]held;reg[31:0]want;begin
  cp_s_valid=0;command(0);
  for(integer z=0;z<156;z=z+1)begin
   wait(cp_m_valid);@(negedge clk);want=zero_image?32'b0:pristine[z];
   if(cp_m_data!==want||cp_m_index!==z||cp_m_last!==(z==155))$fatal(1,"export mismatch word=%0d got=%h want=%h",z,cp_m_data,want);
   held={cp_m_last,cp_m_index,cp_m_data};
   repeat(2)begin @(negedge clk);if(!cp_m_valid||{cp_m_last,cp_m_index,cp_m_data}!==held||req_ready)$fatal(1,"backpressure");end
   $display("EVT O %0d %0d %08h %0d",cycles,z,cp_m_data,cp_m_last);exports=exports+1;
   cp_m_ready=1;@(negedge clk);cp_m_ready=0;
  end
  response(0);if(cp_crc!==image_crc(zero_image))$fatal(1,"export CRC");
  checks=checks+1;$display("CASE EXPORT %0d PASS",zero_image);
 end endtask
 initial begin
  #200;
  for(x=0;x<156;x=x+1)pristine[x]=0;
  for(s=0;s<4;s=s+1)begin
   pristine[s*39]=1;pristine[s*39+1]=32;pristine[s*39+2]=3+s;
   pristine[s*39+3]=1;pristine[s*39+4]=2;
   pristine[s*39+5]=active_design[31:0];pristine[s*39+6]=active_design[63:32];
   for(y=0;y<32;y=y+1)pristine[s*39+7+y]=10+s*100+y;
  end
  reset_controller;
  load(0);save_image(0);save_image(0);
  load(1);save_image(0);
  load(2);save_image(0);
  load(3);save_image(0);
  load(4);save_image(0);
  reset_controller;if(slot_valid!==0)$fatal(1,"reset slots");save_image(1);
  if(commands!=12||responses!=12||imports!=477||exports!=1092||checks!=12)$fatal(1,"coverage counts c=%0d r=%0d i=%0d o=%0d checks=%0d",commands,responses,imports,exports,checks);
  $display("STAGE_BANK_MATRIX_PASS commands=%0d responses=%0d imports=%0d exports=%0d checks=%0d cycles=%0d",commands,responses,imports,exports,checks,cycles);
  $finish;
 end
endmodule
