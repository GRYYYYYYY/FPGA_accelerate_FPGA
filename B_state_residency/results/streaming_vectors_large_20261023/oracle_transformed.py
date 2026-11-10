"""Independent dictionary/transaction oracle; public-port commands only.

No import of RTL or cycle-level state. Real traces constrain every search read;
transport exports are also checked against backing before accepting COMPLETE.
"""
from collections import Counter, OrderedDict
from pathlib import Path
import hashlib
import json
import random
import struct
import sys

ROOT=Path(__file__).resolve().parents[2]
Q,B,R,W,U,WB,RF,BEAT,DONE,EXPORT,FENCE,FINISH=range(12)
OK,STALE,DIRTY,BAD,BUSY,EXHAUSTED,INCOMPLETE,WAIT=range(8)

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

class Oracle:
    def __init__(self,stream,tx_bits=16):
        self.stream=stream; self.limit=1<<tx_bits; self.active=None; self.draining=False
        self.used_queries=set(); self.last_gen={}; self.frames={}; self.issued=[]
        self.count=0; self.statuses=Counter(); self.ops=Counter(); self.fences=0
    def emit(self,op,slot=0,page=0,q=0,price=0,gen=0,tx=0,kind=0,present=0,
             off=0,field=0,value=0,payload=0,peer=0,empty=0,expect=None):
        key=(page,q,price,gen); f=self.frames.get(slot)
        bound=f is not None and f['key']==key
        current=self.active==(q,price)
        desc=bound and f['io'] is not None and f['io'][:2]==(tx,kind)
        status=OK; word=seen=dirty=outtx=0
        if op==Q:
            if self.draining:status=WAIT
            elif q in self.used_queries:status=EXHAUSTED
            else:self.active=(q,price);self.used_queries.add(q)
        elif op==B:
            if self.draining:status=WAIT
            elif not current:status=STALE
            elif f is not None:status=BUSY
            elif slot in self.last_gen and gen<=self.last_gen[slot]:status=EXHAUSTED
            else:
                self.frames[slot]=dict(key=key,words={},dirty=False,pristine=True,io=None)
                self.last_gen[slot]=gen
        elif op in (R,W):
            if not bound or not current or self.draining:status=STALE
            elif f['io'] is not None:status=BUSY
            elif op==W and (field>4 or (field==4 and value>255)):status=BAD
            else:
                if op==W:
                    width=8 if field==4 else 32
                    f['words'][off]=(f['words'].get(off,0)&~(((1<<width)-1)<<(field*32)))|(value<<(field*32))
                    f['dirty']=True;f['pristine']=False
                word=f['words'].get(off,0);seen=int(off in f['words']);dirty=int(f['dirty'])
        elif op==U:
            if not bound:status=STALE
            elif f['io'] is not None:status=BUSY
            elif f['dirty']:status=DIRTY;dirty=1
            else:del self.frames[slot]
        elif op in (WB,RF):
            if self.draining:status=WAIT
            elif not bound or (op==RF and not current):status=STALE
            elif f['io'] is not None:status=BUSY
            elif op==RF and not f['pristine']:status=BAD
            elif len(self.issued)==self.limit:status=EXHAUSTED
            else:
                outtx=len(self.issued);self.issued.append((slot,key,op==RF))
                f['io']=(outtx,int(op==RF),set())
                if op==RF:f['pristine']=False
        elif op in (BEAT,EXPORT):
            if not desc or kind!=int(op==BEAT):status=STALE
            elif off in f['io'][2]:status=BUSY
            elif op==BEAT and (payload>>136 or (not present and payload)):status=BAD
            else:
                if op==BEAT:
                    if present:f['words'][off]=payload;word=payload;seen=1
                else:word=f['words'].get(off,0);seen=int(off in f['words']);dirty=int(f['dirty'])
                f['io'][2].add(off)
        elif op==DONE:
            if not desc:status=STALE
            elif len(f['io'][2])!=64:status=INCOMPLETE
            else:f['io']=None;f['dirty']=False
        elif op==FENCE:
            if self.draining:status=BUSY
            elif any(f['dirty'] and f['io'] is None for f in self.frames.values()):status=DIRTY;dirty=1
            else:self.active=None;self.draining=True
        elif op==FINISH:
            if not self.draining or self.frames or not peer or not empty:status=WAIT
            else:
                self.draining=False;self.used_queries.clear();self.last_gen.clear();self.issued.clear();self.fences+=1
        else:status=BAD
        if expect is not None and status!=expect:raise AssertionError((self.count,op,status,expect))
        columns=(op,slot,page,q,price,gen,tx,kind,present,off,field,value,payload,peer,empty,
                 status,word,seen,dirty,outtx,int(self.draining))
        self.stream.emit_row(columns)
        self.count+=1;self.statuses[status]+=1;self.ops[op]+=1
        return status,word,seen,dirty,outtx
    def frame(self,op,slot=0,**kwargs):
        page,q,price,gen=self.frames[slot]['key']
        return self.emit(op,slot,page,q,price,gen,**kwargs)
    def move(self,slot,refill=None):
        tx=self.frame(RF if refill is not None else WB,slot,expect=OK)[4]
        for off in range(64):
            if refill is None:self.frame(EXPORT,slot,tx=tx,off=off,expect=OK)
            else:self.frame(BEAT,slot,tx=tx,kind=1,off=off,present=int(off in refill),payload=refill.get(off,0),expect=OK)
        self.frame(DONE,slot,tx=tx,kind=int(refill is not None),expect=OK)
        return tx
    def drain(self):
        for slot in list(self.frames):
            if self.frames[slot]['dirty']:self.move(slot)
            self.frame(U,slot,expect=OK)
        self.emit(FENCE,expect=OK);self.emit(FINISH,peer=1,empty=1,expect=OK)
    def summary(self):return dict(commands=self.count,status_counts=dict(self.statuses),op_counts=dict(self.ops),fences=self.fences)

def boundaries(o):
    o.emit(FINISH,peer=1,empty=1,expect=WAIT)
    for cycle in range(12):
        q=cycle%4;p=cycle%16
        o.emit(Q,q=q,price=p,expect=OK);o.emit(Q,q=q,price=p^1,expect=EXHAUSTED)
        o.emit(B,page=7,q=q,price=p,gen=0,expect=OK)
        for field,value in enumerate((0x7fc12345,0x80000000,0xffffffff,0x7fffffff,255)):
            o.frame(W,field=field,value=value,expect=OK)
        o.frame(W,field=4,value=256,expect=BAD);o.frame(W,field=7,expect=BAD)
        o.frame(U,expect=DIRTY);o.emit(FENCE,expect=DIRTY)
        # Four in-flight descriptors may complete out of order.
        for slot in (1,2,3):o.emit(B,slot=slot,page=7+slot,q=q,price=p,gen=0,expect=OK)
        tx0=o.frame(WB,expect=OK)[4]
        txs={s:o.frame(RF,s,expect=OK)[4] for s in (1,2,3)}
        for s in range(4):
            o.frame(R,s,expect=BUSY);o.frame(W,s,value=9,expect=BUSY);o.frame(U,s,expect=BUSY)
            o.frame(DONE,s,tx=tx0 if s==0 else txs[s],kind=int(s!=0),expect=INCOMPLETE)
        o.frame(DONE,tx=tx0,kind=1,expect=STALE)
        o.frame(DONE,tx=tx0^7,expect=STALE)
        # Every descriptor field has a negative completion check.
        for change in ({'page':8},{'q':q^1},{'price':p^1},{'gen':1},{'slot':1}):
            args=dict(slot=0,page=7,q=q,price=p,gen=0,tx=tx0);args.update(change)
            o.emit(DONE,**args,expect=STALE)
        o.frame(BEAT,1,tx=txs[1],kind=1,present=1,payload=1<<159,expect=BAD)
        o.frame(BEAT,1,tx=txs[1],kind=1,present=0,payload=1,expect=BAD)
        for off in range(63):
            o.frame(EXPORT,tx=tx0,off=off,expect=OK)
            for s in (3,1,2):o.frame(BEAT,s,tx=txs[s],kind=1,off=off,present=int(off%3==0),payload=(off+1 if off%3==0 else 0),expect=OK)
        o.frame(EXPORT,tx=tx0,off=0,expect=BUSY)
        o.frame(BEAT,1,tx=txs[1],kind=1,off=0,present=1,payload=9,expect=BUSY)
        o.frame(DONE,tx=tx0,expect=INCOMPLETE)
        o.frame(DONE,1,tx=txs[1],kind=1,expect=INCOMPLETE)
        # Switch queries while transfers are pending; old pages must stay hidden.
        o.emit(Q,q=q^1,price=p^1,expect=OK)
        o.frame(R,expect=STALE);o.frame(R,1,expect=STALE)
        o.emit(FENCE,expect=OK);o.emit(FENCE,expect=BUSY)
        o.emit(FINISH,peer=1,empty=1,expect=WAIT)
        o.emit(Q,q=q^2,expect=WAIT);o.frame(WB,expect=WAIT)
        for s in (3,0,2,1):
            t=tx0 if s==0 else txs[s];kind=int(s!=0)
            o.frame(EXPORT if s==0 else BEAT,s,tx=t,kind=kind,off=63,expect=OK)
            o.frame(DONE,s,tx=t,kind=kind,expect=OK)
            o.frame(DONE,s,tx=t,kind=kind,expect=STALE)
            o.frame(R,s,expect=STALE);o.frame(U,s,expect=OK)
        o.emit(FINISH,peer=0,empty=1,expect=WAIT);o.emit(FINISH,peer=1,empty=0,expect=WAIT)
        o.emit(FINISH,peer=1,empty=1,expect=OK)
        # Token allocation failures must neither wrap nor consume a binding.
        o.emit(Q,q=0,expect=OK);o.emit(B,page=9,gen=7,expect=OK)
        for _ in range(o.limit):o.move(0)
        o.frame(WB,expect=EXHAUSTED);o.frame(R,expect=OK);o.frame(U,expect=OK)
        o.emit(B,page=9,gen=0,expect=EXHAUSTED);o.emit(B,page=9,gen=7,expect=EXHAUSTED)
        o.emit(FENCE,expect=OK);o.emit(FINISH,peer=1,empty=1,expect=OK)
    # Deterministic interleaved legal and malformed commands, with exact failures.
    rng=random.Random(20261023)
    for epoch in range(16):
        o.emit(Q,q=epoch%4,price=epoch,expect=OK)
        for s in range(4):o.emit(B,slot=s,page=100+s,q=epoch%4,price=epoch,gen=0,expect=OK)
        for step in range(1000):
            s=rng.randrange(4);f=o.frames[s];op=rng.choice((R,W,RF,WB,BEAT,DONE,EXPORT,15))
            t,k,_=f['io'] if f['io'] else (0,0,set())
            args=dict(tx=t if rng.randrange(4) else t^1,kind=k,off=rng.randrange(64),
                      field=rng.randrange(8),value=rng.getrandbits(32),present=rng.randrange(2),payload=rng.getrandbits(136))
            if rng.randrange(20)==0:
                page,q,p,g=f['key'];o.emit(op,s,page^1,q,p,g,**args)
            else:o.frame(op,s,**args)
        for s in range(4):
            f=o.frames[s]
            if f['io']:
                t,k,done=f['io']
                for off in set(range(64))-done:o.frame(BEAT if k else EXPORT,s,tx=t,kind=k,off=off,expect=OK)
                o.frame(DONE,s,tx=t,kind=k,expect=OK)
        o.drain()

def real(o,capture,selected_attempts):
    counts=Counter();selected=[]
    with (capture/'trace.values').open('rb') as binary:
        for line in (capture/'trace.queries.jsonl').read_text().splitlines():
            row=json.loads(line)
            if row['attempt'] not in selected_attempts:continue
            q=counts['queries']%4;p=row['iteration'];o.emit(Q,q=q,price=p,expect=OK)
            selected.append(row['attempt']);counts['queries']+=1
            backing={};lru=OrderedDict();slots={};generations=[0]*4
            def evict(page):
                s=slots.pop(page)
                if o.frames[s]['dirty']:
                    o.move(s);counts['writebacks']+=1
                # Public exports in move compare every node with the independent
                # field-event word oracle; no direct DUT memory read is used.
                o.frame(U,s,expect=OK);del lru[page]
            binary.seek(row['byte_offset']);raw=binary.read(row['count']*20)
            if len(raw)!=row['count']*20:raise ValueError('Truncated actual trace')
            for node,source,bits,field,write,reserved,hist in struct.iter_unpack('<IIIBBHI',raw):
                if field>4 or write>1 or reserved:raise ValueError('Bad actual record')
                page,off=divmod(node,64)
                if page not in slots:
                    if len(slots)==4:evict(next(iter(lru)))
                    s=next(s for s in range(4) if s not in slots.values());generations[s]+=1
                    o.emit(B,s,page,q,p,generations[s],expect=OK);slots[page]=s;lru[page]=None
                    if page in backing:o.move(s,dict(backing[page]));counts['refills']+=1
                else:lru.move_to_end(page)
                s=slots[page];word=backing.get(page,{}).get(off,0);width=8 if field==4 else 32
                if write:
                    word=(word&~(((1<<width)-1)<<(field*32)))|(bits<<(field*32))
                    backing.setdefault(page,{})[off]=word
                    got=o.frame(W,s,off=off,field=field,value=bits,expect=OK)
                else:
                    if ((word>>(field*32))&((1<<width)-1))!=bits:raise ValueError('Actual read oracle mismatch')
                    got=o.frame(R,s,off=off,expect=OK)
                if got[1]!=word:raise ValueError('Independent page/trace oracle disagreement')
                counts['field_accesses']+=1
            for page in list(slots):evict(page)
            o.emit(FENCE,expect=OK);o.emit(FINISH,peer=1,empty=1,expect=OK)
    return dict(counts,selected_attempts=selected)

def main():
    out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
    capture=ROOT/'results/real_field_values_20261023T024250Z'
    frozen=json.loads((capture/'manifest.json').read_text());inputs=[Path(__file__).resolve()]
    for name in ('trace.values','trace.queries.jsonl'):
        p=capture/name
        if sha(p)!=frozen['artifacts'][str(p)]:raise ValueError('Capture changed')
        inputs.append(p)
    result=dict(status='running',files={str(p):sha(p) for p in inputs},cases={})
    for name,bits in (('boundaries',3),('actual',16)):
        path=out/(name+'.txt')
        if path.exists():raise ValueError('Never overwrite prior vectors')
        with path.open('w') as stream:
            o=Oracle(stream,bits)
            extra=boundaries(o) if bits==3 else real(o,capture)
        result['cases'][name]=dict(o.summary(),tx_bits=bits,generation_bits=bits,actual=extra)
        result['files'][str(path.resolve())]=sha(path)
    result['status']='passed';(out/'vectors_manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result['cases'],indent=2))

if __name__=='__main__':main()
