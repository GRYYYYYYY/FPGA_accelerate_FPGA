#!/usr/bin/env python3
"""Observe the existing software chain, then validate actual U280 graph backends."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
HLS=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls')
PREFIX=ROOT/'results/hls_u280_pipeline_20261022_v1'
BUNDLE=ROOT/'data/derived/hls_u280_fixtures_20261022_v1'


def run_variant(variant):
    prefix=ROOT/'results'/('hls_u280_'+variant+'_20261022_v1')
    state={'owner_pid':os.getpid(),'variant':variant,'status':'running','steps':[]}
    def save():
        temp=prefix.with_suffix('.tmp');temp.write_text(json.dumps(state,indent=2)+'\n')
        temp.replace(prefix.with_suffix('.json'))
    save()
    try:
        for stage in ['synth','cosim','impl']:
            state['stage']=stage;save()
            env=os.environ.copy();env.update(LD_PRELOAD='/lib/x86_64-linux-gnu/libudev.so.1',
                A_FIXED_SOURCE=str(BUNDLE/variant),A_FIXED_PROJECT=str(ROOT/'build'/('hls_u280_'+variant+'_20261022_v1')),A_FIXED_STAGE=stage)
            log=prefix.with_name(prefix.name+'_'+stage+'.log')
            with log.open('x') as stream:
                child=subprocess.Popen([str(HLS),'-f',str(ROOT/'hardware/hls/run_fixed.tcl')],cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT)
                state['child_pid']=child.pid;save();code=child.wait()
            content=log.read_text();marker='FIXED_'+stage.upper()+'_COMPLETE'
            state['steps'].append({'stage':stage,'exit_code':code,'log':str(log.relative_to(ROOT)),
                                   'completion_marker':marker in content})
            state.pop('child_pid',None);save()
            if code or marker not in content or 'ERROR:' in content:raise RuntimeError(variant+'/'+stage+' failed')
        state['status']='completed';state['stage']='await_report';save()
        return variant
    except BaseException as exc:
        state['status']='failed';state['error']=str(exc);save();raise


def main():
    lock=PREFIX.with_suffix('.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    state={'owner_pid':os.getpid(),'status':'running','stage':'wait_existing_software_chain',
           'started_utc':datetime.now(timezone.utc).isoformat(),'completed_variants':[]}
    def save():
        tmp=PREFIX.with_suffix('.tmp');tmp.write_text(json.dumps(state,indent=2)+'\n');tmp.replace(PREFIX.with_suffix('.json'))
    save()
    try:
        experiment=ROOT/'data/derived/netlist_integration16_20261022_v1'
        while not (experiment/'report.json').exists():
            parent=json.loads((ROOT/'results/netlist_pipeline_20261022_v1.json').read_text())
            pid=parent['owner_pid'];proc=Path('/proc')/str(pid)
            try:
                command=(proc/'cmdline').read_bytes()
                status=(proc/'stat').read_text().split(') ',1)[1].split()[0]
            except FileNotFoundError:
                raise RuntimeError('Software chain process ended before its integration report')
            if status=='Z' or b'netlist_pipeline.py' not in command or parent['status']=='failed':
                raise RuntimeError('Existing software chain stopped or failed; reconcile before hardware work')
            time.sleep(30)
        state['stage']='prepare_actual_u280_fixtures';save()
        log=ROOT/'results/hls_u280_prepare_20261022_v1.log'
        with log.open('x') as stream:
            child=subprocess.Popen([sys.executable,str(ROOT/'hardware/hls/prepare_u280_fixtures.py'),
                '--experiment',str(experiment),'--output',str(BUNDLE)],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
            state['child_pid']=child.pid;save();code=child.wait()
        state.pop('child_pid',None)
        if code:raise RuntimeError('Actual U280 fixture preparation failed')
        state['stage']='validate_both_fixed_modes';save()
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(run_variant,variant) for variant in ['csr','compact']]
            for future in as_completed(futures):
                state['completed_variants'].append(future.result());save()
        state['status']='completed';state['stage']='await_actual_u280_report';save()
    except BaseException as exc:
        state['status']='failed';state['error']=str(exc);save();raise


if __name__=='__main__':main()
