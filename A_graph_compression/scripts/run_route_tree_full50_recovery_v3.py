#!/usr/bin/env python3
"""Full50 after naming-corrected full RTL gates; preserve every previous trial."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/derived/route_tree_rtl_recovery_20261031_v3'
PROJECT = ROOT / 'build/route_tree_rtl_recovery_20261031_v3'
AUDIT = ROOT / 'results/route_tree_rtl_recovery_audit_20261031_v3.json'
CONTROL = ROOT / 'data/derived/route_tree_rtl_recovery_control_20261031_v3'


from owned_sim_resource_policy_v1 import POLICY, observe, abort_reason
from run_compact_nonzero_native_rtl_v2 import stop
from route_tree_serial_prerequisites_v2 import validate_predecessors
from check_vitis_kernel import digest,require


def main():
    def interrupted(signum, frame):
        raise SystemExit(128 + signum)
    signal.signal(signal.SIGTERM, interrupted)
    predecessors=validate_predecessors()
    # Preflight includes all original input bindings and absence of old PIDs.
    check = subprocess.run([sys.executable, str(ROOT / 'scripts/check_route_tree_recovery_preflight_v2.py')], cwd=ROOT)
    if check.returncode:
        return check.returncode
    if any(p.exists() for p in [OUT, PROJECT, AUDIT, CONTROL]):
        raise RuntimeError('Recovery artifact already exists; no automatic retry')
    initial=observe()
    CONTROL.mkdir()
    # Preserve the original ASan CPU check, whose virtual shadow reservation is
    # much larger than its resident memory; do not impose a global RLIMIT_AS.
    command = ['prlimit', '--core=0:0', '--',
               sys.executable, str(ROOT / 'scripts/route_tree_rtl_pipeline_v2.py'),
               '--output', str(OUT), '--project', str(PROJECT), '--audit-output', str(AUDIT), '--cpu', '118']
    state = dict(owner_pid=os.getpid(), status='running', command=command,
                 transactions_required=50,
                 resource_policy=POLICY,free_memory_gate_removed_by_user=True,start_memory=initial,predecessors=predecessors,
                 rtl_compiler_postcheck_as_bytes=64*1024**3,
                 note='Full50 original DUT/C oracle; setup regenerated, not a transaction4 checkpoint resume. CPU ASan shadow remains uncapped; xelab/RTL/postcheck AS64GiB.')

    def save():
        temp = CONTROL / 'state.tmp'
        temp.write_text(json.dumps(state, indent=2) + '\n')
        temp.replace(CONTROL / 'state.json')

    save()
    child = None
    try:
        with (CONTROL / 'pipeline.log').open('x') as log:
            child = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                     start_new_session=True)
            state['child_pid'] = child.pid
            save()
            while child.poll() is None:
                current=observe();reason=abort_reason(initial,current)
                state['last_memory']=current
                save()
                if reason is not None:
                    state.update(resource_abort=True,resource_abort_reason=reason,resource_abort_observation=current)
                    stop(child)
                    break
                time.sleep(2)
        final=observe();state['end_memory']=final
        if abort_reason(initial,final) is not None:state.update(resource_abort=True,resource_abort_reason=abort_reason(initial,final))
        succeeded = child.returncode == 0 and not state.get('resource_abort', False)
        state.update(status='complete' if succeeded else 'failed', exit_code=child.returncode)
        if succeeded and not AUDIT.exists():
            raise RuntimeError('Pipeline returned zero without independent audit')
        if succeeded:
            audit=json.loads(AUDIT.read_text())
            require(audit['status']=='production_route_tree_full_depth_50_transactions_rtl_verified' and audit['transactions']==50 and len(audit['cycles'])==50,'Incomplete tree acceptance')
            for p,h in audit['files'].items():require(digest(p)==h,'Changed tree audit binding')
        save()
        return 0 if succeeded else 1
    except BaseException as error:
        if child is not None and child.poll() is None:
            stop(child)
        state.update(status='failed', error=str(error))
        save()
        raise


if __name__ == '__main__':
    raise SystemExit(main())
