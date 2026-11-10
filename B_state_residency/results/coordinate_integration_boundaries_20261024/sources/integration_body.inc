 integer cases=0,cycles=0,i;reg[494:0]held;
 wire[494:0]bundle={rsp_status,rsp_op,rsp_query,rsp_price,rsp_cookie,rsp_node,rsp_y,rsp_slr,rsp_next,rsp_prev_column,rsp_label_prev,rsp_north,rsp_prev_read,rsp_prev_present,rsp_attrs};
 always @(posedge clk)begin cycles<=cycles+1;if(cycles>2000000)$fatal(1,"integration watchdog");end
 task reset_case;
 begin
  @(negedge clk);rst=1;abort=0;inject_graph=0;inject_table=0;inject_pager=0;inject_pager_b=0;
  req_valid=0;rsp_ready=0;host_ctrl_valid=0;host_io_valid=0;host_ctrl_rsp_ready=0;host_io_rsp_ready=0;g_cfg_valid=0;t_cfg_valid=0;g_cfg_rsp_ready=0;t_cfg_rsp_ready=0;
  repeat(5)@(negedge clk);rst=0;
  @(negedge clk);g_cfg_valid=1;t_cfg_valid=1;wait(g_cfg_ready&&t_cfg_ready);@(posedge clk);@(negedge clk);g_cfg_valid=0;t_cfg_valid=0;
  wait(g_cfg_rsp_valid&&t_cfg_rsp_valid);@(negedge clk);if(g_cfg_status||t_cfg_status)$fatal(1,"config");g_cfg_rsp_ready=1;t_cfg_rsp_ready=1;@(negedge clk);g_cfg_rsp_ready=0;t_cfg_rsp_ready=0;
  host_ctrl_op=0;host_ctrl_query=1;host_ctrl_price=3;host_ctrl_valid=1;wait(host_ctrl_ready);@(posedge clk);@(negedge clk);host_ctrl_valid=0;
  wait(host_ctrl_rsp_valid);@(negedge clk);if(host_ctrl_status||fault)$fatal(1,"open");host_ctrl_rsp_ready=1;@(negedge clk);host_ctrl_rsp_ready=0;
 end endtask
 task write_prev(input integer n,input[31:0]v);
 begin
  @(negedge clk);host_io_valid=1;host_io_write=1;host_io_node=n;host_io_field=2;host_io_value=v;
  wait(host_io_ready);@(posedge clk);@(negedge clk);host_io_valid=0;
  wait(host_io_rsp_valid);@(negedge clk);if(host_io_status||fault)$fatal(1,"write_prev");host_io_rsp_ready=1;@(negedge clk);host_io_rsp_ready=0;
 end endtask
 task start(input integer op,n);
 begin
  @(negedge clk);req_valid=1;req_op=op;req_query=1;req_price=3;req_cookie=42;req_node=n;
  wait(req_ready);@(posedge clk);@(negedge clk);req_valid=0;
 end endtask
 task retire(input integer status,input bad);
 begin
  wait(rsp_valid);@(negedge clk);if(rsp_status!=status||fault!==bad)$fatal(1,"integration case=%0d status=%0d/%0d fault=%b gf=%b tf=%b pf=%b",cases,rsp_status,status,fault,dut.g_fault,dut.t_fault,dut.p_fault);
  held=bundle;repeat(5)begin @(negedge clk);if(!rsp_valid||held!==bundle)$fatal(1,"integration unstable");end
  rsp_ready=1;@(negedge clk);rsp_ready=0;repeat(3)@(negedge clk);
  if(bad&&(!fault||req_ready||host_ctrl_ready||host_io_ready))$fatal(1,"integration fault not stopped");
 end endtask
 initial begin
  g_cfg_offsets_base=64'h1fffff000;g_cfg_edges_base=64'h10fffff000;g_cfg_attrs_base=64'h20fffff000;g_cfg_nodes=64;g_cfg_edges=0;
  t_cfg_rows_base=64'h31fffff000;t_cfg_columns_base=64'h41fffff000;t_cfg_rows=128;t_cfg_columns=64;
  graph_size0=320;graph_size1=0;graph_size2=2048;table_size0=1024;table_size1=512;
  for(i=0;i<7;i=i+1)begin
   reset_case;
   case(i)
    0:begin inject_graph=1;start(0,0);retire(5,1);end
    1:begin inject_table=1;start(1,0);retire(5,1);end
    2:begin write_prev(1,64);start(0,1);retire(7,1);end
    3:begin write_prev(1,32'hffffffff);write_prev(9,32'hffffffff);inject_pager=1;start(0,1);retire(5,1);end
    4:begin write_prev(1,32'hffffffff);inject_pager_b=1;start(0,9);retire(5,1);end
    5:begin start(0,1);abort=1;@(negedge clk);abort=0;retire(5,1);end
    6:begin start(0,0);wait(rsp_valid);@(negedge clk);held=bundle;abort=1;@(negedge clk);abort=0;if(held!==bundle)$fatal(1,"integration late fault");retire(0,1);end
   endcase
   cases=cases+1;
   // Coordinated cold reset flushes all mocked fabric transactions.
   reset_case;start(0,0);wait(rsp_valid);if(rsp_y!=70)$fatal(1,"recovery coordinate");retire(0,0);
  end
  $display("INTEGRATED_BOUNDARIES_PASS faults=%0d recoveries=%0d cycles=%0d",cases,cases,cycles);$finish;
 end
