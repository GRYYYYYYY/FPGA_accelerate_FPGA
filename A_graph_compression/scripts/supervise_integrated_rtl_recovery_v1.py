#!/usr/bin/env python3
"""Continue the full integrated RTL chain after native v3 independent acceptance."""
import ast
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from binary_fsm_full44_prerequisites_v2 import validate as validate_native
from check_vitis_kernel import digest, require
from supervise_search_axi_dpi_v3 import atomic, identity

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/tmp/A_graph_compression_recovery_20261025_v1')
OUT = ROOT / 'data/derived/integrated_rtl_recovery_supervision_20261027_v1'
UPSTREAM = BASE / 'compact_native_stack_final_audit_v3'


def jobs(root=ROOT, base=BASE):
    specs = [
        ('csr', 'compressed_bus64_binary_fsm_rtl_v2', 'compressed_batch_bus64_binary_fsm_rtl_v2',
         'compressed_bus64_binary_fsm_rtl_audit_20261025_v1.json',
         'binary_fsm_full44_four_transaction_dpi_rtl_original_c_and_complete_snapshots_independently_verified', 4, 44, 30),
        ('compact', 'compressed_compact_bus64_binary_fsm_rtl_v2', 'compressed_batch_compact_bus64_binary_fsm_rtl_v2',
         'compressed_compact_bus64_binary_fsm_rtl_audit_20261025_v1.json',
         'compact_binary_fsm_full44_four_transaction_dpi_rtl_original_c_and_complete_snapshots_independently_verified', 4, 44, 30),
        ('snapshot', 'snapshot_dpi_rtl_v4', 'snapshot_dpi_rtl_v4',
         'snapshot_dpi_rtl_audit_20261025_v3.json',
         'full30_snapshot_dpi_rtl_original_c_and_every_complete_output_word_independently_verified', 30, 13, 10),
        ('read_control', 'search_read_control_staging_dpi_rtl_v3', 'search_read_control_staging_dpi_rtl_v3',
         'search_read_control_staging_rtl_audit_20261025_v1.json',
         'read_control_staging_full2tx_dpi_rtl_all_output_bytes_and_original_c_oracle_independently_verified', 2, None, 7),
    ]
    return [dict(name=name, driver=str(root/'scripts'/('run_'+stem+'.py')),
                 checker=str(root/'scripts'/('check_'+stem+'.py')), bundle=str(base/bundle),
                 report=str(root/'results'/report), accepted_status=status,
                 transactions=tx, pointers=ports, models=models)
            for name, stem, bundle, report, status, tx, ports, models in specs]


def verify_files(files):
    for path, checksum in files.items():
        require(digest(path) == checksum, 'Changed scheduled input: '+path)


def source_closure(paths, scripts):
    """Freeze local Python imports too; no imports are executed by this walk."""
    pending = list(paths)
    files = {}
    while pending:
        path = Path(pending.pop()).resolve()
        if str(path) in files:
            continue
        files[str(path)] = digest(path)
        if path.suffix != '.py':
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            names = ([node.module] if isinstance(node, ast.ImportFrom) and node.module else
                     [item.name for item in node.names] if isinstance(node, ast.Import) else [])
            for name in names:
                local = scripts/(name.split('.')[0]+'.py')
                if local.is_file():
                    pending.append(local)
    return files


def wait_upstream(folder, owner, lookup=identity, sleep=time.sleep):
    while True:
        state = json.loads((folder/'state.json').read_text())
        require(state['owner_pid'] == owner['pid'], 'Upstream audit owner changed')
        if state['status'] != 'running':
            require(state['status'] == 'complete' and state['stage'] == 'independently_audited',
                    'Native v3 independent acceptance failed; do not start downstream')
            if lookup(owner['pid']) != owner:
                return
        else:
            require(lookup(owner['pid']) == owner,
                    'Upstream owner missing or replaced without terminal acceptance')
        sleep(30)


def accept_report(job):
    path = Path(job['report'])
    require(path.is_file(), 'Independent acceptance report missing: '+job['name'])
    report = json.loads(path.read_text())
    require(report.get('status') == job['accepted_status'], 'Wrong independent status')
    cycles = report.get('cycles', [])
    require(len(cycles) == job['transactions'] and all(type(c) is int and c > 0 for c in cycles),
            'Incomplete transaction cycles')
    require(report.get('models') == job['models'], 'Incomplete model matrix')
    if job['name'] in ('csr', 'compact'):
        require(report.get('ports') == 44 and report.get('candidate_encoding_changed') is True,
                'Wrong full44 encoded candidate')
        snapshots = report.get('snapshots', [])
        require([s.get('transaction') for s in snapshots] == list(range(4)) and
                all(s.get('bytes') == 946498280 for s in snapshots), 'Incomplete full snapshots')
    else:
        require(report.get('rtl_verified') is True and report.get('transactions') == job['transactions'],
                'Incomplete RTL acceptance')
        if job['name'] == 'snapshot':
            require(report.get('pointers') == 13, 'Incomplete snapshot pointer matrix')
        else:
            require(report.get('output_files') == 5, 'Incomplete search output matrix')
    bindings = report.get('files')
    require(isinstance(bindings, dict) and bindings, 'Missing independent report bindings')
    verify_files(bindings)
    return digest(path)


def execute_jobs(schedule, files, out, state, root=ROOT):
    """One driver then independent checker per job; never retry or skip a failure."""
    for job in schedule:
        require(not Path(job['bundle']).exists() and not Path(job['report']).exists(),
                'Trial/report appeared before execution; refuse duplicate')
        commands = [('execute', [sys.executable, job['driver']]),
                    ('independent_audit', [sys.executable, job['checker'], '--bundle', job['bundle'],
                                           '--output', job['report']])]
        for phase, command in commands:
            verify_files(files)
            label = job['name']+'_'+phase
            state.update(stage=label)
            atomic(out/'state.json', state)
            start = time.monotonic()
            log = out/(label+'.log')
            with log.open('x') as stream:
                child = subprocess.Popen(command, cwd=root, stdout=stream, stderr=subprocess.STDOUT)
                state['child_pid'] = child.pid
                atomic(out/'state.json', state)
                code = child.wait()
            atomic(out/(label+'.receipt.json'), dict(command=command, exit_code=code,
                   elapsed_seconds=time.monotonic()-start, log_sha256=digest(log)))
            state.pop('child_pid', None)
            require(code == 0, 'Phase failed without retry: '+label)
        checksum = accept_report(job)
        state.setdefault('accepted', []).append(dict(name=job['name'], report=job['report'], sha256=checksum))
        atomic(out/'state.json', state)


def main():
    schedule = jobs()
    require(not OUT.exists(), 'Existing chain owner directory; refuse duplicate')
    for job in schedule:
        require(not Path(job['bundle']).exists() and not Path(job['report']).exists(),
                'Existing trial/report; reconcile before scheduling')
    # These are old failed supervisors, not dependencies of the new run.
    for pid in (1909485, 2817644, 3163169, 3560722):
        require(identity(pid) is None, 'Historical downstream PID reused/live; reconcile identity')
    prior = json.loads((UPSTREAM/'state.json').read_text())
    owner = identity(prior['owner_pid'])
    require(owner and owner['cwd'] == str(ROOT) and
            'supervise_compact_native_stack_recovery_audit_v3.py' in owner['command'],
            'Native v3 independent audit owner unavailable')
    kernel = json.loads((BASE/'compact_native_stack_recovery_v3/actual_runtime_limits.json').read_text())
    execution = json.loads((BASE/'compact_native_stack_recovery_v3/state.json').read_text())
    execution_owner = identity(execution['owner_pid'])
    require(execution_owner and 'run_compact_native_stack_recovery_v3.py' in execution_owner['command'],
            'Native v3 execution owner unavailable')
    paths = [Path(__file__).resolve(), UPSTREAM/'plan.json',
             ROOT/'data/derived/integrated_rtl_recovery_chain_20261027_v1/source_changes.json',
             ROOT/'results/compact_native_guard_recovery_launch_20261027_v3.json']
    paths += [Path(job[key]) for job in schedule for key in ('driver', 'checker')]
    files = source_closure(paths, ROOT/'scripts')
    OUT.mkdir(exist_ok=False)
    atomic(OUT/'plan.json', dict(jobs=schedule, upstream_owner=owner, execution_owner=execution_owner,
           upstream_kernel=kernel, files=files, startup_wait_removed_by_user=True,
           per_process_address_space_limit_bytes=64*1024**3, runtime_free_bytes=16*1024**3,
           policy='Native v3 independent acceptance then CSR/compact/full30/read, each one execution and audit; no retry, cap increase, physical or board launch'))
    state = dict(owner_pid=os.getpid(), status='running', stage='waiting_native_v3_independent_acceptance', accepted=[])
    atomic(OUT/'state.json', state)
    try:
        wait_upstream(UPSTREAM, owner)
        require(identity(execution_owner['pid']) != execution_owner, 'Native execution owner still active')
        live_kernel = identity(kernel['pid'])
        require(not live_kernel or live_kernel['start_ticks'] != kernel['start_ticks'], 'Native kernel still active')
        verify_files(files)
        native_bindings = validate_native()
        atomic(OUT/'native_acceptance_bindings.json', native_bindings)
        execute_jobs(schedule, files, OUT, state)
        state.update(status='complete', stage='four_downstream_rtl_experiments_independently_audited')
        atomic(OUT/'state.json', state)
    except BaseException as error:
        state.update(status='failed', error=str(error))
        atomic(OUT/'state.json', state)
        raise


if __name__ == '__main__':
    main()
