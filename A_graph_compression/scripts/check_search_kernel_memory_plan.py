"""Recheck a generated static plan and its exact inputs/configs; no board claim."""
import argparse
import json
from pathlib import Path

import search_kernel_memory_plan as p


def check(plan_path):
    plan_path = Path(plan_path)
    report = json.loads(plan_path.read_text())
    p.require(report['status'] == 'static_capacity_and_source_xml_abi_checked_board_unverified' and
              report['execution_kind'] == 'static_memory_plan', 'wrong evidence kind')
    p.require(report['evidence'] == dict(platform_linked=False, device_allocated=False, hardware_executed=False),
              'static plan cannot assert hardware evidence')
    p.require(report['kernel'] == p.KERNEL and report['compute_unit'] == p.CU, 'kernel identity differs')
    p.require(report['policy'] == dict(host_request_alignment_bytes=4096, reserve_bytes_per_pool=16 * p.MIB,
                                     reserve_is_policy_not_measured_free_memory=True,
                                     all_thirteen_buffers_simultaneously_resident=True,
                                     graph_allocated_at_full_pragma_depth=True), 'memory policy differs')
    inputs = [p.SOURCE, *p.XMLS.values(), Path(p.__file__).resolve()]
    expected_files = {str(path.relative_to(p.ROOT)): p.sha(path) for path in inputs}
    p.require(report['files'] == expected_files, 'source/XML/generator binding differs')
    args = p.parse_source(p.SOURCE)
    p.require(report['arguments'] == args, 'source arguments differ')
    abi = {mode: p.validate_xml(args, path) for mode, path in p.XMLS.items()}
    p.require(abi['csr'] == abi['compact'] and report['abi'] == abi, 'XML ABI differs')
    layouts = p.layouts(args)
    p.require(set(report['layouts']) == set(layouts) and
              set(report['configs']) == {n + '.cfg' for n in layouts}, 'layout set differs')
    for name, mapping in layouts.items():
        config = plan_path.parent / (name + '.cfg')
        p.require(report['configs'][config.name] == p.sha(config), 'config binding differs')
        actual = p.read_connectivity(config.read_text())
        p.require(actual == mapping, 'config does not match named layout')
        p.require(report['layouts'][name] == p.validate_layout(args, actual), 'capacity accounting differs')
    return dict(status='static_full_search_memory_plan_verified_board_pending',
                plan=str(plan_path.resolve()), plan_sha256=p.sha(plan_path),
                checker_sha256=p.sha(__file__), inputs=expected_files, configs=report['configs'],
                buffers=sum(a['pointer'] for a in args),
                total_requested_bytes=report['layouts']['ddr_shared']['total_requested_bytes'],
                hardware_executed=False, platform_linked=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = check(args.plan)
    with args.output.open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
