 integer fd,logfd,rc,cid,parent,child,sink,dead,cases=0,cycles=0,host_commands=0,host_blocks=0,write_before;
 reg[31:0]seq_word,flags,xmin_word,xmax_word,ymin_word,ymax_word;reg[447:0]expected;
 reg[618:0]held;string path;
 always @(posedge clk)begin
  cycles=cycles+1;if(cycles>10000000)$fatal(1,"metadata watchdog case=%0d state=%0d",cid,dut.controller.state);
  if(!rst)begin
   if(fault)$fatal(1,"metadata fault case=%0d state=%0d token=%0d",cid,dut.controller.state,dut.controller.token);
   if(dut.meta_pending)begin if(host_design_req_ready||req_ready)$fatal(1,"host/second request admitted during metadata");if(host_design_req_valid)host_blocks=host_blocks+1;end
   if(dut.host_pending&&req_ready)$fatal(1,"metadata accepted during host reply");
  end
 end
 task host_command(input integer op,node,owner,arg);
  begin
   @(negedge clk);host_commands=host_commands+1;host_design_req_op=op;host_design_req_node=node;host_design_req_owner=owner;host_design_req_arg=arg;host_design_req_cookie=host_commands;host_design_req_valid=1;
   wait(host_design_req_ready);@(posedge clk);@(negedge clk);host_design_req_valid=0;wait(host_design_rsp_valid);@(negedge clk);
   if(host_design_rsp_status||host_design_rsp_cookie!=host_commands)$fatal(1,"design host response op=%0d",op);
   $fdisplay(logfd,"H %0d %0d %0d %0d %0d %0d %0d",op,node,owner,arg,host_design_rsp_flags,host_design_rsp_count,host_design_rsp_mask);
   repeat(2)@(negedge clk);host_design_rsp_ready=1;@(negedge clk);host_design_rsp_ready=0;
  end
 endtask
 initial begin
  rst=1;
  if(!$value$plusargs("commands=%s",path))$fatal(1,"commands");fd=$fopen(path,"r");
  if(!$value$plusargs("observed=%s",path))$fatal(1,"observed");logfd=$fopen(path,"w");
  if(!$value$plusargs("nodes=%d",g_cfg_nodes)||!$value$plusargs("edges=%d",g_cfg_edges))$fatal(1,"sizes");
  if(!fd||!logfd)$fatal(1,"open metadata inputs");
  d_cfg_nodes=g_cfg_nodes;owner_nodes=g_cfg_nodes;owner_configured=1;active=1;active_query=1;active_price=3;
  g_cfg_offsets_base=64'h1fffff000;g_cfg_edges_base=64'h10fffff000;g_cfg_attrs_base=64'h20fffff000;d_cfg_base=64'h61fffff000;
  graph_size0=((g_cfg_nodes+64'd1)*4+63)&~64'd63;graph_size1=(g_cfg_edges*64'd4+63)&~64'd63;graph_size2=(g_cfg_nodes*64'd32+63)&~64'd63;design_size=(g_cfg_nodes*64'd16+63)&~64'd63;
  repeat(4)@(negedge clk);rst=0;
  g_cfg_valid=1;d_cfg_valid=1;wait(g_cfg_ready&&d_cfg_ready);@(posedge clk);@(negedge clk);g_cfg_valid=0;d_cfg_valid=0;
  wait(g_cfg_rsp_valid&&d_cfg_rsp_valid);@(negedge clk);if(g_cfg_status||d_cfg_status)$fatal(1,"configuration");g_cfg_rsp_ready=1;d_cfg_rsp_ready=1;@(negedge clk);g_cfg_rsp_ready=0;d_cfg_rsp_ready=0;
  while(!$feof(fd))begin
   rc=$fscanf(fd,"%d %d %d %d %d %h %h %h %h %h %h %h\n",cid,parent,child,sink,dead,seq_word,flags,xmin_word,xmax_word,ymin_word,ymax_word,expected);
   if(rc!=12)$fatal(1,"command format %0d",rc);
   host_command(2,child,0,0);if(dead)host_command(3,child,0,0);
   if(cases==0&&g_cfg_edges==0)begin
    host_command(1,parent,1,0);if(!design_claim_active||req_ready)$fatal(1,"metadata admitted before cache publication");
    repeat(3)@(negedge clk);host_command(5,parent,1,0);if(design_claim_active)$fatal(1,"cache claim not released");
   end
   write_before=d_writes;
   @(negedge clk);req_parent=parent;req_child=child;req_sink=sink;req_net=0;req_cookie=cid+100;req_sequence=seq_word;req_flags=flags;req_xmin=xmin_word;req_xmax=xmax_word;req_ymin=ymin_word;req_ymax=ymax_word;req_query=1;req_price=3;req_valid=1;
   wait(req_ready);@(posedge clk);@(negedge clk);req_valid=0;
   req_parent=32'hbad;req_child=32'hbad;req_sink=32'hbad;req_flags=32'hffffffff;req_sequence=0;req_cookie=0;req_xmin=0;req_xmax=0;req_ymin=0;req_ymax=0;
   host_design_req_valid=1;host_design_req_op=3;host_design_req_node=child;
   wait(rsp_valid);@(negedge clk);
   if(fault||rsp_status||!rsp_created||rsp_config!==expected||rsp_cookie!=cid+100||rsp_parent!=parent||rsp_child!=child||rsp_sink!=sink||rsp_net||rsp_query!=1||rsp_price!=3)$fatal(1,"metadata case=%0d expected=%h actual=%h status=%0d",cid,expected,rsp_config,rsp_status);
   if(d_writes!=write_before)$fatal(1,"metadata request mutated persistent state");
   held={rsp_status,rsp_cookie,rsp_parent,rsp_child,rsp_sink,rsp_net,rsp_query,rsp_price,rsp_config,rsp_created};
   repeat(3)begin @(negedge clk);if(!rsp_valid||{rsp_status,rsp_cookie,rsp_parent,rsp_child,rsp_sink,rsp_net,rsp_query,rsp_price,rsp_config,rsp_created}!==held)$fatal(1,"metadata response changed");end
   $fdisplay(logfd,"M %0d %0112h",cid,rsp_config);rsp_ready=1;@(negedge clk);rsp_ready=0;host_design_req_valid=0;cases=cases+1;
  end
  if(d_writes!=d_bs||dut.controller.g_pending||dut.controller.d_pending||dut.host_pending||dut.meta_pending)$fatal(1,"outstanding metadata traffic");
  $fclose(logfd);$display("METADATA_PASS cases=%0d host_commands=%0d host_blocks=%0d graph_reads=%0d design_reads=%0d design_writes=%0d cycles=%0d",cases,host_commands,host_blocks,g_reads,d_reads,d_writes,cycles);$finish;
 end
