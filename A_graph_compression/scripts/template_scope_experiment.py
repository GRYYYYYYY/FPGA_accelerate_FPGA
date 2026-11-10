#!/usr/bin/env python3
"""Build and independently validate complete-region template-sharing scope variants."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from packed_graph import PackedGraph
from template_scope import write_scoped
from check_template_scope import digest
from real_experiment import write_new


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cpu', type=int, default=126)
    args = parser.parse_args(); args.output = args.output.resolve()
    if args.cpu not in os.sched_getaffinity(0): raise ValueError('Unavailable CPU')
    os.sched_setaffinity(0, {args.cpu})
    source = ROOT/'data/derived/region_all_nets_cap8_20261022_v1/compact.agr'
    prior_path = ROOT/'data/derived/native_site_routing_20261023_v2/plan.json'
    prior = json.loads(prior_path.read_text())
    if digest(source) != prior['files'][str(source)]: raise ValueError('Verified original image changed')
    regression = ROOT/'results/regression_template_scope_20261023_v1.log'
    if not regression.read_text().rstrip().endswith('OK'): raise ValueError('Regression not passed')
    args.output.mkdir(parents=True, exist_ok=False)
    binary = args.output/'native_check'
    compile_command = ['g++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-Werror',
                       str(ROOT/'src/native/template_scope_check.cpp'), '-o', str(binary)]
    with (args.output/'compile.log').open('x') as stream:
        subprocess.run(compile_command, stdout=stream, stderr=subprocess.STDOUT, check=True)
    paths = [source, prior_path, Path(__file__), ROOT/'src/template_scope.py', ROOT/'src/packed_graph.py',
             ROOT/'scripts/check_template_scope.py', ROOT/'scripts/real_experiment.py',
             ROOT/'src/native/template_scope_check.cpp', ROOT/'src/native/packed_graph.hpp', binary, regression]
    files = {str(path): digest(path) for path in paths}
    plan = {'owner_pid': os.getpid(), 'cpu': args.cpu, 'source': str(source), 'files': files,
            'spans_tiles': [None, 16, 4, 1], 'compile_command': compile_command,
            'scope': 'All original canonical nodes/rows retained; only template dictionary sharing extent changes.',
            'limitations': ['Frozen template family/rules and per-instance exceptions, not retrained template families.',
                           'One build per scope; preparation timings diagnostic, not repeated performance.',
                           'All-row native and static semantic equivalence; complete router runtime remains to measure.']}
    write_new(args.output/'plan.json', plan)
    image = PackedGraph(source); variants = []
    for span in plan['spans_tiles']:
        name = 'global' if span is None else f'span{span}'
        output = args.output/(name+'.agr'); report_path = args.output/(name+'.audit.json')
        start = time.perf_counter(); layout = write_scoped(image, output, span)
        layout['build_from_loaded_image_ms'] = (time.perf_counter()-start)*1000
        command = [sys.executable, '-u', str(ROOT/'scripts/check_template_scope.py'), str(source), str(output),
                   '--native-checker', str(binary), '--output', str(report_path)]
        if span is not None: command.extend(['--span', str(span)])
        with (args.output/(name+'.audit.log')).open('x') as stream:
            child = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT)
            write_new(args.output/(name+'.submission.json'), {'owner_pid': os.getpid(), 'child_pid': child.pid, 'command': command, 'cpu': args.cpu})
            code = child.wait()
        write_new(args.output/(name+'.receipt.json'), {'exit_code': code})
        if code: raise RuntimeError('Independent scope audit failed: '+name)
        audit = json.loads(report_path.read_text())
        if audit['status'] != 'complete_template_scope_equivalence_verified' or audit['bytes'] != layout['file_bytes']:
            raise ValueError('Independent audit scope/size differs')
        variants.append({'name': name, 'image': str(output), 'sha256': digest(output), 'layout': layout,
                         'audit': str(report_path), 'audit_sha256': digest(report_path), 'native_counts': audit['native']})
        print('TEMPLATE_SCOPE_VERIFIED', name, json.dumps(layout), flush=True)
    for path, value in files.items():
        if digest(path) != value: raise ValueError('Experiment dependency changed: '+path)
    write_new(args.output/'report.json', {'status': 'all_four_full_region_template_scopes_verified',
              'plan_sha256': digest(args.output/'plan.json'), 'variants': variants, 'limitations': plan['limitations']})


if __name__ == '__main__': main()
