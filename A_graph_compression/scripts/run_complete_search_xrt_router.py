"""Run the hardware-only full-search router after mode/link and CPU audit gates."""
import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import time

from check_vitis_kernel import digest, require
from check_complete_search_router import METRICS, parse_rows
from search_xrt_board_link import ROOT, verify_link, verify_files, save

BACKEND = 'xrt_hardware_full_search_cpu_negotiation'
COUNTERS = [('controller_counters', 'CONTROLLER_COUNTERS', 11),
            ('snapshot_counters', 'SNAPSHOT_COUNTERS', 10), ('kernel_counters', 'KERNEL_COUNTERS', 7)]
XRT_METRICS = {'xrt_calls', 'xrt_h2d_bytes', 'xrt_d2h_bytes', 'xrt_h2d_ms', 'xrt_d2h_ms', 'xrt_kernel_wall_ms'}


def number(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def validate_result(raw, transport, reference, expected, log, mode, layout, image_bytes):
    require(reference['status'] == 'routed' and len(reference['routes']) == 1062, 'reference is not full workload')
    require(raw['execution'] == 'kernel' and len(raw['batches']) == len(raw['export_ms']) == 2, 'incomplete hardware batches')
    for key, name, width in COUNTERS:
        require([list(row) for row in parse_rows(log, name, width)] == expected[key], 'hardware counters differ: ' + name)
    totals = {key: 0 for key in XRT_METRICS}
    for index, batch in enumerate(raw['batches']):
        require(METRICS | XRT_METRICS | {'backend'} <= batch.keys(), 'missing hardware metrics')
        require(batch['backend'] == BACKEND, 'wrong execution backend')
        require({k: v for k, v in batch.items() if k not in METRICS | XRT_METRICS | {'backend'}} == reference,
                'full route/search/site/negotiation result differs')
        require(batch['cache_hits'] == batch['cache_misses'] == batch['logical_bytes'] == 0, 'native adjacency used')
        require(all(number(batch[k]) for k in METRICS | XRT_METRICS), 'invalid metrics')
        require(all(type(batch[k]) is int for k in ['xrt_calls', 'xrt_h2d_bytes', 'xrt_d2h_bytes']), 'non-integer traffic counts')
        kernel = expected['kernel_counters'][index];calls, submitted, roots = kernel[1], kernel[4], kernel[6]
        require(batch['xrt_calls'] == calls > 0, 'not every search invoked hardware')
        require(8 * submitted + 4 * calls <= batch['xrt_h2d_bytes'] <= 8 * submitted + 4 * roots * calls, 'H2D packet/root volume differs')
        require(batch['xrt_d2h_bytes'] >= 664 * calls, 'missing result/meta readback')
        require(sum(batch[k] for k in ['xrt_h2d_ms', 'xrt_d2h_ms', 'xrt_kernel_wall_ms']) <= batch['route_ms'] + 0.001, 'transport times exceed route wall')
        for key in totals:
            totals[key] += batch[key]
    require(all(number(v) for v in [raw['materialization_ms'], *raw['export_ms']]), 'invalid export/preparation time')
    require(transport['backend'] == BACKEND and transport['complete'] is True and transport['mode'] == mode and transport['layout'] == layout,
            'transport completion/mode/layout differs')
    require(all(isinstance(transport[k], str) and transport[k] for k in ['device_bdf', 'device_name', 'xclbin_uuid']), 'missing device identity')
    require(type(transport['completed']) is int and type(transport['attempts']) is int and
            transport['attempts'] == transport['completed'] == totals['xrt_calls'], 'failed or missing transport attempt')
    require(transport['setup_h2d_bytes'] == image_bytes + 128 + 16, 'resident image setup volume differs')
    for key in ('h2d_bytes', 'd2h_bytes', 'h2d_ms', 'd2h_ms', 'kernel_wall_ms'):
        if key.endswith('_bytes'):
            require(type(transport[key]) is int and transport[key] == totals['xrt_' + key], 'transport byte totals differ: ' + key)
        else:
            require(number(transport[key]) and math.isclose(transport[key], totals['xrt_' + key], rel_tol=1e-12, abs_tol=1e-6), 'transport totals differ: ' + key)
    require(all(number(transport[k]) for k in ('open_ms', 'setup_ms')), 'invalid setup time')
    groups = transport['argument_groups']
    require(len(groups) == 15 and all(type(g) is int and (g == -1 if i in (2, 5) else g >= 0) for i, g in enumerate(groups)), 'invalid runtime group IDs')
    return dict(full_batches_verified=2, routes_per_batch=1062, calls=totals['xrt_calls'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--link', type=Path, required=True)
    parser.add_argument('--host-report', type=Path, required=True)
    parser.add_argument('--device', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cpu', type=int, default=119)
    args = parser.parse_args()
    require(args.cpu in os.sched_getaffinity(0), 'CPU unavailable')
    link = verify_link(args.link)
    host = json.loads(args.host_report.read_text())
    require(host['status'] == 'full_search_xrt_router_compiled_resident_negotiation_cpu_verified_board_pending', 'host integration not verified')
    verify_files(host['inputs']);verify_files(host['artifacts'])
    cpu_path = ROOT / 'results/complete_search_router_audit_20261024_v1.json'
    require(cpu_path.is_file(), 'full production CPU router audit is not complete')
    cpu = json.loads(cpu_path.read_text())
    require(cpu['status'] == 'two_full_router_kernel_conditions_independently_verified', 'CPU full workload audit not passing')
    verify_files(cpu['files'])
    plan_path = ROOT / 'data/derived/complete_search_router_20261024_v1/plan.json'
    plan = json.loads(plan_path.read_text());verify_files(plan['files']);verify_files(plan['generated'])
    mode = link['mode'];index = ('csr', 'compact').index(mode);inp = plan['inputs'][mode]
    require(cpu['results'][index]['condition']['mode'] == mode, 'CPU reference mode differs')
    binary = Path(host['binary']);require(str(binary) in host['artifacts'], 'unbound executable')
    out = args.output.resolve();out.mkdir(parents=True, exist_ok=False)
    command = ['taskset', '-c', str(args.cpu), str(binary), inp['image'], inp['fixture'], inp['sites'],
               '4096', '80', '200000', '8', 'kernel', inp['config'], link['xclbin'], args.device, link['layout'], str(out / 'transport')]
    bound = {str(p.resolve()): digest(p) for p in [Path(__file__), args.host_report, cpu_path, plan_path, binary,
             *(ROOT / 'scripts' / name for name in ('search_xrt_board_link.py', 'check_vitis_kernel.py', 'check_complete_search_router.py')),
             Path(link['xclbin']), *(Path(v) for v in inp.values()), Path(plan['references'][mode])]}
    bound.update(link['files'])
    save(out / 'plan.json', dict(command=command, files=bound, mode=mode, layout=link['layout'], link=link))
    start = time.perf_counter()
    with (out / 'raw.json').open('x') as raw, (out / 'run.log').open('x') as log:
        result = subprocess.run(command, stdout=raw, stderr=log, cwd=ROOT)
    receipt = dict(exit_code=result.returncode, process_wall_ms=(time.perf_counter() - start) * 1000,
                   command=command, plan_sha256=digest(out / 'plan.json'), raw_sha256=digest(out / 'raw.json'), log_sha256=digest(out / 'run.log'))
    save(out / 'receipt.json', receipt);verify_files(bound)
    require(result.returncode == 0, 'hardware run failed; original outputs retained')
    reference = json.loads(Path(plan['references'][mode]).read_text())
    reference = {k: v for k, v in reference.items() if k not in METRICS}
    checks = validate_result(json.loads((out / 'raw.json').read_text()), json.loads((out / 'transport/complete.json').read_text()),
                             reference, cpu['results'][index], (out / 'run.log').read_text(), mode, link['layout'], Path(inp['image']).stat().st_size)
    report = dict(status='two_full_real_router_batches_with_hardware_search_verified', checks=checks, mode=mode, layout=link['layout'],
                  files={str(p): digest(p) for p in out.rglob('*') if p.is_file()}, hardware_executed=True,
                  limitations=['Only search runs on FPGA; snapshot construction, negotiation and occupancy remain CPU work.',
                               '14 physically evidenced site instances; full special-resource semantics remain incomplete.',
                               'One two-batch diagnostic run; no statistical speedup or power measurement.'])
    save(out / 'audit.json', report);print(json.dumps(dict(status=report['status'], output=str(out))))


if __name__ == '__main__':
    main()
