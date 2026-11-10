#!/usr/bin/env python3
"""Audit compact width64 synthesis against its own frozen compact baseline."""
import argparse,json,re
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
def extract(path):
    x=ET.parse(path).getroot();assignments={p.tag:p.text for p in x.find('UserAssignments')}
    require(x.findtext('ReportVersion/Version')=='2022.2' and assignments['TopModelName']=='search_kernel_top' and assignments['Part']=='xcu280-fsvh2892-2L-e','Wrong report tool/top/part')
    require(float(assignments['TargetClockPeriod'])==5 and float(assignments['ClockUncertainty'])==1.35,'Different clock target')
    ports={p.findtext('name'):int(p.findtext('Bits')) for p in x.findall('InterfaceSummary/RtlPorts') if p.findtext('name','').startswith('m_axi_') and p.findtext('name','').endswith('_RDATA')}
    return dict(resources={p.tag:int(p.text) for p in x.find('AreaEstimates/Resources')},estimated_clock_ns=float(x.findtext('PerformanceEstimates/SummaryOfTimingAnalysis/EstimatedClockPeriod')),read_data_port_widths=ports,target=assignments)
def audit():
    out=BASE/'search_packet_width64_compact_hls';plan=json.loads((out/'plan.json').read_text());state=json.loads((out/'state.json').read_text());require(state['status']=='complete' and state['stage']=='synthesized_pending_independent_review','Original compact HLS not complete')
    files=dict(plan['files'])
    for p,h in files.items():require(digest(p)==h,'Changed frozen HLS input '+p)
    require(plan['graph_mode']==1 and plan['transactions']==2 and plan['max_single_file_bytes']==8589934592,'Wrong run controls')
    receipt=json.loads((out/'receipt.json').read_text());log=out/'flow.log';text=log.read_text()
    require(receipt['exit_code']==0 and receipt['command']==plan['command'] and receipt['log_sha256']==digest(log),'Different/failed actual HLS receipt')
    require('ERROR:' not in text and 'CSim done with 0 errors.' in text,'Csim/synthesis failure')
    for marker in ['PACKET_WIDTH_CSIM_COMPLETE','PACKET_WIDTH_SYNTHESIS_COMPLETE','SEARCH_KERNEL_TOP_ALL_PASS transactions=2 full_workspace_limits=1']:
        require(text.splitlines().count(marker)==1,'Missing/duplicate completion marker')
    actual=re.findall(r'^SEARCH_KERNEL_TOP_TRANSACTION_PASS mode=1 transaction=(\d+) status=(\d+) cost=(\d+) path=(\d+)$',text,re.M)
    require(actual==[('0','0','35','2'),('1','3','0','0')],'Wrong literal compact Csim results')
    project=Path(plan['project']);solution=project/'solution'
    app=ET.parse(project/'hls.app').getroot();sources=app.findall('files/file');require(len(sources)==2 and all('-DSEARCH_GRAPH_MODE=1' in f.attrib.get('cflags','') for f in sources),'Wrong HLS mode')
    candidate=extract(solution/'syn/report/search_kernel_top_csynth.xml')
    baseline_path=ROOT/'build/search_kernel_hls_20261024_v3/compact/solution/syn/report/search_kernel_top_csynth.xml';proof_path=ROOT/'results/search_kernel_boundary_setup_20261024_v1.json';proof=json.loads(proof_path.read_text());require(proof['artifacts'].get(str(baseline_path))==digest(baseline_path),'Changed frozen compact baseline report');baseline=extract(baseline_path)
    old=baseline['read_data_port_widths'];new=candidate['read_data_port_widths'];require(old['m_axi_input_mem_RDATA']==512 and new['m_axi_input_mem_RDATA']==64,'Requested bus change not realized')
    require(set(new)==set(old) and all(new[k]==old[k] for k in old if k!='m_axi_input_mem_RDATA'),'Other interface widths changed')
    original=ROOT/'data/derived/search_kernel_hls_20261024_v3/source/search_kernel_top.cpp';modified=out/'source/search_kernel_top.cpp'
    anchor='#pragma HLS INTERFACE m_axi port=packet offset=slave bundle=input_mem depth=4194304';require(modified.read_text().replace(anchor+' max_widen_bitwidth=64',anchor)==original.read_text(),'Algorithm/interface change beyond one pragma')
    for directory in [solution/'syn/report',solution/'syn/verilog']:
        for p in directory.iterdir():
            if p.is_file():files[str(p)]=digest(p)
    for p in [out/'plan.json',out/'state.json',out/'receipt.json',log,project/'hls.app',baseline_path,proof_path,original,Path(__file__).resolve()]:files[str(p)]=digest(p)
    return dict(status='compact_search_packet_width64_two_transaction_csim_and_synthesis_verified_rtl_pending',before=baseline,after=candidate,resource_delta={k:v-baseline['resources'][k] for k,v in candidate['resources'].items()},estimated_clock_delta_ns=candidate['estimated_clock_ns']-baseline['estimated_clock_ns'],estimated_clock_meets_effective_budget=candidate['estimated_clock_ns']<=3.65,warning_counts=dict(Counter(re.findall(r'^WARNING: \[([^]]+)\]',text,re.M))),files=files,rtl_verified=False,physical_timing_verified=False,board_verified=False,limits=['Two synthetic compact Csim transactions at full workspace limits, not complete real traffic or boundary RTL','Actual generated port widths checked, but bandwidth, physical congestion and timing remain unverified','Original failed compact routed baseline is preserved; a smaller HLS estimate does not repair that design'])
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();require(not a.output.exists(),'Refuse overwrite');r=audit()
    with a.output.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
    print(r['status'],r['resource_delta'])
if __name__=='__main__':main()
