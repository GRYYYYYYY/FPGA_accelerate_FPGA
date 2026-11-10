"""Freeze restored stage timing/tradeoff observations without selecting a production design."""
from pathlib import Path
import json
import shutil
from run_checkpoint_authority import ROOT, sha

base = Path('/tmp/B_state_residency_offer_20261025')
q = json.loads((base/'route_stage_synth_followup_v1/manifest.json').read_text())
assert q['status'] == 'observed' and q['stage'] == 'complete'
experiment = base/'route_stage_synth_v1'
a = json.loads((experiment/'source_bound_audit.json').read_text())
rp = ROOT/'results/route_stage_synth_v1_restore_20261025.json'
r = json.loads(rp.read_text())
assert a['status'] == r['status'] == 'passed' and r['audit_byte_identical']
assert a['manifest_sha256'] == sha(experiment/'manifest.json')
assert r['audit_sha256'] == sha(experiment/'source_bound_audit.json')
path = ROOT/'results/route_stage_timing_path_20261029.json'
tradeoff = ROOT/'results/route_stage_tradeoff_20261029.json'
analysis = json.loads(path.read_text())
comparison = json.loads(tradeoff.read_text())
assert analysis['audit_sha256'] == sha(experiment/'source_bound_audit.json')
assert analysis['analyzer_sha256'] == sha(ROOT/'scripts/analyze_route_stage_timing.py')
assert comparison['analyzer_sha256'] == sha(ROOT/'scripts/analyze_route_stage_tradeoff.py')
assert comparison['timing_path_analysis_sha256'] == sha(path)
assert comparison['production_selection'] is None and not comparison['physical_acceptance']
for point in comparison['points']:
    assert point['audit_sha256'] == sha(base/point['name']/'source_bound_audit.json')
freeze = ROOT/'results/route_stage_timing_sources_20261029'
assert not freeze.exists()
freeze.mkdir()
files = {}
sources = [path, tradeoff, rp, experiment/'source_bound_audit.json',
           ROOT/'results/checkpoint_edit_timing_path_20261028.json',
           ROOT/'results/route_path_timing_path_20261029.json',
           ROOT/'scripts/analyze_route_stage_timing.py',
           ROOT/'scripts/analyze_route_stage_tradeoff.py', Path(__file__)]
for source in sources:
    relative = Path('scripts' if source.suffix=='.py' else 'reports')/source.name
    dest = freeze/relative
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,dest)
    files[str(relative)] = dict(source=str(source),sha256=sha(dest))
    assert sha(source) == files[str(relative)]['sha256']
(freeze/'manifest.json').write_text(json.dumps(dict(status='frozen',files=files,
    physical_acceptance=False,production_selection=None,
    scope='Restored synthesis timing navigation and resource/slack comparisons only. No physical or production acceptance.'),indent=2,sort_keys=True)+'\n')
print('ROUTE_STAGE_ANALYSIS_FROZEN',len(files),'files')
