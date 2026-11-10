"""Real TLD addresses with finite IDs, checkpoint fences, and synthetic values."""
from collections import OrderedDict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import os
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.finite_page_values import FinitePageValues
from src.finite_completion import WouldBlock
from src.finite_completion_fast import SequentialFiniteDomain
from src.fence_control import FenceControl


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(1 << 20), b''):
            digest.update(data)
    return digest.hexdigest()


def final_values(pages, query):
    values=dict(pages.backing[query])
    for binding in pages.domain.bindings:
        if binding is not None and binding.query==query:values[binding.page]=pages.values[binding.slot]
    return {(page<<pages.page_bits)|offset:value for page,entries in values.items() for offset,value in entries.items()}


def replay(prefix, progress, *, widths=None):
    configuration=dict(slots=4,page_bits=6,page_id_bits=18,transaction_bits=16,query_bits=2,generation_bits=16,price_bits=4)
    configuration.update(widths or {})
    pages=FinitePageValues(**configuration)
    domain_config={k:v for k,v in configuration.items() if k not in ('page_bits','page_id_bits','queue_capacity')}
    domain_config['page_bits']=configuration['page_id_bits']
    pages.link.domain=SequentialFiniteDomain(**domain_config)
    control=FenceControl(pages,tag_bits=2,capacity=4)
    totals=dict(queries=0,accesses=0,hits=0,checkpoints=0,fences=0,stale_completions_discarded=0,boundary_probe_skips=0,control_requests=0,control_ack_packets=0,control_duplicate_acks=0,control_tag_wraps=0)
    def flush():
        while pages.link.requests:pages.dispatch()
        while pages.link.work:pages.publish()
        while pages.link.responses:
            _,status=pages.deliver()
            if status=='stale':totals['stale_completions_discarded']+=1
    def fence():
        control.begin();control.duplicate_request();totals['control_requests']+=2
        flush()
        while control.requests:control.service()
        control.duplicate_ack();totals['control_ack_packets']+=3
        while control.acks:
            if control.receive()=='duplicate':totals['control_duplicate_acks']+=1
        control.finish();totals['fences']+=1
        if control.next_tag==0:totals['control_tag_wraps']+=1
    with prefix.with_suffix('.jsonl').open() as records,prefix.with_suffix('.accesses').open('rb') as binary:
        offset=0
        for line in records:
            row=json.loads(line)
            if row['access_byte_offset']!=offset:raise ValueError('Access offset mismatch')
            if not row['accesses_selected']:
                if row['access_count']:raise ValueError('Unexpected unselected events')
                continue
            if row['truncated'] or row['access_count']!=row['label_accesses']:raise ValueError('Incomplete query')
            raw=binary.read(row['access_count']*8)
            if len(raw)!=row['access_count']*8:raise ValueError('Truncated binary')
            offset+=len(raw);query=pages.begin_query(0);oracle={};lru=OrderedDict()
            for sequence,(node,source_line) in enumerate(struct.iter_unpack('<ii',raw),1):
                if not 0<=node<9089009 or source_line<=0:raise ValueError('Invalid address trace')
                page=node>>6
                for attempt in range(2):
                    try:
                        if page in lru:totals['hits']+=1;lru.move_to_end(page)
                        else:
                            if len(lru)==4:
                                victim=next(iter(lru));pages.evict(query,victim);flush();del lru[victim]
                            pages.request(query,page);flush();lru[page]=None
                        break
                    except WouldBlock:
                        if attempt:raise RuntimeError('Access still blocked after checkpoint fence')
                        flush();snapshot=pages.checkpoint(query)
                        if final_values(pages,query)!=oracle:raise AssertionError('Checkpoint source state lost values')
                        fence();query=pages.begin_query(snapshot.price);pages.restore(query,snapshot);lru.clear();totals['checkpoints']+=1
                if pages.read(query,node)!=oracle.get(node):raise AssertionError('Value lost across finite IO/fence')
                pages.write(query,node,sequence);oracle[node]=sequence
            flush()
            if final_values(pages,query)!=oracle:raise AssertionError('Final values mismatch')
            # Delay a real dirty writeback until cancellation; backing stays in old namespace.
            if lru and len(pages.domain.used_transactions)<pages.domain.transaction_limit:
                pages.evict(query,next(iter(lru)))
            elif lru:totals['boundary_probe_skips']+=1
            fence();totals['queries']+=1;totals['accesses']+=row['access_count']
            totals.update(writebacks=pages.writeback_effects,refills=pages.refill_effects)
            progress(dict(totals))
        if binary.read(1):raise ValueError('Trailing access data')
    return totals


def main():
    if not __debug__:
        raise RuntimeError('Assertions must remain enabled')
    out = ROOT / 'results' / ('finite_control_real_addresses_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    out.mkdir()
    base = ROOT / 'results/real_trace_20261022T165136Z'
    groups = {'interval_sample': (base / 'trace_0', 1113, 2399968),
              'large_query_tail': (base / 'tail/trace', 19, 13751567)}
    sources = [Path(__file__).resolve(), ROOT / 'src/finite_page_values.py', ROOT / 'src/finite_transport.py', ROOT / 'src/finite_completion.py', ROOT / 'src/finite_completion_fast.py', ROOT / 'src/fence_control.py']
    inputs = [p.with_suffix(s) for p, _, _ in groups.values() for s in ('.jsonl', '.accesses')]
    record = dict(status='running', runner_pid=os.getpid(), execution_kind='finite_real_address_synthetic_value_replay',
                  performance=None, page_bits=6, physical_slots=4, groups={},
                  scope='CPU TLD addresses with synthetic monotonically numbered writes, not real distance values or actual router search. Finite allocator and explicit 2-bit fence control packets with queued duplicate requests/ACKs, closed queue events and midquery actual-state checkpoints; no DMA/RTL/concurrent or real distance proof. No time or bandwidth claim.',
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
