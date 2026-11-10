 integer cases=0,cycles=0,i,j;
 wire[494:0]bundle={rsp_status,rsp_op,rsp_query,rsp_price,rsp_cookie,rsp_node,rsp_y,rsp_slr,rsp_next,rsp_prev_column,rsp_label_prev,rsp_north,rsp_prev_read,rsp_prev_present,rsp_attrs};
 reg[494:0]held;
 always @(posedge clk)begin cycles<=cycles+1;if(cycles>100000)$fatal(1,"watchdog");end
 task reset_case;
 begin
  @(negedge clk);rst=1;req_valid=0;rsp_ready=0;g_rsp_valid=0;t_rsp_valid=0;p_io_rsp_valid=0;
  abort=0;g_fault=0;t_fault=0;p_fault=0;enable=1;active=1;active_query=1;active_price=3;
  nodes=64;table_rows=128;table_columns=64;g_req_ready=0;t_req_ready=0;p_io_ready=0;
  g_rsp_status=0;t_rsp_status=0;p_io_status=0;p_io_payload=0;p_io_present=0;
  repeat(2)@(negedge clk);rst=0;@(negedge clk);if(fault||!req_ready)$fatal(1,"reset recovery");
 end endtask
 task start(input integer op);
 begin
  @(negedge clk);req_valid=1;req_op=op;req_query=1;req_price=3;req_cookie=42;req_node=1;
  wait(req_ready);@(posedge clk);@(negedge clk);req_valid=0;
 end endtask
 task graph_reply(input integer typ,by,ey,ex,corrupt);
 begin
  wait(g_req_valid);@(negedge clk);g_req_ready=1;
  g_rsp_cookie=g_req_cookie;g_rsp_node=g_req_node;g_rsp_parent=g_req_node;g_rsp_index=0;g_rsp_start=0;g_rsp_count=0;
  g_rsp_attrs=0;g_rsp_attrs[71:64]=typ;g_rsp_attrs[111:96]=by;g_rsp_attrs[127:112]=ex;g_rsp_attrs[143:128]=ey;
  case(corrupt)1:g_rsp_cookie=g_req_cookie+1;2:g_rsp_node=g_req_node+1;3:g_rsp_parent=g_req_node+1;4:g_rsp_index=1;5:g_rsp_status=1;endcase
  @(negedge clk);g_req_ready=0;g_rsp_valid=1;wait(g_rsp_ready);@(posedge clk);@(negedge clk);g_rsp_valid=0;
 end endtask
 task prev_reply(input[31:0]v,input present,input integer status);
 begin
  wait(p_io_valid);@(negedge clk);p_io_ready=1;
  @(negedge clk);p_io_ready=0;p_io_payload=0;p_io_payload[95:64]=v;p_io_present=present;p_io_status=status;p_io_rsp_valid=1;
  wait(p_io_rsp_ready);@(posedge clk);@(negedge clk);p_io_rsp_valid=0;
 end endtask
 task table_reply(input integer corrupt);
 begin
  wait(t_req_valid);@(negedge clk);t_req_ready=1;t_rsp_op=t_req_op;t_rsp_index=t_req_index;t_rsp_cookie=t_req_cookie;t_rsp_a=2;t_rsp_b=1;
  case(corrupt)1:t_rsp_cookie=t_req_cookie+1;2:t_rsp_op=~t_req_op;3:t_rsp_index=t_req_index+1;4:t_rsp_status=1;endcase
  @(negedge clk);t_req_ready=0;t_rsp_valid=1;wait(t_rsp_ready);@(posedge clk);@(negedge clk);t_rsp_valid=0;
 end endtask
 task retire(input integer status,input expect_fault);
 begin
  wait(rsp_valid);@(negedge clk);if(rsp_status!==status[3:0]||fault!==expect_fault)$fatal(1,"case=%0d status=%0d expected=%0d fault=%b",cases,rsp_status,status,fault);
  held=bundle;repeat(5)begin @(negedge clk);if(!rsp_valid||bundle!==held||req_ready)$fatal(1,"unstable response");end
  rsp_ready=1;@(negedge clk);rsp_ready=0;repeat(3)@(negedge clk);
  if(expect_fault&&!fault||expect_fault&&req_ready)$fatal(1,"fault not latched");cases=cases+1;
 end endtask
 initial begin
  // Echo and status errors are detected at the service boundary.
  for(i=1;i<=5;i=i+1)begin reset_case;start(0);graph_reply(12,10,70,1,i);retire(i==5?3:4,1);end
  for(i=1;i<=4;i=i+1)begin reset_case;start(1);graph_reply(12,10,70,1,0);table_reply(i);retire(i==4?3:4,1);end
  reset_case;start(0);graph_reply(5,10,70,1,0);prev_reply(64,1,0);retire(7,1);
  reset_case;start(0);graph_reply(5,10,70,1,0);prev_reply(5,0,0);retire(3,1);
  reset_case;start(0);graph_reply(5,10,70,1,0);prev_reply(0,0,1);retire(3,1);
  reset_case;start(1);graph_reply(12,10,-1,1,0);retire(8,1);
  reset_case;start(2);graph_reply(12,10,70,64,0);retire(8,1);
  // Actual reduced token exhaustion: 7 issued tokens, eighth is refused.
  reset_case;for(i=0;i<7;i=i+1)begin start(3);graph_reply(12,10,70,1,0);retire(0,0);end
  start(3);retire(6,1);
  reset_case;start(3);retire(5,1); // timeout while downstream ready remains low
  // Unowned responses and service fault lines while idle are sticky.
  for(i=0;i<6;i=i+1)begin
   reset_case;case(i)0:g_rsp_valid=1;1:t_rsp_valid=1;2:p_io_rsp_valid=1;3:g_fault=1;4:t_fault=1;5:p_fault=1;endcase
   @(negedge clk);if(!fault||req_ready||rsp_valid)$fatal(1,"idle fault");g_rsp_valid=0;t_rsp_valid=0;p_io_rsp_valid=0;g_fault=0;t_fault=0;p_fault=0;
   repeat(3)@(negedge clk);if(!fault)$fatal(1,"idle latch");cases=cases+1;
  end
  // Abort in graph/label/table waits, including an exposed stalled response.
  for(i=0;i<4;i=i+1)begin
   reset_case;start(i==2?1:0);
   if(i==1)graph_reply(5,10,70,1,0);
   if(i==2)graph_reply(12,10,70,1,0);
   if(i==3)begin graph_reply(12,10,70,1,0);wait(rsp_valid);held=bundle;end
   @(negedge clk);abort=1;@(negedge clk);abort=0;
   if(i==3&&bundle!==held)$fatal(1,"late abort mutated response");retire(i==3?0:5,1);
  end
  for(i=0;i<3;i=i+1)for(j=0;j<2;j=j+1)begin
   reset_case;start(3);if(j)begin graph_reply(12,10,70,1,0);wait(rsp_valid);held=bundle;end
   @(negedge clk);case(i)0:active=0;1:active_query=2;2:active_price=4;endcase
   @(negedge clk);if(j&&bundle!==held)$fatal(1,"late owner drift mutated response");retire(j?0:5,1);
  end
  // Predecessor is static: matching SLL predecessor's endY is never recursed.
  reset_case;start(1);graph_reply(5,10,70,1,0);prev_reply(5,1,0);graph_reply(5,20,70,5,0);
  if(t_req_index!=10)$fatal(1,"predecessor recursion");table_reply(0);if(rsp_y!=10||rsp_slr!=2||!rsp_north)$fatal(1,"SLR resolve");retire(0,0);
  $display("CONTROLLER_BOUNDARIES_PASS cases=%0d cycles=%0d",cases,cycles);$finish;
 end
