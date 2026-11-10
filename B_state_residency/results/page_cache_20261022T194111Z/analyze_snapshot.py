"""Parametric fully-associative page LRU on CPU TLD traces; no hardware timing."""
import argparse
from collections import OrderedDict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]


def simulate(nodes, page_bits, capacity):
    if capacity <= 0:
        raise ValueError('Cache must hold at least one page')
    resident = OrderedDict()
    seen = set()
    counts = dict(accesses=0, hits=0, first_page_touches=0, refills=0, evictions=0)
    for node in nodes:
        page = node >> page_bits
        counts['accesses'] += 1
        if page in resident:
            counts['hits'] += 1
            resident.move_to_end(page)
            continue
        if page in seen:
            counts['refills'] += 1
        else:
            counts['first_page_touches'] += 1
            seen.add(page)
        if len(resident) == capacity:
            resident.popitem(last=False)
            counts['evictions'] += 1
        resident[page] = None
    counts['unique_pages'] = len(seen)
    return counts


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(1 << 20), b''):
            h.update(data)
    return h.hexdigest()


def analyze(prefix):
    cases = []
    for bits in (6, 9, 12):
        for budget in (1 << 20, 4 << 20, 16 << 20):
            payload = (1 << bits) * 28
            cases.append(dict(page_bits=bits, budget_bytes=budget, page_payload_bytes=payload,
                              assumed_page_tag_bytes=16, page_capacity=budget // (payload + 16),
                              queries=0, queries_with_refills=0, max_unique_pages=0,
                              accesses=0, hits=0, first_page_touches=0, refills=0, evictions=0))
    with prefix.with_suffix('.accesses').open('rb') as binary, prefix.with_suffix('.jsonl').open() as records:
        offset = selected = 0
        for line in records:
            row = json.loads(line)
            if row['access_byte_offset'] != offset:
                raise ValueError('Noncontiguous binary offset')
            if not row['accesses_selected']:
                if row['access_count']:
                    raise ValueError('Unselected access events')
                continue
            if row['truncated'] or row['access_count'] != row['label_accesses']:
                raise ValueError('Incomplete selected query')
            data = binary.read(row['access_count'] * 8)
            if len(data) != row['access_count'] * 8:
                raise ValueError('Truncated access file')
            offset += len(data)
            selected += 1
            nodes = [node for node, source_line in struct.iter_unpack('<ii', data)]
            if any(node < 0 for node in nodes):
                raise ValueError('Negative node ID')
            for case in cases:
                counts = simulate(nodes, case['page_bits'], case['page_capacity'])
                case['queries'] += 1
                case['queries_with_refills'] += bool(counts['refills'])
                case['max_unique_pages'] = max(case['max_unique_pages'], counts['unique_pages'])
                for key in ('accesses', 'hits', 'first_page_touches', 'refills', 'evictions'):
                    case[key] += counts[key]
        if binary.read(1):
            raise ValueError('Trailing access bytes')
    for case in cases:
        case['modeled_refill_bytes'] = case['refills'] * case['page_payload_bytes']
        case['modeled_writeback_bytes_if_every_touch_dirty'] = case['evictions'] * case['page_payload_bytes']
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=ROOT / 'results/real_trace_20261022T165136Z')
    args = parser.parse_args()
    out = ROOT / 'results' / ('page_cache_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    out.mkdir()
    prefixes = {'interval_sample': args.directory / 'trace_0', 'large_query_tail': args.directory / 'tail/trace'}
    files = [Path(__file__).resolve()] + [p.with_suffix(s) for p in prefixes.values() for s in ('.accesses', '.jsonl')]
    record = dict(status='running', execution_kind='cpu_trace_cache_model', performance=None,
                  assumptions='Independent cold cache per query; fully associative LRU; 24B labels+4B epoch/node+16B page tag. First touch initializes locally; refill reads full page. Writeback scenario marks every touch dirty, discards final resident pages at query end. Budgets are sensitivity parameters, not actual board allocations. CPU TLD events are not hardware memory transactions.',
                  files={str(p): sha(p) for p in files})
    def save():
        (out / 'manifest.json').write_text(json.dumps(record, indent=2) + '\n')
    save()
    try:
        record['groups'] = {}
        for name, prefix in prefixes.items():
            record['groups'][name] = analyze(prefix)
            save()
            print('Completed', name, flush=True)
        if record['groups']['interval_sample'][0]['queries'] != 1113 or record['groups']['large_query_tail'][0]['queries'] != 19:
            raise ValueError('Unexpected sample counts')
        if any(sha(p) != record['files'][str(p)] for p in files):
            raise ValueError('Input changed during analysis')
        record['status'] = 'passed'
    except Exception as error:
        record.update(status='failed', error=repr(error))
        raise
    finally:
        save()
    print(out, flush=True)


if __name__ == '__main__':
    main()
