"""Prepare a passive sampled host/endpoint partition; no stimulus changes."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 source=ROOT/'results/service_profile_observers_20261024/tb_small_endpoint_service_profile.sv';s=source.read_text();out=ROOT/'results/command_profile_observers_20261024';out.mkdir()
 s=s.replace(source.stem,'tb_small_endpoint_command_profile')
 monitor='''
    longint unsigned cmdprof_total=0,cmdprof_rsp_hold=0,cmdprof_rsp_accept=0;
    longint unsigned cmdprof_busy=0,cmdprof_offer=0,cmdprof_idle=0;
    longint unsigned cmdprof_by_op[0:15];
    integer cmdprof_i;
    initial begin for(cmdprof_i=0;cmdprof_i<16;cmdprof_i=cmdprof_i+1)cmdprof_by_op[cmdprof_i]=0;end
    always @(posedge clk) begin
        if(!rst)begin
            cmdprof_total=cmdprof_total+1;
            if(rsp_valid)begin
                if(rsp_ready)cmdprof_rsp_accept=cmdprof_rsp_accept+1;
                else cmdprof_rsp_hold=cmdprof_rsp_hold+1;
            end else if(dut.state!=0)begin
                cmdprof_busy=cmdprof_busy+1;
                cmdprof_by_op[dut.op]=cmdprof_by_op[dut.op]+1;
            end else if(cmd_valid)cmdprof_offer=cmdprof_offer+1;
            else cmdprof_idle=cmdprof_idle+1;
        end
    end
    task automatic command_profile_receipt;
        integer j;
        begin
            if(cmdprof_total!=cmdprof_rsp_hold+cmdprof_rsp_accept+cmdprof_busy+cmdprof_offer+cmdprof_idle)$fatal(1,"command profile partition mismatch");
            $display("COMMAND_PROFILE queries=%0d total=%0d rsp_hold=%0d rsp_accept=%0d busy=%0d offer=%0d idle=%0d",completed_fences,cmdprof_total,cmdprof_rsp_hold,cmdprof_rsp_accept,cmdprof_busy,cmdprof_offer,cmdprof_idle);
            for(j=0;j<16;j=j+1)$display("COMMAND_OP_PROFILE queries=%0d op=%0d busy=%0d",completed_fences,j,cmdprof_by_op[j]);
        end
    endtask
'''
 s=s.replace('    task automatic cold_start;',monitor+'\n    task automatic cold_start;').replace('                if(vo==11)profile_receipt();','                if(vo==11)begin profile_receipt();command_profile_receipt();end')
 p=out/'tb_small_endpoint_command_profile.sv';p.write_text(s)
 spec={'status':'prepared_not_simulated','sources':{'small':{'input':str(ROOT/'hardware/tb/tb_small_endpoint_checkpoint_stream_v3.sv'),'output':p.name,'output_sha256':sha(p)}}};(out/'manifest.json').write_text(json.dumps(spec,indent=2)+'\n')
if __name__=='__main__':main()
