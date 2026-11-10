"""Compile a separate full-search XRT router and test its resident CPU protocol."""
import argparse
import difflib
import json
import os
from pathlib import Path
import shutil
import subprocess

from check_vitis_kernel import digest, require
from derive_search_flat_controller import replace_once as one
from search_xrt_routes_transform import binding, adapter, runtime

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cpu', type=int, default=119)
    args = parser.parse_args()
    prior = ROOT / 'data/derived/complete_search_router_20261024_v1'
    plan_path = prior / 'plan.json'
    plan = json.loads(plan_path.read_text())
    for path, sha in plan['generated'].items():
        require(digest(path) == sha, 'frozen CPU router changed: ' + path)
    host_proof = ROOT / 'results/search_xrt_interface_20261024_v1.json'
    proof = json.loads(host_proof.read_text())
    require(proof['status'] == 'full_search_xrt_host_interface_compiled_and_cpu_protocol_verified_board_pending', 'missing host protocol proof')
    for path, sha in {**proof['inputs'], **proof['artifacts']}.items():
        require(digest(path) == sha, 'changed host interface proof: ' + path)
    old_test = ROOT / 'data/derived/kernel_route_checks_20261024_v2/source/driver.cpp'
    negotiation_proof = ROOT / 'results/kernel_route_component_20261024_v1.json'
    negotiation = json.loads(negotiation_proof.read_text())
    require(digest(old_test) == negotiation['artifacts'][str(old_test)], 'changed differential driver')
    cpu_proof = ROOT / 'results/search_kernel_cpu_component_20261024_v3.json'
    cpu = json.loads(cpu_proof.read_text())
    objects = [ROOT / f'data/derived/search_kernel_cpu_20261024_v3/search_kernel_{m}.o' for m in ('csr', 'compact')]
    for path in objects:
        require(digest(path) == cpu['artifacts'][str(path)], 'changed production C-model object')
    out = args.output.resolve();out.mkdir(parents=True, exist_ok=False)
    source = out / 'source';shutil.copytree(prior / 'source', source)
    dependencies = [plan_path, host_proof, negotiation_proof, cpu_proof, old_test, *objects,
                    Path(__file__).resolve(), ROOT / 'scripts/search_xrt_routes_transform.py',
                    ROOT / 'hardware/vitis/search_xrt_runtime.hpp', ROOT / 'tests/test_search_xrt_exchange.cpp',
                    ROOT / 'tests/synthetic_search_image_v2.hpp', ROOT / 'src/native/site_routes.hpp']
    dependencies += list((prior / 'source').iterdir())
    dependencies += list((ROOT / 'hardware/vitis/search_xrt_v1').iterdir())
    for name, transform in [('search_kernel_binding.hpp', binding), ('search_kernel_route_adapter.hpp', adapter), ('site_runtime.cpp', runtime)]:
        path = source / name;old = path.read_text();new = transform(old);path.write_text(new)
        (out / (name + '.diff')).write_text(''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile='cpu/' + name, tofile='xrt/' + name)))
    shutil.copytree(ROOT / 'hardware/vitis/search_xrt_v1', source / 'search_xrt_v1')
    shutil.copyfile(ROOT / 'hardware/vitis/search_xrt_runtime.hpp', source / 'search_xrt_runtime.hpp')
    shutil.copyfile(ROOT / 'src/native/site_routes.hpp', source / 'oracle_site_routes.hpp')
    shutil.copyfile(ROOT / 'tests/synthetic_search_image_v2.hpp', source / 'synthetic_search_image_v2.hpp')
    test_routes = (source / 'site_routes.hpp').read_text().replace('namespace site_native {', 'namespace snapshot_test_native {\nusing namespace site_native;')
    (source / 'snapshot_test_routes.hpp').write_text(test_routes)
    test_source = (ROOT / 'tests/test_search_xrt_exchange.cpp').read_text()
    cpu_backend = test_source[test_source.index('struct CpuBackend {'):test_source.index('struct FaultBackend {')]
    prototypes = '\n'.join(line for line in test_source.splitlines() if line.startswith('extern "C" void search_kernel_'))
    (source / 'resident_cpu_backend.hpp').write_text('#pragma once\n#include <cstring>\n#include <memory>\n' + prototypes + '\nusing namespace search_xrt;\n' + cpu_backend)
    driver = one(old_test.read_text(), '#include "' + str(ROOT / 'src/native/site_routes.hpp') + '"', '#include "oracle_site_routes.hpp"')
    driver = one(driver, '#include "synthetic_search_image_v2.hpp"', '#include "synthetic_search_image_v2.hpp"\n#include "resident_cpu_backend.hpp"')
    anchor = 'SyntheticSearchImage image(graph.rows,graph.unknown,sites.attributes,mode);kernel_route::ImageScope scope(image.view());'
    driver = one(driver, anchor, anchor + '''
        static CpuBackend backend(0);backend.mode=mode;
        search_xrt::Session<CpuBackend> session(backend,image.image.data(),unsigned(image.image.size()),image.config.data());
        kernel_route::ExchangeScope exchange_scope([&](const uint32_t* roots,size_t count,const uint64_t* packet,size_t words){return session.search(roots,count,packet,words);});''')
    driver = one(driver, 'assert(kernel_route::kernel_counters.calls==expected_searches && kernel_route::kernel_counters.packets==c.snapshots);',
                 'assert(kernel_route::kernel_counters.calls==expected_searches && kernel_route::kernel_counters.packets==c.snapshots);\n        assert(session.stats().completed==expected_searches && !session.failed());')
    driver = driver.replace('KERNEL_ROUTE_RANDOM_PASS', 'RESIDENT_ROUTE_RANDOM_PASS').replace('KERNEL_ROUTE_FULL_RESULTS_PASS', 'RESIDENT_ROUTE_FULL_RESULTS_PASS hardware_executed=false')
    (source / 'resident_driver.cpp').write_text(driver)
    (source / 'sites.txt').write_text('NATIVE_SITES_V1 16 4 4 0 0 0 0 1 1\n')
    inputs = {str(path): digest(path) for path in dependencies}
    generated = {str(path): digest(path) for path in source.rglob('*') if path.is_file()}
    (out / 'plan.json').write_text(json.dumps(dict(inputs=inputs, generated=generated, real_inputs=plan['inputs'], cpu=args.cpu), indent=2) + '\n')
    def state(status, stage):
        (out / 'state.json').write_text(json.dumps(dict(owner_pid=os.getpid(), status=status, stage=stage), indent=2) + '\n')
    def run(name, command):
        state('running', name)
        with (out / (name + '.log')).open('x') as log:
            result = subprocess.run(['taskset', '-c', str(args.cpu), *map(str, command)], stdout=log, stderr=subprocess.STDOUT,
                                    env={**os.environ, 'ASAN_OPTIONS': 'detect_leaks=1:halt_on_error=1', 'UBSAN_OPTIONS': 'halt_on_error=1'})
        (out / (name + '.receipt.json')).write_text(json.dumps(dict(command=list(map(str, command)), exit_code=result.returncode,
                                                                  log_sha256=digest(out / (name + '.log'))), indent=2) + '\n')
        if result.returncode:
            state('failed', name);raise RuntimeError(name + ' failed; original log preserved')
        print(name, 'PASS', flush=True)
    flags = ['g++', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-Wno-unknown-pragmas', '-I' + str(source)]
    binary = out / 'router_xrt'
    run('compile_xrt', [*flags, '-O2', '-I/opt/xilinx/xrt/include', source / 'site_runtime.cpp', '-L/opt/xilinx/xrt/lib',
                        '-Wl,-rpath,/opt/xilinx/xrt/lib', '-lxrt_coreutil', '-luuid', '-pthread', '-o', binary])
    run('symbols', ['nm', '-C', binary])
    require('search_kernel_csr' not in (out / 'symbols.log').read_text() and 'search_kernel_compact' not in (out / 'symbols.log').read_text(), 'C-model fallback linked into board executable')
    for mode in ('csr', 'compact'):
        inp = plan['inputs'][mode]
        run(mode + '_preflight', [binary, '--preflight', inp['image'], inp['config'], mode])
        require((out / (mode + '_preflight.log')).read_text() == 'FULL_SEARCH_XRT_IMAGE_PASS hardware_executed=false\n', 'wrong preflight output')
    run('compile_differential', [*flags, '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                               source / 'resident_driver.cpp', *objects, '-o', out / 'resident_check'])
    run('differential', [out / 'resident_check', source / 'sites.txt'])
    text = (out / 'differential.log').read_text()
    require(text == 'RESIDENT_ROUTE_RANDOM_PASS cases=400 modes=2 snapshots=3750 searches=4938 rounds=1250 node_history_snapshots=2412 site_history_snapshots=2106 site_paths=2896 incomplete=190 routed=210\nRESIDENT_ROUTE_FULL_RESULTS_PASS hardware_executed=false\n', 'differential coverage differs')
    for path, sha in {**inputs, **generated}.items():
        require(digest(path) == sha, 'input changed during compilation/test: ' + path)
    artifacts = {str(path): digest(path) for path in out.rglob('*') if path.is_file() and path.name != 'state.json'}
    report = dict(status='full_search_xrt_router_compiled_resident_negotiation_cpu_verified_board_pending',
                  bundle=str(out), binary=str(binary), inputs=inputs, artifacts=artifacts, cases=400, searches=4938,
                  hardware_executed=False, full_real_workload_executed=False,
                  limitations=['CPU session backend differential; no XRT device opened during preparation.',
                               'Hardware-only executable links no production C-model search symbols; requires audited xclbin launch evidence.',
                               'Outer snapshots, negotiation and dynamic occupancy remain on CPU.',
                               'Physical site semantics still limited to 14 evidenced instances.'])
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    state('complete', 'compiled_and_resident_negotiation_cpu_verified')
    print(report['status'], out, flush=True)


if __name__ == '__main__':
    main()
