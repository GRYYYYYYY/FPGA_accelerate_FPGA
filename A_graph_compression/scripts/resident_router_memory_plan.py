"""Five-component static BO sharing/capacity plan; no platform or device claim."""
import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from search_kernel_memory_plan import parse_source,validate_xml,pool,sha,require,MIB,XMLS,SOURCE

ROOT=Path(__file__).resolve().parents[1]
TOPS=['search_kernel_top','search_node_occupancy_top','search_site_occupancy_top',
      'search_resident_snapshot_top','search_route_tree_top']
ALIASES=[
 ['search_kernel_top.roots','search_route_tree_top.roots','search_node_occupancy_top.new_nodes'],
 ['search_kernel_top.packet','search_resident_snapshot_top.packet'],
 ['search_kernel_top.result','search_route_tree_top.search_result'],
 ['search_kernel_top.path','search_route_tree_top.path'],
 ['search_route_tree_top.demands','search_resident_snapshot_top.initial'],
 *[['search_node_occupancy_top.'+a,'search_resident_snapshot_top.node_'+b]
   for a,b in [('meta','meta'),('counts','counts'),('history','history'),('keys','keys'),('flags','flags')]],
 *[['search_site_occupancy_top.'+a,'search_resident_snapshot_top.site_'+b]
   for a,b in [('meta','meta'),('owners','owners'),('history','history')]],
]


def component_source(path,top):
    text=path.read_text()
    signature=re.search(r'extern "C" void '+top+r'\((.*?)\)\s*\{',text,re.S)
    require(signature is not None,'Unsupported component signature')
    pragmas={}
    for port,bundle,depth in re.findall(r'#pragma HLS INTERFACE m_axi port=(\w+) offset=slave bundle=(\w+) depth=(\d+)',text):
        require(port not in pragmas,'Duplicate interface')
        pragmas[port]=(bundle,int(depth))
    args=[]
    for i,decl in enumerate(signature[1].split(',')):
        match=re.fullmatch(r'\s*(const\s+)?uint(32|64)_t\s*\*\s*(\w+)\s*',decl)
        require(match is not None,'Unsupported component argument')
        name=match[3];require(name in pragmas,'Missing interface')
        bundle,depth=pragmas[name];require(depth>0,'Invalid depth')
        args.append(dict(id=i,name=name,pointer=True,const=bool(match[1]),element_bytes=int(match[2])//8,
                         bundle=bundle,depth=depth,payload_bytes=depth*int(match[2])//8))
    require(set(pragmas)=={a['name'] for a in args},'Extra interface')
    return args


class Union:
    def __init__(self,items):self.parent={x:x for x in items}
    def root(self,x):
        require(x in self.parent,'Unknown sharing endpoint '+x)
        while self.parent[x]!=x:x=self.parent[x]
        return x
    def join(self,a,b):self.parent[self.root(b)]=self.root(a)


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
            require((other['depth'],other['element_bytes'])==(first['depth'],first['element_bytes']),'Incompatible shared buffer ABI')
            shared.join(group[0],endpoint)
    allocations={}
    for endpoint,arg in endpoints.items():
        key=shared.root(endpoint)
        row=allocations.setdefault(key,dict(endpoints=[],payload_bytes=arg['payload_bytes'],requested_bytes=(arg['payload_bytes']+alignment-1)//alignment*alignment))
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


def generate():
    kernels={TOPS[0]:parse_source(SOURCE)};files=[SOURCE,Path(__file__).resolve(),ROOT/'scripts/search_kernel_memory_plan.py']
    abi={mode:validate_xml(kernels[TOPS[0]],xml) for mode,xml in XMLS.items()}
    require(abi['csr']==abi['compact'],'Search XML ABIs differ');files+=list(XMLS.values())
    widths={}
    for top in TOPS[1:]:
        src=ROOT/'hardware/vitis'/f'{top}.cpp';kernels[top]=component_source(src,top)
        stem=top.removeprefix('search_').removesuffix('_top')
        review=ROOT/'results'/f'{stem}_synthesis_review_20261024_v1.json';r=json.loads(review.read_text())
        require(r.get('rtl_verified') is False and 'synthesis_verified' in r['status'],'Missing synthesis review')
        for p,h in {**r['files'],**r['source_bindings']}.items():require(sha(p)==h,'Changed audited component '+p)
        # The source copied into synthesis must equal this proposed source ABI.
        copies=[Path(p) for p in r['source_bindings'] if Path(p).name==src.name]
        require(copies and all(sha(p)==sha(src) for p in copies),'Top source differs from audited synthesis')
        expected={'m_axi_'+a['bundle']+'_RDATA' for a in kernels[top]}
        require(set(r['read_data_port_widths'])==expected,'Synthesis bundle mismatch')
        widths[top]=r['read_data_port_widths'];files += [src,review]
    result=allocate(kernels,ALIASES)
    return dict(status='five_component_static_shared_buffer_capacity_checked_device_unverified',kernels=kernels,
                aliases=ALIASES,**result,search_xml_abi=abi,component_synth_read_widths=widths,
                files={str(p):sha(p) for p in files},
                scheduling='Single owner; no concurrent accesses to shared mutable buffers. All producer events must complete before consumers.',
                evidence=dict(platform_linked=False,device_allocated=False,hardware_executed=False),
                limitations=['Nominal U280 capacities inherited from the frozen search-only plan; installed platform topology remains unverified.',
                 'New component exported XO argument/control ABI and memory group intersections are not yet checked.',
                 'XRT BO sharing must use compatible kernel.group_id values and exported memory topology; numerical group IDs alone do not establish compatibility.',
                 'All buffers are counted at full declared depths; retained routes, host state and future hardware outer scheduler are outside this inventory.',
                 'Connectivity is prospective until v++ link and simultaneous BO allocation pass; no bandwidth, timing, power or throughput claim.'])


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    report=generate();a.output.mkdir(parents=True,exist_ok=False)
    report['configs']={}
    for name,mapping in report['layouts'].items():
        path=a.output/(name+'.cfg');path.write_text(connectivity(report['kernels'],mapping));report['configs'][path.name]=sha(path)
    (a.output/'plan.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','pointer_arguments','unique_buffers','total_requested_bytes','hbm_channels_used']}))


if __name__=='__main__':main()
