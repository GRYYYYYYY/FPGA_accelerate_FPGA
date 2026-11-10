"""Preserve a terminated new-host probe and actually restore all archived bytes."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[2]
BASE = Path('/tmp/B_state_residency_recovery_20261102')


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    run = Path(sys.argv[1]).resolve()
    assert run.parent == BASE
    m = json.loads((run / 'manifest.json').read_text())
    assert m['status'] in ['failed', 'reproduction_observed'] and 'active_process' not in m
    stat = Path('/proc') / str(m['runner_pid']) / 'stat'
    if stat.exists():
        fields = stat.read_text().rsplit(')', 1)[1].split()
        assert fields[19] != m['runner_start_ticks'] or fields[0] == 'Z'
    files = {run.name + '/' + p.relative_to(run).as_posix(): p for p in run.rglob('*') if p.is_file()}
    for name in ['run_' + run.name.replace('ka_', '', 1) + '.py',
                 'audit_' + run.name.replace('ka_', '', 1) + '.py', 'check_publication_release_full_probe_v1.py']:
        p = ROOT / 'scripts/research_checks' / name
        assert p.is_file(), p
        files['tools/' + p.name] = p
    files['tools/' + Path(__file__).name] = Path(__file__).resolve()
    hashes = {n: sha(p) for n, p in files.items()}
    target = ROOT / 'results/recovery_archives_20261102' / (run.name + '_terminal.tar.gz')
    restored = BASE / (run.name + '_terminal_restore')
    partial = target.with_name(target.name + '.partial')
    assert not target.exists() and not partial.exists() and not restored.exists()
    with tarfile.open(partial, 'w:gz', compresslevel=3) as tf:
        for name, p in sorted(files.items()):
            assert not p.is_symlink()
            tf.add(p, arcname=name, recursive=False)
    restored.mkdir()
    seen = set()
    with tarfile.open(partial) as tf:
        for item in tf:
            rel = Path(item.name)
            assert not rel.is_absolute() and '..' not in rel.parts and item.isfile()
            assert item.name in hashes and item.name not in seen
            seen.add(item.name)
            p = restored / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            with tf.extractfile(item) as inp, p.open('xb') as out:
                shutil.copyfileobj(inp, out, 1 << 20)
            assert sha(p) == hashes[item.name]
    assert seen == set(hashes) and {n: sha(p) for n, p in files.items()} == hashes
    partial.rename(target)
    report = {'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'status': 'terminal_bytes_preserved_not_functional_acceptance',
              'run_status': m['status'], 'archive': str(target), 'archive_sha256': sha(target),
              'archive_bytes': target.stat().st_size, 'actual_restore': str(restored),
              'file_sha256': hashes, 'full_system_functional_netlist_validated': False,
              'physical_gate_open': False}
    out = ROOT / 'results' / (run.name + '_terminal_preservation_20261102.json')
    assert not out.exists()
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['run_status', 'archive_sha256', 'archive_bytes']}))


if __name__ == '__main__':
    main()
