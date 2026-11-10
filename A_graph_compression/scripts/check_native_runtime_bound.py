#!/usr/bin/env python3
"""Extend the frozen canonical-runtime auditor with exact submission bindings."""
import argparse
import json
from pathlib import Path
from check_native_runtime import audit as original_audit
from check_vitis_kernel import digest,require

ROOT=Path(__file__).resolve().parents[1]


def audit(directory,capacities,repeats,partial=False):
    plan=json.loads((directory/'plan.json').read_text())
    binary=str(ROOT/'build/native_runtime_20261023_v1')
    require(binary in plan['code_inputs_and_references'],'Native executable is not bound')
    submissions={}
    for index,condition in enumerate(plan['jobs']):
        prefix=directory/f'worker_{index:03d}'
        if partial and not prefix.with_suffix('.json').exists():continue
        path=prefix.with_suffix('.submission.json');submission=json.loads(path.read_text())
        inputs=plan['inputs'][condition['mode']]
        command=[binary,inputs['image'],inputs['fixture'],str(condition['capacity']),
                 '80','200000','8',condition['execution']]
        require(submission['command']==command,'Submitted mode/cache/workload command differs')
        require(submission['owner_pid']==plan['owner_pid'],'Submission owner differs')
        require(type(submission['child_pid']) is int and submission['child_pid']>0,'Invalid child PID')
        submissions[str(path)]=digest(path)
    result=original_audit(directory,capacities,repeats,partial)
    require(result['completed_workers']==len(submissions),'Submission/worker domain differs')
    result['artifacts'].update(submissions)
    result['artifacts'][str(ROOT/'scripts/check_native_runtime.py')]=digest(ROOT/'scripts/check_native_runtime.py')
    result['artifacts'][str(Path(__file__).resolve())]=digest(__file__)
    result['submission_commands_verified']=len(submissions)
    result['bound_auditor_sha256']=digest(__file__)
    result['limitations']+=['These are the earlier canonical-only router trials; their physical site validation failed. Do not combine with the later site-model statistics.',
        'Original raw format has no execution-mode tag. The exact submitted command and frozen binary bind the mode; no retrospective runtime tag is invented.']
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('experiment',type=Path)
    p.add_argument('--capacities',nargs='+',type=int,default=[0,64,4096]);p.add_argument('--repeats',type=int,default=7)
    p.add_argument('--partial',action='store_true');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    report=audit(a.experiment.resolve(),a.capacities,a.repeats,a.partial)
    with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({'status':report['status'],'workers':report['completed_workers'],'submissions':report['submission_commands_verified']}))


if __name__=='__main__':main()
