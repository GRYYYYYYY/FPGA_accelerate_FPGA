"""Add bitmap/offset/codec completeness checks to independent test variants."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def adapt(s):
 assert s.count('record_acks!=8')==2
 s=s.replace('record_acks!=8','record_acks!=expected_ack_count()')
 monitor='''    wire [1535:0] sparse_expected_blob={expected[2],expected[1],expected[0]};
    reg [7:0] sparse_export_seen=0;
    reg sparse_mask_seen=0;
    integer sparse_codec_count=0,sparse_exports=0,sparse_omitted=0,sparse_masks=0;
    function automatic integer expected_ack_count;
        integer bit_id;
        begin
            expected_ack_count=8;
            if(active_op==5)begin
                expected_ack_count=0;
                for(bit_id=0;bit_id<8;bit_id=bit_id+1)
                    expected_ack_count=expected_ack_count+expected[0][bit_id];
            end
        end
    endfunction
    always @(posedge clk)if(!rst)begin
        if(dut.state==6 && dut.q_valid && dut.q_status==0 && active_op==5)begin
            if(dut.q_payload!=={152'b0,expected[0][7:0]})$fatal(1,"WB snapshot bitmap differs from independent page");
            sparse_mask_seen=1;sparse_masks=sparse_masks+1;
        end
        if(dut.q_send && dut.q_ready && dut.q_op==9)begin
            if(!sparse_mask_seen || !expected[0][dut.q_offset] || sparse_export_seen[dut.q_offset])
                $fatal(1,"WB EXPORT absent/duplicate/unattested offset");
            sparse_export_seen[dut.q_offset]=1;sparse_exports=sparse_exports+1;
        end
        if(dut.memory.record_in_valid && dut.record_in_ready)begin
            if(dut.position!=sparse_codec_count || dut.present!==expected[0][dut.position]
               || dut.record!==sparse_expected_blob[8+dut.position*160 +:160])
                $fatal(1,"WB codec representation differs from independent page");
            sparse_codec_count=sparse_codec_count+1;
            if(!dut.present)sparse_omitted=sparse_omitted+1;
        end
        if(dut.q_send && dut.q_ready && dut.q_op==8 && active_op==5)begin
            if(!sparse_mask_seen || sparse_codec_count!=8 || sparse_export_seen!==expected[0][7:0])
                $fatal(1,"WB COMPLETE without exact offset coverage");
        end
    end
'''
 s=s.replace('    task automatic cold_start;',monitor+'    task automatic cold_start;',1)
 s=s.replace('stream_write=0;stream_read=0;record_acks=0;memory_completed=0;page_completed=0;', 'stream_write=0;stream_read=0;record_acks=0;memory_completed=0;page_completed=0;\n                sparse_export_seen=0;sparse_codec_count=0;sparse_mask_seen=0;')
 s=s.replace('$finish;', '$display("SPARSE_WB_COUNTS exports=%0d omitted=%0d masks=%0d",sparse_exports,sparse_omitted,sparse_masks);$finish;')
 return s

def directed():
 s=(ROOT/'hardware/tb/tb_record_epoch6_faults.sv').read_text()
 s=s[:s.index('    initial begin\n            for(err=1;err<=9;err=err+1)begin')]
 s=s.replace('module response_fault_test #(', 'module sparse_writeback_masks_test #(').replace('.EPOCH_BITS(6)','.EPOCH_BITS(16)')
 s+='''    integer mask_id,off_id,tries;
    task automatic finish_retry;
        begin
            tries=0;
            begin: retry_loop
                forever begin
                    send_host(11,0,0,0,0,0,0,0,0,0);
                    while(!rsp_valid)@(negedge clk);
                    if(rsp_status==7)begin
                        receive_host(7,0,0,0,0,1);tries=tries+1;
                        if(tries>20)$fatal(1,"finish retries exhausted");
                    end else begin receive_host(0,0,0,0,0,0);disable retry_loop;end
                end
            end
        end
    endtask
    initial begin
        clear_golden;cold_start;
        for(mask_id=0;mask_id<256;mask_id=mask_id+1)begin
            simple(0,0,0,0,0,0,0,0);simple(1,0,42,0,0,0,0,0);
            clear_golden;golden_bitmap=mask_id;
            for(off_id=0;off_id<8;off_id=off_id+1)if(golden_bitmap[off_id])begin
                // Even offsets are present zero records, distinct from absence.
                golden[off_id]=off_id%2 ? ((mask_id<<16)|off_id) : 0;
                request(3,0,42,0,0,0,off_id,0,golden[off_id][31:0],0,0,golden[off_id],1,1,0,0);
            end
            pack_golden;
            simple(5,0,42,0,0,0,0,0);simple(4,0,42,0,0,0,0,0);
            simple(1,1,42,0,0,0,0,0);
            simple(6,1,42,0,0,0,1,0);
            for(off_id=0;off_id<8;off_id=off_id+1)
                request(2,1,42,0,0,0,off_id,0,0,0,0,golden[off_id],golden_bitmap[off_id],0,0,0);
            simple(4,1,42,0,0,0,0,0);
            simple(10,0,0,0,0,0,0,1);finish_retry;
        end
        if(completed_transfers!=512 || completed_fences!=256 || fault || sparse_exports!=1024 || sparse_omitted!=1024 || sparse_masks!=256)
            $fatal(1,"mask coverage mismatch");
        $display("SPARSE_WB_MASKS_PASS masks=256 transfers=512 fences=256 checks=%0d",checks);
        $finish;
    end
endmodule
module tb_sparse_writeback_masks;sparse_writeback_masks_test test();endmodule
'''
 return adapt(s)

def render():
 return {'tb_sparse_writeback_masks.sv':directed(),
 'tb_sparse_writeback_pilot.sv':adapt((ROOT/'hardware/tb/tb_epoch16_endpoint_checkpoint_stream.sv').read_text().replace('epoch16_endpoint_checkpoint_stream','sparse_writeback_checkpoint_stream')),
 'tb_sparse_writeback_faults.sv':adapt((ROOT/'hardware/tb/tb_record_epoch6_faults.sv').read_text().replace('response_fault_test','sparse_writeback_fault_test').replace('tb_record_epoch6_faults','tb_sparse_writeback_faults').replace('.EPOCH_BITS(6)','.EPOCH_BITS(16)'))}
if __name__=='__main__':
 for name,s in render().items():
  p=ROOT/'hardware/tb'/name;p.write_text(s);print(p)
