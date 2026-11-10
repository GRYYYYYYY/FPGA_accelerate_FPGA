#!/usr/bin/env python3
"""Re-read bounded router outputs, exact execution limits and full semantic references."""
import argparse
import gc
import json
from pathlib import Path
import random
import re
from check_template_scope import digest
from real_experiment import write_new
METRICS={'preparation_ms','route_ms','peak_kib','logical_bytes','cache_hits','cache_misses'}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('directory',type=Path)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--partial',action='store_true')
    a=parser.parse_args();directory=a.directory.resolve();plan_path=directory/'plan.json'
    plan=json.loads(plan_path.read_text())
    jobs=[{'limit_mib':limit,'mode':mode,'execution':execution,'cache_rows':4096}
        for limit in (3072,4096) for mode,execution in [('csr','direct'),('compact','direct'),('compact','expanded')]]
    random.Random(20261023).shuffle(jobs)
    if plan['jobs']!=jobs:raise ValueError('Full matrix differs')
    for path,value in plan['files'].items():
        if digest(path)!=value:raise ValueError('Bound evidence changed: '+path)
    artifacts={str(plan_path):digest(plan_path)};outcomes=[]
    for index,job in enumerate(jobs):
        prefix=directory/f'worker_{index:03d}'
        record_path=prefix.with_suffix('.json')
        if a.partial and not record_path.exists():continue
        record=json.loads(record_path.read_text());receipt_path=prefix.with_suffix('.receipt.json')
        receipt=json.loads(receipt_path.read_text());sub_path=prefix.with_suffix('.submission.json')
        submission=json.loads(sub_path.read_text());source=plan['inputs'][job['mode']];size=job['limit_mib']*1048576
        command=[plan['prlimit'],f'--as={size}:{size}','--',plan['binary'],source['image'],source['fixture'],source['sites'],
                 '4096','80','200000','8',job['execution']]
        if submission['command']!=command or submission['cpu']!=plan['cpu'] or submission['owner_pid']!=plan['owner_pid'] or submission['limit_bytes']!=size:
            raise ValueError('Actual resource-constrained execution differs')
        raw_path=prefix.with_suffix('.raw.json');log_path=prefix.with_suffix('.log')
        if digest(raw_path)!=receipt['raw_sha256'] or digest(log_path)!=receipt['log_sha256'] or record['receipt_sha256']!=digest(receipt_path):
            raise ValueError('Raw output or receipt changed')
        if receipt['condition']!=job or record['condition']!=job:raise ValueError('Condition differs')
        if receipt['exit_code']==0:
            raw=json.loads(raw_path.read_text());reference=json.loads(Path(plan['references'][job['mode']]).read_text())
            expected={k:v for k,v in reference.items() if k not in METRICS}
            if len(reference['routes'])!=1062 or raw['execution']!=job['execution'] or len(raw['batches'])!=2 or len(raw['export_ms'])!=2:
                raise ValueError('Not the full first/resident workload')
            for batch in raw['batches']:
                if {k:v for k,v in batch.items() if k not in METRICS}!=expected:
                    raise ValueError('Complete route tree/attributes/round states differ')
            if record['batches']!=[{k:b[k] for k in METRICS} for b in raw['batches']]:raise ValueError('Reported metrics differ')
            outcome='two_complete_batches_equivalent';del raw,reference,expected;gc.collect()
        else:
            lines=log_path.read_text().splitlines()
            if receipt['exit_code']!=1 or not lines or lines[-1]!='std::bad_alloc' or any(not re.fullmatch(r'NATIVE_SITE_PROGRESS \d+ \d+',line) for line in lines[:-1]):
                raise ValueError('Unexpected failure is not an allocation-limit result')
            if record['batches'] is not None:raise ValueError('Failed run claims complete batch metrics')
            outcome='address_space_allocation_failed'
        if record['outcome']!=outcome:raise ValueError('Incorrect outcome classification')
        outcomes.append(record)
        artifacts.update({str(p):digest(p) for p in (record_path,receipt_path,sub_path,raw_path,log_path)})
    if not outcomes:raise ValueError('No completed trial')
    if not a.partial:
        report_path=directory/'report.json';report=json.loads(report_path.read_text())
        if report['status']!='all_six_bounded_site_router_trials_classified' or report['plan_sha256']!=digest(plan_path) or report['records']!=outcomes:
            raise ValueError('Final report lacks complete matrix binding')
        artifacts[str(report_path)]=digest(report_path)
        for mode,execution in [('csr','direct'),('compact','direct'),('compact','expanded')]:
            selected=sorted([r for r in outcomes if r['condition']['mode']==mode and r['condition']['execution']==execution],key=lambda r:r['condition']['limit_mib'])
            if selected[0]['outcome']=='two_complete_batches_equivalent' and selected[1]['outcome']!='two_complete_batches_equivalent':
                raise ValueError('Nonmonotone feasibility needs investigation')
    write_new(a.output,{'status':'partial_bounded_router_outcomes_audited' if a.partial else 'all_six_bounded_router_outcomes_independently_audited',
        'completed_workers':len(outcomes),'planned_workers':6,'outcomes':outcomes,'artifacts':artifacts,
        'auditor_sha256':digest(Path(__file__)),'limitations':plan['limitations']})
    print('SITE_CAPACITY_AUDITED',len(outcomes),'partial' if a.partial else 'complete')


if __name__=='__main__':main()
