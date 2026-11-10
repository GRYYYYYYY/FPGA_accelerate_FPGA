"""Replay captured actual scratch fields through finite queues and bounded raw backing."""
import argparse
from collections import OrderedDict
from dataclasses import replace
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha
from audit_real_value_trace import RECORD
from src.scratch_page_values import ScratchLabel, ScratchPageValues
from src.finite_completion import WouldBlock
from src.finite_completion_fast import SequentialFiniteDomain
from src.fence_control import FenceControl

FIELDS = ('lb_bits','upstream_bits','prev','visited','target')


def logical_values(pages, query):
    result = {}
    for owner,page in pages.pool.owners:
        if owner == query:
            result.update({page*64+offset:value for offset,value in pages.codec.decode(pages.pool.read((owner,page))).items()})
    for binding in pages.domain.bindings:
        if binding and binding.query == query:
            result.update({binding.page*64+offset:value for offset,value in pages.values[binding.slot].items()})
    return result


def replay(prefix, selected, progress, transaction_bits):
    widths = dict(slots=4,page_bits=18,transaction_bits=transaction_bits,query_bits=2,generation_bits=transaction_bits,price_bits=4)
    configuration = dict(widths); configuration['page_id_bits']=configuration.pop('page_bits')
    pages = ScratchPageValues(backing_bytes=30*(1<<20),page_bits=6,**configuration)
    pages.link.domain = SequentialFiniteDomain(**widths)
    control = FenceControl(pages,tag_bits=2,capacity=4)
    totals = dict(queries=0,accesses=0,reads=0,writes=0,hits=0,checkpoints=0,fences=0,
                  duplicate_acks=0,stale_completions=0,late_writeback_probes=0,peak_backing_pages=0)
    def flush():
        while pages.link.requests: pages.dispatch()
        while pages.link.work: pages.publish()
        while pages.link.responses:
            _,status=pages.deliver()
            if status=='stale': totals['stale_completions']+=1
    def fence():
        control.begin(); control.duplicate_request(); flush()
        while control.requests: control.service()
        control.duplicate_ack()
        while control.acks:
            if control.receive()=='duplicate': totals['duplicate_acks']+=1
        control.finish(); totals['fences']+=1
    offset=0
    with Path(str(prefix)+'.queries.jsonl').open() as metadata, Path(str(prefix)+'.values').open('rb') as events:
        for line in metadata:
            row=json.loads(line)
            if row['byte_offset']!=offset: raise ValueError('Query offset mismatch')
            size=row['count']*RECORD.size; offset+=size
            if row['attempt'] not in selected:
                events.seek(size,1); continue
            raw=events.read(size)
            if len(raw)!=size: raise ValueError('Truncated real field trace')
            query=pages.begin_query(row['iteration']); oracle={}; lru=OrderedDict(); read_count=write_count=0
            for node,source,bits,field,write,reserved,hist in RECORD.iter_unpack(raw):
                if not 0<=node<9089009 or field>=5 or write not in (0,1) or reserved or source<=0:
                    raise ValueError('Invalid field record')
                page=node>>6
                for attempt in range(2):
                    try:
                        if page in lru: totals['hits']+=1; lru.move_to_end(page)
                        else:
                            if len(lru)==4:
                                victim=next(iter(lru)); pages.evict(query,victim); flush(); del lru[victim]
                            pages.request(query,page); flush(); lru[page]=None
                        break
                    except WouldBlock:
                        if attempt: raise RuntimeError('Still blocked after same-query checkpoint fence')
                        flush(); snapshot=pages.checkpoint(query)
                        if logical_values(pages,query)!=oracle: raise AssertionError('Raw checkpoint state mismatch')
                        fence(); query=pages.begin_query(snapshot.price); pages.restore(query,snapshot); lru.clear(); totals['checkpoints']+=1
                actual=pages.read(query,node) or ScratchLabel()
                expected=oracle.get(node,ScratchLabel())
                if actual!=expected: raise AssertionError('Scratch fields lost across IO')
                if write:
                    value=bits-(1<<32) if field in (2,3) and bits>=(1<<31) else bits
                    pages.write(query,node,replace(actual,**{FIELDS[field]:value}))
                    oracle[node]=replace(expected,**{FIELDS[field]:value}); write_count+=1
                else:
                    if getattr(actual,FIELDS[field]) & 0xffffffff != bits:
                        raise AssertionError('Actual router read bits differ from bounded page model')
                    read_count+=1
                totals['peak_backing_pages']=max(totals['peak_backing_pages'],len(pages.pool.owners))
            if (read_count,write_count)!=(row['reads'],row['writes']): raise ValueError('Query operation counts differ')
            if logical_values(pages,query)!=oracle: raise AssertionError('Final raw scratch state mismatch')
            dirty=next((binding for binding in pages.domain.bindings if binding and pages.dirty[binding.slot]),None)
            if dirty and len(pages.domain.used_transactions)<pages.domain.transaction_limit:
                pages.evict(query,dirty.page); totals['late_writeback_probes']+=1
            fence(); totals['queries']+=1; totals['accesses']+=row['count']; totals['reads']+=read_count; totals['writes']+=write_count
            totals.update(writebacks=pages.writeback_effects,refills=pages.refill_effects)
            progress(dict(totals))
        if events.tell()!=Path(str(prefix)+'.values').stat().st_size or events.read(1): raise ValueError('Trace byte coverage mismatch')
    return totals


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot',action='store_true'); args=parser.parse_args()
    capture=ROOT/'results/real_field_values_20261023T024250Z'
    reference=json.loads((capture/'manifest.json').read_text())
    completion=json.loads((capture/'completion_audit.json').read_text())
    if reference['status']!='passed' or completion['status']!='passed' or completion['manifest_sha256']!=sha(capture/'manifest.json'):
        raise ValueError('Real trace capture not audited')
    for path,digest in reference['artifacts'].items():
        if sha(path)!=digest: raise ValueError('Real capture artifact changed')
    trace=json.loads((capture/'trace.audit.json').read_text())
    selected={row['attempt'] for row in trace['queries'] if not args.pilot or row['count']<=100000}
    expected={key:sum(row[key] for row in trace['queries'] if row['attempt'] in selected) for key in ('count','reads','writes')}
    out=ROOT/'results'/(('real_scratch_pilot_' if args.pilot else 'real_scratch_full_')+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')); out.mkdir()
    sources=[Path(__file__).resolve(),ROOT/'scripts/audit_real_value_trace.py', *[ROOT/'src'/name for name in ('scratch_page_values.py','bounded_backing.py','finite_page_values.py','finite_transport.py','finite_completion.py','finite_completion_fast.py','fence_control.py')]]
    inputs=[capture/'manifest.json',capture/'completion_audit.json',capture/'trace.audit.json',capture/'trace.queries.jsonl',capture/'trace.values']
    files={str(path):sha(path) for path in sources+inputs}
    for source in sources: (out/source.name).write_bytes(source.read_bytes())
    record=dict(status='running',runner_pid=os.getpid(),performance=None,selected_attempts=sorted(selected),pilot=args.pilot,
                backing_budget_bytes=30*(1<<20),stride_bytes=1344,physical_slots=4,transaction_bits=10 if args.pilot else 16,files=files,
                scope='Actual five-field bit-pattern trace replay, fixed raw backing and finite data/control queues. Global hist is not transported or recomputed; query iteration used as a bounded price tag. Host metadata/checkpoints excluded. Not actual router execution on a device or hardware performance.')
    def save():
        temp=out/'manifest.json.tmp';temp.write_text(json.dumps(record,indent=2)+'\n');temp.replace(out/'manifest.json')
    def progress(counts):
        record['totals']=counts;save();print(counts['queries'],'queries verified',flush=True)
    save();print(out,flush=True)
    try:
        result=replay(capture/'trace',selected,progress,record['transaction_bits'])
        if (result['queries'],result['accesses'],result['reads'],result['writes'])!=(len(selected),expected['count'],expected['reads'],expected['writes']):
            raise ValueError('Real field coverage mismatch')
        if any(sha(path)!=digest for path,digest in files.items()):raise ValueError('Frozen source/input changed')
        record.update(status='passed',totals=result)
    except Exception as error:
        record.update(status='failed',error=repr(error)); raise
    finally: save()


if __name__=='__main__': main()
