"""Extract nine AXI fault cases with small-page-correct 4KiB boundaries."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def render():
 s=(ROOT/'hardware/tb/tb_small_endpoint_checkpoint_stream_v3.sv').read_text()
 s=s[:s.index('\nmodule tb_small_endpoint_checkpoint_stream_v3_small;')]
 s=s.replace('small_endpoint_checkpoint_stream_v3_test','response_fault_test')
 s=s.replace('localparam integer TB_FRAMES=SMALL?4:REPLAY_FRAMES,TB_INDEX=SMALL?2:REPLAY_INDEX;','localparam integer TB_FRAMES=32,TB_INDEX=5;')
 s=s.replace('localparam integer TB_HASH=SMALL?2:18;','localparam integer TB_HASH=6;')
 start=s.index('    initial begin\n        clear_golden;cold_start;')
 fault_start=s.index('            for(err=1;err<=9;err=err+1)begin',start)
 fault_end=s.index('            if(completed_fences!=25',fault_start)
 loop=s[fault_start:fault_end].replace('goal_frame=(err>=6 && err<=8)?3:0;','goal_frame=(err>=6 && err<=8)?21:0;')
 main='''    initial begin
'''+loop+'''        if(errors!=9)$fatal(1,"missing fault cases");
        $display("RESPONSE_FAULT_PASS errors=%0d transfers=%0d checks=%0d",errors,completed_transfers,checks);
        $finish;
    end
endmodule
module tb_response_faults;response_fault_test test();endmodule
'''
 return s[:start]+main
if __name__=='__main__':
 p=ROOT/'hardware/tb/tb_response_faults.sv';p.write_text(render());print(p)
