#!/usr/bin/env python3
"""Single downstream audit owner for the existing serialized full DPI replay."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from check_vitis_kernel import digest, require
from supervise_search_axi_dpi_v3 import atomic, identity

ROOT=Path(__file__).resolve().parents[1]
def main():
    upstream=ROOT/'data/derived/search_axi_dpi_serialized_supervision_20261025_v3'
    source=json.loads((upstream/'state.json').read_text())
    owner=identity(source['owner_pid']);require(owner and 'supervise_search_axi_dpi_v3.py' in owner['command'],'Original replay owner missing; reconcile')
    out=ROOT/'data/derived/search_axi_dpi_final_audit_supervision_20261025_v3';out.mkdir(exist_ok=False)
    checker=ROOT/'scripts/check_search_axi_dpi_replay_v3.py'
    inputs=[checker,Path(__file__).resolve(),upstream/'plan.json',ROOT/'scripts/supervise_search_axi_dpi_v3.py',ROOT/'scripts/check_axi_dpi_storage_edits_v1.py']
    hashes={str(p):digest(p) for p in inputs};atomic(out/'plan.json',dict(upstream_owner=owner,files=hashes))
    state=dict(owner_pid=os.getpid(),status='running',stage='waiting_original_serialized_replay_owner')
    atomic(out/'state.json',state)
    try:
        while identity(owner['pid'])==owner:time.sleep(30)
        source=json.loads((upstream/'state.json').read_text())
        require(source['status']=='complete' and source['stage']=='full_replay_accepted_pending_independent_audit','Upstream replay did not complete; no success inferred')
        for p,h in hashes.items():require(digest(p)==h,'Changed final audit input '+p)
        bundle=Path('/tmp/A_graph_compression_recovery_20261025_v1/search_axi_dpi_replay_v3')
        result=ROOT/'results/search_axi_dpi_replay_audit_20261025_v3.json'
        require(not result.exists(),'Final result already exists; no duplicate audit')
        command=[sys.executable,str(checker),'--bundle',str(bundle),'--output',str(result)]
        state['stage']='independent_full_depth_cycle_output_and_c_oracle_audit';atomic(out/'state.json',state)
        with (out/'audit.log').open('x') as log:
            child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
            state['child_pid']=child.pid;atomic(out/'state.json',state);code=child.wait()
        require(code==0 and result.exists(),'Independent acceptance failed')
        state.update(status='complete',stage='search_core_full_depth_dpi_replay_independently_audited',report=str(result),report_sha256=digest(result),audit_log_sha256=digest(out/'audit.log'))
        atomic(out/'state.json',state)
    except BaseException as e:state.update(status='failed',error=str(e));atomic(out/'state.json',state);raise
if __name__=='__main__':main()
