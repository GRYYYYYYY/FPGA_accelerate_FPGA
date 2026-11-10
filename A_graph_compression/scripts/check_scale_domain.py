"""Audit selected complete rows against source capture and both packed decoders."""
from collections import Counter
import json
from pathlib import Path
import struct
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from canonical_graph import signature, split_name, validate
from packed_graph import PackedGraph


def check_selection(source, domain, selection):
    denominator = selection['denominator']
    if type(denominator) is not int or denominator < 1:
        raise ValueError('Invalid denominator')
    tiles = sorted({r.split('/', 1)[0] for r in source['roots']}, key=lambda t:
        tuple(int(source['tiles'][t][k]) for k in ('SLR_REGION_ID', 'COLUMN', 'ROW'))+(t,))
    retained_tiles = tiles[:max(1, (len(tiles)+denominator-1)//denominator)]
    retained_set = set(retained_tiles)
    selected = {r for r in source['roots'] if r.split('/', 1)[0] in retained_set}
    if selection['source_tiles'] != retained_tiles or selection['sources'] != sorted(selected):
        raise ValueError('Source selection differs from predetermined spatial prefix')
    expected_edges = [e for e in source['edges'] if e['src'] in selected]
    if Counter(map(signature, expected_edges)) != Counter(map(signature, domain['edges'])):
        raise ValueError('Selected complete adjacency changed')
    nodes = selected | {e['dst'] for e in expected_edges}
    aliases = {w:n for w,n in source['aliases'].items() if n in nodes}
    tile_names = {split_name(w)[0] for w in aliases}
    # Full control must retain even any otherwise extraneous captured metadata.
    expected = source if denominator == 1 else {
        'roots': {r:source['roots'][r] for r in selected},
        'oracle_children': {r:source['oracle_children'][r] for r in selected},
        'nodes': {n:source['nodes'][n] for n in nodes}, 'aliases': aliases,
        'tiles': {t:source['tiles'][t] for t in tile_names},
        'pips': {e['pip']:source['pips'][e['pip']] for e in expected_edges}}
    for name in ('roots', 'oracle_children', 'nodes', 'aliases', 'tiles', 'pips'):
        if domain[name] != expected[name]: raise ValueError('Source semantic field changed: '+name)
    validate(domain)


def check_image(domain, image_path, dump_path, native):
    image = PackedGraph(image_path)
    for name, actual in (
        ('nodes', {image.text(n[0]):image.attrs(n[1]) for n in image.nodes}),
        ('tiles', {image.text(t[0]):image.attrs(t[1]) for t in image.tiles}),
        ('aliases', {image.text(image.tiles[t][0])+'/'+image.text(w):image.text(image.nodes[n][0])
                     for (t,w),n in image.aliases.items()}),
        ('roots', {image.text(image.nodes[n][0]):{'pip_count':pc,'child_count':cc}
                    for n,pc,cc in image.roots})):
        if actual != domain[name]: raise ValueError('Packed static semantics differ: '+name)
    adjacency = validate(domain)
    counts = dict(nodes=len(image.nodes), known_rows=0, unknown_rows=0,
                  empty_known_rows=0, directed_edges=0)
    with Path(dump_path).open('rb') as stream:
        for node, info in enumerate(image.nodes):
            name = image.text(info[0])
            if name not in domain['roots']:
                if info[3] != -1: raise ValueError('Unknown boundary promoted to known row')
                try: image.numeric_neighbors(node)
                except KeyError: pass
                else: raise ValueError('Unknown boundary decoded as empty')
                counts['unknown_rows'] += 1
                continue
            decoded = image.decoded_neighbors(node)
            if Counter(signature(e) for e,p in decoded) != Counter(map(signature, adjacency[name])):
                raise ValueError('Packed edge identity/direction/multiplicity differs')
            for edge, pip in decoded:
                if pip != domain['pips'][edge['pip']]: raise ValueError('Packed PIP attributes differ')
            rows = image.numeric_neighbors(node)
            expected = b''.join(struct.pack('<8I', node, *edge) for edge in rows)
            if stream.read(len(expected)) != expected: raise ValueError('Native complete records differ')
            counts['known_rows'] += 1
            counts['empty_known_rows'] += not rows
            counts['directed_edges'] += len(rows)
        if stream.read(1): raise ValueError('Extra native records')
    if native['status'] != 'complete_native_adjacency_scan' or any(native[k] != v for k,v in counts.items()):
        raise ValueError('Native complete domain/status counts differ')
    return counts
