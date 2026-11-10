#!/usr/bin/env python3
"""Check source/config/ABI controls before comparing three integrated HLS estimates."""
import json,os,tempfile
from pathlib import Path
import xml.etree.ElementTree as ET
from check_vitis_kernel import digest,require
from search_kernel_memory_plan_v2 import parse_source
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
def main():
    target=ROOT/'results/compressed_batch_bus_width_ablation_20261025_v1.json';require(not target.exists(),'Refuse overwrite')
    names=[('default','compressed_batch_hls','compressed_batch_synthesis_review_20261025_v1.json'),('packet64','compressed_batch_width64_hls','compressed_batch_width64_synthesis_review_20261025_v2.json'),('all64','compressed_batch_bus64_hls','compressed_batch_bus64_synthesis_review_20261025_v1.json')]
    data=[];files={};reference_helpers=None;reference_args=None;reference_flow=None;reference_top=None;reference_target=None
    anchor='#pragma HLS INTERFACE m_axi port=packet offset=slave bundle=input_mem depth=4194304'
    for label,bundle_name,report_name in names:
        path=ROOT/'results'/report_name;r=json.loads(path.read_text());require('csim_synthesis_verified_rtl_pending' in r['status'],'Missing independent synthesis gate')
        files[str(path)]=digest(path);bundle=BASE/bundle_name;source=bundle/'source';top=source/'search_batch_trace_top_v2.cpp'
        helpers={p.name:digest(p) for p in source.iterdir() if p.suffix in ['.h','.hpp','.cpp'] and not p.name.startswith('test') and p!=top}
        for name,h in helpers.items():
            p=source/name;require(r['files'].get(str(p))==h,'Unbound/changed helper '+str(p));files[str(p)]=h
        if reference_helpers is None:reference_helpers=helpers
        else:require(helpers==reference_helpers,'Algorithm helper sources differ')
        require(r['files'].get(str(top))==digest(top),'Changed/unbound top source');files[str(top)]=digest(top)
        text=top.read_text()
        if label=='packet64':require(text.splitlines().count(anchor+' max_widen_bitwidth=64')==1,'Missing sole packet change');text=text.replace(anchor+' max_widen_bitwidth=64',anchor)
        if reference_top is None:reference_top=text
        else:require(text==reference_top,'Top algorithm differs beyond the selected interface pragma')
        args=parse_source(top)
        for arg in args:arg.pop('max_widen_bitwidth',None)
        if reference_args is None:reference_args=args
        else:require(args==reference_args,'Argument order/identity/depth/capacity differs')
        flow=bundle/'flow.tcl';lines=flow.read_text().splitlines();require('config_compile -pipeline_loops 0' in lines,'Different loop compilation policy')
        config='config_interface -m_axi_max_widen_bitwidth 64'
        require(lines.count(config)==int(label=='all64'),'Unexpected global interface configuration')
        normalized='\n'.join(l for l in lines if not l.startswith('add_files -tb ') and l!=config)
        if reference_flow is None:reference_flow=normalized
        else:require(normalized==reference_flow,'Synthesis flow differs beyond declared single-variable settings')
        files[str(flow)]=digest(flow)
        target_settings={k:r['target'][k] for k in ['TopModelName','Part','TargetClockPeriod','ClockUncertainty']}
        if reference_target is None:reference_target=target_settings
        else:require(target_settings==reference_target,'Different tool target/clock constraints')
        app=Path(json.loads((bundle/'plan.json').read_text())['project'])/'hls.app'
        rtl_files=[x for x in ET.parse(app).getroot().findall('files/file') if x.attrib.get('tb')!='1'];require(len(rtl_files)==1 and rtl_files[0].attrib.get('cflags')=='-std=c++14 -DSEARCH_GRAPH_MODE=0','Different DUT compilation flags');files[str(app)]=digest(app)
        data.append(dict(configuration=label,resources=r['resources'],estimated_clock_ns=r['estimated_clock_ns'],read_data_port_widths=r['read_data_port_widths'],declared_payload_bytes=sum(a['payload_bytes'] for a in args if a['pointer']),argument_count=len(args),pointer_count=sum(a['pointer'] for a in args),independent_report=str(path)))
    base=data[0]
    for row in data:
        row['lut_ratio_to_default']=row['resources']['LUT']/base['resources']['LUT'];row['lut_saved_percent']=100*(1-row['lut_ratio_to_default']);row['effective_clock_budget_gap_ns']=row['estimated_clock_ns']-3.65;row['hls_lut_below_whole_device_reference']=row['resources']['LUT']<=1303680
    for p in [Path(__file__).resolve(),ROOT/'scripts/search_kernel_memory_plan_v2.py',ROOT/'scripts/check_vitis_kernel.py']:files[str(p)]=digest(p)
    result=dict(status='three_integrated_csr_interface_configurations_source_abi_constraints_controlled_hls_estimates_compared',rows=data,helper_files_per_configuration=len(reference_helpers),files=files,limits=['Same synthesizable algorithm/helpers/ABI/capacity/mode and clock constraints; TB allocation changed from old baseline to full44 validation and is not synthesis input','HLS estimates only; no mapped/platform fit, RTL equivalence, memory bandwidth or speedup claim','Global64 estimate3.715ns still exceeds effective3.65ns target despite LUT reduction','Only the original configuration has the completed four-real-CPU-batch diagnostic audit; new configurations require RTL and board evidence'])
    fd,tmp=tempfile.mkstemp(dir=target.parent)
    with os.fdopen(fd,'w') as f:json.dump(result,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,target);print(result['status']);print([(r['configuration'],r['resources']['LUT'],r['estimated_clock_ns']) for r in data])
if __name__=='__main__':main()
