#!/usr/bin/env python3
"""One isolated full44/4tx runtime trial of the existing snapshot at stack256MiB."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from check_vitis_kernel import digest, require

ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')

def atomic(path, value):
    fd,tmp=tempfile.mkstemp(dir=path.parent)
    with os.fdopen(fd,'w') as f:
        json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)

def main():
    original=BASE/'compressed_batch_compact_rtl_guarded_v1'
    require(json.loads((original/'elaborate.receipt.json').read_text())['exit_code']==0,'No compiled snapshot')
    incident=ROOT/'results/compact_native_xsim_crash_incident_20261025_v1.json'
    diagnosis=ROOT/'results/compact_xsim_core_location_20261025_v1.json'
    require(json.loads(incident.read_text())['postcheck_exit_code']==1,'Different original failure')
    require(json.loads(diagnosis.read_text())['prologue_stack_reservation_bytes']==32919624,'Different stack evidence')
    maximum=int(Path('/sys/fs/cgroup/memory.max').read_text())
    require(maximum-int(Path('/sys/fs/cgroup/memory.current').read_text())>=128*1024**3,'Insufficient runtime headroom')
    out=BASE/'compact_native_stack_recovery_v1';out.mkdir(exist_ok=False)
    state=dict(owner_pid=os.getpid(),status='running',stage='copy_original_snapshot')
    atomic(out/'state.json',state)
    try:
        def ignore(directory,names):
            return [n for n in names if n.startswith(('core.','rtl.')) or n.endswith(('.log','.jou','.wdb')) or '.performance.' in n]
        shutil.copytree(original/'sim',out/'sim',ignore=ignore)
        copied={}
        for p in (out/'sim').rglob('*'):
            if p.is_file():
                source=original/'sim'/p.relative_to(out/'sim')
                checksum=digest(p);require(checksum==digest(source),'Snapshot copy differs')
                copied[str(p)]=dict(source=str(source),sha256=checksum)
        tcl=out/'bounded.tcl';tcl.write_text('run 10 sec\nputs COMPACT_STACK_RECOVERY_BOUNDED_RETURNED\nquit\n')
        prefix=['prlimit','--stack=268435456:268435456','--core=0:0','--as=103079215104:103079215104','--']
        directory=out/'sim/verilog';pc=out/'sim/wrapc_pc'
        jobs=[('rtl',prefix+[str(Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin/xsim')),'--noieeewarnings','search_batch_trace_top_v2','-tclbatch',str(tcl)],directory),
              ('postcheck',prefix+[str(pc/'cosim.pc.exe')],pc)]
        plan=dict(files={str(incident):digest(incident),str(diagnosis):digest(diagnosis),str(Path(__file__).resolve()):digest(__file__),str(original/'plan.json'):digest(original/'plan.json')},copied=copied,commands=[dict(phase=n,command=c,cwd=str(d)) for n,c,d in jobs],stack_bytes=268435456,address_space_bytes=103079215104,core_bytes=0,transactions=4,pointers=44,dut_unchanged=True,compiled_snapshot_unchanged=True)
        atomic(out/'plan.json',plan)
        env={**os.environ,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1','A_BATCH_RTL_SNAPSHOT_PREFIX':str(out/'rtl')}
        for phase,cmd,cwd in jobs:
            state.update(stage=phase);atomic(out/'state.json',state);start=time.monotonic();aborted=False
            log=out/(phase+'.log')
            with log.open('x') as f:
                child=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
                state['child_pid']=child.pid;atomic(out/'state.json',state)
                while child.poll() is None:
                    if maximum-int(Path('/sys/fs/cgroup/memory.current').read_text())<16*1024**3:
                        import signal
                        os.killpg(child.pid,signal.SIGTERM);aborted=True
                    time.sleep(1)
                code=child.wait()
            text=log.read_text(errors='replace');atomic(out/(phase+'.receipt.json'),dict(command=cmd,cwd=str(cwd),exit_code=code,elapsed_seconds=time.monotonic()-start,resource_abort=aborted,log_sha256=digest(log)))
            require(code==0 and not aborted and not any(x in text for x in ['ERROR:','FATAL_ERROR','A_RO_','Simulator command interrupted','engine not responding','unexpected manner']),phase+' failed')
            if phase=='rtl':
                import re
                require(re.search(r'RTL Simulation :\s*4 / 4',text) is not None,'Full4tx incomplete')
            else:require('FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode=1 ports=44 transactions=4' in text and 'SEARCH_BATCH_PASS mode=1' in text,'Original C oracle absent')
        for i in range(4):
            actual=out/f'rtl_1_{i}.bin';reference=BASE/f'compressed_batch_compact_cosim_setup/hls_1_{i}.bin'
            require(actual.stat().st_size==reference.stat().st_size==946498280 and digest(actual)==digest(reference),'Full44 snapshot differs')
        state.update(status='complete',stage='independent_audit_pending');atomic(out/'state.json',state)
    except BaseException as exc:
        state.update(status='failed',error=str(exc));atomic(out/'state.json',state);raise

if __name__=='__main__':main()
