"""Eight-component candidate including bounded per-net canonical-node retention."""
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
    retained='search_retained_nodes_top';retained_src=ROOT/'hardware/vitis/search_retained_nodes_top.cpp'
    retained_review=ROOT/'results/retained_nodes_synthesis_review_20261024_v1.json'
    retained_proof=json.loads(retained_review.read_text())
    require(retained_proof['status']=='retained_nodes_csim_and_synthesis_verified_rtl_pending','Retention synthesis not audited')
    for path,h in {**retained_proof['files'],**retained_proof['source_bindings']}.items():require(sha(path)==h,'Changed audited retention '+path)
    retained_copies=[Path(path) for path in retained_proof['source_bindings'] if Path(path).name==retained_src.name]
    require(retained_copies and all(sha(path)==sha(retained_src) for path in retained_copies),'Changed retention source')
    r['kernels'][retained]=component_source(retained_src,retained)
    require(set(retained_proof['read_data_port_widths'])=={'m_axi_'+x['bundle']+'_RDATA' for x in r['kernels'][retained]},'Retention bundle mismatch')
    r['component_synth_read_widths'][retained]=retained_proof['read_data_port_widths']
    r['aliases'] += [['search_route_tree_top.roots',retained+'.nodes'],['search_node_occupancy_top.old_nodes',retained+'.output']]
    for path in [retained_src,retained_review]:r['files'][str(path)]=sha(path)
    round_top='search_round_control_top';round_src=ROOT/'hardware/vitis/search_round_control_top.cpp'
    round_review=ROOT/'results/round_control_synthesis_review_20261024_v1.json'
    round_proof=json.loads(round_review.read_text())
    require(round_proof['status']=='round_control_csim_and_synthesis_verified_rtl_pending','Round synthesis not audited')
    for path,h in {**round_proof['files'],**round_proof['source_bindings']}.items():require(sha(path)==h,'Changed audited round control '+path)
    copies=[Path(path) for path in round_proof['source_bindings'] if Path(path).name==round_src.name]
    require(copies and all(sha(path)==sha(round_src) for path in copies),'Changed round top')
    r['kernels'][round_top]=component_source(round_src,round_top)
    require(set(round_proof['read_data_port_widths'])=={'m_axi_'+x['bundle']+'_RDATA' for x in r['kernels'][round_top]},'Round bundle mismatch')
    r['component_synth_read_widths'][round_top]=round_proof['read_data_port_widths']
    r['aliases'].append(['search_node_occupancy_top.counts',round_top+'.counts'])
    for path in [round_src,round_review]:r['files'][str(path)]=sha(path)
    r.update(allocate(r['kernels'],r['aliases']))
    r['status']='eight_component_static_shared_buffer_capacity_checked_device_unverified'
    for path in [src,review,Path(__file__).resolve()]:r['files'][str(path)]=sha(path)
    r['limitations'].append('Round control reads the existing node-count BO; completion flags and commands still require outer control. Retained edges and an autonomous hardware scheduler remain outside this inventory.')
    a.output.mkdir(parents=True,exist_ok=False);r['configs']={}
    for name,mapping in r['layouts'].items():
        path=a.output/(name+'.cfg');path.write_text(connectivity(r['kernels'],mapping));r['configs'][path.name]=sha(path)
    (a.output/'plan.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:r[k] for k in ['status','pointer_arguments','unique_buffers','total_requested_bytes','hbm_channels_used']}))


if __name__=='__main__':main()
