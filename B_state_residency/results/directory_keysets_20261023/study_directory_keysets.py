"""Hash-table sizing on real dirty-page key sets; not a temporal routing replay."""
from pathlib import Path
import hashlib
import json
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
RECORD = struct.Struct('<IIIBBHI')


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def mixed(key):
    key ^= key >> 16
    key = (key * 0x85ebca6b) & 0xffffffff
    key ^= key >> 13
    key = (key * 0xc2b2ae35) & 0xffffffff
    return key ^ (key >> 16)


def measure(keys, capacity, hash_function):
    table = [None] * capacity
    mask = capacity - 1
    costs = []
    for frame, key in enumerate(keys):
        start = hash_function(key) & mask
        for probe in range(1, capacity + 1):
            slot = (start + probe - 1) & mask
            if table[slot] is None:
                table[slot] = (key, frame)
                costs.append(probe)
                break
        else:
            raise ValueError('Table unexpectedly full')
    # Independent successful-lookup pass must recover the original frame map.
    oracle = dict(zip(keys, range(len(keys))))
    hits = []
    for key, expected in oracle.items():
        start = hash_function(key) & mask
        for probe in range(1, capacity + 1):
            entry = table[(start + probe - 1) & mask]
            if entry is None:
                raise AssertionError('Published key lost')
            if entry[0] == key:
                if entry[1] != expected:
                    raise AssertionError('Wrong frame binding')
                hits.append(probe)
                break
        else:
            raise AssertionError('Lookup did not terminate')
    if costs != hits:
        raise AssertionError('Insertion/lookup displacement disagreement')
    ordered = sorted(hits)
    def percentile(p):
        return ordered[max(0, (len(ordered) * p + 99) // 100 - 1)] if ordered else 0
    return {'entries': len(keys), 'capacity': capacity, 'load_fraction': len(keys) / capacity,
            'probe_sum': sum(hits), 'mean_probe_reads': sum(hits) / len(hits) if hits else 0,
            'p95': percentile(95), 'p99': percentile(99), 'max': max(hits, default=0),
            'over_16': sum(p > 16 for p in hits), 'over_64': sum(p > 64 for p in hits),
            'over_256': sum(p > 256 for p in hits), 'verified_bindings': len(hits)}


def main():
    out = Path(sys.argv[1]).resolve()
    out.mkdir()
    capture = ROOT / 'results/real_field_values_20261023T024250Z'
    parent = json.loads((capture / 'manifest.json').read_text())
    completion = json.loads((capture / 'completion_audit.json').read_text())
    if parent['status'] != 'passed' or sha(capture / 'manifest.json') != completion['manifest_sha256']:
        raise ValueError('Capture is not authenticated')
    paths = [capture / 'trace.values', capture / 'trace.queries.jsonl']
    for path in paths:
        if sha(path) != parent['artifacts'][str(path)]:
            raise ValueError('Changed real trace')
    keysets = []
    totals = {'queries': 0, 'accesses': 0, 'reads': 0, 'writes': 0}
    with paths[0].open('rb') as data, paths[1].open() as metadata:
        for line in metadata:
            row = json.loads(line)
            if data.tell() != row['byte_offset']:
                raise ValueError('Query offset gap')
            raw = data.read(row['count'] * RECORD.size)
            if len(raw) != row['count'] * RECORD.size:
                raise ValueError('Truncated values')
            pages = {}; reads = writes = 0
            for node, source, bits, field, write, reserved, hist in RECORD.iter_unpack(raw):
                if not (0 <= node < 9089009 and source > 0 and field < 5 and write in (0, 1) and reserved == 0):
                    raise ValueError('Invalid captured field')
                if write:
                    pages.setdefault(node >> 6, len(pages)); writes += 1
                else:
                    reads += 1
            if (reads, writes) != (row['reads'], row['writes']):
                raise ValueError('Read/write count mismatch')
            keysets.append({'attempt': row['attempt'], 'iteration': row['iteration'],
                            'accesses': row['count'], 'dirty_pages_first_write_order': list(pages)})
            totals['queries'] += 1; totals['accesses'] += row['count']
            totals['reads'] += reads; totals['writes'] += writes
        if data.read(1):
            raise ValueError('Uncovered trace suffix')
    if totals != {'queries': 38, 'accesses': 14047736, 'reads': 10324516, 'writes': 3723220}:
        raise ValueError('Real trace coverage changed')
    trials = []
    for row in keysets:
        for tag in range(4):
            keys = [((row['iteration'] & 15) << 20) | (tag << 18) | page
                    for page in row['dirty_pages_first_write_order']]
            for capacity in [32768, 65536]:
                for name, function in [('identity', lambda key: key), ('mixed32', mixed)]:
                    trials.append(dict(attempt=row['attempt'], query_tag=tag, hash=name,
                                       **measure(keys, capacity, function)))
    # A deliberately colliding legal 24-bit key set demonstrates lack of a
    # distribution-independent 64-probe bound for the low-bit identity map.
    adversarial = measure([i * 32768 for i in range(320)], 32768, lambda key: key)
    if adversarial['max'] != 320 or adversarial['over_64'] != 256:
        raise AssertionError('Collision control failed')
    (out / 'keysets.jsonl').write_text(''.join(json.dumps(row) + '\n' for row in keysets))
    (out / 'trials.json').write_text(json.dumps(trials, indent=2) + '\n')
    script = Path(__file__).resolve()
    (out / script.name).write_bytes(script.read_bytes())
    aggregates = {}
    for capacity in [32768, 65536]:
        for name in ['identity', 'mixed32']:
            rows = [t for t in trials if t['capacity'] == capacity and t['hash'] == name]
            count = sum(t['entries'] for t in rows)
            aggregates[f'{name}_{capacity}'] = {
                'trials': len(rows), 'verified_bindings': count,
                'weighted_mean_probe_reads': sum(t['probe_sum'] for t in rows) / count,
                'maximum_probe_reads': max(t['max'] for t in rows),
                'over_16': sum(t['over_16'] for t in rows), 'over_64': sum(t['over_64'] for t in rows),
                'over_256': sum(t['over_256'] for t in rows)}
    result = {'status': 'passed', 'trace_totals': totals, 'trial_count': len(trials),
              'max_dirty_pages_per_query': max(len(r['dirty_pages_first_write_order']) for r in keysets),
              'aggregates': aggregates, 'adversarial_identity': adversarial,
              'performance': None, 'rtl_implementation': False,
              'scope': ('Per-query dirty-page key sets in first-write order, four query tags and real iteration prices. '
                        'Not actual allocation/refill traffic, checkpoint epochs, concurrent-query mixtures, '
                        'a capped-probe implementation, worst-case guarantee or measured acceleration.'),
              'inputs': {str(p): sha(p) for p in paths + [capture / 'manifest.json']},
              'source': {str(script): sha(script)},
              'artifacts': {p.name: sha(p) for p in out.iterdir() if p.is_file()}}
    (out / 'manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    (out / 'completion_audit.json').write_text(json.dumps({'status': 'passed', 'manifest_sha256': sha(out / 'manifest.json')}, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['trace_totals', 'max_dirty_pages_per_query', 'aggregates']}, indent=2), flush=True)


if __name__ == '__main__':
    main()
