 integer fd_vec,fd_out,fd_attrs,rc,k,j,nread,cycles=0,queries=0,host_blocks=0,native_reads=0,services=0,builds=0,checkpoints=0;
 integer golden_count=0;reg[31:0]golden_node[0:1023];reg[159:0]golden_value[0:1023];
 reg[20:0]bound_page[0:31];reg[31:0]bound_valid=0;reg native_pending=0;integer pending_op,pending_slot,pending_node;reg[159:0]pending_value;reg pending_present;
 string vecpath,outpath,command;
 integer cookie,op,node,query,price,control_op,control_query,control_price,field;
 reg[31:0]value,expected[0:8];reg[255:0]expected_attrs;
 wire[554:0]response_bundle={rsp_status,rsp_op,rsp_query,rsp_price,rsp_cookie,rsp_node,rsp_y,rsp_slr,rsp_next,rsp_prev_column,rsp_label_prev,rsp_north,rsp_prev_read,rsp_prev_present,rsp_attrs};
 reg[554:0]held_response;
 function integer lookup(input[31:0]id);integer i;begin lookup=-1;for(i=0;i<golden_count;i=i+1)if(golden_node[i]==id)lookup=i;end endfunction
 always @(posedge clk)begin
  cycles<=cycles+1;if(cycles>100000000)$fatal(1,"watchdog");
  if(rst)begin native_pending<=0;bound_valid<=0;end
  else begin
   if(fault)$fatal(1,"coordinate fault cookie=%0d state=%0d status=%0d gf=%b tf=%b pf=%b unexpected=%b",req_cookie,dut.controller.state,rsp_status,dut.g_fault,dut.t_fault,dut.p_fault,dut.controller.unexpected);
   if(busy)begin
    if(host_ctrl_ready||host_io_ready||req_ready)$fatal(1,"host admitted during coordinate request");
    if(host_ctrl_valid&&host_io_valid)host_blocks=host_blocks+1;
   end
   if(dut.host_pending&&req_ready)$fatal(1,"coordinate admitted during host command");
   if(dut.pager.native_cmd_valid&&dut.pager.native_cmd_ready)begin
    if(native_pending)$fatal(1,"native overlap");native_pending<=1;pending_op=dut.pager.native_cmd_op;pending_slot=dut.pager.native_cmd_slot;
    if(pending_op==2)begin
     if(!bound_valid[pending_slot])$fatal(1,"native read unbound");pending_node=bound_page[pending_slot]*8+dut.pager.native_cmd_offset;j=lookup(pending_node);
     pending_present=j>=0;pending_value=j>=0?golden_value[j]:160'b0;
    end
    if(pending_op==1)bound_page[pending_slot]<=dut.pager.native_cmd_page;
   end
   if(dut.pager.native_rsp_valid&&dut.pager.native_rsp_ready)begin
    if(!native_pending)$fatal(1,"native unowned");native_pending<=0;
    if(dut.pager.native_rsp_status==0)begin
     if(pending_op==1)bound_valid[pending_slot]<=1;
     if(pending_op==4)bound_valid[pending_slot]<=0;
     if(pending_op==12)begin if(bound_valid!=0)$fatal(1,"checkpoint bound slots");checkpoints=checkpoints+1;end
    end
    if(pending_op==2)begin
     if(dut.pager.native_rsp_status!=0||dut.pager.native_rsp_payload!==pending_value||dut.pager.native_rsp_present!==pending_present)$fatal(1,"native label mismatch node=%0d expected=%h got=%h present=%b/%b",pending_node,pending_value,dut.pager.native_rsp_payload,pending_present,dut.pager.native_rsp_present);
     native_reads=native_reads+1;
    end
   end
  end
 end
 task control(input integer op,q,p);
  begin
   @(negedge clk);host_ctrl_op=op;host_ctrl_query=q;host_ctrl_price=p;host_ctrl_valid=1;
   wait(host_ctrl_ready);@(posedge clk);@(negedge clk);host_ctrl_valid=0;wait(host_ctrl_rsp_valid);@(negedge clk);
   if(host_ctrl_status!=0)$fatal(1,"control %d/%d",op,host_ctrl_status);
   repeat(2)@(negedge clk);host_ctrl_rsp_ready=1;@(negedge clk);host_ctrl_rsp_ready=0;
   if(op==0)golden_count=0;
   $fdisplay(fd_out,"Q %0d %0d %0d",op,q,p);
  end
 endtask
 task write_label(input integer n,f,input[31:0]v);
  integer gi;
  begin
   @(negedge clk);host_io_write=1;host_io_node=n;host_io_field=f;host_io_value=v;host_io_valid=1;
   wait(host_io_ready);@(posedge clk);@(negedge clk);host_io_valid=0;wait(host_io_rsp_valid);@(negedge clk);
   if(host_io_status!=0)$fatal(1,"label write");host_io_rsp_ready=1;@(negedge clk);host_io_rsp_ready=0;
   gi=lookup(n);if(gi<0)begin gi=golden_count;golden_count=golden_count+1;if(golden_count>1024)$fatal(1,"golden capacity");golden_node[gi]=n;golden_value[gi]=0;end
   golden_value[gi][f*32+:32]=v;$fdisplay(fd_out,"L %0d %0d %0d",n,f,v);
  end
 endtask
 initial begin
  if(!$value$plusargs("vectors=%s",vecpath)||!$value$plusargs("output=%s",outpath))$fatal(1,"TB paths");
  if(!$value$plusargs("nodes=%d",g_cfg_nodes)||!$value$plusargs("edges=%d",g_cfg_edges)||!$value$plusargs("rows=%d",t_cfg_rows)||!$value$plusargs("columns=%d",t_cfg_columns))$fatal(1,"TB sizes");
  fd_vec=$fopen(vecpath,"r");fd_out=$fopen(outpath,"w");if(!fd_vec||!fd_out)$fatal(1,"TB opens");
  g_cfg_offsets_base=64'h1fffff000;g_cfg_edges_base=64'h10fffff000;g_cfg_attrs_base=64'h20fffff000;
  t_cfg_rows_base=64'h31fffff000;t_cfg_columns_base=64'h41fffff000;
  graph_size0=((g_cfg_nodes+64'd1)*4+63)&~64'd63;graph_size1=(g_cfg_edges*64'd4+63)&~64'd63;graph_size2=(g_cfg_nodes*64'd32+63)&~64'd63;
  table_size0=(t_cfg_rows*64'd8+63)&~64'd63;table_size1=(t_cfg_columns*64'd8+63)&~64'd63;
  rst=1;repeat(5)@(negedge clk);rst=0;
  @(negedge clk);g_cfg_valid=1;t_cfg_valid=1;wait(g_cfg_ready&&t_cfg_ready);@(posedge clk);@(negedge clk);g_cfg_valid=0;t_cfg_valid=0;
  wait(g_cfg_rsp_valid&&t_cfg_rsp_valid);@(negedge clk);if(g_cfg_status||t_cfg_status)$fatal(1,"configure");g_cfg_rsp_ready=1;t_cfg_rsp_ready=1;@(negedge clk);g_cfg_rsp_ready=0;t_cfg_rsp_ready=0;
  while(!$feof(fd_vec))begin
   rc=$fscanf(fd_vec,"%s",command);if(rc!=1)$fatal(1,"command parse");
   if(command=="C")begin rc=$fscanf(fd_vec,"%d %d %d\n",control_op,control_query,control_price);if(rc!=3)$fatal(1,"C parse");control(control_op,control_query,control_price);end
   else if(command=="W")begin rc=$fscanf(fd_vec,"%d %d %h\n",node,field,value);if(rc!=3)$fatal(1,"W parse");write_label(node,field,value);end
   else if(command=="R")begin
    rc=$fscanf(fd_vec,"%d %d %d %d %d %h %h %h %h %h %h %h %h %h %h\n",cookie,op,node,query,price,expected[0],expected[1],expected[2],expected[3],expected[4],expected[5],expected[6],expected[7],expected[8],expected_attrs);if(rc!=15)$fatal(1,"R parse rc=%0d",rc);
    @(negedge clk);req_cookie=cookie;req_op=op;req_node=node;req_query=query;req_price=price;req_valid=1;
    wait(req_ready);@(posedge clk);@(negedge clk);req_valid=0;
    host_ctrl_valid=1;host_ctrl_op=2;host_ctrl_query=p_active_query;host_ctrl_price=p_active_price;
    host_io_valid=1;host_io_node=node;host_io_field=2;host_io_value=32'hbadabcde;host_io_write=1;
    wait(rsp_valid);@(negedge clk);
    if(rsp_cookie!==cookie||rsp_op!==op[1:0]||rsp_node!==node||rsp_query!==query[1:0]||rsp_price!==price[3:0])$fatal(1,"response identity");
    if(rsp_status!==expected[0][3:0]||rsp_y!==expected[1]||rsp_slr!==expected[2]||rsp_next!==expected[3]||rsp_prev_column!==expected[4]||rsp_label_prev!==expected[5]||rsp_prev_read!==expected[6][0]||rsp_prev_present!==expected[7][0]||rsp_north!==expected[8][0]||rsp_attrs!==expected_attrs)$fatal(1,"response cookie=%0d op=%0d node=%0d status=%0d/%0d y=%0d/%0d prev=%h/%h present=%b/%b attrs=%h/%h",cookie,op,node,rsp_status,expected[0],rsp_y,expected[1],rsp_label_prev,expected[5],rsp_prev_present,expected[7][0],rsp_attrs,expected_attrs);
    held_response=response_bundle;repeat(3)begin @(negedge clk);if(!rsp_valid||response_bundle!==held_response)$fatal(1,"response unstable");end
    $fdisplay(fd_out,"R %0d %0d %0d %0d %0d %h %h %h %h %h %h %h %h %h %064h",cookie,rsp_op,rsp_node,rsp_query,rsp_price,rsp_status,rsp_y,rsp_slr,rsp_next,rsp_prev_column,rsp_label_prev,rsp_prev_read,rsp_prev_present,rsp_north,rsp_attrs);
    rsp_ready=1;@(negedge clk);rsp_ready=0;host_ctrl_valid=0;host_io_valid=0;queries=queries+1;
   end else $fatal(1,"unknown command %s",command);
  end
  if(g_reads!=g_rbeats||t_reads!=t_rbeats||p_writes!=p_bs||native_pending||dut.p_page_leases||dut.p_memory_leases)$fatal(1,"outstanding memory");
  $fflush(fd_out);$fclose(fd_out);
  $display("COORDINATE_PASS queries=%0d native_reads=%0d checkpoints=%0d host_blocks=%0d graph_reads=%0d table_reads=%0d label_reads=%0d label_writes=%0d cycles=%0d",queries,native_reads,checkpoints,host_blocks,g_reads,t_reads,p_reads,p_writes,cycles);$finish;
 end
