 integer scenario=0,cycles=0,k,old_reads;reg expected_fault=0;
 reg[164:0]held_result;reg[351:0]held_child;
 always @(posedge clk)begin
  cycles<=cycles+1;if(cycles>1000000)$fatal(1,"boundary watchdog scenario=%0d state=%0d",scenario,dut.controller.state);
  if(!rst)begin
   if(fault&&!expected_fault)$fatal(1,"unplanned fault scenario=%0d state=%0d status=%0d detail=%0d",scenario,dut.controller.state,result_status,result_detail);
   if(busy&&(host_ctrl_ready||host_io_ready||expand_ready))$fatal(1,"admission during busy/fault");
  end
 end
 task configure;
  begin
   rst=1;repeat(5)@(negedge clk);rst=0;
   g_cfg_offsets_base=64'h1fffff000;g_cfg_edges_base=64'h10fffff000;g_cfg_attrs_base=64'h20fffff000;g_cfg_nodes=9089009;g_cfg_edges=40469536;
   d_cfg_base=64'h31fffff000;d_cfg_nodes=scenario==11?9089008:9089009;
   @(negedge clk);g_cfg_valid=1;d_cfg_valid=1;wait(g_cfg_ready&&d_cfg_ready);@(posedge clk);@(negedge clk);g_cfg_valid=0;d_cfg_valid=0;
   wait(g_cfg_rsp_valid&&d_cfg_rsp_valid);@(negedge clk);if(g_cfg_status||d_cfg_status)$fatal(1,"config");g_cfg_rsp_ready=1;d_cfg_rsp_ready=1;@(negedge clk);g_cfg_rsp_ready=0;d_cfg_rsp_ready=0;
  end
 endtask
 task open_query;
  begin
   @(negedge clk);host_ctrl_valid=1;host_ctrl_op=0;host_ctrl_query=1;host_ctrl_price=3;wait(host_ctrl_ready);@(posedge clk);@(negedge clk);host_ctrl_valid=0;
   wait(host_ctrl_rsp_valid);@(negedge clk);if(host_ctrl_status)$fatal(1,"open");host_ctrl_rsp_ready=1;@(negedge clk);host_ctrl_rsp_ready=0;
  end
 endtask
 task start(input[31:0]parent,prune,laguna);
  begin
   @(negedge clk);expand_parent=parent;expand_prune=prune;expand_has_laguna=laguna;expand_cookie=expand_cookie+1;expand_valid=1;
   wait(expand_ready);@(posedge clk);@(negedge clk);expand_valid=0;
   host_ctrl_valid=1;host_ctrl_op=2;host_io_valid=1;host_io_write=1;host_io_node=parent;host_io_field=2;host_io_value=32'hbadabcde;
  end
 endtask
 task response(input integer status,detail,failed);
  begin
   wait(result_valid);@(negedge clk);
   if(result_status!=status||result_detail!=detail||result_cookie!=expand_cookie||fault!==failed)$fatal(1,"response scenario=%0d st=%0d/%0d detail=%0d/%0d fault=%b/%0d",scenario,result_status,status,result_detail,detail,fault,failed);
   held_result={result_status,result_detail,result_cookie,result_count,result_raw_count,result_mask,result_hit};
   repeat(4)begin @(negedge clk);if(!result_valid||{result_status,result_detail,result_cookie,result_count,result_raw_count,result_mask,result_hit}!==held_result||!busy)$fatal(1,"result hold");end
   result_ready=1;@(negedge clk);result_ready=0;host_ctrl_valid=0;host_io_valid=0;
   if(failed&&!busy)$fatal(1,"fault lost lock");
  end
 endtask
 initial begin
  if(!$value$plusargs("scenario=%d",scenario))$fatal(1,"scenario");expected_fault=scenario!=0;
  configure();
  if(scenario==11)begin
   repeat(5)@(negedge clk);host_ctrl_valid=1;host_io_valid=1;
   repeat(5)begin @(negedge clk);if(!fault||!busy||result_valid||host_ctrl_ready||host_io_ready||expand_ready||g_reads||d_reads)$fatal(1,"mismatched config");end
  end else begin
   open_query();
   case(scenario)
    0:begin
     start(0,2,0);response(1,0,0);start(0,0,2);response(1,0,0);start(9089009,0,0);response(1,0,0);
     if(g_reads||d_reads)$fatal(1,"invalid request AXI");start(0,0,0);response(0,0,0);
    end
    1:begin inject_graph=1;start(0,0,0);response(4,0,1);if(dut.d_claim_active||d_writes)$fatal(1,"META error claimed state");end
    2:begin inject_design=1;start(0,0,0);response(4,0,1);if(dut.d_claim_active||d_writes)$fatal(1,"CLAIM read error wrote");end
    3:begin start(9,0,0);wait(dut.g_req_valid&&dut.g_req_op==1);inject_graph=1;response(4,0,1);if(!dut.d_claim_active)$fatal(1,"NEXT error lost claim");end
    4:begin start(9,0,0);wait(dut.d_req_valid&&dut.d_req_op==2);inject_design_b=1;response(4,0,1);if(!dut.d_claim_active||d_writes!=1)$fatal(1,"CREATE error lost claim");end
    5:begin start(0,0,0);wait(dut.d_req_valid&&dut.d_req_op==5);inject_design_b=1;response(4,0,1);if(!dut.d_claim_active||d_writes!=1)$fatal(1,"PUBLISH error lost claim");end
    6:begin start(9,0,0);wait(dut.p_edge_valid);force dut.p_fault=1;response(4,0,1);if(!dut.d_claim_active)$fatal(1,"pager fault claim");release dut.p_fault;end
    7:begin start(0,0,0);wait(dut.g_rsp_valid);force dut.g_rsp_cookie=0;response(5,1,1);release dut.g_rsp_cookie;end
    8:begin start(0,0,0);wait(dut.d_rsp_valid);force dut.d_rsp_cookie=0;response(5,5,1);release dut.d_rsp_cookie;end
    9:begin start(9,0,0);wait(dut.p_result_valid);force dut.p_result_cookie=0;response(5,24,1);release dut.p_result_cookie;end
    10:begin
     start(0,0,0);wait(result_valid);@(negedge clk);held_result={result_status,result_detail,result_cookie,result_count,result_raw_count,result_mask,result_hit};force dut.g_fault=1;
     repeat(4)begin @(negedge clk);if(!fault||!result_valid||{result_status,result_detail,result_cookie,result_count,result_raw_count,result_mask,result_hit}!==held_result)$fatal(1,"late final mutation");end
     response(0,0,1);release dut.g_fault;
    end
    12:begin
     start(9,0,0);wait(out_valid);@(negedge clk);held_child={out_node,out_position,out_sequence,out_attrs};force dut.g_fault=1;
     repeat(4)begin @(negedge clk);if(!fault||!out_valid||{out_node,out_position,out_sequence,out_attrs}!==held_child)$fatal(1,"late stream mutation");end
     out_ready=1;@(negedge clk);out_ready=0;response(4,0,1);release dut.g_fault;
    end
    13:begin
     start(9,0,0);response(3,1,1);
     if(dut.controller.token!=15||!dut.d_claim_active||dut.d_claim_mask!=3)$fatal(1,"token exhaustion boundary token=%d mask=%h",dut.controller.token,dut.d_claim_mask);
    end
    14:begin
     for(k=0;k<7;k=k+1)begin start(0,0,0);response(0,0,0);end
     old_reads=g_reads;start(0,0,0);response(3,0,1);
     if(dut.controller.last_owner!=7||g_reads!=old_reads||dut.d_claim_active)$fatal(1,"owner exhaustion boundary");
    end
    default:$fatal(1,"unknown scenario");
   endcase
  end
  repeat(8)@(negedge clk);
  if(scenario!=0&&(!fault||!busy||expand_ready||host_ctrl_ready||host_io_ready))$fatal(1,"fault persistence");
  $display("EXPANSION_BOUNDARY_PASS scenario=%0d fault=%0d claim=%0d token=%0d owner=%0d graph_reads=%0d design_reads=%0d design_writes=%0d cycles=%0d",scenario,fault,dut.d_claim_active,dut.controller.token,dut.controller.last_owner,g_reads,d_reads,d_writes,cycles);$finish;
 end
