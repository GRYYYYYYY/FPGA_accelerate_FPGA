#!/usr/bin/env python3
"""Serialize verified canonical route trees for Vivado FIXED_ROUTE assignment."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'),str(ROOT/'adapters')]
from import_vivado import read_export, sha256
from netlist import read_snapshot
from netlist_routing import validate_routes


def directed_route(route):
    children = defaultdict(list)
    for edge in route['edges']:
        children[edge['src']].append(edge['dst'])
    visited = set()
    def branch(node):
        if node in visited or not re.fullmatch(r'[A-Za-z0-9_./]+', node):
            raise ValueError('Repeated/unsupported node in directed route')
        visited.add(node)
        result = [node]
        following = sorted(children[node])
        for child in following[:-1]:
            result.append('{ '+branch(child)+' }')
        if following:
            result.append(branch(following[-1]))
        return ' '.join(result)
    text = branch(route['source'])
    if visited != set(route['nodes']):
        raise ValueError('Unreachable route nodes')
    return text


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('experiment',type=Path)
    p.add_argument('--provider',choices=['csr','templates','reference'],default='csr')
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--config',type=Path,default=ROOT/'configs/netlist_u280_v2.json')
    args = p.parse_args()
    audit = json.loads((args.experiment/'report.json').read_text())
    cfg = json.loads(args.config.read_text())
    capture_path = ROOT/cfg['output_dir']/'capture.json'
    capture = json.loads(capture_path.read_text())
    snapshot_path = ROOT/cfg['snapshot']
    for path, digest in ((args.config,audit['inputs']['config']),
                         (capture_path,audit['inputs']['capture']),
                         (snapshot_path,audit['inputs']['snapshot'])):
        if sha256(path) != digest:
            raise ValueError('Audited routing input changed: '+str(path))
    for entry in capture['files'].values():
        if sha256(ROOT/entry['path']) != entry['sha256']:
            raise ValueError('Captured routing input changed: '+entry['path'])
    for name in ('queries.json',args.provider+'_routes.json'):
        if sha256(args.experiment/name) != audit['artifacts'][name]:
            raise ValueError('Audited routing artifact changed: '+name)
    graph_path = (ROOT/capture['graph']['path']
                  if capture.get('scope_kind') == 'independent_endpoint_region'
                  else ROOT/cfg['output_dir']/'reference_domain.tsv')
    graph = read_export(graph_path)
    snapshot = read_snapshot(snapshot_path)
    queries = json.loads((args.experiment/'queries.json').read_text())
    source = args.experiment/(args.provider+'_routes.json')
    result = json.loads(source.read_text())
    validation = validate_routes(graph,snapshot,queries,result)
    if not validation['all_nets_routed_without_conflicts']:
        raise ValueError('Only complete independently validated batches may be applied')
    with args.output.open('x') as f:
        f.write('meta\tschema\tcanonical_routes_v1\n')
        f.write('meta\tinput_sha256\t'+sha256(source)+'\n')
        f.write('meta\tgraph_sha256\t'+sha256(graph_path)+'\n')
        f.write('meta\treport_sha256\t'+sha256(args.experiment/'report.json')+'\n')
        for name, route in sorted(result['routes'].items()):
            if any(c in name for c in '\t\n\r'):
                raise ValueError('Control character in net name')
            f.write('\t'.join(['net',name,directed_route(route)])+'\n')
            for node in sorted(route['nodes']):
                f.write('\t'.join(['node',name,node])+'\n')
            for pip in sorted({e['pip'] for e in route['edges']}):
                f.write('\t'.join(['pip',name,pip])+'\n')
        f.write('complete\t'+str(len(result['routes']))+'\n')
    print(json.dumps({'file':str(args.output),'sha256':sha256(args.output),'validation':validation},indent=2))


if __name__ == '__main__':
    main()
