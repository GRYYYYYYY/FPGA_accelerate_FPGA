"""Defer a no-write capacity refusal once; retain the normal two-pass fast path."""
from pathlib import Path
HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/warm_retry_system_v2/sources/recovery_coordinator.sv')
def rep(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def make():
 s=BASE.read_text();s=rep(s,'reg configured,owned,stopped,verify_pass;', 'reg configured,owned,stopped,verify_pass;reg deferred_capacity,repair_retry;')
 s=rep(s,'stopped<=0;verify_pass<=0;error_code<=0;', 'stopped<=0;verify_pass<=0;deferred_capacity<=0;repair_retry<=0;error_code<=0;')
 s=rep(s,'index<=0;verify_pass<=0;reset_ticks<=0;owner_cookie<=recover_cookie;', 'index<=0;verify_pass<=0;deferred_capacity<=0;repair_retry<=0;reset_ticks<=0;owner_cookie<=recover_cookie;')
 s=rep(s,"a_cookie=rsp_cookie^index^(verify_pass?32'h80000000:0)","a_cookie=rsp_cookie^index^(verify_pass?32'h80000000:0)^(repair_retry?32'h40000000:0)")
 a='''     else if(o_status!=0||o_rsp_cookie!=owner_cookie||o_count>65535||o_occupancy>65535||(o_count!=0&&o_occupancy==0))fail(3);'''
 b='''     // Owner status5 is a pre-write capacity refusal. An earlier missing
     // owner can depend on a later excess owner freeing the same full pool.
     // Only accept the known unchanged response, defer once, then fail closed
     // if capacity is still unavailable. Real bus/errors never take this path.
     else if(!verify_pass&&!repair_retry&&o_op==1&&o_status==5&&o_rsp_cookie==owner_cookie&&observed_refs==0&&o_count==observed_refs&&o_occupancy==observed_occ)begin deferred_capacity<=1;state<=NEXT;end
'''+a
 s=rep(s,a,b)
 a='''     else if(!verify_pass)begin verify_pass<=1;index<=0;state<=AS;end'''
 b='''     else if(!verify_pass)begin
      if(deferred_capacity&&!repair_retry)begin repair_retry<=1;deferred_capacity<=0;index<=0;state<=AS;end
      else begin verify_pass<=1;index<=0;state<=AS;end
     end'''
 s=rep(s,a,b);return s
if __name__=='__main__':(HERE/'recovery_coordinator.sv').write_text(make())
