#!/usr/bin/env python3
"""Isolate a full-depth TB, reuse frozen synthesis and execute bounded RTL exactly once."""
import argparse
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import xml.etree.ElementTree as ET
from check_vitis_kernel import digest, require
from node_occupancy_rtl_contract import golden, transactions

ROOT=Path(__file__).resolve().parents[1]
HLS=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls')


def save(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--project',type=Path,required=True);parser.add_argument('--audit-output',type=Path,required=True)
    parser.add_argument('--cpu',type=int,default=118);a=parser.parse_args()
    out=a.output.resolve();project=a.project.resolve();audit_output=a.audit_output.resolve()
    require(not project.exists() and not audit_output.exists(),'Existing RTL project/output; do not restart')
    review_path=ROOT/'results/node_occupancy_synthesis_review_20261024_v1.json';review=json.loads(review_path.read_text())
    require(review['status']=='bounded_node_occupancy_csim_and_synthesis_verified_rtl_pending','Missing production synthesis audit')
    for p,h in {**review['files'],**review['source_bindings']}.items():require(digest(p)==h,'Changed audited synthesis input '+p)
    original=ROOT/'build/node_occupancy_hls_20261024_v1'
    out.mkdir(parents=True,exist_ok=False);source=out/'source';source.mkdir()
    tb_source=ROOT/'hardware/vitis/test_node_occupancy_rtl.cpp';tb=source/tb_source.name;shutil.copyfile(tb_source,tb)
    original_source=ROOT/'data/derived/node_occupancy_hls_20261024_v1/source'
    for name in ['search_node_occupancy.hpp','search_node_occupancy_top.cpp']:shutil.copyfile(original_source/name,source/name)
    shutil.copytree(original,project,ignore=lambda path,names:[n for n in names if Path(path)==original/'solution' and n in ['sim','csim']])
    app=project/'hls.app';text=app.read_text();xml=ET.fromstring(text)
    tbs=[node for node in xml.findall('files/file') if node.attrib.get('tb')=='1']
    original_tb=str(original_source/'test_search_node_occupancy.cpp')
    require(len(tbs)==1 and tbs[0].attrib['name']==original_tb and text.count(original_tb)==1,'Unexpected original testbench')
    app.write_text(text.replace(original_tb,str(tb)))
    initial_app=out/'initial.hls.app';shutil.copyfile(app,initial_app)
    synthesis={}
    for p in (original/'solution/syn').rglob('*'):
        if p.is_file():
            copied=project/p.relative_to(original);require(digest(copied)==digest(p),'Changed synthesis copy')
            synthesis[str(p)]=digest(p);synthesis[str(copied)]=digest(copied)
    script=out/'prepare.tcl'
    script.write_text('open_project {'+str(project)+'}\nopen_solution solution\ncsim_design -clean\nputs NODE_OCCUPANCY_RTL_CSIM_COMPLETE\ncosim_design -rtl verilog -trace_level none -setup\nputs NODE_OCCUPANCY_COSIM_SETUP_COMPLETE\nexit\n')
    bounded=out/'bounded.tcl';bounded.write_text('run 2 sec\nputs NODE_OCCUPANCY_BOUNDED_RUN_RETURNED\nquit\n')
    dependencies=[review_path,tb_source,script,bounded,initial_app,Path(__file__).resolve(),
                  ROOT/'scripts/check_node_occupancy_rtl_v2.py',ROOT/'scripts/node_occupancy_rtl_contract.py',ROOT/'scripts/check_vitis_kernel.py']
    dependencies+=list(source.iterdir())
    files={str(p):digest(p) for p in dependencies}
    prefix=['prlimit','--stack=67108864:67108864','--','taskset','-c',str(a.cpu)]
    binary=out/'cpu_check'
    commands={
        'compile_cpu':dict(command=['taskset','-c',str(a.cpu),'g++','-std=c++14','-O1','-g','-Wall','-Wextra','-Werror',
            '-Wno-unknown-pragmas','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(tb),
            str(source/'search_node_occupancy_top.cpp'),'-o',str(binary)],cwd=str(out)),
        'cpu':dict(command=prefix+[str(binary)],cwd=str(out)),
        'prepare':dict(command=prefix+[str(HLS),'-f',str(script)],cwd=str(out))}
    plan=dict(files=files,synthesis=synthesis,project=str(project),original_project=str(original),commands=commands,
              cpu=a.cpu,stack_bytes=67108864,simulation_bound_ns=2000000000,transactions=28,
              scope='Unchanged full-capacity occupancy RTL; complete pointer depths and per-transaction persistent-state checks.')
    save(out/'plan.json',plan)
    state=dict(owner_pid=os.getpid(),status='running',stage='compile_cpu')
    def update():
        temp=out/'state.tmp';temp.write_text(json.dumps(state,indent=2)+'\n');temp.replace(out/'state.json')
    update()
    env={**os.environ,'ASAN_OPTIONS':'detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1'}
    env.pop('LD_PRELOAD',None)
    def run(phase,job):
        state['stage']=phase;update();log=out/(phase+'.log')
        with log.open('x') as stream:
            phase_env=dict(env)
            if phase not in ['compile_cpu','cpu']:phase_env['LD_PRELOAD']='/lib/x86_64-linux-gnu/libudev.so.1'
            child=subprocess.Popen(job['command'],cwd=job['cwd'],env=phase_env,stdout=stream,stderr=subprocess.STDOUT)
            state['child_pid']=child.pid;update()
            save(out/(phase+'.submission.json'),dict(pid=child.pid,command=job['command'],cwd=job['cwd'],plan_sha256=digest(out/'plan.json')))
            code=child.wait()
        save(out/(phase+'.receipt.json'),dict(exit_code=code,command=job['command'],log_sha256=digest(log)))
        text=log.read_text(errors='replace');require(code==0 and not any(s in text for s in ['ERROR:','FATAL_ERROR','runtime error:']),phase+' failed')
        if phase in ['cpu','postcheck']:golden(text)
        print(phase,'PASS',flush=True)
    try:
        for phase in ['compile_cpu','cpu','prepare']:run(phase,commands[phase])
        log=(out/'prepare.log').read_text();require('NODE_OCCUPANCY_COSIM_SETUP_COMPLETE' in log,'Missing cosim setup')
        for p,h in synthesis.items():require(digest(p)==h,'Production synthesis changed during TB setup')
        solution=project/'solution';directory=solution/'sim/verilog';pc=solution/'sim/wrapc_pc'
        golden((solution/'csim/report/search_node_occupancy_top_csim.log').read_text())
        before,after=log.split('Running: cosim_design',1);golden(before);golden(after)
        require(re.search(r'parameter AUTOTB_TRANSACTION_NUM = 28;', (directory/'search_node_occupancy_top.autotb.v').read_text()),'Wrong generated transaction count')
        for p in (solution/'syn/verilog').glob('*.v'):require(digest(directory/p.name)==digest(p),'Simulation RTL differs')
        setup_files={}
        for parent in [directory,solution/'sim/tv/cdatafile']:
            for p in parent.iterdir():
                if p.is_file() and p.suffix in ['.v','.sv','.dat','.tcl','.sh','.prj']:setup_files[str(p)]=digest(p)
        for p in [pc/'cosim.pc.exe',pc/'apatb_search_node_occupancy_top.cpp',solution/'csim/report/search_node_occupancy_top_csim.log',app,solution/'solution.aps']:
            setup_files[str(p)]=digest(p)
        save(out/'setup.json',dict(status='full_depth_28_transaction_setup_verified_rtl_pending',files=setup_files,production_synthesis='unchanged'))
        raw_commands=[shlex.split(s) for s in (directory/'run_xsim.sh').read_text().splitlines() if s.strip() and not s.strip().startswith('#')]
        require(len(raw_commands)==2 and Path(raw_commands[0][0]).name=='xelab' and Path(raw_commands[1][0]).name=='xsim'
                and raw_commands[1][-2:]==['-tclbatch','search_node_occupancy_top.tcl'],'Unexpected simulator driver')
        commands.update(elaborate=dict(command=prefix+raw_commands[0],cwd=str(directory)),
            rtl=dict(command=prefix+raw_commands[1][:-1]+[str(bounded)],cwd=str(directory)),
            postcheck=dict(command=prefix+[str(pc/'cosim.pc.exe')],cwd=str(pc)))
        save(out/'execution_plan.json',dict(commands=commands,files=files,plan_sha256=digest(out/'plan.json'),setup_sha256=digest(out/'setup.json')))
        for phase in ['elaborate','rtl','postcheck']:
            run(phase,commands[phase])
            if phase=='rtl':transactions((directory/'search_node_occupancy_top.performance.result.transaction.xml').read_text())
        state['stage']='independent_audit';update()
        save(out/'audit_owner_state.json',state)
        command=['taskset','-c',str(a.cpu),'python3',str(ROOT/'scripts/check_node_occupancy_rtl_v2.py'),'--bundle',str(out),'--output',str(audit_output)]
        with (out/'audit.log').open('x') as stream:code=subprocess.run(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT).returncode
        save(out/'audit.receipt.json',dict(exit_code=code,command=command,log_sha256=digest(out/'audit.log')))
        require(code==0,'Independent RTL audit failed')
        state.update(status='complete',stage='independently_audited');update()
    except BaseException as error:
        state.update(status='failed',error=str(error));update();raise


if __name__=='__main__':main()
