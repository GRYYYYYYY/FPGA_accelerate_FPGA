 integer cycles=0,cases=0,recoveries=0,i,j,owner_error=-1;reg auto_owner=0,owner_pending=0;integer owner_delay=0;
 reg[329:0]held;wire[329:0]bundle={rsp_status,rsp_cookie,rsp_parent,rsp_child,rsp_sink,rsp_net,rsp_bits,rsp_action,rsp_steps,rsp_services,rsp_query,rsp_price};
 always @(posedge clk)begin cycles<=cycles+1;if(cycles>2000000)$fatal(1,"watchdog");end
 always @(posedge clk)begin
  if(rst)begin owner_pending<=0;o_rsp_valid<=0;o_req_ready<=0;end
  else if(auto_owner)begin
   o_req_ready<=!owner_pending&&!o_rsp_valid;
   if(o_req_valid&&o_req_ready)begin
    owner_pending<=1;owner_delay<=2;o_rsp_kind<=o_req_kind;o_rsp_phase<=o_req_phase;o_rsp_node<=o_req_node;o_rsp_net<=o_req_net;o_rsp_cookie<=o_req_cookie;o_rsp_query<=o_req_query;o_rsp_price<=o_req_price;o_rsp_value<=0;o_rsp_status<=0;
    case(owner_error)0:o_rsp_cookie<=o_req_cookie+1;1:o_rsp_kind<=6;2:o_rsp_phase<=o_req_phase+1;3:o_rsp_node<=o_req_node+1;4:o_rsp_net<=1;5:o_rsp_query<=2;6:o_rsp_price<=4;7:o_rsp_status<=1;endcase
   end
   if(owner_pending&&!o_rsp_valid)begin if(owner_delay)owner_delay<=owner_delay-1;else o_rsp_valid<=1;end
   if(o_rsp_valid&&o_rsp_ready)begin owner_pending<=0;o_rsp_valid<=0;end
  end
 end
 task reset_case;
 begin
  @(negedge clk);rst=1;abort=0;inject_graph=0;inject_table=0;inject_pager=0;inject_pager_b=0;auto_owner=0;owner_error=-1;o_fault=0;
  req_valid=0;rsp_ready=0;host_ctrl_valid=0;host_io_valid=0;host_ctrl_rsp_ready=0;host_io_rsp_ready=0;g_cfg_valid=0;t_cfg_valid=0;g_cfg_rsp_ready=0;t_cfg_rsp_ready=0;
  repeat(5)@(negedge clk);rst=0;
  @(negedge clk);g_cfg_valid=1;t_cfg_valid=1;wait(g_cfg_ready&&t_cfg_ready);@(posedge clk);@(negedge clk);g_cfg_valid=0;t_cfg_valid=0;
  wait(g_cfg_rsp_valid&&t_cfg_rsp_valid);@(negedge clk);if(g_cfg_status||t_cfg_status)$fatal(1,"config");g_cfg_rsp_ready=1;t_cfg_rsp_ready=1;@(negedge clk);g_cfg_rsp_ready=0;t_cfg_rsp_ready=0;
  host_ctrl_op=0;host_ctrl_query=1;host_ctrl_price=3;host_ctrl_valid=1;wait(host_ctrl_ready);@(posedge clk);@(negedge clk);host_ctrl_valid=0;
  wait(host_ctrl_rsp_valid);@(negedge clk);if(host_ctrl_status||fault)$fatal(1,"open");host_ctrl_rsp_ready=1;@(negedge clk);host_ctrl_rsp_ready=0;
 end endtask
 task write_label(input integer n,f,input[31:0]v);
 begin
  @(negedge clk);host_io_valid=1;host_io_write=1;host_io_node=n;host_io_field=f;host_io_value=v;wait(host_io_ready);@(posedge clk);@(negedge clk);host_io_valid=0;
  wait(host_io_rsp_valid);@(negedge clk);if(host_io_status||fault)$fatal(1,"label setup");host_io_rsp_ready=1;@(negedge clk);host_io_rsp_ready=0;
 end endtask
 task start(input integer node,flags);
 begin
  @(negedge clk);req_config=0;req_config[31:0]=17;req_config[63:32]=flags;req_config[95:64]=node; // synthetic child ids0..17 match types
  req_config[127:96]=0;req_config[159:128]=0;req_config[191:160]=node%3;req_config[223:192]=node%5;req_config[255:224]=1;
  req_config[287:256]=0;req_config[319:288]=29;req_config[351:320]=-100;req_config[383:352]=100;req_config[415:384]=-100;req_config[447:416]=100;
  req_valid=1;req_cookie=42;req_parent=18;req_child=node;req_sink=36;req_net=0;req_query=1;req_price=3;
  wait(req_ready);@(posedge clk);@(negedge clk);req_valid=0;
 end endtask
 task retire(input integer status,input bad);
 begin
  wait(rsp_valid);@(negedge clk);if(rsp_status!=status||fault!==bad)$fatal(1,"case=%0d status=%0d/%0d fault=%b af=%b df=%b cf=%b",cases,rsp_status,status,fault,dut.a_fault,dut.d_fault,dut.c_fault);
  held=bundle;repeat(5)begin @(negedge clk);if(!rsp_valid||held!==bundle)$fatal(1,"unstable");end
  rsp_ready=1;@(negedge clk);rsp_ready=0;repeat(3)@(negedge clk);if(bad&&(!fault||req_ready||host_ctrl_ready||host_io_ready))$fatal(1,"fault not stopped");
 end endtask
 task recovery;
 begin reset_case;start(12,0);wait(rsp_valid);@(negedge clk);if(rsp_action!=1||rsp_bits||rsp_services!=2)$fatal(1,"recovery value case=%0d status=%0d action=%0d bits=%0d services=%0d fault=%b af=%b df=%b cf=%b ds=%0d",cases,rsp_status,rsp_action,rsp_bits,rsp_services,fault,dut.a_fault,dut.d_fault,dut.c_fault,dut.dispatch.rsp_status);retire(0,0);recoveries=recoveries+1;end endtask
 initial begin
  g_cfg_offsets_base=64'h1fffff000;g_cfg_edges_base=64'h10fffff000;g_cfg_attrs_base=64'h20fffff000;g_cfg_nodes=64;g_cfg_edges=0;
  t_cfg_rows_base=64'h31fffff000;t_cfg_columns_base=64'h41fffff000;t_cfg_rows=128;t_cfg_columns=64;graph_size0=320;graph_size1=0;graph_size2=2048;table_size0=1024;table_size1=512;
  for(i=0;i<6;i=i+1)begin
   reset_case;
   case(i)
    0:begin inject_graph=1;start(0,4);end
    1:begin inject_table=1;auto_owner=1;start(6,8);end
    2:begin write_label(5,2,64);start(5,4);end
    3:begin write_label(1,4,1);write_label(9,3,33);inject_pager=1;start(1,0);end
    4:begin write_label(9,3,33);inject_pager_b=1;start(1,0);end
    5:begin start(6,8);end // no owner readiness: dispatcher timeout256
   endcase
   retire(5,1);cases=cases+1;recovery;
  end
  for(i=0;i<8;i=i+1)begin reset_case;auto_owner=1;owner_error=i;start(6,8);retire(5,1);cases=cases+1;recovery;end
  // Abort at kernel work, label wait, coordinate wait, and final response.
  for(i=0;i<4;i=i+1)begin
   reset_case;start(0,4);
   case(i)0:repeat(3)@(negedge clk);1:wait(dut.dispatch.state==2);2:wait(dut.dispatch.state==4);3:begin wait(rsp_valid);@(negedge clk);held=bundle;end endcase
   @(negedge clk);abort=1;@(negedge clk);abort=0;if(i==3&&held!==bundle)$fatal(1,"late abort mutated result");retire(i==3?0:5,1);cases=cases+1;recovery;
  end
  reset_case;start(12,0);wait(rsp_valid);@(negedge clk);held=bundle;o_fault=1;@(negedge clk);if(bundle!==held)$fatal(1,"late owner fault");retire(0,1);cases=cases+1;recovery;
  $display("ACCESS_FABRIC_BOUNDARIES_PASS faults=%0d recoveries=%0d cycles=%0d",cases,recoveries,cycles);$finish;
 end
