from pathlib import Path
import importlib.util,re
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
BASE=ROOT/'results/route_checkpoint_fault_regression_v1/sources/tb_query_fault.sv'
def make():
 builder=HERE/'build.py' if (HERE/'build.py').exists() else HERE/'authority_build.py'
 sp=importlib.util.spec_from_file_location('aqbuild',builder);b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b)
 s=BASE.read_text()
 s=s.replace('reg k_a_ready=0,k_a_rsp_valid=0','wire k_a_ready,k_a_rsp_valid').replace('reg[31:0]k_a_rsp_cookie=0,k_a_rsp_checkpoint=0,k_a_refs=0,k_a_occ=0;reg[63:0]k_a_rsp_design=0;reg[3:0]k_a_status=0;', 'wire[31:0]k_a_rsp_cookie,k_a_rsp_checkpoint,k_a_refs,k_a_occ;wire[63:0]k_a_rsp_design;wire[3:0]k_a_status;')
 s=s.replace(';k_a_ready<=0;k_a_rsp_valid<=0;auth_delay<=0;', ';')
 start=s.index('  k_a_ready<=cycles%4==0;');end=s.index('  if(k_a_rsp_valid&&k_a_rsp_ready)k_a_rsp_valid<=0;',start)+len('  if(k_a_rsp_valid&&k_a_rsp_ready)k_a_rsp_valid<=0;')
 s=s[:start]+'''  if(k_a_valid&&k_a_ready)$fdisplay(trace,"KA %0d %0d %0d %0d %0d",cycles,k_a_checkpoint,k_a_node,k_a_net,k_a_cookie);
  if(k_a_rsp_valid&&k_a_rsp_ready)$fdisplay(trace,"AS_REPLY %0d %0d %0d %0d %016h",cycles,k_a_status,k_a_refs,k_a_occ,as_rsp_generation);'''+s[end:]
 decl=b.PORTS.replace('input wire','wire').replace('output wire','wire').replace(',wire',';wire').replace(',output',';output').replace(',input',';input')
 # Every line in the generated top is a declaration group.
 decl='\n'.join(l.rstrip(',')+';'for l in decl.splitlines())
 agent='''
reg authority_bind=0,authority_ack=0;integer as_reads,as_writes,as_rbeats,as_wbeats,as_bresponses;
axi_file_memory #(.ADDR_BITS(64),.READ_ONLY(1),.MAX_BEATS(1),.TAG("snapshot")) authority_memory(
.clk(clk),.rst(k_cold_rst),.base0(64'h91fffff000),.base1(64'h9208aaef40),.base2(64'h9208aaef40),.size0(64'd145424192),.size1(64'd0),.size2(64'd64),
'''
 names=['araddr','arlen','arsize','arburst','arid','arvalid','arready','rdata','rid','rresp','rlast','rvalid','rready','awaddr','awlen','awsize','awburst','awid','awvalid','awready','wdata','wstrb','wlast','wvalid','wready','bid','bresp','bvalid','bready']
 agent+=','.join('.'+n+'(as_m_'+n+')'for n in names)+''',.inject_r(1'b0),.inject_b(1'b0),.reads(as_reads),.writes(as_writes),.rbeats(as_rbeats),.wbeats(as_wbeats),.bresponses(as_bresponses));
 always @(posedge clk)if(!k_cold_rst)begin
  if(as_m_awvalid||as_m_wvalid||as_writes||as_bresponses)$fatal(1,"snapshot authority write");
  if(k_target_reset&&(!as_drained||!as_retired))$fatal(1,"system target reset before authority retired");
 end
 task install_authority;begin
  @(negedge clk);authority_bind=1;do @(posedge clk);while(!as_cfg_ready);@(negedge clk);authority_bind=0;
  wait(as_cfg_rsp_valid);@(negedge clk);if(as_cfg_status||!as_configured||as_bound_generation!=64'h100000001)$fatal(1,"authority install");
  repeat(5)begin @(negedge clk);if(!as_cfg_rsp_valid||qc_cmd_ready||rc_req_ready)$fatal(1,"authority config lease");end
  $fdisplay(trace,"AS_BIND %0d %016h %0d %016h",cycles,as_bound_design,as_bound_checkpoint,as_bound_generation);
  authority_ack=1;@(negedge clk);authority_ack=0;wait(!as_busy&&!system.as_cfg_lease);
 end endtask
'''
 s=s.replace('reg last_k_reset=0',decl+agent+'\nreg last_k_reset=0')
 overrides={'as_cfg_valid':'authority_bind','as_cfg_rsp_ready':'authority_ack','as_cfg_design':'design_id','as_cfg_generation':"64'h100000001",'as_cfg_primary':"64'h91fffff000",'as_cfg_pool':"64'h9208aaef40",'as_cfg_allocator':"64'h9208aaef40",'as_cfg_checkpoint':"32'd17",'as_cfg_nodes':"32'd9089009",'as_cfg_nets':"32'd27960",'as_cfg_capacity':"32'd0"}
 s=s.replace(')system(.pc_acquire_valid',')system('+','.join('.'+n+'('+overrides.get(n,n)+')'for n in b.PN)+',.pc_acquire_valid')
 s=s.replace(' install_checkpoint;install_config_snapshot;', ' install_authority;install_checkpoint;install_config_snapshot;')
 return s
if __name__=='__main__':(HERE/'tb_query_fault.sv').write_text(make())
