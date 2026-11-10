#!/usr/bin/env python3
"""Select matched degree strata from the independently audited full golden graph."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import random
import struct
import sys
from check_vitis_kernel import digest, require

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from packed_graph import PackedGraph
SEED = 20261023
BUCKETS = [('empty', 0, 0), ('degree_1_2', 1, 2), ('degree_3_4', 3, 4),
           ('degree_5_8', 5, 8), ('degree_9_63', 9, 63), ('degree_64_127', 64, 127),
           ('degree_128_255', 128, 255), ('degree_256_511', 256, 511),
           ('degree_512_1024', 512, 1024), ('unknown', -1, -1)]


def read_full_case(data):
    require(len(data) >= 16 and len(data) % 4 == 0, 'Malformed golden length')
    n, capacity, written, failed = struct.unpack_from('<4I', data)
    require(n <= 65536 and capacity <= 1048576 and written <= capacity // 8,
            'Invalid golden bounds')
    require(len(data) == 16 + 16*n + 32*written, 'Golden size differs')
    requests = struct.unpack_from(f'<{n}I', data, 16)
    require(len(set(requests)) == n, 'Duplicate node')
    rows = {}
    cursor = failures = 0
    for i, node in enumerate(requests):
        start, degree, status = struct.unpack_from('<3I', data, 16+4*n+12*i)
        require(status in (0, 1) and start == cursor and start+degree <= written,
                'Invalid full-graph status or offset')
        require(status == 0 or degree == 0, 'Unknown node contains edges')
        begin = 16+16*n+32*start
        edges = data[begin:begin+32*degree]
        records = list(struct.iter_unpack('<8I', edges))
        require(all(edge[0] == node for edge in records), 'Edge source differs')
        require(records == sorted(records), 'Golden edge order differs')
        rows[node] = (status, degree, edges)
        cursor += degree
        failures += status != 0
    require(cursor == written and failures == failed, 'Golden counters differ')
    return rows


def encode_case(rows, nodes):
    results, edges, cursor, failed = [], [], 0, 0
    for node in nodes:
        status, degree, raw = rows[node]
        results.extend([cursor, degree, status])
        edges.append(raw)
        cursor += degree
        failed += status != 0
    require(cursor <= 1048576//8, 'Selected batch exceeds output capacity')
    words = [len(nodes), 1048576, cursor, failed, *nodes, *results]
    return struct.pack(f'<{len(words)}I', *words) + b''.join(edges)


def load_original():
    original = ROOT/'data/derived/hls_region_fixtures_20261023_v1'
    manifest_path = original/'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    prior = ROOT/'results/hls_region_check_20261023_v1.json'
    require(digest(manifest_path) == json.loads(prior.read_text())['source_bundle_manifest_sha256'],
            'Golden manifest changed')
    bound = {str(manifest_path): digest(manifest_path), str(prior): digest(prior)}
    for name, sha in manifest['files'].items():
        path = original/name
        require(digest(path) == sha, 'Original fixture changed: '+name)
        bound[str(path)] = sha
    for entry in manifest['image_files'].values():
        require(digest(entry['path']) == entry['sha256'], 'Original graph changed')
        bound[entry['path']] = entry['sha256']
    rows = {'csr': {}, 'compact': {}}
    for i in range(9):
        for mode in rows:
            part = read_full_case((original/mode/f'full_{i}.bin').read_bytes())
            require(not rows[mode].keys() & part.keys(), 'Overlapping full batches')
            rows[mode].update(part)
    for mode, values in rows.items():
        require(set(values) == set(range(274732)), 'Full node coverage differs')
        require(sum(row[1] for row in values.values()) == 1100754, 'Full edge coverage differs')
        require(sum(row[0] == 1 for row in values.values()) == 53759, 'Unknown row coverage differs')
    require(all(rows['csr'][n][:2] == rows['compact'][n][:2] for n in rows['csr']),
            'Full graph status/degree differs')
    return original, manifest, rows, bound


def canonical_rows(reader, rows, nodes):
    """Map representation-local string/property IDs before cross-mode comparison."""
    canonical = {}
    for node in nodes:
        status, degree, raw = rows[node]
        require(status == (1 if reader.nodes[node][3] < 0 else 0), 'Node known status differs')
        records = list(struct.iter_unpack('<8I', raw))
        if not status:
            require([tuple(r[1:]) for r in records] == reader.numeric_neighbors(node),
                    'Selected golden differs from packed graph')
        result = []
        for src, dst, tile, pip, up, down, attr, direction in records:
            require(direction in (0, 1), 'Invalid edge direction')
            result.append((reader.text(reader.nodes[src][0]), reader.text(reader.nodes[dst][0]),
                           reader.text(reader.tiles[tile][0]), reader.text(pip), reader.text(up),
                           reader.text(down), tuple(sorted(reader.attrs(attr).items())), direction))
        canonical[node] = (reader.text(reader.nodes[node][0]), status, degree, sorted(result))
    return canonical


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    original, manifest, mode_rows, bound = load_original()
    rows = mode_rows['csr']
    rng = random.Random(SEED)
    cases, empty_strata = [], []
    for label, lo, hi in BUCKETS:
        population = sorted(node for node, (status, degree, _) in rows.items()
                            if lo <= (-1 if status else degree) <= hi)
        if not population:
            empty_strata.append(label)
            continue
        selected = rng.sample(population, min(2, len(population)))
        cases.append({'label': label, 'population_rows': len(population), 'nodes': selected,
                      'degrees': [-1 if rows[n][0] else rows[n][1] for n in selected]})
    selected = rng.sample(sorted(rows), 64)
    cases.append({'label': 'uniform_64', 'population_rows': len(rows), 'nodes': selected,
                  'degrees': [-1 if rows[n][0] else rows[n][1] for n in selected]})
    all_nodes = sorted({n for case in cases for n in case['nodes']})
    canonical = {}
    for mode in mode_rows:
        reader = PackedGraph(manifest['image_files'][mode]['path'])
        canonical[mode] = canonical_rows(reader, mode_rows[mode], all_nodes)
        del reader
    require(canonical['csr'] == canonical['compact'], 'Selected canonical edge semantics differ')
    for path in (ROOT/'src').glob('*.py'):
        bound[str(path)] = digest(path)
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    generated = {}
    for mode in ('csr', 'compact'):
        rows = mode_rows[mode]
        target = out/mode
        target.mkdir()
        image = manifest['image_files'][mode]['path']
        config = original/mode/'config.bin'
        lines = []
        for case in cases:
            path = target/(case['label']+'.bin')
            path.write_bytes(encode_case(rows, case['nodes']))
            # Re-read the entire serialized result, including all eight edge fields.
            recovered = read_full_case(path.read_bytes())
            require(recovered == {n: rows[n] for n in case['nodes']}, 'Selected golden differs')
            lines.append(f'{image} {config} {path}')
            generated[str(path)] = digest(path)
        for name in ('capacity', 'wrong_mode'):
            cfg = original/mode/('wrong_mode.config.bin' if name == 'wrong_mode' else 'config.bin')
            lines.append(f'{image} {cfg} {original/mode/(name+".bin")}')
        path = target/'rtl.txt'
        path.write_text('\n'.join(lines)+'\n')
        generated[str(path)] = digest(path)
    bound[str(Path(__file__).resolve())] = digest(__file__)
    report = {'status': 'matched_golden_strata_prepared_not_rtl_executed',
              'created_utc': datetime.now(timezone.utc).isoformat(), 'seed': SEED,
              'files': bound, 'generated': generated, 'cases': cases, 'empty_strata': empty_strata,
              'full_degree_histogram': dict(sorted(Counter(-1 if s else d for s,d,_ in rows.values()).items())),
              'selected_canonical_semantics_equal': True,
              'scope': 'Two uniformly sampled nodes per nonempty degree stratum, plus an independent uniform 64-node batch. Same canonical requests and edge multisets; each mode retains its own string/property IDs and exact eight-field golden output.',
              'limitations': ['Stratum timings are diagnostic, not population-weighted full-router latency.',
                              'Uniform batch is a small node sample, not the actual router access distribution.',
                              'Memory model remains HLS cosimulation AXI, not board DDR/HBM.']}
    with (out/'plan.json').open('x') as stream:
        json.dump(report, stream, indent=2); stream.write('\n')
    print(json.dumps({'status': report['status'], 'cases': cases}))


if __name__ == '__main__':
    main()
