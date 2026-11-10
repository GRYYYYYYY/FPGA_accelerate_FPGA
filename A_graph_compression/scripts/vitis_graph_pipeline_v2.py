#!/usr/bin/env python3
"""Own both independent wrapper Csim/synthesis/RTL/export chains exactly once."""
from concurrent.futures import ThreadPoolExecutor,as_completed
import json
import os
from pathlib import Path
import subprocess
from check_template_scope import digest
from real_experiment import write_new
ROOT=Path(__file__).resolve().parents[1]
BUNDLE=ROOT/'data/derived/vitis_graph_kernel_20261023_v2'
HLS=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls')


def save(path,data):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(path)


def run_mode(mode,cpu):
    state_path=BUNDLE/(mode+'.state.json')
    state={'owner_pid':os.getpid(),'mode':mode,'cpu':cpu,'status':'running','steps':[]}
    save(state_path,state)
    try:
        for stage in ('synth','cosim','export'):
            env=os.environ.copy();env.update(LD_PRELOAD='/lib/x86_64-linux-gnu/libudev.so.1',
                A_VITIS_SOURCE=str(BUNDLE/mode),A_VITIS_PROJECT=str(ROOT/'build'/f'vitis_graph_{mode}_20261023_v2'),A_VITIS_STAGE=stage)
            command=['taskset','-c',str(cpu),str(HLS),'-f',str(ROOT/'hardware/vitis/run.tcl')]
            log=BUNDLE/mode/(stage+'.log')
            with log.open('x') as stream:
                child=subprocess.Popen(command,cwd=BUNDLE/mode,env=env,stdout=stream,stderr=subprocess.STDOUT)
                state.update(stage=stage,child_pid=child.pid,command=command);save(state_path,state)
                code=child.wait()
            text=log.read_text();marker='VITIS_GRAPH_'+stage.upper()+'_COMPLETE'
            receipt={'stage':stage,'exit_code':code,'completion_marker':marker in text,'log_sha256':digest(log),'command':command}
            write_new(BUNDLE/mode/(stage+'.receipt.json'),receipt)
            state['steps'].append(receipt);state.pop('child_pid',None);save(state_path,state)
            if code or marker not in text or 'ERROR:' in text:raise RuntimeError(mode+'/'+stage+' failed')
        state.update(status='complete',stage='exported');save(state_path,state)
        return mode
    except Exception as exc:
        state.update(status='failed',error=str(exc));save(state_path,state);raise


def main():
    plan_path=BUNDLE/'plan.json';plan=json.loads(plan_path.read_text())
    for path,value in {**plan['files'],**plan['generated']}.items():
        if digest(path)!=value:raise ValueError('Prepared kernel source changed')
    if not {122,123}<=os.sched_getaffinity(0):raise ValueError('Build CPUs unavailable')
    state_path=BUNDLE/'pipeline.json'
    state={'owner_pid':os.getpid(),'status':'running','stage':'hls_flows','plan_sha256':digest(plan_path),
        'files':{str(Path(__file__).resolve()):digest(Path(__file__)),str(ROOT/'hardware/vitis/run.tcl'):digest(ROOT/'hardware/vitis/run.tcl')},'completed_modes':[]}
    write_new(state_path,state)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(run_mode,mode,cpu) for mode,cpu in [('csr',122),('compact',123)]]
            for result in as_completed(futures):
                state['completed_modes'].append(result.result());save(state_path,state)
        for path,value in {**plan['files'],**plan['generated'],**state['files']}.items():
            if digest(path)!=value:raise ValueError('Frozen HLS dependency changed')
        state.update(status='complete',stage='await_independent_artifact_audit');save(state_path,state)
    except Exception as exc:
        state.update(status='failed',error=str(exc));save(state_path,state);raise


if __name__=='__main__':main()
