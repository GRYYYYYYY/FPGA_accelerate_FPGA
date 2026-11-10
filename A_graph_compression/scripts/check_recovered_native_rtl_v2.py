#!/usr/bin/env python3
"""Independently accept only all4 recovered RTL transactions and full original C outputs."""
import json
from pathlib import Path
import re
import shlex
from check_vitis_kernel import digest, require
from owned_sim_resource_policy_v1 import abort_reason, POLICY
from run_recovered_native_rtl_v2 import ROOT, BASE, OUT, TRIAL, BIN, COMPILE_AUDIT, ERRORS

REPORT = ROOT/'results/collision_safe_recovered_native_rtl_audit_20261030_v2.json'


def audit():
    require((OUT/'state.json').exists(), 'Recovered RTL trial has not started')
    state = json.loads((OUT/'state.json').read_text())
    require(state['status'] == 'complete' and state['stage'] == 'recovered_full4tx_independent_final_audit_pending',
            'Recovered full RTL/C execution has not completed')
    plan = json.loads((OUT/'plan.json').read_text()); original = json.loads((TRIAL/'plan.json').read_text())
    files = {}
    def bind(path):
        checksum = digest(path)
        require(str(path) not in files or files[str(path)] == checksum, 'Conflicting evidence binding')
        files[str(path)] = checksum
        return checksum
    proof = json.loads(COMPILE_AUDIT.read_text())
    require(proof['status'] == 'surviving_original_native_compiler_exit0_snapshot_and_full_inputs_independently_verified_RTL_pending',
            'Missing independent recovered compiler gate')
    for name, checksum in proof['files'].items(): require(bind(name) == checksum, 'Changed original compiler evidence '+name)
    bind(COMPILE_AUDIT)
    for name, checksum in plan['files'].items(): require(bind(name) == checksum, 'Changed recovery input '+name)
    require((plan['transactions'],plan['pointers'],plan['models']) == (4,44,30) and
            plan['compile_reused'] is True and plan['compile_wait_receipt_fabricated'] is False and
            plan['original_trial'] == str(TRIAL), 'Changed recovery scope')
    require(plan['resource_policy'] == POLICY and plan['startup_free_memory_gate'] is False and
            (plan['runtime_as_bytes'],plan['stack_bytes'],plan['core_bytes']) == (96*1024**3,256*1024**2,0), 'Different resource contract')
    expected_dirs={str(OUT/'sim'/p.relative_to(TRIAL/'sim')) for p in (TRIAL/'sim').rglob('*') if p.is_dir()}
    require(set(plan['sim_directories'])==expected_dirs and all(Path(p).is_dir() for p in expected_dirs), 'Missing preserved directory hierarchy')
    original_files = {str(p) for p in (TRIAL/'sim').rglob('*') if p.is_file()}
    require({row['source'] for row in plan['copies'].values()} == original_files and
            len(plan['copies']) == len(original_files), 'Incomplete compiled simulation copy')
    for name, row in plan['copies'].items():
        require(Path(name) == OUT/'sim'/Path(row['source']).relative_to(TRIAL/'sim'), 'Wrong copy mapping')
        require(bind(row['source']) == row['sha256'] and bind(name) == row['sha256'], 'Changed copied simulation file '+name)
    expected_inputs = {str(OUT/'sim'/Path(name).relative_to(TRIAL/'sim')):row['sha256'] for name,row in original['copied'].items()}
    kernel = OUT/'sim/verilog/xsim.dir/search_batch_trace_top_v2/xsimk'
    expected_inputs[str(kernel)] = proof['files'][str(TRIAL/'sim/verilog/xsim.dir/search_batch_trace_top_v2/xsimk')]
    require(len(expected_inputs) == 294 and plan['preserved_inputs'] == expected_inputs, 'Incomplete original full44 inputs/kernel')
    for name, checksum in expected_inputs.items(): require(bind(name) == checksum, 'Modified actual RTL input '+name)
    require(bind(OUT/'bounded.tcl') == original['files'][str(TRIAL/'bounded.tcl')], 'Changed original simulation bound/probes')
    prefix = ['prlimit','--as=103079215104:103079215104','--stack=268435456:268435456','--core=0:0','--']
    jobs = [dict(phase='rtl',command=prefix+[str(BIN/'xsim'),'--noieeewarnings','search_batch_trace_top_v2','-tclbatch',str(OUT/'bounded.tcl')],cwd=str(OUT/'sim/verilog')),
            dict(phase='postcheck',command=prefix+[str(OUT/'sim/wrapc_pc/cosim.pc.exe')],cwd=str(OUT/'sim/wrapc_pc'))]
    require(plan['commands'] == jobs, 'Different execution commands')
    for job in jobs:
        phase = job['phase']; receipt_path = OUT/(phase+'.receipt.json'); actual_path = OUT/(phase+'.actual_limits.json')
        receipt = json.loads(receipt_path.read_text()); actual = json.loads(actual_path.read_text())
        log = OUT/(phase+'.log'); text = log.read_text(errors='replace')
        require(receipt['command'] == job['command'] and receipt['cwd'] == job['cwd'] and receipt['actual_limits'] == actual,
                'Different actual execution receipt')
        require(receipt['exit_code'] == 0 and receipt['abort_reason'] is None and receipt['elapsed_seconds'] > 0 and
                receipt['log_sha256'] == bind(log) and abort_reason(plan['initial_memory'],receipt['final_memory']) is None,
                'Execution failed/aborted or log changed')
        require(not any(error in text for error in ERRORS), 'Runtime error in '+phase)
        require(actual['address_space'] == [96*1024**3]*2 and actual['stack'] == [256*1024**2]*2 and
                actual['core'] == [0,0] and actual['cwd'] == job['cwd'] and actual['pid'] > 0 and
                int(actual['start_ticks']) > 0, 'Different/missing actual limits or identity')
        expected_exe = 'xsimk' if phase == 'rtl' else 'cosim.pc.exe'
        require(Path(shlex.split(actual['command'])[0]).name == expected_exe, 'Different phase binary')
        if phase == 'rtl':
            require(re.search(r'RTL Simulation\s*:\s*4\s*/\s*4',text) is not None and
                    'COLLISION_SAFE_NATIVE_BOUNDED_RETURNED' in text, 'Incomplete full4 RTL')
        else:
            require('FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode=1 ports=44 transactions=4' in text and
                    'SEARCH_BATCH_PASS mode=1' in text, 'Missing original full C oracle')
        bind(receipt_path); bind(actual_path)
    perf = OUT/'sim/verilog/search_batch_trace_top_v2.performance.result.transaction.xml'
    cycles = [tuple(map(int,row)) for row in re.findall(r'^transaction\s+(\d+):\s+(\d+)\s+(?:\d+|x)\s*$',perf.read_text(),re.M)]
    require([tx for tx,c in cycles] == [0,1,2,3] and all(c > 0 for tx,c in cycles), 'Incomplete positive transaction cycles'); bind(perf)
    snapshots = []
    for tx in range(4):
        actual = OUT/f'rtl_1_{tx}.bin'; fresh = BASE/'collision_safe_compact_cosim_setup_v1'/f'hls_1_{tx}.bin'
        original_cpu = BASE/'compressed_batch_rtl_tb_cpu_v2'/f'cpu_1_{tx}.bin'
        require(all(p.stat().st_size == 946498280 for p in [actual,fresh,original_cpu]), 'Truncated full44 snapshot')
        require(bind(actual) == bind(fresh) == bind(original_cpu), 'Different original/fresh C/RTL output')
        snapshots.append(dict(transaction=tx,path=str(actual),bytes=946498280,sha256=files[str(actual)]))
    comparison = json.loads((OUT/'comparison.json').read_text())
    require(comparison['status'] == 'recovered_full4_RTL_snapshots_equal_original_C' and comparison['snapshots'] == snapshots,
            'Wrong comparison receipt')
    raw = list((OUT/'sim/tv/rtldatafile').glob('rtl.*.dat'))
    expected_raw = {p.name for p in (BASE/'compact_nonzero_native_rtl_v2/sim/tv/rtldatafile').glob('rtl.*.dat')}
    require(len(raw) == 25 and {p.name for p in raw} == expected_raw, 'Incomplete raw RTL outputs')
    for p in raw: bind(p)
    for p in [OUT/'state.json',OUT/'plan.json',OUT/'comparison.json',Path(__file__).resolve()]:bind(p)
    return dict(status='recovered_collision_safe_native_full4tx_full44_original_C_independently_verified',files=files,
                cycles=[c for tx,c in cycles],snapshots=snapshots,transactions=4,pointers=44,models=30,
                original_driver_exit_code=143,rtl_verified=True,physical_verified=False,board_verified=False,
                limits=['Complete original synthetic transactions only; real routing and platform remain separate requirements.',
                        'Original driver interruption preserved; compiler recovered via independently observed terminal evidence.',
                        'No physical capacity, timing closure, bandwidth, power or FPGA speedup claim.'])


if __name__ == '__main__':
    require(not REPORT.exists(), 'Refuse overwrite')
    result = audit()
    with REPORT.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(result['status'])
