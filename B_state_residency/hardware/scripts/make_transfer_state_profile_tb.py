"""Passive endpoint-state histogram for page transfer operations."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 src=ROOT/'results/command_profile_observers_20261024/tb_small_endpoint_command_profile.sv';s=src.read_text();out=ROOT/'results/transfer_state_observers_20261024';out.mkdir()
 s=s.replace(src.stem,'tb_small_endpoint_transfer_state_profile')
 monitor='''
    longint unsigned transfer_states[0:63];
    integer transfer_init;
    initial begin for(transfer_init=0;transfer_init<64;transfer_init=transfer_init+1)transfer_states[transfer_init]=0;end
    always @(posedge clk)begin
        if(!rst && !rsp_valid && dut.state!=0 && (dut.op==5 || dut.op==6))
            transfer_states[(dut.op==6?32:0)+dut.state]=transfer_states[(dut.op==6?32:0)+dut.state]+1;
    end
    task automatic transfer_state_receipt;
        integer j;
        begin
            for(j=0;j<64;j=j+1)
                $display("TRANSFER_STATE_PROFILE queries=%0d op=%0d state=%0d cycles=%0d",completed_fences,j<32?5:6,j%32,transfer_states[j]);
        end
    endtask
'''
 s=s.replace('    task automatic cold_start;',monitor+'\n    task automatic cold_start;').replace('profile_receipt();command_profile_receipt();end','profile_receipt();command_profile_receipt();transfer_state_receipt();end')
 p=out/'tb_small_endpoint_transfer_state_profile.sv';p.write_text(s)
 (out/'manifest.json').write_text(json.dumps({'status':'prepared_not_simulated','sources':{'small':{'input':str(ROOT/'hardware/tb/tb_small_endpoint_checkpoint_stream_v3.sv'),'output':p.name,'output_sha256':sha(p)}}},indent=2)+'\n')
if __name__=='__main__':main()
