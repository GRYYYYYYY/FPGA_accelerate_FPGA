"""Independent provenance and report audit for fresh static-stage physical artifacts."""
from pathlib import Path
import csv
import json
import re
import sys
from check_stage_static_cp_physical_inputs_v4 import evidence
from prepare_stage_static_cp_physical_v4 import OUTPUT
from check_stage_static_cp_physical_inputs_v4 import ROOT, TARGET, FULL
from config_native_publication_synth_common_v1 import sha, read, identity, runtime_environment
from audit_state_ooc_physical_v2 import utilization, timing_summary, route_status
from audit_state_route_recovery_v2 import commands, checks, methodology, drc
from parse_state_timing_paths import parse_report


def report_evidence(p):
    """Parse actual reports, retaining timing failures independently of provenance."""
    original = commands(p/'constraints_input.xdc')
    assert 'create_clock -period 10.000 -name core_clk [get_ports clk]' in original
    for name in ['constraints_input.xdc', 'constraints_routed.xdc', 'inspection/constraints.xdc']:
        assert commands(p/name) == original
        assert not any(x in (p/name).read_text() for x in
            ['set_input_delay', 'set_output_delay', 'set_false_path', 'set_multicycle_path',
             'HD.CLK_SRC', 'HD.PARTPIN_LOCS'])
    for name in ['clocks_input.rpt', 'clocks_routed.rpt']:
        assert re.search(r'^core_clk\s+10\.000\b', (p/name).read_text(), re.M)
    route = route_status(p/'route_status.rpt')
    assert route == route_status(p/'inspection/route_status.rpt')
    assert route['routable nets'] > 0
    complete = route['routable nets'] == route['fully routed nets'] and route['nets with routing errors'] == 0
    resources = {stage: utilization(p/name) for stage, name in [
        ('input', 'utilization_input.rpt'), ('placed', 'utilization_placed.rpt'),
        ('routed', 'utilization_routed.rpt'), ('reopened', 'inspection/utilization.rpt')]}
    assert resources['routed'] == resources['reopened']
    timings = {stage: timing_summary(p/name) for stage, name in [
        ('placed', 'timing_placed.rpt'), ('routed', 'timing_routed.rpt'), ('reopened', 'inspection/timing.rpt')]}
    assert timings['routed'] == timings['reopened']
    parsed = {stage: parse_report((p/name).read_text(), 'core_clk') for stage, name in [
        ('routed', 'timing_routed.rpt'), ('reopened', 'inspection/timing.rpt')]}
    fields = ['path_type', 'source', 'destination', 'slack_ns', 'logic_levels',
              'data_delay_ns', 'logic_delay_ns', 'net_delay_ns', 'net_placement_counts']
    assert [{k: x[k] for k in fields} for x in parsed['routed']] == [
        {k: x[k] for k in fields} for x in parsed['reopened']]
    tc = {stage: checks(p/name) for stage, name in [('input', 'check_timing_input.rpt'),
        ('routed', 'check_timing_routed.rpt'), ('reopened', 'inspection/check_timing.rpt')]}
    assert tc['routed'] == tc['reopened']
    methods = {stage: methodology(p/name) for stage, name in [('input', 'methodology_input.rpt'),
        ('routed', 'methodology_routed.rpt'), ('reopened', 'inspection/methodology.rpt')]}
    assert methods['routed'] == methods['reopened']
    violations = drc(p/'drc_routed.rpt')
    assert violations == drc(p/'inspection/drc.rpt')
    with (p/'internal_paths.tsv').open() as handle:
        paths = list(csv.DictReader(handle, delimiter='\t'))
    assert len(paths) == 20
    worst = {}
    for dtype, kind, key, period in [('max', 'Setup', 'WNS_ns', 10), ('min', 'Hold', 'WHS_ns', 0)]:
        selected = [x for x in paths if x['delay_type'] == dtype]
        assert len(selected) == 10 and all(float(x['requirement_ns']) == period for x in selected)
        worst[dtype] = min(float(x['slack_ns']) for x in selected)
        assert worst[dtype] == timings['routed'][key]
        literal = min((x for x in parsed['routed'] if x['path_type'] == kind), key=lambda x: x['slack_ns'])
        assert literal['slack_ns'] == worst[dtype]
        assert any(x['startpoint'] == literal['source'] and x['endpoint'] == literal['destination']
                   and float(x['slack_ns']) == worst[dtype] for x in selected)
    critical = [line for name in ['stdout.log', 'inspection/stdout.log']
                for line in (p/name).read_text().splitlines() if line.startswith('CRITICAL WARNING:')]
    qualified = all(tc['routed'][k] == 0 for k in ['no_clock', 'unconstrained_internal_endpoints', 'loops', 'latch_loops'])
    met = (complete and violations == 0 and qualified and resources['routed']['latches'] == 0
           and worst['max'] >= 0 and worst['min'] >= 0 and not critical
           and all(n == 0 for n in timings['routed']['failing_endpoints'].values()))
    return dict(route=route, complete_route=complete, resources=resources, timing_summaries=timings,
        timing_checks=tc, methodology=methods, drc_violation_count=violations, internal_paths=paths,
        sampled_internal_setup_slack_ns=worst['max'], sampled_internal_hold_slack_ns=worst['min'],
        constrained_internal_10ns_setup_hold_met=met, critical_warnings=critical)


def main():
    p = Path(sys.argv[1]).resolve()
    assert p == OUTPUT
    proof = evidence()
    m = read(p/'manifest.json'); im = read(p/'inspection/manifest.json')
    assert m['status'] == 'observed' and m['exit_code'] == 0
    assert m['stage'] == 'implementation_complete_pending_independent_inspection'
    assert identity(m['runner_pid']) != str(m['runner_start_ticks']) and not m.get('active_process')
    assert [x['stage'] for x in m['commands']] == ['version', 'implementation']
    assert all(x['exit_code'] == 0 for x in m['commands'])
    assert sha(p/'runner.py') == m['runner_sha256'] == sha(ROOT/'scripts/run_stage_static_cp_physical_v2.py')
    assert m['preparer_sha256'] == sha(ROOT/'scripts/prepare_stage_static_cp_physical_v4.py')
    for name, digest in proof.items():
        assert m['external_evidence_sha256'][name] == digest
    for name, digest in m['external_evidence_sha256'].items(): assert sha(name) == digest
    for name, digest in {**m['inputs'], **m['artifact_sha256']}.items(): assert sha(p/name) == digest
    template = ROOT/'hardware/scripts/implement_state_ooc.tcl'
    assert sha(template) == m['template_sha256']
    assert (p/'run.tcl').read_text() == template.read_text().replace('@OUT@', str(p))
    assert im['status'] == 'observed' and im['stage'] == 'complete' and im['exit_code'] == 0
    assert identity(im['inspector_pid']) != str(im['inspector_start_ticks']) and not im.get('active_process')
    assert im['implementation_manifest_sha256'] == sha(p/'manifest.json')
    assert im['inspector_sha256'] == sha(ROOT/'scripts/inspect_stage_static_cp_physical_v2.py')
    template = ROOT/'hardware/scripts/inspect_state_route_v1.tcl'
    assert im['template_sha256'] == sha(template)
    assert (p/'inspection/inspect.tcl').read_text() == template.read_text().replace('@OUT@', str(p))
    for name, digest in im['artifact_sha256'].items(): assert sha(p/'inspection'/name) == digest
    assert sha(p/'routed.dcp') == im['routed_checkpoint_sha256']
    assert runtime_environment()[1] == m['runtime'] == im['runtime']
    rm = read(TARGET/'manifest.json'); sa = read(TARGET/'source_bound_audit.json')
    assert m['reference'] == str(TARGET) and m['full_system_reference'] == str(FULL)
    assert m['rtl'] == rm['rtl'] and m['parameters'] == rm['parameters'] and m['part'] == rm['part']
    assert sha(p/'inputs/synthesized.dcp') == sa['artifact_sha256']['synth.dcp']
    for name in m['rtl']: assert sha(p/'sources'/name) == rm['sources'][name]
    assert (p/'inputs/clock.xdc').read_text() == 'create_clock -name core_clk -period 10.000 [get_ports clk]\n'
    assert 'Vivado v2022.2' in (p/'version.stdout.log').read_text()
    for name, marker in [('stdout.log', 'STATE_FULL_PHYSICAL_DONE'),
                         ('inspection/stdout.log', 'STATE_ROUTE_RECOVERY_REOPENED')]:
        text = (p/name).read_text(); assert marker in text and not re.search(r'^ERROR:', text, re.M)
    assert 'STATE_FULL_PHYSICAL_DONE version=2022.2 part=xcu280-fsvh2892-2L-e period=10.' in (p/'completed.txt').read_text()
    reports = report_evidence(p)
    assert reports['resources']['input'] == sa['utilization']
    parsers = ['audit_state_ooc_physical_v2.py', 'audit_state_route_recovery_v2.py', 'parse_state_timing_paths.py']
    result = dict(status='passed', audit_kind='fresh static-stage physical artifacts and independent routed DCP reopen',
        manifest_sha256=sha(p/'manifest.json'), inspection_manifest_sha256=sha(p/'inspection/manifest.json'),
        auditor_sha256=sha(Path(__file__)), parser_sha256={name: sha(ROOT/'scripts'/name) for name in parsers},
        artifact_sha256=m['artifact_sha256'], inspection_artifact_sha256=im['artifact_sha256'],
        independent_reopened_dcp_matches=True, **reports, timing_qualified=False, board_acceptance=False,
        full_behavior_matrix_complete=False, scope=m['scope'],
        limitations=['Unspecified platform IO budgets and clock locations.',
                     'Passing artifact audit does not imply setup/hold closure or all DRC checks passed.',
                     'No new static-stage eight-case matrix, post-route functional simulation or board result.'])
    (p/'source_bound_audit.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print('STATIC_STAGE_PHYSICAL_AUDITED', reports['complete_route'], reports['timing_summaries']['routed'])


if __name__ == '__main__': main()
