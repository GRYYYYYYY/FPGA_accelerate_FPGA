"""Compare restored OOC observations; never promote a design to physical acceptance."""
from pathlib import Path
import json
import math
from run_checkpoint_authority import ROOT, sha

BASE = Path('/tmp/B_state_residency_offer_20261025')
RESOURCES = ('LUT', 'FF', 'BRAM', 'DSP', 'URAM')


def load_verified(name, date):
    p = BASE/name
    report_path = ROOT/'results'/f'{name.removesuffix("_v1")}_{date}.json'
    report = json.loads(report_path.read_text())
    m = json.loads((p/'manifest.json').read_text())
    a = json.loads((p/'source_bound_audit.json').read_text())
    receipt_path = ROOT/'results'/f'{name}_restore_20261025.json'
    receipt = json.loads(receipt_path.read_text())
    assert m['status'] == 'observed' and m['exit_code'] == 0
    assert report['status'] == 'matched_ooc_artifacts_restored'
    assert report['audit'] == a and report['restoration'] == receipt
    assert a['status'] == receipt['status'] == 'passed'
    assert receipt['audit_byte_identical']
    assert a['manifest_sha256'] == sha(p/'manifest.json')
    assert receipt['audit_sha256'] == sha(p/'source_bound_audit.json')
    assert len(m['rtl']) == len(set(m['rtl'])) == 133
    assert a['clock_period_ns'] == m['clock_period_ns'] == 10
    assert a['parameters'] == m['parameters']
    point = dict(name=name, resources={k:a['utilization'][k] for k in RESOURCES},
                 preplacement_wns_ns=a['preplacement_wns_ns'],
                 structurally_eligible=(a['check_timing_counts']['loops'] == 0
                     and not a['timing_loop_warnings'] and not a['critical_warnings']
                     and a['facts']['latches'] == a['facts']['blackboxes'] == 0),
                 loops=a['check_timing_counts']['loops'],
                 automatic_loop_cuts=len(a['timing_loop_warnings']),
                 report_sha256=sha(report_path), audit_sha256=sha(p/'source_bound_audit.json'),
                 restoration_sha256=sha(receipt_path), timing_qualified=False,
                 full_behavior_matrix_complete=report['full_behavior_matrix_complete'])
    assert all(math.isfinite(v) and v >= 0 for v in point['resources'].values())
    assert math.isfinite(point['preplacement_wns_ns'])
    return point, m


def dominates(left, right):
    """No larger in any resource, no worse slack, and strictly better somewhere."""
    if not left['structurally_eligible'] or not right['structurally_eligible']:
        return False
    no_worse = (all(left['resources'][k] <= right['resources'][k] for k in RESOURCES)
                and left['preplacement_wns_ns'] >= right['preplacement_wns_ns'])
    strict = (any(left['resources'][k] < right['resources'][k] for k in RESOURCES)
              or left['preplacement_wns_ns'] > right['preplacement_wns_ns'])
    return no_worse and strict


def compare(points):
    assert len({p['name'] for p in points}) == len(points)
    valid = [p for p in points if p['structurally_eligible']]
    assert valid, 'No structurally eligible comparison point'
    dominated_by = {p['name']:[q['name'] for q in valid if dominates(q,p)] for p in points}
    best_slack = max(p['preplacement_wns_ns'] for p in valid)
    least_lut = min(p['resources']['LUT'] for p in valid)
    return dict(dominated_by=dominated_by,
                non_dominated=[p['name'] for p in valid if not dominated_by[p['name']]],
                excluded_structurally=[p['name'] for p in points if not p['structurally_eligible']],
                best_preplacement_slack=[p['name'] for p in valid if p['preplacement_wns_ns']==best_slack],
                minimum_lut=[p['name'] for p in valid if p['resources']['LUT']==least_lut])


def main():
    q = json.loads((BASE/'route_stage_synth_followup_v1/manifest.json').read_text())
    assert q['status'] == 'observed' and q['stage'] == 'complete', 'Wait for restoration/freeze'
    specs = [('checkpoint_edit_synth_v1','20261028'), ('route_path_synth_v1','20261028'),
             ('route_stage_synth_v1','20261029')]
    loaded = [load_verified(*spec) for spec in specs]
    points = [p for p,m in loaded]
    reference = loaded[0][1]
    changed = {'route_commit_controller.sv', 'route_commit_host_adapter.sv'}
    for point,m in loaded:
        root = BASE/point['name']
        ref = BASE/specs[0][0]
        assert m['rtl'] == reference['rtl'] and m['parameters'] == reference['parameters']
        assert m['part'] == reference['part']
        assert (root/'clock.xdc').read_bytes() == (ref/'clock.xdc').read_bytes()
        assert (root/'synth.tcl').read_text() == (ref/'synth.tcl').read_text().replace(str(ref),str(root))
        for name in m['rtl']:
            assert sha(root/'sources'/name) == m['sources'][name], name
            if name not in changed:
                assert m['sources'][name] == reference['sources'][name], name
    comparisons = {}
    stage = points[2]
    for baseline in points[:2]:
        comparisons[baseline['name']] = dict(
            resource_delta={k:stage['resources'][k]-baseline['resources'][k] for k in RESOURCES},
            preplacement_wns_delta_ns=stage['preplacement_wns_ns']-baseline['preplacement_wns_ns'])
    analysis_path = ROOT/'results/route_stage_timing_path_20261029.json'
    path_analysis_sha = None
    if stage['structurally_eligible']:
        analysis = json.loads(analysis_path.read_text())
        assert analysis['audit_sha256'] == stage['audit_sha256']
        assert analysis['slack_ns'] == stage['preplacement_wns_ns']
        path_analysis_sha = sha(analysis_path)
    result = dict(status='restored_matched_ooc_tradeoff_observation',
                  analyzer_sha256=sha(Path(__file__)), points=points,
                  comparison=compare(points), stage_deltas=comparisons,
                  timing_path_analysis_sha256=path_analysis_sha,
                  physical_acceptance=False, production_selection=None,
                  scope='Same 133 RTL, part, parameters, Tcl and 10ns clock. '
                        'Resource/slack dominance describes these unplaced synthesis observations only. '
                        'Different worst path endpoints are not a same-path causal proof. '
                        'No candidate promotion, physical timing, new full matrix, or board-speed claim.')
    out = ROOT/'results/route_stage_tradeoff_20261029.json'
    assert not out.exists()
    out.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print('ROUTE_STAGE_TRADEOFF_OBSERVED', json.dumps(result['comparison'], sort_keys=True))


if __name__ == '__main__':
    main()
