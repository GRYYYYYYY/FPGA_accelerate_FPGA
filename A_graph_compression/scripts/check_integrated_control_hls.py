#!/usr/bin/env python3
"""Audit actual synthesis of integrated control; no RTL/physical claim."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
def audit(kind,bundle,output):
    require(kind in ['connection','sink_loop'] and not output.exists(),'Invalid/existing review')
    top='search_'+kind+'_top';prefix='CONNECTION' if kind=='connection' else 'SINK_LOOP'
    plan=json.loads((bundle/'plan.json').read_text());state=json.loads((bundle/'state.json').read_text());receipt=json.loads((bundle/'receipt.json').read_text())
    require(state['status']=='complete' and state['stage']=='synthesized_pending_independent_review_and_rtl','Original HLS flow incomplete')
    files={**plan['files'],**plan['generated']}
    for p,h in files.items():require(digest(p)==h,'Changed HLS input '+p)
    log=bundle/'flow.log';text=log.read_text()
    require(receipt['exit_code']==0 and receipt['command']==plan['command'] and receipt['log_sha256']==digest(log),'Different/failed synthesis')
    for marker in [prefix+'_CSIM_COMPLETE',prefix+'_SYNTHESIS_COMPLETE']:
        require(text.splitlines().count(marker)==1,'Missing/duplicate flow marker')
    require('CSim done with 0 errors.' in text and 'ERROR:' not in text,'Failed Csim or synthesis')
    if kind=='connection':
        require(text.splitlines().count('SEARCH_CONNECTION_REJECTION_PASS cases=8 preflight_no_search=3 search=2 tree=1 edge=2 edge_failure_keeps_accepted_tree=1')==1 and text.splitlines().count('SEARCH_CONNECTION_PASS transactions=2 internal_search_tree_edge_sequence=1 nonfound_preserves_tree_edges=1')==1,'Missing complete connection checks')
    else:
        require(text.splitlines().count('SEARCH_SINK_LOOP_PASS mode=0 sorted_duplicate_sinks=3 empty=1 rejected=2 unknown_incomplete=1 internal_roots_patch_search_tree_edges=1')==1,'Missing multi-sink scope')
    project=Path(plan['project']);solution=project/'solution';xml=solution/('syn/report/'+top+'_csynth.xml');x=ET.parse(xml).getroot();u={p.tag:p.text for p in x.find('UserAssignments')}
    require(x.findtext('ReportVersion/Version')=='2022.2' and u['TopModelName']==top and u['Part']==plan['part']=='xcu280-fsvh2892-2L-e' and float(u['TargetClockPeriod'])==plan['clock_ns']==5 and float(u['ClockUncertainty'])==plan['uncertainty_ns']==1.35,'Different HLS tool or constraints')
    app=ET.parse(project/'hls.app').getroot();sources=app.findall('files/file');require(sources and all('-DSEARCH_GRAPH_MODE=0' in p.attrib.get('cflags','') for p in sources),'Different graph mode')
    require(not any('SEARCH_SINK_LOOP_OBSERVE' in p.attrib.get('cflags','') for p in sources),'Diagnostic callback in synthesis project')
    resources={p.tag:int(p.text) for p in x.find('AreaEstimates/Resources')};require(set(resources)=={'BRAM_18K','DSP','FF','LUT','URAM'} and resources['LUT']>0,'Missing resources')
    ports={p.findtext('name'):int(p.findtext('Bits')) for p in x.findall('InterfaceSummary/RtlPorts') if p.findtext('name','').startswith('m_axi_') and p.findtext('name','').endswith('_RDATA')}
    bundles={'graph_mem','input_mem','heap_mem','index_mem','record_mem','key_mem','output_mem','tree_meta_mem','tree_mem','state_mem','edge_meta_mem','edge_store_mem'}
    if kind=='sink_loop':bundles.add('sink_mem')
    require(set(ports)=={'m_axi_'+p+'_RDATA' for p in bundles},'Missing/extra memory interface')
    rtl=solution/'syn/verilog';require((rtl/(top+'.v')).is_file(),'Missing actual generated top')
    for directory in [solution/'syn/report',rtl]:
        for p in directory.iterdir():
            if p.is_file():files[str(p)]=digest(p)
    for p in [bundle/'plan.json',bundle/'state.json',bundle/'receipt.json',log,project/'hls.app',Path(__file__).resolve()]:files[str(p)]=digest(p)
    warnings=Counter(re.findall(r'^WARNING: \[([^]]+)\]',text,re.M))
    report=dict(status=kind+'_integrated_control_csim_synthesis_verified_rtl_pending',files=files,target=u,resources=resources,read_data_port_widths=ports,estimated_clock_ns=float(x.findtext('PerformanceEstimates/SummaryOfTimingAnalysis/EstimatedClockPeriod')),latency_estimates={p.tag:p.text for p in x.find('PerformanceEstimates/SummaryOfOverallLatency')},warning_counts=dict(warnings),all_loop_constraints_satisfied=False if 'All loop constraints were NOT satisfied' in text else True if 'All loop constraints were satisfied' in text else None,rtl_verified=False,physical_timing_verified=False,board_verified=False,limitations=['Actual integrated Csim and synthesis only; no complete negotiated routing RTL or device proof.','Original search architecture retained; do not apply packet-width64 resource/timing results to this design.','Static HLS resource and latency estimates do not prove platform fit or throughput.','Remaining net ownership/snapshot construction/site commit/round control are external; no cross-stage rollback.','Multi-sink dead build-path elimination and final stage ordering require generated RTL/operation-level validation beyond interface presence.'])
    with output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(report['status'],resources,dict(warnings))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=['connection','sink_loop'],required=True);p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();audit(a.kind,a.bundle.resolve(),a.output.resolve())
