`timescale 1ns/1ps
module tb_scratch_page_codec_small_static_diff;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,start_valid=0,start_decode=0,cancel=0,record_in_valid=0,record_in_present=0;
 reg [2:0] record_in_offset=0;reg [159:0] record_in_payload=0;
 reg record_out_ready=0,raw_in_valid=0,raw_out_ready=0,commit_valid=0,commit_ok=0,done_ready=0;
 reg [511:0] raw_in_data=0;
 wire start_ready,busy,record_in_ready,record_out_valid,record_out_present,raw_in_ready,raw_out_valid,raw_out_last,commit_ready,done_valid,done_error;
 wire [2:0] record_out_offset;wire [159:0] record_out_payload;wire [511:0] raw_out_data;
 scratch_page_codec_small_static dut(.*);
 wire ref_start_ready,ref_busy,ref_record_in_ready,ref_record_out_valid,ref_record_out_present,ref_raw_in_ready,ref_raw_out_valid,ref_raw_out_last,ref_commit_ready,ref_done_valid,ref_done_error;
 wire [2:0] ref_record_out_offset;wire [159:0] ref_record_out_payload;wire [511:0] ref_raw_out_data;
 scratch_page_codec_small reference_codec(.start_ready(ref_start_ready),.busy(ref_busy),.record_in_ready(ref_record_in_ready),
 .record_out_valid(ref_record_out_valid),.record_out_present(ref_record_out_present),.record_out_offset(ref_record_out_offset),.record_out_payload(ref_record_out_payload),
 .raw_in_ready(ref_raw_in_ready),.raw_out_valid(ref_raw_out_valid),.raw_out_last(ref_raw_out_last),.raw_out_data(ref_raw_out_data),
 .commit_ready(ref_commit_ready),.done_valid(ref_done_valid),.done_error(ref_done_error),.*);
 integer compared_cycles=0;
 always @(negedge clk)begin
  #1;
  if(!rst)begin
   if({start_ready,busy,record_in_ready,record_out_valid,raw_in_ready,raw_out_valid,commit_ready,done_valid} !==
      {ref_start_ready,ref_busy,ref_record_in_ready,ref_record_out_valid,ref_raw_in_ready,ref_raw_out_valid,ref_commit_ready,ref_done_valid})$fatal(1,"cycle control differential");
   if(done_valid && done_error!==ref_done_error)$fatal(1,"done differential");
   if(record_out_valid && {record_out_offset,record_out_present,record_out_payload}!=={ref_record_out_offset,ref_record_out_present,ref_record_out_payload})$fatal(1,"record differential");
   if(raw_out_valid && {raw_out_data,raw_out_last}!=={ref_raw_out_data,ref_raw_out_last})$fatal(1,"raw differential");
   compared_cycles=compared_cycles+1;
  end
 end

 reg [1535:0] expected,damaged;reg [159:0] words[0:7];reg [7:0] valid_bits;
 integer checks=0,cases=0,i,j,k;
 task tick;begin @(posedge clk);#1;end endtask
 task start(input bit decode);begin
  @(negedge clk);start_decode=decode;start_valid=1;
  while(!start_ready)tick;tick;
  @(negedge clk);start_valid=0;
 end endtask
 task finish_check(input bit error);begin
  while(!done_valid)tick;
  if(done_error!==error)$fatal(1,"done_error expected %b got %b",error,done_error);
  repeat(3)begin tick;if(!done_valid || done_error!==error || start_ready)$fatal(1,"done hold");end
  @(negedge clk);done_ready=1;tick;@(negedge clk);done_ready=0;checks=checks+1;
 end endtask
 task encode;integer n,b;begin
  start(0);
  for(n=0;n<8;n=n+1)begin
   @(negedge clk);record_in_valid=1;record_in_offset=n;record_in_present=valid_bits[n];record_in_payload=words[n];
   while(!record_in_ready)tick;tick;
   @(negedge clk);record_in_valid=0;tick;
  end
  for(b=0;b<3;b=b+1)begin
   while(!raw_out_valid)tick;
   repeat(3)begin
    if(raw_out_data!==expected[b*512 +:512] || raw_out_last!==(b==2))$fatal(1,"raw encode mismatch beat %0d",b);
    tick;
   end
   @(negedge clk);raw_out_ready=1;tick;@(negedge clk);raw_out_ready=0;checks=checks+1;
  end
  finish_check(0);cases=cases+1;
 end endtask
 task decode(input reg[1535:0] data,input bit approved,input bit error);integer n,b;begin
  start(1);
  for(b=0;b<3;b=b+1)begin
   @(negedge clk);raw_in_data=data[b*512 +:512];raw_in_valid=1;
   while(!raw_in_ready)tick;tick;@(negedge clk);raw_in_valid=0;
   if(record_out_valid)$fatal(1,"premature record");tick;
  end
  while(!commit_ready)begin if(record_out_valid)$fatal(1,"record before validation");tick;end
  repeat(4)begin if(record_out_valid || done_valid)$fatal(1,"record before commit");tick;end
  @(negedge clk);commit_valid=1;commit_ok=approved;tick;@(negedge clk);commit_valid=0;
  if(!error)for(n=0;n<8;n=n+1)begin
   while(!record_out_valid)tick;
   repeat(2)begin
    if(record_out_offset!==n[2:0] || record_out_present!==valid_bits[n] || record_out_payload!==words[n])$fatal(1,"decoded record mismatch %0d",n);
    tick;
   end
   @(negedge clk);record_out_ready=1;tick;@(negedge clk);record_out_ready=0;checks=checks+1;
  end
  else if(record_out_valid)$fatal(1,"invalid record exposed");
  finish_check(error);cases=cases+1;
 end endtask

 task prepare_phase(input integer phase);integer n;begin
  if(phase<2)begin
   start(0);
   if(phase==1)for(n=0;n<8;n=n+1)begin
    @(negedge clk);record_in_valid=1;record_in_offset=n;record_in_present=valid_bits[n];record_in_payload=words[n];
    while(!record_in_ready)tick;tick;@(negedge clk);record_in_valid=0;
   end
  end else begin
   start(1);
   if(phase>2)begin
    for(n=0;n<3;n=n+1)begin
     @(negedge clk);raw_in_valid=1;raw_in_data=expected[n*512 +:512];
     while(!raw_in_ready)tick;tick;@(negedge clk);raw_in_valid=0;
    end
    if(phase>3)begin
     while(!commit_ready)tick;
     if(phase==5)begin
      @(negedge clk);commit_valid=1;commit_ok=1;tick;@(negedge clk);commit_valid=0;
      if(!record_out_valid)$fatal(1,"prepare output phase");
     end
    end
   end
  end
 end endtask
 initial begin
  repeat(4)tick;@(negedge clk);rst=0;
  for(k=0;k<16;k=k+1)begin
   valid_bits=(k==0)?8'hff:(k==1?8'h00:(8'ha5^k));expected=0;expected[7:0]=valid_bits;
   for(i=0;i<8;i=i+1)begin
    words[i]=0;
    if(valid_bits[i])begin
     for(j=0;j<17;j=j+1)words[i][j*8 +:8]=(k*37+i*19+j*11)&255;
     if(k==0 && i==0)words[i]=0;
     if(k==0 && i==7)words[i][135:0]={136{1'b1}};
    end
    for(j=0;j<20;j=j+1)expected[(1+i*20+j)*8 +:8]=words[i][j*8 +:8];
   end
   encode;decode(expected,1,0);decode(expected,0,1);
   damaged=expected;damaged[(1+7*20+19)*8]=1;decode(damaged,1,1);
   damaged=expected;damaged[1535]=1;decode(damaged,1,1);
  end
  // Absent record with nonzero data; bitmap is deliberately cleared.
  damaged=expected;damaged[0]=0;damaged[8]=1;decode(damaged,1,1);
  // Wrong input offset must abort without emitting page data.
  start(0);@(negedge clk);record_in_valid=1;record_in_offset=7;tick;
  @(negedge clk);record_in_valid=0;if(raw_out_valid)$fatal(1,"bad encode leaked");finish_check(1);cases=cases+1;
  // Cancellation during decode intake returns error and no record.
  start(1);@(negedge clk);cancel=1;tick;@(negedge clk);cancel=0;
  if(record_out_valid)$fatal(1,"cancel leaked");finish_check(1);cases=cases+1;

  // Reach each active phase using public handshakes, then cancel or reset.
  for(k=0;k<6;k=k+1)begin
   prepare_phase(k);@(negedge clk);cancel=1;
   #1;if(raw_out_valid || record_out_valid || raw_in_ready || record_in_ready || commit_ready)$fatal(1,"cancel qualifier");
   tick;@(negedge clk);cancel=0;finish_check(1);cases=cases+1;
   prepare_phase(k);@(negedge clk);rst=1;tick;
   if(done_valid || raw_out_valid || record_out_valid || busy)$fatal(1,"reset did not clear");
   @(negedge clk);rst=0;tick;if(!start_ready)$fatal(1,"reset recovery");checks=checks+1;cases=cases+1;
  end
  for(k=0;k<2;k=k+1)begin
   start(0);@(negedge clk);record_in_valid=1;record_in_offset=0;record_in_present=(k==0);
   record_in_payload=(k==0)?(160'b1<<136):160'b1;tick;
   @(negedge clk);record_in_valid=0;if(raw_out_valid)$fatal(1,"illegal encode payload");finish_check(1);cases=cases+1;
  end
  // Full valid transaction after all abort/reset/error paths.
  encode;decode(expected,1,0);
  if(compared_cycles<1000)$fatal(1,"insufficient differential cycles");
  $display("STATIC_DIFF_PASS cycles=%0d",compared_cycles);
  $display("SMALL_CODEC_EDGES_PASS cases=%0d checks=%0d",cases,checks);$finish;
 end
 initial begin #1000000;$fatal(1,"watchdog");end
endmodule
