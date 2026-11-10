#!/usr/bin/env python3
"""Single-owner continuation from regional capture to all eligible routing queries."""
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'adapters'),str(ROOT/'scripts')]
from import_vivado import sha256
from real_experiment import write_new


def main():
    prefix=ROOT/'results/region_routing_pipeline_20261022_v1'
    lock=prefix.with_suffix('.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    capture_state=ROOT/'results/region_u280_capture_20261022_v1.json'
    original=json.loads(capture_state.read_text());capture_pid=original['owner_pid']
    if original['status']=='running':
        command=Path(f'/proc/{capture_pid}/cmdline').read_bytes()
        if b'scripts/region_capture.py' not in command:raise ValueError('Capture owner identity changed')
    files=['scripts/netlist_experiment.py','src/netlist_routing.py','src/row_cache.py',
           'src/search_experiment.py','src/template_codec.py','src/heldout.py',
           'src/packed_graph.py','src/canonical_graph.py','scripts/real_experiment.py',
           'configs/region_u280_v1.json']
    command=[sys.executable,str(ROOT/'scripts/netlist_experiment.py'),'--config',str(ROOT/'configs/region_u280_v1.json'),
             '--iterations','80','--present-cap','8','--max-expansions','200000',
             '--template-provider','prepared','--row-cache-capacity','4096',
             '--output-dir',str(ROOT/'data/derived/region_all_nets_cap8_20261022_v1')]
    plan={'owner_pid':os.getpid(),'capture_owner_pid':capture_pid,'command':command,
          'files':{p:sha256(ROOT/p) for p in files},'scope':'All 1062 frozen eligible nets; no reference containment filtering; unknown boundaries retained.'}
    write_new(prefix.with_suffix('.plan.json'),plan)
    state={'owner_pid':os.getpid(),'stage':'waiting_capture','status':'running'}
    def update(**values):
        state.update(values);tmp=prefix.with_suffix('.tmp');tmp.write_text(json.dumps(state,indent=2)+'\n');tmp.replace(prefix.with_suffix('.json'))
    update()
    while True:
        receipt=json.loads(capture_state.read_text())
        if receipt['owner_pid']!=capture_pid:raise ValueError('Capture owner changed')
        if receipt['status']=='failed':
            update(status='failed',stage='capture_failed');return 1
        if receipt['status']=='complete':break
        try:os.kill(capture_pid,0)
        except ProcessLookupError:
            update(status='failed',stage='capture_owner_missing_without_complete_receipt');return 1
        time.sleep(10)
    for name,digest in plan['files'].items():
        if sha256(ROOT/name)!=digest:
            update(status='failed',stage='source_changed',file=name);return 1
    with (ROOT/'results/region_all_nets_cap8_20261022_v1.log').open('x') as stream:
        child=subprocess.Popen(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
        update(stage='routing',child_pid=child.pid);code=child.wait()
    update(status='complete' if code==0 else 'failed',stage='inspect_routing_results' if code==0 else 'routing_failed',exit_code=code)
    return code


if __name__=='__main__':raise SystemExit(main())
