"""Audit implementation provenance and reports independently of the execution driver."""
from pathlib import Path
import csv
import json
import re
import sys
from run_checkpoint_authority import ROOT, sha


def utilization(path):
    text = path.read_text()
    values = {}
    for key, label in [('LUT','CLB LUTs*'), ('FF','CLB Registers'), ('BRAM','Block RAM Tile'),
                       ('DSP','DSPs'), ('URAM','URAM'), ('latches','Register as Latch')]:
        match = re.search(r'^\|\s*'+re.escape(label).replace(r'\*',r'\*?')+r'\s*\|\s*([\d,.]+)\s*\|', text, re.M)
        assert match, (path, label)
        values[key] = float(match[1].replace(',', ''))
    return values


def timing_summary(path):
    text = path.read_text()
    block = text.split('Design Timing Summary', 1)[1].split('Clock Summary', 1)[0]
    rows = [line.split() for line in block.splitlines()]
    rows = [row for row in rows if len(row)==12 and re.fullmatch(r'-?\d+\.\d+',row[0])]
    assert len(rows)==1, path
    row = rows[0]
    return dict(WNS_ns=float(row[0]), TNS_ns=float(row[1]), WHS_ns=float(row[4]), THS_ns=float(row[5]),
                failing_endpoints=dict(setup=int(row[2]), hold=int(row[6]), pulse_width=int(row[10])),
                endpoint_counts=dict(setup=int(row[3]), hold=int(row[7]), pulse_width=int(row[11])))


def route_status(path):
    text = path.read_text()
    result = {}
    for label in ['routable nets', 'fully routed nets', 'nets with routing errors']:
        match = re.search(r'# of '+label+r'\.*\s*:\s*(\d+)', text)
        assert match, (path,label)
        result[label] = int(match[1])
    return result


def main():
    p = Path(sys.argv[1]).resolve()
    m = json.loads((p/'manifest.json').read_text())
    assert m['status'] == 'observed' and m['exit_code'] == 0
    assert sha(p/'runner.py') == m['runner_sha256'] == sha(ROOT/'scripts/run_state_ooc_physical.py')
    assert sha(p/'run.tcl') == m['tcl_sha256']
    template = ROOT/'hardware/scripts/implement_state_ooc.tcl'
    assert sha(template) == m['template_sha256'] == sha(p/'tools/implement_state_ooc.tcl')
    assert (p/'run.tcl').read_text() == template.read_text().replace('@OUT@', str(p))
    assert sha(ROOT/'scripts/prepare_state_ooc_physical.py') == m['preparer_sha256']
    for name, digest in {**m['inputs'], **m['artifact_sha256']}.items():
        assert sha(p/name) == digest, name
    ref = Path(m['reference'])
    original = json.loads((p/'inputs/synthesis_audit.json').read_text())
    rm = json.loads((p/'inputs/synthesis_manifest.json').read_text())
    receipt = json.loads((p/'inputs/synthesis_restoration.json').read_text())
    assert original['status'] == receipt['status'] == 'passed' and receipt['audit_byte_identical']
    assert rm['status'] == 'observed' and rm['exit_code'] == 0
    assert original['manifest_sha256'] == sha(p/'inputs/synthesis_manifest.json')
    assert receipt['audit_sha256'] == sha(p/'inputs/synthesis_audit.json') == m['synthesis_audit_sha256']
    assert sha(ref/'source_bound_audit.json') == m['synthesis_audit_sha256']
    assert original['artifact_sha256']['synth.dcp'] == sha(p/'inputs/synthesized.dcp')
    assert original['check_timing_counts']['loops'] == 0 and not original['timing_loop_warnings']
    assert not original['critical_warnings']
    assert m['rtl'] == rm['rtl'] and len(m['rtl']) == 133
    assert m['parameters'] == rm['parameters'] and m['part'] == rm['part'] == 'xcu280-fsvh2892-2L-e'
    full = Path(m['full_system_reference'])
    fa = json.loads((p/'inputs/full_system_audit.json').read_text())
    fr = json.loads((p/'inputs/full_system_restoration.json').read_text())
    assert fa['status'] == fr['status'] == 'passed' and fr['audit_byte_identical']
    assert fr['audit_sha256'] == sha(p/'inputs/full_system_audit.json') == m['full_system_audit_sha256']
    assert sha(full/'source_bound_audit.json') == m['full_system_audit_sha256']
    assert len(fa['exact_comparisons']) == 27
    for name in m['rtl']:
        assert sha(p/'sources'/name) == rm['sources'][name] == sha(full/'sources'/name), name
    assert (p/'inputs/clock.xdc').read_text() == 'create_clock -name core_clk -period 10.000 [get_ports clk]\n'
    for stage in ['input','routed']:
        constraints = (p/f'constraints_{stage}.xdc').read_text()
        assert re.search(r'create_clock -period 10\.000 -name core_clk\b',constraints)
        assert not any(command in constraints for command in ['set_input_delay','set_output_delay','set_false_path','set_multicycle_path','HD.CLK_SRC'])
        assert re.search(r'^core_clk\s+10\.000\b',(p/f'clocks_{stage}.rpt').read_text(),re.M)
    done = (p/'completed.txt').read_text()
    assert 'STATE_FULL_PHYSICAL_DONE version=2022.2 part=xcu280-fsvh2892-2L-e period=10.' in done
    log = (p/'vivado.log').read_text()
    assert 'STATE_FULL_PHYSICAL_DONE' in log and not re.search(r'^ERROR:',log,re.M)
    routed = route_status(p/'route_status.rpt')
    assert routed['routable nets'] > 0
    complete_route = (routed['routable nets']==routed['fully routed nets'] and routed['nets with routing errors']==0)
    summaries = {stage:timing_summary(p/f'timing_{stage}.rpt') for stage in ['placed','routed']}
    resources = {stage:utilization(p/f'utilization_{stage}.rpt') for stage in ['input','placed','routed']}
    assert all(resources['input'][k] == original['utilization'][k] for k in resources['input'])
    text = (p/'timing_routed.rpt').read_text()
    assert 'xcu280-fsvh2892' in text and 'Speed File        : -2L' in text and 'Temperature Grade : E' in text
    checks = {}
    methodology = {}
    for stage in ['input','routed']:
        checks[stage] = {k:int(n) for k,n in re.findall(r'^\d+\. checking (\w+) \((\d+)\)',(p/f'check_timing_{stage}.rpt').read_text(),re.M)}
        assert all(k in checks[stage] for k in ['no_clock','unconstrained_internal_endpoints','loops','latch_loops','no_input_delay','no_output_delay'])
        rows = re.findall(r'^\|\s*([A-Z]+-\d+)\s*\|\s*([^|]+)\|[^|]+\|\s*(\d+)\s*\|',(p/f'methodology_{stage}.rpt').read_text(),re.M)
        methodology[stage] = {rule:dict(severity=severity.strip(),count=int(n)) for rule,severity,n in rows}
    drc_match = re.search(r'Violations found:\s*(\d+)',(p/'drc_routed.rpt').read_text())
    assert drc_match
    drc_count = int(drc_match[1])
    with (p/'internal_paths.tsv').open() as handle:
        paths = list(csv.DictReader(handle,delimiter='\t'))
    max_paths = [x for x in paths if x['delay_type']=='max']
    min_paths = [x for x in paths if x['delay_type']=='min']
    assert len(paths)==20 and len(max_paths)==len(min_paths)==10
    assert all(float(x['requirement_ns'])==10 for x in max_paths)
    assert all(float(x['requirement_ns'])==0 for x in min_paths)
    setup = min(float(x['slack_ns']) for x in max_paths)
    hold = min(float(x['slack_ns']) for x in min_paths)
    qualified_checks = all(checks['routed'][k]==0 for k in ['no_clock','unconstrained_internal_endpoints','loops','latch_loops'])
    summary = summaries['routed']
    critical = [line for line in log.splitlines() if line.startswith('CRITICAL WARNING:')]
    internal_met = (complete_route and drc_count==0 and qualified_checks and resources['routed']['latches']==0
                    and setup>=0 and hold>=0 and summary['WNS_ns']>=0 and summary['WHS_ns']>=0
                    and not critical and all(n==0 for n in summary['failing_endpoints'].values()))
    result = dict(status='passed', audit_kind='physical artifact integrity and observations, not platform acceptance',
                  manifest_sha256=sha(p/'manifest.json'), auditor_sha256=sha(Path(__file__)),
                  synthesis_audit_sha256=m['synthesis_audit_sha256'], full_system_audit_sha256=m['full_system_audit_sha256'],
                  route=routed, complete_route=complete_route, drc_violation_count=drc_count,
                  resources=resources, timing_summaries=summaries, timing_checks=checks, methodology=methodology,
                  sampled_internal_setup_slack_ns=setup, sampled_internal_hold_slack_ns=hold,
                  internal_paths=paths, constrained_internal_10ns_setup_hold_met=internal_met,
                  critical_warnings=critical,
                  timing_qualified=False, board_acceptance=False, full_behavior_matrix_complete=False,
                  artifact_sha256=m['artifact_sha256'], scope=m['scope'],
                  limitations=['Original research clock only; external I/O budgets and physical clock-source location remain unspecified.',
                               'One default placement/routing per input checkpoint; no seed or frequency sweep.',
                               'No post-route functional simulation, new eight-case behavior matrix, board timing or acceleration proof.'])
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('STATE_FULL_PHYSICAL_AUDITED', p.name, 'route_complete', complete_route,
          'WNS', summary['WNS_ns'], 'WHS', summary['WHS_ns'], 'internal_met', internal_met)


if __name__ == '__main__':
    main()
