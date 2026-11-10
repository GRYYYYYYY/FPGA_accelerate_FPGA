"""Freeze audited path-capacity, q3 inputs and complete-system continuity sources."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    reports = ['path_capacity_20261027', 'iter2_third_cost_20261027',
               'path_capacity_third_20261027']
    for name in reports:
        report = json.loads((ROOT / 'results' / (name + '.json')).read_text())
        assert report['status'] == 'passed'
        for case, receipt in report['restores'].items():
            assert receipt['status'] == 'passed' and receipt['audit_byte_identical'], case
            source = Path(receipt['restored_root']) / 'source_bound_audit.json'
            assert sha(source) == receipt['audit_sha256'], case
            assert json.loads(source.read_text()) == report['cases'][case], case
    inherited = ['owner_g3_publish_sources_20261027', 'iter2_third_sources_20261027']
    files = set()
    for name in inherited:
        old = json.loads((ROOT / 'results' / name / 'manifest.json').read_text())
        for relative, digest in old['sources'].items():
            assert sha(ROOT / relative) == digest, relative
        files.update(old['sources'])
    directory = ROOT / 'hardware/variants/path_capacity_v1'
    files.update(str(p.relative_to(ROOT)) for p in directory.iterdir()
                 if p.is_file() and p.suffix in ('.sv', '.py', '.md'))
    files.update('scripts/' + name for name in [
        'run_path_capacity_system.py', 'run_path_capacity_unit.py',
        'audit_path_capacity.py', 'run_path_capacity_third_system.py',
        'audit_path_capacity_third.py', 'audit_path_native_records.py',
        'prepare_followup_cost.py', 'audit_followup_cost.py',
        'verify_followup_filters.py', 'audit_followup_filters_replay.py',
        'archive_offer_result.py', 'restore_offer_result.py',
        'verify_search_retire_restore.py', 'freeze_path_capacity.py'])
    files.update(['adapters/followup_cost_v1/export_inputs.hpp',
                  'adapters/natural_query_v1/make_replay.py',
                  'adapters/natural_query_v1/derive_cost_inputs.py'])
    out = ROOT / 'results/path_capacity_sources_20261027'
    assert not out.exists()
    out.mkdir()
    sources = {}
    for relative in sorted(files):
        dest = out / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, dest)
        assert sha(dest) == sha(ROOT / relative)
        sources[relative] = sha(dest)
    (out / 'manifest.json').write_text(json.dumps(dict(
        status='frozen', sources=sources, inherited=inherited,
        reports={name: sha(ROOT / 'results' / (name + '.json')) for name in reports},
        scope='Source closure for path capacity and normal q3 continuity. Prior archived graphs, CPU captures and source dependencies remain required; not a standalone simulator distribution.'), indent=2) + '\n')
    print('FROZEN', len(sources))


if __name__ == '__main__':
    main()
