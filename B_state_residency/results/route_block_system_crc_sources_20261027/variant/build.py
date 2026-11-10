"""Expose the source-proven idle fault term without weakening full route faults."""
from pathlib import Path
import hashlib, json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = Path('/tmp/B_state_residency_offer_20261025/combined_loops_synth_v1')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def sources(fixed):
    m = json.loads((BASE / 'manifest.json').read_text())
    assert m['status'] == 'observed' and m['exit_code'] == 0
    proof = json.loads((ROOT / 'results/route_block_identity_20261027.json').read_text())
    assert proof['status'] == 'local_boolean_identity_verified_not_rtl_validation'
    assert proof['valuations'] == 262144
    result = {}
    for n in ['route_commit_controller.sv', 'route_commit_host_adapter.sv']:
        p = BASE / 'sources' / n
        assert sha(p) == m['sources'][n] == proof['source_sha256'][n]
        result[n] = p.read_text()
    if fixed:
        s = result['route_commit_controller.sv']
        old = 'output wire busy,fault,output reg[PATH_SLOTS-1:0]slot_valid,'
        assert s.count(old) == 1
        s = s.replace(old, 'output wire busy,fault,idle_fault,output reg[PATH_SLOTS-1:0]slot_valid,')
        old = ' assign fault=!rst&&(stopped||fail_now);'
        assert s.count(old) == 1
        s = s.replace(old, ''' // This reduced term is for the host adapter's !held && !busy branch only.
 // Full fault below retains unexpected responses, drift, timeout and errors.
 assign idle_fault=!rst&&(stopped||abort);
 assign fault=!rst&&(stopped||fail_now);''')
        result['route_commit_controller.sv'] = s
        s = result['route_commit_host_adapter.sv']
        for old, new in [
            ('wire c_ready,c_busy,c_fault,', 'wire c_ready,c_busy,c_fault,c_idle_fault,'),
            ('assign block_external=held||c_busy||c_fault;',
             'assign block_external=held||c_busy||c_idle_fault;'),
            ('.busy(c_busy),.fault(c_fault),.slot_valid(slot_valid)',
             '.busy(c_busy),.fault(c_fault),.idle_fault(c_idle_fault),.slot_valid(slot_valid)'),
        ]:
            assert s.count(old) == 1, old
            s = s.replace(old, new)
        result['route_commit_host_adapter.sv'] = s
    return result

if __name__ == '__main__':
    for mode in ['baseline', 'fixed']:
        d = HERE / mode
        d.mkdir()
        for name, text in sources(mode == 'fixed').items():
            (d / name).write_text(text)
    print('ROUTE_BLOCK_CANDIDATE_PREPARED_NOT_VALIDATED')
