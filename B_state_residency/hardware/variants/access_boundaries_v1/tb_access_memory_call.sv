`timescale 1ns/1ps
module tb_access_memory_call;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,abort=0,active=1,req_valid=0,rsp_ready=0;
 reg [1:0] active_query=2,req_query=2;reg [3:0] active_price=9,req_price=9;
 reg [639:0] req_words=0;reg [31:0] req_cookie=32'hd00d0001;
 wire req_ready,rsp_valid,busy,fault;wire [191:0] rsp_words;
 wire [31:0] rsp_cookie;wire [1:0] rsp_query,rsp_status;wire [3:0] rsp_price;
 wire ap_start;reg ap_idle=1,ap_ready=0,ap_done=0;
 reg [4:0] ia0=0,ia1=0;reg ic0=0,ic1=0;wire [31:0] iq0,iq1;
 reg [2:0] oa0=0,oa1=0;reg oc0=0,oc1=0,ow0=0,ow1=0;reg [31:0] od0=0,od1=0;
 access_memory_call #(.MAX_CALL_CYCLES(16)) dut(.*);
 integer a,b,c,d,e,z,n,perms=0,checks=0,caseid,cycles=0,f;
 integer order[0:5];reg [191:0] held;reg [31:0] hc;
 always @(posedge clk)begin cycles=cycles+1;if(cycles>60000)$fatal(1,"watchdog");end
 task clear_events;
 begin ap_ready=0;ap_done=0;ic0=0;ic1=0;oc0=0;oc1=0;ow0=0;ow1=0;#1;end endtask
 task reset;
 begin
  @(negedge clk);rst=1;abort=0;req_valid=0;rsp_ready=0;active=1;
  active_query=2;active_price=9;req_query=2;req_price=9;ap_idle=1;clear_events();
  repeat(2)@(posedge clk);@(negedge clk);rst=0;
  @(negedge clk);if(fault||!req_ready||rsp_valid)$fatal(1,"reset");
 end endtask
 task launch;
 begin
  for(n=0;n<20;n=n+1)req_words[n*32+:32]=32'h12340000+n;
  req_valid=1;@(posedge clk);#1;req_valid=0;req_words=0;
  @(negedge clk);if(!ap_start||req_ready||fault)$fatal(1,"launch");ap_idle=0;
 end endtask
 task write0(input integer addr);
 begin oa0=addr;od0=32'hfeed0000+addr;oc0=1;ow0=1;end endtask
 task write1(input integer addr);
 begin oa1=addr;od1=32'hfeed0000+addr;oc1=1;ow1=1;end endtask
 task step;
 begin @(posedge clk);#1;@(negedge clk);end endtask
 task expect_stop(input integer id);
 begin
  @(posedge clk);#1;if(!fault||req_ready)$fatal(1,"missing fault %0d",id);
  @(negedge clk);clear_events();abort=0;active=1;active_query=2;active_price=9;
  repeat(3)begin @(posedge clk);#1;if(!fault||req_ready||ap_start)$fatal(1,"fault not latched %0d",id);end
  checks=checks+1;$fdisplay(f,"FAULT %0d",id);
 end endtask
 initial begin
  f=$fopen("collector_cases.txt","w");
  for(a=0;a<6;a=a+1)for(b=0;b<6;b=b+1)for(c=0;c<6;c=c+1)for(d=0;d<6;d=d+1)for(e=0;e<6;e=e+1)for(z=0;z<6;z=z+1)
   if(a!=b&&a!=c&&a!=d&&a!=e&&b!=c&&b!=d&&b!=e&&c!=d&&c!=e&&d!=e&&z!=a&&z!=b&&z!=c&&z!=d&&z!=e)begin
    reset();launch();
    ia0=19;ia1=0;ic0=1;ic1=1;step();
    if(iq0!==32'h12340013||iq1!==32'h12340000)$fatal(1,"snapshot/read latency");clear_events();
    order[0]=a;order[1]=b;order[2]=c;order[3]=d;order[4]=e;
    write0(a);write1(b);step();clear_events();
    if(fault||rsp_valid)$fatal(1,"early outputs rejected");
    write0(c);write1(d);step();clear_events();
    write0(e);write1(z);ap_done=1;ap_ready=1;step();clear_events();ap_idle=1;
    if(!rsp_valid||fault||ap_start||rsp_status!==0||rsp_cookie!==req_cookie||rsp_query!==2||rsp_price!==9)$fatal(1,"completion");
    for(n=0;n<6;n=n+1)if(rsp_words[n*32+:32]!==32'hfeed0000+n)$fatal(1,"word %0d",n);
    held=rsp_words;repeat(20)begin step();if(!rsp_valid||fault||rsp_words!==held)$fatal(1,"stall/timeout");end
    rsp_ready=1;step();rsp_ready=0;if(rsp_valid||!req_ready)$fatal(1,"retire");
    perms=perms+1;$fdisplay(f,"ORDER %0d %0d %0d %0d %0d %0d",a,b,c,d,e,z);
   end
  // Each case isolates one contract violation, no hierarchical force/deposit.
  for(caseid=0;caseid<18;caseid=caseid+1)begin
   reset();if(caseid!=6&&caseid!=7&&caseid!=17)launch();
   case(caseid)
    0:begin ia0=20;ic0=1;end
    1:begin ia1=31;ic1=1;end
    2:write0(6);
    3:write1(7);
    4:begin write0(2);step();clear_events();write1(2);end
    5:begin write0(1);write1(1);end
    6:write0(0);
    7:begin ap_done=1;ap_ready=1;end
    8:ap_ready=1;
    9:ap_done=1;
    10:begin write0(0);ap_done=1;ap_ready=1;end
    11:begin repeat(17)step();end
    12:active_query=3;
    13:active_price=8;
    14:active=0;
    15:abort=1;
    16:begin
     write0(0);write1(1);step();clear_events();write0(2);write1(3);step();clear_events();
     write0(4);write1(5);ap_done=1;ap_ready=1;step();clear_events();ap_idle=1;
     if(!rsp_valid||fault)$fatal(1,"late fault setup");held=rsp_words;hc=rsp_cookie;abort=1;
     repeat(3)begin step();if(!rsp_valid||rsp_words!==held||rsp_cookie!==hc)$fatal(1,"late fault altered payload");end
    end
    17:begin ia0=0;ic0=1;end
   endcase
   expect_stop(caseid);
  end
  // Complete on final allowed cycle wins over timeout.
  reset();launch();write0(0);write1(1);step();clear_events();write0(2);write1(3);step();clear_events();
  repeat(13)step();write0(4);write1(5);ap_done=1;ap_ready=1;step();clear_events();ap_idle=1;
  if(!rsp_valid||fault)$fatal(1,"completion/timeout boundary");
  $fdisplay(f,"END %0d %0d",perms,checks);$fclose(f);
  $display("ACCESS_MEMORY_CALL_PASS permutations=%0d fault_cases=%0d timeout_boundary=1",perms,checks);$finish;
 end
endmodule
