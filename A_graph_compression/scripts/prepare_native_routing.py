#!/usr/bin/env python3
"""Bind canonical numeric queries/protection to an audited real packed graph."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'adapters')]
from import_vivado import sha256
from netlist import read_snapshot, ownership
from packed_graph import PackedGraph
from real_experiment import write_new


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--experiment',type=Path,default=ROOT/'data/derived/region_all_nets_cap8_20261022_v1')
    p.add_argument('--config',type=Path,default=ROOT/'configs/region_u280_v1.json')
    p.add_argument('--mode',choices=['csr','compact'],required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();audit=json.loads((a.experiment/'report.json').read_text())
    cfg=json.loads(a.config.read_text());capture_path=ROOT/cfg['output_dir']/'capture.json'
    capture=json.loads(capture_path.read_text());snapshot_path=ROOT/cfg['snapshot']
    for path,key in ((a.config,'config'),(capture_path,'capture'),(snapshot_path,'snapshot')):
        if sha256(path)!=audit['inputs'][key]:raise ValueError('Audited input changed: '+str(path))
    for item in capture['files'].values():
        if sha256(ROOT/item['path'])!=item['sha256']:raise ValueError('Capture changed')
    for name in ('queries.json','csr.agr','compact.agr'):
        if sha256(a.experiment/name)!=audit['artifacts'][name]:raise ValueError('Audited artifact changed: '+name)
    # Template-only strings/attributes can shift pool IDs. Bind every numeric
    # fixture to its own image; canonical names remain the comparison domain.
    image=PackedGraph(a.experiment/(a.mode+'.agr'))
    names=[image.text(n[0]) for n in image.nodes]
    if names!=sorted(set(names)):raise ValueError('Node IDs do not preserve canonical lexical order')
    node_ids={n:i for i,n in enumerate(names)}
    strings={image.text(i):i for i in range(len(image.str_offsets)-1)}
    tiles={image.text(t[0]):i for i,t in enumerate(image.tiles)}
    queries=json.loads((a.experiment/'queries.json').read_text())
    net_names=[q['net'] for q in queries]
    if len(set(net_names))!=len(net_names):raise ValueError('Duplicate net queries')
    protected,pips=ownership(read_snapshot(snapshot_path),net_names)
    protected_ids=sorted(node_ids[n] for n in protected if n in node_ids)
    protected_pips=[]
    for name in pips:
        tile,suffix=name.split('/',1)
        if tile in tiles and suffix in strings:protected_pips.append((tiles[tile],strings[suffix]))
    blocked_attrs=[]
    for aid in range(len(image.attr_offsets)-1):
        attrs=image.attrs(aid)
        if any(attrs.get(k)=='1' for k in ('IS_EXCLUDED_PIP','IS_TEST_PIP')):blocked_attrs.append(aid)
    numeric=[{'net_id':i,'net':q['net'],'source':node_ids[q['source']],
              'sinks':[node_ids[n] for n in q['sinks']]} for i,q in enumerate(queries)]
    lines=['NATIVE_ROUTING_V1',str(len(names)),str(len(protected_ids)),*map(str,protected_ids),
           str(len(protected_pips)),*[f'{t} {p}' for t,p in sorted(protected_pips)],
           str(len(blocked_attrs)),*map(str,blocked_attrs),str(len(numeric))]
    lines.extend(' '.join(map(str,[q['net_id'],q['source'],len(q['sinks']),*q['sinks']])) for q in numeric)
    a.output.mkdir(parents=True,exist_ok=False)
    fixture=a.output/'routing.txt';fixture.write_text('\n'.join(lines)+'\n')
    write_new(a.output/'queries.json',numeric)
    inputs=[a.config,capture_path,snapshot_path,a.experiment/'report.json',a.experiment/'queries.json',
            a.experiment/'csr.agr',a.experiment/'compact.agr',Path(__file__),ROOT/'src/packed_graph.py',
            ROOT/'src/netlist.py',ROOT/'adapters/import_vivado.py']
    write_new(a.output/'manifest.json',{'status':'prepared','mode':a.mode,
        'image':str((a.experiment/(a.mode+'.agr')).resolve()),
        'scope':'Full audited canonical-node workload; physical/site legality is not implied.',
        'nodes':len(names),'queries':len(queries),'protected_nodes_in_image':len(protected_ids),
        'protected_nodes_outside_image':len(set(protected)-set(node_ids)),
        'protected_pips':len(protected_pips),'blocked_attribute_ids':len(blocked_attrs),
        'canonical_node_order_sha256':hashlib.sha256(json.dumps(names,ensure_ascii=False).encode()).hexdigest(),
        'files':{str(p.resolve()):sha256(p) for p in inputs},
        'outputs':{p.name:sha256(p) for p in (fixture,a.output/'queries.json')}})
    print(json.dumps({'output':str(a.output),'queries':len(queries),'nodes':len(names)}))


if __name__=='__main__':main()
