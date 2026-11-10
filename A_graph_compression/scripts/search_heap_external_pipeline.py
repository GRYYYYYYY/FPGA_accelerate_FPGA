#!/usr/bin/env python3
"""External-memory heap component validation on the local 2022.2 HLS tool."""
import json
import os
from pathlib import Path
import shutil
import subprocess
from prepare_search_heap_router import digest

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/derived/search_heap_external_20261024_v1'
PROJECT=ROOT/'build/search_heap_external_20261024_v1'
HLS=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls')
def save(name,value):
    p=OUT/name;temp=p.with_suffix('.tmp');temp.write_text(json.dumps(value,indent=2)+'\n');temp.replace(p)

def main():
    if PROJECT.exists():raise RuntimeError('Existing project; inspect original owner')
    OUT.mkdir(parents=True,exist_ok=False);source=OUT/'source';source.mkdir();files={}
    for name in ['search_heap.hpp','search_heap_external.hpp','search_heap_external_top.cpp','test_search_heap_external_top.cpp','run_search_heap_external.tcl']:
        p=ROOT/'hardware/vitis'/name;files[str(p)]=digest(p);shutil.copyfile(p,source/name)
    for p in [Path(__file__).resolve(),ROOT/'scripts/check_search_heap_external.py',ROOT/'scripts/prepare_search_heap_router.py']:
        files[str(p)]=digest(p)
    copied={str(p):digest(p) for p in source.iterdir()}
    save('plan.json',{'files':files,'copied':copied,'project':str(PROJECT),'cpu':120,'part':'xcu280-fsvh2892-2L-e','clock_ns':5,'capacity':131072,
                     'scope':'External AXI word-addressed heap component; not complete router or physical board execution'})
    state={'owner_pid':os.getpid(),'status':'running','stage':'csim_synth_cosim'};save('state.json',state)
    try:
        env=os.environ.copy();env.update(A_SEARCH_HEAP_SOURCE=str(source),A_SEARCH_HEAP_PROJECT=str(PROJECT),LD_PRELOAD='/lib/x86_64-linux-gnu/libudev.so.1')
        command=['taskset','-c','120',str(HLS),'-f',str(source/'run_search_heap_external.tcl')]
        with (OUT/'flow.log').open('x') as log:
            child=subprocess.Popen(command,cwd=OUT,env=env,stdout=log,stderr=subprocess.STDOUT)
            state.update(child_pid=child.pid,command=command);save('state.json',state);code=child.wait()
        save('receipt.json',{'exit_code':code,'command':command,'log_sha256':digest(OUT/'flow.log')})
        text=(OUT/'flow.log').read_text()
        if code or 'EXTERNAL_HEAP_FLOW_COMPLETE' not in text or 'ERROR:' in text:raise RuntimeError('External heap HLS flow failed')
        for p,h in {**files,**copied}.items():
            if digest(p)!=h:raise RuntimeError('Changed input '+p)
        state.update(stage='independent_audit');state.pop('child_pid',None);save('state.json',state)
        report=ROOT/'results/search_heap_external_audit_20261024_v1.json'
        command=['python3',str(ROOT/'scripts/check_search_heap_external.py'),'--bundle',str(OUT),'--output',str(report)]
        with (OUT/'audit.log').open('x') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
        save('audit_receipt.json',{'exit_code':r.returncode,'command':command,'log_sha256':digest(OUT/'audit.log'),'report_sha256':digest(report) if report.exists() else None})
        if r.returncode:raise RuntimeError('External heap independent audit failed')
        state.update(status='complete',stage='independently_audited');save('state.json',state)
    except BaseException as e:
        state.update(status='failed',error=str(e));save('state.json',state);raise

if __name__=='__main__':main()
