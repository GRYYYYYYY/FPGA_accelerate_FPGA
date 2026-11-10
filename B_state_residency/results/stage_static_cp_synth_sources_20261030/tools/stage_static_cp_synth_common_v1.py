"""CP-only static-stage OOC gates; reuse validated runtime and waits."""
from prepare_stage_static_cp_synth_v1 import ROOT, BASE, TARGET, REFERENCE, VARIANT, sha, read, restored, verify_freeze, identity
from prepare_stage_static_cp_synth_v1 import evidence as prepared_evidence
from config_native_publication_synth_common_v1 import BIN, runtime_environment, memory_admission, wait_preserving
TOOLS = ['stage_static_cp_synth_common_v1.py', 'prepare_stage_static_cp_synth_v1.py',
 'run_stage_static_cp_synth_v1.py', 'inspect_stage_static_cp_synth_v1.py',
 'audit_stage_static_cp_synth_v1.py', 'freeze_stage_static_cp_synth_v1.py',
 'config_native_publication_synth_common_v1.py', 'host_edit_system_common_v1.py',
 'analyze_restore_seed_loops.py', 'audit_restore_seed_diagnostics.py',
 'read_tcl_list_records.tcl', 'archive_offer_result.py', 'verify_search_retire_restore.py',
 'restore_offer_result.py', 'run_checkpoint_authority.py']
PREPARATION=ROOT/'results/stage_static_cp_synth_tools_preparation_20261030.json'

def evidence():
    rm, cm, proof = prepared_evidence()
    fm, fa, _ = restored(BASE/'stage_static_cp_system_v1')
    ra = read(REFERENCE/'source_bound_audit.json')
    receipt=read(PREPARATION)
    assert receipt['status']=='stage_static_synth_tools_prepared_not_executed'
    assert set(receipt['tools'])=={str(ROOT/'scripts'/n) for n in TOOLS}
    for path,digest in receipt['tools'].items(): assert sha(path)==digest
    runtime_environment()
    return rm,ra,fm,fa,proof
