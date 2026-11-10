"""Shared source and predecessor checks for the separate real host-edit runs."""
from pathlib import Path
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/tmp/B_state_residency_offer_20261025')
REFERENCE = BASE / 'checkpoint_edit_system_crc_pressure_v1'
TARGETS = {'baseline': BASE / 'query_host_edit_system_v1',
           'cp': BASE / 'checkpoint_host_edit_system_v1'}
VARIANT = ROOT / 'hardware/variants/checkpoint_host_edit_system_v1'
CHANGED = {'query_lifecycle.sv', 'query_residency_system.sv'}
TOOLS = ['host_edit_system_common_v1.py', 'run_host_edit_system_v1.py',
         'audit_host_edit_system_v1.py', 'freeze_host_edit_system_v1.py',
         'check_host_edit_trace_v1.py', 'archive_offer_result.py',
         'verify_search_retire_restore.py', 'restore_offer_result.py',
         'run_config_native_feedback_probe_v1.py']


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1048576), b''):
            h.update(chunk)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def identity(pid):
    try:
        return Path('/proc', str(pid), 'stat').read_text().split(') ', 1)[1].split()[19]
    except FileNotFoundError:
        return None


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def restored(path):
    mf, af = path / 'manifest.json', path / 'source_bound_audit.json'
    rp = ROOT / 'results' / f'{path.name}_restore_20261025.json'
    m, a, r = read(mf), read(af), read(rp)
    assert m['status'] == 'observed' and a['status'] == r['status'] == 'passed'
    assert a['manifest_sha256'] == sha(mf) and r['audit_byte_identical']
    assert r['audit_sha256'] == sha(af) == sha(Path(r['preserved_original']) / 'source_bound_audit.json')
    return m, a, [mf, af, rp]


def verify_freeze(directory):
    m = read(directory / 'manifest.json'); assert m['status'] == 'frozen'
    for name, entry in m['files'].items():
        assert sha(directory / name) == entry['sha256'] == sha(entry['source'])
    return directory / 'manifest.json'


def predecessors(mode):
    # Reuse the already-bound matrix and generic gates without changing their tools.
    previous = load('host_edit_probe_predecessors', ROOT / 'scripts/run_config_native_feedback_probe_v1.py')
    files = previous.matrix_evidence() + previous.generic_evidence()
    native = BASE / 'config_native_feedback_probe_v1'
    m, a, evidence = restored(native)
    assert m['stage'] == 'complete' and identity(m['runner_pid']) != str(m['runner_start_ticks'])
    assert not m.get('active_process')
    accepted = ROOT / 'results/config_native_feedback_probe_20261030.json'; report = read(accepted)
    assert report['status'] == 'original_rtl_native_feedback_cases_restored' and report['audit'] == a
    assert a['events'] == 21 and a['checks'] == 689 and a['native_feedback_with_xz_observed']
    files += evidence + [accepted, verify_freeze(ROOT / 'results/config_native_feedback_probe_sources_20261030')]
    if mode == 'cp':
        bm, ba, more = restored(TARGETS['baseline'])
        assert bm['stage'] == 'complete' and bm['mode'] == 'baseline'
        assert identity(bm['runner_pid']) != str(bm['runner_start_ticks']) and not bm.get('active_process')
        assert ba['host_edit']['host_writes'] == 1 and ba['host_edit']['final_pending'] == 0
        files += more
    return {str(f): sha(f) for f in files}


def sources():
    tools_receipt = ROOT / 'results/checkpoint_host_edit_tools_preparation_20261030.json'
    tr = read(tools_receipt)
    assert tr['status'] == 'host_edit_full_system_tools_prepared_not_executed'
    assert set(tr['tools']) == {str(ROOT / 'scripts' / name) for name in TOOLS}
    for path, digest in tr['tools'].items():
        assert sha(path) == digest
    prep = ROOT / 'results/checkpoint_host_edit_testbench_preparation_20261030.json'
    preflight = ROOT / 'results/checkpoint_host_edit_preflight_20261030.json'
    p, pf = read(prep), read(preflight)
    assert p['status'] == 'real_port_host_edit_testbench_prepared_not_compiled_or_simulated'
    assert pf['status'] == 'static_insertion_and_artificial_parser_preflight_only'
    for entries in [p['bound'], pf['bound'], pf['reference_source_bindings']]:
        for path, digest in entries.items():
            assert sha(path) == digest
    assert len(pf['insertion_negative_controls']) == 4 and len(pf['parser_negative_controls']) == 19
    tb = Path(p['testbench']); assert sha(tb) == p['testbench_sha256']
    builder = load('host_edit_checked_builder', VARIANT / 'build.py')
    original, _ = builder.evidence()
    assert tb.read_text() == builder.instrument(original)
    rm, ra, reference_files = restored(REFERENCE)
    assert list(rm['cases']) == ['pressure'] and len(ra['exact_comparisons']) == 27
    originals = {}
    for mode, name in [('baseline', 'query_native_synth_v1'), ('cp', 'checkpoint_edit_synth_v1')]:
        sm, _, evidence = restored(BASE / name)
        assert len(sm['rtl']) == 133
        originals[mode] = sm
        reference_files += evidence
        for n in sm['rtl']:
            assert sha(BASE / name / 'sources' / n) == sm['sources'][n]
    assert originals['baseline']['rtl'] == originals['cp']['rtl']
    for n in originals['cp']['rtl']:
        assert sha(REFERENCE / 'sources' / n) == originals['cp']['sources'][n]
        assert (originals['baseline']['sources'][n] != originals['cp']['sources'][n]) == (n in CHANGED)
    files = reference_files + [tools_receipt, prep, preflight, tb, VARIANT / 'CONTRACT.md', VARIANT / 'build.py',
                              VARIANT / 'declarations.svh', VARIANT / 'extension.svh']
    files += [ROOT / 'scripts' / name for name in TOOLS]
    return rm, ra, tb, originals, list(dict.fromkeys(files))
