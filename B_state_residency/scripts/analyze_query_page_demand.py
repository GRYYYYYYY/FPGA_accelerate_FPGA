"""Audit complete selected address traces; report per-query backing upper bounds."""
import hashlib
import json
import struct
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def analyze(prefix, expected_queries, expected_accesses):
    demands = []
    offset = 0
    with prefix.with_suffix('.jsonl').open() as metadata, prefix.with_suffix('.accesses').open('rb') as binary:
        for line_number, line in enumerate(metadata, 1):
            row = json.loads(line)
            if row['access_byte_offset'] != offset:
                raise ValueError('Access offset mismatch')
            if not row['accesses_selected']:
                if row['access_count']:
                    raise ValueError('Unselected events')
                continue
            if row['truncated'] or row['access_count'] != row['label_accesses']:
                raise ValueError('Incomplete selected query')
            raw = binary.read(row['access_count'] * 8)
            if len(raw) != row['access_count'] * 8:
                raise ValueError('Truncated binary')
            offset += len(raw)
            pages = set()
            for node, source_line in struct.iter_unpack('<ii', raw):
                if not 0 <= node < 9089009 or source_line <= 0:
                    raise ValueError('Invalid trace address')
                pages.add(node >> 6)
            demands.append(dict(metadata_line=line_number, accesses=row['access_count'], unique_pages=len(pages)))
        if binary.read(1):
            raise ValueError('Trailing access bytes')
    if len(demands) != expected_queries or sum(row['accesses'] for row in demands) != expected_accesses:
        raise ValueError('Unexpected coverage')
    maximum = max(row['unique_pages'] for row in demands)
    return dict(queries=len(demands), accesses=expected_accesses, maximum_unique_pages=maximum,
                synthetic_int64_raw_upper_bound_bytes=maximum * 576,
                node_dyn_payload_upper_bound_bytes=maximum * 1536, per_query=demands)


def main():
    base = ROOT / 'results/real_trace_20261022T165136Z'
    groups = {'interval_sample': (base / 'trace_0', 1113, 2399968),
              'large_query_tail': (base / 'tail/trace', 19, 13751567)}
    paths = [Path(__file__).resolve()] + [prefix.with_suffix(suffix) for prefix, _, _ in groups.values() for suffix in ('.jsonl', '.accesses')]
    hashes = {str(path): sha(path) for path in paths}
    result = dict(status='running', performance=None, page_nodes=64, synthetic_stride_bytes=576,
                  node_dyn_payload_page_bytes=1536, files=hashes, groups={})
    for name, arguments in groups.items():
        result['groups'][name] = analyze(*arguments)
    if any(sha(path) != hashes[str(path)] for path in paths):
        raise ValueError('Input/source changed')
    maximum = max(group['maximum_unique_pages'] for group in result['groups'].values())
    result.update(status='passed', selected_raw_budget_bytes=((maximum * 576 + (1 << 20) - 1) // (1 << 20)) * (1 << 20),
                  scope='Per-query unique-page upper bound, with complete fences between queries. Synthetic int64 codec only; NodeDyn bytes are payload arithmetic, not an implemented codec. Excludes host metadata, checkpoints, resident slots, global occupancy/history and concurrency. No timing/bandwidth claim.')
    out = ROOT / 'results' / ('query_page_demand_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    out.mkdir()
    (out / 'manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    (out / Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    print(out)
    print(json.dumps({name: {key: value for key, value in group.items() if key != 'per_query'} for name, group in result['groups'].items()}, indent=2))
    print('selected_raw_budget_bytes', result['selected_raw_budget_bytes'])


if __name__ == '__main__':
    main()
