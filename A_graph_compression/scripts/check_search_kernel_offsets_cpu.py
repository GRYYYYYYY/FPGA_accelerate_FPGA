#!/usr/bin/env python3
"""Audit CPU packet rejection and complete real-search differential receipts."""
import json
from pathlib import Path
from prepare_search_heap_router import ROOT,digest
BUNDLE=ROOT/'data/derived/search_kernel_cpu_20261024_v3'
OUTPUT=ROOT/'results/search_kernel_cpu_component_20261024_v3.json'

def main():
    pp=BUNDLE/'plan.json';plan=json.loads(pp.read_text());state=json.loads((BUNDLE/'state.json').read_text())
    if state['status']!='complete' or state['completed']!=['packet','cost','csr','compact']:raise ValueError('Incomplete top CPU check')
    artifacts=dict(plan['files'])
    for p,h in artifacts.items():
        if digest(p)!=h:raise ValueError('Changed input '+p)
    expected={'cost':'OFFSET_COST_RANDOM_PASS cases=10000 compatible=1252 incompatible=8748\n','packet':''.join(f'KERNEL_PACKET_PASS mode={i} successful_transactions=6 rejected_preflight=38 literal_offsets=pass guards=pass\n' for i in range(2)),
        'csr':'KERNEL_REAL_SEARCH_PASS queries=32 found=32 site_paths=0 with_unknown_evidence=32 expanded=217245 attributes=43770\n',
        'compact':'KERNEL_REAL_SEARCH_PASS queries=32 found=32 site_paths=0 with_unknown_evidence=32 expanded=217245 attributes=43834\n'}
    for name in ['packet','cost','csr','compact']:
        log=BUNDLE/(name+'.log');rp=BUNDLE/(name+'.receipt.json');sp=BUNDLE/(name+'.submission.json');r=json.loads(rp.read_text());s=json.loads(sp.read_text())
        cmd=['taskset','-c','120',str(BUNDLE/name)]
        if name in ['csr','compact']:
            inp=plan['inputs'][name];cmd=['taskset','-c','120',str(BUNDLE/'real'),inp['image'],inp['fixture'],inp['sites'],inp['config']]
        if r['exit_code'] or r['command']!=cmd or s['command']!=cmd or s['plan_sha256']!=digest(pp) or r['log_sha256']!=digest(log) or log.read_text()!=expected[name]:raise ValueError('Top CPU evidence mismatch '+name)
        for p in [log,rp,sp]:artifacts[str(p)]=digest(p)
    for p in [pp,BUNDLE/'state.json',Path(__file__).resolve()]:artifacts[str(p)]=digest(p)
    report={'status':'complete_search_top_cpu_real_probes_and_packet_abi_verified','modes':['csr','compact'],
        'offset_cost_native_random_cases':10000,'per_mode':{'real_queries':32,'found':32,'site_paths':0,'with_unknown_evidence':32,'expanded':217245,'small_packet_transactions':6,'rejected_packet_preflights':38},
        'scope':'Offset-based production top at real workspace limits: static decoder, flat key/index/heap/records/path/PIPs, packet snapshot, complete search and backtrace.',
        'checks':['Real native oracle full path/state/status/unknown evidence/cost/expansion comparisons.','16 empty occupancy/history probes and 16 deterministic nonzero node penalty probes per mode.','Independent literal packet offsets and path words; stateful dynamic site owners/history/fixed checks in synthetic packet transactions.','Malformed header/counts/flags/states/cost metadata/configuration rejection preserves workspace and metadata.','Strict C++14/17 ASAN/UBSAN builds.'],
        'limitations':plan['limitations']+['Real probes do not traverse modeled site requirements; synthetic packet transactions cover those operations separately.'],
        'artifacts':artifacts}
    with OUTPUT.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print('SEARCH_KERNEL_CPU_VERIFIED',OUTPUT,digest(OUTPUT))

if __name__=='__main__':main()
