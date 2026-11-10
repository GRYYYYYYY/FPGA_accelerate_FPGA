#!/usr/bin/env python3
"""Bind complete negotiated routing differential through production top ABI."""
import json
from pathlib import Path
from prepare_search_heap_router import ROOT,digest
from derive_search_kernel_route_adapter import TARGET,derive
from run_kernel_route_checks_v2 import driver
BUNDLE=ROOT/'data/derived/kernel_route_checks_20261024_v2'
OUTPUT=ROOT/'results/kernel_route_component_20261024_v1.json'

def main():
    plan=json.loads((BUNDLE/'plan.json').read_text());state=json.loads((BUNDLE/'state.json').read_text())
    if state['status']!='complete':raise ValueError('Incomplete negotiation check')
    if TARGET.read_text()!=derive() or (BUNDLE/'source/driver.cpp').read_text()!=driver():raise ValueError('Different integration/test derivation')
    artifacts=dict(plan['files'])
    for p,h in artifacts.items():
        if digest(p)!=h:raise ValueError('Changed test input '+p)
    for stage in ['compile','run']:
        rp=BUNDLE/(stage+'.receipt.json');log=BUNDLE/(stage+'.log');r=json.loads(rp.read_text())
        expected=plan['compile_command'] if stage=='compile' else ['taskset','-c','119',str(BUNDLE/'check'),str(BUNDLE/'source/sites.txt')]
        if r['exit_code'] or r['command']!=expected or r['plan_sha256']!=digest(BUNDLE/'plan.json') or r['log_sha256']!=digest(log) or r['binary_sha256']!=digest(BUNDLE/'check'):raise ValueError('Failed or mismatched receipt '+stage)
        for p in [rp,log]:artifacts[str(p)]=digest(p)
    expected='KERNEL_ROUTE_RANDOM_PASS cases=400 modes=2 snapshots=3750 searches=4938 rounds=1250 node_history_snapshots=2412 site_history_snapshots=2106 site_paths=2896 incomplete=190 routed=210\nKERNEL_ROUTE_FULL_RESULTS_PASS\n'
    if (BUNDLE/'run.log').read_text()!=expected:raise ValueError('Wrong negotiated coverage')
    for p in [BUNDLE/'plan.json',BUNDLE/'state.json',BUNDLE/'check',Path(__file__).resolve()]:artifacts[str(p)]=digest(p)
    result={'status':'production_search_top_full_negotiation_cpu_differential_verified','cases':400,'modes':2,'snapshots':3750,'searches':4938,'rounds':1250,'node_history_snapshots':2412,'site_history_snapshots':2106,'site_paths':2896,'routed':210,'incomplete':190,
        'checks':['Actual frozen production CSR and compact top objects at full hardware capacities.','All intermediate search paths, statuses, demand states, unknown sets, costs and expansion counts compared to native search.','All final routes and all round node/site conflicts and incomplete nets compared.','Native adjacency disabled for candidate; every search matched kernel invocation counters.','Synthetic aliases made canonical before reference/candidate runs; stable production row ordering retains parallel edges.','Strict C++17 ASAN/UBSAN.'],
        'limitations':['CPU C model with synthetic graph payloads, not real full 1062-net results or RTL.','Host constructs snapshots and performs negotiation/occupancy updates.','Real special-resource model remains limited to existing physically tested instances.'], 'artifacts':artifacts}
    with OUTPUT.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(OUTPUT,digest(OUTPUT))

if __name__=='__main__':main()
