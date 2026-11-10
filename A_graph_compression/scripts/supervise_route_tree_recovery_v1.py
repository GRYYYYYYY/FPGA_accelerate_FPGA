#!/usr/bin/env python3
"""Wait for existing recovery admission, execute once, never retry."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from run_route_tree_full50_recovery_v1 import ROOT, free_bytes, OUT, PROJECT, AUDIT, CONTROL

FOLDER = ROOT / 'data/derived/route_tree_recovery_supervision_20261027_v1'


def main():
    FOLDER.mkdir(exist_ok=False)
    state = dict(owner_pid=os.getpid(), status='waiting', stage='memory_admission',
                 admission_bytes=128 * 2**30, transactions_required=50)

    def save():
        p = FOLDER / 'state.tmp'
        p.write_text(json.dumps(state, indent=2) + '\n')
        p.replace(FOLDER / 'state.json')

    try:
        while True:
            if any(p.exists() for p in [OUT, PROJECT, AUDIT, CONTROL]):
                raise RuntimeError('Recovery artifacts exist; refuse competing execution')
            state['observed_free_bytes'] = free_bytes()
            save()
            if state['observed_free_bytes'] >= state['admission_bytes']:
                break
            time.sleep(30)
        state.update(status='running', stage='full50_recovery')
        save()
        with (FOLDER / 'execution.log').open('x') as log:
            child = subprocess.Popen([sys.executable, str(ROOT / 'scripts/run_route_tree_full50_recovery_v1.py')],
                                     cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
            state['child_pid'] = child.pid
            save()
            code = child.wait()
        state.update(status='complete' if code == 0 else 'failed', exit_code=code)
        save()
    except BaseException as error:
        state.update(status='failed', error=str(error))
        save()
        raise


if __name__ == '__main__':
    main()
