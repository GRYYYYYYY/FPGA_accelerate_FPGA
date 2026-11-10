from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).parent
def make():
    s=(ROOT/'hardware/variants/query_fault_v1/tb_query_fault.sv').read_text()
    s=s.replace('integer fi_cycle=0;reg replayed=0;', 'integer fi_cycle=0,fault_after=0,eligible_responses=0;reg replayed=0;\ninitial begin if($value$plusargs("faultafter=%d",fault_after))begin if(fault_after<0)$fatal(1,"negative fault ordinal");end end')
    s=s.replace('armed&&!injection_seen&&fault_case==3&&qc_phase==4','armed&&!injection_seen&&fault_case==3&&qc_phase==4&&eligible_responses==fault_after')
    s=s.replace('armed&&!injection_seen&&fault_case==4&&qc_phase==4','armed&&!injection_seen&&fault_case==4&&qc_phase==4&&eligible_responses==fault_after')
    c='system.inner.backend.dut.core'
    extra=f'''
always @(posedge clk)if(!rst&&armed&&!injection_seen&&qc_phase==4)begin
 if((fault_case==3&&g_m_rvalid&&g_m_rready)||(fault_case==4&&cs_m_rvalid&&cs_m_rready))eligible_responses<=eligible_responses+1;
end
always @(posedge clk)if(!rst&&qc_rsp_valid)begin
 if({c}.arb_g_busy||{c}.arb_d_busy||{c}.arb_io_busy||{c}.pc_arb_busy||{c}.capture_depth!=0||{c}.g_rsp_valid||{c}.d_rsp_valid||{c}.b_result_valid||{c}.ce_result_valid)$fatal(1,"query completed with internal ownership");
end
always @(posedge clk)if(!rst&&armed&&!injection_seen&&((g_m_rvalid&&g_m_rready&&g_m_rresp!=0)||(cs_m_rvalid&&cs_m_rready&&cs_m_rresp!=0)))
 $fdisplay(trace,"FAULT_OWNER %0d %0d %0d expand=%0d metadata=%0d coordinate=%0d controller=%0d",cycles,fault_case,eligible_responses,{c}.expansion.state,{c}.metadata.state,{c}.coordinates.state,{c}.controller.state);
'''
    s=s.replace('initial begin\n trace=$fopen',extra+'\ninitial begin\n trace=$fopen',1)
    needle=' $fflush(trace);$display("QUERY_FAULT_OBSERVED case=%0d outcome=stalled cycles=%0d",fault_case,cycles);$finish;'
    assert needle in s
    diag=f''' $fdisplay(trace,"DETAIL arb_g=%b arb_d=%b arb_io=%b pc_arb=%b capture=%0d capstate=%0d framefault=%b expand=%0d controller=%0d gvalid=%b gready=%b prefetch=%0d post=%0d",{c}.arb_g_busy,{c}.arb_d_busy,{c}.arb_io_busy,{c}.pc_arb_busy,{c}.capture_depth,{c}.child_capture.state,{c}.child_capture.frame_fault,{c}.expansion.state,{c}.controller.state,{c}.g_rsp_valid,{c}.g_rsp_ready,system.inner.backend.dut.prefetch.state,system.inner.backend.dut.post_inputs.state);
'''
    return s.replace(needle,diag+needle)
if __name__=='__main__':(HERE/'tb_query_fault.sv').write_text(make())
