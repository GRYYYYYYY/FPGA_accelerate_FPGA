"""Persist and actually restore the independently audited CPU recovery evidence."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import tarfile

ROOT = Path(__file__).resolve().parents[2]
RUN = Path('/tmp/B_state_residency_recovery_20261102/followup_iter2_next_cost_v1')
RESTORE = Path('/tmp/B_state_residency_recovery_verified_20261102')


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main():
    m = json.loads((RUN / 'manifest.json').read_text())
    a = json.loads((RUN / 'source_bound_audit.json').read_text())
    assert m['status'] == a['status'] == 'passed'
    assert a['manifest_sha256'] == sha(RUN / 'manifest.json')
    assert a['cost_packets'] == 302
    assert [c['exit_code'] for c in m['commands']] == [0, 0]
    inputs = json.loads((ROOT / 'results/followup_iter2_inputs_20261025.json').read_text())['regions']
    for name, key in [('cost.bin', 'cost_history_prices_nets'), ('connections.bin', 'connections')]:
        assert sha(RUN / name) == inputs[key]['sha256']
    tools = [ROOT / 'scripts/audit_followup_cost.py', Path(__file__).resolve(),
             ROOT / 'scripts/research_checks/recover_probe_inputs_new_host_v2.py']
    assert sha(tools[0]) == a['auditor_sha256']
    files = {}
    for p in RUN.rglob('*'):
        assert not p.is_symlink()
        if p.is_file():
            files[RUN.name + '/' + p.relative_to(RUN).as_posix()] = p
    for p in tools:
        files['recovery_tools/' + p.name] = p
    expected = {n: sha(p) for n, p in files.items()}
    dest = ROOT / 'results/recovery_archives_20261102'
    dest.mkdir(exist_ok=True)
    archive = dest / (RUN.name + '.tar.gz')
    partial = archive.with_name(archive.name + '.partial')
    assert not archive.exists() and not partial.exists() and not RESTORE.exists()
    with tarfile.open(partial, 'w:gz', compresslevel=3) as tf:
        for name, path in sorted(files.items()):
            tf.add(path, arcname=name, recursive=False)
    RESTORE.mkdir()
    with tarfile.open(partial, 'r:gz') as tf:
        seen = set()
        for item in tf:
            rel = Path(item.name)
            assert not rel.is_absolute() and '..' not in rel.parts
            assert item.isfile() and item.name in expected and item.name not in seen
            seen.add(item.name)
            p = RESTORE / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            with tf.extractfile(item) as inp, p.open('xb') as out:
                shutil.copyfileobj(inp, out, 1 << 20)
            assert sha(p) == expected[item.name], item.name
        assert seen == set(expected)
    # Detect changes to the source during archival as well as extraction errors.
    assert {n: sha(p) for n, p in files.items()} == expected
    partial.rename(archive)
    report = {'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'status': 'CPU_cost_reference_reconstructed_audited_and_actually_restored',
              'run': str(RUN), 'archive': str(archive), 'archive_sha256': sha(archive),
              'archive_bytes': archive.stat().st_size, 'actual_restore': str(RESTORE),
              'file_sha256': expected, 'cost_packets': a['cost_packets'],
              'cost_input_words': a['cost_input_words'], 'cost_result_words': a['cost_result_words'],
              'reference_files_compared': m['compared'], 'commands': m['commands'],
              'scope': 'New CPU reference reconstruction from archived prepared state; nine original search-state/event files match and costs independently audited. Historical missing cost-vector file SHA is unavailable; not claimed byte-identical to that missing file. No full RTL or formal job resumed.',
              'old_host_backend_processes': 'unconfirmed', 'full_system_functional_netlist_validated': False,
              'physical_gate_open': False}
    output = ROOT / 'results/new_host_next_cost_reconstruction_review_20261102.json'
    assert not output.exists()
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['status', 'archive_sha256', 'archive_bytes', 'cost_packets']}))


if __name__ == '__main__':
    main()
