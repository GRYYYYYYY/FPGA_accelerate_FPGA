`timescale 1ns/1ps
module tb_frontier_reset;
reg clk=0;always #5 clk=~clk;
reg rst=1,start=0;wire ready,done,idle;
reg [31:0] op=0,key_bits=0,id=0;
wire [127:0] data;wire [3:0] valid;
reg [127:0] held=0;reg [3:0] seen=0;reg done_seen=0;
integer i,calls=0;
frontier_step dut(.ap_clk(clk),.ap_rst(rst),.ap_start(start),.ap_ready(ready),.ap_done(done),.ap_idle(idle),
.op(op),.key_bits(key_bits),.id(id),.status(data[31:0]),.result_bits(data[63:32]),.result_id(data[95:64]),.size(data[127:96]),
.status_ap_vld(valid[0]),.result_bits_ap_vld(valid[1]),.result_id_ap_vld(valid[2]),.size_ap_vld(valid[3]));
always @(posedge clk)if(!rst)begin
 if(done)done_seen<=1;
 for(i=0;i<4;i=i+1)if(valid[i])begin held[32*i+:32]<=data[32*i+:32];seen[i]<=1;end
end
task call(input [31:0] command,input [31:0] bits,input [31:0] node,input [31:0] status,input [31:0] size);
begin
 @(negedge clk);seen=0;done_seen=0;op=command;key_bits=bits;id=node;start=1;
 do @(posedge clk);while(!ready);
 @(negedge clk);start=0;
 wait(done_seen&&(&seen));@(negedge clk);
 if(held[31:0]!==status||held[127:96]!==size)$fatal(1,"call %0d got=%h status=%d size=%d",calls,held,status,size);
 calls=calls+1;
end endtask
task reset;begin @(negedge clk);rst=1;start=0;repeat(6)@(negedge clk);rst=0;end endtask
initial begin #100000;$fatal(1,"watchdog");end
initial begin
 reset;call(0,0,0,0,0);call(1,32'h3f800000,32'hdeadbeef,0,1);call(1,32'h40000000,32'habcd0123,0,2);
 reset;call(3,0,0,0,2);call(2,0,0,0,1);
 if(held[63:32]!==32'h3f800000||held[95:64]!==32'hdeadbeef)$fatal(1,"unexpected stale entry");
 $display("RAW_RESET_RETAINS_OLD_HEAP size_after_reset=2 stale_id=deadbeef");
 call(0,0,0,0,0);call(2,0,0,1,0);call(1,32'hbf800000,42,0,1);call(2,0,0,0,0);
 if(held[63:32]!==32'hbf800000||held[95:64]!==42)$fatal(1,"new entry wrong");
 $display("FRONTIER_RESET_CHARACTERIZED calls=%0d clear_hides_old_heap=1",calls);$finish;
end
endmodule
