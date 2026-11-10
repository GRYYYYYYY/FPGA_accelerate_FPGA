`timescale 1ns/1ps
module tb_checkpoint_authority;
reg clk=0;always #5 clk=~clk;
reg rst=1,abort=0,cfg_permit=0,cfg_valid=0,cfg_rsp_ready=0,rearm_valid=0,req_valid=0,rsp_ready=0;
reg[63:0]cfg_design=0,cfg_generation=0,cfg_primary=0,cfg_pool=0,cfg_allocator=0;
reg[31:0]cfg_checkpoint=0,cfg_nodes=0,cfg_nets=0,cfg_capacity=0;
wire cfg_ready,rearm_ready,cfg_rsp_valid,cfg_rearmed,configured,req_ready,rsp_valid,busy,fault,drained;wire[2:0]cfg_status;wire[3:0]rsp_status;
wire[63:0]bound_design,bound_generation,rsp_design,rsp_generation;wire[31:0]bound_checkpoint,rsp_checkpoint,rsp_cookie,rsp_refs,rsp_occupancy;
reg[63:0]req_design=0,req_generation=0;reg[31:0]req_checkpoint=0,req_node=0,req_net=0,req_cookie=0;
wire[63:0]m_araddr,m_awaddr;wire[7:0]m_arlen,m_awlen;wire[2:0]m_arsize,m_awsize;wire[1:0]m_arburst,m_awburst;wire[3:0]m_arid,m_awid,m_rid,m_bid;
wire m_arvalid,m_arready,m_rvalid,m_rready,m_rlast,m_awvalid,m_awready,m_wvalid,m_wready,m_wlast,m_bvalid,m_bready;
wire[511:0]m_rdata,m_wdata;wire[63:0]m_wstrb;wire[1:0]m_rresp,m_bresp;
checkpoint_authority_reader dut(.*);
reg allow_ar=1,inject_r=0;wire agent_arready;
assign m_arready=allow_ar&&agent_arready;
reg[63:0]primary_base,pool_base,allocator_base,primary_bytes,pool_bytes,D=64'h123456789abcdef0,G;
reg[31:0]N,C,CP;integer reads,writes,rbeats,wbeats,bresponses;
axi_file_memory #(.ADDR_BITS(64),.READ_ONLY(1),.MAX_BEATS(1),.TAG("snapshot")) memory(
.clk(clk),.rst(rst),.base0(primary_base),.base1(pool_base),.base2(allocator_base),.size0(primary_bytes),.size1(pool_bytes),.size2(64'd64),
.araddr(m_araddr),.arlen(m_arlen),.arsize(m_arsize),.arburst(m_arburst),.arid(m_arid),.arvalid(m_arvalid&&allow_ar),.arready(agent_arready),.rdata(m_rdata),.rid(m_rid),.rresp(m_rresp),.rlast(m_rlast),.rvalid(m_rvalid),.rready(m_rready),
.awaddr(m_awaddr),.awlen(m_awlen),.awsize(m_awsize),.awburst(m_awburst),.awid(m_awid),.awvalid(m_awvalid),.awready(m_awready),.wdata(m_wdata),.wstrb(m_wstrb),.wlast(m_wlast),.wvalid(m_wvalid),.wready(m_wready),.bid(m_bid),.bresp(m_bresp),.bvalid(m_bvalid),.bready(m_bready),
.inject_r(inject_r),.inject_b(1'b0),.*);
integer fd,events,rc,id,node,net,status,refs,occ,wanted_reads,before_reads,checks=0,cfg_checks=0,cycles=0;reg[63:0]vd,vg;reg[31:0]vcp;
string path;reg ar_held=0;reg[63:0]held_ar;reg prior_drained=0,prior_rsp=0,prior_core_busy=0;reg[2:0]prior_state=0;
always @(posedge clk)begin
 cycles<=cycles+1;if(cycles>10000000)$fatal(1,"watchdog state=%0d store=%0d",dut.state,dut.store.state);
 if(!rst)begin
  if(m_awvalid||m_wvalid||writes||wbeats||bresponses)$fatal(1,"checkpoint snapshot write offered");
  if(ar_held&&(!m_arvalid||m_araddr!==held_ar))$fatal(1,"snapshot AR retracted/changed");
  if(dut.state==1&&prior_state!=1)begin
   if(!prior_drained||prior_rsp||prior_core_busy)$fatal(1,"private rearm reset before retirement");
   $fdisplay(events,"RESET %0d %0d %016h",cycles,cfg_checks,bound_generation);
  end
  if(req_valid&&req_ready)$fdisplay(events,"A %0d %0d %0d %0d %016h %0d %016h",cycles,req_cookie,req_node,req_net,req_design,req_checkpoint,req_generation);
  if(rearm_valid&&rearm_ready)$fdisplay(events,"ARM %0d %016h",cycles,bound_generation);
 end
 ar_held<=!rst&&m_arvalid&&!m_arready;held_ar<=m_araddr;prior_drained<=drained;prior_rsp<=rsp_valid;prior_core_busy<=dut.c_busy;prior_state<=dut.state;
end
task cfg_result(input integer expected,input integer rearmed);reg[3:0]hold;begin
 wait(cfg_rsp_valid);@(negedge clk);if(cfg_status!=expected||cfg_rearmed!=rearmed)$fatal(1,"config result %0d/%0d",cfg_status,expected);
 hold={cfg_status,cfg_rearmed};repeat(7)begin @(negedge clk);if(!cfg_rsp_valid||cfg_ready||req_ready||{cfg_status,cfg_rearmed}!==hold)$fatal(1,"held config response");end
 $fdisplay(events,"CFG %0d %0d %0d %0d %016h %0d %016h",cycles,cfg_checks,cfg_status,cfg_rearmed,bound_design,bound_checkpoint,bound_generation);cfg_checks=cfg_checks+1;
 cfg_rsp_ready=1;@(negedge clk);cfg_rsp_ready=0;repeat(2)@(negedge clk);
end endtask
task install(input integer expected);begin
 @(negedge clk);cfg_valid=1;do @(posedge clk);while(!cfg_ready);@(negedge clk);cfg_valid=0;
 // Descriptor pins may immediately move to the next host transaction.
 cfg_design=~cfg_design;cfg_generation=~cfg_generation;cfg_primary=~cfg_primary;cfg_pool=~cfg_pool;cfg_allocator=~cfg_allocator;cfg_nodes=~cfg_nodes;cfg_capacity=~cfg_capacity;
 cfg_result(expected,0);
end endtask
task send(input integer cookie,n,p,input[63:0]d,input[31:0]cp,input[63:0]g);begin
 @(negedge clk);req_cookie=cookie;req_node=n;req_net=p;req_design=d;req_checkpoint=cp;req_generation=g;req_valid=1;
 do @(posedge clk);while(!req_ready);@(negedge clk);req_valid=0;
 req_design=~req_design;req_generation=~req_generation;req_node=~req_node;req_net=~req_net;req_cookie=~req_cookie;req_checkpoint=~req_checkpoint;
end endtask
task result(input integer cookie,st,count,occupancy,nreads,input integer arm);reg[259:0]hold;begin
 wait(rsp_valid);@(negedge clk);
 if(rsp_status!=st||rsp_cookie!=cookie||rsp_refs!=count||rsp_occupancy!=occupancy||rsp_design!==D||rsp_checkpoint!=CP||rsp_generation!==G||!drained||reads-before_reads!=nreads)$fatal(1,"authority result cookie=%0d status=%0d/%0d refs=%0d/%0d occ=%0d/%0d reads=%0d/%0d",cookie,rsp_status,st,rsp_refs,count,rsp_occupancy,occupancy,reads-before_reads,nreads);
 hold={rsp_status,rsp_design,rsp_generation,rsp_checkpoint,rsp_cookie,rsp_refs,rsp_occupancy};
 if(arm)begin rearm_valid=1;cfg_permit=1;end
 repeat(8)begin @(negedge clk);if(!rsp_valid||req_ready||rearm_ready||!drained||dut.core_rst||{rsp_status,rsp_design,rsp_generation,rsp_checkpoint,rsp_cookie,rsp_refs,rsp_occupancy}!==hold)$fatal(1,"authority held completion changed/early reset");end
 $fdisplay(events,"R %0d %0d %0d %0d %0d %0d %016h %0d %016h",cycles,cookie,rsp_status,rsp_refs,rsp_occupancy,reads-before_reads,rsp_design,rsp_checkpoint,rsp_generation);checks=checks+1;
 rsp_ready=1;@(negedge clk);rsp_ready=0;
 if(arm)begin do @(posedge clk);while(!rearm_ready);@(negedge clk);rearm_valid=0;cfg_result(0,1);cfg_permit=0;end
 repeat(2)@(negedge clk);
end endtask
initial begin
 if(!$value$plusargs("nodes=%d",N)||!$value$plusargs("capacity=%d",C)||!$value$plusargs("checkpoint=%d",CP)||!$value$plusargs("generation=%h",G)||!$value$plusargs("primary=%h",primary_base)||!$value$plusargs("pool=%h",pool_base)||!$value$plusargs("allocator=%h",allocator_base)||!$value$plusargs("primarybytes=%d",primary_bytes)||!$value$plusargs("poolbytes=%d",pool_bytes))$fatal(1,"snapshot layout args");
 if(!$value$plusargs("vectors=%s",path))$fatal(1,"vectors path");fd=$fopen(path,"r");if(!$value$plusargs("events=%s",path))$fatal(1,"events path");events=$fopen(path,"w");
 repeat(5)@(negedge clk);rst=0;repeat(3)@(negedge clk);if(req_ready||configured)$fatal(1,"unbound authority admitted read");
 cfg_design=0;cfg_generation=G;cfg_checkpoint=CP;cfg_nodes=N;cfg_nets=27960;cfg_capacity=C;cfg_primary=primary_base;cfg_pool=pool_base;cfg_allocator=allocator_base;cfg_valid=1;
 repeat(5)begin @(negedge clk);if(cfg_ready||cfg_rsp_valid)$fatal(1,"configuration accepted without lease");end
 cfg_permit=1;do @(posedge clk);while(!cfg_ready);@(negedge clk);cfg_valid=0;cfg_result(1,0);
 cfg_design=D;cfg_generation=G;cfg_checkpoint=CP;cfg_nodes=N;cfg_nets=27960;cfg_capacity=C;cfg_primary=primary_base+1;cfg_pool=pool_base;cfg_allocator=allocator_base;install(2);
 if(configured||!fault||reads)$fatal(1,"invalid layout bound/read memory");
 cfg_design=D;cfg_generation=G;cfg_checkpoint=CP;cfg_nodes=N;cfg_nets=27960;cfg_capacity=C;cfg_primary=primary_base;cfg_pool=pool_base;cfg_allocator=allocator_base;
 @(negedge clk);cfg_valid=1;do @(posedge clk);while(!cfg_ready);@(negedge clk);cfg_valid=0;cfg_permit=0;cfg_result(3,0);
 if(configured||!fault||reads)$fatal(1,"cancelled bind published");cfg_permit=1;
 cfg_design=D;cfg_generation=G;cfg_checkpoint=CP;cfg_nodes=N;cfg_nets=27960;cfg_capacity=C;cfg_primary=primary_base;cfg_pool=pool_base;cfg_allocator=allocator_base;install(0);
 if(!configured||bound_design!==D||bound_generation!==G||bound_checkpoint!=CP||reads)$fatal(1,"descriptor bind failed");
 cfg_design=D;cfg_generation=G+1;cfg_checkpoint=CP+1;cfg_nodes=N;cfg_nets=27960;cfg_capacity=C;cfg_primary=primary_base;cfg_pool=pool_base;cfg_allocator=allocator_base;install(1);
 if(!configured||bound_generation!==G||bound_checkpoint!=CP||reads)$fatal(1,"immutable descriptor remapped");cfg_permit=0;
 while(!$feof(fd))begin
  rc=$fscanf(fd,"%d %d %d %h %d %h %d %d %d %d\n",id,node,net,vd,vcp,vg,status,refs,occ,wanted_reads);if(rc!=10)$fatal(1,"vector format");
  before_reads=reads;send(id,node,net,vd,vcp,vg);result(id,status,refs,occ,wanted_reads,0);
 end
 // Real SLVERR on an actual immutable allocator read. Old completion must retire
 // before a private service reset; descriptor and snapshot generation survive.
 before_reads=reads;inject_r=1;send(32'h70000000,0,0,D,CP,G);result(32'h70000000,9,0,0,1,1);inject_r=0;
 before_reads=reads;send(32'h70000001,0,0,D,CP,G); // Expected row0 is supplied by first vector below.
 rc=$fseek(fd,0,0);rc=$fscanf(fd,"%d %d %d %h %d %h %d %d %d %d\n",id,node,net,vd,vcp,vg,status,refs,occ,wanted_reads);
 if(node!=0||net!=0)$fatal(1,"first vector must cover node0/net0");result(32'h70000001,0,refs,occ,wanted_reads,0);
 before_reads=reads;allow_ar=0;send(32'h70000002,0,0,D,CP,G);wait(m_arvalid);@(negedge clk);abort=1;cfg_permit=1;rearm_valid=1;
 repeat(6)begin @(negedge clk);if(!m_arvalid||rsp_valid||drained||rearm_ready)$fatal(1,"cancel withdrew exposed read or replied early");end
 allow_ar=1;@(negedge clk);abort=0;result(32'h70000002,12,0,0,1,1);
 before_reads=reads;send(32'h70000003,0,0,D,CP,G);result(32'h70000003,0,refs,occ,wanted_reads,0);
 if(fault||!configured||busy||!drained||writes||wbeats||bresponses)$fatal(1,"authority final state");
 $fflush(events);$fclose(events);$display("CHECKPOINT_AUTHORITY_PASS checks=%0d cfg=%0d reads=%0d writes=%0d cycles=%0d",checks,cfg_checks,reads,writes,cycles);$finish;
end
endmodule
