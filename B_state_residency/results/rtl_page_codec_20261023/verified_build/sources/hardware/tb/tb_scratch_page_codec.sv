`timescale 1ns/1ps
module tb_scratch_page_codec;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,start_valid=0,start_decode=0,cancel=0;
 wire start_ready,busy;
 reg record_in_valid=0,record_in_present=0;wire record_in_ready;
 reg [5:0] record_in_offset=0;reg [159:0] record_in_payload=0;
 wire record_out_valid,record_out_present;reg record_out_ready=0;
 wire [5:0] record_out_offset;wire [159:0] record_out_payload;
 reg raw_in_valid=0;wire raw_in_ready;reg [511:0] raw_in_data=0;
 wire raw_out_valid,raw_out_last;reg raw_out_ready=0;wire [511:0] raw_out_data;
 reg commit_valid=0,commit_ok=0;wire commit_ready;
 wire done_valid,done_error;reg done_ready=0;
 scratch_page_codec dut(.*);
 reg [511:0] pages[0:1343];reg [160:0] records[0:4095];
 reg [4095:0] pages_path,records_path;
 integer cycle=0,p,n,b,i,checks=0,encoded=0,decoded=0,errors=0,aborts=0,stalls=0;
 reg allowed=0,held_raw=0,held_record=0,held_done=0,was_cancel=0;
 reg [512:0] saved_raw;reg [166:0] saved_record;reg saved_error;
 always @(posedge clk)begin
  cycle<=cycle+1;
  if(!rst && !cancel && !was_cancel)begin
   if(record_out_valid && !allowed)$fatal(1,"record exposed before successful commit");
   if(held_raw && (!raw_out_valid || {raw_out_last,raw_out_data}!==saved_raw))$fatal(1,"raw changed under stall");
   if(held_record && (!record_out_valid || {record_out_offset,record_out_present,record_out_payload}!==saved_record))$fatal(1,"record changed under stall");
   if(held_done && (!done_valid || done_error!==saved_error))$fatal(1,"done changed under stall");
   if((raw_out_valid&&!raw_out_ready)||(record_out_valid&&!record_out_ready))stalls<=stalls+1;
  end
  held_raw<=!rst && !cancel && raw_out_valid&&!raw_out_ready;saved_raw<={raw_out_last,raw_out_data};
  held_record<=!rst && !cancel && record_out_valid&&!record_out_ready;saved_record<={record_out_offset,record_out_present,record_out_payload};
  held_done<=!rst && done_valid&&!done_ready;saved_error<=done_error;was_cancel<=cancel;
 end
 task automatic start(input integer reading);
  begin
   @(negedge clk);if(!start_ready)$fatal(1,"start blocked");allowed=0;start_decode=reading;start_valid=1;
   @(posedge clk);@(negedge clk);start_valid=0;
  end
 endtask
 task automatic finish(input integer err);
  integer t;
  begin
   t=0;while(!done_valid)begin @(negedge clk);t=t+1;if(err && commit_ready)$fatal(1,"malformed page accepted");if(t>3000)$fatal(1,"done timeout");end
   repeat(5)begin if(!done_valid || done_error!==err[0] || start_ready)$fatal(1,"wrong done error");@(negedge clk);end
   done_ready=1;@(posedge clk);@(negedge clk);done_ready=0;
   if(busy || !start_ready)$fatal(1,"completion not retired");checks=checks+1;
  end
 endtask
 task automatic put_record(input integer offset_value,input reg [160:0] value);
  integer t;
  begin
   @(negedge clk);record_in_valid=1;record_in_offset=offset_value;record_in_present=value[160];record_in_payload=value[159:0];
   t=0;@(posedge clk);while(!record_in_ready)begin @(posedge clk);t=t+1;if(t>30)$fatal(1,"record input stuck");end
   @(negedge clk);record_in_valid=0;record_in_payload='1;
  end
 endtask
 task automatic put_raw(input reg [511:0] value);
  integer t;
  begin
   @(negedge clk);raw_in_valid=1;raw_in_data=value;
   t=0;@(posedge clk);while(!raw_in_ready)begin @(posedge clk);t=t+1;if(t>30)$fatal(1,"raw input stuck");end
   @(negedge clk);raw_in_valid=0;raw_in_data='1;
  end
 endtask
 task automatic commit(input integer ok);
  integer t;
  begin
   t=0;while(!commit_ready)begin @(negedge clk);t=t+1;if(t>40)$fatal(1,"commit wait timeout");end
   repeat(17)begin if(record_out_valid || done_valid)$fatal(1,"decode escaped commit gate");@(negedge clk);end
   commit_valid=1;commit_ok=ok;allowed=ok;
   @(posedge clk);@(negedge clk);commit_valid=0;commit_ok=0;
  end
 endtask
 task automatic take_records(input integer page_value);
  integer j,t;
  begin
   j=0;t=0;
   while(j<64)begin
    @(negedge clk);record_out_ready=cycle%7>=3;
    @(posedge clk);
    if(record_out_valid && record_out_ready)begin
     if(record_out_offset!==j[5:0] || {record_out_present,record_out_payload}!==records[page_value*64+j])$fatal(1,"decoded record mismatch page=%0d node=%0d",page_value,j);
     j=j+1;checks=checks+1;
    end
    t=t+1;if(t>2000)$fatal(1,"record output stuck");
   end
   @(negedge clk);record_out_ready=0;
  end
 endtask
 task automatic abort_page;
  begin
   @(negedge clk);cancel=1;@(posedge clk);@(negedge clk);cancel=0;
   if(!done_valid || !done_error)$fatal(1,"abort did not terminate page");
   if(record_out_valid || raw_out_valid)$fatal(1,"output survives abort");finish(1);aborts=aborts+1;
  end
 endtask
 initial begin #100000000;$fatal(1,"codec watchdog");end
 initial begin
  if(!$value$plusargs("PAGES=%s",pages_path) || !$value$plusargs("RECORDS=%s",records_path))$fatal(1,"missing fixtures");
  $readmemh(pages_path,pages);$readmemh(records_path,records);
  repeat(3)@(negedge clk);rst=0;
  for(p=0;p<64;p=p+1)begin
   start(0);for(n=0;n<64;n=n+1)put_record(n,records[p*64+n]);
   b=0;i=0;
   while(b<21)begin
    @(negedge clk);raw_out_ready=cycle%11>=5;@(posedge clk);
    if(raw_out_valid && raw_out_ready)begin
     if(raw_out_data!==pages[p*21+b] || raw_out_last!==(b==20))$fatal(1,"encoded byte mismatch page=%0d beat=%0d",p,b);
     b=b+1;checks=checks+1;
    end
    i=i+1;if(i>2000)$fatal(1,"raw output stuck");
   end
   @(negedge clk);raw_out_ready=0;finish(0);encoded=encoded+1;
   start(1);for(b=0;b<21;b=b+1)put_raw(pages[p*21+b]);commit(1);take_records(p);finish(0);decoded=decoded+1;
  end
  // Failed memory completion must never publish even a fully valid page.
  start(1);for(b=0;b<21;b=b+1)put_raw(pages[21+b]);commit(0);finish(1);errors=errors+1;
  // Bad absent payload, record padding and page tail, respectively.
  for(p=0;p<3;p=p+1)begin
   start(1);
   for(b=0;b<21;b=b+1)begin
    if(p==0 && b==0)put_raw(pages[b]^(512'd1<<64));
    else if(p==1 && b==0)put_raw(pages[21+b]^(512'd1<<200));
    else if(p==2 && b==20)put_raw(pages[21+b]^(512'd1<<511));
    else put_raw(pages[(p==0?0:21)+b]);
   end
   finish(1);errors=errors+1;
  end
  start(0);put_record(1,records[64]);finish(1);errors=errors+1;
  start(0);put_record(0,records[64]^(161'd1<<136));finish(1);errors=errors+1;
  start(0);put_record(0,161'd1);finish(1);errors=errors+1;
  // Abort each externally blocked phase, then decode empty page without RAM reset.
  start(0);put_record(0,records[64]);abort_page;
  start(0);for(n=0;n<64;n=n+1)put_record(n,records[64+n]);wait(raw_out_valid);abort_page;
  start(1);put_raw(pages[21]);abort_page;
  start(1);for(b=0;b<21;b=b+1)put_raw(pages[21+b]);wait(commit_ready);abort_page;
  start(1);for(b=0;b<21;b=b+1)put_raw(pages[21+b]);commit(1);wait(record_out_valid);abort_page;
  start(1);for(b=0;b<21;b=b+1)put_raw(pages[b]);commit(1);take_records(0);finish(0);decoded=decoded+1;
  $display("TEST_PASS scratch_page_codec checks=%0d encoded=%0d decoded=%0d rejected=%0d aborted=%0d stalls=%0d",checks,encoded,decoded,errors,aborts,stalls);$finish;
 end
endmodule
