 integer fd,rc,i,j,k,cycles=0,expansions=0,decisions=0,early_count=0,raw_seen=0,host_blocks=0,limit=0;
 integer cookie,parent,prune,laguna,hit,raw_count,nchildren,ci,sink,net,seq,flags,xmin,xmax,ymin,ymax;
 integer cn[0:31],cp[0:31],an[0:31],ab[0:31],aa[0:31],asvc[0:31];reg[447:0]acfg[0:31];
 integer acount,allowed,early,pruned,ordinal,child,bits,action,services,op,q,price,node,field;reg[31:0]mask,value,word_value;
 string path,output_path,command;integer output_fd;
 reg[767:0]held_out;reg[196:0]held_final;
 always @(posedge clk)begin
  cycles<=cycles+1;if(cycles>100000000)$fatal(1,"watchdog");
  if(!rst)begin
   if(fault)$fatal(1,"candidate fault cookie=%d k=%d e=%d m=%d a=%d gf=%b df=%b pf=%b of=%b",cookie,dut.controller.state,dut.expansion.state,dut.metadata.state,dut.access.controller.state,dut.g_fault,dut.d_fault,dut.p_fault,dut.o_fault);
   if(dut.operation_pending)begin
    if(host_ctrl_ready||host_io_ready||host_design_req_ready||host_owner_req_ready||expand_ready)$fatal(1,"host lock gap");
    if(host_ctrl_valid&&host_io_valid&&host_design_req_valid&&host_owner_req_valid)host_blocks<=host_blocks+1;
   end
   if(dut.e_out_valid&&dut.e_out_ready)begin
    if(raw_seen>=nchildren||dut.e_out_node!==cn[raw_seen]||dut.e_out_position!==cp[raw_seen]||dut.e_out_sequence!==raw_seen)$fatal(1,"expanded child mismatch");
    raw_seen<=raw_seen+1;
   end
  end
 end
 task control(input integer operation,query,version);
  begin
   @(negedge clk);host_ctrl_op=operation;host_ctrl_query=query;host_ctrl_price=version;host_ctrl_valid=1;
   wait(host_ctrl_ready);@(posedge clk);@(negedge clk);host_ctrl_valid=0;wait(host_ctrl_rsp_valid);@(negedge clk);
   if(host_ctrl_status)$fatal(1,"control");host_ctrl_rsp_ready=1;@(negedge clk);host_ctrl_rsp_ready=0;
  end
 endtask
 task label_write(input integer n,f,input[31:0]v);
  begin
   @(negedge clk);host_io_write=1;host_io_node=n;host_io_field=f;host_io_value=v;host_io_valid=1;
   wait(host_io_ready);@(posedge clk);@(negedge clk);host_io_valid=0;wait(host_io_rsp_valid);@(negedge clk);
   if(host_io_status)$fatal(1,"label write");host_io_rsp_ready=1;@(negedge clk);host_io_rsp_ready=0;
  end
 endtask
 initial begin
  rst=1;
  if(!$value$plusargs("vectors=%s",path)||!$value$plusargs("output=%s",output_path))$fatal(1,"paths");rc=$value$plusargs("limit=%d",limit);
  fd=$fopen(path,"r");output_fd=$fopen(output_path,"w");if(!fd||!output_fd)$fatal(1,"open");
  g_cfg_offsets_base=64'h1fffff000;g_cfg_edges_base=64'h10fffff000;g_cfg_attrs_base=64'h20fffff000;g_cfg_nodes=9089009;g_cfg_edges=40469536;
  d_cfg_base=64'h31fffff000;d_cfg_nodes=9089009;t_cfg_rows_base=64'h41fffff000;t_cfg_columns_base=64'h51fffff000;t_cfg_rows=311;t_cfg_columns=0;
  owner_cfg_primary=64'h61fffff000;owner_cfg_nodes=9089009;owner_cfg_capacity=64;owner_cfg_pool=owner_cfg_primary+145428288;owner_cfg_allocator=owner_cfg_primary+145433408;
  repeat(5)@(negedge clk);rst=0;
  @(negedge clk);g_cfg_valid=1;d_cfg_valid=1;t_cfg_valid=1;owner_cfg_valid=1;
  wait(g_cfg_ready&&d_cfg_ready&&t_cfg_ready&&owner_cfg_ready);@(posedge clk);@(negedge clk);g_cfg_valid=0;d_cfg_valid=0;t_cfg_valid=0;owner_cfg_valid=0;
  wait(g_cfg_rsp_valid&&d_cfg_rsp_valid&&t_cfg_rsp_valid&&owner_cfg_rsp_valid);@(negedge clk);
  if(g_cfg_status||d_cfg_status||t_cfg_status||owner_cfg_status)$fatal(1,"config");g_cfg_rsp_ready=1;d_cfg_rsp_ready=1;t_cfg_rsp_ready=1;owner_cfg_rsp_ready=1;
  @(negedge clk);g_cfg_rsp_ready=0;d_cfg_rsp_ready=0;t_cfg_rsp_ready=0;owner_cfg_rsp_ready=0;
  while(!$feof(fd)&&(limit==0||expansions<limit))begin
   rc=$fscanf(fd,"%s",command);if(rc!=1)$fatal(1,"parse");
   if(command=="Q")begin rc=$fscanf(fd,"%d %d %d\n",op,q,price);if(rc!=3)$fatal(1,"Q");control(op,q,price);end
   else if(command=="L")begin rc=$fscanf(fd,"%d %d %d\n",node,field,value);if(rc!=3)$fatal(1,"L");label_write(node,field,value);end
   else if(command=="E")begin
    rc=$fscanf(fd,"%d %d %d %d %d %d %d %d\n",cookie,parent,prune,laguna,hit,raw_count,mask,nchildren);if(rc!=8)$fatal(1,"E");
    for(i=0;i<nchildren;i=i+1)begin rc=$fscanf(fd,"%s %d %d\n",command,cp[i],cn[i]);if(rc!=3||command!="C")$fatal(1,"C");end
    rc=$fscanf(fd,"%s %d %d %d %d %d %d %d %d %d\n",command,ci,sink,net,seq,flags,xmin,xmax,ymin,ymax);if(rc!=10||command!="D")$fatal(1,"D");
    acount=0;command="";
    while(command!="Z")begin
     rc=$fscanf(fd,"%s",command);if(rc!=1)$fatal(1,"decision parse");
     if(command=="L")begin rc=$fscanf(fd,"%d %d %d\n",node,field,value);if(rc!=3)$fatal(1,"target L");label_write(node,field,value);end
     else if(command=="A")begin
      rc=$fscanf(fd,"%d %d %d %d %d",ordinal,child,bits,action,services);if(rc!=5||ordinal!=acount)$fatal(1,"A");
      an[acount]=child;ab[acount]=bits;aa[acount]=action;asvc[acount]=services;
      for(j=0;j<14;j=j+1)begin rc=$fscanf(fd,"%d",word_value);if(rc!=1)$fatal(1,"Config");acfg[acount][j*32+:32]=word_value;end
      acount=acount+1;
     end else if(command=="Z")begin rc=$fscanf(fd,"%d %d %d\n",allowed,early,pruned);if(rc!=3)$fatal(1,"Z");end
     else $fatal(1,"unknown decision");
    end
    @(negedge clk);raw_seen=0;expand_cookie=cookie;expand_parent=parent;expand_prune=prune;expand_has_laguna=laguna;expand_sink=sink;expand_net=net;expand_sequence=seq;expand_flags=flags&32'h11c;
    expand_xmin=xmin;expand_xmax=xmax;expand_ymin=ymin;expand_ymax=ymax;expand_valid=1;
    wait(expand_ready);@(posedge clk);@(negedge clk);expand_valid=0;
    host_ctrl_valid=1;host_io_valid=1;host_design_req_valid=1;host_owner_req_valid=1;
    for(k=0;k<acount;k=k+1)begin
     wait(out_valid);@(negedge clk);
     if(out_cookie!==cookie||out_node!==an[k]||out_sequence!==k||out_position!==cp[k]||out_bits!==ab[k]||out_action!==aa[k]||out_services!==asvc[k]||out_config!==acfg[k])$fatal(1,"decision mismatch cookie=%d ordinal=%d bits=%d/%d action=%d/%d svc=%d/%d config=%h/%h",cookie,k,out_bits,ab[k],out_action,aa[k],out_services,asvc[k],out_config,acfg[k]);
     held_out={out_config,out_attrs,out_bits,out_action};repeat(2)begin @(negedge clk);if(!out_valid||{out_config,out_attrs,out_bits,out_action}!==held_out)$fatal(1,"out stability");end
     $fdisplay(output_fd,"A %0d %0d %0d %0d %0d %0112h",cookie,k,out_node,out_bits,out_action,out_config);
     out_ready=1;@(negedge clk);out_ready=0;decisions=decisions+1;
    end
    wait(result_valid);@(negedge clk);
    if(result_status||result_cookie!==cookie||result_count!==acount||result_expanded_count!==nchildren||result_raw_count!==raw_count||result_mask!==mask||result_hit!==hit[0]||result_early!==early[0]||raw_seen!=nchildren)$fatal(1,"final mismatch cookie=%d status=%d counts=%d/%d expanded=%d/%d rawseen=%d",cookie,result_status,result_count,acount,result_expanded_count,nchildren,raw_seen);
    repeat(3)@(negedge clk);result_ready=1;@(negedge clk);result_ready=0;host_ctrl_valid=0;host_io_valid=0;host_design_req_valid=0;host_owner_req_valid=0;
    expansions=expansions+1;early_count=early_count+early;
   end else $fatal(1,"unknown command %s",command);
  end
  $fclose(fd);$fclose(output_fd);
  if(owner_writes!=0)$fatal(1,"readonly candidate mutated ownership");
  $display("CANDIDATE_PASS expansions=%0d decisions=%0d early=%0d host_blocks=%0d graph_reads=%0d design_reads=%0d design_writes=%0d owner_reads=%0d cycles=%0d",expansions,decisions,early_count,host_blocks,g_reads,d_reads,d_writes,owner_reads,cycles);$finish;
 end
