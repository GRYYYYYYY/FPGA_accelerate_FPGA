"""G3 warm recovery after the second q3 commit write, without a cold reset."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = Path('/tmp/B_state_residency_offer_20261025/path_capacity_third_full_v1')

RESTORE = r'''
task third_warm_restore;begin
 q_cfg_valid=0;g_cfg_valid=0;d_cfg_valid=0;t_cfg_valid=0;owner_cfg_valid=0;cs_cfg_valid=0;host_ctrl_valid=0;host_design_req_valid=0;host_io_valid=0;host_owner_req_valid=0;cc_req_valid=0;expand_valid=0;seed_valid=0;cs_req_valid=0;k_cfg_valid=0;cf_load_valid=0;rc_req_valid=0;
 recovering=1;armed=0;as_recover_version=6;as_recover_query=0;crc_pin_flip=0;retry_cookie=32'hc0030001;
 warm_pcrc=g3_saved_pcrc;warm_qcrc=g3_saved_qcrc;
 if(g3_saved_count!=781||ls_count!=781||ls_crc!=g3_saved_lcrc||k_count!=3||k_saved_checkpoint!=19||as_bound_generation!=64'h100000003)$fatal(1,"G3 warm descriptor");
 $fdisplay(trace,"THIRD_WARM_START %0d %0d %0d %08h %08h %08h",cycles,k_count,k_saved_checkpoint,g3_saved_lcrc,warm_pcrc,warm_qcrc);
 k_rec_valid=1;do @(posedge clk);while(!k_rec_ready);@(negedge clk);k_rec_valid=0;
 wait(k_rcfg_valid);@(negedge clk);restore_epoch=k_new_query;restore_version=k_new_version;
 wait(k_labels_valid);@(negedge clk);
 if(k_count!=3||k_corrected!=1||!wm_owned||wm_fault||as_bound_generation!=64'h100000003)$fatal(1,"G3 warm owner repair corrected=%0d journal=%0d",k_corrected,k_count);
 $fdisplay(trace,"THIRD_WARM_OWNER %0d %0d %0d",cycles,k_corrected,k_count);
 if(!$value$plusargs("g3imports=%s",warm_path))$fatal(1,"G3 warm source path");warm_fd=$fopen(warm_path,"r");if(!warm_fd)$fatal(1,"G3 warm source open");
 for(integer x=0;x<g3_saved_count;x=x+1)begin
  rc=$fscanf(warm_fd,"%d",import_node);if(rc!=1)$fatal(1,"G3 import node");
  for(integer f=0;f<5;f=f+1)begin rc=$fscanf(warm_fd,"%h",word);if(rc!=1)$fatal(1,"G3 import field");import_record[f*32+:32]=word;end
  @(negedge clk);lr_s_valid=1;lr_s_node=import_node;lr_s_payload=import_record;lr_s_last=x+1==g3_saved_count;do @(posedge clk);while(!lr_s_ready);@(negedge clk);lr_s_valid=0;
 end
 $fclose(warm_fd);
 wait(wm_receipts[0]);
 if(lr_source_crc!=g3_saved_lcrc||lr_written!=781||lr_verified!=781||wm_joined||k_rsp_valid)$fatal(1,"G3 label receipt");
 $fdisplay(trace,"THIRD_WARM_LABELS %0d %0d %0d %08h",cycles,lr_written,lr_verified,lr_source_crc);
 cap_path_restore=1;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<117;x=x+1)begin
  @(negedge clk);warm_pi=x;warm_pd=g3_saved_path[x];warm_plast=x==116;warm_psv=1;do @(posedge clk);while(!system.cp_s_ready);@(negedge clk);warm_psv=0;
  $fdisplay(trace,"THIRD_WARM_PATH %0d %0d %08h",cycles,x,g3_saved_path[x]);
 end
 wait(cap_path_rsp_valid);repeat(8)begin @(negedge clk);
  if(cap_path_status||cap_path_crc!=g3_saved_pcrc||wm_receipts!=1||wm_joined||k_rsp_valid||!wm_owned||recover_open||pc_owned)$fatal(1,"G3 path held");
 end
 cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
 qc_cp_restore=1;qc_cp_expected_crc=g3_saved_qcrc;qc_cp_generation=0;qc_cp_valid=1;do @(posedge clk);while(!qc_cp_ready);@(negedge clk);qc_cp_valid=0;
 for(integer x=0;x<10;x=x+1)begin
  @(negedge clk);qc_cp_s_index=x;qc_cp_s_data=g3_saved_query[x];qc_cp_s_last=x==9;qc_cp_s_valid=1;do @(posedge clk);while(!qc_cp_s_ready);@(negedge clk);qc_cp_s_valid=0;
  $fdisplay(trace,"THIRD_WARM_QUERY %0d %0d %08h",cycles,x,g3_saved_query[x]);
 end
 wait(qc_cp_rsp_valid);repeat(8)begin @(negedge clk);
  if(qc_cp_status||qc_cp_crc!=g3_saved_qcrc||wm_receipts!=3||wm_joined||k_rsp_valid||!wm_owned||recover_open)$fatal(1,"G3 query held");
 end
 qc_cp_rsp_ready=1;@(negedge clk);qc_cp_rsp_ready=0;
 wait(k_rsp_valid);repeat(8)begin @(negedge clk);
  if(k_rsp_status||k_rsp_cookie!=32'hc0030001||k_corrected!=1||k_count||!wm_owned||!wm_joined||wm_fault||recover_open||rc_slots!=3||system.controller.last_sequence!=180328)$fatal(1,"G3 warm complete");
  $fdisplay(trace,"THIRD_WARM_HELD %0d %0d %0d %0d %0d %0d %0d",cycles,k_rsp_status,k_corrected,k_count,wm_receipts,wm_owned,recover_open);
 end
 k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;wait(recover_open);
 if(wm_owned||query_version!=6||p_active_query!=0||p_active_price!=6||rc_slots!=3||system.controller.last_sequence!=180328||k_saved_checkpoint!=19)$fatal(1,"G3 warm release");
 $fdisplay(trace,"THIRD_WARM_RELEASE %0d %0d %0d %0d %0d %0d",cycles,query_version,p_active_query,p_active_price,rc_slots,system.controller.last_sequence);
 owner_op(0,339193,1,1);owner_op(0,990179,2,2);owner_op(0,558358,4,2);owner_op(0,265324,5,1);iter2_foreign_probe;
end endtask
'''


def make():
    m = json.loads((BASE / 'manifest.json').read_text())
    assert json.loads((BASE / 'source_bound_audit.json').read_text())['status'] == 'passed'
    s = (BASE / 'sources/tb_query_fault.sv').read_text()
    assert hashlib.sha256(s.encode()).hexdigest() == m['sources']['tb_query_fault.sv']['sha256']
    s = s.replace('reg wm_enable=0;', 'reg g3_warm_mode=0;reg wm_enable=0;', 1)
    for old, new in [
        ('.wm_source_version(32\'d3)', '.wm_source_version(g3_warm_mode?32\'d5:32\'d3)'),
        ('.wm_source_query(2\'d1)', '.wm_source_query(g3_warm_mode?2\'d3:2\'d1)'),
        ('.wm_source_price(4\'d3)', '.wm_source_price(g3_warm_mode?4\'d5:4\'d3)'),
        ('.recover_checkpoint(wm_enable?32\'d18:32\'d17)', '.recover_checkpoint(g3_warm_mode?32\'d19:(wm_enable?32\'d18:32\'d17))'),
        ('.snapshot_checkpoint(wm_enable?32\'d18:32\'d17)', '.snapshot_checkpoint(g3_warm_mode?32\'d19:(wm_enable?32\'d18:32\'d17))'),
    ]:
        assert s.count(old) == 1, old
        s = s.replace(old, new)
    s = s.replace('cycles>4000000', 'cycles>8000000')
    start = s.index('task third_query;begin\n')
    split = s.index(' $fclose(fd_gold);', start)
    preparation = s[start + len('task third_query;begin\n'):split]
    s = s[:start] + '''reg[31:0]g3_saved_path[0:116],g3_saved_query[0:9];
reg[31:0]g3_saved_pcrc,g3_saved_qcrc,g3_saved_lcrc,g3_saved_count;
task third_prepare;begin
''' + preparation + '''end endtask
task third_query;begin
 for(integer x=0;x<117;x=x+1)g3_saved_path[x]=cap_path_image[x];
 for(integer x=0;x<10;x=x+1)g3_saved_query[x]=qcp_image[x];
 g3_saved_pcrc=g3_pcrc;g3_saved_qcrc=g3_qcrc;g3_saved_lcrc=g3_lcrc;g3_saved_count=g3_lcount;
 third_prepare;
''' + s[split:]
    start = s.index('task third_query;begin\n')
    old = ' autonomous_query;\n'
    pos = s.index(old, start)
    s = s[:pos] + r'''
 g3_warm_mode=1;replayed=0;armed=1;injection_seen=0;fault_case=5;wm_enable=1;warm_fault_node=558358;warm_running=1;
 // Keep recovering asserted until this task explicitly submits the new descriptor.
 recovering=1;
 $fdisplay(trace,"THIRD_FAULT_BEGIN %0d",cycles);
 fault_query;
 if(commits!=302||candidate_i!=565||expand_i!=113||poll_i!=114||qc_rsp_status!=7||qc_rsp_detail!=5||qc_rsp_committed||k_count!=3)$fatal(1,"G3 fault numerical/journal result");
 $fdisplay(trace,"THIRD_FAULT_DONE %0d %0d %0d %0d %0d",cycles,poll_i,expand_i,candidate_i,commits);
 third_warm_restore;
 third_prepare;
 rc=$fseek(polls_fd,0,0);if(rc)$fatal(1,"third poll rewind");rc=$fseek(candidates_fd,0,0);if(rc)$fatal(1,"third candidate rewind");rc=$fseek(fd_gold,0,0);if(rc)$fatal(1,"third cost rewind");
 poll_i=0;expand_i=0;candidate_i=0;commits=0;outputs=0;offers=0;count2=0;physical_expands=0;metadata_calls=0;visited_reads=0;stopped=0;replayed=1;warm_running=0;
 $fdisplay(trace,"THIRD_RETRY_BEGIN %0d",cycles);
 autonomous_query;
''' + s[pos + len(old):]
    # Only q3's final context assertions change; the earlier G2 prefix stays exact.
    start = s.index('task third_query;begin\n')
    tail = s[start:].replace('query_version!=5||p_active_query!=3||p_active_price!=5', 'query_version!=6||p_active_query!=0||p_active_price!=6')
    tail = tail.replace("qcp_image[6]!=5||qcp_image[7]!=32'h57", "qcp_image[6]!=6||qcp_image[7]!=32'h58")
    tail = tail.replace('$display("THIRD_QUERY_PASS polls=114 expands=113 candidates=565 costs=302");', '$display("THIRD_WARM_PASS polls=114 expands=113 candidates=565 costs=302");')
    s = s[:start] + tail
    s = s.replace('\nendmodule', RESTORE + '\nendmodule', 1)
    return s


if __name__ == '__main__':
    (HERE / 'tb_third_warm.sv').write_text(make())
