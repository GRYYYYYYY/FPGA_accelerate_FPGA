#!/usr/bin/env python3
"""Validate full RTL acceptance and arm protection for one dedicated Vivado session."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from binary_fsm_full44_prerequisites_v2 import validate as validate_native
from read_control_pipeline_prerequisites_v1 import validate_prerequisites
from check_vitis_kernel import digest, require
from supervise_search_axi_dpi_v3 import atomic, identity

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_FREE_BYTES = 16*1024**3


def verify_files(files):
    require(isinstance(files, dict) and files, 'Missing file bindings')
    for name, checksum in files.items():
        require(digest(name) == checksum, 'Changed physical input/evidence: '+name)


def validate_functional(root=ROOT):
    files = validate_native(root)
    files.update(validate_prerequisites(root/'results'))
    path = root/'results/search_read_control_staging_rtl_audit_20261025_v1.json'
    require(path.is_file(), 'Complete read-control RTL acceptance missing')
    report = json.loads(path.read_text())
    require(report.get('status') == 'read_control_staging_full2tx_dpi_rtl_all_output_bytes_and_original_c_oracle_independently_verified'
            and report.get('rtl_verified') is True and report.get('transactions') == 2
            and report.get('models') == 7 and report.get('output_files') == 5, 'Incomplete read-control acceptance')
    cycles = report.get('cycles', [])
    require(len(cycles) == 2 and all(type(c) is int and c > 0 for c in cycles), 'Incomplete read-control cycles')
    verify_files(report.get('files'))
    for name, checksum in report['files'].items():
        require(name not in files or files[name] == checksum, 'Conflicting acceptance binding')
        files[name] = checksum
    files[str(path)] = digest(path)
    return files


def validate_bundle(bundle, job_name):
    plan = json.loads((bundle/'plan.json').read_text())
    require(plan['status'] == 'full_scope_physical_entries_prepared_not_executed', 'Wrong execution preparation')
    require(plan['part'] == 'xcu280-fsvh2892-2L-e' and plan['clock_ns'] == 5 and
            plan['setup_uncertainty_ns'] == 1.35 and plan['max_threads'] == 2, 'Changed physical target')
    require(plan['startup_wait_removed_by_user'] is True and plan['runtime_free_bytes'] == RUNTIME_FREE_BYTES,
            'Changed memory policy')
    require([j['name'] for j in plan['jobs']] == ['csr', 'compact', 'read_control'], 'Incomplete physical matrix')
    matches = [j for j in plan['jobs'] if j['name'] == job_name]
    require(len(matches) == 1, 'Unknown physical job')
    verify_files(plan['files'])
    for job in plan['jobs']:
        source = Path(job['work'])/'source'
        require(source.is_relative_to(bundle) and
                {p.name for p in source.iterdir() if p.is_file()} == set(job['source_names']), 'Changed complete RTL/ROM membership')
    return plan, matches[0]


def same_owner(expected):
    actual = identity(expected['pid'])
    return bool(actual and actual['start_ticks'] == expected['start_ticks'] and actual['command'] == expected['command'])


def watch(control, cg=Path('/sys/fs/cgroup')):
    plan = json.loads((control/'plan.json').read_text())
    owner = plan['owner']
    require(same_owner(owner), 'Vivado owner missing/reused before arming')
    pidfd = os.pidfd_open(owner['pid'])
    state = dict(owner_pid=os.getpid(), status='running', stage='armed', vivado_owner=owner,
                 resource_abort=False, runtime_free_bytes=RUNTIME_FREE_BYTES)
    atomic(control/'state.json', state)
    flow = Path(plan['work'])/'state.json'
    try:
        while True:
            if flow.is_file():
                result = json.loads(flow.read_text())
                require(result['owner_pid'] == owner['pid'], 'Physical flow owner changed')
                if result['status'] in ('complete', 'failed'):
                    state.update(status='complete' if result['status'] == 'complete' else 'failed',
                                 stage='flow_terminal', flow_state_sha256=digest(flow), flow_status=result['status'])
                    atomic(control/'state.json', state)
                    return
            require(same_owner(owner), 'Vivado owner disappeared without terminal flow receipt')
            free = int((cg/'memory.max').read_text())-int((cg/'memory.current').read_text())
            if free < RUNTIME_FREE_BYTES:
                state.update(resource_abort=True, triggering_raw_free_bytes=free,
                             stage='runtime_memory_abort', observed_unix=time.time())
                atomic(control/'state.json', state)
                raise RuntimeError('Physical runtime memory protection triggered')
            time.sleep(0.5)
    except BaseException as error:
        state.update(status='failed', error=str(error))
        atomic(control/'state.json', state)
        if same_owner(owner):
            signal.pidfd_send_signal(pidfd, signal.SIGTERM)
            deadline = time.monotonic()+15
            while same_owner(owner) and time.monotonic() < deadline:
                time.sleep(0.5)
            if same_owner(owner):
                signal.pidfd_send_signal(pidfd, signal.SIGKILL)
        raise
    finally:
        os.close(pidfd)


def arm(bundle, name, owner_pid):
    # Reject missing actual RTL before creating a control/trial state or subprocess.
    functional = validate_functional()
    plan, job = validate_bundle(bundle, name)
    work = Path(job['work'])
    require(not (work/'state.json').exists() and not (work/'guard').exists(), 'Existing physical execution; refuse restart')
    chain_path = ROOT/'data/derived/integrated_rtl_recovery_supervision_20261027_v1/state.json'
    chain = json.loads(chain_path.read_text())
    require(chain['status'] == 'complete' and chain['stage'] == 'four_downstream_rtl_experiments_independently_audited',
            'Full local RTL chain has not completed')
    require(identity(chain['owner_pid']) is None, 'Functional chain owner still live')
    # At most one physical mode at a time. A prior measured quality failure is retained.
    for other in plan['jobs']:
        if other['name'] == name:
            continue
        control = Path(other['work'])/'guard'
        if (control/'plan.json').exists():
            prior = json.loads((control/'plan.json').read_text())
            require(not same_owner(prior['owner']), 'Another physical mode session still live')
    owner = identity(owner_pid)
    require(owner and 'vivado' in owner['command'] and owner['cwd'] == str(work), 'Dedicated Vivado owner/cwd mismatch')
    cg = Path('/sys/fs/cgroup')
    free = int((cg/'memory.max').read_text())-int((cg/'memory.current').read_text())
    require(free >= RUNTIME_FREE_BYTES, 'Runtime protection already active at entry')
    control = work/'guard'
    control.mkdir(exist_ok=False)
    atomic(control/'plan.json', dict(owner=owner, work=str(work), job=name, functional_files=functional,
           bundle_plan_sha256=digest(bundle/'plan.json'), script_sha256=digest(__file__), entry_raw_free_bytes=free,
           runtime_free_bytes=RUNTIME_FREE_BYTES, functional_chain_state_sha256=digest(chain_path)))
    with (control/'watch.log').open('x') as log:
        child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--watch', str(control)],
                                 cwd=ROOT, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    deadline = time.monotonic()+15
    while time.monotonic() < deadline and child.poll() is None:
        if (control/'state.json').exists():
            state = json.loads((control/'state.json').read_text())
            require(state['owner_pid'] == child.pid and state['status'] == 'running' and state['stage'] == 'armed',
                    'Physical protection failed to arm')
            print('PHYSICAL_PROTECTION_ARMED '+str(child.pid), flush=True)
            return
        time.sleep(0.05)
    if child.poll() is None:
        child.terminate()
        try: child.wait(timeout=5)
        except subprocess.TimeoutExpired: child.kill(); child.wait()
    raise RuntimeError('Physical protection did not arm; do not source flow')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path)
    parser.add_argument('--job', choices=['csr', 'compact', 'read_control'])
    parser.add_argument('--owner-pid', type=int)
    parser.add_argument('--watch', type=Path)
    args = parser.parse_args()
    if args.watch:
        watch(args.watch.resolve())
    else:
        require(args.bundle and args.job and args.owner_pid, 'bundle/job/owner-pid required')
        arm(args.bundle.resolve(), args.job, args.owner_pid)


if __name__ == '__main__':
    main()
