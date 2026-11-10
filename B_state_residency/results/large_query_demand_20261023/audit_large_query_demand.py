"""Count complete-query 4-page LRU demand without truncating finite-ID overflows.

This is an address/lifecycle demand census, not a value replay or a checkpoint
implementation. It determines which complete traces fit one current RTL epoch.
"""
from collections import OrderedDict, Counter
from pathlib import Path
import hashlib
import json
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


def main():
    out = Path(sys.argv[1]).resolve()
    out.mkdir()
    capture = ROOT / 'results/real_field_values_20261023T024250Z'
    parent = json.loads((capture / 'manifest.json').read_text())
    assert sha(capture / 'manifest.json') == 'e6eaa58c27c56125f727d01f1d9189c71e943de2e9343912ea71a38f5f374aac'
    inputs = [capture / name for name in ['trace.values', 'trace.queries.jsonl']]
    for p in inputs:
        assert sha(p) == parent['artifacts'][str(p)]
    rows = []; totals = Counter(); small = Counter()
    with inputs[0].open('rb') as stream:
        for line in inputs[1].read_text().splitlines():
            row = json.loads(line)
            assert stream.tell() == row['byte_offset']
            raw = stream.read(row['count'] * RECORD.size)
            assert len(raw) == row['count'] * RECORD.size
            slots = {}; lru = OrderedDict(); dirty = set(); backing = set(); generations = [0] * 4
            counts = Counter()
            def evict(page):
                if page in dirty:
                    counts['writebacks'] += 1; dirty.remove(page)
                del slots[page]; del lru[page]
            for node, source, bits, field, write, reserved, hist in RECORD.iter_unpack(raw):
                assert node < 9089009 and source > 0 and field < 5 and write in (0, 1) and reserved == 0
                assert field != 4 or bits <= 255
                page = node >> 6
                if page not in slots:
                    if len(slots) == 4:
                        evict(next(iter(lru)))
                    slot = next(s for s in range(4) if s not in slots.values())
                    slots[page] = slot; lru[page] = None
                    generations[slot] += 1; counts['bindings'] += 1
                    if page in backing:
                        counts['refills'] += 1
                else:
                    counts['hits'] += 1; lru.move_to_end(page)
                counts['accesses'] += 1; counts['writes' if write else 'reads'] += 1
                if write:
                    backing.add(page); dirty.add(page)
            for page in list(slots):
                evict(page)
            assert (counts['accesses'], counts['reads'], counts['writes']) == (row['count'], row['reads'], row['writes'])
            counts['transfers'] = counts['writebacks'] + counts['refills']
            counts['public_commands'] = 3 + 2 * counts['bindings'] + counts['accesses'] + counts['transfers']
            result = {'attempt': row['attempt'], 'iteration': row['iteration'], **dict(counts),
                      'unique_backing_pages': len(backing), 'slot_generation_counts': generations,
                      'fits_transaction_ids_16': counts['transfers'] <= 65536,
                      'fits_generation_ids_16': max(generations) < 65536,
                      'fits_frames_23405': len(backing) <= 23405,
                      'expected_page_hex_bytes': counts['transfers'] * 21 * 129}
            result['fits_current_epoch'] = all(result[k] for k in ['fits_transaction_ids_16', 'fits_generation_ids_16', 'fits_frames_23405'])
            rows.append(result); totals.update(counts)
            if row['count'] <= 100000:
                small.update(counts)
            print(row['attempt'], 'transfers', counts['transfers'], 'max_generation', max(generations),
                  'fits_epoch', result['fits_current_epoch'], flush=True)
        assert not stream.read(1)
    # Reproduce the already completed 19-query vector census independently.
    assert {k: small[k] for k in ['accesses', 'writebacks', 'refills', 'bindings', 'public_commands']} == {
        'accesses': 56588, 'writebacks': 2702, 'refills': 3384, 'bindings': 7184, 'public_commands': 77099}
    assert len(rows) == 38 and totals['accesses'] == 14047736
    script = Path(__file__).resolve()
    (out / script.name).write_bytes(script.read_bytes())
    (out / 'queries.json').write_text(json.dumps(rows, indent=2) + '\n')
    result = {'status': 'passed', 'queries': len(rows), 'totals_without_checkpoints': dict(totals),
              'large_queries_fit_one_epoch': [r['attempt'] for r in rows if r['accesses'] > 100000 and r['fits_current_epoch']],
              'large_queries_need_checkpoint': [r['attempt'] for r in rows if r['accesses'] > 100000 and not r['fits_current_epoch']],
              'small_reference_matched': dict(small), 'board_performance': None,
              'scope': 'Complete 38-query address/LRU census with unbounded counting; no checkpoint/restore, field-value checking or RTL execution. Overflowing queries are flagged, not truncated.',
              'inputs': {str(p): sha(p) for p in inputs + [capture / 'manifest.json']},
              'source': {str(script): sha(script)},
              'artifacts': {p.name: sha(p) for p in out.iterdir() if p.is_file()}}
    (out / 'manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    (out / 'completion_audit.json').write_text(json.dumps({'status': 'passed', 'manifest_sha256': sha(out / 'manifest.json')}, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['large_queries_fit_one_epoch', 'large_queries_need_checkpoint', 'totals_without_checkpoints']}, indent=2), flush=True)


if __name__ == '__main__':
    main()
