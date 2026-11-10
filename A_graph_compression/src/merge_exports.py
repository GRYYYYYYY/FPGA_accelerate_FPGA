"""Strict canonical merge: shared records must agree, source rows stay disjoint."""
from canonical_graph import validate


def merge_graphs(graphs,expected_sources,metadata):
    result={'schema':'canonical_graph_v1','dataset_kind':'real_device_region','metadata':dict(metadata),
            'provenance':{},'seed_tiles':[],'selections':[],
            **{key:{} for key in ['tiles','nodes','aliases','pips','roots','oracle_children']},'edges':[]}
    sources=set();seeds=set()
    for graph in graphs:
        validate(graph)
        if graph['metadata']['part']!=metadata['part']:raise ValueError('Shard part mismatch')
        for key in ['vivado_version','vivado_build']:
            if key in graph['metadata']:
                value=graph['metadata'][key]
                if key in result['metadata'] and result['metadata'][key]!=value:
                    raise ValueError('Shard tool version mismatch: '+key)
                result['metadata'][key]=value
        overlap=sources&set(graph['roots'])
        if overlap:raise ValueError('Duplicate source rows across shards: '+str(sorted(overlap)[:3]))
        sources.update(graph['roots'])
        for key in ['tiles','nodes','aliases','pips','roots','oracle_children']:
            for name,value in graph[key].items():
                if name in result[key] and result[key][name]!=value:
                    raise ValueError('Conflicting '+key+' record: '+name)
                result[key][name]=value
        result['edges'].extend(graph['edges']);result['selections'].extend(graph['selections'])
        seeds.update(graph['seed_tiles'])
    if sources!=set(expected_sources):raise ValueError('Merged source domain differs from frozen selection')
    result['seed_tiles']=sorted(seeds)
    validate(result)
    return result


def write_tsv(path,graph):
    """Canonical v1 TSV, exclusive creation, complete marker only after all rows."""
    validate(graph)
    with path.open('x') as f:
        def row(*values):
            values=list(map(str,values))
            if any(any(c in value for c in '\t\r\n') for value in values):raise ValueError('Control character in TSV')
            f.write('\t'.join(values)+'\n')
        row('meta','schema','vivado_graph_tsv_v1')
        for key,value in sorted(graph['metadata'].items()):
            if key!='schema':row('meta',key,value)
        for key in ['tiles','nodes']:
            for name,attrs in sorted(graph[key].items()):
                row('tile' if key=='tiles' else 'node',name,*[v for k in sorted(attrs) for v in (k,attrs[k])])
        for wire,node in sorted(graph['aliases'].items()):row('alias',wire,node)
        for name,pip in sorted(graph['pips'].items()):
            attrs=pip['attributes'];row('pip',name,pip['up_wire'],pip['down_wire'],*[v for k in sorted(attrs) for v in (k,attrs[k])])
        for root,counts in sorted(graph['roots'].items()):row('root',root,counts['pip_count'],counts['child_count'])
        for edge in graph['edges']:row('edge',*[edge[k] for k in ['pip','direction','src','dst','src_wire','dst_wire']])
        for root,children in sorted(graph['oracle_children'].items()):
            for child in children:row('oracle_child',root,child)
        for tile in graph['seed_tiles']:row('seed_tile',tile)
        for selection in graph['selections']:row('selection',selection['node'],selection['seed_tile'],selection['reason'])
        row('complete',len(graph['roots']),len(graph['nodes']),len(graph['pips']))
