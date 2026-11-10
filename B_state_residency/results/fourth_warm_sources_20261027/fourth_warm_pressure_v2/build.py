"""Lease-owned read-only authority inspection through native root reader."""
from pathlib import Path
HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/checkpoint_system_v4/sources/query_residency_system.sv')
PORTS='''input wire ap_valid,ap_rsp_ready,output wire ap_ready,ap_rsp_valid,
input wire[63:0]ap_design,ap_generation,input wire[31:0]ap_checkpoint,ap_node,ap_net,ap_cookie,
output wire[63:0]ap_rsp_design,ap_rsp_generation,output wire[31:0]ap_rsp_checkpoint,ap_rsp_cookie,ap_refs,ap_occ,output wire[3:0]ap_status,
'''
def rep(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def make():
 s=BASE.read_text();i=s.index(')(\n')+3;s=s[:i]+PORTS+s[i:]
 s=rep(s,'wire jp_permit;','reg ap_owned;wire jp_permit;')
 wires='''wire ap_native_ready,ap_native_valid;
wire ap_allow=!rst&&!k_cold_rst&&!abort&&pc_owned&&!jp_owned&&!k_busy&&!k_rec_valid&&!as_cfg_lease&&!k_a_valid&&!ap_owned;
wire ap_offer=ap_allow&&ap_valid;
assign ap_ready=ap_allow&&ap_native_ready;
assign k_a_ready=!ap_offer&&!ap_owned&&ap_native_ready;
assign ap_rsp_valid=ap_owned&&ap_native_valid;
assign k_a_rsp_valid=!ap_owned&&ap_native_valid;
assign ap_rsp_design=k_a_rsp_design;assign ap_rsp_generation=as_rsp_generation;
assign ap_rsp_checkpoint=k_a_rsp_checkpoint;assign ap_rsp_cookie=k_a_rsp_cookie;
assign ap_refs=k_a_refs;assign ap_occ=k_a_occ;assign ap_status=as_core_status;
always @(posedge clk)begin
 if(k_cold_rst)ap_owned<=0;
 else if(ap_valid&&ap_ready)ap_owned<=1;
 else if(ap_rsp_valid&&ap_rsp_ready)ap_owned<=0;
end
'''
 s=rep(s,'checkpoint_authority_rotator authority(',wires+'checkpoint_authority_rotator authority(')
 for key,a,b in [('req_valid','k_a_valid','!ap_owned&&(k_a_valid||ap_offer)'),('req_ready','k_a_ready','ap_native_ready'),('req_design','k_a_design','ap_offer?ap_design:k_a_design'),('req_generation','as_bound_generation','ap_offer?ap_generation:as_bound_generation'),('req_checkpoint','k_a_checkpoint','ap_offer?ap_checkpoint:k_a_checkpoint'),('req_node','k_a_node','ap_offer?ap_node:k_a_node'),('req_net','k_a_net','ap_offer?ap_net:k_a_net'),('req_cookie','k_a_cookie','ap_offer?ap_cookie:k_a_cookie'),('rsp_valid','k_a_rsp_valid','ap_native_valid'),('rsp_ready','k_a_rsp_ready','ap_owned?ap_rsp_ready:k_a_rsp_ready')]:s=rep(s,f'.{key}({a})',f'.{key}({b})')
 s=rep(s,'wire jp_start_open=!cp_valid','wire jp_start_open=!ap_valid&&!ap_owned&&!cp_valid')
 s=rep(s,'.no_offers(f_sv==0', '.no_offers(!ap_valid&&f_sv==0')
 s=rep(s,'.command_busy(cp_busy', '.command_busy(ap_owned||cp_busy')
 s=rep(s,'.command_valid(cp_valid||qc_cp_valid)', '.command_valid(ap_valid||cp_valid||qc_cp_valid)')
 (HERE/'query_residency_system.sv').write_text(s)
if __name__=='__main__':make()
