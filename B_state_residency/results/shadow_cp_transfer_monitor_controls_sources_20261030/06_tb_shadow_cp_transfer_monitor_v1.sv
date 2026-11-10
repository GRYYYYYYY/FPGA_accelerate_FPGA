`timescale 1ns/1ps
`default_nettype none
module shadow_cp_transfer_monitor;
 integer fd,words=0;
 initial begin
  fd=$fopen("shadow_cp_export.log","w");
  if(!fd)$fatal(1,"CP_TRANSFER_MONITOR_OPEN");
 end
 always @(posedge stage_static_cp_shadow.drive_clk)begin
  if(stage_static_cp_shadow.armed&&
     stage_static_cp_shadow.actual_cp_m_valid===1'b1&&
     stage_static_cp_shadow.drive_cp_m_ready===1'b1)begin
   $fdisplay(fd,"CP_WORD %0t %0d %08h %b",$time,
     stage_static_cp_shadow.actual_cp_m_index,
     stage_static_cp_shadow.actual_cp_m_data,
     stage_static_cp_shadow.actual_cp_m_last);
   words=words+1;
   $fflush(fd);
  end
 end
 final begin
  $display("CP_TRANSFER_MONITOR_END words=%0d",words);
  if(fd)$fclose(fd);
 end
endmodule
`default_nettype wire
