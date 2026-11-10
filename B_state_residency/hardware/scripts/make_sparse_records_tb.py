"""Independent RF representation/seal monitors, plus preserved WB checks."""
from pathlib import Path
from make_sparse_writeback_tb import render as wb_tbs,adapt as wb_adapt
from make_sparse_writeback_cycle64_tb import render as cycle64_render
ROOT=Path(__file__).resolve().parents[2]
def adapt_rf(s,paired=False):
 if paired:
  assert 'parameter integer SPARSE_WB=1,SMALL=0' in s
  s=s.replace('parameter integer SPARSE_WB=1,SMALL=0','parameter integer SPARSE_WB=1,SPARSE_RF=1,SMALL=0')
  s=s.replace('if(SPARSE_WB && active_op==5)begin','if((SPARSE_WB && active_op==5) || (SPARSE_RF && active_op==6))begin')
  # The new checker bounds response waiting as well as retry count.
  s=s.replace('integer retry_count,retained_frames,retained_epoch;', 'integer retry_count,retained_frames,retained_epoch,response_wait;')
  s=s.replace('while(!rsp_valid)@(negedge clk);', 'response_wait=0;while(!rsp_valid)begin @(negedge clk);response_wait=response_wait+1;if(response_wait>30000+(1<<TB_HASH)+2*TB_FRAMES)$fatal(1,"FINISH response timeout");end')
 else:
  s=s.replace('    localparam integer TB_TX=', '    localparam integer SPARSE_RF=1;\n    localparam integer TB_TX=',1)
  s=s.replace('if(active_op==5)begin','if(active_op==5 || active_op==6)begin')
 assert s.count('if(dut.q_send && dut.q_op>=12)')==1
 s=s.replace('if(dut.q_send && dut.q_op>=12)', 'if(dut.q_send && dut.q_op>=12 && !(dut.q_op==14 && dut.state==30 && active_op==6))')
 monitor='''    reg [7:0] rf_beat_seen=0;
    reg rf_seal_ack=0;
    integer rf_codec_count=0,rf_beats=0,rf_omitted=0,rf_masks=0;
    always @(posedge clk)if(!rst && SPARSE_RF)begin
        if(dut.record_out_valid && dut.memory.record_out_ready)begin
            if(dut.record_out_offset!=rf_codec_count || dut.record_out_present!==expected[0][dut.record_out_offset]
               || dut.record_out_payload!==sparse_expected_blob[8+dut.record_out_offset*160 +:160])
                $fatal(1,"RF decoded representation differs from independent page");
            rf_codec_count=rf_codec_count+1;
            if(!dut.record_out_present)rf_omitted=rf_omitted+1;
        end
        if(dut.q_send && dut.q_ready && dut.q_op==7)begin
            if(active_op!=6 || !expected[0][dut.q_offset] || rf_beat_seen[dut.q_offset])
                $fatal(1,"RF BEAT absent/duplicate offset");
            rf_beat_seen[dut.q_offset]=1;rf_beats=rf_beats+1;
        end
        if(dut.q_send && dut.q_ready && dut.q_op==14)begin
            if(active_op!=6 || dut.state!=30 || rf_codec_count!=8 || rf_beat_seen!==expected[0][7:0]
               || dut.pages.cmd_payload!=={152'b0,expected[0][7:0]})
                $fatal(1,"RF seal without complete exact representation");
            rf_masks=rf_masks+1;
        end
        if(dut.state==31 && dut.q_valid && dut.q_status==0)rf_seal_ack=1;
        if(dut.q_send && dut.q_ready && dut.q_op==8 && active_op==6)begin
            if(!rf_seal_ack || rf_codec_count!=8 || rf_beat_seen!==expected[0][7:0])
                $fatal(1,"RF COMPLETE before seal acknowledgement");
        end
    end
'''
 s=s.replace('    task automatic cold_start;',monitor+'    task automatic cold_start;',1)
 s=s.replace('sparse_export_seen=0;sparse_codec_count=0;sparse_mask_seen=0;', 'sparse_export_seen=0;sparse_codec_count=0;sparse_mask_seen=0;rf_beat_seen=0;rf_codec_count=0;rf_seal_ack=0;')
 s=s.replace('$finish;', '$display("SPARSE_RF_COUNTS beats=%0d omitted=%0d masks=%0d",rf_beats,rf_omitted,rf_masks);$finish;')
 # New independent tests all use the same unsigned64 scheduling counter.
 s=s.replace('integer cycle=0;','longint unsigned cycle=0;')
 return s

def render():
 originals=wb_tbs();result={}
 s=adapt_rf(originals['tb_sparse_writeback_masks.sv']).replace('sparse_writeback_masks','sparse_records_masks').replace('SPARSE_WB_MASKS_PASS','SPARSE_RECORD_MASKS_PASS')
 s=s.replace('clear_golden;cold_start;\n        for(mask_id=', 'clear_golden;cold_start;simple(14,0,0,0,0,3,0,0);\n        for(mask_id=')
 s=s.replace('        $display("SPARSE_RECORD_MASKS_PASS', '        if(rf_beats!=1024 || rf_omitted!=1024 || rf_masks!=256)$fatal(1,"RF mask coverage");\n        $display("SPARSE_RECORD_MASKS_PASS')
 result['tb_sparse_records_masks.sv']=s
 result['tb_sparse_records_faults.sv']=adapt_rf(originals['tb_sparse_writeback_faults.sv']).replace('sparse_writeback_fault_test','sparse_records_fault_test').replace('tb_response_faults','tb_sparse_records_faults')
 stalls=wb_adapt((ROOT/'hardware/tb/tb_record_epoch16_stalls.sv').read_text().replace('tb_record_epoch16_stalls','tb_sparse_records_stalls'))
 result['tb_sparse_records_stalls.sv']=adapt_rf(stalls)
 s=adapt_rf(cycle64_render(),paired=True).replace('sparse_writeback_cycle64','sparse_records')
 s=s.replace('#(.SPARSE_WB(0)) test();','#(.SPARSE_WB(1),.SPARSE_RF(0)) test();')
 result['tb_sparse_records_pilot.sv']=s
 return result
if __name__=='__main__':
 for name,s in render().items():
  p=ROOT/'hardware/tb'/name;p.write_text(s);print(p)
