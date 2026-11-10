#!/usr/bin/env python3
"""Audit selected golden rows, unchanged RTL, and per-stratum transactions."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import struct
from check_vitis_kernel import digest, require, validate_case_log
from prepare_vitis_stratified import read_full_case

ROOT = Path(__file__).resolve().parents[1]


def check_fixtures(bundle):
    plan_path = bundle/'plan.json'
    plan = json.loads(plan_path.read_text())
    for path, sha in {**plan['files'], **plan['generated']}.items():
        require(digest(path) == sha, 'Fixture dependency changed: '+path)
    original = ROOT/'data/derived/hls_region_fixtures_20261023_v1'
    modes = {}
    for mode in ('csr', 'compact'):
        source_rows = {}
        for i in range(9):
            source_rows.update(read_full_case((original/mode/f'full_{i}.bin').read_bytes()))
        lines = (bundle/mode/'rtl.txt').read_text().splitlines()
        require(len(lines) == len(plan['cases'])+2, 'Unexpected stimulus count')
        for case, line in zip(plan['cases'], lines):
            image, cfg, path = map(Path, line.split())
            require(path == bundle/mode/(case['label']+'.bin'), 'Case path/order differs')
            require(str(image) in plan['files'] and cfg == original/mode/'config.bin', 'Unbound image/config')
            data = path.read_bytes()
            n = struct.unpack_from('<I', data)[0]
            nodes = list(struct.unpack_from(f'<{n}I', data, 16))
            require(nodes == case['nodes'], 'Request order differs')
            selected = read_full_case(data)
            require(selected == {node: source_rows[node] for node in nodes}, 'Selected eight-field golden differs')
            require(case['degrees'] == [-1 if selected[node][0] else selected[node][1] for node in nodes],
                    'Stratum degree labels differ')
        modes[mode] = [line.split()[-1] for line in lines]
    return plan


def audit(bundle):
    state = json.loads((bundle/'pipeline.json').read_text())
    require(state['status'] == 'complete' and sorted(state['completed_modes']) == ['compact', 'csr'],
            'Cosimulation pipeline incomplete')
    plan = json.loads((bundle/'plan.json').read_text())
    for path, sha in plan['files'].items():
        require(digest(path) == sha, 'Frozen dependency changed: '+path)
    fixture = Path(plan['fixtures'])
    fp = check_fixtures(fixture)
    files = {str(p): digest(p) for p in [bundle/'pipeline.json', bundle/'plan.json', Path(__file__).resolve()]}
    modes = {}
    for mode in ('csr', 'compact'):
        work = bundle/mode
        project = Path(plan['projects'][mode])
        receipt_path = work/'receipt.json'
        receipt = json.loads(receipt_path.read_text())
        log = work/'cosim.log'
        content = log.read_text()
        require(receipt['exit_code'] == 0 and receipt['log_sha256'] == digest(log), 'Bad cosim receipt')
        require('ERROR:' not in content and 'VITIS_STRATIFIED_COSIM_COMPLETE' in content, 'Cosim failed')
        manifest = fixture/mode/'rtl.txt'
        cases = validate_case_log(content, manifest, 2)
        validate_case_log((work/'cpu.log').read_text(), manifest, 1)
        original = ROOT/'build'/f'vitis_graph_{mode}_20261023_v2/solution/syn/verilog'
        copied = project/'solution/syn/verilog'
        old = {p.name: p for p in original.glob('*.v')}
        new = {p.name: p for p in copied.glob('*.v')}
        require(old and old.keys() == new.keys(), 'RTL file set differs')
        for name in old:
            require(digest(old[name]) == digest(new[name]), 'RTL differs from audited baseline')
            files[str(new[name])] = digest(new[name])
        cosim = project/'solution/sim/report/graph_accel_cosim.rpt'
        transaction = project/'solution/sim/report/verilog/result.transaction.rpt'
        require(re.search(r'Verilog\s*\|\s*Pass', cosim.read_text()), 'RTL report not passing')
        pairs = [(int(i), int(c)) for i,c in re.findall(r'^transaction\s+(\d+):\s+(\d+)', transaction.read_text(), re.M)]
        require([i for i,c in pairs] == list(range(len(cases))) and all(c > 0 for i,c in pairs),
                'Missing/repeated/reordered RTL transactions')
        for case, (_, cycles) in zip(cases, pairs):
            case['label'] = Path(case['case']).stem
            case['cycles'] = cycles
        modes[mode] = cases
        for path in [receipt_path, log, work/'cpu.log', work/'compile.log', work/'cpu_test',
                     work/'copied_project.json', cosim, transaction]:
            files[str(path)] = digest(path)
    ratios = []
    for csr, compact in zip(modes['csr'], modes['compact']):
        require(all(csr[k] == compact[k] for k in ['label', 'requests', 'records', 'failed']), 'Matched workload differs')
        ratios.append({'label': csr['label'], 'requests': csr['requests'], 'records': csr['records'],
                       'csr_cycles': csr['cycles'], 'compact_cycles': compact['cycles'],
                       'compact_over_csr': compact['cycles']/csr['cycles']})
    return {'status': 'stratified_golden_and_unchanged_rtl_verified',
            'created_utc': datetime.now(timezone.utc).isoformat(), 'files': files,
            'fixture_plan_sha256': digest(fixture/'plan.json'), 'selection': fp['cases'],
            'empty_strata': fp['empty_strata'], 'modes': modes, 'comparisons': ratios,
            'limitations': fp['limitations'] + ['No algorithm optimization is applied in this experiment.']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bundle', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    report = audit(a.bundle.resolve())
    with a.output.open('x') as stream:
        json.dump(report, stream, indent=2); stream.write('\n')
    print(json.dumps({'status': report['status'], 'comparisons': report['comparisons']}))


if __name__ == '__main__':
    main()
