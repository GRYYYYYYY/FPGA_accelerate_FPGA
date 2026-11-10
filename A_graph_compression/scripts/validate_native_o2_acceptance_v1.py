#!/usr/bin/env python3
"""Read-only O2 prerequisite validation; does not transfer execution ownership."""
import json
from pathlib import Path

from check_vitis_kernel import digest, require
from check_native_o2_full_rtl_v1 import audit
from run_native_o2_full_rtl_v1 import OUT, REPORT, CHECKER

STATUS = 'unchanged_native_O2_full4tx_full44_original_C_independently_verified'


def owner_exited(state):
    pid, ticks = state['owner_pid'], state['owner_start_ticks']
    require(type(pid) is int and pid > 0 and str(ticks).isdigit() and int(ticks) > 0,
            'Invalid O2 owner identity')
    try:
        current = (Path('/proc') / str(pid) / 'stat').read_text().rsplit(')', 1)[1].split()
    except FileNotFoundError:
        return
    # A reused PID belongs to another process. A matching zombie is conservatively
    # rejected until reaped; permission/read errors propagate rather than imply exit.
    require(current[19] != str(ticks), 'O2 owner has not exited')


def validate():
    state = json.loads((OUT / 'state.json').read_text())
    require(state.get('status') == 'complete' and
            state.get('stage') == 'full4_RTL_C_independent_audit_pending',
            'O2 full RTL/C execution is not complete')
    owner_exited(state)
    terminal_path = OUT / 'terminal.json'
    receipt_path = OUT / 'audit.receipt.json'
    log_path = OUT / 'audit.log'
    require(all(p.is_file() for p in (terminal_path, receipt_path, log_path, REPORT)),
            'Missing O2 independent acceptance artifacts')
    # Recheck these bytes after the expensive full audit to reject concurrent edits.
    paths = [OUT / 'state.json', terminal_path, receipt_path, log_path, REPORT,
             Path(__file__).resolve()]
    bindings = {str(p): digest(p) for p in paths}
    report_hash = bindings[str(REPORT)]
    terminal = json.loads(terminal_path.read_text())
    require(terminal == dict(status='full4_O2_RTL_independently_verified',
                            report=str(REPORT), report_sha256=report_hash,
                            downstream_gates_rewired=False, physical_verified=False,
                            board_verified=False), 'Wrong O2 terminal or report binding')
    receipt = json.loads(receipt_path.read_text())
    command = ['prlimit', '--as=17179869184:17179869184',
               '--stack=67108864:67108864', '--core=0:0', '--', 'python3', str(CHECKER)]
    require(receipt.get('command') == command and receipt.get('exit_code') == 0 and
            receipt.get('abort_reason') is None and receipt.get('elapsed_seconds', 0) > 0 and
            receipt.get('report_sha256') == report_hash and
            receipt.get('log_sha256') == bindings[str(log_path)],
            'O2 independent audit receipt failed or changed')
    require(log_path.read_text().splitlines().count(STATUS) == 1,
            'Missing or duplicated independent audit completion')
    report = json.loads(REPORT.read_text())
    require(report.get('status') == STATUS and report.get('rtl_verified') is True and
            (report.get('transactions'), report.get('pointers'), report.get('models')) == (4, 44, 30),
            'Wrong O2 accepted scope')
    # Reuse the original independent checker in memory: all compiler/input/model
    # bindings, RTL/C receipts, four full snapshots, raw outputs and cycles.
    require(audit() == report, 'Fresh full O2 audit differs from accepted report')
    for path, checksum in bindings.items():
        require(digest(path) == checksum, 'O2 acceptance changed during validation')
    owner_exited(state)
    files = dict(report['files'])
    for path, checksum in bindings.items():
        require(path not in files or files[path] == checksum, 'Conflicting O2 evidence')
        files[path] = checksum
    return dict(status='O2_full_acceptance_revalidated_no_ownership_transfer',
                files=files, report=str(REPORT), report_sha256=report_hash,
                downstream_gates_rewired=False)


if __name__ == '__main__':
    result = validate()
    print(json.dumps({k: v for k, v in result.items() if k != 'files'}, indent=2))
