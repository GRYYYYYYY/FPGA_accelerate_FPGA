#!/usr/bin/env python3
"""Accept only completed fresh native RTL, original postcheck and full outputs."""
import json
from pathlib import Path
import re
import shlex
from check_vitis_kernel import digest, require
from owned_sim_resource_policy_v1 import abort_reason, POLICY
from run_collision_safe_native_rtl_v1 import ROOT, BASE, OUT, PREP, AUDIT, HLS_AUDIT, BIN, ERRORS, diagnostic_tcl

REPORT = ROOT/'results/collision_safe_native_rtl_audit_20261030_v1.json'


def audit():
    state = json.loads((OUT/'state.json').read_text())
    require(state['status'] == 'complete' and state['stage'] == 'independent_final_rtl_audit_pending',
            'Full fresh RTL and original postcheck have not completed')
    files = {}

    def bind(path):
        path = Path(path)
        checksum = digest(path)
        require(str(path) not in files or files[str(path)] == checksum, 'Conflicting binding '+str(path))
        files[str(path)] = checksum
        return checksum

    def bound_report(path, status):
        obj = json.loads(Path(path).read_text())
        require(obj['status'] == status, 'Wrong prerequisite '+str(path))
        for name, checksum in obj['files'].items():
            require(bind(name) == checksum, 'Changed prerequisite '+name)
        bind(path)
        return obj

    prep_audit = bound_report(AUDIT, 'collision_safe_native_full44_inputs_all30_guards_all44_relocations_independently_verified')
    hls = bound_report(HLS_AUDIT, 'collision_safe_native_compact_hls_all9_dynamic_connections_and_full44_C_verified_rtl_pending')
    setup = bound_report(BASE/'collision_safe_compact_cosim_setup_v1/setup.json',
                         'collision_safe_full44_four_transaction_csim_and_fresh_setup_verified_rtl_pending')
    preparation = json.loads((PREP/'preparation.json').read_text())
    plan = json.loads((OUT/'plan.json').read_text())
    require((plan['transactions'], plan['pointers'], plan['models']) == (4, 44, 30), 'Changed scope')
    require(plan['resource_policy'] == POLICY and plan['startup_free_memory_gate'] is False and
            plan['original_postcheck_preserved'] is True, 'Changed execution policy')
    require((plan['compiler_as_bytes'], plan['runtime_as_bytes'], plan['stack_bytes'], plan['core_bytes']) ==
            (192*1024**3, 96*1024**3, 256*1024**2, 0), 'Changed finite limits')
    for name, checksum in plan['files'].items():
        require(bind(name) == checksum, 'Changed execution input '+name)
    expected_sources = {str(p) for p in (PREP/'sim').rglob('*') if p.is_file()}
    require({r['source'] for r in plan['copied'].values()} == expected_sources and
            len(plan['copied']) == len(expected_sources), 'Incomplete copied inputs')
    for name, row in plan['copied'].items():
        expected = OUT/'sim'/Path(row['source']).relative_to(PREP/'sim')
        require(name == str(expected) and row['sha256'] == prep_audit['files'][row['source']] and
                bind(name) == row['sha256'], 'Changed actual simulation input '+name)
    tcl, probes = diagnostic_tcl(OUT/'sim/verilog', hls)
    require((OUT/'bounded.tcl').read_text() == tcl and plan['diagnostic_probes'] == probes, 'Changed bound/probes')
    runtime = ['prlimit', '--as=103079215104:103079215104', '--stack=268435456:268435456', '--core=0:0', '--']
    jobs = [dict(phase='elaborate', command=preparation['compile_command'], cwd=str(OUT/'sim/verilog')),
            dict(phase='rtl', command=runtime+[str(BIN/'xsim'), '--noieeewarnings', 'search_batch_trace_top_v2',
                 '-tclbatch', str(OUT/'bounded.tcl')], cwd=str(OUT/'sim/verilog')),
            dict(phase='postcheck', command=runtime+[str(OUT/'sim/wrapc_pc/cosim.pc.exe')], cwd=str(OUT/'sim/wrapc_pc'))]
    require(plan['commands'] == jobs, 'Changed commands')
    for job in jobs:
        phase = job['phase']
        receipt_path = OUT/(phase+'.receipt.json')
        receipt = json.loads(receipt_path.read_text())
        actual_path = OUT/(phase+'.actual_limits.json')
        actual = json.loads(actual_path.read_text())
        log = OUT/(phase+'.log'); text = log.read_text(errors='replace')
        require(receipt['command'] == job['command'] and receipt['cwd'] == job['cwd'] and
                receipt['actual_limits'] == actual, 'Executed phase differs')
        require(receipt['exit_code'] == 0 and receipt['abort_reason'] is None and receipt['elapsed_seconds'] > 0 and
                receipt['log_sha256'] == bind(log), 'Failed or changed phase')
        require(abort_reason(plan['initial_memory'], receipt['final_memory']) is None, 'OOM/reset during trial')
        require(not any(e in text for e in ERRORS), 'Execution error '+phase)
        cap = (192 if phase == 'elaborate' else 96)*1024**3
        require(actual['address_space'] == [cap, cap] and actual['stack'] == [256*1024**2]*2 and
                actual['core'] == [0, 0] and actual['cwd'] == job['cwd'] and actual['pid'] > 0 and
                int(actual['start_ticks']) > 0, 'Missing actual process identity/limits')
        executable = {'elaborate':'xelab', 'rtl':'xsimk', 'postcheck':'cosim.pc.exe'}[phase]
        require(Path(shlex.split(actual['command'])[0]).name == executable, 'Wrong actual process')
        if phase == 'rtl':
            require(re.search(r'RTL Simulation\s*:\s*4\s*/\s*4', text) is not None and
                    'COLLISION_SAFE_NATIVE_BOUNDED_RETURNED' in text, 'Incomplete RTL')
        if phase == 'postcheck':
            require('SEARCH_BATCH_PASS mode=1' in text and
                    'FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode=1 ports=44 transactions=4' in text, 'Original C oracle missing')
        bind(receipt_path); bind(actual_path)
    perf = OUT/'sim/verilog/search_batch_trace_top_v2.performance.result.transaction.xml'
    cycles = [tuple(map(int, x)) for x in re.findall(r'^transaction\s+(\d+):\s+(\d+)\s+(?:\d+|x)\s*$', perf.read_text(), re.M)]
    require([i for i, c in cycles] == list(range(4)) and all(c > 0 for i, c in cycles), 'Incomplete positive cycles')
    bind(perf)
    snapshots = []
    comparison = json.loads((OUT/'comparison.json').read_text())
    require(comparison['status'] == 'four_complete_RTL_snapshots_equal_original_C_reference', 'Missing comparison')
    for tx in range(4):
        actual = OUT/f'rtl_1_{tx}.bin'
        reference = BASE/'collision_safe_compact_cosim_setup_v1'/f'hls_1_{tx}.bin'
        original = BASE/'compressed_batch_rtl_tb_cpu_v2'/f'cpu_1_{tx}.bin'
        require(all(p.stat().st_size == 946498280 for p in [actual, reference, original]), 'Truncated full44 output')
        require(bind(actual) == bind(reference) == bind(original), 'Full RTL/C/original output mismatch')
        snapshots.append(dict(transaction=tx, actual=str(actual), reference=str(reference), bytes=946498280, sha256=files[str(actual)]))
    require(comparison['snapshots'] == snapshots, 'Comparison manifest differs')
    raw = list((OUT/'sim/tv/rtldatafile').glob('rtl.*.dat'))
    expected_raw = {p.name for p in (BASE/'compact_nonzero_native_rtl_v2/sim/tv/rtldatafile').glob('rtl.*.dat')}
    require(len(raw) == 25 and {p.name for p in raw} == expected_raw, 'Incomplete raw output collection')
    for p in raw: bind(p)
    for p in [OUT/'comparison.json', OUT/'state.json', OUT/'plan.json', OUT/'bounded.tcl', Path(__file__).resolve()]: bind(p)
    return dict(status='collision_safe_native_full4tx_full44_original_C_oracle_independently_verified',
                files=files, transactions=4, pointers=44, models=30, cycles=[c for i,c in cycles],
                snapshots=snapshots, pointer_address_offset=4096, rtl_verified=True,
                physical_timing_verified=False, board_verified=False,
                limits=['Full synthetic transactions only; no real routing traffic or platform claim.',
                        'Naming-only candidate is distinct from the preserved failed original RTL.',
                        'No physical capacity, clock closure, bandwidth, power or speedup acceptance.'])


if __name__ == '__main__':
    require(not REPORT.exists(), 'Refuse overwrite')
    result = audit()
    with REPORT.open('x') as stream:
        json.dump(result, stream, indent=2); stream.write('\n')
    print(result['status'])
