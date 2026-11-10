from pathlib import Path
import runpy
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'iter2_pair_v1/build_tb.py'
def make():
 s=runpy.run_path(str(BASE))['make']()
 s=s.replace(' iter2_next_query;',' iter2_publish_g2;\n iter2_next_query;',1)
 s=s.replace('ap_rsp_generation!=generation','ap_rsp_generation!=as_bound_generation')
 s=s.replace(".ap_checkpoint(32'd17)",'.ap_checkpoint(k_saved_checkpoint)').replace('ap_rsp_checkpoint!=17','ap_rsp_checkpoint!=k_saved_checkpoint')
 old=s[s.index('task joint_commit_check;'):s.index(' ap_get(0,4754',s.index('task joint_commit_check;'))]
 body=old.split('begin\n',1)[1].replace('k_count!=6','k_count!=4').replace('last_sequence!=1','last_sequence!=180327')
 extra='''
task iter2_export_query;begin
 qcp_start(0);
 for(integer x=0;x<10;x=x+1)begin
  wait(qc_cp_m_valid);@(negedge clk);if(qc_cp_m_index!=x||qc_cp_m_last!=(x==9))$fatal(1,"g2 ledger boundary");qcp_image[x]=qc_cp_m_data;qc_cp_m_ready=1;@(negedge clk);qc_cp_m_ready=0;
 end
 qcp_result(0);if(qcp_image[8]!=180327)$fatal(1,"g2 ledger floor");
end endtask
task iter2_publish_g2;reg[1:0]accepted;begin
 @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;
 cap_path_restore=0;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<78;x=x+1)begin
  wait(cap_path_m_valid);@(negedge clk);if(cap_path_m_index!=x||cap_path_m_last!=(x==77))$fatal(1,"g2 path export");cap_path_image[x]=cap_path_m_data;cap_path_m_ready=1;@(negedge clk);cap_path_m_ready=0;
 end
 wait(cap_path_rsp_valid);@(negedge clk);if(cap_path_status||cap_path_image[0]!=1||cap_path_image[39]!=0)$fatal(1,"g2 path export status");warm_pcrc=cap_path_crc;cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
 qc_cp_generation=64'h100000002;iter2_export_query;warm_qcrc=qc_cp_crc;
 if({qcp_image[5],qcp_image[4]}!=64'h100000002||system.as_bound_generation!=64'h100000001||k_count!=4)$fatal(1,"g2 source capture identity");
 $fdisplay(trace,"G2_CAPTURE %0d %08h %08h %0d",cycles,warm_pcrc,warm_qcrc,system.controller.last_sequence);
'''+body+'''
 ap_get(339193,26422,64'h100000001,1,0,0);
 ap_get(339193,26422,64'h100000002,0,1,1);ap_get(990179,26422,64'h100000002,0,1,2);ap_get(558358,26422,64'h100000002,0,3,2);ap_get(265324,26422,64'h100000002,0,4,1);
 qc_cp_generation=0;iter2_export_query;if({qcp_image[5],qcp_image[4]}!=64'h100000002||qc_cp_crc!=warm_qcrc)$fatal(1,"g2 active export differs candidate");
 qc_cp_expected_crc=qc_cp_crc;qcp_load(0);if(qc_restore_pending||system.controller.last_sequence!=180327)$fatal(1,"g2 active ledger import");
 pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;wait(!pc_owned);
 $fdisplay(trace,"ITER2_G2_PUBLISHED %0d %0d %0d %016h",cycles,k_saved_checkpoint,k_count,as_bound_generation);
end endtask
'''
 return s.replace('\nendmodule',extra+'\nendmodule')
if __name__=='__main__':HERE.joinpath('tb_g2.sv').write_text(make())
