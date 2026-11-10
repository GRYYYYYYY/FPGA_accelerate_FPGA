"""Freeze the G3 publication extension after audited archive restoration."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    report = json.loads((ROOT / 'results/owner_g3_publish_20261027.json').read_text())
    assert report['status'] == 'passed'
    for name, receipt in report['restores'].items():
        assert receipt['status'] == 'passed' and receipt['audit_byte_identical'], name
        assert sha(Path(receipt['restored_root']) / 'source_bound_audit.json') == receipt['audit_sha256']
    previous = json.loads((ROOT / 'results/cumulative_owner_system_sources_20261027/manifest.json').read_text())
    files = set(previous['sources'])
    for name, digest in previous['sources'].items():
        assert sha(ROOT / name) == digest, name
    for directory in ['owner_g3_publish_v1', 'owner_g3_publish_v2']:
        files.update(str(p.relative_to(ROOT)) for p in (ROOT / 'hardware/variants' / directory).iterdir()
                     if p.is_file() and p.suffix in ('.sv', '.py', '.md'))
    files.update('scripts/' + name for name in [
        'run_export_manifest_unit.py', 'audit_export_manifest_unit.py',
        'run_owner_receipt_busy_unit.py', 'audit_owner_receipt_busy_unit.py',
        'run_owner_receipt_retire_unit.py', 'audit_owner_receipt_retire_unit.py',
        'run_owner_g3_publish.py', 'audit_owner_g3_publish.py',
        'audit_owner_g3_receipt_only_failure.py',
        'run_owner_g3_retired_publish.py', 'audit_owner_g3_retired_publish.py',
        'release_experiment_cache.py', 'freeze_owner_g3_publish.py'])
    out = ROOT / 'results/owner_g3_publish_sources_20261027'
    assert not out.exists()
    out.mkdir()
    sources = {}
    for name in sorted(files):
        dest = out / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, dest)
        assert sha(dest) == sha(ROOT / name)
        sources[name] = sha(dest)
    (out / 'manifest.json').write_text(json.dumps(dict(
        status='frozen', sources=sources,
        scope='Inherited cumulative-owner source closure and G3 extension; prior archived dependencies remain required. Not a standalone simulator distribution.'), indent=2) + '\n')
    print('FROZEN', len(sources))


if __name__ == '__main__':
    main()
