"""Handwritten RRT1 fixtures. These are NOT real FPGA routing benchmarks."""
import json
import struct
from pathlib import Path


def create(path, shared_candidate=True, disconnected=False, shared_path=False, same_net=False):
    nodes, conns = [], []

    def node(x, y, kind=12):
        idx = len(nodes)
        nodes.append({'x': x, 'y': y, 'type': kind, 'children': []})
        return idx

    # Two spatially disjoint groups, four independent nets per group, unequal chain lengths.
    for group in range(2):
        for row in range(4):
            x, y = 2 + group * 30, 3 + row * 4
            length = 5 + row * 2
            chain = [node(x + step, y, 0 if step == 0 else 4 if step == length-1 else 12)
                     for step in range(length)]
            for a, b in zip(chain, chain[1:]):
                nodes[a]['children'].append(b)
            conns.append({'source': chain[0], 'sink': chain[-1], 'hpwl': length,
                          'bbox': [x-1, x+length, y-1, y+1]})
    # The first left net writes this node's label; all right nets inspect its label BEFORE
    # rejecting it by bbox. Used paths remain distinct. This tests read/write audit semantics.
    if shared_candidate:
        shared = conns[0]['source'] + 1
        for c in conns[4:]:
            nodes[c['source']]['children'].insert(0, shared)
    if disconnected:
        nodes[conns[-1]['source']]['children'] = []
    if shared_path:
        common = conns[0]['source'] + 1
        second = conns[1]['source'] + 1
        nodes[common]['children'].append(second)
        nodes[conns[1]['source']]['children'] = [common]
        conns[1]['bbox'][2] = conns[0]['bbox'][2]
        if same_net:
            conns[1]['source'] = conns[0]['source']

    b = bytearray(b'RRT1')

    def put(fmt, *args):
        b.extend(struct.pack('<' + fmt, *args))

    put('7i', 8, 0, 0, 0, 0, 0, 1)  # iterations, extensions, fixed bbox, use bbox
    put('6f', .8, 1, .5, 2, 1, 1000)
    put('3i', 0, 60, 0)
    put('i', 32)
    put('32i', *([0]*32))
    put('i', 0)  # no Laguna
    put('i', len(nodes))
    for i, n in enumerate(nodes):
        put('iiBB5hfiii', i+1, 0, n['type'], 1, n['x'], n['y'], n['x'], n['y'],
            1, 1., i, -1, len(n['children']))
        for child in n['children']:
            put('i', child)
    groups = [[i] for i in range(len(conns))]
    if same_net:
        groups = [[0,1], *groups[2:]]
    put('i', len(groups))
    for group in groups:
        c = conns[group[0]]
        src, sink = nodes[c['source']], nodes[c['sink']]
        put('ffhiii', (src['x']+sink['x'])/2, src['y'], 2*c['hpwl'], len(group), c['source'], len(group))
        for i in group:
            c = conns[i]
            put('4i', 100+i, c['source'], c['sink'], 0)
            put('5h3Bi', *c['bbox'], c['hpwl'], 0, 0, 0, 0)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as f:
        f.write(b)
    meta = {'dataset_kind': 'synthetic_router_fixture', 'nodes': len(nodes), 'connections': len(conns),
            'shared_candidate': shared_candidate, 'disconnected': disconnected,
            'shared_path': shared_path, 'same_net': same_net,
            'description': 'Handwritten chain graph in upstream RRT1 format; no physical device provenance'}
    with path.with_suffix('.json').open('x') as f:
        json.dump(meta, f, indent=2)
        f.write('\n')
    return meta
