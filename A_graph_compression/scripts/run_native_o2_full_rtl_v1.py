#!/usr/bin/env python3
"""Full four-state/four-transaction run using the existing bound O2 snapshot.

Original DUT, models, input capacities and oracle are unchanged. Periodic Tcl
queries add observability. The old O0 run and its acceptance chain stay separate.
"""
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
from run_recovered_native_rtl_v2 import ROOT, BASE, BIN, TRIAL, OUT as LIVE, gate as original_gate, ERRORS, COMPILE_AUDIT

OUT = BASE/'native_o2_full_rtl_20261103_v1'
BENCH = BASE/'native_xsim_optimization_diagnostic_v1'
SNAPSHOT = 'search_batch_trace_top_v2_optimization_diagnostic_O2'
AUDIT = ROOT/'results/native_xsim_optimization_independent_audit_20261102_v1.json'
REPORT = ROOT/'results/native_o2_full_rtl_audit_20261103_v1.json'
CHECKER = ROOT/'scripts/check_native_o2_full_rtl_v1.py'


def gate():
    original_proof = original_gate()
    proof = json.loads(AUDIT.read_text())
    require(proof['status'] == 'repeated_bounded_100us_O0_O2_diagnostic_independently_rechecked_no_functional_acceptance', 'Wrong O2 provenance audit')
    bound = dict(original_proof['files'])
    for name, checksum in proof['files'].items():
        require(name not in bound or bound[name] == checksum, 'Conflicting compiler provenance')
        bound[name] = checksum
    bound[str(COMPILE_AUDIT)] = digest(COMPILE_AUDIT)
    bound[str(AUDIT)] = digest(AUDIT)
    inputs = json.loads((BENCH/'immutable_runtime_inputs.json').read_text())
    require(len(inputs) == 311, 'Incomplete O2 input/snapshot set')
    for name, checksum in {**bound, **inputs}.items():
        require(digest(name) == checksum, 'O2 provenance changed '+name)
    command = json.loads((BENCH/'plan.json').read_text())['compiler_command_optimized']
    require(command.count('--O2') == 1 and command[command.index('-s')+1] == SNAPSHOT, 'Wrong actual optimized compiler command')
    receipt = json.loads((BENCH/'elaborate_O2.receipt.json').read_text())
    require(receipt['command'] == command and receipt['exit_code'] == 0 and receipt['abort_reason'] is None, 'O2 compilation failed')
    require(receipt['log_sha256'] == digest(BENCH/'elaborate_O2.log'), 'O2 compiler log changed')
    return bound, inputs


def progress_tcl():
    top = '/apatb_search_batch_trace_top_v2_top'
    worker = top+'/AESL_inst_search_batch_trace_top_v2/grp_batch_worker_fu_1174'
    trace = worker+'/grp_a_write_net_trace_record_fu_2547'
    probes = [top+'/finish_cnt', top+'/start_cnt', top+'/clk_cnt', top+'/AESL_done',
              worker+'/i_135_fu_658', worker+'/ap_CS_fsm_state1509', worker+'/ap_CS_fsm_state1510',
              trace+'/ap_start', trace+'/ap_done', trace+'/i_105_fu_596', trace+'/i_117_fu_676',
              trace+'/ap_CS_fsm_state3314', trace+'/ap_CS_fsm_state5328']
    text = ['proc progress {step} {', ' puts "A_O2_PROGRESS step=$step wall_ms=[clock milliseconds]"']
    for i, p in enumerate(probes):
        text += [f' if {{[llength [get_objects {{{p}}}]] == 1}} {{',
                 f'  puts "A_O2_VALUE {i} [get_value -radix hex {{{p}}}]"',
                 f' }} else {{puts "A_O2_UNAVAILABLE {i}"}}']
    text += [' flush stdout', '}', 'progress 0',
             'for {set step 1} {$step <= 100000} {incr step} {',
             ' run 100 us', ' progress $step',
             f' set completed [get_value -radix unsigned {{{top}/finish_cnt}}]',
             ' if {$completed == 4} {break}', '}',
             'if {$completed != 4} {error "NATIVE_O2_INCOMPLETE_AT_10_SECOND_BOUND"}',
             'puts NATIVE_O2_FULL4_SIMULATION_RETURNED', 'flush stdout', 'quit']
    return '\n'.join(text)+'\n', probes


def main():
    def interrupted(signum, frame):
        raise SystemExit(128+signum)
    signal.signal(signal.SIGTERM, interrupted)
    require(not OUT.exists() and not REPORT.exists(), 'Refuse duplicate full O2 run')
    require(CHECKER.is_file(), 'Independent checker missing')
    proof, optimized = gate()
    original = json.loads((LIVE/'plan.json').read_text())
    initial = observe()
    OUT.mkdir()
    state = dict(owner_pid=os.getpid(), owner_start_ticks=Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19],
                 status='running', stage='copy_full_inputs', transactions=4, pointers=44, models=30,
                 original_O0_modified=False, full_kernel_accepted=False)
    atomic(OUT/'state.json', state)
    child = None
    try:
        copies = {}
        for name, row in original['copies'].items():
            relative = Path(name).relative_to(LIVE/'sim')
            if 'xsim.dir' in relative.parts:
                continue
            require(abort_reason(initial, observe()) is None, 'New OOM during copy')
            source = Path(row['source'])
            target = OUT/'sim'/relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            require(digest(target) == row['sha256'], 'Original full input copy changed')
            copies[str(target)] = dict(source=str(source), sha256=row['sha256'])
        snapshot_files = {p:h for p,h in optimized.items() if Path(p).is_relative_to(BENCH/'sim/verilog/xsim.dir'/SNAPSHOT)}
        require(len(snapshot_files) == 9, 'Incomplete O2 snapshot')
        for name, checksum in snapshot_files.items():
            source = Path(name)
            target = OUT/'sim'/source.relative_to(BENCH/'sim')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            require(digest(target) == checksum, 'O2 snapshot copy differs')
            copies[str(target)] = dict(source=str(source), sha256=checksum)
        for name in original['sim_directories']:
            relative = Path(name).relative_to(LIVE/'sim')
            if 'xsim.dir' not in relative.parts:
                (OUT/'sim'/relative).mkdir(parents=True, exist_ok=True)
        require((OUT/'sim/tv/rtldatafile').is_dir() and not list((OUT/'sim/tv/rtldatafile').iterdir()), 'Output tree not fresh')
        frozen = json.loads((TRIAL/'plan.json').read_text())['copied']
        preserved = {str(OUT/'sim'/Path(p).relative_to(TRIAL/'sim')):r['sha256'] for p,r in frozen.items()}
        require(len(preserved) == 293, 'Full original input set changed')
        for name, checksum in preserved.items():
            require(digest(name) == checksum, 'Full input differs '+name)
        tcl, probes = progress_tcl()
        (OUT/'progress.tcl').write_text(tcl)
        prefix = ['prlimit','--as=103079215104:103079215104','--stack=268435456:268435456','--core=0:0','--']
        jobs = [dict(phase='rtl', command=prefix+[str(BIN/'xsim'),'--noieeewarnings',SNAPSHOT,'-tclbatch',str(OUT/'progress.tcl')],cwd=str(OUT/'sim/verilog')),
                dict(phase='postcheck',command=prefix+[str(OUT/'sim/wrapc_pc/cosim.pc.exe')],cwd=str(OUT/'sim/wrapc_pc'))]
        files = dict(proof)
        files.update({str(p):digest(p) for p in [Path(__file__).resolve(), CHECKER, OUT/'progress.tcl', LIVE/'plan.json',
                      BENCH/'plan.json', BENCH/'immutable_runtime_inputs.json', ROOT/'scripts/run_recovered_native_rtl_v2.py',
                      ROOT/'scripts/run_compact_nonzero_native_rtl_v2.py', ROOT/'scripts/owned_sim_resource_policy_v1.py']})
        plan = dict(files=files,copies=copies,preserved_inputs=preserved,snapshot_files=snapshot_files,commands=jobs,
                    initial_memory=initial,resource_policy=POLICY,startup_free_memory_gate=False,
                    transactions=4,pointers=44,models=30,snapshot=SNAPSHOT,probes=probes,
                    runtime_as_bytes=96*1024**3,stack_bytes=256*1024**2,core_bytes=0,
                    simulation_bound_seconds=10,wall_timeout_seconds=45*86400,
                    source_or_memory_model_edits=False,original_O0_modified=False)
        atomic(OUT/'plan.json', plan)
        env = {**os.environ,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1','A_BATCH_RTL_SNAPSHOT_PREFIX':str(OUT/'rtl')}
        for job in jobs:
            phase = job['phase']
            state.update(stage=phase)
            atomic(OUT/'state.json', state)
            require(abort_reason(initial, observe()) is None, 'New OOM before '+phase)
            started = time.monotonic()
            actual = reason = None
            last = 0
            with (OUT/(phase+'.log')).open('x') as log:
                child = subprocess.Popen(job['command'],cwd=job['cwd'],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                state['child_pid'] = child.pid
                atomic(OUT/'state.json', state)
                while child.poll() is None:
                    if actual is None:
                        actual = observe_limits(child, phase)
                        if actual:
                            atomic(OUT/(phase+'.actual_limits.json'), actual)
                    current = observe()
                    reason = abort_reason(initial,current)
                    if time.monotonic()-started > plan['wall_timeout_seconds']:
                        reason = reason or 'full_run_wall_timeout'
                    if time.monotonic()-last >= 30:
                        atomic(OUT/'resource_observation.json', dict(phase=phase,memory=current,actual_limits=actual))
                        last = time.monotonic()
                    if reason:
                        stop(child)
                        break
                    time.sleep(1)
                code = child.wait()
                child = None
            final = observe()
            reason = reason or abort_reason(initial,final)
            log = OUT/(phase+'.log')
            text = log.read_text(errors='replace')
            atomic(OUT/(phase+'.receipt.json'), dict(command=job['command'],cwd=job['cwd'],exit_code=code,abort_reason=reason,
                   actual_limits=actual,final_memory=final,elapsed_seconds=time.monotonic()-started,log_sha256=digest(log)))
            require(code == 0 and reason is None and actual is not None and not any(e in text for e in ERRORS), 'Failed O2 '+phase)
            if phase == 'rtl':
                require(re.search(r'RTL Simulation\s*:\s*4\s*/\s*4',text) and
                        re.search(r'^NATIVE_O2_FULL4_SIMULATION_RETURNED$',text,re.M), 'Four RTL transactions incomplete')
            else:
                require('FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode=1 ports=44 transactions=4' in text and
                        'SEARCH_BATCH_PASS mode=1' in text, 'Full original C postcheck failed')
        for name, checksum in {**files, **preserved}.items():
            require(digest(name) == checksum, 'O2 execution input changed '+name)
        state.update(status='complete',stage='full4_RTL_C_independent_audit_pending')
        atomic(OUT/'state.json', state)
        audit_command = ['prlimit','--as=17179869184:17179869184','--stack=67108864:67108864','--core=0:0','--',
                         'python3',str(CHECKER)]
        with (OUT/'audit.log').open('x') as log:
            child = subprocess.Popen(audit_command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            audit_started = time.monotonic()
            while child.poll() is None:
                reason = abort_reason(initial, observe())
                if time.monotonic()-audit_started > 3600:
                    reason = reason or 'audit_wall_timeout'
                if reason:
                    stop(child)
                    break
                time.sleep(1)
            code = child.wait()
            child = None
        atomic(OUT/'audit.receipt.json',dict(command=audit_command,exit_code=code,abort_reason=reason,
               elapsed_seconds=time.monotonic()-audit_started,log_sha256=digest(OUT/'audit.log'),
               report_sha256=digest(REPORT) if REPORT.exists() else None))
        require(code == 0 and reason is None and REPORT.exists(), 'Independent full O2 audit failed')
        atomic(OUT/'terminal.json',dict(status='full4_O2_RTL_independently_verified',report=str(REPORT),report_sha256=digest(REPORT),
               downstream_gates_rewired=False,physical_verified=False,board_verified=False))
    except BaseException as exc:
        if child is not None:
            stop(child)
        state.update(status='failed',error=str(exc))
        atomic(OUT/'state.json',state)
        raise


if __name__ == '__main__':
    main()
