#!/usr/bin/env python3
"""Bound trace words from audited raw unknown sets without claiming exact size.

Streaming scanner is specific to the frozen site_runtime.cpp JSON serializer.
It is used only after validating the raw file hash against its full JSON audit.
"""
import argparse
import json
from pathlib import Path
import re
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
PATTERN=re.compile(r'"iterations":\[|"preparation_ms":|\{"status":"')
def scan(path):
    decoder=json.JSONDecoder();buffer='';position=0;eof=False;active=False;current=None;results=[]
    with path.open() as stream:
        while True:
            match=PATTERN.search(buffer,position)
            if match is None:
                if eof:break
                extra=stream.read(1024*1024);eof=not extra
                buffer=buffer[max(position,len(buffer)-40):]+extra;position=0
                continue
            token=match.group();position=match.end()
            if token=='"iterations":[':
                require(not active,'Nested batches');active=True;current=dict(searches=0,unknown_nodes=0,unknown_pips=0,search_words_lower_bound=0,status_counts={})
            elif token=='"preparation_ms":':
                require(active,'Batch end without iterations');active=False;results.append(current)
            elif active:
                start=match.start()
                while True:
                    try:record,end=decoder.raw_decode(buffer,start);break
                    except json.JSONDecodeError:
                        buffer=buffer[start:];start=0
                        extra=stream.read(1024*1024);require(extra,'Truncated audited search JSON')
                        buffer+=extra
                require(set(record)=={'status','cost','expanded','blocked','unknown_sources','unknown_pips'},'Changed raw search schema')
                nu=len(record['unknown_sources']);np=len(record['unknown_pips']);current['searches']+=1
                current['unknown_nodes']+=nu;current['unknown_pips']+=np;current['search_words_lower_bound']+=90+nu+np
                status=record['status'];current['status_counts'][status]=current['status_counts'].get(status,0)+1
                position=end
    require(not active and len(results)==2,'Incomplete raw batches');return results

def audit(output):
    require(not output.exists(),'Existing lower-bound report')
    proof=ROOT/'results/batch_router_audit_20261025_v1.json';d=json.loads(proof.read_text());require(d['status']=='batch_two_full_router_conditions_independently_verified','Missing full workload proof')
    bundle=ROOT/'data/derived/batch_router_full_20261025_v1';plan=json.loads((bundle/'plan.json').read_text());files={str(proof):digest(proof)};results=[]
    # Query/sink counts come from the immutable fixture, not inferred node counts.
    fixture=Path(plan['inputs']['csr']['fixture']);tokens=fixture.read_text().split();require(tokens[0]=='NATIVE_ROUTING_V1','Bad fixture')
    at=1;nodes=int(tokens[at]);at+=1
    for stride in [1,2,1]:
        count=int(tokens[at]);at+=1+stride*count
    nets=int(tokens[at]);at+=1;ns=0
    for _ in range(nets):
        count=int(tokens[at+2]);ns+=count;at+=3+count
    require(at==len(tokens),'Trailing fixture tokens');files[str(fixture)]=digest(fixture)
    for mode,index in [('csr',0),('compact',1)]:
        raw=bundle/f'worker_{index:03d}.raw.json';require(digest(raw)==d['files'][str(raw)],'Changed audited raw')
        batches=scan(raw);expected=d['results'][index]
        for batch,b in enumerate(batches):
            calls=expected['counters']['KERNEL_COUNTERS'][batch][1];net_calls=expected['counters']['SNAPSHOT_COUNTERS'][batch][1]
            require(b['searches']==calls and net_calls%nets==0,'Search/net counts differ from audited counters')
            rounds=net_calls//nets
            # At least one round snapshot; each nonterminal round advances both
            # histories and therefore has a post snapshot. Final may need one too.
            round_records=2*rounds-1
            begin=24+4*nets+(ns+1)//2
            minimum_round=42+2*nodes+(nets+1)//2
            total=begin+b['search_words_lower_bound']+121*net_calls+minimum_round*round_records+20
            b.update(mode=mode,batch=batch,nodes=nodes,nets=nets,sinks=ns,rounds=rounds,minimum_round_records=round_records,minimum_words=total,minimum_bytes=8*total,capacity_words=16777216,capacity_proven_insufficient=total>16777216)
            results.append(b)
        files[str(raw)]=digest(raw)
    for p in [Path(__file__).resolve(),ROOT/'hardware/vitis/search_trace_v2.hpp',ROOT/'hardware/vitis/search_trace_records.hpp',ROOT/'hardware/vitis/search_round_trace.hpp',ROOT/'hardware/vitis/search_batch_trace_frames.hpp',bundle/'plan.json']:
        files[str(p)]=digest(p)
    r=dict(status='audited_real_workload_diagnostic_trace_capacity_lower_bound_only',files=files,results=results,limits=['Not a hardware run or actual binary trace export','Omits all search path words, additional roots, nonminimal net snapshots and site state/history payloads','Lower bound above capacity proves insufficient; lower bound below capacity does not prove fit','No truncation or summary substitution is accepted as exact trace'])
    with output.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps(results),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();audit(a.output.resolve())
