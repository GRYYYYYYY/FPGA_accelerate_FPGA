"""Mutate isolated copies; require each changed semantic guard to be detected."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BIN = Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parent = Path(sys.argv[1]).resolve()
    sources = parent / 'sources'
    out = parent / 'negative_guards'
    out.mkdir()
    original = (sources / 'backing_frame_directory_indexed.sv').read_text()
    variants = {
        'drop_overflow_scan': ("index<=0;state<=SCAN_READ;\n                    end else begin bucket",
                               "rsp_valid<=1;rsp_status<=UNREADY;state<=IDLE;\n                    end else begin bucket", 1),
        'ignore_owner_namespace': ('read_word[23:0]==owner', 'read_word[17:0]==owner[17:0]', 2),
        'hide_published_on_index_hit': ('rsp_frame<=indexed_frame;rsp_published<=read_word[24]',
                                       "rsp_frame<=indexed_frame;rsp_published<=1'b0", 1),
        'respond_before_wrap_scrub': ('clear_response<=1;state<=CLEAR_INDEX;rsp_valid<=0',
                                      'clear_response<=1;state<=CLEAR_INDEX;rsp_valid<=1', 1),
    }
    manifest = {'status': 'running', 'source': {str(Path(__file__).resolve()): sha(Path(__file__).resolve())},
                'parent_manifest_sha256': sha(parent / 'manifest.json'), 'cases': {}}
    def save():
        (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    save()
    for name, (before, after, count) in variants.items():
        if original.count(before) != count:
            raise ValueError('Ambiguous negative mutation: ' + name)
        folder = out / name
        folder.mkdir()
        variant = folder / 'mutated.sv'
        variant.write_text(original.replace(before, after))
        (folder / 'simulate.tcl').write_text('run 1s\nquit\n')
        row = {'status': 'running', 'mutation': {'before': before, 'after': after, 'count': count}, 'commands': []}
        manifest['cases'][name] = row
        commands = [('compile', [BIN / 'xvlog', '--sv', '--work', 'xil_defaultlib',
                                sources / 'backing_frame_directory_lookup.sv', variant, sources / 'tb_indexed_directory.sv']),
                    ('elaborate', [BIN / 'xelab', 'xil_defaultlib.tb_indexed_directory_small', '--snapshot', 'negative_tb', '--debug', 'typical', '--mt', '2']),
                    ('simulate', [BIN / 'xsim', 'negative_tb', '--tclbatch', 'simulate.tcl', '--log', 'simulate.log',
                                  '--testplusarg', 'VECTORS=' + str(ROOT / 'results/indexed_directory_vectors_20261023/small.txt')])]
        for stage, command in commands:
            args = list(map(str, command))
            with (folder / (stage + '.console.log')).open('w') as stream:
                result = subprocess.run(args, cwd=folder, stdout=stream, stderr=subprocess.STDOUT)
            row['commands'].append({'stage': stage, 'argv': args, 'exit_code': result.returncode})
            save()
            if stage != 'simulate' and result.returncode:
                raise RuntimeError(name + ': mutation did not compile/elaborate')
        log = (folder / 'simulate.log').read_text()
        fatal = [x for x in log.splitlines() if x.startswith('Fatal:')]
        expected = 'exposed incomplete index scrub' if name == 'respond_before_wrap_scrub' else 'indexed mismatch'
        if not fatal or expected not in fatal[0] or 'TEST_PASS' in log:
            raise RuntimeError(name + ': intended semantic guard not observed')
        row.update(status='detected', first_failure=fatal[0], artifacts={p.name: sha(p) for p in folder.iterdir()
                                                                      if p.is_file() and p.suffix in ['.sv', '.log', '.tcl']})
        save()
        print(name, fatal[0], flush=True)
    manifest['status'] = 'passed'
    save()
    (out / 'completion_audit.json').write_text(json.dumps({'status': 'passed', 'manifest_sha256': sha(out / 'manifest.json')}, indent=2) + '\n')


if __name__ == '__main__':
    main()
