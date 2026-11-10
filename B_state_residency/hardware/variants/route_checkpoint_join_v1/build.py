from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
BASE=ROOT/'results/recovery_retry_normal_v1/sources'
CP=ROOT/'results/route_checkpoint_unit_v8/sources/route_commit_controller.sv'
PORTS='''input wire cp_valid,cp_restore,
output wire cp_ready,cp_busy,cp_rsp_valid,input wire cp_rsp_ready,
output wire[3:0]cp_status,output wire[31:0]cp_crc,
input wire[63:0]cp_design,input wire[31:0]cp_nodes,cp_nets,cp_expected_crc,
input wire cp_s_valid,output wire cp_s_ready,input wire[31:0]cp_s_index,cp_s_data,input wire cp_s_last,
output wire cp_m_valid,input wire cp_m_ready,output wire[31:0]cp_m_index,cp_m_data,output wire cp_m_last,
input wire cp_test_reset,output wire pc_route_retired,
'''
NAMES=['cp_valid','cp_restore','cp_ready','cp_busy','cp_rsp_valid','cp_rsp_ready','cp_status','cp_crc','cp_design','cp_nodes','cp_nets','cp_expected_crc','cp_s_valid','cp_s_ready','cp_s_index','cp_s_data','cp_s_last','cp_m_valid','cp_m_ready','cp_m_index','cp_m_data','cp_m_last','cp_test_reset','pc_route_retired']
GUARD='`timescale 1ns/1ps\nmodule checkpoint_lease_guard(\n input wire clk,rst,acquire_valid,release_valid,healthy,retired,no_offers,route_retired,command_busy,command_valid,test_reset,\n output wire acquire_ready,release_ready,safe,output reg owned\n);\n assign acquire_ready=!rst&&!owned&&healthy&&route_retired&&no_offers&&!command_busy&&!test_reset;\n assign release_ready=!rst&&owned&&retired&&route_retired&&!command_busy&&!command_valid&&!test_reset;\n assign safe=!rst&&owned&&healthy;\n always @(posedge clk)begin\n  if(rst)owned<=0;\n  else if(acquire_valid&&acquire_ready)owned<=1;\n  else if(release_valid&&release_ready)owned<=0;\n end\nendmodule\n'
def rep(s,a,b):
 assert s.count(a)==1,a
 return s.replace(a,b)
def connect(names=NAMES,overrides=None):
 overrides=overrides or {};return ','.join('.'+n+'('+overrides.get(n,n)+')'for n in names)+','
def ports(s,root=False):
 at=s.index(')(\n')+3
 return s[:at]+PORTS+('input wire pc_acquire_valid,output wire pc_acquire_ready,output wire pc_owned,\ninput wire pc_release_valid,output wire pc_release_ready,\n'if root else'input wire pc_hold,pc_safe,\n')+s[at:]
def make():
 out={'route_commit_controller.sv':CP.read_text(),'checkpoint_lease_guard.sv':GUARD}
 s=ports((BASE/'route_commit_host_adapter.sv').read_text())
 s=rep(s,' .clk(clk),.rst(rst),.abort(abort)', ' '+connect([n for n in NAMES if n not in ['cp_test_reset','pc_route_retired']],{'cp_valid':'cp_valid&&pc_hold&&!cp_reset_held','cp_ready':'cp_core_ready'})+'.cp_safe(pc_safe&&pc_hold&&backend_drained&&!held&&!owner_pending),\n .clk(clk),.rst(rst||cp_reset_held),.abort(abort)')
 s=rep(s,' reg held;wire core_rsp_valid;',''' reg held;wire core_rsp_valid;wire cp_core_ready;wire owner_pending;reg cp_reset_held;
 assign cp_ready=pc_hold&&!cp_reset_held&&cp_core_ready;
 always @(posedge clk)begin
  if(rst)cp_reset_held<=0;
  else cp_reset_held<=cp_test_reset&&pc_hold&&pc_safe&&!held&&!owner_pending&&!cp_busy&&!cp_valid;
 end''')
 s=rep(s,'.lease(held||admit)' , '.lease(held||admit||pc_hold)')
 s=rep(s,' wire owner_pending=owner_send||owner_wait;', ' assign owner_pending=owner_send||owner_wait;\n assign pc_route_retired=!held&&!owner_pending&&!c_busy&&!core_rsp_valid&&!l_valid&&!o_valid;')
 out['route_commit_host_adapter.sv']=s
 s=ports((BASE/'residency_system.sv').read_text())
 s=rep(s,' route_join(.clk(clk)', ' route_join('+connect()+'.pc_hold(pc_hold),.pc_safe(pc_safe),.clk(clk)')
 out['residency_system.sv']=s
 s=ports((BASE/'search_residency_system.sv').read_text())
 # The extracted backend remains the same instance, with explicit checkpoint pins.
 at=s.index('residency_system #');b=s.index('backend(',at)+len('backend(');s=s[:b]+connect()+'.pc_hold(pc_hold),.pc_safe(pc_safe),'+s[b:]
 out['search_residency_system.sv']=s
 s=ports((BASE/'query_residency_system.sv').read_text(),True)
 s=rep(s,'wire host_open=!qc_busy&&!qc_fault;', '''// Acquire only with no previously offered normal request. Before acceptance,
// normal traffic proceeds unchanged; after it, no transaction can be retracted.
wire pc_quiet=!rst&&!k_cold_rst&&!abort&&p_active&&k_permit&&f_phase==0&&f_normal_retired&&f_backend_idle&&f_all_drained&&!qc_busy&&!ss_busy&&!qc_fault&&!ss_fault&&!fault&&!rc_fault&&!k_fault&&!cf_fault&&!lr_fault&&!f_fault&&!k_busy&&!f_recovery_owned;
wire pc_safe;
wire pc_retired=!rst&&!k_cold_rst&&f_normal_retired&&f_backend_idle&&f_all_drained&&!qc_busy&&!ss_busy&&!k_busy&&!f_recovery_owned&&(f_phase==0||f_phase==6);
checkpoint_lease_guard checkpoint_lease(.clk(clk),.rst(rst||k_cold_rst),.acquire_valid(pc_acquire_valid),.acquire_ready(pc_acquire_ready),.release_valid(pc_release_valid),.release_ready(pc_release_ready),.owned(pc_owned),.healthy(pc_quiet),.retired(pc_retired),.route_retired(pc_route_retired),.no_offers(f_sv==0&&!rc_req_valid&&!qc_cmd_valid&&!k_rec_valid),.command_busy(cp_busy),.command_valid(cp_valid),.test_reset(cp_test_reset),.safe(pc_safe));
wire host_open=!qc_busy&&!qc_fault&&!pc_owned;''')
 s=rep(s,'assign b_k_rec_valid=!qc_busy&&k_rec_valid;assign k_rec_ready=!qc_busy&&b_k_rec_ready;', 'assign b_k_rec_valid=!qc_busy&&!pc_owned&&k_rec_valid;assign k_rec_ready=!qc_busy&&!pc_owned&&b_k_rec_ready;')
 s=rep(s,'.cmd_valid(qc_cmd_valid)', '.cmd_valid(qc_cmd_valid&&!pc_owned)')
 s=rep(s,'.admit(k_permit&&', '.admit(!pc_owned&&k_permit&&')
 at=s.index('search_residency_system #');b=s.index('inner(',at)+len('inner(')
 s=s[:b]+connect(overrides={'cp_valid':'cp_valid&&pc_owned','cp_test_reset':'ENABLE_TEST_INJECTION&&pc_owned&&cp_test_reset'})+'.pc_hold(pc_owned),.pc_safe(pc_safe),'+s[b:]
 out['query_residency_system.sv']=s
 return out
if __name__=='__main__':
 for n,s in make().items():(HERE/n).write_text(s)
