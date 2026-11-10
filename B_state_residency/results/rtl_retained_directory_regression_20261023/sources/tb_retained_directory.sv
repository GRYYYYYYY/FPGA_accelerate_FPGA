`timescale 1ns/1ps
module tb_retained_directory;
reg clk=0; always #5 clk=~clk;
reg rst=1,cmd_valid=0,rsp_ready=0,memory_success=1,fence_retired=0;
reg [2:0] cmd_op=0;reg [23:0] cmd_owner=0;
reg [2:0] cmd_frame=0;reg [63:0] cmd_cookie=0;
wire cmd_ready,rsp_valid,rsp_published,any_fault;
wire [2:0] rsp_status,rsp_frame;wire [31:0] rsp_address;
wire [3:0] allocated,leased;
backing_frame_directory_retained #(.FRAMES(8),.INDEX_BITS(3),.HASH_BITS(1),.PROBE_LIMIT(1),.EPOCH_BITS(2)) dut(.*);
integer checks=0,j,k;reg [63:0] ck;
function automatic [63:0] cookie(input integer tx,input integer slot,input integer own,input integer rf);
 cookie=(64'(tx)<<42)|(64'(1)<<26)|(64'(own)<<2)|64'(slot)|(64'(rf)<<58);
endfunction
// Interface checker includes stalled-response stability and command exclusion.
task automatic send(input integer op,input integer own,input integer frame,input [63:0] c,
                    input bit fence,input bit success,input integer status,input integer outframe,input integer pub);
 integer wait_cycles;reg [38:0] held;
 begin
 @(negedge clk);cmd_op=op;cmd_owner=own;cmd_frame=frame;cmd_cookie=c;
 fence_retired=fence;memory_success=success;cmd_valid=1;rsp_ready=0;
 wait_cycles=0;
 while(!cmd_ready)begin @(negedge clk);wait_cycles=wait_cycles+1;if(wait_cycles>200)$fatal(1,"command timeout");end
 @(posedge clk);@(negedge clk);cmd_valid=0;wait_cycles=0;
 while(!rsp_valid)begin @(negedge clk);wait_cycles=wait_cycles+1;if(wait_cycles>200)$fatal(1,"response timeout");end
 if(rsp_status!==status[2:0])$fatal(1,"status check=%0d op=%0d got=%0d expected=%0d",checks,op,rsp_status,status);
 if(outframe>=0 && (rsp_frame!==outframe[2:0] || rsp_address!==outframe*1344))$fatal(1,"frame/address mismatch");
 if(pub>=0 && rsp_published!==pub[0])$fatal(1,"published mismatch");
 held={rsp_status,rsp_frame,rsp_published,rsp_address};
 repeat(3)begin @(negedge clk);if(!rsp_valid || cmd_ready || held!=={rsp_status,rsp_frame,rsp_published,rsp_address})$fatal(1,"response hold");end
 rsp_ready=1;@(posedge clk);@(negedge clk);rsp_ready=0;checks=checks+1;
 end
endtask
initial begin
 repeat(4)@(negedge clk);rst=0;
 // More owners than hash buckets forces retained overflow-scan coverage.
 for(j=0;j<6;j=j+1)begin
 send(0,100+j,0,0,0,1,0,j,0);
 ck=cookie(j,j%4,100+j,0);
 send(1,0,j,ck,0,1,0,j,0);
 send(2,0,j,ck,0,1,0,j,1);
 send(3,0,j,ck,0,1,0,j,1);
 end
 for(k=0;k<40;k=k+1)begin
 // First raise the high water mark to the real 16-bit maximum.
 ck=cookie(65535,0,100,1);
 send(1,0,0,ck,0,1,0,0,1);
 send(6,0,0,0,1,1,2,-1,-1); // INFLIGHT cannot recycle.
 send(2,0,0,ck,0,1,0,0,1);
 send(6,0,0,0,1,1,2,-1,-1); // COMPLETE but unretired cannot recycle.
 send(3,0,0,ck,0,1,0,0,1);
 send(1,0,0,cookie(0,0,100,1),0,1,5,-1,-1);
 send(6,0,0,0,0,1,2,-1,-1); // Missing drain proof.
 send(1,0,0,cookie(0,0,100,1),0,1,5,-1,-1);
 send(6,0,0,0,1,1,0,0,0);
 if(allocated!==6 || leased!==0 || any_fault)$fatal(1,"retained allocation");
 for(j=0;j<6;j=j+1)begin
 send(5,100+j,0,0,0,1,0,j,1);
 send(0,100+j,0,0,0,1,0,j,1);
 end
 ck=cookie(0,0,100,1);
 send(1,0,0,ck,0,1,0,0,1); // Zero is legal only after successful recycle.
 send(2,0,0,ck,0,1,0,0,1);
 send(3,0,0,ck,0,1,0,0,1);
 end
 // Ordinary recycle must still invalidate all owners through epoch wrap.
 for(k=0;k<6;k=k+1)begin
 send(4,0,0,0,1,1,0,0,0);
 if(allocated!==0)$fatal(1,"full recycle retained owners");
 send(5,100,0,0,0,1,6,-1,-1);
 send(0,100,0,0,0,1,0,0,0);
 end
 ck=cookie(0,0,100,0);
 send(1,0,0,ck,0,1,0,0,0);
 send(2,0,0,ck,0,0,7,-1,-1);
 send(6,0,0,0,1,1,2,-1,-1);
 if(!any_fault || leased==0)$fatal(1,"failed lease lost");
 send(7,0,0,0,1,1,3,-1,-1);
 $display("RETAINED_DIRECTORY_PASS checks=%0d checkpoints=40 full_recycles=6",checks);$finish;
end
initial begin #(64'd10000000);$fatal(1,"watchdog");end
endmodule
