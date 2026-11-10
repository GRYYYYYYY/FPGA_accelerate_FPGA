#!/usr/bin/env python3
"""One serial continuation: accepted full30 snapshot, compact full44, staged search."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from check_vitis_kernel import digest, require
from supervise_search_axi_dpi_v3 import atomic, identity
from compact_bus64_prerequisites_v1 import validate_prerequisites

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/tmp/A_graph_compression_recovery_20261025_v1')


def main():
    upstream = ROOT/'data/derived/snapshot_dpi_supervision_20261025_v2'
    prior = json.loads((upstream/'state.json').read_text())
    owner = identity(prior['owner_pid'])
    require(owner and 'supervise_snapshot_dpi_rtl_v2.py' in owner['command'], 'Expected existing snapshot supervisor missing')
    jobs = [
        dict(name='compact_full44', driver='run_compressed_compact_bus64_dpi_rtl_v2.py', checker='check_compressed_compact_bus64_dpi_rtl_v2.py',
             bundle='compressed_batch_compact_bus64_dpi_rtl_v2', report='compressed_compact_bus64_dpi_rtl_audit_20261025_v1.json', free_gib=168,
             accepted='compact_bus64_full44_four_transaction_dpi_rtl_c_postcheck_and_complete_snapshots_independently_verified'),
        dict(name='staged_search_full2', driver='run_search_read_control_staging_dpi_rtl_v1.py', checker='check_search_read_control_staging_dpi_rtl_v1.py',
             bundle='search_read_control_staging_dpi_rtl_v1', report='search_read_control_staging_rtl_audit_20261025_v1.json', free_gib=152,
             accepted='read_control_staging_full2tx_dpi_rtl_all_output_bytes_and_original_c_oracle_independently_verified'),
    ]
    for job in jobs:
        require(not (BASE/job['bundle']).exists() and not (ROOT/'results'/job['report']).exists(), 'Existing downstream attempt; refuse duplicate')
    output = ROOT/'data/derived/post_snapshot_rtl_supervision_20261025_v1'
    output.mkdir(exist_ok=False)
    paths = [Path(__file__).resolve(), upstream/'plan.json', ROOT/'scripts/compact_bus64_prerequisites_v1.py', ROOT/'scripts/supervise_search_axi_dpi_v3.py']
    paths += [ROOT/'scripts'/job[key] for job in jobs for key in ('driver', 'checker')]
    files = {str(path): digest(path) for path in paths}
    atomic(output/'plan.json', dict(upstream_owner=owner, jobs=jobs, files=files,
        policy='Single serial owner, original capacities/oracles preserved; no automatic retries; no physical flow launched'))
    state = dict(owner_pid=os.getpid(), status='running', stage='waiting_existing_full30_snapshot_independent_acceptance')
    atomic(output/'state.json', state)
    try:
        while identity(owner['pid']) == owner:
            time.sleep(30)
        prior = json.loads((upstream/'state.json').read_text())
        require(prior['status'] == 'complete' and prior['stage'] == 'full30_snapshot_dpi_independently_verified', 'Original full30 chain did not pass')
        require(digest(ROOT/'results/snapshot_dpi_rtl_audit_20261025_v1.json') == prior['report_sha256'], 'Changed snapshot acceptance report')
        validate_prerequisites(ROOT/'results')
        cg = Path('/sys/fs/cgroup')
        for job in jobs:
            state['stage'] = 'waiting_memory_for_'+job['name']
            atomic(output/'state.json', state)
            while int((cg/'memory.max').read_text())-int((cg/'memory.current').read_text()) < job['free_gib']*1024**3:
                time.sleep(30)
            bundle = BASE/job['bundle']
            report = ROOT/'results'/job['report']
            require(not bundle.exists() and not report.exists(), 'Downstream attempt appeared; no duplicate')
            commands = [('execute', [sys.executable, str(ROOT/'scripts'/job['driver'])]),
                        ('audit', [sys.executable, str(ROOT/'scripts'/job['checker']), '--bundle', str(bundle), '--output', str(report)])]
            for phase, command in commands:
                for path, checksum in files.items():
                    require(digest(path) == checksum, 'Changed scheduled source '+path)
                label = job['name']+'_'+phase
                state['stage'] = label
                atomic(output/'state.json', state)
                start = time.monotonic()
                with (output/(label+'.log')).open('x') as log:
                    child = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
                    state['child_pid'] = child.pid
                    atomic(output/'state.json', state)
                    code = child.wait()
                atomic(output/(label+'.receipt.json'), dict(command=command, exit_code=code,
                    elapsed_seconds=time.monotonic()-start, log_sha256=digest(output/(label+'.log'))))
                require(code == 0, 'Downstream phase failed '+label+'; preserve evidence without retry')
            accepted = json.loads(report.read_text())
            require(accepted['status'] == job['accepted'], 'Wrong independent acceptance '+job['name'])
            state.setdefault('accepted', {})[job['name']] = dict(report=str(report), sha256=digest(report))
            atomic(output/'state.json', state)
        state.update(status='complete', stage='compact_full44_and_staged_search_independently_verified')
        atomic(output/'state.json', state)
    except BaseException as error:
        state.update(status='failed', error=str(error))
        atomic(output/'state.json', state)
        raise


if __name__ == '__main__':
    main()
