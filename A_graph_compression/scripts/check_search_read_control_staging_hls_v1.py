#!/usr/bin/env python3
"""Independently inspect full-kernel Csim, controlled inputs and actual helper stages."""
import json,re,sys
from pathlib import Path
import xml.etree.ElementTree as ET
from check_vitis_kernel import digest,require
from check_search_packet_width_compact_hls import extract
from run_compact_native_stack_recovery_v1 import atomic
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
def main():
    out=BASE/'search_read_control_staging_hls_v1';output=ROOT/'results/search_read_control_staging_hls_audit_20261025_v1.json';require(not output.exists(),'Refuse overwrite')
    state=json.loads((out/'state.json').read_text());require(state['status']=='complete' and state['stage']=='full_kernel_csim_synthesis_pending_independent_audit','Full kernel HLS incomplete')
    plan=json.loads((out/'plan.json').read_text());files=dict(plan['files'])
    for p,h in files.items():require(digest(p)==h,'Changed HLS input '+p)
    require(plan['graph_mode']==0 and plan['transactions']==2 and plan['full_workspace_testbench_unchanged'] and plan['address_space_bytes']==68719476736 and plan['core_bytes']==0 and plan['max_single_file_bytes']==8589934592,'Scope/resource controls changed')
    predecessor=Path(plan['predecessor_source']);actual={p.name:p for p in (out/'source').iterdir() if p.is_file()};old={p.name:p for p in predecessor.iterdir() if p.is_file()};require(actual.keys()==old.keys(),'Source file set changed')
    changed=[n for n in actual if digest(actual[n])!=digest(old[n])];require(changed==plan['changed_files']==['search_label_records.hpp'],'Uncontrolled source change')
    require(digest(actual['search_label_records.hpp'])==digest(ROOT/'hardware/vitis/search_control_staging_v1/search_label_records.hpp'),'Different candidate header')
    log=out/'flow.log';text=log.read_text();receipt=json.loads((out/'receipt.json').read_text())
    require(receipt['exit_code']==0 and not receipt['resource_abort'] and receipt['command']==plan['command'] and receipt['log_sha256']==digest(log),'Different or failed actual run')
    for marker in ['PACKET_WIDTH_CSIM_COMPLETE','PACKET_WIDTH_SYNTHESIS_COMPLETE','SEARCH_KERNEL_TOP_ALL_PASS transactions=2 full_workspace_limits=1']:require(text.splitlines().count(marker)==1,'Missing/duplicate completion')
    require('ERROR:' not in text and 'CSim done with 0 errors.' in text,'Csim/synthesis errors')
    rows=re.findall(r'^SEARCH_KERNEL_TOP_TRANSACTION_PASS mode=0 transaction=(\d+) status=(\d+) cost=(\d+) path=(\d+)$',text,re.M);require(rows==[('0','0','35','2'),('1','3','0','0')],'Different full-workspace C oracle')
    project=Path(plan['project']);solution=project/'solution';app=ET.parse(project/'hls.app').getroot();sources=app.findall('files/file');require(len(sources)==2 and all('-DSEARCH_GRAPH_MODE=0' in f.attrib.get('cflags','') for f in sources),'Different graph mode')
    candidate=extract(solution/'syn/report/search_kernel_top_csynth.xml');baseline_path=ROOT/'build/search_packet_width64_20261024_v1/solution/syn/report/search_kernel_top_csynth.xml';baseline=extract(baseline_path)
    prior_path=ROOT/'results/search_packet_width64_comparison_20261024_v1.json';prior=json.loads(prior_path.read_text());require(prior['files'][str(baseline_path)]==digest(baseline_path),'Changed frozen packet64 baseline')
    require(candidate['read_data_port_widths']==baseline['read_data_port_widths'] and candidate['read_data_port_widths']['m_axi_input_mem_RDATA']==64,'Memory interfaces changed')
    helpers=[]
    for p in sorted((solution/'syn/report').glob('*valid_decoded_record*_csynth.xml')):
        x=ET.parse(p).getroot();timing={n.tag:n.text for n in x.find('PerformanceEstimates/SummaryOfOverallLatency')};helpers.append(dict(report=str(p),latency=timing))
    achieved=bool(helpers) and all(h['latency'].get('Best-caseLatency','').isdigit() and int(h['latency']['Best-caseLatency'])>=2 and h['latency'].get('Interval-min')=='1' for h in helpers)
    for parent in [solution/'syn/report',solution/'syn/verilog']:
        for p in parent.iterdir():
            if p.is_file():files[str(p)]=digest(p)
    for p in [out/'plan.json',out/'state.json',out/'receipt.json',log,project/'hls.app',baseline_path,prior_path,Path(__file__).resolve(),ROOT/'scripts/check_search_packet_width_compact_hls.py',ROOT/'scripts/check_vitis_kernel.py',ROOT/'scripts/run_compact_native_stack_recovery_v1.py']:files[str(p)]=digest(p)
    result=dict(status='full_kernel_csim_synthesis_verified_scalar_validity_staging_'+('achieved' if achieved else 'not_confirmed')+'_rtl_pending',files=files,before=baseline,after=candidate,helpers=helpers,helper_min2_ii1_achieved=achieved,resource_delta={k:candidate['resources'][k]-baseline['resources'][k] for k in candidate['resources']},estimated_clock_delta_ns=candidate['estimated_clock_ns']-baseline['estimated_clock_ns'],rtl_verified=False,physical_timing_verified=False,board_verified=False,limits=['Two original full-workspace search-core transactions, not full44 negotiated batch or real traffic','Actual helper latency/II report inspected; HLS estimate does not prove routed timing','Internal pipeline timing changes; original RTL cycle count cannot be reused as new equivalence evidence'])
    atomic(output,result);print(result['status'],candidate['resources'],candidate['estimated_clock_ns'])
if __name__=='__main__':main()
