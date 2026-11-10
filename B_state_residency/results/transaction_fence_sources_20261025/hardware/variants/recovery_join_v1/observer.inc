reg last_k_reset=0,prior_drained=0;integer last_j_cycle=0;reg[31:0]last_j_node=0;
always @(posedge clk)begin
 if(k_cold_rst)begin k_normal_retired<=1;last_k_reset<=0;prior_drained<=0;k_a_ready<=0;k_a_rsp_valid<=0;auth_delay<=0;end
 else begin
  prior_drained<=label_drained&&owner_drained;last_k_reset<=k_target_reset;
  if(rc_req_valid&&rc_req_ready)k_normal_retired<=0;
  if(rc_rsp_valid&&rc_rsp_ready)k_normal_retired<=1;
  if(k_target_reset&&!last_k_reset)begin
   if(!prior_drained||!k_normal_retired)$fatal(1,"RTL reset before drain/retire");$fdisplay(trace,"RESET %0d %0d",cycles,k_count);
  end
  if(k_j_valid&&k_j_ready)begin last_j_cycle<=cycles;last_j_node<=k_j_node;$fdisplay(trace,"J %0d %0d %0d %0d",cycles,k_j_node,k_j_net,k_j_op);end
  if(route_join.held&&b_o_valid&&b_o_ready)begin
   if(cycles<=last_j_cycle||b_o_node!=last_j_node)$fatal(1,"owner forwarded before journal");$fdisplay(trace,"BF %0d %0d %0d",cycles,b_o_op,b_o_node);
  end
  if(k_o_valid&&k_o_ready)$fdisplay(trace,"KO %0d %0d %0d %0d",cycles,k_o_op,k_o_node,k_o_cookie);
  if(k_o_rsp_valid&&k_o_rsp_ready)$fdisplay(trace,"KR %0d %0d %0d %0d",cycles,host_owner_rsp_status,host_owner_rsp_count,host_owner_rsp_occupancy);
  if(!recover_open&&k_busy&&(rc_req_ready||expand_ready||seed_ready))$fatal(1,"coordinator gate leak");
  k_a_ready<=cycles%4==0;
  if(k_a_valid&&k_a_ready)begin
   if(auth_delay||k_a_rsp_valid)$fatal(1,"authority overlap");auth_match=-1;
   for(integer ax=0;ax<6;ax=ax+1)if(authority_node[ax]==k_a_node&&authority_net[ax]==k_a_net)auth_match=ax;
   if(auth_match<0||k_a_design!=design_id||(k_a_checkpoint!=17&&k_a_checkpoint!=18))$fatal(1,"authority key binding");
   k_a_rsp_cookie<=k_a_cookie;k_a_rsp_checkpoint<=k_a_checkpoint;k_a_rsp_design<=k_a_design;k_a_status<=0;
   k_a_refs<=k_a_checkpoint==17?authority_refs0[auth_match]:authority_refs1[auth_match];k_a_occ<=k_a_checkpoint==17?authority_occ0[auth_match]:authority_occ1[auth_match];auth_delay<=3;
   $fdisplay(trace,"KA %0d %0d %0d %0d %0d",cycles,k_a_checkpoint,k_a_node,k_a_net,k_a_cookie);
  end
  if(auth_delay>0)begin auth_delay<=auth_delay-1;if(auth_delay==1)k_a_rsp_valid<=1;end
  if(k_a_rsp_valid&&k_a_rsp_ready)k_a_rsp_valid<=0;
 end
end
