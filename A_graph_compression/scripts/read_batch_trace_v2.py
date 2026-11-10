#!/usr/bin/env python3
"""Strengthen frozen mixed reader with demand inheritance and net ledger totals."""
import argparse
import json
from pathlib import Path
from read_search_trace import require
from read_batch_trace import decode_file as base_file, decode_words as base_words

def preserves(previous,current):
    if not set(previous['signals']).issubset(current['signals']):return False
    bits={f:(m,v) for f,m,v in current['bits']}
    for field,mask,value in previous['bits']:
        if field not in bits:return False
        newmask,newvalue=bits[field]
        if mask&~newmask or (newvalue^value)&mask:return False
    values=dict(current['values'])
    return all(values.get(field)==value for field,value in previous['values'])

def strengthen(d):
    snapshots={(n['iteration'],n['query']):n for n in d['nets']}
    states={}
    empty=dict(signals=[],bits=[],values=[])
    for search in d['searches']:
        key=(search['iteration'],search['query']>>32)
        previous=states.get(key,empty)
        if search['result'][0]==0:
            current=search['demands']
            require(preserves(previous,current),'Successful search dropped/changed an inherited demand')
            if not search['path']:
                require(all(previous[k]==current[k] for k in ['signals','bits','values']),'Zero-edge search changed demands')
            states[key]=current
    for key,n in snapshots.items():
        previous=states.get(key,empty)
        require(all(previous[k]==n['demands'][k] for k in ['signals','bits','values']),'Net demand differs from final inherited state')
    # Seeded ledgers can contain external nets; complete totals require reset.
    if d['initial_state_verified']:
        routes={};edges={};sites={}
        for n in d['nets']:
            net=n['net'];routes[net]=n['roots'];edges[net]=n['edges'];sites[net]=n['site_owners']
            total_nodes=sum(map(len,routes.values()));total_edges=sum(map(len,edges.values()))
            require(n['node_meta'][2]==total_nodes and n['retained_meta'][2]==total_nodes and n['retained_meta'][4]==len(routes),'Net global node/retention totals mismatch')
            require(n['edge_meta'][2]==total_edges and n['edge_meta'][4]==sum(bool(v) for v in edges.values()),'Net global edge totals mismatch')
            require(n['site_meta'][2]==sum(map(len,sites.values())),'Net global site totals mismatch')
    d['status']=d['status']+'_demand_inheritance_and_net_totals_verified'
    return d

def decode_words(words,nodes):return strengthen(base_words(words,nodes))
def decode_file(path,nodes):return strengthen(base_file(path,nodes))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('path',type=Path);p.add_argument('--nodes',type=int,required=True);a=p.parse_args();print(json.dumps(decode_file(a.path,a.nodes),indent=2))
