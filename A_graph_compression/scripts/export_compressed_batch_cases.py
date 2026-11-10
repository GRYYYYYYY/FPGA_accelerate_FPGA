#!/usr/bin/env python3
"""After the existing400-case gate, export and independently decode every case."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from check_vitis_kernel import digest,require
from supervise_batch_hls import identity
from read_batch_trace_v3 import decode_file
ROOT=Path(__file__).resolve().parents[1]
def main():
    original=Path('/tmp/A_graph_compression_recovery_20261025_v1/compressed_batch_router');out=original/'exact_trace_export';out.mkdir(exist_ok=False)
    old=json.loads((original/'state.json').read_text());pid=old['owner_pid'];observed=identity(pid) if old['status']=='running' else None
    state=dict(owner_pid=os.getpid(),status='running',stage='await_original_differential',original_owner=pid)
    def save():
        p=out/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(out/'state.json')
    save()
    try:
        while True:
            current=json.loads((original/'state.json').read_text());require(current['owner_pid']==pid,'Original owner changed')
            if current['status']!='running':break
            require(observed is not None and identity(pid)==observed,'Original owner missing/changed; do not restart');time.sleep(10)
        require(current['status']=='complete','Original differential failed')
        state['stage']='component_audit';save()
        cmd=['python3',str(ROOT/'scripts/check_compressed_batch_component.py')]
        with (out/'component_audit.log').open('x') as f:code=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT).returncode
        require(code==0,'Component audit failed')
        proof=ROOT/'results/compressed_batch_component_20261025_v1.json';d=json.loads(proof.read_text())
        for p,h in d['files'].items():require(digest(p)==h,'Changed complete differential proof')
        state['stage']='export400';save();env={k:v for k,v in os.environ.items() if k!='LD_PRELOAD'};env.update(ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1',A_BATCH_TRACE_OUTPUT_PREFIX=str(out/'case'))
        cmd=['taskset','-c','125',str(original/'differential'),str(original/'source/sites.txt')]
        with (out/'export.log').open('x') as f:
            child=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT);state['child_pid']=child.pid;save();code=child.wait()
        (out/'export.receipt.json').write_text(json.dumps(dict(command=cmd,exit_code=code,log_sha256=digest(out/'export.log')),indent=2)+'\n');require(code==0,'Trace export failed')
        require((out/'export.log').read_text()==(original/'differential.log').read_text(),'Export changed full native differential')
        paths=sorted(out.glob('case_*.bin'));require(len(paths)==400,'Missing/duplicate trace exports')
        state['stage']='independent_decode400';save();summaries=[];searches=rounds=nets=0
        for path in paths:
            # Synthetic graph domain is encoded in the first net snapshot's
            # tree metadata, cross-checked by every subsequent reader component.
            import struct
            raw=path.read_bytes();w=list(struct.unpack('<%dQ'%(len(raw)//8),raw));at=8;nodes=None
            while at<len(w):
                if w[at]==2:nodes=w[at+90];break
                at+=w[at+1]
            require(nodes is not None,'Missing domain-bearing net snapshot')
            r=decode_file(path,nodes);require(r['complete_batch'],'Synthetic reset trace not complete')
            searches+=len(r['searches']);nets+=len(r['nets']);rounds+=sum(x['phase']==0 for x in r['rounds'])
            summaries.append(dict(path=str(path),sha256=digest(path),nodes=nodes,searches=len(r['searches']),nets=len(r['nets']),terminal=r['terminal'],words=r['metadata'][2]))
        require(searches==4938 and nets==3750 and rounds==1250,'Independent trace coverage differs')
        files={**d['files'],str(proof):digest(proof)}
        for p in [Path(__file__).resolve(),ROOT/'scripts/check_compressed_batch_component.py',out/'export.log',out/'export.receipt.json',*paths]:files[str(p)]=digest(p)
        for name in ['read_batch_trace_v3.py','read_compressed_search_trace.py','read_trace_set_codec.py','read_batch_trace_v2.py','read_batch_trace.py','read_net_trace.py','read_round_trace.py','read_search_trace.py']:
            p=ROOT/'scripts'/name;files[str(p)]=digest(p)
        r=dict(status='compressed_batch_all400_native_differential_and_exact_trace_independently_verified_real_workload_pending',files=files,traces=summaries,cases=400,searches=searches,net_snapshots=nets,rounds=rounds,limits=['Synthetic CPU under sanitizers; no real full workload trace export, HLS/RTL/physical/device proof','Artifacts currently in temporary local storage'])
        with (ROOT/'results/compressed_batch_trace_cases_20261025_v1.json').open('x') as f:json.dump(r,f,indent=2);f.write('\n')
        state.update(status='complete',stage='all400_exact_traces_independently_verified');save()
    except BaseException as e:state.update(status='failed',error=str(e));save();raise
if __name__=='__main__':main()
