#!/usr/bin/env python3
"""Frozen full-capacity single-search HLS flow, two representations."""
from concurrent.futures import ThreadPoolExecutor,as_completed
import json
import os
from pathlib import Path
import shutil
import subprocess
from prepare_search_heap_router import ROOT,digest
OUT=ROOT/'data/derived/search_kernel_hls_20261024_v2'
PROJECT=ROOT/'build/search_kernel_hls_20261024_v2'
HLS=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls')
NAMES=['search_kernel.hpp','search_kernel_top.cpp','test_search_kernel_top.cpp','run_search_kernel.tcl','search_graph_adjacency.hpp','search_controller_flat.hpp','search_controller.hpp','search_key_words.hpp','search_snapshot_provider.hpp','search_cost_snapshot.hpp','search_heap_external.hpp','search_heap.hpp','search_label_index.hpp','search_label_records.hpp','search_site_state.hpp']

def save(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n')

def main():
    from derive_search_kernel_inline import verify,OUT as INLINE_SOURCE
    verify()
    prior=ROOT/'results/search_kernel_cpu_component_20261024_v1.json';audit=json.loads(prior.read_text())
    if audit['status']!='complete_search_top_cpu_real_probes_and_packet_abi_verified':raise ValueError('Missing CPU evidence')
    for p,h in audit['artifacts'].items():
        if digest(p)!=h:raise ValueError('Changed CPU evidence '+p)
    if PROJECT.exists():raise ValueError('Existing HLS project; inspect original owner')
    OUT.mkdir(exist_ok=False);source=OUT/'source';source.mkdir();PROJECT.mkdir();files={str(prior):digest(prior)}
    for name in NAMES:
        original=ROOT/'hardware/vitis'/name;files[str(original)]=digest(original)
        p=INLINE_SOURCE/name;shutil.copyfile(p,source/name);files[str(p)]=digest(p)
    p=INLINE_SOURCE/'search_kernel_packet.hpp';shutil.copyfile(p,source/p.name);files[str(p)]=digest(p)
    p=ROOT/'scripts/derive_search_kernel_inline.py';files[str(p)]=digest(p)
    for mode in ['csr','compact']:
        path=OUT/('preflight_'+mode);shutil.copyfile('/tmp/a_search_kernel_top_'+mode+'_20261024',path);path.chmod(0o755);files[str(path)]=digest(path)
    shutil.copyfile('/tmp/a_search_hls_options_20261024.log',OUT/'tool_options.log')
    files[str(OUT/'tool_options.log')]=digest(OUT/'tool_options.log');files[str(Path(__file__).resolve())]=digest(__file__)
    copied={str(p):digest(p) for p in source.iterdir()}
    plan={'files':files,'copied':copied,'project':str(PROJECT),'jobs':[{'mode':'csr','mode_id':0,'cpu':120},{'mode':'compact','mode_id':1,'cpu':123}],
        'part':'xcu280-fsvh2892-2L-e','clock_ns':5,'pipeline_loops':0,'derivation':'Only 19 function-scope INLINE directives on pointer-bearing call boundaries; stripping these yields frozen CPU-verified source.',
        'scope':'Full-capacity complete single-search top; actual AXI word interfaces, static adjacency and snapshot provider. Two synthetic functional transactions per mode.',
        'limitations':['No complete negotiation or occupancy updates in this kernel.','No real board memory controller, timing closure or power evidence.','RTL small-workload functional checks do not cover full graph traffic or observed maximum heap occupancy.'],
        'option_sources':['https://docs.amd.com/r/2022.2-English/ug1399-vitis-hls/config_compile','https://docs.amd.com/r/en-US/ug1399-vitis-hls/Compile']}
    save(OUT/'plan.json',plan)
    state={'owner_pid':os.getpid(),'status':'running','stage':'preflight','completed':[]}
    def update():
        p=OUT/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(OUT/'state.json')
    update()
    def run(job):
        mode=job['mode'];bundle=OUT/mode;bundle.mkdir();env=os.environ.copy()
        env.update(A_SEARCH_KERNEL_SOURCE=str(source),A_SEARCH_KERNEL_PROJECT=str(PROJECT/mode),A_SEARCH_KERNEL_MODE=str(job['mode_id']),LD_PRELOAD='/lib/x86_64-linux-gnu/libudev.so.1')
        command=['taskset','-c',str(job['cpu']),str(HLS),'-f',str(source/'run_search_kernel.tcl')]
        log=bundle/'flow.log'
        with log.open('x') as stream:
            child=subprocess.Popen(command,cwd=bundle,env=env,stdout=stream,stderr=subprocess.STDOUT)
            save(bundle/'submission.json',{'command':command,'pid':child.pid,'plan_sha256':digest(OUT/'plan.json')});code=child.wait()
        save(bundle/'receipt.json',{'exit_code':code,'command':command,'log_sha256':digest(log)})
        content=log.read_text()
        if code or 'SEARCH_KERNEL_FLOW_COMPLETE' not in content or 'ERROR:' in content:raise RuntimeError('Search kernel HLS failed '+mode)
        return mode
    try:
        for mode in ['csr','compact']:
            command=['taskset','-c','120',str(OUT/('preflight_'+mode))];log=OUT/('preflight_'+mode+'.log')
            with log.open('x') as stream:r=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT)
            save(OUT/('preflight_'+mode+'.receipt.json'),{'exit_code':r.returncode,'command':command,'log_sha256':digest(log)})
            if r.returncode:raise RuntimeError('Full capacity HLS testbench preflight failed '+mode)
        state['stage']='csim_synth_cosim';update()
        with ThreadPoolExecutor(max_workers=2) as pool:
            for f in as_completed([pool.submit(run,j) for j in plan['jobs']]):state['completed'].append(f.result());update()
        for p,h in {**files,**copied}.items():
            if digest(p)!=h:raise ValueError('Changed HLS input '+p)
        state.update(status='complete',stage='flow_complete_pending_independent_audit');update()
    except BaseException as e:
        state.update(status='failed',error=str(e));update();raise

if __name__=='__main__':main()
