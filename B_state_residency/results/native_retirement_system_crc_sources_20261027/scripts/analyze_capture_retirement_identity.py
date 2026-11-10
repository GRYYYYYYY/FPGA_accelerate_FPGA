"""Prove the redundant capture reply gate under actual zero-depth retirement."""
from pathlib import Path
from itertools import product
import json
from run_checkpoint_authority import ROOT,sha

p=Path('/tmp/B_state_residency_offer_20261025/route_block_system_crc_pressure_v1')
m=json.loads((p/'manifest.json').read_text());a=json.loads((p/'source_bound_audit.json').read_text())
rpath=ROOT/'results/route_block_system_crc_pressure_v1_restore_20261025.json'
r=json.loads(rpath.read_text())
assert m['status']=='observed'and a['status']==r['status']=='passed'
assert a['manifest_sha256']==sha(p/'manifest.json')and r['audit_byte_identical']
assert r['audit_sha256']==sha(p/'source_bound_audit.json')
expressions={
 'priced/candidate_recursive_query_core.sv':[
  'expansion_capture #(.DEPTH(4),.CAPACITY(32)) child_capture(',
  '.busy(capture_busy),.fault(capture_fault),.depth(capture_depth),',
  '.result_valid(e_result_valid),',
  ' assign retired_idle=!rst&&!busy&&!arb_g_busy&&!arb_d_busy&&!arb_io_busy&&!pc_arb_busy&&\n capture_depth==0&&b_retired_idle&&\n !g_rsp_valid&&!d_rsp_valid&&!b_result_valid&&!ce_result_valid&&!e_result_valid&&\n !m_rsp_valid&&!a_rsp_valid&&!s_rsp_valid&&!c_rsp_valid&&!t_rsp_valid&&!o_rsp_valid&&!o_b_rsp_valid&&!p_result_valid;'],
 'capture/expansion_capture.sv':[
  'children_frames #(.DEPTH(DEPTH),.CAPACITY(CAPACITY),.CONTEXT_BITS(512)) frames(',
  '.capture_active(capturing),.fault(frame_fault),.error_code(frame_error),.depth(depth),',
  '.frame_done(frame_done),',
  ' assign result_valid=frame_done&&state==0&&(fault||!expand_valid||result_offered);'],
 'capture/children_frames.sv':[
  ' wire has_frame=level!=0;',
  ' assign depth=level;',
  " assign frame_done=!rst&&!capturing&&has_frame&&!push&&((fault||abort)?!presented[top]:cursors[top]==counts[top]);"]}
source_hash={}
for n,guards in expressions.items():
    f=p/'sources'/n;s=f.read_text();assert sha(f)==m['sources'][n]['sha256']
    for guard in guards:assert s.count(guard)==1,(n,guard)
    source_hash[n]=sha(f)
count=0;reply_seen=0
for state in range(4):
    for values in product([False,True],repeat=11):
        has_frame,rst,capturing,push,frame_fault_or_abort,presented,cursor_equal,capture_fault,expand_valid,offered,other_idle=values
        frame_done=not rst and not capturing and has_frame and not push and (not presented if frame_fault_or_abort else cursor_equal)
        reply=frame_done and state==0 and (capture_fault or not expand_valid or offered)
        original=other_idle and not has_frame and not reply
        candidate=other_idle and not has_frame
        assert original==candidate
        assert not reply or has_frame
        count+=1;reply_seen+=int(reply)
assert reply_seen>0
result=dict(status='zero_depth_retirement_identity_not_rtl_validation',
    analyzer_sha256=sha(Path(__file__)),reference=str(p),reference_audit_sha256=sha(p/'source_bound_audit.json'),
    reference_restore_sha256=sha(rpath),source_sha256=source_hash,checked_source_expressions=expressions,
    valuations=count,nonvacuous_reply_valuations=reply_seen,
    rewrite='Remove only !e_result_valid from query core retired_idle, retaining capture_depth==0 and every other retirement gate.',
    scope='Source-bound two-state Boolean identity. Zero/nonzero abstraction covers every 32-bit level. The native capture result implies nonzero depth without FSM reachability assumptions. Not an X/Z proof, sequential formal proof, synthesis result or full-system validation.')
out=ROOT/'results/capture_retirement_identity_20261027.json';assert not out.exists()
out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('CAPTURE_RETIREMENT_IDENTITY',count,'reply_true',reply_seen)
