"""Serialize candidate compilation behind original full native acceptance."""
import json
from pathlib import Path
from check_vitis_kernel import digest, require

ROOT = Path(__file__).resolve().parents[1]
REPORTS = {
    'compact_native_stack_recovery_rtl_audit_20261027_v3.json':
        'compact_native_stack256_full4tx_full44_rtl_and_original_postcheck_verified',
    'hls_binary_fsm_candidate_edit_audit_20261025_v1.json':
        'binary_fsm_candidate_exact_edits_and_legal_state_encoding_map_independently_checked',
    'fsm_binary_four_state_regression_20261025_v1.json':
        'seven_state_encoding_mechanism_four_state_control_reset_and_outputs_regression_passed',
    'full_rtl_stricter_cap_incident_20261025_v1.json':
        'full44_dpi_compile_llvm_allocation_failure_and_native_compact_guard_abort_preserved',
}


def validate(root=ROOT):
    files = {str(Path(__file__).resolve()): digest(__file__)}
    for name, status in REPORTS.items():
        path = root/'results'/name
        require(path.is_file(), 'Serialized binary-FSM prerequisite missing: '+name)
        report = json.loads(path.read_text())
        require(report.get('status')==status, 'Unaccepted binary-FSM prerequisite: '+name)
        bindings = report.get('files')
        require(isinstance(bindings,dict) and bindings, 'Missing exact prerequisite bindings')
        if name.startswith('compact_native'):
            require(report.get('rtl_verified') is True and len(report.get('snapshots',[]))==4, 'Original full native acceptance incomplete')
        if name.startswith('fsm_binary_four'):
            require(report.get('samples')==1280 and report.get('input_level_cases')==64 and report.get('all_seven_states_observed') is True, 'Mechanism matrix incomplete')
        for source, checksum in bindings.items():
            require(digest(source)==checksum, 'Changed binary-FSM prerequisite evidence: '+source)
            require(source not in files or files[source]==checksum, 'Conflicting prerequisite binding')
            files[source] = checksum
        files[str(path)] = digest(path)
    return files
