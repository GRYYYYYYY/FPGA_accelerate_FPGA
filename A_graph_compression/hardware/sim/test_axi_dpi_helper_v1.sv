`timescale 1ns/1ps
module memory_case #(parameter W=64,D=23,P=4)(output reg done=0);
// A_DPI_STORAGE_ONLY: protocol, depths and transaction pages unchanged.
import "DPI-C" function int a_model_register(input string name,input int bits,input longint depth,input int pages);
import "DPI-C" function void a_model_read(input int id,input int page,input longint index,output logic[511:0] value);
import "DPI-C" function void a_model_write(input int id,input int page,input longint index,input logic[511:0] value);
import "DPI-C" function void a_model_enqueue(input int id,input int page,input longint index,input logic[511:0] value);
import "DPI-C" function void a_model_commit(input int id);
integer a_storage_id=-1;
reg a_storage_commit=0;
function integer a_storage_ensure();
 if(a_storage_id<0)a_storage_id=a_model_register($sformatf("%m"),W,D,P);
 if(a_storage_id<0)$fatal(1,"A_DPI_STORAGE_ALLOCATION_FAILED");
 return a_storage_id;
endfunction
function [W-1:0] a_storage_read(input integer page,input logic[63:0] index);
 logic[511:0] value;
 if(^index===1'bx)return 'x;
 a_model_read(a_storage_ensure(),page,index,value);return value[W-1:0];
endfunction
function [15:0] a_storage_read_low16(input integer page,input logic[63:0] index);
 reg[W-1:0] value;
 value=a_storage_read(page,index);return value[15:0];
endfunction
function a_storage_read_bit(input integer page,input logic[63:0] index,input integer bit_index);
 reg[W-1:0] value;
 if((^bit_index===1'bx)||bit_index<0||bit_index>=W)return 1'bx;
 value=a_storage_read(page,index);return value[bit_index];
endfunction
task a_storage_write_blk(input integer page,input logic[63:0] index,input logic[W-1:0] value);
 if(^index!==1'bx)a_model_write(a_storage_ensure(),page,index,value);
endtask
task a_storage_write_nba(input integer page,input logic[63:0] index,input logic[W-1:0] value);
 if(^index!==1'bx)begin a_model_enqueue(a_storage_ensure(),page,index,value);a_storage_commit<=~a_storage_commit;end
endtask
always @(a_storage_commit)if(a_storage_id>=0)a_model_commit(a_storage_id);
initial if(P!=4 || W<32 || W>512 || W%32)$fatal(1,"A_DPI_STORAGE_UNSUPPORTED_PARAMETERS");
reg clk=0;always #5 clk=~clk;
reg[W-1:0] reference[0:P*D-1]='{default:'0};
function [W-1:0] read_reference(input int page,input logic[63:0] index);
 if((^index===1'bx)||page<0||page>=P||index>=D)return 'x;
 return reference[page*D+index];
endfunction
task compare(input int page,input logic[63:0] index);
 reg[W-1:0] expected;integer k;
 expected=read_reference(page,index);
 if(a_storage_read(page,index)!==expected)$fatal(1,"HELPER_WORD_MISMATCH");
 if(a_storage_read_low16(page,index)!==expected[15:0])$fatal(1,"HELPER_LOW16_MISMATCH");
 for(k=0;k<W;k=k+1)if(a_storage_read_bit(page,index,k)!==expected[k])$fatal(1,"HELPER_BIT_MISMATCH");
 if(a_storage_read_bit(page,index,W)!==1'bx || a_storage_read_bit(page,index,-1)!==1'bx || a_storage_read_bit(page,index,32'hxxxxxxxx)!==1'bx)$fatal(1,"HELPER_INVALID_BIT_MISMATCH");
endtask
task write_blocking(input int page,input logic[63:0] index,input logic[W-1:0] value);
 if((^index!==1'bx)&&page>=0&&page<P&&index<D)reference[page*D+index]=value;
 a_storage_write_blk(page,index,value);
endtask
task write_nonblocking(input int page,input logic[63:0] index,input logic[W-1:0] value);
 if((^index!==1'bx)&&page>=0&&page<P&&index<D)reference[page*D+index]<=value;
 a_storage_write_nba(page,index,value);
endtask
integer i,j,page,index;reg[31:0] rng=32'h483a75c1;reg[W-1:0] value,partial;
initial begin
 #2;
 for(page=0;page<P;page=page+1)for(index=0;index<D;index=index+1)compare(page,index);
 compare(0,D);compare(-1,0);compare(P,0);compare(0,64'hxxxxxxxxxxxxxxxx);
 for(i=0;i<128;i=i+1)begin
  @(posedge clk);page=(i*7)%P;index=(i*11)%D;
  for(j=0;j<W;j=j+32)begin rng=rng*32'd1664525+32'd1013904223;value[j+:32]=rng;end
  if(i%7==0)begin value[0]=1'bx;value[W-1]=1'bz;end
  write_blocking(page,index,value);compare(page,index);
  partial=read_reference(page,index);
  for(j=0;j<W;j=j+8)if((i+j/8)%3==0)partial[j+:8]=~value[j+:8];
  write_nonblocking(page,index,partial);
  // The active and inactive regions must still observe the old committed word.
  compare(page,index);#0;compare(page,index);
  #0.001;compare(page,index);
  // Two NBAs to the same location preserve last-write ordering.
  @(negedge clk);write_nonblocking(page,index,value);write_nonblocking(page,index,~value);
  compare(page,index);#0.001;compare(page,index);
 end
 $display("DPI_MEMORY_CASE_PASS width=%0d pages=%0d depth=%0d updates=128",W,P,D);done=1;
end
endmodule
module test_axi_dpi_helper_v1;
wire[4:0]done;
memory_case #(.W(32),.P(4))a(done[0]);
memory_case #(.W(64),.P(4))b(done[1]);
memory_case #(.W(128),.P(4))c(done[2]);
memory_case #(.W(256),.P(4))d(done[3]);
memory_case #(.W(512),.P(4))e(done[4]);
initial begin wait(&done);$display("DPI_MEMORY_ALL_PASS cases=5");$finish;end
initial begin #100000;$fatal(1,"DPI_MEMORY_TIMEOUT");end
endmodule
