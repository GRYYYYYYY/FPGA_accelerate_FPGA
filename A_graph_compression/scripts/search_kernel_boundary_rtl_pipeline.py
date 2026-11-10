#!/usr/bin/env python3
"""Run the eight boundary RTL transactions only after the original replay audit."""
from concurrent.futures import ThreadPoolExecutor,as_completed
import json
import os
from pathlib import Path
import shlex
import subprocess
from prepare_search_kernel_boundary_rtl import ROOT,OUT,PROJECT,digest
from supervise_search_router_chain import save
from search_boundary_rtl_contract import require,golden,transactions
SETUP=ROOT/'results/search_kernel_boundary_setup_20261024_v1.json'
PRIOR=ROOT/'results/search_kernel_xsim_replay_audit_20261024_v1.json'

def main():
    require(not (OUT/'state.json').exists(),'Existing boundary RTL owner; no duplicate launch')
    setup=json.loads(SETUP.read_text());prior=json.loads(PRIOR.read_text())
    require(setup['status']=='state_capacity_boundary_hls_setup_verified_rtl_pending','Missing boundary setup proof')
    require(prior['status']=='unchanged_search_kernel_rtl_replay_and_original_postcheck_verified','Original replay not audited')
    for p,h in {**setup['artifacts'],**setup['generated']}.items():require(digest(p)==h,'Changed prepared boundary artifact '+p)
    bindings={str(p):digest(p) for p in [SETUP,PRIOR,Path(__file__).resolve(),ROOT/'scripts/check_search_kernel_boundary_rtl.py',ROOT/'scripts/search_boundary_rtl_contract.py']}
    jobs=[]
    for mode,cpu in [('csr',120),('compact',123)]:
        directory=PROJECT/mode/'solution/sim/verilog';script=directory/'run_xsim.sh'
        commands=[shlex.split(s) for s in script.read_text().splitlines() if s.strip() and not s.strip().startswith('#')]
        require(len(commands)==2 and Path(commands[0][0]).name=='xelab' and Path(commands[1][0]).name=='xsim','Unexpected simulation driver')
        require(commands[1][-2:]==['-tclbatch','search_kernel_top.tcl'],'Unexpected simulation script')
        bounded=OUT/(mode+'.bounded.tcl')
        with bounded.open('x') as f:f.write('run 100 ms\nputs BOUNDARY_BOUNDED_RUN_RETURNED\nquit\n')
        bindings[str(bounded)]=digest(bounded)
        prefix=['prlimit','--stack=67108864:67108864','--','taskset','-c',str(cpu)]
        jobs.append({'mode':mode,'cpu':cpu,'directory':str(directory),'elaborate':prefix+commands[0],
            'rtl':prefix+commands[1][:-1]+[str(bounded)],'postcheck':prefix+[str(directory.parent/'wrapc_pc/cosim.pc.exe')],
            'postcheck_directory':str(directory.parent/'wrapc_pc')})
    save(OUT/'execution_plan.json',{'files':bindings,'jobs':jobs,'stack_bytes':67108864,'bound_ns':100000000,'prepared_report_sha256':digest(SETUP),'prior_replay_sha256':digest(PRIOR)})
    state={'owner_pid':os.getpid(),'status':'running','stage':'rtl_and_original_postcheck','completed':[]}
    def update():
        p=OUT/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(OUT/'state.json')
    update()
    def run(job):
        mode=job['mode'];mid=0 if mode=='csr' else 1;env=os.environ.copy();env['LD_PRELOAD']='/lib/x86_64-linux-gnu/libudev.so.1'
        for phase in ['elaborate','rtl','postcheck']:
            log=OUT/(mode+'.'+phase+'.log');cwd=job['postcheck_directory'] if phase=='postcheck' else job['directory']
            with log.open('x') as stream:
                child=subprocess.Popen(job[phase],cwd=cwd,env=env,stdout=stream,stderr=subprocess.STDOUT)
                save(OUT/(mode+'.'+phase+'.submission.json'),{'pid':child.pid,'command':job[phase],'cwd':cwd,'plan_sha256':digest(OUT/'execution_plan.json')});code=child.wait()
            save(OUT/(mode+'.'+phase+'.receipt.json'),{'exit_code':code,'command':job[phase],'log_sha256':digest(log)})
            text=log.read_text(errors='replace')
            require(code==0 and 'ERROR:' not in text and 'FATAL_ERROR' not in text,'Boundary phase failed '+mode+' '+phase)
            if phase=='rtl':
                require('BOUNDARY_BOUNDED_RUN_RETURNED' in text,'Bounded simulation did not return')
                transactions((Path(cwd)/'search_kernel_top.performance.result.transaction.xml').read_text())
            if phase=='postcheck':golden(text,mid)
        return mode
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            for f in as_completed([pool.submit(run,j) for j in jobs]):state['completed'].append(f.result());update()
        state.update(status='complete',stage='pending_independent_boundary_rtl_audit');update()
    except BaseException as error:
        state.update(status='failed',error=str(error));update();raise

if __name__=='__main__':main()
