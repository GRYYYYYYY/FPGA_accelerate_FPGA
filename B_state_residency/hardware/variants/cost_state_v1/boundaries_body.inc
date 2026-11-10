 integer fd,rc,k,cycles=0,checks=0,reloads=0,errors=0;string initial_path;
 reg[7:0]initial_bytes[0:4095],four[0:3];reg[80:0]held_ar,held_aw;reg[575:0]held_w;reg[237:0]held_response;
 always @(posedge clk)begin cycles<=cycles+1;if(cycles>100000)$fatal(1,"boundary watchdog state=%d owned=%b rsp=%b",dut.state,dut.owned,rsp_valid);end
 task tick;begin @(posedge clk);#1;end endtask
 task ck(input bit ok,input string message);begin if(!ok)$fatal(1,"%s state=%d",message,dut.state);checks=checks+1;end endtask
 task reset_reload(input[31:0]version);
  begin
   @(negedge clk);rst=1;abort=0;query_active=0;decision_lock=0;active_query=0;active_price=0;req_valid=0;rsp_ready=0;cfg_valid=0;cfg_rsp_ready=0;hold_ar=0;hold_aw=0;hold_w=0;inject_r=0;inject_b=0;
   cfg_history=64'h1fffff000;cfg_prices=cfg_history+1024;cfg_nets=cfg_history+2048;cfg_nodes=32;cfg_net_count=16;cfg_version=version;cfg_design_id=reloads+1;
   repeat(2)tick();rc=$fseek(memory.fd[0],0,0);if(rc)$fatal(1,"reload seek");for(k=0;k<4096;k=k+1)$fwrite(memory.fd[0],"%c",initial_bytes[k]);$fflush(memory.fd[0]);reloads=reloads+1;$fdisplay(memory.logfd,"N %0d",reloads);
   @(negedge clk);rst=0;cfg_valid=1;wait(cfg_ready);tick();@(negedge clk);cfg_valid=0;wait(cfg_rsp_valid);ck(cfg_status==0&&configured,"config");cfg_rsp_ready=1;tick();@(negedge clk);cfg_rsp_ready=0;
  end
 endtask
 task send(input bit host,input[2:0]op,input[31:0]index,value);
  begin
   wait(!busy);@(negedge clk);req_host=host;req_op=op;req_cookie=32'h1234;req_index=index;req_value=value;req_version=published_version;req_query=active_query;req_price=active_price;req_valid=1;
   wait(req_ready);tick();@(negedge clk);req_valid=0;req_op=7;req_index=0;req_value=32'hbad;req_version=0;
  end
 endtask
 task response(input[3:0]status);
  begin
   wait(rsp_valid);@(negedge clk);ck(rsp_status==status&&rsp_cookie==32'h1234,"response status/cookie");held_response={rsp_status,rsp_cookie,rsp_index,rsp_version,rsp_op,rsp_host,rsp_query,rsp_price,rsp_data};
   repeat(3)begin tick();ck(rsp_valid&&{rsp_status,rsp_cookie,rsp_index,rsp_version,rsp_op,rsp_host,rsp_query,rsp_price,rsp_data}===held_response,"response stable");end
  end
 endtask
 task retire;
  begin @(negedge clk);rsp_ready=1;tick();@(negedge clk);rsp_ready=0;wait(!busy);end
 endtask
 task begin_edit;
  begin send(1,4,0,0);response(0);retire();ck(editing&&!ready_for_query,"edit fence");end
 endtask
 task query_on;
  begin @(negedge clk);query_active=1;decision_lock=1;active_query=2;active_price=published_version[3:0];end
 endtask
 task stopped_check;
  begin ck(fault&&!req_ready&&!ready_for_query&&!rsp_valid,"stopped after drain");errors=errors+1;end
 endtask
 initial begin
  rst=1;if(!$value$plusargs("initial=%s",initial_path))$fatal(1,"initial path");fd=$fopen(initial_path,"rb");if(!fd)$fatal(1,"initial open");rc=$fread(initial_bytes,fd);if(rc!=4096)$fatal(1,"initial bytes");$fclose(fd);
  // Actual R error and stable already-exposed error under late abort.
  reset_reload(1);query_on();inject_r=1;send(0,0,1,0);response(4);abort=1;tick();ck(rsp_status==4,"late abort does not replace error");retire();abort=0;stopped_check();
  // An error B has already changed backing bytes: no rollback.
  reset_reload(1);begin_edit();inject_b=1;send(1,1,17,32'h41000000);response(4);retire();rc=$fseek(memory.fd[0],68,0);rc=$fread(four,memory.fd[0]);ck(rc==4&&{four[3],four[2],four[1],four[0]}==32'h41000000,"failed B physically changed history");stopped_check();
  // AR is retained through abort; error can retire before physical drain.
  reset_reload(1);query_on();hold_ar=1;send(0,0,17,0);wait(m_arvalid);@(negedge clk);held_ar={m_araddr,m_arlen,m_arsize,m_arburst,m_arid};abort=1;
  repeat(4)begin tick();ck(m_arvalid&&{m_araddr,m_arlen,m_arsize,m_arburst,m_arid}===held_ar&&!m_arready,"AR stable on abort");end
  response(5);@(negedge clk);rsp_ready=1;tick();@(negedge clk);rsp_ready=0;ck(busy&&m_arvalid,"busy until late AR drain");hold_ar=0;abort=0;wait(!busy);stopped_check();
  // AW and W each retain their payload when the other channel has progressed.
  reset_reload(1);begin_edit();hold_aw=1;send(1,1,2,32'h40400000);wait(m_awvalid);@(negedge clk);held_aw={m_awaddr,m_awlen,m_awsize,m_awburst,m_awid};abort=1;
  repeat(4)begin tick();ck(m_awvalid&&{m_awaddr,m_awlen,m_awsize,m_awburst,m_awid}===held_aw&&!m_awready,"AW stable on abort");end
  response(5);@(negedge clk);abort=0;hold_aw=0;retire();stopped_check();
  reset_reload(1);begin_edit();hold_w=1;send(1,1,31,32'h40800000);wait(m_wvalid);@(negedge clk);held_w={m_wstrb,m_wdata};abort=1;
  repeat(4)begin tick();ck(m_wvalid&&{m_wstrb,m_wdata}===held_w&&!m_wready,"W stable on abort");end
  response(5);@(negedge clk);abort=0;hold_w=0;retire();stopped_check();
  // Timeout also preserves pending AR and requires drain before reuse/reset.
  reset_reload(1);query_on();hold_ar=1;send(0,2,255,0);response(5);ck(m_arvalid&&busy,"timeout pending AR");@(negedge clk);hold_ar=0;retire();stopped_check();
  // Query context cannot change while a reader owns a request.
  reset_reload(1);query_on();hold_ar=1;send(0,6,15,0);wait(m_arvalid);@(negedge clk);active_query=1;response(5);hold_ar=0;retire();stopped_check();
  // A caller attempting to enter a query during editing violates the fence.
  reset_reload(1);begin_edit();query_on();tick();ck(fault&&!rsp_valid&&!ready_for_query,"query/edit fence violation");errors=errors+1;
  // Never wrap the full published generation.
  reset_reload(32'hffffffff);begin_edit();send(1,5,0,0);response(6);retire();ck(published_version==32'hffffffff&&editing,"version did not wrap");stopped_check();
  // Explicit final reload recovers, and persistent storage matches imported state.
  reset_reload(1);query_on();send(0,0,17,0);response(0);ck(rsp_data==128'h40040000,"reload recovered imported history");retire();ck(!fault&&ready_for_query,"normal recovery");
  $display("COST_STATE_BOUNDARY_PASS checks=%0d errors=%0d reloads=%0d reads=%0d writes=%0d bs=%0d cycles=%0d",checks,errors,reloads,reads,writes,bs,cycles);$finish;
 end
