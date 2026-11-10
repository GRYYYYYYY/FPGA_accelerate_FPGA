"""Exercise a full 16-bit epoch rollover using legal endpoint commands."""
from make_record_epoch6_wrap_tb import render as previous_render,ROOT
def render():
 s=previous_render().replace('.EPOCH_BITS(6)','.EPOCH_BITS(16)').replace("#(64'd500000000000)","#(64'd200000000)")
 s=s.replace('integer finish_retries=0,attempts,old_ar;','integer finish_retries=0,attempts,old_ar,expected_allocation;')
 s=s.replace('            attempts=0;','            attempts=0;expected_allocation=allocated;').replace('allocated!=1 || page_leases!=0','allocated!=expected_allocation || page_leases!=0')
 start=s.index('    initial begin\n        clear_golden;cold_start;simple')
 s=s[:start]+'''    integer selected_page,data_queries=0;
    initial begin
        clear_golden;cold_start;simple(0,0,0,0,0,0,0,0);
        for(loop_id=0;loop_id<65536;loop_id=loop_id+1)begin
            if(loop_id==0 || loop_id>=65533)begin
                data_queries=data_queries+1;selected_page=(loop_id==65533 || loop_id==65534)?43:42;
                clear_golden;golden_bitmap=1;golden[0]=loop_id+1;pack_golden;
                simple(1,0,selected_page,0,0,0,0,0);
                old_ar=ar_count;simple(6,0,selected_page,0,0,8,0,0);
                if(allocated!=0 || ar_count!=old_ar)$fatal(1,"stale backing visible across epoch16 lifetime");
                request(2,0,selected_page,0,0,0,0,0,0,0,0,0,0,0,0,0);
                request(3,0,selected_page,0,0,0,0,0,loop_id+1,0,0,golden[0],1,1,0,0);
                simple(5,0,selected_page,0,0,0,0,0);simple(4,0,selected_page,0,0,0,0,0);
                simple(1,1,selected_page,0,0,0,0,0);simple(6,1,selected_page,0,0,0,1,0);
                request(2,1,selected_page,0,0,0,0,0,0,0,0,golden[0],1,0,0,0);
                simple(4,1,selected_page,0,0,0,0,0);
            end
            simple(10,0,0,0,0,0,0,1);finish_with_retry;
            if(dut.memory.memory_service.directory.epoch!=((loop_id+1)%65535)+1)$fatal(1,"wrong 16bit epoch");
            simple(0,0,0,0,0,0,0,0);
            if((loop_id+1)%4096==0)$display("EPOCH16_LIFECYCLE_PROGRESS recycled=%0d",completed_fences);
        end
        if(completed_fences!=65536 || data_queries!=4 || completed_transfers!=8 || tag_wraps!=16384 || index_wraps!=1 || index_clear_cycles!=128 || index_overflows!=0 || fault || checks!=196649+finish_retries)
            $fatal(1,"epoch16 lifecycle coverage");
        $display("EPOCH16_WRAP_PASS queries=65536 transfers=8 data_queries=4 tag_wraps=16384 epoch_wraps=1 clear_cycles=128 retries=%0d checks=%0d",finish_retries,checks);
        $finish;
    end
endmodule
module tb_record_epoch16_wrap;response_fault_test test();endmodule
'''
 return s
if __name__=='__main__':(ROOT/'hardware/tb/tb_record_epoch16_wrap.sv').write_text(render())
