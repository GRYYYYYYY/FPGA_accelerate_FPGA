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
    require(kind in ['compressed_batch_trace'] and not output.exists(),'Invalid/existing review')
    top='search_batch_trace_top_v2';prefix='COMPRESSED_BATCH_TRACE'
    plan=json.loads((bundle/'plan.json').read_text());state=json.loads((bundle/'state.json').read_text());receipt=json.loads((bundle/'receipt.json').read_text())
    require(state['status']=='complete' and state['stage']=='csim_synthesized_pending_independent_review_rtl','Original HLS flow incomplete')
    files=dict(plan['files'])
    for p,h in files.items():require(digest(p)==h,'Changed HLS input '+p)
    log=bundle/'flow.log';text=log.read_text()
    require(receipt['exit_code']==0 and receipt['command']==plan['command'] and receipt['log_sha256']==digest(log),'Different/failed synthesis')
    for marker in [prefix+'_CSIM_COMPLETE',prefix+'_SYNTHESIS_COMPLETE']:
        require(text.splitlines().count(marker)==1,'Missing/duplicate flow marker')
    require('CSim done with 0 errors.' in text and 'ERROR:' not in text,'Failed Csim or synthesis')
    require(text.splitlines().count('SEARCH_BATCH_PASS mode=0 routed=1 persistent_conflict_rounds=2 final_history_advance=1 incomplete_early_stop=1 invalid=1')==1,'Missing complete net transaction checks')
    project=Path(plan['project']);solution=project/'solution';xml=solution/('syn/report/'+top+'_csynth.xml');x=ET.parse(xml).getroot();u={p.tag:p.text for p in x.find('UserAssignments')}
    require(x.findtext('ReportVersion/Version')=='2022.2' and u['TopModelName']==top and u['Part']==plan['part']=='xcu280-fsvh2892-2L-e' and float(u['TargetClockPeriod'])==plan['clock_ns']==5 and float(u['ClockUncertainty'])==plan['uncertainty_ns']==1.35,'Different HLS tool or constraints')
    app=ET.parse(project/'hls.app').getroot();sources=app.findall('files/file');require(sources and all('-DSEARCH_GRAPH_MODE=0' in p.attrib.get('cflags','') for p in sources),'Different graph mode')
    require(not any('SEARCH_SINK_LOOP_OBSERVE' in p.attrib.get('cflags','') for p in sources),'Diagnostic callback in synthesis project')
    resources={p.tag:int(p.text) for p in x.find('AreaEstimates/Resources')};require(set(resources)=={'BRAM_18K','DSP','FF','LUT','URAM'} and resources['LUT']>0,'Missing resources')
    ports={p.findtext('name'):int(p.findtext('Bits')) for p in x.findall('InterfaceSummary/RtlPorts') if p.findtext('name','').startswith('m_axi_') and p.findtext('name','').endswith('_RDATA')}
    bundles={'graph_mem','input_mem','heap_mem','index_mem','record_mem','key_mem','output_mem','tree_meta_mem','tree_mem','state_mem','edge_meta_mem','edge_store_mem'}
    bundles.update({'sink_mem','batch_input_mem','query_mem','completion_mem','site_scratch_mem','static_mem','node_meta_mem','node_count_mem','node_history_mem','node_table_mem','site_meta_mem','site_owner_mem','site_history_mem','site_request_mem','retained_meta_mem','retained_store_mem','old_node_mem','trace_mem'})
    require(set(ports)=={'m_axi_'+p+'_RDATA' for p in bundles},'Missing/extra memory interface')
    rtl=solution/'syn/verilog';require((rtl/(top+'.v')).is_file(),'Missing actual generated top')
    for directory in [solution/'syn/report',rtl]:
        for p in directory.iterdir():
            if p.is_file():files[str(p)]=digest(p)
    for p in [bundle/'plan.json',bundle/'state.json',bundle/'receipt.json',log,project/'hls.app',Path(__file__).resolve()]:files[str(p)]=digest(p)
    from search_kernel_memory_plan import parse_source
    args=parse_source(bundle/'source/search_batch_trace_top_v2.cpp')
    require(len(args)==45 and sum(a['pointer'] for a in args)==44,'Different batch source interface')
    files[str(ROOT/'scripts/search_kernel_memory_plan.py')]=digest(ROOT/'scripts/search_kernel_memory_plan.py')
    from read_batch_trace_v4 import decode_file
    for case in range(4):
        path=solution/'csim/build'/f'trace_mode_0_case_{case}.bin'
        cpu=Path('/tmp/A_graph_compression_recovery_20261025_v1/trace_v2_cpu')/path.name
        require(path.is_file() and digest(path)==digest(cpu),'Csim trace differs from CPU '+str(case))
        if case<3:
            decoded=decode_file(path,4)
            require(decoded['complete_batch']==(case!=1),'Wrong initial-state acceptance')
        else:
            try:decode_file(path,4)
            except ValueError:pass
            else:raise ValueError('Error trace wrongly accepted')
        files[str(path)]=digest(path)
    for name in ['read_batch_trace_v4.py','read_round_trace_v2.py','read_compressed_search_trace.py','read_trace_set_codec.py','read_batch_trace_v2.py','read_batch_trace.py','read_search_trace.py','read_net_trace.py','read_round_trace.py']:
        p=ROOT/'scripts'/name;files[str(p)]=digest(p)
    warnings=Counter(re.findall(r'^WARNING: \[([^]]+)\]',text,re.M))
    report=dict(status=kind+'_integrated_control_csim_synthesis_verified_rtl_pending',files=files,target=u,resources=resources,source_arguments=args,actual_xo_control_abi_verified=False,read_data_port_widths=ports,estimated_clock_meets_effective_budget=float(x.findtext('PerformanceEstimates/SummaryOfTimingAnalysis/EstimatedClockPeriod'))<=3.65,estimated_clock_ns=float(x.findtext('PerformanceEstimates/SummaryOfTimingAnalysis/EstimatedClockPeriod')),latency_estimates={p.tag:p.text for p in x.find('PerformanceEstimates/SummaryOfOverallLatency')},warning_counts=dict(warnings),all_loop_constraints_satisfied=False if 'All loop constraints were NOT satisfied' in text else True if 'All loop constraints were satisfied' in text else None,rtl_verified=False,physical_timing_verified=False,board_verified=False,limitations=['Actual integrated Csim and synthesis only; no complete negotiated routing RTL or device proof.','Original search architecture retained; do not apply packet-width64 resource/timing results to this design.','Static HLS resource and latency estimates do not prove platform fit or throughput.','All-net iteration, net transactions and round/history control execute internally. Inputs still require static provenance/unique-query/reservation validation. No global or cross-stage rollback.','Trace CPU/Csim bytes match, but no synthesized trace or round finite-state validation in RTL. Fixed-capacity overflow invalidates acceptance; seeded initial state remains unverified.','Final stage ordering, finite-state execution and complete real workload require RTL/operation-level validation beyond interface presence.'])
    with output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(report['status'],resources,dict(warnings))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=['compressed_batch_trace'],required=True);p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();audit(a.kind,a.bundle.resolve(),a.output.resolve())
