"""Prepare passive initialization timing variants; never modify frozen replay TBs."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
MONITOR='''
    // Passive sampling at negedge: sequential DUT updates have settled.
    reg init_seen_reset=0,init_reported=0;
    time init_release;
    longint unsigned init_clear_samples=0;
    always @(negedge clk) begin
        if(rst) begin
            init_seen_reset=1; init_reported=0; init_clear_samples=0;
            init_release=$time;
        end else if(init_seen_reset && !init_reported) begin
            if(dut.memory.memory_service.directory.state==14)
                init_clear_samples=init_clear_samples+1;
            if(dut.memory.memory_service.directory.cmd_ready) begin
                init_reported=1;
                $display("INIT_DIRECTORY_READY time_ps=%0t last_reset_sample_ps=%0t clear_samples=%0d",$time,init_release,init_clear_samples);
            end
        end
    end
'''
def main():
    out=ROOT/'results/initialization_observers_20261024';out.mkdir(exist_ok=False)
    sources={}
    for label,name in [('old','tb_memory_endpoint_checkpoint_stream_cycle64'),('small','tb_small_endpoint_checkpoint_stream_v3')]:
        p=ROOT/'hardware/tb'/f'{name}.sv';s=p.read_text()
        assert s.count('    task automatic cold_start;')==1
        new=s.replace(name,name+'_init_observer').replace('    task automatic cold_start;',MONITOR+'\n    task automatic cold_start;')
        target=out/f'{name}_init_observer.sv';target.write_text(new)
        sources[label]={'input':str(p),'input_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'output':target.name,'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
    (out/'manifest.json').write_text(json.dumps({'status':'prepared_not_simulated','sources':sources,'scope':'Directory-ready boundary only; not entire endpoint readiness. Last reset sample is a sampled timestamp, not exact deassertion. Require unchanged query receipts and total cycles versus pilot before interpreting measurements.'},indent=2)+'\n')
    print(out)
if __name__=='__main__':main()
