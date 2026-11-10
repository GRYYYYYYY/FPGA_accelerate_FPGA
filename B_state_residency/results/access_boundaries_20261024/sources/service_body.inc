 integer cycles=0,cases=0,resets=0,i,j,baseline_cycles=0,begin_cycle;
 reg auto_service=0,auto_pending=0;integer bad_field=-1;
 reg[329:0]held;
 wire[329:0]bundle={rsp_status,rsp_cookie,rsp_parent,rsp_child,rsp_sink,rsp_net,rsp_bits,rsp_action,rsp_steps,rsp_services,rsp_query,rsp_price};
 always @(posedge clk)begin cycles<=cycles+1;if(cycles>100000)$fatal(1,"watchdog");end
 // Independent one-outstanding echo service, only VISITED/TARGET for this fixture.
 always @(negedge clk)begin
  if(rst)begin auto_pending=0;end
  else if(auto_service)begin
   svc_ready=1;
   if(auto_pending)begin svc_rsp_valid=0;auto_pending=0;end
   if(dut.controller.state==4&&!svc_rsp_valid)begin
    svc_rsp_cookie=svc_cookie;svc_rsp_kind=svc_kind;svc_rsp_phase=svc_phase;svc_rsp_node=svc_node;svc_rsp_net=svc_net;svc_rsp_query=svc_query;svc_rsp_price=svc_price;
    svc_rsp_value=0;svc_rsp_status=0;svc_rsp_valid=1;auto_pending=1;
   end
  end
 end
 task reset_case;
 begin
  @(negedge clk);rst=1;auto_service=0;auto_pending=0;req_valid=0;rsp_ready=0;svc_ready=0;svc_rsp_valid=0;svc_rsp_status=0;svc_fault=0;
  abort=0;enable=1;active=1;active_query=1;active_price=3;req_query=1;req_price=3;req_config=0;
  req_config[31:0]=17;req_config[95:64]=12;req_config[127:96]=12;req_config[159:128]=12;
  repeat(2)@(negedge clk);rst=0;@(negedge clk);if(fault||!req_ready)$fatal(1,"reset");resets=resets+1;
 end endtask
 task start;
 begin
  @(negedge clk);req_valid=1;req_cookie=42;req_parent=10;req_child=11;req_sink=12;req_net=13;
  wait(req_ready);@(posedge clk);@(negedge clk);req_valid=0;
 end endtask
 task retire(input integer status,input bad);
 begin
  wait(rsp_valid);@(negedge clk);if(rsp_status!=status||fault!==bad)$fatal(1,"case=%0d status=%0d/%0d fault=%b state=%0d",cases,rsp_status,status,fault,dut.controller.state);
  held=bundle;repeat(5)begin @(negedge clk);if(!rsp_valid||bundle!==held||req_ready)$fatal(1,"unstable");end
  rsp_ready=1;@(negedge clk);rsp_ready=0;repeat(3)@(negedge clk);if(bad&&(!fault||req_ready))$fatal(1,"not sticky");cases=cases+1;
 end endtask
 task normal;
 begin
  auto_service=1;begin_cycle=cycles;start;wait(rsp_valid);@(negedge clk);baseline_cycles=cycles-begin_cycle;
  if(rsp_action!=1||rsp_bits||rsp_steps!=3||rsp_services!=2)$fatal(1,"normal decision");retire(0,0);auto_service=0;
 end endtask
 initial begin
  reset_case;active=0;start;retire(1,0);
  reset_case;req_query=2;start;retire(2,0);
  reset_case;req_price=4;start;retire(2,0);
  reset_case;req_config[63:32]=512;start;retire(3,1);
  // Every service echo field, plus nonzero status, is independently corrupted.
  for(i=0;i<8;i=i+1)begin
   reset_case;start;wait(svc_valid);@(negedge clk);svc_ready=1;
   svc_rsp_cookie=svc_cookie;svc_rsp_kind=svc_kind;svc_rsp_phase=svc_phase;svc_rsp_node=svc_node;svc_rsp_net=svc_net;svc_rsp_query=svc_query;svc_rsp_price=svc_price;svc_rsp_value=0;
   @(negedge clk);svc_ready=0;
   case(i)0:svc_rsp_cookie=svc_rsp_cookie+1;1:svc_rsp_kind=2;2:svc_rsp_phase=2;3:svc_rsp_node=12;4:svc_rsp_net=14;5:svc_rsp_query=2;6:svc_rsp_price=4;7:svc_rsp_status=1;endcase
   svc_rsp_valid=1;wait(svc_rsp_ready);@(posedge clk);@(negedge clk);svc_rsp_valid=0;retire(i==7?3:4,1);
  end
  reset_case;svc_rsp_valid=1;@(negedge clk);if(!fault||rsp_valid||req_ready)$fatal(1,"unowned response");svc_rsp_valid=0;@(negedge clk);if(!fault)$fatal(1,"idle sticky");cases=cases+1;
  reset_case;start;retire(5,1); // actual 128-cycle timeout while waiting for service ready
  reset_case;normal;auto_service=1;start;retire(6,1);auto_service=0; // actual TOKEN_BITS3 exhaustion
  for(i=0;i<4;i=i+1)for(j=0;j<2;j=j+1)begin
   reset_case;auto_service=1;start;
   if(j)begin wait(rsp_valid);@(negedge clk);held=bundle;end
   else begin repeat(4)@(negedge clk);end
   case(i)0:abort=1;1:active=0;2:active_query=2;3:active_price=4;endcase
   @(negedge clk);if(j&&held!==bundle)$fatal(1,"late owner/abort changed result");retire(j?0:5,1);auto_service=0;
  end
  reset_case;start;wait(svc_valid);@(negedge clk);svc_fault=1;retire(5,1);
  // Backpressure is outside timeout, even after a successful multi-step decision.
  reset_case;auto_service=1;start;wait(rsp_valid);@(negedge clk);held=bundle;
  repeat(140)begin @(negedge clk);if(fault||!rsp_valid||bundle!==held)$fatal(1,"backpressure timeout");end
  retire(0,0);auto_service=0;
  // Reset at every cycle offset across computation, service, and exposed response.
  for(i=0;i<96;i=i+1)begin
   reset_case;auto_service=1;start;repeat(i)@(negedge clk);
   reset_case;normal;
  end
  $display("ACCESS_BOUNDARIES_PASS cases=%0d reset_offsets=96 resets=%0d normal_cycles=%0d cycles=%0d",cases,resets,baseline_cycles,cycles);$finish;
 end
