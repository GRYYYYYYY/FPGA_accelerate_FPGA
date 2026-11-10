"""Integrate immutable snapshot authority into the production query hierarchy."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
BASE=ROOT/'results/route_checkpoint_fault_regression_v1/sources'
READER=ROOT/'hardware/variants/checkpoint_authority_v1/checkpoint_authority_reader.sv'
def rep(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
HOOK='''input wire as_drained,as_retired,as_fault,as_configured,
input wire[63:0]as_bound_design,as_bound_generation,input wire[31:0]as_bound_checkpoint,
output wire as_attempt_reset,
'''
HN=['as_drained','as_retired','as_fault','as_configured','as_bound_design','as_bound_generation','as_bound_checkpoint','as_attempt_reset']
def pins(names):return ','.join('.'+n+'('+n+')'for n in names)+','
def addports(s,p):
 at=s.index(')(\n')+3;return s[:at]+p+s[at:]
def service_ports():
 s=READER.read_text();s=s[s.index('(\n')+2:s.index('\n);')]
 # Root exposes only config/AXI and bound-state inspection; data traffic stays internal.
 lines=s.splitlines();result=[]
 for line in lines:
  if any(x in line for x in ['input wire cfg_valid','input wire[31:0]cfg_checkpoint','output reg configured','output wire[63:0]m_araddr','output wire m_arvalid','output wire[63:0]m_awaddr','output wire m_awvalid','input wire[3:0]m_bid']):
   line=line.replace('output reg','output wire');line=re.sub(r'\b(cfg_\w+|bound_\w+|configured|m_\w+)\b',lambda m:'as_'+m[0],line);result.append(line.rstrip(',')+',')
 return '\n'.join(result)+'\noutput wire as_cfg_rsp_valid,input wire as_cfg_rsp_ready,output wire[2:0]as_cfg_status,\noutput wire as_busy,as_fault,as_drained,as_retired,output wire[63:0]as_rsp_generation,\n'
PORTS=service_ports()
PN=re.findall(r'\bas_[A-Za-z0-9_]+\b',PORTS)
def make():
 out={'checkpoint_authority_reader.sv':READER.read_text()}
 s=addports((BASE/'residency_system.sv').read_text(),HOOK)
 s=rep(s,'wire k_labels_done;wire k_attempt_reset;wire k_retry_safe;','wire k_labels_done;wire k_attempt_reset;wire k_retry_safe;\nassign as_attempt_reset=k_attempt_reset;')
 s=rep(s,'assign f_all_drained=label_drained','assign f_all_drained=as_drained&&label_drained')
 s=rep(s,'.retired_idle(f_backend_idle)', '.retired_idle(as_backend_idle)')
 s=rep(s,'wire label_drained;', 'wire as_backend_idle;assign f_backend_idle=as_backend_idle&&as_retired;\nwire label_drained;')
 s=rep(s,'.cfg_authoritative(fd_fa_authoritative)', '.cfg_authoritative(fd_fa_authoritative&&as_configured&&as_bound_design==fd_fa_design&&as_bound_checkpoint==fd_fa_checkpoint&&as_bound_generation!=0)')
 s=rep(s,'.backend_drained(f_all_drained),.normal_retired(f_normal_retired),.cfg_valid(fd_k_cfg_valid)', '.backend_drained(f_all_drained),.normal_retired(f_normal_retired&&as_retired),.cfg_valid(fd_k_cfg_valid)')
 s=rep(s,'.abort(f_fault||cf_fault||', '.abort(as_fault||f_fault||cf_fault||')
 s=rep(s,'.normal_fault(fault||rc_fault||k_fault||cf_fault||lr_fault)', '.normal_fault(as_fault||fault||rc_fault||k_fault||cf_fault||lr_fault)')
 out['residency_system.sv']=s
 s=addports((BASE/'search_residency_system.sv').read_text(),HOOK)
 s=rep(s,'backend(', 'backend('+pins(HN));out['search_residency_system.sv']=s
 s=addports((BASE/'query_residency_system.sv').read_text(),PORTS)
 # Former response inputs become read-only debug outputs; host cannot supply authority.
 for n in ['k_a_occ','k_a_ready','k_a_refs','k_a_rsp_checkpoint','k_a_rsp_cookie','k_a_rsp_design','k_a_rsp_valid','k_a_status']:
  s=re.sub(r'input wire([^\n]*\b'+n+r'\b[^\n]*)',r'output wire\1',s,count=1)
 s=rep(s,'wire host_open=!qc_busy&&!qc_fault&&!pc_owned;', 'wire host_open=!qc_busy&&!qc_fault&&!pc_owned&&!as_cfg_lease;')
 s=rep(s,'!qc_busy&&!pc_owned&&k_rec_valid','!qc_busy&&!pc_owned&&!as_cfg_lease&&k_rec_valid')
 s=rep(s,'!qc_busy&&!pc_owned&&b_k_rec_ready','!qc_busy&&!pc_owned&&!as_cfg_lease&&b_k_rec_ready')
 s=rep(s,'.cmd_valid(qc_cmd_valid&&!pc_owned)', '.cmd_valid(qc_cmd_valid&&!pc_owned&&!as_cfg_lease)')
 s=rep(s,'.admit(!pc_owned&&', '.admit(!as_cfg_lease&&!pc_owned&&!as_fault&&')
 s=rep(s,'&&!k_busy&&!f_recovery_owned;', '&&!k_busy&&!f_recovery_owned&&!as_cfg_lease&&!as_fault;')
 s=rep(s,'inner(', 'inner('+pins(HN))
 body='''
wire as_attempt_reset,as_rearm_ready,as_core_cfg_ready,as_core_cfg_valid,as_core_cfg_rearmed;
wire[2:0]as_core_cfg_status;wire[63:0]as_bound_design,as_bound_generation;wire[31:0]as_bound_checkpoint;
wire[3:0]as_core_status;reg as_cfg_lease;
wire as_initial_safe=!rst&&!k_cold_rst&&!abort&&!pc_owned&&!pc_acquire_valid&&!cp_valid&&!cp_test_reset&&!qc_busy&&!ss_busy&&!k_busy&&!f_recovery_owned&&f_normal_retired&&f_backend_idle&&f_all_drained&&f_sv==0&&!rc_req_valid&&!qc_cmd_valid&&!k_rec_valid;
assign as_cfg_ready=as_initial_safe&&as_core_cfg_ready;
assign as_cfg_rsp_valid=as_core_cfg_valid&&!as_core_cfg_rearmed;
assign as_cfg_status=as_core_cfg_status;
assign as_retired=!as_busy&&!as_core_cfg_valid;
assign k_a_status=as_rsp_generation==as_bound_generation?as_core_status:4'd14;
always @(posedge clk)begin
 if(k_cold_rst)as_cfg_lease<=0;
 else if((as_cfg_valid&&as_cfg_ready)||(as_attempt_reset&&as_rearm_ready))as_cfg_lease<=1;
 else if(as_core_cfg_valid&&(as_core_cfg_rearmed||as_cfg_rsp_ready))as_cfg_lease<=0;
end
checkpoint_authority_reader authority(.clk(clk),.rst(k_cold_rst),.abort(1'b0),.cfg_permit(as_initial_safe||as_cfg_lease||as_attempt_reset),
.cfg_valid(as_cfg_valid&&as_initial_safe),.cfg_ready(as_core_cfg_ready),.cfg_design(as_cfg_design),.cfg_generation(as_cfg_generation),.cfg_primary(as_cfg_primary),.cfg_pool(as_cfg_pool),.cfg_allocator(as_cfg_allocator),.cfg_checkpoint(as_cfg_checkpoint),.cfg_nodes(as_cfg_nodes),.cfg_nets(as_cfg_nets),.cfg_capacity(as_cfg_capacity),
.rearm_valid(as_attempt_reset),.rearm_ready(as_rearm_ready),.cfg_rsp_valid(as_core_cfg_valid),.cfg_rsp_ready(as_core_cfg_rearmed||as_cfg_rsp_ready),.cfg_status(as_core_cfg_status),.cfg_rearmed(as_core_cfg_rearmed),.configured(as_configured),.bound_design(as_bound_design),.bound_generation(as_bound_generation),.bound_checkpoint(as_bound_checkpoint),
.req_valid(k_a_valid),.req_ready(k_a_ready),.req_design(k_a_design),.req_generation(as_bound_generation),.req_checkpoint(k_a_checkpoint),.req_node(k_a_node),.req_net(k_a_net),.req_cookie(k_a_cookie),.rsp_valid(k_a_rsp_valid),.rsp_ready(k_a_rsp_ready),.rsp_status(as_core_status),.rsp_design(k_a_rsp_design),.rsp_generation(as_rsp_generation),.rsp_checkpoint(k_a_rsp_checkpoint),.rsp_cookie(k_a_rsp_cookie),.rsp_refs(k_a_refs),.rsp_occupancy(k_a_occ),.busy(as_busy),.fault(as_fault),.drained(as_drained),
'''+','.join('.'+n+'(as_'+n+')'for n in re.findall(r'\bm_[A-Za-z0-9_]+\b',READER.read_text().split('\n);')[0]))+''');
'''
 # configured/bound outputs from service_ports already contain bound wires.
 body=body.replace('wire[2:0]as_core_cfg_status;wire[63:0]as_bound_design,as_bound_generation;wire[31:0]as_bound_checkpoint;', 'wire[2:0]as_core_cfg_status;')
 at=s.index(');\n')+3;s=s[:at]+body+s[at:];out['query_residency_system.sv']=s
 return out
if __name__=='__main__':
 for n,s in make().items():(HERE/n).write_text(s)
