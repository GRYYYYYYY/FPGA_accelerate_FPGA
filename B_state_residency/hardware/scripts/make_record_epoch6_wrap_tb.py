"""Build a composed endpoint lifetime test across a real 6-bit epoch wrap."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def render():
 s=(ROOT/'hardware/tb/tb_record_epoch6_faults.sv').read_text()
 start=s.index('    initial begin\n            for(err=1;err<=9;err=err+1)begin')
 main='''    integer finish_retries=0,attempts,old_ar;
    task automatic finish_with_retry;
        begin
            attempts=0;
            begin: retry_finish
                forever begin
                    send_host(11,0,0,0,0,0,0,0,0,0);
                    while(!rsp_valid)@(negedge clk);
                    if(rsp_status==7)begin
                        if(!draining || !dut.fence_open || allocated!=1 || page_leases!=0 || memory_leases!=0)
                            $fatal(1,"FENCE_WAIT changed lifetime state");
                        receive_host(7,0,0,0,0,1);finish_retries=finish_retries+1;
                        attempts=attempts+1;if(attempts>20)$fatal(1,"finish retry did not converge");
                    end else begin
                        receive_host(0,0,0,0,0,0);disable retry_finish;
                    end
                end
            end
        end
    endtask
    initial begin
        clear_golden;cold_start;simple(0,0,0,0,0,0,0,0);
        for(loop_id=0;loop_id<70;loop_id=loop_id+1)begin
            clear_golden;golden_bitmap=1;golden[0]=loop_id+1;pack_golden;
            simple(1,0,42,0,0,0,0,0);
            old_ar=ar_count;simple(6,0,42,0,0,8,0,0);
            if(allocated!=0 || ar_count!=old_ar)$fatal(1,"stale backing visible after recycle");
            request(2,0,42,0,0,0,0,0,0,0,0,0,0,0,0,0);
            request(3,0,42,0,0,0,0,0,loop_id+1,0,0,golden[0],1,1,0,0);
            simple(5,0,42,0,0,0,0,0);simple(4,0,42,0,0,0,0,0);
            simple(1,1,42,0,0,0,0,0);simple(6,1,42,0,0,0,1,0);
            request(2,1,42,0,0,0,0,0,0,0,0,golden[0],1,0,0,0);
            simple(4,1,42,0,0,0,0,0);simple(10,0,0,0,0,0,0,1);
            finish_with_retry;
            if(dut.memory.memory_service.directory.epoch!=((loop_id+1)%63)+1)
                $fatal(1,"wrong epoch after recycle=%0d",loop_id+1);
            simple(0,0,0,0,0,0,0,0);
        end
        if(completed_fences!=70 || completed_transfers!=140 || tag_wraps!=17 || index_wraps!=1 || index_clear_cycles!=128 || index_overflows!=0 || fault)
            $fatal(1,"composite wrap coverage fences=%0d transfers=%0d tags=%0d wraps=%0d clear=%0d",completed_fences,completed_transfers,tag_wraps,index_wraps,index_clear_cycles);
        $display("COMPOSITE_WRAP_PASS queries=70 transfers=140 tag_wraps=17 epoch_wraps=1 clear_cycles=128 retries=%0d checks=%0d",finish_retries,checks);
        $finish;
    end
endmodule
module tb_record_epoch6_wrap;response_fault_test test();endmodule
'''
 return s[:start]+main
if __name__=='__main__':
 p=ROOT/'hardware/tb/tb_record_epoch6_wrap.sv';p.write_text(render());print(p)
