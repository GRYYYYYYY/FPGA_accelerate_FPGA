"""Freeze full route-recovery observations after byte-identical restored audit."""
from pathlib import Path
import json
import shutil
import sys
from run_checkpoint_authority import ROOT, sha

p=Path(sys.argv[1]).resolve(); assert p.name=='checkpoint_edit_route_recovery_v1'
m=json.loads((p/'manifest.json').read_text()); a=json.loads((p/'source_bound_audit.json').read_text())
rp=ROOT/'results'/f'{p.name}_restore_20261025.json'; r=json.loads(rp.read_text())
assert m['status']=='observed' and m['stage']=='complete' and m['exit_code']==0
assert a['status']==r['status']=='passed' and r['audit_byte_identical']
assert a['manifest_sha256']==sha(p/'manifest.json') and r['audit_sha256']==sha(p/'source_bound_audit.json')
assert a['auditor_sha256']==sha(ROOT/'scripts/audit_state_route_recovery_v1.py')
assert a['independent_reopened_dcp_matches'] and not a['timing_qualified'] and not a['board_acceptance']
for name,digest in {**m['inputs'],**m['artifact_sha256']}.items(): assert sha(p/name)==digest,name
out=ROOT/'results/checkpoint_edit_route_recovery_20261030.json'
freeze=ROOT/'results/checkpoint_edit_route_recovery_sources_20261030'
assert not out.exists() and not freeze.exists()
out.write_text(json.dumps(dict(status='full_system_route_recovery_artifacts_restored',audit=a,restoration=r,
    reference=m['reference'],failed_attempt=m['failed_attempt'],scope=m['scope'],
    timing_qualified=False,board_acceptance=False,full_behavior_matrix_complete=False),indent=2,sort_keys=True)+'\n')
freeze.mkdir(); files={}
def copy(source,relative):
    dest=freeze/relative; dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,dest); files[str(relative)]=dict(source=str(source),sha256=sha(dest))
    assert sha(source)==files[str(relative)]['sha256']
for name in m['inputs']:
    if not name.endswith('.dcp'): copy(p/name,Path(name))
for name in m['artifact_sha256']:
    if not name.endswith('.dcp'): copy(p/name,Path('artifacts')/name)
for name in ['manifest.json','source_bound_audit.json','run.tcl','inspect.tcl','runner.py']:
    copy(p/name,Path('experiment')/name)
for source in [out,rp]: copy(source,Path('reports')/source.name)
for name in ['prepare_state_route_recovery_v1.py','run_state_route_recovery_v1.py','audit_state_route_recovery_v1.py',
             'freeze_state_route_recovery_v1.py','audit_state_ooc_physical_v2.py','parse_state_timing_paths.py',
             'archive_offer_result.py','verify_search_retire_restore.py']:
    copy(ROOT/'scripts'/name,Path('scripts')/name)
(freeze/'manifest.json').write_text(json.dumps(dict(status='frozen',files=files,timing_qualified=False,
    board_acceptance=False,checkpoints='Copied synthesized/placed inputs and routed checkpoint are in the actual-restored verified archive, SHA-bound by the audit.'),indent=2,sort_keys=True)+'\n')
print('STATE_ROUTE_RECOVERY_FROZEN',len(files))
