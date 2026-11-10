"""Streaming checkpoint replay retains public, page-byte and AXI checks."""
from pathlib import Path
from make_streaming_endpoint_tb_v2 import generate as parent
ROOT=Path(__file__).resolve().parents[2]
def generate():
 text=parent()
 def r(before,after):
  nonlocal text
  assert text.count(before)==1,before
  text=text.replace(before,after)
 text=text.replace('memory_endpoint_stream','memory_endpoint_checkpoint_stream')
 r('memory_scratch_endpoint_indexed #(','memory_scratch_endpoint_retained #(')
 r('EXPECT_TRANSFERS=6086,EXPECT_QUERIES=19);','EXPECT_TRANSFERS=6086,EXPECT_QUERIES=19,EXPECT_CHECKPOINTS=0);')
 r('    task automatic cold_start;', '''    integer completed_checkpoints=0;
    reg checkpoint_page_done=0,checkpoint_memory_done=0;
    always @(posedge clk)begin
        if(rst)begin checkpoint_page_done<=0;checkpoint_memory_done<=0;end
        else begin
            if(dut.state==21)begin checkpoint_page_done<=0;checkpoint_memory_done<=0;end
            if(dut.state==25 && dut.q_valid && dut.q_status==0)checkpoint_page_done<=1;
            if(dut.state==26 && dut.m_send && dut.m_ready && (!checkpoint_page_done || page_leases!=0 || memory_leases!=0))
                $fatal(1,"stream checkpoint before page fence");
            if(dut.state==27 && dut.m_valid && dut.m_status==0)checkpoint_memory_done<=1;
            if(dut.state==28 && !checkpoint_memory_done)$fatal(1,"stream resume before memory reset");
            if(dut.state>=21 && cmd_ready)$fatal(1,"stream checkpoint exposed ingress");
            if(dut.q_send && dut.q_op>=12)$fatal(1,"checkpoint leaked to queue control");
        end
    end
    task automatic cold_start;''')
 r('vector_count=vector_count+1;', '''vector_count=vector_count+1;
                if(vo==12)begin
                    if(vstatus!=0 || !checkpoint_page_done || !checkpoint_memory_done || page_leases!=0 || memory_leases!=0 || fault)
                        $fatal(1,"stream checkpoint incomplete");
                    completed_checkpoints=completed_checkpoints+1;
                    $display("STREAM_CHECKPOINT_DONE checkpoints=%0d commands=%0d transfers=%0d time_ps=%0t",completed_checkpoints,vector_count,completed_transfers,$time);
                end''')
 r('if(vector_count!=EXPECT_COMMANDS ||', 'if(completed_checkpoints!=EXPECT_CHECKPOINTS || vector_count!=EXPECT_COMMANDS ||')
 r('.EXPECT_COMMANDS(3286037),.EXPECT_TRANSFERS(414485),.EXPECT_QUERIES(7)', '.EXPECT_COMMANDS(21662794),.EXPECT_TRANSFERS(2743929),.EXPECT_QUERIES(38),.EXPECT_CHECKPOINTS(31)')
 return text
if __name__=='__main__':(ROOT/'hardware/tb/tb_memory_endpoint_checkpoint_stream.sv').write_text(generate())
