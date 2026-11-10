#!/usr/bin/env python3
"""Full-query first/resident router feasibility under bounded virtual address space."""
import argparse
import gc
import json
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import time
from check_template_scope import digest
from real_experiment import write_new
ROOT=Path(__file__).resolve().parents[1]
METRICS={'preparation_ms','route_ms','peak_kib','logical_bytes','cache_hits','cache_misses'}


def design():
    jobs=[{'limit_mib':limit,'mode':mode,'execution':execution,'cache_rows':4096}
          for limit in (3072,4096) for mode,execution in
          [('csr','direct'),('compact','direct'),('compact','expanded')]]
    random.Random(20261023).shuffle(jobs)
    return jobs


def allocation_failure(exit_code, log):
    lines=log.splitlines()
    if exit_code!=1 or not lines or lines[-1]!='std::bad_alloc':
        raise ValueError('Unexplained failure is not memory capacity evidence')
    if any(not re.fullmatch(r'NATIVE_SITE_PROGRESS \d+ \d+',line) for line in lines[:-1]):
        raise ValueError('Allocation failure log contains unexplained diagnostics')
    return 'address_space_allocation_failed'


def check_success(raw, reference, job):
    if raw['execution']!=job['execution'] or len(raw['batches'])!=2 or len(raw['export_ms'])!=2:
        raise ValueError('Complete first/resident scope differs')
    expected={k:v for k,v in reference.items() if k not in METRICS}
    if len(reference['routes'])!=1062:raise ValueError('Reference is not full workload')
    for batch in raw['batches']:
        if {k:v for k,v in batch.items() if k not in METRICS}!=expected:
            raise ValueError('Bounded full route semantics differ')
    return 'two_complete_batches_equivalent'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--cpu',type=int,default=124)
    a=parser.parse_args();a.output=a.output.resolve()
    if a.cpu not in os.sched_getaffinity(0):raise ValueError('CPU unavailable')
    os.sched_setaffinity(0,{a.cpu})
    upstream=ROOT/'data/derived/native_site_runtime_validation_20261023_v1/plan.json'
    verified_path=ROOT/'results/native_site_runtime_validation_audit_20261023_v1.json'
    old=json.loads(upstream.read_text());verified=json.loads(verified_path.read_text())
    if verified['status']!='complete_site_runtime_matrix_independently_audited' or verified['completed_workers']!=3 or not verified['all_raw_complete_workloads_rechecked']:
        raise ValueError('Complete independent runtime validation required')
    if verified['artifacts'][str(upstream)]!=digest(upstream):raise ValueError('Validated plan changed')
    files=dict(old['code_inputs_and_references'])
    for path,value in files.items():
        if digest(path)!=value:raise ValueError('Frozen runtime source changed: '+path)
    binary=ROOT/'build/native_site_runtime_20261023_v1';prlimit=Path(shutil.which('prlimit') or '')
    if str(binary) not in files or not prlimit.is_file():raise ValueError('Missing bound executable')
    regression=ROOT/'results/regression_site_capacity_20261023_v1.log'
    if not regression.read_text().rstrip().endswith('OK'):raise ValueError('Capacity regression required')
    for path in (upstream,verified_path,Path(__file__),ROOT/'scripts/check_site_capacity.py',
                 ROOT/'scripts/check_template_scope.py',ROOT/'scripts/real_experiment.py',regression,prlimit):
        files[str(path)]=digest(path)
    a.output.mkdir(parents=True,exist_ok=False)
    limits=['Two full1062-net first/resident batches under the physically checked14-instance model; remaining special resource semantics are incomplete.',
        'RLIMIT_AS bounds native executable/libraries/image, routing state, search and complete traces. It is virtual address space, not RSS or board memory.',
        'Input acquisition, packing/fixture construction and Python audits are outside this bound.',
        'Single fresh process per condition and tested limit, not repeated timing or exact minimum-memory measurement.',
        'Shared host and file caches are uncontrolled; all modes retain the same complete outputs.',
        'Allocation failures preserve partial stdout and complete stderr; unexpected exceptions/signals stop the experiment.']
    plan={'owner_pid':os.getpid(),'cpu':a.cpu,'jobs':design(),'files':files,'binary':str(binary),'prlimit':str(prlimit),
          'inputs':old['inputs'],'references':old['references'],'limitations':limits,'seed':20261023}
    write_new(a.output/'plan.json',plan)
    state={'owner_pid':os.getpid(),'status':'running','stage':'capacity_trials','completed_workers':0}
    def save():
        tmp=a.output/'state.tmp';tmp.write_text(json.dumps(state,indent=2)+'\n');tmp.replace(a.output/'state.json')
    save();records=[]
    try:
        for index,job in enumerate(plan['jobs']):
            source=plan['inputs'][job['mode']];limit=job['limit_mib']*1048576
            command=[str(prlimit),f'--as={limit}:{limit}','--',str(binary),source['image'],source['fixture'],source['sites'],
                     '4096','80','200000','8',job['execution']]
            prefix=a.output/f'worker_{index:03d}';start=time.perf_counter()
            with prefix.with_suffix('.raw.json').open('x') as output,prefix.with_suffix('.log').open('x') as log:
                child=subprocess.Popen(command,stdout=output,stderr=log)
                write_new(prefix.with_suffix('.submission.json'),{'owner_pid':os.getpid(),'child_pid':child.pid,
                    'command':command,'cpu':a.cpu,'limit_bytes':limit})
                state.update(worker=index,condition=job,child_pid=child.pid);save()
                print('SITE_CAPACITY_BEGIN',index,job,child.pid,flush=True)
                code=child.wait()
            receipt={'condition':job,'exit_code':code,'process_wall_ms_diagnostic':(time.perf_counter()-start)*1000,
                'raw_sha256':digest(prefix.with_suffix('.raw.json')),'log_sha256':digest(prefix.with_suffix('.log'))}
            write_new(prefix.with_suffix('.receipt.json'),receipt)
            if code:
                outcome=allocation_failure(code,prefix.with_suffix('.log').read_text());metrics=None
            else:
                raw=json.loads(prefix.with_suffix('.raw.json').read_text())
                reference=json.loads(Path(plan['references'][job['mode']]).read_text())
                outcome=check_success(raw,reference,job)
                metrics=[{k:batch[k] for k in METRICS} for batch in raw['batches']]
                del raw,reference;gc.collect()
            record={'condition':job,'outcome':outcome,'batches':metrics,'receipt_sha256':digest(prefix.with_suffix('.receipt.json'))}
            write_new(prefix.with_suffix('.json'),record);records.append(record)
            state['completed_workers']=len(records);state.pop('child_pid',None);save()
            print('SITE_CAPACITY_VERIFIED',index,outcome,flush=True)
        for path,value in files.items():
            if digest(path)!=value:raise ValueError('Frozen capacity dependency changed')
        write_new(a.output/'report.json',{'status':'all_six_bounded_site_router_trials_classified','records':records,
            'plan_sha256':digest(a.output/'plan.json'),'limitations':limits})
        audit=a.output/'independent_audit.json'
        command=[sys.executable,str(ROOT/'scripts/check_site_capacity.py'),str(a.output),'--output',str(audit)]
        with (a.output/'independent_audit.log').open('x') as log:
            child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
            state.update(stage='independent_audit',child_pid=child.pid,command=command);save()
            code=child.wait()
        if code:raise RuntimeError('Independent capacity audit failed')
        state.update(status='complete',stage='independently_audited',audit=str(audit),audit_sha256=digest(audit))
        state.pop('child_pid',None);save()
    except Exception as exc:
        state.update(status='failed',error=str(exc));save();raise


if __name__=='__main__':main()
