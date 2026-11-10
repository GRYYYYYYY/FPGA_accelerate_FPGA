`timescale 1ns/1ps
module tb_recovery_coordinator;
 reg retry_safe=1;wire attempt_reset;integer attempt_resets=0;
 reg clk=0;always #5 clk=~clk;
 reg cold_rst=1,abort=0,backend_drained=1,normal_retired=1;
 reg cfg_valid=0,cfg_authoritative=1,cfg_rsp_ready=0;wire cfg_ready,cfg_rsp_valid,cfg_status;
 reg[63:0]cfg_design=64'h12345678;reg[31:0]cfg_checkpoint=17,cfg_version=3;reg[1:0]cfg_query=1;reg[3:0]cfg_price=3;
 reg j_valid=0;wire j_ready,journal_full,permit_work;reg[31:0]j_node=0,j_net=0;reg[2:0]j_op=1;wire[31:0]journal_count;
 reg recover_valid=0;wire recover_ready;reg[31:0]recover_cookie=0,recover_checkpoint=17,recover_version=4;reg[63:0]recover_design=64'h12345678;reg[1:0]recover_query=2;reg[3:0]recover_price=4;
 wire target_reset,reconfigure_valid,labels_valid;reg reconfigure_done=0,labels_done=0;wire[63:0]saved_design;wire[31:0]saved_checkpoint,new_version;wire[1:0]new_query;wire[3:0]new_price;
 wire rsp_valid,busy,fault;reg rsp_ready=0;wire[3:0]rsp_status;wire[31:0]rsp_cookie,rsp_corrected;
 wire a_valid,a_rsp_ready,o_valid,o_rsp_ready;reg a_ready=0,a_rsp_valid=0,o_ready=0,o_rsp_valid=0;wire[31:0]a_node,a_net,a_cookie,a_checkpoint,o_node,o_net,o_cookie;wire[63:0]a_design;wire[2:0]o_op;
 reg[3:0]a_status=0,o_status=0;reg[31:0]a_rsp_cookie=0,a_rsp_checkpoint=0,a_refs=0,a_occupancy=0,o_rsp_cookie=0,o_count=0,o_occupancy=0;reg[63:0]a_rsp_design=0;
 recovery_coordinator #(.ENTRIES(4),.RESET_HOLD(3),.MAX_CORRECTIONS(4),.MAX_CYCLES(512))dut(.*);
 integer current_refs[0:1][0:1],authority[0:1][0:1];integer ticks=0,mode=0,aw=0,ow=0,rw=0,lw=0,ai=0,oi=0,ni,nn,after_count,after_occ,resets=0,checks=0,i,j;integer logfd;string path;
 reg held_a=0,held_o=0;reg[223:0]a_hold;reg[98:0]o_hold;
 always @(posedge clk)begin
  ticks=ticks+1;if(ticks>30000)$fatal(1,"watchdog mode=%0d state=%0d",mode,dut.state);
  if(cold_rst)begin attempt_resets<=0;a_rsp_valid<=0;o_rsp_valid<=0;aw<=0;ow<=0;rw<=0;lw<=0;a_ready<=0;o_ready<=0;reconfigure_done<=0;labels_done<=0;ai<=0;oi<=0;resets<=0;held_a<=0;held_o<=0;end
  else begin
   if(attempt_reset)begin attempt_resets<=attempt_resets+1;abort<=0;if(journal_count==0||!retry_safe||!backend_drained||!normal_retired)$fatal(1,"unsafe/empty retry reset");$fdisplay(logfd,"SOFT %0d %0d %0d",mode,journal_count,new_version);end
   if(held_a&&(!a_valid||{a_design,a_checkpoint,a_node,a_net,a_cookie}!==a_hold))$fatal(1,"authority request not stable");
   if(held_o&&(!o_valid||{o_op,o_node,o_net,o_cookie}!==o_hold))$fatal(1,"owner request not stable");
   held_a<=a_valid&&!a_ready;a_hold<={a_design,a_checkpoint,a_node,a_net,a_cookie};held_o<=o_valid&&!o_ready;o_hold<={o_op,o_node,o_net,o_cookie};
   a_ready<=ticks%3==0&&mode!=8;o_ready<=ticks%4==0&&mode!=9;
   if(target_reset)begin resets<=resets+1;if(!backend_drained||!normal_retired)$fatal(1,"reset before drain");end
   if(reconfigure_valid&&!reconfigure_done)begin rw<=rw+1;if(rw==(mode==12?600:3))reconfigure_done<=1;end
   if(!reconfigure_valid)begin rw<=0;reconfigure_done<=0;end
   if(labels_valid&&!labels_done)begin lw<=lw+1;if(lw==(mode==13?600:3))labels_done<=1;end
   if(!labels_valid)begin lw<=0;labels_done<=0;end
   if(a_valid&&a_ready)begin
    if(aw||a_rsp_valid)$fatal(1,"overlap authority");ai<=ai+1;aw<=mode==11?600:3;ni=a_node==100?0:1;nn=a_net-1;
    if((a_node!=100&&a_node!=200)||a_net<1||a_net>2)$fatal(1,"bad authority key");
    if($isunknown(a_design))$fatal(1,"authority request design X saved=%h internal=%h",saved_design,dut.a_design);a_status<=0;a_rsp_cookie<=a_cookie+(mode==2);a_rsp_checkpoint<=a_checkpoint+(mode==1);if(mode==19)a_rsp_design<=a_design+64'd1;else a_rsp_design<=a_design;
    a_refs<=mode==3?70000:authority[ni][nn];a_occupancy<=mode==4&&dut.verify_pass?2:(authority[ni][0]>0)+(authority[ni][1]>0);
    $fdisplay(logfd,"A %0d %0d %0d %0d %0d",mode,dut.verify_pass,a_node,a_net,authority[ni][nn]);
   end
   if(aw>0)begin aw<=aw-1;if(aw==1)a_rsp_valid<=1;end
   if(a_rsp_valid&&a_rsp_ready)begin if($isunknown({a_rsp_design,a_rsp_checkpoint,a_rsp_cookie,a_status}))$fatal(1,"unknown authority reply");$fdisplay(logfd,"AD %0d %h %h %h",mode,a_rsp_design,saved_design,dut.a_design);a_rsp_valid<=0;end
   if(o_valid&&o_ready)begin
    if(ow||o_rsp_valid)$fatal(1,"overlap owner");oi<=oi+1;ow<=3;ni=o_node==100?0:1;nn=o_net-1;
    if((o_node!=100&&o_node!=200)||o_net<1||o_net>2||o_op>2)$fatal(1,"bad owner key");
    after_count=current_refs[ni][nn]+(o_op==1?1:o_op==2?-1:0);if(after_count<0)$fatal(1,"underflow");
    current_refs[ni][nn]=after_count;after_occ=(current_refs[ni][0]>0)+(current_refs[ni][1]>0);
    o_rsp_cookie<=o_cookie+(mode==6);o_status<=mode==5?9:0;o_count<=after_count+(mode==7&&o_op!=0);o_occupancy<=after_occ;
    $fdisplay(logfd,"O %0d %0d %0d %0d %0d %0d",mode,dut.verify_pass,o_op,o_node,o_net,after_count);
   end
   if(ow>0)begin ow<=ow-1;if(ow==1)o_rsp_valid<=1;end
   if(o_rsp_valid&&o_rsp_ready)o_rsp_valid<=0;
  end
 end
 task init;begin
  @(negedge clk);cold_rst=1;retry_safe=1;abort=0;cfg_valid=0;cfg_rsp_ready=0;j_valid=0;recover_valid=0;rsp_ready=0;backend_drained=1;normal_retired=1;
  cfg_authoritative=1;cfg_checkpoint=17;cfg_version=3;cfg_query=1;cfg_price=3;recover_checkpoint=17;recover_version=4;recover_query=2;recover_price=4;recover_design=64'h12345678;
  authority[0][0]=2;authority[0][1]=0;authority[1][0]=0;authority[1][1]=1;
  for(integer x=0;x<2;x=x+1)for(integer y=0;y<2;y=y+1)current_refs[x][y]=authority[x][y];
  repeat(3)@(negedge clk);cold_rst=0;repeat(2)@(negedge clk);
 end endtask
 task install(input integer status);begin
  @(negedge clk);cfg_valid=1;do @(posedge clk);while(!cfg_ready);@(negedge clk);cfg_valid=0;
  wait(cfg_rsp_valid);@(negedge clk);if(cfg_status!=status)$fatal(1,"install status");repeat(3)@(negedge clk);cfg_rsp_ready=1;@(negedge clk);cfg_rsp_ready=0;repeat(2)@(negedge clk);
 end endtask
 task intent(input integer node,net,op);begin
  @(negedge clk);j_node=node;j_net=net;j_op=op;j_valid=1;do @(posedge clk);while(!j_ready);@(negedge clk);j_valid=0;
  current_refs[node==100?0:1][net-1]=current_refs[node==100?0:1][net-1]+(op==1?1:-1);
 end endtask
 task dirty;begin
  intent(100,1,2);intent(100,2,1);intent(100,2,1);intent(200,2,2);intent(200,1,1);
  if(journal_count!=4||!journal_full)$fatal(1,"unique journal");
 end endtask
 task request;begin
  @(negedge clk);recover_cookie=recover_cookie+100;recover_valid=1;do @(posedge clk);while(!recover_ready);@(negedge clk);recover_valid=0;
 end endtask
 task retire(input integer status,corrected);reg[67:0]hold;begin
  wait(rsp_valid);@(negedge clk);if(rsp_status!=status||rsp_corrected!=corrected||rsp_cookie!=recover_cookie)$fatal(1,"result mode=%0d status=%0d/%0d corrected=%0d/%0d",mode,rsp_status,status,rsp_corrected,corrected);
  if(permit_work||a_valid||o_valid||aw||ow||a_rsp_valid||o_rsp_valid)$fatal(1,"completion or release before drain");
  hold={rsp_status,rsp_cookie,rsp_corrected};repeat(5)begin @(negedge clk);if(!rsp_valid||permit_work||{rsp_status,rsp_cookie,rsp_corrected}!==hold)$fatal(1,"held completion changed");end
  $fdisplay(logfd,"R %0d %0d %0d %0d",mode,rsp_status,rsp_corrected,journal_count);checks=checks+1;
  rsp_ready=1;@(negedge clk);rsp_ready=0;repeat(2)@(negedge clk);
 end endtask
 initial begin
  if(!$value$plusargs("events=%s",path))$fatal(1,"events path");logfd=$fopen(path,"w");
  mode=0;init;install(0);dirty;
  // Full journal cannot accept a fifth distinct dirty key.
  @(negedge clk);j_node=300;j_net=1;j_valid=1;repeat(5)begin @(negedge clk);if(j_ready||journal_count!=4)$fatal(1,"journal overflow");end j_valid=0;
  cfg_checkpoint=18;cfg_authoritative=0;install(1);if(journal_count!=4||saved_checkpoint!=17)$fatal(1,"invalid install discarded log");cfg_checkpoint=17;cfg_authoritative=1;
  backend_drained=0;normal_retired=0;request;repeat(7)begin @(negedge clk);if(target_reset||permit_work)$fatal(1,"early reset");end backend_drained=1;repeat(3)@(negedge clk);if(target_reset)$fatal(1,"reply not retired");normal_retired=1;
  wait(labels_valid);@(negedge clk);backend_drained=0;repeat(8)begin @(negedge clk);if(rsp_valid||permit_work)$fatal(1,"label completion without drain");end backend_drained=1;
  retire(0,5);if(!permit_work||fault||resets!=3||journal_count!=0)$fatal(1,"successful restore publication");
  for(i=0;i<2;i=i+1)for(j=0;j<2;j=j+1)if(current_refs[i][j]!=authority[i][j])$fatal(1,"authority mismatch");
  intent(100,1,1);authority[0][0]=3;cfg_checkpoint=18;cfg_version=4;cfg_query=2;cfg_price=4;install(0);if(journal_count||saved_checkpoint!=18)$fatal(1,"committed checkpoint install");
  // Reuse the same coordinator after a trusted checkpoint advance.
  intent(100,1,2);recover_checkpoint=18;recover_version=5;recover_query=3;recover_price=5;request;retire(0,1);
  if(current_refs[0][0]!=3||saved_checkpoint!=18||resets!=6||new_version!=5||!permit_work)$fatal(1,"second recovery episode");
  mode=1;init;install(0);dirty;request;retire(2,0);if(!fault||journal_count!=4)$fatal(1,"authority identity failure");
  mode=2;init;install(0);dirty;request;retire(2,0);
  mode=3;init;install(0);dirty;request;retire(2,0);
  mode=4;init;install(0);dirty;request;retire(4,5);if(labels_valid||!fault)$fatal(1,"occupancy verification bypass");
  mode=5;init;install(0);dirty;request;retire(3,0);
  mode=6;init;install(0);dirty;request;retire(3,0);
  mode=7;init;install(0);dirty;request;retire(3,1);
  mode=8;init;install(0);dirty;request;wait(a_valid);@(negedge clk);abort=1;repeat(5)@(negedge clk);if(!a_valid||rsp_valid)$fatal(1,"cancel withdrew authority");mode=0;retire(6,0);
  mode=9;init;install(0);dirty;request;wait(o_valid);@(negedge clk);abort=1;repeat(5)@(negedge clk);if(!o_valid||rsp_valid)$fatal(1,"cancel withdrew owner");mode=0;retire(6,0);
  mode=10;init;install(0);dirty;request;wait(o_op==1&&dut.state==7);@(negedge clk);abort=1;retire(6,1);
  mode=11;init;install(0);dirty;request;retire(6,0);
  mode=12;init;install(0);dirty;request;retire(6,0);
  mode=13;init;install(0);dirty;request;retire(6,5);
  mode=14;init;install(0);recover_version=3;request;retire(1,0);if(resets||fault||!permit_work)$fatal(1,"bad generation reject");
  recover_version=4;recover_price=3;request;retire(1,0);if(resets||fault)$fatal(1,"bad price reject");
  recover_price=4;recover_checkpoint=99;request;retire(1,0);recover_checkpoint=17;
  recover_design=64'h12345679;request;retire(1,0);recover_design=64'h12345678;
  recover_query=1;request;retire(1,0);recover_query=2;
  request;retire(0,0);if(ai||oi||resets!=3||!permit_work)$fatal(1,"empty journal restore");
  mode=15;init;install(0);dirty;current_refs[0][0]=9;request;retire(5,0);
  mode=16;init;install(0);intent(100,1,2);intent(100,2,1);
  @(negedge clk);j_node=200;j_net=2;j_op=2;j_valid=1;recover_cookie=recover_cookie+100;recover_valid=1;
  @(posedge clk);if(!j_ready||recover_ready)$fatal(1,"pending journal must precede recovery");
  @(negedge clk);j_valid=0;current_refs[1][1]=0;
  do @(posedge clk);while(!recover_ready);@(negedge clk);recover_valid=0;retire(0,3);
  mode=17;init;install(0);dirty;intent(200,1,1);if(journal_count!=4||!journal_full)$fatal(1,"full-journal duplicate");request;retire(0,6);
  mode=18;init;install(0);backend_drained=0;normal_retired=0;request;repeat(600)@(negedge clk);
  if(!fault||rsp_valid||target_reset)$fatal(1,"timeout released old transaction");backend_drained=1;normal_retired=1;retire(6,0);if(resets)$fatal(1,"reset despite canceled drain");
  mode=19;init;install(0);dirty;request;retire(2,0);
  // A trusted new snapshot cannot install ahead of an existing normal intent.
  mode=20;init;install(0);normal_retired=0;cfg_checkpoint=18;
  @(negedge clk);j_node=100;j_net=1;j_op=1;j_valid=1;cfg_valid=1;
  @(posedge clk);if(!j_ready||cfg_ready)$fatal(1,"checkpoint overtook journal");
  @(negedge clk);j_valid=0;current_refs[0][0]=3;authority[0][0]=3;
  repeat(4)begin @(negedge clk);if(cfg_ready||journal_count!=1)$fatal(1,"checkpoint before normal retirement");end
  normal_retired=1;do @(posedge clk);while(!cfg_ready);@(negedge clk);cfg_valid=0;
  wait(cfg_rsp_valid);@(negedge clk);if(cfg_status||journal_count||saved_checkpoint!=18)$fatal(1,"trusted install");cfg_rsp_ready=1;@(negedge clk);cfg_rsp_ready=0;
  mode=21;init;install(0);
  // Accepted intent did not physically execute: do not invert the op blindly.
  @(negedge clk);j_node=100;j_net=1;j_op=2;j_valid=1;do @(posedge clk);while(!j_ready);@(negedge clk);j_valid=0;
  request;retire(0,0);if(current_refs[0][0]!=2||oi!=2)$fatal(1,"journal intent is not a committed mutation");
  mode=22;init;install(0);intent(100,1,2);current_refs[0][1]=1;request;retire(4,1);
  if(!fault||permit_work||journal_count!=1)$fatal(1,"unlogged other-net occupancy accepted");

  // Retry the same dirty journal without a cold reset or authority re-install.
  mode=5;init;install(0);dirty;request;retire(3,0);
  recover_query=3;request;retire(1,0); // version4 already consumed by failed attempt
  recover_version=5;recover_price=5;recover_query=2;request;retire(1,0);
  recover_query=1;request;retire(1,0); // current committed query identity
  recover_query=3;recover_checkpoint=18;request;retire(1,0);recover_checkpoint=17;
  recover_price=4;request;retire(1,0);recover_price=5;
  if(journal_count!=4||resets!=3||attempt_resets||!fault||permit_work)$fatal(1,"invalid retry discarded state");
  mode=0;retry_safe=0;abort=1;
  @(negedge clk);recover_cookie=recover_cookie+100;recover_valid=1;
  repeat(7)begin @(negedge clk);if(recover_ready||attempt_reset||journal_count!=4)$fatal(1,"retry before service retirement");end
  retry_safe=1;backend_drained=0;repeat(4)begin @(negedge clk);if(recover_ready||attempt_reset)$fatal(1,"retry before physical drain");end
  backend_drained=1;normal_retired=0;repeat(4)begin @(negedge clk);if(recover_ready||attempt_reset)$fatal(1,"retry before normal retirement");end
  normal_retired=1;a_rsp_valid=1;repeat(4)begin @(negedge clk);if(recover_ready||attempt_reset)$fatal(1,"retry admitted unexpected authority response");end
  a_rsp_valid=0;do @(posedge clk);while(!recover_ready);@(negedge clk);recover_valid=0;
  retire(0,5);if(journal_count||fault||!permit_work||resets!=6||attempt_resets!=1||new_version!=5||new_query!=3)$fatal(1,"journal preserving retry");
  for(i=0;i<2;i=i+1)for(j=0;j<2;j=j+1)if(current_refs[i][j]!=authority[i][j])$fatal(1,"retry authority mismatch");
  // Failed reply after a physical correction: reread actual refs, no blind inverse.
  mode=7;init;install(0);dirty;request;retire(3,1);
  mode=0;recover_version=5;recover_price=5;recover_query=3;request;retire(0,4);
  if(journal_count||attempt_resets!=1||resets!=6||!permit_work)$fatal(1,"partial repair retry");
  // Labels timeout occurs after all owner corrections; retry must not redo INC/DEC.
  mode=13;init;install(0);dirty;request;retire(6,5);
  mode=0;recover_version=5;recover_price=5;recover_query=3;request;retire(0,0);
  if(journal_count||attempt_resets!=1||resets!=6||!permit_work)$fatal(1,"labels retry");

  $fflush(logfd);$fclose(logfd);$display("RECOVERY_COORDINATOR_PASS checks=%0d",checks);$finish;
 end
endmodule
