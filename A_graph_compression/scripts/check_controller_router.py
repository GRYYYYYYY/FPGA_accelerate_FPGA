#!/usr/bin/env python3
"""Audit complete route outputs and bounded controller use against frozen evidence."""
import gc
import json
import math
from pathlib import Path
import re
from prepare_controller_router import ROOT,OUT,digest,PRIOR,PRIOR_STATUS

METRICS={'preparation_ms','route_ms','peak_kib','logical_bytes','cache_hits','cache_misses'}

def require(ok,message):
    if not ok:raise ValueError(message)

def validate_counters(log,plan,prior,searches,found):
    pattern=r'^CONTROLLER_COUNTERS '+r' '.join([r'(\d+)']*11)+r'$'
    counters=[tuple(map(int,m)) for m in re.findall(pattern,log,re.M)]
    require(len(counters)==2 and [c[0] for c in counters]==[0,1],'Missing controller counters')
    require(counters[0][1:]==counters[1][1:],'Resident controller behavior differs')
    require(prior['full_batches_verified']==2,'Incomplete predecessor')
    for cc,hc,lc,rc in zip(counters,prior['queue_counters'],prior['label_counters'],prior['record_counters']):
        batch,n,push,pop,improve,success,capacity,invalid,heap,labels,probes=cc
        require(batch==hc[0]==lc[0]==rc[0],'Different predecessor batch')
        require(n==searches==hc[1]==lc[1]==rc[1] and n>0,'Not every search uses controller')
        require(success==found==rc[4] and success>0,'Found path coverage differs')
        require(push==hc[2]==rc[2]+rc[3] and pop==hc[3] and improve==rc[3],'Search operation sequence counts differ')
        require(push>=pop>0 and capacity==invalid==0,'Failed controller or invalid operation counts')
        require(0<heap==hc[5]<=plan['capacity'],'Heap peak differs/exceeds capacity')
        require(0<labels==lc[5]==rc[6]<=plan['label_capacity'],'Label peak differs/exceeds capacity')
        require(0<probes==lc[6]<=plan['index_slots'],'Index probe peak differs/exceeds capacity')
    require(all(len(prior[k])==2 for k in ['queue_counters','label_counters','record_counters']),'Incomplete predecessor counters')
    return counters

def audit():
    pp=OUT/'plan.json';plan=json.loads(pp.read_text())
    for p,h in {**plan['files'],**plan['generated']}.items():require(digest(p)==h,'Changed frozen input '+p)
    gate=json.loads((OUT/'prior_audit_binding.json').read_text())
    require(gate=={'path':str(PRIOR),'sha256':digest(PRIOR),'status':PRIOR_STATUS},'Changed prior audit binding')
    prior=json.loads(PRIOR.read_text());require(prior['status']==PRIOR_STATUS,'Prior audit failed')
    expected=[('csr','direct',122),('csr','expanded',124),('compact','direct',125),('compact','expanded',126)]
    require([(j['mode'],j['execution'],j['cpu']) for j in plan['jobs']]==expected,'Incomplete matrix')
    require(len(prior['results'])==4,'Incomplete predecessor matrix')
    files={str(pp):digest(pp),str(PRIOR):digest(PRIOR),str(OUT/'prior_audit_binding.json'):digest(OUT/'prior_audit_binding.json')}
    results=[];reference=None;cached_mode=None
    for i,job in enumerate(plan['jobs']):
        previous=prior['results'][i];require(previous['condition']==job,'Different predecessor condition')
        prefix=OUT/f'worker_{i:03d}'
        paths={k:prefix.with_suffix(s) for k,s in [('raw','.raw.json'),('log','.log'),('receipt','.receipt.json'),('submission','.submission.json')]}
        receipt=json.loads(paths['receipt'].read_text());submission=json.loads(paths['submission'].read_text())
        inp=plan['inputs'][job['mode']]
        command=['taskset','-c',str(job['cpu']),plan['binary'],inp['image'],inp['fixture'],inp['sites'],'4096','80','200000','8',job['execution']]
        require(submission['command']==command and submission['condition']==job and submission['plan_sha256']==digest(pp),'Different submission')
        require(receipt['exit_code']==0 and receipt['condition']==job and receipt['command']==command,'Failed/different run')
        require(digest(paths['raw'])==receipt['raw_sha256'] and digest(paths['log'])==receipt['log_sha256'],'Changed outputs')
        if cached_mode!=job['mode']:
            reference=None;gc.collect();reference=json.loads(Path(plan['references'][job['mode']]).read_text())
            reference={k:v for k,v in reference.items() if k not in METRICS};cached_mode=job['mode']
            require(reference['status']=='routed' and len(reference['routes'])==1062,'Incomplete reference')
        searches=sum(len(conn) for it in reference['iterations'] for conn in it['connections'])
        found=sum(c['status']=='found' for it in reference['iterations'] for conn in it['connections'] for c in conn)
        counters=validate_counters(paths['log'].read_text(),plan,previous,searches,found)
        raw=json.loads(paths['raw'].read_text())
        require(raw['execution']==job['execution'] and len(raw['batches'])==2 and len(raw['export_ms'])==2,'Incomplete result')
        for batch in raw['batches']:
            require(METRICS<=batch.keys(),'Missing metrics')
            require({k:v for k,v in batch.items() if k not in METRICS}==reference,'Route/search/site/negotiation semantics differ')
            for k in METRICS:require(math.isfinite(batch[k]) and batch[k]>=0,'Invalid metric')
        for v in [raw['materialization_ms'],*raw['export_ms'],receipt['process_wall_ms']]:require(math.isfinite(v) and v>=0,'Invalid timing')
        results.append({'condition':job,'full_batches_verified':2,'controller_counters':counters,'searches_per_batch':searches,'found_per_batch':found,'routes_per_batch':1062})
        for p in paths.values():files[str(p)]=digest(p)
        del raw;gc.collect()
    report={'status':'four_full_router_controller_conditions_independently_verified','files':files,'results':results,'limitations':plan['limitations']}
    with (ROOT/'results/controller_router_audit_20261024_v1.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(report['status'],flush=True)

if __name__=='__main__':audit()
