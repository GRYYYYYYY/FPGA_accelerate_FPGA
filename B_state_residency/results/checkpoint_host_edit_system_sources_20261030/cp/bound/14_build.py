"""Prepare a verification-only real host edit suffix; never launch a solver."""
from pathlib import Path
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = Path('/tmp/B_state_residency_offer_20261025')
REFERENCE = BASE / 'checkpoint_edit_system_crc_pressure_v1'
MODULE = 'module tb_candidate_offer;'
MARKER = ' $fdisplay(trace,"FOURTH_PASS %0d %0d %0d %0d %0d %0d %0d %08h",cycles,poll_i,expand_i,candidate_i,commits,rc_slots,system.controller.last_sequence,qc_cp_crc);'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def instrument(original):
    assert original.count(MODULE) == original.count(MARKER) == original.count('\nendmodule') == 1
    assert 'he_active' not in original and 'HOST_EDIT_NATIVE_PASS' not in original
    assert original.count('CHECKPOINT_EDIT_EXCLUSION_PASS') == 1
    assert len(re.findall(r'\blabel_write\b', original)) == 1
    declarations = (HERE / 'declarations.svh').read_text()
    extension = (HERE / 'extension.svh').read_text()
    assert not re.search(r'\b(force|release)\s+', declarations + extension)
    assert not re.search(r'\bsystem\.[\w.\[\]:]+\s*(?:<=|=(?!=))', extension)
    result = original.replace(MODULE, MODULE + '\n' + declarations)
    result = result.replace(MARKER, MARKER + '\n host_edit_extension;')
    result = result.replace('\nendmodule', '\n' + extension + '\nendmodule')
    # Removal of exactly the three inserted blocks must recover every original byte.
    recovered = result.replace(MODULE + '\n' + declarations, MODULE, 1)
    recovered = recovered.replace(MARKER + '\n host_edit_extension;', MARKER, 1)
    recovered = recovered.replace('\n' + extension + '\nendmodule', '\nendmodule', 1)
    assert recovered == original
    assert len(re.findall(r'\blabel_write\b', result)) == 2
    return result


def evidence():
    mfile = REFERENCE / 'manifest.json'; afile = REFERENCE / 'source_bound_audit.json'
    rfile = ROOT / 'results/checkpoint_edit_system_crc_pressure_v1_restore_20261025.json'
    m, a, r = [json.loads(p.read_text()) for p in [mfile, afile, rfile]]
    assert m['status'] == 'observed' and a['status'] == r['status'] == 'passed'
    assert r['audit_byte_identical'] and r['audit_sha256'] == sha(afile)
    assert a['manifest_sha256'] == sha(mfile) and len(a['exact_comparisons']) == 27
    assert a['checkpoint_edit_exclusion']['edit'] == 0
    tb = REFERENCE / 'sources/tb_query_fault.sv'
    assert sha(tb) == m['sources']['tb_query_fault.sv']['sha256']
    analysis = ROOT / 'results/checkpoint_host_edit_coverage_20261030.json'
    am = json.loads(analysis.read_text())
    assert am['status'] == 'restored_stimulus_gap_identified_not_new_functional_result'
    freeze = ROOT / 'results/checkpoint_host_edit_coverage_sources_20261030'
    for name, entry in json.loads((freeze / 'manifest.json').read_text())['files'].items():
        assert sha(freeze / name) == entry['sha256'] == sha(entry['source'])
    bound = [mfile, afile, rfile, tb, analysis, freeze / 'manifest.json',
             HERE / 'build.py', HERE / 'declarations.svh', HERE / 'extension.svh']
    return tb.read_text(), {str(p): sha(p) for p in bound}


def prepare():
    original, bound = evidence()
    output = HERE / 'prepared'
    report = ROOT / 'results/checkpoint_host_edit_testbench_preparation_20261030.json'
    assert not output.exists() and not report.exists()
    generated = instrument(original)
    output.mkdir(); target = output / 'tb_query_fault.sv'; target.write_text(generated)
    report.write_text(json.dumps(dict(status='real_port_host_edit_testbench_prepared_not_compiled_or_simulated',
        bound=bound, testbench=str(target), testbench_sha256=sha(target),
        original_stimulus_preserved_bytewise_after_removing_insertions=True,
        insertion='After FOURTH_PASS, before original summary checks; original trace prefix is retained.',
        extra_expected=dict(host_requests=3,host_replies=3,host_writes=1,write_replies=1,
            cp_requests=3,cp_replies=3,import_words=20,export_words=10,
            clean_reject_checks=1,dirty_accept_checks=1,edit_cycles=1,atomic_checks='nonzero'),
        cp_total_expected=dict(requests=15,replies=15,imports=60,exports=90,edit=1),
        extension_watchdog_cycles=100000, production_rtl_changed=False,
        scope='Prepared suffix only. Both baseline and CP require separate actual full-system runs, exact output/event/cycle comparison, independent audit, archive and actual restore before acceptance. Existing matrix and generic/native descriptor probes retain their execution order; no new runner, solver, automatic followup or functional result.'),
        indent=2, sort_keys=True) + '\n')
    print('HOST_EDIT_TB_PREPARED', sha(target))


if __name__ == '__main__':
    prepare()
