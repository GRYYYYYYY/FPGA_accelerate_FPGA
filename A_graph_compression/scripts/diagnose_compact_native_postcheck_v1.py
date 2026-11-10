#!/usr/bin/env python3
"""Preserve and diagnose the completed v3 RTL's failed first C postcheck.

Read-only with respect to the failed trial. This never emits an acceptance report.
"""
import argparse
import datetime
import json
from pathlib import Path
import re
import struct

from check_vitis_kernel import digest, require

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/tmp/A_graph_compression_recovery_20261025_v1')
TRIAL = BASE/'compact_native_stack_recovery_v3'


def snapshot_index(path):
    inventory = json.loads((ROOT/'hardware/vitis/compressed_batch_rtl_full_depth_inventory.json').read_text())
    expected = {p['id']: p for p in inventory['ports']}
    with path.open('rb') as f:
        header = struct.unpack('<4Q', f.read(32))
        require(header == (0x4142534e41503031, 1, 0, 44), 'Wrong first compact snapshot header')
        result = {}
        for _ in range(44):
            port, width, depth = struct.unpack('<3Q', f.read(24))
            require(port in expected and port not in result, 'Missing/duplicate snapshot port')
            item = expected[port]
            require(depth == item['depth'] and width == item['element_bytes'], 'Snapshot shape changed')
            result[port] = dict(name=item['name'], offset=f.tell(), bytes=width*depth, width=width, depth=depth)
            f.seek(width*depth, 1)
        require(f.tell() == path.stat().st_size == 946498280, 'Incomplete/extra full snapshot data')
    return result


def read_words(path, port, count=None):
    with path.open('rb') as f:
        f.seek(port['offset'])
        count = port['depth'] if count is None else count
        require(count <= port['depth'], 'Read exceeds port')
        return list(struct.unpack('<'+('Q' if port['width'] == 8 else 'I')*count, f.read(count*port['width'])))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'Refuse overwrite')
    files = {}

    def bind(p):
        p = Path(p)
        files[str(p)] = digest(p)
        return p

    state = json.loads(bind(TRIAL/'state.json').read_text())
    require(state['status'] == 'failed' and state['stage'] == 'postcheck', 'Different failure')
    for pid in [1318691, 1323871, 1328613, 646675, 1497979]:
        require(not Path('/proc', str(pid)).exists(), 'Original owner PID still present')
    receipts = {}
    for stage in ['rtl', 'postcheck']:
        receipt = json.loads(bind(TRIAL/(stage+'.receipt.json')).read_text())
        log = bind(TRIAL/(stage+'.log'))
        require(files[str(log)] == receipt['log_sha256'], 'Execution log changed')
        require(receipt['resource_abort'] is False, 'Unexpected resource abort')
        receipts[stage] = receipt
    require(receipts['rtl']['exit_code'] == 0 and receipts['postcheck']['exit_code'] == -6, 'Different terminal receipts')
    require('RTL Simulation : 4 / 4' in (TRIAL/'rtl.log').read_text(), 'Incomplete RTL')
    require('test_compressed_batch_rtl_full_depth.cpp:165:' in (TRIAL/'postcheck.log').read_text(), 'Different assertion')
    performance = bind(TRIAL/'sim/verilog/search_batch_trace_top_v2.performance.result.transaction.xml')
    cycles = [(int(i), int(c)) for i, c in re.findall(r'^transaction\s+(\d+):\s+(\d+)\s+(?:\d+|x)\s*$', performance.read_text(), re.M)]
    require([i for i, _ in cycles] == list(range(4)) and all(c > 0 for _, c in cycles), 'Missing actual cycles')
    execution = json.loads(bind(TRIAL/'plan.json').read_text())
    changed_copies = []
    for name, record in execution['copied'].items():
        require(digest(record['source']) == record['sha256'], 'Original snapshot source changed: '+record['source'])
        actual = digest(name)
        if actual != record['sha256']:
            changed_copies.append(name)
        files[name] = actual
    require(all(name.endswith('/xsim_script.tcl') for name in changed_copies), 'Unexpected cloned input mutation')
    for name, sha in execution['files'].items():
        require(digest(name) == sha, 'Execution prerequisite changed: '+name)
        files[name] = sha
    setup = json.loads(bind(BASE/'compressed_batch_compact_cosim_setup/setup.json').read_text())
    for name, sha in setup['files'].items():
        require(digest(name) == sha, 'Frozen C/RTL input changed: '+name)
        files[name] = sha
    actual = bind(TRIAL/'rtl_1_0.bin')
    golden = bind(BASE/'compressed_batch_compact_cosim_setup/hls_1_0.bin')
    ai, gi = snapshot_index(actual), snapshot_index(golden)
    require(ai == gi, 'Snapshot layouts differ')
    comparison = []
    with actual.open('rb') as af, golden.open('rb') as gf:
        for port, info in ai.items():
            af.seek(info['offset']); gf.seek(info['offset'])
            left = info['bytes']; first = None; different_chunks = 0; at = 0
            while left:
                n = min(left, 1024*1024); a, g = af.read(n), gf.read(n)
                require(len(a) == len(g) == n, 'Truncated payload')
                if a != g:
                    different_chunks += 1
                    if first is None:
                        offset = next(i for i, (x, y) in enumerate(zip(a, g)) if x != y)
                        first = at+offset
                at += n; left -= n
            row = dict(port=port, **info, equal=first is None, first_differing_byte=first,
                       different_1MiB_chunks=different_chunks)
            if info['bytes'] <= 648:
                row.update(actual=read_words(actual, info), golden=read_words(golden, info))
            comparison.append(row)
    pointer_names = ['image_r', 'config_r', 'root_nodes', 'packet', 'heap', 'slots', 'records', 'keys',
                     'unknown_nodes', 'unknown_pips', 'path', 'meta']
    pointers = {}
    for name in pointer_names:
        p = bind(TRIAL/'sim/tv/cdatafile'/('c.search_batch_trace_top_v2.autotvin_'+name+'.dat'))
        rows = re.findall(r'\[\[transaction\]\]\s+(\d+)\s+0x([0-9a-fA-F]+)\s+\[\[/transaction\]\]', p.read_text())
        require([int(i) for i, _ in rows] == list(range(4)), 'Wrong pointer transactions')
        pointers[name] = [int(value, 16) for _, value in rows]
    rtl = bind(TRIAL/'sim/verilog/search_batch_trace_top_v2_sink_loop_worker.v')
    source = rtl.read_text()
    zero_inputs = [n for n, values in pointers.items() if values == [0]*4]
    for name in zero_inputs:
        require(re.search(r'assign \w+ = \(\('+name+r" == 64'd0\) \? 1'b1 : 1'b0\);", source) is not None,
                'No synthesized null predicate for '+name)
    assignments = [dict(line=i, text=line) for i, line in enumerate(source.splitlines(), 1)
                   if line.startswith('assign ') and
                   (line.startswith('assign brmerge1733_') or re.match(r'assign tmp(?:7\d|80)_', line)
                    or re.match(r'assign tobool\d+_i_not_', line))]
    require('brmerge1733_reg_52374 == 1\'d1' in source, 'Null check is not used')
    for p in (TRIAL/'sim/tv/rtldatafile').iterdir():
        if p.is_file(): bind(p)
    for p in [TRIAL/'actual_runtime_limits.json', TRIAL/'sim/wrapc_pc/trace_mode_1_case_0.bin',
              ROOT/'data/derived/integrated_rtl_recovery_supervision_20261027_v1/state.json',
              ROOT/'hardware/vitis/compressed_batch_rtl_full_depth_inventory.json', Path(__file__).resolve()]:
        bind(p)
    observed = {ai[p]['name']: read_words(actual, ai[p]) for p in [13, 19, 34, 41, 43]}
    require(observed['result'][0] == 6 and observed['control_result'][:2] == [4, 3]
            and observed['net_result'][:3] == [2, 6, 4] and observed['batch_result'][:3] == [3, 2, 2],
            'Different failure chain')
    result = dict(status='full4tx_rtl_completed_but_original_postcheck_failed', observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  rtl_verified=False, postcheck_verified=False, full_experiment_complete=False,
                  receipts=receipts, cycles=[c for _, c in cycles], transactions_executed=4, pointers=44,
                  observed_first_transaction=observed, full_first_snapshot_comparison=comparison,
                  pointer_addresses_by_transaction=pointers, zero_address_inputs_with_synthesized_null_checks=zero_inputs,
                  null_check_rtl_assignments=assignments, changed_cloned_inputs=changed_copies, files=files,
                  diagnosis='Zero-based cosimulation pointer allocation activates synthesized host-pointer null checks; first search returns invalid_input and propagates through sink/net/batch error statuses.',
                  limitations=['Static RTL predicate and actual vector/output evidence; no internal waveform was captured.',
                               'Only transaction0 produced a C postcheck snapshot before assertion; all4 raw RTL output sets are preserved.',
                               'No failure waived, no accepted RTL report emitted, no DUT or active trial modified.',
                               'Recovery must preserve all4 transactions/44 pointers/full capacities and original C oracle.'])
    with args.output.open('x') as f: json.dump(result, f, indent=2); f.write('\n')
    print(json.dumps(dict(status=result['status'], bindings=len(files), differing_ports=sum(not r['equal'] for r in comparison), zero_address_inputs=zero_inputs)))


if __name__ == '__main__':
    main()
