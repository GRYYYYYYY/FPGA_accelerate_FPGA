"""Public-command four-query isolation and fence namespace reuse test."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def render():
 s=(ROOT/'hardware/tb/tb_record_epoch6_faults.sv').read_text()
 s=s[:s.index('    initial begin\n            for(err=1;err<=9;err=err+1)begin')]
 s=s.replace('module response_fault_test #(parameter integer SMALL=0,','module query_lifetime_test #(parameter integer TEST_EPOCH=6,SMALL=0,').replace('.EPOCH_BITS(6)', '.EPOCH_BITS(TEST_EPOCH)')
 return s+'''    integer qid,old_ar,attempts,finish_retries=0,keep_allocated;
    initial begin
        clear_golden;cold_start;
        for(qid=0;qid<4;qid=qid+1)begin
            simple(0,0,0,qid,0,0,0,0);
            simple(1,0,42,qid,qid,0,0,0);
            old_ar=ar_count;
            simple(6,0,42,qid,qid,8,0,0);
            if(allocated!=qid || ar_count!=old_ar)$fatal(1,"cross-query backing alias");
            simple(2,0,42,qid,qid,0,0,0);
            clear_golden;golden_bitmap=1;golden[0]=256+qid;pack_golden;
            request(3,0,42,qid,0,qid,0,0,256+qid,0,0,golden[0],1,1,0,0);
            request(5,0,42,qid,0,qid,0,0,0,qid,0,0,0,0,2*qid,0);
            simple(4,0,42,qid,qid,0,0,0);
            simple(1,1,42,qid,qid,0,0,0);
            request(6,1,42,qid,0,qid,0,0,0,qid,0,0,0,0,2*qid+1,0);
            request(2,1,42,qid,0,qid,0,0,0,0,0,golden[0],1,0,0,0);
            simple(4,1,42,qid,qid,0,0,0);
            if(allocated!=qid+1)$fatal(1,"prior query ownership discarded");
            if(qid==1)begin
                simple(12,0,0,0,0,3,0,0);
                if(allocated!=2)$fatal(1,"rejected checkpoint recycled backing");
            end
        end
        simple(0,0,0,0,0,5,0,0);
        request(0,0,0,0,1,0,0,0,0,0,5,0,0,0,0,0);
        simple(1,0,42,0,4,1,0,0);
        simple(12,0,0,0,0,3,0,0);
        if(allocated!=4 || page_leases!=0 || memory_leases!=0 || fault)
            $fatal(1,"rejections damaged retained state");
        simple(10,0,0,0,0,0,0,1);
        keep_allocated=allocated;attempts=0;
        begin: retry_finish
            forever begin
                send_host(11,0,0,0,0,0,0,0,0,0);
                while(!rsp_valid)@(negedge clk);
                if(rsp_status==7)begin
                    if(!draining || !dut.fence_open || allocated!=keep_allocated || page_leases!=0 || memory_leases!=0)
                        $fatal(1,"FENCE_WAIT changed lifetime state");
                    receive_host(7,0,0,0,0,1);finish_retries=finish_retries+1;
                    attempts=attempts+1;if(attempts>20)$fatal(1,"finish retry did not converge");
                end else begin receive_host(0,0,0,0,0,0);disable retry_finish;end
            end
        end
        if(allocated!=0 || dut.memory.memory_service.directory.epoch!=2)$fatal(1,"fence did not recycle directory");
        simple(0,0,0,0,0,0,0,0);
        simple(1,0,42,0,0,0,0,0);
        old_ar=ar_count;simple(6,0,42,0,0,8,0,0);
        if(allocated!=0 || ar_count!=old_ar)$fatal(1,"old backing visible after full fence");
        simple(2,0,42,0,0,0,0,0);simple(4,0,42,0,0,0,0,0);
        if(completed_transfers!=8 || completed_fences!=1 || completed_checkpoints!=0 || fault)
            $fatal(1,"lifetime coverage mismatch");
        $display("LIFETIME_DOMAINS_PASS epoch_bits=%0d retained_query_ids=4 transfers=8 full_recycles=1 checkpoint_rejections=2 namespace_exhaustions=2 checks=%0d retries=%0d",TEST_EPOCH,checks,finish_retries);
        $finish;
    end
endmodule
module tb_query_lifetime6;query_lifetime_test #(.TEST_EPOCH(6)) test();endmodule
module tb_query_lifetime16;query_lifetime_test #(.TEST_EPOCH(16)) test();endmodule
'''
if __name__=='__main__':
 p=ROOT/'hardware/tb/tb_query_lifetime.sv';p.write_text(render());print(p)
