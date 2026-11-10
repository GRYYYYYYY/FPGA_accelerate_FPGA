#!/usr/bin/env python3
"""Run all4 native RTL transactions from an independently audited surviving build."""
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time
from check_vitis_kernel import digest, require
from owned_sim_resource_policy_v1 import observe, abort_reason, POLICY
from run_compact_native_stack_recovery_v3 import atomic
from run_compact_nonzero_native_rtl_v2 import observe_limits, stop
from run_collision_safe_native_rtl_v1 import BASE, BIN, ERRORS
from check_orphaned_native_compiler_v1 import ROOT, TRIAL, REPORT as COMPILE_AUDIT

OUT = BASE/'collision_safe_native_owner_recovery_v1'


def gate():
    require(COMPILE_AUDIT.is_file(), 'Independent surviving compiler audit missing')
    proof = json.loads(COMPILE_AUDIT.read_text())
    require(proof['status'] == 'surviving_original_native_compiler_exit0_snapshot_and_full_inputs_independently_verified_RTL_pending', 'Wrong compiler gate')
    for name, checksum in proof['files'].items(): require(digest(name) == checksum, 'Changed recovered compiler evidence '+name)
    return proof


def main():
    def interrupted(signum, frame):
        raise SystemExit(128+signum)
    signal.signal(signal.SIGTERM,interrupted)
    require(not OUT.exists(), 'Refuse duplicate recovery trial')
    proof = gate()
    original = json.loads((TRIAL/'plan.json').read_text())
    require((original['transactions'],original['pointers'],original['models']) == (4,44,30), 'Changed original scope')
    # Copy to a separate directory so the interrupted compiler's evidence stays
    # immutable, including its generated debug databases and runtime logs.
    initial = observe(); OUT.mkdir()
    state = dict(owner_pid=os.getpid(),status='running',stage='copy_audited_compiled_simulation',
                 full_kernel_accepted=False,transactions=4,pointers=44,models=30)
    atomic(OUT/'state.json',state); child = None
    try:
        copies = {}; preserved_inputs = {}
        for source in (TRIAL/'sim').rglob('*'):
            if not source.is_file(): continue
            require(not source.is_symlink(), 'Unexpected compiled simulation symlink '+str(source))
            require(abort_reason(initial,observe()) is None, 'New OOM during recovery copy')
            target = OUT/'sim'/source.relative_to(TRIAL/'sim')
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source,target)
            checksum = digest(target)
            require(checksum == digest(source), 'Recovery copy differs')
            copies[str(target)] = dict(source=str(source),sha256=checksum)
            if str(source) in original['copied']:
                require(checksum == original['copied'][str(source)]['sha256'], 'Original full input changed')
                preserved_inputs[str(target)] = checksum
        require(len(preserved_inputs) == len(original['copied']) == 293, 'Incomplete full simulation inputs')
        kernel = OUT/'sim/verilog/xsim.dir/search_batch_trace_top_v2/xsimk'
        require(digest(kernel) == proof['files'][str(TRIAL/'sim/verilog/xsim.dir/search_batch_trace_top_v2/xsimk')], 'Different compiled kernel')
        preserved_inputs[str(kernel)] = digest(kernel)
        rtl = OUT/'sim/verilog'; pc = OUT/'sim/wrapc_pc'
        bounded = OUT/'bounded.tcl'; shutil.copy2(TRIAL/'bounded.tcl',bounded)
        require(digest(bounded) == original['files'][str(TRIAL/'bounded.tcl')], 'Changed original bounded Tcl')
        runtime = ['prlimit','--as=103079215104:103079215104','--stack=268435456:268435456','--core=0:0','--']
        jobs = [dict(phase='rtl',command=runtime+[str(BIN/'xsim'),'--noieeewarnings','search_batch_trace_top_v2','-tclbatch',str(bounded)],cwd=str(rtl)),
                dict(phase='postcheck',command=runtime+[str(pc/'cosim.pc.exe')],cwd=str(pc))]
        files = {str(p):digest(p) for p in [COMPILE_AUDIT,TRIAL/'plan.json',Path(__file__).resolve(),bounded,
                 ROOT/'scripts/run_compact_nonzero_native_rtl_v2.py',ROOT/'scripts/owned_sim_resource_policy_v1.py',
                 ROOT/'scripts/run_collision_safe_native_rtl_v1.py',ROOT/'scripts/check_orphaned_native_compiler_v1.py']}
        plan = dict(files=files,copies=copies,preserved_inputs=preserved_inputs,commands=jobs,initial_memory=initial,
                    resource_policy=POLICY,startup_free_memory_gate=False,transactions=4,pointers=44,models=30,
                    compile_reused=True,compile_wait_receipt_fabricated=False,original_trial=str(TRIAL),
                    runtime_as_bytes=96*1024**3,stack_bytes=256*1024**2,core_bytes=0)
        atomic(OUT/'plan.json',plan)
        env = {**os.environ,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1','A_BATCH_RTL_SNAPSHOT_PREFIX':str(OUT/'rtl')}
        for job in jobs:
            phase = job['phase']; state.update(stage=phase); atomic(OUT/'state.json',state)
            require(abort_reason(initial,observe()) is None, 'New OOM before '+phase)
            started = time.monotonic(); actual = None; reason = None; last = 0
            with (OUT/(phase+'.log')).open('x') as log:
                child = subprocess.Popen(job['command'],cwd=job['cwd'],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                state['child_pid'] = child.pid; atomic(OUT/'state.json',state)
                while child.poll() is None:
                    if actual is None:
                        actual = observe_limits(child,phase)
                        if actual: atomic(OUT/(phase+'.actual_limits.json'),actual)
                    memory = observe(); reason = abort_reason(initial,memory)
                    if time.monotonic()-last >= 30:
                        atomic(OUT/'resource_observation.json',dict(phase=phase,memory=memory,actual_limits=actual)); last=time.monotonic()
                    if reason: stop(child); break
                    time.sleep(1)
                code = child.wait(); child = None
            final = observe(); reason = reason or abort_reason(initial,final)
            log = OUT/(phase+'.log'); text = log.read_text(errors='replace')
            receipt = dict(command=job['command'],cwd=job['cwd'],exit_code=code,abort_reason=reason,actual_limits=actual,
                           final_memory=final,elapsed_seconds=time.monotonic()-started,log_sha256=digest(log))
            atomic(OUT/(phase+'.receipt.json'),receipt)
            require(code == 0 and reason is None and actual is not None and not any(e in text for e in ERRORS), 'Failed recovery '+phase)
            if phase == 'rtl':
                require(re.search(r'RTL Simulation\s*:\s*4\s*/\s*4',text) is not None and
                        'COLLISION_SAFE_NATIVE_BOUNDED_RETURNED' in text, 'Incomplete four RTL transactions')
            else:
                require('FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode=1 ports=44 transactions=4' in text and
                        'SEARCH_BATCH_PASS mode=1' in text, 'Original full C postcheck failed')
        snapshots = []
        for tx in range(4):
            actual = OUT/f'rtl_1_{tx}.bin'; reference = BASE/'collision_safe_compact_cosim_setup_v1'/f'hls_1_{tx}.bin'
            original_cpu = BASE/'compressed_batch_rtl_tb_cpu_v2'/f'cpu_1_{tx}.bin'
            require(actual.stat().st_size == reference.stat().st_size == original_cpu.stat().st_size == 946498280, 'Incomplete full44 output')
            checksum = digest(actual); require(checksum == digest(reference) == digest(original_cpu), 'Full output differs')
            snapshots.append(dict(transaction=tx,path=str(actual),bytes=946498280,sha256=checksum))
        for name, checksum in {**files,**preserved_inputs}.items(): require(digest(name) == checksum, 'Execution input changed '+name)
        # The original compiler evidence remains independently readable after
        # runtime writes have occurred only in the private copy.
        gate()
        atomic(OUT/'comparison.json',dict(status='recovered_full4_RTL_snapshots_equal_original_C',snapshots=snapshots))
        state.update(status='complete',stage='recovered_full4tx_independent_final_audit_pending'); atomic(OUT/'state.json',state)
    except BaseException as exc:
        if child is not None and child.poll() is None: stop(child)
        state.update(status='failed',error=str(exc)); atomic(OUT/'state.json',state); raise


if __name__ == '__main__':main()
