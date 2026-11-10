#!/usr/bin/env python3
"""Full raw audit of negotiation through the static snapshot provider."""
import gc
import json
import math
from pathlib import Path
import re
from prepare_snapshot_router import ROOT,OUT,digest,PRIOR,PRIOR_STATUS

METRICS={'preparation_ms','route_ms','peak_kib','logical_bytes','cache_hits','cache_misses'}

def require(ok,message):
    if not ok:raise ValueError(message)

def parse_rows(log,name,width):
    pattern=r'^'+name+' '+r' '.join([r'(\d+)']*width)+r'$'
    rows=[tuple(map(int,m)) for m in re.findall(pattern,log,re.M)]
    require(len(rows)==2 and [r[0] for r in rows]==[0,1],'Missing '+name)
    require(rows[0][1:]==rows[1][1:],'Resident '+name+' differs')
    return rows

def validate_counters(log,plan,prior,reference):
    cc=parse_rows(log,'CONTROLLER_COUNTERS',11);sc=parse_rows(log,'SNAPSHOT_COUNTERS',10)
    require(cc==[tuple(r) for r in prior['controller_counters']],'Controller operation counts differ from predecessor')
    rounds=reference['iterations'];snapshots=sum(len(r['connections']) for r in rounds)
    searches=sum(len(c) for r in rounds for c in r['connections'])
    found=sum(c['status']=='found' for r in rounds for conn in r['connections'] for c in conn)
    node_seen=False;site_keys=set();node_history=site_history=0
    for r in rounds:
        node_history+=len(r['connections'])*bool(node_seen);site_history+=len(r['connections'])*bool(site_keys)
        node_seen=node_seen or bool(r['conflicts'])
        site_keys.update(tuple(c[:2]) for c in r['site_conflicts'])
    # The final reference is routed: its final round cannot add conflicts.
    require(not rounds[-1]['conflicts'] and not rounds[-1]['site_conflicts'],'Nonterminal reference conflicts')
    final_site_nets=sum(any(r['demands']) for r in reference['routes'])
    for c,s in zip(cc,sc):
        require(c[1]==searches and c[5]==found and c[6]==c[7]==0,'Missing/failed search coverage')
        require(0<c[8]<=plan['capacity'] and 0<c[9]<=plan['label_capacity'] and 0<c[10]<=plan['index_slots'],'Controller capacity exceeded')
        _,n,occupied,nh,so,sh,site_paths,fail,peak_owners,peak_history=s
        require(n==snapshots and occupied==snapshots-1,'Snapshot/current node ownership coverage differs')
        require(nh==node_history and sh==site_history and peak_history==len(site_keys),'Historical penalties not bound per round')
        require(fail==0 and 0<=so<=snapshots and final_site_nets<=site_paths<=found,'Invalid snapshot/site path coverage')
        require(0<=peak_owners<=plan['config_owners'] and 0<=peak_history<=plan['config_history'],'Snapshot capacity exceeded')
        require(bool(so)==bool(peak_owners),'Site owner peak/coverage mismatch')
        if final_site_nets>1:require(so>0 and site_paths>0,'Real dynamic site demands never used')
    return cc,sc

def audit():
    pp=OUT/'plan.json';plan=json.loads(pp.read_text())
    for p,h in {**plan['files'],**plan['generated']}.items():require(digest(p)==h,'Changed frozen input '+p)
    gate=json.loads((OUT/'prior_audit_binding.json').read_text())
    require(gate=={'path':str(PRIOR),'sha256':digest(PRIOR),'status':PRIOR_STATUS},'Changed predecessor binding')
    prior=json.loads(PRIOR.read_text());require(prior['status']==PRIOR_STATUS,'Predecessor not verified')
    expected=[('csr','direct',122),('csr','expanded',124),('compact','direct',125),('compact','expanded',126)]
    require([(j['mode'],j['execution'],j['cpu']) for j in plan['jobs']]==expected and len(prior['results'])==4,'Incomplete matrix')
    files={str(pp):digest(pp),str(PRIOR):digest(PRIOR),str(OUT/'prior_audit_binding.json'):digest(OUT/'prior_audit_binding.json')}
    results=[];reference=None;cached_mode=None
    for i,job in enumerate(plan['jobs']):
        previous=prior['results'][i];require(previous['condition']==job and previous['full_batches_verified']==2,'Different predecessor condition')
        prefix=OUT/f'worker_{i:03d}';paths={k:prefix.with_suffix(s) for k,s in [('raw','.raw.json'),('log','.log'),('receipt','.receipt.json'),('submission','.submission.json')]}
        receipt=json.loads(paths['receipt'].read_text());submission=json.loads(paths['submission'].read_text());inp=plan['inputs'][job['mode']]
        command=['taskset','-c',str(job['cpu']),plan['binary'],inp['image'],inp['fixture'],inp['sites'],'4096','80','200000','8',job['execution']]
        require(submission['command']==command and submission['condition']==job and submission['plan_sha256']==digest(pp),'Different submission')
        require(receipt['exit_code']==0 and receipt['condition']==job and receipt['command']==command,'Failed/different run')
        require(digest(paths['raw'])==receipt['raw_sha256'] and digest(paths['log'])==receipt['log_sha256'],'Changed outputs')
        if cached_mode!=job['mode']:
            reference=None;gc.collect();reference=json.loads(Path(plan['references'][job['mode']]).read_text())
            reference={k:v for k,v in reference.items() if k not in METRICS};cached_mode=job['mode']
            require(reference['status']=='routed' and len(reference['routes'])==1062,'Incomplete reference')
        cc,sc=validate_counters(paths['log'].read_text(),plan,previous,reference)
        raw=json.loads(paths['raw'].read_text())
        require(raw['execution']==job['execution'] and len(raw['batches'])==len(raw['export_ms'])==2,'Incomplete batches')
        for batch in raw['batches']:
            require(METRICS<=batch.keys(),'Missing metrics')
            require({k:v for k,v in batch.items() if k not in METRICS}==reference,'Route/search/site/negotiation semantics differ')
            for k in METRICS:require(math.isfinite(batch[k]) and batch[k]>=0,'Invalid metric')
        for v in [raw['materialization_ms'],*raw['export_ms'],receipt['process_wall_ms']]:require(math.isfinite(v) and v>=0,'Invalid timing')
        results.append({'condition':job,'full_batches_verified':2,'controller_counters':cc,'snapshot_counters':sc,'routes_per_batch':1062,'searches_per_batch':cc[0][1]})
        for p in paths.values():files[str(p)]=digest(p)
        del raw;gc.collect()
    report={'status':'four_full_router_snapshot_conditions_independently_verified','files':files,'results':results,'limitations':plan['limitations']}
    with (ROOT/'results/snapshot_router_audit_20261024_v1.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(report['status'],flush=True)

if __name__=='__main__':audit()
