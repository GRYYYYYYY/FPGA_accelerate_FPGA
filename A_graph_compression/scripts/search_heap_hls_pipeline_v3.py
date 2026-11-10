#!/usr/bin/env python3
"""Isolated 2022.2 heap component Csim/synthesis/RTL verification."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/derived/search_heap_hls_20261024_v3'
PROJECT=ROOT/'build/search_heap_hls_20261024_v3'
HLS=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls')
def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,value):
    p=OUT/name;t=p.with_suffix('.tmp');t.write_text(json.dumps(value,indent=2)+'\n');t.replace(p)
def main():
    if PROJECT.exists():raise RuntimeError('Existing project; inspect original owner')
    OUT.mkdir(parents=True,exist_ok=False)
    source=OUT/'source';source.mkdir()
    files={}
    for name in ['search_heap.hpp','search_heap_top_v3.cpp','test_search_heap_top.cpp','run_search_heap_v3.tcl']:
        p=ROOT/'hardware/vitis'/name;files[str(p)]=digest(p);shutil.copyfile(p,source/name)
    files[str(Path(__file__).resolve())]=digest(__file__)
    copied={str(p):digest(p) for p in source.iterdir()}
    save('plan.json',{'files':files,'copied':copied,'project':str(PROJECT),'cpu':120,'part':'xcu280-fsvh2892-2L-e','clock_ns':5,'capacity':1023,'scope':'heap component only; no full router or board claim'})
    state={'owner_pid':os.getpid(),'status':'running','stage':'csim_synth_cosim'};save('state.json',state)
    try:
        env=os.environ.copy();env.update(A_SEARCH_HEAP_SOURCE=str(source),A_SEARCH_HEAP_PROJECT=str(PROJECT),LD_PRELOAD='/lib/x86_64-linux-gnu/libudev.so.1')
        command=['taskset','-c','120',str(HLS),'-f',str(source/'run_search_heap_v3.tcl')]
        with (OUT/'flow.log').open('x') as log:
            child=subprocess.Popen(command,cwd=OUT,env=env,stdout=log,stderr=subprocess.STDOUT)
            state.update(child_pid=child.pid,command=command);save('state.json',state);code=child.wait()
        save('receipt.json',{'exit_code':code,'command':command,'log_sha256':digest(OUT/'flow.log')})
        text=(OUT/'flow.log').read_text()
        if code or 'SEARCH_HEAP_FLOW_COMPLETE' not in text or 'ERROR:' in text:raise RuntimeError('HLS flow failed; inspect flow.log')
        for p,h in {**files,**copied}.items():
            if digest(p)!=h:raise RuntimeError('Changed input: '+p)
        synth=PROJECT/'solution/syn/report/search_heap_top_csynth.xml'
        cosim=PROJECT/'solution/sim/report/search_heap_top_cosim.rpt'
        if 'Pass' not in cosim.read_text():raise RuntimeError('No passing RTL result')
        if text.count('HEAP_TOP_ALL_PASS')<2:raise RuntimeError('Missing Csim/RTL golden markers')
        xml=ET.parse(synth).getroot()
        if xml.findtext('UserAssignments/Part')!='xcu280-fsvh2892-2L-e':raise RuntimeError('Part differs')
        if float(xml.findtext('UserAssignments/TargetClockPeriod'))!=5:raise RuntimeError('Clock differs')
        save('report.json',{'status':'component_csim_synthesis_cosim_passed_pending_independent_review','files':files,'copied':copied,'artifacts':{str(p):digest(p) for p in [synth,cosim,OUT/'flow.log',OUT/'receipt.json']},'estimated_clock_ns':float(xml.findtext('PerformanceEstimates/SummaryOfTimingAnalysis/EstimatedClockPeriod')),'estimated_resources':{e.tag:int(e.text) for e in xml.find('AreaEstimates/Resources')},'limitations':['1023-entry component validation only','No full search integration, physical implementation, or board measurements']})
        state.update(status='complete',stage='await_independent_review');state.pop('child_pid',None);save('state.json',state)
    except BaseException as e:
        state.update(status='failed',error=str(e));save('state.json',state);raise
if __name__=='__main__':main()
