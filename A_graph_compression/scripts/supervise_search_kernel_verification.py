#!/usr/bin/env python3
"""Single owner for prepared boundary audit, existing replay audit and RTL follow-up."""
import json
import os
from pathlib import Path
import subprocess
import time
from supervise_search_router_chain import ROOT,digest,save,live_owner
OUT=ROOT/'data/derived/search_kernel_verification_chain_20261024_v1'
PREP=ROOT/'data/derived/search_kernel_boundary_rtl_20261024_v1'
REPLAY=ROOT/'data/derived/search_kernel_xsim_stack_20261024_v1'


def observe(path,script):
    state=json.loads(path.read_text())
    if state['status']=='complete':return state
    if state['status']!='running':raise RuntimeError('Predecessor failed: '+str(path))
    if not live_owner(state['owner_pid'],script):
        state=json.loads(path.read_text())
        if state['status']=='complete':return state
        raise RuntimeError('Predecessor owner missing; reconcile instead of restarting: '+str(path))
    return state


def main():
    initial=observe(PREP/'prepare_state.json','prepare_search_kernel_boundary_rtl.py')
    observe(REPLAY/'state.json','replay_search_kernel_xsim_stack.py')
    OUT.mkdir(exist_ok=False)
    names=['supervise_search_kernel_verification.py','supervise_search_router_chain.py','prepare_search_heap_router.py',
        'check_search_kernel_boundary_setup.py','check_search_kernel_xsim_replay.py','check_search_kernel_hls.py',
        'search_kernel_boundary_rtl_pipeline.py','check_search_kernel_boundary_rtl.py','search_boundary_rtl_contract.py',
        'prepare_search_kernel_boundary_rtl.py','replay_search_kernel_xsim_stack.py']
    files={str(ROOT/'scripts'/name):digest(ROOT/'scripts'/name) for name in names}
    for p in [PREP/'prepare_plan.json',REPLAY/'plan.json']:files[str(p)]=digest(p)
    save(OUT/'plan.json',{'files':files,'policy':'Observe existing preparation/replay owners. Independently audit prepared cases, then completed replay. Launch boundary RTL once after both gates; audit full eight-transaction matrix. No automatic restart on unknown failure.'})
    state={'owner_pid':os.getpid(),'status':'running','stage':'await_boundary_setup','completed':[],
           'observed_owner':initial['owner_pid'],'observed_stage':initial['stage']}
    def update():
        p=OUT/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(OUT/'state.json')
    update()
    def wait(path,script,stage):
        state['stage']=stage;update()
        while True:
            original=observe(path,script)
            if original['status']=='complete':return
            if state.get('observed_owner')!=original['owner_pid'] or state.get('observed_stage')!=original['stage']:
                state.update(observed_owner=original['owner_pid'],observed_stage=original['stage']);update()
            time.sleep(15)
    def run(stage,script,report=None,status=None):
        for p,h in files.items():
            if digest(p)!=h:raise RuntimeError('Changed verification chain binding '+p)
        if report and report.exists():raise RuntimeError('Audit already exists; reconcile duplicate ownership '+str(report))
        command=['taskset','-c','119','python3',str(ROOT/'scripts'/script)]
        log=OUT/(stage+'.log')
        with log.open('x') as stream:
            child=subprocess.Popen(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
            save(OUT/(stage+'.submission.json'),{'command':command,'pid':child.pid,'plan_sha256':digest(OUT/'plan.json')})
            state.update(stage=stage,child_pid=child.pid);update();code=child.wait()
        save(OUT/(stage+'.receipt.json'),{'exit_code':code,'command':command,'log_sha256':digest(log)})
        if code:raise RuntimeError('Verification stage failed '+stage)
        if report:
            content=json.loads(report.read_text())
            if content['status']!=status:raise RuntimeError('Unexpected independent audit status '+stage)
            save(OUT/(stage+'.gate.json'),{'path':str(report),'sha256':digest(report),'status':status})
        state['completed'].append(stage);update()
    try:
        wait(PREP/'prepare_state.json','prepare_search_kernel_boundary_rtl.py','await_boundary_setup')
        run('boundary_setup_audit','check_search_kernel_boundary_setup.py',ROOT/'results/search_kernel_boundary_setup_20261024_v1.json','state_capacity_boundary_hls_setup_verified_rtl_pending')
        wait(REPLAY/'state.json','replay_search_kernel_xsim_stack.py','await_original_replay')
        run('original_replay_audit','check_search_kernel_xsim_replay.py',ROOT/'results/search_kernel_xsim_replay_audit_20261024_v1.json','unchanged_search_kernel_rtl_replay_and_original_postcheck_verified')
        if (PREP/'state.json').exists():raise RuntimeError('Boundary RTL already acquired an owner')
        run('boundary_rtl','search_kernel_boundary_rtl_pipeline.py')
        run('boundary_rtl_audit','check_search_kernel_boundary_rtl.py',ROOT/'results/search_kernel_boundary_rtl_audit_20261024_v1.json','production_search_top_full_state_capacity_boundaries_rtl_verified')
        state.update(status='complete',stage='original_and_boundary_rtl_independently_audited');update()
    except BaseException as error:
        state.update(status='failed',error=str(error));update();raise

if __name__=='__main__':main()
