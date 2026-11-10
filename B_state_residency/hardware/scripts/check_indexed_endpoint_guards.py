"""Require full endpoint test to reject broken index and retirement boundaries."""
from pathlib import Path
import json
import subprocess
import sys
from verify_indexed_endpoint import BIN, ROOT, RTL, sha


def main():
    out = Path(sys.argv[1]).resolve()
    target = out / 'negative_guards'
    target.mkdir()
    sources = out / 'sources'
    variants = {
        'drop_overflow_scan': ('backing_frame_directory_indexed',
            "index<=0;state<=SCAN_READ;\n                    end else begin bucket",
            "rsp_valid<=1;rsp_status<=UNREADY;state<=IDLE;\n                    end else begin bucket", 'host mismatch'),
        'respond_before_index_scrub': ('backing_frame_directory_indexed',
            'clear_response<=1;state<=CLEAR_INDEX;rsp_valid<=0',
            'clear_response<=1;state<=CLEAR_INDEX;rsp_valid<=1', 'index scrub exposed incomplete directory'),
        'expose_query_during_recycle': ('memory_scratch_endpoint_indexed',
            'assign cmd_ready=!rst && state==IDLE && !rsp_valid;',
            'assign cmd_ready=!rst && (state==IDLE || state==M_RECYCLE_WAIT) && !rsp_valid;',
            'new host command before address recycle')}
    record = {'status': 'running', 'simulation_manifest_sha256': sha(out / 'simulation_manifest.json'),
              'sources': {str(p): sha(p) for p in [Path(__file__).resolve(), ROOT / 'hardware/scripts/verify_indexed_endpoint.py']},
              'cases': {}}
    def save():
        (target / 'manifest.json').write_text(json.dumps(record, indent=2) + '\n')
    save()
    for name, (module, before, after, expected) in variants.items():
        folder = target / name
        folder.mkdir()
        original = (sources / f'hardware/rtl/{module}.sv').read_text()
        if original.count(before) != 1:
            raise ValueError('Ambiguous mutation')
        mutated = folder / (module + '.sv')
        mutated.write_text(original.replace(before, after))
        row = {'status': 'running', 'module': module, 'before': before, 'after': after,
               'expected_failure': expected, 'commands': []}
        record['cases'][name] = row
        (folder / 'simulate.tcl').write_text('run 2s\nquit\n')
        files = [mutated if r == module else sources / f'hardware/rtl/{r}.sv' for r in RTL]
        files += [sources / 'hardware/tb/tb_memory_endpoint_indexed.sv']
        commands = [('compile', [BIN / 'xvlog', '--sv', '--work', 'xil_defaultlib', *files]),
                    ('elaborate', [BIN / 'xelab', 'xil_defaultlib.tb_memory_endpoint_indexed_small', '--snapshot', 'negative_tb', '--debug', 'typical', '--mt', '2']),
                    ('simulate', [BIN / 'xsim', 'negative_tb', '--tclbatch', 'simulate.tcl', '--log', 'simulate.log'])]
        for stage, command in commands:
            args = list(map(str, command))
            with (folder / (stage + '.console.log')).open('w') as stream:
                process = subprocess.run(args, cwd=folder, stdout=stream, stderr=subprocess.STDOUT)
            row['commands'].append({'stage': stage, 'argv': args, 'exit_code': process.returncode})
            save()
            if stage != 'simulate' and process.returncode:
                raise RuntimeError(name + ': failed before simulation')
        log = (folder / 'simulate.log').read_text()
        fatal = [line for line in log.splitlines() if line.startswith('Fatal:')]
        if not fatal or expected not in fatal[0] or 'TEST_PASS' in log:
            raise RuntimeError(name + ': unexpected negative verdict')
        row.update(status='detected', first_failure=fatal[0], artifacts={p.name: sha(p) for p in folder.iterdir()
                                                                      if p.is_file() and p.suffix in ['.sv', '.log', '.tcl']})
        save()
        print(name, fatal[0], flush=True)
    record['status'] = 'passed'; save()
    (target / 'completion_audit.json').write_text(json.dumps({'status': 'passed', 'manifest_sha256': sha(target / 'manifest.json')}, indent=2) + '\n')


if __name__ == '__main__':
    main()
