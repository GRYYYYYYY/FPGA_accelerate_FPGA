"""Freeze diagnosed runtime controls after actual restore and identical independent audit."""
from pathlib import Path
import json
import shutil
from run_checkpoint_authority import ROOT, sha

p=Path('/tmp/B_state_residency_offer_20261025/udev_route_probe_v2')
a=json.loads((p/'source_bound_audit.json').read_text())
rp=ROOT/'results/udev_route_probe_v2_restore_20261025.json'; r=json.loads(rp.read_text())
assert a['status']==r['status']=='passed' and r['audit_byte_identical']
assert r['audit_sha256']==sha(p/'source_bound_audit.json')
assert a['manifest_sha256']==sha(p/'manifest.json')
assert a['auditor_sha256']==sha(ROOT/'scripts/audit_udev_route_probe_v2.py')
for name,digest in a['artifact_sha256'].items(): assert sha(p/name)==digest
for name,digest in a['external_evidence_sha256'].items(): assert sha(Path(name))==digest
out=ROOT/'results/udev_runtime_recovery_20261030.json'; freeze=ROOT/'results/udev_runtime_recovery_sources_20261030'
assert not out.exists() and not freeze.exists()
out.write_text(json.dumps(dict(status='runtime_controls_restored',audit=a,restoration=r,
    interpretation='Allocator/deepbind incompatibility is reproduced in independent real libudev controls. '
    'The baseline tiny Vivado flow aborts in the same libudev/WebTalk stack after routing. '
    'Preloading unchanged libraries lets the tiny flow route, save and reopen its DCP. '
    'This authorizes testing the runtime environment in a new full-system recovery; it does not prove it succeeds.',
    reference='https://man7.org/linux/man-pages/man3/dlopen.3.html',
    timing_qualified=False,board_acceptance=False),indent=2,sort_keys=True)+'\n')
freeze.mkdir(); files={}
def copy(source,relative):
    dest=freeze/relative; dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,dest); files[str(relative)]=dict(source=str(source),sha256=sha(dest))
    assert sha(source)==files[str(relative)]['sha256']
for name in a['artifact_sha256']:
    if not name.endswith('.dcp'): copy(p/name,Path('experiment')/name)
for name in a['external_evidence_sha256']:
    source=Path(name); copy(source,Path('controls')/source.relative_to(p.parent))
copy(p/'source_bound_audit.json',Path('experiment/source_bound_audit.json'))
for source in [out,rp]: copy(source,Path('reports')/source.name)
for name in ['audit_udev_route_probe_v2.py','freeze_udev_route_probe_v2.py','archive_offer_result.py','verify_search_retire_restore.py',
             'run_udev_route_probe_v1.py','audit_udev_route_probe_v1.py']:
    copy(ROOT/'scripts'/name,Path('scripts')/name)
copy(ROOT/'results/udev_route_probe_harness_failure_20261030.json',Path('reports/udev_route_probe_harness_failure_20261030.json'))
(freeze/'manifest.json').write_text(json.dumps(dict(status='frozen',files=files,
    checkpoints='DCPs remain in the verified archive and restored runtime probe, source-bound by the audit.'),indent=2,sort_keys=True)+'\n')
print('UDEV_RUNTIME_CONTROLS_FROZEN',len(files))
