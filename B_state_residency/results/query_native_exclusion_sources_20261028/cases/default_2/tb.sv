`timescale 1ns/1ps
module tb_query_lifecycle;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,abort=0,admit=1,backend_fault=0,backend_drained=1,active=1,host_label_edit=0;
 reg[63:0]active_design=64'h1234;reg[31:0]active_version=3;reg[1:0]active_query=1;reg[3:0]active_price=3;reg[1:0]route_slots=0;
 reg cmd_valid=0,cmd_slot=0;wire cmd_ready;reg[31:0]cmd_cookie=0,cmd_route_cookie=100,cmd_source=10,cmd_key=0,cmd_nodes=32,cmd_max_polls=10,cmd_poll_cookie=200;
 reg[63:0]cmd_design=64'h1234;reg[1:0]cmd_query=1;reg[3:0]cmd_price=3;reg[447:0]cmd_expand=0;
 wire rsp_valid;reg rsp_ready=0;wire[3:0]rsp_status,rsp_detail;wire[31:0]rsp_cookie,rsp_nodes,rsp_acked,prepare_acked,cleanup_acked;wire rsp_committed,busy,fault,prepared_event;wire[3:0]phase;
 wire service_valid,service_ready;wire[3:0]service_lane;wire[447:0]service_payload;reg service_rsp_valid=0;wire service_rsp_ready;reg[255:0]service_rsp_payload=0;
 wire search_valid,search_ready,search_abort;wire[31:0]search_cookie,search_source,search_key,search_nodes,search_max_polls,search_poll_cookie;wire[63:0]search_design;wire[1:0]search_query;wire[3:0]search_price;wire[447:0]search_expand;
 reg search_rsp_valid=0;wire search_rsp_ready;reg[3:0]search_status=0;reg[31:0]search_rsp_cookie=0,search_result_node=0;
 wire route_valid,route_ready;wire[191:0]route_payload;reg route_rsp_valid=0;wire route_rsp_ready;reg[3:0]route_status=0;reg[31:0]route_rsp_cookie=0,route_nodes=0,route_acked=0;

 integer cycles=0,commands=0,checks=0,mode=0,service_count=0,searches=0,routes=0,events;
 reg service_hold=0,search_hold=0,route_hold=0;integer sd=0,qd=0,rd=0;reg[3:0]lane;reg[447:0]packet;reg[191:0]route_packet;
 reg[159:0]labels[0:31];reg[255:0]response;reg[3:0]status;reg[31:0]node,seq,sink,source;string path;
 reg sh=0,qh=0,rh=0;reg[451:0]sp;reg[447:0]qp;reg[191:0]rp;

 localparam EARLY=2;
 reg injected=0;integer injected_count=0,observed_cycles=0;
 wire early_service=!rst&&!injected&&EARLY==1&&service_valid&&service_ready;
 wire early_search=!rst&&!injected&&EARLY==2&&search_valid&&search_ready;
 wire early_route=!rst&&!injected&&EARLY==3&&route_valid&&route_ready;
 always @(posedge clk)begin
  if(!rst)begin
   observed_cycles<=observed_cycles+1;
   if(EARLY==0&&((service_ready&&service_rsp_valid)!==1'b0||(search_ready&&search_rsp_valid)!==1'b0||(route_ready&&route_rsp_valid)!==1'b0))$fatal(1,"native pair overlap or unknown");
   if(early_service||early_search||early_route)begin
    injected<=1;injected_count<=injected_count+1;
    $fdisplay(events,"EARLY %0d %0d",EARLY,cycles);
   end
  end
 end
 query_lifecycle #(.MAX_CYCLES(300))dut(.cp_rebase(1'b0),.cp_rebase_permit(1'b0),.cp_source_version(32'd0),.cp_source_query(2'd0),.cp_source_price(4'd0),
 .active_generation(64'd1),.cp_valid(1'b0),.cp_restore(1'b0),.cp_safe(1'b0),.cp_ready(),.cp_busy(),
 .cp_expected_crc(32'd0),.cp_rsp_valid(),.cp_rsp_ready(1'b0),.cp_status(),.cp_crc(),
 .cp_s_valid(1'b0),.cp_s_ready(),.cp_s_index(32'd0),.cp_s_data(32'd0),.cp_s_last(1'b0),
 .cp_m_valid(),.cp_m_ready(1'b0),.cp_m_index(),.cp_m_data(),.cp_m_last(),
 .service_rsp_valid(service_rsp_valid||early_service),
 .search_rsp_valid(search_rsp_valid||early_search),
 .route_rsp_valid(route_rsp_valid||early_route),.*);

 assign service_ready=!service_hold&&sd==0&&!service_rsp_valid&&cycles%3==0;
 assign search_ready=!search_hold&&qd==0&&!search_rsp_valid&&cycles%3==0;
 assign route_ready=!route_hold&&rd==0&&!route_rsp_valid&&cycles%3==0;
 always @(posedge clk)begin
  cycles<=cycles+1;if(cycles>30000)$fatal(1,"watchdog");
  if(rst)begin
   sd<=0;qd<=0;rd<=0;service_rsp_valid<=0;search_rsp_valid<=0;route_rsp_valid<=0;service_count<=0;searches<=0;routes<=0;route_slots<=0;sh<=0;qh<=0;rh<=0;
   for(integer i=0;i<32;i=i+1)labels[i]<={32'd0,32'd99,32'hffffffff,32'h40000000,32'h40400000};
  end else begin
   if(service_valid&&!service_ready)begin if(sh&&{service_lane,service_payload}!==sp)$fatal(1,"service request changed");sp<={service_lane,service_payload};sh<=1;end else sh<=0;
   if(search_valid&&!search_ready)begin if(qh&&search_expand!==qp)$fatal(1,"search descriptor changed");qp<=search_expand;qh<=1;end else qh<=0;
   if(route_valid&&!route_ready)begin if(rh&&route_payload!==rp)$fatal(1,"route request changed");rp<=route_payload;rh<=1;end else rh<=0;
   if(service_valid&&service_ready)begin sd<=3;packet<=service_payload;lane<=service_lane;service_count<=service_count+1;$fdisplay(events,"IO %0d %0d %0d %0112h",commands,cycles,service_lane,service_payload);end
   if(sd>0)sd<=sd-1;
   if(sd==1)begin
    response=0;status=0;node=packet[32:1];
    if(lane==8)begin
     if(packet[0])begin
      if(mode==5&&packet[67:65]==0)status=2;
      if(mode==12&&packet[67:65]==4&&packet[64:33]==0)status=2;
      if(status==0)labels[node][packet[67:65]*32+:32]=packet[64:33];
     end
     response[4]=mode!=3;response[164:5]=labels[node];if(mode==4&&!packet[0])response[100:69]=0;
    end else if(lane==6)begin if(mode==13)status=2;end else $fatal(1,"unexpected service lane");
    response[3:0]=status;service_rsp_payload<=response;service_rsp_valid<=1;
   end
   if(service_rsp_valid&&service_rsp_ready)service_rsp_valid<=0;
   if(search_valid&&search_ready)begin
    if(search_source!=source||search_expand[191:160]!=sink||search_expand[255:224]!=seq||search_expand[447:416]!=3||search_design!=64'h1234)$fatal(1,"captured search descriptor");
    if(labels[source][31:0]!=0||labels[source][63:32]!=0||labels[source][127:96]!=seq||!labels[sink][128])$fatal(1,"search before prepare");
    qd<=5;search_rsp_cookie<=search_cookie+(mode==7?1:0);search_result_node<=sink+(mode==8?1:0);search_status<=mode==6?3:0;searches<=searches+1;
    $fdisplay(events,"SEARCH %0d %0d %0d %0d",commands,source,sink,seq);
   end
   if(qd>0)begin qd<=qd-1;if(search_abort)search_status<=8;end
   if(qd==1)search_rsp_valid<=1;
   if(search_rsp_valid&&search_rsp_ready)search_rsp_valid<=0;
   if(route_valid&&route_ready)begin
    if(route_payload[65:34]!=source||route_payload[97:66]!=sink||route_payload[161:130]!=seq||route_payload[0])$fatal(1,"captured route descriptor");
    if(!labels[sink][128])$fatal(1,"cleared target before route");rd<=5;route_packet<=route_payload;routes<=routes+1;$fdisplay(events,"ROUTE %0d %048h",commands,route_payload);
   end
   if(rd>0)rd<=rd-1;
   if(rd==1)begin
    route_rsp_valid<=1;route_rsp_cookie<=route_packet[33:2]+(mode==10?1:0);route_status<=mode==9?5:0;route_nodes<=source==sink?0:6;route_acked<=mode==9?2:mode==11?5:source==sink?0:6;
    if(mode!=9&&mode!=10)route_slots[route_packet[1]]<=1;
   end
   if(route_rsp_valid&&route_rsp_ready)route_rsp_valid<=0;
  end
 end
 task defaults;begin
  abort=0;backend_fault=0;backend_drained=1;active_version=3;host_label_edit=0;service_hold=0;search_hold=0;route_hold=0;
  source=10;sink=20;seq=7;cmd_slot=0;cmd_source=10;cmd_key=0;cmd_nodes=32;cmd_max_polls=10;cmd_design=64'h1234;cmd_expand=0;cmd_expand[31:0]=9;cmd_expand[63:32]=100;cmd_expand[191:160]=20;cmd_expand[223:192]=5;cmd_expand[255:224]=7;cmd_expand[447:416]=3;
 end endtask
 task reset_case;begin @(negedge clk);rst=1;defaults;repeat(3)@(negedge clk);rst=0;end endtask
 task launch(input integer n);begin
  mode=n;commands=commands+1;cmd_cookie=commands;cmd_route_cookie=100+commands;
  @(negedge clk);cmd_valid=1;do @(posedge clk);while(!cmd_ready);@(negedge clk);cmd_valid=0;
  cmd_source=31;cmd_expand=~cmd_expand;cmd_route_cookie=32'hdeadbeef; // accepted descriptor immutable
 end endtask
 task finish(input integer status,input integer committed);begin
  wait(rsp_valid);@(negedge clk);
  if(rsp_status!=status||rsp_cookie!=commands||rsp_committed!=committed||fault!=(status!=0&&status!=1))$fatal(1,"result mode=%0d status=%0d expected=%0d committed=%b",mode,rsp_status,status,rsp_committed);
  repeat(5)begin @(negedge clk);if(!rsp_valid||!busy||cmd_ready||service_valid||search_valid||route_valid||rsp_status!=status)$fatal(1,"held completion");end
  if(status==0&&(!rsp_committed||prepare_acked!=4||cleanup_acked!=1||labels[sink][128]))$fatal(1,"success before lifecycle complete");
  $fdisplay(events,"DONE %0d %0d %0d %0d %0d %0d %0d %0d %0d %0d %0d",commands,mode,status,rsp_committed,prepare_acked,cleanup_acked,rsp_nodes,rsp_acked,service_count,searches,routes);
  rsp_ready=1;@(negedge clk);rsp_ready=0;checks=checks+1;
 end endtask
 initial begin
  if(!$value$plusargs("events=%s",path))$fatal(1,"events");events=$fopen(path,"w");
  reset_case;launch(0);finish(0,1);
  if(injected_count!=1)$fatal(1,"missing unique overlap injection");
  $fdisplay(events,"MONITOR %0d %0d",observed_cycles,injected_count);$fclose(events);$display("QUERY_LIFECYCLE_PASS checks=%0d",checks);$finish;
 end
endmodule
