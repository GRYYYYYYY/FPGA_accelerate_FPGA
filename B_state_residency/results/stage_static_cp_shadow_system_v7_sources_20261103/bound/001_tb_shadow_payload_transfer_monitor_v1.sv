`timescale 1ns/1ps
`default_nettype none
module shadow_payload_transfer_monitor;
 integer ka_fd,pw_fd,ka_words=0,pw_words=0,pw_addresses=0;
 initial begin
  ka_fd=$fopen("shadow_ka_requests.log","w");
  pw_fd=$fopen("shadow_pw_beats.log","w");
  if(!ka_fd||!pw_fd)$fatal(1,"PAYLOAD_TRANSFER_MONITOR_OPEN");
 end
 always @(posedge stage_static_cp_shadow.drive_clk)begin
  if(stage_static_cp_shadow.armed)begin
   if(stage_static_cp_shadow.actual_k_a_valid===1'b1&&stage_static_cp_shadow.actual_k_a_ready===1'b1)begin
    $fdisplay(ka_fd,"KA_WORD %0t %0d %0d %0d %0d %016h",$time,
      stage_static_cp_shadow.actual_k_a_checkpoint,
      stage_static_cp_shadow.actual_k_a_node,
      stage_static_cp_shadow.actual_k_a_net,
      stage_static_cp_shadow.actual_k_a_cookie,
      stage_static_cp_shadow.actual_k_a_design);
    ka_words=ka_words+1;$fflush(ka_fd);
   end
   if(stage_static_cp_shadow.actual_p_m_awvalid===1'b1&&stage_static_cp_shadow.drive_p_m_awready===1'b1)begin
    $fdisplay(pw_fd,"PW_AW %0t %08h %0d %0d %0d %h",$time,
      stage_static_cp_shadow.actual_p_m_awaddr,
      stage_static_cp_shadow.actual_p_m_awlen,
      stage_static_cp_shadow.actual_p_m_awsize,
      stage_static_cp_shadow.actual_p_m_awburst,
      stage_static_cp_shadow.actual_p_m_awid);
    pw_addresses=pw_addresses+1;$fflush(pw_fd);
   end
   if(stage_static_cp_shadow.actual_p_m_wvalid===1'b1&&stage_static_cp_shadow.drive_p_m_wready===1'b1)begin
    $fdisplay(pw_fd,"PW_W %0t %0128h %016h %b",$time,
      stage_static_cp_shadow.actual_p_m_wdata,
      stage_static_cp_shadow.actual_p_m_wstrb,
      stage_static_cp_shadow.actual_p_m_wlast);
    pw_words=pw_words+1;$fflush(pw_fd);
   end
  end
 end
 final begin
  $display("PAYLOAD_TRANSFER_MONITOR_END ka=%0d pw=%0d aw=%0d",ka_words,pw_words,pw_addresses);
  if(ka_fd)$fclose(ka_fd);if(pw_fd)$fclose(pw_fd);
 end
endmodule
`default_nettype wire
