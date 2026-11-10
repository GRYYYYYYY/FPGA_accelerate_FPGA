#!/usr/bin/env python3
"""Run each full real workload once, then independently compare every raw semantic field."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import subprocess
import time
from check_vitis_kernel import digest, require

ROOT = Path(__file__).resolve().parents[1]


def save(path, value):
    with path.open('x') as stream:json.dump(value, stream, indent=2);stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__);parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True);args = parser.parse_args()
    out = args.bundle.resolve();output = args.output.resolve()
    require(not (out / 'state.json').exists() and not output.exists(), 'Existing owner or output; reconcile instead of restarting')
    prep = json.loads((out / 'prepare_state.json').read_text());require(prep['status'] == 'complete', 'Preparation incomplete')
    report = json.loads((out / 'report.json').read_text())
    require(report['status'] == 'bounded_site_occupancy_full_search_cpu_differential_verified_full_workload_pending', 'Missing differential gate')
    for p, sha in {**report['files'], **report['artifacts']}.items():require(digest(p) == sha, 'Changed input ' + p)
    plan = json.loads((out / 'plan.json').read_text())
    old_plan = json.loads((Path(plan['prior_bundle']) / 'plan.json').read_text())
    old_execution = json.loads((Path(plan['prior_bundle']) / 'execution_plan.json').read_text())
    for mode, inp in plan['inputs'].items():
        require(inp == old_plan['inputs'][mode], 'Different full workload inputs')
        for p in inp.values():require(digest(p) == old_execution['files'][p], 'Changed full workload input ' + p)
    files = [out / 'plan.json', out / 'report.json', out / 'prepare_state.json', Path(__file__).resolve(),
             ROOT / 'scripts/check_site_occupancy_router.py', ROOT / 'scripts/check_vitis_kernel.py']
    for inp in plan['inputs'].values(): files.extend(map(Path, inp.values()))
    execution = dict(files={str(p): digest(p) for p in files}, jobs=plan['jobs'], output=str(output),
                     policy='One owner; four full workload batches. Any failure is retained; never auto-restart.')
    save(out / 'execution_plan.json', execution)
    state = dict(owner_pid=os.getpid(), status='running', stage='four_full_workloads', completed=[])
    save(out / 'state.json', state)
    def update():
        temp = out / 'state.tmp';temp.write_text(json.dumps(state, indent=2) + '\n');temp.replace(out / 'state.json')
    def run(index, job):
        inp = plan['inputs'][job['mode']];prefix = out / f'worker_{index:03d}'
        command = ['taskset', '-c', str(job['cpu']), plan['binary'], inp['image'], inp['fixture'], inp['sites'],
                   '4096', '80', '200000', '8', 'kernel', inp['config']]
        with prefix.with_suffix('.raw.json').open('x') as raw, prefix.with_suffix('.log').open('x') as log:
            started = time.monotonic();child = subprocess.Popen(command, stdout=raw, stderr=log, cwd=ROOT)
            save(prefix.with_suffix('.submission.json'), dict(command=command, condition=job, child_pid=child.pid,
                owner_pid=os.getpid(), execution_plan_sha256=digest(out / 'execution_plan.json')))
            code = child.wait();wall = 1000 * (time.monotonic() - started)
        save(prefix.with_suffix('.receipt.json'), dict(command=command, condition=job, exit_code=code,
            process_wall_ms=wall, raw_sha256=digest(prefix.with_suffix('.raw.json')), log_sha256=digest(prefix.with_suffix('.log'))))
        require(code == 0, 'Workload failed ' + str(index));return index
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            for future in as_completed([pool.submit(run, i, j) for i, j in enumerate(plan['jobs'])]):
                state['completed'].append(future.result());update()
        state['stage'] = 'independent_full_audit';update()
        for p, sha in execution['files'].items(): require(digest(p) == sha, 'Changed execution dependency ' + p)
        command = ['taskset', '-c', '116', 'python3', str(ROOT / 'scripts/check_site_occupancy_router.py'),
                   '--bundle', str(out), '--output', str(output)]
        with (out / 'audit.log').open('x') as log:code = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, cwd=ROOT).returncode
        save(out / 'audit_receipt.json', dict(command=command, exit_code=code, log_sha256=digest(out / 'audit.log')))
        require(code == 0, 'Independent full audit failed')
        state.update(status='complete', stage='independently_audited');update()
    except BaseException as error:
        state.update(status='failed', error=str(error));update();raise


if __name__ == '__main__':main()
