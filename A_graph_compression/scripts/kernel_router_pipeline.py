#!/usr/bin/env python3
"""Single owner for four full-router C-model integration trials and their independent audit."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from check_vitis_kernel import digest,require

ROOT=Path(__file__).resolve().parents[1]
PREP=ROOT/'data/derived/kernel_router_cmodel_20261023_v1'
OUT=ROOT/'data/derived/kernel_router_integration_20261023_v1'


def save(path,value):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(value,indent=2)+'\n');tmp.replace(path)


def main():
    preparation_path=PREP/'preparation.json';prep=json.loads(preparation_path.read_text())
    require(prep['status']=='both_full_graph_abi_providers_verified_router_not_yet_executed','Provider preparation failed')
    require(digest(PREP/'plan.json')==prep['plan_sha256'],'Preparation plan changed')
    source=json.loads((PREP/'plan.json').read_text())
    files={**source['files'],**source['generated']}
    for mode in ['csr','compact']:files.update(prep['modes'][mode]['files'])
    refs=set(source['references'].values())
    for path,sha in files.items():
        if path not in refs:require(digest(path)==sha,'Frozen provider input changed: '+path)
    deps=[Path(__file__).resolve(),ROOT/'scripts/check_kernel_router.py',ROOT/'scripts/check_vitis_kernel.py',
          PREP/'plan.json',preparation_path]
    files.update({str(p):digest(p) for p in deps})
    configs={m:str(ROOT/'data/derived/hls_region_fixtures_20261023_v1'/m/'config.bin') for m in ['csr','compact']}
    files.update({p:digest(p) for p in configs.values()})
    jobs=[{'mode':mode,'execution':execution,'cpu':cpu} for execution in ['expanded','direct'] for mode,cpu in [('csr',122),('compact',124)]]
    OUT.mkdir(parents=True,exist_ok=False)
    plan={'created_utc':datetime.now(timezone.utc).isoformat(),'owner_pid':os.getpid(),'files':files,
          'inputs':source['inputs'],'references':source['references'],'configs':configs,
          'binaries':{m:str(PREP/m/'router') for m in ['csr','compact']},'jobs':jobs,
          'limitations':source['limitations']+['One process per condition, two full1062-net batches; protocol/equivalence validation, not repeated performance statistics.',
               'Actual execution is CPU C model. No XRT invocation, PCIe/DDR/HBM measurement, full-FPGA search, or new physical readback.',
               'Existing search, cost, occupancy and site-state algorithms are unchanged. CPU modes share the same golden routes.']}
    save(OUT/'plan.json',plan)
    state_path=OUT/'state.json';state={'owner_pid':os.getpid(),'status':'running','stage':'full_router_trials','completed_modes':[]}
    save(state_path,state)
    def mode_trials(mode):
        for i,job in enumerate(jobs):
            if job['mode']!=mode:continue
            prefix=OUT/f'worker_{i:03d}';inp=plan['inputs'][mode]
            command=[plan['binaries'][mode],inp['image'],inp['fixture'],inp['sites'],'4096','80','200000','8',job['execution'],configs[mode]]
            before=time.monotonic_ns()
            with prefix.with_suffix('.raw.json').open('x') as out,prefix.with_suffix('.log').open('x') as err:
                # taskset avoids fork-time Python callbacks in this multithreaded owner.
                child=subprocess.Popen(['taskset','-c',str(job['cpu']),*command],stdout=out,stderr=err)
                save(prefix.with_suffix('.submission.json'),{'owner_pid':os.getpid(),'child_pid':child.pid,
                    'cpu':job['cpu'],'command':command,'launch_command':['taskset','-c',str(job['cpu']),*command],
                    'started_monotonic_ns':before})
                code=child.wait()
            elapsed=(time.monotonic_ns()-before)/1e6
            save(prefix.with_suffix('.receipt.json'),{'exit_code':code,'condition':job,'process_wall_ms':elapsed,
                 'raw_sha256':digest(prefix.with_suffix('.raw.json')),'log_sha256':digest(prefix.with_suffix('.log'))})
            require(code==0,'Full router C-model trial failed: '+str(i))
            print('KERNEL_ROUTER_WORKER_COMPLETE',i,mode,job['execution'],flush=True)
        return mode
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            for future in as_completed([pool.submit(mode_trials,m) for m in ['csr','compact']]):
                state['completed_modes'].append(future.result());save(state_path,state)
        output=ROOT/'results/kernel_router_integration_audit_20261023_v1.json'
        command=['taskset','-c','124',sys.executable,str(ROOT/'scripts/check_kernel_router.py'),'--bundle',str(OUT),'--output',str(output)]
        with (OUT/'audit.log').open('x') as log:
            child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
            state.update(stage='independent_full_audit',child_pid=child.pid);save(state_path,state);code=child.wait()
        require(code==0,'Independent full-router audit failed')
        state.pop('child_pid',None);state.update(status='complete',stage='independently_audited',report=str(output),report_sha256=digest(output));save(state_path,state)
    except BaseException as exc:
        state.update(status='failed',error=str(exc));save(state_path,state);raise


if __name__=='__main__':main()
