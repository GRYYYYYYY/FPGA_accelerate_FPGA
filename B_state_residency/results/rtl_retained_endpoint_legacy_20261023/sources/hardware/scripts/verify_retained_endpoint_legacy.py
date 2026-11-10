"""Freeze the indexed endpoint composition and execute original protocol oracles."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
from make_indexed_endpoint import outputs

ROOT = Path(__file__).resolve().parents[2]
BIN = Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
RTL = ['bounded_sync_fifo', 'scratch_frame_store_bram', 'scratch_page_controller', 'queued_scratch_endpoint',
       'scratch_page_axi', 'backing_frame_directory_retained', 'backing_page_service_retained',
       'scratch_page_codec_wide', 'record_backing_service_retained', 'memory_scratch_endpoint_retained']
PARENTS = {'results/rtl_wide_codec_20261023/manifest.json': '64f217d65ddf19a3347d7104d3d2a9a42d26c9d5d3d79dcd5081fe4a81b8dc9d',
           'results/rtl_indexed_directory_20261023/final_manifest.json': '68296cc4cc3029d072956d0e919803bd67a24f44fe6e6c0e70cb3a91a57d8193',
           'results/rtl_memory_endpoint_20261023/manifest.json': '6c22b2762a8e22dbfeb940ac41727c65aa2caf2e5f68e1c0a0061380535ecccb'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = Path(sys.argv[1]).resolve()
    out.mkdir()
    sources = out / 'sources'
    source_names = [f'hardware/rtl/{name}.sv' for name in RTL] + [
        'hardware/tb/tb_memory_endpoint_retained.sv', 'hardware/tb/tb_memory_endpoint_retained_profile.sv',
        'hardware/rtl/backing_page_service_lookup.sv', 'hardware/rtl/record_backing_service_wide.sv',
        'hardware/rtl/memory_scratch_endpoint_wide.sv', 'hardware/tb/tb_memory_endpoint_wide.sv',
        'hardware/tb/tb_memory_endpoint_wide_profile.sv', 'hardware/scripts/make_indexed_endpoint.py',
        'hardware/scripts/verify_retained_endpoint_legacy.py', 'hardware/INDEXED_ENDPOINT_CONTRACT.md']
    for name, text in outputs().items():
        if (ROOT / name).read_text() != text:
            raise ValueError('Non-mechanical change: ' + name)
    for name, expected in PARENTS.items():
        if sha(ROOT / name) != expected:
            raise ValueError('Changed parent: ' + name)
    vectors = ROOT / 'results/rtl_memory_endpoint_20261023/vectors'
    vm = json.loads((vectors / 'manifest.json').read_text())
    ep = json.loads((ROOT / 'results/rtl_memory_endpoint_20261023/manifest.json').read_text())
    if sha(vectors / 'manifest.json') != ep['artifacts'][str(vectors / 'manifest.json')]:
        raise ValueError('Changed vector manifest')
    for name, expected in vm['files'].items():
        if sha(Path(name)) != expected:
            raise ValueError('Changed vector input')
    manifest = {'status': 'running', 'sources': {}, 'parents': PARENTS,
                'vectors': {'manifest_sha256': sha(vectors / 'manifest.json'), 'files': vm['files']},
                'cases': {}, 'full_router': False, 'board_performance': None}
    for name in source_names:
        original = ROOT / name
        destination = sources / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, destination)
        manifest['sources'][name] = sha(original)
    def save():
        (out / 'simulation_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    save()
    try:
        for size, top in [('small', 'tb_memory_endpoint_retained_small'), ('actual', 'tb_memory_endpoint_retained_profile')]:
            folder = out / size
            folder.mkdir()
            (folder / 'simulate.tcl').write_text('run 2s\nquit\n')
            row = {'status': 'running', 'commands': []}
            manifest['cases'][size] = row
            files = [sources / f'hardware/rtl/{name}.sv' for name in RTL]
            files += [sources / 'hardware/tb/tb_memory_endpoint_retained.sv', sources / 'hardware/tb/tb_memory_endpoint_retained_profile.sv']
            commands = [('compile', [BIN / 'xvlog', '--sv', '--work', 'xil_defaultlib', *files]),
                        ('elaborate', [BIN / 'xelab', 'xil_defaultlib.' + top, '--snapshot', 'endpoint_tb', '--debug', 'typical', '--mt', '2']),
                        ('simulate', [BIN / 'xsim', 'endpoint_tb', '--tclbatch', 'simulate.tcl', '--log', 'simulate.log',
                                      '--testplusarg', 'VECTORS=' + str(vectors / 'actual.txt'), '--testplusarg', 'PAGES=' + str(vectors / 'pages.hex'),
                                      '--testplusarg', 'PROFILE=' + str(out / 'profile')])]
            for stage, command in commands:
                args = list(map(str, command))
                with (folder / (stage + '.console.log')).open('w') as log:
                    process = subprocess.run(args, cwd=folder, stdout=log, stderr=subprocess.STDOUT)
                row['commands'].append({'stage': stage, 'argv': args, 'exit_code': process.returncode})
                save()
                if process.returncode:
                    raise RuntimeError(size + '/' + stage + ' failed')
            log = (folder / 'simulate.log').read_text()
            passed = [line for line in log.splitlines() if line.startswith('TEST_PASS memory_endpoint ')]
            index = [line for line in log.splitlines() if line.startswith('INDEX_ENDPOINT_PASS ')]
            if len(passed) != 1 or len(index) != 1 or 'Fatal:' in log or '$finish' not in log:
                raise RuntimeError(size + ': incomplete semantic regression')
            row.update(status='passed', result=passed[0], index_result=index[0])
            save()
            print(size, passed[0], index[0], flush=True)
        manifest['status'] = 'completed'
        manifest['artifacts'] = {str(p.relative_to(out)): sha(p) for p in out.rglob('*')
                                 if p.is_file() and p.suffix in ['.sv', '.py', '.md', '.log', '.csv', '.tcl']
                                 and not any(s in p.parts for s in ['.Xil', 'xsim.dir'])}
        save()
        print('Simulation complete; profile and provenance audit required', flush=True)
    except Exception as exc:
        manifest.update(status='failed', error=repr(exc)); save(); raise


if __name__ == '__main__':
    main()
