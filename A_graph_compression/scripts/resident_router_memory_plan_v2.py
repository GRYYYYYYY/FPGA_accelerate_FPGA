"""Six-component candidate, extending frozen v1 with the packed request encoder."""
import argparse
import json
from pathlib import Path
from resident_router_memory_plan import generate,component_source,allocate,connectivity,ROOT,sha,require


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    r=generate();top='search_site_request_top';src=ROOT/'hardware/vitis/search_site_request_top.cpp'
    review=ROOT/'results/site_request_synthesis_review_20261024_v1.json';proof=json.loads(review.read_text())
    require(proof['status']=='site_request_csim_and_synthesis_verified_rtl_pending','Encoder synthesis not audited')
    for path,h in {**proof['files'],**proof['source_bindings']}.items():require(sha(path)==h,'Changed audited encoder '+path)
    copies=[Path(path) for path in proof['source_bindings'] if Path(path).name==src.name]
    require(copies and all(sha(path)==sha(src) for path in copies),'Changed encoder top')
    r['kernels'][top]=component_source(src,top)
    require(set(proof['read_data_port_widths'])=={'m_axi_'+x['bundle']+'_RDATA' for x in r['kernels'][top]},'Encoder bundle mismatch')
    r['component_synth_read_widths'][top]=proof['read_data_port_widths']
    r['aliases'] += [['search_route_tree_top.demands',top+'.state'],['search_site_occupancy_top.request',top+'.request']]
    r.update(allocate(r['kernels'],r['aliases']))
    r['status']='six_component_static_shared_buffer_capacity_checked_device_unverified'
    for path in [src,review,Path(__file__).resolve()]:r['files'][str(path)]=sha(path)
    r['limitations'].append('Encoder record count still needs outer control; this inventory does not implement that scheduler.')
    a.output.mkdir(parents=True,exist_ok=False);r['configs']={}
    for name,mapping in r['layouts'].items():
        path=a.output/(name+'.cfg');path.write_text(connectivity(r['kernels'],mapping));r['configs'][path.name]=sha(path)
    (a.output/'plan.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:r[k] for k in ['status','pointer_arguments','unique_buffers','total_requested_bytes','hbm_channels_used']}))


if __name__=='__main__':main()
