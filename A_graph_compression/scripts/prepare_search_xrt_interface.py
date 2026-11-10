"""Freeze and compile the full-search host interface; verify CPU protocol only."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

from check_search_kernel_memory_plan import check as check_memory

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cpu', type=int, default=119)
    args = parser.parse_args()
    assert args.cpu in os.sched_getaffinity(0), 'CPU unavailable'
    memory_path = ROOT / 'hardware/vitis/search_kernel_memory_v1/plan.json'
    memory_proof = check_memory(memory_path)
    memory = json.loads(memory_path.read_text())
    cpu_path = ROOT / 'results/search_kernel_cpu_component_20261024_v3.json'
    cpu = json.loads(cpu_path.read_text())
    assert cpu['status'] == 'complete_search_top_cpu_real_probes_and_packet_abi_verified'
    objects = [ROOT / f'data/derived/search_kernel_cpu_20261024_v3/search_kernel_{m}.o'
               for m in ('csr', 'compact')]
    for path in objects:
        assert digest(path) == cpu['artifacts'][str(path)], 'production object changed'
    top = ROOT / 'hardware/vitis/search_xrt_v1'
    expected = [(a['name'], a['port'], a.get('payload_bytes', 0),
                 memory['abi']['csr'][a['id']]['control_offset'],
                 memory['abi']['csr'][a['id']]['host_size']) for a in memory['arguments']]
    actual = [(name, port, int(size), int(offset), int(host_size)) for name, port, size, offset, host_size in
              re.findall(r'\{"(\w+)","(\w+)",(\d+),(\d+),(\d+)\}', (top / 'abi.hpp').read_text())]
    assert actual == expected, 'generated host ABI differs from checked source/XML'
    assert json.loads((top / 'abi_source.json').read_text())['source_plan_sha256'] == memory_proof['plan_sha256']
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    source = out / 'source'
    sources = list(top.iterdir()) + [ROOT / 'hardware/vitis/host_contract.hpp']
    sources += list((ROOT / 'hardware/vitis/search_kernel_offsets_v3').iterdir())
    sources += [ROOT / 'tests' / name for name in ('test_search_xrt_exchange.cpp', 'test_search_xrt_topology.cpp',
                                                 'test_search_xrt_compile.cpp', 'search_xrt_fixture_v1.hpp')]
    for path in sources:
        target = source / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    dependencies = [*sources, *objects, cpu_path, memory_path, Path(__file__).resolve(),
                    ROOT / 'scripts/check_search_kernel_memory_plan.py', ROOT / 'scripts/search_kernel_memory_plan.py',
                    Path('/opt/xilinx/xrt/lib/libxrt_coreutil.so').resolve()]
    dependencies += [Path('/opt/xilinx/xrt/include') / n for n in (
        'xclbin.h', 'xrt/xrt_kernel.h', 'xrt/xrt_bo.h', 'xrt/xrt_device.h', 'experimental/xrt_xclbin.h')]
    inputs = {str(path): digest(path) for path in dependencies}
    state_path = out / 'state.json'
    def state(status, stage):
        state_path.write_text(json.dumps(dict(status=status, stage=stage, owner_pid=os.getpid()), indent=2) + '\n')
    def run(name, command):
        state('running', name)
        start = datetime.now(timezone.utc).isoformat()
        with (out / (name + '.log')).open('x') as log:
            result = subprocess.run(['taskset', '-c', str(args.cpu), *map(str, command)], stdout=log,
                                    stderr=subprocess.STDOUT,
                                    env={**os.environ, 'ASAN_OPTIONS': 'detect_leaks=1:halt_on_error=1',
                                         'UBSAN_OPTIONS': 'halt_on_error=1'})
        receipt = dict(command=list(map(str, command)), cpu=args.cpu, start=start,
                       end=datetime.now(timezone.utc).isoformat(), returncode=result.returncode,
                       log_sha256=digest(out / (name + '.log')))
        (out / (name + '.receipt.json')).write_text(json.dumps(receipt, indent=2) + '\n')
        if result.returncode:
            state('failed', name)
            raise RuntimeError(f'{name} failed; original log retained at {out}')
        print(name, 'PASS', flush=True)
    flags = ['g++', '-std=c++17', '-Wall', '-Wextra', '-Werror']
    sanitize = ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    include = '-I' + str(source / 'hardware/vitis/search_kernel_offsets_v3')
    testdir = source / 'tests'
    run('compile_exchange', [*flags, *sanitize, '-Wno-unknown-pragmas', include,
                             testdir / 'test_search_xrt_exchange.cpp', *objects, '-o', out / 'exchange'])
    run('exchange', [out / 'exchange'])
    run('compile_topology', [*flags, *sanitize, '-I/opt/xilinx/xrt/include',
                            testdir / 'test_search_xrt_topology.cpp', '-o', out / 'topology'])
    run('topology', [out / 'topology'])
    run('compile_xrt', [*flags, '-O2', '-I/opt/xilinx/xrt/include', testdir / 'test_search_xrt_compile.cpp',
                       '-L/opt/xilinx/xrt/lib', '-Wl,-rpath,/opt/xilinx/xrt/lib', '-lxrt_coreutil',
                       '-luuid', '-pthread', '-o', out / 'xrt_link'])
    run('xrt_link', [out / 'xrt_link'])
    exchange = (out / 'exchange.log').read_text()
    assert exchange == ''.join(f'RESIDENT_CMODEL_PASS mode={mode} transactions=11 full_state=32,16,8 full_workspace=1 hardware_executed=false\n'
                               for mode in (0, 1)) + 'SEARCH_EXCHANGE_ALL_PASS production_transactions=22 transport_faults=12 host_preflight_recovery=1 hardware_executed=false\n'
    assert (out / 'topology.log').read_text() == 'SEARCH_TOPOLOGY_PASS layouts=3 corruptions=16 truncations=4 group_ids_distinct_from_physical=1 hardware_executed=false\n'
    assert (out / 'xrt_link.log').read_text() == 'SEARCH_XRT_LINK_PASS hardware_executed=false\n'
    for path, sha in inputs.items():
        assert digest(path) == sha, 'input changed during verification'
    artifacts = {str(path): digest(path) for path in sorted(out.rglob('*')) if path.is_file() and path != state_path}
    report = dict(status='full_search_xrt_host_interface_compiled_and_cpu_protocol_verified_board_pending',
                  inputs=inputs, artifacts=artifacts, memory_plan_sha256=memory_proof['plan_sha256'],
                  production_transactions=22, transport_faults_rejected=12, topology_layouts=3,
                  topology_corruptions_rejected=16, topology_truncations_rejected=4,
                  hardware_executed=False, xrt_library='2.14.354',
                  limitations=['Standalone host interface; not yet integrated into the full negotiated router.',
                               'No real xclbin has exercised group topology parsing, allocation or kernel launch.',
                               'Caller must bind CSR/compact xclbin hash to an audited build report; XML ABI alone cannot distinguish modes.',
                               'CPU C-model fixtures and synthetic malformed topologies are not board execution or throughput evidence.',
                               'Host sync byte counters measure submitted spans, not physical PCIe/HBM traffic.'])
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    state('complete', 'compiled_and_cpu_protocol_verified_board_pending')
    print(report['status'], out, flush=True)


if __name__ == '__main__':
    main()
