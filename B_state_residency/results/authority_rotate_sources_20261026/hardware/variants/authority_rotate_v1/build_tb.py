from pathlib import Path
import importlib.util
HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('bank_builder',HERE/'build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
def make():
 ps=b.ports(b.BASE.read_text());decl=[];conn=[]
 for d,w,n in ps:
  decl.append(f'{"reg"if d=="input"else"wire"} {w}{n}'+('=0;'if d=='input'else';'));conn.append(f'.{n}({n})')
 extra=['cfg_stage','publish_valid','publish_permit','discard_valid'];decl += [f'reg {n}=0;'for n in extra];conn += [f'.{n}({n})'for n in extra]
 for w,n in [('',x)for x in ['publish_ready','discard_ready','active_slot','staged_valid']]+[('[63:0]',x)for x in ['staged_design','staged_generation']]+[('[31:0]','staged_checkpoint')]:decl.append(f'wire {w}{n};');conn.append(f'.{n}({n})')
 # Memory-driven AXI input wires must not be procedural regs.
 for n in ['m_arready','m_rdata','m_rid','m_rresp','m_rlast','m_rvalid','m_awready','m_wready','m_bid','m_bresp','m_bvalid']:
  decl=[s.replace('reg ','wire ',1).replace('=0;',';')if s.split(']')[-1].startswith(n)or s.startswith('reg '+n+'=')else s for s in decl]
 text='`timescale 1ns/1ps\nmodule tb_rotate;\n'+'\n'.join(decl)+'\ncheckpoint_authority_rotator dut('+','.join(conn)+');\n'
 text+='''
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
 if(publish_valid&&publish_ready)$fdisplay(events,"P %0d %016h %016h %0d",cycles,bound_generation,staged_generation,staged_checkpoint);
 if(discard_valid&&discard_ready)$fdisplay(events,"X %0d %016h",cycles,bound_generation);
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
initial begin
 events=$fopen("events.txt","w");rst=1;repeat(4)tick();rst=0;cfg_permit=1;tick();check(!configured&&!req_ready&&!publish_ready,"cold unbound");
 config_bank(0,G1,17,OLD,0);check(configured&&bound_generation==G1&&bound_checkpoint==17,"initial binding");get(G1,17,263946,2717,0,0,0);get(G1,17,existing[0],existing[1],0,1,1);get(G1,17,existing[0],2717,0,0,1);
 config_bank(0,G2,18,WARM,1);check(bound_generation==G1&&bound_design==D,"initial binding cannot be overwritten");
 config_bank(1,G2,18,WARM,0);check(staged_valid&&staged_generation==G2&&bound_generation==G1,"prepared standby hidden");
 config_bank(1,G3,19,WARM,1);check(staged_valid&&staged_generation==G2,"prepared candidate preserved after conflicting config");
 publish_permit=0;publish_valid=1;repeat(5)begin tick();check(!publish_ready&&bound_generation==G1,"permission required");end publish_valid=0;
 get(G1,17,263946,2717,0,0,0);get(G2,18,263946,2717,1,0,0);
 start_get(G1,17,554512,2717);wait(rsp_valid);@(negedge clk);publish_permit=1;publish_valid=1;repeat(6)begin tick();check(!publish_ready&&bound_generation==G1,"held old reply prevents switch");end publish_valid=0;finish_get(0,0,0);
 publish_now();get(G2,18,existing[0],existing[1],0,1,1);for(integer k=0;k<6;k=k+1)get(G2,18,warm_nodes[k],2717,0,1,1);get(G1,17,263946,2717,1,0,0);get(G2,18,263946,2717,0,1,1);get(G2,18,554512,2717,0,1,1);get(G2,18,65185,2717,0,0,0);get(G2,18,263946,0,0,0,1);
 get(G2,18,N,2717,2,0,0);get(G2,18,263946,NETS,2,0,0);
 config_bank(1,64'd3,19,WARM,1);check(!staged_valid&&bound_generation==G2,"full 64bit monotonic floor");
 config_bank(1,G3,18,WARM,1);check(!staged_valid,"checkpoint monotonic floor");
 config_bank_design(~D,1,G3,19,WARM,1);check(bound_design==D&&!staged_valid,"cross-design stage rejected");
 config_bank(1,G3,19,WARM+1,2);check(!staged_valid&&!fault&&bound_generation==G2,"native bad layout does not poison active");get(G2,18,263946,2717,0,1,1);
 config_bank(1,G3,19,WARM,0);check(staged_valid,"candidate after failed layout");discard_valid=1;do @(posedge clk);while(!discard_ready);@(negedge clk);discard_valid=0;tick();check(!staged_valid&&bound_generation==G2,"discard preserves active");
 config_bank(1,G3,19,WARM,0);abort=1;publish_valid=1;tick();abort=0;publish_valid=0;tick();check(!staged_valid&&bound_generation==G2&&!fault,"abort prevents candidate publication");get(G2,18,263946,2717,0,1,1);
 inject=1;get(G2,18,263946,2717,9,0,0);inject=0;check(fault&&!req_ready,"real AXI read failure retained");
 // A failed rearm disables service but must never erase the established namespace.
 rearm_valid=1;do @(posedge clk);while(!rearm_ready);@(negedge clk);rearm_valid=0;abort=1;tick();abort=0;
 wait(cfg_rsp_valid);@(negedge clk);check(cfg_status==3&&cfg_rearmed&&bound_generation==G2&&!configured&&fault,"canceled rearm retains namespace");cfg_rsp_ready=1;tick();cfg_rsp_ready=0;tick();
 config_bank(0,G1,17,OLD,1);check(bound_generation==G2&&!configured&&fault,"initial bind cannot bypass failed-rearm identity");
 rearm_valid=1;do @(posedge clk);while(!rearm_ready);@(negedge clk);rearm_valid=0;wait(cfg_rsp_valid);@(negedge clk);check(cfg_status==0&&cfg_rearmed&&bound_generation==G2,"real active-bank rearm");cfg_rsp_ready=1;tick();cfg_rsp_ready=0;tick();check(!fault,"active fault cleared after rearm");get(G2,18,263946,2717,0,1,1);
 // Cancel only after the standby native reader has accepted its configuration.
 cfg_stage=1;cfg_design=D;cfg_generation=G3;cfg_checkpoint=19;cfg_primary=WARM;cfg_pool=WARM+BYTES;cfg_allocator=WARM+BYTES;cfg_nodes=N;cfg_nets=NETS;cfg_capacity=0;cfg_valid=1;
 do @(posedge clk);while(!cfg_ready);@(negedge clk);cfg_valid=0;
 do @(posedge clk);while(!((dut.bank0.cfg_valid&&dut.bank0.cfg_ready)||(dut.bank1.cfg_valid&&dut.bank1.cfg_ready)));
 @(negedge clk);abort=1;tick();abort=0;wait(cfg_rsp_valid);@(negedge clk);check(cfg_status==3&&!staged_valid&&bound_generation==G2&&!fault,"native accepted prepare cancellation preserves active");
 cfg_rsp_ready=1;tick();cfg_rsp_ready=0;tick();get(G2,18,263946,2717,0,1,1);
 config_bank(1,G4,20,WARM,0);publish_now();get(G2,18,263946,2717,1,0,0);get(G4,20,263946,2717,0,1,1);get(G4,20,existing[0],existing[1],0,1,1);
 $fdisplay(events,"DONE %0d %0d %0d %0d",checks,reads,rbeats,writes);$fflush(events);$display("AUTHORITY_ROTATE_PASS checks=%0d reads=%0d",checks,reads);$finish;
end
initial begin #2000000;$fatal(1,"timeout");end
endmodule
'''
 return text
if __name__=='__main__':(HERE/'tb_rotate.sv').write_text(make())
