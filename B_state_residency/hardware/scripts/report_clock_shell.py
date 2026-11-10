"""Audit clock-shell semantics, clock routing, IO coverage and measured slack."""
import csv
import json
from pathlib import Path
import re
import sys
import tempfile
from make_clock_shell import generate
from report_codec_timing import digest, require, rules, summary, utilization

ROOT = Path(__file__).resolve().parents[2]


def main():
    out = Path(sys.argv[1]).resolve()
    inputs = json.loads((out / 'inputs.json').read_text())
    for name, expected in inputs['files'].items():
        require(digest(ROOT / name) == expected, 'Changed source: ' + name)
        require(digest(out / 'sources' / name) == expected, 'Changed snapshot: ' + name)
    parents = {}
    for name, expected in inputs['parents'].items():
        require(digest(ROOT / name) == expected, 'Changed parent: ' + name)
        parents[name] = json.loads((ROOT / name).read_text())
    prior = {'baseline': parents['results/rtl_memory_endpoint_20261023/manifest.json'],
             'wide': parents['results/rtl_wide_codec_20261023/manifest.json']}
    for variant, parent in prior.items():
        require(parent['status'] == 'passed', 'Prior semantic verification incomplete')
    vector_manifest = ROOT / 'results/rtl_memory_endpoint_20261023/vectors/manifest.json'
    require(digest(vector_manifest) == prior['baseline']['artifacts'][str(vector_manifest)],
            'Changed vector manifest')
    vectors = json.loads(vector_manifest.read_text())
    require(vectors['status'] == 'passed', 'Vector generation incomplete')
    for name, expected in vectors['files'].items():
        require(digest(Path(name)) == expected, 'Changed vector input: ' + name)
    for name, expected in inputs['files'].items():
        if name.startswith('hardware/rtl/') and 'clock_shell' not in name:
            require(any(p['files'].get(str(ROOT / name)) == expected for p in prior.values()),
                    'Endpoint RTL not authenticated by a prior manifest: ' + name)
    with tempfile.TemporaryDirectory() as tmp:
        generate(Path(tmp))
        for path in Path(tmp).rglob('*.sv'):
            require(path.read_bytes() == (out / 'sources' / path.relative_to(tmp)).read_bytes(),
                    'Wrapper or TB changed beyond mechanical transform')
    env = json.loads((out / 'session_environment.json').read_text())
    require(env['LD_PRELOAD'] == '/lib/x86_64-linux-gnu/libc.so.6', 'Unexpected allocator override')
    require(digest(Path(env['LD_PRELOAD'])) == env['libc_sha256'], 'Allocator library changed')
    completion = json.loads((out / 'implementation_completion.json').read_text())
    require(completion['exit_code'] == 0, 'Implementation did not return success')
    log = (out / 'implementation_session.log').read_text()
    require(log.count('\nB_CLOCK_SHELL_PAIR_DONE\n') == 1, 'Missing unique pair completion marker')
    require(not re.search(r'^ERROR:', log, re.M), 'Implementation command error')
    require('HD.CLK_SRC' not in log, 'Clock source still incomplete')
    sims = json.loads((out / 'simulation/manifest.json').read_text())
    require(sims['status'] == 'completed' and len(sims['cases']) == 4, 'Missing semantic regressions')
    sim_results = {}
    for name, case in sims['cases'].items():
        require(case['status'] == 'passed' and len(case['commands']) == 3, 'Incomplete simulation')
        require(all(c['exit_code'] == 0 for c in case['commands']), 'Simulator tool error')
        variant, size = name.split('_')
        text = (out / 'simulation' / name / 'simulate.log').read_text()
        require('Fatal:' not in text and text.count('TEST_PASS memory_endpoint ') == 1, 'Bad test outcome')
        match = re.search(r'^TEST_PASS memory_endpoint (.+)$', text, re.M)
        counters = {key: int(value) for key, value in re.findall(r'(\w+)=(\d+)', match[1])}
        reference = prior[variant]['simulation'][size + ('_final' if variant == 'baseline' else '')]
        require(counters == {k: v for k, v in reference.items() if k != 'end_time_ns'},
                'Semantic count changed: ' + name)
        end = re.search(r'\$finish called at time : (\d+) ns', text)
        require(end is not None, 'No simulation termination')
        end_ns = int(end[1])
        expected_ns = reference.get('end_time_ns', {'small': 820130, 'actual': 105164880}[size])
        require(end_ns == expected_ns, 'Clock wrapper changed simulation cycles: ' + name)
        sim_results[name] = dict(counters, end_time_ns=end_ns)
    result = {'status': 'completed', 'audit_status': 'passed', 'toolchain': 'Vivado/XSim 2022.2',
              'part': inputs['part'], 'model': inputs, 'simulation': sim_results, 'variants': {},
              'platform_timing_closed': False, 'board_performance': None, 'environment': env,
              'vectors': {'manifest_sha256': digest(vector_manifest), 'files': vectors['files']}}
    for variant in ['baseline', 'wide']:
        folder = out / variant
        require((folder / 'completed.txt').read_text().strip() ==
                f'B_CLOCK_SHELL_VARIANT_DONE {variant} version=2022.2', 'Missing variant completion')
        require((folder / 'routed.dcp').stat().st_size > 10000, 'Missing routed checkpoint')
        timing = summary(folder / 'timing_routed.rpt')
        for check in ['no_input_delay', 'no_output_delay', 'partial_input_delay', 'partial_output_delay']:
            require(timing['check_timing'][check] == 0, 'Uncovered IO constraint: ' + check)
        clock = list(csv.DictReader((folder / 'clock_network.tsv').open(), delimiter='\t'))
        require(len(clock) == 1 and clock[0]['type'] == 'BUFGCE', 'Expected one physical clock buffer')
        require(clock[0]['location'].startswith('BUFGCE_'), 'Clock buffer unplaced')
        require(clock[0]['route_status'] == 'ROUTED', 'Clock network not routed')
        paths = list(csv.DictReader((folder / 'paths.tsv').open(), delimiter='\t'))
        groups = {}
        for group in ['internal', 'input', 'output', 'feedthrough']:
            groups[group] = {}
            for delay, key in [('max', 'setup'), ('min', 'hold')]:
                selected = [p for p in paths if p['group'] == group and p['delay_type'] == delay]
                require(selected and all(p['startpoint'] and p['endpoint'] for p in selected),
                        'Missing path group: ' + group + '/' + delay)
                groups[group][key] = min(float(p['slack_ns']) for p in selected)
        require(abs(min(v['setup'] for v in groups.values()) - timing['wns_ns']) <= .0011,
                'Setup path groups disagree with summary')
        require(abs(min(v['hold'] for v in groups.values()) - timing['whs_ns']) <= .0011,
                'Hold path groups disagree with summary')
        route = (folder / 'route_status.rpt').read_text()
        route_counts = {name.rstrip('. '): int(value) for name, value in
                        re.findall(r'^\s*# of ([^\n:]+?)\s*:\s*(\d+)\s*:\s*$', route, re.M)}
        require(route_counts.get('nets with routing errors') == 0, 'Route errors')
        require(route_counts.get('routable nets', 0) > 0 and
                route_counts['routable nets'] == route_counts.get('fully routed nets'), 'Incomplete routing')
        xdc = (folder / 'constraints.xdc').read_text()
        require(not re.search(r'^\s*(set_false_path|set_multicycle_path|create_waiver)\b', xdc, re.M),
                'Unexpected path exceptions')
        for cmd, kind, value in [('set_input_delay', '-max', '2.000'),
                                 ('set_input_delay', '-min', '0.500'),
                                 ('set_output_delay', '-max', '2.000'),
                                 ('set_output_delay', '-min', '-0.500')]:
            require(any(line.startswith(cmd) and kind in line and value in line and 'b_clock/O' in line
                        for line in xdc.splitlines()), 'Missing explicit IO budget')
        result['variants'][variant] = {
            'timing': timing, 'clock': clock[0], 'path_groups': groups, 'paths': paths,
            'methodology': rules(folder / 'methodology.rpt'), 'drc': rules(folder / 'drc.rpt'),
            'route_counts': route_counts, 'utilization': utilization(folder / 'utilization.rpt'),
            'research_model_timing_met': all(timing[k] >= 0 for k in ['wns_ns', 'whs_ns', 'wpws_ns'])}
    result['scope'] = ('Clock-only BUFG wrappers with a declared IO timing envelope; unchanged semantic oracles. '
                       'Measured internal and boundary timing, not a board/platform closure or full router speedup.')
    scripts = [Path(__file__).resolve(), ROOT / 'hardware/scripts/report_codec_timing.py']
    result['audit_sources'] = {str(p.relative_to(ROOT)): digest(p) for p in scripts}
    artifacts = [p for p in out.rglob('*') if p.is_file() and not any(s in p.parts for s in
                 ['.vivado-ai', '.Xil', 'xsim.dir']) and p.name not in ['manifest.json', 'completion_audit.json']]
    artifacts.append(out / 'simulation/manifest.json')
    result['artifacts'] = {str(p.relative_to(out)): digest(p) for p in sorted(set(artifacts))}
    (out / 'manifest.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    audit = {'status': 'passed', 'manifest_sha256': digest(out / 'manifest.json'),
             'scope': 'Semantic regression and physical evidence integrity; timing success is reported separately.'}
    (out / 'completion_audit.json').write_text(json.dumps(audit, indent=2) + '\n')
    print(json.dumps(audit))


if __name__ == '__main__':
    main()
