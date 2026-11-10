"""Run unchanged small and actual endpoint oracles through the clock-only shells."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BIN = Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')


def main():
    out = Path(sys.argv[1]).resolve()
    sources = out / 'sources'
    simulation = out / 'simulation'
    simulation.mkdir()
    manifest = {'status': 'running', 'cases': {}}
    def save():
        (simulation / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    save()
    try:
        for variant in ['baseline', 'wide']:
            for size in ['small', 'actual']:
                name = variant + '_' + size
                folder = simulation / name
                folder.mkdir()
                row = {'status': 'running', 'commands': []}
                manifest['cases'][name] = row
                files = sorted((sources / 'hardware/rtl').glob('*.sv'))
                files += [sources / f'hardware/tb/tb_clock_shell_{variant}.sv']
                (folder / 'simulate.tcl').write_text('run 2s\nquit\n')
                commands = [
                    ('compile', [BIN / 'xvlog', '--sv', '--work', 'xil_defaultlib', *files]),
                    ('elaborate', [BIN / 'xelab', f'xil_defaultlib.tb_clock_shell_{variant}_{size}',
                                   '-L', 'unisims_ver', '--snapshot', 'clock_shell_tb', '--debug', 'typical', '--mt', '2']),
                    ('simulate', [BIN / 'xsim', 'clock_shell_tb', '--tclbatch', 'simulate.tcl', '--log', 'simulate.log',
                                  '--testplusarg', 'VECTORS=' + str(ROOT / 'results/rtl_memory_endpoint_20261023/vectors/actual.txt'),
                                  '--testplusarg', 'PAGES=' + str(ROOT / 'results/rtl_memory_endpoint_20261023/vectors/pages.hex')])]
                for stage, command in commands:
                    args = list(map(str, command))
                    with (folder / (stage + '.console.log')).open('w') as stream:
                        process = subprocess.run(args, cwd=folder, stdout=stream, stderr=subprocess.STDOUT)
                    row['commands'].append({'stage': stage, 'argv': args, 'exit_code': process.returncode})
                    save()
                    if process.returncode:
                        raise ValueError(name + '/' + stage + ' failed')
                log = (folder / 'simulate.log').read_text()
                passed = [line for line in log.splitlines() if line.startswith('TEST_PASS memory_endpoint ')]
                if len(passed) != 1 or 'Fatal:' in log or '$finish' not in log:
                    raise ValueError(name + ' incomplete semantic regression')
                row.update(status='passed', result=passed[0])
                save()
                print(name, passed[0], flush=True)
        manifest['status'] = 'completed'
        save()
    except Exception as exc:
        manifest.update(status='failed', error=repr(exc))
        save()
        raise


if __name__ == '__main__':
    main()
