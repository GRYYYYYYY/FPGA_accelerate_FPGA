#!/usr/bin/env python3
"""Implement separate copies of audited v2 projects; preserve the XO baseline."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
from check_vitis_kernel import digest,require
from real_experiment import write_new
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/derived/vitis_ooc_20261023_v1'
HLS=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls')

def save(path,data):
    temporary=path.with_suffix('.tmp');temporary.write_text(json.dumps(data,indent=2)+'\n');temporary.replace(path)

def run(mode,cpu):
    target=ROOT/'build'/f'vitis_graph_{mode}_ooc_20261023_v1';work=OUT/mode;work.mkdir()
    state_path=OUT/(mode+'.state.json');state={'owner_pid':os.getpid(),'status':'running','stage':'copy_audited_project','cpu':cpu,'mode':mode}
    save(state_path,state)
    try:
        source=ROOT/'build'/f'vitis_graph_{mode}_20261023_v2'
        def ignore(directory,names):return [n for n in names if n!='report'] if Path(directory).name=='sim' else []
        shutil.copytree(source,target,ignore=ignore)
        copied={str(p.relative_to(target)):digest(p) for p in target.rglob('*') if p.is_file()}
        write_new(work/'copied_project.json',{'original':str(source),'copy':str(target),'initial_files':copied,
            'copy_policy':'Regular byte copies, no hardlinks; sim retains reports only. Copy is mutable implementation workspace.'})
        env=os.environ.copy();env.update(A_VITIS_IMPL_PROJECT=str(target),LD_PRELOAD='/lib/x86_64-linux-gnu/libudev.so.1')
        command=['taskset','-c',str(cpu),str(HLS),'-f',str(ROOT/'hardware/vitis/run_impl.tcl')]
        log=work/'impl.log'
        with log.open('x') as stream:
            child=subprocess.Popen(command,cwd=work,env=env,stdout=stream,stderr=subprocess.STDOUT)
            state.update(stage='implementation',child_pid=child.pid,command=command,project=str(target));save(state_path,state);code=child.wait()
        content=log.read_text();receipt={'exit_code':code,'completion_marker':'VITIS_GRAPH_OOC_IMPL_COMPLETE' in content,'log_sha256':digest(log),'command':command}
        write_new(work/'receipt.json',receipt)
        state.pop('child_pid',None);require(code==0 and receipt['completion_marker'] and 'ERROR:' not in content,'OOC implementation failed')
        state.update(status='complete',stage='await_independent_report');save(state_path,state);return mode
    except BaseException as exc:
        state.update(status='failed',error=str(exc));save(state_path,state);raise

def main():
    require({122,123}<=os.sched_getaffinity(0),'Independent build CPUs unavailable')
    audit=ROOT/'results/vitis_graph_kernel_audit_20261023_v2.json';report=json.loads(audit.read_text())
    require(report['status']=='verified_vitis_xo_not_platform_linked','Kernel baseline not audited')
    source_plan=ROOT/'data/derived/vitis_graph_kernel_20261023_v2/plan.json';plan=json.loads(source_plan.read_text())
    files={**report['artifacts'],**plan['files'],**plan['generated']}
    for path,value in files.items():require(digest(path)==value,'Audited baseline changed')
    files.update({str(p):digest(p) for p in [Path(__file__).resolve(),ROOT/'hardware/vitis/run_impl.tcl',audit]})
    OUT.mkdir(parents=True,exist_ok=False)
    write_new(OUT/'plan.json',{'created_utc':datetime.now(timezone.utc).isoformat(),'files':files,
        'scope':'HLS export_design -flow impl on copied2022.2 projects. OOC only, no platform xclbin or board timing.',
        'modes':['csr','compact'],'cpu_bindings':[122,123]})
    state_path=OUT/'pipeline.json';state={'owner_pid':os.getpid(),'status':'running','stage':'independent_ooc_implementations','completed_modes':[]}
    save(state_path,state)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            for future in as_completed([pool.submit(run,mode,cpu) for mode,cpu in [('csr',122),('compact',123)]]):
                state['completed_modes'].append(future.result());save(state_path,state)
        for path,value in files.items():require(digest(path)==value,'Original audited artifact changed during copied implementation')
        state.update(status='complete',stage='await_independent_report');save(state_path,state)
    except BaseException as exc:
        state.update(status='failed',error=str(exc));save(state_path,state);raise

if __name__=='__main__':main()
