#!/usr/bin/env python3
"""Compare full raw routing and every actual diagnostic trace against baseline."""
import argparse
import gc
import json
from pathlib import Path
from check_vitis_kernel import digest,require
from check_batch_router import semantic_batch,counters
from read_batch_trace_v4 import decode_file
ROOT=Path(__file__).resolve().parents[1]
def audit(bundle,output):
    require(not output.exists(),'Existing diagnostic audit')
    plan=json.loads((bundle/'plan.json').read_text());old_dir=Path(plan['prior_bundle']);old=json.loads(Path(plan['prior_audit']).read_text())
    for p,h in plan['files'].items():require(digest(p)==h,'Changed real run input '+p)
    files=dict(plan['files']);results=[]
    for index,job in enumerate(plan['jobs']):
        prefix=bundle/f'worker_{index:03d}';previous=old_dir/f'worker_{index:03d}';rp=prefix.with_suffix('.receipt.json');sp=prefix.with_suffix('.submission.json');receipt=json.loads(rp.read_text());submission=json.loads(sp.read_text())
        require(receipt['exit_code']==0 and receipt['command']==submission['command']==plan['commands'][index] and receipt['condition']==submission['condition']==job and submission['plan_sha256']==digest(bundle/'plan.json'),'Failed/different worker')
        for suffix,key in [('.raw.json','raw_sha256'),('.log','log_sha256')]:require(digest(prefix.with_suffix(suffix))==receipt[key],'Changed worker output')
        for suffix in ['.raw.json','.log']:require(digest(previous.with_suffix(suffix))==old['files'][str(previous.with_suffix(suffix))],'Changed audited baseline')
        require(counters(prefix.with_suffix('.log').read_text())==counters(previous.with_suffix('.log').read_text()),'CC/SC/KC changed')
        actual=json.loads(prefix.with_suffix('.raw.json').read_text());expected=json.loads(previous.with_suffix('.raw.json').read_text())
        require(actual['execution']==expected['execution']=='kernel' and len(actual['batches'])==len(expected['batches'])==2,'Wrong batch count/mode')
        for a,b in zip(actual['batches'],expected['batches']):require(semantic_batch(a)==semantic_batch(b),'Full intermediate/final raw routing changed')
        del expected;gc.collect()
        mode=index;mode_results=[]
        fixture=Path(plan['inputs'][job['mode']]['fixture']);nodes=int(fixture.read_text().split()[1])
        for batch,raw_batch in enumerate(actual['batches']):
            path=bundle/f'trace_{mode}_{batch}.bin';trace=decode_file(path,nodes)
            require(trace['complete_batch'] and trace['terminal'][3:8]==[4,4248,16836,16836,1],'Wrong complete diagnostic totals')
            require(trace['metadata'][2]<=plan['trace_capacity_words'] and path.stat().st_size==64+8*trace['metadata'][2],'Trace capacity/length mismatch')
            cursor=0
            for iteration,raw_round in enumerate(raw_batch['iterations']):
                for q,connections in enumerate(raw_round['connections']):
                    for sink,connection in enumerate(connections):
                        search=trace['searches'][cursor];cursor+=1;r=search['result']
                        require((search['iteration'],search['query'])==(iteration,(q<<32)|sink),'Search order changed')
                        require(connection['status']=='found' and r[0]==0 and connection['cost']==r[1] and connection['expanded']==r[2] and connection['blocked']==r[3],'Search raw result mismatch')
                        require(connection['unknown_sources']==search['unknown_nodes'] and connection['unknown_pips']==[[key>>32,key&0xffffffff] for key in search['unknown_pips']],'Unknown membership differs from raw baseline')
            require(cursor==len(trace['searches'])==16836,'Missing full searches')
            final={n['net']:n for n in trace['nets'] if n['iteration']==3}
            require(len(final)==1062,'Missing final net snapshots')
            for route in raw_batch['routes']:
                nr=final[route['net']];d=nr['demands']
                require(route['complete']==bool(nr['result'][5]) and route['nodes']==nr['roots'] and route['edges']==nr['edges'] and route['demands']==[d['signals'],d['bits'],d['values']],'Final raw route/trace mismatch')
            mode_results.append(dict(batch=batch,trace=str(path),committed_words=trace['metadata'][2],committed_bytes=trace['metadata'][2]*8,capacity_words=plan['trace_capacity_words'],searches=cursor,nets=len(trace['nets']),round_snapshots=len(trace['rounds'])))
            files[str(path)]=digest(path);del trace;gc.collect()
        results.append(dict(mode=job['mode'],batches=mode_results))
        for p in [rp,sp,prefix.with_suffix('.raw.json'),prefix.with_suffix('.log')]:files[str(p)]=digest(p)
        del actual;gc.collect()
    require(len(list(bundle.glob('trace_*.bin')))==4,'Missing/extra diagnostic traces')
    for p in [bundle/'plan.json',Path(__file__).resolve(),ROOT/'scripts/read_batch_trace_v4.py',ROOT/'scripts/read_round_trace_v2.py',ROOT/'results/compressed_batch_trace_cases_20261025_v2.json']:files[str(p)]=digest(p)
    r=dict(status='compressed_batch_two_modes_two_full_batches_raw_and_exact_trace_independently_verified_cpu_only',files=files,results=results,hardware_executed=False,limits=['Actual full diagnostic CPU execution, not a synthesized/board run','Trace capacity measured for these unchanged four batches only, not all possible workloads','No HLS/RTL/physical timing or board performance/power proof','Artifacts currently local temporary storage; durable promotion remains required'])
    with output.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
    print(r['status'],flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();audit(a.bundle.resolve(),a.output.resolve())
