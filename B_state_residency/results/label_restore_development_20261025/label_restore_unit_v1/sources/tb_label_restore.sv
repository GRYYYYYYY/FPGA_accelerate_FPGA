`timescale 1ns/1ps
module tb_label_restore;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,abort=0,backend_drained=1,start_valid=0,rsp_ready=0,s_valid=0;
 wire start_ready,s_ready,rsp_valid,busy,fault;reg[63:0]start_design=123,expected_design=123;
 reg[31:0]start_checkpoint=17,expected_checkpoint=17,start_cookie=100,start_count=3,start_nodes=16,start_probe=2,start_version=4;
 reg[1:0]start_query=2;reg[3:0]start_price=4;reg[31:0]s_node=0,s_cookie=100;reg[159:0]s_payload=0;reg s_last=0;
 wire[3:0]rsp_status;wire[31:0]rsp_cookie,written,verified;
 wire c_valid,c_rsp_ready,l_valid,l_write,l_rsp_ready;reg c_ready=0,c_rsp_valid=0,l_ready=0,l_rsp_valid=0;
 wire[1:0]c_op,c_query;wire[3:0]c_price;wire[31:0]c_version,l_node,l_value;wire[2:0]l_field;
 reg[3:0]c_status=0,l_status=0;reg l_present=0;reg[159:0]l_payload=0;
 label_restore_controller #(.MAX_RECORDS(4),.MAX_CYCLES(1024))dut(.*);
 reg[159:0]mem[0:15];reg present[0:15];integer ticks=0,mode=0,cwait=0,lwait=0,controls=0,reads=0,writes=0,checks=0,i,j,fd;
 reg hc=0,hl=0;reg[39:0]ch;reg[67:0]lh;string path;
 always @(posedge clk)begin
  ticks<=ticks+1;if(ticks>30000)$fatal(1,"watchdog mode=%0d state=%0d",mode,dut.state);
  if(rst)begin c_ready<=0;l_ready<=0;c_rsp_valid<=0;l_rsp_valid<=0;cwait<=0;lwait<=0;controls<=0;reads<=0;writes<=0;hc<=0;hl<=0;end
  else begin
   if(hc&&(!c_valid||{c_op,c_query,c_price,c_version}!==ch))$fatal(1,"control VALID changed under stall");
   if(hl&&(!l_valid||{l_write,l_node,l_field,l_value}!==lh))$fatal(1,"label VALID changed under stall");
   hc<=c_valid&&!c_ready;ch<={c_op,c_query,c_price,c_version};hl<=l_valid&&!l_ready;lh<={l_write,l_node,l_field,l_value};
   c_ready<=ticks%3==0&&(mode!=17||abort);l_ready<=ticks%4==0;
   if(c_valid&&c_ready)begin
    if(cwait||c_rsp_valid)$fatal(1,"control overlap");cwait<=3;controls<=controls+1;c_status<=mode==6||mode==16&&c_op==1?9:0;
    if(c_op==0)for(integer x=0;x<16;x=x+1)present[x]=0;
    $fdisplay(fd,"C %0d %0d %0d",mode,ticks,c_op);
   end
   if(cwait>0)begin cwait<=cwait-1;if(cwait==1)c_rsp_valid<=1;end
   if(c_rsp_valid&&c_rsp_ready)c_rsp_valid<=0;
   if(l_valid&&l_ready)begin
    if(lwait||l_rsp_valid)$fatal(1,"label overlap");if(l_node>=16||l_field>4)$fatal(1,"bad label request");
    lwait<=mode==18?12:3;l_status<=mode==8||mode==15&&l_write||mode==20&&!l_write&&reads>0?9:0;
    if(l_write)begin mem[l_node][l_field*32+:32]=l_value;present[l_node]=1;writes<=writes+1;end
    else begin reads<=reads+1;l_payload<=mem[l_node]^(mode==13&&reads>0?160'd1:160'd0);l_present<=reads==0?(mode==7):mode==14?0:present[l_node];end
    $fdisplay(fd,"L %0d %0d %0d %0d %0d %08h",mode,ticks,l_write,l_node,l_field,l_value);
   end
   if(lwait>0)begin lwait<=lwait-1;if(lwait==1)l_rsp_valid<=1;end
   if(l_rsp_valid&&l_rsp_ready)l_rsp_valid<=0;
  end
 end
 task init(input integer m);begin
  @(negedge clk);rst=1;mode=m;abort=0;backend_drained=1;start_valid=0;s_valid=0;rsp_ready=0;
  start_design=123;start_checkpoint=17;start_count=3;start_nodes=16;start_probe=2;start_version=4;start_query=2;start_price=4;start_cookie=100+m;
  for(integer x=0;x<16;x=x+1)begin mem[x]=0;present[x]=0;end
  repeat(3)@(negedge clk);rst=0;
 end endtask
 task request;begin
  @(negedge clk);start_valid=1;do @(posedge clk);while(!start_ready);@(negedge clk);start_valid=0;
 end endtask
 task feed(input integer n);begin
  @(negedge clk);s_valid=1;s_node=n+2;s_cookie=start_cookie;s_payload={32'd9,32'd8,32'd7,32'd6,32'd5}+n;s_last=n==2;
  if(mode==9)s_cookie=s_cookie+1;if(mode==10)s_last=1;if(mode==11)s_node=16;if(mode==12&&n==2)s_last=0;
  do @(posedge clk);while(!s_ready);@(negedge clk);s_valid=0;
 end endtask
 task retire(input integer want);reg[99:0]hold;begin
  wait(rsp_valid);@(negedge clk);
  if(rsp_status!=want||rsp_cookie!=start_cookie||fault!=(want!=0)||!backend_drained||cwait||lwait||c_rsp_valid||l_rsp_valid)$fatal(1,"result m=%0d got=%0d want=%0d",mode,rsp_status,want);
  if(want==0)begin
   if(written!=3||verified!=3||controls!=2||writes!=15||reads!=4)$fatal(1,"success counters");
   for(integer x=0;x<3;x=x+1)if(mem[x+2]!==({32'd9,32'd8,32'd7,32'd6,32'd5}+x))$fatal(1,"final bytes");
  end
  hold={rsp_status,rsp_cookie,written,verified};repeat(5)begin @(negedge clk);if(!rsp_valid||start_ready||{rsp_status,rsp_cookie,written,verified}!==hold)$fatal(1,"response instability");end
  $fdisplay(fd,"R %0d %0d %0d %0d %0d %0d %0d",mode,rsp_status,written,verified,controls,writes,reads);checks=checks+1;
  rsp_ready=1;@(negedge clk);rsp_ready=0;@(negedge clk);if(want!=0&&start_ready)$fatal(1,"failed service reopened");
 end endtask
 initial begin
  if(!$value$plusargs("events=%s",path))$fatal(1,"events path");fd=$fopen(path,"w");
  for(i=0;i<=22;i=i+1)begin
   init(i);
   if(i==1)start_design=124;if(i==2)start_count=0;if(i==3)start_count=5;if(i==4)start_price=3;if(i==5)start_probe=16;
   request;
   if(i==17)begin wait(c_valid);@(negedge clk);backend_drained=0;abort=1;wait(c_rsp_valid&&c_rsp_ready);repeat(10)begin @(negedge clk);if(rsp_valid)$fatal(1,"abort completed before drain");end backend_drained=1;end
   else if(i==18)begin wait(l_valid&&l_ready);@(negedge clk);abort=1;end
   else if(i==19)begin wait(s_ready);end
   else if(i==22)begin feed(0);end
   else if(i==0||i>=9&&i<=16||i==20||i==21)begin
    if(i==21)backend_drained=0;
    for(j=0;j<3;j=j+1)begin feed(j);if(i==9||i==10||i==11||i==15)j=3;end
    if(i==21)begin wait(dut.state==11);repeat(10)begin @(negedge clk);if(rsp_valid)$fatal(1,"early successful completion");end backend_drained=1;end
   end
   retire(i==0||i==21?0:i<=5?1:i==6||i==16?2:i==7?3:i==8||i==15||i==20?4:i==9||i==10||i==11||i==12?5:i==13||i==14?6:7);
  end
  $fflush(fd);$fclose(fd);$display("LABEL_RESTORE_PASS checks=%0d",checks);$finish;
 end
endmodule
