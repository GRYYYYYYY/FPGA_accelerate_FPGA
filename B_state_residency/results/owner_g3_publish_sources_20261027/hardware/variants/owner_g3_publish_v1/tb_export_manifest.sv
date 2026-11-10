`timescale 1ns/1ps
module tb_export_manifest;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,lease=1,arm=0,abort=0,source_write=0,published=0;
 reg[63:0]active_design=64'h123456789abcdef0,target_generation=64'h100000003,selected_design=64'h123456789abcdef0,selected_generation=64'h100000003;
 reg[31:0]target_checkpoint=19,active_version=5,active_sequence=180328,selected_checkpoint=19,selected_version=5;
 reg[1:0]active_query=3,selected_query=3,active_slots=3;reg[3:0]active_price=5,selected_price=5;
 reg owner_manifest=1,label_manifest=1;
 reg label_accept=0,label_restore=0,label_done=0;reg[1:0]label_query=3;reg[3:0]label_price=5,label_status=0;reg[31:0]label_count=781,label_crc=32'h1234;
 reg path_accept=0,path_restore=0,path_done=0,path_word=0;reg[3:0]path_status=0;reg[31:0]path_index=0,path_data=0,path_crc=0;reg path_last=0;
 reg query_accept=0,query_restore=0,query_done=0,query_word=0;reg[3:0]query_status=0;reg[31:0]query_index=0,query_data=0,query_crc=0;reg query_last=0;
 wire owned,fault,manifest_ready;wire[2:0]receipts;wire[31:0]saved_label_count,saved_label_crc,saved_path_crc,saved_query_crc;
 reg[31:0]pw[0:77],qw[0:9];integer checks=0,trace;string path;
 export_manifest dut(.*);
 function automatic[31:0]fold(input[31:0]a,b);reg[31:0]x;begin x=a^b;repeat(32)x=x[0]?(x>>1)^32'hedb88320:x>>1;fold=x;end endfunction
 task ck(input bit yes,input string why);begin checks=checks+1;if(!yes)$fatal(1,"manifest check%0d %s",checks,why);end endtask
 task setup;begin
  @(negedge clk);rst=1;lease=1;arm=0;abort=0;source_write=0;published=0;label_accept=0;label_done=0;label_restore=0;label_status=0;label_query=3;label_price=5;
  path_accept=0;path_done=0;path_word=0;path_restore=0;path_status=0;query_accept=0;query_done=0;query_word=0;query_restore=0;query_status=0;
  active_design=64'h123456789abcdef0;selected_design=active_design;selected_generation=target_generation;selected_checkpoint=19;active_sequence=180328;selected_version=5;active_version=5;selected_query=3;active_query=3;selected_price=5;active_price=5;active_slots=3;
  repeat(3)@(negedge clk);rst=0;arm=1;@(negedge clk);arm=0;ck(owned&&!fault&&!manifest_ready,"armed not complete");
 end endtask
 task labels;begin label_accept=1;@(negedge clk);label_accept=0;label_done=1;@(negedge clk);label_done=0;end endtask
 task paths(input integer mode);reg[31:0]sum;begin
  path_accept=1;@(negedge clk);path_accept=0;sum=32'hffffffff;
  for(integer i=0;i<78;i=i+1)begin
   path_word=1;path_index=i;path_data=pw[i];path_last=i==77;
   if(mode==2&&i==5)path_data=path_data^1;
   if(mode==3&&i==20)path_index=19;
   sum=fold(sum,path_data);$fdisplay(trace,"PATH %0d %08h %0d",path_index,path_data,path_last);@(negedge clk);
  end
  path_word=0;path_crc=~sum^(mode==1?1:0);
  repeat(4)begin @(negedge clk);ck(!manifest_ready&&!receipts[1],"path native reply not consumed");end
  path_done=1;@(negedge clk);path_done=0;
 end endtask
 task queries(input integer mode);reg[31:0]sum;begin
  query_accept=1;@(negedge clk);query_accept=0;sum=32'hffffffff;
  for(integer i=0;i<10;i=i+1)begin
   query_word=1;query_index=i;query_data=qw[i];query_last=i==9;
   if(mode==2&&i==8)query_data=query_data-1;
   if(mode==3&&i==4)query_data=query_data-1;
   sum=fold(sum,query_data);$fdisplay(trace,"QUERY %0d %08h %0d",query_index,query_data,query_last);@(negedge clk);
  end
  query_word=0;query_crc=~sum^(mode==1?1:0);
  repeat(4)begin @(negedge clk);ck(!manifest_ready&&!receipts[2],"query native reply not consumed");end
  query_done=1;@(negedge clk);query_done=0;
 end endtask
 task state_line(input integer scenario);begin $fdisplay(trace,"RESULT %0d %0d %0d %0d %0d %08h %08h",scenario,owned,fault,receipts,manifest_ready,saved_path_crc,saved_query_crc);end endtask
 initial begin
  if(!$value$plusargs("trace=%s",path))$fatal(1,"trace");trace=$fopen(path,"w");
  for(integer i=0;i<78;i=i+1)pw[i]=0;
  for(integer s=0;s<2;s=s+1)begin pw[s*39]=1;pw[s*39+1]=3;pw[s*39+2]=26422;pw[s*39+3]=66893;pw[s*39+4]=s?67922:204279;pw[s*39+5]=32'h9abcdef0;pw[s*39+6]=32'h12345678;pw[s*39+7]=s?990179:339193;pw[s*39+8]=558358;pw[s*39+9]=265324;end
  qw[0]=32'h51435031;qw[1]=1;qw[2]=32'h9abcdef0;qw[3]=32'h12345678;qw[4]=3;qw[5]=1;qw[6]=5;qw[7]=32'h57;qw[8]=180328;qw[9]=0;
  setup;labels;paths(0);queries(0);ck(manifest_ready&&receipts==7&&!fault,"complete native exports");state_line(0);
  selected_generation=target_generation+1;#1;ck(!manifest_ready,"selected generation mismatch");selected_generation=target_generation;
  selected_checkpoint=20;#1;ck(!manifest_ready,"selected checkpoint mismatch");selected_checkpoint=19;
  selected_design=0;#1;ck(!manifest_ready,"selected design mismatch");selected_design=active_design;
  selected_version=6;#1;ck(!manifest_ready,"selected version mismatch");selected_version=5;
  selected_query=0;#1;ck(!manifest_ready,"selected query mismatch");selected_query=3;
  selected_price=6;#1;ck(!manifest_ready,"selected price mismatch");selected_price=5;
  owner_manifest=0;repeat(8)begin @(negedge clk);ck(!manifest_ready&&receipts==7&&!fault,"temporary owner busy does not fabricate receipt");end
  owner_manifest=1;#1;ck(manifest_ready,"owner proof ready again");published=1;@(negedge clk);published=0;ck(!owned&&!fault&&!manifest_ready,"publication retires bundle");state_line(1);
  setup;labels;paths(1);ck(fault&&!manifest_ready,"path CRC reject");state_line(2);
  setup;labels;paths(2);ck(fault&&!manifest_ready,"path design reject with recomputed valid CRC");state_line(3);
  setup;labels;paths(3);ck(fault&&!manifest_ready,"path order reject");state_line(4);
  setup;labels;paths(0);queries(1);ck(fault&&!manifest_ready,"query CRC reject");state_line(5);
  setup;labels;paths(0);queries(2);ck(fault&&!manifest_ready,"query floor reject with valid CRC");state_line(6);
  setup;labels;paths(0);queries(3);ck(fault&&!manifest_ready,"query generation reject with valid CRC");state_line(7);
  setup;label_query=2;labels;ck(fault&&!manifest_ready,"wrong label context");state_line(8);
  setup;labels;paths(0);queries(0);source_write=1;@(negedge clk);source_write=0;ck(fault&&!manifest_ready,"source write invalidates bundle");state_line(9);
  setup;labels;paths(0);queries(0);lease=0;@(negedge clk);ck(fault&&!manifest_ready,"lease loss");state_line(10);
  setup;labels;paths(0);queries(0);active_sequence=180329;@(negedge clk);ck(fault&&!manifest_ready,"active ledger drift");state_line(11);
  setup;path_restore=1;paths(0);ck(fault&&!manifest_ready,"restore cannot count as export");state_line(12);
  setup;labels;label_accept=1;@(negedge clk);label_accept=0;ck(fault&&!manifest_ready,"duplicate label export");state_line(13);
  $display("EXPORT_MANIFEST_PASS checks=%0d",checks);$fclose(trace);$finish;
 end
 initial begin #1000000;$fatal(1,"manifest watchdog");end
endmodule
