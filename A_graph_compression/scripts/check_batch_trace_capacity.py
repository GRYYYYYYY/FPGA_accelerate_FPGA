#!/usr/bin/env python3
"""Independently check exact-fit acceptance and every exported overflow prefix."""
import argparse
import json
from pathlib import Path
import struct
from check_vitis_kernel import digest,require
from read_batch_trace_v2 import decode_words
ROOT=Path(__file__).resolve().parents[1]
def read(p):
    raw=p.read_bytes();require(len(raw)%8==0,'Unaligned trace')
    return list(struct.unpack('<%dQ'%(len(raw)//8),raw))
def split(w):
    records=[];at=8
    while at<len(w):
        require(at+2<=len(w),'Truncated header');size=w[at+1];require(size>=8 and at+size<=len(w),'Partial committed frame')
        records.append(w[at:at+size]);at+=size
    require(len(records)==w[3],'Record count mismatch');return records
def audit(bundle,output):
    require(not output.exists(),'Existing capacity audit')
    state=json.loads((bundle/'state.json').read_text());require(state['status']=='complete' and state['completed']==[0,1],'Incomplete CPU test')
    files=json.loads((bundle/'files.json').read_text())
    for p,h in files.items():require(digest(p)==h,'Changed test input/output '+p)
    for mode in [0,1]:
        for phase in ['compile','run']:
            log=bundle/f'{phase}_{mode}.log';receipt=json.loads((bundle/f'{phase}_{mode}.receipt.json').read_text())
            require(receipt['exit_code']==0 and receipt['log_sha256']==digest(log),'Failed sanitizer phase')
        require(f'BATCH_TRACE_CAPACITY_PASS mode={mode} cuts=16 exact_fit=1 invalid_controls=3' in (bundle/f'run_{mode}.log').read_text(),'Missing capacity contract marker')
        exact=read(bundle/f'mode_{mode}_exact_fit.bin');require(exact[1]==exact[2] and decode_words(exact,4)['complete_batch'],'Exact fit did not validate')
        baseline=split(exact);cases=list(bundle.glob(f'mode_{mode}_capacity_*.bin'));require(len(cases)==16,'Missing capacity cuts')
        for path in cases:
            w=read(path);capacity=int(path.stem.rsplit('_',1)[1])
            require(w[1]==capacity and w[2]<=capacity and w[4]==2 and w[5]==w[3]+1 and len(w)==8+w[2],'Wrong overflow metadata')
            try:decode_words(w,4)
            except ValueError:pass
            else:raise ValueError('Overflow accepted as complete batch')
            records=split(w);require(len(records)<len(baseline),'Overflow unexpectedly committed terminal')
            delta=None
            for actual,expected in zip(records,baseline):
                a=actual.copy();b=expected.copy()
                if a[0]==1:
                    current=a[21]-b[21]
                    if delta is None:delta=current
                    require(delta==current,'Unexpected epoch progression within prefix');a[21]=b[21]
                require(a==b,'Non-epoch payload changed under capacity cut')
            require(w[2]+len(baseline[len(records)])>capacity,'Sticky trace stopped before a capacity failure')
    dependencies=[Path(__file__).resolve(),ROOT/'scripts/read_batch_trace_v2.py',ROOT/'scripts/read_batch_trace.py',ROOT/'scripts/read_search_trace.py',ROOT/'scripts/read_net_trace.py',ROOT/'scripts/read_round_trace.py',bundle/'files.json']
    for p in dependencies:files[str(p)]=digest(p)
    r=dict(status='diagnostic_batch_both_modes_atomic_capacity_prefix_and_exact_fit_cpu_verified',files=files,modes=2,capacity_cuts_per_mode=16,invalid_trace_controls_per_mode=3,exact_fit_per_mode=1,limits=['Synthetic CPU entry under ASAN/UBSAN; no generated RTL or board execution','Search epoch changes across invocations are checked as a constant prefix offset, all other committed words are exact','Overflow metadata is rejected by independent mixed reader, even when routing itself succeeded','Original failed v1 test assumed identical epochs; no kernel change was needed'])
    with output.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
    print(r['status'])
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();audit(a.bundle.resolve(),a.output.resolve())
