"""Scoped two-state admission checks; deliberately not an RTL formal proof."""
from itertools import product
from pathlib import Path
import hashlib
import json

BASE = Path('/tmp/B_state_residency_offer_20261025/stage_static_cp_shadow_system_v6/sources')
REQUIRED = {
    'query_residency_system.sv': [
        'wire ap_allow=!rst&&!k_cold_rst&&!abort&&pc_owned&&!jp_owned&&!k_busy&&!k_rec_valid&&!as_cfg_lease&&!k_a_valid&&!ap_owned;',
        'assign b_k_rec_valid=!boot_pending&&!qc_busy&&!pc_owned&&!as_cfg_lease&&k_rec_valid;',
        'wire jp_start_open=!ap_valid&&!ap_owned&&!cp_valid&&!qc_cp_valid&&!as_cfg_valid&&f_sv==0&&!k_rec_valid&&!boot_pending;',
        'assign as_retired=!as_busy&&!as_core_cfg_valid;',
        '.no_offers(!ap_valid&&f_sv==0&&!rc_req_valid&&!qc_cmd_valid&&!k_rec_valid)',
    ],
    'checkpoint_lease_guard.sv': [
        'assign acquire_ready=!rst&&!owned&&healthy&&route_retired&&no_offers&&!command_busy&&!test_reset;',
    ],
    'recovery_coordinator.sv': [
        'DRAIN:if(backend_drained&&normal_retired)',
        'AS:if(a_ready)state<=AW;',
    ],
    'residency_system.sv': [
        '.normal_retired(f_normal_retired&&as_retired&&(!wm_on||wm_services_retired))',
        'assign as_attempt_reset=k_attempt_reset;',
    ],
}


def main():
    evidence = {}
    for name, snippets in REQUIRED.items():
        p = BASE / name
        raw = p.read_bytes()
        source = raw.decode()
        for snippet in snippets:
            assert snippet in source, (name, snippet)
        evidence[name] = {'path': str(p), 'sha256': hashlib.sha256(raw).hexdigest(),
                          'required_source_fragments': snippets}
    checked = 0
    # Other admission qualifiers are overapproximated as independent enables.
    # If a pair is excluded even here, additional conjunctions cannot enable it.
    for pc, rec_valid, ap_valid, ka_valid, busy, lease, boot, qc, ap_owned, jp_owned in product((False, True), repeat=10):
        rec_offer = not boot and not qc and not pc and not lease and rec_valid
        ap_offer = pc and not jp_owned and not busy and not rec_valid and not lease and not ka_valid and not ap_owned and ap_valid
        lease_acquire = not pc and not rec_valid and not ap_valid
        publication_start = pc and not rec_valid and not ap_valid and not ap_owned and not boot
        assert not (rec_offer and ap_offer)
        assert not (rec_offer and lease_acquire)
        assert not (rec_offer and publication_start)
        checked += 1
    for drained, retired, authority_busy, cfg_response in product((False, True), repeat=4):
        leave_drain = drained and retired and not authority_busy and not cfg_response
        assert not (leave_drain and (authority_busy or cfg_response))
    report = {
        'status': 'scoped_two_state_admission_pairs_excluded_not_full_reachability_proof',
        'source_evidence': evidence, 'admission_assignments_checked': checked,
        'drain_assignments_checked': 16,
        'excluded_same_cycle_pairs': ['recovery/AP offer', 'recovery/new lease acquisition',
                                      'recovery/publication start'],
        'drain_result': 'cannot leave DRAIN while authority busy or configuration response pending',
        'limitations': ['hand-transcribed conjunction overapproximations checked against source fragments',
                       'does not prove sequential invariants or X/Z behavior',
                       'does not prove KA stall globally unreachable or full functional acceptance'],
        'full_system_functional_netlist_validated': False, 'physical_gate_open': False,
    }
    out = Path('results/stage_static_cp_shadow_v6_ka_admission_pairs_20261031.json')
    assert not out.exists(), 'preserve existing evidence'
    report['checker_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(out)


if __name__ == '__main__':
    main()
