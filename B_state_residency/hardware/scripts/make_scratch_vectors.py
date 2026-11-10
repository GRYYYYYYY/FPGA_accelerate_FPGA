"""Create public-interface RTL commands from complete small actual-value queries."""
from collections import OrderedDict
import json
from pathlib import Path
import struct
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha


def main():
    capture=ROOT/'results/real_field_values_20261023T024250Z'
    manifest=json.loads((capture/'manifest.json').read_text())
    if manifest['status']!='passed':raise ValueError('Capture incomplete')
    binary=capture/'trace.values';metadata=capture/'trace.queries.jsonl'
    for path in (binary,metadata):
        if sha(path)!=manifest['artifacts'][str(path)]:raise ValueError('Actual trace changed')
    out=ROOT/'results/rtl_scratch_20261023';path=out/'actual_vectors.txt'
    if path.exists():raise ValueError('Do not overwrite frozen vectors')
    commands=0;queries=0;accesses=0;generations=[1]*4;selected=[];exports=loads=0
    with path.open('w') as stream,binary.open('rb') as events,metadata.open() as rows:
        def emit(op,slot,page,query,price,gen,offset=0,field=0,value=0,payload=0,status=0,expected=0,present=0,dirty=0):
            nonlocal commands
            columns=(op,slot,page,query,price,gen,offset,field,value,payload,status,expected,present,dirty)
            stream.write(' '.join(format(value,'x') for value in columns)+'\n');commands+=1
        for line in rows:
            row=json.loads(line)
            if row['count']>100000:continue
            query=queries%4;price=row['iteration'];selected.append(row['attempt']);queries+=1
            events.seek(row['byte_offset']);raw=events.read(row['count']*20)
            if len(raw)!=row['count']*20:raise ValueError('Truncated actual field query')
            backing={};lru=OrderedDict();frames={};dirty_pages=set()
            def remove(page):
                nonlocal exports
                slot=frames[page];gen=generations[slot]
                if page in dirty_pages:
                    # Every live label is checked at the RTL read port before CLEAN.
                    for offset,word in backing[page].items():
                        emit(1,slot,page,query,price,gen,offset,expected=word,present=1,dirty=1);exports+=1
                    emit(3,slot,page,query,price,gen);dirty_pages.remove(page)
                emit(4,slot,page,query,price,gen);del frames[page];del lru[page]
            for node,source,bits,field,write,reserved,hist in struct.iter_unpack('<IIIBBHI',raw):
                if field>4 or write>1 or reserved:raise ValueError('Invalid actual field event')
                page=node>>6;offset=node&63
                if page not in frames:
                    if len(frames)==4:remove(next(iter(lru)))
                    slot=next(slot for slot in range(4) if slot not in frames.values())
                    generations[slot]+=1;gen=generations[slot];frames[page]=slot;lru[page]=None
                    emit(0,slot,page,query,price,gen)
                    for saved_offset,word in backing.get(page,{}).items():
                        emit(5,slot,page,query,price,gen,saved_offset,payload=word,expected=word,present=1);loads+=1
                else:lru.move_to_end(page)
                slot=frames[page];gen=generations[slot]
                word=backing.get(page,{}).get(offset,0)
                if write:
                    width=8 if field==4 else 32;shift=field*32
                    word=(word&~(((1<<width)-1)<<shift))|(bits<<shift)
                    backing.setdefault(page,{})[offset]=word;dirty_pages.add(page)
                    emit(2,slot,page,query,price,gen,offset,field,bits,expected=word,present=1,dirty=1)
                else:
                    if ((word>>(field*32))&((1<<(8 if field==4 else 32))-1))!=bits:
                        raise ValueError('Captured actual read does not match vector oracle')
                    emit(1,slot,page,query,price,gen,offset,expected=word,
                         present=int(offset in backing.get(page,{})),dirty=int(page in dirty_pages))
                accesses+=1
            for page in list(frames):remove(page)
    record=dict(status='passed',queries=queries,actual_field_accesses=accesses,commands=commands,
                export_label_reads=exports,restored_labels=loads,selected_attempts=selected,
                files={str(p):sha(p) for p in (Path(__file__).resolve(),binary,metadata,path)},
                scope='Full selected small actual queries, 4 slots, exact public-port export checks before trusted CLEAN and reload input. External backing is a testbench/reference source, not a DMA controller; no finite wrap/fence proof.')
    (out/'vectors_manifest.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k!='files'},indent=2))


if __name__=='__main__':main()
