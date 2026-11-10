from pathlib import Path
import json,hashlib
from check_shadow_fixture_ready_control_logs_v1 import parse
R=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def positive(n):
 a,s,t,e,i,d=[33,18,5,11,251,251] if n=='ready_nba' else [30,16,5,10,254,254]
 return f'''PAYLOAD_GROUP_PASS group=KA active=15 stalled=0 transfers=5 edges=5 idle=269 idle_differences=269
PAYLOAD_GROUP_PASS group=PW active={a} stalled={s} transfers={t} edges={e} idle={i} idle_differences={d}
FULL_SHADOW_FIXTURE_READY_CANDIDATE_PASS outputs=346 unconditional=342 qualified=cp_m_data,k_a_node,k_a_net,p_m_wdata checks=190 reset_edges=5 original_end=1000000 last_checked=1201000 active={a} stalled={s} transfers={t} edges={e} idle={i} idle_differences={d}
$finish called at time : 1202 ns
'''
gold=positive('matching');assert parse(gold,'matching')['verdict']=='match';assert parse(positive('ready_nba'),'ready_nba')['verdict']=='match'
negative='Fatal: KA_FIXTURE_READY_INVARIANT phase=0 time=345999\n';assert parse(negative,'ka_unexpected_stall','KA_FIXTURE_READY_INVARIANT')['verdict']=='expected_rejection'
mutations={
 'duplicate_pass':gold+gold.splitlines()[2]+'\n',
 'missing_pass':'\n'.join(gold.splitlines()[:2]),
 'missing_KA':'\n'.join(gold.splitlines()[1:]),
 'duplicate_KA':gold+gold.splitlines()[0]+'\n',
 'KA_stall':gold.replace('active=15 stalled=0','active=15 stalled=1'),
 'KA_zero_transfers':gold.replace('transfers=5 edges=5','transfers=0 edges=5'),
 'KA_wrong_edges':gold.replace('transfers=5 edges=5','transfers=5 edges=4'),
 'KA_wrong_idle':gold.replace('idle=269','idle=268'),
 'PW_no_stall':gold.replace('group=PW active=30 stalled=16','group=PW active=30 stalled=0'),
 'CP_no_stall':gold.replace('last_checked=1201000 active=30 stalled=16','last_checked=1201000 active=30 stalled=0'),
 'short_reset':gold.replace('reset_edges=5','reset_edges=4'),
 'short_window':gold.replace('checks=190','checks=189'),
 'unknown_count':gold.replace('active=15','active=x'),
 'wrong_finish':gold.replace('1202 ns','1201 ns'),
 'wrong_terminal_time':gold.replace('original_end=1000000','original_end=999999'),
 'old_pass_marker':gold.replace('FULL_SHADOW_FIXTURE_READY_CANDIDATE_PASS','FULL_SHADOW_PROTOCOL_PASS'),
 'fatal_with_pass':gold+negative,
 'error_with_pass':'ERROR: bad\n'+gold}
for n,l in mutations.items():
 try:parse(l,'matching')
 except AssertionError:pass
 else:raise AssertionError(n)
for n,l in {'wrong_fatal':'Fatal: KA_DATA_UNKNOWN\n','duplicate_fatal':negative+negative,'pass_on_fault':negative+gold}.items():
 try:parse(l,'ka_unexpected_stall','KA_FIXTURE_READY_INVARIANT')
 except AssertionError:pass
 else:raise AssertionError(n)
out=R/'results/shadow_fixture_ready_log_parser_calibration_20261101.json';assert not out.exists();out.write_text(json.dumps({'status':'synthetic_log_parser_calibration_passed_not_simulation','positive_synthetic_logs':3,'rejected_corruptions':len(mutations)+3,'parser_sha256':sha(Path(__file__).with_name('check_shadow_fixture_ready_control_logs_v1.py')),'calibrator_sha256':sha(Path(__file__)),'scope':'Synthetic parser calibration only. Actual58 XSim controls not run; counts still require independent observed reconciliation.','full_system_functional_netlist_validated':False,'physical_gate_open':False},indent=2)+'\n');print('3 synthetic positives and',len(mutations)+3,'corruptions checked')
