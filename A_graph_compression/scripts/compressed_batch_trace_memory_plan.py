#!/usr/bin/env python3
"""Source-only disjoint BO plan for the diagnostic trace entry."""
import json
from pathlib import Path
from search_kernel_memory_plan import parse_source,sha,require
from resident_router_memory_plan import allocate,connectivity,ROOT

def main():
    out=ROOT/'hardware/vitis/compressed_batch_trace_memory_v1';require(not out.exists(),'Existing diagnostic plan')
    source=ROOT/'hardware/vitis/search_batch_trace_top_v2.cpp';proof=ROOT/'results/compressed_batch_trace_cases_20261025_v2.json';d=json.loads(proof.read_text())
    require(d['status']=='compressed_batch_all400_native_differential_and_exact_trace_v4_independently_verified_real_workload_pending','Missing CPU trace gate')
    for p,h in d['files'].items():require(sha(p)==h,'Changed CPU gate '+p)
    args=parse_source(source);require(len(args)==45 and sum(a['pointer'] for a in args)==44,'Wrong trace ABI')
    kernels={'search_batch_trace_top_v2':args}
    r=dict(status='diagnostic_batch_source_buffer_capacity_checked_platform_unverified',kernels=kernels,aliases=[],files={str(p):sha(p) for p in [source,proof,Path(__file__).resolve(),ROOT/'scripts/search_kernel_memory_plan.py',ROOT/'scripts/resident_router_memory_plan.py']},actual_xo_abi_verified=False,hardware_executed=False,
           limitations=['Source inventory only; no actual exported kernel.xml offsets, qualifiers, group mappings or XO proof.','All 44 buffers disjoint, including 128MiB trace_data; trace_control/meta each rounded to independent 4096-byte BO.','Nominal HBM/DDR capacity with 16MiB pool reserve; no platform link or simultaneous device allocation.','Fixed trace capacity is not a guarantee that a full real workload fits; sticky overflow invalidates trace acceptance.','No hardware throughput, timing, bandwidth or power proof.'])
    r.update(allocate(kernels,[]));out.mkdir();r['configs']={}
    for name,mapping in r['layouts'].items():
        p=out/(name+'.cfg');p.write_text(connectivity(kernels,mapping));r['configs'][p.name]=sha(p)
    (out/'plan.json').write_text(json.dumps(r,indent=2)+'\n')
    print({k:r[k] for k in ['pointer_arguments','unique_buffers','total_requested_bytes','hbm_channels_used']})
if __name__=='__main__':main()
