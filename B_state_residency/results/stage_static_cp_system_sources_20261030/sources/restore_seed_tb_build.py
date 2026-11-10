"""Inject one optimized restore failure, then retry without external cold reset."""
from pathlib import Path
import runpy
HERE=Path(__file__).resolve().parent
replace=runpy.run_path(str(HERE/'build.py'))['replace']

def make():
    s=runpy.run_path(str(HERE/'base_tb.py'))['make']()
    s=replace(s,'reg seed_start_consumed=0;', '''
`ifdef SEED_CRC_FAILURE
localparam SEED_CRC_FAILURE=1;
`else
localparam SEED_CRC_FAILURE=0;
`endif
reg seed_failure_seen=0;
integer seed_trial=0;
reg seed_start_consumed=0;''')
    # Keep the pre-failure baseline prefix byte/cycle exact.
    marker=' $fdisplay(trace,"FOURTH_WARM_OWNER %0d %0d %0d",cycles,k_corrected,k_count);'
    s=replace(s,marker,marker+'\n seed_fail_then_retry;')
    begin=s.index('task fourth_query;')
    end=s.index('// Observe actual downstream acceptance',begin)
    part=s[begin:end]
    for old,new,count in [('query_version!=7','query_version!=8',3),
                          ('p_active_query!=1','p_active_query!=2',3),
                          ('p_active_price!=7','p_active_price!=8',3),
                          ('qcp_image[6]!=7','qcp_image[6]!=8',1),
                          ("qcp_image[7]!=32'h5d","qcp_image[7]!=32'h62",1),
                          ("k_rsp_cookie!=32'hc0040001||k_corrected!=3", "k_rsp_cookie!=32'hc0040002||k_corrected!=0",1)]:
        part=replace(part,old,new,count)
    s=s[:begin]+part+s[end:]
    old='''  if(lr_rsp_status!=0||lr_written!=781||lr_verified!=781||seed_requests!=3905)
   $fatal(1,"seed bypass restore completion mismatch");
  $fdisplay(seed_log,"PASS %0d %0d %0d %0d",cycles,seed_requests,lr_written,lr_verified);'''
    new='''  if(seed_trial==1)begin
   if(lr_rsp_status!=(SEED_CRC_FAILURE?8:7)||lr_written!=(SEED_CRC_FAILURE?780:0)||lr_verified||seed_requests!=(SEED_CRC_FAILURE?3900:3))
    $fatal(1,"seed failure native receipt");
   seed_failure_seen<=1;
   $fdisplay(seed_log,"FAIL %0d %0d %0d %0d %0d",cycles,seed_requests,lr_written,lr_verified,lr_rsp_status);
   $fdisplay(trace,"SEED_FAILURE_RECEIPT %0d %0d %0d %0d %0d",cycles,lr_rsp_status,lr_written,lr_verified,seed_requests);
  end else begin
   if(seed_trial!=2||lr_rsp_status!=0||lr_written!=781||lr_verified!=781||seed_requests!=3905)
    $fatal(1,"seed bypass retry completion mismatch");
   $fdisplay(seed_log,"PASS %0d %0d %0d %0d",cycles,seed_requests,lr_written,lr_verified);
  end'''
    s=replace(s,old,new)
    s=replace(s,'endmodule',(HERE/'failure_task.sv').read_text()+'\nendmodule')
    return s

if __name__=='__main__':(HERE/'tb_restore_seed.sv').write_text(make())
