"""Prepare a passive, mutually exclusive cycle partition for replay profiling."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 source=ROOT/'results/initialization_observers_20261024/tb_small_endpoint_checkpoint_stream_v3_init_observer.sv'
 out=ROOT/'results/service_profile_observers_20261024';out.mkdir()
 s=source.read_text();old=source.stem;new='tb_small_endpoint_service_profile'
 s=s.replace(old,new)
 monitor='''
    longint unsigned prof_total=0,prof_clear=0,prof_checkpoint=0,prof_probe=0,prof_other=0;
    longint unsigned prof_probe_in_checkpoint=0;
    always @(posedge clk) begin
        if(!rst) begin
            prof_total=prof_total+1;
            if(dut.memory.memory_service.directory.state==14)prof_clear=prof_clear+1;
            else if(dut.state>=21)prof_checkpoint=prof_checkpoint+1;
            else if(dut.memory.memory_service.directory.state==10 || dut.memory.memory_service.directory.state==11)prof_probe=prof_probe+1;
            else prof_other=prof_other+1;
            if(dut.state>=21 && (dut.memory.memory_service.directory.state==10 || dut.memory.memory_service.directory.state==11))
                prof_probe_in_checkpoint=prof_probe_in_checkpoint+1;
        end
    end
    task automatic profile_receipt;
        begin
            if(prof_total!=prof_clear+prof_checkpoint+prof_probe+prof_other)$fatal(1,"profile partition mismatch");
            $display("SERVICE_PROFILE queries=%0d total=%0d clear=%0d checkpoint=%0d probe=%0d other=%0d probe_in_checkpoint=%0d",completed_fences,prof_total,prof_clear,prof_checkpoint,prof_probe,prof_other,prof_probe_in_checkpoint);
        end
    endtask
'''
 s=s.replace('    task automatic cold_start;',monitor+'\n    task automatic cold_start;')
 marker='                if(vo==11)$display('
 assert s.count(marker)==1;s=s.replace(marker,'                if(vo==11)profile_receipt();\n'+marker)
 p=out/(new+'.sv');p.write_text(s)
 spec={'status':'prepared_not_simulated','sources':{'small':{'input':str(ROOT/'hardware/tb/tb_small_endpoint_checkpoint_stream_v3.sv'),'input_sha256':sha(ROOT/'hardware/tb/tb_small_endpoint_checkpoint_stream_v3.sv'),'output':p.name,'output_sha256':sha(p)}}}
 (out/'manifest.json').write_text(json.dumps(spec,indent=2)+'\n')
if __name__=='__main__':main()
