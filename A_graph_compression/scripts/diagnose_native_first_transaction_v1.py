#!/usr/bin/env python3
"""Bounded diagnostic replay; never grants functional acceptance or edits live RTL."""
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time

from check_vitis_kernel import digest, require
from owned_sim_resource_policy_v1 import observe, abort_reason
from run_compact_native_stack_recovery_v3 import atomic
from run_compact_nonzero_native_rtl_v2 import observe_limits, stop
from run_recovered_native_rtl_v2 import gate, OUT as LIVE, BIN

ROOT = Path(__file__).resolve().parents[1]
OUT = LIVE.parent / 'native_first_transaction_diagnostic_replay_v1'
PREP = ROOT / 'data/derived/native_first_transaction_diagnosis_20261102_v1'


def main():
    def interrupted(signum, frame):
        raise SystemExit(128 + signum)
    signal.signal(signal.SIGTERM, interrupted)
    require(not OUT.exists(), 'Refuse duplicate diagnostic replay')
    OUT.mkdir()
    initial = observe()
    child = None
    state = dict(owner_pid=os.getpid(), status='running', stage='verify_compiler',
                 functional_acceptance=False, live_run_modified=False)
    atomic(OUT/'state.json', state)
    try:
        proof = gate()
        original = json.loads((LIVE/'plan.json').read_text())
        require((original['transactions'], original['pointers'], original['models']) == (4,44,30), 'Scope mismatch')
        state['stage'] = 'copy_complete_compiled_snapshot'
        atomic(OUT/'state.json', state)
        copied = {}
        # Copy from the preserved compiler trial, not mutable live simulation files.
        for live_name, row in original['copies'].items():
            source = Path(row['source'])
            relative = Path(live_name).relative_to(LIVE/'sim')
            target = OUT/'sim'/relative
            require(not source.is_symlink(), 'Unexpected symlink')
            require(abort_reason(initial, observe()) is None, 'OOM/reset during copy')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            require(digest(target) == row['sha256'], 'Changed compiled snapshot input '+str(source))
            copied[str(target)] = row['sha256']
        for name in original['sim_directories']:
            (OUT/'sim'/Path(name).relative_to(LIVE/'sim')).mkdir(parents=True, exist_ok=True)
        require(not list((OUT/'sim/tv/rtldatafile').iterdir()), 'Diagnostic output directory not empty')
        probes = json.loads((PREP/'report.json').read_text())['probe_paths']
        # Also expose batch-worker internal AXI handshake, before the bus adapter.
        worker = '/apatb_search_batch_trace_top_v2_top/AESL_inst_search_batch_trace_top_v2/grp_batch_worker_fu_1174'
        probes += [worker+'/m_axi_node_table_mem_'+s for s in ['AWVALID','AWREADY','WVALID','WREADY']]
        lines = ['proc sample {step} {', ' puts "A_DIAG_SAMPLE $step"']
        for i, path in enumerate(probes):
            lines += [f' if {{[llength [get_objects {{{path}}}]] != 1}} {{error "Missing diagnostic object {i}"}}',
                      f' puts "A_DIAG_VALUE {i} [get_value -radix hex {{{path}}}]"']
        lines += [' flush stdout', '}', 'sample 0']
        # 100 us total: early observations, then a longer initialization interval.
        steps = [1]*10 + [10]*9
        for i, us in enumerate(steps, 1):
            lines += [f'run {us} us', f'sample {i}']
        lines += ['puts A_DIAG_BOUNDED_CAPTURE_COMPLETE', 'flush stdout', 'quit']
        tcl = OUT/'diagnostic.tcl'; tcl.write_text('\n'.join(lines)+'\n')
        command = ['prlimit','--as=103079215104:103079215104',
                   '--stack=268435456:268435456','--core=0:0','--',
                   str(BIN/'xsim'),'--noieeewarnings','search_batch_trace_top_v2','-tclbatch',str(tcl)]
        atomic(OUT/'plan.json', dict(command=command, copied=copied, probes=probes,
               simulation_us=sum(steps), wall_timeout_seconds=1800, functional_acceptance=False,
               live_run_modified=False, initial_memory=initial,
               files={str(Path(__file__).resolve()):digest(__file__),str(tcl):digest(tcl),
                      str(LIVE/'plan.json'):digest(LIVE/'plan.json'),
                      str(PREP/'report.json'):digest(PREP/'report.json')},
               compiler_audit_status=proof['status']))
        state['stage']='diagnostic_replay'
        atomic(OUT/'state.json', state)
        start=time.monotonic(); actual=None; reason=None
        with (OUT/'diagnostic.log').open('x') as log:
            child=subprocess.Popen(command,cwd=OUT/'sim/verilog',start_new_session=True,
                  stdout=log,stderr=subprocess.STDOUT,env={**os.environ,
                  'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1',
                  'A_BATCH_RTL_SNAPSHOT_PREFIX':str(OUT/'diagnostic_only')})
            state['child_pid']=child.pid;atomic(OUT/'state.json',state)
            while child.poll() is None:
                if actual is None:
                    actual=observe_limits(child,'rtl')
                    if actual:atomic(OUT/'actual_limits.json',actual)
                reason=abort_reason(initial,observe())
                if time.monotonic()-start>1800:reason=reason or 'diagnostic_wall_timeout'
                if reason:stop(child);break
                time.sleep(1)
            code=child.wait();child=None
        reason=reason or abort_reason(initial,observe())
        log_text=(OUT/'diagnostic.log').read_text(errors='replace')
        atomic(OUT/'receipt.json',dict(exit_code=code,abort_reason=reason,actual_limits=actual,
               elapsed_seconds=time.monotonic()-start,log_sha256=digest(OUT/'diagnostic.log'),
               functional_acceptance=False))
        require(code==0 and reason is None and actual is not None,'Diagnostic execution failed')
        require('A_DIAG_BOUNDED_CAPTURE_COMPLETE' in log_text,'Diagnostic capture incomplete')
        require(not any(s in log_text for s in ['ERROR:','Fatal:','A_REBASE_','A_RO_']), 'Diagnostic error')
        state.update(status='complete',stage='bounded_diagnostic_capture_only')
        atomic(OUT/'state.json',state)
    except BaseException as exc:
        if child is not None and child.poll() is None:stop(child)
        state.update(status='failed',error=str(exc));atomic(OUT/'state.json',state)
        raise


if __name__=='__main__':main()
