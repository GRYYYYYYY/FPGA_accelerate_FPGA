"""Counterexample to treating empirical hash probe limits as a guarantee."""
from pathlib import Path
import json
import sys
from study_directory_keysets import measure, mixed, sha

ROOT = Path(__file__).resolve().parents[1]


def main():
    out = Path(sys.argv[1]).resolve()
    study = json.loads((out / 'manifest.json').read_text())
    audit = json.loads((out / 'completion_audit.json').read_text())
    if study['status'] != 'passed' or audit['manifest_sha256'] != sha(out / 'manifest.json'):
        raise ValueError('Study not authenticated')
    for group in ['inputs', 'source']:
        for path, expected in study[group].items():
            if sha(Path(path)) != expected:
                raise ValueError('Changed study input: ' + path)
    for path, expected in study['artifacts'].items():
        if sha(out / path) != expected:
            raise ValueError('Changed study output: ' + path)
    keys = []
    # All owners have the same query tag 0 and price 1, and valid page IDs
    # for the actual 9,089,009-node device graph. Only page selection is adversarial.
    for page in range((9089009 + 63) // 64):
        key = (1 << 20) | page
        if (mixed(key) & 32767) < 64:
            keys.append(key)
        if len(keys) == 192:
            break
    if len(keys) != 192 or len(set(keys)) != 192:
        raise AssertionError('Counterexample construction incomplete')
    result = measure(keys, 32768, mixed)
    # 192 distinct occupied slots starting from only 64 possible hash slots
    # force at least one successful probe path longer than 64 entries.
    if result['max'] < 129 or result['over_64'] == 0:
        raise AssertionError('Expected finite-bound counterexample not observed')
    output = {'status': 'passed', 'kind': 'constructed_adversarial_control_not_real_trace',
              'query_tag': 0, 'price': 1, 'initial_bucket_range': [0, 63],
              'node_count': 9089009, 'keys': keys, 'measurement': result,
              'conclusion': 'A 64-probe cutoff needs a safe overflow/fallback or explicit rejection protocol.',
              'scope': 'Legal owner bit widths and single query/price; not claimed to arise in the captured router trace.',
              'study_manifest_sha256': sha(out / 'manifest.json'),
              'source': {str(Path(__file__).resolve()): sha(Path(__file__).resolve())}}
    (out / 'probe_bound_control.json').write_text(json.dumps(output, indent=2) + '\n')
    (out / 'probe_bound_control_audit.json').write_text(json.dumps({
        'status': 'passed', 'control_sha256': sha(out / 'probe_bound_control.json'),
        'study_manifest_sha256': sha(out / 'manifest.json')}, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
