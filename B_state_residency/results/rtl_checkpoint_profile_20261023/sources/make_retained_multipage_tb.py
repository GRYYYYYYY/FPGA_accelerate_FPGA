"""Four backing pages, all five fields, nonzero query/price and repeated ID reuse."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def generate():
 text=(ROOT/'hardware/tb/tb_retained_endpoint.sv').read_text()
 text=text[:text.index('    initial begin\n        clear_golden;cold_start;')]
 text=text.replace('module tb_retained_endpoint;','module tb_retained_endpoint_multipage;')
 text+='''    function automatic [159:0] page_word(input integer page_id,node_id);
        reg [159:0] word;
        begin
            word=0;
            word[31:0]=32'h7fc12345 ^ (page_id<<8) ^ node_id;
            word[63:32]=32'h80000000 | (page_id<<16) | node_id;
            word[95:64]=32'hffffffff - page_id*64-node_id;
            word[127:96]=32'h3f800000 + page_id*64+node_id;
            word[135:128]=255-page_id-node_id;
            page_word=word;
        end
    endfunction
    task automatic expected_page(input integer page_id);
        begin clear_golden;golden_bitmap=64'h8000000000000001;
            golden[0]=page_word(page_id,0);golden[63]=page_word(page_id,63);pack_golden;end
    endtask
    integer pidx,nodeidx,fidx,roundidx,cp_total=0;
    reg [159:0] target_word,partial_word;
    initial begin
        clear_golden;cold_start;
        request(0,0,0,2,9,0,0,0,0,0,0,0,0,0,0,0);
        for(pidx=0;pidx<4;pidx=pidx+1)begin
            expected_page(pidx);
            request(1,pidx,100+pidx,2,9,0,0,0,0,pidx,0,0,0,0,0,0);
            for(nodeidx=0;nodeidx<2;nodeidx=nodeidx+1)begin
                target_word=page_word(pidx,nodeidx==0?0:63);partial_word=0;
                for(fidx=0;fidx<5;fidx=fidx+1)begin
                    partial_word[fidx*32 +:32]=target_word[fidx*32 +:32];
                    request(3,pidx,100+pidx,2,9,0,nodeidx==0?0:63,fidx,target_word[fidx*32 +:32],pidx,0,partial_word,1,1,0,0);
                end
            end
            request(5,pidx,100+pidx,2,9,0,0,0,0,pidx,0,0,0,0,pidx,0);
            request(4,pidx,100+pidx,2,9,0,0,0,0,pidx,0,0,0,0,0,0);
        end
        for(roundidx=0;roundidx<8;roundidx=roundidx+1)begin
            simple(12,0,999,0,7,0,0,0);cp_total=cp_total+1;
            if(allocated!=4 || fault || !cp_finish_seen || !cp_memory_seen)$fatal(1,"multipage checkpoint metadata");
            for(pidx=0;pidx<4;pidx=pidx+1)begin
                expected_page(pidx);
                request(1,pidx,100+pidx,2,9,0,0,0,0,pidx,0,0,0,0,0,0);
                request(6,pidx,100+pidx,2,9,0,0,0,0,pidx,0,0,0,0,pidx,0);
                for(nodeidx=0;nodeidx<2;nodeidx=nodeidx+1)begin
                    target_word=page_word(pidx,nodeidx==0?0:63);
                    request(2,pidx,100+pidx,2,9,0,nodeidx==0?0:63,0,0,pidx,0,target_word,1,0,0,0);
                end
                request(4,pidx,100+pidx,2,9,0,0,0,0,pidx,0,0,0,0,0,0);
            end
        end
        if(cp_total!=8 || completed_transfers!=36 || tag_wraps!=4 || checks!=221)$fatal(1,"multipage coverage");
        $display("RETAINED_MULTIPAGE_PASS pages=4 fields=5 checkpoints=%0d transfers=%0d checks=%0d tag_wraps=%0d",cp_total,completed_transfers,checks,tag_wraps);
        $finish;
    end
endmodule
'''
 return text
if __name__=='__main__':(ROOT/'hardware/tb/tb_retained_endpoint_multipage.sv').write_text(generate())
