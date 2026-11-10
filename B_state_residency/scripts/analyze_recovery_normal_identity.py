"""Prove state-qualified coordinator admission identities without editing RTL."""
from itertools import product
from pathlib import Path
import json
from run_checkpoint_authority import ROOT, sha

p = Path('/tmp/B_state_residency_offer_20261025/combined_loops_synth_v1')
m = json.loads((p / 'manifest.json').read_text())
a = json.loads((p / 'source_bound_audit.json').read_text())
assert m['status'] == 'observed' and a['status'] == 'passed'
assert a['manifest_sha256'] == sha(p / 'manifest.json')
src = p / 'sources/recovery_coordinator.sv'
assert sha(src) == m['sources']['recovery_coordinator.sv']
s = src.read_text()
equations = [
    'localparam NORMAL=0,DRAIN=1,RESET=2,RECONFIG=3,AS=4,AW=5,OS=6,OW=7,NEXT=8,LABELS=9,FAILWAIT=10,DONE=11,REARM=12;',
    'reg[3:0]state;',
    'wire unexpected=(a_rsp_valid&&state!=AW&&!(state==AS&&a_ready))||(o_rsp_valid&&state!=OW&&!(state==OS&&o_ready));',
    'wire fail_now=(abort&&state!=REARM)||timeout||unexpected;',
    'assign fault=!cold_rst&&(stopped||fail_now);',
    'assign staged_valid=!cold_rst&&!abort&&prepared&&!cfg_rsp_valid&&state==NORMAL&&!fault;',
    'assign permit_work=!cold_rst&&!prepared&&configured&&!fault&&state==NORMAL&&!cfg_rsp_valid&&!cfg_valid&&!recover_valid;',
    'assign j_ready=!cold_rst&&!prepared&&configured&&!fault&&state==NORMAL&&!cfg_rsp_valid&&(j_op==1||j_op==2)&&(duplicate||journal_count<ENTRIES);',
    'assign recover_ready=!cold_rst&&!prepared&&configured&&state==NORMAL&&!cfg_rsp_valid&&!cfg_valid&&!j_valid&&!unexpected&&(!fault||(stopped&&retry_safe&&backend_drained&&normal_retired));',
    'assign cfg_ready=!cold_rst&&!fault&&state==NORMAL&&!cfg_rsp_valid&&!recover_valid&&!j_valid&&backend_drained&&normal_retired;',
]
for equation in equations:
    assert s.count(equation) == 1, equation

# gate abstracts each unchanged conjunction of the remaining admission inputs.
# timeout is arbitrary, covering a superset of its realizable sequential values.
count = 0
for state in range(16):
    for (cold, stopped, abort, timeout, av, ov, ar, ore, safe, drained,
         retired, gate) in product([False, True], repeat=12):
        unexpected = (av and state != 5 and not (state == 4 and ar)) or (ov and state != 7 and not (state == 6 and ore))
        fault = not cold and (stopped or (abort and state != 12) or timeout or unexpected)
        normal_fault = stopped or abort or timeout or av or ov
        normal_unexpected = av or ov
        normal_gate = not cold and state == 0 and gate
        ordinary_old = normal_gate and not fault
        ordinary_new = normal_gate and not normal_fault
        assert ordinary_old == ordinary_new
        retry_override = stopped and safe and drained and retired
        retry_old = normal_gate and not unexpected and (not fault or retry_override)
        retry_new = normal_gate and not normal_unexpected and (not normal_fault or retry_override)
        assert retry_old == retry_new
        assert not ordinary_new or not fault
        count += 1

result = dict(status='normal_admission_boolean_identity_not_rtl_validation', valuations=count,
    reference=str(p), reference_audit_sha256=sha(p / 'source_bound_audit.json'),
    source_sha256=sha(src), analyzer_sha256=sha(Path(__file__)), checked_source_expressions=equations,
    candidate_predicates=dict(normal_fault='stopped || abort || timeout || a_rsp_valid || o_rsp_valid',
                              normal_unexpected='a_rsp_valid || o_rsp_valid'),
    ordinary_outputs=['staged_valid', 'permit_work', 'j_ready', 'cfg_ready'],
    separate_retry_output='recover_ready',
    proven=['All four ordinary outputs retain their value after substitution under their existing NORMAL/cold_rst gates',
            'recover_ready retains the stopped/safe/drained/retired override and its value',
            'State-qualified ordinary permission implies the original complete fault is false'],
    limitations=['Two-state combinational identities only, no X/Z or sequential proof',
                 'Full fault, fail_now and unexpected outside these NORMAL-gated outputs must remain unchanged',
                 'Does not justify replacing publication fault or other arbitrary fault consumers',
                 'No production RTL modification, synthesis, simulation or full-root loop-removal claim'])
out = ROOT / 'results/recovery_normal_identity_20261027.json'
assert not out.exists()
out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print('RECOVERY_NORMAL_LOCAL_IDENTITIES', count, 'valuations; no RTL modification')
