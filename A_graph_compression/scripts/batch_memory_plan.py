"""Source-based full batch BO inventory, separate from the frozen multi-CU plans."""
import json
from pathlib import Path
from search_kernel_memory_plan import parse_source,sha,require
from resident_router_memory_plan import allocate,connectivity,ROOT

def main():
    out=ROOT/'hardware/vitis/search_batch_memory_v1';require(not out.exists(),'Existing batch memory candidate')
    source=ROOT/'hardware/vitis/search_batch_top.cpp';proof_path=ROOT/'results/batch_component_20261025_v1.json';proof=json.loads(proof_path.read_text())
    require(proof['status']=='batch_full_negotiation_intermediate_differential_verified_real_workload_pending','Missing complete batch CPU gate')
    require(proof['files'][str(source)]==sha(source),'Changed actual batch source')
    args=parse_source(source);require(len(args)==42 and sum(a['pointer'] for a in args)==41,'Different batch ABI')
    kernels={'search_batch_top':args};r=dict(status='integrated_batch_source_buffer_capacity_checked_platform_unverified',kernels=kernels,aliases=[],files={str(p):sha(p) for p in [source,proof_path,Path(__file__).resolve(),ROOT/'scripts/search_kernel_memory_plan.py',ROOT/'scripts/resident_router_memory_plan.py']},actual_xo_abi_verified=False,hardware_executed=False,
        limitations=['Source declaration and pragma inventory only; exported kernel.xml offsets/qualifiers/port mapping remain unverified.','All41 buffers disjoint within the integrated CU; internal state sharing is already expressed by the single top.','Nominal bank capacity and16MiB reserve policy only; no real platform, group_id intersection or simultaneous BO allocation.','No board timing, throughput, bandwidth or power proof.','Per-query/net/round trace export is not implemented by this interface; final ledgers and completion flags alone do not replace complete diagnostic validation.'])
    r.update(allocate(kernels,[]));out.mkdir();r['configs']={}
    for name,mapping in r['layouts'].items():
        path=out/(name+'.cfg');path.write_text(connectivity(kernels,mapping));r['configs'][path.name]=sha(path)
    (out/'plan.json').write_text(json.dumps(r,indent=2)+'\n');print({k:r[k] for k in ['pointer_arguments','unique_buffers','total_requested_bytes','hbm_channels_used']})
if __name__=='__main__':main()
