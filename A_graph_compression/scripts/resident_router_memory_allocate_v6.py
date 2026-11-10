"""Allocate a maximum-depth u32 path BO; preserve strict other alias contracts."""
from resident_router_memory_plan import Union,pool,require,MIB

def allocate(kernels,aliases,alignment=4096,reserve=16*MIB):
    require(alignment>0 and not alignment&(alignment-1),'Invalid alignment')
    require(reserve>=0,'Invalid reserve')
    endpoints={k+'.'+a['name']:{**a,'kernel':k} for k,aa in kernels.items() for a in aa if a['pointer']}
    shared=Union(endpoints)
    for group in aliases:
        require(len(group)>1 and len(set(group))==len(group),'Invalid alias group')
        first=endpoints.get(group[0]);require(first is not None,'Unknown alias')
        for endpoint in group:
            require(endpoint in endpoints,'Unknown alias')
            other=endpoints[endpoint]
            require(other['element_bytes']==first['element_bytes'],'Incompatible shared element width')
            if other['depth']!=first['depth']:
                require(set(group)<={'search_kernel_top.path','search_route_tree_top.path','search_retained_edges_top.path'} and first['element_bytes']==4,'Unapproved unequal-depth alias')
            shared.join(group[0],endpoint)
    allocations={}
    for endpoint,arg in endpoints.items():
        key=shared.root(endpoint)
        row=allocations.setdefault(key,dict(endpoints=[],payload_bytes=arg['payload_bytes'],requested_bytes=(arg['payload_bytes']+alignment-1)//alignment*alignment))
        row['payload_bytes']=max(row['payload_bytes'],arg['payload_bytes'])
        row['requested_bytes']=(row['payload_bytes']+alignment-1)//alignment*alignment
        row['endpoints'].append(endpoint)
    # A component's pointers must be disjoint even when their banks coincide.
    for row in allocations.values():
        names=[endpoints[x]['kernel'] for x in row['endpoints']]
        require(len(names)==len(set(names)),'Aliasing within one component violates its buffer contract')
    banks=Union(allocations)
    bundles={}
    for endpoint,arg in endpoints.items():
        identity=(arg['kernel'],arg['bundle']);bo=shared.root(endpoint)
        if identity in bundles:banks.join(bundles[identity],bo)
        else:bundles[identity]=bo
    groups={}
    for bo,row in allocations.items():groups.setdefault(banks.root(bo),[]).append(bo)
    split={};channel=0;summary=[]
    for group,bos in groups.items():
        size=sum(allocations[bo]['requested_bytes'] for bo in bos)
        width=(size+reserve+256*MIB-1)//(256*MIB)
        require(channel+width<=32,'Insufficient nominal HBM channels')
        memory=f'HBM[{channel}]' if width==1 else f'HBM[{channel}:{channel+width-1}]'
        _,capacity=pool(memory);require(size+reserve<=capacity,'HBM capacity exceeded')
        summary.append(dict(memory=memory,buffers=bos,requested_bytes=size,reserve_bytes=reserve,capacity_bytes=capacity))
        for bo in bos:
            allocations[bo]['hbm_group']=memory
            for endpoint in allocations[bo]['endpoints']:split[endpoint]=memory
        channel+=width
    ddr={x:'DDR[0]' for x in endpoints}
    total=sum(a['requested_bytes'] for a in allocations.values())
    require(total+reserve<=pool('DDR[0]')[1],'DDR capacity exceeded')
    return dict(allocations=allocations,hbm_groups=summary,hbm_channels_used=channel,
                layouts={'hbm_shared_buffers':split,'ddr_shared_buffers':ddr},
                pointer_arguments=len(endpoints),unique_buffers=len(allocations),
                total_payload_bytes=sum(a['payload_bytes'] for a in allocations.values()),total_requested_bytes=total)


def connectivity(kernels,mapping):
    lines=['# Static candidate; validate exported XO arguments, platform link and BO groups before use.','[connectivity]']
    lines += [f'nk={k}:1:{k}_1' for k in kernels]
    lines += [f'sp={k}_1.{a["name"]}:{mapping[k+"."+a["name"]]}' for k,aa in kernels.items() for a in aa if a['pointer']]
    return '\n'.join(lines)+'\n'

