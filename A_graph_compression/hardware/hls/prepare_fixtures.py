#!/usr/bin/env python3
"""Build HLS stimuli and independent Python golden records from audited AGRAPH01."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'adapters')]
from packed_graph import PackedGraph, write_packed
from canonical_graph import validate
from import_vivado import read_export, sha256

SECTIONS = ['NODE', 'TILE', 'GRID', 'ALIAS', 'INSTANCE', 'TPL_OFF', 'RULE',
            'REMOVE', 'ADD', 'PATCH', 'CSR_OFF', 'CSR_EDGE']
IMAGE_DEPTH, MAX_REQUESTS, OUTPUT_DEPTH, MAX_DEGREE = 2097152, 65536, 1048576, 1024


def descriptor(reader):
    if len(reader.data) % 4 or len(reader.data) > IMAGE_DEPTH * 4:
        raise ValueError('Graph exceeds hardware image capacity')
    config = [reader.mode]
    for section in SECTIONS:
        offset, _, count, _ = reader.layout.get(section, (0, 0, 0, 0))
        config.extend([offset // 4, count])
    config += [len(reader.str_offsets)-1, len(reader.attr_offsets)-1, len(reader.data)//4]
    config += [0] * (32-len(config))
    # Hardware binary searches require sorted tables; PackedGraph's dict lookup
    # alone would also accept unsorted input. Validate the stronger contract here.
    for section, width in [('GRID', 2), ('ALIAS', 2)]:
        keys = [r[:width] for r in reader.table(section)]
        if keys != sorted(keys) or len(keys) != len(set(keys)):
            raise ValueError('Unsorted or duplicate hardware lookup keys')
    if reader.mode:
        for _, rs, rc, _, _, ps, pc in reader.instances:
            for rows in (reader.removed[rs:rs+rc], reader.patched[ps:ps+pc]):
                if rows != sorted(rows):
                    raise ValueError('Unsorted hardware exception index')
    validate(reader.materialize())  # Validate all directed edges, attributes and mappings.
    return config


def case(path, reader, requests, capacity):
    if len(requests) > MAX_REQUESTS or capacity > OUTPUT_DEPTH:
        raise ValueError('Batch exceeds hardware contract')
    results, output, failed = [], [], 0
    for node in requests:
        start = len(output)
        if node >= len(reader.nodes):
            status, edges = 4, []
        elif reader.nodes[node][3] < 0:
            status, edges = 1, []
        else:
            edges = reader.numeric_neighbors(node)
            status = 2 if len(edges) > MAX_DEGREE or start+len(edges) > capacity//8 else 0
        if status:
            failed += 1
            edges = []
        results.append((start, len(edges), status))
        output.extend((node, *edge) for edge in edges)
    with path.open('xb') as f:
        f.write(struct.pack('<4I', len(requests), capacity, len(output), failed))
        f.write(struct.pack('<'+'I'*len(requests), *requests))
        for row in results:
            f.write(struct.pack('<3I', *row))
        for row in output:
            f.write(struct.pack('<8I', *row))
    return {'requests': len(requests), 'records': len(output), 'failed': failed,
            'output_capacity_words': capacity}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--report', type=Path, default=ROOT/'results/packed_check_20261022_v2.json')
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    report = json.loads(args.report.read_text())
    manifests, evidence = {'full': [], 'rtl': [], 'matched': []}, {}
    entries = {name:report['artifacts'][name+'.agr'] for name in
               ['csr', 'traversal', 'intent', 'traversal_full_rules', 'traversal_equal_budget']}
    # The earlier independent held-out region has real parallel PIPs that are
    # absent from the traversal workload. Include both representations explicitly.
    region_cfg = json.loads((ROOT/'configs/region_query.json').read_text())
    held_entry = region_cfg['heldout']
    held_path = ROOT/held_entry['path']
    if sha256(held_path) != held_entry['sha256']:
        raise ValueError('Held-out source hash differs')
    held_graph = read_export(held_path)
    bank_entry = report['artifacts']['intent_bank.json']
    if sha256(Path(bank_entry['path'])) != bank_entry['sha256']:
        raise ValueError('Frozen bank hash differs')
    bank = json.loads(Path(bank_entry['path']).read_text())
    for mode in ['csr','compact']:
        path = args.output/('heldout_'+mode+'.agr')
        write_packed(path, held_graph, mode, bank if mode=='compact' else None)
        entries['heldout_'+mode] = {'path':str(path.resolve()),'sha256':sha256(path)}
    readers, selections = {}, {}
    for name, entry in entries.items():
        image = Path(entry['path'])
        if hashlib.sha256(image.read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError('Audited source hash differs')
        reader = PackedGraph(image)
        cfg = args.output/(name+'.config.bin')
        cfg.write_bytes(struct.pack('<32I', *descriptor(reader)))
        degree = {node: len(reader.numeric_neighbors(node)) for node,_,_ in reader.roots}
        if max(degree.values()) > MAX_DEGREE:
            raise ValueError('Actual row exceeds decoder capacity')
        selected = {min(degree), max(degree, key=degree.get)}
        coverage = {}
        for node in degree:
            edges = reader.numeric_neighbors(node)
            categories = []
            if not edges:
                categories.append('known_sink')
            if any(e[-1] for e in edges):
                categories.append('reverse')
            if len({e[0] for e in edges}) < len(edges):
                categories.append('parallel_destination')
            if reader.mode:
                tid,rs,rc,ads,adc,ps,pc = reader.instances[reader.nodes[node][3]]
                if tid < 0: categories.append('fallback')
                if rc: categories.append('remove')
                if adc and tid >= 0: categories.append('add')
                if pc: categories.append('attribute_patch')
                if tid >= 0 and not (rc or adc or pc): categories.append('exact_template')
            for category in categories:
                if category not in coverage:
                    selected.add(node)
                    coverage[category] = node
        unknown = next(i for i,n in enumerate(reader.nodes) if n[3] < 0)
        selected.add(unknown)
        selected.add(len(reader.nodes))
        readers[name], selections[name] = reader, selected
        cases = {}
        specs = [('full', list(range(len(reader.nodes)))+[len(reader.nodes)], OUTPUT_DEPTH),
                 ('rtl', sorted(selected), OUTPUT_DEPTH),
                 ('capacity', [max(degree, key=degree.get), unknown, len(reader.nodes)], 0)]
        for kind, requests, capacity in specs:
            path = args.output/(name+'.'+kind+'.bin')
            cases[kind] = case(path, reader, requests, capacity)
            line = ' '.join(str(x.resolve()) for x in [image, cfg, path])
            manifests['full'].append(line) if kind != 'rtl' else None
            if kind != 'full' and name in ['csr', 'traversal', 'intent', 'heldout_csr', 'heldout_compact']:
                manifests['rtl'].append(line)
        evidence[name] = {'image': str(image), 'sha256': entry['sha256'],
                          'max_degree': max(degree.values()), 'coverage': coverage, 'cases': cases}
    for group in [['csr','traversal','intent'],['heldout_csr','heldout_compact']]:
        requests = sorted(set().union(*(selections[name] for name in group)))
        names = [[reader.text(n[0]) for n in reader.nodes] for reader in [readers[name] for name in group]]
        if any(n != names[0] for n in names):
            raise ValueError('Matched numeric requests refer to different canonical nodes')
        for name in group:
            path = args.output/(name+'.matched.bin')
            evidence[name]['cases']['matched'] = case(path,readers[name],requests,OUTPUT_DEPTH)
            image = Path(entries[name]['path'])
            cfg = args.output/(name+'.config.bin')
            manifests['matched'].append(' '.join(str(x.resolve()) for x in [image,cfg,path]))
    for mode, lines in manifests.items():
        (args.output/(mode+'.txt')).write_text('\n'.join(lines)+'\n')
    metadata = {'created_utc': datetime.now(timezone.utc).isoformat(), 'inputs': evidence,
                'scope': 'Generic decoder target U280; stimuli are audited VU13P graph data. No device databases are merged.',
                'source_report': str(args.report.resolve())}
    metadata['code_sha256'] = {str(p.relative_to(ROOT)):sha256(p) for p in
                              [Path(__file__),ROOT/'hardware/hls/graph_expand.cpp',ROOT/'hardware/hls/graph_expand.hpp',
                               ROOT/'hardware/hls/test_graph_expand.cpp',ROOT/'hardware/hls/run.tcl']}
    metadata['files'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in args.output.iterdir()}
    (args.output/'manifest.json').write_text(json.dumps(metadata, indent=2)+'\n')
    print(json.dumps(evidence, indent=2))


if __name__ == '__main__':
    main()
