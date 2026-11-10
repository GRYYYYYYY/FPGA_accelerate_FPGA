#!/usr/bin/env python3
"""Single-owner validation of complete 128-MiB regional decoder fixtures."""
from concurrent.futures import ThreadPoolExecutor,as_completed
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]
BUNDLE=ROOT/'data/derived/hls_region_fixtures_20261023_v1'
PREFIX=ROOT/'results/hls_region_pipeline_20261023_v1'
HLS=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls')
FIXTURE_PID=1478184


def save(path,state):
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(state,indent=2)+'\n');temp.replace(path)


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def variant(mode):
    prefix=ROOT/'results'/('hls_region_'+mode+'_20261023_v1')
    state={'owner_pid':os.getpid(),'mode':mode,'status':'running','steps':[]}
    try:
        for stage in ('synth','cosim','impl'):
            env=os.environ.copy();env.update(LD_PRELOAD='/lib/x86_64-linux-gnu/libudev.so.1',
                A_FIXED_SOURCE=str(BUNDLE/mode),A_FIXED_PROJECT=str(ROOT/'build'/('hls_region_'+mode+'_20261023_v1')),A_FIXED_STAGE=stage)
            log=prefix.with_name(prefix.name+'_'+stage+'.log')
            with log.open('x') as stream:
                child=subprocess.Popen([str(HLS),'-f',str(ROOT/'hardware/hls/run_fixed.tcl')],cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT)
                state.update(stage=stage,child_pid=child.pid);save(prefix.with_suffix('.json'),state)
                code=child.wait()
            content=log.read_text();marker='FIXED_'+stage.upper()+'_COMPLETE'
            state['steps'].append({'stage':stage,'exit_code':code,'completion_marker':marker in content,'log':str(log.relative_to(ROOT))})
            state.pop('child_pid',None);save(prefix.with_suffix('.json'),state)
            if code or marker not in content or 'ERROR:' in content:raise RuntimeError(mode+'/'+stage+' failed')
        state.update(status='complete',stage='await_report');save(prefix.with_suffix('.json'),state)
        return mode
    except BaseException as exc:
        state.update(status='failed',error=str(exc));save(prefix.with_suffix('.json'),state);raise


def main():
    lock=PREFIX.with_suffix('.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    path=PREFIX.with_suffix('.json')
    if path.exists():raise ValueError('Refusing existing pipeline state')
    frozen={str(p):digest(p) for p in (Path(__file__),ROOT/'hardware/hls/run_fixed.tcl',ROOT/'hardware/hls/prepare_u280_fixtures.py',ROOT/'hardware/hls/prepare_fixtures.py')}
    state={'owner_pid':os.getpid(),'status':'running','stage':'wait_fixture_owner','fixture_owner_pid':FIXTURE_PID,'completed_modes':[],'code_sha256':frozen}
    save(path,state)
    try:
        while True:
            proc=Path('/proc')/str(FIXTURE_PID)
            try:
                command=(proc/'cmdline').read_bytes()
                status=(proc/'stat').read_text().split(') ',1)[1].split()[0]
            except FileNotFoundError:break
            if status=='Z':break
            if b'prepare_u280_fixtures.py' not in command:raise ValueError('Fixture process identity changed')
            time.sleep(10)
        manifest=json.loads((BUNDLE/'manifest.json').read_text())
        if manifest['image_depth_words']!=33554432:raise ValueError('Expected explicit 128-MiB capacity')
        for name,value in frozen.items():
            if digest(Path(name))!=value:raise ValueError('Frozen pipeline source changed')
        for name,value in manifest['files'].items():
            if digest(BUNDLE/name)!=value:raise ValueError('Fixture artifact changed: '+name)
        for info in manifest['image_files'].values():
            image=Path(info['path'])
            if digest(image)!=info['sha256'] or image.stat().st_size>manifest['image_depth_words']*4:raise ValueError('Complete image mismatch/overflow')
        state.update(stage='validate_fixed_modes',fixture_manifest_sha256=digest(BUNDLE/'manifest.json'));save(path,state)
        with ThreadPoolExecutor(max_workers=2) as pool:
            for future in as_completed([pool.submit(variant,m) for m in ('csr','compact')]):
                state['completed_modes'].append(future.result());save(path,state)
        state.update(status='complete',stage='await_regional_decoder_report');save(path,state)
    except BaseException as exc:
        state.update(status='failed',error=str(exc));save(path,state);raise


if __name__=='__main__':main()
