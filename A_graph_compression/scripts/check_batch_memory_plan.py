"""Independently account unique BOs, shared-port banks and candidate configs."""
import argparse
import json
from pathlib import Path
from search_kernel_memory_plan import pool,sha,require,MIB


def audit(directory,output):
    require(not output.exists(),'Existing audit')
    path=directory/'plan.json';r=json.loads(path.read_text())
    for p,h in r['files'].items():require(sha(p)==h,'Changed input '+p)
    from search_kernel_memory_plan import parse_source
    root=Path(__file__).resolve().parents[1];source=root/'hardware/vitis/search_batch_top.cpp'
    require(r['kernels']=={'search_batch_top':parse_source(source)},'Changed source/manifest argument inventory')
    proof=json.loads((root/'results/batch_component_20261025_v1.json').read_text())
    for p,h in proof['files'].items():require(sha(p)==h,'Changed complete batch proof '+p)
    endpoints={k+'.'+a['name']:a for k,aa in r['kernels'].items() for a in aa if a['pointer']}
    require(len(r['kernels'])==1 and len(endpoints)==41,'Wrong full component inventory')
    seen={};total=0;payload=0
    for name,row in r['allocations'].items():
        require(row['endpoints'] and len(row['endpoints'])==len(set(row['endpoints'])),'Duplicate allocation endpoint')
        sizes=set();kernels=set()
        for e in row['endpoints']:
            require(e in endpoints and e not in seen,'Unknown/duplicate endpoint')
            k=e.split('.')[0];require(k not in kernels,'Aliasing within component');kernels.add(k)
            a=endpoints[e];sizes.add(a['depth']*a['element_bytes']);seen[e]=name
        require(len(sizes)==1 and sizes.pop()==row['payload_bytes'],'Shared buffer size mismatch')
        aligned=(row['payload_bytes']+4095)//4096*4096
        require(row['requested_bytes']==aligned,'Incorrect alignment')
        total+=aligned;payload+=row['payload_bytes']
    require(set(seen)==set(endpoints) and r['unique_buffers']==len(r['allocations'])==41,'Incomplete BO inventory')
    require(r['total_requested_bytes']==total and r['total_payload_bytes']==payload,'Incorrect shared accounting')
    for group in r['aliases']:require(len({seen[e] for e in group})==1,'Broken zero-copy sharing')
    config_hashes={}
    for name,mapping in r['layouts'].items():
        require(set(mapping)==set(endpoints),'Incomplete connectivity')
        groups={};bundles={};occupied=set()
        for bo,row in r['allocations'].items():
            banks={mapping[e] for e in row['endpoints']};require(len(banks)==1,'Shared BO connected to different banks')
            memory=banks.pop();channels,capacity=pool(memory)
            if memory not in groups:
                require(not occupied.intersection(channels),'Overlapping memory pools');occupied.update(channels)
                groups[memory]=[0,capacity]
            groups[memory][0]+=row['requested_bytes']
        for e,a in endpoints.items():
            key=(e.split('.')[0],a['bundle'])
            if key in bundles:require(bundles[key]==mapping[e],'AXI bundle bank mismatch')
            bundles[key]=mapping[e]
        for size,capacity in groups.values():require(size+16*MIB<=capacity,'Pool aggregate capacity exceeded')
        cfg=directory/(name+'.cfg');lines=[x.strip() for x in cfg.read_text().splitlines() if x.strip() and not x.startswith('#')]
        expected=['[connectivity]']+[f'nk={k}:1:{k}_1' for k in r['kernels']]
        expected += [f'sp={k}_1.{a["name"]}:{mapping[k+"."+a["name"]]}' for k,aa in r['kernels'].items() for a in aa if a['pointer']]
        require(lines==expected and sha(cfg)==r['configs'][cfg.name],'Changed/incorrect candidate config')
        config_hashes[str(cfg)]=sha(cfg)
    evidence={'status':'integrated_batch_source_buffers_independently_checked_actual_abi_platform_pending',
              'files':{**proof['files'],**r['files'],str(path):sha(path),**config_hashes,str(Path(__file__).resolve()):sha(__file__)},
              'pointer_arguments':41,'unique_buffers':41,'requested_bytes':total,
              'hardware_executed':False,'limitations':r['limitations']}
    with output.open('x') as f:json.dump(evidence,f,indent=2);f.write('\n')
    print(evidence['status'],total)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();audit(a.directory.resolve(),a.output.resolve())
