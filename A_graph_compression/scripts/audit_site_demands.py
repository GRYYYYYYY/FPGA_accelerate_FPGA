#!/usr/bin/env python3
"""Diagnose candidate LUT route-through demands; never certify physical legality."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from lut_equation import equivalent


def audit(raw, routes_path):
    sites = defaultdict(list)
    for line in (raw/'pseudo_sites.tsv').read_text().splitlines():
        f = line.split('\t')
        if f[0] == 'site': sites[f[1]].append((f[2],f[3]))
    configs = {}
    for line in (raw/'bel_config.tsv').read_text().splitlines():
        f = line.split('\t')
        if f[0] == 'config': configs[(f[1],f[2])] = f[3]
    pseudo = {}
    for line in (raw/'pseudo_pips.tsv').read_text().splitlines():
        f = line.split('\t')
        if f[0] == 'pip': pseudo[f[1]] = f[2:]
    routes = json.loads(routes_path.read_text())['routes']
    demands = []; unresolved = []; users = defaultdict(set)
    for net, route in routes.items():
        for edge in route['edges']:
            pip = edge['pip']
            if pip not in pseudo: continue
            src,dst,tile = pseudo[pip]
            a = re.fullmatch(r'CLE_CLE_[LM]_SITE_0_([A-H])([1-6])',src.split('/')[-1])
            b = re.fullmatch(r'CLE_CLE_[LM]_SITE_0_([A-H])(?:MUX|_O)',dst.split('/')[-1])
            candidates = [s for s,t in sites[tile] if t in ('SLICEL','SLICEM')]
            if not a or not b or a[1] != b[1] or len(candidates) != 1:
                unresolved.append({'net':net,'pip':pip}); continue
            bel = candidates[0]+'/'+a[1]+'6LUT'
            required = 'O6=A'+a[2]
            baseline = configs.get((bel,'CONFIG.EQN'))
            try:
                semantic_match = equivalent(baseline or '',required)
            except ValueError:
                semantic_match = None
            users[bel].add(net)
            demands.append({'net':net,'pip':pip,'bel':bel,'inferred_equation':required,
                            'baseline_equation':baseline,
                            'baseline_semantic_match':semantic_match,
                            'baseline_differs':baseline != required})
    return {'status':'diagnostic_only','demands':demands,'unresolved':unresolved,
            'shared_bels':{b:sorted(n) for b,n in users.items() if len(n)>1},
            'limitations':['Equation requirements inferred from recognized CLE input/output names; validate against Vivado before enforcing.',
                           'Baseline equation mismatch alone does not establish protected ownership or illegality.',
                           'Site mux, LUT5/6 sharing, constants and dynamic configuration compatibility remain to be modeled.']}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--raw',type=Path,required=True)
    p.add_argument('--routes',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=audit(a.raw,a.routes)
    paths=[a.routes,*[a.raw/n for n in ('pseudo_sites.tsv','bel_config.tsv','pseudo_pips.tsv')],Path(__file__)]
    r['input_sha256']={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in paths}
    with a.output.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps({'recognized_demands':len(r['demands']),'unresolved':len(r['unresolved']),
                      'shared_bels':len(r['shared_bels']),
                      'baseline_mismatches':sum(d['baseline_differs'] for d in r['demands'])}))


if __name__=='__main__':main()
