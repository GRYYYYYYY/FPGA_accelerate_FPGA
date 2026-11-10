#!/usr/bin/env python3
"""Independently verify sharing groups, unchanged static semantics, and all native rows."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from packed_graph import PackedGraph
from real_experiment import write_new


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''): h.update(block)
    return h.hexdigest()


def check_layout(original, candidate, span):
    if span is not None and (type(span) is not int or span <= 0):
        raise ValueError('Invalid span')
    if original.mode != 1 or candidate.mode != 1 or set(original.layout) != set(candidate.layout):
        raise ValueError('Compact layout differs')
    unchanged = set(original.layout) - {'TPL_OFF', 'RULE', 'INSTANCE'}
    for name in unchanged:
        ao, al, ac, aw = original.layout[name]
        bo, bl, bc, bw = candidate.layout[name]
        if (al, ac, aw) != (bl, bc, bw) or original.data[ao:ao+al] != candidate.data[bo:bo+bl]:
            raise ValueError('Static/exception section changed: '+name)
    if len(original.instances) != len(candidate.instances):
        raise ValueError('Instance count changed')
    if span is None:
        if original.data != candidate.data: raise ValueError('Global control must be byte identical')
        return
    group_to_tid, tid_to_group = {}, {}
    for row, (left, right) in enumerate(zip(original.instances, candidate.instances)):
        if left[1:] != right[1:]: raise ValueError('Per-instance exceptions changed')
        if left[0] < 0:
            if right[0] != -1: raise ValueError('Unknown family fallback changed')
            continue
        tile = original.tiles[original.nodes[original.roots[row][0]][2]]
        group = (int(tile[4]), int(tile[2])//span, int(tile[3])//span, left[0])
        if group in group_to_tid and group_to_tid[group] != right[0]: raise ValueError('Group not shared')
        if right[0] in tid_to_group and tid_to_group[right[0]] != group: raise ValueError('Sharing crosses group')
        group_to_tid[group] = right[0]
        tid_to_group[right[0]] = group
        if right[0] < 0: raise ValueError('Known template became fallback')
        old = original.rules[original.offsets[left[0]][0]:original.offsets[left[0]+1][0]]
        new = candidate.rules[candidate.offsets[right[0]][0]:candidate.offsets[right[0]+1][0]]
        if old != new: raise ValueError('Frozen template rules changed')
    if set(tid_to_group) != set(range(len(candidate.offsets)-1)):
        raise ValueError('Missing or unused template storage')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original', type=Path); parser.add_argument('candidate', type=Path)
    parser.add_argument('--span', type=int)
    parser.add_argument('--native-checker', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    original, candidate = PackedGraph(args.original), PackedGraph(args.candidate)
    check_layout(original, candidate, args.span)
    command = [str(args.native_checker.resolve()), str(args.original.resolve()), str(args.candidate.resolve())]
    native = subprocess.run(command, check=True, text=True, capture_output=True)
    result = json.loads(native.stdout)
    if result['status'] != 'all_native_rows_equivalent' or result['known_rows'] != len(original.roots) or result['nodes'] != len(original.nodes):
        raise ValueError('Native complete domain not verified')
    files = {str(path.resolve()): digest(path) for path in
             (args.original, args.candidate, args.native_checker, Path(__file__), ROOT/'src/packed_graph.py',
              ROOT/'src/native/template_scope_check.cpp', ROOT/'src/native/packed_graph.hpp')}
    write_new(args.output, {'status': 'complete_template_scope_equivalence_verified', 'span_tiles': args.span,
              'files': files, 'native': result, 'native_command': command,
              'bytes': len(candidate.data), 'templates': len(candidate.offsets)-1, 'rule_records': len(candidate.rules),
              'limitations': ['Dictionary sharing extent only; no changed training or query/domain filtering.',
                              'Complete static adjacency equivalence, not new full-router runtime or FPGA performance.']})
    print(json.dumps(result))


if __name__ == '__main__': main()
