#!/usr/bin/env python3
"""Bind full-row comparison receipts and exact decoder derivation."""
import json
from pathlib import Path
from prepare_search_heap_router import ROOT,digest
from derive_search_graph_adjacency import derive,TARGET
BUNDLE=ROOT/'data/derived/search_graph_checks_20261024_v1'
OUTPUT=ROOT/'results/search_graph_adjacency_component_20261024_v1.json'

def main():
    plan_path=BUNDLE/'plan.json';plan=json.loads(plan_path.read_text());state=json.loads((BUNDLE/'state.json').read_text())
    if state['status']!='complete' or state['completed']!=['csr','compact']:raise ValueError('Incomplete full-row run')
    artifacts=dict(plan['files'])
    for p,h in artifacts.items():
        if digest(p)!=h:raise ValueError('Changed input '+p)
    if TARGET.read_text()!=derive():raise ValueError('Different decoder derivation')
    for mode_id,mode in enumerate(['csr','compact']):
        log=BUNDLE/(mode+'.log');rp=BUNDLE/(mode+'.receipt.json');sp=BUNDLE/(mode+'.submission.json')
        receipt=json.loads(rp.read_text());submission=json.loads(sp.read_text());inp=plan['inputs'][mode]
        command=['taskset','-c','120',plan['binary'],inp['image'],inp['config']]
        if receipt['exit_code']!=0 or receipt['log_sha256']!=digest(log) or receipt['command']!=command or submission['command']!=command or submission['plan_sha256']!=digest(plan_path):raise ValueError('Receipt mismatch '+mode)
        expected=f'SEARCH_GRAPH_FULL_PASS mode={mode_id} nodes=274732 known=220973 unknown=53759 edges=1100754 max_degree=642\nSEARCH_GRAPH_REJECTION_GUARDS_PASS\n'
        if log.read_text()!=expected:raise ValueError('Unexpected full-row evidence '+mode)
        for p in [log,rp,sp]:artifacts[str(p)]=digest(p)
    for p in [plan_path,BUNDLE/'state.json',Path(__file__).resolve()]:artifacts[str(p)]=digest(p)
    report={'status':'search_graph_all_canonical_rows_cpu_verified','modes':['csr','compact'],'per_mode':{'nodes':274732,'known':220973,'unknown':53759,'directed_edges':1100754,'maximum_degree':642},
        'checks':['All seven edge fields and exact stable native search ordering, including parallel edges.','Unknown rows, invalid node, short output capacity and malformed configuration rejection.','Output guards and untouched tail per row; ASAN/UBSAN strict compilation.','Exact frozen decoder derivation; source/input/binary/submission/receipt/log bindings.'],
        'limitations':['CPU validation only; no HLS synthesis, RTL or board evidence for this wrapper.','Host must validate full AGRAPH01 descriptor identity before hardware use.','No complete search or negotiation is executed by this particular test.'],
        'artifacts':artifacts}
    with OUTPUT.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print('SEARCH_GRAPH_COMPONENT_VERIFIED',OUTPUT,digest(OUTPUT))

if __name__=='__main__':main()
