"""Integrate receipt join with actual recovery handshake and native callbacks."""
from pathlib import Path
HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/checkpoint_commit_v6/sources')
LEAF=[('input',1,'wm_on'),('input',1,'wm_arm_ready'),('input',1,'wm_owned'),('input',1,'wm_joined'),('input',1,'wm_label_allow'),('input',1,'wm_fault'),('output',1,'wm_rec_offer'),('output',1,'wm_rec_accept'),('output',1,'wm_owner_repaired'),('output',1,'wm_label_accept'),('output',1,'wm_label_done'),('output',1,'wm_label_busy'),('output',4,'wm_label_status'),('output',32,'wm_label_cookie'),('output',32,'wm_label_written'),('output',32,'wm_label_verified'),('output',32,'wm_snapshot_cookie'),('output',32,'wm_snapshot_count')]
HOST=[('input',1,'wm_enable'),('input',32,'wm_source_version'),('input',2,'wm_source_query'),('input',4,'wm_source_price'),('input',32,'wm_path_crc'),('input',32,'wm_query_crc'),('output',1,'wm_owned'),('output',1,'wm_fault'),('output',1,'wm_joined'),('output',3,'wm_receipts')]
def decl(items,local=False):return ''.join(('wire'if local else d+' wire')+(''if w==1 else f'[{w-1}:0]')+' '+n+(';'if local else ',')+'\n'for d,w,n in items)
def ports(s,items):i=s.index(')(\n')+3;return s[:i]+decl(items)+s[i:]
def rep(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def make():
 s=ports((BASE/'residency_system.sv').read_text(),LEAF)
 s=rep(s,'wire k_labels_done;', '''wire wm_native_recover_ready;
assign f_brecover_ready=wm_native_recover_ready&&(!wm_on||wm_arm_ready);
assign wm_rec_offer=f_brecover_valid;assign wm_rec_accept=f_brecover_valid&&f_brecover_ready;
assign wm_owner_repaired=k_labels_valid;
assign wm_label_accept=lr_start_valid&&lr_start_ready;
assign wm_label_done=lr_rsp_valid&&lr_rsp_ready;
assign wm_label_busy=lr_busy;assign wm_label_status=lr_rsp_status;assign wm_label_cookie=lr_rsp_cookie;
assign wm_label_written=lr_written;assign wm_label_verified=lr_verified;
assign wm_snapshot_cookie=snapshot_cookie_held;assign wm_snapshot_count=snapshot_count_held;
wire k_labels_done;''')
 # Declarations must precede assignments in VRFC2022.2; move observation block to instances.
 a=s.index('assign f_brecover_ready=wm_native');b=s.index('wire k_labels_done;',a);observe=s[a:b];s=s[:a]+s[b:];i=s.index('assign lr_start_valid=');s=s[:i]+observe+s[i:]
 s=rep(s,'assign k_labels_done=lr_rsp_valid;', 'assign k_labels_done=wm_on?wm_joined:lr_rsp_valid;')
 s=rep(s,'assign lr_start_valid=k_labels_valid;', 'assign lr_start_valid=k_labels_valid&&(!wm_on||wm_label_allow);')
 s=rep(s,'assign lr_rsp_ready=!k_labels_valid;', 'assign lr_rsp_ready=wm_on?wm_owned:!k_labels_valid;')
 s=rep(s,'.recover_valid(f_brecover_valid),.recover_ready(f_brecover_ready)', '.recover_valid(f_brecover_valid&&(!wm_on||wm_arm_ready)),.recover_ready(wm_native_recover_ready)')
 s=rep(s,'.abort(as_fault||f_fault||cf_fault', '.abort((wm_on&&wm_fault)||as_fault||f_fault||cf_fault')
 s=rep(s,')label_restore(.clk(clk),.rst(k_cold_rst||k_attempt_reset),.abort(1\'b0)', ")label_restore(.clk(clk),.rst(k_cold_rst||k_attempt_reset),.abort(wm_on&&(wm_fault||abort))")
 s=rep(s,'assign recover_open=k_permit&&!f_recovery_owned&&!k_rec_valid;', 'assign recover_open=k_permit&&!f_recovery_owned&&!k_rec_valid&&!(wm_on&&(wm_owned||wm_fault));')
 (HERE/'residency_system.sv').write_text(s)
 s=ports((BASE/'search_residency_system.sv').read_text(),LEAF);s=rep(s,')backend(',')backend('+''.join(f'.{n}({n}),'for _,_,n in LEAF));(HERE/'search_residency_system.sv').write_text(s)
 s=ports((BASE/'query_residency_system.sv').read_text(),HOST);s=rep(s,'ENABLE_TEST_INJECTION=0','ENABLE_TEST_INJECTION=0,ENABLE_WARM_RECOVERY=0')
 internals=[x for x in LEAF if x[2]not in {y[2]for y in HOST}]
 insert=decl(internals,True)+'''wire wm_safe,wm_path_allow,wm_query_allow;
reg wm_attempt;reg[31:0]wm_src_version,wm_pcrc,wm_qcrc,wm_rversion,wm_rcp,wm_rcookie;reg[1:0]wm_src_query,wm_rquery;reg[3:0]wm_src_price,wm_rprice;reg[63:0]wm_rdesign;
assign wm_on=wm_owned?wm_attempt:((ENABLE_WARM_RECOVERY!=0)&&wm_enable&&wm_rec_offer);
always @(posedge clk)begin
 if(k_cold_rst)begin wm_attempt<=0;wm_src_version<=0;wm_src_query<=0;wm_src_price<=0;wm_pcrc<=0;wm_qcrc<=0;wm_rversion<=0;wm_rcp<=0;wm_rcookie<=0;wm_rquery<=0;wm_rprice<=0;wm_rdesign<=0;end
 else if(k_rec_valid&&k_rec_ready)begin
  wm_attempt<=(ENABLE_WARM_RECOVERY!=0)&&wm_enable;
  wm_src_version<=wm_source_version;wm_src_query<=wm_source_query;wm_src_price<=wm_source_price;wm_pcrc<=wm_path_crc;wm_qcrc<=wm_query_crc;
  wm_rversion<=recover_version;wm_rquery<=recover_query;wm_rprice<=recover_price;wm_rdesign<=recover_design;wm_rcp<=recover_checkpoint;wm_rcookie<=recover_cookie;
 end
end
'''
 s=rep(s,'reg ap_owned;',insert+'reg ap_owned;')
 s=rep(s,')inner(',')inner('+''.join(f'.{n}({n}),'for _,_,n in LEAF))
 for field,held in [('version','wm_rversion'),('query','wm_rquery'),('price','wm_rprice'),('design','wm_rdesign'),('checkpoint','wm_rcp'),('cookie','wm_rcookie')]:s=rep(s,f'.recover_{field}(recover_{field})',f'.recover_{field}(wm_owned?{held}:recover_{field})')
 s=rep(s,'assign qc_cp_ready=!boot_done_held&&!jp_owned&&pc_owned', 'assign qc_cp_ready=!boot_done_held&&!jp_owned&&(wm_owned?(wm_query_allow&&qc_cp_restore):pc_owned)')
 s=rep(s,'assign cp_ready=!boot_done_held&&!jp_owned&&!qc_cp_valid', 'assign cp_ready=!boot_done_held&&!jp_owned&&(!wm_owned||(wm_path_allow&&cp_restore))&&!qc_cp_valid')
 s=rep(s,'.cp_valid(!boot_done_held&&!jp_owned&&cp_valid&&pc_owned', '.cp_valid(!boot_done_held&&!jp_owned&&cp_valid&&(wm_owned?(wm_path_allow&&cp_restore):pc_owned)')
 s=rep(s,'.pc_hold(pc_owned),.pc_safe(pc_safe)', '.pc_hold(pc_owned||wm_owned),.pc_safe(wm_owned?wm_safe:pc_safe)')
 s=rep(s,'query_lifecycle controller(','''query_lifecycle #(.ENABLE_REBASE(1)) controller(.cp_rebase(wm_owned),.cp_rebase_permit(wm_safe),.cp_source_version(wm_src_version),.cp_source_query(wm_src_query),.cp_source_price(wm_src_price),''')
 s=rep(s,'.cp_valid(!boot_done_held&&!jp_owned&&qc_cp_valid)', '.cp_valid(!boot_done_held&&!jp_owned&&qc_cp_valid&&(!wm_owned||(wm_query_allow&&qc_cp_restore)))')
 s=rep(s,'.cp_safe(pc_owned&&pc_safe&&!qc_reset_held)', '.cp_safe((wm_owned?wm_safe:(pc_owned&&pc_safe))&&!qc_reset_held)')
 s=rep(s,'wire host_base=!qc_busy', 'wire host_base=!wm_owned&&!qc_busy')
 s=rep(s,'.admit(!boot_pending&&!qc_pending', '.admit(!wm_owned&&!boot_pending&&!qc_pending')
 # Keep all old response routes. Only administrator admission is qualified.
 gate='''
wire wm_retired=f_normal_retired&&f_backend_idle&&f_all_drained&&!qc_busy&&!ss_busy&&!cp_busy&&!qc_cp_busy&&!wm_label_busy&&!as_busy&&!as_cfg_lease&&!as_core_cfg_valid&&!ap_owned;
warm_restore_receipt_join warm_join(.clk(clk),.cold_rst(k_cold_rst),.abort(abort),.recovery_owned(f_recovery_owned),.backend_drained(f_all_drained),.retired(wm_retired),.owner_repaired(wm_owner_repaired),
.arm_valid(wm_on&&wm_rec_accept),.arm_ready(wm_arm_ready),.arm_design(wm_owned?wm_rdesign:recover_design),.arm_generation(as_bound_generation),.bound_design(as_bound_design),.bound_generation(as_bound_generation),.arm_checkpoint(wm_owned?wm_rcp:recover_checkpoint),.bound_checkpoint(as_bound_checkpoint),.arm_version(wm_owned?wm_rversion:recover_version),.active_version(query_version),.arm_query(wm_owned?wm_rquery:recover_query),.active_query(p_active_query),.arm_price(wm_owned?wm_rprice:recover_price),.active_price(p_active_price),.arm_cookie(wm_owned?wm_snapshot_cookie:snapshot_cookie),.arm_labels(wm_owned?wm_snapshot_count:snapshot_count),.arm_path_crc(wm_owned?wm_pcrc:wm_path_crc),.arm_query_crc(wm_owned?wm_qcrc:wm_query_crc),
.label_accept(wm_label_accept),.label_done(wm_label_done),.label_status(wm_label_status),.label_cookie(wm_label_cookie),.label_written(wm_label_written),.label_verified(wm_label_verified),
.path_accept(cp_valid&&cp_ready),.path_restore(cp_restore),.path_done(cp_rsp_valid&&cp_rsp_ready),.path_status(cp_status),.path_crc(cp_crc),
.query_accept(qc_cp_valid&&qc_cp_ready),.query_restore(qc_cp_restore),.query_done(qc_cp_rsp_valid&&qc_cp_rsp_ready),.query_status(qc_cp_status),.query_crc(qc_cp_crc),
.completion_consumed(k_rsp_valid&&k_rsp_ready),.owned(wm_owned),.label_allow(wm_label_allow),.admin_safe(wm_safe),.path_allow(wm_path_allow),.query_allow(wm_query_allow),.joined(wm_joined),.fault(wm_fault),.receipts(wm_receipts));
'''
 # Ignore ordinary label/path/query observations while unarmed: module IDLE does.
 s=rep(s,'endmodule',gate+'endmodule');(HERE/'query_residency_system.sv').write_text(s)
if __name__=='__main__':make()
