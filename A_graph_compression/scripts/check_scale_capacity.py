#!/usr/bin/env python3
"""Independent receipt/command/coverage audit for the bounded native decoder matrix."""
import argparse
import json
from pathlib import Path
import random
from check_template_scope import digest
from real_experiment import write_new


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path);parser.add_argument('--output',type=Path,required=True)
    a=parser.parse_args();directory=a.directory.resolve()
    plan_path=directory/'plan.json';report_path=directory/'report.json'
    plan=json.loads(plan_path.read_text());report=json.loads(report_path.read_text())
    for path,value in plan['files'].items():
        if digest(path)!=value:raise ValueError('Bound dependency changed')
    if report['status']!='all_48_bounded_native_scan_outcomes_verified' or report['plan_sha256']!=digest(plan_path):
        raise ValueError('Missing complete report binding')
    jobs=[{'denominator':d,'mode':m,'limit_mib':b} for d in (16,4,2,1) for b in (8,16,32,64,96,128) for m in ('csr','compact')]
    random.Random(20261023).shuffle(jobs)
    if plan['jobs']!=jobs or len(report['records'])!=48:raise ValueError('Matrix scope differs')
    binaries=[Path(p) for p in plan['files'] if Path(p).name=='native_scan']
    if len(binaries)!=1:raise ValueError('Ambiguous executable')
    binary=binaries[0];source=binary.parent
    original=json.loads((source/'report.json').read_text())
    if plan['files'][str(source/'report.json')]!=digest(source/'report.json'):raise ValueError('Source reference changed')
    domains={d['denominator']:d for d in original['domains']}
    prlimit=[p for p in plan['files'] if Path(p).name=='prlimit']
    if len(prlimit)!=1:raise ValueError('Missing resource limit executable')
    matrix={};artifacts={str(plan_path):digest(plan_path),str(report_path):digest(report_path)}
    for index,job in enumerate(jobs):
        prefix=directory/f'worker_{index:03d}'
        receipt_path=prefix.with_suffix('.receipt.json');submission_path=prefix.with_suffix('.submission.json')
        receipt=json.loads(receipt_path.read_text());submission=json.loads(submission_path.read_text())
        size=job['limit_mib']*1048576
        image=source/f"fraction_1_{job['denominator']}"/(job['mode']+'.agr')
        expected=[prlimit[0],f'--as={size}:{size}','--',str(binary),str(image)]
        if submission['command']!=expected or submission['cpu']!=plan['cpu'] or submission['owner_pid']!=plan['owner_pid'] or submission['address_space_limit_bytes']!=size:
            raise ValueError('Actual constrained execution differs')
        if receipt['condition']!=job:raise ValueError('Receipt condition differs')
        if receipt['exit_code']==0:
            if receipt['stderr'] or json.loads(receipt['stdout'])!=domains[job['denominator']]['modes'][job['mode']]['native']:
                raise ValueError('Complete reference scan differs')
            outcome='complete_equivalent_scan'
        elif receipt['exit_code']==3 and receipt['stdout']=='' and receipt['stderr']=='ALLOCATION_FAILED\n':
            outcome='address_space_allocation_failed'
        else:raise ValueError('Unexplained failure cannot count as capacity limit')
        if report['records'][index]!={'condition':job,'outcome':outcome,'receipt_sha256':digest(receipt_path)}:
            raise ValueError('Summary contradicts raw outcome')
        key=f"1/{job['denominator']}/{job['mode']}"
        matrix.setdefault(key, {})[str(job['limit_mib'])]=outcome
        artifacts.update({str(p):digest(p) for p in (receipt_path,submission_path)})
    summary=[]
    for denominator in (16,4,2,1):
        row={'denominator':denominator,'nodes':domains[denominator]['counts']['nodes'],
             'known_rows':domains[denominator]['counts']['roots'],'modes':{}}
        for mode in ('csr','compact'):
            outcomes=matrix[f'1/{denominator}/{mode}']
            passed=sorted(int(b) for b,o in outcomes.items() if o=='complete_equivalent_scan')
            failed=sorted(int(b) for b,o in outcomes.items() if o=='address_space_allocation_failed')
            if not passed or failed and max(failed)>min(passed):raise ValueError('Missing success or nonmonotone outcomes')
            row['modes'][mode]={'image_bytes':domains[denominator]['modes'][mode]['layout']['file_bytes'],
                'smallest_successful_tested_limit_mib':min(passed),'failed_tested_limits_mib':failed}
        summary.append(row)
    write_new(a.output,{'status':'all_48_bounded_native_scans_independently_audited','workers':48,
        'summary':summary,'matrix':matrix,'artifacts':artifacts,'auditor_sha256':digest(Path(__file__)),
        'limitations':report['limitations']})
    print(json.dumps(summary))


if __name__=='__main__':main()
