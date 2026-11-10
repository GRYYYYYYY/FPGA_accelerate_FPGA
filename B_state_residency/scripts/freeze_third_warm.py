"""Freeze the G3 warm extension after selected and legacy archive restore audits."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    report_path = ROOT/'results/third_warm_20261027.json'
    report = json.loads(report_path.read_text())
    assert report['status'] == 'passed'
    for name, receipt in report['restores'].items():
        assert receipt['status'] == 'passed' and receipt['audit_byte_identical'], name
        p = Path(receipt['restored_root'])/'source_bound_audit.json'
        assert sha(p) == receipt['audit_sha256'], name
        assert json.loads(p.read_text()) == report['cases'][name]
    old = json.loads((ROOT/'results/path_capacity_sources_20261027/manifest.json').read_text())
    files = set(old['sources'])
    for name, digest in old['sources'].items():
        assert sha(ROOT/name) == digest, name
    for directory in ['third_warm_v1', 'third_warm_v2']:
        files.update(str(p.relative_to(ROOT)) for p in (ROOT/'hardware/variants'/directory).iterdir()
                     if p.is_file() and p.suffix in ['.py', '.sv', '.md'])
    files.update('scripts/'+name for name in ['run_third_warm_system.py', 'audit_third_warm_system.py',
        'audit_third_warm_records.py', 'audit_third_warm_observer_legacy.py', 'audit_third_warm_observer_stable.py',
        'analyze_third_warm_phases.py', 'freeze_third_warm.py'])
    out = ROOT/'results/third_warm_sources_20261027'
    assert not out.exists()
    out.mkdir()
    sources = {}
    for name in sorted(files):
        dest = out/name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/name, dest)
        assert sha(dest) == sha(ROOT/name)
        sources[name] = sha(dest)
    (out/'manifest.json').write_text(json.dumps(dict(status='frozen', sources=sources,
        inherited='path_capacity_sources_20261027', report_sha256=sha(report_path),
        scope='G3 warm extension and inherited source closure. Prior archived graphs, source captures and runtime dependencies remain required; not a standalone simulator distribution.'), indent=2)+'\n')
    print('FROZEN', len(sources))


if __name__ == '__main__':
    main()
