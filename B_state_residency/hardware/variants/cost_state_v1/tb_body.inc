 integer fd,fo,rc,cycles=0,commands=0,queries=0,op,host,index,version,q,p,status,active;
 reg[31:0]value;reg[127:0]expected;reg[237:0]held;string path,outpath,kind;
 always @(posedge clk)begin
  cycles<=cycles+1;if(cycles>200000)$fatal(1,"watchdog");
  if(!rst&&editing&&ready_for_query)$fatal(1,"query ready while editing");
  if(!rst&&fault)$fatal(1,"unexpected fault op=%d q=%d ver=%d",req_op,active_query,published_version);
 end
 initial begin
  rst=1;if(!$value$plusargs("commands=%s",path)||!$value$plusargs("observed=%s",outpath))$fatal(1,"paths");fd=$fopen(path,"r");fo=$fopen(outpath,"w");if(!fd||!fo)$fatal(1,"open");
  cfg_history=64'h1fffff000;cfg_prices=cfg_history;cfg_nets=cfg_history+nets_offset;cfg_nodes=32;cfg_net_count=16;cfg_version=1;cfg_design_id=64'h123456789abcdef0;
  rc=$value$plusargs("nodes=%d",cfg_nodes);rc=$value$plusargs("nets=%d",cfg_net_count);rc=$value$plusargs("bytes=%d",image_size);rc=$value$plusargs("prices_offset=%d",prices_offset);rc=$value$plusargs("nets_offset=%d",nets_offset);cfg_nets=cfg_history+nets_offset;
  repeat(5)@(negedge clk);rst=0;
  @(negedge clk);cfg_valid=1;wait(cfg_ready);@(posedge clk);@(negedge clk);cfg_valid=0;wait(cfg_rsp_valid);@(negedge clk);if(cfg_status!=1||configured)$fatal(1,"overlap config accepted");cfg_rsp_ready=1;@(negedge clk);cfg_rsp_ready=0;
  cfg_prices=cfg_history+prices_offset;cfg_valid=1;wait(cfg_ready);@(posedge clk);@(negedge clk);cfg_valid=0;wait(cfg_rsp_valid);@(negedge clk);
  if(cfg_status||!configured||design_id!=64'h123456789abcdef0)$fatal(1,"config");repeat(3)begin @(negedge clk);if(req_ready||ready_for_query)$fatal(1,"cfg response not retired");end
  cfg_rsp_ready=1;@(negedge clk);cfg_rsp_ready=0;
  while(!$feof(fd))begin
   rc=$fscanf(fd,"%s",kind);if(rc!=1)$fatal(1,"parse kind");wait(!busy);@(negedge clk);
   if(kind=="Q")begin
    rc=$fscanf(fd,"%d %d %d\n",active,q,p);if(rc!=3)$fatal(1,"Q");if(active&&!ready_for_query)$fatal(1,"query entered edit/busy");query_active=active;decision_lock=active;active_query=q;active_price=p;queries=queries+1;
   end else if(kind=="C")begin
    rc=$fscanf(fd,"%d %d %d %h %d %d %d %d %h\n",host,op,index,value,version,q,p,status,expected);if(rc!=9)$fatal(1,"C");
    req_host=host;req_op=op;req_cookie=commands+1;req_index=index;req_value=value;req_version=version;req_query=q;req_price=p;req_valid=1;
    wait(req_ready);@(posedge clk);@(negedge clk);req_valid=0;req_op=7;req_cookie=32'hdeadbeef;req_index=32'hbad;req_value=0;req_version=0;req_query=0;req_price=0;req_host=!host;
    wait(rsp_valid);@(negedge clk);
    if(rsp_status!==status[3:0]||rsp_cookie!==commands+1||rsp_op!==op[2:0]||rsp_index!==index||rsp_host!==host[0]||rsp_version!==version||rsp_query!==q[1:0]||rsp_price!==p[3:0]||rsp_data!==expected)$fatal(1,"response cmd=%0d status=%0d/%0d data=%h/%h",commands+1,rsp_status,status,rsp_data,expected);
    held={rsp_status,rsp_cookie,rsp_index,rsp_version,rsp_op,rsp_host,rsp_query,rsp_price,rsp_data};
    repeat(3)begin @(negedge clk);if(req_ready||!rsp_valid||{rsp_status,rsp_cookie,rsp_index,rsp_version,rsp_op,rsp_host,rsp_query,rsp_price,rsp_data}!==held)$fatal(1,"response stability");end
    $fdisplay(fo,"C %0d %0d %032h %0d %0d",commands+1,rsp_status,rsp_data,published_version,editing);rsp_ready=1;@(negedge clk);rsp_ready=0;commands=commands+1;
   end else $fatal(1,"kind");
  end
  wait(!busy);$fclose(fd);$fclose(fo);$display("COST_STATE_PASS commands=%0d queries=%0d version=%0d reads=%0d writes=%0d bs=%0d cycles=%0d",commands,queries,published_version,reads,writes,bs,cycles);$finish;
 end
