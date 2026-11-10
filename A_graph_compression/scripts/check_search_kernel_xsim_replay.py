#!/usr/bin/env python3
"""Audit unchanged v3 RTL replay plus the original C functional postchecker."""
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from replay_search_kernel_xsim_stack import ROOT,OUT,PRIOR,PROJECT,digest
from check_search_kernel_hls import golden,require

def transactions(text):
    rows=[tuple(map(int,row)) for row in re.findall(r'^transaction\s+(\d+):\s+(\d+)\s+(?:\d+|x)\s*$',text,re.M)]
    require([i for i,_ in rows]==[0,1] and all(c>0 for _,c in rows),'Incomplete RTL transactions')
    return [c for _,c in rows]

def main():
    pp=OUT/'plan.json';plan=json.loads(pp.read_text());state_path=OUT/'state.json';state=json.loads(state_path.read_text())
    require(state['status']=='complete' and sorted(state['completed'])==['compact','csr'],'Replay not complete')
    require(plan['stack_bytes']==67108864 and plan['runtime_bound_ns']==100000000,'Different replay setup')
    artifacts={**plan['files'],**plan['copied']}
    for p,h in artifacts.items():require(digest(p)==h,'Changed replay input '+p)
    require([(j['mode'],j['cpu']) for j in plan['jobs']]==[('csr',120),('compact',123)],'Different mode matrix')
    results=[]
    for job in plan['jobs']:
        mode=job['mode'];mid=0 if mode=='csr' else 1;b=OUT/mode
        expected=['prlimit','--stack=67108864:67108864','--','taskset','-c',str(job['cpu'])]
        require(job['command'][:6]==expected,'Stack adjustment not applied to simulator')
        for phase,command,cwd in [('rtl',job['command'],job['cwd']),('postcheck',job['postcheck'],job['postcheck_cwd'])]:
            log=b/(phase+'.log');rp=b/(phase+'.receipt.json');sp=b/(phase+'.submission.json')
            r=json.loads(rp.read_text());s=json.loads(sp.read_text());text=log.read_text(errors='replace')
            require(r['exit_code']==0 and r['command']==s['command']==command and s['cwd']==cwd,'Failed/different replay command')
            require(s['plan_sha256']==digest(pp) and r['log_sha256']==digest(log),'Changed replay receipt')
            require('FATAL_ERROR' not in text and 'ERROR:' not in text and 'runtime error:' not in text,'Replay error')
            if phase=='postcheck':golden(text,mid,1)
            else:require('SEARCH_REPLAY_BOUNDED_RUN_RETURNED' in text and re.search(r'RTL Simulation :\s*2 / 2',text),'Missing completed RTL marker')
            for p in [log,rp,sp]:artifacts[str(p)]=digest(p)
        perf=b/'rtl_transactions.xml';original_perf=b/'sim/verilog/search_kernel_top.performance.result.transaction.xml'
        require(digest(perf)==digest(original_perf),'Changed transaction copy')
        cycles=transactions(perf.read_text())
        sol=PROJECT/mode/'solution';synth=sol/'syn/report/search_kernel_top_csynth.xml';csim=sol/'csim/report/search_kernel_top_csim.log'
        golden(csim.read_text(),mid,1)
        xml=ET.parse(synth).getroot()
        require(xml.findtext('UserAssignments/Part')=='xcu280-fsvh2892-2L-e' and float(xml.findtext('UserAssignments/TargetClockPeriod'))==5,'Wrong synthesis part or clock')
        outputs=sorted((b/'sim/tv/rtldatafile').glob('rtl.*.autotvout_*.dat'))
        require(outputs,'Missing actual RTL output vectors')
        for p in [perf,original_perf,synth,csim,*outputs]:artifacts[str(p)]=digest(p)
        results.append({'mode':mode,'cycles':cycles,'transactions':2,'original_C_postcheck':'passed','estimated_clock_ns':float(xml.findtext('PerformanceEstimates/SummaryOfTimingAnalysis/EstimatedClockPeriod')),
            'estimated_resources':{e.tag:int(e.text) for e in xml.find('AreaEstimates/Resources')}})
    for p in [pp,state_path,Path(__file__).resolve(),ROOT/'scripts/check_search_kernel_hls.py']:artifacts[str(p)]=digest(p)
    report={'status':'unchanged_search_kernel_rtl_replay_and_original_postcheck_verified','results':results,'artifacts':artifacts,'stack_bytes':plan['stack_bytes'],
        'limitations':['Original v3 HLS flow failed at simulator initialization; this is separately audited direct replay of its unchanged compiled RTL snapshot.',
            'Two synthetic transactions per representation; capacity boundary CPU cases are not part of this RTL stimulus.',
            'HLS estimates are not post-route timing closure. No board memory, power or full hardware negotiation evidence.']}
    output=ROOT/'results/search_kernel_xsim_replay_audit_20261024_v1.json'
    with output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({'status':report['status'],'results':results}))

if __name__=='__main__':main()
