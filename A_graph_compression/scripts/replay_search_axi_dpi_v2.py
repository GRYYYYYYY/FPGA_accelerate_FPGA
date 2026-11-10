#!/usr/bin/env python3
"""Replay an already verified full-capacity two-transaction RTL with only storage hooks."""
import json,os,re,shlex,shutil,signal,subprocess,time
from pathlib import Path
from check_vitis_kernel import digest,require
from transform_axi_memory_dpi_v2 import transform
ROOT=Path(__file__).resolve().parents[1];BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1');BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def main():
    cg=Path('/sys/fs/cgroup');require(int((cg/'memory.max').read_text())-int((cg/'memory.current').read_text())>=64*1024**3,'Insufficient cgroup admission margin')
    gate=ROOT/'results/search_packet_width64_rtl_audit_20261025_v1.json';proof=json.loads(gate.read_text());require(proof['rtl_verified'] and proof['cycles']==[2132461,12404],'Missing original actual RTL oracle')
    for p,h in proof['files'].items():require(digest(p)==h,'Changed original actual RTL evidence '+p)
    unit=ROOT/'results/axi_dpi_memory_unit_20261025_v2.json';parity=json.loads(unit.read_text());require(parity['cases']==5,'Five-width storage parity pending')
    for p,h in parity['files'].items():require(digest(p)==h,'Changed storage parity source '+p)
    original=ROOT/'build/search_packet_width64_rtl_20261025_v1/solution/sim'
    out=BASE/'search_axi_dpi_replay_v2';out.mkdir(exist_ok=False);dst=out/'sim'
    state=dict(owner_pid=os.getpid(),status='running',stage='copy_verified_setup')
    def save():
        p=out/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(out/'state.json')
    save()
    try:
        shutil.copytree(original,dst,ignore=lambda directory,names:[n for n in names if n in ['xsim.dir','.Xil','rtldatafile'] or n.endswith(('.log','.pb','.jou')) or 'performance.result' in n])
        (dst/'tv/rtldatafile').mkdir(exist_ok=True)
        directory=dst/'verilog';pc=dst/'wrapc_pc';files={str(gate):digest(gate),str(unit):digest(unit),str(Path(__file__).resolve()):digest(__file__),str(ROOT/'scripts/transform_axi_memory_dpi_v2.py'):digest(ROOT/'scripts/transform_axi_memory_dpi_v2.py')};models=[]
        for p in directory.glob('AESL_axi_master_*.v'):
            before=p.read_text();after,ledger=transform(before);p.write_text(after)
            q=out/(p.stem+'.edits.json');q.write_text(json.dumps(ledger,indent=2)+'\n');models.append(dict(path=str(p),ledger=str(q),before_sha256=digest(original/'verilog'/p.name),after_sha256=digest(p),pages=ledger['pages']));files[str(q)]=digest(q)
        require(len(models)==7,'Different model matrix')
        for p,h in proof['files'].items():
            source=Path(p)
            if source.is_relative_to(original):
                q=dst/source.relative_to(original)
                if 'rtldatafile' in source.parts or 'performance.result' in source.name or source.suffix in ['.log','.pb','.jou']:continue
                if q.name.startswith('AESL_axi_master_') and q.suffix=='.v':continue
                require(q.is_file() and digest(q)==h,'Missing/changed copied DUT/fixture '+str(q));files[str(q)]=h
        cpp=ROOT/'hardware/sim/axi_dpi_memory_v1.cpp';files[str(cpp)]=digest(cpp)
        commands=[shlex.split(l) for l in (directory/'run_xsim.sh').read_text().splitlines() if l.strip() and not l.startswith('#')];require(len(commands)==2,'Unexpected generated simulator commands')
        bounded=out/'bounded.tcl';bounded.write_text('run 10 sec\nputs DPI_REPLAY_BOUNDED_RETURNED\nquit\n');files[str(bounded)]=digest(bounded)
        prefix=['prlimit','--stack=67108864:67108864','--','taskset','-c','122']
        jobs=[('xsc',prefix+[str(BIN/'xsc'),'--cppversion','14',str(cpp)],directory),('elaborate',prefix+['/usr/bin/time','-v']+commands[0]+['-mt','off','--O0','--stats','--sv_lib','dpi','--sv_root','xsim.dir/work/xsc'],directory),('rtl',prefix+commands[1][:-1]+[str(bounded)],directory),('postcheck',prefix+[str(pc/'cosim.pc.exe')],pc)]
        plan=dict(files=files,models=models,commands=[dict(phase=n,command=c,cwd=str(d)) for n,c,d in jobs],original_sim=str(original),transactions=2,depths_unchanged=True,pages_unchanged=True,dut_unchanged=True,simulation_bound_ns=10000000000,resource_abort_free_bytes=16*1024**3)
        (out/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');env={**os.environ,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1'}
        for phase,command,cwd in jobs:
            state['stage']=phase;save();start=time.monotonic()
            with (out/(phase+'.log')).open('x') as f:
                child=subprocess.Popen(command,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);state['child_pid']=child.pid;save();aborted=False
                while child.poll() is None:
                    free=int((cg/'memory.max').read_text())-int((cg/'memory.current').read_text())
                    if free<plan['resource_abort_free_bytes']:
                        os.killpg(child.pid,signal.SIGTERM);aborted=True;break
                    time.sleep(2)
                code=child.wait()
            receipt=dict(exit_code=code,command=command,cwd=str(cwd),elapsed_seconds=time.monotonic()-start,log_sha256=digest(out/(phase+'.log')),resource_admission_abort=aborted)
            (out/(phase+'.receipt.json')).write_text(json.dumps(receipt,indent=2)+'\n');text=(out/(phase+'.log')).read_text(errors='replace')
            require(not aborted and code==0 and not any(x in text for x in ['ERROR:','Fatal:','FATAL_ERROR','runtime error:']),phase+' failed; preserve new attempt')
            if phase=='rtl':require('DPI_REPLAY_BOUNDED_RETURNED' in text and re.search(r'RTL Simulation :\s*2 / 2',text),'Incomplete actual RTL replay')
            if phase=='postcheck':require('SEARCH_KERNEL_TOP_ALL_PASS transactions=2 full_workspace_limits=1' in text,'Original C postcheck failed')
        perf=directory/'search_kernel_top.performance.result.transaction.xml';rows=[tuple(map(int,x)) for x in re.findall(r'^transaction\s+(\d+):\s+(\d+)\s+(?:\d+|x)\s*$',perf.read_text(),re.M)];require([i for i,_ in rows]==[0,1] and all(c>0 for _,c in rows),'Incomplete transaction performance')
        require([c for _,c in rows]==proof['cycles'],'Cycle-level memory-model parity failed')
        outputs=list((dst/'tv/rtldatafile').glob('rtl.*.autotvout_*.dat'));require(outputs,'No actual RTL outputs')
        require({p.name for p in outputs}=={p.name for p in (original/'tv/rtldatafile').glob('rtl.*.autotvout_*.dat')},'Missing or extra complete RTL output file')
        for p in outputs:require(digest(p)==digest(original/'tv/rtldatafile'/p.name),'Complete RTL output differs '+p.name)
        for p,h in files.items():require(digest(p)==h,'Frozen input changed '+p)
        state.update(status='complete',stage='actual_rtl_cycles_outputs_and_original_postcheck_equal_pending_independent_audit',cycles=[c for _,c in rows]);save()
    except BaseException as e:state.update(status='failed',error=str(e));save();raise
if __name__=='__main__':main()
