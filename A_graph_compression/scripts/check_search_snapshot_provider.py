#!/usr/bin/env python3
"""Bind component checks and both real probe receipts without widening scope."""
import json
import re
from pathlib import Path
from prepare_search_heap_router import ROOT,digest
from run_snapshot_real_probes import OUT

def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    pp=OUT/'plan.json';plan=json.loads(pp.read_text())
    for p,h in plan['files'].items():require(digest(p)==h,'Changed frozen probe input '+p)
    files={str(pp):digest(pp)};probes=[]
    for mode,attributes in [('csr',43770),('compact',43834)]:
        paths={k:OUT/(mode+suffix) for k,suffix in [('log','.log'),('receipt','.receipt.json'),('submission','.submission.json')]}
        receipt=json.loads(paths['receipt'].read_text());submission=json.loads(paths['submission'].read_text())
        inp=plan['inputs'][mode]
        expected=['taskset','-c','120',plan['binary'],inp['image'],inp['fixture'],inp['sites']]
        require(receipt['exit_code']==0 and receipt['command']==submission['command']==expected,'Probe failed or different command')
        require(submission['plan_sha256']==digest(pp) and receipt['log_sha256']==digest(paths['log']),'Changed probe evidence')
        pattern=r'SNAPSHOT_REAL_SEARCH_PASS queries=(\d+) found=(\d+) site_paths=(\d+) with_unknown_evidence=(\d+) expanded=(\d+) attributes=(\d+)\n'
        match=re.fullmatch(pattern,paths['log'].read_text());require(match is not None,'Missing real probe result')
        values=list(map(int,match.groups()));require(values==[16,16,0,16,105236,attributes],'Unexpected probe coverage')
        probes.append(dict(mode=mode,queries=values[0],found=values[1],site_paths=values[2],with_unknown_evidence=values[3],expanded=values[4],attributes=values[5]))
        for p in paths.values():files[str(p)]=digest(p)
    logs={
        'results/search_cost_snapshot_20261024_v1.log':['COST_RANDOM_PASS cases=10000 compatible=1252 incompatible=8748','COST_GLOBAL_CONFIG_PASS fields=954','COST_BOUNDARY_PASS','COST_ALL_PASS'],
        'results/search_snapshot_provider_20261024_v1.log':['SNAPSHOT_SEARCH_PASS cases=1000 budget_exhausted=138 found=451 incomplete_domain=81 no_path=207 unknown_site_semantics=123','SNAPSHOT_PROVIDER_BOUNDS_PASS','SNAPSHOT_PROVIDER_ALL_PASS'],
        'results/search_snapshot_cxx14_20261024_v1.log':['SNAPSHOT_CXX14_COMPLETE_SEARCH_PASS transactions=3','SNAPSHOT_METADATA_REJECTION_PASS'],
        'results/search_snapshot_real_sites_20261024_v1.log':['SNAPSHOT_REAL_SITE_PASS mode=csr requirements=14 attributes=43770 fixed_bits=954 fixed_records=954','SNAPSHOT_REAL_SITE_PASS mode=compact requirements=14 attributes=43834 fixed_bits=954 fixed_records=954','SNAPSHOT_REAL_SITES_ALL_PASS']}
    for name,lines in logs.items():
        p=ROOT/name;require(p.read_text().splitlines()==lines,'Component check log differs '+name);files[str(p)]=digest(p)
    names=['hardware/vitis/search_cost_snapshot.hpp','hardware/vitis/search_snapshot_provider.hpp','src/native/search_snapshot_inputs.hpp',
           'tests/test_search_cost_snapshot.cpp','tests/test_search_snapshot_provider.cpp','tests/test_search_snapshot_cxx14.cpp','tests/test_search_snapshot_real_sites.cpp',
           'results/search_snapshot_real_sites_20261024_attempt1.log','scripts/check_search_snapshot_provider.py']
    for name in names:files[str(ROOT/name)]=digest(ROOT/name)
    report={'status':'bounded_snapshot_provider_cpu_and_real_probes_verified','files':files,'real_probes':probes,
            'checks':{'cost_random_cases':10000,'full_search_random_cases':1000,'cxx14_transactions':3,'real_site_requirements_per_mode':14,'global_fixed_bits':954,'sanitizers':['address','undefined']},
            'limitations':plan['limitations']+[
                'Real independent probes have zero site-demand paths. Real metadata is checked separately; randomized complete searches and the C++14 fixture exercise site-dependent paths.',
                'Adjacency in real probes is native CPU decoding; the static provider removes native semantics, compatibility and cost callbacks only.',
                'Snapshot creation and between-search occupancy/history updates remain host operations; no complete negotiated routing integration for this provider yet.',
                'Cost records have an explicit word layout; key/state arrays and complete HLS top/storage layout remain to be implemented and synthesized.'],
            'development_failure':'Initial real-site test bound 4096 attributes was rejected. Corrected test capacity 65536 covers actual domains 43770 and 43834; original failure log retained.'}
    target=ROOT/'results/search_snapshot_provider_component_20261024_v1.json'
    with target.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(report['status'],digest(target))

if __name__=='__main__':main()
