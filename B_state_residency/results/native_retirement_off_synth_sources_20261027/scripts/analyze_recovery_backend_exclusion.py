"""Check actual native wiring's request-ready / response-valid exclusion.

This is a source-bound two-state compositional check, not an RTL formal tool.
It does not change the generic coordinator's protocol or any production source.
"""
from itertools import product
from pathlib import Path
import json, re
from run_checkpoint_authority import ROOT, sha

p = Path('/tmp/B_state_residency_offer_20261025/combined_loops_synth_v1')
m = json.loads((p / 'manifest.json').read_text())
a = json.loads((p / 'source_bound_audit.json').read_text())
assert a['status'] == 'passed' and a['manifest_sha256'] == sha(p / 'manifest.json')
names = ['checkpoint_authority_reader.sv', 'checkpoint_authority_rotator.sv',
         'query_residency_system.sv', 'residency_system.sv',
         'transaction_fence.sv', 'recovery_coordinator.sv']
text = {n: (p / 'sources' / n).read_text() for n in names}
for n in names:
    assert sha(p / 'sources' / n) == m['sources'][n]
required = {
 names[0]: [
    'localparam IDLE=0,CORE_RESET=1,CFG_SEND=2,CFG_WAIT=3,CFG_REPLY=4,OWNER_SEND=5,OWNER_WAIT=6,REPLY=7;',
    'reg[2:0]state;',
    'assign req_ready=!rst&&state==IDLE&&!cfg_rsp_valid&&!cfg_valid&&!rearm_valid&&configured&&!fault&&!abort&&drained&&!c_busy;',
    'assign rsp_valid=!rst&&state==REPLY;'],
 names[1]: [
    'assign req_ready=!rst&&state==IDLE&&!cfg_valid&&!publish_valid&&!discard_valid&&!rearm_valid&&(active_bank?b1_req_ready:b0_req_ready);',
    'assign rsp_valid=active_bank?b1_rsp_valid:b0_rsp_valid;'],
 names[2]: [
    'assign k_a_ready=!ap_offer&&!ap_owned&&ap_native_ready;',
    'assign k_a_rsp_valid=!ap_owned&&ap_native_valid;',
    '.req_ready(ap_native_ready)', '.rsp_valid(ap_native_valid)',
    '.k_a_ready(k_a_ready)', '.k_a_rsp_valid(k_a_rsp_valid)'],
 names[3]: [
    'assign k_o_ready=f_cbr[9];', 'assign k_o_rsp_valid=f_cbrv[9];',
    '.cb_ready(f_cbr)', '.cb_rsp_valid(f_cbrv)',
    '.a_ready(k_a_ready)', '.a_rsp_valid(k_a_rsp_valid)',
    '.o_ready(k_o_ready)', '.o_rsp_valid(k_o_rsp_valid)'],
 names[4]: [
    'localparam IDLE=0,LREQ=1,LRSP=2,LDRAIN=3,ROUTE=4,RDRAIN=5,BLOCKED=6,RECWAIT=7,RECSEND=8,RECRUN=9,RECDRAIN=10;',
    'reg[3:0]state;',
    's_ready=0;s_rsp_valid=0;cb_ready=0;cb_rsp_valid=0;d_valid=0;d_rsp_ready=0;choice=-1;dep_accept=0;',
    'if(!rst)begin',
    'if(state==RECRUN)begin\n    d_valid=cb_valid&CALLBACK_MASK&~callback_pending;\n    cb_ready=d_ready&CALLBACK_MASK&~callback_pending;\n    cb_rsp_valid=d_rsp_valid&callback_pending;d_rsp_ready=cb_rsp_ready&callback_pending;'],
 names[5]: [
    'localparam NORMAL=0,DRAIN=1,RESET=2,RECONFIG=3,AS=4,AW=5,OS=6,OW=7,NEXT=8,LABELS=9,FAILWAIT=10,DONE=11,REARM=12;',
    'reg[3:0]state;',
    'wire unexpected=(a_rsp_valid&&state!=AW&&!(state==AS&&a_ready))||(o_rsp_valid&&state!=OW&&!(state==OS&&o_ready));'],
}
for name, expressions in required.items():
    for expression in expressions:
        assert text[name].count(expression) == 1, (name, expression)
for bank in [0, 1]:
    lines = [line for line in text[names[1]].splitlines() if 'checkpoint_authority_reader #' in line and f' bank{bank}(' in line]
    assert len(lines) == 1
    assert f'.req_ready(b{bank}_req_ready)' in lines[0]
    assert f'.rsp_valid(b{bank}_rsp_valid)' in lines[0]
assert len(re.findall(r'\bcb_ready\s*=', text[names[4]])) == 2
assert len(re.findall(r'\bcb_rsp_valid\s*=', text[names[4]])) == 2

# Abstract all other readiness gates as arbitrary booleans; this overapproximates
# every combination of configuration, faults, drains and reset administration.
leaf_count = 0
leaf_pairs = set()
for state, rst, gate in product(range(8), [False, True], [False, True]):
    ready = not rst and state == 0 and gate
    valid = not rst and state == 7
    assert not (ready and valid)
    leaf_pairs.add((ready, valid))
    leaf_count += 1
authority_count = 0
for bank0, bank1, active, outer_gate, ap_owned, ap_offer in product(
        sorted(leaf_pairs), sorted(leaf_pairs), [0, 1], [False, True], [False, True], [False, True]):
    ready, valid = [bank0, bank1][active]
    native_ready = outer_gate and ready
    a_ready = not ap_offer and not ap_owned and native_ready
    a_valid = not ap_owned and valid
    assert not (a_ready and a_valid)
    authority_count += 1
fence_count = 0
for state in range(16):
    for rst, mask, pending, dr, dv in product([False, True], repeat=5):
        enabled = not rst and state == 9
        o_ready = enabled and dr and mask and not pending
        o_valid = enabled and dv and pending
        assert not (o_ready and o_valid)
        fence_count += 1
coordinator_count = 0
for state, (ar, av), (ore, ov) in product(range(16), sorted(leaf_pairs), sorted(leaf_pairs)):
    old = (av and state != 5 and not (state == 4 and ar)) or (ov and state != 7 and not (state == 6 and ore))
    specialized = (av and state != 5) or (ov and state != 7)
    assert old == specialized
    coordinator_count += 1
# Outside that integrated contract the generic coordinator deliberately permits
# a response alongside AS/OS request acceptance. A default-off specialization
# is required; silently changing every coordinator instance would be wrong.
counterexamples = []
for state, ar, av, ore, ov in [(4, True, True, False, False), (6, False, False, True, True)]:
    old = (av and state != 5 and not (state == 4 and ar)) or (ov and state != 7 and not (state == 6 and ore))
    specialized = (av and state != 5) or (ov and state != 7)
    assert not old and specialized
    counterexamples.append(dict(state=state, a_ready=ar, a_rsp_valid=av, o_ready=ore, o_rsp_valid=ov,
                                generic_unexpected=old, specialized_unexpected=specialized))
result = dict(status='native_interface_exclusion_verified_not_rtl_validation',
    reference=str(p), reference_audit_sha256=sha(p / 'source_bound_audit.json'),
    source_sha256={n: sha(p / 'sources' / n) for n in names},
    analyzer_sha256=sha(Path(__file__)), checked_source_expressions=required,
    valuations=dict(reader=leaf_count, rotator_and_host_mux=authority_count,
                    callback_fence=fence_count, coordinator_under_exclusion=coordinator_count),
    permitted_ready_reply_pairs=sorted(leaf_pairs), generic_overlap_counterexamples=counterexamples,
    scope='Composition of actual native reader/rotator/AP mux and callback lane9 wiring, all two-state FSM encodings and arbitrary residual readiness gates. Request READY and response VALID are mutually exclusive at both coordinator backends. Not a general AXI property, reachability proof, X/Z proof, RTL formal verification or full-root structural result. No production code changed; specialization must default off for generic backends.')
out = ROOT / 'results/recovery_backend_exclusion_20261027.json'
assert not out.exists()
out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print('NATIVE_BACKEND_EXCLUSION', result['valuations'], 'generic_overlap_counterexamples', len(counterexamples))
