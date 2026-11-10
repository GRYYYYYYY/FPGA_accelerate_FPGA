"""New-host predecessor binding and conservative admission for the unchanged controls."""
from pathlib import Path
import os
import socket
import time
from host_edit_system_common_v1 import ROOT, read, sha, identity

BASE = Path('/tmp/B_state_residency_recovery_20261102')
PRIOR = BASE / 'ka_publication_release_full_rtl_v5'
REVIEW = ROOT / 'results/ka_publication_release_full_rtl_v5_counterexample_review_20261102.json'
ARCHIVE = ROOT / 'results/recovery_archives_20261102/ka_publication_release_full_rtl_v5_terminal.tar.gz'


def predecessor():
    m, r = read(PRIOR / 'manifest.json'), read(REVIEW)
    assert m['status'] == 'failed' and not m.get('active_process')
    assert m['hostname'] == socket.gethostname()
    assert m['boot_id'] == Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    assert m['pid_namespace'] == os.readlink('/proc/self/ns/pid')
    assert identity(m['runner_pid']) != str(m['runner_start_ticks'])
    assert r['status'] == 'initialized_full_RTL_overlap_counterexample_audited'
    assert r['run_status_preserved'] == 'failed'
    for name, digest in r['evidence_sha256'].items():
        assert sha(PRIOR / name) == digest, name
    assert sha(ARCHIVE) == r['terminal_archive_sha256']
    assert not r['full_system_functional_netlist_validated'] and not r['physical_gate_open']
    return {'run_root': str(PRIOR), 'manifest_sha256': sha(PRIOR / 'manifest.json'),
            'review_sha256': sha(REVIEW), 'archive_sha256': sha(ARCHIVE),
            'status': 'failed', 'meaning': 'terminal counterexample; not functional acceptance'}


def memory_admission(record, save):
    stable = None
    deadline = time.monotonic() + 10800
    record['memory_policy'] = {'absolute_max_gib': 225, 'max_fraction': '3/4',
                               'stable_seconds': 60, 'poll_seconds': 10}
    samples = record.setdefault('memory_samples', [])
    while True:
        now = time.monotonic()
        cg = Path('/sys/fs/cgroup')
        current = int((cg / 'memory.current').read_text())
        limit = int((cg / 'memory.max').read_text())
        eligible = current <= min(225 * 2**30, limit * 3 // 4)
        stable = (now if stable is None else stable) if eligible else None
        seconds = 0 if stable is None else now - stable
        sample = dict(current_bytes=current, limit_bytes=limit,
                      stable_seconds=seconds, monotonic_seconds=now)
        samples.append(sample)
        record['memory_admission'] = sample
        save()
        if seconds >= 60:
            return
        assert now < deadline, 'Memory observation expired before starting controls'
        time.sleep(10)
