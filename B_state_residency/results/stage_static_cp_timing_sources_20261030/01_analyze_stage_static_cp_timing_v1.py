"""Index the restored static-stage OOC path, including every MUX level."""
from pathlib import Path
import json
from host_edit_system_common_v1 import ROOT,BASE,read,sha,restored,identity
from analyze_route_stage_timing_v2 import parse_report


def main():
    follow=read(BASE/'stage_static_cp_synth_followup_v1/manifest.json')
    assert follow['status']=='observed' and follow['stage']=='complete'
    assert identity(follow['runner_pid'])!=str(follow['runner_start_ticks'])
    p=BASE/'stage_static_cp_synth_v1';m,a,files=restored(p)
    assert a['check_timing_counts']['loops']==0 and not a['timing_loop_warnings']
    accepted=ROOT/'results/stage_static_cp_synth_20261030.json'
    assert read(accepted)['audit']==a
    report=p/'timing_synth.rpt';assert sha(report)==a['artifact_sha256'][report.name]
    result=parse_report(report.read_text())
    assert result['slack_ns']==a['preplacement_wns_ns']
    baseline_path=ROOT/'results/checkpoint_edit_timing_path_20261028.json'
    baseline=read(baseline_path)
    assert baseline['audit_sha256']==m['reference_audit_sha256']
    result.update(status='source_bound_static_stage_worst_path_navigation',
                  analyzer_sha256=sha(__file__),
                  parser_sha256=sha(ROOT/'scripts/analyze_route_stage_timing_v2.py'),
                  report_sha256=sha(report),audit_sha256=sha(p/'source_bound_audit.json'),
                  restore_receipt_sha256=sha(files[2]),baseline_analysis_sha256=sha(baseline_path),
                  comparison_to_cp=dict(source=baseline['source'],destination=baseline['destination'],
                      same_endpoint_names=result['source']==baseline['source'] and result['destination']==baseline['destination'],
                      slack_delta_ns=result['slack_ns']-baseline['slack_ns'],
                      logic_level_delta=result['logic_levels']-baseline['logic_levels'],
                      logic_delay_delta_ns=result['logic_delay_ns']-baseline['logic_delay_ns'],
                      estimated_net_delay_delta_ns=result['estimated_net_delay_ns']-baseline['estimated_net_delay_ns']),
                  scope='First worst setup path from actual-restored matched OOC. Count every combinational primitive and unplaced data net. Different endpoints do not establish same-path causality; unplaced estimates do not prove physical timing, board frequency or correctness of an RTL edit.')
    out=ROOT/'results/stage_static_cp_timing_path_20261030.json';assert not out.exists()
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('STATIC_STAGE_WORST_PATH',result['logic_levels'],'levels',result['lut_levels'],'LUTs')
    print(result['source'],'->',result['destination'])
    print('HIERARCHIES',sorted(result['hierarchy_totals'].items(),key=lambda x:x[1]['levels'],reverse=True)[:6])


if __name__=='__main__':main()
