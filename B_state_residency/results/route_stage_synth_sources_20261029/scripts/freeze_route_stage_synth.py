"""Freeze actually restored matched CP OOC; keep physical timing unqualified."""
from pathlib import Path
import json
import shutil
from run_checkpoint_authority import ROOT, sha

p = Path('/tmp/B_state_residency_offer_20261025/route_stage_synth_v1')
m = json.loads((p/'manifest.json').read_text())
a = json.loads((p/'source_bound_audit.json').read_text())
rp = ROOT/'results'/f'{p.name}_restore_20261025.json'
r = json.loads(rp.read_text())
assert m['status'] == 'observed' and a['status'] == r['status'] == 'passed'
assert r['audit_byte_identical'] and r['audit_sha256'] == sha(p/'source_bound_audit.json')
assert a['manifest_sha256'] == sha(p/'manifest.json')
assert a['auditor_sha256'] == sha(ROOT/'scripts/audit_route_stage_synth.py')
ref = Path(m['reference'])
assert ref.name == 'route_path_synth_v1'
assert sha(ref/'source_bound_audit.json') == m['reference_audit_sha256']
ra = json.loads((ref/'source_bound_audit.json').read_text())
delta = {k: a['utilization'][k]-ra['utilization'][k]
         for k in ['LUT', 'FF', 'BRAM', 'DSP', 'URAM']}
report = ROOT/'results/route_stage_synth_20261029.json'
f = ROOT/'results/route_stage_synth_sources_20261029'
assert not report.exists() and not f.exists()
for name, digest in m['sources'].items():
    assert sha(p/'sources'/name) == digest
report.write_text(json.dumps(dict(
    status='matched_ooc_artifacts_restored', audit=a, restoration=r,
    reference_audit_sha256=sha(ref/'source_bound_audit.json'),
    utilization_delta_candidate_minus_reference=delta,
    preplacement_wns_delta_ns=a['preplacement_wns_ns']-ra['preplacement_wns_ns'],
    cp_timing_reference=a['cp_timing_reference'],
    utilization_delta_candidate_minus_cp=a['utilization_delta_candidate_minus_cp'],
    preplacement_wns_delta_candidate_minus_cp_ns=a['preplacement_wns_delta_candidate_minus_cp_ns'],
    timing_qualified=False, full_behavior_matrix_complete=False,
    scope='Stage-write factoring on matched path OOC, with independent CP timing reference. '
          'Same 133 production sources, parameters, part and 10ns constraints. '
          'Worst endpoints can differ; slack delta is not same-path proof. '
          'No physical implementation, IO timing, board frequency or acceleration conclusion.'
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
for source in [p/'manifest.json', p/'source_bound_audit.json', rp, report]:
    copy(source, Path('reports')/source.name)
copy(ref/'source_bound_audit.json', Path('reports/reference_audit.json'))
cp_ref=Path(a['cp_timing_reference']['root'])
assert sha(cp_ref/'source_bound_audit.json')==a['cp_timing_reference']['audit_sha256']
copy(cp_ref/'source_bound_audit.json', Path('reports/cp_timing_reference_audit.json'))
for name in ['prepare_route_stage_synth.py', 'audit_route_stage_synth.py',
             'freeze_route_stage_synth.py', 'run_restore_seed_synth.py',
             'inspect_restore_seed_synth.py', 'analyze_restore_seed_loops.py',
             'audit_restore_seed_diagnostics.py', 'run_checkpoint_authority.py']:
    copy(ROOT/'scripts'/name, Path('scripts')/name)
v = ROOT/'hardware/variants'
copy(v/'route_stage_system_v1/build.py', Path('variants/system/build.py'))
for name in ['build.py', 'manifest.json', 'CONTRACT.md']:
    copy(v/'route_stage_write_v1'/name, Path('variants/parent')/name)
for mode in ['baseline', 'fixed']:
    for name in ['route_commit_controller.sv', 'route_commit_host_adapter.sv']:
        copy(v/'route_stage_write_v1'/mode/name, Path('variants/parent')/mode/name)
(f/'manifest.json').write_text(json.dumps(dict(
    status='frozen', files=files, timing_qualified=False
), indent=2, sort_keys=True)+'\n')
print('ROUTE_STAGE_SYNTH_FROZEN', len(files), 'files')
