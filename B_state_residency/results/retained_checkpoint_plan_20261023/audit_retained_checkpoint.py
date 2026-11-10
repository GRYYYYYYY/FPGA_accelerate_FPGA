"""Audit frozen replay receipts and exercise destructive checkpoint controls."""
import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/retained_checkpoint_plan_20261023'
spec = importlib.util.spec_from_file_location('frozen_planner', OUT / 'replay_retained_checkpoint.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
sha = module.sha
p = json.loads((OUT / 'manifest.json').read_text())
assert p['status'] == 'passed'
assert sha(OUT / 'manifest.json') == json.loads((OUT / 'completion_audit.json').read_text())['manifest_sha256']
for path, digest in {**p['inputs'], **p['source']}.items():
    assert sha(Path(path)) == digest, path
assert sha(OUT / 'replay_retained_checkpoint.py') == next(iter(p['source'].values()))
demand_path = ROOT / 'results/large_query_demand_20261023/manifest.json'
assert sha(demand_path) == 'cbc1340cf62b89ea6b00e3f1a62a8476857a5ac3c36bc0a0ca78243a16c6fbda'
demand = json.loads(demand_path.read_text())
counts = Counter()
for query in p['queries']:
    for key, value in query['counts'].items():
        if not key.startswith('max_'):
            counts[key] += value
    assert query['counts']['max_transaction'] < 65536
    assert query['counts']['max_generation'] < 65536
    assert len(query['checkpoints']) == query['counts'].get('checkpoints', 0)
    for receipt in query['checkpoints']:
        assert receipt['after_drain_transactions'] <= 65536
        assert receipt['after_drain_transactions'] - receipt['before_drain_transactions'] == receipt['dirty_pages_flushed']
        assert 0 <= receipt['dirty_pages_flushed'] <= 4
assert [q['attempt'] for q in p['queries'] if q['checkpoints']] == demand['large_queries_need_checkpoint']
small = Counter()
for query in p['queries']:
    if query['counts']['accesses'] <= 100000:
        small.update(query['counts'])
for key, value in demand['small_reference_matched'].items():
    if key not in ('transfers', 'public_commands'):
        assert small[key] == value, key

negative = []
for fault in ('drop_published_page', 'corrupt_published_value', 'skip_dirty_flush'):
    planner = module.Planner(4, 3)
    planner.access(0, 0, True, 0x12345678)
    if fault == 'skip_dirty_flush':
        planner.live[0]['dirty'] = False
    planner.checkpoint()
    if fault == 'drop_published_page':
        planner.backing.clear()
    elif fault == 'corrupt_published_value':
        planner.backing[0][0] ^= 1
    try:
        planner.access(0, 0, False, 0x12345678)
    except AssertionError as exc:
        assert 'actual read differs' in str(exc)
        negative.append({'fault': fault, 'detected': True, 'error': str(exc)})
    else:
        raise AssertionError('Negative control escaped: ' + fault)
counts['transfers'] = counts['writebacks'] + counts['refills']
delta = {key: counts[key] - value for key, value in demand['totals_without_checkpoints'].items()
         if key in counts}
result = {'status': 'passed', 'manifest_sha256': sha(OUT / 'manifest.json'),
          'demand_manifest_sha256': sha(demand_path), 'totals': dict(counts),
          'delta_from_unbounded_no_checkpoint_census': delta,
          'negative_controls': negative, 'rtl_checkpoint_proven': False,
          'source_sha256': sha(Path(__file__))}
(OUT / 'independent_audit.json').write_text(json.dumps(result, indent=2) + '\n')
(OUT / Path(__file__).name).write_bytes(Path(__file__).read_bytes())
print(json.dumps(result, indent=2))
