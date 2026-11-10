"""Navigate restored CP placed/routed paths; never infer board frequency."""
from pathlib import Path
import json
from run_checkpoint_authority import ROOT, sha
from parse_state_timing_paths import parse_report


def main():
    base = Path('/tmp/B_state_residency_offer_20261025')
    gate = json.loads((base/'checkpoint_edit_physical_queue_v2/manifest.json').read_text())
    assert gate['status']=='observed' and gate['stage']=='complete', 'Wait for existing physical owner, actual restoration and freeze'
    p = base/'checkpoint_edit_physical_v1'
    assert Path(gate['target'])==p
    m = json.loads((p/'manifest.json').read_text())
    a = json.loads((p/'source_bound_audit.json').read_text())
    rp = ROOT/'results/checkpoint_edit_physical_v1_restore_20261025.json'
    r = json.loads(rp.read_text())
    acceptance_path = ROOT/'results/checkpoint_edit_physical_20261029.json'
    acceptance = json.loads(acceptance_path.read_text())
    assert m['status']=='observed' and m['exit_code']==0
    assert a['status']==r['status']=='passed' and r['audit_byte_identical']
    assert a['manifest_sha256']==sha(p/'manifest.json')
    assert r['audit_sha256']==sha(p/'source_bound_audit.json')
    assert acceptance['audit']==a and acceptance['restoration']==r
    freeze = ROOT/'results/checkpoint_edit_physical_sources_20261029'
    fm = json.loads((freeze/'manifest.json').read_text())
    for name,entry in fm['files'].items():
        assert sha(freeze/name)==entry['sha256']==sha(Path(entry['source'])),name
    assert a['timing_checks']['routed']['loops']==0 and a['timing_checks']['routed']['latch_loops']==0
    observations = {}
    report_hashes = {}
    for stage in ['placed','routed']:
        report = p/f'timing_{stage}.rpt'
        assert sha(report)==a['artifact_sha256'][report.name]
        report_hashes[stage] = sha(report)
        paths = parse_report(report.read_text(),'core_clk')
        worst = {}
        for kind,key in [('Setup','WNS_ns'),('Hold','WHS_ns')]:
            selected = [x for x in paths if x['path_type']==kind]
            assert selected
            path = min(selected,key=lambda x:x['slack_ns'])
            assert path['slack_ns']==a['timing_summaries'][stage][key],(stage,kind)
            if stage=='routed':
                dtype = 'max' if kind=='Setup' else 'min'
                samples = [x for x in a['internal_paths'] if x['delay_type']==dtype]
                assert path['slack_ns']==min(float(x['slack_ns']) for x in samples)
                assert any(x['startpoint']==path['source'] and x['endpoint']==path['destination']
                           and float(x['slack_ns'])==path['slack_ns'] for x in samples)
                if a['complete_route']:
                    assert set(path['net_placement_counts'])=={'routed'}
            worst[kind] = path
        observations[stage] = dict(worst=worst,reported_path_count=len(paths),
            reported_paths=[{key:x[key] for key in ['path_type','source','destination','slack_ns','logic_levels',
                                                  'data_delay_ns','logic_delay_ns','net_delay_ns','net_placement_counts']}
                            for x in paths])
    baseline_path = ROOT/'results/checkpoint_edit_timing_path_20261028.json'
    baseline = json.loads(baseline_path.read_text())
    assert baseline['audit_sha256']==m['synthesis_audit_sha256']
    routed = observations['routed']['worst']['Setup']
    comparison = dict(synthesis_analysis_sha256=sha(baseline_path),
        same_endpoint_names=baseline['source']==routed['source'] and baseline['destination']==routed['destination'],
        synthesis_source=baseline['source'],synthesis_destination=baseline['destination'],
        synthesis_wns_ns=baseline['slack_ns'],routed_wns_ns=routed['slack_ns'],
        worst_slack_delta_ns=routed['slack_ns']-baseline['slack_ns'],
        synthesis_logic_levels=baseline['logic_levels'],routed_logic_levels=routed['logic_levels'],
        synthesis_estimated_net_delay_ns=baseline['estimated_net_delay_ns'],routed_net_delay_ns=routed['net_delay_ns'],
        scope='Each stage worst reported setup path, possibly different endpoints/cones. Estimated synthesis nets and routed nets are different observations, not same-path causal evidence or a board-frequency measurement.')
    result = dict(status='restored_full_system_physical_path_navigation',
        analyzer_sha256=sha(Path(__file__)),parser_sha256=sha(ROOT/'scripts/parse_state_timing_paths.py'),
        audit_sha256=sha(p/'source_bound_audit.json'),restore_receipt_sha256=sha(rp),
        acceptance_report_sha256=sha(acceptance_path),report_sha256=report_hashes,
        observations=observations,synthesis_comparison=comparison,
        complete_route=a['complete_route'],drc_violation_count=a['drc_violation_count'],
        constrained_internal_10ns_setup_hold_met=a['constrained_internal_10ns_setup_hold_met'],
        timing_qualified=False,board_acceptance=False,
        scope='Only paths printed in the restored reports. All declared logic types, wrapped physical rows, launch delays and data-net delays are reconciled. Clock-network rows are excluded from data-cone ranking. Interpretation retains all physical audit limitations; no new simulation, candidate selection or board acceleration claim.')
    out = ROOT/'results/checkpoint_edit_physical_timing_20261029.json'
    assert not out.exists()
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('CHECKPOINT_PHYSICAL_PATHS_INDEXED','WNS',routed['slack_ns'],'levels',routed['logic_levels'])


if __name__=='__main__':
    main()
