#!/usr/bin/env python3
"""Execute the narrowed, audited CSR RTL once with original two-call oracle."""
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
from check_vitis_kernel import digest,require
from run_compact_native_stack_recovery_v1 import atomic
from compressed_batch_compact_bus64_hls_v3 import atomic_text,child_limits
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
def golden(text):
    rows=re.findall(r'^SEARCH_KERNEL_TOP_TRANSACTION_PASS mode=0 transaction=(\d+) status=(\d+) cost=(\d+) path=(\d+)$',text,re.M)
    require(rows==[('0','0','35','2'),('1','3','0','0')] and text.splitlines().count('SEARCH_KERNEL_TOP_ALL_PASS transactions=2 full_workspace_limits=1')==1,'Different original CSR oracle')
def main():
    require(int(Path('/sys/fs/cgroup/memory.max').read_text())-int(Path('/sys/fs/cgroup/memory.current').read_text())>=128*1024**3,'Insufficient setup headroom')
    proof_path=ROOT/'results/search_read_control_staging_hls_audit_20261025_v1.json';proof=json.loads(proof_path.read_text())
    require(proof['status']=='full_kernel_csim_synthesis_verified_scalar_validity_staging_achieved_rtl_pending' and proof['helper_min2_ii1_achieved'],'Missing structural-change gate')
    for p,h in proof['files'].items():require(digest(p)==h,'Changed compared input '+p)
    original=BASE/'search_read_control_staging_hls_project_v1';project=BASE/'search_read_control_staging_cosim_project_v1'
    out=BASE/'search_read_control_staging_cosim_setup_v1';out.mkdir(exist_ok=False);require(not project.exists(),'Existing RTL project')
    shutil.copytree(original,project,ignore=lambda path,names:[n for n in names if Path(path)==original/'solution' and n in ['sim','csim']])
    files={str(proof_path):digest(proof_path),str(Path(__file__).resolve()):digest(__file__)}
    for p in (original/'solution/syn').rglob('*'):
        if p.is_file():
            copied=project/p.relative_to(original);require(digest(p)==digest(copied),'Changed synthesis copy');files[str(p)]=digest(p);files[str(copied)]=digest(copied)
    source=BASE/'search_read_control_staging_hls_v1/source'
    for p in source.iterdir():files[str(p)]=digest(p)
    setup=out/'setup.tcl';atomic_text(setup,'cd {'+str(project.parent)+'}\nopen_project {'+project.name+'}\nopen_solution solution\ncsim_design -clean\ncosim_design -rtl verilog -trace_level none -setup\nputs READ_CONTROL_RTL_SETUP_COMPLETE\nexit\n')
    bounded=out/'bounded.tcl';atomic_text(bounded,'run 10 sec\nputs READ_CONTROL_RTL_BOUNDED_RETURNED\nquit\n')
    for p in [setup,bounded]:files[str(p)]=digest(p)
    plan=dict(files=files,project=str(project),transactions=2,stack_bytes=67108864,simulation_bound_ns=10000000000)
    atomic(out/'plan.json',plan)
    state=dict(owner_pid=os.getpid(),status='running',stage='setup')
    def save():
        atomic(out/'state.json',state)
    prefix=['prlimit','--stack=67108864:67108864','--','taskset','-c','122']
    def run(name,cmd,cwd):
        state['stage']=name;save();env={**os.environ,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1'}
        with (out/(name+'.log')).open('x') as log:
            child=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,preexec_fn=child_limits);state['child_pid']=child.pid;save();code=child.wait()
        atomic(out/(name+'.receipt.json'),dict(command=cmd,cwd=str(cwd),exit_code=code,log_sha256=digest(out/(name+'.log')),plan_sha256=digest(out/'plan.json')))
        text=(out/(name+'.log')).read_text(errors='replace');require(code==0 and not any(t in text for t in ['ERROR:','FATAL_ERROR','runtime error:']),name+' failed')
        print(name,'PASS',flush=True);return text
    save()
    try:
        text=run('setup',prefix+['/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls','-f',str(setup)],out)
        before,after=text.split('Running: cosim_design',1);golden(before);golden(after);require('READ_CONTROL_RTL_SETUP_COMPLETE' in text,'Incomplete setup')
        solution=project/'solution';directory=solution/'sim/verilog';pc=solution/'sim/wrapc_pc'
        require(re.search(r'parameter AUTOTB_TRANSACTION_NUM = 2;', (directory/'search_kernel_top.autotb.v').read_text()),'Wrong transaction count')
        for p in (solution/'syn/verilog').glob('*.v'):require(digest(p)==digest(directory/p.name),'Different simulation RTL')
        commands=[shlex.split(l) for l in (directory/'run_xsim.sh').read_text().splitlines() if l.strip() and not l.startswith('#')]
        require(len(commands)==2 and Path(commands[0][0]).name=='xelab' and Path(commands[1][0]).name=='xsim','Wrong simulator commands')
        require(commands[1][-2:]==['-tclbatch','search_kernel_top.tcl'],'Wrong simulator Tcl')
        for parent in [directory,solution/'sim/tv/cdatafile',pc]:
            for p in parent.iterdir():
                if p.is_file():files[str(p)]=digest(p)
        atomic(out/'execution_plan.json',dict(files=files,commands=commands,transactions=2,depths_unchanged=True,rtl_executed=False,planned_rtl_stack_bytes=268435456))
        for p,h in files.items():require(digest(p)==h,'Changed closed setup input '+p)
        state.update(status='complete',stage='full_depth_cosim_setup_verified_rtl_not_executed');save()
    except BaseException as e:state.update(status='failed',error=str(e));save();raise
if __name__=='__main__':main()
