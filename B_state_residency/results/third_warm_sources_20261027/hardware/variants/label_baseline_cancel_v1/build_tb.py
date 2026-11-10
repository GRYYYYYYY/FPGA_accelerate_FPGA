from pathlib import Path
import runpy
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE=ROOT/'hardware/variants/label_baseline_crc_retry_v1/build_tb.py'
def make():
 s=runpy.run_path(str(BASE))['make']()
 a=s.index('task iter2_g2_warm_restore;');b=s.index('\nend endtask',a)+len('\nend endtask');task=s[a:b]
 start=task.index(' for(integer x=0;x<ls_count;x=x+1)begin');end=task.index(' if(bad_crc)begin',start)
 stream=task[start:end]
 stream=stream.replace('for(integer x=0;', 'begin : cancel_stream\n for(integer x=0;',1)
 mark='@(negedge clk);lr_s_valid=0;';assert mark in stream
 stream=stream.replace(mark,mark+'\n  if(x==20)begin wait(cancel_started);disable cancel_stream;end',1)+' end\n'
 task=task[:start]+stream+task[end:]
 start=task.index(' if(bad_crc)begin');end=task.index(' wait(wm_receipts[0]);',start)
 fail=''' if(cancel_started)begin
  wait(k_rsp_valid);repeat(8)begin @(negedge clk);if(k_rsp_status!=6||k_count!=2||!wm_owned||!wm_fault||recover_open||wm_receipts||lr_written!=20||lr_verified||cancel_r_count!=1||cancel_front_count!=1||!baseline_retired)$fatal(1,"cancel recovery quarantine");end
  $fdisplay(trace,"BASELINE_CANCEL_FAILURE %0d %0d %0d %0d %0d",cycles,k_rsp_status,k_count,lr_written,lr_verified);
  k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;abort=0;cancel_active=0;
  repeat(8)begin @(negedge clk);if(!wm_owned||!wm_fault||recover_open||qc_cmd_ready||rc_req_ready||pc_acquire_ready)$fatal(1,"cancel failure opened work");end
  cancel_retry_restore;disable crc_initial_attempt;
 end
'''
 task=task[:start]+fail+task[end:];s=s[:a]+task+s[b:]
 s=s.replace('crc_retry_restore','cancel_retry_restore').replace('CRC_RETRY_REJECT','CANCEL_RETRY_REJECT').replace('CRC_RETRY_OWNER_VERIFIED','CANCEL_RETRY_OWNER_VERIFIED').replace('CRC_HIGHER_ATTEMPT','CANCEL_HIGHER_ATTEMPT')
 decl='''reg cancel_hold_release=0,cancel_active=0;integer cancel_r_count=0,cancel_front_count=0,cancel_wait_count=0;
wire cancel_hold=!retry_started&&!cancel_hold_release&&((wm_owned&&k_labels_valid&&lr_written==20)||cancel_active);
'''
 s=s.replace('reg bcfg_valid=',decl+'reg bcfg_valid=',1)
 s=s.replace('baseline_mem(.clk(clk)', 'baseline_mem(.hold_r(cancel_hold),.clk(clk)',1)
 extra='''
initial begin
 @(negedge bench_rst);
 do @(posedge clk);while(!(bv&&by&&wm_owned&&k_labels_valid&&lr_written==20&&!retry_started));
 @(negedge clk);cancel_started=1;cancel_active=1;abort=1;
 $fdisplay(trace,"BASELINE_CANCEL_AR %0d %016h",cycles,ba);
 repeat(64)begin
  @(negedge clk);cancel_wait_count=cancel_wait_count+1;
  if(baseline_retired||baseline_physical||!baseline_owned||k_rsp_valid||k_target_reset||!wm_owned||recover_open||!lr_busy||cancel_r_count||f_all_drained||f_backend_idle)$fatal(1,"baseline cancel premature completion");
  $fdisplay(trace,"BASELINE_CANCEL_WAIT %0d %0d %0d %0d %0d %0d",cycles,baseline_retired,baseline_physical,baseline_owned,k_rsp_valid,lr_busy);
 end
 cancel_hold_release=1;$fdisplay(trace,"BASELINE_CANCEL_RELEASE %0d",cycles);
end
always @(posedge clk)if(!bench_rst&&cancel_active)begin
 if(brv&&brr)begin cancel_r_count=cancel_r_count+1;$fdisplay(trace,"BASELINE_CANCEL_R %0d",cycles);end
 if(baseline_rsp_valid&&baseline_rsp_ready)begin cancel_front_count=cancel_front_count+1;$fdisplay(trace,"BASELINE_CANCEL_FRONT %0d",cycles);end
end
'''
 return s.replace('\nendmodule',extra+'\nendmodule')
if __name__=='__main__':(HERE/'tb_cancel.sv').write_text(make())
