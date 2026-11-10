#!/usr/bin/env python3
"""Validate full RTL acceptance and arm protection for one dedicated Vivado session."""
import argparse
import json
import os
from pathlib import Path
import signal
import resource
import subprocess
import sys
import time

from snapshot_read_serial_prerequisites_v2 import validate_read,merge_report,READ,SNAPSHOT
from owned_sim_resource_policy_v1 import POLICY,observe,abort_reason
from check_vitis_kernel import digest, require
from supervise_search_axi_dpi_v3 import atomic, identity

ROOT = Path(__file__).resolve().parents[1]
PHYSICAL_AS_BYTES = 192*1024**3
SIM_BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')


def verify_files(files):
    require(isinstance(files, dict) and files, 'Missing file bindings')
    for name, checksum in files.items():
        require(digest(name) == checksum, 'Changed physical input/evidence: '+name)


def validate_functional(root=ROOT):
    files=validate_read(root)
    path=root/'results'/READ
    report=merge_report(path,files)
    require(report.get('status')=='read_control_staging_full2tx_dpi_rtl_all_output_bytes_and_original_c_oracle_independently_verified'
            and report.get('rtl_verified') is True and (report.get('transactions'),report.get('pointers'),report.get('models'),report.get('pages'),report.get('output_files'))==(2,13,7,4,5),'Incomplete current read-control acceptance')
    require(report.get('resource_policy')==POLICY and report.get('original_address_environment_unchanged') is True and report.get('original_cycle_parity_claimed') is False,'Different read-control identity')
    cycles=report.get('cycles',[])
    require(len(cycles)==2 and all(type(c) is int and c>0 for c in cycles),'Incomplete read-control cycles')
    require(report['files'].get(str(root/'results'/SNAPSHOT))==files[str(root/'results'/SNAPSHOT)],'Read control accepted a different full30 snapshot')
    return files


def validate_accepted_sources(plan,functional):
    trials={'csr':'collision_safe_bus64_full_rtl_v1/mode_0',
            'compact':'collision_safe_bus64_full_rtl_v1/mode_1',
            'read_control':'search_read_control_staging_dpi_rtl_v5'}
    result={}
    for job in plan['jobs']:
        source=Path(job['work'])/'source';sim=SIM_BASE/trials[job['name']]/'sim/verilog'
        for name in job['source_names']:
            physical=source/name;accepted=sim/name
            require(functional.get(str(accepted))==digest(physical),'Physical DUT/ROM differs from actual accepted same-mode RTL: '+str(physical))
        result[job['name']]=dict(source_files=len(job['source_names']),accepted_sim=str(sim))
    return result


def validate_bundle(bundle, job_name):
    plan = json.loads((bundle/'plan.json').read_text())
    require(plan['status'] == 'full_scope_physical_entries_prepared_not_executed', 'Wrong execution preparation')
    require(plan['part'] == 'xcu280-fsvh2892-2L-e' and plan['clock_ns'] == 5 and
            plan['setup_uncertainty_ns'] == 1.35 and plan['max_threads'] == 2, 'Changed physical target')
    require(plan['startup_wait_removed_by_user'] is True and plan['runtime_rawfree_gate_removed_by_user'] is True and plan['resource_policy']==POLICY and plan['physical_as_bytes']==PHYSICAL_AS_BYTES,
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


def watch(control,cg=Path('/sys/fs/cgroup')):
    plan=json.loads((control/'plan.json').read_text());owner=plan['owner']
    require(same_owner(owner),'Vivado owner missing/reused before arming')
    require(plan['resource_policy']==POLICY and plan['physical_as_bytes']==PHYSICAL_AS_BYTES,'Different physical resource policy')
    initial=plan['entry_memory'];pidfd=os.pidfd_open(owner['pid'])
    state=dict(owner_pid=os.getpid(),status='running',stage='armed',vivado_owner=owner,
               resource_abort=False,resource_policy=POLICY,physical_as_bytes=PHYSICAL_AS_BYTES)
    atomic(control/'state.json',state);flow=Path(plan['work'])/'state.json';last_sample=0
    try:
        while True:
            current=observe(cg);reason=abort_reason(initial,current)
            if reason is not None:
                state.update(resource_abort=True,resource_abort_reason=reason,resource_abort_observation=current,
                             stage='runtime_oom_abort',observed_unix=time.time())
                atomic(control/'state.json',state)
                raise RuntimeError('New cgroup OOM event during physical flow')
            if time.monotonic()-last_sample>=30:
                atomic(control/'resource_observation.json',current);last_sample=time.monotonic()
            if flow.is_file():
                result=json.loads(flow.read_text());require(result['owner_pid']==owner['pid'],'Physical flow owner changed')
                if result['status'] in ('complete','failed'):
                    state.update(status='complete' if result['status']=='complete' else 'failed',stage='flow_terminal',
                                 flow_state_sha256=digest(flow),flow_status=result['status'],end_memory=current)
                    atomic(control/'state.json',state);return
            require(same_owner(owner),'Vivado owner disappeared without terminal flow receipt')
            time.sleep(.5)
    except BaseException as error:
        state.update(status='failed',error=str(error));atomic(control/'state.json',state)
        if same_owner(owner):
            signal.pidfd_send_signal(pidfd,signal.SIGTERM)
            deadline=time.monotonic()+15
            while same_owner(owner) and time.monotonic()<deadline:time.sleep(.5)
            if same_owner(owner):signal.pidfd_send_signal(pidfd,signal.SIGKILL)
        raise
    finally:os.close(pidfd)


def arm(bundle, name, owner_pid):
    # Reject missing actual RTL before creating a control/trial state or subprocess.
    functional = validate_functional()
    plan, job = validate_bundle(bundle, name)
    accepted_sources=validate_accepted_sources(plan,functional)
    work = Path(job['work'])
    require(not (work/'state.json').exists() and not (work/'guard').exists(), 'Existing physical execution; refuse restart')
    chain_path = ROOT/'data/derived/snapshot_read_serial_supervision_20261031_v2/state.json'
    chain = json.loads(chain_path.read_text())
    require(chain['status'] == 'complete' and chain['stage'] == 'full30_snapshot_and_read_control_independently_audited',
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
    entry_memory=observe()
    previous_limits=dict(address_space=list(resource.prlimit(owner_pid,resource.RLIMIT_AS)),core=list(resource.prlimit(owner_pid,resource.RLIMIT_CORE)))
    require(all(limit==-1 or limit>=PHYSICAL_AS_BYTES for limit in previous_limits['address_space']),
            'Existing Vivado AS is below the prepared cap; no automatic cap increase')
    resource.prlimit(owner_pid,resource.RLIMIT_AS,(PHYSICAL_AS_BYTES,PHYSICAL_AS_BYTES))
    resource.prlimit(owner_pid,resource.RLIMIT_CORE,(0,0))
    require(resource.prlimit(owner_pid,resource.RLIMIT_AS)==(PHYSICAL_AS_BYTES,PHYSICAL_AS_BYTES) and resource.prlimit(owner_pid,resource.RLIMIT_CORE)==(0,0),'Physical limits not applied')
    require(same_owner(owner),'Vivado owner changed during limit setup')
    control = work/'guard'
    control.mkdir(exist_ok=False)
    atomic(control/'plan.json', dict(owner=owner, work=str(work), job=name, functional_files=functional,
           bundle_plan_sha256=digest(bundle/'plan.json'), script_sha256=digest(__file__),entry_memory=entry_memory,resource_policy=POLICY,
           physical_as_bytes=PHYSICAL_AS_BYTES,previous_limits=previous_limits,actual_address_space=[PHYSICAL_AS_BYTES]*2,actual_core=[0,0],
           accepted_source_bindings=accepted_sources,functional_chain_state_sha256=digest(chain_path)))
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
