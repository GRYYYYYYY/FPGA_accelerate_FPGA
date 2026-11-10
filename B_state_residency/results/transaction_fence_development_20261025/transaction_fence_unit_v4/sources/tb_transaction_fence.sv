`timescale 1ns/1ps
module tb_transaction_fence;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,work_permit=1,normal_fault=0,backend_drained=1,backend_idle=1,route_block=0;
 reg[2:0]s_valid=0,s_rsp_ready=0,cb_valid=0,cb_rsp_ready=0;wire[2:0]s_ready,s_rsp_valid,cb_ready,cb_rsp_valid,d_valid,d_rsp_ready,callback_pending;
 reg[23:0]s_payload=0,cb_payload=0;wire[23:0]s_rsp_payload,cb_rsp_payload,d_payload;reg[2:0]d_ready=0,d_rsp_valid=0;reg[23:0]d_rsp_payload=0;
 reg route_valid=0,route_rsp_ready=0,backend_route_ready=0,backend_route_rsp_valid=0,route_error=0;
 reg[191:0]route_payload=0;wire route_ready,route_rsp_valid,backend_route_valid,backend_route_rsp_ready;wire[191:0]backend_route_payload;
 reg recover_valid=0,recover_rsp_ready=0,backend_recover_ready=0,backend_recover_rsp_valid=0,recover_error=0;
 wire recover_ready,backend_recover_valid,recover_rsp_valid,backend_recover_rsp_ready,normal_retired,recovery_owned,fault;wire[3:0]phase;
 transaction_fence #(.LANES(3),.REQ_BITS(8),.RSP_BITS(8),.ADMIN_FIRST(2),.CALLBACK_MASK(3'b011),.DEPENDENT_MASK(3'b010),.PARENT_LANE(0),.HOST_FLAG_LANE(-1))dut(.*);
 integer ticks=0,mode=0,fd,checks=0;integer delays[0:2],seen[0:2];reg[2:0]hold_ready=0,held=0;reg[23:0]hold_payload;string path;
 always @(posedge clk)begin
  ticks<=ticks+1;if(ticks>10000)$fatal(1,"watchdog mode=%0d phase=%0d",mode,phase);
  if(rst)begin d_ready<=0;d_rsp_valid<=0;held<=0;for(integer x=0;x<3;x=x+1)begin delays[x]<=0;seen[x]<=0;end end
  else begin
   for(integer x=0;x<3;x=x+1)begin
    if(held[x]&&(!d_valid[x]||d_payload[x*8+:8]!==hold_payload[x*8+:8]))$fatal(1,"backend request withdrawn/changed");
    d_ready[x]<=ticks%(x+2)==0&&!hold_ready[x];
    if(d_valid[x]&&d_ready[x])begin
     if(delays[x]||d_rsp_valid[x])$fatal(1,"lane overlap");delays[x]<=3+x;seen[x]<=seen[x]+1;d_rsp_payload[x*8+:8]<=d_payload[x*8+:8]^8'h5a;
     $fdisplay(fd,"A %0d %0d %0d %0d %02h",mode,ticks,phase,x,d_payload[x*8+:8]);
    end
    if(delays[x]>0)begin delays[x]<=delays[x]-1;if(delays[x]==1)d_rsp_valid[x]<=1;end
    if(d_rsp_valid[x]&&d_rsp_ready[x])begin d_rsp_valid[x]<=0;$fdisplay(fd,"B %0d %0d %0d %0d",mode,ticks,phase,x);end
   end
   held<=d_valid&~d_ready;hold_payload<=d_payload;
   if(recovery_owned&&(s_ready||route_ready))$fatal(1,"ingress during recovery");
   if(backend_recover_valid&&backend_recover_ready)$fdisplay(fd,"K %0d %0d",mode,ticks);
  end
 end
 task init(input integer m);begin
  @(negedge clk);rst=1;mode=m;work_permit=1;normal_fault=0;backend_drained=1;backend_idle=1;route_block=0;hold_ready=0;
  s_valid=0;s_rsp_ready=0;cb_valid=0;cb_rsp_ready=0;route_valid=0;route_rsp_ready=0;backend_route_ready=0;backend_route_rsp_valid=0;route_error=0;
  recover_valid=0;recover_rsp_ready=0;backend_recover_ready=0;backend_recover_rsp_valid=0;recover_error=0;
  repeat(3)@(negedge clk);rst=0;
 end endtask
 task normal_send(input integer lane,value);begin
  @(negedge clk);s_valid[lane]=1;s_payload[lane*8+:8]=value;do @(posedge clk);while(!s_ready[lane]);@(negedge clk);s_valid[lane]=0;s_payload[lane*8+:8]=~value;
 end endtask
 task normal_reply(input integer lane,value);begin
  wait(s_rsp_valid[lane]);@(negedge clk);
  if(s_rsp_payload[lane*8+:8]!=(value^8'h5a))$fatal(1,"normal payload not captured");
  repeat(4)begin @(negedge clk);if(!s_rsp_valid[lane]||s_ready||cb_rsp_valid)$fatal(1,"normal held response ownership");end
  s_rsp_ready[lane]=1;@(negedge clk);s_rsp_ready[lane]=0;
 end endtask
 task acquire;begin
  @(negedge clk);recover_valid=1;backend_recover_ready=1;do @(posedge clk);while(!recover_ready);@(negedge clk);recover_valid=0;
 end endtask
 task automatic cb_send(input integer lane,value);begin
  @(negedge clk);cb_valid[lane]=1;cb_payload[lane*8+:8]=value;do @(posedge clk);while(!cb_ready[lane]);@(negedge clk);cb_valid[lane]=0;
 end endtask
 task complete_recovery(input integer bad);begin
  @(negedge clk);backend_recover_rsp_valid=1;recover_error=bad;
  wait(recover_rsp_valid);repeat(5)begin @(negedge clk);if(!recover_rsp_valid||s_ready||route_ready||callback_pending)$fatal(1,"held recovery completion");end
  recover_rsp_ready=1;@(negedge clk);recover_rsp_ready=0;backend_recover_rsp_valid=0;
  wait(phase==(bad||normal_fault||fault?6:0));
 end endtask
 task check_done;begin
  for(integer x=0;x<3;x=x+1)if(delays[x]||d_rsp_valid[x])$fatal(1,"unretired backend");
  $fdisplay(fd,"R %0d %0d %0d %0d %0d %0d",mode,phase,fault,seen[0],seen[1],seen[2]);checks=checks+1;
 end endtask
 initial begin
  if(!$value$plusargs("events=%s",path))$fatal(1,"events path");fd=$fopen(path,"w");
  // Normal work snapshots payload before backend exposure; recovery waits reply and drain.
  init(0);hold_ready[0]=1;normal_send(0,8'h31);recover_valid=1;work_permit=0;
  repeat(8)begin @(negedge clk);if(!d_valid[0]||backend_recover_valid||normal_retired)$fatal(1,"pending request lost on quiesce");end hold_ready[0]=0;
  backend_drained=0;normal_reply(0,8'h31);repeat(5)begin @(negedge clk);if(backend_recover_valid)$fatal(1,"recovery before physical drain");end backend_drained=1;acquire;complete_recovery(0);check_done;
  // Parallel callbacks and premature coordinator completion must drain individually.
  init(1);acquire;fork cb_send(0,8'h42);cb_send(1,8'h53);join
  backend_recover_rsp_valid=1;backend_drained=0;wait(cb_rsp_valid==3);repeat(5)begin @(negedge clk);if(recover_rsp_valid||s_rsp_valid)$fatal(1,"callback reply leaked");end
  cb_rsp_ready=3;wait(callback_pending==0);@(negedge clk);cb_rsp_ready=0;repeat(5)begin @(negedge clk);if(recover_rsp_valid)$fatal(1,"callback physical drain skipped");end backend_drained=1;complete_recovery(0);check_done;
  // Buffered route remains stable while backend stalls, even after recovery intent.
  init(2);route_payload=192'h123;route_valid=1;do @(posedge clk);while(!route_ready);@(negedge clk);route_valid=0;route_payload=192'h999;recover_valid=1;
  repeat(8)begin @(negedge clk);if(!backend_route_valid||backend_route_payload!=192'h123||backend_recover_valid)$fatal(1,"route lost ownership before backend accept");end
  backend_route_ready=1;@(negedge clk);backend_route_ready=0;backend_route_rsp_valid=1;route_error=1;route_block=1;
  wait(route_rsp_valid);repeat(4)@(negedge clk);if(recover_ready)$fatal(1,"route reply not retired");route_rsp_ready=1;@(negedge clk);route_rsp_ready=0;backend_route_rsp_valid=0;acquire;route_block=0;complete_recovery(0);check_done;
  // A failed recovery keeps normal ingress blocked.
  init(3);acquire;complete_recovery(1);s_valid=1;route_valid=1;repeat(5)begin @(negedge clk);if(s_ready||route_ready)$fatal(1,"failed recovery reopened normal work");end check_done;
  // Admin can initialize before work permission; ordinary work waits.
  init(4);work_permit=0;s_valid=1;s_payload[7:0]=8'h64;normal_send(2,8'h75);normal_reply(2,8'h75);wait(phase==0);repeat(5)begin @(negedge clk);if(s_ready[0])$fatal(1,"unconfigured normal ingress");end work_permit=1;
  do @(posedge clk);while(!s_ready[0]);@(negedge clk);s_valid=0;normal_reply(0,8'h64);wait(phase==0);check_done;
  // Recovery waits logical idle even if physical counters are empty.
  init(5);backend_idle=0;recover_valid=1;repeat(8)begin @(negedge clk);if(backend_recover_valid||recover_ready)$fatal(1,"recovery before logical idle");end backend_idle=1;acquire;complete_recovery(0);check_done;
  // Illegal callback lane cannot reach a normal/admin backend.
  init(6);acquire;cb_valid=4;repeat(3)@(negedge clk);if(!fault||d_valid||cb_ready[2])$fatal(1,"illegal callback lane accepted");cb_valid=0;complete_recovery(1);check_done;
  // Essential continuations may retire a parent after quiesce, including parent reply backpressure.
  init(7);normal_send(0,8'h86);wait(s_rsp_valid[0]);recover_valid=1;normal_send(1,8'h97);normal_reply(1,8'h97);normal_reply(0,8'h86);acquire;complete_recovery(0);check_done;
  // Front parent reply can retire first; native parent ACK waits its accepted continuation.
  init(8);normal_send(0,8'ha8);wait(s_rsp_valid[0]);normal_send(1,8'hb9);@(negedge clk);s_rsp_ready[0]=1;@(negedge clk);s_rsp_ready[0]=0;
  repeat(4)begin @(negedge clk);if(s_rsp_valid[0]||d_rsp_ready[0]||normal_retired)$fatal(1,"parent ACK lost a continuation");end
  normal_reply(1,8'hb9);wait(phase==0);check_done;
  $fflush(fd);$fclose(fd);$display("TRANSACTION_FENCE_PASS checks=%0d",checks);$finish;
 end
endmodule
