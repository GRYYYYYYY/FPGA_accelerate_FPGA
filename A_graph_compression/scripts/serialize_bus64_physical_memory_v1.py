#!/usr/bin/env python3
"""Protect the same owned physical process from concurrent compiler memory growth."""
import json
import os
import signal
import time
from pathlib import Path
from check_vitis_kernel import digest,require
from supervise_search_axi_dpi_v3 import atomic,identity

ROOT=Path(__file__).resolve().parents[1]
def main():
    target=identity(1924562);require(target and 'vivado' in target['command'] and target['cwd']==str(ROOT/'data/derived/compressed_batch_bus64_physical_20261025_v1/csr/source'),'Wrong physical owner')
    blockers=[identity(pid) for pid in [2516537,1509104]]
    require(all(blockers) and all('/xelab ' in p['command'] for p in blockers),'Original compiler identities differ')
    out=ROOT/'data/derived/bus64_physical_memory_serialization_20261025_v1';out.mkdir(exist_ok=False)
    atomic(out/'plan.json',dict(target=target,blockers=blockers,source_sha256=digest(__file__),
        pressure_threshold_bytes=270*1024**3,resume_raw_free_bytes=64*1024**3,
        policy='Signal only the same target PID; never restart, alter input or signal existing compilers. Ignore already suspended compilers for resume dependency.'))
    state=dict(owner_pid=os.getpid(),status='running',stage='monitoring_original_concurrent_flows',target=target,suspended_by_this_controller=False)
    atomic(out/'state.json',state);cg=Path('/sys/fs/cgroup')
    target_fd=os.pidfd_open(target['pid'])
    try:
        while True:
            current=identity(target['pid']);require(current==target,'Original physical process missing/reused; reconcile state')
            memory={k:int(v) for k,v in (line.split() for line in (cg/'memory.stat').read_text().splitlines())}
            pressure=sum(memory.get(k,0) for k in ['anon','kernel_stack','pagetables','slab_unreclaimable','shmem','file_dirty','file_writeback'])
            maximum=int((cg/'memory.max').read_text());used=int((cg/'memory.current').read_text());active=[]
            for b in blockers:
                if identity(b['pid'])==b:
                    mode=(Path('/proc')/str(b['pid'])/'stat').read_text().rsplit(')',1)[1].split()[0]
                    if mode not in ['T','t','Z']:active.append(b['pid'])
            state.update(observed_unix=time.time(),active_compiler_pids=active,memory=dict(pressure_proxy_bytes=pressure,current_bytes=used,maximum_bytes=maximum,raw_free_bytes=maximum-used,anon_bytes=memory['anon'],file_bytes=memory['file']),events=(cg/'memory.events').read_text())
            flow=json.loads((Path(target['cwd']).parent/'state.json').read_text())
            if flow['status'] in ['complete','failed'] and not state['suspended_by_this_controller']:
                state.update(status='complete',stage='original_physical_flow_terminal_no_suspended_process');atomic(out/'state.json',state);break
            if not state['suspended_by_this_controller'] and active and pressure>=270*1024**3:
                require(not (Path('/proc')/str(target['pid'])/'task'/str(target['pid'])/'children').read_text().strip(),'New child process requires separate resource review')
                require(identity(target['pid'])==target,'Identity changed before stop')
                signal.pidfd_send_signal(target_fd,signal.SIGSTOP)
                state.update(suspended_by_this_controller=True,stage='same_physical_pid_suspended_waiting_active_compilers')
            elif state['suspended_by_this_controller'] and not active and maximum-used>=64*1024**3:
                require(identity(target['pid'])==target,'Identity changed before resume')
                signal.pidfd_send_signal(target_fd,signal.SIGCONT)
                state.update(suspended_by_this_controller=False,stage='same_physical_pid_resumed_monitoring')
            atomic(out/'state.json',state);time.sleep(5)
    except BaseException as e:
        state.update(status='failed',error=str(e),resume_required_for_existing_pid=target['pid'] if state['suspended_by_this_controller'] else None);atomic(out/'state.json',state);raise
    finally:os.close(target_fd)
if __name__=='__main__':main()
