"""Build the boot-gated query root without changing archived baselines."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/bundle_capture_v3/sources')
def rep(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def make():
 s=(BASE/'query_residency_system.sv').read_text()
 ports='''input wire boot_required,boot_cfg_valid,output wire boot_cfg_ready,
input wire[63:0]boot_design,boot_generation,
input wire[31:0]boot_checkpoint,boot_version,boot_nodes,boot_label_count,boot_label_crc,boot_path_crc,boot_query_crc,
input wire[1:0]boot_query,boot_slots,input wire[3:0]boot_price,input wire[2303:0]boot_payload,
output wire boot_pending,boot_rsp_valid,input wire boot_rsp_ready,output wire[3:0]boot_status,
input wire boot_verify_valid,output wire boot_verify_ready,output wire[31:0]boot_verified_count,output wire[3:0]boot_verify_status,
output wire[4:0]boot_receipts,output wire[7:0]boot_config_receipts,
'''
 at=s.index(')(\n')+3;s=s[:at]+ports+s[at:]
 s=rep(s,'wire pc_safe;', 'wire boot_admin_allowed,boot_done_held;wire pc_safe;')
 s=rep(s,'assign qc_cp_ready=pc_owned', 'assign qc_cp_ready=!boot_done_held&&pc_owned')
 s=rep(s,'assign cp_ready=!qc_cp_valid', 'assign cp_ready=!boot_done_held&&!qc_cp_valid')
 s=rep(s,'assign as_cfg_ready=as_initial_safe&&as_core_cfg_ready;', 'assign as_cfg_ready=(!boot_pending||boot_admin_allowed)&&as_initial_safe&&as_core_cfg_ready;')
 s=rep(s,'.cfg_valid(as_cfg_valid&&as_initial_safe)', '.cfg_valid((!boot_pending||boot_admin_allowed)&&as_cfg_valid&&as_initial_safe)')
 s=rep(s,'.command_busy(cp_busy||qc_cp_busy||qc_pending)', '.command_busy(cp_busy||qc_cp_busy||qc_pending||(boot_pending&&pc_owned))')
 s=rep(s,'wire host_open=!qc_busy&&!qc_fault&&!pc_owned&&!as_cfg_lease;', '''wire host_base=!qc_busy&&!qc_fault&&!pc_owned&&!as_cfg_lease;
wire host_open=host_base&&!boot_pending;
wire boot_admin_open=host_base&&boot_admin_allowed;
wire[15:0]host_mask={16{host_open}}|({16{boot_admin_open}}&16'hc17f);''')
 s=rep(s,"assign f_sr=host_open?b_f_sr:16'd0;assign f_srv=host_open?b_f_srv:16'd0;", 'assign f_sr=b_f_sr&host_mask;assign f_srv=b_f_srv&host_mask;')
 s=s.replace('(host_open&&f_sv[i])','(host_mask[i]&&f_sv[i])').replace('(host_open&&f_srr[i])','(host_mask[i]&&f_srr[i])')
 s=s.replace('=host_open&&f_sv[i]','=host_mask[i]&&f_sv[i]').replace('=host_open&&f_srr[i]','=host_mask[i]&&f_srr[i]')
 s=rep(s,'assign b_k_rec_valid=!qc_busy', 'assign b_k_rec_valid=!boot_pending&&!qc_busy')
 s=rep(s,'assign k_rec_ready=!qc_busy', 'assign k_rec_ready=!boot_pending&&!qc_busy')
 s=rep(s,'.cp_valid(cp_valid&&pc_owned', '.cp_valid(!boot_done_held&&cp_valid&&pc_owned')
 s=rep(s,'.cp_valid(qc_cp_valid)', '.cp_valid(!boot_done_held&&qc_cp_valid)')
 s=rep(s,'.cmd_valid(qc_cmd_valid&&!pc_owned', '.cmd_valid(!boot_pending&&qc_cmd_valid&&!pc_owned')
 s=rep(s,'.admit(!qc_pending', '.admit(!boot_pending&&!qc_pending')
 s=rep(s,'wire[15:0]host_mask={16{host_open}}|({16{boot_admin_open}}&16\'hc17f);', """wire[15:0]host_mask={16{host_open}}|({16{boot_admin_open}}&16'hc17f);
// Accepted host requests retain a response route even if admission is canceled.
reg[15:0]host_reply_owned;
always @(posedge clk)begin
 if(rst||k_cold_rst)host_reply_owned<=0;
 else host_reply_owned<=(host_reply_owned|(f_sv&f_sr))&~(f_srv&f_srr);
end
wire[15:0]host_response_mask=host_mask|host_reply_owned;""")
 s=rep(s,'assign f_sr=b_f_sr&host_mask;assign f_srv=b_f_srv&host_mask;', 'assign f_sr=b_f_sr&host_mask;assign f_srv=b_f_srv&host_response_mask;')
 s=s.replace('host_mask[i]&&f_srr[i]', 'host_response_mask[i]&&f_srr[i]')
 gate='''
// Only consumed native transactions earn bootstrap receipts. No test hooks.
wire boot_retired=!rst&&!k_cold_rst&&!abort&&f_phase==0&&f_all_drained&&f_backend_idle&&f_normal_retired&&!qc_busy&&!qc_cp_busy&&!cp_busy&&!ss_busy&&!rc_busy&&!as_busy&&!k_busy&&!as_cfg_rsp_valid&&!as_cfg_valid&&!(|(f_sv&16'hc17f));
boot_restore_gate boot_gate(
.clk(clk),.cold_rst(k_cold_rst),.work_rst(rst||abort),.required(boot_required),
.cfg_valid(boot_cfg_valid),.cfg_ready(boot_cfg_ready),.cfg_design(boot_design),.cfg_generation(boot_generation),
.cfg_checkpoint(boot_checkpoint),.cfg_version(boot_version),.cfg_nodes(boot_nodes),.cfg_label_count(boot_label_count),.cfg_label_crc(boot_label_crc),.cfg_path_crc(boot_path_crc),.cfg_query_crc(boot_query_crc),
.cfg_query(boot_query),.cfg_slots(boot_slots),.cfg_price(boot_price),.cfg_payload(boot_payload),
.pending(boot_pending),.admin_allowed(boot_admin_allowed),.done_held(boot_done_held),.rsp_valid(boot_rsp_valid),.rsp_ready(boot_rsp_ready),.rsp_status(boot_status),.receipts(boot_receipts),.config_receipts(boot_config_receipts),
.verify_valid(boot_verify_valid),.verify_ready(boot_verify_ready),.verified_count(boot_verified_count),.verify_status(boot_verify_status),
.sv(f_sv),.sr(f_sr),.srv(f_srv),.srr(f_srr),.sp(f_sp),.rp(f_srp),
.owner_configured(owner_configured),.authority_configured(as_configured),.authority_design(as_bound_design),.authority_generation(as_bound_generation),.authority_checkpoint(as_bound_checkpoint),
.providers_configured(q_configured&&g_configured&&d_configured&&t_configured&&cs_configured),.active(p_active),.active_design(design_id),.active_version(query_version),.published_version(cs_published_version),
.active_query(p_active_query),.route_slots(rc_slots),.active_price(p_active_price),.recovery_permit(k_permit),.recovery_design(k_saved_design),.recovery_checkpoint(k_saved_checkpoint),
.path_accept(cp_valid&&cp_ready),.path_restore(cp_restore),.path_done(cp_rsp_valid&&cp_rsp_ready),.path_status(cp_status),.path_crc(cp_crc),
.query_accept(qc_cp_valid&&qc_cp_ready),.query_restore(qc_cp_restore),.query_done(qc_cp_rsp_valid&&qc_cp_rsp_ready),.query_status(qc_cp_status),.query_crc(qc_cp_crc),
.retired(boot_retired),.lease_owned(pc_owned));
'''
 s=rep(s,'endmodule',gate+'\nendmodule')
 return {'query_residency_system.sv':s,'boot_restore_gate.sv':(HERE/'boot_restore_gate.sv').read_text()}
if __name__=='__main__':
 for n,s in make().items():
  if n=='boot_restore_gate.sv':continue
  (HERE/n).write_text(s)
