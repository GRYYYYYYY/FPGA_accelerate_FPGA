#!/usr/bin/env python3
"""Resume unexecuted matched HLS jobs after independent surviving-compiler audit."""
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import time
from check_vitis_kernel import digest, require
from experiment_status_v6 import process
from owned_sim_resource_policy_v1 import observe, abort_reason, POLICY
from run_compact_native_stack_recovery_v3 import atomic
from run_collision_safe_batch_hls_v1 import stop
from prepare_collision_safe_bus64_pair_v1 import ROOT, BASE, OUT as PREPARED, REPORT
from check_orphaned_native_compiler_v1 import REPORT as COMPILER_GATE

OUT = BASE/'collision_safe_bus64_pair_execution_v2'
RECOVERY = ROOT/'data/derived/native_owner_recovery_supervision_20261030_v1'


def actual_hls(child):
    pending = [child.pid]; seen = set()
    while pending:
        pid = pending.pop()
        if pid in seen: continue
        seen.add(pid); proc = Path('/proc')/str(pid)
        try:
            for task in (proc/'task').iterdir():
                try: pending.extend(map(int, (task/'children').read_text().split()))
                except (FileNotFoundError, ProcessLookupError): pass
            args = (proc/'cmdline').read_bytes().split(b'\0')
            if Path(os.fsdecode(args[0])).name != 'vitis_hls': continue
            # Shell launchers are not evidence of the actual HLS binary.
            if Path(os.readlink(proc/'exe')).name != 'vitis_hls': continue
            limits = {}
            for name, kind, value in [('address_space', resource.RLIMIT_AS, 64*1024**3),
                                      ('stack', resource.RLIMIT_STACK, 64*1024**2),
                                      ('core', resource.RLIMIT_CORE, 0)]:
                limits[name] = list(resource.prlimit(pid, kind))
                require(limits[name] == [value, value], 'Wrong actual HLS '+name)
            return dict(pid=pid, start_ticks=(proc/'stat').read_text().rsplit(')',1)[1].split()[19],
                        cwd=os.readlink(proc/'cwd'), command=b' '.join(args).decode(), **limits)
        except (FileNotFoundError, ProcessLookupError): pass
    return None


def main():
    def interrupted(signum, frame): raise SystemExit(128+signum)
    signal.signal(signal.SIGTERM,interrupted)
    require(not OUT.exists(), 'Refuse duplicate execution')
    prep = json.loads(REPORT.read_text())
    require(prep['status'] == 'collision_safe_bus64_CSR_compact_matched_full44_inputs_prepared_not_executed', 'Wrong preparation')
    previous = json.loads((PREPARED/'state.json').read_text())
    require(previous['status'] == 'failed' and previous['completed_modes'] == [] and
            process(previous['owner_pid']) is None, 'Original paired attempt not terminal/unexecuted')
    current = json.loads((RECOVERY/'state.json').read_text()); owner = process(current['owner_pid'])
    require(current['status'] == 'running' and owner and owner['state'] != 'Z' and
            'supervise_native_owner_recovery_v1.py' in owner['command'], 'Current recovery owner not verified')
    for job in prep['jobs']:
        require(not Path(job['project']).exists() and not (Path(job['cwd'])/'hls.log').exists(), 'HLS job already started')
    OUT.mkdir()
    files = dict(prep['files'])
    for p in [REPORT, Path(__file__).resolve(), ROOT/'scripts/owned_sim_resource_policy_v1.py',
              ROOT/'scripts/run_collision_safe_batch_hls_v1.py', PREPARED/'state.json',
              ROOT/'scripts/check_orphaned_native_compiler_v1.py']:
        files[str(p)] = digest(p)
    atomic(OUT/'execution_plan.json', dict(files=files, jobs=prep['jobs'], recovery_owner=owner,
           independent_compiler_gate=str(COMPILER_GATE), resource_policy=POLICY, wait_only_for_native_elaboration=True,
           no_rtl_or_physical_launch=True))
    state = dict(owner_pid=os.getpid(), status='running', stage='waiting_independent_compiler_recovery_gate', completed_modes=[])
    atomic(OUT/'state.json', state); child = None
    try:
        while True:
            current = json.loads((RECOVERY/'state.json').read_text()); live = process(owner['pid'])
            require(current['owner_pid'] == owner['pid'], 'Recovery owner changed')
            # The completion flag is written atomically only after the checker
            # has finished publishing its full report and exited successfully.
            if 'compiler_independent_audit' in current['completed']:
                gate = json.loads(COMPILER_GATE.read_text())
                require(gate['status'] == 'surviving_original_native_compiler_exit0_snapshot_and_full_inputs_independently_verified_RTL_pending',
                        'Wrong compiler recovery acceptance')
                receipt_path = RECOVERY/'compiler_independent_audit.receipt.json'
                receipt = json.loads(receipt_path.read_text())
                require(receipt['exit_code'] == 0 and receipt['log_sha256'] == digest(RECOVERY/'compiler_independent_audit.log'),
                        'Failed compiler independent audit')
                for name, checksum in gate['files'].items(): require(digest(name) == checksum, 'Changed recovered compiler gate '+name)
                atomic(OUT/'compiler_gate.json',dict(path=str(COMPILER_GATE),sha256=digest(COMPILER_GATE),
                       receipt=str(receipt_path),receipt_sha256=digest(receipt_path)))
                break
            require(current['status'] != 'failed' and live and live['state'] != 'Z' and
                    live['start_ticks'] == owner['start_ticks'] and live['command'] == owner['command'],
                    'Recovery owner failed/missing before compiler audit; no restart')
            atomic(OUT/'wait_observation.json',dict(recovery_stage=current['stage'],recovery_owner_verified=True,
                   monotonic_seconds=time.monotonic()))
            time.sleep(10)
        for name, checksum in files.items(): require(digest(name) == checksum, 'Changed paired input '+name)
        initial = observe(); atomic(OUT/'initial_memory.json', initial)
        for job in prep['jobs']:
            mode = job['mode']; work = Path(job['cwd']); state.update(stage='csim_csynth', mode=mode)
            atomic(OUT/'state.json', state)
            require(abort_reason(initial, observe()) is None, 'New OOM before HLS')
            env = {**os.environ, 'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1',
                   'A_BATCH_RTL_SNAPSHOT_PREFIX':job['snapshot_prefix']}
            start = time.monotonic(); actual = None; reason = None; last = 0
            with (work/'hls.log').open('x') as log:
                child = subprocess.Popen(job['command'], cwd=work, env=env, stdout=log,
                                         stderr=subprocess.STDOUT, start_new_session=True)
                state['child_pid'] = child.pid; atomic(OUT/'state.json', state)
                while child.poll() is None:
                    if actual is None:
                        actual = actual_hls(child)
                        if actual: atomic(work/'actual_limits.json', actual)
                    observed = observe(); reason = abort_reason(initial, observed)
                    if time.monotonic()-last >= 30:
                        atomic(OUT/'resource_observation.json', dict(mode=mode, memory=observed, actual_limits=actual)); last=time.monotonic()
                    if reason: stop(child); break
                    time.sleep(1)
                code = child.wait(); child = None
            final = observe(); reason = reason or abort_reason(initial, final)
            receipt = dict(command=job['command'], cwd=str(work), exit_code=code, abort_reason=reason,
                           actual_limits=actual, final_memory=final, elapsed_seconds=time.monotonic()-start,
                           log_sha256=digest(work/'hls.log'))
            atomic(work/'receipt.json', receipt)
            text = (work/'hls.log').read_text(errors='replace')
            require(code == 0 and reason is None and actual is not None, 'Failed or unobserved HLS')
            require(not any(e in text for e in ['ERROR:', 'Fatal:', 'LLVM ERROR', 'runtime error:']), 'HLS error')
            for marker in ['COLLISION_SAFE_BUS64_CSIM_COMPLETE', 'COLLISION_SAFE_BUS64_CSYNTH_COMPLETE']:
                require(text.splitlines().count(marker) == 1, 'Missing HLS marker')
            require(f'FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode={mode} ports=44 transactions=4' in text and
                    f'SEARCH_BATCH_PASS mode={mode}' in text, 'Missing original full C checks')
            snapshots = []
            for tx in range(4):
                p = work/f'csim_{mode}_{tx}.bin'; golden = BASE/'compressed_batch_rtl_tb_cpu_v2'/f'cpu_{mode}_{tx}.bin'
                require(p.stat().st_size == golden.stat().st_size == 946498280 and digest(p) == digest(golden), 'Full44 C output differs')
                trace = work/'project/solution/csim/build'/f'trace_mode_{mode}_case_{tx}.bin'
                require(digest(trace) == digest(BASE/'compressed_batch_rtl_tb_cpu_v2'/trace.name), 'Exact trace differs')
                snapshots.append(dict(transaction=tx, snapshot=str(p), sha256=digest(p), trace=str(trace), trace_sha256=digest(trace)))
            atomic(work/'comparison.json', dict(status='full4tx_full44_C_snapshots_and_traces_match_original', snapshots=snapshots))
            for name, checksum in files.items(): require(digest(name) == checksum, 'Bound input changed '+name)
            state['completed_modes'].append(mode); atomic(OUT/'state.json', state)
        state.update(status='complete', stage='paired_hls_complete_independent_audit_pending'); atomic(OUT/'state.json', state)
    except BaseException as exc:
        if child is not None and child.poll() is None: stop(child)
        state.update(status='failed', error=str(exc)); atomic(OUT/'state.json', state); raise


if __name__ == '__main__': main()
