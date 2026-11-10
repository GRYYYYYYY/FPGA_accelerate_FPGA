"""Isolated non-cold warm retry candidate, based on audited cancellation fix."""
from pathlib import Path
HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/warm_cancel_fixed_v2/sources')
def rep(s,a,b):
 assert s.count(a)==1,(a,s.count(a))
 return s.replace(a,b)
def make():
 s=(BASE/'warm_restore_receipt_join.sv').read_text()
 s=rep(s,'output wire owned,label_allow','output wire retry_window,\n output wire owned,label_allow')
 s=rep(s,'reg ls,ps,qs,ld,pd,qd;','reg ls,ps,qs,ld,pd,qd;reg failure_consumed,fence_released;\n wire retry_identity=arm_design==d&&arm_generation==g&&arm_checkpoint==cp&&arm_version>v;')
 s=rep(s,'assign arm_ready=!cold_rst&&!abort&&state==IDLE&&recovery_owned&&backend_drained&&retired;', '''// HALT retains business isolation throughout fence turnover and re-arm.
 // Acceptance of an invalid retry still lets the native coordinator return
 // its error; it cannot start restore services or erase the retained floor.
 assign retry_window=!cold_rst&&!abort&&state==HALT&&failure_consumed&&fence_released&&recovery_owned&&backend_drained&&retired;
 assign arm_ready=(!cold_rst&&!abort&&state==IDLE&&recovery_owned&&backend_drained&&retired)||retry_window;''')
 s=rep(s,'qd<=0;end\n  else if(fail_now)state<=HALT;', '''qd<=0;failure_consumed<=0;fence_released<=0;end
  else begin
   if(completion_consumed&&(state==HALT||state==WAIT||fail_now))failure_consumed<=1;
   if(failure_consumed&&!recovery_owned)fence_released<=1;
   // Fresh acceptance outranks old HALT fault/context drift. No ownership gap.
   if(state==HALT&&arm_valid&&arm_ready)begin
    failure_consumed<=0;fence_released<=0;
    if(arm_ok&&retry_identity)begin
     d<=arm_design;g<=arm_generation;cp<=arm_checkpoint;v<=arm_version;q<=arm_query;price<=arm_price;cookie<=arm_cookie;count<=arm_labels;pcrc<=arm_path_crc;qcrc<=arm_query_crc;
     ls<=0;ps<=0;qs<=0;ld<=0;pd<=0;qd<=0;state<=WAIT;
    end
   end
   else if(fail_now)state<=HALT;''')
 s=rep(s,'IDLE:if(arm_valid&&arm_ready)begin','IDLE:if(arm_valid&&arm_ready)begin\n    failure_consumed<=0;fence_released<=0;')
 s=rep(s,'  endcase\n end','  endcase\n  end\n end')
 (HERE/'warm_restore_receipt_join.sv').write_text(s)
 s=(BASE/'query_residency_system.sv').read_text()
 s=rep(s,'wire wm_arm_ready;','wire wm_arm_ready,wm_retry_window;')
 s=rep(s,'wire wm_rec_offer;', 'wire wm_rec_offer;\nwire wm_old_command=wm_owned&&!(wm_retry_window&&wm_rec_offer);')
 # All command fields switch together only in an actual new backend offer.
 for a,b in [('wm_rdesign','recover_design'),('wm_rcp','recover_checkpoint'),('wm_rcookie','recover_cookie'),('wm_rversion','recover_version'),('wm_rquery','recover_query'),('wm_rprice','recover_price'),('wm_snapshot_cookie','snapshot_cookie'),('wm_snapshot_count','snapshot_count'),('wm_pcrc','wm_path_crc'),('wm_qcrc','wm_query_crc')]:
  s=s.replace('wm_owned?'+a+':'+b,'wm_old_command?'+a+':'+b)
 s=rep(s,'.completion_consumed(k_rsp_valid&&k_rsp_ready),','.retry_window(wm_retry_window),.completion_consumed(k_rsp_valid&&k_rsp_ready),')
 (HERE/'query_residency_system.sv').write_text(s)
if __name__=='__main__':make()
