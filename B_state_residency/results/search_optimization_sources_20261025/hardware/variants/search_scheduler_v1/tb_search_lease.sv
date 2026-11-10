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
 integer cycles=0,mode=0,delay=0,reads=0,accepted=0,checks=0,events,commands=0;reg pending=0,sent_candidate=0;reg[3:0]lane;reg[447:0]packet;reg[255:0]response;reg[159:0]record;
 reg hold_request=0;reg saw_held=0;reg[447:0]held_request;string path;
wire c_req_valid;
wire c_req_ready;
wire [3:0] c_req_lane;
wire [447:0] c_req_payload;
wire c_reply_valid;
wire c_reply_ready;
wire [255:0] c_reply_payload;
wire lease_admit,lease_cancel;wire[15:0]hv=busy?16'hffff:16'd0;wire[15:0]hr,hrv,sv,sr,srv,srr;
 wire[38911:0]sp;wire[4095:0]srp,hrp;wire route_ready,recover_ready,route_valid,recover_valid,out_consume;
 wire recover_intent=mode==9&&abort;
 assign req_valid=sv[c_req_lane];assign req_lane=c_req_lane;assign req_payload=sp[c_req_lane*2432+:448];assign reply_ready=srr[c_req_lane];
 generate for(genvar i=0;i<16;i=i+1)begin:fake_backend
  assign sr[i]=i==c_req_lane&&req_ready;assign srv[i]=i==c_req_lane&&reply_valid;
  assign srp[i*256+:256]=reply_payload;
 end endgenerate
 search_host_fence lease(.search_busy(busy),.search_fault(fault),.start_valid(start_valid),.system_admit(admit),
 .h_valid(hv),.h_ready(hr),.h_payload({38912{1'b1}}),.h_rsp_valid(hrv),.h_rsp_ready(16'hffff),.h_rsp_payload(hrp),
 .h_route_valid(busy),.h_route_ready(route_ready),.h_recover_valid(recover_intent),.h_recover_ready(recover_ready),.h_out_ready(1'b0),
 .s_valid(sv),.s_ready(sr),.s_payload(sp),.s_rsp_valid(srv),.s_rsp_ready(srr),.s_rsp_payload(srp),
 .s_route_valid(route_valid),.s_route_ready(1'b1),.s_recover_valid(recover_valid),.s_recover_ready(1'b1),.s_out_ready(out_consume),
 .c_valid(c_req_valid),.c_ready(c_req_ready),.c_lane(c_req_lane),.c_payload(c_req_payload),
 .c_rsp_valid(c_reply_valid),.c_rsp_ready(c_reply_ready),.c_rsp_payload(c_reply_payload),.c_candidate_ready(candidate_ready),.admit(lease_admit),.cancel(lease_cancel));
 always @(posedge clk)if(!rst&&busy)begin
  if(hr||hrv||route_ready||route_valid||recover_ready||recover_valid)$fatal(1,"query lease leaked host/recovery");
  if(sv!=(c_req_valid?(16'b1<<c_req_lane):16'b0))$fatal(1,"unexpected host acceptance");
  if(out_consume!=candidate_ready)$fatal(1,"candidate ownership");
 end
 search_scheduler #(.MAX_CYCLES(200))dut(.clk(clk),.rst(rst),.abort(mode==9?lease_cancel:abort),.admit(lease_admit),.backend_fault(backend_fault),.backend_drained(backend_drained),.active(active),.active_design(active_design),.active_version(active_version),.active_query(active_query),.active_price(active_price),.start_valid(start_valid),.start_ready(start_ready),.start_cookie(start_cookie),.start_source(start_source),.start_key(start_key),.start_nodes(start_nodes),.start_max_polls(start_max_polls),.start_poll_cookie(start_poll_cookie),.start_design(start_design),.start_query(start_query),.start_price(start_price),.start_expand(start_expand),.rsp_valid(rsp_valid),.rsp_ready(rsp_ready),.rsp_status(rsp_status),.rsp_cookie(rsp_cookie),.polls(polls),.expands(expands),.candidates(candidates),.result_node(result_node),.result_key(result_key),.busy(busy),.fault(fault),.phase(phase),.req_valid(c_req_valid),.req_ready(c_req_ready),.req_lane(c_req_lane),.req_payload(c_req_payload),.reply_valid(c_reply_valid),.reply_ready(c_reply_ready),.reply_payload(c_reply_payload),.candidate_valid(candidate_valid),.candidate_ready(candidate_ready),.candidate_error(candidate_error),.poll_event(poll_event),.poll_node(poll_node),.poll_key(poll_key),.poll_size(poll_size));

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
  if(!recover_ready||!recover_valid||hr||route_ready||start_ready)$fatal(1,"recovery handoff after consumed completion");
  $fdisplay(events,"RECOVERY %0d",commands);
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
