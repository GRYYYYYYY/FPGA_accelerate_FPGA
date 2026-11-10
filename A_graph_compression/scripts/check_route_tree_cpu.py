#!/usr/bin/env python3
"""Compile/run the actual route-tree top against its independent CPU oracle.

This is a CPU component receipt, not an RTL or complete-router acceptance.
Existing reports are never overwritten.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--build', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists() or args.build.exists():
        raise SystemExit('refusing to overwrite existing evidence')
    args.build.mkdir(parents=True)
    env = dict(os.environ)
    env.pop('LD_PRELOAD', None)
    sources = ['tests/test_search_route_tree.cpp', 'hardware/vitis/search_route_tree_top.cpp']
    base = ['g++', '-std=c++14', '-Ihardware/vitis']
    dependencies = subprocess.check_output(base + ['-MM'] + sources, env=env, text=True)
    inputs = set()
    for line in dependencies.replace('\\\n', ' ').splitlines():
        inputs.update(line.split(':', 1)[1].split())
    inputs.add(__file__)

    def digest(path):
        p = Path(path)
        return {'path': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size}

    bindings = [digest(p) for p in sorted(inputs)]
    binary = args.build / 'test_route_tree'
    command = base + ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                      '-Wall', '-Wextra', '-Werror', '-Wno-unknown-pragmas'] + sources + ['-o', str(binary)]
    receipts = []
    for name, cmd in [('compile', command), ('cpu', [str(binary.resolve())])]:
        log = args.build / (name + '.log')
        with log.open('w') as stream:
            run = subprocess.run(cmd, env=env, stdout=stream, stderr=subprocess.STDOUT)
        receipts.append({'command': cmd, 'returncode': run.returncode, 'log': digest(log)})
        (args.build / 'receipts.json').write_text(json.dumps(receipts, indent=2) + '\n')
        if run.returncode:
            raise SystemExit(f'{name} failed; retained {log}')
    actual = (args.build / 'cpu.log').read_text().splitlines()
    expected = ['random accepted=1000 nonfound=1000 atomic_rejections=21',
                'production nodes=1048576 max_path=524288 state=32/16/8 full_buffers_and_guards=PASS',
                'route_tree_cpu PASS']
    if actual != expected:
        raise SystemExit('unexpected CPU test receipt')
    for item in bindings:
        if digest(item['path']) != item:
            raise SystemExit('input changed during verification')
    report = {'status': 'route_tree_production_top_cpu_oracle_and_sanitizers_passed',
              'inputs': bindings, 'binary': digest(binary), 'receipts': receipts,
              'coverage': expected, 'limitations': ['CPU component only; no RTL synthesis/simulation evidence',
                'Full router integration pending', 'Path connectivity and state inclusion checked; physical edge/site semantics trusted from search',
                'Internal state trusted; buffers must be disjoint and exclusively owned']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(report['status'])


if __name__ == '__main__':
    main()
