"""Audit the full indexed endpoint, including an independent directory work model."""
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import re
import sys
from make_indexed_endpoint import outputs
from report_indexed_directory import resource_counts
from verify_indexed_endpoint import PARENTS, ROOT, sha

PHASES = {'idle_and_response_hold': [0], 'ordinary_page_commands': [1, 2], 'owner_lookup': [3, 4],
          'transfer_start': [5, 6, 7], 'write_export_and_feed': [8, 9, 10], 'read_decode_and_beat': [11, 12, 13],
          'memory_completion_wait': [14], 'page_complete_and_address_retire': [15, 16, 17, 18], 'address_recycle': [19, 20]}


def require(test, message):
    if not test:
        raise ValueError(message)


def count_csv(path):
    result = {}
    with path.open() as stream:
        for row in csv.DictReader(stream):
            key = row['group'], int(row['op']), int(row['index'])
            require(key not in result, 'Duplicate profile counter')
            result[key] = int(row['cycles'])
    return result


def mixed(value):
    value ^= value >> 16
    value = value * 0x85ebca6b & 0xffffffff
    value ^= value >> 13
    value = value * 0xc2b2ae35 & 0xffffffff
    return value ^ (value >> 16)


def directory_work(vectors):
    """Model membership and bucket occupancy, not RTL signal transitions."""
    owners = {}; table = {}; epoch = 1; complete = True
    counts = Counter({14: 32768})
    facts = Counter()
    for command in vectors:
        op, _, page, query, price = command[:5]
        if op in (5, 6):
            key = page | query << 18 | price << 20
            facts['owner_requests'] += 1
            candidate = None; found = False
            require(owners or op == 5, 'Unexpected empty refill')
            for state in (7, 8, 9):
                counts[state] += 1
            for offset in range(64):
                bucket = (mixed(key) + offset) & 32767
                counts[10] += 1; counts[11] += 1
                entry = table.get(bucket)
                if entry is None or entry[0] != epoch:
                    candidate = bucket
                    break
                counts[12] += 1; counts[13] += 1
                if entry[1] == key:
                    found = True
                    facts['indexed_hits'] += 1
                    break
            else:
                facts['exhausted_searches'] += 1
            if not found and (candidate is None or not complete):
                comparisons = owners[key] + 1 if key in owners else len(owners)
                counts[1] += comparisons; counts[2] += comparisons
                facts['fallback_searches'] += 1
                found = key in owners
            if not found:
                require(op == 5 and key not in owners and len(owners) < 512, 'Invalid model allocation')
                owners[key] = len(owners)
                counts[3] += 1
                if candidate is None:
                    complete = False; facts['unindexed_allocations'] += 1
                else:
                    table[candidate] = (epoch, key)
            require(owners[key] == command[15], 'Directory model changed frame address')
            # Every successful WB/RF performs exactly one successful PIN.
            for state in (4, 5, 6):
                counts[state] += 1
        elif op == 11:
            owners.clear(); complete = True
            if epoch == 255:
                epoch = 1; table.clear(); counts[14] += 32768
            else:
                epoch += 1
    return counts, facts


def main():
    out = Path(sys.argv[1]).resolve()
    sim_path = out / 'simulation_manifest.json'
    sim = json.loads(sim_path.read_text())
    require(sim['status'] == 'completed', 'Simulation incomplete')
    parents = {}
    for name, expected in PARENTS.items():
        require(sha(ROOT / name) == expected == sim['parents'][name], 'Changed parent: ' + name)
        parents[name] = json.loads((ROOT / name).read_text())
    wide = parents['results/rtl_wide_codec_20261023/manifest.json']
    endpoint = parents['results/rtl_memory_endpoint_20261023/manifest.json']
    for name, expected in sim['sources'].items():
        require(sha(ROOT / name) == expected == sha(out / 'sources' / name), 'Changed source: ' + name)
    for name, text in outputs().items():
        require((out / 'sources' / name).read_text() == text, 'Non-mechanical composition or stimulus')
    # Authenticate inherited modules/tests against previously completed parents.
    generated = set(outputs())
    directory_parent = parents['results/rtl_indexed_directory_20261023/final_manifest.json']
    directory_sim = ROOT / 'results/rtl_indexed_directory_20261023/manifest.json'
    require(sha(directory_sim) == directory_parent['simulation_manifest_sha256'], 'Directory parent changed')
    directory_sources = json.loads(directory_sim.read_text())['sources']
    for name, expected in sim['sources'].items():
        if name.endswith('.sv') and name not in generated:
            require(any(p['files'].get(str(ROOT / name)) == expected for p in [wide, endpoint])
                    or directory_sources.get(name) == expected, 'Unverified inherited RTL/TB: ' + name)
    for name, expected in sim['artifacts'].items():
        require(sha(out / name) == expected, 'Changed simulation artifact')
    for name, expected in sim['vectors']['files'].items():
        require(sha(Path(name)) == expected, 'Changed real vector/page input')
    vmanifest = ROOT / 'results/rtl_memory_endpoint_20261023/vectors/manifest.json'
    require(sha(vmanifest) == sim['vectors']['manifest_sha256'] == endpoint['artifacts'][str(vmanifest)], 'Unbound vectors')
    outcomes = {}
    for size, row in sim['cases'].items():
        require(row['status'] == 'passed' and len(row['commands']) == 3 and all(c['exit_code'] == 0 for c in row['commands']), 'Incomplete tool stages')
        log = (out / size / 'simulate.log').read_text()
        require(not re.search(r'^(Fatal|ERROR):', log, re.M) and log.count('TEST_PASS memory_endpoint ') == 1 and '$finish' in log, 'Bad simulation verdict')
        values = {k: int(v) for k, v in re.findall(r'(\w+)=(\d+)', row['result'])}
        expected = {k: v for k, v in wide['simulation'][size].items() if k != 'end_time_ns'}
        require({k: v for k, v in values.items() if k != 'gap_cycles'} == {k: v for k, v in expected.items() if k != 'gap_cycles'}, 'Semantic work changed')
        index = {k: int(v) for k, v in re.findall(r'(\w+)=(\d+)', row['index_result'])}
        if size == 'small':
            require(index['wraps'] >= 2 and index['overflows'] > 0, 'Integration boundary coverage missing')
            require(values['gap_cycles'] - expected['gap_cycles'] == 4 * index['wraps'], 'Unexplained fence gap growth')
        else:
            require(index['clear_cycles'] == 32768 and values['gap_cycles'] == expected['gap_cycles'], 'Incorrect actual lifecycle')
        outcomes[size] = dict(values, index=index, end_time_ns=int(re.search(r'\$finish called at time : (\d+) ns', log)[1]))
    prior = ROOT / 'results/rtl_wide_codec_20261023'
    for name in ['profile.counts.csv', 'profile.commands.csv']:
        require(sha(prior / name) == wide['artifacts'][str(prior / name)], 'Changed paired profile')
    old = count_csv(prior / 'profile.counts.csv'); new = count_csv(out / 'profile.counts.csv')
    total = new['scalar', -1, 0]; baseline = old['scalar', -1, 0]
    require(baseline == wide['paired_cycles']['wide'], 'Wrong baseline cycle total')
    require(outcomes['actual']['end_time_ns'] == total * 10 + 40, 'Timing/sample disagreement')
    require(f'PROFILE_PASS samples={total} accepted=77099 retired=77099' in (out / 'actual/simulate.log').read_text(), 'Profile incomplete')
    for group, size in [('endpoint', 21), ('directory', 15), ('codec', 14), ('axi', 5), ('service', 8)]:
        require(sum(new[group, -1, i] for i in range(size)) == total, 'Incomplete partition: ' + group)
    for i in (2, 3, 4, 5, 6, 7, 12, 13, 14):
        require(new['scalar', -1, i] == old['scalar', -1, i], 'Changed handshake work')
    vectors = [[int(x, 16) for x in line.split()] for line in (vmanifest.parent / 'actual.txt').read_text().splitlines()]
    expected, facts = directory_work(vectors)
    for state in range(1, 15):
        require(new['directory', -1, state] == expected[state], f'Independent directory work mismatch state={state}')
    with (prior / 'profile.commands.csv').open() as stream:
        before = list(csv.DictReader(stream))
    with (out / 'profile.commands.csv').open() as stream:
        after = list(csv.DictReader(stream))
    require(len(before) == len(after) == len(vectors) == 77099, 'Command coverage missing')
    per_query = []; per_op = defaultdict(lambda: dict(count=0, baseline_cycles=0, indexed_cycles=0))
    inclusive = Counter(); last = 0
    for index, (a, b, vector) in enumerate(zip(before, after, vectors)):
        a = {k: int(v) for k, v in a.items()}; b = {k: int(v) for k, v in b.items()}
        require(all(a[k] == b[k] for k in ['index', 'op', 'query', 'page']), 'Changed command order')
        require((b['index'], b['op'], b['query'], b['page']) == (index, vector[0], vector[3], vector[2]), 'Wrong vector attribution')
        start, available, end = (b[k] for k in ['accept_cycle', 'response_cycle', 'retire_cycle'])
        require(last < start < available <= end and end - available == 4, 'Bad response timing')
        op = b['op']
        if op == 0:
            per_query.append(dict(query_ordinal=len(per_query), commands=0, baseline_cycles=0, indexed_cycles=0))
        old_cycles = a['retire_cycle'] - a['accept_cycle'] + 1; cycles = end - start + 1
        for row in [per_query[-1], per_op[op]]:
            row['baseline_cycles'] += old_cycles; row['indexed_cycles'] += cycles
        per_query[-1]['commands'] += 1; per_op[op]['count'] += 1; inclusive[op] += cycles; last = end
    require(last == total and len(per_query) == 19, 'Wrong terminal coverage')
    require(sum(inclusive.values()) + new['scalar', -1, 1] == total, 'Lost cycles')
    for op in range(16):
        require(sum(new['operation', op, s] for s in range(21)) == inclusive[op], 'Operation accounting inconsistent')
    for state in range(21):
        assigned = sum(new['operation', op, state] for op in range(16)) + (new['scalar', -1, 1] if state == 0 else 0)
        require(assigned == new['endpoint', -1, state], 'State accounting inconsistent')
    phases = {name: {'baseline_cycles': sum(old['endpoint', -1, s] for s in states),
                     'indexed_cycles': sum(new['endpoint', -1, s] for s in states)} for name, states in PHASES.items()}
    negative_path = out / 'negative_guards/classified_manifest.json'
    negative = json.loads(negative_path.read_text())
    require(negative['status'] == 'passed' and len(negative['cases']) == 3, 'Missing integration negative tests')
    require(sha(out / 'negative_guards/manifest.json') == negative['original_manifest_sha256'], 'Original negative evidence changed')
    require(sha(negative_path) == json.loads((out / 'negative_guards/classification_audit.json').read_text())['manifest_sha256'], 'Classification changed')
    for name, expected_hash in negative['classification_source'].items():
        require(sha(Path(name)) == expected_hash, 'Changed classification source')
    require(negative['simulation_manifest_sha256'] == sha(sim_path), 'Negative parent changed')
    for name, expected_hash in negative['sources'].items():
        require(sha(Path(name)) == expected_hash, 'Changed negative driver')
    for name, row in negative['cases'].items():
        require(row['status'] == 'detected' and all(c['exit_code'] == 0 for c in row['commands'][:2]), 'Invalid negative execution')
        folder = out / 'negative_guards' / name
        for filename, expected_hash in row['artifacts'].items():
            require(sha(folder / filename) == expected_hash, 'Changed negative artifact')
        original = (out / 'sources/hardware/rtl' / (row['module'] + '.sv')).read_text()
        require(original.count(row['before']) == 1 and (folder / (row['module'] + '.sv')).read_text() == original.replace(row['before'], row['after']), 'Undeclared mutation')
        log = (folder / 'simulate.log').read_text()
        require(row['first_failure'] in log and row['expected_failure'] in row['first_failure'] and 'TEST_PASS' not in log, 'Wrong negative verdict')
    synthesis = out / 'synthesis'
    receipt = json.loads((synthesis / 'completion.json').read_text())
    require(receipt['exit_code'] == 0 and sha(Path(receipt['source'])) == receipt['source_sha256'] == sha(synthesis / Path(receipt['source']).name), 'Unbound synthesis')
    log = (synthesis / 'synthesis_session.log').read_text()
    require(log.count('\nB_INDEXED_ENDPOINT_SYNTH_DONE\n') == 1 and not re.search(r'^(ERROR|CRITICAL WARNING):', log, re.M), 'Synthesis failed')
    require((synthesis / 'memory_scratch_endpoint_indexed.dcp').stat().st_size > 10000, 'Missing DCP')
    resources = resource_counts(synthesis / 'utilization.rpt')
    require(resources['Register as Latch'] == 0, 'Unexpected latches')
    rams = (synthesis / 'ram_cells.txt').read_text().splitlines()
    require(sum(x.startswith('memory/memory_service/directory/') for x in rams) == 39, 'Directory RAM lost')
    require(sum(x.startswith('memory/codec/') for x in rams) == 2 and sum(x.startswith('pages/endpoint/storage/') for x in rams) == 2, 'Codec/page RAM lost')
    baseline_resources = wide['synthesis']['utilization']
    result = {'status': 'passed', 'simulation': outcomes, 'paired_cycles': {'baseline': baseline, 'indexed': total,
              'saved': baseline - total, 'reduction_fraction': 1 - total / baseline, 'same_clock_ratio': baseline / total,
              'phases': phases, 'queries': per_query, 'operations': dict(per_op)},
              'directory_work': {'state_cycles': dict(expected), 'facts': dict(facts), 'verified_against_rtl': True},
              'synthesis': {'utilization': resources, 'baseline_wide_utilization': baseline_resources, 'ram_cells': rams, 'receipt': receipt},
              'negative_controls': {name: row['first_failure'] for name, row in negative['cases'].items()},
              'board_performance': None, 'platform_timing_closed': False, 'full_large_query_rtl': False,
              'scope': 'Same deterministic 19-small-query full state-endpoint protocol/byte oracle; includes index startup. Not full router or hardware acceleration.',
              'parents': PARENTS, 'simulation_manifest_sha256': sha(sim_path), 'warnings': re.findall(r'^WARNING:.*$', log, re.M)}
    scripts = [Path(__file__).resolve(), ROOT / 'hardware/scripts/report_indexed_directory.py', ROOT / 'hardware/scripts/report_codec_timing.py']
    result['audit_sources'] = {str(p): sha(p) for p in scripts}
    result['artifacts'] = {str(p.relative_to(out)): sha(p) for p in out.rglob('*') if p.is_file()
                           and not any(x in p.parts for x in ['.vivado-ai', '.Xil', 'xsim.dir'])
                           and p.name not in ['manifest.json', 'completion_audit.json']}
    result['artifacts']['negative_guards/manifest.json'] = negative['original_manifest_sha256']
    (out / 'manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    audit = {'status': 'passed', 'manifest_sha256': sha(out / 'manifest.json')}
    (out / 'completion_audit.json').write_text(json.dumps(audit, indent=2) + '\n')
    print(json.dumps(audit)); print(json.dumps(result['paired_cycles'], indent=2)); print(json.dumps(resources))


if __name__ == '__main__':
    main()
