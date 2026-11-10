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
from read_trace_set_codec import rle_byte_count
import os
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
                require(not active,'Nested batches');active=True;current=dict(searches=0,unknown_nodes=0,unknown_pips=0,search_words_lower_bound=0,status_counts={},encoded_set_words=0,node_encoded_bytes=0,pip_encoded_bytes=0,raw_fallback_sets=0)
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
                node_keys=record['unknown_sources'];pip_keys=[(tile<<32)|pip for tile,pip in record['unknown_pips']]
                require(all(a<b for a,b in zip(node_keys,node_keys[1:])) and all(a<b for a,b in zip(pip_keys,pip_keys[1:])),'Unordered unknown set')
                for name,keys in [('node',node_keys),('pip',pip_keys)]:
                    raw_bytes=8*len(keys);rle=rle_byte_count(keys);encoded=min(raw_bytes,rle)
                    current[name+'_encoded_bytes']+=encoded;current['encoded_set_words']+=(encoded+7)//8
                    current['raw_fallback_sets']+=rle>=raw_bytes
                status=record['status'];current['status_counts'][status]=current['status_counts'].get(status,0)+1
                position=end
    require(not active and len(results)==2,'Incomplete raw batches');return results

def main():
    out=ROOT/'data/derived/trace_set_codec_real_20261025_v1';out.mkdir(exist_ok=False)
    proof=ROOT/'results/batch_trace_real_capacity_review_20261025_v1.json';review=json.loads(proof.read_text())
    bound=ROOT/'results/batch_trace_real_capacity_lower_bound_20261025_v1.json';baseline=json.loads(bound.read_text())
    files={str(proof):digest(proof),str(bound):digest(bound),str(Path(__file__).resolve()):digest(__file__),str(ROOT/'scripts/read_trace_set_codec.py'):digest(ROOT/'scripts/read_trace_set_codec.py')}
    state=dict(status='running',owner_pid=os.getpid(),completed=[])
    def save():
        p=out/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(out/'state.json')
    save();results=[]
    try:
        for mode,index in [('csr',0),('compact',1)]:
            path=ROOT/f'data/derived/batch_router_full_20261025_v1/worker_{index:03d}.raw.json'
            require(digest(path)==review['files'][str(path)],'Changed audited raw');files[str(path)]=digest(path)
            batches=scan(path)
            for batch,row in enumerate(batches):
                old=next(r for r in baseline['results'] if r['mode']==mode and r['batch']==batch)
                require(all(row[k]==old[k] for k in ['searches','unknown_nodes','unknown_pips']),'Different workload statistics')
                words=old['minimum_words']-row['unknown_nodes']-row['unknown_pips']+row['encoded_set_words']+4*row['searches']
                row.update(mode=mode,batch=batch,proposed_format_lower_bound_words=words,proposed_format_lower_bound_bytes=8*words,capacity_proven_insufficient=words>16777216)
                results.append(row)
            state['completed'].append(mode);save()
        for p,h in files.items():require(digest(p)==h,'Changed measurement input')
        report=dict(status='real_unknown_set_lossless_run_encoding_size_measured_full_trace_fit_unproven',files=files,results=results,limits=['Exact selected-codec unknown set byte sizes from audited raw sets, not a synthesized encoder run','Proposed trace format charges two descriptor words per set','Full-path/root/net/site overhead still only lower bounded; below 128MiB does not prove full trace fit','No top integration, HLS/RTL or device proof'])
        with (ROOT/'results/trace_set_codec_real_20261025_v1.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
        state.update(status='complete');save()
    except BaseException as e:state.update(status='failed',error=str(e));save();raise
if __name__=='__main__':main()
