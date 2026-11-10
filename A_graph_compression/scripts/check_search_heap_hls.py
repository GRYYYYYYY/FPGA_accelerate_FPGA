#!/usr/bin/env python3
"""Audit heap C/RTL golden outputs, transaction coverage and synthesis identity."""
import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from prepare_search_heap_router import digest

def require(ok,message):
    if not ok:raise ValueError(message)

def golden(text,count):
    require('ERROR:' not in text and 'HEAP_TOP_MISMATCH' not in text,'Failed test log')
    require(re.findall(r'^HEAP_TOP_BATCH_PASS (\d+) operations=(\d+)$',text,re.M)==[('0','4096'),('1','4096')]*count,'Missing/reordered golden batches')
    require(len(re.findall(r'^HEAP_TOP_ALL_PASS$',text,re.M))==count,'Missing completion marker')

def transactions(text):
    pairs=[tuple(map(int,p)) for p in re.findall(r'^transaction\s+(\d+):\s+(\d+)',text,re.M)]
    require([i for i,c in pairs]==[0,1] and all(c>0 for i,c in pairs),'Invalid RTL transactions')
    return [c for i,c in pairs]

def audit(bundle):
    plan_path=bundle/'plan.json';plan=json.loads(plan_path.read_text())
    state=json.loads((bundle/'state.json').read_text())
    require(state['status']=='complete','Pipeline not complete')
    for p,h in {**plan['files'],**plan['copied']}.items():require(digest(p)==h,'Frozen input changed '+p)
    receipt_path=bundle/'receipt.json';receipt=json.loads(receipt_path.read_text());log=bundle/'flow.log';text=log.read_text()
    require(receipt['exit_code']==0 and receipt['log_sha256']==digest(log),'Receipt failed or changed')
    require('ERROR:' not in text and 'SEARCH_HEAP_FLOW_COMPLETE' in text,'Flow not complete')
    require('C/RTL co-simulation finished: PASS' in text,'Missing RTL completion')
    segments=text.split('Running: cosim_design')
    require(len(segments)==2,'Unexpected cosim flow')
    golden(segments[0],1);golden(segments[1],2)
    solution=Path(plan['project'])/'solution'
    csim=solution/'csim/report/search_heap_top_csim.log';golden(csim.read_text(),1)
    synth=solution/'syn/report/search_heap_top_csynth.xml'
    cosim=solution/'sim/report/search_heap_top_cosim.rpt'
    trans=solution/'sim/report/verilog/result.transaction.rpt'
    require(re.search(r'Verilog\s*\|\s*Pass',cosim.read_text()),'RTL not passing')
    cycles=transactions(trans.read_text());xml=ET.parse(synth).getroot()
    require(xml.findtext('UserAssignments/Part')==plan['part']=='xcu280-fsvh2892-2L-e','Part mismatch')
    require(float(xml.findtext('UserAssignments/TargetClockPeriod'))==plan['clock_ns']==5,'Clock mismatch')
    rtl=sorted((solution/'syn/verilog').glob('*.v'));require(rtl,'No synthesized RTL')
    artifacts=[plan_path,receipt_path,log,csim,synth,cosim,trans,Path(__file__).resolve(),*rtl]
    return {'status':'heap_component_csim_synthesis_rtl_independently_verified','artifacts':{str(p):digest(p) for p in artifacts},
            'transactions':2,'operations_per_transaction':4096,'capacity':1023,'cycles':cycles,
            'estimated_clock_ns':float(xml.findtext('PerformanceEstimates/SummaryOfTimingAnalysis/EstimatedClockPeriod')),
            'estimated_resources':{e.tag:int(e.text) for e in xml.find('AreaEstimates/Resources')},
            'warnings':[s for s in text.splitlines() if s.startswith('WARNING:')],
            'limitations':['Fixed 1023-entry component; complete search and occupancy not synthesized.',
                           'No physical timing closure, board runtime, or full-workload FPGA evidence.',
                           'Test covers valid 4096-operation calls; operations>4096 early return is not tested.']}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--bundle',required=True,type=Path);parser.add_argument('--output',required=True,type=Path);a=parser.parse_args()
    report=audit(a.bundle.resolve())
    with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({k:report[k] for k in ['status','cycles','estimated_clock_ns','estimated_resources']}))

if __name__=='__main__':main()
