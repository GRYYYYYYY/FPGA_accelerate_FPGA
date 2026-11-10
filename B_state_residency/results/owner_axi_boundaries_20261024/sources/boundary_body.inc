 integer cycles=0,faults=0,recoveries=0,checks=0,fixture=0,cookie=1000,rc,i,j,start_w,start_b;
 reg[127:0]value,held;reg[100:0]held_response;
 reg stalled_ar=0,stalled_aw=0,stalled_w=0;reg[63:0]held_ar,held_aw,held_strb;reg[511:0]held_w;
 always @(posedge clk)begin
  cycles=cycles+1;if(cycles>300000)$fatal(1,"boundary watchdog fixture=%0d state=%0d",fixture,dut.state);
  if(!rst)begin
   if(stalled_ar&&(!m_arvalid||m_araddr!==held_ar))$fatal(1,"AR withdrawn/changed");
   if(stalled_aw&&(!m_awvalid||m_awaddr!==held_aw))$fatal(1,"AW withdrawn/changed");
   if(stalled_w&&(!m_wvalid||m_wdata!==held_w||m_wstrb!==held_strb))$fatal(1,"W withdrawn/changed");
  end
  stalled_ar=!rst&&m_arvalid&&!m_arready;held_ar=m_araddr;
  stalled_aw=!rst&&m_awvalid&&!m_awready;held_aw=m_awaddr;
  stalled_w=!rst&&m_wvalid&&!m_wready;held_w=m_wdata;held_strb=m_wstrb;
 end
 task put_record(input integer offset,input[127:0]data);
  integer n;
  begin
   for(n=0;n<16;n=n+1)begin rc=$fseek(memory.fd[0],offset+n,0);if(rc!=0)$fatal(1,"host seek");$fwrite(memory.fd[0],"%c",data[n*8+:8]);end
   $fflush(memory.fd[0]);$fdisplay(memory.logfd,"H %0d %032h",offset,data);$fflush(memory.logfd);
  end
 endtask
 task get_record(input integer offset,output[127:0]data);
  reg[7:0]bytes[0:15];integer n;
  begin
   rc=$fseek(memory.fd[0],offset,0);if(rc!=0)$fatal(1,"read host seek");rc=$fread(bytes,memory.fd[0]);if(rc!=16)$fatal(1,"host read");
   data=0;for(n=0;n<16;n=n+1)data[n*8+:8]=bytes[n];
  end
 endtask
 task reset_design;
  integer n;
  begin
   @(negedge clk);rst=1;abort=0;req_valid=0;rsp_ready=0;cfg_valid=0;cfg_rsp_ready=0;
   hold_ar=0;hold_aw=0;hold_w=0;hold_r=0;hold_b=0;inject_r=0;inject_b=0;bad_rid=0;bad_bid=0;bad_last=0;phantom_r=0;phantom_b=0;
   cfg_primary=BASE;cfg_pool=BASE+4096;cfg_allocator=BASE+12288;cfg_nodes=128;cfg_capacity=256;
   repeat(3)@(negedge clk);
   // Explicit new-design load, not a query reset and not a failed-write rollback.
   rc=$fseek(memory.fd[0],0,0);for(n=0;n<16384;n=n+1)$fwrite(memory.fd[0],"%c",8'b0);$fflush(memory.fd[0]);
   fixture=fixture+1;$fdisplay(memory.logfd,"RESET %0d",fixture);$fflush(memory.logfd);
   rst=0;@(negedge clk);
  end
 endtask
 task configure(input integer expected);
  begin
   cfg_valid=1;while(!cfg_ready)@(negedge clk);@(negedge clk);cfg_valid=0;
   while(!cfg_rsp_valid)@(negedge clk);
   if(cfg_status!==expected)$fatal(1,"config status %0d expected %0d",cfg_status,expected);
   repeat(2)begin @(negedge clk);if(!cfg_rsp_valid||cfg_status!==expected)$fatal(1,"config stability");end
   cfg_rsp_ready=1;@(negedge clk);cfg_rsp_ready=0;checks=checks+1;
  end
 endtask
 task boot;
  begin reset_design;configure(0);if(!configured||fault)$fatal(1,"boot");end
 endtask
 task send(input[2:0]operation,input[31:0]node_id,net_id);
  begin
   @(negedge clk);cookie=cookie+1;req_op=operation;req_node=node_id;req_net=net_id;req_cookie=cookie;req_valid=1;
   while(!req_ready)@(negedge clk);@(negedge clk);req_valid=0;
  end
 endtask
 task normal(input[2:0]operation,input[31:0]node_id,net_id,input integer status,count,occ);
  begin
   send(operation,node_id,net_id);while(!rsp_valid)begin @(negedge clk);if(fault)$fatal(1,"normal fault fixture=%0d",fixture);end
   if(fault||rsp_status!==status||rsp_cookie!==cookie||rsp_count!==count||rsp_occupancy!==occ)$fatal(1,"normal result fixture=%0d status=%0d",fixture,rsp_status);
   rsp_ready=1;@(negedge clk);rsp_ready=0;checks=checks+1;
  end
 endtask
 task fault_result(input integer status);
  begin
   while(!rsp_valid)@(negedge clk);
   if(!fault||rsp_status!==status||rsp_cookie!==cookie||req_ready)$fatal(1,"fault result fixture=%0d status=%0d expected=%0d",fixture,rsp_status,status);
   held_response={rsp_status,rsp_cookie,rsp_count,rsp_occupancy,rsp_will_overuse};
   repeat(7)begin @(negedge clk);if(!rsp_valid||!fault||{rsp_status,rsp_cookie,rsp_count,rsp_occupancy,rsp_will_overuse}!==held_response)$fatal(1,"fault reply stability");end
   rsp_ready=1;@(negedge clk);rsp_ready=0;
   repeat(100)@(negedge clk);
   if(!fault||req_ready||cfg_ready||dut.state!=0||m_arvalid||m_awvalid||m_wvalid)$fatal(1,"failed to drain and stop fixture=%0d state=%0d",fixture,dut.state);
   faults=faults+1;$display("OWNER_FAULT fixture=%0d status=%0d drained=1",fixture,status);
   boot;normal(1,0,0,0,1,1);normal(0,0,0,0,1,1);recoveries=recoveries+1;
  end
 endtask
 initial begin
  repeat(4)@(negedge clk);
  reset_design;cfg_nodes=0;configure(1);
  reset_design;cfg_primary=BASE+1;configure(1);
  reset_design;cfg_pool=BASE;configure(1);
  reset_design;cfg_allocator=BASE;configure(1);
  reset_design;cfg_primary=64'hffffffffffffffc0;configure(1);
  reset_design;cfg_pool=64'hffffffffffffffc0;configure(1);
  reset_design;cfg_capacity=0;configure(0);normal(1,0,0,0,1,1);normal(1,0,1,5,0,1);
  reset_design;normal(0,0,0,13,0,0);
  boot;inject_r=1;send(0,0,0);fault_result(9);
  boot;bad_rid=1;send(0,0,0);fault_result(9);
  boot;bad_last=1;send(0,0,0);fault_result(9);
  boot;inject_b=1;send(1,0,0);fault_result(9);
  boot;bad_bid=1;send(1,0,0);fault_result(9);
  boot;normal(1,0,0,0,1,1);start_w=writes;start_b=bresponses;send(1,0,1);
  while(bresponses<start_b+1)@(negedge clk);inject_b=1;
  while(!rsp_valid)@(negedge clk);
  if(writes-start_w!=2)$fatal(1,"partial write bound %0d",writes-start_w);
  get_record(12288,value);if(value!=0)$fatal(1,"allocator unexpectedly committed");
  get_record(0,value);if(value[95:64]!=1||value[63:48]!=2)$fatal(1,"partial primary not physically visible");
  get_record(4096,value);if(value[31:0]!=2||value[63:32]!=1)$fatal(1,"partial pool not physically visible");
  $display("OWNER_PARTIAL_COMMIT writes=2 allocator_unchanged=1 backing_changed=1");fault_result(9);
  boot;put_record(12288,{32'd1,96'b0});send(0,0,0);fault_result(6);
  boot;put_record(0,{32'd1,96'b0});send(0,0,0);fault_result(6);
  boot;put_record(0,{64'b0,32'h00020001,32'd1});send(0,0,0);fault_result(6);
  boot;put_record(0,{32'b0,32'd1,32'h00010001,32'd1});send(0,0,0);fault_result(6);
  boot;put_record(0,{64'b0,32'h00010001,32'd1});put_record(12288,{32'b0,32'b0,32'd1,32'd1});put_record(4096,{32'b0,32'd1,64'b0});send(1,0,1);fault_result(6);
  boot;put_record(0,{32'b0,32'd1,32'h00030001,32'd1});put_record(12288,{32'b0,32'd2,32'b0,32'd2});put_record(4096,{32'b0,32'd2,32'd1,32'd2});put_record(4112,{64'b0,32'd1,32'd2});send(0,0,0);fault_result(6);
  boot;hold_ar=1;send(0,0,0);abort=1;repeat(3)@(negedge clk);
  if(!m_arvalid||!rsp_valid||!fault)$fatal(1,"AR abort did not hold VALID");abort=0;hold_ar=0;fault_result(12);
  boot;hold_aw=1;send(1,0,0);while(!dut.w_done)@(negedge clk);abort=1;repeat(3)@(negedge clk);
  if(!m_awvalid||!rsp_valid||!fault)$fatal(1,"AW abort did not hold VALID");abort=0;hold_aw=0;fault_result(12);
  boot;hold_w=1;send(1,0,0);while(!dut.aw_done)@(negedge clk);abort=1;repeat(3)@(negedge clk);
  if(!m_wvalid||!rsp_valid||!fault)$fatal(1,"W abort did not hold VALID");abort=0;hold_w=0;fault_result(12);
  boot;send(1,0,0);while(dut.state!=8)@(negedge clk);start_w=writes;abort=1;repeat(2)@(negedge clk);abort=0;
  if(writes!=start_w)$fatal(1,"abort PLAN issued a write");fault_result(12);
  boot;hold_ar=1;send(0,0,0);while(!rsp_valid)@(negedge clk);
  if(!m_arvalid)$fatal(1,"timeout withdrew AR");hold_ar=0;fault_result(11);
  boot;hold_b=1;send(1,0,0);while(!raw_bvalid)@(negedge clk);
  while(dut.elapsed<2047)@(negedge clk);hold_b=0;@(negedge clk);
  if(!rsp_valid||rsp_status!=11)$fatal(1,"last B/timeout tie");fault_result(11);
  boot;send(0,0,0);while(!rsp_valid)@(negedge clk);held_response={rsp_status,rsp_cookie,rsp_count,rsp_occupancy,rsp_will_overuse};
  abort=1;repeat(2)@(negedge clk);abort=0;
  if({rsp_status,rsp_cookie,rsp_count,rsp_occupancy,rsp_will_overuse}!==held_response)$fatal(1,"late abort changed exposed response");fault_result(0);
  boot;send(0,0,0);while(!rsp_valid)@(negedge clk);phantom_r=1;repeat(2)@(negedge clk);phantom_r=0;fault_result(0);
  boot;phantom_r=1;repeat(2)@(negedge clk);phantom_r=0;
  if(!fault||req_ready||rsp_valid)$fatal(1,"idle R");$display("OWNER_IDLE_FAULT kind=R");faults=faults+1;boot;normal(0,0,0,0,0,0);recoveries=recoveries+1;
  boot;phantom_b=1;repeat(2)@(negedge clk);phantom_b=0;
  if(!fault||req_ready||rsp_valid)$fatal(1,"idle B");$display("OWNER_IDLE_FAULT kind=B");faults=faults+1;boot;normal(0,0,0,0,0,0);recoveries=recoveries+1;
  if(faults!=22||recoveries!=22)$fatal(1,"case counts %0d %0d",faults,recoveries);
  $display("OWNER_BOUNDARIES_PASS faults=%0d recoveries=%0d checks=%0d cycles=%0d",faults,recoveries,checks,cycles);$finish;
 end
