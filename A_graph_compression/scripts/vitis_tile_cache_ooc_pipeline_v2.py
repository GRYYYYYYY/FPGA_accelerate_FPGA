#!/usr/bin/env python3
"""Implement one copy of the audited tile-cache candidate; preserve all earlier projects."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from check_vitis_kernel import digest,require
from real_experiment import write_new
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/derived/vitis_tile_cache_ooc_20261023_v2'
HLS=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls')

def save(path,data):
    temporary=path.with_suffix('.tmp');temporary.write_text(json.dumps(data,indent=2)+'\n');temporary.replace(path)

def run(mode,cpu):
    target=ROOT/'build'/f'vitis_graph_{mode}_tile_cache_ooc_20261023_v2';work=OUT/mode;work.mkdir()
    state_path=OUT/(mode+'.state.json');state={'owner_pid':os.getpid(),'status':'running','stage':'copy_audited_project','cpu':cpu,'mode':mode}
    save(state_path,state)
    try:
        source=ROOT/'build'/f'vitis_graph_{mode}_tile_cache_cosim_20261023_v1'
        def ignore(directory,names):return [n for n in names if n!='report'] if Path(directory).name=='sim' else []
        shutil.copytree(source,target,ignore=ignore)
        staging=ROOT/'build'/f'vitis_graph_{mode}_tile_cache_20261023_v1/solution/impl'
        require(not (target/'solution/impl').exists(),'Unexpected existing implementation staging')
        shutil.copytree(staging,target/'solution/impl')
        for path in staging.rglob('*'):
            if path.is_file():require(digest(path)==digest(target/'solution/impl'/path.relative_to(staging)),'Staging copy mismatch')
        copied={str(p.relative_to(target)):digest(p) for p in target.rglob('*') if p.is_file()}
        write_new(work/'copied_project.json',{'original':str(source),'copy':str(target),'initial_files':copied,
            'implementation_staging_source':str(staging),'copy_policy':'Same-candidate synthesis impl staging restored; regular byte copies, no hardlinks; sim retains reports only. Copy is mutable implementation workspace.'})
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
    require({122}<=os.sched_getaffinity(0),'Independent build CPUs unavailable')
    audit=ROOT/'results/vitis_tile_cache_cosim_audit_20261023_v1.json';report=json.loads(audit.read_text())
    require(report['status']=='tile_cache_rtl_golden_verified','Kernel baseline not audited')
    source_plan=ROOT/'data/derived/vitis_tile_cache_cosim_20261023_v1/plan.json';plan=json.loads(source_plan.read_text())
    files={**report['files'],**plan['files'],**plan.get('generated',{})}
    for path,value in files.items():require(digest(path)==value,'Audited baseline changed')
    files.update({str(p):digest(p) for p in [Path(__file__).resolve(),ROOT/'hardware/vitis/run_impl.tcl',audit,ROOT/'scripts/check_vitis_tile_cache_ooc_v2.py',ROOT/'scripts/check_netlist_quality.py',ROOT/'scripts/check_vitis_ooc.py']})
    synthesis=ROOT/'build/vitis_graph_compact_tile_cache_20261023_v1/solution'
    cosim=ROOT/'build/vitis_graph_compact_tile_cache_cosim_20261023_v1/solution'
    original={p.name:digest(p) for p in (synthesis/'syn/verilog').glob('*.v')}
    audited={p.name:digest(p) for p in (cosim/'syn/verilog').glob('*.v')}
    require(original and original==audited,'Staging synthesis RTL differs from audited candidate')
    require((synthesis/'impl/verilog/graph_accel.v').is_file(),'Missing implementation staging top')
    files.update({str(p):digest(p) for base in [synthesis/'impl',synthesis/'syn/verilog'] for p in base.rglob('*') if p.is_file()})
    OUT.mkdir(parents=True,exist_ok=False)
    write_new(OUT/'plan.json',{'created_utc':datetime.now(timezone.utc).isoformat(),'files':files,
        'scope':'HLS export_design -flow impl on copied2022.2 projects. OOC only, no platform xclbin or board timing.',
        'modes':['compact'],'cpu_bindings':[122]})
    state_path=OUT/'pipeline.json';state={'owner_pid':os.getpid(),'status':'running','stage':'independent_ooc_implementations','completed_modes':[]}
    save(state_path,state)
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            for future in as_completed([pool.submit(run,mode,cpu) for mode,cpu in [('compact',122)]]):
                state['completed_modes'].append(future.result());save(state_path,state)
        for path,value in files.items():require(digest(path)==value,'Original audited artifact changed during copied implementation')
        state.update(status='complete',stage='await_independent_report');save(state_path,state)
        audit_output=ROOT/'results/vitis_tile_cache_ooc_audit_20261023_v2.json'
        command=['taskset','-c','122',sys.executable,str(ROOT/'scripts/check_vitis_tile_cache_ooc_v2.py'),'--output',str(audit_output)]
        with (OUT/'audit.log').open('x') as log:
            child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
            code=child.wait()
        write_new(OUT/'audit_receipt.json',{'exit_code':code,'log_sha256':digest(OUT/'audit.log'),
            'output':str(audit_output),'report_sha256':digest(audit_output) if audit_output.exists() else None})
        require(code==0,'Independent tile-cache OOC audit failed')
        print('TILE_CACHE_OOC_INDEPENDENT_AUDIT_COMPLETE',flush=True)
    except BaseException as exc:
        if (OUT/'audit_receipt.json').exists():
            save(OUT/'audit_failure.json',{'error':str(exc)})
        else:
            state.update(status='failed',error=str(exc));save(state_path,state)
        raise

if __name__=='__main__':main()
