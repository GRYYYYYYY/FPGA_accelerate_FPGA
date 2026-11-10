"""Navigate only restored, independently reopened CP route-recovery reports."""
from pathlib import Path
import json
from run_checkpoint_authority import ROOT, sha
from parse_state_timing_paths import parse_report
from audit_state_ooc_physical_v2 import timing_summary


def observe_report(report, summary, samples=None, require_routed=False):
    assert timing_summary(report)==summary
    paths=parse_report(report.read_text(),'core_clk')
    worst={}
    for kind,key,dtype in [('Setup','WNS_ns','max'),('Hold','WHS_ns','min')]:
        selected=[p for p in paths if p['path_type']==kind]
        assert selected
        path=min(selected,key=lambda p:p['slack_ns'])
        assert path['slack_ns']==summary[key],(report,kind)
        if samples is not None:
            entries=[p for p in samples if p['delay_type']==dtype]
            assert len(entries)==10
            assert path['slack_ns']==min(float(p['slack_ns']) for p in entries)
            assert any(p['startpoint']==path['source'] and p['endpoint']==path['destination']
                       and float(p['slack_ns'])==path['slack_ns'] for p in entries)
        if require_routed:
            assert set(path['net_placement_counts'])=={'routed'}
        worst[kind]=path
    keys=['path_type','source','destination','slack_ns','logic_levels','data_delay_ns',
          'logic_delay_ns','net_delay_ns','net_placement_counts']
    return dict(worst=worst,reported_path_count=len(paths),
                reported_paths=[{key:p[key] for key in keys} for p in paths])


def main():
    base=Path('/tmp/B_state_residency_offer_20261025')
    owner=base/'checkpoint_edit_route_recovery_followup_v1'
    gate=json.loads((owner/'manifest.json').read_text())
    assert gate['status']=='observed' and gate['stage']=='complete', 'Wait for recovery owner, actual restoration and freeze'
    assert not Path('/proc',str(gate['runner_pid'])).exists(), 'Wait for postprocessing owner to exit'
    p=base/'checkpoint_edit_route_recovery_v1'; assert Path(gate['target'])==p
    m=json.loads((p/'manifest.json').read_text()); a=json.loads((p/'source_bound_audit.json').read_text())
    rp=ROOT/'results/checkpoint_edit_route_recovery_v1_restore_20261025.json'
    r=json.loads(rp.read_text())
    ap=ROOT/'results/checkpoint_edit_route_recovery_20261030.json'; accepted=json.loads(ap.read_text())
    assert m['status']=='observed' and m['stage']=='complete' and m['exit_code']==0
    assert a['status']==r['status']=='passed' and r['audit_byte_identical']
    assert a['manifest_sha256']==sha(p/'manifest.json') and r['audit_sha256']==sha(p/'source_bound_audit.json')
    assert accepted['audit']==a and accepted['restoration']==r
    assert a['auditor_sha256']==sha(ROOT/'scripts/audit_state_route_recovery_v2.py')
    assert a['parser_sha256']==sha(ROOT/'scripts/parse_state_timing_paths.py')
    assert a['independent_reopened_dcp_matches']
    freeze=ROOT/'results/checkpoint_edit_route_recovery_sources_20261030'
    fm=json.loads((freeze/'manifest.json').read_text())
    for name,entry in fm['files'].items():
        assert sha(freeze/name)==entry['sha256']==sha(Path(entry['source'])),name
    assert a['timing_checks']['routed']['loops']==a['timing_checks']['routed']['latch_loops']==0
    report_files={'placed':'prior/timing_placed.rpt','resume':'timing_resume.rpt',
                  'routed':'timing_routed.rpt','reopened':'inspection/timing.rpt'}
    hashes={}; observations={}
    for stage,name in report_files.items():
        report=p/name
        hashes[stage]=sha(report)
        expected=m['inputs'][name] if stage=='placed' else a['artifact_sha256'][name]
        assert hashes[stage]==expected
        postroute=stage in ['routed','reopened']
        observations[stage]=observe_report(report,a['timing_summaries'][stage],
            a['internal_paths'] if postroute else None,postroute and a['complete_route'])
    for first,second in [('placed','resume'),('routed','reopened')]:
        assert observations[first]['reported_paths']==observations[second]['reported_paths']
    baseline_file=ROOT/'results/checkpoint_edit_timing_path_20261028.json'
    baseline=json.loads(baseline_file.read_text()); assert baseline['audit_sha256']==m['synthesis_audit_sha256']
    routed=observations['routed']['worst']['Setup']; placed=observations['placed']['worst']['Setup']
    comparisons={}
    for label,old in [('synthesis',baseline),('placed',placed)]:
        comparisons[label]=dict(source=old['source'],destination=old['destination'],slack_ns=old['slack_ns'],
            logic_levels=old['logic_levels'],same_endpoint_names=old['source']==routed['source'] and old['destination']==routed['destination'],
            routed_worst_slack_delta_ns=routed['slack_ns']-old['slack_ns'],
            scope='Worst printed paths at each stage; matching endpoint names alone do not establish identical mapped cones or same-path causality.')
    result=dict(status='restored_route_recovery_path_navigation',analyzer_sha256=sha(Path(__file__)),
        parser_sha256=sha(ROOT/'scripts/parse_state_timing_paths.py'),
        summary_parser_sha256=sha(ROOT/'scripts/audit_state_ooc_physical_v2.py'),
        owner_manifest_sha256=sha(owner/'manifest.json'),audit_sha256=sha(p/'source_bound_audit.json'),
        restoration_sha256=sha(rp),acceptance_sha256=sha(ap),physical_freeze_manifest_sha256=sha(freeze/'manifest.json'),
        saved_placement_sha256=m['saved_placement_sha256'],runtime_audit_sha256=m['runtime_audit_sha256'],
        synthesis_analysis_sha256=sha(baseline_file),report_files=report_files,report_sha256=hashes,
        observations=observations,comparisons=comparisons,complete_route=a['complete_route'],
        drc_violation_count=a['drc_violation_count'],
        constrained_internal_10ns_setup_hold_met=a['constrained_internal_10ns_setup_hold_met'],
        timing_qualified=False,board_acceptance=False,full_behavior_matrix_complete=False,
        limitations=a['limitations'],
        scope='Navigate every printed setup/hold path and retain full worst-path data cells/nets, '
              'locations, hierarchy, fanout and delays. Clock-network rows are excluded from data-cone ranking. '
              'Recovered route is measured independently of the crashed process, which had no saved routed checkpoint. '
              'No new RTL candidate, behavior proof, constraint waiver or board-frequency inference.')
    out=ROOT/'results/checkpoint_edit_route_recovery_timing_20261030.json'; assert not out.exists()
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('ROUTE_RECOVERY_PATHS_INDEXED','WNS',routed['slack_ns'],'levels',routed['logic_levels'])


if __name__=='__main__': main()
