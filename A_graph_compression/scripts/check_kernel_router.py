#!/usr/bin/env python3
"""Compare all router states against frozen native references after Vitis-ABI C-model calls."""
import argparse
import gc
import json
import math
from pathlib import Path
from check_vitis_kernel import digest,require

OLD_METRICS={'preparation_ms','route_ms','peak_kib','logical_bytes','cache_hits','cache_misses'}
NEW_METRICS=(OLD_METRICS-{'logical_bytes'})|{'kernel_payload_bytes','kernel_calls'}


def audit(bundle):
    pp=bundle/'plan.json';plan=json.loads(pp.read_text())
    for path,sha in plan['files'].items():require(digest(path)==sha,'Frozen integration input changed: '+path)
    files={str(pp):digest(pp),str(Path(__file__).resolve()):digest(__file__)}
    results=[];cached_mode=None;reference=None
    for i,job in enumerate(plan['jobs']):
        prefix=bundle/f'worker_{i:03d}';receipt_path=prefix.with_suffix('.receipt.json')
        receipt=json.loads(receipt_path.read_text());submission_path=prefix.with_suffix('.submission.json')
        submission=json.loads(submission_path.read_text());mode=job['mode']
        inp=plan['inputs'][mode]
        command=[plan['binaries'][mode],inp['image'],inp['fixture'],inp['sites'],'4096','80','200000','8',job['execution'],plan['configs'][mode]]
        require(submission['command']==command and submission['cpu']==job['cpu'],'Submitted integration command differs')
        require(receipt['exit_code']==0 and receipt['condition']==job,'Worker failed or changed condition')
        raw_path=prefix.with_suffix('.raw.json');log_path=prefix.with_suffix('.log')
        require(digest(raw_path)==receipt['raw_sha256'] and digest(log_path)==receipt['log_sha256'],'Raw integration evidence changed')
        if cached_mode!=mode:
            reference=None;gc.collect();reference=json.loads(Path(plan['references'][mode]).read_text())
            reference={k:v for k,v in reference.items() if k not in OLD_METRICS};cached_mode=mode
            require(len(reference['routes'])==1062 and reference['status']=='routed','Incomplete reference workload')
        raw=json.loads(raw_path.read_text())
        require(raw['backend']=='cpu_vitis_abi_cmodel' and raw['execution']==job['execution'],'Backend/scope differs')
        require(len(raw['batches'])==2 and len(raw['export_ms'])==2,'Missing first/resident result')
        metrics=[]
        for batch in raw['batches']:
            require(set(NEW_METRICS)<=batch.keys(),'Missing provider counters')
            require({k:v for k,v in batch.items() if k not in NEW_METRICS}==reference,
                    'Full route trees, site demands or negotiation/search outcomes differ')
            for k in NEW_METRICS:require(math.isfinite(batch[k]) and batch[k]>=0,'Invalid metric')
            if job['execution']=='direct':
                require(batch['kernel_calls']==batch['cache_misses'] and batch['kernel_calls']>0,'Direct mode did not invoke kernel on cache misses')
            else:require(batch['kernel_calls']==0 and batch['kernel_payload_bytes']==0,'Expanded mode has per-search kernel calls')
            metrics.append({k:batch[k] for k in sorted(NEW_METRICS)})
        for t in [raw['materialization_ms'],*raw['export_ms']]:require(math.isfinite(t) and t>=0,'Invalid preparation/export time')
        results.append({'condition':job,'full_batches_verified':2,'batch_metrics':metrics,
                        'materialization_ms':raw['materialization_ms'],'export_ms':raw['export_ms'],
                        'process_wall_ms':receipt['process_wall_ms']})
        for p in [receipt_path,submission_path,raw_path,log_path]:files[str(p)]=digest(p)
        del raw;gc.collect()
    require(len(results)==4,'Incomplete representation/execution matrix')
    return {'status':'four_full_router_vitis_abi_cmodel_conditions_independently_verified',
            'files':files,'results':results,'limitations':plan['limitations']}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();report=audit(a.bundle.resolve())
    with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({'status':report['status'],'conditions':len(report['results'])}))


if __name__=='__main__':main()
