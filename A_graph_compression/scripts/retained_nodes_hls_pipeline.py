#!/usr/bin/env python3
"""Run local 2022.2 C simulation and synthesis with the complete occupancy capacities."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
from check_vitis_kernel import digest, require

ROOT = Path(__file__).resolve().parents[1]
HLS = Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls')


def main():
    parser = argparse.ArgumentParser(description=__doc__);parser.add_argument('--prepared', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True);parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--cpu', type=int, default=119);args = parser.parse_args()
    prior = args.prepared.resolve();out = args.output.resolve();project = args.project.resolve()
    require(not project.exists(), 'Existing HLS project; do not restart')
    report_path = prior / 'report.json';report = json.loads(report_path.read_text())
    require(report['status'] == 'retained_nodes_full_search_cpu_differential_verified_full_workload_pending', 'Missing component/integration gate')
    files = {}
    for p, sha in {**report['files'], **report['artifacts']}.items():
        require(digest(p) == sha, 'Prepared occupancy source/evidence drift ' + p)
    out.mkdir(parents=True, exist_ok=False);source = out / 'source';source.mkdir()
    # Use one flat, frozen include tree: mixing root and offsets-v3 copies of
    # pragma-once headers would define the same state/index types twice.
    for path in (prior / 'source').iterdir():
        if path.is_file():files[str(path)] = digest(path);shutil.copyfile(path, source / path.name)
    flow = ROOT / 'hardware/vitis/run_retained_nodes_synthesis.tcl';shutil.copyfile(flow, source / flow.name)
    for p in [flow, Path(__file__).resolve(), ROOT / 'scripts/check_vitis_kernel.py', report_path]:files[str(p)] = digest(p)
    generated = {str(p): digest(p) for p in source.iterdir()}
    command = ['taskset', '-c', str(args.cpu), str(HLS), '-f', str(source / flow.name)]
    plan = dict(files=files, generated=generated, command=command, project=str(project), clock_ns=5,
                setup_uncertainty_ns=1.35, nodes=1048576, pairs=2097152, nets=65536, part='xcu280-fsvh2892-2L-e',
                scope='Full-capacity retained canonical-node component; Csim and synthesis only, no RTL/board claim.')
    (out / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
    state = dict(owner_pid=os.getpid(), status='running', stage='csim_and_synthesis')
    def update():
        temp = out / 'state.tmp';temp.write_text(json.dumps(state, indent=2) + '\n');temp.replace(out / 'state.json')
    update()
    try:
        env = {**os.environ, 'A_RETAINED_NODES_SOURCE': str(source), 'A_RETAINED_NODES_PROJECT': str(project),
               'LD_PRELOAD': '/lib/x86_64-linux-gnu/libudev.so.1'}
        with (out / 'flow.log').open('x') as log:
            child = subprocess.Popen(command, cwd=out, env=env, stdout=log, stderr=subprocess.STDOUT)
            state['child_pid'] = child.pid;update();code = child.wait()
        (out / 'receipt.json').write_text(json.dumps(dict(exit_code=code, command=command, log_sha256=digest(out / 'flow.log')), indent=2) + '\n')
        text = (out / 'flow.log').read_text()
        require(code == 0 and 'ERROR:' not in text and 'RETAINED_NODES_SYNTHESIS_COMPLETE' in text
                and 'RETAINED_NODES_CSIM_COMPLETE' in text and 'RETAINED_ALL_PASS' in text,
                'Occupancy HLS flow failed; inspect retained log')
        for p, sha in {**files, **generated}.items():require(digest(p) == sha, 'Changed HLS input ' + p)
        state.update(status='complete', stage='synthesized_pending_independent_audit_and_rtl');update()
    except BaseException as error:
        state.update(status='failed', error=str(error));update();raise


if __name__ == '__main__':main()
