#!/usr/bin/env python3
"""Sum consistent HLS estimates, separately from routed/platform utilization."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
KEYS={'BRAM_18K','DSP','FF','LUT','URAM'}
def read(path):
    x=ET.parse(path).getroot();u=x.find('UserAssignments')
    require(u.findtext('Part')=='xcu280-fsvh2892-2L-e' and float(u.findtext('TargetClockPeriod'))==5 and float(u.findtext('ClockUncertainty'))==1.35 and x.findtext('ReportVersion/Version')=='2022.2','Different synthesis target '+str(path))
    used={a.tag:int(a.text) for a in x.find('AreaEstimates/Resources')};available={a.tag:int(a.text) for a in x.find('AreaEstimates/AvailableResources')}
    require(set(used)==set(available)==KEYS and all(v>0 for v in available.values()),'Incomplete resources')
    return used,available
def main():
    output=ROOT/'results/resident_resource_estimates_20261025_v1.json';require(not output.exists(),'Existing resource budget')
    files={};helpers={};capacity=None
    for name in ['node_occupancy','site_occupancy','resident_snapshot','route_tree','site_request','retained_nodes','round_control','retained_edges']:
        path=ROOT/('results/'+name+'_synthesis_review_20261024_'+('v2' if name=='site_request' else 'v1')+'.json');proof=json.loads(path.read_text())
        candidates=[Path(p) for p in proof['files'] if p.endswith('_csynth.xml')];require(len(candidates)==1,'Missing component synthesis XML')
        xml=candidates[0];require(digest(xml)==proof['files'][str(xml)],'Changed synthesis report')
        used,available=read(xml);require(used==proof['resources'],'Different audited resource estimate')
        require(capacity is None or capacity==available,'Different device capacity');capacity=available;helpers[name]=used
        for p in [path,xml]:files[str(p)]=digest(p)
    scenarios={}
    physical=ROOT/'results/search_kernel_physical_csr_audit_20261024_v1.json';old=json.loads(physical.read_text());files[str(physical)]=digest(physical)
    for mode in ['csr','compact']:
        directory=ROOT/('build/search_kernel_hls_20261024_v3/'+mode+'/solution/syn');xml=directory/'report/search_kernel_top_csynth.xml';rtl=directory/'verilog/search_kernel_top.v'
        require(digest(rtl)==old['files'][str(rtl)],'Changed baseline search RTL')
        search,available=read(xml);require(available==capacity,'Different search capacity')
        total={k:search[k]+sum(v[k] for v in helpers.values()) for k in KEYS}
        scenarios[mode]=dict(search_estimates=search,total_hls_estimates=total,whole_device_percent={k:100*total[k]/capacity[k] for k in KEYS},estimates_within_whole_device=all(total[k]<=capacity[k] for k in KEYS))
        for p in [xml,rtl]:files[str(p)]=digest(p)
    files[str(Path(__file__).resolve())]=digest(__file__)
    result=dict(status='nine_component_hls_resource_estimates_accounted_platform_budget_unverified',files=files,device_capacity=capacity,helper_estimates=helpers,scenarios=scenarios,platform_resources_known=False,hardware_executed=False,limitations=['Sum of HLS estimates only; not a simultaneous mapped/placed/routed design and not proof of device fit.','Whole-device capacity includes resources reserved by a real platform; no platform resource reserve was measured.','Search HLS estimates differ substantially from its separately routed utilization; do not mix these estimation levels to claim fit.','AXI adapters/interconnect/clock/reset/platform and autonomous controller utilization and congestion remain unmeasured.'])
    with output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(scenarios,indent=2))
if __name__=='__main__':main()
