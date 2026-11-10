#!/usr/bin/env python3
"""Replay unchanged v3 snapshots with a bounded run and a larger process stack."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import re
import resource
import shutil
import subprocess
from prepare_search_heap_router import ROOT,digest
from supervise_search_router_chain import save
OUT=ROOT/'data/derived/search_kernel_xsim_stack_20261024_v1'
PRIOR=ROOT/'data/derived/search_kernel_hls_20261024_v3'
PROJECT=ROOT/'build/search_kernel_hls_20261024_v3'
XSIM=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin/xsim')

def main():
    old_state=json.loads((PRIOR/'state.json').read_text())
    if old_state['status']!='failed':raise RuntimeError('Original flow is not terminal failed')
    original=json.loads((PRIOR/'plan.json').read_text())
    files={**original['files'],**original['copied']}
    for p,h in files.items():
        if digest(p)!=h:raise RuntimeError('Changed HLS input '+p)
    for p in [PRIOR/'plan.json',PRIOR/'state.json',Path(__file__).resolve()]:files[str(p)]=digest(p)
    OUT.mkdir(exist_ok=False)
    state={'owner_pid':os.getpid(),'status':'running','stage':'prepare_isolated_replays','completed':[]}
    def update():
        p=OUT/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(OUT/'state.json')
    update()
    try:
        jobs=[];copies={}
        for mode,cpu in [('csr',120),('compact',123)]:
            old=PRIOR/mode;receipt=json.loads((old/'receipt.json').read_text());log=(old/'flow.log').read_text()
            if receipt['exit_code']==0 or receipt['log_sha256']!=digest(old/'flow.log') or 'Time: 0 ps  Iteration: 0' not in log or 'FATAL_ERROR: Vivado Simulator kernel' not in log:
                raise RuntimeError('Different failure signature '+mode)
            for p in [old/'receipt.json',old/'submission.json',old/'flow.log']:files[str(p)]=digest(p)
            source=PROJECT/mode/'solution/sim';destination=OUT/mode/'sim';destination.parent.mkdir()
            subprocess.run(['cp','-a','--reflink=auto',str(source),str(destination)],check=True)
            # Remove only copied failed outputs. Preserve every original artifact.
            for name in ['report','tv/rtldatafile']:
                p=destination/name;shutil.rmtree(p);p.mkdir(parents=True)
            for p in (destination/'verilog').glob('*.result.*'):p.unlink()
            snapshot=destination/'verilog/xsim.dir/search_kernel_top'
            for name in ['xsimcrash.log','xsimkernel.log']:
                p=snapshot/name
                if p.exists():p.unlink()
            immutable=[*list((source/'tv/cdatafile').rglob('*')),*list((source/'wrapc_pc').rglob('*'))]
            immutable += [p for p in (source/'verilog').rglob('*') if p.is_file() and (p.suffix in ['.v','.sv','.prj','.mem','.dbg','.xdbg','.rtti','.reloc','.type','.svtype'] or p.name=='xsimk')]
            for p in immutable:
                if p.is_file():
                    h=digest(p);q=destination/p.relative_to(source)
                    if digest(q)!=h:raise RuntimeError('Replay copy differs '+str(q))
                    files[str(p)]=h;copies[str(q)]=h
            bounded=destination/'verilog/replay_bounded.tcl'
            bounded.write_text('run 100 ms\nputs SEARCH_REPLAY_BOUNDED_RUN_RETURNED\nquit\n')
            copies[str(bounded)]=digest(bounded)
            command=['prlimit','--stack=67108864:67108864','--','taskset','-c',str(cpu),str(XSIM),'--noieeewarnings','search_kernel_top','-tclbatch',bounded.name]
            jobs.append({'mode':mode,'cpu':cpu,'command':command,'cwd':str(destination/'verilog'),
                'postcheck':[str(destination/'wrapc_pc/cosim.pc.exe')],'postcheck_cwd':str(destination/'wrapc_pc')})
        save(OUT/'plan.json',{'files':files,'copied':copies,'jobs':jobs,'stack_bytes':67108864,'launch_parent_stack_limit':resource.getrlimit(resource.RLIMIT_STACK),
            'runtime_bound_ns':100000000,'unchanged':'Copied synthesized RTL, compiled XSim snapshots, C input vectors, postcheck binary and original two-transaction oracle.',
            'hypothesis':'Original failing FSM process has 0xbd4d08-byte native stack frame; current parent default soft stack is 8MiB. Test 64MiB only on new simulator subprocesses.',
            'limitations':['Simulator environment recovery attempt, not a kernel logic or capacity change.','Must complete both RTL transactions and original C postcheck before functional pass.','Independent audit still required; no board or physical timing claim.']})
        state['stage']='bounded_rtl_and_original_postcheck';update()
        def run(job):
            mode=job['mode'];folder=OUT/mode;env=os.environ.copy();env['LD_PRELOAD']='/lib/x86_64-linux-gnu/libudev.so.1'
            for phase,command,cwd in [('rtl',job['command'],job['cwd']),('postcheck',job['postcheck'],job['postcheck_cwd'])]:
                log=folder/(phase+'.log')
                with log.open('x') as stream:
                    child=subprocess.Popen(command,cwd=cwd,env=env,stdout=stream,stderr=subprocess.STDOUT)
                    save(folder/(phase+'.submission.json'),{'command':command,'cwd':cwd,'pid':child.pid,'plan_sha256':digest(OUT/'plan.json')});code=child.wait()
                save(folder/(phase+'.receipt.json'),{'exit_code':code,'command':command,'log_sha256':digest(log)})
                text=log.read_text(errors='replace')
                if code or 'FATAL_ERROR' in text or 'ERROR:' in text:raise RuntimeError('Replay failed '+mode+' '+phase)
                if phase=='rtl':
                    perf=Path(cwd)/'search_kernel_top.performance.result.transaction.xml'
                    if not perf.exists():raise RuntimeError('No completed RTL transactions before bound '+mode)
                    shutil.copyfile(perf,folder/'rtl_transactions.xml')
                else:
                    mid=0 if mode=='csr' else 1
                    rows=[tuple(map(int,r)) for r in re.findall(r'^SEARCH_KERNEL_TOP_TRANSACTION_PASS mode=(\d+) transaction=(\d+) status=(\d+) cost=(\d+) path=(\d+)$',text,re.M)]
                    if rows!=[(mid,0,0,35,2),(mid,1,3,0,0)] or text.count('SEARCH_KERNEL_TOP_ALL_PASS transactions=2 full_workspace_limits=1')!=1:raise RuntimeError('Original RTL postcheck did not pass '+mode)
            return mode
        with ThreadPoolExecutor(max_workers=2) as pool:
            for future in as_completed([pool.submit(run,j) for j in jobs]):state['completed'].append(future.result());update()
        state.update(status='complete',stage='pending_independent_replay_audit');update()
    except BaseException as error:
        state.update(status='failed',error=str(error));update();raise

if __name__=='__main__':main()
