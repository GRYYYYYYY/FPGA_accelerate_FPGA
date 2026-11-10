#!/usr/bin/env python3
"""Check the diagnostic C replay against the original first C search trace."""
import argparse
import json
from pathlib import Path

from check_vitis_kernel import digest, require
from diagnose_compact_native_postcheck_v1 import ROOT, BASE, TRIAL, snapshot_index, read_words
from read_batch_trace_v4 import decode_words


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    require(not args.output.exists(), 'Refuse overwrite')
    diagnosis_path = ROOT/'results/compact_native_v3_postcheck_diagnosis_20261029_v1.json'
    diagnosis = json.loads(diagnosis_path.read_text())
    require(diagnosis['status'] == 'full4tx_rtl_completed_but_original_postcheck_failed'
            and diagnosis['rtl_verified'] is False, 'Wrong diagnosis')
    files = {str(diagnosis_path): digest(diagnosis_path)}
    directory = ROOT/'data/derived/compact_native_first_search_replay_20261029_v1'
    setup_path = BASE/'compressed_batch_compact_cosim_setup/setup.json'
    require(digest(setup_path) == diagnosis['files'][str(setup_path)], 'Changed setup')
    setup = json.loads(setup_path.read_text())
    for name, sha in setup['files'].items():
        require(digest(name) == sha, 'Changed frozen replay dependency: '+name)
        files[name] = sha
    source = BASE/'compressed_batch_compact_cosim_setup/source'
    expected = {
        'compile': ['g++', '-std=c++14', '-O1', '-Wall', '-Wextra', '-Wno-unknown-pragmas', '-I'+str(source),
                    str(ROOT/'scripts/replay_compact_failed_search_v1.cpp'), '-o', str(directory/'replay')],
        'replay': [str(directory/'replay'), str(TRIAL/'rtl_1_0.bin')],
    }
    prefix = ['prlimit', '--as=4294967296:4294967296', '--core=0:0', '--stack=268435456:268435456', '--']
    for stage, command in expected.items():
        receipt_path = directory/(stage+'.receipt.json'); log = directory/(stage+'.log')
        receipt = json.loads(receipt_path.read_text())
        require(receipt['command'] == prefix+command and receipt['exit_code'] == 0
                and receipt['elapsed_seconds'] > 0 and receipt['log_sha256'] == digest(log), 'Bad diagnostic receipt')
        files[str(receipt_path)] = digest(receipt_path); files[str(log)] = digest(log)
    actual = TRIAL/'rtl_1_0.bin'; golden = BASE/'compressed_batch_compact_cosim_setup/hls_1_0.bin'
    for path in [actual, golden]:
        require(digest(path) == diagnosis['files'][str(path)], 'Snapshot changed')
        files[str(path)] = digest(path)
    index = snapshot_index(golden)
    meta = read_words(golden, index[43])
    trace = decode_words(meta+read_words(golden, index[44], meta[2]), 4)
    require(trace['complete_batch'] is True and trace['initial_state_verified'] is True, 'Original golden is incomplete')
    first = trace['searches'][0]
    require(first['iteration'] == 0 and first['query'] == 0 and first['target'] == 1 and first['roots'] == [0], 'Wrong first search')
    lines = (directory/'replay.log').read_text().splitlines()
    require(len(lines) == 4 and lines[0] == 'NULL_IMAGE_REJECTED 6', 'Unexpected replay output')
    require(lines[1].startswith('RESULT ') and lines[2].startswith('PATH ') and lines[3].startswith('META '), 'Missing replay fields')
    result = list(map(int, lines[1].split()[1:]))
    path = list(map(int, lines[2].split()[1:]))
    require(result == first['result'], 'C replay differs from original complete81-word first-search oracle')
    require(path == [word for edge in first['path'] for word in edge], 'C replay path differs')
    require(list(map(int, lines[3].split()[1:])) == result[13:15] == [1, 2], 'C replay workspace counters differ')
    for file in [directory/'replay', ROOT/'scripts/replay_compact_failed_search_v1.cpp',
                 ROOT/'scripts/diagnose_compact_native_postcheck_v1.py', Path(__file__).resolve(), setup_path]:
        files[str(file)] = digest(file)
    report = dict(status='saved_failed_rtl_first_search_inputs_match_original_C_search_oracle_when_host_pointers_nonnull',
                  first_search_result=result, path=first['path'], null_image_result=6,
                  actual_rtl_first_search_result=diagnosis['observed_first_transaction']['result'], files=files,
                  rtl_verified=False, full44_postcheck_verified=False,
                  limits=['Diagnostic single-search C replay at original production capacities; not a replacement for four-transaction RTL acceptance.',
                          'All81 result words and all path words match the first search from original complete C trace.',
                          'Original failed RTL and original C/RTL sources remain unchanged. A new full-scope memory-address mapping trial is required.'])
    with args.output.open('x') as f: json.dump(report, f, indent=2); f.write('\n')
    print(report['status'], 'bindings', len(files))


if __name__ == '__main__':
    main()
