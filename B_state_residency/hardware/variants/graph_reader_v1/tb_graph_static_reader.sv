`timescale 1ns/1ps
module tb_graph_static_reader;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,cfg_valid=0,cfg_rsp_ready=0,req_valid=0,rsp_ready=0;
 wire cfg_ready,cfg_rsp_valid,configured,req_ready,rsp_valid,fault;
 reg [63:0] cfg_offsets_base=64'h1fffff000,cfg_edges_base=64'h10fffff000,cfg_attrs_base=64'h20fffff000;
 reg [31:0] cfg_nodes=9089009,cfg_edges=40469536;
 wire [2:0] cfg_status;reg[1:0]req_op=0;reg[31:0]req_cookie=0,req_node=0,req_index=0;
 wire[3:0]rsp_status;wire[31:0]rsp_cookie,rsp_parent,rsp_index,rsp_node,rsp_start,rsp_count;wire[255:0]rsp_attrs;
 wire[63:0]m_araddr;wire[7:0]m_arlen;wire[2:0]m_arsize;wire[1:0]m_arburst;wire[3:0]m_arid;wire m_arvalid,m_rready;
 reg[511:0]m_rdata=0;reg[3:0]m_rid=0;reg[1:0]m_rresp=0;reg m_rlast=1,m_rvalid=0;
 reg[31:0]rng=32'hbea15231;
 reg pending=0;integer latency=0;
 wire m_arready=!rst&&!pending&&!m_rvalid&&(rng[2:0]!=0);
 graph_static_reader dut(.*);
 integer fd_offsets,fd_edges,fd_attrs,fd_vectors,fd_trace,rc,k,which,relative,nread,fd;
 reg[7:0]bytes[0:63];reg[511:0]data;
 string graph,vectors,trace;
 integer cycles=0,ars=0,rs=0,checks=0,normal=0,faultcases=0,configcases=0,blocked=0,kind_at_ar;
 integer inj=0,inj_beat=1,request_beats=0;
 reg check_addresses=0;
 reg[63:0]expected_addr[0:3];integer expected_beats;
 // Fault modes: 1 RRESP, 2 RID, 3 RLAST, 4 descending offsets,
 // 5 last>E, 6 first sentinel, 7 last sentinel, 8 invalid child.
 always @(posedge clk)begin
  cycles<=cycles+1;rng<={rng[30:0],rng[31]^rng[21]^rng[1]^rng[0]};
  if(cycles>20000000)$fatal(1,"global watchdog");
  if(rst)begin pending<=0;m_rvalid<=0;latency<=0;m_rdata<=0;m_rid<=0;m_rresp<=0;m_rlast<=1;end
  else begin
   if(m_arvalid&&!m_arready)blocked=blocked+1;
   if(m_arvalid&&m_arready)begin
    if(pending||m_arlen!==0||m_arsize!==6||m_arburst!==1||m_arid!==0||m_araddr[5:0]!==0)$fatal(1,"AR shape/ownership");
    if(check_addresses&&(request_beats>=expected_beats||m_araddr!==expected_addr[request_beats]))$fatal(1,"AR address request=%0d beat=%0d got=%h expected=%h",normal,request_beats,m_araddr,expected_addr[request_beats]);
    if(m_araddr>=cfg_offsets_base&&m_araddr<cfg_offsets_base+((64'd4*(cfg_nodes+64'd1)+63)&~64'd63))begin fd=fd_offsets;relative=m_araddr-cfg_offsets_base;which=0;end
    else if(m_araddr>=cfg_edges_base&&m_araddr<cfg_edges_base+((64'd4*cfg_edges+63)&~64'd63))begin fd=fd_edges;relative=m_araddr-cfg_edges_base;which=1;end
    else if(m_araddr>=cfg_attrs_base&&m_araddr<cfg_attrs_base+((64'd32*cfg_nodes+63)&~64'd63))begin fd=fd_attrs;relative=m_araddr-cfg_attrs_base;which=2;end
    else $fatal(1,"out of range AR %h",m_araddr);
    for(k=0;k<64;k=k+1)bytes[k]=0;
    rc=$fseek(fd,relative,0);if(rc!=0)$fatal(1,"fseek");nread=$fread(bytes,fd);
    if(nread<=0)$fatal(1,"empty read");
    data=0;for(k=0;k<64;k=k+1)data[k*8+:8]=bytes[k];
    request_beats=request_beats+1;ars=ars+1;
    m_rid<=0;m_rresp<=0;m_rlast<=1;
    if(request_beats==inj_beat)begin
     case(inj)
      1:m_rresp<=2;2:m_rid<=1;3:m_rlast<=0;
      4:begin data[(req_node%16)*32+:32]=2;data[(req_node%16+1)*32+:32]=1;end
      5:data[(req_node%16+1)*32+:32]=cfg_edges+1;
      6:data[31:0]=1;
      7:data[((req_node+1)%16)*32+:32]=cfg_edges-1;
      8:data[((dut.start_offset+req_index)%16)*32+:32]=cfg_nodes;
     endcase
    end
    if(check_addresses)$fdisplay(fd_trace,"A %0d %016h",req_cookie,m_araddr);
    m_rdata<=data;pending<=1;latency<=rng[6:3];
   end
   if(pending&&!m_rvalid)begin
    if(latency==0)m_rvalid<=1;else latency<=latency-1;
   end
   if(m_rvalid&&m_rready)begin m_rvalid<=0;pending<=0;rs=rs+1;end
  end
 end
 task reset;
  begin
   @(negedge clk);rst=1;req_valid=0;rsp_ready=0;cfg_valid=0;cfg_rsp_ready=0;check_addresses=0;inj=0;
   repeat(4)@(negedge clk);rst=0;@(negedge clk);
   if(fault||configured||rsp_valid)$fatal(1,"reset");
  end
 endtask
 task configure(input integer expected);
  reg[2:0]held;
  begin
   @(negedge clk);cfg_valid=1;wait(cfg_ready);@(posedge clk);@(negedge clk);cfg_valid=0;
   wait(cfg_rsp_valid);@(negedge clk);held=cfg_status;
   if(cfg_status!==expected||configured!==(expected==0))$fatal(1,"config status got=%d want=%d",cfg_status,expected);
   repeat(3)begin @(negedge clk);if(!cfg_rsp_valid||cfg_status!==held||req_ready)$fatal(1,"config backpressure");end
   cfg_rsp_ready=1;@(negedge clk);cfg_rsp_ready=0;configcases=configcases+1;
  end
 endtask
 task start(input integer op,node,index);
  begin
   @(negedge clk);req_op=op;req_node=node;req_index=index;req_cookie=req_cookie+1;request_beats=0;req_valid=1;
   wait(req_ready);@(posedge clk);@(negedge clk);req_valid=0;
  end
 endtask
 task finish_response(input integer status,target,first,count,input[255:0]attrs,input integer fault_expected);
  reg[483:0]held;
  begin
   wait(rsp_valid);@(negedge clk);
   if(rsp_status!==status||rsp_cookie!==req_cookie||rsp_parent!==req_node||rsp_index!==req_index||rsp_node!==target||rsp_start!==first||rsp_count!==count||rsp_attrs!==attrs||fault!==fault_expected)
    $fatal(1,"reply cookie=%0d status=%0d/%0d node=%0d/%0d start=%0d/%0d count=%0d/%0d attr=%h/%h fault=%b/%0d",req_cookie,rsp_status,status,rsp_node,target,rsp_start,first,rsp_count,count,rsp_attrs,attrs,fault,fault_expected);
   held={rsp_status,rsp_cookie,rsp_parent,rsp_index,rsp_node,rsp_start,rsp_count,rsp_attrs};
   repeat(3)begin @(negedge clk);if(!rsp_valid||{rsp_status,rsp_cookie,rsp_parent,rsp_index,rsp_node,rsp_start,rsp_count,rsp_attrs}!==held||req_ready)$fatal(1,"reply instability");end
   if(check_addresses)begin
    if(request_beats!=expected_beats)$fatal(1,"AR count");
    $fdisplay(fd_trace,"R %0d %0d %0d %0d %0d %064h",req_cookie,rsp_status,rsp_node,rsp_start,rsp_count,rsp_attrs);
   end
   rsp_ready=1;@(negedge clk);rsp_ready=0;checks=checks+1;
  end
 endtask
 task restore_config;
  begin
   cfg_offsets_base=64'h1fffff000;cfg_edges_base=64'h10fffff000;cfg_attrs_base=64'h20fffff000;cfg_nodes=9089009;cfg_edges=40469536;
  end
 endtask
 integer op,node,index,status,target,first,count,mode,beat,old_ar,limit;
 reg[255:0]attrs;reg[483:0]held_late;
 initial begin
  if(!$value$plusargs("graph=%s",graph)||!$value$plusargs("vectors=%s",vectors)||!$value$plusargs("trace=%s",trace))$fatal(1,"arguments");
  if(!$value$plusargs("limit=%d",limit))limit=0;
  fd_offsets=$fopen({graph,"/offsets.u32le"},"rb");fd_edges=$fopen({graph,"/edges.u32le"},"rb");fd_attrs=$fopen({graph,"/nodes.rrt32"},"rb");fd_vectors=$fopen(vectors,"r");fd_trace=$fopen(trace,"w");
  if(!fd_offsets||!fd_edges||!fd_attrs||!fd_vectors||!fd_trace)$fatal(1,"open");
  reset();start(0,0,0);finish_response(1,0,0,0,0,0);if(request_beats!=0)$fatal(1,"unconfigured read");
  cfg_offsets_base=64'h1fffff001;configure(1);restore_config();cfg_nodes=0;configure(2);restore_config();cfg_nodes=32'h1000001;configure(2);
  restore_config();cfg_attrs_base=64'hffffffffffffffc0;configure(2);
  restore_config();cfg_edges_base=cfg_offsets_base;configure(3);
  restore_config();cfg_attrs_base=cfg_offsets_base+64;configure(3);
  // Last physical byte 2^64-1 is legal, zero-sized edge table may overlap.
  restore_config();cfg_nodes=1;cfg_edges=0;cfg_attrs_base=64'hffffffffffffffc0;cfg_edges_base=cfg_offsets_base;configure(0);
  reset();restore_config();configure(0);
  cfg_valid=1;repeat(3)begin @(negedge clk);if(cfg_ready)$fatal(1,"configuration must lock");end;cfg_valid=0;
  start(2,0,0);finish_response(2,0,0,0,0,0);if(request_beats!=0)$fatal(1,"bad op AR");
  start(0,cfg_nodes,0);finish_response(2,0,0,0,0,0);if(request_beats!=0)$fatal(1,"bad node AR");
  start(0,0,1);finish_response(2,0,0,0,0,0);if(request_beats!=0)$fatal(1,"bad index AR");
  while(!$feof(fd_vectors)&&(limit==0||normal<limit))begin
   rc=$fscanf(fd_vectors,"%d %d %d %d %d %d %d %h %d %h %h %h %h\n",op,node,index,status,target,first,count,attrs,expected_beats,expected_addr[0],expected_addr[1],expected_addr[2],expected_addr[3]);
   if(rc!=13)$fatal(1,"vector parse %0d",rc);
   check_addresses=1;start(op,node,index);finish_response(status,target,first,count,attrs,0);normal=normal+1;
  end
  check_addresses=0;
  // Exercise each AXI phase using node95 (cross-line offsets). Its child0 exists in real image.
  for(mode=1;mode<=3;mode=mode+1)for(beat=1;beat<=4;beat=beat+1)begin
   reset();restore_config();configure(0);inj=mode;inj_beat=beat;
   start(1,95,0);finish_response(3,0,0,0,0,1);
   if(request_beats!=beat||req_ready||cfg_ready||m_arvalid)$fatal(1,"fault did not stop");faultcases=faultcases+1;
  end
  for(mode=4;mode<=8;mode=mode+1)begin
   reset();restore_config();configure(0);inj=mode;inj_beat=(mode==8)?2:1;
   start(mode==8?1:0,mode==6?0:mode==7?9089008:mode==8?9:1,0);finish_response(4,0,0,0,0,1);
   if(req_ready||cfg_ready||m_arvalid)$fatal(1,"corrupt image did not stop");faultcases=faultcases+1;
  end
  // Unsolicited R without an owner: no invented response, block future work.
  reset();restore_config();configure(0);@(negedge clk);force m_rvalid=1;
  @(negedge clk);if(!fault||req_ready||rsp_valid||m_arvalid)$fatal(1,"unsolicited R");release m_rvalid;faultcases=faultcases+1;
  // Fault while a successful response is held must not mutate already offered payload.
  reset();restore_config();configure(0);start(0,0,0);wait(rsp_valid);@(negedge clk);
  held_late={rsp_status,rsp_cookie,rsp_parent,rsp_index,rsp_node,rsp_start,rsp_count,rsp_attrs};force m_rvalid=1;
  repeat(3)begin @(negedge clk);if(!fault||!rsp_valid||{rsp_status,rsp_cookie,rsp_parent,rsp_index,rsp_node,rsp_start,rsp_count,rsp_attrs}!==held_late)$fatal(1,"late fault reply");end
  release m_rvalid;rsp_ready=1;@(negedge clk);rsp_ready=0;faultcases=faultcases+1;
  reset();restore_config();configure(0);start(0,0,1);finish_response(2,0,0,0,0,0);
  if(ars!=rs)$fatal(1,"AR/R conservation %0d/%0d",ars,rs);
  $fclose(fd_trace);$display("GRAPH_READER_PASS queries=%0d checks=%0d configurations=%0d faults=%0d AR=%0d R=%0d blocked=%0d cycles=%0d",normal,checks,configcases,faultcases,ars,rs,blocked,cycles);$finish;
 end
endmodule
