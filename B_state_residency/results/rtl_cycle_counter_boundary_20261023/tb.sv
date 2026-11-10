`timescale 1ns/1ps
module tb;
 integer old_cycle=2147483644;
 longint unsigned new_cycle=64'd2147483644;
 integer i,old_progress=0,new_progress=0;
 initial begin
  for(i=0;i<64;i=i+1)begin
   if(new_cycle<64'd2147483648 && ((old_cycle%5>=2)!=(new_cycle%5>=2)))$fatal(1,"prewrap mismatch");
   if(new_cycle>=64'd2147483648)begin
    if(old_cycle%5>=2 || old_cycle%7>=2 || old_cycle%11>=4 || old_cycle%13>=5)old_progress=old_progress+1;
    if(new_cycle%5>=2)new_progress=new_progress+1;
   end
   old_cycle=old_cycle+1;new_cycle=new_cycle+1;
  end
  if(old_progress!=0 || new_progress==0)$fatal(1,"overflow hypothesis not reproduced");
  $display("COUNTER_BOUNDARY_PASS old_progress=%0d new_progress=%0d",old_progress,new_progress);$finish;
 end
endmodule
