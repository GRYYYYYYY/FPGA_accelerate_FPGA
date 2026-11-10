"""Real TLD addresses, synthetic values: stress page state preservation only."""
from collections import OrderedDict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import os
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from lifecycle import Authority, Context, Replica
from page_residency import ResidentPages


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(1 << 20), b''):
            digest.update(data)
    return digest.hexdigest()


def final_values(pages):
    values = dict(pages.backing)
    for slot in pages.slots:
        if slot.query is pages.query:
            if slot.transfer:
                raise ValueError('Final validation requires completed current-query IO')
            values[slot.page] = slot.values
    return {(page << pages.page_bits) | offset: value
            for page, entries in values.items() for offset, value in entries.items()}


def replay(prefix, progress):
    authority = Authority({})
    replica = Replica(authority.design)
    context = Context(authority, replica, 0, epoch_bits=2)
    pages = ResidentPages(context, capacity=4, page_bits=6)
    totals = dict(queries=0, accesses=0, hits=0, first_pages=0, writebacks=0,
                  refills=0, stale_completions_discarded=0)
    pending_old = None
    with prefix.with_suffix('.jsonl').open() as records, prefix.with_suffix('.accesses').open('rb') as binary:
        offset = 0
        for line in records:
            row = json.loads(line)
            if row['access_byte_offset'] != offset:
                raise ValueError('Access offset mismatch')
            if not row['accesses_selected']:
                if row['access_count']:
                    raise ValueError('Unexpected unselected events')
                continue
            if row['truncated'] or row['access_count'] != row['label_accesses']:
                raise ValueError('Incomplete query')
            raw = binary.read(row['access_count'] * 8)
            if len(raw) != row['access_count'] * 8:
                raise ValueError('Truncated binary')
            offset += len(raw)
            query = context.begin()
            pages.bind(query)
            if pending_old is not None:
                if pages.slots[pending_old.slot].query is not pending_old.query:
                    raise AssertionError('Cancelled transfer lost its slot lease before ack')
                if pages.complete(pending_old):
                    raise AssertionError('Old query transfer accepted')
                totals['stale_completions_discarded'] += 1
            oracle, lru = {}, OrderedDict()
            for sequence, (node, source_line) in enumerate(struct.iter_unpack('<ii', raw), 1):
                if not 0 <= node < 9089009 or source_line <= 0:
                    raise ValueError('Invalid address trace')
                page = node >> 6
                if page in lru:
                    totals['hits'] += 1
                    lru.move_to_end(page)
                else:
                    if len(lru) == 4:
                        victim, _ = lru.popitem(last=False)
                        token = pages.evict(query, victim)
                        if token is not None:
                            pages.complete(token)
                            totals['writebacks'] += 1
                    token = pages.request(query, page)
                    if token is not None:
                        pages.complete(token)
                        totals['refills'] += 1
                    else:
                        totals['first_pages'] += 1
                    lru[page] = None
                if pages.read(query, node) != oracle.get(node):
                    raise AssertionError('Value lost across page eviction/refill')
                # Values deliberately do NOT model the route's actual distance.
                pages.write(query, node, sequence)
                oracle[node] = sequence
            if final_values(pages) != oracle:
                raise AssertionError('Final resident+backing state differs from independent oracle')
            totals['queries'] += 1
            totals['accesses'] += row['access_count']
            pending_old = pages.evict(query, next(iter(lru))) if lru else None
            context.finish(query)
            progress(dict(totals))
        if binary.read(1):
            raise ValueError('Trailing access data')
    if pending_old is not None:
        if pages.complete(pending_old):
            raise AssertionError('Finished query completion accepted')
        totals['stale_completions_discarded'] += 1
    totals['context_wraps'] = context.incarnation
    return totals


def main():
    if not __debug__:
        raise RuntimeError('Assertions must remain enabled')
    out = ROOT / 'results' / ('page_protocol_real_addresses_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    out.mkdir()
    base = ROOT / 'results/real_trace_20261022T165136Z'
    groups = {'interval_sample': (base / 'trace_0', 1113, 2399968),
              'large_query_tail': (base / 'tail/trace', 19, 13751567)}
    sources = [Path(__file__).resolve(), ROOT / 'src/page_residency.py', ROOT / 'src/lifecycle.py']
    inputs = [p.with_suffix(s) for p, _, _ in groups.values() for s in ('.jsonl', '.accesses')]
    record = dict(status='running', runner_pid=os.getpid(), execution_kind='real_address_synthetic_value_protocol_replay',
                  performance=None, page_bits=6, physical_slots=4, groups={},
                  scope='CPU TLD addresses with synthetic monotonically numbered writes, not real distance values or actual router search. Sequential transfer events; no DMA/RTL/concurrent/finite-width proof. No time or bandwidth claim.',
                  files={str(p): sha(p) for p in sources + inputs})
    def save():
        temp = out / 'manifest.json.tmp'
        temp.write_text(json.dumps(record, indent=2) + '\n')
        temp.replace(out / 'manifest.json')
    for source in sources:
        (out / source.name).write_bytes(source.read_bytes())
    save()
    try:
        for name, (prefix, queries, accesses) in groups.items():
            def progress(counts):
                record['groups'][name] = counts
                if counts['queries'] % 25 == 0 or name == 'large_query_tail':
                    save()
                    print(name, counts['queries'], 'queries verified', flush=True)
            result = replay(prefix, progress)
            if result['queries'] != queries or result['accesses'] != accesses:
                raise ValueError('Unexpected selected query/access totals')
            record['groups'][name] = result
            save()
        if any(sha(p) != record['files'][str(p)] for p in sources + inputs):
            raise ValueError('Source or trace changed')
        record['status'] = 'passed'
    except Exception as error:
        record.update(status='failed', error=repr(error))
        raise
    finally:
        save()
    print(out, flush=True)


if __name__ == '__main__':
    main()
