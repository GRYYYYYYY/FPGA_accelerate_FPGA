 integer cycles=0,errors=0,recoveries=0,normal_checks=0,cookie=100,rc,ix,fixture=0,old_reads,old_writes;
 reg[447:0]numeric_expected;reg[618:0]held;reg[63:0]held_ar;string path;integer fd;
 always @(posedge clk)begin cycles=cycles+1;if(cycles>50000)$fatal(1,"boundary watchdog fixture=%0d state=%0d",fixture,dut.controller.state);end
 task configure;
  begin
   g_cfg_valid=1;d_cfg_valid=1;wait(g_cfg_ready&&d_cfg_ready);@(posedge clk);@(negedge clk);g_cfg_valid=0;d_cfg_valid=0;
   wait(g_cfg_rsp_valid&&d_cfg_rsp_valid);@(negedge clk);if(g_cfg_status||d_cfg_status)$fatal(1,"configuration");g_cfg_rsp_ready=1;d_cfg_rsp_ready=1;@(negedge clk);g_cfg_rsp_ready=0;d_cfg_rsp_ready=0;
  end
 endtask
 task reset_design;
  begin
   @(negedge clk);rst=1;abort=0;hold_graph_ar=0;inject_graph=0;inject_design=0;inject_design_b=0;req_valid=0;rsp_ready=0;host_design_req_valid=0;host_design_rsp_ready=0;g_cfg_valid=0;d_cfg_valid=0;
   owner_configured=1;owner_nodes=64;active=1;active_query=1;active_price=3;g_cfg_nodes=64;d_cfg_nodes=64;
   req_parent=18;req_child=0;req_sink=36;req_net=7;req_sequence=32'hffffffff;req_flags=32'h11d;req_xmin=32'h80000000;req_xmax=32'h7fffffff;req_ymin=32'hffffffff;req_ymax=0;req_query=1;req_price=3;
   repeat(4)@(negedge clk);rc=$fseek(mem_d.fd[0],0,0);for(ix=0;ix<1024;ix=ix+1)$fwrite(mem_d.fd[0],"%c",8'b0);$fflush(mem_d.fd[0]);fixture=fixture+1;$fdisplay(mem_d.logfd,"RESET %0d",fixture);$fflush(mem_d.logfd);rst=0;@(negedge clk);
  end
 endtask
 task boot;
  begin reset_design;configure;end
 endtask
 task host(input integer operation);
  begin
   @(negedge clk);cookie=cookie+1;host_design_req_op=operation;host_design_req_node=0;host_design_req_owner=0;host_design_req_arg=0;host_design_req_cookie=cookie;host_design_req_valid=1;
   wait(host_design_req_ready);@(posedge clk);@(negedge clk);host_design_req_valid=0;wait(host_design_rsp_valid);@(negedge clk);
   if(fault||host_design_rsp_status||host_design_rsp_cookie!=cookie)$fatal(1,"host preparation");host_design_rsp_ready=1;@(negedge clk);host_design_rsp_ready=0;
  end
 endtask
 task prepare;
  begin host(2);host(3);end
 endtask
 task send;
  begin
   @(negedge clk);cookie=cookie+1;req_cookie=cookie;req_valid=1;wait(req_ready);@(posedge clk);@(negedge clk);req_valid=0;
  end
 endtask
 task accept_reply;
  begin rsp_ready=1;@(negedge clk);rsp_ready=0;end
 endtask
 task normal;
  begin
   prepare;old_writes=d_writes;send;wait(rsp_valid);@(negedge clk);
   if(fault||rsp_status||rsp_config!==numeric_expected||!rsp_created||rsp_cookie!=cookie||rsp_parent!=18||rsp_child!=0||rsp_sink!=36||rsp_net!=7||rsp_query!=1||rsp_price!=3||d_writes!=old_writes)$fatal(1,"numeric/static/identity snapshot");
   held={rsp_status,rsp_cookie,rsp_parent,rsp_child,rsp_sink,rsp_net,rsp_query,rsp_price,rsp_config,rsp_created};repeat(5)begin @(negedge clk);if({rsp_status,rsp_cookie,rsp_parent,rsp_child,rsp_sink,rsp_net,rsp_query,rsp_price,rsp_config,rsp_created}!==held)$fatal(1,"numeric reply stability");end
   accept_reply;normal_checks=normal_checks+1;
  end
 endtask
 task recover;
  begin boot;normal;recoveries=recoveries+1;end
 endtask
 task failed_reply(input integer expected);
  begin
   wait(rsp_valid);@(negedge clk);if(!fault||rsp_status!==expected||rsp_cookie!=cookie)$fatal(1,"fault status fixture=%0d got=%0d expected=%0d",fixture,rsp_status,expected);
   held={rsp_status,rsp_cookie,rsp_parent,rsp_child,rsp_sink,rsp_net,rsp_query,rsp_price,rsp_config,rsp_created};
   repeat(5)begin @(negedge clk);if(!rsp_valid||{rsp_status,rsp_cookie,rsp_parent,rsp_child,rsp_sink,rsp_net,rsp_query,rsp_price,rsp_config,rsp_created}!==held)$fatal(1,"fault changed exposed response");end
   accept_reply;repeat(100)@(negedge clk);
   if(!fault||req_ready||host_design_req_ready||dut.controller.g_pending||dut.controller.d_pending)$fatal(1,"metadata failed to stop/drain");
   errors=errors+1;$display("METADATA_FAULT fixture=%0d status=%0d drained=1",fixture,expected);recover;
  end
 endtask
 task config_failure;
  begin
   configure;repeat(3)@(negedge clk);
   if(!fault||req_ready||rsp_valid||g_m_arvalid||d_m_arvalid)$fatal(1,"configuration mismatch gate");errors=errors+1;$display("METADATA_CONFIG_FAULT fixture=%0d",fixture);recover;
  end
 endtask
 initial begin
  rst=1;g_cfg_offsets_base=64'h1fffff000;g_cfg_edges_base=64'h10fffff000;g_cfg_attrs_base=64'h20fffff000;g_cfg_edges=0;d_cfg_base=64'h61fffff000;graph_size0=320;graph_size1=0;graph_size2=2048;design_size=1024;
  if(!$value$plusargs("expected=%s",path))$fatal(1,"numeric expected path");fd=$fopen(path,"r");rc=$fscanf(fd,"%h",numeric_expected);if(rc!=1)$fatal(1,"numeric expected");$fclose(fd);repeat(4)@(negedge clk);
  boot;req_child=18;send;wait(rsp_valid);@(negedge clk);
  if(fault||rsp_status||!rsp_created||rsp_config[63:32]!=32'h1fd||rsp_config[191:160]!=0||rsp_config[223:192]!=3||d_writes!=0)$fatal(1,"initial static created merge");
  accept_reply;normal_checks=normal_checks+1;
  boot;g_cfg_nodes=999;d_cfg_nodes=999;normal; // Accepted configuration values are held.
  reset_design;g_cfg_nodes=65;config_failure;
  reset_design;d_cfg_nodes=65;config_failure;
  reset_design;owner_nodes=65;config_failure;
  boot;old_reads=g_reads+d_reads;req_child=64;send;wait(rsp_valid);@(negedge clk);if(fault||rsp_status!=1||g_reads+d_reads!=old_reads)$fatal(1,"invalid node issued memory");accept_reply;
  req_child=0;req_flags=2;send;wait(rsp_valid);@(negedge clk);if(fault||rsp_status!=1||g_reads+d_reads!=old_reads)$fatal(1,"external dead/static option accepted");accept_reply;req_flags=32'h11d;normal;
  boot;send;failed_reply(4); // Static created was deliberately cleared; no CREATE yet.
  boot;active=0;send;failed_reply(2);
  boot;req_query=2;send;failed_reply(2);
  boot;req_price=4;send;failed_reply(2);
  boot;prepare;inject_graph=1;send;failed_reply(5);
  boot;prepare;inject_design=1;send;failed_reply(5);
  boot;prepare;hold_graph_ar=1;send;wait(g_m_arvalid);@(negedge clk);held_ar=g_m_araddr;abort=1;repeat(3)@(negedge clk);
  if(!g_m_arvalid||g_m_araddr!==held_ar)$fatal(1,"accepted graph read withdrew VALID");abort=0;hold_graph_ar=0;failed_reply(5);
  boot;prepare;send;wait(dut.controller.g_pending);@(negedge clk);owner_configured=0;failed_reply(5);
  boot;prepare;hold_graph_ar=1;send;wait(rsp_valid);@(negedge clk);if(!g_m_arvalid)$fatal(1,"timeout withdrew current graph read");hold_graph_ar=0;failed_reply(5);
  boot;prepare;send;wait(rsp_valid);@(negedge clk);abort=1;@(negedge clk);abort=0;failed_reply(0);
  boot;normal;send;failed_reply(6); // Actual token3 exhausts before the second design GET.
  boot;inject_design_b=1;cookie=cookie+1;host_design_req_cookie=cookie;host_design_req_op=2;host_design_req_node=0;host_design_req_owner=0;host_design_req_arg=0;host_design_req_valid=1;
  wait(host_design_req_ready);@(posedge clk);@(negedge clk);host_design_req_valid=0;wait(host_design_rsp_valid);@(negedge clk);
  if(!fault||host_design_rsp_status!=5||host_design_rsp_cookie!=cookie||rsp_valid)$fatal(1,"host B error propagation");host_design_rsp_ready=1;@(negedge clk);host_design_rsp_ready=0;errors=errors+1;$display("METADATA_HOST_B_FAULT fixture=%0d",fixture);recover;
  if(errors!=15||recoveries!=15)$fatal(1,"boundary counts %0d/%0d",errors,recoveries);
  $display("METADATA_BOUNDARIES_PASS errors=%0d recoveries=%0d normal_checks=%0d cycles=%0d",errors,recoveries,normal_checks,cycles);$finish;
 end
