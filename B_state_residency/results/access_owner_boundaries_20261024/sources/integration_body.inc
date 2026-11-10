reg expecting_fault=0;
 integer fd,ctxfd,logfd,rc,i,row,case_id,saved_case,cases=0,steps=0,services=0,cycles=0,case_steps,case_services,j;
 integer native_reads=0,checkpoints=0,host_blocks=0,golden_count=0;
 reg[31:0]golden_node[0:1023];reg[159:0]golden_value[0:1023];
 reg[31:0]ins[0:19],outs[0:5];reg[639:0]expected_input;reg[191:0]expected_output;
 reg[31:0]parent_id,child_id,sink_id,pred_id,parent_prev,child_prev,visited,target,kind,phase,expected_node,value,final_bits,final_action;
 integer occ,uses,ctx_case,limit=0;string vecpath,ctxpath,outpath;
 reg[329:0]held_response;
 wire[329:0]response_bundle={rsp_status,rsp_cookie,rsp_parent,rsp_child,rsp_sink,rsp_net,rsp_bits,rsp_action,rsp_steps,rsp_services,rsp_query,rsp_price};
 reg owner_pending=0;integer owner_calls=0,owner_commands=0,owner_blocks=0;
 reg[110:0]owner_identity;
 always @(posedge clk)begin
  if(rst)owner_pending<=0;
  else begin
   if(dut.o_req_valid&&dut.o_req_ready)begin
    if(owner_pending||dut.o_req_node!=child_id||dut.o_req_net||!(dut.o_req_kind==4||dut.o_req_kind==6))$fatal(1,"owner request scope");
    owner_pending<=1;owner_identity<={dut.o_req_kind,dut.o_req_phase,dut.o_req_node,dut.o_req_net,dut.o_req_cookie,dut.o_req_query,dut.o_req_price};owner_calls=owner_calls+1;
   end
   if(dut.o_rsp_valid&&dut.o_rsp_ready)begin
    if(!owner_pending||{dut.o_rsp_kind,dut.o_rsp_phase,dut.o_rsp_node,dut.o_rsp_net,dut.o_rsp_cookie,dut.o_rsp_query,dut.o_rsp_price}!==owner_identity)$fatal(1,"owner identity echo");owner_pending<=0;
   end
   if(dut.access_pending)begin
    if(host_owner_req_ready||owner_cfg_ready)$fatal(1,"owner host/config admitted during decision");
    if(host_owner_req_valid)owner_blocks=owner_blocks+1;
   end
   if(dut.bridge_host_pending&&req_ready)$fatal(1,"decision admitted during owner transaction");
  end
 end
 integer old_occ=0,old_uses=0,old_child=0,nuser,branch;
 task owner_command(input integer operation,input[31:0]id,net);
  begin
   @(negedge clk);owner_commands=owner_commands+1;host_owner_req_op=operation;host_owner_req_cookie=owner_commands;host_owner_req_node=id;host_owner_req_net=net;host_owner_req_valid=1;
   wait(host_owner_req_ready);@(posedge clk);@(negedge clk);host_owner_req_valid=0;wait(host_owner_rsp_valid);@(negedge clk);
   if(fault||host_owner_rsp_status!=0||host_owner_rsp_cookie!=owner_commands)$fatal(1,"owner host response");
   $fdisplay(logfd,"O %0d %0d %0d %0d %0d %0d",operation,id,net,host_owner_rsp_count,host_owner_rsp_occupancy,host_owner_rsp_will_overuse);
   repeat(2)begin @(negedge clk);if(req_ready)$fatal(1,"decision during held host owner response");end
   host_owner_rsp_ready=1;@(negedge clk);host_owner_rsp_ready=0;
  end
 endtask
 task prepare_owner;
  begin
   for(branch=0;branch<old_uses;branch=branch+1)owner_command(2,old_child,0);
   for(nuser=1;nuser<=old_occ-(old_uses!=0);nuser=nuser+1)owner_command(2,old_child,nuser);
   for(branch=0;branch<uses;branch=branch+1)owner_command(1,child_id,0);
   for(nuser=1;nuser<=occ-(uses!=0);nuser=nuser+1)owner_command(1,child_id,nuser);
   old_child=child_id;old_occ=occ;old_uses=uses;
  end
 endtask
 reg[20:0]bound_page[0:31];reg[31:0]bound_valid=0;reg native_pending=0;integer pending_op,pending_slot,pending_node;reg[159:0]pending_value;reg pending_present;
 function integer lookup(input[31:0]id);integer i;begin lookup=-1;for(i=0;i<golden_count;i=i+1)if(golden_node[i]==id)lookup=i;end endfunction
 always @(posedge clk)begin
  cycles<=cycles+1;if(cycles>100000000)$fatal(1,"watchdog");
  if(rst)begin native_pending<=0;bound_valid<=0;end
  else begin
   if(fault&&!expecting_fault)$fatal(1,"fabric fault case=%0d astate=%0d dstate=%0d ast=%0d c_fault=%b d_fault=%b",saved_case,dut.access.controller.state,dut.dispatch.state,rsp_status,dut.c_fault,dut.d_fault);
   if(dut.a_busy)begin if(host_ctrl_ready||host_io_ready||req_ready)$fatal(1,"host admitted during decision");if(host_ctrl_valid&&host_io_valid)host_blocks=host_blocks+1;end
   if(dut.host_pending&&req_ready)$fatal(1,"decision admitted during host operation");

   if(dut.coordinates.pager.native_cmd_valid&&dut.coordinates.pager.native_cmd_ready)begin
    if(native_pending)$fatal(1,"native overlap");native_pending<=1;pending_op=dut.coordinates.pager.native_cmd_op;pending_slot=dut.coordinates.pager.native_cmd_slot;
    if(pending_op==2)begin
     if(!bound_valid[pending_slot])$fatal(1,"native read unbound");pending_node=bound_page[pending_slot]*8+dut.coordinates.pager.native_cmd_offset;j=lookup(pending_node);
     pending_present=j>=0;pending_value=j>=0?golden_value[j]:160'b0;
    end
    if(pending_op==1)bound_page[pending_slot]<=dut.coordinates.pager.native_cmd_page;
   end
   if(dut.coordinates.pager.native_rsp_valid&&dut.coordinates.pager.native_rsp_ready)begin
    if(!native_pending)$fatal(1,"native unowned");native_pending<=0;
    if(dut.coordinates.pager.native_rsp_status==0)begin
     if(pending_op==1)bound_valid[pending_slot]<=1;
     if(pending_op==4)bound_valid[pending_slot]<=0;
     if(pending_op==12)begin if(bound_valid!=0)$fatal(1,"checkpoint bound slots");checkpoints=checkpoints+1;end
    end
    if(pending_op==2)begin
     if(dut.coordinates.pager.native_rsp_status!=0||dut.coordinates.pager.native_rsp_payload!==pending_value||dut.coordinates.pager.native_rsp_present!==pending_present)$fatal(1,"native label mismatch node=%0d expected=%h got=%h present=%b/%b",pending_node,pending_value,dut.coordinates.pager.native_rsp_payload,pending_present,dut.coordinates.pager.native_rsp_present);
     native_reads=native_reads+1;
    end
   end
  end
 end
 integer owner_writes_before_control;
 task control(input integer op,q,p);
  begin
   owner_writes_before_control=owner_writes;@(negedge clk);host_ctrl_op=op;host_ctrl_query=q;host_ctrl_price=p;host_ctrl_valid=1;
   wait(host_ctrl_ready);@(posedge clk);@(negedge clk);host_ctrl_valid=0;wait(host_ctrl_rsp_valid);@(negedge clk);
   if(host_ctrl_status!=0)$fatal(1,"control %d/%d",op,host_ctrl_status);
   repeat(2)@(negedge clk);host_ctrl_rsp_ready=1;@(negedge clk);host_ctrl_rsp_ready=0;
   if(owner_writes!=owner_writes_before_control)$fatal(1,"query control mutated design owner");
   if(op==0)golden_count=0;
    $fdisplay(logfd,"Q %0d %0d %0d",op,q,p);
  end
 endtask
 task write_label(input integer n,f,input[31:0]v);
  integer gi;
  begin
   @(negedge clk);host_io_write=1;host_io_node=n;host_io_field=f;host_io_value=v;host_io_valid=1;
   wait(host_io_ready);@(posedge clk);@(negedge clk);host_io_valid=0;wait(host_io_rsp_valid);@(negedge clk);
   if(host_io_status!=0)$fatal(1,"label write");host_io_rsp_ready=1;@(negedge clk);host_io_rsp_ready=0;
   gi=lookup(n);if(gi<0)begin gi=golden_count;golden_count=golden_count+1;if(golden_count>1024)$fatal(1,"golden capacity");golden_node[gi]=n;golden_value[gi]=0;end
   golden_value[gi][f*32+:32]=v; $fdisplay(logfd,"L %0d %0d %0d",n,f,v);
  end
 endtask
 task read_row;
 begin
  rc=$fscanf(fd,"%d %d",row,case_id);if(rc!=2)$fatal(1,"header parse");
  for(i=0;i<20;i=i+1)begin rc=$fscanf(fd,"%h",ins[i]);if(rc!=1)$fatal(1,"input parse");expected_input[i*32+:32]=ins[i];end
  for(i=0;i<6;i=i+1)begin rc=$fscanf(fd,"%h",outs[i]);if(rc!=1)$fatal(1,"output parse");expected_output[i*32+:32]=outs[i];end
  rc=$fscanf(fd,"\n");
 end endtask

 integer failures=0,recoveries=0,reset_index=0,ix,seek_rc,first_owner_writes;reg[63:0]held_owner_ar;integer max_cold_wait=0;
 localparam[447:0]CONFIG=448'h000000210000001b00000002fffffffe0000001d00000000000000010000000100000000000000000000000000000006000000fd00000011;
 always @(posedge clk)if(!rst&&dut.dispatch.elapsed>max_cold_wait)max_cold_wait=dut.dispatch.elapsed;
 task setup;
  begin
   @(negedge clk);rst=1;expecting_fault=0;abort=0;hold_owner_ar=0;inject_owner=0;inject_owner_b=0;req_valid=0;rsp_ready=0;host_owner_req_valid=0;host_owner_rsp_ready=0;
   host_ctrl_valid=0;host_ctrl_rsp_ready=0;host_io_valid=0;host_io_rsp_ready=0;g_cfg_valid=0;t_cfg_valid=0;owner_cfg_valid=0;
   repeat(4)@(negedge clk);
   // Whole-design recovery explicitly reloads owner backing; graph/tables immutable.
   seek_rc=$fseek(mem_owner.fd[0],0,0);for(ix=0;ix<owner_image_size;ix=ix+1)$fwrite(mem_owner.fd[0],"%c",8'b0);$fflush(mem_owner.fd[0]);
   reset_index=reset_index+1;$fdisplay(mem_owner.logfd,"RESET %0d",reset_index);$fflush(mem_owner.logfd);
   rst=0;@(negedge clk);g_cfg_valid=1;t_cfg_valid=1;wait(g_cfg_ready&&t_cfg_ready);@(posedge clk);@(negedge clk);g_cfg_valid=0;t_cfg_valid=0;
   wait(g_cfg_rsp_valid&&t_cfg_rsp_valid);@(negedge clk);if(g_cfg_status||t_cfg_status)$fatal(1,"graph/table config");g_cfg_rsp_ready=1;t_cfg_rsp_ready=1;@(negedge clk);g_cfg_rsp_ready=0;t_cfg_rsp_ready=0;
   owner_cfg_valid=1;wait(owner_cfg_ready);@(posedge clk);@(negedge clk);owner_cfg_valid=0;wait(owner_cfg_rsp_valid);@(negedge clk);if(owner_cfg_status)$fatal(1,"owner config");owner_cfg_rsp_ready=1;@(negedge clk);owner_cfg_rsp_ready=0;
   parent_id=18;child_id=6;sink_id=36;old_occ=0;old_uses=0;occ=1;uses=0;golden_count=0;saved_case=3888;
  end
 endtask
 task prepare;
  begin owner_command(1,6,1);control(0,1,3);end
 endtask
 task request_decision;
  begin
   @(negedge clk);req_config=CONFIG;req_parent=18;req_child=6;req_sink=36;req_net=0;req_query=1;req_price=3;req_cookie=reset_index;req_valid=1;
   wait(req_ready);@(posedge clk);@(negedge clk);req_valid=0;
  end
 endtask
 task normal_decision;
  begin
   request_decision;wait(rsp_valid);@(negedge clk);
   if(fault||rsp_status||rsp_action!=1||rsp_bits||rsp_steps!=7||rsp_services!=6)$fatal(1,"recovery decision result %0d/%0d",rsp_steps,rsp_services);
   rsp_ready=1;@(negedge clk);rsp_ready=0;control(2,1,3);owner_command(0,6,0);
   if(host_owner_rsp_count!=0||host_owner_rsp_occupancy!=1)$fatal(1,"recovery persisted owner");recoveries=recoveries+1;
  end
 endtask
 task finish_fault;
  begin
   wait(rsp_valid);@(negedge clk);if(!fault||rsp_status!=5)$fatal(1,"expected integration fault %0d",rsp_status);
   held_response=response_bundle;repeat(7)begin @(negedge clk);if(response_bundle!==held_response)$fatal(1,"fault response changed");end
   rsp_ready=1;@(negedge clk);rsp_ready=0;repeat(100)@(negedge clk);
   if(req_ready||host_owner_req_ready||!fault||dut.raw_busy)$fatal(1,"fault did not stop/drain");failures=failures+1;
   $display("ACCESS_OWNER_FAULT kind=%0d status=5 drained=1",failures);
   setup;prepare;normal_decision;
  end
 endtask
 initial begin
  g_cfg_nodes=64;g_cfg_edges=0;t_cfg_rows=128;t_cfg_columns=64;
  g_cfg_offsets_base=64'h1fffff000;g_cfg_edges_base=64'h10fffff000;g_cfg_attrs_base=64'h20fffff000;t_cfg_rows_base=64'h31fffff000;t_cfg_columns_base=64'h41fffff000;
  graph_size0=320;graph_size1=0;graph_size2=2048;table_size0=1024;table_size1=512;
  owner_cfg_primary=64'h51fffff000;owner_cfg_pool=owner_cfg_primary+1024+4096;owner_cfg_allocator=owner_cfg_pool+1024+4096;owner_cfg_nodes=64;owner_cfg_capacity=64;owner_image_size=10304;
  logfd=$fopen("integration_events.txt","w");repeat(4)@(negedge clk);
  setup;prepare;normal_decision;
  setup;prepare;expecting_fault=1;inject_owner=1;request_decision;finish_fault;
  setup;prepare;expecting_fault=1;hold_owner_ar=1;request_decision;
  wait(owner_m_arvalid);@(negedge clk);held_owner_ar=owner_m_araddr;abort=1;repeat(3)@(negedge clk);
  if(!owner_m_arvalid||owner_m_araddr!==held_owner_ar||!fault)$fatal(1,"integrated abort withdrew owner AR");abort=0;hold_owner_ar=0;finish_fault;
  setup;prepare;expecting_fault=1;request_decision;wait(dut.o_rsp_valid);@(negedge clk);abort=1;@(negedge clk);abort=0;finish_fault;
  setup;expecting_fault=1;inject_owner_b=1;host_owner_req_op=1;host_owner_req_node=6;host_owner_req_net=1;host_owner_req_cookie=32'hfeed;host_owner_req_valid=1;
  wait(host_owner_req_ready);@(posedge clk);@(negedge clk);host_owner_req_valid=0;wait(host_owner_rsp_valid);@(negedge clk);
  if(!fault||host_owner_rsp_status!=9||host_owner_rsp_cookie!=32'hfeed)$fatal(1,"owner host B failure propagation");
  host_owner_rsp_ready=1;@(negedge clk);host_owner_rsp_ready=0;repeat(100)@(negedge clk);if(req_ready||dut.raw_busy)$fatal(1,"host B did not drain and stop");failures=failures+1;
  $display("ACCESS_OWNER_FAULT kind=4 status=host9 drained=1");setup;prepare;normal_decision;
  if(failures!=4||recoveries!=5||max_cold_wait<262100)$fatal(1,"counts/default cold wait %0d/%0d/%0d",failures,recoveries,max_cold_wait);
  $display("ACCESS_OWNER_BOUNDARIES_PASS faults=%0d recoveries=%0d max_service_cycles=%0d cycles=%0d",failures,recoveries,max_cold_wait,cycles);$finish;
 end
