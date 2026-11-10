"""Freeze physical observations only after actual archive restoration and identical audit."""
from pathlib import Path
import json
import shutil
import sys
from run_checkpoint_authority import ROOT, sha

p = Path(sys.argv[1]).resolve()
m = json.loads((p/'manifest.json').read_text())
a = json.loads((p/'source_bound_audit.json').read_text())
rp = ROOT/'results'/f'{p.name}_restore_20261025.json'
r = json.loads(rp.read_text())
assert m['status'] == 'observed' and m['exit_code'] == 0
assert a['status'] == r['status'] == 'passed' and r['audit_byte_identical']
assert a['manifest_sha256'] == sha(p/'manifest.json')
assert r['audit_sha256'] == sha(p/'source_bound_audit.json')
assert a['auditor_sha256'] == sha(ROOT/'scripts/audit_state_ooc_physical_v2.py')
assert not a['timing_qualified'] and not a['board_acceptance']
for name, digest in {**m['inputs'], **m['artifact_sha256']}.items():
    assert sha(p/name) == digest, name
name = p.name.removesuffix('_v1')
report = ROOT/'results'/f'{name}_20261029.json'
freeze = ROOT/'results'/f'{name}_sources_20261029'
assert not report.exists() and not freeze.exists()
record = dict(status='full_system_physical_artifacts_restored', reference=m['reference'],
              audit=a, restoration=r, timing_qualified=False, board_acceptance=False,
              full_behavior_matrix_complete=False,
              scope='Audited complete-system OOC implementation reports and actual archive restoration. '
                    'Internal constrained timing is reported separately from unconstrained platform I/O; '
                    'artifact integrity is not board timing, complete behavior coverage, or acceleration proof.')
report.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
freeze.mkdir()
files = {}


def copy(source, relative):
    dest = freeze/relative
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,dest)
    files[str(relative)] = dict(source=str(source),sha256=sha(dest))
    assert sha(source) == files[str(relative)]['sha256']


for relative in m['inputs']:
    if not relative.endswith('.dcp'):
        copy(p/relative,Path(relative))
for relative in m['artifact_sha256']:
    if not relative.endswith('.dcp'):
        copy(p/relative,Path('artifacts')/relative)
for relative in ['manifest.json','source_bound_audit.json','run.tcl','runner.py']:
    copy(p/relative,Path('experiment')/relative)
for source in [rp,report]:
    copy(source,Path('reports')/source.name)
for relative in ['run_state_ooc_physical.py','audit_state_ooc_physical_v2.py',
                 'freeze_state_ooc_physical_v2.py','archive_offer_result.py','verify_search_retire_restore.py']:
    copy(ROOT/'scripts'/relative,Path('scripts')/relative)
(freeze/'manifest.json').write_text(json.dumps(dict(status='frozen',files=files,
    checkpoints='All input/optimized/placed/routed DCPs are retained in the verified archive and restored experiment; their SHA values are in the audit.',
    timing_qualified=False,board_acceptance=False),indent=2,sort_keys=True)+'\n')
print('STATE_FULL_PHYSICAL_FROZEN',p.name,len(files),'files')
