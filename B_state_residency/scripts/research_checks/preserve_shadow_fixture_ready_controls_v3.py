"""Archive actual terminal controls, restore every byte, and rerun the independent auditor."""
from pathlib import Path
import ast
import datetime
import hashlib
import json
import shutil
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[2]
BASE = Path('/tmp/B_state_residency_recovery_20261102')
RUN = BASE / 'shadow_fixture_ready_controls_v3'


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    m = json.loads((RUN / 'manifest.json').read_text())
    assert m['status'] == 'observed' and m['stage'] == 'complete' and not m.get('active_process')
    stat = Path('/proc') / str(m['runner_pid']) / 'stat'
    if stat.exists():
        assert stat.read_text().rsplit(')', 1)[1].split()[19] != str(m['runner_start_ticks'])
    audit_path = RUN / 'source_bound_audit.json'
    audit = json.loads(audit_path.read_text())
    assert audit['status'] == 'actual58_candidate_controls_independently_audited'
    assert len(audit['outcomes']) == 58 and audit['manifest_sha256'] == sha(RUN / 'manifest.json')
    assert sum(x['verdict'] == 'match' for x in audit['outcomes'].values()) == 2
    prep = ROOT / 'results/shadow_fixture_ready_controls_v3_preparation_20261102.json'
    pr = json.loads(prep.read_text())
    evidence = [ROOT / n for n in pr['file_sha256']]
    for n, h in pr['file_sha256'].items():
        assert sha(ROOT / n) == h
    evidence += [prep, Path(__file__).resolve(),
                 ROOT / 'results/ka_publication_release_full_rtl_v5_counterexample_review_20261102.json']
    # Preserve the local Python import closure, without copying environments or credentials.
    seen = set()
    queue = [p for p in evidence if p.suffix == '.py']
    while queue:
        p = queue.pop()
        if p in seen:
            continue
        seen.add(p)
        for node in ast.walk(ast.parse(p.read_text())):
            modules = ([node.module] if isinstance(node, ast.ImportFrom) else
                       [x.name for x in node.names] if isinstance(node, ast.Import) else [])
            for module in modules:
                if not module:
                    continue
                for folder in [ROOT / 'scripts', ROOT / 'scripts/research_checks']:
                    dep = folder / (module.replace('.', '/') + '.py')
                    if dep.is_file() and dep not in seen:
                        queue.append(dep)
    evidence += list(seen)
    files = {RUN.name + '/' + p.relative_to(RUN).as_posix(): p
             for p in RUN.rglob('*') if p.is_file()}
    files.update({'repo/' + p.relative_to(ROOT).as_posix(): p for p in evidence})
    assert all(not p.is_symlink() for p in files.values())
    hashes = {n: sha(p) for n, p in files.items()}
    archive = ROOT / 'results/recovery_archives_20261102/shadow_fixture_ready_controls_v3.tar.gz'
    partial = archive.with_suffix(archive.suffix + '.partial')
    restored = BASE / 'shadow_fixture_ready_controls_v3_actual_restore'
    assert not archive.exists() and not partial.exists() and not restored.exists()
    with tarfile.open(partial, 'w:gz', compresslevel=3) as tf:
        for name, p in sorted(files.items()):
            tf.add(p, arcname=name, recursive=False)
    restored.mkdir()
    names = set()
    with tarfile.open(partial) as tf:
        for item in tf:
            rel = Path(item.name)
            assert item.isfile() and not rel.is_absolute() and '..' not in rel.parts
            assert item.name in hashes and item.name not in names
            names.add(item.name)
            dst = restored / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            with tf.extractfile(item) as src, dst.open('xb') as out:
                shutil.copyfileobj(src, out, 1 << 20)
            assert sha(dst) == hashes[item.name]
    assert names == set(hashes)
    # The auditor writes an immutable new report. Move only the restored report
    # aside and require its newly generated replacement to be byte identical.
    restored_run = restored / RUN.name
    saved_audit = restored / 'original_source_bound_audit.json'
    (restored_run / 'source_bound_audit.json').rename(saved_audit)
    auditor = ROOT / 'scripts/audit_shadow_fixture_ready_controls_v3.py'
    assert sha(auditor) == audit['auditor_sha256']
    command = [sys.executable, '-B', str(auditor), str(restored_run)]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    (restored / 'reaudit.stdout.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, result.stdout + result.stderr
    assert sha(saved_audit) == sha(restored_run / 'source_bound_audit.json') == sha(audit_path)
    assert {n: sha(restored / n) for n in hashes} == hashes
    assert {n: sha(p) for n, p in files.items()} == hashes
    partial.rename(archive)
    report = {
        'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'actual58_fixture_ready_controls_audited_restored_and_reaudited',
        'positive_cases': 2, 'expected_rejection_cases': 56,
        'audit': audit, 'archive': str(archive), 'archive_sha256': sha(archive),
        'archive_bytes': archive.stat().st_size, 'actual_restore': str(restored),
        'reaudit_command': command, 'reaudit_exit_code': result.returncode,
        'restored_audit_byte_identical': True, 'all_restored_files_byte_identical': True,
        'file_sha256': hashes, 'memory_admission': m['memory_admission'],
        'scope': 'Bounded fake-model checker controls only. No new real full-system shadow, physical timing, or production RTL repair.',
        'full_system_functional_netlist_validated': False, 'physical_gate_open': False,
    }
    out = ROOT / 'results/shadow_fixture_ready_controls_v3_review_20261102.json'
    assert not out.exists()
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['status', 'positive_cases', 'expected_rejection_cases', 'archive_bytes', 'archive_sha256']}))


if __name__ == '__main__':
    main()
