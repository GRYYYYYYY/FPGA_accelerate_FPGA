#!/usr/bin/env python3
"""Audit new Csim/vector generation and unchanged full production RTL."""
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from prepare_search_kernel_boundary_rtl import ROOT,OUT,PROJECT,digest
from search_boundary_rtl_contract import require,golden

def main():
    pp=OUT/'prepare_plan.json';plan=json.loads(pp.read_text());state=OUT/'prepare_state.json';s=json.loads(state.read_text())
    require(s['status']=='complete' and s['completed']==['csr','compact'],'Boundary preparation incomplete')
    artifacts={**plan['files'],**plan['synthesis'],**plan['initial_metadata']}
    for p,h in artifacts.items():require(digest(p)==h,'Changed boundary preparation input '+p)
    require([j['mode'] for j in plan['jobs']]==['csr','compact'],'Different boundary mode pair')
    generated={};results=[]
    for job in plan['jobs']:
        mode=job['mode'];mid=0 if mode=='csr' else 1
        log=OUT/(mode+'.prepare.log');rp=OUT/(mode+'.prepare.receipt.json');sp=OUT/(mode+'.prepare.submission.json')
        r=json.loads(rp.read_text());sub=json.loads(sp.read_text());text=log.read_text()
        require(r['exit_code']==0 and r['command']==sub['command']==job['command'],'Failed/different setup')
        require(r['log_sha256']==digest(log) and sub['plan_sha256']==digest(pp),'Changed preparation receipt')
        require('BOUNDARY_COSIM_SETUP_COMPLETE' in text and 'BOUNDARY_CSIM_COMPLETE' in text,'Missing setup stages')
        before,after=text.split('Running: cosim_design',1);golden(before,mid);golden(after,mid)
        sol=PROJECT/mode/'solution';csim=sol/'csim/report/search_kernel_top_csim.log';golden(csim.read_text(),mid)
        tb=sol/'sim/verilog/search_kernel_top.autotb.v'
        require(re.search(r'parameter AUTOTB_TRANSACTION_NUM = 8;',tb.read_text()),'Wrong generated RTL transaction count')
        rtl=sol/'sim/verilog/search_kernel_top.v';synth=sol/'syn/verilog/search_kernel_top.v'
        require(digest(rtl)==digest(synth),'Simulated top differs from production synthesis')
        app=ET.parse(PROJECT/mode/'hls.app').getroot();source=app.findall('files/file')
        require(len(source)==2 and sum(x.attrib.get('tb')=='1' for x in source)==1,'Unexpected HLS source matrix')
        for p in [log,rp,sp,csim,PROJECT/mode/'hls.app',sol/'solution.aps']:artifacts[str(p)]=digest(p)
        inputs=[*list((sol/'sim/verilog').glob('*')),*list((sol/'sim/tv/cdatafile').glob('*'))]
        inputs += [sol/'sim/wrapc_pc/cosim.pc.exe',sol/'sim/wrapc_pc/apatb_search_kernel_top.cpp']
        for p in inputs:
            if p.is_file() and (p.suffix in ['.v','.sv','.dat','.tcl','.sh','.prj','.exe','.cpp']):generated[str(p)]=digest(p)
        require(str(sol/'sim/wrapc_pc/cosim.pc.exe') in generated,'Missing original C postcheck')
        results.append({'mode':mode,'csim_transactions':8,'vector_generation_transactions':8,'rtl_executed':False})
    for p in [pp,state,Path(__file__).resolve(),ROOT/'scripts/search_boundary_rtl_contract.py']:artifacts[str(p)]=digest(p)
    report={'status':'state_capacity_boundary_hls_setup_verified_rtl_pending','results':results,'artifacts':artifacts,'generated':generated,'scope':plan['scope'],'limitations':plan['limitations']}
    output=ROOT/'results/search_kernel_boundary_setup_20261024_v1.json'
    with output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(report['status'])

if __name__=='__main__':main()
