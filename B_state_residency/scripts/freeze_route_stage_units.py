"""Freeze restored route-label unit evidence without a system/timing claim."""
from pathlib import Path
import json
import shutil
from run_checkpoint_authority import ROOT, sha

p = Path('/tmp/B_state_residency_offer_20261025/route_stage_units_v1')
m = json.loads((p/'manifest.json').read_text())
a = json.loads((p/'source_bound_audit.json').read_text())
rp = ROOT/'results/route_stage_units_v1_restore_20261025.json'
r = json.loads(rp.read_text())
assert m['status'] == 'observed' and a['status'] == r['status'] == 'passed'
assert r['audit_byte_identical'] and r['audit_sha256'] == sha(p/'source_bound_audit.json')
assert a['manifest_sha256'] == sha(p/'manifest.json')
assert a['auditor_sha256'] == sha(ROOT/'scripts/audit_route_stage_units.py')
assert len(a['cases']) == 12 and a['exact_trace_comparisons'] == 8
assert a['generic_overlap_preserved']
for case in a['cases'].values():
    assert case['stage_checked_cycles'] > 0
for mode in ['baseline','default','factored']:
    for suite in ['checkpoint','checkpoint32']:
        case=a['cases'][f'{mode}_{suite}']
        assert case['stage_captures'] > 0 and case['stage_imports'] > 0
report = ROOT/'results/route_stage_units_20261029.json'
f = ROOT/'results/route_stage_units_sources_20261029'
assert not report.exists() and not f.exists()
report.write_text(json.dumps(dict(
    status='twelve_route_stage_unit_cases_passed', audit=a, restoration=r,
    full_system_validated=False, timing_qualified=False,
    scope='Original route/checkpoint8/32 and generic simultaneous replies preserved. '
          'Eight exact trace/cycle comparisons include every changed path and stage word. '
          'Old-tree reference compares all stage words after every checked clock, with nonempty import/export in CP cases. '
          'Controller with modeled backend only; no X/Z formal equivalence, full-system or OOC claim.'
), indent=2, sort_keys=True)+'\n')
f.mkdir()
files = {}


def copy(source, relative):
    target = f/relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    assert sha(source) == sha(target)
    files[str(relative)] = dict(source=str(source), sha256=sha(target))


for name, digest in m['bound'].items():
    assert sha(p/'tools'/name) == digest
    copy(p/'tools'/name, Path('tools')/name)
for name in ['labels.txt', 'manifest.json', 'source_bound_audit.json']:
    copy(p/name, Path('reports')/name)
for source in [report, rp, ROOT/'results/route_stage_write_factoring_20261029.json', ROOT/'results/route_stage_model_preflight_failure_20261029.json']:
    copy(source, Path('reports')/source.name)
for name in ['audit_route_stage_units.py', 'freeze_route_stage_units.py', 'analyze_route_stage_write_factoring_v2.py', 'analyze_route_stage_write_factoring.py']:
    copy(ROOT/'scripts'/name, Path('scripts')/name)
for case in m['cases']:
    name = f"{case['mode']}_{case['suite']}"
    for artifact in ['tb.sv', 'route_commit_controller.sv', 'events.txt', 'simulate.log', 'bank_events.txt', 'stage_events.txt']:
        copy(p/name/artifact, Path('cases')/name/artifact)
(f/'manifest.json').write_text(json.dumps(dict(
    status='frozen', files=files, full_system_validated=False, timing_qualified=False
), indent=2, sort_keys=True)+'\n')
print('ROUTE_STAGE_UNITS_FROZEN', len(files), 'files')
