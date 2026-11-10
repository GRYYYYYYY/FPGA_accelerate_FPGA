`timescale 1ns/1ps
module tb_joint;
wire pc_owned,pc_acquire_ready,pc_release_ready,pc_safe;
wire k_fault,c_fault,c_load_rsp_valid,c_busy;
wire cfg_ready_core,admit_a,admit_k,admit_c;
reg pc_acquire_valid=0,pc_release_valid=0;
wire[2:0]prepared_bits,pub_ready,discard_ready_bits,pub,discard;
wire tx_owned,prepare_allowed,tx_done_valid,tx_start_ready,tx_commit_ready,tx_cancel_ready;
wire[1:0]tx_status;
reg tx_start_valid=0,tx_commit_valid=0,tx_cancel_valid=0,tx_done_ready=0,manifest_ready=1;
reg[31:0]effective_words[0:71];wire[2303:0]effective;
initial $readmemh("config_effective.hex",effective_words);
generate for(genvar z=0;z<72;z=z+1)begin assign effective[z*32+:32]=effective_words[z];end endgenerate

reg clk=0;
reg rst=0;
reg abort=0;
reg cfg_permit=0;
reg cfg_valid=0;
wire cfg_ready;
reg [63:0]cfg_design=0;
reg [63:0]cfg_generation=0;
reg [63:0]cfg_primary=0;
reg [63:0]cfg_pool=0;
reg [63:0]cfg_allocator=0;
reg [31:0]cfg_checkpoint=0;
reg [31:0]cfg_nodes=0;
reg [31:0]cfg_nets=0;
reg [31:0]cfg_capacity=0;
reg rearm_valid=0;
wire rearm_ready;
wire cfg_rsp_valid;
reg cfg_rsp_ready=0;
wire [2:0]cfg_status;
wire cfg_rearmed;
wire configured;
wire [63:0]bound_design;
wire [63:0]bound_generation;
wire [31:0]bound_checkpoint;
reg req_valid=0;
wire req_ready;
reg [63:0]req_design=0;
reg [63:0]req_generation=0;
reg [31:0]req_checkpoint=0;
reg [31:0]req_node=0;
reg [31:0]req_net=0;
reg [31:0]req_cookie=0;
wire rsp_valid;
reg rsp_ready=0;
wire [3:0]rsp_status;
wire [63:0]rsp_design;
wire [63:0]rsp_generation;
wire [31:0]rsp_checkpoint;
wire [31:0]rsp_cookie;
wire [31:0]rsp_refs;
wire [31:0]rsp_occupancy;
wire busy;
wire fault;
wire drained;
wire [63:0]m_araddr;
wire [7:0]m_arlen;
wire [2:0]m_arsize;
wire [1:0]m_arburst;
wire [3:0]m_arid;
wire m_arvalid;
wire m_arready;
wire [511:0]m_rdata;
wire [3:0]m_rid;
wire [1:0]m_rresp;
wire m_rlast;
wire m_rvalid;
wire m_rready;
wire [63:0]m_awaddr;
wire [7:0]m_awlen;
wire [2:0]m_awsize;
wire [1:0]m_awburst;
wire [3:0]m_awid;
wire m_awvalid;
wire m_awready;
wire [511:0]m_wdata;
wire [63:0]m_wstrb;
wire m_wlast;
wire m_wvalid;
wire m_wready;
wire [3:0]m_bid;
wire [1:0]m_bresp;
wire m_bvalid;
wire m_bready;
reg cfg_stage=0;
reg publish_valid=0;
reg publish_permit=0;
reg discard_valid=0;
wire publish_ready;
wire discard_ready;
wire active_slot;
wire staged_valid;
wire [63:0]staged_design;
wire [63:0]staged_generation;
wire [31:0]staged_checkpoint;
checkpoint_authority_rotator dut(.clk(clk),.rst(rst),.abort(abort),.cfg_permit(cfg_permit&&(pc_owned||bound_generation==0)),.cfg_valid(cfg_valid&&admit_a),.cfg_ready(cfg_ready_core),.cfg_design(cfg_design),.cfg_generation(cfg_generation),.cfg_primary(cfg_primary),.cfg_pool(cfg_pool),.cfg_allocator(cfg_allocator),.cfg_checkpoint(cfg_checkpoint),.cfg_nodes(cfg_nodes),.cfg_nets(cfg_nets),.cfg_capacity(cfg_capacity),.rearm_valid(rearm_valid),.rearm_ready(rearm_ready),.cfg_rsp_valid(cfg_rsp_valid),.cfg_rsp_ready(cfg_rsp_ready),.cfg_status(cfg_status),.cfg_rearmed(cfg_rearmed),.configured(configured),.bound_design(bound_design),.bound_generation(bound_generation),.bound_checkpoint(bound_checkpoint),.req_valid(req_valid),.req_ready(req_ready),.req_design(req_design),.req_generation(req_generation),.req_checkpoint(req_checkpoint),.req_node(req_node),.req_net(req_net),.req_cookie(req_cookie),.rsp_valid(rsp_valid),.rsp_ready(rsp_ready),.rsp_status(rsp_status),.rsp_design(rsp_design),.rsp_generation(rsp_generation),.rsp_checkpoint(rsp_checkpoint),.rsp_cookie(rsp_cookie),.rsp_refs(rsp_refs),.rsp_occupancy(rsp_occupancy),.busy(busy),.fault(fault),.drained(drained),.m_araddr(m_araddr),.m_arlen(m_arlen),.m_arsize(m_arsize),.m_arburst(m_arburst),.m_arid(m_arid),.m_arvalid(m_arvalid),.m_arready(m_arready),.m_rdata(m_rdata),.m_rid(m_rid),.m_rresp(m_rresp),.m_rlast(m_rlast),.m_rvalid(m_rvalid),.m_rready(m_rready),.m_awaddr(m_awaddr),.m_awlen(m_awlen),.m_awsize(m_awsize),.m_awburst(m_awburst),.m_awid(m_awid),.m_awvalid(m_awvalid),.m_awready(m_awready),.m_wdata(m_wdata),.m_wstrb(m_wstrb),.m_wlast(m_wlast),.m_wvalid(m_wvalid),.m_wready(m_wready),.m_bid(m_bid),.m_bresp(m_bresp),.m_bvalid(m_bvalid),.m_bready(m_bready),.cfg_stage(cfg_stage),.publish_valid(pub[0]),.publish_permit(pc_owned&&!fault&&!k_fault&&!c_fault),.discard_valid(discard[0]),.publish_ready(publish_ready),.discard_ready(discard_ready),.active_slot(active_slot),.staged_valid(staged_valid),.staged_design(staged_design),.staged_generation(staged_generation),.staged_checkpoint(staged_checkpoint));

localparam[63:0]D=64'h123456789abcdef0,G1=64'h100000001,G2=64'h100000002,G3=64'h100000003,G4=64'h100000004;
localparam[63:0]OLD=64'h1000000000,WARM=64'h2000000000;
localparam integer N=9089009,NETS=27960,BYTES=145424192;
reg inject=0;integer reads,writes,rbeats,wbeats,bs,checks=0,cycles=0,events;
reg[31:0]next_cookie=1;reg[31:0]warm_nodes[0:5],existing[0:1];initial $readmemh("existing.hex",existing);initial $readmemh("nodes.hex",warm_nodes);
axi_file_memory #(.ADDR_BITS(64),.READ_ONLY(1),.MAX_BEATS(1),.TAG("snapshot"))memory(
.clk(clk),.rst(rst),.base0(OLD),.base1(WARM),.base2(64'd0),.size0(64'd145424256),.size1(64'd145424256),.size2(64'd0),
.araddr(m_araddr),.arlen(m_arlen),.arsize(m_arsize),.arburst(m_arburst),.arid(m_arid),.arvalid(m_arvalid),.arready(m_arready),.rdata(m_rdata),.rid(m_rid),.rresp(m_rresp),.rlast(m_rlast),.rvalid(m_rvalid),.rready(m_rready),
.awaddr(m_awaddr),.awlen(m_awlen),.awsize(m_awsize),.awburst(m_awburst),.awid(m_awid),.awvalid(m_awvalid),.awready(m_awready),.wdata(m_wdata),.wstrb(m_wstrb),.wlast(m_wlast),.wvalid(m_wvalid),.wready(m_wready),.bid(m_bid),.bresp(m_bresp),.bvalid(m_bvalid),.bready(m_bready),
.inject_r(inject),.inject_b(1'b0),.reads(reads),.writes(writes),.rbeats(rbeats),.wbeats(wbeats),.bresponses(bs));
always #5 clk=~clk;
always @(posedge clk)if(!rst)begin
 cycles<=cycles+1;
 if(dut.bank0.cfg_valid&&dut.bank0.cfg_ready)$fdisplay(events,"K %0d 0 %016h %0d",cycles,dut.bank0.cfg_generation,dut.bank0.cfg_checkpoint);
 if(dut.bank1.cfg_valid&&dut.bank1.cfg_ready)$fdisplay(events,"K %0d 1 %016h %0d",cycles,dut.bank1.cfg_generation,dut.bank1.cfg_checkpoint);
 if(dut.bank0.cfg_rsp_valid&&dut.bank0.cfg_rsp_ready)$fdisplay(events,"L %0d 0 %0d %0d",cycles,dut.bank0.cfg_status,dut.bank0.cfg_rearmed);
 if(dut.bank1.cfg_rsp_valid&&dut.bank1.cfg_rsp_ready)$fdisplay(events,"L %0d 1 %0d %0d",cycles,dut.bank1.cfg_status,dut.bank1.cfg_rearmed);
 if(m_awvalid||m_wvalid||writes||bs)$fatal(1,"authority wrote immutable memory");
 if(cfg_valid&&cfg_ready)$fdisplay(events,"C %0d %0d %016h %016h %0d %016h",cycles,cfg_stage,cfg_design,cfg_generation,cfg_checkpoint,cfg_primary);
 if(cfg_rsp_valid&&cfg_rsp_ready)$fdisplay(events,"F %0d %0d %0d %016h %0d",cycles,cfg_status,cfg_rearmed,bound_generation,staged_valid);
 if(pub[0]&&publish_ready)$fdisplay(events,"P %0d %016h %016h %0d",cycles,bound_generation,staged_generation,staged_checkpoint);
 if(discard[0]&&discard_ready)$fdisplay(events,"X %0d %016h",cycles,bound_generation);
 if(rearm_valid&&rearm_ready)$fdisplay(events,"A %0d %016h",cycles,bound_generation);
 if(abort)$fdisplay(events,"ABORT %0d %016h",cycles,bound_generation);
 if(req_valid&&req_ready)$fdisplay(events,"Q %0d %016h %016h %0d %0d %0d %0d %0d",cycles,req_design,req_generation,req_checkpoint,req_node,req_net,req_cookie,inject);
 if(rsp_valid&&rsp_ready)$fdisplay(events,"R %0d %016h %016h %0d %0d %0d %0d %0d",cycles,rsp_design,rsp_generation,rsp_checkpoint,rsp_cookie,rsp_status,rsp_refs,rsp_occupancy);
 $fflush(events);
end
task tick;begin @(posedge clk);#1;@(negedge clk);end endtask
task check(input bit good,input string why);begin checks=checks+1;if(!good)$fatal(1,"check %0d %s active=%h staged=%h",checks,why,bound_generation,staged_generation);end endtask
task config_bank_design(input[63:0]design_id,input bit stage,input[63:0]gen,input[31:0]cp,input[63:0]addr,input integer expected);
reg[63:0]before_gen;begin
 before_gen=bound_generation;cfg_stage=stage;cfg_design=design_id;cfg_generation=gen;cfg_checkpoint=cp;cfg_primary=addr;cfg_pool=addr+BYTES;cfg_allocator=addr+BYTES;cfg_nodes=N;cfg_nets=NETS;cfg_capacity=0;cfg_valid=1;
 do @(posedge clk);while(!cfg_ready);@(negedge clk);cfg_valid=0;
 // Change all offered fields after acceptance: the bank must use the held packet.
 cfg_stage=~stage;cfg_design=~cfg_design;cfg_generation=~gen;cfg_checkpoint=~cp;cfg_primary=~addr;cfg_pool=0;cfg_allocator=0;cfg_nodes=0;cfg_nets=0;
 wait(cfg_rsp_valid);@(negedge clk);check(cfg_status==expected&&!cfg_rearmed,"native cfg status");
 if(stage)check(bound_generation==before_gen,"stage keeps published generation");
 publish_valid=1;publish_permit=1;
 repeat(5)begin tick();check(cfg_rsp_valid&&cfg_status==expected&&!publish_ready,"held cfg reply blocks publication");end
 publish_valid=0;cfg_rsp_ready=1;tick();cfg_rsp_ready=0;tick();
end endtask
task config_bank(input bit stage,input[63:0]gen,input[31:0]cp,input[63:0]addr,input integer expected);begin config_bank_design(D,stage,gen,cp,addr,expected);end endtask
task start_get(input[63:0]gen,input[31:0]cp,node,net);begin
 req_design=D;req_generation=gen;req_checkpoint=cp;req_node=node;req_net=net;req_cookie=next_cookie;next_cookie=next_cookie+1;req_valid=1;
 do @(posedge clk);while(!req_ready);@(negedge clk);req_valid=0;
end endtask
task finish_get(input integer status,refs,occ);reg[259:0]hold;begin
 wait(rsp_valid);@(negedge clk);check(rsp_status==status&&rsp_refs==refs&&rsp_occupancy==occ&&rsp_cookie==next_cookie-1&&rsp_design==D&&rsp_generation==bound_generation&&rsp_checkpoint==bound_checkpoint,"native owner response");
 hold={rsp_status,rsp_design,rsp_generation,rsp_checkpoint,rsp_cookie,rsp_refs,rsp_occupancy};
 repeat(3)begin tick();check(rsp_valid&&{rsp_status,rsp_design,rsp_generation,rsp_checkpoint,rsp_cookie,rsp_refs,rsp_occupancy}===hold,"held GET stable");end
 rsp_ready=1;tick();rsp_ready=0;tick();
end endtask
task get(input[63:0]gen,input[31:0]cp,node,net,input integer status,refs,occ);begin start_get(gen,cp,node,net);finish_get(status,refs,occ);end endtask
task publish_now;reg[63:0]gen;begin gen=staged_generation;publish_permit=1;publish_valid=1;do @(posedge clk);while(!publish_ready);@(negedge clk);publish_valid=0;tick();check(bound_generation==gen&&!staged_valid,"atomic selector publication");end endtask
reg k_cfg_stage=0;
wire k_publish_ready;
wire k_discard_ready;
wire k_staged_valid;
wire [63:0]k_staged_design;
wire [31:0]k_staged_checkpoint;
wire [31:0]k_staged_version;
wire [31:0]k_active_version;
wire [1:0]k_staged_query;
wire [1:0]k_active_query;
wire [3:0]k_staged_price;
wire [3:0]k_active_price;
reg k_abort=0;
reg k_retry_safe=0;
wire k_attempt_reset;
reg k_cfg_valid=0;
wire k_cfg_ready,k_cfg_ready_core;assign k_cfg_ready=k_cfg_ready_core&&admit_k;
reg k_cfg_authoritative=0;
reg [63:0]k_cfg_design=0;
reg [31:0]k_cfg_checkpoint=0;
reg [31:0]k_cfg_version=0;
reg [1:0]k_cfg_query=0;
reg [3:0]k_cfg_price=0;
wire k_cfg_rsp_valid;
reg k_cfg_rsp_ready=0;
wire k_cfg_status;
reg k_j_valid=0;
wire k_j_ready;
reg [31:0]k_j_node=0;
reg [31:0]k_j_net=0;
reg [2:0]k_j_op=0;
wire [31:0]k_journal_count;
wire k_journal_full;
wire k_permit_work;
reg k_recover_valid=0;
wire k_recover_ready;
reg [31:0]k_recover_cookie=0;
reg [31:0]k_recover_checkpoint=0;
reg [31:0]k_recover_version=0;
reg [63:0]k_recover_design=0;
reg [1:0]k_recover_query=0;
reg [3:0]k_recover_price=0;
wire k_target_reset;
wire k_reconfigure_valid;
wire k_labels_valid;
reg k_reconfigure_done=0;
reg k_labels_done=0;
wire [63:0]k_saved_design;
wire [31:0]k_saved_checkpoint;
wire [31:0]k_new_version;
wire [1:0]k_new_query;
wire [3:0]k_new_price;
wire k_rsp_valid;
reg k_rsp_ready=0;
wire [3:0]k_rsp_status;
wire [31:0]k_rsp_cookie;
wire [31:0]k_rsp_corrected;
wire k_busy;
wire k_a_valid;
reg k_a_ready=0;
wire [31:0]k_a_node;
wire [31:0]k_a_net;
wire [31:0]k_a_cookie;
wire [31:0]k_a_checkpoint;
wire [63:0]k_a_design;
reg k_a_rsp_valid=0;
wire k_a_rsp_ready;
reg [3:0]k_a_status=0;
reg [31:0]k_a_rsp_cookie=0;
reg [31:0]k_a_rsp_checkpoint=0;
reg [31:0]k_a_refs=0;
reg [31:0]k_a_occupancy=0;
reg [63:0]k_a_rsp_design=0;
wire k_o_valid;
reg k_o_ready=0;
wire [2:0]k_o_op;
wire [31:0]k_o_node;
wire [31:0]k_o_net;
wire [31:0]k_o_cookie;
reg k_o_rsp_valid=0;
wire k_o_rsp_ready;
reg [3:0]k_o_status=0;
reg [31:0]k_o_rsp_cookie=0;
reg [31:0]k_o_count=0;
reg [31:0]k_o_occupancy=0;
recovery_coordinator k_engine(.cfg_stage(k_cfg_stage),.publish_valid(pub[1]),.publish_permit(pc_owned&&drained&&!fault&&!k_fault&&!c_fault),.discard_valid(discard[1]),.publish_ready(k_publish_ready),.discard_ready(k_discard_ready),.staged_valid(k_staged_valid),.staged_design(k_staged_design),.staged_checkpoint(k_staged_checkpoint),.staged_version(k_staged_version),.active_version(k_active_version),.staged_query(k_staged_query),.active_query(k_active_query),.staged_price(k_staged_price),.active_price(k_active_price),.clk(clk),.cold_rst(rst),.abort(k_abort),.backend_drained(drained),.normal_retired(!busy&&!c_busy&&!cfg_rsp_valid&&!c_load_rsp_valid),.retry_safe(k_retry_safe),.attempt_reset(k_attempt_reset),.cfg_valid(k_cfg_valid&&admit_k),.cfg_ready(k_cfg_ready_core),.cfg_authoritative(k_cfg_authoritative),.cfg_design(k_cfg_design),.cfg_checkpoint(k_cfg_checkpoint),.cfg_version(k_cfg_version),.cfg_query(k_cfg_query),.cfg_price(k_cfg_price),.cfg_rsp_valid(k_cfg_rsp_valid),.cfg_rsp_ready(k_cfg_rsp_ready),.cfg_status(k_cfg_status),.j_valid(k_j_valid),.j_ready(k_j_ready),.j_node(k_j_node),.j_net(k_j_net),.j_op(k_j_op),.journal_count(k_journal_count),.journal_full(k_journal_full),.permit_work(k_permit_work),.recover_valid(k_recover_valid),.recover_ready(k_recover_ready),.recover_cookie(k_recover_cookie),.recover_checkpoint(k_recover_checkpoint),.recover_version(k_recover_version),.recover_design(k_recover_design),.recover_query(k_recover_query),.recover_price(k_recover_price),.target_reset(k_target_reset),.reconfigure_valid(k_reconfigure_valid),.labels_valid(k_labels_valid),.reconfigure_done(k_reconfigure_done),.labels_done(k_labels_done),.saved_design(k_saved_design),.saved_checkpoint(k_saved_checkpoint),.new_version(k_new_version),.new_query(k_new_query),.new_price(k_new_price),.rsp_valid(k_rsp_valid),.rsp_ready(k_rsp_ready),.rsp_status(k_rsp_status),.rsp_cookie(k_rsp_cookie),.rsp_corrected(k_rsp_corrected),.busy(k_busy),.fault(k_fault),.a_valid(k_a_valid),.a_ready(k_a_ready),.a_node(k_a_node),.a_net(k_a_net),.a_cookie(k_a_cookie),.a_checkpoint(k_a_checkpoint),.a_design(k_a_design),.a_rsp_valid(k_a_rsp_valid),.a_rsp_ready(k_a_rsp_ready),.a_status(k_a_status),.a_rsp_cookie(k_a_rsp_cookie),.a_rsp_checkpoint(k_a_rsp_checkpoint),.a_refs(k_a_refs),.a_occupancy(k_a_occupancy),.a_rsp_design(k_a_rsp_design),.o_valid(k_o_valid),.o_ready(k_o_ready),.o_op(k_o_op),.o_node(k_o_node),.o_net(k_o_net),.o_cookie(k_o_cookie),.o_rsp_valid(k_o_rsp_valid),.o_rsp_ready(k_o_rsp_ready),.o_status(k_o_status),.o_rsp_cookie(k_o_rsp_cookie),.o_count(k_o_count),.o_occupancy(k_o_occupancy));
reg c_load_stage=0;
wire c_publish_ready;
wire c_discard_ready;
wire c_staged_valid;
wire [63:0]c_staged_design;
wire [31:0]c_staged_checkpoint;
wire [31:0]c_staged_version;
wire [31:0]c_active_version;
wire [2303:0]c_staged_payload;
wire [2303:0]c_active_payload;
reg c_abort=0;
reg c_attempt_reset=0;
reg c_load_valid=0;
wire c_load_ready,c_load_ready_core;assign c_load_ready=c_load_ready_core&&admit_c;
reg c_load_authoritative=0;
reg [2303:0]c_load_payload=0;
reg [63:0]c_load_design=0;
reg [31:0]c_load_checkpoint=0;
reg c_load_rsp_ready=0;
wire c_load_status;
reg c_start_valid=0;
wire c_start_ready;
reg [63:0]c_start_design=0;
reg [31:0]c_start_checkpoint=0;
reg [31:0]c_start_cookie=0;
reg [31:0]c_start_version=0;
reg [3:0]c_start_price=0;
wire [5:0]c_cfg_valid;
reg [5:0]c_cfg_ready=0;
wire [2303:0]c_cfg_payload;
reg [5:0]c_cfg_rsp_valid=0;
wire [5:0]c_cfg_rsp_ready;
reg [17:0]c_cfg_status=0;
wire c_rsp_valid;
reg c_rsp_ready=0;
wire [3:0]c_rsp_status;
wire [31:0]c_rsp_cookie;
wire [5:0]c_sent;
wire [5:0]c_retired;
wire [63:0]c_saved_design;
wire [31:0]c_saved_checkpoint;
config_restore_controller c_engine(.load_stage(c_load_stage),.publish_valid(pub[2]),.publish_permit(pc_owned&&drained&&!fault&&!k_fault&&!c_fault),.discard_valid(discard[2]),.publish_ready(c_publish_ready),.discard_ready(c_discard_ready),.staged_valid(c_staged_valid),.staged_design(c_staged_design),.staged_checkpoint(c_staged_checkpoint),.staged_version(c_staged_version),.active_version(c_active_version),.staged_payload(c_staged_payload),.active_payload(c_active_payload),.clk(clk),.rst(rst),.abort(c_abort),.backend_drained(drained),.normal_retired(!busy&&!k_busy&&!cfg_rsp_valid&&!k_cfg_rsp_valid),.attempt_reset(c_attempt_reset),.load_valid(c_load_valid&&admit_c),.load_ready(c_load_ready_core),.load_authoritative(c_load_authoritative),.load_payload(c_load_payload),.load_design(c_load_design),.load_checkpoint(c_load_checkpoint),.load_rsp_valid(c_load_rsp_valid),.load_rsp_ready(c_load_rsp_ready),.load_status(c_load_status),.start_valid(c_start_valid),.start_ready(c_start_ready),.start_design(c_start_design),.start_checkpoint(c_start_checkpoint),.start_cookie(c_start_cookie),.start_version(c_start_version),.start_price(c_start_price),.cfg_valid(c_cfg_valid),.cfg_ready(c_cfg_ready),.cfg_payload(c_cfg_payload),.cfg_rsp_valid(c_cfg_rsp_valid),.cfg_rsp_ready(c_cfg_rsp_ready),.cfg_status(c_cfg_status),.rsp_valid(c_rsp_valid),.rsp_ready(c_rsp_ready),.rsp_status(c_rsp_status),.rsp_cookie(c_rsp_cookie),.busy(c_busy),.fault(c_fault),.sent(c_sent),.retired(c_retired),.saved_design(c_saved_design),.saved_checkpoint(c_saved_checkpoint));

assign admit_a=!tx_owned?!pc_owned:(prepare_allowed&&cfg_stage);
assign admit_k=!tx_owned?!pc_owned:(prepare_allowed&&k_cfg_stage);
assign admit_c=!tx_owned?!pc_owned:(prepare_allowed&&c_load_stage);
assign cfg_ready=cfg_ready_core&&admit_a;
wire stage_busy=busy||k_busy||c_busy||cfg_rsp_valid||k_cfg_rsp_valid||c_load_rsp_valid;
wire retired_all=drained&&!stage_busy;
assign prepared_bits={c_staged_valid,k_staged_valid,staged_valid};
assign pub_ready={c_publish_ready,k_publish_ready,publish_ready};
assign discard_ready_bits={c_discard_ready,k_discard_ready,discard_ready};
checkpoint_lease_guard lease(.clk(clk),.rst(rst),.acquire_valid(pc_acquire_valid),.acquire_ready(pc_acquire_ready),.release_valid(pc_release_valid),.release_ready(pc_release_ready),.owned(pc_owned),.healthy(configured&&k_saved_design!=0&&c_saved_design!=0&&!fault&&!k_fault&&!c_fault&&retired_all),.retired(retired_all),.route_retired(1'b1),.no_offers(!cfg_valid&&!k_cfg_valid&&!c_load_valid&&!req_valid),.command_busy(tx_owned||tx_done_valid||stage_busy||(|prepared_bits)),.command_valid(tx_start_valid||tx_commit_valid||tx_cancel_valid||cfg_valid||k_cfg_valid||c_load_valid),.test_reset(1'b0),.safe(pc_safe));
checkpoint_publish_barrier barrier(.clk(clk),.rst(rst),.lease_owned(pc_owned),.retired(retired_all),.stage_busy(stage_busy),.fault(fault||k_fault||c_fault),.manifest_ready(manifest_ready),
.start_valid(tx_start_valid),.start_ready(tx_start_ready),.start_design(D),.start_generation(G2),.start_checkpoint(32'd18),.start_version(32'd4),.start_query(2'd2),.start_price(4'd4),
.commit_valid(tx_commit_valid),.commit_ready(tx_commit_ready),.cancel_valid(tx_cancel_valid),.cancel_ready(tx_cancel_ready),.owned(tx_owned),.prepare_allowed(prepare_allowed),.done_valid(tx_done_valid),.done_ready(tx_done_ready),.done_status(tx_status),
.prepared(prepared_bits),.publish_ready(pub_ready),.discard_ready(discard_ready_bits),.publish_valid(pub),.discard_valid(discard),
.a_design(bound_design),.a_generation(bound_generation),.a_checkpoint(bound_checkpoint),.k_design(k_saved_design),.k_checkpoint(k_saved_checkpoint),.k_version(k_active_version),.k_query(k_active_query),.k_price(k_active_price),.journal_count(k_journal_count),.c_design(c_saved_design),.c_checkpoint(c_saved_checkpoint),.c_version(c_active_version),
.sa_design(staged_design),.sa_generation(staged_generation),.sa_checkpoint(staged_checkpoint),.sk_design(k_staged_design),.sk_checkpoint(k_staged_checkpoint),.sk_version(k_staged_version),.sk_query(k_staged_query),.sk_price(k_staged_price),.sc_design(c_staged_design),.sc_checkpoint(c_staged_checkpoint),.sc_version(c_staged_version));
always @(posedge clk)if(!rst)begin
 if(c_cfg_valid||k_target_reset||k_reconfigure_valid||k_labels_valid||k_a_valid||k_o_valid)$fatal(1,"metadata transaction ran recovery/provider callbacks");
 if(c_abort)$fdisplay(events,"ABORT_CF %0d %0d %0d",cycles,c_saved_checkpoint,c_active_version);
 if(pc_acquire_valid&&pc_acquire_ready)$fdisplay(events,"LEASE %0d A",cycles);
 if(pc_release_valid&&pc_release_ready)$fdisplay(events,"LEASE %0d R",cycles);
 if(k_recover_valid&&k_recover_ready)$fdisplay(events,"KRQ %0d %0d %0d %0d",cycles,k_recover_checkpoint,k_recover_version,k_recover_query);
 if(k_rsp_valid&&k_rsp_ready)$fdisplay(events,"KRR %0d %0d %0d",cycles,k_rsp_status,k_rsp_cookie);
 if(k_cfg_valid&&k_cfg_ready)$fdisplay(events,"KC %0d %0d %0d %0d",cycles,k_cfg_stage,k_cfg_checkpoint,k_cfg_version);
 if(k_cfg_rsp_valid&&k_cfg_rsp_ready)$fdisplay(events,"KF %0d %0d %0d %0d",cycles,k_cfg_status,k_saved_checkpoint,k_journal_count);
 if(c_load_valid&&c_load_ready)$fdisplay(events,"CC %0d %0d %0d %0d",cycles,c_load_stage,c_load_checkpoint,c_load_payload[2240+:32]);
 if(c_load_rsp_valid&&c_load_rsp_ready)$fdisplay(events,"CF %0d %0d %0d %0d",cycles,c_load_status,c_saved_checkpoint,c_active_version);
 if(k_j_valid&&k_j_ready)$fdisplay(events,"J %0d %0d %0d",cycles,k_j_node,k_j_net);
 if(tx_commit_valid&&tx_commit_ready)$fdisplay(events,"COMMIT %0d %b",cycles,pub);
 if(tx_cancel_valid&&tx_cancel_ready)$fdisplay(events,"CANCEL %0d",cycles);
 if(tx_start_valid&&tx_start_ready)$fdisplay(events,"START %0d %0d %0d %016h",cycles,k_saved_checkpoint,k_journal_count,bound_generation);
 if(|pub)$fdisplay(events,"JOIN %0d %b %0d %0d %0d %016h",cycles,pub,k_saved_checkpoint,c_saved_checkpoint,k_journal_count,bound_generation);
 if(|(discard&discard_ready_bits))$fdisplay(events,"DROP %0d %b",cycles,discard&discard_ready_bits);
 if(tx_done_valid&&tx_done_ready)$fdisplay(events,"END %0d %0d %0d %0d %0d %016h",cycles,tx_status,k_saved_checkpoint,c_saved_checkpoint,k_journal_count,bound_generation);
end
task config_k(input bit shadow,input[31:0]cp,v,input integer expected);reg[31:0]old_cp,old_count;begin
 old_cp=k_saved_checkpoint;old_count=k_journal_count;k_cfg_stage=shadow;k_cfg_authoritative=1;k_cfg_design=D;k_cfg_checkpoint=cp;k_cfg_version=v;k_cfg_query=2;k_cfg_price=v[3:0];k_cfg_valid=1;
 do @(posedge clk);while(!k_cfg_ready);@(negedge clk);k_cfg_valid=0;wait(k_cfg_rsp_valid);@(negedge clk);check(k_cfg_status==expected,"coordinator prepare result");
 repeat(5)begin tick();if(shadow)check(k_saved_checkpoint==old_cp&&k_journal_count==old_count&&!k_staged_valid,"coordinator mutated before publication");end
 k_cfg_rsp_ready=1;tick();k_cfg_rsp_ready=0;tick();
end endtask
task config_c(input bit shadow,input[31:0]cp,v,input integer expected);reg[31:0]old_cp;begin
 old_cp=c_saved_checkpoint;c_load_stage=shadow;c_load_authoritative=1;c_load_design=D;c_load_checkpoint=cp;c_load_payload=effective;c_load_payload[2240+:32]=v;c_load_valid=1;
 do @(posedge clk);while(!c_load_ready);@(negedge clk);c_load_valid=0;wait(c_load_rsp_valid);@(negedge clk);check(c_load_status==expected,"config shadow result");
 repeat(5)begin tick();if(shadow)check(c_saved_checkpoint==old_cp&&c_active_payload==effective&&!c_staged_valid,"active config mutated before publication");end
 c_load_rsp_ready=1;tick();c_load_rsp_ready=0;tick();
end endtask
task begin_tx;begin
 pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;check(pc_owned,"real lease acquired");tx_start_valid=1;do @(posedge clk);while(!tx_start_ready);@(negedge clk);tx_start_valid=0;check(tx_owned&&prepare_allowed,"transaction owns lease");
end endtask
task end_tx(input integer expected);begin
 wait(tx_done_valid);@(negedge clk);check(tx_status==expected,"transaction completion");pc_release_valid=1;
 repeat(8)begin tick();check(pc_owned&&!pc_release_ready&&tx_done_valid&&tx_status==expected,"held result retains lease");end
 pc_release_valid=0;tx_done_ready=1;tick();tx_done_ready=0;tick();pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;check(!pc_owned&&!tx_owned,"release after result consumption");
end endtask
initial begin
 events=$fopen("events.txt","w");rst=1;repeat(4)tick();rst=0;cfg_permit=1;tick();
 config_bank(0,G1,17,OLD,0);config_k(0,17,4,0);config_c(0,17,4,0);
 for(integer i=0;i<6;i=i+1)begin k_j_node=warm_nodes[i];k_j_net=2717;k_j_op=1;k_j_valid=1;do @(posedge clk);while(!k_j_ready);@(negedge clk);k_j_valid=0;tick();end
 check(k_journal_count==6&&k_permit_work,"six old journal keys retained");get(G1,17,263946,2717,0,0,0);
 // No lease: a stage request must report rejection, not clear the old baseline.
 config_k(0,18,4,1);config_c(0,18,4,1);config_k(1,18,4,1);config_c(1,18,4,1);check(k_journal_count==6&&k_saved_checkpoint==17&&c_saved_checkpoint==17,"no-lease staging unchanged");
 begin_tx();config_bank(1,G2,18,WARM,0);config_k(1,18,5,1);config_c(1,18,5,1);config_k(1,19,4,0);config_c(1,18,4,0);
 check(prepared_bits==7&&!k_permit_work&&!k_j_ready&&!k_recover_ready,"prepared snapshot freezes coordinator");
 tx_commit_valid=1;do @(posedge clk);while(!tx_commit_ready);@(negedge clk);tx_commit_valid=0;end_tx(1);check(k_journal_count==6&&k_saved_checkpoint==17&&c_saved_checkpoint==17&&bound_generation==G1,"mismatched checkpoint canceled atomically");
 begin_tx();config_bank(1,G2,18,WARM,0);config_k(1,18,4,0);config_c(1,18,4,0);tx_cancel_valid=1;do @(posedge clk);while(!tx_cancel_ready);@(negedge clk);tx_cancel_valid=0;end_tx(2);check(k_journal_count==6&&k_saved_checkpoint==17&&c_saved_checkpoint==17&&bound_generation==G1,"explicit cancel preserves old state");
 begin_tx();config_bank(1,G2,18,WARM,0);config_k(1,18,4,0);config_c(1,18,4,0);
 c_abort=1;tx_commit_valid=1;#1;check(!tx_commit_ready&&pub==0,"CF abort masks joint publication");tick();c_abort=0;tx_commit_valid=0;check(!c_staged_valid&&c_saved_checkpoint==17&&k_journal_count==6,"CF abort leaves active baseline unchanged");
 tx_cancel_valid=1;do @(posedge clk);while(!tx_cancel_ready);@(negedge clk);tx_cancel_valid=0;end_tx(2);check(k_journal_count==6&&k_saved_checkpoint==17&&c_saved_checkpoint==17&&bound_generation==G1,"partial prepared cancellation preserved baseline");
 begin_tx();config_bank(1,G2,18,WARM,0);config_k(1,18,4,0);config_c(1,18,4,0);
 manifest_ready=0;repeat(5)begin tick();check(!tx_commit_ready&&pub==0&&k_journal_count==6,"manifest receipt required");end tx_commit_valid=0;manifest_ready=1;
 start_get(G1,17,263946,2717);wait(rsp_valid);@(negedge clk);tx_commit_valid=1;
 repeat(6)begin tick();check(!tx_commit_ready&&pub==0&&k_journal_count==6&&k_saved_checkpoint==17,"old reply prevents all three publications");end
 finish_get(0,0,0);@(negedge clk);tx_commit_valid=0;end_tx(0);
 check(bound_generation==G2&&bound_checkpoint==18&&k_saved_checkpoint==18&&c_saved_checkpoint==18&&k_journal_count==0&&c_active_payload==effective&&k_active_version==4&&k_active_query==2&&k_active_price==4&&k_permit_work,"all metadata published together");
 // A checkpoint publication may clear the journal, but not the attempt floor.
 k_recover_design=D;k_recover_checkpoint=18;k_recover_version=4;k_recover_query=3;k_recover_price=4;k_recover_cookie=77;k_recover_valid=1;
 do @(posedge clk);while(!k_recover_ready);@(negedge clk);k_recover_valid=0;wait(k_rsp_valid);@(negedge clk);check(k_rsp_status==1&&k_rsp_cookie==77,"attempt floor retained after publication");
 repeat(5)begin tick();check(k_rsp_valid&&k_rsp_status==1&&k_journal_count==0&&k_saved_checkpoint==18,"invalid recovery held without changing baseline");end
 k_rsp_ready=1;tick();k_rsp_ready=0;tick();check(k_active_version==4&&k_active_query==2&&k_active_price==4&&k_permit_work,"rejected recovery preserved context");
 get(G1,17,263946,2717,1,0,0);get(G2,18,263946,2717,0,1,1);get(G2,18,existing[0],existing[1],0,1,1);
 $fdisplay(events,"JOINT_DONE %0d %0d %0d %0d",checks,reads,k_journal_count,k_saved_checkpoint);$fflush(events);$display("CHECKPOINT_JOINT_PASS checks=%0d reads=%0d",checks,reads);$finish;
end
initial begin #2000000;$fatal(1,"timeout");end
endmodule
