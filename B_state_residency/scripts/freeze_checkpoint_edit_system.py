"""Freeze a genuinely restored CP full-system case; never infer timing acceptance."""
from pathlib import Path
import json
import shutil
from run_checkpoint_authority import ROOT, sha

p = Path('/tmp/B_state_residency_offer_20261025/checkpoint_edit_system_crc_pressure_v1')
m = json.loads((p/'manifest.json').read_text())
a = json.loads((p/'source_bound_audit.json').read_text())
rp = ROOT/'results'/f'{p.name}_restore_20261025.json'
r = json.loads(rp.read_text())
assert m['status'] == 'observed' and a['status'] == r['status'] == 'passed'
assert r['audit_byte_identical'] and r['audit_sha256'] == sha(p/'source_bound_audit.json')
assert a['manifest_sha256'] == sha(p/'manifest.json')
assert a['auditor_sha256'] == sha(ROOT/'scripts/audit_checkpoint_edit_system.py')
assert a['monitor_generator_sha256'] == sha(ROOT/'scripts/prepare_checkpoint_edit_monitor.py')
assert len(a['exact_comparisons']) == 27
c = a['checkpoint_edit_exclusion']
assert all(c[k] > 0 for k in ['cycles', 'safe', 'busy', 'requests', 'replies', 'imports', 'exports'])
assert c['requests'] == c['replies'] and c['edit'] >= 0
assert c['cycles'] == a['query_interface_exclusion']['cycles']
report = ROOT/'results/checkpoint_edit_system_crc_20261028.json'
f = ROOT/'results/checkpoint_edit_system_crc_sources_20261028'
assert not report.exists() and not f.exists()
# Check source integrity before creating any publication artifacts.
for name, entry in m['sources'].items():
    assert sha(p/'sources'/name) == entry['sha256'], name
report.write_text(json.dumps(dict(
    status='one_checkpoint_edit_full_system_case_passed', audit=a, restoration=r,
    full_matrix_complete=False, full_root_loops=None, timing_qualified=False,
    scope='One real four-query CRC pressure replay, actual CP-safe/edit ports, '
          '27 literal outputs and identical finish time. Archive actually restored and re-audited. '
          'No arbitrary-input proof, new full matrix, matched OOC, physical timing or board claim.'
), indent=2, sort_keys=True)+'\n')
f.mkdir()
files = {}


def copy(source, relative):
    target = f/relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    assert sha(source) == sha(target)
    files[str(relative)] = dict(source=str(source), sha256=sha(target))


for name in m['sources']:
    copy(p/'sources'/name, Path('sources')/name)
for name in ['manifest.json', 'source_bound_audit.json']:
    copy(p/name, Path('reports')/name)
for source in [report, rp]:
    copy(source, Path('reports')/source.name)
for name in ['run_checkpoint_edit_system.py', 'audit_checkpoint_edit_system.py',
             'freeze_checkpoint_edit_system.py', 'prepare_checkpoint_edit_monitor.py',
             'run_checkpoint_authority.py']:
    copy(ROOT/'scripts'/name, Path('scripts')/name)
copy(ROOT/'hardware/variants/checkpoint_edit_system_v1/build.py', Path('variant/build.py'))
v = ROOT/'hardware/variants/checkpoint_edit_exclusion_v1'
for name in ['build.py', 'manifest.json', 'CONTRACT.md']:
    copy(v/name, Path('parent')/name)
for mode in ['baseline', 'fixed']:
    for name in ['query_lifecycle.sv', 'query_residency_system.sv']:
        copy(v/mode/name, Path('parent')/mode/name)
for case in m['cases']:
    copy(p/case/'simulate.log', Path('cases')/case/'simulate.log')
(f/'manifest.json').write_text(json.dumps(dict(
    status='frozen', files=files, full_matrix_complete=False, timing_qualified=False
), indent=2, sort_keys=True)+'\n')
print('CHECKPOINT_EDIT_SYSTEM_FROZEN', len(files), 'files')
