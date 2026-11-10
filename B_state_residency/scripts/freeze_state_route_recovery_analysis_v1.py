"""Freeze observed recovery timing navigation without selecting an RTL candidate."""
from pathlib import Path
import json
import shutil
from run_checkpoint_authority import ROOT, sha

p=Path('/tmp/B_state_residency_offer_20261025/checkpoint_edit_route_recovery_v1')
owner=p.parent/'checkpoint_edit_route_recovery_followup_v1'
gate=json.loads((owner/'manifest.json').read_text())
assert gate['status']=='observed' and gate['stage']=='complete'
out=ROOT/'results/checkpoint_edit_route_recovery_timing_20261030.json'
a=json.loads(out.read_text())
assert a['status']=='restored_route_recovery_path_navigation'
assert a['analyzer_sha256']==sha(ROOT/'scripts/analyze_state_route_recovery_v1.py')
assert a['parser_sha256']==sha(ROOT/'scripts/parse_state_timing_paths.py')
assert a['summary_parser_sha256']==sha(ROOT/'scripts/audit_state_ooc_physical_v2.py')
assert a['owner_manifest_sha256']==sha(owner/'manifest.json')
assert a['audit_sha256']==sha(p/'source_bound_audit.json')
rp=ROOT/'results/checkpoint_edit_route_recovery_v1_restore_20261025.json'
r=json.loads(rp.read_text()); assert r['status']=='passed' and r['audit_byte_identical']
assert r['audit_sha256']==a['audit_sha256'] and sha(rp)==a['restoration_sha256']
ap=ROOT/'results/checkpoint_edit_route_recovery_20261030.json'; assert sha(ap)==a['acceptance_sha256']
physical=ROOT/'results/checkpoint_edit_route_recovery_sources_20261030'
assert sha(physical/'manifest.json')==a['physical_freeze_manifest_sha256']
for name,entry in json.loads((physical/'manifest.json').read_text())['files'].items():
    assert sha(physical/name)==entry['sha256']==sha(Path(entry['source']))
freeze=ROOT/'results/checkpoint_edit_route_recovery_timing_sources_20261030'; assert not freeze.exists()
freeze.mkdir(); files={}
def copy(source,relative):
    dest=freeze/relative; dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,dest); files[str(relative)]=dict(source=str(source),sha256=sha(dest))
    assert sha(source)==files[str(relative)]['sha256']
for stage,name in a['report_files'].items():
    assert sha(p/name)==a['report_sha256'][stage]
    copy(p/name,Path('reports')/f'{stage}.rpt')
for name in ['analyze_state_route_recovery_v1.py','freeze_state_route_recovery_analysis_v1.py',
             'parse_state_timing_paths.py','audit_state_ooc_physical_v2.py']:
    copy(ROOT/'scripts'/name,Path('scripts')/name)
for source in [out,rp,ap,ROOT/'results/checkpoint_edit_timing_path_20261028.json']:
    copy(source,Path('observations')/source.name)
for name in ['manifest.json','source_bound_audit.json']:
    copy(p/name,Path('experiment')/name)
copy(owner/'manifest.json',Path('owner/manifest.json'))
copy(physical/'manifest.json',Path('physical_freeze/manifest.json'))
(freeze/'manifest.json').write_text(json.dumps(dict(status='frozen',files=files,
    timing_qualified=False,board_acceptance=False,candidate_selected=False),indent=2,sort_keys=True)+'\n')
print('ROUTE_RECOVERY_TIMING_FROZEN',len(files))
