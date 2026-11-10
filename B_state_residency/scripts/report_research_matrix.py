"""Read-only summary of the frozen real routing matrix, with explicit completeness."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
from statistics import median


def read_memory(directory):
    """Sampled post-load RSS is distinct from /usr/bin/time's full-process peak."""
    peaks = {}
    path = directory / 'memory_observations.jsonl'
    if path.exists():
        for line in path.read_text().splitlines():
            try:
                sample = json.loads(line)
            except json.JSONDecodeError:
                # A running observer may be writing its final record right now.
                continue
            if sample.get('after_load'):
                name = sample['name']
                peaks[name] = max(peaks.get(name, 0), sample['rss_kib'])
    return peaks


def run_memory(directory, run, sampled_peaks):
    result = {'process_peak_rss_kib': run['max_rss_kib'],
              'sampled_after_load_peak_rss_kib': sampled_peaks.get(run['name'])}
    path = directory / (run['name'] + '.labels.json')
    if path.exists():
        labels = json.loads(path.read_text())
        contexts = labels['contexts']
        # End-of-run allocated capacities, not peak allocations or DRAM traffic.
        result['end_label_context_capacity_bytes'] = sum(
            sum(c.get(k, 0) for k in ('pool_capacity_bytes', 'node_epoch_bytes',
                                     'page_table_bytes', 'compact_payload_bytes')) for c in contexts)
        result['end_global_dyn_capacity_bytes'] = labels['global_dyn_bytes']
        result['context_count'] = len(contexts)
    return result


def summarize(directory):
    data = json.loads((directory / 'manifest.json').read_text())
    cfg = data['config']
    expected = {(d['id'], c['mode'], c['variant'], c['page_bits']): set(range(cfg['repetitions']))
                for d in cfg['datasets'] for c in cfg['cases']}
    references = {d['id']: d['reference_results'] for d in cfg['datasets']}
    groups = defaultdict(list)
    sampled_peaks = read_memory(directory)
    seen = set()
    for run in data['runs']:
        if not run.get('verified'):
            continue
        key = (run['dataset'], run['mode'], run['variant'], run['page_bits'])
        identity = key + (run['repetition'],)
        if key not in expected or run['repetition'] not in expected[key] or identity in seen:
            raise ValueError('Unexpected or duplicated verified run: ' + run['name'])
        seen.add(identity)
        if run['exit_code'] != 0 or run['result_sha256'] != references[key[0]][key[1]]:
            raise ValueError('Result mismatch: ' + run['name'])
        groups[key].append(run)
    rows = []
    for key, repetitions in expected.items():
        runs = groups[key]
        complete = {r['repetition'] for r in runs} == repetitions
        row = dict(dataset=key[0], mode=key[1], variant=key[2], page_bits=key[3],
                   verified_repetitions=len(runs), required_repetitions=len(repetitions), complete=complete)
        memory = [run_memory(directory, r, sampled_peaks) for r in runs]
        row['memory_samples'] = [dict(name=r['name'], **m) for r, m in zip(runs, memory)]
        if complete:
            row.update(route_ms_median=median(r['metrics']['route_ms'] for r in runs),
                       route_ms_range=[min(r['metrics']['route_ms'] for r in runs),
                                       max(r['metrics']['route_ms'] for r in runs)],
                       max_rss_kib_median=median(r['max_rss_kib'] for r in runs))
            for field in ('sampled_after_load_peak_rss_kib', 'end_label_context_capacity_bytes',
                          'end_global_dyn_capacity_bytes'):
                values = [m.get(field) for m in memory]
                if all(v is not None for v in values):
                    row[field + '_median'] = median(values)
        else:
            row['partial_route_ms'] = [r['metrics']['route_ms'] for r in runs]
        rows.append(row)
    complete = all(r['complete'] for r in rows) and data['status'] == 'passed'
    return dict(status='complete' if complete else 'partial', source_status=data['status'],
                verified_runs=len(seen), required_runs=sum(map(len, expected.values())),
                scope='Same dataset and schedule only; full route time, not FPGA/GPU speedup. RSS is process peak.',
                memory_scope='Label capacities are end-of-run allocations excluding allocator overhead; global dyn is separate. Post-load RSS peaks are externally sampled, not exact.',
                rows=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--require-complete', action='store_true')
    args = parser.parse_args()
    result = summarize(args.directory)
    print(json.dumps(result, indent=2))
    if args.require_complete and result['status'] != 'complete':
        raise SystemExit('Formal matrix incomplete; no final aggregate accepted')


if __name__ == '__main__':
    main()
