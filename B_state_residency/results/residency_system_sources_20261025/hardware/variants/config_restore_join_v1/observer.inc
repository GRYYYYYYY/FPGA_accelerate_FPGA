reg cf_last_rsp=0;
always @(posedge clk)begin
 if(k_cold_rst)cf_last_rsp<=0;
 else begin
  cf_last_rsp<=cf_rsp_valid;
  for(integer cx=0;cx<6;cx=cx+1)begin
   if(cf_valid[cx]&&cf_ready[cx])$fdisplay(trace,"CQ %0d %0d %096h",cycles,cx,cf_payload[cx*384+:384]);
   if(cf_replies[cx]&&cf_reply_ready[cx])$fdisplay(trace,"CP %0d %0d %0d",cycles,cx,cf_status[cx*3+:3]);
  end
  if(cf_rsp_valid&&!cf_last_rsp)begin
   if(cf_rsp_status||cf_sent!=63||cf_retired!=63||cf_fault)$fatal(1,"hardware config restore result");
   $fdisplay(trace,"CD %0d %0d %0d %0d",cycles,cf_rsp_status,cf_sent,cf_retired);
  end
  if(cf_busy&&(q_cfg_ready||g_cfg_ready||d_cfg_ready||t_cfg_ready||owner_cfg_ready||cs_cfg_ready))$fatal(1,"config restore host lease");
 end
end
