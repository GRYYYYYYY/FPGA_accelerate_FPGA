#!/usr/bin/env python3
"""Check applied routes plus every unselected resource and all cell placements."""
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'),str(ROOT/'adapters')]
from import_vivado import sha256
from netlist import read_snapshot, terminals


def check(before, after, routes):
    if not set(routes) <= set(before['nets']):
        raise ValueError('Unknown selected net in candidate routes')
    if before['metadata']['part'] != after['metadata']['part'] or before['cells'] != after['cells']:
        raise ValueError('Device or cell LOC/BEL/reference changed')
    if set(before['nets']) != set(after['nets']):
        raise ValueError('Physical net group domain changed')
    for name, old in before['nets'].items():
        new = after['nets'][name]
        for key in ['type','segments','site_pins','leaf_pins']:
            # Endpoint ordering may change during route database updates.
            keyfn = lambda x: json.dumps(x,sort_keys=True)
            a,b = old[key],new[key]
            if isinstance(a,list): a,b = sorted(a,key=keyfn),sorted(b,key=keyfn)
            if a != b: raise ValueError('Net connectivity/terminals changed: '+name+'/'+key)
        if name not in routes:
            for key in ['nodes','pips']:
                if set(old[key]) != set(new[key]):raise ValueError('Protected net resources changed: '+name)
            if old['status'] != new['status'] or old['fixed'] != new['fixed']:
                raise ValueError('Protected net status/fixed flag changed: '+name)
        else:
            route = routes[name]
            if new['status'] != 'ROUTED' or set(new['nodes']) != set(route['nodes']) or set(new['pips']) != {e['pip'] for e in route['edges']}:
                raise ValueError('Applied node/PIP route differs: '+name)
    return {'all_placements_unchanged':True,'protected_nets_unchanged':len(before['nets'])-len(routes),
            'selected_route_readback_exact':len(routes),'all_connectivity_unchanged':True}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('routes',type=Path);p.add_argument('applied_dir',type=Path)
    args=p.parse_args()
    baseline=ROOT/'data/netlist/routeracc_cost_u280_20261022_v1/snapshot.tsv'
    routes=json.loads(args.routes.read_text())['routes']
    result=check(read_snapshot(baseline),read_snapshot(args.applied_dir/'snapshot.tsv'),routes)
    result['files']={f.name:sha256(f) for f in args.applied_dir.iterdir() if f.is_file()}
    with (args.applied_dir/'readback_check.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
