#!/usr/bin/env python3
"""Independently audit both complete-search HLS flows, without board claims."""
import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from prepare_search_heap_router import digest

def require(ok,message):
    if not ok:raise ValueError(message)

def golden(text,mode,copies):
    require('ERROR:' not in text,'Error in functional log')
    rows=[tuple(map(int,r)) for r in re.findall(r'^SEARCH_KERNEL_TOP_TRANSACTION_PASS mode=(\d+) transaction=(\d+) status=(\d+) cost=(\d+) path=(\d+)$',text,re.M)]
    expected=[(mode,0,0,35,2),(mode,1,3,0,0)]*copies
    require(rows==expected,'Missing or different complete-search transactions')
    markers=re.findall(r'^SEARCH_KERNEL_TOP_ALL_PASS transactions=2 full_workspace_limits=1$',text,re.M)
    require(len(markers)==copies,'Missing full-capacity marker')

def audit(bundle):
    pp=bundle/'plan.json';plan=json.loads(pp.read_text());state_path=bundle/'state.json';state=json.loads(state_path.read_text())
    require(state['status']=='complete' and sorted(state['completed'])==['compact','csr'],'Incomplete mode pair')
    artifacts={**plan['files'],**plan['copied']}
    for p,h in artifacts.items():require(digest(p)==h,'Changed frozen input '+p)
    results=[]
    for job in plan['jobs']:
        mode=job['mode'];mid=job['mode_id'];b=bundle/mode;log=b/'flow.log';rp=b/'receipt.json';sp=b/'submission.json'
        receipt=json.loads(rp.read_text());submission=json.loads(sp.read_text());content=log.read_text()
        require(receipt['exit_code']==0 and receipt['log_sha256']==digest(log),'Failed/changed flow receipt')
        require(receipt['command']==submission['command'] and submission['plan_sha256']==digest(pp),'Different submission')
        require('SEARCH_KERNEL_FLOW_COMPLETE' in content and 'C/RTL co-simulation finished: PASS' in content and 'ERROR:' not in content,'Missing terminal RTL pass')
        segments=content.split('Running: cosim_design');require(len(segments)==2,'Wrong number of cosim invocations')
        golden(segments[0],mid,1);golden(segments[1],mid,2)
        sol=Path(plan['project'])/mode/'solution';csim=sol/'csim/report/search_kernel_top_csim.log'
        golden(csim.read_text(),mid,1)
        synth=sol/'syn/report/search_kernel_top_csynth.xml';cosim=sol/'sim/report/search_kernel_top_cosim.rpt';trans=sol/'sim/report/verilog/result.transaction.rpt'
        require(re.search(r'Verilog\s*\|\s*Pass',cosim.read_text()),'No passing Verilog report')
        pairs=[tuple(map(int,r)) for r in re.findall(r'^transaction\s+(\d+):\s+(\d+)',trans.read_text(),re.M)]
        require([i for i,_ in pairs]==[0,1] and all(c>0 for _,c in pairs),'Incomplete RTL transaction coverage')
        xml=ET.parse(synth).getroot();require(xml.findtext('UserAssignments/Part')==plan['part']=='xcu280-fsvh2892-2L-e','Wrong part')
        require(float(xml.findtext('UserAssignments/TargetClockPeriod'))==plan['clock_ns']==5,'Wrong target clock')
        rtl=sorted((sol/'syn/verilog').glob('*.v'));require(rtl,'Missing generated RTL')
        for p in [log,rp,sp,csim,synth,cosim,trans,*rtl]:artifacts[str(p)]=digest(p)
        prelog=bundle/('preflight_'+mode+'.log');pr=bundle/('preflight_'+mode+'.receipt.json');pre=json.loads(pr.read_text())
        require(pre['exit_code']==0 and pre['log_sha256']==digest(prelog),'Failed testbench preflight');golden(prelog.read_text(),mid,1)
        for p in [prelog,pr]:artifacts[str(p)]=digest(p)
        results.append({'mode':mode,'cycles':[c for _,c in pairs],'estimated_clock_ns':float(xml.findtext('PerformanceEstimates/SummaryOfTimingAnalysis/EstimatedClockPeriod')),
            'estimated_resources':{e.tag:int(e.text) for e in xml.find('AreaEstimates/Resources')},'warnings':[line for line in content.splitlines() if line.startswith('WARNING:')],
            'automatic_pipeline_log_lines':[line for line in content.splitlines() if 'auto' in line.lower() and 'pipelin' in line.lower()]})
    require({(j['mode'],j['mode_id']) for j in plan['jobs']}=={('csr',0),('compact',1)},'Wrong mode matrix')
    for p in [pp,state_path,Path(__file__).resolve()]:artifacts[str(p)]=digest(p)
    return {'status':'complete_single_search_top_csim_synthesis_two_transaction_rtl_verified','results':results,'artifacts':artifacts,
        'scope':plan['scope'],'limitations':plan['limitations']+['Functional synthetic RTL workloads; not full real-graph traffic or 1062-net negotiated routing.','HLS timing/resource estimates are not post-route timing or physical-board measurements.']}

def main():
    p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    report=audit(a.bundle.resolve())
    with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({'status':report['status'],'results':report['results']}))

if __name__=='__main__':main()
