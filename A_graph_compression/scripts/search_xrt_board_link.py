"""Bind a full-search xclbin to audited mode-specific RTL before board use."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile

from check_vitis_kernel import digest, require
from check_search_kernel_memory_plan import check as check_memory
from search_kernel_memory_plan import parse_source, validate_xml, SOURCE

ROOT = Path(__file__).resolve().parents[1]
VPP = Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis/2022.2/bin/v++')
MEMORY = ROOT / 'hardware/vitis/search_kernel_memory_v1'
CODE_INPUTS = [Path(__file__).resolve(), *(ROOT / 'scripts' / name for name in (
    'check_vitis_kernel.py', 'check_search_kernel_memory_plan.py', 'search_kernel_memory_plan.py'))]
GATES = {
    ROOT / 'results/search_kernel_xsim_replay_audit_20261024_v1.json': 'unchanged_search_kernel_rtl_replay_and_original_postcheck_verified',
    ROOT / 'results/search_kernel_boundary_rtl_audit_20261024_v1.json': 'production_search_top_full_state_capacity_boundaries_rtl_verified',
}


def verify_files(files):
    for path, sha in files.items():
        require(Path(path).is_file() and digest(path) == sha, 'bound file missing/changed: ' + path)


def gates():
    files = {}
    for path, status in GATES.items():
        require(path.is_file(), 'required RTL audit is not complete: ' + str(path))
        report = json.loads(path.read_text())
        require(report['status'] == status, 'RTL audit not passing: ' + str(path))
        verify_files(report['artifacts'])
        for name, sha in report['artifacts'].items():
            require(name not in files or files[name] == sha, 'inconsistent RTL evidence binding')
            files[name] = sha
        files[str(path)] = digest(path)
    return files


def archive_binding(xo, rtl, xml, bound):
    """Pure archive check; does not itself establish the RTL gates or linking."""
    rtl = Path(rtl)
    references = {p.name: p for p in rtl.iterdir() if p.suffix in ('.v', '.dat')}
    require(references and any(p.suffix == '.v' for p in references.values()), 'no reference RTL')
    for path in references.values():
        require(bound.get(str(path)) == digest(path), 'reference RTL/ROM not bound by audit')
    with zipfile.ZipFile(xo) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)) and archive.testzip() is None, 'duplicate/corrupt archive entries')
        packaged = [n for n in names if (n.endswith('.v') and '/hdl/verilog/' in n) or n.endswith('.dat')]
        by_name = {Path(n).name: n for n in packaged}
        require(len(packaged) == len(by_name) and set(by_name) == set(references), 'packaged RTL/ROM set differs')
        for name, path in references.items():
            require(archive.read(by_name[name]) == path.read_bytes(), 'packaged RTL/ROM differs: ' + name)
        xmls = [n for n in names if n == 'kernel.xml' or n.endswith('/kernel.xml')]
        require(len(xmls) == 1, 'XO must contain exactly one kernel XML')
        args = parse_source(SOURCE)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'kernel.xml';path.write_bytes(archive.read(xmls[0]))
            require(validate_xml(args, path) == validate_xml(args, xml), 'XO ABI differs from production XML')
    return {str(path): digest(path) for path in references.values()}


def xo_binding(xo, mode, gate_files):
    require(mode in ('csr', 'compact'), 'explicit production mode required')
    check_memory(MEMORY / 'plan.json')
    project = ROOT / 'build/search_kernel_hls_20261024_v3' / mode
    bound = archive_binding(xo, project / 'solution/syn/verilog', project / 'kernel.xml', gate_files)
    bound.update({str(Path(xo).resolve()): digest(xo), str(project / 'kernel.xml'): digest(project / 'kernel.xml'),
                  str(MEMORY / 'plan.json'): digest(MEMORY / 'plan.json')})
    return bound


def command(out, platform, config, xo):
    return [str(VPP), '--link', '--target', 'hw', '--platform', str(platform), '--config', str(config),
            '--kernel_frequency', '200', '--temp_dir', str(out / 'tmp'), '--log_dir', str(out / 'logs'),
            '--report_dir', str(out / 'reports'), '-o', str(out / 'search.xclbin'), str(xo)]


def save(path, value):
    with Path(path).open('x') as f:
        json.dump(value, f, indent=2);f.write('\n')


def link(args):
    bound = gates()
    xo = args.xo.resolve();bound.update(xo_binding(xo, args.mode, bound))
    config = MEMORY / (args.layout + '.cfg');platform = args.platform.resolve()
    require(platform.is_file() and platform.suffix == '.xpfm', 'installed .xpfm required')
    require(VPP.is_file(), 'Vitis linker missing')
    out = args.output.resolve();out.mkdir(parents=True, exist_ok=False)
    cmd = command(out, platform, config, xo)
    bound.update({str(p): digest(p) for p in [config, platform, VPP, *CODE_INPUTS]})
    plan = dict(kind='full_search_mode_bound_hardware_link', mode=args.mode, layout=args.layout,
                xo=str(xo), platform=str(platform), config=str(config), command=cmd, files=bound)
    save(out / 'plan.json', plan)
    env = {**os.environ, 'LD_PRELOAD': '/lib/x86_64-linux-gnu/libudev.so.1'}
    with (out / 'link.log').open('x') as log:
        result = subprocess.run(cmd, cwd=out, env=env, stdout=log, stderr=subprocess.STDOUT)
    verify_files(bound)
    binary = out / 'search.xclbin';ok = result.returncode == 0 and binary.is_file()
    receipt = dict(status='linked' if ok else 'failed', exit_code=result.returncode,
                   plan_sha256=digest(out / 'plan.json'), log_sha256=digest(out / 'link.log'),
                   xclbin=str(binary), xclbin_sha256=digest(binary) if binary.is_file() else None)
    save(out / 'receipt.json', receipt)
    require(ok, 'link failed; original evidence retained')
    print(json.dumps(receipt))


def verify_link(directory):
    out = Path(directory).resolve()
    plan = json.loads((out / 'plan.json').read_text());receipt = json.loads((out / 'receipt.json').read_text())
    require(plan['kind'] == 'full_search_mode_bound_hardware_link', 'wrong link evidence kind')
    require(plan['mode'] in ('csr', 'compact') and plan['layout'] in ('ddr_shared', 'hbm_shared', 'hbm_split'), 'wrong mode/layout')
    require(receipt['status'] == 'linked' and receipt['exit_code'] == 0, 'hardware link not complete')
    require(receipt['plan_sha256'] == digest(out / 'plan.json') and receipt['log_sha256'] == digest(out / 'link.log'), 'link receipt changed')
    config = MEMORY / (plan['layout'] + '.cfg');xo = Path(plan['xo']);platform = Path(plan['platform'])
    require(plan['config'] == str(config) and plan['command'] == command(out, platform, config, xo), 'link command differs')
    require(receipt['xclbin'] == str(out / 'search.xclbin') and receipt['xclbin_sha256'] == digest(receipt['xclbin']), 'linked xclbin changed')
    verify_files(plan['files'])
    gate_files = gates();required = xo_binding(xo, plan['mode'], gate_files)
    required.update(gate_files)
    required.update({str(p): digest(p) for p in [config, platform, VPP, *CODE_INPUTS]})
    require(plan['files'] == required, 'link plan omits or changes required source/mode/gate bindings')
    return dict(status='full_search_xclbin_mode_and_link_verified_board_pending', mode=plan['mode'],
                layout=plan['layout'], xclbin=receipt['xclbin'], xclbin_sha256=receipt['xclbin_sha256'],
                files={str(p): digest(p) for p in [out / 'plan.json', out / 'receipt.json', out / 'link.log']},
                hardware_executed=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__);sub = parser.add_subparsers(dest='action', required=True)
    p = sub.add_parser('link');p.add_argument('--xo', type=Path, required=True)
    p.add_argument('--mode', choices=['csr', 'compact'], required=True)
    p.add_argument('--layout', choices=['ddr_shared', 'hbm_shared', 'hbm_split'], required=True)
    p.add_argument('--platform', type=Path, required=True);p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('verify');p.add_argument('--link', type=Path, required=True)
    args = parser.parse_args()
    if args.action == 'link':
        link(args)
    else:
        print(json.dumps(verify_link(args.link)))


if __name__ == '__main__':
    main()
