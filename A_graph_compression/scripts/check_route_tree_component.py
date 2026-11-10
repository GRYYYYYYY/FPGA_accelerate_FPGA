#!/usr/bin/env python3
"""Independently bind native-oracle component and complete-search differential evidence."""
import argparse
import json
from pathlib import Path
from check_vitis_kernel import digest, require
from route_tree_routes_transform import routes, adapter, builder


def audit(bundle, output):
    require(not output.exists(), 'Refusing to overwrite component audit')
    root = Path(__file__).resolve().parents[1]
    state_path = bundle / 'prepare_state.json'
    require(json.loads(state_path.read_text())['status'] == 'complete', 'Preparation incomplete')
    report_path = bundle / 'report.json';report = json.loads(report_path.read_text())
    require(report['status'] == 'route_tree_full_search_cpu_differential_verified_full_workload_pending',
            'Wrong preparation status')
    for p, sha in {**report['files'], **report['artifacts']}.items():
        require(digest(p) == sha, 'Changed prepared dependency ' + p)
    plan_path = bundle / 'plan.json';plan = json.loads(plan_path.read_text())
    require(plan['occupancy'] == dict(nodes=1048576, pairs=2097152, site_owners=65536,
                                    site_history=65536, site_requests=65536, packet_words=4194304), 'Changed production capacity')
    prior = Path(plan['prior_bundle']);source = bundle / 'source'
    for name, transform in [('site_routes.hpp', routes), ('search_kernel_route_adapter.hpp', adapter), ('resident_snapshot_adapter.hpp', builder)]:
        require((source / name).read_text() == transform((prior / 'source' / name).read_text()),
                'Unexpected integration transform ' + name)
    for name in ['search_route_tree.hpp', 'search_route_tree_top.cpp']:
        require(digest(source / name) == digest(root / 'hardware/vitis' / name), 'Component source differs')
    for name in ['site_ledger.hpp', 'site_state.hpp']:
        require(digest(source / name) == digest(root / 'src/native' / name), 'Changed native oracle')
    require('#include "site_ledger.hpp"' in (source / 'site_occupancy_snapshot_adapter.hpp').read_text(),
            'Native component oracle missing')
    require(digest(source / 'oracle_site_routes.hpp') == digest(root / 'src/native/site_routes.hpp'),
            'Changed full negotiation oracle')
    steps = ['compile_top', 'compile_component', 'component', 'compile_differential', 'differential', 'compile_top_regular', 'compile_router']
    for name in steps:
        receipt = json.loads((bundle / (name + '.receipt.json')).read_text())
        require(receipt['exit_code'] == 0 and receipt['log_sha256'] == digest(bundle / (name + '.log')),
                'Failed/changed actual step ' + name)
        command = receipt['command']
        require(command[:2] == ['taskset', '-c'], 'Unexpected execution wrapper')
        if name.startswith('compile_'):
            require(command[3] == 'g++' and '-Werror' in command and not any('NDEBUG' in x for x in command),
                    'Disabled assertions/strict compilation')
        if name in ('compile_top', 'compile_component', 'compile_differential'):
            require('-fsanitize=address,undefined' in command, 'Missing sanitizers')
            require(('-std=c++14' if name=='compile_top' else '-std=c++17') in command, 'Wrong language scope')
    expected_component = ('random accepted=1000 nonfound=1000 atomic_rejections=21\n'
                          'production nodes=1048576 max_path=524288 state=32/16/8 full_buffers_and_guards=PASS\n'
                          'route_tree_cpu PASS\n')
    expected_differential = ('ROUTE_TREE_ROUTE_RANDOM_PASS cases=400 modes=2 snapshots=3750 searches=4938 rounds=1250 '
                            'node_history_snapshots=2412 site_history_snapshots=2106 site_paths=2896 incomplete=190 routed=210\n'
                            'ROUTE_TREE_ROUTE_FULL_RESULTS_PASS\n')
    require((bundle / 'component.log').read_text() == expected_component, 'Incomplete/different component coverage')
    require((bundle / 'differential.log').read_text() == expected_differential, 'Incomplete/different route coverage')
    paths = [plan_path, report_path, state_path, Path(__file__).resolve(), root / 'scripts/check_vitis_kernel.py',
             root / 'scripts/route_tree_routes_transform.py']
    result = dict(status='route_tree_raw_state_and_full_search_differential_independently_verified',
                  files={str(p): digest(p) for p in paths}, source_and_artifact_bindings={**report['files'], **report['artifacts']},
                  component_random_paths=1000, component_failed_searches=1000, rejected_operations=21, full_negotiation_cases=400, searches=4938,
                  full_real_workload_verified=False, rtl_verified=False, physical_verified=False, board_verified=False,
                  limitations=plan['limitations'])
    with output.open('x') as stream:json.dump(result, stream, indent=2);stream.write('\n')
    print(result['status'])


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True);parser.add_argument('--output', type=Path, required=True)
    args=parser.parse_args();audit(args.bundle.resolve(), args.output.resolve())
