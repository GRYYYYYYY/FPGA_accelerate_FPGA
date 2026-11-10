#!/usr/bin/env python3
"""Measure exhaustive decoder completion under explicit Linux address-space limits.

This bounds the native decoder process only, not graph conversion, full routing,
host physical RAM or FPGA memory. No timing performance is inferred.
"""
import argparse
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import time
from check_template_scope import digest
from real_experiment import write_new
ROOT=Path(__file__).resolve().parents[1]


def classify(receipt, expected):
    if receipt['exit_code']==0:
        if receipt['stderr'] or json.loads(receipt['stdout'])!=expected:
            raise ValueError('Bounded scan differs from fully validated exhaustive reference')
        return 'complete_equivalent_scan'
    if receipt['exit_code']==3 and receipt['stderr']=='ALLOCATION_FAILED\n' and not receipt['stdout']:
        return 'address_space_allocation_failed'
    raise ValueError('Unexpected failure is not capacity evidence')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--cpu',type=int,default=124);a=p.parse_args()
    a.source=a.source.resolve();a.output=a.output.resolve()
    if a.cpu not in os.sched_getaffinity(0):raise ValueError('Unavailable CPU')
    os.sched_setaffinity(0,{a.cpu})
    report_path=a.source/'report.json';report=json.loads(report_path.read_text())
    if report['status']!='all_four_nested_real_domains_verified':raise ValueError('Incomplete source experiment')
    prior_path=a.source/'plan.json';prior=json.loads(prior_path.read_text())
    if digest(prior_path)!=report['plan_sha256']:raise ValueError('Source plan changed')
    for path,value in {**prior['files'],**report['artifacts']}.items():
        if digest(path)!=value:raise ValueError('Audited source evidence changed: '+path)
    binary=a.source/'native_scan';prlimit=Path(shutil.which('prlimit') or '')
    if not prlimit.is_file():raise ValueError('prlimit unavailable')
    # Both modes receive exactly the same resource limits at every real scale.
    budgets=[8,16,32,64,96,128]
    jobs=[{'denominator':d,'mode':m,'limit_mib':b} for d in (16,4,2,1) for b in budgets for m in ('csr','compact')]
    random.Random(20261023).shuffle(jobs)
    a.output.mkdir(parents=True,exist_ok=False)
    regression=ROOT/'results/regression_scale_capacity_20261023_v1.log'
    if not regression.read_text().rstrip().endswith('OK'):raise ValueError('Capacity regression not passed')
    paths=[Path(__file__),ROOT/'scripts/check_template_scope.py',ROOT/'scripts/real_experiment.py',regression,
           report_path,prior_path,binary,prlimit]
    paths.extend(a.source/f'fraction_1_{d}'/(m+'.agr') for d in (16,4,2,1) for m in ('csr','compact'))
    files={str(path):digest(path) for path in paths}
    limits=['RLIMIT_AS includes the executable, libraries, image and native decoder allocations; it is virtual address space, not physical RSS.',
        'The source parser, bank/fixture preparation, routing occupancy/search/trace and external auditing are outside this process limit.',
        'One fresh process per cell. Outcomes are feasibility at tested limits, not an exact minimum or statistical runtime comparison.',
        'Uses real nested source domains with full outgoing edges; no graph replication and no claim beyond the largest captured domain.',
        'Spatial prefixes vary resource composition and row density as well as size; compare CSR and compact within each domain, not as a pure node-count scaling law.',
        'These are CPU decoder capacity measurements, not board DDR/HBM capacity or whole-router capacity.']
    plan={'owner_pid':os.getpid(),'cpu':a.cpu,'jobs':jobs,'seed':20261023,'files':files,'limitations':limits}
    write_new(a.output/'plan.json',plan);records=[]
    domains={d['denominator']:d for d in report['domains']}
    for index,job in enumerate(jobs):
        image=a.source/f"fraction_1_{job['denominator']}"/(job['mode']+'.agr')
        limit=job['limit_mib']*1024*1024
        command=[str(prlimit),f'--as={limit}:{limit}','--',str(binary),str(image)]
        start=time.perf_counter()
        child=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        prefix=a.output/f'worker_{index:03d}'
        write_new(prefix.with_suffix('.submission.json'),{'owner_pid':os.getpid(),'child_pid':child.pid,
            'command':command,'cpu':a.cpu,'address_space_limit_bytes':limit})
        stdout,stderr=child.communicate()
        receipt={'condition':job,'exit_code':child.returncode,'stdout':stdout,'stderr':stderr,
                 'process_wall_ms_diagnostic':(time.perf_counter()-start)*1000}
        write_new(prefix.with_suffix('.receipt.json'),receipt)
        outcome=classify(receipt,domains[job['denominator']]['modes'][job['mode']]['native'])
        records.append({'condition':job,'outcome':outcome,'receipt_sha256':digest(prefix.with_suffix('.receipt.json'))})
        print('CAPACITY',index,job,outcome,flush=True)
    for d in (16,4,2,1):
        for m in ('csr','compact'):
            ordered=sorted((r for r in records if r['condition']['denominator']==d and r['condition']['mode']==m),key=lambda r:r['condition']['limit_mib'])
            seen_success=False
            for r in ordered:
                success=r['outcome']=='complete_equivalent_scan'
                if seen_success and not success:raise ValueError('Nonmonotone capacity outcome requires investigation')
                seen_success|=success
            if not seen_success:raise ValueError('Largest budget did not complete exhaustive scan')
    for path,value in files.items():
        if digest(path)!=value:raise ValueError('Capacity experiment dependency changed')
    write_new(a.output/'report.json',{'status':'all_48_bounded_native_scan_outcomes_verified',
        'plan_sha256':digest(a.output/'plan.json'),'records':records,'limitations':limits})


if __name__=='__main__':main()
