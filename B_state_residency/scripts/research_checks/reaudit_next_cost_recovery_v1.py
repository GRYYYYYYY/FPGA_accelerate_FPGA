"""Restore immutable CPU evidence and re-audit without Python cache writes."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[2]


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main():
    r = json.loads((ROOT / 'results/new_host_next_cost_reconstruction_review_20261102.json').read_text())
    old = Path(r['actual_restore'])
    changed = {n: {'expected': h, 'actual': sha(old / n)}
               for n, h in r['file_sha256'].items() if sha(old / n) != h}
    assert changed and all('/__pycache__/' in n and n.endswith('.pyc') for n in changed)
    fail = ROOT / 'results/new_host_next_cost_restore_cache_difference_20261102.json'
    assert not fail.exists()
    fail.write_text(json.dumps({'status': 'first_reaudit_passed_but_cache_byte_identity_failed',
                               'changed_files': changed, 'first_restore': str(old),
                               'all_other_files_unchanged': True}, indent=2) + '\n')
    dest = Path('/tmp/B_state_residency_recovery_reaudit_no_bytecode_20261102')
    assert not dest.exists()
    archive = Path(r['archive'])
    assert sha(archive) == r['archive_sha256']
    dest.mkdir()
    with tarfile.open(archive) as tf:
        seen = set()
        for item in tf:
            rel = Path(item.name)
            assert not rel.is_absolute() and '..' not in rel.parts
            assert item.isfile() and item.name in r['file_sha256'] and item.name not in seen
            seen.add(item.name)
            p = dest / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            with tf.extractfile(item) as inp, p.open('xb') as out:
                for block in iter(lambda: inp.read(1 << 20), b''):
                    out.write(block)
            assert sha(p) == r['file_sha256'][item.name]
        assert seen == set(r['file_sha256'])
    auditor = ROOT / 'scripts/audit_followup_cost.py'
    assert sha(auditor) == r['file_sha256']['recovery_tools/audit_followup_cost.py']
    argv = [sys.executable, '-B', str(auditor), str(dest / 'followup_iter2_next_cost_v1')]
    log = dest / 'reaudit.stdout.log'
    with log.open('w') as stream:
        result = subprocess.run(argv, stdout=stream, stderr=subprocess.STDOUT)
    assert result.returncode == 0, log
    for n, h in r['file_sha256'].items():
        assert sha(dest / n) == h, n
    report = {'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'status': 'actual_restored_CPU_reaudit_passed_byte_identical',
              'script_sha256': sha(Path(__file__)), 'actual_restore': str(dest),
              'verified_files': len(r['file_sha256']), 'archive_sha256': r['archive_sha256'],
              'reaudit_command': argv, 'reaudit_exit_code': result.returncode,
              'reaudit_stdout_sha256': sha(log), 'cost_packets': 302,
              'all_original_probe_external_readonly_scratch_paths_now_resolvable': True,
              'prior_cache_difference_report': str(fail),
              'full_system_functional_netlist_validated': False, 'physical_gate_open': False,
              'old_host_backend_status': 'unknown; user confirms old Codex stopped only',
              'new_RTL_started': False}
    output = ROOT / 'results/new_host_next_cost_restore_reaudit_20261102.json'
    assert not output.exists()
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
