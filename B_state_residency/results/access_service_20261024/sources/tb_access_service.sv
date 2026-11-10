`timescale 1ns/1ps
module tb_access_service;
reg clk=0;always #5 clk=~clk;
reg  rst=0;
reg  abort=0;
reg  enable=0;
reg  active=0;
reg [1:0] active_query=0;
reg [3:0] active_price=0;
reg  req_valid=0;
wire  req_ready;
reg [447:0] req_config=0;
reg [31:0] req_cookie=0;
reg [31:0] req_parent=0;
reg [31:0] req_child=0;
reg [31:0] req_sink=0;
reg [31:0] req_net=0;
reg [1:0] req_query=0;
reg [3:0] req_price=0;
wire  rsp_valid;
reg  rsp_ready=0;
wire [3:0] rsp_status;
wire [31:0] rsp_cookie;
wire [31:0] rsp_parent;
wire [31:0] rsp_child;
wire [31:0] rsp_sink;
wire [31:0] rsp_net;
wire [31:0] rsp_bits;
wire [31:0] rsp_action;
wire [31:0] rsp_steps;
wire [31:0] rsp_services;
wire [1:0] rsp_query;
wire [3:0] rsp_price;
wire  busy;
wire  fault;
wire  svc_valid;
reg  svc_ready=0;
wire [3:0] svc_kind;
wire [4:0] svc_phase;
wire [31:0] svc_node;
wire [31:0] svc_net;
wire [31:0] svc_cookie;
wire [1:0] svc_query;
wire [3:0] svc_price;
reg  svc_rsp_valid=0;
wire  svc_rsp_ready;
reg [3:0] svc_rsp_status=0;
reg [3:0] svc_rsp_kind=0;
reg [4:0] svc_rsp_phase=0;
reg [31:0] svc_rsp_node=0;
reg [31:0] svc_rsp_net=0;
reg [31:0] svc_rsp_cookie=0;
reg [31:0] svc_rsp_value=0;
reg [1:0] svc_rsp_query=0;
reg [3:0] svc_rsp_price=0;
reg  svc_fault=0;
access_service dut(.*);
 integer fd,logfd,rc,i,row,case_id,saved_case,cases=0,steps=0,services=0,cycles=0,case_steps,case_services;
 integer allowed=0,skipped=0,lookahead=0,early=0,pruned=0;
 reg[31:0]ins[0:19],outs[0:5];reg[639:0]expected_input;reg[191:0]expected_output;
 reg[31:0]last_token=0,expected_node,value,kind,phase,final_bits,final_action;
 reg[142:0]svc_held;reg[329:0]rsp_held;
 wire[142:0]svc_bundle={svc_kind,svc_phase,svc_node,svc_net,svc_cookie,svc_query,svc_price};
 wire[329:0]rsp_bundle={rsp_status,rsp_cookie,rsp_parent,rsp_child,rsp_sink,rsp_net,rsp_bits,rsp_action,rsp_steps,rsp_services,rsp_query,rsp_price};
 always @(posedge clk)begin
  cycles<=cycles+1;if(cycles>10000000)$fatal(1,"watchdog");
  if(!rst)begin
   if(fault)$fatal(1,"access fault case=%0d state=%0d status=%0d kfault=%b",saved_case,dut.controller.state,rsp_status,dut.k_fault);
   if(busy&&req_ready)$fatal(1,"overlap admitted");
   if(dut.k_req_valid&&dut.k_req_ready)begin
    if(dut.k_req_words!==expected_input)$fatal(1,"state snapshot case=%0d row=%0d expected=%h actual=%h",saved_case,row,expected_input,dut.k_req_words);
    if(dut.k_req_cookie<=last_token)$fatal(1,"kernel token reuse");last_token=dut.k_req_cookie;
   end
   if(svc_valid&&svc_ready)begin if(svc_cookie<=last_token)$fatal(1,"service token reuse");last_token=svc_cookie;end
  end
 end
 task read_row;
 begin
  rc=$fscanf(fd,"%d %d",row,case_id);if(rc!=2)$fatal(1,"header parse");
  for(i=0;i<20;i=i+1)begin rc=$fscanf(fd,"%h",ins[i]);if(rc!=1)$fatal(1,"input parse");expected_input[i*32+:32]=ins[i];end
  for(i=0;i<6;i=i+1)begin rc=$fscanf(fd,"%h",outs[i]);if(rc!=1)$fatal(1,"output parse");expected_output[i*32+:32]=outs[i];end
  rc=$fscanf(fd,"\n");
 end endtask
 initial begin
  fd=$fopen("vectors.txt","r");logfd=$fopen("observed.txt","w");if(!fd||!logfd)$fatal(1,"open");
  rst=1;enable=1;active=1;active_query=1;active_price=3;repeat(5)@(negedge clk);rst=0;
  while(!$feof(fd))begin
   read_row;if(ins[0]!=0||case_id!=cases)$fatal(1,"start row");saved_case=case_id;case_steps=0;case_services=0;
   @(negedge clk);req_valid=1;req_cookie=case_id+100;req_config=expected_input[639:192];req_parent=0;req_child=1;req_sink=2;req_net=0;req_query=1;req_price=3;
   wait(req_ready);@(posedge clk);@(negedge clk);req_valid=0;req_config=~req_config;req_cookie=32'hbad;req_parent=31;req_child=32;req_sink=33;req_net=34;
   begin:decision
    while(1)begin
     wait(dut.k_rsp_valid);@(negedge clk);
     if(dut.k_rsp_words!==expected_output||dut.k_rsp_status)$fatal(1,"HLS step row=%0d expected=%h actual=%h",row,expected_output,dut.k_rsp_words);
     $fdisplay(logfd,"K %0d %0d %048h",row,saved_case,dut.k_rsp_words);steps=steps+1;case_steps=case_steps+1;
     kind=outs[4];phase=outs[1];final_bits=outs[2];final_action=outs[5];
     expected_node=kind==8?2:kind==9?0:kind==10?outs[3]:1;
     if(kind==0)disable decision;
     read_row;if(case_id!=saved_case||ins[0]!=1)$fatal(1,"advance row");value=ins[5];
     wait(svc_valid);@(negedge clk);
     if(svc_kind!==kind[3:0]||svc_phase!==phase[4:0]||svc_node!==expected_node||svc_net||svc_query!=1||svc_price!=3)$fatal(1,"service mapping case=%0d kind=%0d/%0d node=%0d/%0d",saved_case,svc_kind,kind,svc_node,expected_node);
     svc_held=svc_bundle;repeat(2)begin @(negedge clk);if(!svc_valid||svc_bundle!==svc_held)$fatal(1,"service unstable");end
     svc_rsp_kind=svc_kind;svc_rsp_phase=svc_phase;svc_rsp_node=svc_node;svc_rsp_net=svc_net;svc_rsp_cookie=svc_cookie;svc_rsp_query=svc_query;svc_rsp_price=svc_price;
     svc_ready=1;@(negedge clk);svc_ready=0;repeat(3)@(negedge clk);svc_rsp_status=0;svc_rsp_value=value;svc_rsp_valid=1;
     wait(svc_rsp_ready);@(posedge clk);@(negedge clk);svc_rsp_valid=0;services=services+1;case_services=case_services+1;
     $fdisplay(logfd,"S %0d %0d %0d %0d %0d %0d %08h",saved_case,kind,phase,expected_node,0,svc_rsp_cookie,value);
    end
   end
   wait(rsp_valid);@(negedge clk);
   if(rsp_status||rsp_cookie!=saved_case+100||rsp_parent||rsp_child!=1||rsp_sink!=2||rsp_net||rsp_query!=1||rsp_price!=3||rsp_bits!=final_bits||rsp_action!=final_action||rsp_steps!=case_steps||rsp_services!=case_services)$fatal(1,"decision result case=%0d",saved_case);
   rsp_held=rsp_bundle;repeat(3)begin @(negedge clk);if(!rsp_valid||rsp_bundle!==rsp_held)$fatal(1,"result unstable");end
   $fdisplay(logfd,"D %0d %0d %0d %0d %0d",saved_case,rsp_bits,rsp_action,rsp_steps,rsp_services);
   allowed=allowed+(rsp_action!=0);skipped=skipped+(rsp_action==0);lookahead=lookahead+(rsp_action==2);early=early+((rsp_bits&4)!=0);pruned=pruned+((rsp_bits&8)!=0);
   rsp_ready=1;@(negedge clk);rsp_ready=0;cases=cases+1;
  end
  $fclose(logfd);$display("ACCESS_SERVICE_PASS cases=%0d steps=%0d services=%0d allowed=%0d skipped=%0d lookahead=%0d early=%0d pruned=%0d cycles=%0d",cases,steps,services,allowed,skipped,lookahead,early,pruned,cycles);$finish;
 end

endmodule
