#!/usr/bin/env python3
"""Single-owner eight-process read-only capture; strict merge after all receipts."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
from time import perf_counter

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'adapters')]
from canonical_graph import validate
from import_vivado import read_export,sha256


def main():
    prefix=ROOT/'results/region_u280_capture_20261022_v1'
    owner_lock=prefix.with_suffix('.lock').open('a');fcntl.flock(owner_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    cfg_path=ROOT/'configs/region_u280_v1.json';cfg=json.loads(cfg_path.read_text())
    directory=ROOT/cfg['output_dir'];plan=json.loads((directory/'execution_plan.json').read_text())
    pilot=json.loads((directory/'pilot_check.json').read_text())
    if not pilot['equal']:raise ValueError('Adapter pilot did not pass')
    logs=directory/'logs';logs.mkdir(exist_ok=False)
    state={'owner_pid':os.getpid(),'status':'running','stage':'capture',
           'started_utc':datetime.now(timezone.utc).isoformat(),'jobs':[{**j,'status':'pending'} for j in plan['jobs']]}
    mutex=threading.Lock();failed=threading.Event()
    def change(index=None,**values):
        with mutex:
            (state if index is None else state['jobs'][index]).update(values)
            tmp=prefix.with_suffix('.tmp');tmp.write_text(json.dumps(state,indent=2)+'\n');tmp.replace(prefix.with_suffix('.json'))
    change()
    def run(index,job):
        if failed.is_set():change(index,status='not_started_after_failure');return False
        try:
            if sha256(cfg_path)!=plan['config_sha256'] or sha256(ROOT/job['roots'])!=job['roots_sha256']:
                raise ValueError('Frozen config/source list changed')
            for name,digest in plan['code_sha256'].items():
                if sha256(ROOT/name)!=digest:raise ValueError('Exporter code changed')
            command=['/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin/vivado',
                '-mode','batch','-source',str(ROOT/'adapters/export_region_shard.tcl'),
                '-log',str(logs/(job['id']+'.log')),'-journal',str(logs/(job['id']+'.jou')),
                '-tclargs',str(ROOT/job['roots']),str(ROOT/job['output']),str(ROOT/cfg['checkpoint']),plan['config_sha256'],job['id']]
            env=os.environ.copy();env['LD_PRELOAD']='/lib/x86_64-linux-gnu/libudev.so.1'
            start=perf_counter()
            stdout=logs/(job['id']+'.stdout')
            with stdout.open('x') as stream:
                child=subprocess.Popen(command,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT)
                change(index,status='running',pid=child.pid,command=command,stdout=str(stdout.relative_to(ROOT)))
                code=child.wait()
            marker='REGION_SHARD_COMPLETE id='+job['id']+' roots='+str(job['sources'])
            text=stdout.read_text()
            if code or marker not in text or 'ERROR:' in text:raise RuntimeError('Vivado partition failed')
            graph=read_export(ROOT/job['output']);validate(graph)
            if set(graph['roots'])!=set((ROOT/job['roots']).read_text().splitlines()):raise ValueError('Source coverage differs')
            change(index,status='complete',exit_code=code,wall_seconds=perf_counter()-start,
                   sha256=sha256(ROOT/job['output']),summary={k:len(graph[k]) for k in ['roots','nodes','aliases','pips','edges']})
            return True
        except BaseException as exc:
            failed.set();change(index,status='failed',error=str(exc));return False
    with ThreadPoolExecutor(max_workers=cfg['workers']) as pool:
        outcomes=[f.result() for f in as_completed([pool.submit(run,i,j) for i,j in enumerate(plan['jobs'])])]
    if not all(outcomes):change(status='failed',stage='inspect_partition_failures');return 1
    change(stage='merge_validate')
    log=ROOT/'results/region_u280_merge_20261022_v1.log'
    with log.open('x') as stream:
        child=subprocess.Popen([sys.executable,str(ROOT/'scripts/finalize_region_capture.py')],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
        change(child_pid=child.pid);code=child.wait()
    change(status='complete' if code==0 else 'failed',stage='capture_ready' if code==0 else 'inspect_merge_failure',merge_exit_code=code)
    return code


if __name__=='__main__':raise SystemExit(main())
