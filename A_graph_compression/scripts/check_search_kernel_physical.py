#!/usr/bin/env python3
"""Audit the full search kernel's frozen OOC flow; never launches or repairs Vivado."""
import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re

from check_netlist_quality import drc_status, route_status
from check_vitis_kernel import digest, require

ROOT = Path(__file__).resolve().parents[1]
CHECKS = ('no_clock', 'constant_clock', 'pulse_width_clock',
          'unconstrained_internal_endpoints', 'no_input_delay', 'no_output_delay',
          'multiple_clock', 'generated_clocks', 'loops', 'partial_input_delay',
          'partial_output_delay', 'latch_loops')


def coverage(text):
    result = {}
    for name in CHECKS:
        counts = re.findall(r'checking ' + name + r' \((\d+)\)', text)
        require(counts and len(set(counts)) == 1, 'Missing/inconsistent check: ' + name)
        result[name] = int(counts[0])
    return result


def timing(text):
    rows = re.findall(r'^\s*WNS\(ns\)[^\n]*\n[ -]+\n([^\n]+)', text, re.M)
    require(len(rows) == 1, 'Missing/ambiguous complete timing table')
    values = rows[0].split()
    require(len(values) == 12, 'Missing setup/hold/pulse-width fields')
    result = {}
    for i, kind in enumerate(('setup', 'hold', 'pulse_width')):
        slack, total_slack, failing, total = values[i * 4:i * 4 + 4]
        require(all(math.isfinite(float(x)) for x in (slack, total_slack)), 'Nonfinite timing')
        require(failing.isdecimal() and total.isdecimal(), 'Invalid endpoint count')
        require(0 <= int(failing) <= int(total), 'Impossible endpoint count')
        result[kind] = dict(slack_ns=float(slack), total_negative_slack_ns=float(total_slack),
                            failing_endpoints=int(failing), total_endpoints=int(total))
    result['coverage'] = coverage(text)
    clock_section = re.search(r'\| Clock Summary\b(.*?)(?=\n\| [A-Za-z]|\Z)', text, re.S)
    require(clock_section is not None, 'Missing clock summary')
    clocks = re.findall(r'^\s*(\S+)\s+\{([^}]+)\}\s+([\d.]+)\s+([\d.]+)\s*$',
                        clock_section[1], re.M)
    require(len(clocks) == 1, 'Expected exactly one clock')
    name, waveform, period, frequency = clocks[0]
    require(name == 'ap_clk' and float(period) == 5 and float(frequency) == 200,
            'Actual clock differs from frozen 5ns/200MHz target')
    require([float(x) for x in waveform.split()] == [0, 2.5], 'Unexpected clock waveform')
    result['clock'] = dict(name=name, period_ns=float(period), frequency_mhz=float(frequency))
    return result


def utilization(text, top='search_kernel_top'):
    rows = [[x.strip() for x in line.strip().split('|')[1:-1]]
            for line in text.splitlines() if line.strip().startswith('|')]
    headers = [r for r in rows if r[:2] == ['Instance', 'Module']]
    require(len(headers) == 1, 'Missing/ambiguous utilization header')
    header = headers[0]
    selected = [r for r in rows if len(r) == len(header) and r[:2] == [top, '(top)']]
    require(len(selected) == 1, 'Missing/ambiguous full-top utilization')
    require(all(v.isdecimal() for v in selected[0][2:]), 'Invalid utilization values')
    counts = dict(zip(header[2:], map(int, selected[0][2:])))
    require({'Total LUTs', 'Logic LUTs', 'LUTRAMs', 'SRLs', 'FFs', 'RAMB36', 'RAMB18',
             'URAM', 'DSP Blocks'} <= counts.keys(), 'Missing resource class')
    require(counts['Total LUTs'] > 0 and counts['FFs'] > 0, 'Empty implementation')
    return counts


def quality_gates(t, r, d, methodology):
    internal = {k: v for k, v in t['coverage'].items()
                if k not in ('no_input_delay', 'no_output_delay')}
    return dict(
        internal_timing_met=all(x['slack_ns'] >= 0 and x['total_negative_slack_ns'] == 0
                               and x['failing_endpoints'] == 0 and x['total_endpoints'] > 0
                               for x in (t['setup'], t['hold'], t['pulse_width'])),
        internal_constraint_checks_clear=all(v == 0 for v in internal.values()),
        all_nets_routed=(r['routable nets'] > 0 and r['fully routed nets'] == r['routable nets']
                         and r['nets with routing errors'] == 0),
        no_drc_violations=d['total'] == 0,
        no_methodology_violations=methodology['total'] == 0)


def session_gate(snapshot, job, state, work, started):
    require(snapshot['session_id'] == job['session_id'], 'Wrong MCP session')
    status = snapshot['status']
    observed = datetime.fromisoformat(snapshot['observed_utc'].replace('Z', '+00:00'))
    completed = datetime.fromisoformat(state['updated_utc'].replace('Z', '+00:00'))
    require(observed.tzinfo is not None and observed >= completed, 'Stale MCP observation')
    require(state['status'] == 'complete' and state['stage'] == 'ooc_complete_pending_independent_audit'
            and state['mode'] == job['mode'], 'Physical flow not complete')
    require(status.get('is_command_running') is False and status.get('last_completed_code') == 0
            and status.get('queue_length') == 0, 'MCP flow still running, failed or queued')
    require(status['process_id'] == state['owner_pid'] == started['process_id'], 'Owner changed')
    require(Path(status['working_dir']).resolve() == work, 'Wrong MCP working directory')
    require(Path(status['log_file']).resolve() == Path(started['log']).resolve(), 'Wrong session log')
    command = status.get('last_completed', '')
    # MCP truncates last_completed for display. The raw log below binds the full source command.
    prefix = command[:-3] if command.endswith('...') else command
    require(len(prefix) > 20 and job['source_command'].startswith(prefix), 'Wrong completed command')
    require('SEARCH_PHYSICAL_FLOW_COMPLETE' in status.get('last_completed_output', ''),
            'Missing MCP flow completion output')


def constraints(text):
    active = '\n'.join(line for line in text.splitlines() if not line.lstrip().startswith('#'))
    require(not re.search(r'\b(?:set_false_path|set_multicycle_path|set_max_delay|set_min_delay|'
                          r'set_disable_timing|set_clock_groups|create_waiver)\b', active),
            'Timing exceptions/waivers require separate review')
    uncertainty = re.findall(r'^\s*set_clock_uncertainty\s+-setup\s+([\d.]+)\s+'
                             r'\[get_clocks\s+\{?ap_clk\}?\]\s*$', active, re.M)
    require(len(uncertainty) == 1 and float(uncertainty[0]) == 1.35,
            'Written setup uncertainty differs from 1.35ns')
    require(len(re.findall(r'^\s*create_clock\b', active, re.M)) == 1, 'Wrong clock constraints')


def summary(text, t):
    words = text.split()
    require(len(words) == 12, 'Unexpected Tcl summary')
    values = dict(zip(words[::2], words[1::2]))
    require(set(values) == {'version', 'part', 'clock_period', 'setup_slack', 'hold_slack', 'cells'},
            'Missing/duplicate summary keys')
    require(values['version'] == '2022.2' and values['part'] == 'xcu280-fsvh2892-2L-e'
            and float(values['clock_period']) == 5 and int(values['cells']) > 0,
            'Wrong tool/part/clock or empty netlist')
    for kind in ('setup', 'hold'):
        value = float(values[kind + '_slack'])
        require(math.isfinite(value) and abs(value - t[kind]['slack_ns']) <= 0.0011,
                'Path-query/report slack mismatch')
    return values


def audit(bundle, session_path):
    bundle = bundle.resolve()
    plan_path = bundle / 'plan.json'
    plan = json.loads(plan_path.read_text())
    start_path = bundle / 'observation_0001.json'
    start = json.loads(start_path.read_text())
    require(digest(plan_path) == start['plan_sha256'], 'Physical plan changed')
    require(plan['part'] == 'xcu280-fsvh2892-2L-e' and plan['clock_ns'] == 5
            and plan['setup_uncertainty_ns'] == 1.35 and plan['vivado_version'] == '2022.2',
            'Wrong frozen physical target')
    snapshots = json.loads(session_path.read_text())
    require(set(snapshots) == {'csr', 'compact'}, 'Missing mode MCP observation')
    require(sorted(j['mode'] for j in plan['jobs']) == ['compact', 'csr'], 'Wrong mode matrix')
    # Fail promptly while running, before hashing large completed artifacts.
    for job in plan['jobs']:
        mode = job['mode']; work = bundle / mode
        state = json.loads((work / 'state.json').read_text())
        original = [v for v in start['observations'] if v['mode'] == mode]
        require(len(original) == 1, 'Missing/duplicate submission observation')
        session_gate(snapshots[mode], job, state, work, original[0])
    files = {}
    def bind(path):
        path = Path(path); files[str(path)] = digest(path)
    for group in ('inputs', 'generated'):
        for name, sha in plan[group].items():
            require(digest(name) == sha, 'Changed frozen physical input: ' + name)
            files[name] = sha
    for path in (plan_path, start_path, session_path, Path(__file__).resolve(),
                 ROOT / 'scripts/check_netlist_quality.py', ROOT / 'scripts/check_vitis_kernel.py'):
        bind(path)
    modes = {}
    for job in plan['jobs']:
        mode = job['mode']; work = bundle / mode; reports = work / 'reports'
        source = work / 'source'
        original = ROOT / 'build/search_kernel_hls_20261024_v3' / mode / 'solution/syn/verilog'
        actual = {p.name: p for p in source.iterdir() if p.suffix in ('.v', '.dat')}
        reference = {p.name: p for p in original.iterdir() if p.suffix in ('.v', '.dat')}
        require(actual.keys() == reference.keys() and len(actual) == job['rtl_files'] + job['rom_files'],
                'RTL/ROM set changed')
        for name, path in actual.items():
            require(digest(path) == digest(reference[name]), 'RTL/ROM content differs')
        require(not (work / 'error.txt').exists(), 'Physical flow has an error receipt')
        log_path = Path(snapshots[mode]['status']['log_file'])
        log = log_path.read_text(errors='replace')
        require(job['source_command'] in log, 'Full source command not bound in session log')
        require(len(re.findall(r'^SEARCH_PHYSICAL_FLOW_COMPLETE[ \t]*$', log, re.M)) == 1,
                'Missing/duplicate flow completion in log')
        # Earlier interactive help errors are retained; only inspect this flow's log segment.
        run_log = log[log.index('SEARCH_PHYSICAL_STAGE ' + mode + ' running prepare'):]
        require(not re.search(r'^ERROR:', run_log, re.M), 'Flow log contains an error')
        require('Got license for feature' in run_log and "device 'xcu280'" in run_log,
                'Missing actual device synthesis license checkout')
        for path in (work / 'state.json', log_path): bind(path)
        for name in ('synthesized.dcp', 'placed.dcp', 'routed.dcp'):
            path = work / name
            require(path.is_file() and path.stat().st_size > 0, 'Missing checkpoint: ' + name)
            bind(path)
        stages = {}
        for stage in ('synthesis', 'routed'):
            paths = {name: reports / (stage + '_' + name) for name in
                     ('timing.rpt', 'check_timing.rpt', 'utilization.rpt', 'drc.rpt',
                      'methodology.rpt', 'timing.xdc', 'summary.tcllist', 'methodology_properties.tcllist')}
            for path in paths.values(): bind(path)
            texts = {key: path.read_text() for key, path in paths.items()}
            for name in ('timing.rpt', 'utilization.rpt', 'drc.rpt', 'methodology.rpt'):
                require(re.search(r'\| Design\s*:\s*search_kernel_top\s*$', texts[name], re.M),
                        'Report belongs to a different design: ' + name)
                require('Vivado v.2022.2' in texts[name] and 'xcu280-fsvh2892' in texts[name],
                        'Wrong report tool/device: ' + name)
            t = timing(texts['timing.rpt'])
            require(t['coverage'] == coverage(texts['check_timing.rpt']), 'Coverage reports disagree')
            constraints(texts['timing.xdc'])
            stages[stage] = dict(timing=t, summary=summary(texts['summary.tcllist'], t),
                                 resources=utilization(texts['utilization.rpt']),
                                 drc=drc_status(paths['drc.rpt']),
                                 methodology=drc_status(paths['methodology.rpt']))
            if stage == 'routed':
                require(re.search(r'\| Design State\s*:\s*(?:Fully )?Routed\s*$',
                                  texts['utilization.rpt'], re.M), 'Resources are not post-route')
        route_path = reports / 'route_status.rpt'; bind(route_path)
        routed = stages['routed']; r = route_status(route_path)
        gates = quality_gates(routed['timing'], r, routed['drc'], routed['methodology'])
        modes[mode] = dict(stages=stages, route=r, quality_gates=gates,
                           external_io_timing_complete=False, platform_timing_verified=False)
    passed = all(all(m['quality_gates'].values()) for m in modes.values())
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),
                status=('full_search_ooc_all_quality_gates_verified' if passed
                        else 'full_search_ooc_completed_with_quality_failures_or_review_required'),
                all_quality_gates_pass=passed, modes=modes, files=files,
                functional_rtl_verified_by_this_audit=False, board_verified=False,
                limitations=plan['limitations'] + [
                    'Methodology warnings are retained and make the all-quality gate false; no implicit waivers.',
                    'DCPs are bound by digest; this audit does not reopen or simulate them.',
                    'External IO coverage remains outside this bare-device OOC characterization.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--session-status', type=Path, required=True,
                        help='JSON mode -> {session_id, observed_utc, status: raw MCP session status}')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'Refusing to overwrite existing physical audit')
    report = audit(args.bundle, args.session_status)
    with args.output.open('x') as stream:
        json.dump(report, stream, indent=2); stream.write('\n')
    print(json.dumps(dict(status=report['status'], output=str(args.output))))
    return 0 if report['all_quality_gates_pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
