"""Recover selected immutable inputs; never resume a process or rewrite old receipts."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import socket
import tarfile

ROOT = Path(__file__).resolve().parents[2]
ARCHIVES = ROOT / 'results/offer_archives_20261025'
DEST = Path('/tmp/B_state_residency_recovery_20261102')
OLD = Path('/tmp/B_state_residency_offer_20261025')


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def recover(name, selected):
    index = ARCHIVES / (name + '.json')
    record = json.loads(index.read_text())
    archive = ARCHIVES / (name + '.tar.gz')
    assert record['status'] == 'passed'
    assert sha(archive) == record['archive_sha256']
    expected = {n: record['members'][n] for n in selected}
    target = DEST / name
    target.mkdir(parents=True, exist_ok=True)
    seen = set()
    with tarfile.open(archive, 'r:gz') as tf:
        for item in tf:
            rel = Path(item.name).relative_to(name)
            assert not rel.is_absolute() and '..' not in rel.parts
            key = rel.as_posix()
            if key not in expected:
                continue
            assert item.isfile() and key not in seen
            seen.add(key)
            output = target / rel
            if output.exists():
                assert sha(output) == expected[key], output
                continue
            output.parent.mkdir(parents=True, exist_ok=True)
            partial = output.with_name(output.name + '.recovery-partial')
            with tf.extractfile(item) as inp, partial.open('xb') as out:
                shutil.copyfileobj(inp, out, 1 << 20)
            assert sha(partial) == expected[key], partial
            partial.rename(output)
    assert seen == set(expected)
    for name_, digest in expected.items():
        assert sha(target / name_) == digest
    return {'archive_sha256': record['archive_sha256'],
            'index_sha256': sha(index), 'selected_files': expected,
            'scope': 'Selected members only; all selected bytes verified after extraction.'}


def main():
    reference = DEST / 'stage_static_cp_host_full_static_v1'
    index = ARCHIVES / 'stage_static_cp_host_full_static_v1.json'
    receipt = json.loads(index.read_text())
    assert sha(ARCHIVES / 'stage_static_cp_host_full_static_v1.tar.gz') == receipt['archive_sha256']
    for name, digest in receipt['members'].items():
        assert sha(reference / name) == digest, name
    manifest = json.loads((reference / 'manifest.json').read_text())
    assert sha(reference / 'source_bound_audit.json') == 'f087aaff4c300605867c02d9fadf149b67125ebb6d9e13f6599edc7dbd01c770'
    for name, info in manifest['sources'].items():
        assert sha(reference / 'sources' / name) == info['sha256'], name
    production = [n for n in manifest['rtl'] if n not in
                  ['tb_directory_observer.sv', 'tb_query_fault.sv', 'axi_file_memory.sv']]
    assert len(production) == 133 and len(manifest['rtl']) == 136
    old_prep = json.loads((ROOT / 'results/ka_publication_release_full_rtl_v2_preparation_review_20261101.json').read_text())
    assert manifest['parameters'] == old_prep['parameters']
    binding = Path(manifest['binding'])
    assert sha(binding) == manifest['binding_sha256']
    regions = json.loads(binding.read_text())['regions']
    groups = {}
    for entry in regions.values():
        rel = Path(entry['path']).relative_to(OLD)
        assert len(rel.parts) == 2
        groups.setdefault(rel.parts[0], set()).add(rel.parts[1])
    groups['followup_iter2_cost_v1'].add('cost_vectors.txt')
    groups['label_baseline_image_v1'] = {'baseline.bin', 'manifest.json'}
    for name in ['followup_iter2_third_cost_v1', 'followup_iter2_fourth_cost_v1']:
        groups[name] = {'cost_vectors.txt', 'manifest.json', 'source_bound_audit.json'}
    recovered = {name: recover(name, sorted(files)) for name, files in groups.items()}
    verified_regions = {}
    for key, entry in regions.items():
        output = DEST / Path(entry['path']).relative_to(OLD)
        assert output.stat().st_size == entry['bytes'] and sha(output) == entry['sha256']
        verified_regions[key] = dict(entry, recovered_path=str(output))
    assert sha(DEST / 'label_baseline_image_v1/manifest.json') == manifest['baseline_manifest_sha256']
    for field in ['third_inputs', 'fourth_inputs']:
        for old_path, digest in manifest[field].items():
            name = Path(old_path).name
            if name in recovered:
                assert sha(DEST / name / 'source_bound_audit.json') == digest
    # Keep unresolved input paths explicit; do not fabricate a replacement oracle.
    missing_external = []
    for token in manifest['cases']['full']['commands'][-1]['argv']:
        if '=' not in token:
            continue
        key, value = token.split('=', 1)
        path = Path(value)
        if not path.is_absolute() or not path.is_relative_to(OLD):
            continue
        rel = path.relative_to(OLD)
        if rel.parts[0] == reference.name:
            continue  # Local runtime files will be created by the future runner.
        if not (DEST / rel).is_file():
            missing_external.append({'argument': key, 'original_path': value})
    report = {'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'host': socket.gethostname(), 'status': 'reference_and_selected_original_inputs_verified',
              'script_sha256': sha(Path(__file__)), 'reference_files_verified': len(receipt['members']),
              'reference_archive_sha256': receipt['archive_sha256'],
              'reference_sources_verified': len(manifest['sources']),
              'production_count': len(production), 'compile_file_count': len(manifest['rtl']),
              'parameters': manifest['parameters'], 'binding_sha256': sha(binding),
              'recovered_archives': recovered, 'verified_regions': verified_regions,
              'missing_external_inputs': missing_external,
              'old_host_process_status': 'unknown; user reports old Codex stopped, backend processes uncertain',
              'new_simulation_started': False, 'full_system_functional_netlist_validated': False,
              'physical_gate_open': False}
    out = ROOT / 'results/new_host_probe_input_recovery_20261102.json'
    assert not out.exists(), out
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'report': str(out), 'reference_files_verified': report['reference_files_verified'],
                      'input_regions_verified': len(verified_regions), 'missing_external_inputs': missing_external}))


if __name__ == '__main__':
    main()
