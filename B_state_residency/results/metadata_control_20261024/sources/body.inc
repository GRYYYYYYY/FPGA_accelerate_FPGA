 integer cycles=0,checks=0,errors=0,i;reg[618:0]held;
 always @(posedge clk)begin cycles=cycles+1;if(cycles>5000)$fatal(1,"controller watchdog %0d",dut.state);end
 task boot;
  begin
   @(negedge clk);rst=1;req_valid=0;rsp_ready=0;g_req_ready=0;d_req_ready=0;g_rsp_valid=0;d_rsp_valid=0;g_fault=0;d_fault=0;abort=0;claim_active=0;enable=1;nodes=64;active=1;active_query=2;active_price=6;
   req_cookie=123;req_parent=17;req_child=33;req_sink=49;req_net=55;req_sequence=44;req_flags=0;req_query=2;req_price=6;req_xmin=0;req_xmax=0;req_ymin=0;req_ymax=0;
   repeat(3)@(negedge clk);rst=0;@(negedge clk);
  end
 endtask
 task send;
  begin req_valid=1;#1;while(!req_ready)@(negedge clk);@(negedge clk);req_valid=0;req_cookie=999;req_parent=999;req_child=999;req_sink=999;req_net=999;req_query=0;req_price=0;req_sequence=999;req_flags=32'hffffffff;end
 endtask
 task graph_reply(input integer bad);
  reg[31:0]tag,id;
  begin
   if(!g_req_valid)$fatal(1,"no graph request");tag=g_req_cookie;id=g_req_node;g_req_ready=1;@(negedge clk);g_req_ready=0;
   g_rsp_cookie=tag+(bad==1);g_rsp_parent=id+(bad==2);g_rsp_node=id+(bad==3);g_rsp_index=bad==4;g_rsp_status=bad==5;g_rsp_attrs=0;g_rsp_attrs[72]=1;g_rsp_start=0;g_rsp_count=0;g_rsp_valid=1;
   @(negedge clk);g_rsp_valid=0;#1;
  end
 endtask
 task three_graphs;
  begin graph_reply(0);graph_reply(0);graph_reply(0);end
 endtask
 task design_accept;
  begin if(!d_req_valid||d_req_op||d_req_owner||d_req_arg||d_req_node!=33)$fatal(1,"design request identity");d_req_ready=1;@(negedge clk);d_req_ready=0;end
 endtask
 task design_reply(input integer bad);
  begin
   design_accept;d_rsp_cookie=d_req_cookie+(bad==1);d_rsp_status=bad==2;d_rsp_flags=0;d_rsp_count=0;d_rsp_mask=0;d_rsp_valid=1;@(negedge clk);d_rsp_valid=0;#1;
  end
 endtask
 task reply(input integer status,bad);
  begin
   while(!rsp_valid)@(negedge clk);#1;
   if(rsp_status!==status||fault!==bad[0]||rsp_cookie!=123||rsp_parent!=17||rsp_child!=33||rsp_sink!=49||rsp_net!=55||rsp_query!=2||rsp_price!=6)$fatal(1,"controller result %0d/%0d fault=%b/%0d",rsp_status,status,fault,bad);
   held={rsp_status,rsp_cookie,rsp_parent,rsp_child,rsp_sink,rsp_net,rsp_query,rsp_price,rsp_config,rsp_created};
   repeat(3)begin @(negedge clk);if(!rsp_valid||{rsp_status,rsp_cookie,rsp_parent,rsp_child,rsp_sink,rsp_net,rsp_query,rsp_price,rsp_config,rsp_created}!==held)$fatal(1,"controller response stability");end
   rsp_ready=1;@(negedge clk);rsp_ready=0;checks=checks+1;if(bad)errors=errors+1;
  end
 endtask
 initial begin
  boot;send;three_graphs;design_reply(0);if(rsp_config!==448'd44||!rsp_created)$fatal(1,"captured descriptor/static-created merge");reply(0,0);
  for(i=1;i<=5;i=i+1)begin boot;send;graph_reply(i);reply(i==5?3:4,1);end
  for(i=1;i<=2;i=i+1)begin boot;send;three_graphs;design_reply(i);reply(i==2?3:4,1);end
  boot;send;active_query=3;reply(5,1);
  boot;send;active_price=7;reply(5,1);
  boot;send;active=0;reply(5,1);
  boot;send;claim_active=1;reply(5,1);
  boot;g_rsp_valid=1;@(negedge clk);g_rsp_valid=0;#1;if(!fault||rsp_valid||req_ready)$fatal(1,"unowned graph response");checks=checks+1;errors=errors+1;
  boot;d_rsp_valid=1;@(negedge clk);d_rsp_valid=0;#1;if(!fault||rsp_valid||req_ready)$fatal(1,"unowned design response");checks=checks+1;errors=errors+1;
  boot;send;g_req_ready=1;@(negedge clk);g_req_ready=0;g_fault=1;@(negedge clk);
  if(!g_rsp_ready||!fault)$fatal(1,"failed current service cannot drain");g_rsp_valid=1;@(negedge clk);g_rsp_valid=0;#1;reply(5,1);if(dut.g_pending)$fatal(1,"drain pending");
  boot;send;three_graphs;design_accept;while(dut.elapsed<31)@(negedge clk);
  d_rsp_cookie=d_req_cookie;d_rsp_status=0;d_rsp_flags=1;d_rsp_valid=1;@(negedge clk);d_rsp_valid=0;#1;reply(5,1);
  boot;send;three_graphs;design_reply(0);abort=1;@(negedge clk);abort=0;#1;reply(0,1);
  if(checks!=17||errors!=16)$fatal(1,"matrix counts %0d/%0d",checks,errors);
  $display("METADATA_CONTROL_PASS checks=%0d errors=%0d cycles=%0d",checks,errors,cycles);$finish;
 end
