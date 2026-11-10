"""Bind the observed full-system race to the earlier slice's explicit start interlock."""
from pathlib import Path
import datetime
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
FULL = Path('/tmp/B_state_residency_recovery_20261102/ka_publication_release_full_rtl_v5')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    frozen = ROOT / 'results/checkpoint_joint_sources_20261026'
    selected = ROOT / 'results/checkpoint_joint_20261026.json'
    receipt = json.loads(selected.read_text())
    fm = json.loads((frozen / 'manifest.json').read_text())
    assert receipt['status'] == 'passed' and receipt['sources'] == fm
    inputs = [selected, frozen / 'manifest.json']
    names = ['hardware/variants/checkpoint_stage_v1/tb_joint.sv',
             'hardware/variants/checkpoint_stage_v1/build_tb.py',
             'hardware/variants/checkpoint_stage_v1/CONTRACT.md']
    for name in names:
        assert sha(frozen / name) == fm[name]
        inputs.append(frozen / name)
    early = (frozen / names[0]).read_text()
    early_lease = next(l for l in early.splitlines() if 'checkpoint_lease_guard lease(' in l)
    assert '.command_valid(tx_start_valid||tx_commit_valid||tx_cancel_valid||cfg_valid||k_cfg_valid||c_load_valid)' in early_lease
    assert '.start_valid(tx_start_valid)' in early
    guard = FULL / 'sources/checkpoint_lease_guard.sv'
    query = FULL / 'sources/query_residency_system.sv'
    barrier = FULL / 'sources/checkpoint_publish_barrier.sv'
    m = json.loads((FULL / 'preparation.json').read_text())
    # Bind directly to the already reviewed full-run source hashes, irrespective
    # of differences between preparation receipt formats.
    manifest = json.loads((FULL / 'manifest.json').read_text())
    prep_text = json.dumps(m)
    for p in [guard, query, barrier]:
        assert sha(p) in prep_text, p
    assert manifest['status'] == 'failed' and not manifest.get('active_process')
    full_text = query.read_text()
    full_lease = next(l for l in full_text.splitlines() if 'checkpoint_lease_guard checkpoint_lease(' in l)
    assert '.command_valid(ap_valid||cp_valid||qc_cp_valid)' in full_lease
    assert '||jp_owned||' in full_lease
    start_open = next(l for l in full_text.splitlines() if l.startswith('wire jp_start_open='))
    assert 'pc_release' not in start_open
    assert '.start_valid(jp_start&&jp_start_open)' in full_text
    release_expression = re.search(r'assign release_ready=([^;]+);', guard.read_text()).group(1)
    assert release_expression == '!rst&&owned&&retired&&route_retired&&!command_busy&&!command_valid&&!test_reset'
    review = ROOT / 'results/ka_publication_release_full_rtl_v5_counterexample_review_20261102.json'
    r = json.loads(review.read_text())
    assert r['status'] == 'initialized_full_RTL_overlap_counterexample_audited'
    for n, h in r['evidence_sha256'].items():
        assert sha(FULL / n) == h
    for n in ['pc_release_valid', 'pc_release_ready', 'jp_start', 'jp_start_ready', 'pc_owned']:
        assert r['pre_accept_values'][n] == 1
    assert r['post_accept_values']['jp_owned'] == 1 and r['post_accept_values']['pc_owned'] == 0
    contracts = ['hardware/variants/checkpoint_stage_v1/CONTRACT.md',
                 'hardware/variants/checkpoint_system_v1/CONTRACT.md',
                 'hardware/variants/checkpoint_commit_v1/CONTRACT.md',
                 'hardware/variants/route_checkpoint_join_v1/CONTRACT.md',
                 'hardware/variants/query_checkpoint_join_v1/CONTRACT.md',
                 'hardware/variants/stage_static_cp_system_sources_v1/CONTRACT.md']
    contract_evidence = {}
    for name in contracts:
        p = ROOT / name
        contract_evidence[name] = {'sha256': sha(p), 'relevant_lines': [
            {'line': i, 'text': line} for i, line in enumerate(p.read_text().splitlines(), 1)
            if any(word in line for word in ['lease', '释放', '同拍', 'READY', 'admission'])]}
        inputs.append(p)
    inputs += [guard, query, barrier, FULL / 'preparation.json', FULL / 'manifest.json', review, Path(__file__)]
    report = {
        'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'start_release_interlock_lineage_difference_source_bound',
        'frozen_slice_lease_instance': early_lease,
        'full_lease_instance': full_lease,
        'full_start_open': start_open,
        'release_ready_expression': release_expression,
        'finding': 'The earlier frozen slice connects transaction start to lease.command_valid. The full query connects AP/CP/QC offers but omits publication start; jp_owned blocks only after acceptance. The full initialized run actually accepted both requests and lost the lease.',
        'boolean_consequence': 'In the slice, tx_start_valid implies command_valid, which forces release_ready=0. The same interlock is absent from the full query wiring.',
        'classification': 'Observed full RTL ownership-invariant violation; source evidence supports an integration interlock omission. Six reviewed contracts do not explicitly specify simultaneous idle start/release arbitration. This is not proof that every possible external caller contract permits overlap.',
        'reviewed_contracts': contract_evidence,
        'next_verification': 'Evaluate an isolated start-to-command_valid interlock candidate with held VALID, response backpressure, cancellation, release-only and simultaneous-start tests before choosing a production repair. Preserve original failing full probe.',
        'production_rtl_changed': False,
        'file_sha256': {str(p): sha(p) for p in inputs},
        'full_system_functional_netlist_validated': False,
        'physical_gate_open': False,
    }
    out = ROOT / 'results/ka_publication_release_contract_lineage_review_20261102.json'
    assert not out.exists()
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(report['status'])


if __name__ == '__main__':
    main()
