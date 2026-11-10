"""Independent WB bitmap control ablation; public/page/AXI formats unchanged."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/variants/sparse_writeback'
BASE=ROOT/'results/record_epoch16_pilot_20261024/pilot/sources'
def replace(s,a,b):
 assert s.count(a)==1,(a,s.count(a))
 return s.replace(a,b)
def render():
 result={}
 s=(BASE/'scratch_frame_store_bram.sv').read_text()
 s=replace(s,'CLEAN=3, UNBIND=4, LOAD=5;','CLEAN=3, UNBIND=4, LOAD=5, READ_MASK=6;')
 s=replace(s,'cmd_op > LOAD','cmd_op > READ_MASK')
 s=replace(s,'                end else if (cmd_op==LOAD) begin','                end else if (cmd_op==READ_MASK) begin\n                    // Trusted controller only; binding authorization precedes this case.\n                    rsp_payload <= {{(160-NODES){1\'b0}},present[cmd_slot]};\n                end else if (cmd_op==LOAD) begin')
 result['scratch_frame_store_bram.sv']=s
 s=(BASE/'scratch_page_controller_small.sv').read_text()
 s=replace(s,'                        WRITE: begin dirty[saved_slot]<=1;', '''                        WRITEBACK: begin
                            // Lock was established before this synchronous mask read.
                            // Absent offsets are represented by canonical codec zeros.
                            transferred[saved_slot]<=~core_payload[7:0];
                            rsp_tx<=transaction[saved_slot];
                        end
                        WRITE: begin dirty[saved_slot]<=1;''')
 s=replace(s,'                            if(cmd_op==REFILL) pristine[cmd_slot]<=0;', '''                            if(cmd_op==REFILL) pristine[cmd_slot]<=0;
                            else begin core_op<=6; core_valid<=1; rsp_valid<=0; end''')
 result['scratch_page_controller_small.sv']=s
 s=(BASE/'memory_scratch_endpoint_small_staticcodec.sv').read_text()
 s=replace(s,'    reg [2:0] offset,position;','    reg [7:0] wb_bitmap;\n    reg [2:0] offset,position;')
 s=replace(s,'state==WB_EXPORT_SEND || state==RF_BEAT_SEND || state==Q_COMPLETE_SEND', '(state==WB_EXPORT_SEND && wb_bitmap[position]) || state==RF_BEAT_SEND || state==Q_COMPLETE_SEND')
 s=replace(s,'offset<=0;position<=0;field<=0;','wb_bitmap<=0;offset<=0;position<=0;field<=0;')
 s=replace(s,'else begin transaction<=q_tx;state<=M_TRANSFER_SEND;end','''else if(!kind && q_payload[159:8]!=0)fail_closed;
                    else begin transaction<=q_tx;wb_bitmap<=q_payload[7:0];state<=M_TRANSFER_SEND;end''')
 s=replace(s,'                WB_EXPORT_SEND:if(q_ready)state<=WB_EXPORT_WAIT;','''                WB_EXPORT_SEND:begin
                    if(!wb_bitmap[position])begin record<=0;present<=0;state<=WB_PUT;end
                    else if(q_ready)state<=WB_EXPORT_WAIT;
                end''')
 result['memory_scratch_endpoint_small_staticcodec.sv']=s
 return result
if __name__=='__main__':
 for name,s in render().items():
  (OUT/name).write_text(s);print(OUT/name)
