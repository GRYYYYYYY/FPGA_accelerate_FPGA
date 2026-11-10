`timescale 1ns/1ps
module tb_search_scheduler;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,abort=0,admit=1,backend_fault=0,backend_drained=1,active=1;
 reg[63:0]active_design=64'h1234;reg[31:0]active_version=3;reg[1:0]active_query=1;reg[3:0]active_price=3;
 reg start_valid=0,rsp_ready=0;wire start_ready,rsp_valid,busy,fault;wire[3:0]rsp_status,phase;
 reg[31:0]start_cookie=0,start_source=10,start_key=0,start_nodes=100,start_max_polls=10,start_poll_cookie=32'hc0000000;
 reg[63:0]start_design=64'h1234;reg[1:0]start_query=1;reg[3:0]start_price=3;reg[447:0]start_expand=0;
 wire[31:0]rsp_cookie,polls,expands,candidates,result_node,result_key;
 wire req_valid;reg req_ready=0;wire[3:0]req_lane;wire[447:0]req_payload;
 reg reply_valid=0;wire reply_ready;reg[255:0]reply_payload=0;
 reg candidate_valid=0,candidate_error=0;wire candidate_ready,poll_event;wire[31:0]poll_node,poll_key,poll_size;
 search_scheduler #(.MAX_CYCLES(200))dut(.*);
 integer cycles=0,mode=0,delay=0,reads=0,accepted=0,checks=0,events,commands=0;reg pending=0,sent_candidate=0;reg[3:0]lane;reg[447:0]packet;reg[255:0]response;reg[159:0]record;
 reg hold_request=0;reg saw_held=0;reg[447:0]held_request;string path;
 always @(posedge clk)begin
  cycles<=cycles+1;if(cycles>20000)$fatal(1,"unit watchdog");
  if(rst)begin req_ready<=0;reply_valid<=0;candidate_valid<=0;pending<=0;delay<=0;reads<=0;accepted<=0;sent_candidate<=0;saw_held<=0;end
  else begin
   req_ready<=!hold_request&&!pending&&!reply_valid&&cycles%3==0;
   if(req_valid&&!req_ready)begin
    if(saw_held&&req_payload!==held_request)$fatal(1,"request changed under stall");saw_held<=1;held_request<=req_payload;
   end else saw_held<=0;
   if(req_valid&&req_ready)begin
    if(pending||reply_valid)$fatal(1,"overlap");pending<=1;delay<=3;lane<=req_lane;packet<=req_payload;accepted<=accepted+1;sent_candidate<=0;
    $fdisplay(events,"REQ %0d %0d %0d %0112h",commands,cycles,req_lane,req_payload);
   end
   if(pending&&delay>0)delay<=delay-1;
   if(pending&&delay==1)begin
    response=0;
    if(lane==12)begin
     response[63:32]=packet[127:96];
     if(packet[31:0]==1)begin response[31:0]=(mode==1?2:0);response[95:64]=(mode==16?2:1);reads<=0;end
     else if(packet[31:0]==2)begin
      response[31:0]=(mode==2?1:0);if(mode==3)response[63:32]=packet[127:96]+1;
      response[159:128]=(reads==0?10:20);response[127:96]=(reads==0?0:32'h3f800000);response[95:64]=(mode==17?5:0);reads<=reads+1;
     end else if(packet[31:0]!=4)$fatal(1,"bad frontier operation");
    end else if(lane==8)begin
     record=0;record[31:0]=(packet[32:1]==10?0:32'h3f800000);record[127:96]=7;
     record[128]=(packet[32:1]==20||mode==6||mode==11);
     response[4]=(mode!=4);if(mode==5)record[31:0]=32'hdeadbeef;
     response[164:5]=record;
    end else if(lane==11)begin
     if(packet[95:64]!=10||packet[191:160]!=20||packet[255:224]!=7||packet[447:416]!=3)$fatal(1,"captured query/parent");
     response[35:4]=packet[63:32];response[3:0]=(mode==7?1:0);
    end else if(lane==6)response[3:0]=(mode==8?1:0);else $fatal(1,"bad lane");
    reply_payload<=response;reply_valid<=1;pending<=0;
   end
   if(reply_valid&&reply_ready)reply_valid<=0;
   if(pending&&lane==11&&!sent_candidate)begin candidate_valid<=1;candidate_error<=mode==15;end
   if(candidate_valid&&candidate_ready)begin candidate_valid<=0;sent_candidate<=1;end
  end
 end
 task defaults;begin
  abort=0;backend_fault=0;active_version=3;backend_drained=1;hold_request=0;
  start_source=10;start_key=0;start_nodes=100;start_max_polls=10;start_expand=0;start_expand[31:0]=9;start_expand[63:32]=100;start_expand[191:160]=20;start_expand[255:224]=7;start_expand[447:416]=3;
 end endtask
 task reset_case;begin @(negedge clk);rst=1;defaults;repeat(3)@(negedge clk);rst=0;end endtask
 task launch(input integer m);begin
  mode=m;commands=commands+1;start_cookie=commands;
  if(mode==11)start_expand[191:160]=10;
  if(mode==12)start_max_polls=1;
  if(mode==14)start_nodes=0;
  @(negedge clk);start_valid=1;do @(posedge clk);while(!start_ready);@(negedge clk);start_valid=0;
  // Frontend input reuse cannot change the accepted command.
  start_expand=~start_expand;start_source=99;start_key=32'habcdef01;
 end endtask
 task finish(input integer status);reg[31:0]held_polls,held_expands;begin
  wait(rsp_valid);@(negedge clk);
  if(rsp_status!=status||rsp_cookie!=commands||fault!=(status!=0&&status!=1))$fatal(1,"result mode=%0d got=%0d expected=%0d fault=%b",mode,rsp_status,status,fault);
  held_polls=polls;held_expands=expands;
  repeat(5)begin @(negedge clk);if(!rsp_valid||!busy||start_ready||req_valid||rsp_status!=status||polls!=held_polls||expands!=held_expands)$fatal(1,"held completion");end
  $fdisplay(events,"DONE %0d %0d %0d %0d %0d %0d %0d",commands,mode,status,polls,expands,candidates,accepted);
  rsp_ready=1;@(negedge clk);rsp_ready=0;checks=checks+1;
 end endtask
 initial begin
  if(!$value$plusargs("events=%s",path))$fatal(1,"events");events=$fopen(path,"w");
  reset_case;launch(0);finish(0);defaults;launch(0);finish(0); // same instance reusable on success
  for(integer n=1;n<=8;n=n+1)begin reset_case;launch(n);finish(n==1||n==3?4:n==2?3:n==4||n==5?5:n==6?6:7);end
  reset_case;hold_request=1;launch(9);wait(req_valid);repeat(4)@(negedge clk);abort=1;repeat(5)begin @(negedge clk);if(!req_valid||rsp_valid)$fatal(1,"cancel withdrew offered request");end
  hold_request=0;finish(8);
  reset_case;hold_request=1;launch(10);repeat(205)@(negedge clk);if(!req_valid||rsp_valid||!fault)$fatal(1,"timeout containment");hold_request=0;finish(10);
  reset_case;launch(11);finish(0);if(expands!=0||polls!=1)$fatal(1,"source equals sink");
  reset_case;launch(12);finish(2);if(polls!=1||expands!=1)$fatal(1,"poll bound");
  reset_case;launch(13);wait(req_valid);@(negedge clk);active_version=4;finish(8);
  reset_case;launch(14);finish(1);if(accepted!=0)$fatal(1,"invalid metadata side effect");
  reset_case;launch(15);finish(9);
  reset_case;launch(16);finish(4);
  reset_case;launch(17);finish(0); // target with remaining frontier issues CLEAR then CHECKPOINT
  reset_case;backend_drained=0;launch(0);wait(phase==3);repeat(8)begin @(negedge clk);if(rsp_valid||!busy)$fatal(1,"completion before drain");end
  backend_drained=1;finish(0);
  $fclose(events);$display("SEARCH_SCHEDULER_PASS checks=%0d",checks);$finish;
 end
endmodule
