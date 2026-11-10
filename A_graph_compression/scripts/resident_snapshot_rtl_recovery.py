#!/usr/bin/env python3
"""Recover a terminal failed elaboration in isolation; never alter frozen v1."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from check_vitis_kernel import digest,require
from resident_snapshot_rtl_contract import golden,transactions
ROOT=Path(__file__).resolve().parents[1]
def save(p,v):
    with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def main():
    old=ROOT/'data/derived/resident_snapshot_rtl_20261024_v1';oldstate=json.loads((old/'state.json').read_text())
    require(oldstate['status']=='failed' and oldstate['stage']=='elaborate','Not the observed failed baseline')
    require(not Path('/proc',str(oldstate['owner_pid'])).exists(),'Original owner still live')
    rp=json.loads((old/'elaborate.receipt.json').read_text());require(rp['exit_code']==137,'Different failure signature')
    require(rp['log_sha256']==digest(old/'elaborate.log'),'Changed failure log')
    p=json.loads((old/'plan.json').read_text());setup=json.loads((old/'setup.json').read_text())
    inputs={**p['files'],**p['synthesis'],**setup['files']}
    for path,h in inputs.items():require(digest(path)==h,'Changed original input '+path)
    for phase in ['compile_cpu','cpu','prepare']:
        receipt=json.loads((old/(phase+'.receipt.json')).read_text())
        require(receipt['exit_code']==0 and receipt['log_sha256']==digest(old/(phase+'.log')),'Failed baseline preflight '+phase)
    golden((old/'cpu.log').read_text())
    out=ROOT/'data/derived/resident_snapshot_rtl_recovery_20261025_v1';out.mkdir(exist_ok=False)
    project=ROOT/'build/resident_snapshot_rtl_recovery_20261025_v1';require(not project.exists(),'Existing recovery project')
    state=dict(owner_pid=os.getpid(),status='running',stage='copy_verified_setup')
    def update():
        q=out/'state.tmp';q.write_text(json.dumps(state,indent=2)+'\n');q.replace(out/'state.json')
    update()
    original=Path(p['project']);src=original/'solution/sim';dst=project/'solution/sim'
    def ignore(directory,names):
        return [n for n in names if n in ['xsim.dir','.Xil'] or n.endswith(('.log','.pb','.jou'))]
    shutil.copytree(src,dst,ignore=ignore)
    copied={}
    for path,h in setup['files'].items():
        source=Path(path)
        if source.is_relative_to(src):
            target=dst/source.relative_to(src);require(target.is_file() and digest(target)==h,'Different copied setup '+str(target));copied[str(target)]=h
    directory=dst/'verilog';pc=dst/'wrapc_pc'
    bounded=out/'bounded.tcl';shutil.copyfile(old/'bounded.tcl',bounded)
    help_source=Path('/tmp/a_snapshot_xelab_20261025_help.txt');help_copy=out/'local_xelab_help.txt';shutil.copyfile(help_source,help_copy)
    require('--O0' in help_copy.read_text() and '--mt' in help_copy.read_text(),'Unsupported local recovery options')
    execution=json.loads((old/'execution_plan.json').read_text())
    original_cmd=execution['commands']['elaborate']['command'];xelab=original_cmd.index('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin/xelab')
    command=original_cmd[:xelab]+['/usr/bin/time','-v']+original_cmd[xelab:]+['-mt','off','--O0','--stats']
    rtl=execution['commands']['rtl']['command'].copy();rtl[-1]=str(bounded)
    postcheck=execution['commands']['postcheck']['command'].copy();postcheck[-1]=str(pc/'cosim.pc.exe')
    commands={phase:dict(command=cmd,cwd=str(cwd)) for phase,cmd,cwd in [('elaborate',command,directory),('rtl',rtl,directory),('postcheck',postcheck,pc)]}
    dependencies=[old/'state.json',old/'plan.json',old/'setup.json',old/'execution_plan.json',old/'elaborate.receipt.json',old/'elaborate.log',old/'cpu.log',old/'prepare.log',bounded,help_copy,Path(__file__).resolve(),ROOT/'scripts/check_resident_snapshot_rtl_recovery.py',ROOT/'scripts/resident_snapshot_rtl_contract.py',ROOT/'scripts/check_vitis_kernel.py']
    inputs.update({str(f):digest(f) for f in dependencies})
    save(out/'plan.json',dict(files=inputs,copied=copied,commands=commands,project=str(project),old_bundle=str(old),original_elaborate_command=original_cmd,transactions=30,changes=['xelab -mt off','xelab --O0','resource measurement /usr/bin/time -v and --stats'],root_cause='unproven: SIGKILL signature; current cgroup oom_kill counter not attributable',references=['https://docs.amd.com/r/2022.2-English/ug900-vivado-logic-simulation/xelab']))
    save(out/'environment_before.json',dict(utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),cgroup={n:(Path('/sys/fs/cgroup')/n).read_text() for n in ['memory.events','memory.current','memory.max']}))
    env={**os.environ,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1'}
    try:
        for phase,job in commands.items():
            state.update(stage=phase);update();start=time.monotonic()
            with (out/(phase+'.log')).open('x') as f:
                child=subprocess.Popen(job['command'],cwd=job['cwd'],env=env,stdout=f,stderr=subprocess.STDOUT);state['child_pid']=child.pid;update()
                save(out/(phase+'.submission.json'),dict(pid=child.pid,command=job['command'],cwd=job['cwd'],plan_sha256=digest(out/'plan.json')));code=child.wait()
            save(out/(phase+'.receipt.json'),dict(exit_code=code,command=job['command'],log_sha256=digest(out/(phase+'.log')),elapsed_seconds=time.monotonic()-start))
            text=(out/(phase+'.log')).read_text(errors='replace')
            require(code==0 and not any(s in text for s in ['ERROR:','FATAL_ERROR','runtime error:']),phase+' failed; preserve new incident')
            if phase=='rtl':transactions((directory/'search_resident_snapshot_top.performance.result.transaction.xml').read_text())
            if phase=='postcheck':golden(text)
        state.update(stage='independent_audit');update()
        cmd=['python3',str(ROOT/'scripts/check_resident_snapshot_rtl_recovery.py'),'--bundle',str(out),'--output',str(ROOT/'results/resident_snapshot_rtl_recovery_audit_20261025_v1.json')]
        with (out/'audit.log').open('x') as f:code=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT).returncode
        require(code==0,'Recovery audit failed');state.update(status='complete',stage='independently_audited');update()
    except BaseException as e:state.update(status='failed',error=str(e));update();raise
if __name__=='__main__':main()
