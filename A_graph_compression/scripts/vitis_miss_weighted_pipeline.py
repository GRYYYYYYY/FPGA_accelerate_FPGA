#!/usr/bin/env python3
"""Run isolated CSR, compact and tile-cache matched weighted RTL experiments."""
from concurrent.futures import ThreadPoolExecutor,as_completed
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/derived/vitis_miss_weighted_cosim_20261023_v1'
FIXTURE=ROOT/'data/derived/vitis_miss_weighted_fixtures_20261023_v1'
HLS='/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls'
def save(path,data):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(path)
def run(label,entry):
    work=OUT/label;work.mkdir();state={'status':'running','stage':'copy','owner_pid':os.getpid()};sp=work/'state.json';save(sp,state)
    try:
        original=Path(entry['original']);project=Path(entry['project'])
        shutil.copytree(original,project,ignore=shutil.ignore_patterns('csim','sim','impl'))
        save(work/'copied_project.json',{'original':str(original),'copy':str(project),'files':{str(p.relative_to(project)):digest(p) for p in project.rglob('*') if p.is_file()}})
        env=os.environ.copy();env.update(A_STRATIFIED_PROJECT=str(project),A_STRATIFIED_MANIFEST=entry['manifest'],LD_PRELOAD='/lib/x86_64-linux-gnu/libudev.so.1')
        command=['taskset','-c',str(entry['cpu']),HLS,'-f',str(ROOT/'hardware/vitis/run_stratified_cosim.tcl')]
        with (work/'cosim.log').open('x') as f:
            child=subprocess.Popen(command,cwd=work,env=env,stdout=f,stderr=subprocess.STDOUT)
            state.update(stage='cosimulation',child_pid=child.pid,command=command);save(sp,state);code=child.wait()
        save(work/'receipt.json',{'exit_code':code,'log_sha256':digest(work/'cosim.log'),'command':command})
        require(code==0,'Cosim failed');state.update(status='complete',stage='await_audit');save(sp,state)
        return label
    except BaseException as exc:state.update(status='failed',error=str(exc));save(sp,state);raise

def main():
    require({121,123,124}<=os.sched_getaffinity(0),'CPUs unavailable')
    fp=FIXTURE/'plan.json';fixture=json.loads(fp.read_text());files={**fixture['files'],**fixture['generated'],str(fp):digest(fp)}
    for ap in [ROOT/'results/vitis_graph_kernel_audit_20261023_v2.json',ROOT/'results/vitis_tile_cache_cosim_audit_20261023_v1.json']:
        a=json.loads(ap.read_text());bindings=a['files'] if 'files' in a else a['artifacts']
        for path,sha in bindings.items():require(digest(path)==sha,'Prior audit dependency changed: '+path)
        files.update(bindings);files[str(ap)]=digest(ap)
    runs={}
    for label,mode,cpu,original in [('csr','csr',121,'vitis_graph_csr_20261023_v2'),('compact','compact',123,'vitis_graph_compact_20261023_v2'),('tile_cache','compact',124,'vitis_graph_compact_tile_cache_cosim_20261023_v1')]:
        orig=ROOT/'build'/original
        runs[label]={'original':str(orig),'project':str(ROOT/'build'/f'vitis_graph_{label}_miss_weighted_20261023_v1'),'cpu':cpu,'manifest':str(FIXTURE/mode/'rtl.txt')}
        for p in (orig/'solution/syn/verilog').glob('*.v'):files[str(p)]=digest(p)
    for p in [Path(__file__).resolve(),ROOT/'scripts/check_vitis_miss_weighted.py',ROOT/'hardware/vitis/run_stratified_cosim.tcl']:
        files[str(p)]=digest(p)
    for path,sha in files.items():require(digest(path)==sha,'Frozen input changed: '+path)
    OUT.mkdir(parents=True,exist_ok=False);save(OUT/'plan.json',{'files':files,'runs':runs,'fixture_plan':str(fp)})
    state={'owner_pid':os.getpid(),'status':'running','stage':'cosimulation','completed':[]};save(OUT/'state.json',state)
    try:
        with ThreadPoolExecutor(max_workers=3) as pool:
            for future in as_completed([pool.submit(run,label,entry) for label,entry in runs.items()]):
                state['completed'].append(future.result());save(OUT/'state.json',state)
        state.update(stage='independent_audit');save(OUT/'state.json',state)
        output=ROOT/'results/vitis_miss_weighted_audit_20261023_v1.json'
        command=['taskset','-c','121',sys.executable,str(ROOT/'scripts/check_vitis_miss_weighted.py'),'--bundle',str(OUT),'--output',str(output)]
        with (OUT/'audit.log').open('x') as f:code=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT).returncode
        save(OUT/'audit_receipt.json',{'exit_code':code,'log_sha256':digest(OUT/'audit.log'),'output':str(output),'report_sha256':digest(output) if output.exists() else None})
        require(code==0,'Independent audit failed');state.update(status='complete',stage='independently_audited');save(OUT/'state.json',state)
    except BaseException as exc:state.update(status='failed',error=str(exc));save(OUT/'state.json',state);raise
if __name__=='__main__':main()
