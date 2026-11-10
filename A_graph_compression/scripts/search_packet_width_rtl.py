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
ROOT=Path(__file__).resolve().parents[1]
def golden(text):
    rows=re.findall(r'^SEARCH_KERNEL_TOP_TRANSACTION_PASS mode=0 transaction=(\d+) status=(\d+) cost=(\d+) path=(\d+)$',text,re.M)
    require(rows==[('0','0','35','2'),('1','3','0','0')] and text.splitlines().count('SEARCH_KERNEL_TOP_ALL_PASS transactions=2 full_workspace_limits=1')==1,'Different original CSR oracle')
def main():
    proof_path=ROOT/'results/search_packet_width64_comparison_20261024_v1.json';proof=json.loads(proof_path.read_text())
    require(proof['status']=='packet_width_single_variable_csim_synthesis_compared_physical_unverified' and proof['input_width_is_64'],'Missing structural-change gate')
    for p,h in proof['files'].items():require(digest(p)==h,'Changed compared input '+p)
    original=ROOT/'build/search_packet_width64_20261024_v1';project=ROOT/'build/search_packet_width64_rtl_20261025_v1'
    out=ROOT/'data/derived/search_packet_width64_rtl_20261025_v1';out.mkdir(exist_ok=False);require(not project.exists(),'Existing RTL project')
    shutil.copytree(original,project,ignore=lambda path,names:[n for n in names if Path(path)==original/'solution' and n in ['sim','csim']])
    files={str(proof_path):digest(proof_path),str(Path(__file__).resolve()):digest(__file__)}
    for p in (original/'solution/syn').rglob('*'):
        if p.is_file():
            copied=project/p.relative_to(original);require(digest(p)==digest(copied),'Changed synthesis copy');files[str(p)]=digest(p);files[str(copied)]=digest(copied)
    source=ROOT/'data/derived/search_packet_width64_20261024_v1/source'
    for p in source.iterdir():files[str(p)]=digest(p)
    setup=out/'setup.tcl';setup.write_text('cd {'+str(project.parent)+'}\nopen_project {'+project.name+'}\nopen_solution solution\ncsim_design -clean\ncosim_design -rtl verilog -trace_level none -setup\nputs WIDTH64_RTL_SETUP_COMPLETE\nexit\n')
    bounded=out/'bounded.tcl';bounded.write_text('run 10 sec\nputs WIDTH64_RTL_BOUNDED_RETURNED\nquit\n')
    for p in [setup,bounded]:files[str(p)]=digest(p)
    plan=dict(files=files,project=str(project),transactions=2,stack_bytes=67108864,simulation_bound_ns=10000000000)
    (out/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    state=dict(owner_pid=os.getpid(),status='running',stage='setup')
    def save():
        p=out/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(out/'state.json')
    prefix=['prlimit','--stack=67108864:67108864','--','taskset','-c','122']
    def run(name,cmd,cwd):
        state['stage']=name;save();env={**os.environ,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1'}
        with (out/(name+'.log')).open('x') as log:
            child=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;save();code=child.wait()
        (out/(name+'.receipt.json')).write_text(json.dumps(dict(command=cmd,cwd=str(cwd),exit_code=code,log_sha256=digest(out/(name+'.log')),plan_sha256=digest(out/'plan.json')),indent=2)+'\n')
        text=(out/(name+'.log')).read_text(errors='replace');require(code==0 and not any(t in text for t in ['ERROR:','FATAL_ERROR','runtime error:']),name+' failed')
        print(name,'PASS',flush=True);return text
    save()
    try:
        text=run('setup',prefix+['/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls','-f',str(setup)],out)
        before,after=text.split('Running: cosim_design',1);golden(before);golden(after);require('WIDTH64_RTL_SETUP_COMPLETE' in text,'Incomplete setup')
        solution=project/'solution';directory=solution/'sim/verilog';pc=solution/'sim/wrapc_pc'
        require(re.search(r'parameter AUTOTB_TRANSACTION_NUM = 2;', (directory/'search_kernel_top.autotb.v').read_text()),'Wrong transaction count')
        for p in (solution/'syn/verilog').glob('*.v'):require(digest(p)==digest(directory/p.name),'Different simulation RTL')
        commands=[shlex.split(l) for l in (directory/'run_xsim.sh').read_text().splitlines() if l.strip() and not l.startswith('#')]
        require(len(commands)==2 and Path(commands[0][0]).name=='xelab' and Path(commands[1][0]).name=='xsim','Wrong simulator commands')
        require(commands[1][-2:]==['-tclbatch','search_kernel_top.tcl'],'Wrong simulator Tcl')
        for parent in [directory,solution/'sim/tv/cdatafile',pc]:
            for p in parent.iterdir():
                if p.is_file():files[str(p)]=digest(p)
        (out/'execution_plan.json').write_text(json.dumps(dict(files=files,commands=commands),indent=2)+'\n')
        run('elaborate',prefix+commands[0],directory)
        rtl=run('rtl',prefix+commands[1][:-1]+[str(bounded)],directory)
        require('WIDTH64_RTL_BOUNDED_RETURNED' in rtl and re.search(r'RTL Simulation :\s*2 / 2',rtl),'Incomplete RTL')
        perf=directory/'search_kernel_top.performance.result.transaction.xml'
        cycles=[tuple(map(int,r)) for r in re.findall(r'^transaction\s+(\d+):\s+(\d+)\s+(?:\d+|x)\s*$',perf.read_text(),re.M)]
        require([i for i,_ in cycles]==[0,1] and all(c>0 for _,c in cycles),'Missing RTL transaction timing')
        golden(run('postcheck',prefix+[str(pc/'cosim.pc.exe')],pc))
        for p,h in files.items():require(digest(p)==h,'Changed RTL execution input '+p)
        state.update(status='complete',stage='rtl_and_original_postcheck_complete_pending_independent_audit',cycles=cycles);save()
    except BaseException as e:state.update(status='failed',error=str(e));save();raise
if __name__=='__main__':main()
