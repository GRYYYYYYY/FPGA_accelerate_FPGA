 integer cycles=0,checks=0,fault_cases=0;
 reg[110:0]identity;
 always @(posedge clk)begin cycles=cycles+1;if(cycles>5000)$fatal(1,"bridge watchdog state=%0d",dut.state);end
 task boot;
  begin
   @(negedge clk);rst=1;s_req_valid=0;s_rsp_ready=0;h_req_valid=0;h_rsp_ready=0;b_req_ready=0;b_rsp_valid=0;b_fault=0;abort=0;
   active=1;active_query=1;active_price=3;decision_lock=1;
   repeat(3)@(negedge clk);rst=0;@(negedge clk);
  end
 endtask
 task service(input[3:0]kind);
  begin
   s_req_kind=kind;s_req_phase=13;s_req_node=99;s_req_net=9;s_req_cookie=12345;s_req_query=1;s_req_price=3;s_req_valid=1;
   identity={s_req_kind,s_req_phase,s_req_node,s_req_net,s_req_cookie,s_req_query,s_req_price};
   while(!s_req_ready)@(negedge clk);@(negedge clk);s_req_valid=0;
   s_req_kind=15;s_req_phase=31;s_req_node=999;s_req_net=999;s_req_cookie=32'hbad;s_req_query=0;s_req_price=0;
  end
 endtask
 task backend(input[31:0]cookie,input[3:0]status);
  begin
   if(b_req_valid)begin
    if(b_req_op!=0||b_req_cookie!=12345||b_req_node!=99||b_req_net!=9)$fatal(1,"captured service request");
    b_req_ready=1;@(negedge clk);b_req_ready=0;
   end
   if(!b_rsp_ready)$fatal(1,"backend not owned");
   b_rsp_cookie=cookie;b_rsp_status=status;b_rsp_count=7;b_rsp_occupancy=2;b_rsp_will_overuse=1;b_rsp_valid=1;
   @(negedge clk);b_rsp_valid=0;
  end
 endtask
 task reply(input integer status,value,bad);
  reg[146:0]held;
  begin
   if(!s_rsp_valid||s_rsp_status!==status||s_rsp_value!==value||fault!==bad[0]||{s_rsp_kind,s_rsp_phase,s_rsp_node,s_rsp_net,s_rsp_cookie,s_rsp_query,s_rsp_price}!==identity)$fatal(1,"service reply status=%0d/%0d value=%0d/%0d fault=%b/%0d",s_rsp_status,status,s_rsp_value,value,fault,bad);
   held={s_rsp_status,s_rsp_value,identity};
   repeat(3)begin @(negedge clk);if(!s_rsp_valid||{s_rsp_status,s_rsp_value,s_rsp_kind,s_rsp_phase,s_rsp_node,s_rsp_net,s_rsp_cookie,s_rsp_query,s_rsp_price}!==held)$fatal(1,"held service response");end
   s_rsp_ready=1;@(negedge clk);s_rsp_ready=0;checks=checks+1;if(bad)fault_cases=fault_cases+1;
  end
 endtask
 task host_start;
  begin
   decision_lock=0;h_req_valid=1;h_req_op=1;h_req_cookie=456;h_req_node=101;h_req_net=12;
   while(!h_req_ready)@(negedge clk);@(negedge clk);h_req_valid=0;
   h_req_cookie=32'hbad;h_req_node=999;h_req_net=999;
   if(!host_pending||!b_req_valid||b_req_cookie!=456||b_req_node!=101||b_req_net!=12||b_req_op!=1)$fatal(1,"host capture");
   b_req_ready=1;@(negedge clk);b_req_ready=0;
  end
 endtask
 initial begin
  boot;h_req_valid=1;repeat(3)begin @(negedge clk);if(h_req_ready)$fatal(1,"host admitted while decision locked");end
  h_req_valid=0;service(4);backend(12345,0);reply(0,1,0);
  service(6);backend(12345,0);reply(0,7,0);
  boot;service(6);backend(12346,0);reply(5,7,1);
  boot;service(6);backend(12345,1);reply(3,7,1);
  boot;service(6);active_query=2;backend(12345,0);reply(5,7,1);
  boot;service(6);active_price=4;backend(12345,0);reply(5,7,1);
  boot;service(6);decision_lock=0;backend(12345,0);reply(5,7,1);
  boot;active=0;service(6);if(b_req_valid)$fatal(1,"inactive sent backend");reply(2,0,1);
  boot;service(3);if(b_req_valid)$fatal(1,"invalid kind sent backend");reply(1,0,1);
  boot;service(6);repeat(17)@(negedge clk);if(!fault||!b_req_valid)$fatal(1,"timeout withdrew captured request");backend(12345,0);reply(5,7,1);
  boot;service(6);backend(12345,0);abort=1;@(negedge clk);abort=0;reply(0,7,1);
  boot;service(6);b_fault=1;backend(12345,9);reply(3,7,1);
  boot;host_start;b_rsp_cookie=456;b_rsp_status=5;b_rsp_count=0;b_rsp_occupancy=2;b_rsp_will_overuse=1;b_rsp_valid=1;
  @(negedge clk);b_rsp_valid=0;
  if(!h_rsp_valid||h_rsp_status!=5||h_rsp_cookie!=456||fault||!host_pending)$fatal(1,"host logical failure forwarding");
  repeat(3)begin @(negedge clk);if(h_req_ready||!host_pending)$fatal(1,"host pending retired early");end
  h_rsp_ready=1;@(negedge clk);h_rsp_ready=0;checks=checks+1;
  host_start;b_rsp_cookie=457;b_rsp_status=0;b_rsp_valid=1;@(negedge clk);b_rsp_valid=0;
  if(!h_rsp_valid||h_rsp_status!=10||!fault)$fatal(1,"host cookie mismatch");checks=checks+1;fault_cases=fault_cases+1;
  boot;b_rsp_valid=1;@(negedge clk);b_rsp_valid=0;if(!fault||s_req_ready||h_req_ready)$fatal(1,"unowned backend");checks=checks+1;fault_cases=fault_cases+1;
  if(checks!=15||fault_cases!=12)$fatal(1,"counts %0d %0d",checks,fault_cases);
  $display("OWNER_BRIDGE_PASS checks=%0d fault_cases=%0d cycles=%0d",checks,fault_cases,cycles);$finish;
 end
