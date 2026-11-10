#!/usr/bin/env python3
"""Full raw audit of negotiation through the static snapshot provider."""
import gc
import json
import math
from pathlib import Path
import re
import struct
from prepare_complete_search_router import ROOT,OUT,digest,PRIOR,PRIOR_STATUS

METRICS={'preparation_ms','route_ms','peak_kib','logical_bytes','cache_hits','cache_misses'}

def require(ok,message):
    if not ok:raise ValueError(message)

def parse_rows(log,name,width):
    pattern=r'^'+name+' '+r' '.join([r'(\d+)']*width)+r'$'
    rows=[tuple(map(int,m)) for m in re.findall(pattern,log,re.M)]
    require(len(rows)==2 and [r[0] for r in rows]==[0,1],'Missing '+name)
    require(rows[0][1:]==rows[1][1:],'Resident '+name+' differs')
    return rows

from check_word_snapshot_router import validate_counters

def validate_kernel_counters(log,plan,cc,sc,node_count,attribute_count):
    rows=parse_rows(log,'KERNEL_COUNTERS',7)
    minimum=32+65+(node_count+63)//64+2*node_count+2*((attribute_count+7)//8)
    for k,c,s in zip(rows,cc,sc):
        batch,calls,packets,serialized,submitted,maximum,roots=k
        require(batch==c[0]==s[0],'Kernel batch mismatch')
        require(calls==c[1]>0 and packets==s[1]>0,'Not every snapshot/search uses the kernel')
        require(minimum<=maximum<=plan['packet_words'],'Invalid kernel packet peak')
        require(packets*minimum<=serialized<=packets*maximum,'Invalid serialized snapshot volume')
        require(calls*minimum<=submitted<=calls*maximum,'Invalid submitted ABI volume')
        require(1<roots<=min(node_count,plan['roots']),'Missing multi-root use or root overflow')
    return rows

def audit():
    pp=OUT/'plan.json';plan=json.loads(pp.read_text())
    for p,h in {**plan['files'],**plan['generated']}.items():require(digest(p)==h,'Changed frozen input '+p)
    gate=json.loads((OUT/'prior_audit_binding.json').read_text())
    require(gate=={'path':str(PRIOR),'sha256':digest(PRIOR),'status':PRIOR_STATUS},'Changed predecessor binding')
    prior=json.loads(PRIOR.read_text());require(prior['status']==PRIOR_STATUS,'Predecessor not verified')
    expected=[('csr','kernel',122),('compact','kernel',125)]
    require([(j['mode'],j['execution'],j['cpu']) for j in plan['jobs']]==expected and len(prior['results'])==4,'Incomplete matrix')
    files={str(pp):digest(pp),str(PRIOR):digest(PRIOR),str(OUT/'prior_audit_binding.json'):digest(OUT/'prior_audit_binding.json')}
    results=[];reference=None;cached_mode=None
    for i,job in enumerate(plan['jobs']):
        previous=prior['results'][2*i];require(previous['condition']=={'mode':job['mode'],'execution':'direct','cpu':job['cpu']} and previous['full_batches_verified']==2,'Different predecessor condition')
        prefix=OUT/f'worker_{i:03d}';paths={k:prefix.with_suffix(s) for k,s in [('raw','.raw.json'),('log','.log'),('receipt','.receipt.json'),('submission','.submission.json')]}
        receipt=json.loads(paths['receipt'].read_text());submission=json.loads(paths['submission'].read_text());inp=plan['inputs'][job['mode']]
        command=['taskset','-c',str(job['cpu']),plan['binary'],inp['image'],inp['fixture'],inp['sites'],'4096','80','200000','8',job['execution'],inp['config']]
        require(submission['command']==command and submission['condition']==job and submission['plan_sha256']==digest(pp),'Different submission')
        require(receipt['exit_code']==0 and receipt['condition']==job and receipt['command']==command,'Failed/different run')
        require(digest(paths['raw'])==receipt['raw_sha256'] and digest(paths['log'])==receipt['log_sha256'],'Changed outputs')
        if cached_mode!=job['mode']:
            reference=None;gc.collect();reference=json.loads(Path(plan['references'][job['mode']]).read_text())
            reference={k:v for k,v in reference.items() if k not in METRICS};cached_mode=job['mode']
            require(reference['status']=='routed' and len(reference['routes'])==1062,'Incomplete reference')
        cc,sc=validate_counters(paths['log'].read_text(),plan,previous,reference)
        config=struct.unpack('<32I',Path(inp['config']).read_bytes())
        kc=validate_kernel_counters(paths['log'].read_text(),plan,cc,sc,config[2],config[26])
        raw=json.loads(paths['raw'].read_text())
        require(raw['execution']==job['execution'] and len(raw['batches'])==len(raw['export_ms'])==2,'Incomplete batches')
        for batch in raw['batches']:
            require(METRICS<=batch.keys(),'Missing metrics')
            require(batch['cache_hits']==batch['cache_misses']==batch['logical_bytes']==0,'Native adjacency used during kernel search')
            require({k:v for k,v in batch.items() if k not in METRICS}==reference,'Route/search/site/negotiation semantics differ')
            for k in METRICS:require(math.isfinite(batch[k]) and batch[k]>=0,'Invalid metric')
        for v in [raw['materialization_ms'],*raw['export_ms'],receipt['process_wall_ms']]:require(math.isfinite(v) and v>=0,'Invalid timing')
        results.append({'condition':job,'full_batches_verified':2,'controller_counters':cc,'snapshot_counters':sc,'kernel_counters':kc,'routes_per_batch':1062,'searches_per_batch':cc[0][1]})
        for p in paths.values():files[str(p)]=digest(p)
        del raw;gc.collect()
    report={'status':'two_full_router_kernel_conditions_independently_verified','files':files,'results':results,'limitations':plan['limitations']}
    with (ROOT/'results/complete_search_router_audit_20261024_v1.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(report['status'],flush=True)

if __name__=='__main__':audit()
