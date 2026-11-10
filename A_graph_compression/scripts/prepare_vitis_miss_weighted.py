#!/usr/bin/env python3
"""Prepare matched RTL batches sampled with replacement from audited known misses."""
import argparse
from bisect import bisect_right
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import random
import struct
from check_vitis_kernel import digest, require
from prepare_vitis_stratified import ROOT, load_original, canonical_rows, encode_case, PackedGraph
from check_router_access_profile import read_profile


def weighted_nodes(weights, count, seed):
    require(count > 0 and weights and all(type(w) is int and w >= 0 for w in weights), 'Invalid sampling inputs')
    cumulative = []
    total = 0
    for weight in weights:
        total += weight
        cumulative.append(total)
    require(total > 0, 'Empty miss population')
    rng = random.Random(seed)
    return [bisect_right(cumulative, rng.randrange(total)) for _ in range(count)]


def validate_case(data, rows, nodes):
    require(len(data) >= 16, 'Truncated header')
    n, capacity, written, failed = struct.unpack_from('<4I', data)
    require(n == len(nodes) and capacity == 1048576, 'Request bounds differ')
    require(len(data) == 16+16*n+32*written and written <= capacity//8, 'Serialized size differs')
    require(list(struct.unpack_from(f'<{n}I', data, 16)) == nodes, 'Request order/multiplicity differs')
    cursor = failures = 0
    for i, node in enumerate(nodes):
        status, degree, raw = rows[node]
        require(struct.unpack_from('<3I', data, 16+4*n+12*i) == (cursor, degree, status), 'Result differs')
        start = 16+16*n+32*cursor
        require(data[start:start+32*degree] == raw, 'Eight-field edge payload differs')
        cursor += degree
        failures += status != 0
    require((cursor, failures) == (written, failed), 'Final counters differ')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    original, manifest, modes, bound = load_original()
    audit_path = ROOT/'results/router_access_profile_audit_20261023_v1.json'
    audit = json.loads(audit_path.read_text())
    require(audit['status'] == 'two_full_router_batches_and_canonical_access_profiles_independently_verified', 'Access audit missing')
    bound[str(audit_path)] = digest(audit_path)
    rows = modes['compact']
    degrees = [-1 if rows[n][0] else rows[n][1] for n in range(len(rows))]
    cases, distributions = [], []
    for batch in range(2):
        path = ROOT/f'data/derived/router_access_profile_run_20261023_v1/access.batch_{batch}.tsv'
        require(digest(path) == audit['files'][str(path)], 'Audited access TSV changed')
        bound[str(path)] = digest(path)
        totals = audit['profiles'][batch]['totals']
        parsed = read_profile(path, degrees, batch, totals['hits'], totals['misses'], totals['hits']+totals['misses'])
        require(parsed == audit['profiles'][batch], 'Access distribution differs from audit')
        with path.open() as f:
            next(f)
            weights = [int(line.split('\t')[3]) for line in f]
        require(sum(weights) == totals['misses'], 'Miss weights differ')
        distributions.append({'batch': batch, 'total_known_misses': sum(weights),
                              'misses_by_degree': dict(sorted(Counter({d:sum(w for w,degree in zip(weights,degrees) if degree==d) for d in set(degrees)}).items()))})
        for replicate in range(3):
            seed = 2026102300+batch*10+replicate
            nodes = weighted_nodes(weights, 128, seed)
            require(all(rows[n][0] == 0 and weights[n] > 0 for n in nodes), 'Sample outside known misses')
            cases.append({'label': f'batch_{batch}_replicate_{replicate}', 'batch':batch, 'seed': seed,
                          'nodes': nodes, 'degrees': [degrees[n] for n in nodes],
                          'distinct_nodes': len(set(nodes)), 'sample_edges': sum(degrees[n] for n in nodes),
                          'degree_histogram': dict(sorted(Counter(degrees[n] for n in nodes).items()))})
    selected = sorted({n for c in cases for n in c['nodes']})
    canonical = {}
    for mode in modes:
        reader = PackedGraph(manifest['image_files'][mode]['path'])
        canonical[mode] = canonical_rows(reader, modes[mode], selected)
        del reader
    require(canonical['csr'] == canonical['compact'], 'Canonical semantics differ across representations')
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    generated = {}
    for mode in modes:
        directory = out/mode
        directory.mkdir()
        lines = []
        for case in cases:
            path = directory/(case['label']+'.bin')
            data = encode_case(modes[mode], case['nodes'])
            validate_case(data, modes[mode], case['nodes'])
            path.write_bytes(data)
            generated[str(path)] = digest(path)
            lines.append(f"{manifest['image_files'][mode]['path']} {original/mode/'config.bin'} {path}")
        path = directory/'rtl.txt'
        path.write_text('\n'.join(lines)+'\n')
        generated[str(path)] = digest(path)
    for directory in [ROOT/'src']:
        bound.update({str(p):digest(p) for p in directory.glob('*.py')})
    for p in [Path(__file__).resolve(), ROOT/'scripts/prepare_vitis_stratified.py', ROOT/'scripts/check_router_access_profile.py', ROOT/'scripts/check_vitis_kernel.py']:
        bound[str(p)] = digest(p)
    report = {'status':'matched_known_miss_weighted_fixtures_prepared_not_rtl_executed',
              'created_utc':datetime.now(timezone.utc).isoformat(), 'files':bound, 'generated':generated,
              'cases':cases, 'population_distributions':distributions, 'canonical_semantics_equal':True,
              'sampling':'Integer inverse CDF, with replacement, canonical-node order; 3 independent seeded 128-request batches for each first/resident distribution. Duplicates retained.',
              'limitations':['Samples exclude cache hits and unknown accesses; they are conditional on known misses.',
                             'Counts do not preserve chronological access order. These are resampled requests, not a trace.',
                             'Small samples can omit rare degrees. No full-router timing or board traffic inference.',
                             'Batch kernel calls differ from current direct provider single-row calls; no host-launch cost inference.']}
    with (out/'plan.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({'status':report['status'],'cases':[{k:v for k,v in c.items() if k not in ('nodes','degrees')} for c in cases]},indent=2))

if __name__ == '__main__':main()
