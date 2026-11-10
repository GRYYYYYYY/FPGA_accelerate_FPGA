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
from route_tree_routes_transform import routes, adapter, builder

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cpu', type=int, default=119)
    args = parser.parse_args()
    base = ROOT / 'data/derived/resident_snapshot_router_20261024_v1'
    pp = base / 'plan.json'; prior = json.loads(pp.read_text())
    for p, sha in prior['generated'].items():
        require(digest(p) == sha, 'Changed production CPU router input: ' + p)
    report_path = ROOT / 'results/resident_snapshot_component_20261024_v1.json'
    require(json.loads(report_path.read_text())['status'] == 'resident_snapshot_native_packet_and_full_search_differential_independently_verified',
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
    extra = [ROOT / 'hardware/vitis/search_route_tree.hpp', ROOT / 'hardware/vitis/search_route_tree_top.cpp',
             ROOT / 'src/native/route_tree_adapter.hpp', ROOT / 'tests/test_search_route_tree.cpp']
    for p in extra: shutil.copyfile(p, source / p.name)
    test = source / 'test_search_route_tree.cpp'
    for name, transform in [('site_routes.hpp', routes), ('search_kernel_route_adapter.hpp', adapter), ('resident_snapshot_adapter.hpp', builder)]:
        path = source / name; old = path.read_text(); new = transform(old); path.write_text(new)
        (out / (name + '.diff')).write_text(''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
            fromfile='original/' + name, tofile='bounded_occupancy/' + name)))
    shutil.copyfile(ROOT / 'src/native/site_routes.hpp', source / 'oracle_site_routes.hpp')
    test_routes = (source / 'site_routes.hpp').read_text().replace('namespace site_native {',
                   'namespace snapshot_test_native {\nusing namespace site_native;')
    (source / 'snapshot_test_routes.hpp').write_text(test_routes)
    driver = old_driver.read_text().replace(str(ROOT / 'src/native/site_routes.hpp'), 'oracle_site_routes.hpp')
    driver = driver.replace('KERNEL_ROUTE_RANDOM_PASS', 'ROUTE_TREE_ROUTE_RANDOM_PASS').replace(
                            'KERNEL_ROUTE_FULL_RESULTS_PASS', 'ROUTE_TREE_ROUTE_FULL_RESULTS_PASS')
    (source / 'driver.cpp').write_text(driver)
    (source / 'sites.txt').write_text('NATIVE_SITES_V1 16 4 4 0 0 0 0 1 1\n')
    inputs = [pp, report_path, cpu_path, component_path, old_driver, *objects, *extra,
              ROOT / 'src/native/site_routes.hpp', Path(__file__).resolve(),
              ROOT / 'scripts/route_tree_routes_transform.py', ROOT / 'scripts/check_vitis_kernel.py']
    inputs += list((base / 'source').iterdir())
    regular_objects = [ROOT / 'data/derived/complete_search_router_20261024_v1' / f'search_kernel_{mode}.o' for mode in ('csr', 'compact')]
    resident_objects = [base / 'resident_top.o', base / 'resident_top_regular.o']
    for p in resident_objects: require(digest(p) == json.loads((base / 'report.json').read_text())['artifacts'][str(p)], 'Changed resident object')
    inputs += regular_objects + resident_objects
    inputs += [Path(p) for inp in prior['inputs'].values() for p in inp.values()]
    inputs += [base / 'execution_plan.json']
    bindings = {str(p): digest(p) for p in inputs}
    generated = {str(p): digest(p) for p in source.iterdir()}
    plan = dict(files=bindings, generated=generated, inputs=prior['inputs'], references=prior['references'],
                prior_bundle=str(base), prior_audit=str(report_path), binary=str(out / 'router'),
                jobs=[dict(mode='csr', execution='kernel', cpu=116), dict(mode='compact', execution='kernel', cpu=117)],
                occupancy=dict(nodes=1048576, pairs=2097152, site_owners=65536, site_history=65536, site_requests=65536, packet_words=4194304),
                limitations=['CPU execution of bounded ownership/history helper and unchanged production search C model.',
                             'Current-tree roots and demands use bounded top, passed raw between search and snapshot. Outer scheduling, retained traces and final occupancy marshalling remain host work.',
                             'No HLS/RTL/physical/board proof for the new tree component yet.',
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
                env={**{k:v for k,v in os.environ.items() if k!='LD_PRELOAD'}, 'ASAN_OPTIONS': 'detect_leaks=1:halt_on_error=1', 'UBSAN_OPTIONS': 'halt_on_error=1'})
            state.update(child_pid=child.pid);update();code = child.wait()
        (out / (name + '.receipt.json')).write_text(json.dumps(dict(command=command, exit_code=code,
            log_sha256=digest(out / (name + '.log'))), indent=2) + '\n')
        require(code == 0, name + ' failed; log retained')
        print(name, 'PASS', flush=True)
    update()
    try:
        flags = ['g++', '-Wall', '-Wextra', '-Werror', '-Wno-unknown-pragmas', '-I' + str(source)]
        sanitizer = ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
        run('compile_top', [*flags, '-std=c++14', *sanitizer, '-c', source / 'search_route_tree_top.cpp', '-o', out / 'tree_top.o'])
        run('compile_component', [*flags, '-std=c++17', *sanitizer, test, out / 'tree_top.o', '-o', out / 'component_test'])
        run('component', [out / 'component_test'])
        require((out / 'component.log').read_text().endswith('route_tree_cpu PASS\n'), 'Missing complete component test')
        run('compile_differential', [*flags, '-std=c++17', *sanitizer, source / 'driver.cpp', out / 'tree_top.o', resident_objects[0], *objects, '-o', out / 'differential'])
        run('differential', [out / 'differential', source / 'sites.txt'])
        expected = ('ROUTE_TREE_ROUTE_RANDOM_PASS cases=400 modes=2 snapshots=3750 searches=4938 rounds=1250 '
                    'node_history_snapshots=2412 site_history_snapshots=2106 site_paths=2896 incomplete=190 routed=210\n'
                    'ROUTE_TREE_ROUTE_FULL_RESULTS_PASS\n')
        require((out / 'differential.log').read_text() == expected, 'Full negotiation differential coverage differs')
        run('compile_top_regular', [*flags, '-std=c++14', '-O2', '-c', source / 'search_route_tree_top.cpp', '-o', out / 'tree_top_regular.o'])
        run('compile_router', [*flags, '-std=c++17', '-O2', source / 'site_runtime.cpp', out / 'tree_top_regular.o', resident_objects[1], *regular_objects, '-o', out / 'router'])
        for p, sha in {**bindings, **generated}.items(): require(digest(p) == sha, 'Changed prepared input ' + p)
        artifacts = {str(p): digest(p) for p in out.rglob('*') if p.is_file() and p.name != 'prepare_state.json'}
        report = dict(status='route_tree_full_search_cpu_differential_verified_full_workload_pending',
                      files=bindings, artifacts=artifacts, cases=400, searches=4938,
                      new_component_random_paths=1000, new_component_failed_searches=1000, rejection_cases=21,
                      production_nodes=1048576, production_site_owners=65536, production_site_history=65536, maximum_packet_words=3850849,
                      hardware_executed=False, full_real_workload_executed=False, limitations=plan['limitations'])
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        state.update(status='complete', stage='component_and_full_search_differential_verified');update()
        print(report['status'], flush=True)
    except BaseException as error:
        state.update(status='failed', error=str(error));update();raise


if __name__ == '__main__': main()
