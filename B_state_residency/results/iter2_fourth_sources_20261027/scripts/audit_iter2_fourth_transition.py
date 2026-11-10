"""Audit CPU q180329 completion and q180330 preparation over every node.

This does not execute RTL or independently recompute candidate costs.
"""
from pathlib import Path
import json
import mmap
import struct
import sys
from run_followup_query import sha


def state(root):
    return {t[0]: list(map(int, t[1:])) for t in
            (line.split() for line in (root / 'state.txt').read_text().splitlines())}


def main():
    previous, current = (Path(p).resolve() for p in sys.argv[1:3])
    for root in [previous, current]:
        audit = json.loads((root / 'source_bound_audit.json').read_text())
        assert audit['status'] == 'passed'
        assert audit['manifest_sha256'] == sha(root / 'manifest.json')
        manifest = json.loads((root / 'manifest.json').read_text())
        for name in ['initial_nodes.u32', 'search_final_nodes.u32', 'initial_overflow.u32', 'prices.u32', 'state.txt']:
            assert sha(root / name) == manifest['artifacts'][name]
    prep = json.loads((current / 'prepare_trace_audit.json').read_text())
    assert prep['status'] == 'passed'
    assert prep['trace_sha256'] == sha(current / 'prepare_ripup.txt')
    assert prep['capture_audit_sha256'] == sha(current / 'source_bound_audit.json')
    old, new = state(previous), state(current)
    assert old['sequence'] == [180329] and new['sequence'] == [180330]
    assert old['nodes'] == new['nodes'] and old['net'] == new['net'] == [26422]
    trace = [t.split() for t in (current / 'prepare_ripup.txt').read_text().splitlines()]
    before = {int(t[1]): tuple(map(int, t[2:])) for t in trace if t[0] == 'BEFORE'}
    after = {int(t[1]): tuple(map(int, t[2:])) for t in trace if t[0] == 'AFTER'}
    with (previous / 'search_final_nodes.u32').open('rb') as f, (current / 'initial_nodes.u32').open('rb') as g:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as a, mmap.mmap(g.fileno(), 0, access=mmap.ACCESS_READ) as b:
            assert len(a) == len(b) == new['nodes'][0] * 44
            def row(image, node):
                return list(struct.unpack_from('<11I', image, node * 44))
            chain = []
            node = old['sink'][0]
            while node != 0xffffffff:
                assert node not in chain
                chain.append(node)
                node = row(a, node)[3]
            assert chain[-1] == old['source'][0]
            expected = {}
            for node in chain[1:-1]:
                v = expected.setdefault(node, row(a, node))
                assert v[6] == old['net'][0] and v[7] > 0
                v[7] += 1
            for node, raw in before.items():
                v = expected.setdefault(node, row(a, node))
                assert v[6:9] == [x & 0xffffffff for x in raw[:3]], node
                assert raw[3] == v[7] if v[6] == new['net'][0] else raw[3] == 0
            for change in prep['native_decrements']:
                node = change['node']
                v = expected[node]
                assert v[7] == change['refs_before'] and v[7] > 0
                v[7] -= 1
                if v[7] == 0:
                    assert v[8] == 1 and change['last_owner_removed']
                    v[6] = 0xffffffff
                    v[8] = 0
                assert v[6:9] == [x & 0xffffffff for x in after[node][:3]]
            for node in old['targets']:
                expected.setdefault(node, row(a, node))[5] = 0
            for node in new['targets']:
                expected.setdefault(node, row(a, node))[5] = 1
            v = expected.setdefault(new['source'][0], row(a, new['source'][0]))
            v[0] = v[1] = 0
            v[4] = new['sequence'][0]
            changed = []
            stride = 44 * 16384
            for start in range(0, len(a), stride):
                aa, bb = a[start:start + stride], b[start:start + stride]
                if aa == bb:
                    continue
                for offset in range(0, len(aa), 44):
                    if aa[offset:offset + 44] != bb[offset:offset + 44]:
                        node = (start + offset) // 44
                        assert row(b, node) == expected.get(node, row(a, node)), node
                        changed.append(node)
            for node, v in expected.items():
                assert row(b, node) == v, node
    for name in ['initial_overflow.u32', 'prices.u32']:
        assert sha(previous / name) == sha(current / name), name
    result = dict(status='passed', auditor_sha256=sha(Path(__file__)),
                  previous_audit_sha256=sha(previous / 'source_bound_audit.json'),
                  current_audit_sha256=sha(current / 'source_bound_audit.json'),
                  prepare_audit_sha256=sha(current / 'prepare_trace_audit.json'),
                  full_node_rows_verified=new['nodes'][0], changed_rows=changed,
                  prior_committed_path=chain, next_preparation=prep['native_decrements'],
                  overflow_and_prices_unchanged=True,
                  scope='Entire CPU node transition including q3 owner commit, q4 native old-path ripup including actual sole-owner release, target cleanup/setup and source push. No fourth-query RTL, independent cost oracle, four-slot path-capacity or G4 proof.')
    (current / 'transition_audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
