from pathlib import Path
import runpy
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'label_source_crc_v1/build_tb.py'
def make():
 s=runpy.run_path(str(BASE))['make']()
 a=s.index('task iter2_g2_warm_restore;');b=s.index('\nend endtask',a)+len('\nend endtask');original=s[a:b]
 # Build the retry from the existing good native restore flow, not mock callbacks.
 retry=original.replace('task iter2_g2_warm_restore;','task crc_retry_restore;')
 x=retry.index(' if(bad_crc)begin');y=retry.index(' wait(wm_receipts[0]);',x);retry=retry[:x]+retry[y:]
 retry=retry.replace('as_recover_version=4;as_recover_query=2;', 'as_recover_version=5;as_recover_query=3;')
 retry=retry.replace('k_corrected!=2','k_corrected!=0').replace('ITER2_OWNER_REPAIRED','CRC_RETRY_OWNER_VERIFIED')
 retry=retry.replace('query_version!=4||p_active_query!=2||p_active_price!=4','query_version!=5||p_active_query!=3||p_active_price!=5')
 begin='''task crc_retry_restore;begin
 cancel_started=1;retry_started=1;bad_crc=0;crc_pin_flip=0;retry_cookie=32'hc0020000;
 k_rec_valid=1;do @(posedge clk);while(!k_rec_ready);@(negedge clk);k_rec_valid=0;
 wait(k_rsp_valid);repeat(8)begin @(negedge clk);if(k_rsp_status!=1||k_rsp_cookie!=retry_cookie||k_count!=2||!wm_owned||!wm_fault||recover_open)$fatal(1,"CRC same attempt admitted");end
 $fdisplay(trace,"CRC_RETRY_REJECT %0d %0d %0d %08h",cycles,k_rsp_status,k_count,k_rsp_cookie);
 k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;repeat(8)@(negedge clk);
 retry_cookie=32'hc0020001;
 $fdisplay(trace,"CRC_HIGHER_ATTEMPT %0d",cycles);
'''
 retry=retry.replace('task crc_retry_restore;begin\n',begin,1)
 original=original.replace('task iter2_g2_warm_restore;begin','task iter2_g2_warm_restore;begin: crc_initial_attempt')
 old=' $fflush(trace);$fclose(trace);$display("LABEL_CRC_REJECT_PASS");$finish;'
 assert original.count(old)==1;original=original.replace(old,' crc_retry_restore;disable crc_initial_attempt;')
 s=s[:a]+original+s[b:]
 s=s.replace('system.controller.last_version!=4||p_active_query!=2||p_active_price!=4','system.controller.last_version!=5||p_active_query!=3||p_active_price!=5')
 # Parameterize the source fault via the existing plusarg; this selected run sets it.
 return s.replace('\nendmodule',retry+'\nendmodule')
if __name__=='__main__':HERE.joinpath('tb_retry.sv').write_text(make())
