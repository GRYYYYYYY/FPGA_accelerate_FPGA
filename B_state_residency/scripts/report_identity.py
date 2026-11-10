"""Raw single-repeat identity pilot results; no formal speedup statistics."""
import argparse
import json
from pathlib import Path


def capacity(labels):
    return sum(sum(c.get(k, 0) for k in ('pool_capacity_bytes', 'node_epoch_bytes',
                   'page_table_bytes', 'compact_payload_bytes', 'dense_id_bytes'))
               for c in labels['contexts'])


def summarize(directory):
    data = json.loads((directory / 'manifest.json').read_text())
    reference = json.loads((directory / 'frozen_reference_manifest.json').read_text())
    expected = {(d['id'], mode, variant) for d in reference['config']['datasets']
                for mode in ('serial', 'batch') for variant in ('compact', 'sparse_identity')}
    references = {d['id']: d['reference_results'] for d in reference['config']['datasets']}
    seen, rows = set(), []
    for run in data['runs']:
        if not run.get('verified'):
            continue
        key = (run['dataset'], run['mode'], run['variant'])
        if key in seen or key not in expected:
            raise ValueError('Unexpected or duplicate pilot run')
        seen.add(key)
        if run['exit_code'] or run['result_sha256'] != references[key[0]][key[1]]:
            raise ValueError('Pilot quality mismatch')
        labels = run['labels']
        if key[2] == 'sparse_identity':
            for context in labels['contexts']:
                if context['node_epoch_bytes'] != 0 or context['layout'] != 'sparse_identity':
                    raise ValueError('Identity layout was not exercised')
                if context['dense_id_bytes'] * 6 != context['compact_payload_bytes']:
                    raise ValueError('Identity reverse IDs and 24B payload capacity mismatch')
        rows.append(dict(dataset=key[0], mode=key[1], variant=key[2],
                         page_bits=run['page_bits'], route_ms=run['metrics']['route_ms'],
                         end_context_capacity_bytes=capacity(labels),
                         global_dyn_capacity_bytes=labels['global_dyn_bytes']))
    return dict(status='passed' if seen == expected and data['status'] == 'passed' else 'partial',
                verified_runs=len(seen), required_runs=len(expected),
                scope='One repeat per case; raw route time and end context allocation, not significance or speedup. Global state separate; no RSS measurement.', rows=rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(args.directory), indent=2))
