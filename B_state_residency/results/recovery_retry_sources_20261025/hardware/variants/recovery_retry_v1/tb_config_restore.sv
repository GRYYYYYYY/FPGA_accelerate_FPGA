`timescale 1ns/1ps
module tb_config_restore;
 reg attempt_reset=0;reg[2303:0]saved_descriptor;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,abort=0,backend_drained=1,normal_retired=1;
 reg load_valid=0,load_authoritative=1,load_rsp_ready=0,start_valid=0,rsp_ready=0;
 wire load_ready,load_rsp_valid,load_status,start_ready,rsp_valid,busy,fault;
 reg[2303:0]load_payload=0;reg[63:0]load_design=123,start_design=123;reg[31:0]load_checkpoint=17,start_checkpoint=17,start_cookie=0,start_version=4;reg[3:0]start_price=4;
 wire[5:0]cfg_valid,cfg_rsp_ready,sent,retired;reg[5:0]cfg_ready=0,cfg_rsp_valid=0;reg[17:0]cfg_status=0;wire[2303:0]cfg_payload;wire[3:0]rsp_status;wire[31:0]rsp_cookie;wire[63:0]saved_design;wire[31:0]saved_checkpoint;
 config_restore_controller #(.MAX_CYCLES(256))dut(.*);
 integer ticks=0,mode=0,checks=0,loads=0,fd,j;integer delays[0:5],accepts[0:5];reg permit_stalled=0;reg[5:0]held=0;reg[2303:0]held_payload,gold;string path;
 task payload;begin
 load_payload=0;
 load_payload[0+:384]={128'd0,32'd1,32'd8,32'd16,32'd24,64'd123,64'h1000};
 load_payload[384+:384]={128'd0,32'd32,32'd16,64'h4000,64'h3000,64'h2000};
 load_payload[768+:384]={288'd0,32'd16,64'h5000};
 load_payload[1152+:384]={192'd0,32'd0,32'd311,64'h7000,64'h6000};
 load_payload[1536+:384]={128'd0,32'd0,32'd16,64'h9000,64'h9000,64'h8000};
 load_payload[1920+:384]={32'd0,32'd3,32'd8,32'd16,64'd123,64'hc000,64'hb000,64'ha000};
 end endtask
 always @(posedge clk)begin
  ticks<=ticks+1;if(ticks>15000)$fatal(1,"watchdog mode=%0d state=%0d",mode,dut.state);
  if(rst)begin cfg_ready<=0;cfg_rsp_valid<=0;cfg_status<=0;held<=0;for(integer x=0;x<6;x=x+1)begin delays[x]<=0;accepts[x]<=0;end end
  else begin
   for(integer x=0;x<6;x=x+1)begin
    if(held[x]&&(!cfg_valid[x]||cfg_payload!==held_payload))$fatal(1,"offered config withdrawn/changed lane%0d",x);
    cfg_ready[x]<=ticks%(x+2)==0&&!(mode==12&&x==0&&!permit_stalled)&&!(mode==13&&x==3&&!permit_stalled)&&!(mode==22&&x==4&&!permit_stalled);
    if(cfg_valid[x]&&cfg_ready[x])begin
     if(accepts[x]!=0||delays[x]||cfg_rsp_valid[x])$fatal(1,"duplicate config lane%0d",x);
     if(x>0&&!retired[0])$fatal(1,"dependent lanes before connection config retired");
     if(cfg_payload!=={gold[2303:2272],start_version,gold[2239:0]})$fatal(1,"descriptor corrupted");
     accepts[x]<=accepts[x]+1;delays[x]<=mode==14&&x==2?300:3+x;
     cfg_status[x*3+:3]<=(mode==10&&x==0||mode==11&&x==2||mode==21&&x==5||mode==22&&x==1)?3'd5:0;
     $fdisplay(fd,"C %0d %0d %0d",mode,ticks,x);
    end
    if(delays[x]>0)begin delays[x]<=delays[x]-1;if(delays[x]==1)cfg_rsp_valid[x]<=1;end
    if(cfg_rsp_valid[x]&&cfg_rsp_ready[x])begin cfg_rsp_valid[x]<=0;$fdisplay(fd,"B %0d %0d %0d %0d",mode,ticks,x,cfg_status[x*3+:3]);end
   end
   held<=cfg_valid&~cfg_ready;held_payload<=cfg_payload;
  end
 end
 task init(input integer m);begin
  @(negedge clk);rst=1;attempt_reset=0;mode=m;abort=0;permit_stalled=0;backend_drained=1;normal_retired=1;load_valid=0;start_valid=0;rsp_ready=0;load_rsp_ready=0;
  load_authoritative=1;load_design=123;load_checkpoint=17;start_design=123;start_checkpoint=17;start_cookie=100+m;start_version=4;start_price=4;payload;
  repeat(3)@(negedge clk);rst=0;
 end endtask
 task install(input integer want);begin
  @(negedge clk);load_valid=1;do @(posedge clk);while(!load_ready);@(negedge clk);load_valid=0;
  wait(load_rsp_valid);@(negedge clk);if(load_status!=want)$fatal(1,"load status m=%0d",mode);
  repeat(3)begin @(negedge clk);if(!load_rsp_valid||start_ready)$fatal(1,"load response lease");end
  if(!want)gold=load_payload;$fdisplay(fd,"I %0d %0d",mode,load_status);loads=loads+1;load_rsp_ready=1;@(negedge clk);load_rsp_ready=0;
 end endtask
 task request;begin
  @(negedge clk);start_valid=1;do @(posedge clk);while(!start_ready);@(negedge clk);start_valid=0;
 end endtask
 task result(input integer want,mask);reg[47:0]hold;begin
  wait(rsp_valid);@(negedge clk);
  if(rsp_status!=want||rsp_cookie!=start_cookie||sent!=mask||retired!=mask||fault!=(want!=0)||!backend_drained||!normal_retired||cfg_valid||cfg_rsp_ready||cfg_rsp_valid)$fatal(1,"result m=%0d status=%0d/%0d sent=%h/%h retired=%h",mode,rsp_status,want,sent,mask,retired);
  for(integer x=0;x<6;x=x+1)if(delays[x]||accepts[x]!=((mask>>x)&1))$fatal(1,"unretired/duplicate lane");
  hold={rsp_status,rsp_cookie,sent,retired};repeat(5)begin @(negedge clk);if(!rsp_valid||start_ready||{rsp_status,rsp_cookie,sent,retired}!==hold)$fatal(1,"held result changed");end
  $fdisplay(fd,"R %0d %0d %0d %0d",mode,rsp_status,sent,retired);checks=checks+1;
  rsp_ready=1;@(negedge clk);rsp_ready=0;@(negedge clk);if(want&&start_ready)$fatal(1,"failed instance reopened");
 end endtask

 task soft_clear;begin
  @(negedge clk);attempt_reset=1;repeat(2)@(negedge clk);attempt_reset=0;
  if(fault||!dut.configured||dut.descriptor!==saved_descriptor||saved_design!=123||saved_checkpoint!=17)$fatal(1,"soft reset lost resident descriptor");
  for(integer x=0;x<6;x=x+1)accepts[x]=0;
 end endtask

 initial begin
  if(!$value$plusargs("events=%s",path))$fatal(1,"event path");fd=$fopen(path,"w");
  for(j=0;j<=25;j=j+1)begin
   init(j);
   if(j==1)load_authoritative=0;if(j==2)load_payload[64+:64]=124;if(j==3)load_payload[2176+:32]=17;if(j==4)load_payload[2272+:32]=1;if(j==23)load_payload[160+:32]=0;if(j==24)load_payload[2112+:64]=124;if(j==25)load_payload[2208+:32]=9;
   if(j>=1&&j<=4||j>=23)begin install(1);payload;load_authoritative=1;install(0);end else install(0);
   if(j==5)start_design=124;if(j==6)start_checkpoint=18;if(j==7)start_version=3;if(j==8)start_price=3;
   if(j==9)begin load_checkpoint=16;install(1);end
   if(j==18)load_payload=~load_payload;
   if(j==19)begin load_checkpoint=18;load_payload[2240+:32]=2;install(1);payload;end
   if(j==20)begin
    load_checkpoint=18;start_checkpoint=18;@(negedge clk);load_valid=1;start_valid=1;
    do @(posedge clk);while(!load_ready);if(start_ready)$fatal(1,"simultaneous install/start priority");@(negedge clk);load_valid=0;
    wait(load_rsp_valid);@(negedge clk);if(load_status)$fatal(1,"joint install status");gold=load_payload;$fdisplay(fd,"I %0d %0d",mode,load_status);loads=loads+1;
    repeat(3)begin @(negedge clk);if(start_ready)$fatal(1,"start before install response retired");end
    load_rsp_ready=1;@(negedge clk);load_rsp_ready=0;
    do @(posedge clk);while(!start_ready);@(negedge clk);start_valid=0;
   end else request;
   if(j==18)begin wait(cfg_valid[1]);@(negedge clk);load_payload=0;load_valid=1;repeat(3)begin @(negedge clk);if(load_ready)$fatal(1,"config overwritten during recovery");end load_valid=0;end
   if(j==22)begin wait(cfg_rsp_valid[1]&&cfg_rsp_ready[1]);repeat(20)begin @(negedge clk);if(!cfg_valid[4]||rsp_valid)$fatal(1,"error withdrew another offered lane");end permit_stalled=1;end
   if(j==12)begin wait(cfg_valid[0]);@(negedge clk);abort=1;backend_drained=0;repeat(20)begin @(negedge clk);if(!cfg_valid[0]||rsp_valid)$fatal(1,"abort withdrew first lane");end permit_stalled=1;wait(retired[0]);repeat(8)begin @(negedge clk);if(rsp_valid)$fatal(1,"abort early drain");end backend_drained=1;end
   if(j==13)begin wait(cfg_valid[3]);repeat(270)begin @(negedge clk);if(!cfg_valid[3]||rsp_valid)$fatal(1,"timeout withdrew outstanding lane");end permit_stalled=1;end
   if(j==15)begin backend_drained=0;wait(retired==63);repeat(10)begin @(negedge clk);if(rsp_valid)$fatal(1,"physical drain skipped");end backend_drained=1;end
   if(j==16)begin normal_retired=0;wait(retired==63);repeat(10)begin @(negedge clk);if(rsp_valid)$fatal(1,"normal retirement skipped");end normal_retired=1;end
   if(j==17)begin wait(cfg_valid[1]);@(negedge clk);abort=1;end
   result(j>=5&&j<=8?1:j==10||j==11||j==21||j==22?2:j==12||j==13||j==14||j==17?3:0,j>=5&&j<=8?0:j==10||j==12?1:63);
   if(j==0)begin
    load_checkpoint=18;load_payload[2240+:32]=4;install(0);
    for(integer x=0;x<6;x=x+1)accepts[x]=0;
    start_checkpoint=18;start_version=5;start_price=5;start_cookie=200;request;result(0,63);
   end
  end

  init(11);install(0);saved_descriptor=gold;request;
  wait(rsp_valid);@(negedge clk);attempt_reset=1;
  repeat(4)begin @(negedge clk);if(!rsp_valid||rsp_status!=2||!fault||dut.descriptor!==saved_descriptor)$fatal(1,"soft reset erased unretired reply");end
  attempt_reset=0;result(2,63);
  attempt_reset=1;backend_drained=0;repeat(4)begin @(negedge clk);if(!fault||start_ready)$fatal(1,"soft clear without drain");end
  backend_drained=1;normal_retired=0;repeat(4)begin @(negedge clk);if(!fault||start_ready)$fatal(1,"soft clear before retirement");end
  normal_retired=1;soft_clear;
  mode=0;start_cookie=500;start_version=5;start_price=5;request;result(0,63);
  soft_clear;if(dut.current_version!=5)$fatal(1,"soft clear rolled version back");
  start_cookie=501;request;result(1,0);
  soft_clear;start_cookie=502;start_version=6;start_price=6;request;result(0,63);
  init(12);install(0);saved_descriptor=gold;request;wait(cfg_valid[0]);@(negedge clk);attempt_reset=1;
  repeat(5)begin @(negedge clk);if(!cfg_valid[0]||rsp_valid||dut.descriptor!==saved_descriptor)$fatal(1,"active soft reset withdrew offer");end
  attempt_reset=0;permit_stalled=1;result(0,63);

  $fflush(fd);$fclose(fd);$display("CONFIG_RESTORE_PASS checks=%0d loads=%0d",checks,loads);$finish;
 end
endmodule
