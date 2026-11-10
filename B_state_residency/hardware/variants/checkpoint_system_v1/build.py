"""Wire shadow metadata and native publication barrier through full hierarchy."""
from pathlib import Path
HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/cold_axi_fixed_v1/sources')
STAGE=HERE.parent/'checkpoint_stage_v1'
LEAF=[('input',1,'jp_permit'),('input',2,'jp_publish'),('input',2,'jp_discard'),('input',2,'jp_load'),('input',2,'jp_ack'),('input',64,'jp_design'),('input',32,'jp_checkpoint'),('input',32,'jp_version'),('input',2,'jp_query'),('input',4,'jp_price'),('output',2,'jp_ready'),('output',2,'jp_reply'),('output',2,'jp_status'),('output',2,'jp_prepared'),('output',2,'jp_pubready'),('output',2,'jp_dropready'),('output',64,'jp_kdesign'),('output',64,'jp_cdesign'),('output',32,'jp_kcp'),('output',32,'jp_ccp'),('output',32,'jp_kver'),('output',32,'jp_cver'),('output',2,'jp_kquery'),('output',4,'jp_kprice'),('output',64,'jp_skdesign'),('output',64,'jp_scdesign'),('output',32,'jp_skcp'),('output',32,'jp_sccp'),('output',32,'jp_skver'),('output',32,'jp_scver'),('output',2,'jp_skquery'),('output',4,'jp_skprice')]
HOST=[('input',1,'jp_start'),('output',1,'jp_start_ready'),('input',1,'jp_commit'),('output',1,'jp_commit_ready'),('input',1,'jp_cancel'),('output',1,'jp_cancel_ready'),('output',1,'jp_owned'),('output',1,'jp_done'),('input',1,'jp_done_ready'),('output',2,'jp_result'),('input',1,'jp_manifest_ready'),('input',64,'jp_generation'),('input',64,'jp_design'),('input',32,'jp_checkpoint'),('input',32,'jp_version'),('input',2,'jp_query'),('input',4,'jp_price'),('input',2,'jp_load'),('input',2,'jp_ack'),('output',2,'jp_ready'),('output',2,'jp_reply'),('output',2,'jp_status'),('input',1,'jp_authority_stage')]
def decl(items,internal=False):
 return ''.join((('wire' if internal else d+' wire')+('' if w==1 else f'[{w-1}:0]')+' '+n+(';' if internal else ',')+'\n')for d,w,n in items)
def ports(s,items):
 i=s.index(')(\n')+3;return s[:i]+decl(items)+s[i:]
def rep(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def make():
 leaf=ports((BASE/'residency_system.sv').read_text(),LEAF)
 pre='''wire jp_kr,jp_cr,jp_kv,jp_cv,jp_ks,jp_cs;wire[2303:0]jp_effective;
assign jp_ready={jp_cr,jp_kr};assign jp_reply={jp_cv,jp_kv};assign jp_status={jp_cs,jp_ks};
assign jp_kdesign=k_saved_design;assign jp_kcp=k_saved_checkpoint;assign jp_cdesign=cf_saved_design;assign jp_ccp=cf_saved_checkpoint;
'''
 at=leaf.index('recovery_coordinator #');leaf=leaf[:at]+pre+leaf[at:]
 leaf=rep(leaf,' recovery_ctl(',''' recovery_ctl(.cfg_stage(jp_permit),.publish_valid(jp_publish[0]),.publish_permit(jp_permit),.discard_valid(jp_discard[0]),.publish_ready(jp_pubready[0]),.discard_ready(jp_dropready[0]),.staged_valid(jp_prepared[0]),.staged_design(jp_skdesign),.staged_checkpoint(jp_skcp),.staged_version(jp_skver),.active_version(jp_kver),.staged_query(jp_skquery),.active_query(jp_kquery),.staged_price(jp_skprice),.active_price(jp_kprice),''')
 leaf=rep(leaf,')config_restore(',''')config_restore(.load_stage(jp_permit),.publish_valid(jp_publish[1]),.publish_permit(jp_permit),.discard_valid(jp_discard[1]),.publish_ready(jp_pubready[1]),.discard_ready(jp_dropready[1]),.staged_valid(jp_prepared[1]),.staged_design(jp_scdesign),.staged_checkpoint(jp_sccp),.staged_version(jp_scver),.active_version(jp_cver),.staged_payload(),.active_payload(jp_effective),''')
 # Mux both request and response ownership; old replies must drain before jp_permit.
 for key,old,new in [('cfg_valid','fd_k_cfg_valid','jp_load[0]'),('cfg_ready','fd_k_cfg_ready','jp_kr'),('cfg_authoritative','fd_fa_authoritative&&as_configured&&as_bound_design==fd_fa_design&&as_bound_checkpoint==fd_fa_checkpoint&&as_bound_generation!=0',"1'b1"),('cfg_design','fd_fa_design','jp_design'),('cfg_checkpoint','fd_fa_checkpoint','jp_checkpoint'),('cfg_version','fd_fa_version','jp_version'),('cfg_query','fd_fa_query','jp_query'),('cfg_price','fd_fa_price','jp_price'),('cfg_rsp_valid','fd_k_cfg_rsp_valid','jp_kv'),('cfg_rsp_ready','fd_k_cfg_rsp_ready','jp_ack[0]'),('cfg_status','fd_k_cfg_status','jp_ks'),('load_valid','fd_cf_load_valid','jp_load[1]'),('load_ready','fd_cf_load_ready','jp_cr'),('load_authoritative','fd_fc_authoritative',"1'b1"),('load_payload','fd_fc_payload','jp_effective'),('load_design','fd_fc_design','jp_design'),('load_checkpoint','fd_fc_checkpoint','jp_checkpoint'),('load_rsp_valid','fd_cf_load_rsp_valid','jp_cv'),('load_rsp_ready','fd_cf_load_rsp_ready','jp_ack[1]'),('load_status','fd_cf_load_status','jp_cs')]:
  expr=new if key in ['cfg_ready','cfg_rsp_valid','cfg_status','load_ready','load_rsp_valid','load_status'] else f'jp_permit?{new}:({old})'
  leaf=rep(leaf,f'.{key}({old})',f'.{key}({expr})')
  if key in ['cfg_ready','cfg_rsp_valid','cfg_status','load_ready','load_rsp_valid','load_status']:
   leaf=leaf.replace(pre,pre+f'assign {old}=!jp_permit&&{new};\n');pre+=f'assign {old}=!jp_permit&&{new};\n'
 (HERE/'residency_system.sv').write_text(leaf)
 search=ports((BASE/'search_residency_system.sv').read_text(),LEAF)
 search=rep(search,')backend(',')backend('+''.join(f'.{n}({n}),'for _,_,n in LEAF))
 (HERE/'search_residency_system.sv').write_text(search)
 top=ports((BASE/'query_residency_system.sv').read_text(),HOST)
 internal=[x for x in LEAF if x[2] not in {y[2]for y in HOST}]
 top=rep(top,'wire boot_admin_allowed',decl(internal,True)+'''wire jp_prepare,jp_core_start_ready;wire[2:0]jp_pv,jp_dv;wire jp_ap,jp_apr,jp_adr;wire[63:0]jp_ad,jp_ag;wire[31:0]jp_ac;
wire jp_start_open=!cp_valid&&!qc_cp_valid&&!as_cfg_valid&&f_sv==0&&!k_rec_valid&&!boot_pending;
assign jp_start_ready=jp_core_start_ready&&jp_start_open;
assign jp_publish=jp_pv[2:1];assign jp_discard=jp_dv[2:1];assign jp_permit=pc_owned&&jp_owned;
wire boot_admin_allowed''')
 top=rep(top,')inner(',')inner('+''.join(f'.{n}('+("jp_prepare?jp_load:2'd0" if n=='jp_load' else n)+'),'for _,_,n in LEAF))
 top=rep(top,'checkpoint_authority_reader authority(','''checkpoint_authority_rotator authority(.cfg_stage(jp_authority_stage),.publish_valid(jp_pv[0]),.publish_permit(pc_owned&&jp_owned),.discard_valid(jp_dv[0]),.publish_ready(jp_apr),.discard_ready(jp_adr),.active_slot(),.staged_valid(jp_ap),.staged_design(jp_ad),.staged_generation(jp_ag),.staged_checkpoint(jp_ac),''')
 top=top.replace('as_initial_safe&&as_core_cfg_ready','(as_initial_safe||(jp_prepare&&jp_authority_stage))&&as_core_cfg_ready')
 top=top.replace('as_cfg_valid&&as_initial_safe','as_cfg_valid&&(as_initial_safe||(jp_prepare&&jp_authority_stage))')
 top=rep(top,'.cfg_permit(as_initial_safe||as_cfg_lease||as_attempt_reset)', '.cfg_permit(as_initial_safe||as_cfg_lease||as_attempt_reset||(pc_owned&&jp_owned))')
 top=rep(top,'.command_busy(cp_busy||qc_cp_busy||qc_pending||(boot_pending&&pc_owned))','.command_busy(cp_busy||qc_cp_busy||qc_pending||(boot_pending&&pc_owned)||jp_owned||as_cfg_lease||as_busy||(|jp_reply))')
 # Checkpoint stream commands cannot overlap publication metadata transaction.
 top=top.replace('!boot_done_held&&pc_owned','!boot_done_held&&!jp_owned&&pc_owned').replace('!boot_done_held&&!qc_cp_valid','!boot_done_held&&!jp_owned&&!qc_cp_valid').replace('.cp_valid(!boot_done_held&&cp_valid','.cp_valid(!boot_done_held&&!jp_owned&&cp_valid').replace('.cp_valid(!boot_done_held&&qc_cp_valid','.cp_valid(!boot_done_held&&!jp_owned&&qc_cp_valid')
 barrier='''
checkpoint_publish_barrier publication(.clk(clk),.rst(rst||k_cold_rst),.lease_owned(pc_owned),
.retired(pc_retired&&pc_route_retired&&as_drained&&as_retired&&!cp_busy&&!qc_cp_busy&&!qc_restore_pending),
.stage_busy(as_busy||as_cfg_lease||k_busy||(|jp_reply)),.fault(abort||as_fault||fault||rc_fault||k_fault||cf_fault||lr_fault||f_fault||ss_fault||qc_fault),.manifest_ready(jp_manifest_ready),
.start_valid(jp_start&&jp_start_open),.start_ready(jp_core_start_ready),.start_design(jp_design),.start_generation(jp_generation),.start_checkpoint(jp_checkpoint),.start_version(jp_version),.start_query(jp_query),.start_price(jp_price),
.commit_valid(jp_commit),.commit_ready(jp_commit_ready),.cancel_valid(jp_cancel),.cancel_ready(jp_cancel_ready),.owned(jp_owned),.prepare_allowed(jp_prepare),.done_valid(jp_done),.done_ready(jp_done_ready),.done_status(jp_result),
.prepared({jp_prepared,jp_ap}),.publish_ready({jp_pubready,jp_apr}),.discard_ready({jp_dropready,jp_adr}),.publish_valid(jp_pv),.discard_valid(jp_dv),
.a_design(as_bound_design),.a_generation(as_bound_generation),.a_checkpoint(as_bound_checkpoint),.k_design(jp_kdesign),.c_design(jp_cdesign),.k_checkpoint(jp_kcp),.c_checkpoint(jp_ccp),.k_version(jp_kver),.c_version(jp_cver),.k_query(jp_kquery),.k_price(jp_kprice),.journal_count(k_count),
.sa_design(jp_ad),.sa_generation(jp_ag),.sa_checkpoint(jp_ac),.sk_design(jp_skdesign),.sc_design(jp_scdesign),.sk_checkpoint(jp_skcp),.sc_checkpoint(jp_sccp),.sk_version(jp_skver),.sc_version(jp_scver),.sk_query(jp_skquery),.sk_price(jp_skprice));
'''
 top=rep(top,'endmodule',barrier+'endmodule');(HERE/'query_residency_system.sv').write_text(top)
 if __name__=='__main__':print('full hierarchy generated')
if __name__=='__main__':make()
