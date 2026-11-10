"""Unchanged v5 functional gates plus preserved interruption evidence for a fresh run."""
from host_edit_system_common_v1 import ROOT, BASE, read, sha, identity
from stage_static_cp_shadow_common_v5 import evidence as original_evidence, REFERENCE, SYNTH, VARIANT

TARGET = BASE/'stage_static_cp_shadow_system_v6'


def evidence():
    fm, proof = original_evidence()
    observation = ROOT/'results/stage_static_cp_shadow_v5_interruption_observation_20261030.json'
    preservation = ROOT/'results/stage_static_cp_shadow_v5_interruption_preservation_20261030.json'
    obs, saved = read(observation), read(preservation)
    assert obs['status'] == 'interrupted_without_terminal_receipt_not_accepted'
    assert saved['status'] == 'interrupted_scene_actual_restore_byte_identical_not_functional_acceptance'
    assert saved['observation_sha256'] == sha(observation)
    assert saved['original_unchanged'] and saved['actual_restore_byte_identical']
    assert not saved['full_system_functional_netlist_validated']
    assert sha(saved['archive']) == saved['archive_sha256']
    old = BASE/'stage_static_cp_shadow_system_v5'
    oldm = read(old/'manifest.json')
    supervisor = read(BASE/'stage_static_cp_shadow_system_v5_followup_v1/manifest.json')
    for m in [oldm, supervisor]:
        assert identity(m['runner_pid']) != str(m['runner_start_ticks']), 'Original owner still live'
    active = oldm.get('active_process')
    if active:
        assert identity(active['pid']) != str(active['start_ticks']), 'Original simulator still live'
    assert identity(216051) != '1651661803', 'Original XSim kernel still live'
    for filename, digest in obs['evidence'].items():
        assert sha(filename) == digest
    for source in [observation, preservation, ROOT/'scripts/stage_static_cp_shadow_common_v5.py',
                   ROOT/'scripts/preserve_stage_static_cp_shadow_v5_interruption_v1.py']:
        proof[str(source)] = sha(source)
    assert saved['tool_sha256'] == proof[str(ROOT/'scripts/preserve_stage_static_cp_shadow_v5_interruption_v1.py')]
    return fm, proof
