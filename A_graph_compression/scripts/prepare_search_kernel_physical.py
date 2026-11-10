"""Freeze full-capacity production RTL for independent Vivado OOC evaluation."""
import json
from pathlib import Path
import shutil

from check_vitis_kernel import digest, require

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/derived/search_kernel_physical_20261024_v1'


def main():
    cpu_path = ROOT / 'results/complete_search_router_audit_20261024_v1.json'
    cpu = json.loads(cpu_path.read_text())
    require(cpu['status'] == 'two_full_router_kernel_conditions_independently_verified', 'full CPU audit missing')
    setup_path = ROOT / 'results/search_kernel_boundary_setup_20261024_v1.json'
    setup = json.loads(setup_path.read_text())
    require(setup['status'] == 'state_capacity_boundary_hls_setup_verified_rtl_pending', 'production RTL origin not verified')
    flow = ROOT / 'hardware/vitis/search_kernel_physical_flow.tcl'
    inputs = {str(p): digest(p) for p in [cpu_path, setup_path, flow, Path(__file__).resolve()]}
    generated = {};jobs = []
    for mode, cpus, session in [('csr', [122, 124], 'vivado-20261024-200659-4536a838'),
                               ('compact', [125, 126], 'vivado-20261024-200724-c151e46f')]:
        work = OUT / mode
        require(work.is_dir() and not (work / 'state.json').exists(), 'missing dedicated workspace or existing flow')
        source = work / 'source';source.mkdir(exist_ok=False)
        original = ROOT / 'build/search_kernel_hls_20261024_v3' / mode / 'solution/syn/verilog'
        files = sorted(p for p in original.iterdir() if p.suffix in ('.v', '.dat'))
        require(len(files) == (59 if mode == 'csr' else 62), 'production RTL/ROM file set changed')
        for path in files:
            sha = digest(path);require(setup['artifacts'].get(str(path)) == sha, 'RTL/ROM differs from setup proof')
            inputs[str(path)] = sha;target = source / path.name;shutil.copyfile(path, target)
            require(digest(target) == sha, 'copy changed RTL')
            generated[str(target)] = sha
        xdc = work / 'clock.xdc'
        with xdc.open('x') as f:
            f.write('# Same 5ns target and 1.35ns setup margin as production HLS.\n'
                    '# OOC internal timing only; external AXI delays require the actual platform.\n'
                    'create_clock -name ap_clk -period 5.000 [get_ports ap_clk]\n'
                    'set_clock_uncertainty -setup 1.350 [get_clocks ap_clk]\n')
        script = work / 'run_flow.tcl';shutil.copyfile(flow, script)
        for path in [xdc, script]:generated[str(path)] = digest(path)
        jobs.append(dict(mode=mode, session_id=session, cpus=cpus, source_command='source {' + str(script) + '}',
                         rtl_files=len(files) - 1, rom_files=1))
    for path in [OUT / 'csr/local_help.txt', OUT / 'csr/flow_help.txt']:
        require(path.is_file(), 'local version/command help not captured');inputs[str(path)] = digest(path)
    plan = dict(inputs=inputs, generated=generated, jobs=jobs, part='xcu280-fsvh2892-2L-e', clock_ns=5,
                setup_uncertainty_ns=1.35, vivado_version='2022.2', max_threads_per_mode=2,
                scope='Whole unchanged production search RTL, independent OOC synthesis/place/route on full device.',
                limitations=['Functional RTL replay and full-state boundary RTL remain pending; OOC completion cannot mark those gates passed.',
                             'No U280 platform shell/reserved-resource floorplan; cannot claim platform timing or utilization.',
                             'External AXI input/output delays intentionally await the real platform; report all unconstrained paths without waivers.',
                             'Only 14 physically evidenced site instances; full outer negotiation still CPU.',
                             'No bitstream programming, board throughput or power measurement.'])
    with (OUT / 'plan.json').open('x') as f:
        json.dump(plan, f, indent=2);f.write('\n')
    print(json.dumps(dict(status='frozen_physical_inputs_not_yet_run', output=str(OUT), jobs=jobs)))


if __name__ == '__main__':
    main()
