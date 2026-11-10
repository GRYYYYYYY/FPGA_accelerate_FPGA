"""Partial-label cancellation with a real accepted AXI read or write pending."""
from pathlib import Path
HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/warm_retry_system_v2/sources')
def rep(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def memory():
 s=(BASE/'axi_file_memory.sv').read_text()
 s=rep(s,'input wire inject_r,inject_b,','input wire inject_r,inject_b,hold_r,hold_b,')
 s=rep(s,'if(rp&&!rvalid)begin','if(rp&&!rvalid&&!hold_r)begin')
 s=rep(s,'if(wp&&wend&&!bvalid)begin','if(wp&&wend&&!bvalid&&!hold_b)begin')
 return s
def make():
 s=(BASE/'tb_query_fault.sv').read_text()
 s=rep(s,'reg cancel_started=0;', '''integer axi_cancel_mode=0;reg axi_stall_armed=0,axi_stall_release=0;
wire axi_hold_r,axi_hold_b;
initial begin if($value$plusargs("axicancelmode=%d",axi_cancel_mode))begin end if(axi_cancel_mode<0||axi_cancel_mode>1)$fatal(1,"bad cancel mode");end
reg cancel_started=0;''')
 s=s.replace('.inject_r(','.hold_r(1\'b0),.hold_b(1\'b0),.inject_r(')
 # Label agent only: hold response generation, never mask a DUT handshake.
 marker='axi_file_memory #(.ADDR_BITS(32),.READ_ONLY(0),.MAX_BEATS(3),.TAG("labels"))mem_p('
 i=s.index(marker);j=s.index(');',i)
 piece=s[i:j].replace(".hold_r(1'b0),.hold_b(1'b0)",'.hold_r(axi_hold_r),.hold_b(axi_hold_b)');s=s[:i]+piece+s[j:]
 a=s.index(' for(integer x=0;x<328;x=x+1)begin',s.index('task warm_fault_and_restore;'))
 b=s.index(' // Reject the already-used attempt',a)
 s=s[:a]+''' axi_stall_armed=1;
 fork
  begin : feed_labels
   for(integer x=0;x<328&&!cancel_started;x=x+1)begin
    @(negedge clk);lr_s_valid=1;lr_s_node=warm_nodes[x];lr_s_payload=warm_values[x];lr_s_last=x==327;
    do @(posedge clk);while(!lr_s_ready&&!cancel_started);
    @(negedge clk);lr_s_valid=0;
   end
  end
  begin : cancel_physical
   if(axi_cancel_mode==0)begin
    do @(posedge clk);while(!(axi_hold_r&&p_m_arvalid&&p_m_arready));
    $fdisplay(trace,"AXI_CANCEL_ACCEPT %0d R %08h %0d %0d",cycles,p_m_araddr,p_m_arlen+1,lr_written);
   end else begin
    // Agent has accepted AW and the complete W burst before withholding B.
    wait(axi_hold_b&&mem_p.wp&&mem_p.wend&&!p_m_bvalid);
    @(negedge clk);$fdisplay(trace,"AXI_CANCEL_ACCEPT %0d B %08h %0d %0d",cycles,mem_p.wraddr,mem_p.wrlen,lr_written);
   end
   @(negedge clk);cancel_started=1;abort=1;
   repeat(32)begin @(negedge clk);
    $fdisplay(trace,"AXI_CANCEL_HELD %0d %0d %0d %0d %0d %0d",cycles,axi_cancel_mode,k_rsp_valid,f_all_drained,wm_owned,lr_busy);
    if(k_rsp_valid||f_all_drained||!wm_owned||!wm_fault||!lr_busy||recover_open||qc_cmd_ready||rc_req_ready||pc_acquire_ready)$fatal(1,"pending AXI escaped quarantine");
   end
   $fdisplay(trace,"AXI_CANCEL_RELEASE %0d",cycles);axi_stall_release=1;
  end
 join
 // Restore controller must retire the actual backend reply before failure.
 for(integer waited=0;waited<8192&&!k_rsp_valid;waited=waited+1)@(negedge clk);
 if(!k_rsp_valid)begin $fflush(trace);$fatal(1,"AXI cancellation stuck lr=%0d coor=%0d drained=%0d retired=%0d",system.inner.backend.label_restore.state,system.inner.backend.recovery_ctl.state,f_all_drained,system.wm_retired);end
 repeat(8)begin @(negedge clk);if(k_rsp_status!=6||k_count!=6||!system.wm_retired||!f_all_drained||!wm_owned||!wm_fault||recover_open)$fatal(1,"AXI failure retirement");end
 $fdisplay(trace,"CANCEL_COMPLETE %0d %0d %0d %0d",cycles,k_rsp_status,k_count,k_saved_checkpoint);
 k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;abort=0;repeat(8)begin @(negedge clk);if(!wm_owned||!wm_fault||recover_open)$fatal(1,"cancel opened work");end
'''+s[b:]
 # Passive native AXI completion witness, distinguishes response from release.
 s=s.replace('endmodule','''assign axi_hold_r=axi_stall_armed&&!axi_stall_release&&lr_written>=32&&axi_cancel_mode==0;
assign axi_hold_b=axi_stall_armed&&!axi_stall_release&&lr_written>=32&&axi_cancel_mode==1;
always @(posedge clk)if(axi_stall_armed)begin
 if(p_m_awvalid&&p_m_awready)$fdisplay(trace,"AXI_CANCEL_AW %0d %08h %0d",cycles,p_m_awaddr,p_m_awlen+1);
 if(p_m_wvalid&&p_m_wready)$fdisplay(trace,"AXI_CANCEL_W %0d %0d",cycles,p_m_wlast);
end
always @(posedge clk)if(axi_stall_armed&&cancel_started)begin
 if(p_m_rvalid&&p_m_rready)$fdisplay(trace,"AXI_CANCEL_R %0d %0d",cycles,p_m_rlast);
 if(p_m_bvalid&&p_m_bready)$fdisplay(trace,"AXI_CANCEL_B %0d %0d",cycles,p_m_bresp);
end
endmodule''')
 return s
if __name__=='__main__':
 (HERE/'axi_file_memory.sv').write_text(memory());(HERE/'tb_axi_cancel.sv').write_text(make())
