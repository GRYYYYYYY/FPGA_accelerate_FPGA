`timescale 1ns/1ps
module tb_cost_service_boundaries;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,abort=0,active=1,req_valid=0,rsp_ready=0;
 reg [1:0] active_query=2,req_query=2;reg [3:0] active_price=9,req_price=9;
 reg [735:0] req_words=0;reg [31:0] req_cookie=1;
 wire req_ready,rsp_valid,busy,fault;wire [159:0] rsp_words;
 wire [31:0] rsp_cookie;wire [1:0] rsp_query,rsp_status;wire [3:0] rsp_price;
 cost_service dut(.*);
 reg trst=1,tvalid=0;wire trdy,tv,tf;wire [159:0] tw;
 cost_service #(.MAX_CALL_CYCLES(8)) timed(
  .clk(clk),.rst(trst),.abort(1'b0),.active(1'b1),.active_query(2'd2),.active_price(4'd9),
  .req_valid(tvalid),.req_ready(trdy),.req_words(req_words),.req_cookie(32'd99),.req_query(2'd2),.req_price(4'd9),
  .rsp_valid(tv),.rsp_ready(1'b0),.rsp_words(tw),.rsp_cookie(),.rsp_query(),.rsp_price(),.rsp_status(),.busy(),.fault(tf));
 reg [159:0] golden,held;reg had_reply;integer offsets[0:10];
 integer f,rc,j,mode,k,checks=0,late=0,recovered=0,cycles=0,group,log;
 always @(posedge clk)begin cycles=cycles+1;if(cycles>200000)$fatal(1,"watchdog");end
 task reset;
 begin
  @(negedge clk);rst=1;abort=0;active=1;active_query=2;active_price=9;req_valid=0;rsp_ready=0;
  // Single rising edge resets wrapper and all actual arithmetic state together.
  @(posedge clk);@(negedge clk);rst=0;
  repeat(3)@(negedge clk);
  if(fault||rsp_valid||!req_ready)$fatal(1,"cold recovery");
 end endtask
 task send;
 begin
  @(negedge clk);req_valid=1;if(!req_ready)$fatal(1,"ready");
  @(posedge clk);#1;req_valid=0;
 end endtask
 task good;
 begin
  send();@(negedge clk);while(!rsp_valid)begin if(fault)$fatal(1,"recovery fault");@(negedge clk);end
  if(fault||rsp_words!==golden||rsp_cookie!==1||rsp_query!==2||rsp_price!==9||rsp_status!==0)$fatal(1,"recovery result");
  rsp_ready=1;@(posedge clk);#1;rsp_ready=0;recovered=recovered+1;
 end endtask
 initial begin
  f=$fopen("vectors.txt","r");log=$fopen("boundaries.txt","w");if(!f||!log)$fatal(1,"files");
  rc=$fscanf(f,"%d",group);
  for(j=0;j<23;j=j+1)rc=$fscanf(f,"%h",req_words[j*32+:32]);
  for(j=0;j<5;j=j+1)rc=$fscanf(f,"%h",golden[j*32+:32]);$fclose(f);
  offsets[0]=0;offsets[1]=1;offsets[2]=2;offsets[3]=20;offsets[4]=50;
  offsets[5]=100;offsets[6]=200;offsets[7]=400;offsets[8]=600;offsets[9]=680;offsets[10]=720;
  for(mode=0;mode<4;mode=mode+1)for(k=0;k<11;k=k+1)begin
   reset();send();repeat(offsets[k])@(posedge clk);@(negedge clk);
   had_reply=rsp_valid;held=rsp_words;if(had_reply)late=late+1;
   case(mode)0:abort=1;1:active_query=3;2:active_price=8;3:active=0;endcase
   @(posedge clk);#1;if(!fault||req_ready)$fatal(1,"external failure not detected mode=%0d",mode);
   @(negedge clk);abort=0;active_query=2;active_price=9;active=1;
   repeat(1030)begin
    @(negedge clk);
    if(!fault||req_ready||rsp_valid!==had_reply)$fatal(1,"fault leaked response");
    if(had_reply&&(rsp_words!==held||rsp_cookie!==1||rsp_query!==2||rsp_price!==9||rsp_status!==0))$fatal(1,"late fault payload");
   end
   if(had_reply)begin rsp_ready=1;@(posedge clk);#1;rsp_ready=0;@(negedge clk);if(rsp_valid||!fault||req_ready)$fatal(1,"fault retire");end
   checks=checks+1;$fdisplay(log,"FAULT %0d %0d %0d",mode,offsets[k],had_reply);
   reset();good();
  end
  @(negedge clk);trst=0;repeat(3)@(negedge clk);if(!trdy)$fatal(1,"timed ready");tvalid=1;
  @(posedge clk);#1;tvalid=0;repeat(12)@(negedge clk);
  if(!tf||tv||trdy)$fatal(1,"actual arithmetic timeout");
  repeat(1030)begin @(negedge clk);if(!tf||tv||trdy)$fatal(1,"timeout late leak");end
  checks=checks+1;$fdisplay(log,"TIMEOUT 8");$fdisplay(log,"END %0d %0d %0d",checks,late,recovered);$fclose(log);
  if(late==0||late==44)$fatal(1,"missing active/late cases");
  $display("COST_SERVICE_BOUNDARIES_PASS fault_cases=%0d late_cases=%0d recovered=%0d single_cycle_reset=1",checks,late,recovered);$finish;
 end
endmodule
