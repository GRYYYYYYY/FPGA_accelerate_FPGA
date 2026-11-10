"""Check a source-bound Boolean reduction; do not modify or claim to fix RTL."""
from itertools import product
from pathlib import Path
import json
from run_checkpoint_authority import ROOT, sha

p = Path('/tmp/B_state_residency_offer_20261025/restore_seed_synth_on_v1')
m = json.loads((p / 'manifest.json').read_text())
a = json.loads((p / 'source_bound_audit.json').read_text())
assert a['status'] == 'passed' and a['manifest_sha256'] == sha(p / 'manifest.json')
names = ['route_commit_controller.sv', 'route_commit_host_adapter.sv']
sources = {n: (p / 'sources' / n).read_text() for n in names}
for n in names:
    assert sha(p / 'sources' / n) == m['sources'][n]
required = {
    names[0]: [
        'localparam IDLE=0,LS=1,LW=2,OS=3,OW=4;',
        'reg[2:0]state;',
        'wire drift=owned&&(!active||!lease||q!=active_query||price!=active_price||version!=active_version||ctx_design!=active_design);',
        'wire timed_out=owned&&!rsp_valid&&!stopped&&elapsed>=MAX_CYCLES-1;',
        'wire bad_l=state==LW&&l_rsp_valid&&(l_status!=0||!l_present);',
        'wire bad_o=state==OW&&o_rsp_valid&&(o_status!=0||o_rsp_cookie!=rsp_cookie);',
        'wire unexpected=(l_rsp_valid&&state!=LW&&!(state==LS&&l_ready))||(o_rsp_valid&&state!=OW&&!(state==OS&&o_ready));',
        'wire fail_now=abort||drift||timed_out||bad_l||bad_o||unexpected;',
        'assign fault=!rst&&(stopped||fail_now);',
        'assign busy=!rst&&(owned||state!=IDLE||rsp_valid||cp_busy);',
    ],
    names[1]: [
        '.rst(rst||cp_reset_held)', '.abort(abort)',
        'assign block_external=held||c_busy||c_fault;',
        'assign l_rsp_valid=held&&b_l_rsp_valid;',
        'assign o_rsp_valid=held&&b_o_rsp_valid;',
        '.busy(c_busy),.fault(c_fault)',
    ],
}
for name, expressions in required.items():
    for expression in expressions:
        assert sources[name].count(expression) == 1, (name, expression)

# core_rst includes both the external reset and the adapter's held CP reset.
# Conditions involving data values are abstracted as unconstrained booleans;
# this is a superset of legal data combinations, not a reachability assumption.
count = 0
for state in range(8):
    for (core_rst, held, owned, rsp, cp_busy, stopped, abort, ctx_bad,
         elapsed_limit, blv, bov, lr, ore, bad_ld, bad_od) in product([False, True], repeat=15):
        lv, ov = held and blv, held and bov
        drift = owned and ctx_bad
        timeout = owned and not rsp and not stopped and elapsed_limit
        bad_l = state == 2 and lv and bad_ld
        bad_o = state == 4 and ov and bad_od
        unexpected = (lv and state != 2 and not (state == 1 and lr)) or (ov and state != 4 and not (state == 3 and ore))
        fault = not core_rst and (stopped or abort or drift or timeout or bad_l or bad_o or unexpected)
        busy = not core_rst and (owned or state != 0 or rsp or cp_busy)
        original = held or busy or fault
        reduced = held or busy or (not core_rst and (stopped or abort))
        assert original == reduced
        count += 1

result = dict(status='local_boolean_identity_verified_not_rtl_validation', valuations=count,
    reference=str(p), reference_audit_sha256=sha(p / 'source_bound_audit.json'),
    source_sha256={n: sha(p / 'sources' / n) for n in names},
    analyzer_sha256=sha(Path(__file__)), checked_source_expressions=required,
    original='held || c_busy || c_fault',
    reduced='held || c_busy || (!controller_rst && (controller_stopped || controller_abort))',
    reasoning='If held or c_busy is true, both expressions block. Otherwise non-reset controller is idle, unowned and has no result or CP operation; both routed response valids are zero. Drift, timeout, bad-response and unexpected-response contributions are then false. During controller reset its busy and fault are both zero.',
    limitations=['Two-state combinational identity only; no X/Z, sequential or timing proof',
                 'Uses actual adapter response qualification; not an identity for an isolated controller with arbitrary response valids',
                 'No production RTL change, structural experiment or full-system behavior claim',
                 'A candidate would need an explicit controller output; hierarchical private-state references are not a production interface',
                 'Full-root DCP diagnosis still required; this does not establish removal of a reported loop'])
out = ROOT / 'results/route_block_identity_20261027.json'
assert not out.exists()
out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print('ROUTE_BLOCK_LOCAL_IDENTITY', count, 'valuations; no RTL modification')
