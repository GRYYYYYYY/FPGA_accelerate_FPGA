"""Resolve cross-tool owners without converting placeholders into free space."""


def resolve_owners(snapshot, names):
    segments={}
    for name,net in snapshot['nets'].items():
        for segment in net['segments']:
            if segment in segments and segments[segment]!=name:
                raise ValueError('Ambiguous physical net segment')
            segments[segment]=name
    result={}
    for raw in sorted(set(names)):
        if raw=='GLOBAL_USEDNET':
            result[raw]={'kind':'unknown_occupied','canonical_nets':[]}
        elif raw in ('GLOBAL_LOGIC0','GLOBAL_LOGIC1'):
            ty='GROUND' if raw=='GLOBAL_LOGIC0' else 'POWER'
            members=sorted(n for n,v in snapshot['nets'].items() if v['type']==ty)
            if not members:raise ValueError('Missing static net class: '+ty)
            resources={(frozenset(snapshot['nets'][n]['nodes']),frozenset(snapshot['nets'][n]['pips'])) for n in members}
            if len(resources)!=1:raise ValueError('Static aliases have different physical resources')
            result[raw]={'kind':'static_net_class','type':ty,'canonical_nets':members}
        elif raw in snapshot['nets']:
            result[raw]={'kind':'canonical_net','canonical_nets':[raw]}
        elif raw in segments:
            result[raw]={'kind':'hierarchy_segment','canonical_nets':[segments[raw]]}
        else:
            result[raw]={'kind':'unresolved','canonical_nets':[]}
    return result
