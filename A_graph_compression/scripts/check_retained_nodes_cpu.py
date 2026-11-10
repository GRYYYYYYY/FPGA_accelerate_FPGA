#!/usr/bin/env python3
"""Compile/run the actual retained-node top against its independent CPU oracle.

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
    sources = ['tests/test_search_retained_nodes.cpp', 'hardware/vitis/search_retained_nodes_top.cpp']
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
    binary = args.build / 'test_retained_nodes'
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
    import re
    expected = ['RETAINED_PRODUCTION_PASS nodes=1048576 pairs=2097152 seeded_nets=65536 full_buffers=1','RETAINED_ALL_PASS']
    if len(actual)!=3 or actual[1:]!=expected:
        raise SystemExit('unexpected retained-node test receipt')
    match=re.fullmatch(r'RETAINED_RANDOM_PASS operations=6000 accepted=(\d+) rejected=(\d+)',actual[0])
    if match is None or sum(map(int,match.groups()))!=6000:
        raise SystemExit('missing random coverage')
    expected=actual
    for item in bindings:
        if digest(item['path']) != item:
            raise SystemExit('input changed during verification')
    report = {'status': 'retained_nodes_production_top_cpu_oracle_and_sanitizers_passed',
              'inputs': bindings, 'binary': digest(binary), 'receipts': receipts,
              'coverage': expected, 'limitations': ['CPU component only; no RTL synthesis/simulation evidence',
                'Full router integration pending', 'Node retention only; edges/site state are outside this component.65536-net boundary is explicitly seeded;2m pairs reached by actual operations',
                'Internal state trusted; buffers must be disjoint and exclusively owned']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(report['status'])


if __name__ == '__main__':
    main()
