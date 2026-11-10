"""Preserve the first actual fixture-control failure without rewriting its receipt."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import sys
import tarfile
ROOT = Path(__file__).resolve().parents[2]
BASE = Path('/tmp/B_state_residency_recovery_20261102')
RUN = BASE / 'shadow_fixture_ready_controls_v2'
sys.path.insert(0, str(ROOT / 'scripts/research_checks'))
from check_shadow_fixture_ready_control_logs_v1 import parse


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    m = json.loads((RUN / 'manifest.json').read_text())
    assert m['status'] == 'failed' and m['stage'] == 'ka_ready_x_simulate' and not m.get('active_process')
    stat = Path('/proc') / str(m['runner_pid']) / 'stat'
    if stat.exists():
        assert stat.read_text().rsplit(')', 1)[1].split()[19] != str(m['runner_start_ticks'])
    checked = {}
    for n, c in m['cases'].items():
        for command in c['commands']:
            assert command['exit_code'] == 0
            assert sha(RUN / n / (command['stage'] + '.stdout.log')) == command['stdout_sha256']
        for name, digest in c['inputs'].items():
            assert sha(RUN / n / name) == digest
        if c['status'] == 'observed':
            checked[n] = parse((RUN / n / 'simulate.stdout.log').read_text(), n,
                               None if n in ['matching', 'ready_nba'] else c['expected'])
    assert len(checked) == 35 and len(m['cases']) == 36
    log = (RUN / 'ka_ready_x/simulate.stdout.log').read_text()
    fatal = [l for l in log.splitlines() if l.startswith('Fatal:')]
    assert fatal == ['Fatal: KA_FIXTURE_READY_INVARIANT phase=0 time=346000']
    assert 'FULL_SHADOW_FIXTURE_READY_CANDIDATE_PASS' not in log
    source = (RUN / 'ka_ready_x/control.sv').read_text()
    assert source.count("wire ka_ready=(counter>=12)?1'bx:cp_m_ready;") == 2
    files = {RUN.name + '/' + p.relative_to(RUN).as_posix(): p for p in RUN.rglob('*') if p.is_file()}
    for p in [Path(__file__).resolve(), ROOT / 'scripts/run_shadow_fixture_ready_controls_v2.py',
              ROOT / 'scripts/audit_shadow_fixture_ready_controls_v2.py',
              ROOT / 'scripts/shadow_fixture_ready_recovery_v2.py',
              ROOT / 'scripts/research_checks/check_shadow_fixture_ready_control_logs_v1.py',
              ROOT / 'results/shadow_fixture_ready_controls_v2_preparation_20261102.json']:
        files['repo/' + p.relative_to(ROOT).as_posix()] = p
    hashes = {n: sha(p) for n, p in files.items()}
    archive = ROOT / 'results/recovery_archives_20261102/shadow_fixture_ready_controls_v2_failed.tar.gz'
    restored = BASE / 'shadow_fixture_ready_controls_v2_failed_restore'
    assert not archive.exists() and not restored.exists()
    with tarfile.open(archive, 'w:gz', compresslevel=3) as tf:
        for n, p in sorted(files.items()):
            assert not p.is_symlink()
            tf.add(p, arcname=n, recursive=False)
    restored.mkdir()
    seen = set()
    with tarfile.open(archive) as tf:
        for item in tf:
            n = Path(item.name)
            assert item.isfile() and not n.is_absolute() and '..' not in n.parts
            assert item.name in hashes and item.name not in seen
            seen.add(item.name)
            p = restored / n
            p.parent.mkdir(parents=True, exist_ok=True)
            with tf.extractfile(item) as inp, p.open('xb') as out:
                shutil.copyfileobj(inp, out, 1 << 20)
            assert sha(p) == hashes[item.name]
    assert seen == set(hashes) and {n: sha(p) for n, p in files.items()} == hashes
    report = {'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'status': 'fixture_ready_x_preinjection_stall_failure_preserved',
              'run_status': 'failed', 'completed_cases_independently_checked': checked,
              'first_fatal': fatal[0],
              'cause': 'KA_READY_X uses cp_m_ready before counter12. In this fixture the first active KA precedes that threshold and sees ready0, so the ready1 invariant stops simulation before the intended X injection.',
              'next_change': 'In an isolated new control source only, replace the two KA_READY_X preinjection ready expressions with constant1. Keep shadow.sv and all58 expected outcomes unchanged and rerun58.',
              'archive': str(archive), 'archive_sha256': sha(archive),
              'actual_restore': str(restored), 'file_sha256': hashes,
              'full_system_functional_netlist_validated': False, 'physical_gate_open': False}
    out = ROOT / 'results/shadow_fixture_ready_controls_v2_failure_review_20261102.json'
    assert not out.exists()
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'completed': 35, 'archive_sha256': report['archive_sha256']}))


if __name__ == '__main__':
    main()
