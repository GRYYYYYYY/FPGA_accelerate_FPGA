from pathlib import Path
import runpy
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def make():
 s=runpy.run_path(str(ROOT/'hardware/variants/owner_cumulative_system_v1/build_tb.py'))['make']()
 # Declare before any instance uses (XSim2022.2 implicit-net declarations are not redeclarable).
 s=s.replace('reg jp_start=','reg g3_phase=0,g3_arm=0;integer g3_negative=0;wire g3_bundle_owned,g3_bundle_fault,g3_bundle_manifest;wire[2:0]g3_export_receipts;wire[31:0]g3_lcount,g3_lcrc,g3_pcrc,g3_qcrc;\nreg jp_start=',1)
 s=s.replace(' cumulative_g3_copy;', ' cumulative_g3_copy;\n publish_g3;',1)
 s=s.replace('pre_g3_pc_release_ready&&!g3_block;', 'pre_g3_pc_release_ready&&!g3_block&&!g3_bundle_owned;',1)
 s=s.replace('.jp_manifest_ready(snap_manifest&&label_manifest)', '.jp_manifest_ready(g3_phase ? g3_bundle_manifest : snap_manifest&&label_manifest)',1)
 s=s.replace(".jp_generation(64'h100000002)",".jp_generation(g3_phase ? 64'h100000003 : 64'h100000002)",1)
 s=s.replace(".jp_checkpoint(32'd18)",".jp_checkpoint(g3_phase ? 32'd19 : 32'd18)",1)
 # Keep all original G1/G2 bindings; select new descriptor only for actual G3 authority stage.
 for old,new in [("jp_authority_stage?64'h100000002:64'h100000001","jp_authority_stage ? (g3_phase ? 64'h100000003 : 64'h100000002) : 64'h100000001"),("jp_authority_stage?64'ha000000000:64'h91fffff000","jp_authority_stage ? (g3_phase ? 64'hc000000000 : 64'ha000000000) : 64'h91fffff000"),("jp_authority_stage?64'ha008aaff40:64'h9208aaef40","jp_authority_stage ? (g3_phase ? 64'hc008aaff40 : 64'ha008aaff40) : 64'h9208aaef40"),("jp_authority_stage?64'ha008b81dc0:64'h9208b80dc0","jp_authority_stage ? (g3_phase ? 64'hc008b81dc0 : 64'ha008b81dc0) : 64'h9208b80dc0"),("jp_authority_stage?32'd18:32'd17","jp_authority_stage ? (g3_phase ? 32'd19 : 32'd18) : 32'd17")]:
  assert old in s,old;s=s.replace(old,new,1)
 s=s.replace(".base2(64'h9208b80dc0),.size0(64'd146284032),.size1(64'd146284032),.size2(64'd0)",".base2(64'hc000000000),.size0(64'd146284032),.size1(64'd146284032),.size2(64'd146284032)",1)
 s=s.replace("as_bound_generation==64'h100000001 ? 64'h91fffff000 : 64'ha000000000", "as_bound_generation==64'h100000001 ? 64'h91fffff000 : (as_bound_generation==64'h100000002 ? 64'ha000000000 : 64'hc000000000)",1)
 # G3 uses the actual active query/price. G2 pins remain identical.
 s=s.replace(".cmd_query(2'd1),.cmd_price(4'd3),.cmd_nodes(32'd9089009),.cmd_cookie(32'h1abe0018)",".cmd_query(g3_phase ? p_active_query : 2'd1),.cmd_price(g3_phase ? p_active_price : 4'd3),.cmd_nodes(32'd9089009),.cmd_cookie(32'h1abe0018)",1)
 # Separate native source files and trace tags, preserving all old G2 capture evidence.
 s=s.replace('if(!$value$plusargs("warmimports=%s",warm_path))$fatal(1,"runtime label output path")','if(g3_phase)begin if(!$value$plusargs("g3imports=%s",warm_path))$fatal(1,"g3 label output path");end else if(!$value$plusargs("warmimports=%s",warm_path))$fatal(1,"runtime label output path")',1)
 s=s.replace('$fdisplay(trace,"LABEL_SNAPSHOT_BEGIN %0d",cycles);','begin if(g3_phase)$fdisplay(trace,"G3_LABEL_BEGIN %0d",cycles);else $fdisplay(trace,"LABEL_SNAPSHOT_BEGIN %0d",cycles);end;',1)
 s=s.replace('$fdisplay(trace,"LABEL_SNAPSHOT_DONE %0d %0d %0d %08h",cycles,ls_count,ls_pages,ls_crc);','begin if(g3_phase)$fdisplay(trace,"G3_LABEL_DONE %0d %0d %0d %08h",cycles,ls_count,ls_pages,ls_crc);else $fdisplay(trace,"LABEL_SNAPSHOT_DONE %0d %0d %0d %08h",cycles,ls_count,ls_pages,ls_crc);end;',1)
 s=s.replace('$fdisplay(trace,"FRAME_SCAN_REQUEST %0d %0d",cycles,scan_f)', 'begin if(g3_phase)$fdisplay(trace,"G3_FRAME_REQUEST %0d %0d",cycles,scan_f);else $fdisplay(trace,"FRAME_SCAN_REQUEST %0d %0d",cycles,scan_f);end',1)
 s=s.replace('$fdisplay(trace,"FRAME_SCAN_REPLY %0d %0d %0d %07h %0d",cycles,scan_st,scan_rf,scan_o,scan_pub)', 'begin if(g3_phase)$fdisplay(trace,"G3_FRAME_REPLY %0d %0d %0d %07h %0d",cycles,scan_st,scan_rf,scan_o,scan_pub);else $fdisplay(trace,"FRAME_SCAN_REPLY %0d %0d %0d %07h %0d",cycles,scan_st,scan_rf,scan_o,scan_pub);end',1)
 s=s.replace('$fdisplay(trace,"LABEL_SNAPSHOT_RECORD %0d %0d %040h",cycles,ls_node,ls_payload)', 'begin if(g3_phase)$fdisplay(trace,"G3_LABEL_RECORD %0d %0d %040h",cycles,ls_node,ls_payload);else $fdisplay(trace,"LABEL_SNAPSHOT_RECORD %0d %0d %040h",cycles,ls_node,ls_payload);end',1)
 # Existing export helper is also used after active G3 publication.
 s=s.replace('if(qcp_image[8]!=180327)$fatal(1,"g2 ledger floor")', 'if(qcp_image[8]!=(g3_phase ? 180328 : 180327))$fatal(1,"ledger floor")',1)
 extra='''
export_manifest g3_exports(.clk(clk),.rst(k_cold_rst),.lease(pc_owned),.arm(g3_arm),.abort(abort||owner_watch_fault||wm_owned||wm_fault),
 .source_write((owner_m_awvalid&&owner_m_awready)||(p_m_awvalid&&p_m_awready)),.published(g3_phase&&(&system.jp_pv)),
 .active_design(design_id),.target_generation(64'h100000003),.target_checkpoint(32'd19),.active_version(query_version),.active_sequence(system.controller.last_sequence),.active_query(p_active_query),.active_price(p_active_price),.active_slots(rc_slots),
 .selected_design(design_id),.selected_generation(64'h100000003),.selected_checkpoint(32'd19),.selected_version(query_version),.selected_query(p_active_query),.selected_price(p_active_price),
 .owner_manifest(g3_manifest),.label_manifest(label_manifest),
 .label_accept(ls_cmd&&ls_ready),.label_restore(1'b0),.label_done(ls_rsp&&ls_ack),.label_query(p_active_query),.label_price(p_active_price),.label_status(ls_status),.label_count(ls_count),.label_crc(ls_crc),
 .path_accept(cap_path_valid&&cap_path_ready),.path_restore(cap_path_restore),.path_done(cap_path_rsp_valid&&cap_path_rsp_ready),.path_word(cap_path_m_valid&&cap_path_m_ready),.path_status(cap_path_status),.path_index(cap_path_m_index),.path_data(cap_path_m_data),.path_crc(cap_path_crc),.path_last(cap_path_m_last),
 .query_accept(qc_cp_valid&&qc_cp_ready),.query_restore(qc_cp_restore),.query_done(qc_cp_rsp_valid&&qc_cp_rsp_ready),.query_word(qc_cp_m_valid&&qc_cp_m_ready),.query_status(qc_cp_status),.query_index(qc_cp_m_index),.query_data(qc_cp_m_data),.query_crc(qc_cp_crc),.query_last(qc_cp_m_last),
 .owned(g3_bundle_owned),.fault(g3_bundle_fault),.receipts(g3_export_receipts),.saved_label_count(g3_lcount),.saved_label_crc(g3_lcrc),.saved_path_crc(g3_pcrc),.saved_query_crc(g3_qcrc),.manifest_ready(g3_bundle_manifest));
task publish_g3;reg[1:0]accepted;begin
 g3_phase=1;ls_emitted=0;rc=$value$plusargs("g3negative=%d",g3_negative);
 @(negedge clk);g3_arm=1;@(negedge clk);g3_arm=0;
 runtime_label_snapshot;
 if(ls_count!=781||ls_pages!=393||g3_bundle_fault)$fatal(1,"G3 native label cardinality");
 cap_path_restore=0;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<78;x=x+1)begin
  wait(cap_path_m_valid);@(negedge clk);if(cap_path_m_index!=x||cap_path_m_last!=(x==77))$fatal(1,"G3 path boundary");cap_path_image[x]=cap_path_m_data;
  $fdisplay(trace,"G3_PATH_WORD %0d %0d %08h",cycles,x,cap_path_m_data);cap_path_m_ready=1;@(negedge clk);cap_path_m_ready=0;
 end
 wait(cap_path_rsp_valid);repeat(8)begin @(negedge clk);if(cap_path_status||cap_path_image[0]!=1||cap_path_image[39]!=1||pc_release_ready||!pc_owned)$fatal(1,"G3 path held");end
 $fdisplay(trace,"G3_PATH_RESULT %0d %08h",cycles,cap_path_crc);cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
 qc_cp_generation=64'h100000003;iter2_export_query;
 if({qcp_image[5],qcp_image[4]}!=64'h100000003||qcp_image[6]!=5||qcp_image[7]!=32'h57||qcp_image[8]!=180328||g3_bundle_fault||g3_export_receipts!=7)$fatal(1,"G3 query/bundle identity");
 for(integer x=0;x<10;x=x+1)$fdisplay(trace,"G3_QUERY_WORD %0d %0d %08h",cycles,x,qcp_image[x]);
 $fdisplay(trace,"G3_BUNDLE %0d %0d %08h %08h %08h %0d %0d %0d",cycles,g3_lcount,g3_lcrc,g3_pcrc,g3_qcrc,g3_receipt,g3_manifest,g3_bundle_manifest);
 if(!g3_negative&&!g3_bundle_manifest)$fatal(1,"G3 manifest before publication");
 joint_watch=0;
 @(negedge clk);jp_start=1;do @(posedge clk);while(!jp_start_ready);@(negedge clk);jp_start=0;
 jp_authority_stage=1;authority_bind=1;do @(posedge clk);while(!as_cfg_ready);@(negedge clk);authority_bind=0;
 wait(as_cfg_rsp_valid);repeat(8)begin @(negedge clk);if(as_cfg_status||system.jp_ap||as_bound_generation!=64'h100000002||k_count!=3||pc_release_ready)$fatal(1,"G3 authority held");
  $fdisplay(trace,"G3_AUTH_HELD %0d %0d %0d %0d %0d",cycles,g3_healthy,f_backend_idle,g3_receipt,g3_manifest);
 end
 authority_ack=1;@(negedge clk);authority_ack=0;wait(system.jp_ap);
 jp_load=3;while(jp_load!=0)begin @(posedge clk);accepted=jp_load&jp_ready;@(negedge clk);jp_load=jp_load&~accepted;end
 wait(jp_reply==3);repeat(8)begin @(negedge clk);if(jp_status||pc_release_ready||system.jp_prepared||k_count!=3||k_saved_checkpoint!=18)$fatal(1,"G3 metadata held");end
 jp_ack=3;@(negedge clk);jp_ack=0;wait(system.jp_prepared==3);
 if(g3_negative)begin
  repeat(64)begin @(negedge clk);if(g3_receipt||g3_manifest||g3_bundle_manifest||jp_commit_ready||as_bound_generation!=64'h100000002||k_saved_checkpoint!=18||k_count!=3||joint_pulses!=1||pc_release_ready||g3_bundle_fault||g3_export_receipts!=7)$fatal(1,"G3 negative containment");end
  $fdisplay(trace,"G3_PUBLISH_BLOCKED %0d %0d %0d %0d %0d",cycles,g3_receipt,g3_export_receipts,k_saved_checkpoint,k_count);$fflush(trace);$display("G3_NEGATIVE_OBSERVED");$finish;
 end
 if(!g3_bundle_manifest||g3_bundle_fault||k_saved_checkpoint!=18||k_count!=3||system.jp_ccp!=18)$fatal(1,"G3 prepared identity/manifest");
 jp_commit=1;do @(posedge clk);while(!jp_commit_ready);@(negedge clk);jp_commit=0;
 wait(jp_done);repeat(8)begin @(negedge clk);if(jp_result||pc_release_ready||k_count||k_saved_checkpoint!=19||system.jp_ccp!=19||as_bound_generation!=64'h100000003||joint_pulses!=2||g3_bundle_owned||g3_bundle_fault)$fatal(1,"G3 publication identity");end
 jp_done_ready=1;@(negedge clk);jp_done_ready=0;wait(!jp_owned);jp_authority_stage=0;
 ap_get(339193,26422,64'h100000002,1,0,0);
 ap_get(339193,26422,64'h100000003,0,1,1);ap_get(990179,26422,64'h100000003,0,2,2);ap_get(558358,26422,64'h100000003,0,4,2);ap_get(558358,23916,64'h100000003,0,1,2);ap_get(265324,26422,64'h100000003,0,5,1);
 qc_cp_generation=0;iter2_export_query;
 if({qcp_image[5],qcp_image[4]}!=64'h100000003||qc_cp_crc!=g3_qcrc||system.controller.last_sequence!=180328)$fatal(1,"G3 published query export");
 pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;wait(!pc_owned);
 $fdisplay(trace,"G3_PUBLISHED %0d %016h %0d %0d %0d %0d",cycles,as_bound_generation,k_saved_checkpoint,query_version,rc_slots,system.controller.last_sequence);$display("G3_PUBLISH_PASS");
end endtask
always @(posedge clk)if(!k_cold_rst&&g3_phase)begin
 if(g3_bundle_owned&&(!pc_owned||pc_release_ready))$fatal(1,"G3 bundle lost lease");
 if(g3_bundle_fault)$fatal(1,"G3 native export manifest fault");
end
'''
 return s.replace('\nendmodule',extra+'\nendmodule')
if __name__=='__main__':(HERE/'tb_g3_publish.sv').write_text(make())
