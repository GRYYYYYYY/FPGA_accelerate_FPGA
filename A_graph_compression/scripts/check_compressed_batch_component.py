#!/usr/bin/env python3
"""Independently bind full negotiated CPU differential to actual net-loop sources."""
import json
from pathlib import Path
import re
import subprocess
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
def main():
    b=Path('/tmp/A_graph_compression_recovery_20261025_v1/compressed_batch_router');output=ROOT/'results/compressed_batch_component_20261025_v1.json';require(not output.exists(),'Existing component audit')
    state=json.loads((b/'state.json').read_text());p=json.loads((b/'plan.json').read_text());require(state['status']=='complete' and state['stage']=='all_400_cases_with_exact_compressed_trace_verified_independent_audit_pending','Incomplete full differential')
    files={**p['files'],**p['generated']}
    for path,h in files.items():require(digest(path)==h,'Changed component input '+path)
    for phase in ['compile_csr','compile_compact','compile_differential','differential']:
        log=b/(phase+'.log');rp=b/(phase+'.receipt.json');r=json.loads(rp.read_text());require(r['exit_code']==0 and r['log_sha256']==digest(log),'Failed phase '+phase)
        if phase=='compile_differential':require(r['command']==p['command'],'Wrong complete driver build')
        if phase in ['compile_csr','compile_compact']:require('-DSEARCH_SINK_LOOP_OBSERVE=1' in r['command'] and any(x.endswith('search_batch_trace_observed_top_v2.cpp') for x in r['command']),'Wrong actual net core')
        for path in [log,rp]:files[str(path)]=digest(path)
    expected='ROUND_CONTROL_ROUTE_RANDOM_PASS cases=400 modes=2 snapshots=3750 searches=4938 rounds=1250 node_history_snapshots=2412 site_history_snapshots=2106 site_paths=2896 incomplete=190 routed=210\nROUND_CONTROL_ROUTE_FULL_RESULTS_PASS\n'
    require((b/'differential.log').read_text()==expected,'Different negotiated coverage')
    for name in ['site_routes.hpp','snapshot_test_routes.hpp']:
        text=(b/'source'/name).read_text();require('.route_batch(' in text and not any(x in text for x in ['.route_net(','owners.advance(','ledger.advance(','control.finish(','owners.erase_nodes(','ledger.release(','snapshot.bind(','owners.insert_nodes(','retained.replace(']),'Host still drives net stages')
    adapter=(b/'source/search_kernel_route_adapter.hpp').read_text()
    require('diagnostic compressed trace overflow/invalid' in adapter and 'trace_words_' in adapter and 'A_BATCH_TRACE_OUTPUT_PREFIX' in adapter,'Missing exact trace or overflow rejection')
    tokens=[]
    for label,name in [('canonical','search_batch_trace_top_v2.cpp'),('observed','search_batch_trace_observed_top_v2.cpp')]:
        source=b/'source'/name;path=b/(label+'.audit_synthesis_preprocessed.cpp')
        with path.open('x') as f:subprocess.run(['g++','-std=c++14','-E','-P','-D__SYNTHESIS__','-DSEARCH_SINK_LOOP_OBSERVE=1','-I'+str(b/'source'),str(source)],stdout=f,check=True)
        pattern=r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[A-Za-z_][A-Za-z_0-9]*|[0-9]+|[^\s]'
        tokens.append(re.findall(pattern,path.read_text()));files[str(path)]=digest(path);files[str(source)]=digest(source)
    require(tokens[0]==tokens[1],'CPU observation changes synthesis token stream')
    for path in [b/'state.json',b/'plan.json',b/'differential',b/'batch_csr.o',b/'batch_compact.o',Path(__file__).resolve()]:files[str(path)]=digest(path)
    report=dict(status='compressed_batch_full_negotiation_intermediate_differential_verified_real_trace_pending',files=files,cases=400,modes=2,searches=4938,snapshots=3750,rounds=1250,hardware_executed=False,limitations=['One actual CPU batch top executes all-net iteration, net transactions, round decisions and both history advances; host callbacks reconstruct observations only.','Read-only CPU search observations are excluded from synthesis; preprocessor token identity does not establish RTL equivalence.','Compressed exact trace executed during all400 cases, but independent decode of all400 exports and full real workload remain pending; no HLS/RTL/physical/device proof.','Failures may leave prior stages committed; no cross-stage rollback.'])
    with output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(report['status'])
if __name__=='__main__':main()
