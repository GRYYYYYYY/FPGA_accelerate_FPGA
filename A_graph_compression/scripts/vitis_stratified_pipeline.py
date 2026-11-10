#!/usr/bin/env python3
"""Own private HLS cosimulation copies and automatically audit their terminal outputs."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from check_vitis_kernel import digest, require, validate_case_log
from check_vitis_stratified import check_fixtures

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'data/derived/vitis_stratified_cosim_20261023_v1'
FIXTURE = ROOT/'data/derived/vitis_stratified_fixtures_20261023_v1'
HLS = Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls')


def save(path, data):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2)+'\n')
    temporary.replace(path)


def run(mode, cpu):
    source = ROOT/'data/derived/vitis_graph_kernel_20261023_v2'/mode
    work = OUT/mode
    work.mkdir()
    target = ROOT/'build'/f'vitis_graph_{mode}_stratified_20261023_v1'
    state_path = OUT/(mode+'.state.json')
    state = {'owner_pid': os.getpid(), 'mode': mode, 'cpu': cpu, 'status': 'running', 'stage': 'cpu_golden'}
    save(state_path, state)
    try:
        binary = work/'cpu_test'
        command = ['g++', '-std=c++14', '-O2', '-Wno-unknown-pragmas',
                   *[str(source/name) for name in ['graph_body.cpp', 'graph_accel.cpp', 'test_graph_expand.cpp']],
                   '-o', str(binary)]
        with (work/'compile.log').open('x') as stream:
            subprocess.run(['taskset', '-c', str(cpu), *command], stdout=stream, stderr=subprocess.STDOUT, check=True)
        manifest = FIXTURE/mode/'rtl.txt'
        with (work/'cpu.log').open('x') as stream:
            subprocess.run(['taskset', '-c', str(cpu), str(binary), str(manifest)], stdout=stream,
                           stderr=subprocess.STDOUT, check=True)
        validate_case_log((work/'cpu.log').read_text(), manifest, 1)
        original = ROOT/'build'/f'vitis_graph_{mode}_20261023_v2'
        # New regular files, no hard links; stale simulation/export products are excluded.
        shutil.copytree(original, target, ignore=shutil.ignore_patterns('sim', 'csim', 'impl'))
        save(work/'copied_project.json', {'original': str(original), 'copy': str(target),
             'initial_files': {str(p.relative_to(target)): digest(p) for p in target.rglob('*') if p.is_file()}})
        env = os.environ.copy()
        env.update(A_STRATIFIED_PROJECT=str(target), A_STRATIFIED_MANIFEST=str(manifest),
                   LD_PRELOAD='/lib/x86_64-linux-gnu/libudev.so.1')
        command = ['taskset', '-c', str(cpu), str(HLS), '-f', str(ROOT/'hardware/vitis/run_stratified_cosim.tcl')]
        log = work/'cosim.log'
        with log.open('x') as stream:
            child = subprocess.Popen(command, cwd=work, env=env, stdout=stream, stderr=subprocess.STDOUT)
            state.update(stage='cosimulation', child_pid=child.pid, command=command)
            save(state_path, state)
            code = child.wait()
        save(work/'receipt.json', {'exit_code': code, 'log_sha256': digest(log), 'command': command})
        state.pop('child_pid', None)
        require(code == 0 and 'VITIS_STRATIFIED_COSIM_COMPLETE' in log.read_text(), 'Cosimulation failed')
        state.update(status='complete', stage='await_independent_audit')
        save(state_path, state)
        return mode
    except BaseException as exc:
        state.update(status='failed', error=str(exc)); save(state_path, state)
        raise


def main():
    require({122, 123} <= os.sched_getaffinity(0), 'Build CPUs unavailable')
    check_fixtures(FIXTURE)
    baseline = ROOT/'results/vitis_graph_kernel_audit_20261023_v2.json'
    audited = json.loads(baseline.read_text())
    source_plan = ROOT/'data/derived/vitis_graph_kernel_20261023_v2/plan.json'
    source = json.loads(source_plan.read_text())
    files = {**audited['artifacts'], **source['files'], **source['generated']}
    for path, sha in files.items():
        require(digest(path) == sha, 'Original baseline changed: '+path)
    dependencies = [Path(__file__).resolve(), baseline, source_plan, FIXTURE/'plan.json',
                    ROOT/'scripts/check_vitis_stratified.py', ROOT/'scripts/prepare_vitis_stratified.py',
                    ROOT/'scripts/check_vitis_kernel.py', ROOT/'hardware/vitis/run_stratified_cosim.tcl',
                    ROOT/'tests/test_vitis_stratified.py', ROOT/'results/regression_vitis_stratified_20261023_v1.log']
    files.update({str(p): digest(p) for p in dependencies})
    OUT.mkdir(parents=True, exist_ok=False)
    save(OUT/'plan.json', {'created_utc': datetime.now(timezone.utc).isoformat(), 'files': files,
         'fixtures': str(FIXTURE), 'cpu_bindings': [122, 123],
         'projects': {mode: str(ROOT/'build'/f'vitis_graph_{mode}_stratified_20261023_v1') for mode in ['csr','compact']},
         'scope': 'Additional matched degree-stratified cosimulation of unchanged audited RTL, private regular-file copies.'})
    state_path = OUT/'pipeline.json'
    state = {'owner_pid': os.getpid(), 'status': 'running', 'stage': 'cosimulation', 'completed_modes': []}
    save(state_path, state)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            for future in as_completed([pool.submit(run, mode, cpu) for mode,cpu in [('csr',122),('compact',123)]]):
                state['completed_modes'].append(future.result()); save(state_path, state)
        for path, sha in files.items():
            require(digest(path) == sha, 'Frozen baseline changed during private cosimulation')
        state.update(status='complete', stage='await_independent_audit'); save(state_path, state)
        output = ROOT/'results/vitis_stratified_audit_20261023_v1.json'
        with (OUT/'audit.log').open('x') as stream:
            child = subprocess.run([sys.executable, str(ROOT/'scripts/check_vitis_stratified.py'),
                                    '--bundle', str(OUT), '--output', str(output)],
                                   stdout=stream, stderr=subprocess.STDOUT)
        require(child.returncode == 0, 'Independent audit failed; inspect audit.log')
        # Separate terminal receipt preserves the pipeline snapshot bound by the audit.
        save(OUT/'audit_receipt.json', {'exit_code': child.returncode, 'output': str(output),
             'report_sha256': digest(output), 'log_sha256': digest(OUT/'audit.log')})
    except BaseException as exc:
        state.update(status='failed', error=str(exc)); save(state_path, state)
        raise


if __name__ == '__main__':
    main()
