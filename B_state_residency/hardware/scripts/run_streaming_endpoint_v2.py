"""Run unchanged indexed RTL with sequential expected-page input and full queries."""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
from make_streaming_endpoint_tb_v2 import generate
from verify_indexed_endpoint import BIN, ROOT, RTL, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--large', action='store_true')
    args = parser.parse_args()
    out = args.output.resolve(); out.mkdir()
    size = 'large' if args.large else 'small'
    vectors = ROOT / ('results/streaming_vectors_' + size + '_20261023')
    vm = json.loads((vectors / 'manifest.json').read_text())
    require = lambda test, message: None if test else (_ for _ in ()).throw(ValueError(message))
    require(vm['status'] == 'passed', 'Vector generation incomplete')
    require(sha(vectors / 'manifest.json') == json.loads((vectors / 'completion_audit.json').read_text())['manifest_sha256'], 'Changed vector manifest')
    for name, expected in vm['artifacts'].items():
        require(sha(vectors / name) == expected, 'Changed vectors')
    parent_path = ROOT / 'results/rtl_indexed_endpoint_20261023/manifest.json'
    require(sha(parent_path) == '3e9af59e016e6ca70c7064446504a679a1a3f09d2b3e0d7e7e3d7331fd85b428', 'Changed endpoint parent')
    parent = json.loads(parent_path.read_text())
    sim_path = parent_path.parent / 'simulation_manifest.json'
    require(sha(sim_path) == parent['simulation_manifest_sha256'], 'Changed parent simulation')
    inherited = json.loads(sim_path.read_text())['sources']
    tb = ROOT / 'hardware/tb/tb_memory_endpoint_stream_v2.sv'
    require(tb.read_text() == generate(), 'Streaming transform changed')
    pilot = None
    if args.large:
        pilot_path = ROOT / 'results/rtl_streaming_small_v2_20261023/manifest.json'
        pilot = json.loads(pilot_path.read_text())
        require(pilot['status'] == 'passed' and pilot['parent_cycle_equivalence'], 'Small streaming pilot incomplete')
        require(sha(pilot_path) == json.loads((pilot_path.parent / 'completion_audit.json').read_text())['manifest_sha256'], 'Changed pilot')
    sources = out / 'sources'
    names = [f'hardware/rtl/{name}.sv' for name in RTL] + [
        'hardware/tb/tb_memory_endpoint_indexed.sv', 'hardware/tb/tb_memory_endpoint_stream_v2.sv',
        'hardware/scripts/make_streaming_endpoint_tb.py', 'hardware/scripts/make_streaming_endpoint_tb_v2.py', 'hardware/scripts/make_indexed_endpoint.py',
        'hardware/scripts/run_streaming_endpoint_v2.py', 'hardware/scripts/verify_indexed_endpoint.py']
    record = {'status': 'running', 'large': args.large, 'sources': {}, 'commands': [],
              'vector_manifest': {'path': str(vectors / 'manifest.json'), 'sha256': sha(vectors / 'manifest.json')},
              'parent_manifest_sha256': sha(parent_path), 'board_performance': None, 'full_router': False}
    if args.large:
        record['streaming_pilot_sha256'] = sha(pilot_path)
    for name in names:
        source = ROOT / name
        if name.startswith('hardware/rtl/') or name == 'hardware/tb/tb_memory_endpoint_indexed.sv':
            require(sha(source) == inherited[name], 'Changed inherited RTL or oracle')
        if args.large:
            require(sha(source) == pilot['sources'][name], 'Source changed after streaming pilot')
        dest = sources / name
        dest.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, dest)
        record['sources'][name] = sha(source)
    def save():
        (out / 'manifest.json').write_text(json.dumps(record, indent=2) + '\n')
    save()
    (out / 'simulate.tcl').write_text('run 501s\nquit\n')
    files = [sources / f'hardware/rtl/{name}.sv' for name in RTL] + [sources / 'hardware/tb/tb_memory_endpoint_stream_v2.sv']
    commands = [('compile', [BIN / 'xvlog', '--sv', '--work', 'xil_defaultlib', *files]),
                ('elaborate', [BIN / 'xelab', 'xil_defaultlib.tb_memory_endpoint_stream_' + size, '--snapshot', 'stream_tb', '--debug', 'typical', '--mt', '2']),
                ('simulate', [BIN / 'xsim', 'stream_tb', '--tclbatch', 'simulate.tcl', '--log', 'simulate.log',
                              '--testplusarg', 'VECTORS=' + str(vectors / 'actual.txt'), '--testplusarg', 'PAGES=' + str(vectors / 'pages.hex')])]
    try:
        for stage, command in commands:
            argv = list(map(str, command))
            with (out / (stage + '.console.log')).open('w') as log:
                process = subprocess.Popen(argv, cwd=out, stdout=log, stderr=subprocess.STDOUT)
                row = {'stage': stage, 'argv': argv, 'pid': process.pid, 'exit_code': None}
                record['commands'].append(row); save()
                row['exit_code'] = process.wait(); save()
            require(row['exit_code'] == 0, stage + ' failed')
            if stage == 'compile':
                compile_log = (out / 'compile.console.log').read_text()
                require('VRFC 10-8884' not in compile_log, 'Watchdog constant truncation rejected')
                record['compiler_warnings'] = [line for line in compile_log.splitlines() if line.startswith('WARNING:')]
                save()
        import re
        log = (out / 'simulate.log').read_text()
        passed = re.findall(r'^TEST_PASS memory_endpoint (.+)$', log, re.M)
        require(len(passed) == 1 and 'Fatal:' not in log and '$finish' in log, 'Incomplete protocol test')
        counts = {k: int(v) for k, v in re.findall(r'(\w+)=(\d+)', passed[0])}
        require((counts['checks'], counts['transfers'], counts['fences']) == (vm['public_commands'], vm['transfers'], vm['queries']), 'Incomplete query coverage')
        finished = re.findall(r'^STREAM_QUERY_DONE (.+)$', log, re.M)
        require(len(finished) == vm['queries'], 'Missing query completion receipts')
        end_time = int(re.search(r'\$finish called at time : (\d+) ns', log)[1])
        if not args.large:
            expected = {k: v for k, v in parent['simulation']['actual'].items() if k not in ['index', 'end_time_ns']}
            require(counts == expected and end_time == parent['simulation']['actual']['end_time_ns'], 'Streaming input perturbed baseline')
        index = re.findall(r'^INDEX_ENDPOINT_PASS (.+)$', log, re.M)
        require(len(index) == 1, 'Missing index lifecycle coverage')
        for name, expected in record['sources'].items():
            require(sha(ROOT / name) == expected == sha(sources / name), 'Source changed during run')
        record.update(status='passed', counts=counts, index_result=index[0], query_receipts=finished,
                      end_time_ns=end_time, parent_cycle_equivalence=not args.large,
                      scope='Complete selected query replay with public command, raw page, AXI and lifecycle checks. No timing/board result.')
        record['artifacts'] = {str(p.relative_to(out)): sha(p) for p in out.rglob('*') if p.is_file()
                               and p.name not in ['manifest.json', 'completion_audit.json']
                               and not any(x in p.parts for x in ['.Xil', 'xsim.dir'])}
        save()
        (out / 'completion_audit.json').write_text(json.dumps({'status': 'passed', 'manifest_sha256': sha(out / 'manifest.json')}, indent=2) + '\n')
        print(json.dumps({k: record[k] for k in ['counts', 'index_result', 'end_time_ns', 'parent_cycle_equivalence']}, indent=2), flush=True)
    except Exception as exc:
        record.update(status='failed', error=repr(exc)); save(); raise


if __name__ == '__main__':
    main()
