#!/usr/bin/env python3
"""Independent full-output comparison of bounded-heap router to frozen STL router."""
import gc
import json
import math
from pathlib import Path
import re
from prepare_label_index_router import ROOT,OUT,digest

METRICS={'preparation_ms','route_ms','peak_kib','logical_bytes','cache_hits','cache_misses'}

def require(ok,message):
    if not ok:raise ValueError(message)

def audit():
    pp=OUT/'plan.json';plan=json.loads(pp.read_text())
    for p,h in {**plan['files'],**plan['generated']}.items():require(digest(p)==h,'Changed frozen input '+p)
    files={str(pp):digest(pp)};results=[];reference=None;cached_mode=None
    expected=[('csr','direct',122),('csr','expanded',124),('compact','direct',125),('compact','expanded',126)]
    require([(j['mode'],j['execution'],j['cpu']) for j in plan['jobs']]==expected,'Incomplete matrix')
    for i,job in enumerate(plan['jobs']):
        prefix=OUT/f'worker_{i:03d}';paths={k:prefix.with_suffix(s) for k,s in [('raw','.raw.json'),('log','.log'),('receipt','.receipt.json'),('submission','.submission.json')]}
        receipt=json.loads(paths['receipt'].read_text());sub=json.loads(paths['submission'].read_text())
        inp=plan['inputs'][job['mode']]
        command=['taskset','-c',str(job['cpu']),plan['binary'],inp['image'],inp['fixture'],inp['sites'],'4096','80','200000','8',job['execution']]
        require(sub['command']==command and sub['condition']==job,'Submitted command differs')
        require(receipt['exit_code']==0 and receipt['condition']==job and receipt['command']==command,'Failed/different run')
        require(digest(paths['raw'])==receipt['raw_sha256'] and digest(paths['log'])==receipt['log_sha256'],'Changed outputs')
        counters=[tuple(map(int,m)) for m in re.findall(r'^HEAP_COUNTERS (\d+) (\d+) (\d+) (\d+) (\d+) (\d+)$',paths['log'].read_text(),re.M)]
        require(len(counters)==2 and [c[0] for c in counters]==[0,1],'Missing queue counters')
        for _,searches,pushes,pops,failures,peak in counters:
            require(searches>0 and pushes>=pops>0 and failures==0 and 0<peak<=plan['capacity'],'Invalid queue coverage/capacity')
        require(counters[0][1:]==counters[1][1:],'Resident queue behavior differs')
        pattern=r'^LABEL_COUNTERS '+r' '.join([r'(\d+)']*10)+r'$'
        label_counters=[tuple(map(int,m)) for m in re.findall(pattern,paths['log'].read_text(),re.M)]
        require(len(label_counters)==2 and [c[0] for c in label_counters]==[0,1],'Missing index counters')
        require(label_counters[0][1:]==label_counters[1][1:],'Resident index behavior differs')
        for _,searches,lookups,inserts,failures,peak,probes,signals,bits,values in label_counters:
            require(searches>0 and lookups>0 and inserts>=peak>0 and failures==0,'Invalid index execution counters')
            require(peak<=plan['label_capacity'] and 0<probes<=plan['index_slots'],'Index capacity exceeded')
            require(signals<=32 and bits<=16 and values<=8,'Key state capacity exceeded')

        if cached_mode!=job['mode']:
            reference=None;gc.collect();reference=json.loads(Path(plan['references'][job['mode']]).read_text())
            reference={k:v for k,v in reference.items() if k not in METRICS};cached_mode=job['mode']
            require(reference['status']=='routed' and len(reference['routes'])==1062,'Incomplete reference')
        raw=json.loads(paths['raw'].read_text())
        require(raw['execution']==job['execution'] and len(raw['batches'])==2 and len(raw['export_ms'])==2,'Incomplete result')
        for batch in raw['batches']:
            require(METRICS<=batch.keys(),'Missing metrics')
            require({k:v for k,v in batch.items() if k not in METRICS}==reference,'Route/search/site/negotiation semantics differ')
            for k in METRICS:require(math.isfinite(batch[k]) and batch[k]>=0,'Invalid metric')
        expected_searches=sum(len(conn) for it in reference['iterations'] for conn in it['connections'])
        require(all(c[1]==expected_searches for c in counters),'Not every search used heap')
        require(all(c[1]==expected_searches for c in label_counters),'Not every search used label index')
        for v in [raw['materialization_ms'],*raw['export_ms'],receipt['process_wall_ms']]:require(math.isfinite(v) and v>=0,'Invalid timing')
        results.append({'condition':job,'full_batches_verified':2,'queue_counters':counters,'label_counters':label_counters,'searches_per_batch':expected_searches,'routes_per_batch':1062})
        for p in paths.values():files[str(p)]=digest(p)
        del raw;gc.collect()
    report={'status':'four_full_router_label_index_conditions_independently_verified','files':files,'results':results,'limitations':plan['limitations']}
    p=ROOT/'results/label_index_router_audit_20261024_v1.json'
    with p.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(report['status'],flush=True)

if __name__=='__main__':audit()
