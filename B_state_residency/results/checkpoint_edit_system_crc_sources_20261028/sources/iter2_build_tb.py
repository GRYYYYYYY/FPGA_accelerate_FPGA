from pathlib import Path
import runpy
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def make():
 s=runpy.run_path(str(ROOT/'hardware/variants/owner_g3_publish_v1/build_fixed_tb.py'))['make']()
 s=s.replace('.source_protocol_ok(!owner_watch_fault),', '.publication_retired(owner_drained&&f_all_drained&&f_backend_idle&&f_normal_retired&&!qc_busy&&!ss_busy&&!rc_busy&&!as_busy&&!system.as_cfg_lease&&!system.as_core_cfg_valid&&!k_busy&&!(|jp_reply)&&!qc_cp_busy&&!cap_path_busy),.source_protocol_ok(!owner_watch_fault),',1)
 old=' if(!g3_bundle_manifest||g3_bundle_fault||k_saved_checkpoint!=18||k_count!=3||system.jp_ccp!=18)$fatal(1,"G3 prepared identity/manifest");'
 new=''' for(integer n=0;n<64&&(g3_bundle_manifest!==1'b1);n=n+1)begin
  @(negedge clk);$fdisplay(trace,"G3_RETIRE_WAIT %0d %0d %0d %0d %0d %0d",cycles,g3_receipt,g3_manifest,g3_bundle_manifest,k_permit,g3_writer.publication_retired);
 end
 if(g3_bundle_manifest!==1'b1||g3_bundle_fault||k_saved_checkpoint!=18||k_count!=3||system.jp_ccp!=18||k_permit)$fatal(1,"G3 prepared identity/retired manifest");
 $fdisplay(trace,"G3_PREPARED_PROOF %0d %0d %0d %0d %0d %0d",cycles,g3_receipt,g3_manifest,g3_bundle_manifest,k_permit,g3_writer.publication_retired);'''
 assert old in s;s=s.replace(old,new,1)
 s=s.replace('module tb_candidate_offer;', '`default_nettype none\nmodule tb_candidate_offer;',1)
 s=s.replace('always @(posedge clk)if(!k_cold_rst&&g3_phase)begin', 'always @(posedge clk)if(!k_cold_rst&&g3_phase)begin\n if($isunknown(g3_writer.publication_retired))$fatal(1,"unknown native publication retirement");',1)
 return s+'\n`default_nettype wire\n'
if __name__=='__main__':(HERE/'tb_g3_publish.sv').write_text(make())
