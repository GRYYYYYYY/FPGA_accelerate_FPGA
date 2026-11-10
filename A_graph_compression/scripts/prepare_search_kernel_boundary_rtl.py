#!/usr/bin/env python3
"""Reuse frozen production synthesis; replace only TB in isolated HLS projects."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from prepare_search_heap_router import ROOT,digest
from supervise_search_router_chain import save
OUT=ROOT/'data/derived/search_kernel_boundary_rtl_20261024_v1'
PROJECT=ROOT/'build/search_kernel_boundary_rtl_20261024_v1'
OLD=ROOT/'build/search_kernel_hls_20261024_v3'
HLS=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls')


def main():
    proof_path=ROOT/'results/search_kernel_state_boundaries_20261024_v1.json'
    proof=json.loads(proof_path.read_text())
    if proof['status']!='production_search_top_state_capacity_boundaries_cpu_verified':raise ValueError('Missing full-capacity CPU proof')
    for p,h in proof['artifacts'].items():
        if digest(p)!=h:raise ValueError('Changed boundary CPU proof '+p)
    prior=ROOT/'data/derived/search_kernel_hls_20261024_v3/plan.json';plan=json.loads(prior.read_text())
    for p,h in {**plan['files'],**plan['copied']}.items():
        if digest(p)!=h:raise ValueError('Changed production synthesis input '+p)
    OUT.mkdir(exist_ok=False);PROJECT.mkdir(exist_ok=False)
    tb=ROOT/'data/derived/search_kernel_state_boundaries_20261024_v1/source/test_search_kernel_state_boundaries.cpp'
    original_tb=ROOT/'data/derived/search_kernel_hls_20261024_v3/source/test_search_kernel_top.cpp'
    files={str(p):digest(p) for p in [proof_path,prior,Path(__file__).resolve(),tb,*map(Path,plan['copied'])]}
    jobs=[];synthesis={};metadata={}
    for mode in ['csr','compact']:
        old=OLD/mode;new=PROJECT/mode
        shutil.copytree(old,new,ignore=lambda path,names:[n for n in names if Path(path)==old/'solution' and n in ['sim','csim']])
        app=new/'hls.app';text=app.read_text();xml=ET.fromstring(text)
        items=[e for e in xml.findall('files/file') if e.attrib.get('tb')=='1']
        if len(items)!=1 or items[0].attrib['name']!=str(original_tb):raise ValueError('Unexpected old HLS TB configuration')
        if text.count(str(original_tb))!=1:raise ValueError('Ambiguous old testbench')
        app.write_text(text.replace(str(original_tb),str(tb)))
        before=OUT/(mode+'.initial.hls.app');shutil.copyfile(app,before);metadata[str(before)]=digest(before)
        for p in (old/'solution/syn').rglob('*'):
            if p.is_file():
                h=digest(p);q=new/p.relative_to(old)
                if digest(q)!=h:raise ValueError('Synthesis copy differs')
                files[str(p)]=h;synthesis[str(q)]=h
        script=OUT/(mode+'.prepare.tcl')
        script.write_text('cd {'+str(PROJECT)+'}\nopen_project '+mode+'\nopen_solution solution\ncsim_design -clean\nputs BOUNDARY_CSIM_COMPLETE\ncosim_design -rtl verilog -setup\nputs BOUNDARY_COSIM_SETUP_COMPLETE\nexit\n')
        files[str(script)]=digest(script)
        jobs.append({'mode':mode,'command':['prlimit','--stack=67108864:67108864','--','taskset','-c','119',str(HLS),'-f',str(script)]})
    options=OUT/'tool_commands_help.log';shutil.copyfile('/tmp/a_search_boundary_hls_help_20261024_v2/help.log',options);files[str(options)]=digest(options)
    save(OUT/'prepare_plan.json',{'files':files,'synthesis':synthesis,'initial_metadata':metadata,'jobs':jobs,'project':str(PROJECT),'scope':'Unchanged production synthesis; two representations, eight full-capacity state-boundary transactions each. Prepare Csim and cosim files only; RTL execution waits for the original replay audit.',
        'limitations':['No current boundary RTL pass. Full original capacities retained.','Only verification TB path changed in copied hls.app because local 2022.2 has no remove_files command.','Simulation argv empty in both flows, matching no-argument main.']})
    state={'owner_pid':os.getpid(),'status':'running','stage':'csim_and_cosim_setup','completed':[]}
    def update():
        p=OUT/'prepare_state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(OUT/'prepare_state.json')
    update()
    try:
        env=os.environ.copy();env['LD_PRELOAD']='/lib/x86_64-linux-gnu/libudev.so.1'
        for job in jobs:
            mode=job['mode'];log=OUT/(mode+'.prepare.log')
            with log.open('x') as stream:
                child=subprocess.Popen(job['command'],cwd=OUT,env=env,stdout=stream,stderr=subprocess.STDOUT)
                save(OUT/(mode+'.prepare.submission.json'),{'pid':child.pid,'command':job['command'],'plan_sha256':digest(OUT/'prepare_plan.json')})
                state.update(mode=mode,child_pid=child.pid);update();code=child.wait()
            save(OUT/(mode+'.prepare.receipt.json'),{'exit_code':code,'command':job['command'],'log_sha256':digest(log)})
            if code or 'ERROR:' in log.read_text() or 'BOUNDARY_COSIM_SETUP_COMPLETE' not in log.read_text():raise RuntimeError('Boundary preparation failed '+mode)
            csim=PROJECT/mode/'solution/csim/report/search_kernel_top_csim.log';text=csim.read_text();mid=0 if mode=='csr' else 1
            rows=[tuple(map(int,r)) for r in re.findall(r'^STATE_BOUNDARY_PASS mode=(\d+) transaction=(\d+) status=(\d+) full_capacity=32,16,8 literal_output=1 guards=1$',text,re.M)]
            if rows!=[(mid,i,s) for i,s in enumerate([0,5,5,5,0,1,1,0])]:raise RuntimeError('Boundary Csim incomplete')
            state['completed'].append(mode);update()
        for p,h in synthesis.items():
            if digest(p)!=h:raise ValueError('Production synthesis changed during preparation '+p)
        state.update(status='complete',stage='boundary_csim_and_cosim_setup_complete');update()
        print(state['stage'],flush=True)
    except BaseException as error:
        state.update(status='failed',error=str(error));update();raise

if __name__=='__main__':main()
