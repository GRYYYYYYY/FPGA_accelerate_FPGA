"""Bind prepared physical tools without launching or reading a live synthesis root."""
import ast
import json
from pathlib import Path
from host_edit_system_common_v1 import ROOT, sha, read


def main():
    result = ROOT/'results/config_native_physical_tools_preparation_20261030.json'
    assert not result.exists(), 'Preserve prior preparation binding'
    scripts = ['check_config_native_physical_inputs_v1.py', 'prepare_config_native_physical_v1.py',
        'run_config_native_physical_v1.py', 'inspect_config_native_physical_v1.py',
        'audit_config_native_physical_v1.py', 'freeze_config_native_physical_v1.py',
        'preflight_config_native_physical_v1.py', 'config_native_publication_synth_common_v1.py',
        'host_edit_system_common_v1.py', 'audit_state_ooc_physical_v2.py',
        'audit_state_route_recovery_v2.py', 'parse_state_timing_paths.py', 'run_checkpoint_authority.py',
        'archive_offer_result.py', 'verify_search_retire_restore.py', 'restore_offer_result.py']
    files = [ROOT/'scripts'/name for name in scripts]
    for p in files: ast.parse(p.read_text())
    receipts = [ROOT/'results'/f'config_native_physical_{name}_preparation_20261030.json'
                for name in ['input_gate', 'preparer', 'runner', 'inspector', 'auditor', 'freezer']]
    for p in receipts:
        r = read(p)
        if 'bound' in r:
            for name, digest in r['bound'].items(): assert sha(name) == digest
        if 'tool' in r:
            assert sha(Path(r['tool'])) == r['sha256']
    templates = [ROOT/'hardware/scripts'/name for name in ['implement_state_ooc.tcl', 'inspect_state_route_v1.tcl']]
    result.write_text(json.dumps(dict(status='physical_tools_source_bound_not_executed',
        tools={str(p): sha(p) for p in files+templates},
        preparation_receipts={str(p): sha(p) for p in receipts},
        positive_actual_candidate_execution_pending=True,
        negative_admission_checks_passed=True,
        parser_crosscheck_scope='Restored CP reports only; not native candidate physical results.',
        scope='No run directory, process launch, candidate selection or timing acceptance.'),
        indent=2, sort_keys=True)+'\n')
    print('NATIVE_PHYSICAL_TOOLS_BOUND', len(files+templates))


if __name__ == '__main__': main()
