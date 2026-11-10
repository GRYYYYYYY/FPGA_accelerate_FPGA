#!/usr/bin/env python3
"""Round-trip existing reference trees through the canonical FIXED_ROUTE writer.

Only an API preflight: no new search and no independent full-adjacency claim.
"""
from collections import defaultdict
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'adapters')]
from import_vivado import sha256
from netlist import read_snapshot
from netlist_routing import validate_routes
from prepare_netlist_routes import directed_route


def main():
    directory=ROOT/'data/derived/netlist_preflight_20261022_v1'
    queries=json.loads((directory/'queries.json').read_text())
    snapshot=read_snapshot(ROOT/'data/netlist/routeracc_cost_u280_20261022_v1/snapshot.tsv')
    rows=(directory/'reference_pips.tsv').read_text().splitlines()
    if rows[-1].split('\t')[:2]!=['complete',str(len(queries))]:raise ValueError('Incomplete preflight export')
    adjacency=defaultdict(list)
    pips={}
    records={}
    owners={}
    duplicate_records=0
    for row in rows[:-1]:
        tag,net,pip,un,dn,directional,up,down=row.split('\t')
        if tag!='pip' or directional not in {'0','1'}:raise ValueError('Invalid preflight PIP')
        if (net,pip) in records:
            if records[net,pip]!=row:raise ValueError('Conflicting hierarchy PIP record')
            duplicate_records+=1
            continue
        if pip in owners and owners[pip]!=net:raise ValueError('Shared reference PIP')
        records[net,pip]=row;owners[pip]=net
        # These are actual used reference PIPs. Exclusion policy must still be
        # checked from the full adjacency export for later new candidate paths.
        pips[pip]={'attributes':{'IS_DIRECTIONAL':directional}}
        adjacency[net,un].append({'src':un,'dst':dn,'pip':pip,'direction':'forward','src_wire':up,'dst_wire':down})
        if directional=='0':
            adjacency[net,dn].append({'src':dn,'dst':un,'pip':pip,'direction':'reverse','src_wire':down,'dst_wire':up})
    if int(rows[-1].split('\t')[2])!=len(rows)-1:raise ValueError('PIP record count differs')
    routes={}
    for q in queries:
        reached,todo,edges={q['source']},[q['source']],[]
        for src in todo:
            for edge in adjacency[q['net'],src]:
                if edge['dst'] not in reached:
                    reached.add(edge['dst']);todo.append(edge['dst']);edges.append(edge)
        reference=snapshot['nets'][q['net']]
        if {e['pip'] for e in edges}!=set(reference['pips']) or reached!=set(reference['nodes']):
            raise ValueError('Reference physical tree differs: '+q['net'])
        routes[q['net']]={'source':q['source'],'sinks':q['sinks'],'nodes':sorted(reached),'edges':edges,'complete':True}
    result={'status':'routed','routes':routes}
    graph={'edges':[e for values in adjacency.values() for e in values],'pips':pips}
    check=validate_routes(graph,snapshot,queries,result)
    route_path=directory/'reference_routes.json'
    with route_path.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    with (directory/'routes.tsv').open('x') as f:
        f.write('meta\tschema\tcanonical_routes_v1\nmeta\tinput_sha256\t'+sha256(route_path)+'\n')
        for name,route in sorted(routes.items()):
            f.write('\t'.join(['net',name,directed_route(route)])+'\n')
            for node in sorted(route['nodes']):f.write('\t'.join(['node',name,node])+'\n')
            for pip in sorted({e['pip'] for e in route['edges']}):f.write('\t'.join(['pip',name,pip])+'\n')
        f.write('complete\t'+str(len(routes))+'\n')
    print(json.dumps({'scope':__doc__,'validation':check,'coalesced_identical_hierarchy_records':duplicate_records,
                      'output':str(directory/'routes.tsv')},indent=2))


if __name__=='__main__':main()
