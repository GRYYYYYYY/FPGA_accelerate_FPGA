#!/usr/bin/env python3
"""Freeze/test bounded ownership within the complete production search C-model router."""
import argparse
import difflib
import json
import os
from pathlib import Path
import shutil
import subprocess

from check_vitis_kernel import digest, require
from node_occupancy_routes_transform import routes, adapter

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cpu', type=int, default=119)
    args = parser.parse_args()
    base = ROOT / 'data/derived/complete_search_router_20261024_v1'
    pp = base / 'plan.json'; prior = json.loads(pp.read_text())
    for p, sha in prior['generated'].items():
        require(digest(p) == sha, 'Changed production CPU router input: ' + p)
    report_path = ROOT / 'results/complete_search_router_audit_20261024_v1.json'
    require(json.loads(report_path.read_text())['status'] == 'two_full_router_kernel_conditions_independently_verified',
            'Missing complete reference experiment')
    cpu_path = ROOT / 'results/search_kernel_cpu_component_20261024_v3.json'
    cpu = json.loads(cpu_path.read_text())
    objects = [ROOT / f'data/derived/search_kernel_cpu_20261024_v3/search_kernel_{mode}.o' for mode in ('csr', 'compact')]
    for p in objects: require(digest(p) == cpu['artifacts'][str(p)], 'Changed production sanitizer object')
    old_driver = ROOT / 'data/derived/kernel_route_checks_20261024_v2/source/driver.cpp'
    component_path = ROOT / 'results/kernel_route_component_20261024_v1.json'
    component = json.loads(component_path.read_text())
    require(digest(old_driver) == component['artifacts'][str(old_driver)], 'Changed negotiated differential oracle')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    source = out / 'source'; shutil.copytree(base / 'source', source)
    extra = [ROOT / 'hardware/vitis/search_node_occupancy.hpp', ROOT / 'hardware/vitis/search_node_occupancy_top.cpp',
             ROOT / 'src/native/node_occupancy_adapter.hpp', ROOT / 'tests/test_search_node_occupancy.cpp',
             ROOT / 'tests/synthetic_search_image_v2.hpp']
    for p in extra: shutil.copyfile(p, source / p.name)
    test = source / 'test_search_node_occupancy.cpp'
    test.write_text(test.read_text().replace('../hardware/vitis/search_node_occupancy.hpp', 'search_node_occupancy.hpp'))
    for name, transform in [('site_routes.hpp', routes), ('search_kernel_route_adapter.hpp', adapter)]:
        path = source / name; old = path.read_text(); new = transform(old); path.write_text(new)
        (out / (name + '.diff')).write_text(''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
            fromfile='original/' + name, tofile='bounded_occupancy/' + name)))
    shutil.copyfile(ROOT / 'src/native/site_routes.hpp', source / 'oracle_site_routes.hpp')
    test_routes = (source / 'site_routes.hpp').read_text().replace('namespace site_native {',
                   'namespace snapshot_test_native {\nusing namespace site_native;')
    (source / 'snapshot_test_routes.hpp').write_text(test_routes)
    driver = old_driver.read_text().replace(str(ROOT / 'src/native/site_routes.hpp'), 'oracle_site_routes.hpp')
    driver = driver.replace('KERNEL_ROUTE_RANDOM_PASS', 'NODE_OCCUPANCY_ROUTE_RANDOM_PASS').replace(
                            'KERNEL_ROUTE_FULL_RESULTS_PASS', 'NODE_OCCUPANCY_ROUTE_FULL_RESULTS_PASS')
    (source / 'driver.cpp').write_text(driver)
    (source / 'sites.txt').write_text('NATIVE_SITES_V1 16 4 4 0 0 0 0 1 1\n')
    inputs = [pp, report_path, cpu_path, component_path, old_driver, *objects, *extra,
              ROOT / 'src/native/site_routes.hpp', Path(__file__).resolve(),
              ROOT / 'scripts/node_occupancy_routes_transform.py', ROOT / 'scripts/check_vitis_kernel.py']
    inputs += list((base / 'source').iterdir())
    regular_objects = [base / f'search_kernel_{mode}.o' for mode in ('csr', 'compact')]
    inputs += regular_objects
    bindings = {str(p): digest(p) for p in inputs}
    generated = {str(p): digest(p) for p in source.iterdir()}
    plan = dict(files=bindings, generated=generated, inputs=prior['inputs'], references=prior['references'],
                prior_bundle=str(base), prior_audit=str(report_path), binary=str(out / 'router'),
                jobs=[dict(mode='csr', execution='kernel', cpu=116), dict(mode='compact', execution='kernel', cpu=117)],
                occupancy=dict(nodes=1048576, pairs=2097152, state='distinct canonical node/net pairs plus uint64 history'),
                limitations=['CPU execution of bounded ownership/history helper and unchanged production search C model.',
                             'Site ownership, site history, outer scheduling and packet construction remain host work.',
                             'No RTL equivalence, synthesis, physical implementation or board result for the new component yet.',
                             'Full physical special-resource semantics remain incomplete.'])
    (out / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
    state = dict(owner_pid=os.getpid(), status='running', stage='prepare')
    def update():
        temp = out / 'prepare_state.tmp'; temp.write_text(json.dumps(state, indent=2) + '\n');temp.replace(out / 'prepare_state.json')
    def run(name, command):
        command = ['taskset', '-c', str(args.cpu), *map(str, command)]
        state.update(stage=name); update()
        with (out / (name + '.log')).open('x') as log:
            child = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                env={**os.environ, 'ASAN_OPTIONS': 'detect_leaks=1:halt_on_error=1', 'UBSAN_OPTIONS': 'halt_on_error=1'})
            state.update(child_pid=child.pid);update();code = child.wait()
        (out / (name + '.receipt.json')).write_text(json.dumps(dict(command=command, exit_code=code,
            log_sha256=digest(out / (name + '.log'))), indent=2) + '\n')
        require(code == 0, name + ' failed; log retained')
        print(name, 'PASS', flush=True)
    update()
    try:
        flags = ['g++', '-Wall', '-Wextra', '-Werror', '-Wno-unknown-pragmas', '-I' + str(source)]
        sanitizer = ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
        run('compile_component', [*flags, '-std=c++14', *sanitizer, test, source / 'search_node_occupancy_top.cpp', '-o', out / 'component_test'])
        run('component', [out / 'component_test'])
        require((out / 'component.log').read_text().endswith('NODE_OCCUPANCY_ALL_PASS\n'), 'Missing complete component test')
        run('compile_differential', [*flags, '-std=c++17', *sanitizer, source / 'driver.cpp', *objects, '-o', out / 'differential'])
        run('differential', [out / 'differential', source / 'sites.txt'])
        expected = ('NODE_OCCUPANCY_ROUTE_RANDOM_PASS cases=400 modes=2 snapshots=3750 searches=4938 rounds=1250 '
                    'node_history_snapshots=2412 site_history_snapshots=2106 site_paths=2896 incomplete=190 routed=210\n'
                    'NODE_OCCUPANCY_ROUTE_FULL_RESULTS_PASS\n')
        require((out / 'differential.log').read_text() == expected, 'Full negotiation differential coverage differs')
        run('compile_router', [*flags, '-std=c++17', '-O2', source / 'site_runtime.cpp', *regular_objects, '-o', out / 'router'])
        for p, sha in {**bindings, **generated}.items(): require(digest(p) == sha, 'Changed prepared input ' + p)
        artifacts = {str(p): digest(p) for p in out.rglob('*') if p.is_file() and p.name != 'prepare_state.json'}
        report = dict(status='bounded_node_occupancy_full_search_cpu_differential_verified_full_workload_pending',
                      files=bindings, artifacts=artifacts, cases=400, searches=4938,
                      new_component_random_operations=12000, production_nodes=1048576, production_peak_pairs=1048578,
                      hardware_executed=False, full_real_workload_executed=False, limitations=plan['limitations'])
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        state.update(status='complete', stage='component_and_full_search_differential_verified');update()
        print(report['status'], flush=True)
    except BaseException as error:
        state.update(status='failed', error=str(error));update();raise


if __name__ == '__main__': main()
