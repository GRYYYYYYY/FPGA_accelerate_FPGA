"""Audit observed search footprints against upstream's partition DAG, without changing it."""
from collections import defaultdict
from itertools import combinations
import json
import math


def summarize(path):
    partitions, attempts, final = {}, [], None
    with open(path) as stream:
        for line in stream:
            r = json.loads(line)
            if r['record'] == 'partition':
                if r['task_id'] in partitions:
                    raise ValueError('Duplicate partition record')
                partitions[r['task_id']] = r
            elif r['record'] == 'attempt':
                attempts.append(r)
            elif r['record'] == 'verification':
                if final is not None:
                    raise ValueError('Duplicate verification footer')
                final = r
            else:
                raise ValueError('Unknown trace record')
    if final is None or not partitions:
        raise ValueError('Incomplete trace: missing partition or verification records')
    if len(attempts) != final['attempts_recorded'] or len({a['attempt_id'] for a in attempts}) != len(attempts):
        raise ValueError('Attempt count/ID mismatch')
    owner = {}
    # Upstream ptCollect produces strictly increasing DAG edges. Integer bitsets encode reachability.
    reach = {}
    for t in sorted(partitions, reverse=True):
        bits = 0
        for nxt in partitions[t]['successors']:
            if nxt not in reach or nxt <= t:
                raise ValueError('Invalid upstream DAG edge/order')
            bits |= (1 << nxt) | reach[nxt]
        reach[t] = bits
        for c in partitions[t]['connection_indices']:
            if c in owner:
                raise ValueError('Connection assigned to multiple tasks')
            owner[c] = t

    access, writes, paths, pages = (defaultdict(set) for _ in range(4))
    for a in attempts:
        if a['connection_index'] not in owner:
            raise ValueError('Attempt missing partition assignment')
        task = owner[a['connection_index']]
        for key in a['label_access_resources']:
            access[a['iteration'], key].add(task)
        for key in a['label_write_resources']:
            writes[a['iteration'], key].add(task)
        for key in a['path_resources']:
            paths[a['iteration'], key].add(task)
        pages[a['iteration'], task].update(a['dense_label_pages_512'])

    def audit(index, require_write=False):
        pairs = defaultdict(lambda: {'resources': 0, 'examples': []})
        for (iteration, key), tasks in index.items():
            for left, right in combinations(sorted(tasks), 2):
                if reach[left] & (1 << right):
                    continue  # ordered through any transitive dependency, not just a direct edge
                if require_write and not ({left, right} & writes[iteration, key]):
                    continue
                p = pairs[iteration, left, right]
                p['resources'] += 1
                if len(p['examples']) < 8:
                    p['examples'].append(key)
        examples = []
        disjoint = 0
        for (iteration, left, right), info in sorted(pairs.items()):
            a, b = partitions[left]['bbox'], partitions[right]['bbox']
            overlap = a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]
            disjoint += not overlap
            if len(examples) < 50:
                examples.append({'iteration': iteration, 'tasks': [left, right],
                                 'bbox_disjoint': not overlap, **info})
        return {'iteration_task_pairs': len(pairs), 'bbox_disjoint_pairs': disjoint, 'examples': examples}

    ordered_ns = sorted(a['elapsed_ns'] for a in attempts)
    percentile = lambda p: ordered_ns[max(0, math.ceil(p * len(ordered_ns))-1)] / 1e6 if ordered_ns else None
    complete = len(attempts) == final['attempts_total'] and not any(a['truncated'] for a in attempts)
    budget_attempts = {a['attempt_id'] for a in attempts if a['status'] == 'budget_exhausted'}
    retry_success = sum(a['parent_attempt_id'] in budget_attempts and a['status'] == 'routed' for a in attempts)
    return {
        'scope': 'Observed label accesses/writes and paths; serial execution mapped to original DAG. '
                 'Potential concurrency hazards, not an observed parallel race or proof of physical legality.',
        'coverage': {'all_attempts_and_instrumented_sets_recorded': complete,
                     'unobserved_attempts': final['attempts_total'] - len(attempts),
                     'truncated_attempts': sum(a['truncated'] for a in attempts),
                     'full_memory_access_coverage': False},
        'verification': final,
        'search': {'attempts': len(attempts), 'pops': sum(a['pops'] for a in attempts),
                   'budget_aborts_recorded': len(budget_attempts), 'successful_budget_retries_recorded': retry_success,
                   'attempt_p50_ms_instrumented': percentile(.5), 'attempt_p95_ms_instrumented': percentile(.95),
                   'attempt_max_ms_instrumented': percentile(1),
                   'attempt_sum_ms_instrumented': sum(ordered_ns)/1e6},
        'partition_tasks': len(partitions), 'partition_edges': sum(len(t['successors']) for t in partitions.values()),
        'unordered_label_access': audit(access), 'unordered_label_read_write': audit(access, True),
        'unordered_path_sharing': audit(paths),
        'dense_label_page_counts': [{'iteration': i, 'task': t, 'pages': len(p)} for (i,t), p in sorted(pages.items())],
    }
