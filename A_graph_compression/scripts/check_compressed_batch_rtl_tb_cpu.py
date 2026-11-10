#!/usr/bin/env python3
"""Audit full port depths and retained complete payloads before RTL setup."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
from check_vitis_kernel import digest,require
from search_kernel_memory_plan import parse_source
from read_batch_trace_v4 import decode_file
ROOT=Path(__file__).resolve().parents[1]
def snapshot(path,args,mode,transaction,trace_path):
    ports=[a for a in args if a['pointer']];rows=[];small={};trace_meta=None
    with path.open('rb') as stream:
        require(stream.read(32)==struct.pack('<4Q',0x4142534e41503031,mode,transaction,44),'Wrong snapshot header')
        for arg in ports:
            raw=stream.read(24);require(len(raw)==24,'Truncated port descriptor')
            require(struct.unpack('<3Q',raw)==(arg['id'],arg['element_bytes'],arg['depth']),'Port depth/width/order mismatch')
            total=arg['depth']*arg['element_bytes'];remain=total;hash_=hashlib.sha256();data=[];offset=0
            trace=None
            if arg['name']=='trace_data':
                require(trace_meta is not None,'Trace metadata order changed');trace=trace_path.open('rb');require(trace.read(64)==struct.pack('<8Q',*trace_meta),'Export metadata differs from complete port snapshot')
            while remain:
                block=stream.read(min(remain,8388608));require(block,'Truncated full port payload');hash_.update(block)
                if total<=4096:data.append(block)
                if trace is not None:
                    active=min(len(block),max(0,trace_meta[2]*8-offset))
                    require(trace.read(active)==block[:active],'Export differs from snapshot committed trace bytes')
                remain-=len(block);offset+=len(block)
            if trace is not None:require(trace.read(1)==b'','Extra exported trace data');trace.close()
            if data:
                raw=b''.join(data);small[arg['name']]=list(struct.unpack('<%d%s'%(arg['depth'],'I' if arg['element_bytes']==4 else 'Q'),raw))
                if arg['name']=='trace_meta':trace_meta=small['trace_meta']
            rows.append(dict(id=arg['id'],name=arg['name'],depth=arg['depth'],element_bytes=arg['element_bytes'],sha256=hash_.hexdigest()))
        require(stream.read(1)==b'','Extra snapshot payload')
    require(path.stat().st_size==32+44*24+sum(a['depth']*a['element_bytes'] for a in ports),'Incorrect complete snapshot size')
    return rows,small

def audit(bundle,output):
    require(not output.exists(),'Existing full-depth CPU audit');plan=json.loads((bundle/'plan.json').read_text());state=json.loads((bundle/'state.json').read_text())
    require(state['status']=='complete' and state['completed']==[0,1],'Incomplete full-depth CPU run')
    for p,h in plan['files'].items():require(digest(p)==h,'Changed full-depth source '+p)
    source=bundle/'source/search_batch_trace_top_v2.cpp';args=parse_source(source);require(len(args)==45 and sum(a['pointer'] for a in args)==44,'Wrong source ABI')
    files=dict(plan['files']);results=[]
    for mode in [0,1]:
        for phase in ['compile','run']:
            path=bundle/f'{phase}_{mode}.log';rp=bundle/f'{phase}_{mode}.receipt.json';receipt=json.loads(rp.read_text())
            require(receipt['exit_code']==0 and receipt['log_sha256']==digest(path),'Failed full-depth '+phase)
            if phase=='compile':require(re.findall(r'warning: (.*)',path.read_text())==["unused parameter ‘trace_control’ [-Wunused-parameter]"],'Unexpected compiler warnings')
            else:require(f'FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode={mode} ports=44 transactions=4' in path.read_text(),'Missing full-depth contract')
            for p in [path,rp]:files[str(p)]=digest(p)
        constants={}
        for transaction in range(4):
            path=bundle/f'cpu_{mode}_{transaction}.bin';trace=bundle/f'trace_mode_{mode}_case_{transaction}.bin';rows,small=snapshot(path,args,mode,transaction,trace)
            for row in rows:
                if row['name'] in ['image','config','query_table','all_sinks','trace_control']:
                    name=row['name']
                    if name in constants:require(row['sha256']==constants[name],'Read-only fixture changed '+name)
                    constants[name]=row['sha256']
            require(small['trace_control']==[16777216,0,0,0,0,0,0,0],'Reduced trace capacity')
            if transaction<3:
                decoded=decode_file(trace,4);require(decoded['complete_batch']==(transaction!=1),'Wrong seeded-state acceptance')
                require(decoded['terminal']==small['batch_result'],'Trace terminal differs from complete result port')
            else:
                try:decode_file(trace,4)
                except ValueError:pass
                else:raise ValueError('Invalid preflight trace wrongly accepted')
            results.append(dict(mode=mode,transaction=transaction,snapshot=str(path),bytes=path.stat().st_size,ports=rows,batch_result=small['batch_result']))
            for p in [path,trace]:files[str(p)]=digest(p)
        files[str(bundle/f'mode_{mode}')]=digest(bundle/f'mode_{mode}')
    for p in [bundle/'plan.json',bundle/'state.json',Path(__file__).resolve(),ROOT/'scripts/read_batch_trace_v4.py',ROOT/'scripts/read_round_trace_v2.py']:files[str(p)]=digest(p)
    r=dict(status='compressed_batch_full44_declared_depth_cpu_snapshots_verified_rtl_pending',files=files,results=results,ports=44,transactions_per_mode=4,modes=2,limits=['All declared pointer extents allocated and complete payload retained; logical test graph remains4 nodes','CPU snapshots are future C/RTL reference, not RTL output or device proof','Read-only fixture checks here are host/C observations; generated RTL AXI write-region integrity needs separate setup validation','Local temporary snapshots require durable archival'])
    with output.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
    print(r['status'],results[0]['bytes'],flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();audit(a.bundle.resolve(),a.output.resolve())
