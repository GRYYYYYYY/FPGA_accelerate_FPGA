#!/usr/bin/env python3
"""Isolated O2 compile and repeated bounded O0/O2 diagnostics; no acceptance."""
import json
import os
from pathlib import Path
import re
import shutil
import signal
import statistics
import subprocess
import time

from check_vitis_kernel import digest, require
from owned_sim_resource_policy_v1 import observe, abort_reason, POLICY
from run_compact_native_stack_recovery_v3 import atomic
from run_compact_nonzero_native_rtl_v2 import observe_limits, stop
from run_recovered_native_rtl_v2 import gate, OUT as LIVE, BIN, TRIAL

ROOT = Path(__file__).resolve().parents[1]
OUT = LIVE.parent / 'native_xsim_optimization_diagnostic_v1'
O0 = 'search_batch_trace_top_v2'
O2 = O0 + '_optimization_diagnostic_O2'
REPORT = ROOT / 'results/native_xsim_optimization_diagnostic_20261102_v1.json'
DIAG = ROOT / 'results/native_first_transaction_diagnostic_replay_20261102_v1.json'
ORDER = ['O0', 'O2', 'O2', 'O0']


def samples(text):
    result = {}; step = None
    for line in text.splitlines():
        m = re.fullmatch(r'A_DIAG_SAMPLE (\d+)', line.strip())
        if m:
            step = int(m[1]); require(step not in result, 'Duplicate sample')
            result[step] = {}; continue
        m = re.fullmatch(r'A_DIAG_VALUE (\d+) (.+)', line.strip())
        if m:
            require(step is not None, 'Value before sample')
            index = int(m[1]); require(index not in result[step], 'Duplicate value')
            result[step][index] = m[2]
    require(set(result) == set(range(20)), 'Incomplete diagnostic window')
    require(all(set(row) == set(range(21)) for row in result.values()), 'Missing probe')
    return result


def main():
    def interrupted(signum, frame):
        raise SystemExit(128 + signum)
    signal.signal(signal.SIGTERM, interrupted)
    require(not OUT.exists() and not REPORT.exists(), 'Refuse duplicate benchmark')
    OUT.mkdir()
    state = dict(owner_pid=os.getpid(), status='running', stage='verify_inputs',
                 functional_acceptance=False, live_run_modified=False, completed=[])
    atomic(OUT/'state.json', state)
    initial = observe(); child = None

    def clean_resources():
        require(abort_reason(initial, observe()) is None, 'New OOM/reset')

    def run(name, command, phase, timeout):
        nonlocal child
        clean_resources()
        state.update(stage=name); atomic(OUT/'state.json', state)
        start = time.monotonic(); actual = None; reason = None; last = 0
        logpath = OUT/(name+'.log')
        env = {**os.environ, 'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1',
               'A_BATCH_RTL_SNAPSHOT_PREFIX':str(OUT/(name+'_diagnostic_only'))}
        with logpath.open('x') as log:
            child = subprocess.Popen(command, cwd=OUT/'sim/verilog', env=env,
                                     stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            state['child_pid'] = child.pid; atomic(OUT/'state.json', state)
            while child.poll() is None:
                if actual is None:
                    actual = observe_limits(child, phase)
                    if actual: atomic(OUT/(name+'.actual_limits.json'), actual)
                current = observe(); reason = abort_reason(initial, current)
                if time.monotonic()-start > timeout: reason = reason or 'diagnostic_wall_timeout'
                if time.monotonic()-last >= 30:
                    atomic(OUT/'resource_observation.json', dict(phase=name, memory=current, actual_limits=actual))
                    last = time.monotonic()
                if reason: stop(child); break
                time.sleep(1)
            code = child.wait(); child = None
        reason = reason or abort_reason(initial, observe())
        receipt = dict(command=command, cwd=str(OUT/'sim/verilog'), exit_code=code,
                       elapsed_seconds=time.monotonic()-start, abort_reason=reason,
                       actual_limits=actual, log_sha256=digest(logpath), functional_acceptance=False)
        atomic(OUT/(name+'.receipt.json'), receipt)
        require(code == 0 and reason is None and actual is not None, 'Failed '+name)
        text = logpath.read_text(errors='replace')
        require(not any(s in text for s in ['ERROR:', 'Fatal:', 'FATAL_ERROR', 'A_REBASE_', 'A_RO_']), 'Error in '+name)
        state['completed'].append(name); atomic(OUT/'state.json', state)
        return receipt, text

    try:
        proof = gate()
        original = json.loads((LIVE/'plan.json').read_text())
        compiler = json.loads((TRIAL/'plan.json').read_text())
        require((original['transactions'], original['pointers'], original['models']) == (4,44,30), 'Scope changed')
        diag = json.loads(DIAG.read_text())
        require(diag['status'] == 'bounded_100us_replay_captured_not_functional_acceptance', 'Wrong diagnostic gate')
        for name, checksum in diag['files'].items(): require(digest(name) == checksum, 'Changed replay evidence')
        tcl_source = next(Path(p) for p in diag['files'] if p.endswith('/diagnostic.tcl'))
        historical = samples(Path(next(p for p in diag['files'] if p.endswith('/diagnostic.log'))).read_text())
        help_path = ROOT/'data/derived/native_nonzero_resource_review_20261029_v1/xelab_help.log'
        require(digest(help_path) == 'ed5227e099f7124be3eae63c66478a54a8dcd45aecdfc1b406e5a323904df41d', 'Changed installed help')
        require('--O2' in help_path.read_text(), 'O2 unsupported by installed help')
        state['stage'] = 'copy_complete_inputs_and_original_snapshot'; atomic(OUT/'state.json', state)
        copied = {}
        for name, row in original['copies'].items():
            clean_resources()
            src = Path(row['source']); require(not src.is_symlink(), 'Unexpected symlink')
            dst = OUT/'sim'/Path(name).relative_to(LIVE/'sim')
            dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dst)
            require(digest(dst) == row['sha256'], 'Copy differs '+str(src))
            copied[str(dst)] = row['sha256']
        for name in original['sim_directories']:
            (OUT/'sim'/Path(name).relative_to(LIVE/'sim')).mkdir(parents=True, exist_ok=True)
        require(not list((OUT/'sim/tv/rtldatafile').iterdir()), 'Output directory not empty')
        preserved = {str(OUT/'sim'/Path(p).relative_to(TRIAL/'sim')):v['sha256'] for p,v in compiler['copied'].items()}
        require(len(preserved) == 293, 'Incomplete source/input contract')
        kernel0 = OUT/'sim/verilog/xsim.dir'/O0/'xsimk'
        preserved.update({name:checksum for name,checksum in copied.items()
                          if Path(name).is_relative_to(kernel0.parent)})
        tcl = OUT/'diagnostic.tcl'; shutil.copy2(tcl_source, tcl)
        command = list(compiler['commands'][0]['command'])
        require(command.count('--O0') == 1 and command[command.index('-s')+1] == O0, 'Unexpected compiler command')
        optimized = list(command); optimized[optimized.index('--O0')] = '--O2'
        optimized[optimized.index('-s')+1] = O2
        require([i for i,(a,b) in enumerate(zip(command,optimized)) if a != b] == sorted([command.index('--O0'),command.index('-s')+1]), 'Extra compiler changes')
        files = {str(p):digest(p) for p in [Path(__file__).resolve(), LIVE/'plan.json', TRIAL/'plan.json',
                 DIAG, tcl, help_path, ROOT/'scripts/run_recovered_native_rtl_v2.py',
                 ROOT/'scripts/run_compact_nonzero_native_rtl_v2.py', ROOT/'scripts/owned_sim_resource_policy_v1.py',
                 ROOT/'scripts/run_compact_native_stack_recovery_v3.py', ROOT/'scripts/check_vitis_kernel.py']}
        atomic(OUT/'plan.json', dict(files=files, copied=copied, preserved_inputs=preserved,
               compiler_command_original=command, compiler_command_optimized=optimized,
               optimization_only_plus_unique_snapshot_name=True, order=ORDER, simulation_us=100,
               compiler_wall_timeout_seconds=7200, per_replay_wall_timeout_seconds=1800,
               initial_memory=initial, resource_policy=POLICY, startup_free_memory_gate=False,
               compile_as_bytes=192*1024**3, runtime_as_bytes=96*1024**3,
               transactions_in_inputs=4,pointers=44,models=30, probes=21,
               functional_acceptance=False,live_run_modified=False,compiler_audit_status=proof['status']))

        def verify_preserved():
            for name, checksum in {**files, **preserved}.items():
                clean_resources(); require(digest(name) == checksum, 'Changed immutable input '+name)

        run('elaborate_O2', optimized, 'elaborate', 7200)
        kernel2 = OUT/'sim/verilog/xsim.dir'/O2/'xsimk'
        require(kernel2.is_file(), 'Missing O2 snapshot')
        preserved.update({str(p):digest(p) for p in kernel2.parent.rglob('*') if p.is_file()})
        atomic(OUT/'immutable_runtime_inputs.json', preserved)
        atomic(OUT/'snapshots.json', dict(O0=dict(path=str(kernel0),sha256=digest(kernel0)),
                                        O2=dict(path=str(kernel2),sha256=digest(kernel2))))
        times = {'O0':[], 'O2':[]}; evidence = []
        for index, mode in enumerate(ORDER):
            verify_preserved()
            name = f'replay_{index}_{mode}'
            cmd = ['prlimit','--as=103079215104:103079215104','--stack=268435456:268435456',
                   '--core=0:0','--',str(BIN/'xsim'),'--noieeewarnings', O0 if mode == 'O0' else O2,
                   '-tclbatch',str(tcl)]
            receipt, text = run(name,cmd,'rtl',1800)
            require(len(re.findall(r'^A_DIAG_BOUNDED_CAPTURE_COMPLETE$', text, re.M)) == 1, 'Incomplete diagnostic')
            require(samples(text) == historical, 'Observed probe samples differ from original O0 replay')
            times[mode].append(receipt['elapsed_seconds'])
            evidence.extend([OUT/(name+'.log'), OUT/(name+'.receipt.json')])
        verify_preserved()
        evidence += [OUT/'plan.json',OUT/'snapshots.json',OUT/'immutable_runtime_inputs.json',
                     OUT/'elaborate_O2.log',OUT/'elaborate_O2.receipt.json']
        result = dict(status='repeated_100us_O0_O2_probe_matched_diagnostic_not_functional_acceptance',
                      files={str(p):digest(p) for p in evidence}, elapsed_seconds=times,
                      median_elapsed_seconds={k:statistics.median(v) for k,v in times.items()},
                      O2_over_O0_elapsed_ratio=statistics.median(times['O2'])/statistics.median(times['O0']),
                      matched_samples_per_run=20,probes_per_sample=21,simulation_us=100,order=ORDER,
                      functional_acceptance=False,live_run_modified=False,
                      limits=['Shared host; page cache and host load not controlled.',
                              'Timing includes simulator startup and identical diagnostic queries.',
                              'Only early initialization window; no full transaction completed or equivalence proven.',
                              'Does not justify extrapolating to later trace scans or replacing frozen acceptance runs.'])
        with REPORT.open('x') as f: json.dump(result,f,indent=2);f.write('\n')
        state.update(status='complete',stage='bounded_optimization_diagnostic_complete',report=str(REPORT))
        atomic(OUT/'state.json',state)
    except BaseException as exc:
        if child is not None and child.poll() is None: stop(child)
        state.update(status='failed',error=str(exc)); atomic(OUT/'state.json',state)
        raise


if __name__ == '__main__':
    main()
