from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
BASE=HERE/'tb_checkpoint_authority.sv'
def make():
 s=BASE.read_text();s=s[:s.index('integer fd,events,')]
 s=s.replace('module tb_checkpoint_authority;','module tb_authority_recovery;').replace(',rearm_valid=0,req_valid=0,rsp_ready=0','')
 s=s.replace('wire cfg_ready,', 'wire rearm_valid,req_valid,rsp_ready;wire cfg_ready,')
 s=s.replace('reg[63:0]req_design=0,req_generation=0;reg[31:0]req_checkpoint=0,req_node=0,req_net=0,req_cookie=0;', 'wire[63:0]req_design,req_generation;wire[31:0]req_checkpoint,req_node,req_net,req_cookie;')
 s+='''
localparam[63:0]LB=64'ha1fffff000;
reg recovering=0,h_valid=0,h_rsp_ready=0;reg[2:0]h_op=0;reg[31:0]h_node=0,h_net=0,h_cookie=0;
wire h_ready,l_req_ready,l_rsp_valid,l_fault,l_busy,l_configured,l_cfg_ready,l_cfg_rsp_valid;wire[2:0]l_cfg_status;wire[3:0]l_status;wire[31:0]l_cookie,l_refs,l_occupancy;wire l_will;
wire[63:0]l_araddr,l_awaddr;wire[7:0]l_arlen,l_awlen;wire[2:0]l_arsize,l_awsize;wire[1:0]l_arburst,l_awburst;wire[3:0]l_arid,l_awid,l_rid,l_bid;
wire l_arvalid,l_arready,l_rvalid,l_rready,l_rlast,l_awvalid,l_awready,l_wvalid,l_wready,l_wlast,l_bvalid,l_bready;
wire[511:0]l_rdata,l_wdata;wire[63:0]l_wstrb;wire[1:0]l_rresp,l_bresp;
integer l_reads,l_writes,l_rbeats,l_wbeats,l_bresponses;
reg k_cfg_valid=0,k_cfg_rsp_ready=0,j_valid=0,recover_valid=0,k_rsp_ready=0;reg[31:0]j_node=0,j_net=0;reg[2:0]j_op=0;
reg[31:0]k_version=4,k_cookie=32'hcafe0001;reg[1:0]k_query=2;
wire k_cfg_ready,k_cfg_rsp_valid,k_cfg_status,j_ready,journal_full,permit_work,recover_ready,target_reset,reconfigure_valid,labels_valid,attempt_reset,k_rsp_valid,k_busy,k_fault;
wire[3:0]k_status;wire[31:0]k_rsp_cookie,k_corrected,journal_count,saved_checkpoint,new_version;wire[63:0]saved_design;wire[1:0]new_query;wire[3:0]new_price;
wire o_valid,o_ready,o_rsp_ready;wire[2:0]o_op;wire[31:0]o_node,o_net,o_cookie;
wire both_drained=drained&&l_reads==l_rbeats&&l_writes==l_bresponses&&l_wbeats==l_writes&&!l_arvalid&&!l_rvalid&&!l_awvalid&&!l_wvalid&&!l_bvalid;
wire retired=!busy&&!l_busy&&!cfg_rsp_valid&&!l_cfg_rsp_valid;
assign rearm_valid=attempt_reset;assign req_generation=G;assign h_ready=!recovering&&l_req_ready;assign o_ready=recovering&&l_req_ready;
owner_state_store live_store(.clk(clk),.rst(rst||target_reset),.abort(1'b0),.cfg_valid(!rst&&!target_reset&&!l_configured),.cfg_ready(l_cfg_ready),.cfg_primary(LB),.cfg_pool(LB+primary_bytes),.cfg_allocator(LB+primary_bytes+pool_bytes),.cfg_nodes(N),.cfg_capacity(C),.cfg_rsp_valid(l_cfg_rsp_valid),.cfg_rsp_ready(1'b1),.cfg_status(l_cfg_status),.configured(l_configured),
.req_valid(recovering?o_valid:h_valid),.req_ready(l_req_ready),.req_op(recovering?o_op:h_op),.req_cookie(recovering?o_cookie:h_cookie),.req_node(recovering?o_node:h_node),.req_net(recovering?o_net:h_net),.rsp_valid(l_rsp_valid),.rsp_ready(recovering?o_rsp_ready:h_rsp_ready),.rsp_status(l_status),.rsp_cookie(l_cookie),.rsp_count(l_refs),.rsp_occupancy(l_occupancy),.rsp_will_overuse(l_will),.fault(l_fault),.busy(l_busy),
.m_araddr(l_araddr),.m_arlen(l_arlen),.m_arsize(l_arsize),.m_arburst(l_arburst),.m_arid(l_arid),.m_arvalid(l_arvalid),.m_arready(l_arready),.m_rdata(l_rdata),.m_rid(l_rid),.m_rresp(l_rresp),.m_rlast(l_rlast),.m_rvalid(l_rvalid),.m_rready(l_rready),.m_awaddr(l_awaddr),.m_awlen(l_awlen),.m_awsize(l_awsize),.m_awburst(l_awburst),.m_awid(l_awid),.m_awvalid(l_awvalid),.m_awready(l_awready),.m_wdata(l_wdata),.m_wstrb(l_wstrb),.m_wlast(l_wlast),.m_wvalid(l_wvalid),.m_wready(l_wready),.m_bid(l_bid),.m_bresp(l_bresp),.m_bvalid(l_bvalid),.m_bready(l_bready));
axi_file_memory #(.ADDR_BITS(64),.READ_ONLY(0),.MAX_BEATS(1),.TAG("live")) live_memory(.clk(clk),.rst(rst),.base0(LB),.base1(64'd0),.base2(64'd0),.size0(primary_bytes+pool_bytes+64'd64),.size1(64'd0),.size2(64'd0),
.araddr(l_araddr),.arlen(l_arlen),.arsize(l_arsize),.arburst(l_arburst),.arid(l_arid),.arvalid(l_arvalid),.arready(l_arready),.rdata(l_rdata),.rid(l_rid),.rresp(l_rresp),.rlast(l_rlast),.rvalid(l_rvalid),.rready(l_rready),.awaddr(l_awaddr),.awlen(l_awlen),.awsize(l_awsize),.awburst(l_awburst),.awid(l_awid),.awvalid(l_awvalid),.awready(l_awready),.wdata(l_wdata),.wstrb(l_wstrb),.wlast(l_wlast),.wvalid(l_wvalid),.wready(l_wready),.bid(l_bid),.bresp(l_bresp),.bvalid(l_bvalid),.bready(l_bready),.inject_r(1'b0),.inject_b(1'b0),.reads(l_reads),.writes(l_writes),.rbeats(l_rbeats),.wbeats(l_wbeats),.bresponses(l_bresponses));
recovery_coordinator coordinator(.clk(clk),.cold_rst(rst),.abort(fault),.backend_drained(both_drained),.normal_retired(retired),.retry_safe(both_drained&&retired),.attempt_reset(attempt_reset),
.cfg_valid(k_cfg_valid),.cfg_ready(k_cfg_ready),.cfg_authoritative(configured&&bound_design==D&&bound_checkpoint==CP&&bound_generation==G),.cfg_design(D),.cfg_checkpoint(CP),.cfg_version(32'd3),.cfg_query(2'd1),.cfg_price(4'd3),.cfg_rsp_valid(k_cfg_rsp_valid),.cfg_rsp_ready(k_cfg_rsp_ready),.cfg_status(k_cfg_status),
.j_valid(j_valid),.j_ready(j_ready),.j_node(j_node),.j_net(j_net),.j_op(j_op),.journal_count(journal_count),.journal_full(journal_full),.permit_work(permit_work),
.recover_valid(recover_valid),.recover_ready(recover_ready),.recover_cookie(k_cookie),.recover_checkpoint(CP),.recover_version(k_version),.recover_design(D),.recover_query(k_query),.recover_price(k_version[3:0]),.target_reset(target_reset),.reconfigure_valid(reconfigure_valid),.reconfigure_done(l_configured&&!l_cfg_rsp_valid),.labels_valid(labels_valid),.labels_done(labels_valid),.saved_design(saved_design),.saved_checkpoint(saved_checkpoint),.new_version(new_version),.new_query(new_query),.new_price(new_price),
.rsp_valid(k_rsp_valid),.rsp_ready(k_rsp_ready),.rsp_status(k_status),.rsp_cookie(k_rsp_cookie),.rsp_corrected(k_corrected),.busy(k_busy),.fault(k_fault),
.a_valid(req_valid),.a_ready(req_ready),.a_node(req_node),.a_net(req_net),.a_cookie(req_cookie),.a_checkpoint(req_checkpoint),.a_design(req_design),.a_rsp_valid(rsp_valid),.a_rsp_ready(rsp_ready),.a_status(rsp_generation==G?rsp_status:4'd14),.a_rsp_cookie(rsp_cookie),.a_rsp_checkpoint(rsp_checkpoint),.a_rsp_design(rsp_design),.a_refs(rsp_refs),.a_occupancy(rsp_occupancy),
.o_valid(o_valid),.o_ready(o_ready),.o_op(o_op),.o_node(o_node),.o_net(o_net),.o_cookie(o_cookie),.o_rsp_valid(recovering&&l_rsp_valid),.o_rsp_ready(o_rsp_ready),.o_status(l_status),.o_rsp_cookie(l_cookie),.o_count(l_refs),.o_occupancy(l_occupancy));
integer fd,events,rc,idx,node,net,operation,before_ref,before_occ,after_ref,after_occ,dirty=0,cycles=0,k_checks=0,resets=0,softs=0,last_j_cycle=0,last_j_node=0,last_j_net=0;
string path;reg prior_target=0;reg[31:0]mn[0:31],mt[0:31],mr[0:31],mo[0:31];
always @(posedge clk)begin
 cycles<=cycles+1;if(cycles>2000000)$fatal(1,"join watchdog coordinator=%0d authority=%0d",coordinator.state,dut.state);
 if(!rst)begin
  if(m_awvalid||m_wvalid||writes||bresponses)$fatal(1,"immutable snapshot write");
  if(l_cfg_rsp_valid&&l_cfg_status!=0)$fatal(1,"live config failed");
  if(j_valid&&j_ready)begin last_j_cycle<=cycles;last_j_node<=j_node;last_j_net<=j_net;$fdisplay(events,"J %0d %0d %0d %0d",cycles,j_node,j_net,j_op);end
  if(h_valid&&h_ready)begin
   if(!permit_work)$fatal(1,"normal op while recovery owned");
   if(h_op!=0&&(cycles<=last_j_cycle||h_node!=last_j_node||h_net!=last_j_net))$fatal(1,"mutation before journal");
   $fdisplay(events,"H %0d %0d %0d %0d",cycles,h_op,h_node,h_net);
  end
  if(req_valid&&req_ready)$fdisplay(events,"AK %0d %0d %0d %0d %0d %016h",cycles,coordinator.verify_pass,req_node,req_net,req_cookie,req_generation);
  if(rsp_valid&&rsp_ready)$fdisplay(events,"AB %0d %0d %0d %0d %016h",cycles,rsp_status,rsp_refs,rsp_occupancy,rsp_generation);
  if(o_valid&&o_ready)$fdisplay(events,"O %0d %0d %0d %0d",cycles,o_op,o_node,o_net);
  if(recovering&&l_rsp_valid&&o_rsp_ready)$fdisplay(events,"OB %0d %0d %0d %0d",cycles,l_status,l_refs,l_occupancy);
  if(target_reset)begin resets<=resets+1;if(!drained)$fatal(1,"target reset with snapshot transaction");end
  if(target_reset&&!prior_target)begin if(!retired||!both_drained)$fatal(1,"live reset before actual retirement");$fdisplay(events,"RESET %0d %0d %016h",cycles,journal_count,bound_generation);end
  if(attempt_reset)begin softs<=softs+1;if(!rearm_ready||!both_drained||!retired||journal_count!=dirty)$fatal(1,"authority rearm unsafe/not accepted");$fdisplay(events,"SOFT %0d %0d %016h",cycles,journal_count,bound_generation);end
  if(labels_valid)$fdisplay(events,"LABELS_MOCK %0d",cycles);
 end
 prior_target<=target_reset;
end
task host_op(input integer op,n,t,cnt,occ);begin
 @(negedge clk);h_cookie=h_cookie+1;h_op=op;h_node=n;h_net=t;h_valid=1;do @(posedge clk);while(!h_ready);@(negedge clk);h_valid=0;
 wait(l_rsp_valid);@(negedge clk);if(l_status||l_refs!=cnt||l_occupancy!=occ||l_cookie!=h_cookie||l_fault)$fatal(1,"live host op failed");
 $fdisplay(events,"HB %0d %0d %0d %0d",cycles,l_status,l_refs,l_occupancy);h_rsp_ready=1;@(negedge clk);h_rsp_ready=0;wait(!l_busy&&both_drained);
end endtask
task request_recovery;begin
 @(negedge clk);recover_valid=1;do @(posedge clk);while(!recover_ready);@(negedge clk);recover_valid=0;
end endtask
task k_result(input integer status,corrected,count);reg[35:0]hold;begin
 wait(k_rsp_valid);@(negedge clk);if(k_status!=status||k_corrected!=corrected||journal_count!=count||!both_drained||!retired||k_rsp_cookie!=k_cookie)$fatal(1,"owner recovery result %0d/%0d corrected=%0d/%0d journal=%0d/%0d authority_fault=%b",k_status,status,k_corrected,corrected,journal_count,count,fault);
 hold={k_status,k_corrected};repeat(8)begin @(negedge clk);if(!k_rsp_valid||permit_work||{k_status,k_corrected}!==hold||!both_drained)$fatal(1,"held owner recovery response");end
 $fdisplay(events,"KD %0d %0d %0d %0d %0d",cycles,k_checks,k_status,k_corrected,journal_count);k_checks=k_checks+1;k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;repeat(2)@(negedge clk);
end endtask
initial begin
 if(!$value$plusargs("nodes=%d",N)||!$value$plusargs("capacity=%d",C)||!$value$plusargs("checkpoint=%d",CP)||!$value$plusargs("generation=%h",G)||!$value$plusargs("primary=%h",primary_base)||!$value$plusargs("pool=%h",pool_base)||!$value$plusargs("allocator=%h",allocator_base)||!$value$plusargs("primarybytes=%d",primary_bytes)||!$value$plusargs("poolbytes=%d",pool_bytes))$fatal(1,"layout args");
 if(!$value$plusargs("mutations=%s",path))$fatal(1,"mutations");fd=$fopen(path,"r");if(!$value$plusargs("events=%s",path))$fatal(1,"events");events=$fopen(path,"w");
 repeat(5)@(negedge clk);rst=0;cfg_permit=1;cfg_design=D;cfg_generation=G;cfg_checkpoint=CP;cfg_nodes=N;cfg_nets=27960;cfg_capacity=C;cfg_primary=primary_base;cfg_pool=pool_base;cfg_allocator=allocator_base;
 @(negedge clk);cfg_valid=1;do @(posedge clk);while(!cfg_ready);@(negedge clk);cfg_valid=0;wait(cfg_rsp_valid);@(negedge clk);if(cfg_status)$fatal(1,"snapshot cfg");cfg_rsp_ready=1;@(negedge clk);wait(!busy&&l_configured&&!l_cfg_rsp_valid&&both_drained);
 @(negedge clk);k_cfg_valid=1;do @(posedge clk);while(!k_cfg_ready);@(negedge clk);k_cfg_valid=0;wait(k_cfg_rsp_valid);@(negedge clk);if(k_cfg_status)$fatal(1,"generation not bound to coordinator cfg");k_cfg_rsp_ready=1;@(negedge clk);k_cfg_rsp_ready=0;
 while(!$feof(fd))begin
  rc=$fscanf(fd,"%d %d %d %d %d %d %d %d\\n",idx,node,net,operation,before_ref,before_occ,after_ref,after_occ);if(rc!=8||idx!=dirty)$fatal(1,"mutation record");mn[dirty]=node;mt[dirty]=net;mr[dirty]=before_ref;mo[dirty]=before_occ;
  @(negedge clk);j_node=node;j_net=net;j_op=operation;j_valid=1;do @(posedge clk);while(!j_ready);@(negedge clk);j_valid=0;
  host_op(operation,node,net,after_ref,after_occ);dirty=dirty+1;
 end
 if(journal_count!=dirty||dirty==0)$fatal(1,"dirty journal");recovering=1;inject_r=1;request_recovery;k_result(6,0,dirty);inject_r=0;
 if(!k_fault||permit_work||journal_count!=dirty)$fatal(1,"failed owner recovery discarded state");
 k_version=5;k_query=3;k_cookie=k_cookie+256;request_recovery;k_result(0,dirty,0);
 if(k_fault||fault||!permit_work||resets!=10||softs!=1||bound_generation!==G)$fatal(1,"owner retry final context");
 recovering=0;for(integer x=0;x<dirty;x=x+1)host_op(0,mn[x],mt[x],mr[x],mo[x]);
 $fflush(events);$fclose(events);$display("AUTHORITY_RECOVERY_PASS dirty=%0d resets=%0d soft=%0d snapshot_reads=%0d live_writes=%0d",dirty,resets,softs,reads,l_writes);$finish;
end
endmodule
'''
 return s
if __name__=='__main__':(HERE/'tb_authority_recovery.sv').write_text(make())
