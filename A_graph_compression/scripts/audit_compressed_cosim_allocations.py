#!/usr/bin/env python3
"""Validate generated wrapper allocation extents without modifying frozen setup."""
import hashlib
import json
from pathlib import Path
import re
import os
import tempfile
ROOT=Path(__file__).resolve().parents[1]
def main():
    inv=ROOT/'hardware/vitis/compressed_batch_rtl_full_depth_inventory.json'
    wrapper=Path('/tmp/A_graph_compression_recovery_20261025_v1/compressed_batch_cosim_project/solution/sim/wrapc_pc/apatb_search_batch_trace_top_v2.cpp')
    text=wrapper.read_text();ports=json.loads(inv.read_text())['ports'];lookup={p['name']:p for p in ports};seen=set();rows=[]
    pattern=r'(__xlx_offset_byte_param_\w+)\s*=\s*(\d+)\*(\d+);'
    addresses={name:(int(a)*int(b),int(b)) for name,a,b in re.findall(pattern,text)}
    for match in re.finditer(r'port(\d+)\.param = \{ ([^}]+) \};\s*port\1\.depth = \{ ([^}]+) \};',text):
        params=[x.strip().removeprefix('__xlx_apatb_param_') for x in match[2].split(',')]
        depths=[int(x.strip()) for x in match[3].split(',')]
        assert len(params)==len(depths)
        spans=[]
        for name,depth in zip(params,depths):
            canonical={'image_r':'image','config_r':'config'}.get(name,name)
            assert canonical in lookup and canonical not in seen,canonical
            seen.add(canonical);p=lookup[canonical]
            key='__xlx_offset_byte_param_'+name
            if key in addresses:
                start,unit=addresses[key]
            else:
                assert len(params)==1
                assert re.search(r'port'+match[1]+r'\.offset = \{\s*\};',text)
                model=wrapper.parent.parent/'verilog'/('AESL_axi_master_'+p['bundle']+'.v')
                width=re.search(re.escape(p['bundle'])+r"_DATA_BITWIDTH\s*=\s*32'd\s*(\d+)",model.read_text())
                assert width is not None
                start,unit=0,int(width[1])//8
            size=depth*unit
            assert size>=p['payload_bytes'],(canonical,size,p['payload_bytes'])
            spans.append(dict(name=canonical,start=start,end=start+size,allocated_bytes=size,declared_bytes=p['payload_bytes'],readonly=p['const']))
        ordered=sorted(spans,key=lambda x:x['start'])
        assert all(a['end']<=b['start'] for a,b in zip(ordered,ordered[1:])),ordered
        rows.append(dict(wrapper_port=int(match[1]),regions=spans))
    assert seen==set(lookup),(len(seen),set(lookup)-seen)
    files={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [inv,wrapper,Path(__file__).resolve()]}
    report=dict(status='all44_generated_wrapper_regions_cover_declared_depths_and_are_disjoint_within_each_bundle',allocations=rows,files=files,limits=['Static generated wrapper allocation proof only; no RTL execution or AXI write integrity proof','Scalar pointer address transaction files are not the memory payload files'])
    target=ROOT/'results/compressed_batch_cosim_allocations_20261025_v1.json'
    if target.exists():raise FileExistsError(target)
    fd,tmp=tempfile.mkstemp(dir=target.parent)
    with os.fdopen(fd,'w') as f:json.dump(report,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,target);print(report['status'])
if __name__=='__main__':main()
