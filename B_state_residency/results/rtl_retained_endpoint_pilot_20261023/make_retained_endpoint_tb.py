from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def generate():
 text=(ROOT/'hardware/tb/tb_memory_endpoint_indexed.sv').read_text()
 text=text[:text.index('    initial begin\n        clear_golden;cold_start;')]
 text=text.replace('module memory_endpoint_indexed_test #(parameter integer SMALL=0);','module tb_retained_endpoint;\n    localparam integer SMALL=1;')
 text=text.replace('memory_scratch_endpoint_indexed #(','memory_scratch_endpoint_retained #(')
 text+='''    integer checkpoint_count=0;
    reg cp_finish_seen=0,cp_memory_seen=0;
    always @(posedge clk)begin
        if(rst)begin cp_finish_seen<=0;cp_memory_seen<=0;end
        else begin
            if(dut.state==21)begin cp_finish_seen<=0;cp_memory_seen<=0;end
            if(dut.state==25 && dut.q_valid && dut.q_status==0)cp_finish_seen<=1;
            if(dut.state==26 && dut.m_send && dut.m_ready)begin
                if(!cp_finish_seen || page_leases!=0 || memory_leases!=0)$fatal(1,"checkpoint before page drain");
            end
            if(dut.state==27 && dut.m_valid && dut.m_status==0)cp_memory_seen<=1;
            if(dut.state==28 && !cp_memory_seen)$fatal(1,"query resume before directory reset");
            if(dut.state>=21 && cmd_ready)$fatal(1,"checkpoint exposed host ingress");
            if(dut.q_send && dut.q_op>=12)$fatal(1,"public checkpoint leaked to queue controls");
        end
    end
    initial begin
        clear_golden;cold_start;
        simple(12,0,0,0,0,3,0,0);
        simple(0,0,0,0,0,0,0,0);
        simple(1,0,0,0,0,0,0,0);
        simple(12,0,0,0,0,4,0,0);
        golden_bitmap=1;golden[0]=123;pack_golden;
        request(3,0,0,0,0,0,0,0,123,0,0,123,1,1,0,0);
        simple(12,0,0,0,0,4,0,0);
        simple(5,0,0,0,0,0,0,0);
        simple(4,0,0,0,0,0,0,0);
        for(loop_id=0;loop_id<20;loop_id=loop_id+1)begin
            // Garbage public query/price must not replace the retained identity.
            send_host(12,3,99,3,15,7,63,4,32'hdeadbeef,0);
            while(!rsp_valid)begin @(negedge clk);if(cmd_ready)$fatal(1,"early host acceptance");end
            if(!cp_finish_seen || !cp_memory_seen || allocated!=1 || fault)$fatal(1,"checkpoint result");
            // Hold a competing QUERY throughout the stalled successful response.
            cmd_valid=1;cmd_op=0;cmd_query=2;
            repeat(12)begin @(negedge clk);if(cmd_ready)$fatal(1,"host accepted while checkpoint response held");end
            cmd_valid=0;
            receive_host(0,0,0,0,0,0);checkpoint_count=checkpoint_count+1;
            simple(0,0,0,0,0,5,0,0); // Internal resume consumes same query tag.
            simple(1,0,0,0,0,0,0,0);
            simple(6,0,0,0,0,0,0,0); // Both generation0 and transaction0 reused.
            request(2,0,0,0,0,0,0,0,0,0,0,123,1,0,0,0);
            simple(4,0,0,0,0,0,0,0);
        end
        simple(0,0,0,1,0,0,0,0);
        simple(12,0,0,1,0,3,0,0); // Multiple query namespaces forbid retention.
        fence_and_next_query;
        simple(12,0,0,0,0,0,0,0); // Ordinary recycle restores exclusivity.
        if(allocated!=0 || tag_wraps<10)$fatal(1,"checkpoint lifecycle coverage");
        $display("RETAINED_ENDPOINT_PASS checkpoints=%0d transfers=%0d checks=%0d tag_wraps=%0d",checkpoint_count+1,completed_transfers,checks,tag_wraps);
        $finish;
    end
endmodule
'''
 return text
if __name__=='__main__':(ROOT/'hardware/tb/tb_retained_endpoint.sv').write_text(generate())
