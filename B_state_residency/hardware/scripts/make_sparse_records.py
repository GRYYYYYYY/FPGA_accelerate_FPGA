"""Incremental sparse RF control on frozen WB ablation; no wire compression."""
from pathlib import Path
from make_sparse_writeback import render as wb_render,replace
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/variants/sparse_records'
def render():
 r=wb_render()
 s=r['scratch_page_controller_small.sv']
 s=replace(s,'BEGIN_FENCE=10, FINISH_FENCE=11;','BEGIN_FENCE=10, FINISH_FENCE=11, RF_MASK=14;')
 s=replace(s,'reg [31:0] dirty, pristine, generation_used;','reg [31:0] dirty, pristine, generation_used, rf_sealed;')
 s=replace(s,'dirty<=0; pristine<=0; generation_used<=0;','rf_sealed<=0; dirty<=0; pristine<=0; generation_used<=0;')
 s=replace(s,'if(cmd_op==REFILL) pristine[cmd_slot]<=0;', 'if(cmd_op==REFILL)begin pristine[cmd_slot]<=0;rf_sealed[cmd_slot]<=0;end')
 s=replace(s,'else if(cmd_op==BEAT && (cmd_payload[159:136]!=0 || (!cmd_present && cmd_payload!=0))) rsp_status<=BAD;', 'else if(cmd_op==BEAT && (cmd_payload[159:136]!=0 || !cmd_present || rf_sealed[cmd_slot])) rsp_status<=BAD;')
 s=replace(s,'                        else if(cmd_op==BEAT && !cmd_present) transferred[cmd_slot][cmd_offset]<=1;\n','')
 # A sealed RF cannot accept later records, even if an invalid offset is retried.
 s=replace(s,'                    COMPLETE: begin\n                        if(!descriptor_matches)', '''                    RF_MASK: begin
                        // Trusted adapter sends this only after decoding all 8 offsets.
                        // Public native ingress rejects opcode14. This does not attest DMA.
                        if(!descriptor_matches || !cmd_kind) rsp_status<=STALE;
                        else if(rf_sealed[cmd_slot]) rsp_status<=BUSY;
                        else if(cmd_payload[159:8]!=0) rsp_status<=BAD;
                        else if(transferred[cmd_slot]!=cmd_payload[7:0]) rsp_status<=INCOMPLETE;
                        else begin transferred[cmd_slot]<=8'hff;rf_sealed[cmd_slot]<=1;end
                    end
                    COMPLETE: begin
                        if(!descriptor_matches)''')
 s=replace(s,'else if(!(&transferred[cmd_slot])) rsp_status<=INCOMPLETE;', 'else if((cmd_kind && !rf_sealed[cmd_slot]) || !(&transferred[cmd_slot])) rsp_status<=INCOMPLETE;')
 r['scratch_page_controller_small.sv']=s
 s=r['memory_scratch_endpoint_small_staticcodec.sv']
 s=replace(s,'CP_QUERY_SEND=28,CP_QUERY_WAIT=29;', 'CP_QUERY_SEND=28,CP_QUERY_WAIT=29,RF_MASK_SEND=30,RF_MASK_WAIT=31;')
 s=replace(s,'reg [7:0] wb_bitmap;', 'reg [7:0] wb_bitmap,rf_bitmap;')
 s=replace(s,'|| state==CP_QUERY_SEND;', '|| state==CP_QUERY_SEND || state==RF_MASK_SEND;')
 s=replace(s,'|| state==CP_QUERY_WAIT;', '|| state==CP_QUERY_WAIT || state==RF_MASK_WAIT;')
 s=replace(s,'wire [3:0] q_op=state==CP_BEGIN_SEND?', 'wire [3:0] q_op=state==RF_MASK_SEND?4\'d14:state==CP_BEGIN_SEND?')
 s=replace(s,'    queued_scratch_endpoint_small #(', "    wire [159:0] q_command_payload=state==RF_MASK_SEND?{152'b0,rf_bitmap}:record;\n    queued_scratch_endpoint_small #(")
 s=replace(s,'.cmd_value(value),.cmd_payload(record),','.cmd_value(value),.cmd_payload(q_command_payload),')
 s=replace(s,'wb_bitmap<=0;offset<=0;', 'wb_bitmap<=0;rf_bitmap<=0;offset<=0;')
 s=replace(s,'value<=cmd_value;position<=0;record<=0;', 'value<=cmd_value;position<=0;rf_bitmap<=0;record<=0;')
 s=replace(s,'else begin record<=record_out_payload;present<=record_out_present;state<=RF_BEAT_SEND;end', '''else if(!record_out_present && record_out_payload!=0)fail_closed;
                        else begin
                            rf_bitmap[position]<=record_out_present;
                            if(record_out_present)begin record<=record_out_payload;present<=1;state<=RF_BEAT_SEND;end
                            else if(position==7)state<=RF_MASK_SEND;
                            else position<=position+1'b1;
                        end''')
 s=replace(s,'else if(position==7)state<=M_STATUS;', 'else if(position==7)state<=RF_MASK_SEND;')
 s=replace(s,'                M_STATUS:if(m_valid)begin', '''                RF_MASK_SEND:if(q_ready)state<=RF_MASK_WAIT;
                RF_MASK_WAIT:if(q_valid)begin
                    if(q_status!=0)fail_closed;
                    else state<=M_STATUS;
                end
                M_STATUS:if(m_valid)begin''')
 r['memory_scratch_endpoint_small_staticcodec.sv']=s
 return r
if __name__=='__main__':
 for name,s in render().items():(OUT/name).write_text(s);print(OUT/name)
