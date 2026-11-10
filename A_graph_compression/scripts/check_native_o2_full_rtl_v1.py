#!/usr/bin/env python3
"""Independent full-output audit for the unchanged-source four-state O2 run."""
import json
from pathlib import Path
import re
import shlex
from check_vitis_kernel import digest, require
from owned_sim_resource_policy_v1 import POLICY, abort_reason
from run_native_o2_full_rtl_v1 import ROOT, BASE, OUT, LIVE, TRIAL, BENCH, SNAPSHOT, AUDIT, REPORT, BIN, ERRORS
from run_recovered_native_rtl_v2 import COMPILE_AUDIT


def audit():
    require((OUT/'state.json').is_file(), 'Full O2 trial has not started')
    state = json.loads((OUT/'state.json').read_text())
    require(state['status'] == 'complete' and state['stage'] == 'full4_RTL_C_independent_audit_pending', 'Full RTL/C execution not complete')
    plan = json.loads((OUT/'plan.json').read_text())
    require((plan['transactions'],plan['pointers'],plan['models']) == (4,44,30) and
            plan['snapshot'] == SNAPSHOT and plan['source_or_memory_model_edits'] is False and
            plan['original_O0_modified'] is False, 'Changed full scope or original source contract')
    require(plan['resource_policy'] == POLICY and plan['startup_free_memory_gate'] is False and
            (plan['runtime_as_bytes'],plan['stack_bytes'],plan['core_bytes']) == (96*1024**3,256*1024**2,0), 'Changed execution limits')
    files = {}
    def bind(path):
        name = str(path)
        checksum = digest(path)
        require(name not in files or files[name] == checksum, 'Conflicting evidence')
        files[name] = checksum
        return checksum
    for name, checksum in plan['files'].items():
        require(bind(name) == checksum, 'Changed frozen dependency '+name)
    original_proof = json.loads(COMPILE_AUDIT.read_text())
    require(original_proof['status'] == 'surviving_original_native_compiler_exit0_snapshot_and_full_inputs_independently_verified_RTL_pending', 'Wrong original compiler audit')
    for name, checksum in original_proof['files'].items():
        require(bind(name) == checksum, 'Changed original compiler evidence')
    bind(COMPILE_AUDIT)
    o2_proof = json.loads(AUDIT.read_text())
    require(o2_proof['status'] == 'repeated_bounded_100us_O0_O2_diagnostic_independently_rechecked_no_functional_acceptance', 'Wrong O2 provenance')
    for name, checksum in o2_proof['files'].items():
        require(bind(name) == checksum, 'Changed O2 compiler evidence')
    compiler = json.loads((BENCH/'plan.json').read_text())
    before, after = compiler['compiler_command_original'], compiler['compiler_command_optimized']
    require(before.count('--O0') == after.count('--O2') == 1, 'Wrong optimization comparison')
    expected = list(before)
    expected[expected.index('--O0')] = '--O2'
    expected[expected.index('-s')+1] = SNAPSHOT
    require(after == expected, 'Compiler changes beyond optimization and snapshot name')
    receipt = json.loads((BENCH/'elaborate_O2.receipt.json').read_text())
    require(receipt['exit_code'] == 0 and receipt['abort_reason'] is None and receipt['command'] == after and
            bind(BENCH/'elaborate_O2.log') == receipt['log_sha256'], 'O2 compiler receipt invalid')
    immutable = json.loads((BENCH/'immutable_runtime_inputs.json').read_text())
    require(len(immutable) == 311, 'Incomplete O2 bindings')
    for name, checksum in immutable.items():
        require(bind(name) == checksum, 'Changed O2 compile input/snapshot')
    snapshot = {p:h for p,h in immutable.items() if Path(p).is_relative_to(BENCH/'sim/verilog/xsim.dir'/SNAPSHOT)}
    require(len(snapshot) == 9 and plan['snapshot_files'] == snapshot, 'Incomplete selected snapshot')
    original = json.loads((LIVE/'plan.json').read_text())
    expected_copies = {}
    for name, row in original['copies'].items():
        relative = Path(name).relative_to(LIVE/'sim')
        if 'xsim.dir' not in relative.parts:
            expected_copies[str(OUT/'sim'/relative)] = row
    expected_copies.update({str(OUT/'sim'/Path(p).relative_to(BENCH/'sim')):dict(source=p,sha256=h) for p,h in snapshot.items()})
    require(plan['copies'] == expected_copies, 'Incomplete or substituted full simulation copy')
    for name, row in expected_copies.items():
        require(bind(row['source']) == row['sha256'] and bind(name) == row['sha256'], 'Copied source/snapshot differs '+name)
    frozen = json.loads((TRIAL/'plan.json').read_text())['copied']
    expected_inputs = {str(OUT/'sim'/Path(p).relative_to(TRIAL/'sim')):r['sha256'] for p,r in frozen.items()}
    require(len(expected_inputs) == 293 and expected_inputs == plan['preserved_inputs'], 'Full inputs omitted or changed')
    for name, checksum in expected_inputs.items():
        require(bind(name) == checksum, 'Input changed during execution')
    tcl = (OUT/'progress.tcl').read_text()
    require('run 100 us' in tcl and '$step <= 100000' in tcl and
            'NATIVE_O2_INCOMPLETE_AT_10_SECOND_BOUND' in tcl and
            not re.search(r'(?m)^\s*(force|add_force|restart|set_value|remove_forces)\b',tcl), 'Wrong runtime bound or state mutation')
    prefix = ['prlimit','--as=103079215104:103079215104','--stack=268435456:268435456','--core=0:0','--']
    expected_jobs = [dict(phase='rtl',command=prefix+[str(BIN/'xsim'),'--noieeewarnings',SNAPSHOT,'-tclbatch',str(OUT/'progress.tcl')],cwd=str(OUT/'sim/verilog')),
                     dict(phase='postcheck',command=prefix+[str(OUT/'sim/wrapc_pc/cosim.pc.exe')],cwd=str(OUT/'sim/wrapc_pc'))]
    require(plan['commands'] == expected_jobs, 'Execution command changed')
    for job in expected_jobs:
        phase = job['phase']
        receipt = json.loads((OUT/(phase+'.receipt.json')).read_text())
        actual = json.loads((OUT/(phase+'.actual_limits.json')).read_text())
        text = (OUT/(phase+'.log')).read_text()
        require(receipt['command'] == job['command'] and receipt['cwd'] == job['cwd'] and receipt['actual_limits'] == actual,
                'Actual command/identity mismatch')
        require(receipt['exit_code'] == 0 and receipt['abort_reason'] is None and receipt['elapsed_seconds'] > 0 and
                receipt['log_sha256'] == bind(OUT/(phase+'.log')) and
                abort_reason(plan['initial_memory'],receipt['final_memory']) is None, 'Execution failed or changed')
        require(actual['address_space'] == [96*1024**3]*2 and actual['stack'] == [256*1024**2]*2 and actual['core'] == [0,0] and
                actual['cwd'] == job['cwd'] and actual['pid'] > 0 and int(actual['start_ticks']) > 0, 'Wrong actual limits')
        require(Path(shlex.split(actual['command'])[0]).name == ('xsimk' if phase == 'rtl' else 'cosim.pc.exe'), 'Wrong actual executable')
        require(not any(e in text for e in ERRORS), 'Runtime error')
        if phase == 'rtl':
            require(re.search(r'RTL Simulation\s*:\s*4\s*/\s*4',text) and
                    len(re.findall(r'^NATIVE_O2_FULL4_SIMULATION_RETURNED$',text,re.M)) == 1, 'Four RTL transactions incomplete')
        else:
            require('FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode=1 ports=44 transactions=4' in text and 'SEARCH_BATCH_PASS mode=1' in text, 'Missing full original oracle')
        bind(OUT/(phase+'.receipt.json'))
        bind(OUT/(phase+'.actual_limits.json'))
    perf = OUT/'sim/verilog/search_batch_trace_top_v2.performance.result.transaction.xml'
    cycles = [tuple(map(int, row)) for row in re.findall(r'^transaction\s+(\d+):\s+(\d+)\s+(?:\d+|x)\s*$',perf.read_text(),re.M)]
    require([tx for tx,c in cycles] == [0,1,2,3] and all(c > 0 for tx,c in cycles), 'Missing positive cycles')
    bind(perf)
    snapshots = []
    for tx in range(4):
        actual = OUT/f'rtl_1_{tx}.bin'
        fresh = BASE/'collision_safe_compact_cosim_setup_v1'/f'hls_1_{tx}.bin'
        cpu = BASE/'compressed_batch_rtl_tb_cpu_v2'/f'cpu_1_{tx}.bin'
        require(all(p.stat().st_size == 946498280 for p in (actual,fresh,cpu)), 'Truncated full44 output')
        require(bind(actual) == bind(fresh) == bind(cpu), 'RTL output differs from original/fresh C')
        snapshots.append(dict(transaction=tx,path=str(actual),bytes=946498280,sha256=files[str(actual)]))
    raw = list((OUT/'sim/tv/rtldatafile').glob('rtl.*.dat'))
    expected_raw = {p.name for p in (BASE/'compact_nonzero_native_rtl_v2/sim/tv/rtldatafile').glob('rtl.*.dat')}
    require(len(raw) == 25 and {p.name for p in raw} == expected_raw, 'Incomplete original raw output set')
    for p in raw:
        bind(p)
    for p in (OUT/'state.json',OUT/'plan.json',Path(__file__).resolve(),AUDIT,BENCH/'immutable_runtime_inputs.json'):
        bind(p)
    return dict(status='unchanged_native_O2_full4tx_full44_original_C_independently_verified',files=files,
                cycles=[c for tx,c in cycles],snapshots=snapshots,transactions=4,pointers=44,models=30,
                rtl_verified=True,physical_verified=False,board_verified=False,original_O0_replaced=False,
                downstream_gates_rewired=False,limitations=['Original complete synthetic scope; real workloads remain separate.',
                'Compiler O2 with original four-state XSim and unchanged source/models; runtime telemetry only.',
                'No timing closure, board execution or hardware speedup claim.'])


if __name__ == '__main__':
    require(not REPORT.exists(), 'Refuse overwrite')
    result = audit()
    with REPORT.open('x') as stream:
        json.dump(result,stream,indent=2)
        stream.write('\n')
    print(result['status'])
