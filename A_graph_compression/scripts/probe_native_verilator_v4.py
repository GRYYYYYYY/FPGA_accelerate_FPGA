#!/usr/bin/env python3
"""Experimental four-state compatibility probe; never functional acceptance.

Uses a separate output directory and keeps the original XSim process untouched.
"""
import argparse
import json
import os
from pathlib import Path
import resource
import shlex
import signal
import subprocess
import time

from check_vitis_kernel import digest, require
from owned_sim_resource_policy_v1 import observe, abort_reason
from run_compact_native_stack_recovery_v3 import atomic
from run_compact_nonzero_native_rtl_v2 import stop
from run_recovered_native_rtl_v2 import OUT as LIVE


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tool-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--sources', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    require(not out.exists(), 'Refuse existing probe output')
    tool_root = args.tool_root.resolve()
    binary = tool_root/'verilator/bin/verilator_bin'
    require(binary.is_file(), 'Verilator binary missing')
    initial = observe()
    original = json.loads((LIVE/'plan.json').read_text())
    require((original['transactions'], original['pointers'], original['models']) == (4, 44, 30), 'Changed scope')
    rtl = LIVE/'sim/verilog'
    project = rtl/'search_batch_trace_top_v2.prj'
    sources = []
    for line in project.read_text().splitlines():
        if not line.strip():
            continue
        row = shlex.split(line)
        require(len(row) == 3 and row[0] == 'sv', 'Unsupported source-list record')
        path = (rtl/row[2]).resolve()
        require(path.is_relative_to(rtl), 'Source outside frozen directory')
        require(str(path) in original['preserved_inputs'], 'Unbound source '+str(path))
        require(digest(path) == original['preserved_inputs'][str(path)], 'Changed source '+str(path))
        sources.append(path)
    require(len(sources) == 154 and len(set(sources)) == 154, 'Incomplete source list')
    from normalize_native_fsm_literals_v1 import normalize
    from lower_native_memory_initializers_v1 import lower
    import sys
    sys.set_int_max_str_digits(100000)
    normalization = args.sources.resolve()/'report.json'
    report = json.loads(normalization.read_text())
    require(report['status'] == 'full154_sources_30_models_4pages_static_initializer_candidate_not_accepted', 'Wrong candidate report')
    hex_report_path = Path(report['source_report'])
    require(digest(hex_report_path) == report['source_report_sha256'], 'Changed numeric source report')
    hex_report = json.loads(hex_report_path.read_text())
    require(len(report['files']) == len(hex_report['files']) == 154, 'Incomplete candidate')
    originals = list(sources)
    require([r['source'] for r in hex_report['files']] == list(map(str, originals)), 'Original source set differs')
    sources = []
    for original, hex_row, row in zip(originals, hex_report['files'], report['files']):
        dst = args.sources.resolve()/original.name
        require(row['destination'] == str(dst) and row['source'] == hex_row['destination'], 'Candidate chain differs')
        require(digest(original) == hex_row['original_sha256'], 'Original changed')
        expected, count = normalize(original.read_bytes())
        require(count == hex_row['constants'], 'Wrong constant count')
        if original.name.startswith('AESL_axi_master_'):
            expected = lower(expected.decode(), original.stem.removeprefix('AESL_axi_master_'))[0].encode()
        require(dst.read_bytes() == expected and digest(dst) == row['sha256'], 'Unexpected model or DUT change')
        sources.append(dst)
    contract = Path(__file__).resolve().parents[1]/'data/derived/native_memory_initializer_contract_20261103_v1'
    unit = json.loads((contract/'report.json').read_text())
    require(unit['status'] == 'six_four_state_initializer_contract_cases_passed_not_full_rtl', 'Missing four-state initializer test')
    for name, checksum in unit['files'].items():
        require(digest(name) == checksum, 'Changed initializer test input')
    for receipt in unit['receipts']:
        require(receipt['exit_code'] == 0 and receipt['reason'] is None, 'Initializer test failed')
        require(digest(contract/(receipt['phase']+'.log')) == receipt['log_sha256'], 'Initializer test log changed')
    require((contract/'simulate.log').read_text().count('INITIALIZER_FOUR_STATE_CONTRACT_PASS cases=6 pages=4') == 1, 'Initializer test not complete')
    out.mkdir(parents=True)
    source_list = out/'sources.f'
    source_list.write_text(''.join('"'+str(p)+'"\n' for p in sources))
    command = ['prlimit', '--as=68719476736:68719476736',
               '--stack=268435456:268435456', '--core=0:0', '--',
               str(binary), '--lint-only', '--fourstate', '--timing', '--assert', '-Wno-fatal',
               '--top-module', 'apatb_search_batch_trace_top_v2_top',
               '--Mdir', str(out/'obj'), '-I'+str(rtl), '-f', str(source_list)]
    env = {**os.environ, 'VERILATOR_ROOT': str(tool_root/'verilator')}
    files = {str(p): digest(p) for p in originals + sources + [normalization, hex_report_path, contract/'report.json', contract/'simulate.log', Path(__file__).with_name('lower_native_memory_initializers_v1.py'), Path(__file__).with_name('normalize_native_fsm_literals_v1.py'), project, source_list, binary,
             LIVE/'plan.json', Path(__file__).resolve()]}
    atomic(out/'plan.json', dict(command=command, cwd=str(rtl), files=files,
           scope=dict(transactions=4, pointers=44, models=30, sources=len(sources)),
           initial_memory=initial, timeout_seconds=900, functional_acceptance=False,
           limitations=['Experimental four-state implementation requires independent XSim comparison; no acceptance inferred.',
                        'Lint/compatibility only; no RTL execution or equivalence proof.']))
    state = dict(owner_pid=os.getpid(), status='running', stage='full_source_lint',
                 functional_acceptance=False, live_xsim_modified=False)
    atomic(out/'state.json', state)
    child = None
    def interrupted(signum, frame):
        raise SystemExit(128+signum)
    signal.signal(signal.SIGTERM, interrupted)
    started = time.monotonic()
    reason = None
    try:
        require(abort_reason(initial, observe()) is None, 'OOM before launch')
        with (out/'lint.log').open('x') as log:
            child = subprocess.Popen(command, cwd=rtl, env=env, stdout=log,
                                     stderr=subprocess.STDOUT, start_new_session=True)
            state['child_pid'] = child.pid
            atomic(out/'state.json', state)
            proc = Path('/proc')/str(child.pid)
            identity = dict(pid=child.pid, start_ticks=(proc/'stat').read_text().rsplit(')', 1)[1].split()[19])
            atomic(out/'child.json', identity)
            actual = None
            while child.poll() is None:
                if actual is None:
                    limits = {name: list(resource.prlimit(child.pid, kind)) for name, kind in
                              [('as', resource.RLIMIT_AS), ('stack', resource.RLIMIT_STACK), ('core', resource.RLIMIT_CORE)]}
                    if limits == {'as': [64*1024**3]*2, 'stack': [256*1024**2]*2, 'core': [0, 0]}:
                        actual = dict(identity, limits=limits, command=(proc/'cmdline').read_bytes().replace(b'\0', b' ').decode())
                        atomic(out/'actual_limits.json', actual)
                reason = abort_reason(initial, observe())
                if time.monotonic()-started > 900:
                    reason = reason or 'diagnostic_wall_timeout'
                if reason:
                    stop(child)
                    break
                time.sleep(1)
            code = child.wait()
            child = None
        reason = reason or abort_reason(initial, observe())
        for name, checksum in files.items():
            require(digest(name) == checksum, 'Probe input changed '+name)
        atomic(out/'receipt.json', dict(exit_code=code, abort_reason=reason,
               elapsed_seconds=time.monotonic()-started, log_sha256=digest(out/'lint.log'),
               actual_limits=actual, functional_acceptance=False))
        state.update(status='complete' if code == 0 and reason is None else 'failed',
                     stage='compatibility_probe_finished', exit_code=code, abort_reason=reason)
        atomic(out/'state.json', state)
    except BaseException as exc:
        state.update(status='failed', error=str(exc))
        atomic(out/'state.json', state)
        raise
    finally:
        if child is not None:
            stop(child)


if __name__ == '__main__':
    main()
