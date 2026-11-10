"""Actual-value planner for retaining published backing across an ID checkpoint.

This is a sequential software reference for a proposed protocol. It neither
implements nor proves the future RTL drain/ACK operation.
"""
from collections import OrderedDict, Counter
from pathlib import Path
import hashlib
import json
import os
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
RECORD = struct.Struct('<IIIBBHI')


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


PAGE_NODES = 8
SLOTS = 32
STRIDE = 192


def encode_page(values):
    raw = bytearray(STRIDE)
    for offset, word in values.items():
        assert 0 <= offset < PAGE_NODES and 0 <= word < (1 << 136)
        raw[0] |= 1 << offset
        raw[1 + offset * 20:1 + offset * 20 + 17] = word.to_bytes(17, "little")
    return bytes(raw)


def decode_page(raw):
    assert len(raw) == STRIDE and not any(raw[161:])
    values = {}
    for offset in range(PAGE_NODES):
        start = 1 + offset * 20
        assert not any(raw[start + 17:start + 20])
        if raw[0] & (1 << offset):
            values[offset] = int.from_bytes(raw[start:start + 17], "little")
        else:
            assert not any(raw[start:start + 20])
    return values


class Planner:
    def __init__(self, transaction_bits=16, generation_bits=16):
        self.limit = 1 << transaction_bits
        self.generation_limit = 1 << generation_bits
        assert self.limit >= SLOTS + 2 and self.generation_limit >= 4
        self.live = OrderedDict(); self.backing = {}; self.frames = {}
        self.generations = [0] * SLOTS; self.next_tx = 0
        self.counts = Counter(); self.checkpoints = []

    def transfer(self, kind):
        assert self.next_tx < self.limit, 'transaction overflow'
        self.counts['max_transaction'] = max(self.counts['max_transaction'], self.next_tx)
        self.next_tx += 1; self.counts[kind] += 1

    def evict(self, page):
        state = self.live.pop(page)
        if state['dirty']:
            self.transfer('writebacks')
            self.frames.setdefault(page, len(self.frames))
            self.backing[page] = encode_page(state['values'])
            assert decode_page(self.backing[page]) == state['values']
        self.counts['releases'] += 1

    def checkpoint(self):
        before = self.next_tx
        dirty = sum(s['dirty'] for s in self.live.values())
        assert self.limit - self.next_tx >= dirty, 'no budget to publish dirty state'
        for page in list(self.live):
            self.evict(page)
        # Simulate only the specified retained-state effect. Real drain proof
        # and internal query resume remain obligations of the future RTL.
        retained = self.backing
        addresses = self.frames
        self.checkpoints.append({'before_drain_transactions': before, 'after_drain_transactions': self.next_tx,
                                 'dirty_pages_flushed': dirty, 'backing_pages': len(self.backing),
                                 'max_generation': max(self.generations)})
        self.next_tx = 0; self.generations = [0] * SLOTS
        assert self.backing is retained and self.frames is addresses and not self.live
        self.counts['checkpoints'] += 1

    def access(self, node, field, write, bits):
        # Conservatively reserve up to 32 dirty writebacks plus a WB/RF miss.
        # No data is discarded when a finite domain approaches exhaustion.
        if self.limit - self.next_tx < SLOTS + 2 or max(self.generations) >= self.generation_limit - 2:
            self.checkpoint()
        page, offset = divmod(node, PAGE_NODES)
        if page not in self.live:
            if len(self.live) == SLOTS:
                self.evict(next(iter(self.live)))
            used = {s['slot'] for s in self.live.values()}
            slot = next(s for s in range(SLOTS) if s not in used)
            self.generations[slot] += 1
            assert self.generations[slot] < self.generation_limit
            if page in self.backing:
                self.transfer('refills')
            self.live[page] = {'slot': slot, 'dirty': False, 'values': decode_page(self.backing[page]) if page in self.backing else {}}
            self.counts['bindings'] += 1
            self.counts['max_generation'] = max(self.counts['max_generation'], self.generations[slot])
        else:
            self.live.move_to_end(page); self.counts['hits'] += 1
        state = self.live[page]
        word = state['values'].get(offset, 0)
        width = 8 if field == 4 else 32
        mask = (1 << width) - 1
        assert 0 <= bits <= mask
        if write:
            word = (word & ~(mask << (field * 32))) | (bits << (field * 32))
            state['values'][offset] = word; state['dirty'] = True
            self.counts['writes'] += 1
        else:
            assert ((word >> (field * 32)) & mask) == bits, 'actual read differs after retained checkpoint'
            self.counts['reads'] += 1
        self.counts['accesses'] += 1
        return word

    def finish(self, oracle):
        assert self.limit - self.next_tx >= sum(s['dirty'] for s in self.live.values())
        for page in list(self.live):
            self.evict(page)
        actual = {page * PAGE_NODES + off: word for page, raw in self.backing.items() for off, word in decode_page(raw).items()}
        assert actual == oracle, 'final published image differs from independent logical state'
        assert len(self.frames) == len(self.backing) <= (30 * 1024 * 1024) // STRIDE
        assert sorted(self.frames.values()) == list(range(len(self.frames)))


def boundary_test():
    planner = Planner(6, 3); oracle = {}
    for i in range(160):
        node = (i % 37) * PAGE_NODES
        value = i + 1
        planner.access(node, 0, True, value); oracle[node] = value
        planner.access(node, 0, False, value)
    planner.finish(oracle)
    assert planner.counts['checkpoints'] > 2
    bad = Planner(6, 3)
    for i in range(4):
        bad.access(i * 64, 0, True, i + 1)
    bad.next_tx = 63
    try:
        bad.checkpoint()
    except AssertionError as exc:
        assert 'no budget' in str(exc)
    else:
        raise AssertionError('Missing drain budget guard')
    return dict(planner.counts)


def main():
    out = Path(sys.argv[1]).resolve(); out.mkdir()
    capture = ROOT / 'results/real_field_values_20261023T024250Z'
    parent_path = capture / 'manifest.json'
    assert sha(parent_path) == 'e6eaa58c27c56125f727d01f1d9189c71e943de2e9343912ea71a38f5f374aac'
    parent = json.loads(parent_path.read_text())
    inputs = [capture / name for name in ['trace.values', 'trace.queries.jsonl']]
    for path in inputs:
        assert sha(path) == parent['artifacts'][str(path)]
    source = Path(__file__).resolve()
    (out / source.name).write_bytes(source.read_bytes())
    result = {'status': 'running', 'pid': os.getpid(), 'boundary_test': boundary_test(), 'queries': [],
              'source': {str(source): sha(source)}, 'inputs': {str(p): sha(p) for p in inputs + [parent_path]},
              'page_nodes': PAGE_NODES, 'resident_slots': SLOTS, 'stride_bytes': STRIDE, 'rtl_implemented': False, 'board_performance': None,
              'scope': '8-node pages, 32 slots, 192-byte encoded backing; sequential actual-value checks and finite IDs. No queue/ACK or RTL proof.'}
    def save():
        temp = out / 'manifest.tmp'
        temp.write_text(json.dumps(result, indent=2) + '\n')
        temp.replace(out / 'manifest.json')
    save()
    try:
        with inputs[0].open('rb') as stream:
            for line in inputs[1].read_text().splitlines():
                row = json.loads(line)
                assert stream.tell() == row['byte_offset']
                raw = stream.read(row['count'] * RECORD.size)
                assert len(raw) == row['count'] * RECORD.size
                planner = Planner(); oracle = {}
                for node, site, bits, field, write, reserved, hist in RECORD.iter_unpack(raw):
                    assert node < 9089009 and site > 0 and field < 5 and write in (0, 1) and reserved == 0
                    value = planner.access(node, field, write, bits)
                    old = oracle.get(node, 0)
                    if write:
                        width = 8 if field == 4 else 32
                        keep = ((1 << 136) - 1) ^ (((1 << width) - 1) << (field * 32))
                        oracle[node] = (old & keep) | (bits << (field * 32))
                    assert value == oracle.get(node, 0), 'resident state differs from independent dictionary'
                planner.finish(oracle)
                counts = planner.counts
                assert (counts['accesses'], counts['reads'], counts['writes']) == (row['count'], row['reads'], row['writes'])
                result['queries'].append({'attempt': row['attempt'], 'iteration': row['iteration'], 'counts': dict(counts),
                                          'backing_pages': len(planner.backing), 'checkpoints': planner.checkpoints})
                save(); print(row['attempt'], 'passed', counts['checkpoints'], 'checkpoints', flush=True)
            assert not stream.read(1)
        assert len(result['queries']) == 38
        assert sum(q['counts']['accesses'] for q in result['queries']) == 14047736
        assert sha(source) == result['source'][str(source)]
        result['status'] = 'passed'; save()
        (out / 'completion_audit.json').write_text(json.dumps({'status': 'passed', 'manifest_sha256': sha(out / 'manifest.json')}, indent=2) + '\n')
    except Exception as exc:
        result.update(status='failed', error=repr(exc)); save(); raise


if __name__ == '__main__':
    main()
