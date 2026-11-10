"""Scale the composed lifecycle test to the actual default directory capacity."""
from make_record_epoch6_wrap_tb import render as small_render,ROOT
def render():
 s=small_render().replace('localparam integer TB_FRAMES=32,TB_INDEX=5;','localparam integer TB_FRAMES=163840,TB_INDEX=18;').replace('localparam integer TB_HASH=6;','localparam integer TB_HASH=18;')
 s=s.replace("#(64'd500000000000)","#(64'd50000000)")
 marker='    integer finish_retries=0,attempts,old_ar;'
 assert s.count(marker)==1
 s=s.replace(marker,'''    integer clear_in_fence=0;
    always @(posedge clk)if(!rst && dut.fence_open && dut.memory.memory_service.directory.state==14)clear_in_fence=clear_in_fence+1;
'''+marker)
 s=s.replace('index_clear_cycles!=128','index_clear_cycles!=524288 || clear_in_fence!=262144')
 old='COMPOSITE_WRAP_PASS queries=70 transfers=140 tag_wraps=17 epoch_wraps=1 clear_cycles=128 retries=%0d checks=%0d",finish_retries,checks'
 new='DEFAULT_CAPACITY_WRAP_PASS frames=163840 hash_bits=18 queries=70 transfers=140 tag_wraps=17 epoch_wraps=1 clear_cycles=524288 clear_in_fence=%0d retries=%0d checks=%0d",clear_in_fence,finish_retries,checks'
 assert old in s;s=s.replace(old,new)
 s=s.replace('module tb_record_epoch6_wrap;','module tb_record_epoch6_default_wrap;')
 return s
if __name__=='__main__':
 (ROOT/'hardware/tb/tb_record_epoch6_default_wrap.sv').write_text(render())
