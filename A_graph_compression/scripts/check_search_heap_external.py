#!/usr/bin/env python3
"""Audit external heap real-capacity stimuli and seven RTL transactions."""
import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from prepare_search_heap_router import digest

def require(ok,message):
    if not ok:raise ValueError(message)

def golden(text,copies):
    require('ERROR:' not in text and 'EXTERNAL_HEAP_MISMATCH' not in text,'Failed test log')
    rows=[tuple(map(int,r)) for r in re.findall(r'^EXTERNAL_HEAP_BATCH_PASS (\d+) initial=(\d+) operations=(\d+) final=(\d+) status=(\d+)$',text,re.M)]
    require(len(rows)==7*copies,'Incomplete golden coverage')
    first=rows[:7]
    require([r[0] for r in first]==list(range(7)),'Wrong case order')
    require([r[2] for r in first]==[4096,4096,4096,128,8,4097,0],'Wrong operation coverage')
    require([r[4] for r in first]==[0,0,0,0,1,2,0],'Wrong status coverage')
    require(first[0][1]==0 and first[1][1]==73388 and first[3][1]==131072,'Missing capacity anchors')
    require(first[2][1]==first[1][3],'Missing cross-call continuity')
    require(first[4][1]==first[4][3]==131073,'Wrong invalid-count coverage')
    require(first[5][1]==first[5][3]==first[3][3] and first[6][1]==first[6][3]==first[5][3],'Rejected/empty call altered count')
    require(all(r[3]<=131072 for r in first if r[0]!=4),'Overflowing successful count')
    require(rows==first*copies,'C and RTL golden outputs differ')
    require(len(re.findall(r'^EXTERNAL_HEAP_ALL_PASS$',text,re.M))==copies,'Missing final golden marker')
    return first

def audit(bundle):
    pp=bundle/'plan.json';plan=json.loads(pp.read_text())
    require(plan['capacity']==131072,'Wrong capacity')
    for p,h in {**plan['files'],**plan['copied']}.items():require(digest(p)==h,'Changed frozen input '+p)
    rp=bundle/'receipt.json';receipt=json.loads(rp.read_text());log=bundle/'flow.log';text=log.read_text()
    require(receipt['exit_code']==0 and receipt['log_sha256']==digest(log),'Receipt failed or changed')
    require('EXTERNAL_HEAP_FLOW_COMPLETE' in text and 'C/RTL co-simulation finished: PASS' in text and 'ERROR:' not in text,'Incomplete HLS flow')
    segments=text.split('Running: cosim_design');require(len(segments)==2,'Wrong cosim flow')
    before=golden(segments[0],1);after=golden(segments[1],2);require(before==after,'Csim/RTL outputs differ')
    sol=Path(plan['project'])/'solution';csim=sol/'csim/report/search_heap_external_top_csim.log'
    require(golden(csim.read_text(),1)==before,'Csim report differs')
    synth=sol/'syn/report/search_heap_external_top_csynth.xml';cosim=sol/'sim/report/search_heap_external_top_cosim.rpt';trans=sol/'sim/report/verilog/result.transaction.rpt'
    require(re.search(r'Verilog\s*\|\s*Pass',cosim.read_text()),'No passing RTL')
    pairs=[tuple(map(int,p)) for p in re.findall(r'^transaction\s+(\d+):\s+(\d+)',trans.read_text(),re.M)]
    require([i for i,c in pairs]==list(range(7)) and all(c>0 for i,c in pairs),'Missing RTL transactions')
    xml=ET.parse(synth).getroot();require(xml.findtext('UserAssignments/Part')==plan['part']=='xcu280-fsvh2892-2L-e','Part differs')
    require(float(xml.findtext('UserAssignments/TargetClockPeriod'))==plan['clock_ns']==5,'Clock differs')
    rtl=sorted((sol/'syn/verilog').glob('*.v'));require(rtl,'Missing RTL')
    files=[pp,rp,log,csim,synth,cosim,trans,Path(__file__).resolve(),*rtl]
    return {'status':'external_heap_131072_capacity_csim_synthesis_rtl_independently_verified','artifacts':{str(p):digest(p) for p in files},
            'cases':[{'batch':r[0],'initial':r[1],'operations':r[2],'final':r[3],'status':r[4],'cycles':pairs[i][1]} for i,r in enumerate(before)],
            'estimated_clock_ns':float(xml.findtext('PerformanceEstimates/SummaryOfTimingAnalysis/EstimatedClockPeriod')),
            'estimated_resources':{e.tag:int(e.text) for e in xml.find('AreaEstimates/Resources')},
            'warnings':[s for s in text.splitlines() if s.startswith('WARNING:')],
            'limitations':['AXI simulation model, not DDR/HBM or board timing.','Preseeded valid heap states exercise real/full capacity; not replay of all real search operations.',
                           'Complete label/state/occupancy/search controller not implemented in this component.','Caller must provide valid heap order, count and allocated buffers; top does not validate every existing entry.']}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();r=audit(a.bundle.resolve())
    with a.output.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps({k:r[k] for k in ['status','cases','estimated_resources']}))

if __name__=='__main__':main()
