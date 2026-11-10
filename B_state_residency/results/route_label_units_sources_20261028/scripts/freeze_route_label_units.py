"""Freeze restored route-label unit evidence without a system/timing claim."""
from pathlib import Path
import json
import shutil
from run_checkpoint_authority import ROOT, sha

p = Path('/tmp/B_state_residency_offer_20261025/route_label_units_v2')
m = json.loads((p/'manifest.json').read_text())
a = json.loads((p/'source_bound_audit.json').read_text())
rp = ROOT/'results/route_label_units_v2_restore_20261025.json'
r = json.loads(rp.read_text())
assert m['status'] == 'observed' and a['status'] == r['status'] == 'passed'
assert r['audit_byte_identical'] and r['audit_sha256'] == sha(p/'source_bound_audit.json')
assert a['manifest_sha256'] == sha(p/'manifest.json')
assert a['auditor_sha256'] == sha(ROOT/'scripts/audit_route_label_units_v2.py')
assert len(a['cases']) == 12 and a['exact_trace_comparisons'] == 7
assert a['generic_overlap_specialization_counterexample']
report = ROOT/'results/route_label_units_20261028.json'
f = ROOT/'results/route_label_units_sources_20261028'
assert not report.exists() and not f.exists()
report.write_text(json.dumps(dict(
    status='twelve_route_label_unit_cases_passed', audit=a, restoration=r,
    full_system_validated=False, timing_qualified=False,
    scope='Original route/checkpoint compatibility, separately masked native label backend, '
          'and explicit generic overlap difference. Controller RTL with modeled services. '
          'Actual five-client arbiter/adapter integration, full-system replay and OOC remain required. '
          'v1 testbench compile failure is preserved separately; production candidate unchanged.'
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
for source in [report, rp, ROOT/'results/route_label_exclusion_20261028.json',
               ROOT/'results/route_label_units_compile_failure_20261028.json']:
    copy(source, Path('reports')/source.name)
for name in ['audit_route_label_units_v2.py', 'freeze_route_label_units.py']:
    copy(ROOT/'scripts'/name, Path('scripts')/name)
for case in m['cases']:
    name = f"{case['mode']}_{case['suite']}"
    for artifact in ['tb.sv', 'route_commit_controller.sv', 'events.txt', 'simulate.log']:
        copy(p/name/artifact, Path('cases')/name/artifact)
(f/'manifest.json').write_text(json.dumps(dict(
    status='frozen', files=files, full_system_validated=False, timing_qualified=False
), indent=2, sort_keys=True)+'\n')
print('ROUTE_LABEL_UNITS_FROZEN', len(files), 'files')
