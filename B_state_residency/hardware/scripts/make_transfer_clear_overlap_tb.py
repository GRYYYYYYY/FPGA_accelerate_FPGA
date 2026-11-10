"""Reconstruct the frozen passive overlap observer without overwriting results."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def render():
 text=(ROOT/'results/transfer_state_observers_20261024/tb_small_endpoint_transfer_state_profile.sv').read_text().replace('tb_small_endpoint_transfer_state_profile','tb_small_endpoint_transfer_state_overlap')
 marker='    longint unsigned transfer_states[0:63];\n'
 addition='''    longint unsigned clear_in_wb_lookup=0,clear_in_rf_lookup=0;
    always @(posedge clk)begin
        if(!rst && !rsp_valid && dut.state==4 && dut.memory.memory_service.directory.state==14)begin
            if(dut.op==5)clear_in_wb_lookup=clear_in_wb_lookup+1;
            if(dut.op==6)clear_in_rf_lookup=clear_in_rf_lookup+1;
        end
    end
'''
 assert text.count(marker)==1;text=text.replace(marker,marker+addition)
 marker='''    task automatic transfer_state_receipt;
        integer j;
        begin
'''
 assert text.count(marker)==1
 return text.replace(marker,marker+'            $display("TRANSFER_CLEAR_OVERLAP queries=%0d wb_lookup=%0d rf_lookup=%0d",completed_fences,clear_in_wb_lookup,clear_in_rf_lookup);\n')
if __name__=='__main__':
 frozen=ROOT/'results/transfer_state_overlap_observers_20261024/tb_small_endpoint_transfer_state_overlap.sv'
 assert render()==frozen.read_text();print('OVERLAP_OBSERVER_RECONSTRUCTION_PASS')
