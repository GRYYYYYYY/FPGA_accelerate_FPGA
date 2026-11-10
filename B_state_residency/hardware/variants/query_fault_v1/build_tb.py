"""Actual AXI errors on the unchanged lifecycle stack; bounded diagnostic outcomes."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).parent

def make():
    s = (ROOT/'hardware/variants/query_lifecycle_v1/tb_query_lifecycle_join.sv').read_text()
    s = s.replace('module tb_candidate_offer;', '''module tb_candidate_offer;
integer fi_cycle=0;reg replayed=0;
''', 1)
    a = s.index('always @(posedge clk)if(!rst&&armed)begin')
    b = s.index('task install_config_snapshot;', a)
    s = s[:a] + s[b:]
    # Inject at the memory response producer, so effective errors are in AXI logs.
    for name, r, b in [
        ('mem_p(', 'armed&&!injection_seen&&fault_case==1&&qc_phase==2&&system.controller.operation==0',
         'armed&&!injection_seen&&((fault_case==2&&qc_phase==2&&system.controller.operation>=1&&system.controller.operation<=4)||(fault_case==6&&qc_phase==2&&system.controller.operation==6))'),
        ('mem_g(', 'armed&&!injection_seen&&fault_case==3&&qc_phase==4', "1'b0"),
        ('mem_cs(', 'armed&&!injection_seen&&fault_case==4&&qc_phase==4', "1'b0"),
        ('mem_owner(', "1'b0", 'armed&&!injection_seen&&fault_case==5&&qc_phase==6')]:
        a = s.index(name); bidx = s.index(');', a)
        import re
        part = re.sub(r'\.inject_r\([^\n]*\)', '.inject_r('+r+')', s[a:bidx])
        part = re.sub(r'\.inject_b\([^\n]*\)', '.inject_b('+b+')', part)
        s = s[:a] + part + s[bidx:]
    # Successful prefix remains scored. After an injected error its partial output
    # is diagnostic, and after reset/reload the complete retry is scored again.
    s = s.replace('if(!rst&&ss_busy)begin', 'if(!rst&&ss_busy&&(!injection_seen||replayed))begin')
    s = s.replace('if(rc_rsp_status||rc_rsp_nodes!=6||rc_rsp_acked!=6)$fatal', 'if((!injection_seen||replayed)&&(rc_rsp_status||rc_rsp_nodes!=6||rc_rsp_acked!=6))$fatal')
    s = s.replace('if(cycles-f_last_progress>131072)$fatal', 'if(!injection_seen&&cycles-f_last_progress>131072)$fatal')
    s = s.replace('if(fault&&!armed&&(!recovering||recover_open))$fatal', 'if(fault&&!armed&&(!recovering||recover_open)&&replayed)$fatal')
    # Retry has the new published identity; arithmetic oracle is unchanged.
    s = s.replace('qc_cmd_query=1;qc_cmd_price=3;', 'qc_cmd_query=restore_epoch;qc_cmd_price=restore_version[3:0];')
    s = s.replace("qc_cmd_expand={32'd3,", 'qc_cmd_expand={restore_version,')
    a = s.index('task autonomous_query;'); b = s.index(' wait(qc_rsp_valid);', a)
    start = s[a:b].replace('task autonomous_query;', 'task fault_query;')
    fault_end = '''
 wait(qc_rsp_valid);@(negedge clk);
 if(!injection_seen||!qc_rsp_status||!qc_fault||!f_all_drained||!f_backend_idle||!f_normal_retired)$fatal(1,"fault completion not drained");
 $fdisplay(trace,"FAILED_QUERY %0d %0d %0d %0d %0d %0d %0d",cycles,fault_case,qc_rsp_status,qc_rsp_detail,qc_rsp_committed,qc_rsp_acked,k_count);
 repeat(5)begin @(negedge clk);if(!qc_rsp_valid||!qc_busy||f_sr||rc_req_ready||k_rec_ready)$fatal(1,"fault completion lease");end
 qc_rsp_ready=1;@(negedge clk);qc_rsp_ready=0;
end endtask
always @(posedge clk)if(!rst&&armed&&!injection_seen)begin
 if((p_m_rvalid&&p_m_rready&&p_m_rresp!=0)||(p_m_bvalid&&p_m_bready&&p_m_bresp!=0)||
    (g_m_rvalid&&g_m_rready&&g_m_rresp!=0)||(cs_m_rvalid&&cs_m_rready&&cs_m_rresp!=0)||
    (owner_m_bvalid&&owner_m_bready&&owner_m_bresp!=0))begin
  injection_seen<=1;fi_cycle<=cycles;
  $fdisplay(trace,"FI %0d %0d %0d %0d",cycles,fault_case,qc_phase,system.controller.operation);
 end
end
always @(negedge clk)if(injection_seen&&!recovering)k_rec_valid=1;
always @(negedge clk)if(injection_seen&&!recovering&&!qc_rsp_valid&&cycles-fi_cycle>32768)begin
 $fdisplay(trace,"STALLED %0d %0d qc=%0d ss=%0d fence=%0d drained=%b idle=%b retired=%b pending=%h",cycles,fault_case,qc_phase,ss_phase,f_phase,f_all_drained,f_backend_idle,f_normal_retired,system.inner.backend.f_pending);
 $fdisplay(trace,"OWNED core=%b center=%b prefetch=%b post=%b frontier=%b cost=%b commit=%b offer=%b op=%b lease=%b qlease=%b",system.inner.backend.dut.core_busy,system.inner.backend.dut.center_retired_idle,system.inner.backend.dut.prefetch_retired_idle,system.inner.backend.dut.post_retired_idle,system.inner.backend.dut.frontier_retired_idle,system.inner.backend.dut.k_retired_idle,system.inner.backend.dut.commit_busy,system.inner.backend.dut.offer_busy,system.inner.backend.dut.operation_pending,system.inner.backend.dut.cost_lease,system.inner.backend.dut.q_lease);
 $fflush(trace);$display("QUERY_FAULT_OBSERVED case=%0d outcome=stalled cycles=%0d",fault_case,cycles);$finish;
end
'''
    s = s[:a] + start + fault_end + s[a:]
    a = s.index(' for(query_index=0;')
    # Reuse hardware recovery callbacks; stream initial labels, not search-final.
    old = (ROOT/'hardware/variants/residency_system_v1/tb_system_fault.sv').read_text()
    r0 = old.index(' k_rec_valid=1;recovering=1;')
    r1 = old.index(' @(negedge clk);rc_req_op=0;rc_req_slot=0;rc_req_sink=150697;rc_req_sequence=1;rc_req_cookie=32\'hfabcd002;', r0)
    recovery = old[r0:r1]
    # Drop all host contenders before recovery command is accepted.
    recovery = recovery.replace(' k_rec_valid=1;recovering=1;', ' cc_req_valid=0;cs_req_valid=0;k_cfg_valid=0;cf_load_valid=0;rc_req_valid=0;\n k_rec_valid=1;recovering=1;')
    tail = '''
 control(1);
 if(!$value$plusargs("faultcase=%d",fault_case)||fault_case<1||fault_case>6)$fatal(1,"faultcase");
 query_index=0;armed=1;
 fault_query;
'''+recovery+'''
 replayed=1;query_index=0;poll_i=0;expand_i=0;candidate_i=0;commits=0;outputs=0;offers=0;physical_expands=0;metadata_calls=0;
 rc=$fseek(polls_fd,0,0);if(rc)$fatal(1,"poll rewind");
 rc=$fseek(candidates_fd,0,0);if(rc)$fatal(1,"candidate rewind");
 rc=$fseek(fd_gold,0,0);if(rc)$fatal(1,"cost rewind");
 $fdisplay(trace,"RETRY %0d %0d %0d",cycles,restore_epoch,restore_version);
 autonomous_query;
 for(final_index=0;final_index<328;final_index=final_index+1)begin
  rc=$fscanf(finals_fd,"%d",final_node_id);if(rc!=1)$fatal(1,"final node");
  for(j=0;j<5;j=j+1)begin rc=$fscanf(finals_fd,"%h",word);if(rc!=1)$fatal(1,"final word");gold_final[j*32+:32]=word;end
  if(final_node_id==selected_sink)gold_final[159:128]=0;
  label_read(final_node_id);if(host_record!==gold_final)$fatal(1,"retry final labels node=%0d",final_node_id);
  $fdisplay(trace,"Z %0d %0d %040h",cycles,final_node_id,host_record);
 end
 stage_no=0;probe_owners;
 if(fault||qc_fault||ss_fault||k_fault||cf_fault||lr_fault||!f_all_drained||!f_backend_idle||ss_polls!=73||ss_expands!=72||ss_candidates!=271||commits!=171||offers!=171)$fatal(1,"retry final state");
 $fflush(trace);$fclose(trace);
 $display("QUERY_FAULT_OBSERVED case=%0d outcome=recovered_retry cycles=%0d repairs=%0d",fault_case,cycles,k_corrected);$finish;
end
endmodule
'''
    return s[:a]+tail

if __name__ == '__main__':
    (HERE/'tb_query_fault.sv').write_text(make())
