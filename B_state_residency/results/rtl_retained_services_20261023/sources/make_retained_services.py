"""New service variants; opcode5 is trusted ID-only recycle, not host checkpoint."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def replace(text,before,after):
 assert text.count(before)==1,before
 return text.replace(before,after)
def outputs():
 page=(ROOT/'hardware/rtl/backing_page_service_indexed.sv').read_text()
 for before,after in [
 ('module backing_page_service_indexed #(','module backing_page_service_retained #('),
 ('backing_frame_directory_indexed #(','backing_frame_directory_retained #('),
 ('// cmd4=lookup owner without allocation (UNREADY on miss); 5..7 invalid.','// cmd4=lookup owner; cmd5=trusted ID-only recycle; 6..7 invalid.'),
 ('if(cmd_op>4)','if(cmd_op>5)'),
 ('else if(cmd_op==1 && fault)','else if((cmd_op==1 || cmd_op==5) && fault)'),
 ('4:dir_op<=5;default:dir_op<=7;','4:dir_op<=5;5:dir_op<=6;default:dir_op<=7;')]:page=replace(page,before,after)
 record=(ROOT/'hardware/rtl/record_backing_service_indexed.sv').read_text()
 record=replace(record,'module record_backing_service_indexed #(','module record_backing_service_retained #(')
 record=replace(record,'backing_page_service_indexed #(','backing_page_service_retained #(')
 tb=(ROOT/'hardware/tb/tb_record_backing_service.sv').read_text()
 tb=replace(tb,'module tb_record_backing_service;','module tb_record_backing_service_retained;\n    integer checkpoint_aw,checkpoint_ar;')
 tb=replace(tb,'record_backing_service #(.FRAMES(64),.INDEX_BITS(6))','record_backing_service_retained #(.FRAMES(64),.INDEX_BITS(6),.HASH_BITS(8),.PROBE_LIMIT(8),.EPOCH_BITS(2))')
 tb=replace(tb,'for(j=5;j<8;j=j+1)','for(j=6;j<8;j=j+1)')
 anchor='        // Four independent completed transfers retain address leases until'
 insertion='''        // All published raw pages survive an internal transaction-ID recycle.
        checkpoint_aw=aw_count;checkpoint_ar=ar_count;
        request(5,0,0,0,0,2,0,0);
        request(5,0,0,0,1,0,0,0);
        if(allocated!=64 || leased!=0 || aw_count!=checkpoint_aw || ar_count!=checkpoint_ar)
            $fatal(1,"checkpoint metadata or unexpected AXI");
        txid=0;
        for(fr=0;fr<64;fr=fr+1)begin
            request(4,24'h100000+fr,0,0,0,0,fr,1);
            transfer_page(fr,fr,txid,1,0);
            cookie=make_cookie(24'h100000+fr,txid,1,0);
            request(5,0,0,0,1,2,0,0);
            request(2,0,fr,cookie,0,0,fr,1);txid=txid+1;
        end
        $display("RETAINED_SERVICE_CONTENT_PASS pages=64 records=4096");
'''
 tb=replace(tb,anchor,insertion+anchor)
 return {'hardware/rtl/backing_page_service_retained.sv':page,'hardware/rtl/record_backing_service_retained.sv':record,'hardware/tb/tb_record_backing_service_retained.sv':tb}
if __name__=='__main__':
 for name,text in outputs().items():(ROOT/name).write_text(text)
