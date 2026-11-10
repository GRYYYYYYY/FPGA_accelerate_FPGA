#!/usr/bin/env python3
"""Audit a frozen two-DCP timing comparison without claiming platform closure."""
import csv
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def summary(path):
    text = path.read_text()
    match = re.search(r'^\s+WNS\(ns\).*\n[^\n]*\n([^\n]+)', text, re.M)
    require(match is not None, f'Missing timing table: {path}')
    fields = match[1].split()
    names = ['wns_ns', 'tns_ns', 'setup_failing_endpoints', 'setup_total_endpoints',
             'whs_ns', 'ths_ns', 'hold_failing_endpoints', 'hold_total_endpoints',
             'wpws_ns', 'tpws_ns', 'pulse_failing_endpoints', 'pulse_total_endpoints']
    require(len(fields) == len(names), f'Incomplete timing table: {path}')
    result = {name: (float(value) if name.endswith('_ns') else int(value))
              for name, value in zip(names, fields)}
    checks = dict(re.findall(r'^\d+\. checking (\w+) \((\d+)\)', text, re.M))
    result['check_timing'] = {name: int(value) for name, value in checks.items()}
    require(result['check_timing'].get('unconstrained_internal_endpoints') == 0,
            'Unconstrained internal timing endpoints')
    require(result['check_timing'].get('no_clock') == 0, 'Unclocked registers')
    return result


def constraints(path):
    return [line.strip() for line in path.read_text().splitlines()
            if line.strip() and not line.lstrip().startswith('#')]


def rules(path):
    result = {}
    for line in path.read_text().splitlines():
        cols = [part.strip() for part in line.split('|')]
        if len(cols) == 6 and re.fullmatch(r'[A-Z0-9]+-\d+', cols[1]):
            result[cols[1]] = {'severity': cols[2], 'description': cols[3], 'count': int(cols[4])}
    return result


def utilization(path):
    result = {}
    wanted = {'CLB LUTs', 'CLB Registers', 'LUT as Logic', 'LUT as Memory',
              'Register as Flip Flop', 'Register as Latch', 'Block RAM Tile',
              'RAMB36/FIFO*', 'RAMB18'}
    for line in path.read_text().splitlines():
        cols = [part.strip() for part in line.split('|')]
        if len(cols) >= 4 and cols[1] in wanted:
            result[cols[1]] = float(cols[2])
    require('CLB LUTs' in result and 'Block RAM Tile' in result, 'Missing resource summary')
    require(result.get('Register as Latch') == 0, 'Unexpected latches')
    return result


def main():
    out = Path(sys.argv[1]).resolve()
    inputs = json.loads((out / 'inputs.json').read_text())
    for item in inputs.values():
        require(digest(ROOT / item['path']) == item['sha256'], f'Changed input: {item}')
    for variant in ['baseline', 'wide']:
        parent = json.loads((ROOT / inputs[variant + '_manifest']['path']).read_text())
        dcp = inputs[variant + '_dcp']
        require(parent['status'] == 'passed', 'Parent verification incomplete')
        require(parent['artifacts'][str(ROOT / dcp['path'])] == dcp['sha256'],
                'DCP not authenticated by parent manifest')
    log = (out / 'session.log').read_text()
    process = json.loads((out / 'process_result.json').read_text())
    require(process['exit_code'] == 0, 'Batch process did not exit successfully')
    source = (ROOT / 'hardware/scripts/implement_codec_pair.tcl').read_text()
    batch = (ROOT / 'hardware/scripts/implement_codec_pair_libc.tcl').read_text()
    require(batch == source.replace(
        'set b_out [file join $b_root results rtl_codec_timing_20261023]',
        'set b_out [file join $b_root results rtl_codec_timing_20261023 libc_batch]') + '\nexit\n',
        'Batch fallback changed the comparison flow')
    require(process['environment_override'] == {'LD_PRELOAD': '/lib/x86_64-linux-gnu/libc.so.6'},
            'Unexpected compatibility environment')
    require(digest(Path(process['environment_override']['LD_PRELOAD'])) == process['preload_sha256'],
            'Changed compatibility library')
    require(log.count('B_CODEC_TIMING_PAIR_DONE\n') == 1, 'Missing unique completion marker')
    require(not re.search(r'^ERROR:', log, re.M), 'Implementation command error')
    require('HD.CLK_SRC' in log, 'Clock model limitation missing from evidence')
    result = {'status': 'completed', 'audit_status': 'passed', 'toolchain': 'Vivado 2022.2',
              'part': 'xcu280-fsvh2892-2L-e', 'period_ns': 10.0,
              'flow': ['opt_design', 'place_design -directive Default', 'route_design -directive Default'],
              'max_threads': 2, 'process': process, 'physical_clock_model_complete': False,
              'platform_timing_closed': False, 'board_performance': None, 'variants': {}}
    expected_constraints = ['create_clock -period 10.000 -name core_clk [get_ports clk]',
                            'current_instance -quiet']
    for variant in ['baseline', 'wide']:
        folder = out / variant
        require((folder / 'routed.dcp').stat().st_size > 10000, 'Missing routed checkpoint')
        done = (folder / 'completed.txt').read_text()
        require(f'B_CODEC_TIMING_VARIANT_DONE {variant} version=2022.2' in done, 'Incomplete variant')
        for phase in ['before', 'after']:
            require(constraints(folder / f'constraints_{phase}.xdc') == expected_constraints,
                    f'Unexpected constraint changes: {variant}/{phase}')
        routed = summary(folder / 'timing_routed.rpt')
        paths = list(csv.DictReader((folder / 'internal_paths.tsv').open(), delimiter='\t'))
        for kind, key in [('max', 'wns_ns'), ('min', 'whs_ns')]:
            selected = [p for p in paths if p['delay_type'] == kind]
            require(len(selected) == 10, f'Missing internal {kind} paths')
            require(all(p['startpoint'] and p['endpoint'] for p in selected), 'Missing path endpoints')
            require(abs(min(float(p['slack_ns']) for p in selected) - routed[key]) <= 0.0011,
                    f'Path and summary disagree: {variant}/{kind}')
        route = (folder / 'route_status.rpt').read_text()
        route_counts = {name.rstrip('. '): int(value) for name, value in
                        re.findall(r'^\s*# of ([^\n:]+?)\s*:\s*(\d+)\s*:\s*$', route, re.M)}
        require(route_counts.get('nets with routing errors') == 0, 'Route errors or absent route report')
        require(route_counts.get('routable nets', 0) > 0 and
                route_counts['routable nets'] == route_counts.get('fully routed nets'),
                'Not all routable nets are fully routed')
        result['variants'][variant] = {
            'synthesized_timing': summary(folder / 'timing_synth.rpt'),
            'routed_timing': routed, 'internal_paths': paths,
            'methodology_synth': rules(folder / 'methodology_synth.rpt'),
            'methodology_routed': rules(folder / 'methodology_routed.rpt'),
            'drc': rules(folder / 'drc_routed.rpt'), 'route_counts': route_counts,
            'utilization': utilization(folder / 'utilization_routed.rpt'),
            'internal_constraints_met_in_this_model': all(routed[k] >= 0 for k in ['wns_ns', 'whs_ns', 'wpws_ns'])}
    cycles = json.loads((ROOT / inputs['wide_manifest']['path']).read_text())['paired_cycles']
    result['simulation_cycles'] = {key: cycles[key] for key in ['baseline', 'wide', 'reduction_fraction', 'same_clock_cycle_ratio']}
    result['scope'] = ('Frozen default-capacity OOC netlists, one deterministic implementation each. '
                       'No HD.CLK_SRC, external IO delays, platform shell, top-level clock-tree integration or board measurement. '
                       'Positive slack is internal data-path evidence only; not Fmax or full platform timing closure.')
    result['inputs'] = inputs
    result['files'] = {str(p.relative_to(ROOT)): digest(p) for p in
                       [Path(__file__).resolve(), ROOT / 'hardware/scripts/implement_codec_pair.tcl',
                        ROOT / 'hardware/scripts/implement_codec_pair_batch.tcl',
                        ROOT / 'hardware/scripts/implement_codec_pair_libc.tcl']}
    result['failed_attempts'] = {
        str(p.relative_to(ROOT)): digest(p) for p in
        [out.parent / 'failed_attempt.json', out.parent / 'failed_mcp_session.log',
         out.parent / 'failed_mcp_stack.log', out.parent / 'batch/process_result.json',
         out.parent / 'batch/session.log', out.parent / 'batch/hs_err_pid2389338.log']}
    result['allocator_probe'] = {
        str(p.relative_to(ROOT)): digest(p) for p in
        [out.parent / 'probe/udev_allocator_probe.c', out.parent / 'probe/udev_allocator_probe',
         out.parent / 'probe/allocator_probe_results.json', out.parent / 'probe/probe.log',
         out.parent / 'probe/params.log', out.parent / 'probe/README.md']}
    artifacts = [p for p in out.rglob('*') if p.is_file() and '.Xil' not in p.parts
                 and p.name not in ['manifest.json', 'completion_audit.json']]
    result['artifacts'] = {str(p.relative_to(out)): digest(p) for p in sorted(artifacts)}
    manifest = out / 'manifest.json'
    manifest.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    audit = {'status': 'passed', 'manifest_sha256': digest(manifest),
             'scope': 'Evidence integrity and consistent extraction, not platform timing closure.'}
    (out / 'completion_audit.json').write_text(json.dumps(audit, indent=2) + '\n')
    print(json.dumps(audit))


if __name__ == '__main__':
    main()
