#!/usr/bin/env python3
"""Watch only the dedicated packet64 physopt PID; abort at real raw-free pressure."""
import json,os,signal,time
from pathlib import Path
from run_compact_native_stack_recovery_v1 import atomic
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
def main():
    bundle=ROOT/'data/derived/search_packet64_physopt_20261025_v1';out=bundle/'memory_guard';out.mkdir(exist_ok=False)
    admission=json.loads((bundle/'runtime_admission.json').read_text());pid=admission['pid'];proc=Path('/proc')/str(pid)
    state=dict(owner_pid=os.getpid(),status='running',stage='watching_dedicated_physical_session',target_pid=pid)
    atomic(out/'plan.json',dict(admission_sha256=digest(bundle/'runtime_admission.json'),script_sha256=digest(__file__),minimum_free_bytes=16*1024**3));atomic(out/'state.json',state)
    while True:
        try:
            stat=(proc/'stat').read_text().rsplit(')',1)[1].split();command=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode()
        except FileNotFoundError:
            state.update(status='complete',stage='target_exited_no_restart');break
        require(stat[19]==admission['start_ticks'] and command==admission['command'],'Target PID reused; refuse any signal')
        if (bundle/'state.json').exists():
            flow=json.loads((bundle/'state.json').read_text())
            if flow['status'] in ['complete','failed']:
                state.update(status='complete',stage='flow_terminal',flow_status=flow['status']);break
        maximum=int(Path('/sys/fs/cgroup/memory.max').read_text());current=int(Path('/sys/fs/cgroup/memory.current').read_text())
        if maximum-current<16*1024**3:
            atomic(out/'resource_abort.json',dict(pid=pid,start_ticks=stat[19],command=command,cgroup_current=current,cgroup_maximum=maximum,reason='raw_free_below_16GiB'))
            fd=os.pidfd_open(pid)
            try:signal.pidfd_send_signal(fd,signal.SIGTERM)
            finally:os.close(fd)
            state.update(status='complete',stage='resource_abort_sent_to_verified_owned_pid');break
        time.sleep(2)
    atomic(out/'state.json',state)
if __name__=='__main__':main()
