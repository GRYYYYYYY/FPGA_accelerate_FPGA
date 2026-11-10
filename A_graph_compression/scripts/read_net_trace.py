#!/usr/bin/env python3
"""Independent decoder for exact net snapshots; not a complete batch verifier."""
import argparse
import json
from pathlib import Path
import struct
from read_search_trace import MAGIC, U32, require, state

def decode_words(words, nodes):
    require(1 <= nodes <= 1048576 and len(words) >= 8, 'Invalid domain/header')
    m = words[:8]
    require(m[0] == MAGIC and 0 < m[1] <= 16777216 and m[2] <= m[1]
            and m[4] == 0 and m[5] == m[3]+1 and m[6:] == [0, 0], 'Invalid metadata')
    require(len(words) == 8+m[2], 'Wrong committed length')
    records = []; at = 8; previous = None
    while at < len(words):
        start = at; h = words[at:at+16]
        require(len(h) == 16 and h[0] == 2 and h[10:] == [0]*6, 'Invalid net header')
        _, size, iteration, query, net, nr, nt, no, ne, ns = h[:10]
        require(net <= U32 and nr <= nodes and nt <= nodes and no <= nodes and ne <= 2097152 and ns <= 65536, 'Invalid counts')
        require(size == 116+(nr+1)//2+(nt+1)//2+no+2*nr+4*ne+4*ns and start+size <= len(words), 'Invalid frame length')
        ordinal = (iteration, query)
        require(previous is None or ordinal > previous, 'Reordered net snapshots'); previous = ordinal
        at += 16
        def take(n):
            nonlocal at
            v = words[at:at+n]; at += n; return v
        result = take(8); demand_raw = take(65); tree = take(5); node = take(4)
        retained = take(6); edges = take(6); site = take(6)
        require(result[0:3] == [0, 10, 0] and result[4] <= result[3] and result[5] <= 1 and result[6] == nr and result[7] == edges[2], 'Invalid net result')
        require(tree[0] == 0x4154524545535431 and tree[1] == nodes and tree[2] < nodes and tree[3] == nr and tree[4] == 1+result[4], 'Invalid tree metadata')
        require(node[0] == 0x414e4f44454f5731 and node[1] == nodes and no <= node[2] <= 2097152 and node[3] > 0, 'Invalid node metadata')
        for meta, magic, local in [(retained, 0x415245544e4f4431, nt), (edges, 0x4152455445444731, ne)]:
            require(meta[0] == magic and meta[1] == nodes and local <= meta[2] <= 2097152 and meta[3] < 2 and meta[4] <= min(65536, meta[2]) and meta[5] > 0, 'Invalid retention metadata')
        require(site[0] == 0x41534954454f5731 and site[1] < 2 and ns <= site[2] <= 65536 and site[3] < 2 and site[4] <= 65536 and site[5] > 0, 'Invalid site metadata')
        def unpack(n):
            packed = take((n+1)//2)
            if n % 2: require(packed[-1] >> 32 == 0, 'Nonzero node padding')
            v = [(packed[i//2] >> (32*(i%2))) & U32 for i in range(n)]
            require(v == sorted(set(v)) and all(x < nodes for x in v), 'Invalid canonical node set')
            return v
        roots = unpack(nr); kept = unpack(nt); owned = take(no)
        require(tree[2] in roots and roots == kept and len(set(owned)) == no and all(k >> 32 == net for k in owned) and sorted(k & U32 for k in owned) == roots, 'Tree/retention/ownership mismatch')
        occupancy = [take(2) for _ in roots]
        require(all(0 < count <= U32 for count, _ in occupancy), 'Invalid occupancy')
        raw = take(4*ne); lanes = [v for w in raw for v in [w & U32, w >> 32]]
        paths = [lanes[i:i+8] for i in range(0, len(lanes), 8)]
        root_set = set(roots)
        require(all(p[0] in root_set and p[1] in root_set and p[7] <= 1 for p in paths), 'Invalid retained edge')
        demands = state(demand_raw, 0); owners = [take(4) for _ in range(ns)]
        expected = [[x, net, 0, 0] for x in demands['signals']]
        expected += [[(1 << 32)|f, net, mask, value] for f, mask, value in demands['bits']]
        expected += [[(2 << 32)|f, net, 0, value] for f, value in demands['values']]
        require(owners == expected, 'Site ownership/demand mismatch')
        require(at == start+size, 'Frame boundary mismatch')
        records.append(dict(iteration=iteration, query=query, net=net, result=result, roots=roots, retained=kept, owned_keys=owned, occupancy=occupancy, edges=paths, demands=demands, demand_words=demand_raw, site_owners=owners, tree_meta=tree, node_meta=node, retained_meta=retained, edge_meta=edges, site_meta=site))
    require(len(records) == m[3], 'Record count mismatch')
    return dict(status='net_snapshots_validated', metadata=m, records=records, complete_batch=False, requires_terminal_record=True)

def decode_file(path, nodes):
    data = Path(path).read_bytes()
    require(len(data) % 8 == 0, 'Unaligned byte stream')
    return decode_words(list(struct.unpack('<%dQ' % (len(data)//8), data)), nodes)

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('path', type=Path); p.add_argument('--nodes', type=int, required=True)
    a = p.parse_args(); print(json.dumps(decode_file(a.path, a.nodes), indent=2))
