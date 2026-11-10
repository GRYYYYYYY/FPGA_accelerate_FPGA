"""Restore six copied immutable KA review archives and check original report inventories."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
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
    copied = ROOT / 'results/old_host_ka_review_archive_copy_20261102.json'
    c = json.loads(copied.read_text())
    assert len(c['archives']) == 6 and c['temporary_inspection_terminal_closed']
    destination = BASE / 'ka_review_archives_actual_restore_v1'
    assert not destination.exists()
    destination.mkdir()
    rows = {}
    for row in c['archives']:
        archive, report = Path(row['archive']), Path(row['report'])
        r = json.loads(report.read_text())
        assert sha(report) == row['report_sha256']
        assert sha(archive) == row['archive_sha256'] == r['archive_sha256']
        d = destination / archive.stem
        d.mkdir()
        hashes = r['file_sha256']
        seen = set()
        with tarfile.open(archive) as tf:
            for item in tf:
                name = Path(item.name)
                assert item.isfile() and not name.is_absolute() and '..' not in name.parts
                assert item.name in hashes and item.name not in seen
                seen.add(item.name)
                p = d / name
                p.parent.mkdir(parents=True, exist_ok=True)
                with tf.extractfile(item) as inp, p.open('xb') as out:
                    shutil.copyfileobj(inp, out, 1 << 20)
                assert sha(p) == hashes[item.name]
        assert seen == set(hashes)
        rows[archive.stem] = dict(archive_sha256=sha(archive), files=len(hashes),
                                  report_sha256=sha(report), actual_restore=str(d))
    component = destination / 'ka_as_component_parameters_evidence_v1'
    reference = BASE / 'stage_static_cp_host_full_static_v1/sources'
    matched = {}
    for n in ['query_residency_system.sv', 'residency_system.sv',
              'recovery_coordinator.sv', 'checkpoint_authority_rotator.sv']:
        assert sha(component / 'sources' / n) == sha(reference / n)
        matched[n] = sha(reference / n)
    proof = json.loads((ROOT / 'results/ka_as_ready_temporal_composition_review_20261101.json').read_text())
    for name, digest in proof['dependency_report_sha256'].items():
        assert sha(ROOT / 'results' / name) == digest
    result = {'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'status': 'six_original_KA_review_archives_persisted_and_restored',
              'copy_receipt_sha256': sha(copied), 'archives': rows,
              'matched_full_RTL_sources': matched, 'dependency_reports_matched': 8,
              'scope': 'Original archive bytes and exact six review inventories recovered; four current production source bindings and eight dependency report hashes rechecked. No solver rerun or claim that every lower-level proof artifact is recovered. Full-shadow launch gate still requires its complete dependency review.',
              'full_system_functional_netlist_validated': False, 'physical_gate_open': False}
    out = ROOT / 'results/ka_review_archives_new_host_restore_20261102.json'
    assert not out.exists()
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'files': sum(x['files'] for x in rows.values()), 'source_bindings': len(matched)}))


if __name__ == '__main__':
    main()
