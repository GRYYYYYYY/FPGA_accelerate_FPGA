#!/usr/bin/env python3
"""Monitor the verified surviving compiler; preserve terminal evidence, never relaunch."""
import json
import os
from pathlib import Path
import re
import resource
import signal
import time
from check_vitis_kernel import digest, require
from experiment_status_v6 import process
from owned_sim_resource_policy_v1 import observe, abort_reason
from run_compact_native_stack_recovery_v3 import atomic

ROOT = Path(__file__).resolve().parents[1]
TRIAL = Path('/tmp/A_graph_compression_recovery_20261025_v1/collision_safe_native_rtl_v1')
OUT = ROOT/'data/derived/collision_safe_native_compiler_observation_20261030_v1'


def matches(record):
    live = process(record['pid'])
    return bool(live and live['state'] != 'Z' and live['start_ticks'] == record['start_ticks'] and
                live['command'] == record['command'])


def main():
    require(not OUT.exists(), 'Refuse duplicate observer')
    actual = json.loads((TRIAL/'elaborate.actual_limits.json').read_text())
    old = json.loads((TRIAL/'state.json').read_text())
    require(process(old['owner_pid']) is None, 'Original owner still exists; do not adopt')
    compiler = process(actual['pid']); timer = process(old['child_pid'])
    require(compiler and matches(actual) and timer and timer['command'].startswith('/usr/bin/time -v '), 'Surviving process identities unverified')
    require(os.getpgid(compiler['pid']) == os.getsid(compiler['pid']) == timer['pid'] and
            os.getpgid(timer['pid']) == timer['pid'], 'Unexpected surviving process group')
    for key, kind in [('address_space',resource.RLIMIT_AS),('stack',resource.RLIMIT_STACK),('core',resource.RLIMIT_CORE)]:
        require(list(resource.prlimit(compiler['pid'],kind)) == actual[key], 'Compiler limits changed')
    require(os.readlink(f'/proc/{compiler["pid"]}/cwd') == actual['cwd'], 'Compiler cwd changed')
    initial = json.loads((TRIAL/'plan.json').read_text())['initial_memory']
    OUT.mkdir()
    atomic(OUT/'plan.json', dict(compiler=compiler, timer=timer, actual_limits=actual,
           initial_memory=initial, script_sha256=digest(__file__), trial=str(TRIAL),
           no_compile_restart=True, no_rtl_launch=True, no_free_memory_gate=True))
    state = dict(owner_pid=os.getpid(), status='running', stage='observing_existing_compiler',
                 compiler_pid=compiler['pid'], compiler_accepted=False)
    atomic(OUT/'state.json',state)
    try:
        while True:
            comp_live = matches(compiler); timer_live = matches(timer); memory = observe()
            reason = abort_reason(initial,memory)
            atomic(OUT/'observation.json',dict(compiler_verified=comp_live,timer_verified=timer_live,
                   memory=memory,monotonic_seconds=time.monotonic()))
            if reason:
                # Only this originally owned and still identity-matching session.
                if timer_live and os.getpgid(timer['pid']) == timer['pid']:
                    os.killpg(timer['pid'],signal.SIGTERM)
                    time.sleep(5)
                    if matches(timer) or matches(compiler): os.killpg(timer['pid'],signal.SIGKILL)
                raise RuntimeError(reason)
            if not comp_live and not timer_live: break
            time.sleep(10)
        log = TRIAL/'elaborate.log'; text = log.read_text(errors='replace')
        exits = re.findall(r'^\s*Exit status:\s*(\d+)\s*$',text,re.M)
        built = text.splitlines().count('Built simulation snapshot search_batch_trace_top_v2')
        errors = [s for s in ['ERROR:', 'Fatal:', 'LLVM ERROR', 'Command terminated by signal'] if s in text]
        snapshot = TRIAL/'sim/verilog/xsim.dir/search_batch_trace_top_v2/xsimk'
        result = dict(status='orphaned_compiler_terminal_observation_requires_independent_review',
                      timer_reported_exit_statuses=exits,snapshot_built_markers=built,errors=errors,
                      snapshot_exists=snapshot.is_file(),snapshot_sha256=digest(snapshot) if snapshot.is_file() else None,
                      log_sha256=digest(log),final_memory=observe(),compiler_identity=compiler,timer_identity=timer,
                      limitation='Observed original time utility footer; not a fabricated subprocess.wait receipt and not RTL acceptance.')
        atomic(OUT/'terminal.json',result)
        require(exits == ['0'] and built == 1 and not errors and snapshot.is_file(), 'Compiler did not produce complete success evidence')
        require(abort_reason(initial,result['final_memory']) is None, 'OOM/reset at compiler termination')
        state.update(status='complete',stage='compiler_terminal_evidence_pending_independent_recovery_audit')
        atomic(OUT/'state.json',state)
    except BaseException as exc:
        state.update(status='failed',error=str(exc));atomic(OUT/'state.json',state);raise


if __name__ == '__main__':main()
