#!/usr/bin/env python3
"""Measure a single packet-widening change without claiming physical improvement."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
def summary(path):
    x=ET.parse(path).getroot();u={a.tag:a.text for a in x.find('UserAssignments')}
    require(x.findtext('ReportVersion/Version')=='2022.2' and u['TopModelName']=='search_kernel_top' and u['Part']=='xcu280-fsvh2892-2L-e' and float(u['TargetClockPeriod'])==5 and float(u['ClockUncertainty'])==1.35,'Wrong tool/target/constraints')
    ports={p.findtext('name'):int(p.findtext('Bits')) for p in x.findall('InterfaceSummary/RtlPorts') if p.findtext('name','').startswith('m_axi_') and p.findtext('name','').endswith('_RDATA')}
    require(len(ports)==7 and 'm_axi_input_mem_RDATA' in ports,'Missing memory ports')
    return dict(read_widths=ports,resources={c.tag:int(c.text) for c in x.find('AreaEstimates/Resources')},estimated_clock_ns=float(x.findtext('PerformanceEstimates/SummaryOfTimingAnalysis/EstimatedClockPeriod')),latency={c.tag:c.text for c in x.find('PerformanceEstimates/SummaryOfOverallLatency')})
def rtl_input_width(text):
    values=re.findall(r'parameter\s+C_M_AXI_INPUT_MEM_DATA_WIDTH\s*=\s*(\d+)\s*;',text)
    require(len(values)==1,'Missing/ambiguous actual RTL bundle width');return int(values[0])
def audit(bundle,output):
    require(not output.exists(),'Existing comparison')
    plan=json.loads((bundle/'plan.json').read_text());state=json.loads((bundle/'state.json').read_text())
    require(state['status']=='complete' and state['stage']=='synthesized_pending_structural_comparison','Original experiment incomplete')
    files={**plan['files'],**plan['generated']}
    for p,h in files.items():require(digest(p)==h,'Changed input '+p)
    base=ROOT/'data/derived/search_kernel_hls_20261024_v3/source';source=bundle/'source'
    old='#pragma HLS INTERFACE m_axi port=packet offset=slave bundle=input_mem depth=4194304'
    for p in base.iterdir():
        expected=p.read_text()
        if p.name=='search_kernel_top.cpp':require(expected.count(old)==1,'Wrong baseline pragma');expected=expected.replace(old,old+' max_widen_bitwidth=64')
        require((source/p.name).read_text()==expected,'Not single-variable source '+p.name)
    for phase in ['compile_0','preflight_0','compile_1','preflight_1','hls']:
        log=bundle/(phase+'.log');rp=bundle/(phase+'.receipt.json');r=json.loads(rp.read_text());t=log.read_text()
        require(r['exit_code']==0 and r['log_sha256']==digest(log) and r['plan_sha256']==digest(bundle/'plan.json'),'Bad phase receipt '+phase)
        require(not any(s in t for s in ['ERROR:','runtime error:','AddressSanitizer','Assertion']),'Phase failure '+phase)
        if phase.startswith('preflight_'):
            mode=int(phase[-1]);expected=[f'SEARCH_KERNEL_TOP_TRANSACTION_PASS mode={mode} transaction=0 status=0 cost=35 path=2',f'SEARCH_KERNEL_TOP_TRANSACTION_PASS mode={mode} transaction=1 status=3 cost=0 path=0','SEARCH_KERNEL_TOP_ALL_PASS transactions=2 full_workspace_limits=1']
            require(t.splitlines()==expected,'Different complete preflight')
        if phase=='hls':
            require(t.splitlines().count('PACKET_WIDTH_CSIM_COMPLETE')==t.splitlines().count('PACKET_WIDTH_SYNTHESIS_COMPLETE')==1 and 'CSim done with 0 errors.' in t,'Missing actual Csim/synthesis')
        for p in [log,rp]:files[str(p)]=digest(p)
    original=ROOT/'build/search_kernel_hls_20261024_v3/csr/solution';new=Path(plan['project'])/'solution'
    baseline_audit=ROOT/'results/search_kernel_physical_csr_audit_20261024_v1.json';proof=json.loads(baseline_audit.read_text())
    base_rtl=original/'syn/verilog/search_kernel_top.v';new_rtl=new/'syn/verilog/search_kernel_top.v'
    require(digest(base_rtl)==proof['files'][str(base_rtl)],'Baseline RTL differs from routed experiment')
    before=summary(original/'syn/report/search_kernel_top_csynth.xml');after=summary(new/'syn/report/search_kernel_top_csynth.xml')
    for info,rtl in [(before,base_rtl),(after,new_rtl)]:require(rtl_input_width(rtl.read_text())==info['read_widths']['m_axi_input_mem_RDATA'],'XML/RTL width mismatch')
    require(before['read_widths']['m_axi_input_mem_RDATA']==512,'Different original bus')
    before_bits=before['read_widths']['m_axi_input_mem_RDATA'];after_bits=after['read_widths']['m_axi_input_mem_RDATA']
    for directory in [original/'syn',new/'syn']:
        for p in directory.rglob('*'):
            if p.is_file() and p.suffix in ['.v','.dat','.xml','.rpt']:files[str(p)]=digest(p)
    for p in [bundle/'plan.json',bundle/'state.json',baseline_audit,Path(__file__).resolve()]:files[str(p)]=digest(p)
    report=dict(status='packet_width_single_variable_csim_synthesis_compared_physical_unverified',files=files,before=before,after=after,input_width_reduced=after_bits<before_bits,input_width_is_64=after_bits==64,resource_delta={k:after['resources'][k]-v for k,v in before['resources'].items()},warning_counts=dict(Counter(re.findall(r'^WARNING: \[([^]]+)\]',(bundle/'hls.log').read_text(),re.M))),rtl_verified=False,physical_timing_verified=False,limitations=['Two synthetic transactions per mode under sanitizers and CSR HLS Csim; not full-workload equivalence or RTL proof.','A changed bus width does not prove the failing address/control path was removed or improved.','Narrowing can reduce burst bandwidth or worsen latency; original 200MHz/1.35ns physical and device gates remain.'])
    with output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(report['status'],before_bits,after_bits,report['resource_delta'])
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();audit(a.bundle.resolve(),a.output.resolve())
