#!/usr/bin/env python3
"""Compile a new boundary TB against already audited production top objects."""
import json
import os
from pathlib import Path
import shutil
import subprocess
from prepare_search_heap_router import ROOT, digest
from supervise_search_router_chain import save
OUT=ROOT/'data/derived/search_kernel_state_boundaries_20261024_v1'
PRIOR=ROOT/'results/search_kernel_cpu_component_20261024_v3.json'
SOURCE=ROOT/'hardware/vitis/search_kernel_offsets_v3'

def main():
    audit=json.loads(PRIOR.read_text())
    if audit['status']!='complete_search_top_cpu_real_probes_and_packet_abi_verified':raise ValueError('Missing production-top CPU proof')
    sources=list(SOURCE.iterdir())
    objects=[ROOT/'data/derived/search_kernel_cpu_20261024_v3'/('search_kernel_'+m+'.o') for m in ['csr','compact']]
    for p in sources+objects:
        if digest(p)!=audit['artifacts'][str(p)]:raise ValueError('Changed production artifact '+str(p))
    OUT.mkdir(exist_ok=False);copied=OUT/'source';copied.mkdir()
    tb=ROOT/'tests/test_search_kernel_state_boundaries.cpp'
    files={str(p):digest(p) for p in [PRIOR,tb,Path(__file__).resolve(),ROOT/'scripts/check_search_kernel_state_boundaries.py',*sources,*objects]}
    for p in sources+[tb]:shutil.copyfile(p,copied/p.name)
    generated={str(p):digest(p) for p in copied.iterdir()}
    jobs=[]
    for mode_id,mode in enumerate(['csr','compact']):
        binary=OUT/mode
        command=['g++','-std=c++14','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unknown-pragmas','-fsanitize=address,undefined',
            '-DSEARCH_GRAPH_MODE='+str(mode_id),'-DSEARCH_TOP_NAME=search_kernel_'+mode,'-I'+str(copied),str(copied/tb.name),str(objects[mode_id]),'-o',str(binary)]
        jobs.append({'mode':mode,'mode_id':mode_id,'compile':command,'run':['taskset','-c','119',str(binary)]})
    save(OUT/'plan.json',{'files':files,'copied':generated,'jobs':jobs,'cases':['exact_capacity','signal_overflow','bits_overflow','value_overflow','compatible_full_overlap','last_bit_conflict','last_value_conflict','recovery_after_failure'],
        'limitations':['Synthetic CPU boundary checks of the actual production search top; not RTL or physical hardware evidence.','No change to production kernel, capacities or ongoing experiments.','CPU output guards do not prove RTL behavior outside AXI declared depths.']})
    state={'owner_pid':os.getpid(),'status':'running','stage':'compile','completed':[]}
    def update():
        p=OUT/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(OUT/'state.json')
    update()
    try:
        for job in jobs:
            for phase in ['compile','run']:
                state.update(stage=phase,mode=job['mode']);update()
                log=OUT/(job['mode']+'.'+phase+'.log')
                with log.open('x') as stream:
                    child=subprocess.Popen(job[phase],stdout=stream,stderr=subprocess.STDOUT)
                    save(OUT/(job['mode']+'.'+phase+'.submission.json'),{'pid':child.pid,'command':job[phase],'plan_sha256':digest(OUT/'plan.json')})
                    state['child_pid']=child.pid;update();code=child.wait()
                save(OUT/(job['mode']+'.'+phase+'.receipt.json'),{'exit_code':code,'command':job[phase],'log_sha256':digest(log),'binary_sha256':digest(OUT/job['mode']) if (OUT/job['mode']).exists() else None})
                if code:raise RuntimeError('Boundary '+phase+' failed '+job['mode'])
            print((OUT/(job['mode']+'.run.log')).read_text(),flush=True)
            state['completed'].append(job['mode']);update()
        state.update(status='complete',stage='pending_independent_audit');update()
    except BaseException as error:
        state.update(status='failed',error=str(error));update();raise

if __name__=='__main__':main()
