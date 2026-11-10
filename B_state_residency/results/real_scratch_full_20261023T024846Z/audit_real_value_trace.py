"""Check explicit field records against a dense per-query bit-pattern oracle."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

RECORD = struct.Struct('<IIIBBHI')


def audit(prefix, node_count, expected_selection=None, sites=None):
    prefix = Path(prefix)
    offset = 0
    totals = dict(queries=0, accesses=0, reads=0, writes=0, maximum_unique_pages=0,
                  history_nondefault_observations=0, history_changed_between_selected_queries=0)
    seen = set(); rows = []; historical = {}
    with Path(str(prefix)+'.queries.jsonl').open() as metadata, Path(str(prefix)+'.values').open('rb') as events:
        for line in metadata:
            query = json.loads(line)
            if query['attempt'] in seen or query['byte_offset'] != offset or query['count'] != query['reads']+query['writes']:
                raise ValueError('Invalid query boundary/accounting')
            seen.add(query['attempt']); values = {}; history = {}; reads = writes = 0
            digest = hashlib.sha256()
            remaining = query['count']
            while remaining:
                count = min(remaining, 65536)
                raw = events.read(count*RECORD.size)
                if len(raw) != count*RECORD.size: raise ValueError('Truncated field record')
                digest.update(raw); offset += len(raw); remaining -= count
                for node, source, bits, field, write, reserved, hist in RECORD.iter_unpack(raw):
                    if not 0 <= node < node_count or field >= 5 or write not in (0,1) or reserved or source <= 0:
                        raise ValueError('Invalid field record')
                    if field == 4 and bits > 255: raise ValueError('Invalid target bits')
                    if sites is not None and (source, field, bool(write)) not in sites:
                        raise ValueError('Uncovered source field site')
                    state = values.setdefault(node, [0]*5)
                    if write: state[field] = bits; writes += 1
                    else:
                        if state[field] != bits: raise ValueError(f'Read mismatch: attempt={query["attempt"]}, node={node}, field={field}')
                        reads += 1
                    if node in history and history[node] != hist:
                        raise ValueError('History changed within frozen serial query')
                    history[node] = hist
            if (reads,writes) != (query['reads'],query['writes']): raise ValueError('Read/write counts differ')
            pages = len({node >> 6 for node in values})
            totals['queries'] += 1; totals['accesses'] += query['count']; totals['reads'] += reads; totals['writes'] += writes
            totals['maximum_unique_pages'] = max(totals['maximum_unique_pages'],pages)
            totals['history_nondefault_observations'] += sum(bits != 0x3f800000 for bits in history.values())
            totals['history_changed_between_selected_queries'] += sum(node in historical and historical[node] != bits for node,bits in history.items())
            historical.update(history)
            rows.append(dict(query, unique_pages=pages, raw_sha256=digest.hexdigest()))
        if events.read(1): raise ValueError('Trailing field records')
    if expected_selection is not None and seen != set(expected_selection): raise ValueError('Selected queries missing/extra')
    return dict(status='passed', totals=totals, queries=rows, record_bytes=RECORD.size,
                scope='Actual five-field read/write trace consistency, float/int bits exact; history observed separately and constant within each selected serial query. Does not replay price calculation or prove a transport implementation.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('prefix',type=Path); parser.add_argument('--nodes',type=int,default=9089009)
    args = parser.parse_args(); result = audit(args.prefix,args.nodes)
    Path(str(args.prefix)+'.audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result['totals'],indent=2))
