"""Gated CP specialization overlay. Preparation alone is not RTL validation."""
from pathlib import Path
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PARENT = HERE.parent / 'checkpoint_edit_exclusion_v1'
NAMES = ['query_lifecycle.sv', 'query_residency_system.sv']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def restored(path):
    manifest = json.loads((path/'manifest.json').read_text())
    audit = json.loads((path/'source_bound_audit.json').read_text())
    receipt_path = ROOT/'results'/f'{path.name}_restore_20261025.json'
    receipt = json.loads(receipt_path.read_text())
    assert manifest['status'] == 'observed'
    assert audit['status'] == receipt['status'] == 'passed'
    assert receipt['audit_byte_identical']
    assert audit['manifest_sha256'] == sha(path/'manifest.json')
    assert receipt['audit_sha256'] == sha(path/'source_bound_audit.json')
    return manifest, audit, receipt_path


def evidence(reference):
    assert reference.name == 'query_native_system_crc_pressure_v1'
    rm, ra, rr = restored(reference)
    units = reference.parent/'checkpoint_edit_units_v1'
    um, ua, ur = restored(units)
    assert len(ua['cases']) == 12 and ua['exact_trace_comparisons'] == 7
    assert ua['generic_overlap_specialization_counterexample']
    matrix = ROOT/'results/query_native_matrix_20261028.json'
    mr = json.loads(matrix.read_text())
    assert mr['status'] == 'eight_behavioral_cases_passed'
    assert mr['total_case_file_comparisons'] == 216
    freezes = [ROOT/'results'/f'{name}_sources_20261028'/'manifest.json'
               for name in ['query_native_matrix', 'checkpoint_edit_units']]
    for path in freezes:
        frozen = json.loads(path.read_text())
        assert frozen['status'] == 'frozen'
        for rel, entry in frozen['files'].items():
            assert sha(path.parent/rel) == entry['sha256'], rel
    pm = json.loads((PARENT/'manifest.json').read_text())
    for name in NAMES:
        assert sha(reference/'sources'/name) == pm['sources'][name]['baseline']
        assert sha(PARENT/'fixed'/name) == pm['sources'][name]['fixed']
    return dict(reference_audit_sha256=sha(reference/'source_bound_audit.json'),
                reference_restore_sha256=sha(rr), unit_audit_sha256=sha(units/'source_bound_audit.json'),
                unit_restore_sha256=sha(ur), matrix_sha256=sha(matrix),
                freeze_sha256={str(p.relative_to(ROOT)): sha(p) for p in freezes},
                builder_sha256=sha(HERE/'build.py'))


def sources(reference):
    proof = evidence(reference)
    return {name: (PARENT/'fixed'/name).read_text() for name in NAMES}, proof


def monitored_tb(original):
    path = ROOT/'scripts/prepare_checkpoint_edit_monitor.py'
    spec = importlib.util.spec_from_file_location('cp_edit_monitor', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.instrument(original)
