task fourth_floor_probe;begin
 if(rc_slots!=7||k_count||system.controller.last_sequence!=180329||query_version!=7||p_active_query!=1||p_active_price!=7)$fatal(1,"G4 floor probe preconditions");
 $fdisplay(trace,"FOURTH_FLOOR_BEGIN %0d %0d %0d %0d",cycles,rc_slots,k_count,system.controller.last_sequence);
 @(negedge clk);qc_cmd_cookie=32'hce040001;qc_cmd_source=66893;qc_cmd_key=0;qc_cmd_nodes=9089009;qc_cmd_max_polls=65536;
 qc_cmd_poll_cookie=32'hc0040000;qc_cmd_design=design_id;qc_cmd_query=restore_epoch;qc_cmd_price=restore_version[3:0];
 qc_cmd_expand={restore_version,32'd291,32'd279,32'd31,32'd23,32'd260,32'd180329,32'd26422,32'd6954,32'd0,32'd0,32'd0,32'd100,32'd170791};
 qc_cmd_slot=3;qc_cmd_route_cookie=32'hf0040000;qc_cmd_valid=1;do @(posedge clk);while(!qc_cmd_ready);@(negedge clk);qc_cmd_valid=0;
 wait(qc_rsp_valid);repeat(8)begin @(negedge clk);
  if(qc_rsp_status!=1||qc_rsp_cookie!=32'hce040001||qc_rsp_committed||qc_prepare_acked||qc_cleanup_acked||qc_fault||ss_busy||k_count||rc_slots!=7||system.controller.last_sequence!=180329)$fatal(1,"G4 restored floor rejected incorrectly");
 end
 $fdisplay(trace,"FOURTH_FLOOR_REJECT %0d %0d %0d %0d %0d",cycles,qc_rsp_status,qc_prepare_acked,rc_slots,system.controller.last_sequence);
 qc_rsp_ready=1;@(negedge clk);qc_rsp_ready=0;wait(!qc_busy);
end endtask
