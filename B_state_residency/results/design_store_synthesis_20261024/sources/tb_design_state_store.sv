`timescale 1ns/1ps
module tb_design_state_store;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,cfg_valid=0,cfg_rsp_ready=0,req_valid=0,rsp_ready=0;
 reg[63:0]cfg_base=64'h31fffff000;reg[31:0]cfg_nodes=9089009;
 wire cfg_ready,cfg_rsp_valid,configured,req_ready,rsp_valid,fault;wire[2:0]cfg_status;
 reg[2:0]req_op=0;reg[31:0]req_cookie=0,req_owner=0,req_node=0,req_arg=0;
 wire[3:0]rsp_status;wire[31:0]rsp_cookie,rsp_flags,rsp_count,rsp_mask;
 wire claim_active;wire[31:0]claim_owner,claim_node,claim_count,claim_mask;
 wire[63:0]m_araddr,m_awaddr;wire[7:0]m_arlen,m_awlen;wire[2:0]m_arsize,m_awsize;wire[1:0]m_arburst,m_awburst;wire[3:0]m_arid,m_awid;
 wire m_arvalid,m_rready,m_awvalid,m_wvalid,m_wlast,m_bready;
 wire[511:0]m_wdata;wire[63:0]m_wstrb;
 reg[511:0]m_rdata=0;reg[3:0]m_rid=0,m_bid=0;reg[1:0]m_rresp=0,m_bresp=0;reg m_rlast=1,m_rvalid=0,m_bvalid=0;
 reg[31:0]rng=32'hb17c2491;reg rp=0,aw=0,wd=0,bp=0;integer rd_delay=0,b_delay=0;
 wire m_arready=!rst&&!rp&&(rng[2:0]!=0);
 wire m_awready=!rst&&!aw&&!bp&&(rng[4:2]<3);
 wire m_wready=!rst&&!wd&&!bp&&(rng[8:6]>3);
 design_state_store dut(.*);
 integer fd_mem,fd_vec,fd_trace,k,rc,nread,relative,cycles=0,ars=0,aws=0,ws=0,bs=0,rs=0,normal=0,checks=0,configs=0,faults=0,awfirst=0,wfirst=0,simultaneous=0;
 integer req_ar=0,req_aw=0,inj=0,limit=0,fault_mode=0;
 reg[7:0]bytes[0:63];reg[511:0]data,write_data;reg[63:0]write_addr,write_strb;
 string memory,vectors,trace;
 reg log_enabled=0;
 reg ar_stalled=0,aw_stalled=0,w_stalled=0;reg[63:0]held_ar,held_aw,held_strb;reg[511:0]held_w;
 always @(posedge clk)begin
  cycles<=cycles+1;rng<={rng[30:0],rng[31]^rng[21]^rng[1]^rng[0]};
  if(cycles>30000000)$fatal(1,"watchdog");
  if(rst)begin
   rp<=0;aw<=0;wd<=0;bp<=0;rd_delay<=0;b_delay<=0;m_rvalid<=0;m_bvalid<=0;m_rid<=0;m_rresp<=0;m_rlast<=1;m_bid<=0;m_bresp<=0;
   ar_stalled<=0;aw_stalled<=0;w_stalled<=0;
  end else begin
   if(!fault)begin
    if(ar_stalled&&(!m_arvalid||m_araddr!==held_ar))$fatal(1,"AR stability");
    if(aw_stalled&&(!m_awvalid||m_awaddr!==held_aw))$fatal(1,"AW stability");
    if(w_stalled&&(!m_wvalid||m_wdata!==held_w||m_wstrb!==held_strb))$fatal(1,"W stability");
   end
   ar_stalled<=m_arvalid&&!m_arready;held_ar<=m_araddr;aw_stalled<=m_awvalid&&!m_awready;held_aw<=m_awaddr;
   w_stalled<=m_wvalid&&!m_wready;held_w<=m_wdata;held_strb<=m_wstrb;
   if(m_arvalid&&m_arready)begin
    if(rp||m_araddr[5:0]!==0||m_arlen!==0||m_arsize!==6||m_arburst!==1||m_arid!==0||m_araddr<cfg_base||m_araddr>=cfg_base+((64'd16*cfg_nodes+63)&~64'd63))$fatal(1,"AR shape/range");
    if(m_araddr!==cfg_base+((req_node/4)*64))$fatal(1,"AR record address");
    relative=m_araddr-cfg_base;rc=$fseek(fd_mem,relative,0);if(rc!=0)$fatal(1,"seek read");nread=$fread(bytes,fd_mem);if(nread!=64)$fatal(1,"short backing");
    data=0;for(k=0;k<64;k=k+1)data[k*8+:8]=bytes[k];
    m_rid<=0;m_rresp<=0;m_rlast<=1;
    case(inj)
     1:m_rresp<=2;2:m_rid<=1;3:m_rlast<=0;
     4:data[(req_node%4)*128+:32]=16;
     5:data[(req_node%4)*128+96+:32]=1;
     6:begin data[(req_node%4)*128+:32]=4;data[(req_node%4)*128+32+:32]=33;end
     7:begin data[(req_node%4)*128+:32]=4;data[(req_node%4)*128+32+:32]=1;data[(req_node%4)*128+64+:32]=2;end
     8:begin data[(req_node%4)*128+:32]=0;data[(req_node%4)*128+64+:32]=1;end
     10:begin data[(req_node%4)*128+:32]=4;data[(req_node%4)*128+32+:32]=0;data[(req_node%4)*128+64+:32]=0;end
    endcase
    if(log_enabled)$fdisplay(fd_trace,"A %0d %016h %0128h",req_cookie,m_araddr,data);
    m_rdata<=data;rp<=1;rd_delay<=rng[14:11];ars=ars+1;req_ar=req_ar+1;
   end
   if(rp&&!m_rvalid)begin if(rd_delay==0)m_rvalid<=1;else rd_delay<=rd_delay-1;end
   if(m_rvalid&&m_rready)begin rp<=0;m_rvalid<=0;rs=rs+1;end
   if(m_awvalid&&m_awready)begin
    if(aw||bp||m_awlen!==0||m_awsize!==6||m_awburst!==1||m_awid!==0||m_awaddr!==cfg_base+((req_node/4)*64))$fatal(1,"AW shape/address");
    aw<=1;write_addr<=m_awaddr;aws=aws+1;req_aw=req_aw+1;
    if(!wd&&!(m_wvalid&&m_wready))awfirst=awfirst+1;
    if(m_wvalid&&m_wready)simultaneous=simultaneous+1;
   end
   if(m_wvalid&&m_wready)begin
    if(wd||bp||!m_wlast||m_wstrb!==(64'hffff<<((req_node%4)*16)))$fatal(1,"W shape/strobes");
    wd<=1;write_data<=m_wdata;write_strb<=m_wstrb;ws=ws+1;
    if(!aw&&!(m_awvalid&&m_awready))wfirst=wfirst+1;
   end
   if(aw&&wd&&!bp)begin
    relative=write_addr-cfg_base;
    for(k=0;k<64;k=k+1)if(write_strb[k])begin rc=$fseek(fd_mem,relative+k,0);if(rc!=0)$fatal(1,"seek write");$fwrite(fd_mem,"%c",write_data[k*8+:8]);end
    $fflush(fd_mem);
    if(log_enabled)$fdisplay(fd_trace,"W %0d %016h %016h %0128h",req_cookie,write_addr,write_strb,write_data);
    bp<=1;b_delay<=rng[18:15];m_bid<=inj==12?1:0;m_bresp<=inj==11?2:0;
   end
   if(bp&&!m_bvalid)begin if(b_delay==0)m_bvalid<=1;else b_delay<=b_delay-1;end
   if(m_bvalid&&m_bready)begin if(log_enabled)$fdisplay(fd_trace,"B %0d %0d %0d",req_cookie,m_bid,m_bresp);bp<=0;aw<=0;wd<=0;m_bvalid<=0;bs=bs+1;end
   if(req_op==5&&(aw||wd||bp)&&!m_bvalid&&(!claim_active||rsp_valid))$fatal(1,"publication acknowledged before B");
  end
 end
 task reset;
  begin @(negedge clk);rst=1;req_valid=0;cfg_valid=0;rsp_ready=0;cfg_rsp_ready=0;inj=0;repeat(4)@(negedge clk);rst=0;@(negedge clk);if(fault||configured||claim_active||rsp_valid)$fatal(1,"reset");end
 endtask
 task configure_store(input integer expected);
  begin
   @(negedge clk);cfg_valid=1;wait(cfg_ready);@(posedge clk);@(negedge clk);cfg_valid=0;wait(cfg_rsp_valid);@(negedge clk);
   if(cfg_status!==expected||configured!==(expected==0))$fatal(1,"configure_store %d/%d",cfg_status,expected);
   repeat(3)begin @(negedge clk);if(!cfg_rsp_valid||cfg_status!==expected||req_ready)$fatal(1,"cfg backpressure");end
   cfg_rsp_ready=1;@(negedge clk);cfg_rsp_ready=0;configs=configs+1;
  end
 endtask
 task start(input integer op,node,arg,input[31:0]owner);
  begin @(negedge clk);req_op=op;req_node=node;req_arg=arg;req_owner=owner;req_cookie=req_cookie+1;req_ar=0;req_aw=0;req_valid=1;wait(req_ready);@(posedge clk);@(negedge clk);req_valid=0;end
 endtask
 task finish_response(input integer status,input[31:0]flags,count,mask,input integer fault_expected);
  reg[131:0]held;
  begin
   wait(rsp_valid);@(negedge clk);
   if(rsp_status!==status||rsp_cookie!==req_cookie||rsp_flags!==flags||rsp_count!==count||rsp_mask!==mask||fault!==fault_expected)
    $fatal(1,"response cmd=%0d op=%0d node=%0d status=%0d/%0d flags=%h/%h count=%d/%d mask=%h/%h fault=%b/%0d",req_cookie,req_op,req_node,rsp_status,status,rsp_flags,flags,rsp_count,count,rsp_mask,mask,fault,fault_expected);
   held={rsp_status,rsp_cookie,rsp_flags,rsp_count,rsp_mask};
   repeat(3)begin @(negedge clk);if(!rsp_valid||{rsp_status,rsp_cookie,rsp_flags,rsp_count,rsp_mask}!==held||req_ready)$fatal(1,"reply stability");end
   if(log_enabled)$fdisplay(fd_trace,"R %0d %0d %0d %0d %0d %0d %0d %0d %0d %0d",req_cookie,rsp_status,rsp_flags,rsp_count,rsp_mask,claim_active,claim_owner,claim_node,claim_count,claim_mask);
   rsp_ready=1;@(negedge clk);rsp_ready=0;checks=checks+1;
  end
 endtask
 integer op,node,arg,status,expected_ar,expected_aw,active,mode,t,j;
 reg[31:0]owner,flags,count,mask,cowner,cnode,ccount,cmask;
 reg[131:0]held_late;
 initial begin
  if(!$value$plusargs("memory=%s",memory)||!$value$plusargs("vectors=%s",vectors)||!$value$plusargs("trace=%s",trace))$fatal(1,"args");
  rc=$value$plusargs("limit=%d",limit);rc=$value$plusargs("faults=%d",fault_mode);
  fd_mem=$fopen(memory,"r+b");fd_vec=$fopen(vectors,"r");fd_trace=$fopen(trace,"w");if(!fd_mem||!fd_vec||!fd_trace)$fatal(1,"open");
  reset();start(0,0,0,0);finish_response(1,0,0,0,0);if(req_ar||req_aw)$fatal(1,"unconfigured AXI");
  cfg_base=1;configure_store(1);cfg_base=64'h31fffff000;cfg_nodes=0;configure_store(2);cfg_nodes=32'h1000001;configure_store(2);
  cfg_nodes=9089009;cfg_base=64'hffffffffffffffc0;configure_store(2);cfg_nodes=1;configure_store(0);
  reset();cfg_base=64'h31fffff000;cfg_nodes=9089009;configure_store(0);
  if(!fault_mode)begin
   log_enabled=1;
   while(!$feof(fd_vec)&&(limit==0||normal<limit))begin
    rc=$fscanf(fd_vec,"%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d\n",op,node,arg,owner,status,flags,count,mask,active,cowner,cnode,ccount,cmask,expected_ar,expected_aw);
    if(rc!=15)$fatal(1,"parse %0d",rc);
    start(op,node,arg,owner);finish_response(status,flags,count,mask,0);
    if({claim_active,claim_owner,claim_node,claim_count,claim_mask}!=={active[0],cowner,cnode,ccount,cmask}||req_ar!=expected_ar||req_aw!=expected_aw)$fatal(1,"claim/traffic cmd=%0d",req_cookie);
    normal=normal+1;
   end
   log_enabled=0;
   if(limit==0)begin
    // All commands retired, coordinated cold reset does not erase external design state.
    reset();configure_store(0);start(0,node,0,0);finish_response(0,flags,count,mask,0);
    if(claim_active||req_ar!=1||req_aw!=0)$fatal(1,"persistent cold read");
   end
  end else begin
   for(mode=1;mode<=8;mode=mode+1)begin
    reset();configure_store(0);start(1,100+mode,1,77);finish_response(0,0,0,0,0);
    inj=mode;start(0,100+mode,0,77);finish_response(mode<=3?5:6,0,0,0,1);
    if(!claim_active||claim_owner!=77||req_ready||m_awvalid||m_wvalid)$fatal(1,"read fault claim");faults=faults+1;
   end
   for(mode=11;mode<=12;mode=mode+1)for(t=0;t<2;t=t+1)begin
    reset();configure_store(0);node=200+mode*4+t;start(1,node,1,77);finish_response(0,0,0,0,0);
    start(4,node,0,77);finish_response(0,0,1,1,0);
    inj=mode;start(t==0?2:5,node,0,77);finish_response(5,0,0,0,1);
    if(!claim_active||claim_mask!=1||req_ready||req_aw!=1)$fatal(1,"B fault lost claim");faults=faults+1;
   end
   // Valid cache with mismatched graph count, then unexpected valid before publish.
   reset();configure_store(0);start(1,300,0,77);finish_response(0,0,0,0,0);start(5,300,0,77);finish_response(0,4,0,0,0);
   start(1,300,1,88);finish_response(6,0,0,0,1);faults=faults+1;
   reset();configure_store(0);start(1,301,0,77);finish_response(0,0,0,0,0);inj=10;start(5,301,0,77);finish_response(6,0,0,0,1);
   if(!claim_active||req_aw!=0)$fatal(1,"foreign publication");faults=faults+1;
   for(j=0;j<2;j=j+1)begin
    reset();configure_store(0);@(negedge clk);if(j==0)force m_rvalid=1;else force m_bvalid=1;
    @(negedge clk);if(!fault||rsp_valid||req_ready||m_arvalid||m_awvalid)$fatal(1,"unowned response");release m_rvalid;release m_bvalid;faults=faults+1;
   end
   reset();configure_store(0);start(0,500,0,0);wait(rsp_valid);@(negedge clk);held_late={rsp_status,rsp_cookie,rsp_flags,rsp_count,rsp_mask};force m_bvalid=1;
   repeat(3)begin @(negedge clk);if(!fault||!rsp_valid||{rsp_status,rsp_cookie,rsp_flags,rsp_count,rsp_mask}!==held_late)$fatal(1,"late fault");end
   release m_bvalid;faults=faults+1;reset();configure_store(0);start(0,500,0,0);finish_response(0,0,0,0,0);
  end
  if(ars!=rs||aws!=ws||aws!=bs)$fatal(1,"transaction conservation");
  $fflush(fd_mem);$fclose(fd_mem);$fclose(fd_trace);
  $display("DESIGN_STORE_PASS commands=%0d checks=%0d configurations=%0d faults=%0d AR=%0d R=%0d AW=%0d W=%0d B=%0d awfirst=%0d wfirst=%0d simultaneous=%0d cycles=%0d",normal,checks,configs,faults,ars,rs,aws,ws,bs,awfirst,wfirst,simultaneous,cycles);$finish;
 end
endmodule
