#!/usr/bin/env python3
"""Start one full-depth DPI replay after the original owned jobs terminate."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from check_vitis_kernel import digest, require

ROOT=Path(__file__).resolve().parents[1]
def atomic(path,value):
    temporary=path.with_suffix('.tmp')
    with temporary.open('w') as f:
        json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(temporary,path)
def identity(pid):
    p=Path('/proc')/str(pid)
    try:
        stat=(p/'stat').read_text().rsplit(')',1)[1].split()
        if stat[0]=='Z':return None
        return dict(pid=pid,start_ticks=stat[19],command=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode(),cwd=str((p/'cwd').resolve()))
    except FileNotFoundError:return None
def main():
    out=ROOT/'data/derived/search_axi_dpi_serialized_supervision_20261025_v3'
    out.mkdir(exist_ok=False)
    blockers=[]
    for pid,script in [(2508987,'resident_snapshot_rtl_local_recovery.py'),(1504642,'run_compressed_batch_compact_rtl_guarded.py')]:
        who=identity(pid)
        require(who is not None and script in who['command'] and who['cwd']==str(ROOT),'Original job identity no longer matches; reconcile before scheduling')
        blockers.append(who)
    driver=ROOT/'scripts/replay_search_axi_dpi_v3.py'
    inputs=[driver,Path(__file__).resolve(),ROOT/'scripts/transform_axi_memory_dpi_v2.py',ROOT/'hardware/sim/axi_dpi_memory_v1.cpp']
    for name in ['search_packet_width64_rtl_audit_20261025_v1.json','axi_dpi_memory_unit_20261025_v2.json','axi_dpi_helper_provenance_20261025_v1.json','axi_dpi_protocol_provenance_20261025_v1.json','axi_dpi_protocol_pages_oracle_20261025_v1.json']:
        inputs.append(ROOT/'results'/name)
    plan=dict(blockers=blockers,files={str(p):digest(p) for p in inputs},
              required_raw_free_bytes=184*1024**3,poll_seconds=30,
              command=[sys.executable,str(driver)],
              acceptance='Original two full-depth transactions, exact cycle counts [2132461,12404], complete output file set and bytes, original C postcheck; independent final audit remains required',
              policy='One launch only; no retry, no termination or rescheduling of original jobs')
    atomic(out/'plan.json',plan)
    state=dict(owner_pid=os.getpid(),status='running',stage='waiting_original_jobs_and_raw_cgroup_headroom')
    atomic(out/'state.json',state)
    try:
        cg=Path('/sys/fs/cgroup')
        while True:
            live=[x['pid'] for x in blockers if identity(x['pid'])==x]
            maximum=int((cg/'memory.max').read_text());current=int((cg/'memory.current').read_text())
            state.update(live_blocker_pids=live,memory=dict(maximum_bytes=maximum,current_bytes=current,raw_free_bytes=maximum-current),observed_unix=time.time())
            atomic(out/'state.json',state)
            if not live and maximum-current>=plan['required_raw_free_bytes']:break
            time.sleep(plan['poll_seconds'])
        for p,h in plan['files'].items():require(digest(p)==h,'Scheduled input changed '+p)
        require(not Path('/tmp/A_graph_compression_recovery_20261025_v1/search_axi_dpi_replay_v3').exists(),'Replay attempt already exists; never duplicate')
        with (out/'replay.log').open('x') as log:
            child=subprocess.Popen(plan['command'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
            state.update(stage='full_original_two_transaction_dpi_replay',child_pid=child.pid)
            atomic(out/'state.json',state);code=child.wait()
        state.update(exit_code=code,replay_log_sha256=digest(out/'replay.log'))
        require(code==0,'Full replay failed; preserve trial and return for diagnosis')
        actual=json.loads(Path('/tmp/A_graph_compression_recovery_20261025_v1/search_axi_dpi_replay_v3/state.json').read_text())
        require(actual['status']=='complete' and actual['cycles']==[2132461,12404],'Full replay acceptance missing')
        state.update(status='complete',stage='full_replay_accepted_pending_independent_audit')
        atomic(out/'state.json',state)
    except BaseException as e:
        state.update(status='failed',error=str(e));atomic(out/'state.json',state);raise
if __name__=='__main__':main()
