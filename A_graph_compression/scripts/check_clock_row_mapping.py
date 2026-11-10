#!/usr/bin/env python3
"""Verify row-clock physical endpoint mappings without authorizing routing use."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from packed_graph import PackedGraph
from real_experiment import write_new


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()


def parse_capture(path):
    endpoints={};sites={};configs={};complete=None
    for line in path.read_text().splitlines():
        f=line.split('\t')
        if f[0]=='endpoint':
            if len(f)!=3 or f[1] in endpoints:raise ValueError('Duplicate/malformed endpoint')
            endpoints[f[1]]={'node':f[2],'pins':[]}
        elif f[0]=='pin':
            if len(f)!=5 or f[1] not in endpoints or f[3] not in ('IN','OUT') or f[4] not in ('0','1'):
                raise ValueError('Malformed endpoint pin')
            endpoints[f[1]]['pins'].append({'pin':f[2],'direction':f[3],'used':f[4]=='1'})
        elif f[0]=='site':
            if f[1] in sites:raise ValueError('Duplicate site')
            sites[f[1]]=f[2]
        elif f[0]=='config':
            key=(f[1],f[2])
            if key in configs:raise ValueError('Duplicate BEL config')
            configs[key]=f[3]
        elif f[0]=='complete':
            if complete is not None:raise ValueError('Duplicate completion')
            complete=tuple(map(int,f[1:]))
    if complete!=(len(endpoints),len(sites)):raise ValueError('Incomplete capture')
    for e in endpoints.values():
        if len(e['pins'])!=1:raise ValueError('Ambiguous endpoint pin')
        pin=e['pins'][0];site=pin['pin'].split('/')[0]
        if sites.get(site)!='BUFCE_ROW_FSR':raise ValueError('Unexpected site type')
    return endpoints,sites,configs


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    raw=ROOT/'data/raw/region_u280_20261022_v1';capture=raw/'clock_row_pins_20261023_v1.tsv'
    endpoints,sites,configs=parse_capture(capture)
    pips={}
    for line in (raw/'pseudo_pips.tsv').read_text().splitlines():
        f=line.split('\t')
        if f[0]=='pip' and 'CLK_BUFCE_ROW_FSR' in f[1]:
            if f[1] in pips:raise ValueError('Duplicate PIP')
            pips[f[1]]=f[2:]
    if len(pips)!=26 or len(endpoints)!=39 or len(sites)!=13:raise ValueError('Unexpected physical domain')
    records={}
    for name,(up,down,tile) in pips.items():
        source=endpoints[up]['pins'][0];destination=endpoints[down]['pins'][0]
        site=source['pin'].split('/')[0]
        if source['direction']!='IN' or destination['direction']!='OUT' or destination['pin'].split('/')[0]!=site:
            raise ValueError('Inconsistent site/directions')
        records[name]={'site':site,'source':dict(source,node=endpoints[up]['node'],wire=up),
            'destination':dict(destination,node=endpoints[down]['node'],wire=down),
            'configuration_observed':{bel+'/'+prop:value for (bel,prop),value in configs.items() if bel.startswith(site+'/')},
            'status':'endpoint_mapping_only_not_legality_verified'}
    paths=[capture,raw/'pseudo_pips.tsv',Path(__file__),ROOT/'adapters/export_clock_row_pins_20261023_v1.tcl',
           ROOT/'results/site_full_stage_20261023_v1.json']
    checked={}
    for mode in ('csr','compact'):
        fixture=ROOT/f'data/derived/native_site_{mode}_inputs_20261023_v1/manifest.json'
        manifest=json.loads(fixture.read_text());image_path=Path(manifest['image'])
        if digest(image_path)!=manifest['files'][str(image_path)]:raise ValueError('Packed image changed')
        graph=PackedGraph(image_path);strings={graph.text(i):i for i in range(len(graph.str_offsets)-1)}
        tiles={graph.text(t[0]):i for i,t in enumerate(graph.tiles)}
        for name,(up,down,tile) in pips.items():
            tile_id=tiles[tile];up_id=strings[up.split('/',1)[1]];down_id=strings[down.split('/',1)[1]]
            src=graph.aliases[tile_id,up_id];dst=graph.aliases[tile_id,down_id]
            if graph.text(graph.nodes[src][0])!=endpoints[up]['node'] or graph.text(graph.nodes[dst][0])!=endpoints[down]['node']:
                raise ValueError('Canonical alias differs from live Vivado')
            matches=[e for e in graph.numeric_neighbors(src) if e[:5]==(dst,tile_id,strings[name.split('/',1)[1]],up_id,down_id) and e[6]==0]
            if len(matches)!=1:raise ValueError('Missing/ambiguous forward PIP')
            attrs=graph.attrs(matches[0][5])
            if attrs.get('IS_PSEUDO')!='1' or attrs.get('IS_DIRECTIONAL')!='1':raise ValueError('Incorrect PIP attributes')
        checked[mode]=len(pips);paths.extend([fixture,image_path])
    report={'status':'all_row_clock_endpoints_match_both_packed_images','counts':{'pips':len(pips),'endpoints':len(endpoints),'sites':len(sites)},
        'checked_modes':checked,'clock_row_pips':records,
        'families':dict(Counter(r['source']['pin'].split('/')[1]+'->'+r['destination']['pin'].split('/')[1] for r in records.values())),
        'files':{str(path):digest(path) for path in paths},
        'configuration_scope':'Observed on the current physically validated site candidate; IS_USED=0 does not establish availability.',
        'remaining':['Determine and validate the CE/CLK route-through configurations, input constant/inversion and delay/test controls.',
                     'Establish protected and dynamic intra-site ownership before admitting any instance to the routing requirement adapter.']}
    write_new(a.output,report);print(json.dumps({k:report[k] for k in ('status','counts','checked_modes','families')}))


if __name__=='__main__':main()
