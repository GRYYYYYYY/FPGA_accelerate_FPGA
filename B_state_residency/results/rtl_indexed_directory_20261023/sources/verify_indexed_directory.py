"""Freeze and execute two bounded non-project XSim directory regressions."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BIN = Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = Path(sys.argv[1]).resolve()
    out.mkdir()
    sources = out / 'sources'
    sources.mkdir()
    paths = ['hardware/rtl/backing_frame_directory_lookup.sv', 'hardware/rtl/backing_frame_directory_indexed.sv',
             'hardware/tb/tb_indexed_directory.sv', 'hardware/scripts/make_indexed_directory.py',
             'hardware/scripts/make_indexed_directory_vectors.py', 'hardware/scripts/verify_indexed_directory.py',
             'hardware/INDEXED_DIRECTORY_CONTRACT.md']
    manifest = {'status': 'running', 'sources': {}, 'cases': {}, 'board_performance': None, 'full_transport_replay': False}
    for name in paths:
        original = ROOT / name
        shutil.copyfile(original, sources / original.name)
        manifest['sources'][name] = sha(original)
    vectors = ROOT / 'results/indexed_directory_vectors_20261023'
    vm = json.loads((vectors / 'manifest.json').read_text())
    manifest['vector_manifest'] = {'path': str(vectors / 'manifest.json'), 'sha256': sha(vectors / 'manifest.json')}
    for name, expected in vm['artifacts'].items():
        if sha(vectors / name) != expected:
            raise ValueError('Changed vectors')
    def save():
        (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    save()
    try:
        for size in ['small', 'large']:
            folder = out / size
            folder.mkdir()
            (folder / 'simulate.tcl').write_text('run 1s\nquit\n')
            row = {'status': 'running', 'commands': []}
            manifest['cases'][size] = row
            commands = [('compile', [BIN / 'xvlog', '--sv', '--work', 'xil_defaultlib',
                                    sources / 'backing_frame_directory_lookup.sv',
                                    sources / 'backing_frame_directory_indexed.sv', sources / 'tb_indexed_directory.sv']),
                        ('elaborate', [BIN / 'xelab', 'xil_defaultlib.tb_indexed_directory_' + size,
                                       '--snapshot', 'directory_tb', '--debug', 'typical', '--mt', '2']),
                        ('simulate', [BIN / 'xsim', 'directory_tb', '--tclbatch', 'simulate.tcl', '--log', 'simulate.log',
                                      '--testplusarg', 'VECTORS=' + str(vectors / (size + '.txt'))])]
            for stage, command in commands:
                args = list(map(str, command))
                with (folder / (stage + '.console.log')).open('w') as log:
                    process = subprocess.run(args, cwd=folder, stdout=log, stderr=subprocess.STDOUT)
                row['commands'].append({'stage': stage, 'argv': args, 'exit_code': process.returncode})
                save()
                if process.returncode:
                    raise RuntimeError(size + '/' + stage + ' failed')
            log = (folder / 'simulate.log').read_text()
            lines = [x for x in log.splitlines() if x.startswith('TEST_PASS indexed_directory ')]
            if len(lines) != 1 or 'Fatal:' in log or '$finish' not in log:
                raise RuntimeError(size + ': no complete PASS')
            counts = dict(x.split('=') for x in lines[0].split()[2:])
            if int(counts['checks']) != vm[size + '_commands']:
                raise RuntimeError('Incomplete vector coverage')
            row.update(status='passed', result=lines[0], counters={k: int(v) for k, v in counts.items()})
            save()
            print(size, lines[0], flush=True)
        manifest['status'] = 'passed'
        manifest['artifacts'] = {str(p.relative_to(out)): sha(p) for p in out.rglob('*')
                                 if p.is_file() and (p.suffix in ('.log', '.tcl') or p.parent == sources)
                                 and not any(x in p.parts for x in ['xsim.dir', '.Xil'])}
        save()
        (out / 'completion_audit.json').write_text(json.dumps({'status': 'passed', 'manifest_sha256': sha(out / 'manifest.json')}, indent=2) + '\n')
    except Exception as exc:
        manifest.update(status='failed', error=repr(exc))
        save()
        raise


if __name__ == '__main__':
    main()
