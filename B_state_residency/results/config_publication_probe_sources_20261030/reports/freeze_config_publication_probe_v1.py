"""Freeze an actual restored original-RTL observation, never candidate acceptance."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/tmp/B_state_residency_offer_20261025')
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p = BASE / 'config_publication_probe_v1'
    m = json.loads((p / 'manifest.json').read_text())
    a = json.loads((p / 'source_bound_audit.json').read_text())
    receipt = ROOT / 'results/config_publication_probe_v1_restore_20261025.json'
    r = json.loads(receipt.read_text())
    assert m['status'] == 'observed' and m['stage'] == 'complete'
    assert a['status'] == r['status'] == 'passed' and r['audit_byte_identical']
    assert a['manifest_sha256'] == sha(p / 'manifest.json')
    assert a['auditor_sha256'] == sha(ROOT / 'scripts/audit_config_publication_probe_v1.py')
    assert r['audit_sha256'] == sha(p / 'source_bound_audit.json')
    assert r['audit_sha256'] == sha(Path(r['preserved_original']) / 'source_bound_audit.json')
    assert a['events'] == 17 and a['checks'] == 138 and a['x_and_z_publication_observed']
    assert a['abort_discard_attempt_reset_preserve_active']
    out = ROOT / 'results/config_publication_probe_20261030.json'
    freeze = ROOT / 'results/config_publication_probe_sources_20261030'
    assert not out.exists() and not freeze.exists()
    for name, entry in m['bound'].items():
        assert sha(p / 'bound' / name) == entry['sha256'] == sha(entry['source'])
    report = dict(status='original_rtl_publication_counterexamples_restored', audit=a, restoration=r,
        candidate_selected=False, timing_qualified=False, board_acceptance=False,
        scope='Seven focused cases on the original controller, including X/Z propagation and three cancellation mechanisms. Not an unconditional equivalence proof, full-system unknown-input proof or timing improvement.')
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    freeze.mkdir(); files = {}

    def copy(source, relative):
        dest = freeze / relative; dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
        files[str(relative)] = dict(source=str(source), sha256=sha(source))
        assert sha(dest) == files[str(relative)]['sha256']

    for name in m['bound']:
        copy(p / 'bound' / name, Path('bound') / name)
    for name in ['manifest.json', 'source_bound_audit.json', 'events.txt', 'simulate.log',
                 'compile.stdout.log', 'elaborate.stdout.log', 'simulate.stdout.log', 'run.tcl',
                 'config_restore_controller.sv', 'tb_config_publication_probe_v1.sv']:
        copy(p / name, Path('experiment') / name)
    for source in [out, receipt, Path(__file__).resolve()]:
        copy(source, Path('reports') / source.name)
    (freeze / 'manifest.json').write_text(json.dumps(dict(status='frozen', files=files,
        candidate_selected=False, full_system_knownness_proven=False), indent=2, sort_keys=True) + '\n')
    print('CONFIG_PUBLICATION_PROBE_FROZEN', len(files))


if __name__ == '__main__':
    main()
