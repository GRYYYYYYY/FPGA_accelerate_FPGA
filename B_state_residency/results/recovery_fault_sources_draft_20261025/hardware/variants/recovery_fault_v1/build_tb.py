from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).parent
BASE=ROOT/'results/search_fault_retire_matrix_v6/sources'
def replace(s,a,b):
 assert s.count(a)==1,a
 return s.replace(a,b)
def make():
 s=(BASE/'tb_query_fault.sv').read_text()
 declaration='''integer recovery_fault=0,recovery_injected=0,recovery_fi_cycle=0;reg recovery_done=0;
wire recovery_inject;
initial begin if(!$value$plusargs("recoveryfault=%d",recovery_fault)||recovery_fault<1||recovery_fault>5)$fatal(1,"recovery fault selector");end
'''
 s=replace(s,'integer fi_cycle=0,fault_after=0,eligible_responses=0;reg replayed=0;',declaration+'integer fi_cycle=0,fault_after=0,eligible_responses=0;reg replayed=0;')
 # Edit only the verification memory-agent input pins. No hierarchical force.
 a=s.index('axi_file_memory #(.ADDR_BITS(64),.READ_ONLY(0),.MAX_BEATS(1),.TAG("owners")');b=s.index(');',a)
 q=s[a:b];q=replace(q,".inject_r(1'b0)",'.inject_r(recovery_inject&&recovery_fault==1)')
 q=replace(q,'.inject_b(armed&&!injection_seen&&fault_case==5&&qc_phase==6)', '.inject_b((armed&&!injection_seen&&fault_case==5&&qc_phase==6)||(recovery_inject&&recovery_fault==2))');s=s[:a]+q+s[b:]
 a=s.index('axi_file_memory #(.ADDR_BITS(32),.READ_ONLY(0),.MAX_BEATS(3),.TAG("labels")');b=s.index(');',a);q=s[a:b]
 q=replace(q,'.inject_r(armed&&!injection_seen&&fault_case==1&&qc_phase==2&&system.controller.operation==0)', '.inject_r(recovery_inject&&recovery_fault==5&&system.inner.backend.label_restore.state==10)')
 q=replace(q,'.inject_b(armed&&!injection_seen&&((fault_case==2&&qc_phase==2&&system.controller.operation>=1&&system.controller.operation<=4)||(fault_case==6&&qc_phase==2&&system.controller.operation==6)))', '.inject_b(recovery_inject&&((recovery_fault==3&&system.inner.backend.label_restore.state==7)||(recovery_fault==4&&system.inner.backend.label_restore.state==2&&system.inner.backend.label_restore.checkpoint_phase)))');s=s[:a]+q+s[b:]
 # Independent stream producer may remain blocked after a failed load. Recovery
 # completion must not require a producer to finish an already failed snapshot.
 a=s.index(' wait(k_labels_valid);@(negedge clk);repairs=k_corrected;')
 b=s.index(' wait(lr_rsp_valid);@(negedge clk);',a)
 feed=s[a:b]
 end=s.index('\n replayed=1;',b)
 terminal=''' wait(k_rsp_valid);@(negedge clk);
 if(!recovery_injected||!k_rsp_status||!k_fault||k_count!=1||k_saved_checkpoint!=17||k_saved_design!=design_id||k_rsp_cookie!=32'hc0010001||!f_all_drained||!f_normal_retired||f_pending!=0)$fatal(1,"recovery error completion contract");
 $fdisplay(trace,"RF_DONE %0d %0d %0d %0d %0d %0d %0d",cycles,recovery_fault,k_rsp_status,k_corrected,k_count,lr_written,lr_verified);
 repeat(9)begin @(negedge clk);if(!k_rsp_valid||!k_rsp_status||recover_open||k_permit||f_sr!=0||rc_req_ready||qc_cmd_ready||!f_all_drained||f_pending!=0)$fatal(1,"held recovery error admission");end
 $fdisplay(trace,"RF_HELD %0d %0d",cycles,k_rsp_status);
 k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;k_rec_valid=1;
 repeat(32)begin @(negedge clk);if(recover_open||k_permit||f_sr!=0||rc_req_ready||qc_cmd_ready||k_rec_ready||k_target_reset||!k_fault||k_count!=1||!f_all_drained||f_pending!=0)$fatal(1,"failed recovery reopened or dropped journal");end
 $fdisplay(trace,"RF_CLOSED %0d %0d %0d",cycles,k_count,f_phase);
 recovery_done=1;$fflush(trace);$fclose(trace);
 $display("RECOVERY_FAULT_OBSERVED case=%0d outcome=fail_closed cycles=%0d corrected=%0d",recovery_fault,cycles,k_corrected);$finish;
'''
 s=s[:a]+terminal+s[end:]
 # The old success/retry tail is unreachable and removed, not reinterpreted as
 # successful recovery. It remains covered by the prior unchanged v6 regression.
 a=s.index('\n replayed=1;');s=s[:a]+'\nend\nendmodule\n'
 extra='''
assign recovery_inject=recovering&&!recovery_injected;
initial begin wait(recovering);
'''+feed+'''end
always @(posedge clk)if(!rst&&recovery_inject)begin
 if((owner_m_rvalid&&owner_m_rready&&owner_m_rresp!=0)||(owner_m_bvalid&&owner_m_bready&&owner_m_bresp!=0)||(p_m_rvalid&&p_m_rready&&p_m_rresp!=0)||(p_m_bvalid&&p_m_bready&&p_m_bresp!=0))begin
  recovery_injected<=1;recovery_fi_cycle<=cycles;
  $fdisplay(trace,"RFI %0d %0d ctl=%0d label=%0d owner_op=%0d checkpoint=%b",cycles,recovery_fault,system.inner.backend.recovery_ctl.state,system.inner.backend.label_restore.state,k_o_op,system.inner.backend.label_restore.checkpoint_phase);
 end
end
always @(negedge clk)if(recovery_injected&&!recovery_done&&cycles-recovery_fi_cycle>32768)begin
 $fdisplay(trace,"RF_STALLED %0d %0d ctl=%0d label=%0d pending=%h drained=%b idle=%b rsp=%b",cycles,recovery_fault,system.inner.backend.recovery_ctl.state,system.inner.backend.label_restore.state,f_pending,f_all_drained,f_backend_idle,k_rsp_valid);
 $fflush(trace);$display("RECOVERY_FAULT_OBSERVED case=%0d outcome=stalled cycles=%0d",recovery_fault,cycles);$finish;
end
'''
 s=replace(s,'endmodule',extra+'\nendmodule')
 return s
if __name__=='__main__':(HERE/'tb_recovery_fault.sv').write_text(make())
