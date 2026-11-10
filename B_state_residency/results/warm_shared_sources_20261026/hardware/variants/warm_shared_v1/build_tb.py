"""Only delay warm owner-B error to a real q1/q2 shared node."""
from pathlib import Path
HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/warm_system_v2/sources/tb_query_fault.sv')
def make():
 s=BASE.read_text();i=s.index(';',s.index('module '))+1;s=s[:i]+'''reg[31:0]warm_fault_node=263946;
initial begin if($value$plusargs("warmfaultnode=%d",warm_fault_node))begin end if(warm_fault_node!=263946&&warm_fault_node!=554512)$fatal(1,"unsupported shared fault node");end
'''+s[i:]
 a='.inject_b(armed&&!injection_seen&&fault_case==5&&qc_phase==6)';b='.inject_b(armed&&!injection_seen&&fault_case==5&&qc_phase==6&&(!wm_enable||b_o_node==warm_fault_node))';assert s.count(a)==1;s=s.replace(a,b)
 observer='''always @(posedge clk)if(!rst&&wm_enable&&armed&&!injection_seen&&owner_m_bvalid&&owner_m_bready)
 $fdisplay(trace,"SHARED_B %0d %0d %0d %0d",cycles,b_o_node,owner_m_bresp,k_count);
'''
 return s.replace('endmodule',observer+'endmodule')
if __name__=='__main__':(HERE/'tb_shared.sv').write_text(make())
