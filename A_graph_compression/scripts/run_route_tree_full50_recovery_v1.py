#!/usr/bin/env python3
"""Single full50 rerun in fresh directories; preserve interrupted evidence."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/derived/route_tree_rtl_recovery_20261027_v1'
PROJECT = ROOT / 'build/route_tree_rtl_recovery_20261027_v1'
AUDIT = ROOT / 'results/route_tree_rtl_recovery_audit_20261027_v1.json'
CONTROL = ROOT / 'data/derived/route_tree_rtl_recovery_control_20261027_v1'


def free_bytes():
    maximum = int(Path('/sys/fs/cgroup/memory.max').read_text())
    current = int(Path('/sys/fs/cgroup/memory.current').read_text())
    return maximum - current


def main():
    # Preflight includes all original input bindings and absence of old PIDs.
    check = subprocess.run([sys.executable, str(ROOT / 'scripts/check_route_tree_recovery_preflight_v1.py')], cwd=ROOT)
    if check.returncode:
        return check.returncode
    if any(p.exists() for p in [OUT, PROJECT, AUDIT, CONTROL]):
        raise RuntimeError('Recovery artifact already exists; no automatic retry')
    if free_bytes() < 128 * 2**30:
        return 2
    CONTROL.mkdir()
    # Preserve the original ASan CPU check, whose virtual shadow reservation is
    # much larger than its resident memory; do not impose a global RLIMIT_AS.
    command = ['prlimit', '--core=0:0', '--',
               sys.executable, str(ROOT / 'scripts/route_tree_rtl_pipeline.py'),
               '--output', str(OUT), '--project', str(PROJECT), '--audit-output', str(AUDIT), '--cpu', '118']
    state = dict(owner_pid=os.getpid(), status='running', command=command,
                 transactions_required=50,
                 entry_free_bytes=128 * 2**30, runtime_free_bytes=16 * 2**30,
                 note='Original pipeline regenerates setup and elaborates unchanged production RTL; no transaction7 checkpoint resume.')

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
                available = free_bytes()
                if available < 16 * 2**30:
                    state.update(resource_abort=True, observed_free_bytes=available)
                    os.killpg(child.pid, signal.SIGTERM)
                    try:
                        child.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        os.killpg(child.pid, signal.SIGKILL)
                        child.wait()
                    break
                time.sleep(2)
        succeeded = child.returncode == 0 and not state.get('resource_abort', False)
        state.update(status='complete' if succeeded else 'failed', exit_code=child.returncode)
        if succeeded and not AUDIT.exists():
            raise RuntimeError('Pipeline returned zero without independent audit')
        save()
        return 0 if succeeded else 1
    except BaseException as error:
        if child is not None and child.poll() is None:
            os.killpg(child.pid, signal.SIGTERM)
        state.update(status='failed', error=str(error))
        save()
        raise


if __name__ == '__main__':
    raise SystemExit(main())
