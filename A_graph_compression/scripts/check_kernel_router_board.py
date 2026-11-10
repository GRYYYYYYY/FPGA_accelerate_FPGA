#!/usr/bin/env python3
"""Audit full hybrid routing results, transport accounting and bound execution evidence."""
import argparse
import json
import math
from pathlib import Path
from check_vitis_kernel import digest,require
from check_kernel_router import OLD_METRICS,NEW_METRICS

PHASES=['xrt_h2d_ms','xrt_kernel_wall_ms','xrt_d2h_ms']
TRANSPORT_PHASES=['h2d_ms','kernel_wall_ms','d2h_ms']
METRICS=NEW_METRICS|set(PHASES)


def validate_content(raw,transport,reference,execution,memory,node_count):
    expected={k:v for k,v in reference.items() if k not in OLD_METRICS}
    require(expected['status']=='routed' and len(expected['routes'])==1062,'Full reference not routed')
    require(raw['backend']=='xrt_hardware_adjacency_cpu_search' and raw['execution']==execution,'Wrong execution backend')
    require(len(raw['batches'])==2 and len(raw['export_ms'])==2,'Missing first/resident batch')
    require(transport['backend']=='xrt_hardware' and transport['complete'] is True and transport['memory']==memory,'Transport not complete/memory differs')
    require(all(isinstance(transport.get(k),str) and transport[k] for k in ['device_bdf','device_name','xclbin_uuid']),'Missing device identity')
    require(len(transport['groups'])==6 and all(type(x) is int and x>=0 for x in transport['groups']),'Missing argument memory groups')
    for key in ['setup_ms','graph_h2d_ms',*TRANSPORT_PHASES]:
        require(type(transport[key]) in (int,float) and math.isfinite(transport[key]) and transport[key]>=0,'Invalid transport time')
    for key in ['calls','requests','h2d_bytes','d2h_bytes']:
        require(type(transport[key]) is int and transport[key]>=0,'Invalid transport counter')
    calls=0;measurements=[]
    for batch in raw['batches']:
        require(set(METRICS)<=batch.keys(),'Missing hardware metrics')
        require({k:v for k,v in batch.items() if k not in METRICS}==expected,'Full routing semantics differ')
        for k in METRICS:require(type(batch[k]) in (int,float) and math.isfinite(batch[k]) and batch[k]>=0,'Invalid batch metric')
        require(sum(batch[k] for k in PHASES)<=batch['route_ms']+1e-3,'Transport phases exceed routing wall')
        if execution=='direct':require(batch['kernel_calls']==batch['cache_misses'] and batch['kernel_calls']>0,'Direct callback count differs')
        else:require(batch['kernel_calls']==0 and batch['kernel_payload_bytes']==0 and sum(batch[k] for k in PHASES)==0,'Resident search unexpectedly calls hardware')
        calls+=batch['kernel_calls'];measurements.append({k:batch[k] for k in sorted(METRICS)})
    require(execution in ('direct','expanded'),'Unknown execution mode')
    if execution=='direct':
        require(transport['calls']==calls and transport['requests']==calls,'Direct transport totals differ')
        for a,b in zip(PHASES,TRANSPORT_PHASES):
            require(abs(sum(x[a] for x in raw['batches'])-transport[b])<=1e-3,'Direct transport timing totals differ')
    else:
        require(transport['calls']==(node_count+127)//128 and transport['requests']==node_count,'Full materialization request coverage differs')
        require(sum(transport[k] for k in TRANSPORT_PHASES)<=raw['materialization_ms']+1e-3,'Kernel materialization phases exceed wall')
    # Provider always reserves1024 edges per requested row and eight guard words.
    require(transport['h2d_bytes']==32784*transport['requests']+104*transport['calls'],'H2D guard/payload byte count differs')
    require(transport['d2h_bytes']==32780*transport['requests']+104*transport['calls'],'D2H guard/payload byte count differs')
    for t in [raw['materialization_ms'],*raw['export_ms']]:
        require(type(t) in (int,float) and math.isfinite(t) and t>=0,'Invalid materialization/export time')
    return measurements


def audit(directory):
    plan_path=directory/'plan.json';receipt_path=directory/'receipt.json'
    plan=json.loads(plan_path.read_text());receipt=json.loads(receipt_path.read_text())
    require(receipt['exit_code']==0 and receipt['plan_sha256']==digest(plan_path),'Hardware runner failed or plan changed')
    for path,sha in plan['files'].items():require(digest(path)==sha,'Bound execution artifact changed: '+path)
    raw_path=directory/'router.raw.json';log=directory/'router.log';transport_path=directory/'transport/complete.json'
    require(digest(raw_path)==receipt['raw_sha256'] and digest(log)==receipt['log_sha256'],'Hardware raw output changed')
    raw=json.loads(raw_path.read_text());transport=json.loads(transport_path.read_text())
    reference=json.loads(Path(plan['reference']).read_text())
    metrics=validate_content(raw,transport,reference,plan['execution'],plan['memory'],plan['node_count'])
    artifacts={str(p):digest(p) for p in [plan_path,receipt_path,raw_path,log,transport_path,directory/'transport/opened.json',Path(__file__).resolve()]}
    return {'status':'bound_hybrid_router_full_results_and_transport_verified','artifacts':artifacts,
            'mode':plan['mode'],'execution':plan['execution'],'memory':plan['memory'],'batch_metrics':metrics,
            'transport':transport,'limitations':['CPU search/negotiation with hardware adjacency only; not a full-FPGA router.',
                'Full results match the14-instance site reference; unmodeled special-resource semantics remain.',
                'One process/two batches; no repeated board statistics, power, or new physical readback.',
                'Platform timing and actual kernel frequency need separate evidence; requested200MHz is not measured frequency.',
                'Host-observed kernel launch/wait time includes XRT overhead and is not device profiling.']}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();report=audit(a.directory.resolve())
    with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({'status':report['status'],'output':str(a.output)}))


if __name__=='__main__':main()
