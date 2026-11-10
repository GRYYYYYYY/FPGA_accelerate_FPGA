#!/usr/bin/env python3
"""One capped full-depth replay and independent audit after explicit supervisor handoff."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from check_vitis_kernel import digest,require
from supervise_search_axi_dpi_v3 import atomic
ROOT=Path(__file__).resolve().parents[1]
def main():
    handoff=ROOT/'data/derived/search_dpi_supervision_handoff_20261025_v4/terminal.json'
    require(json.loads(handoff.read_text())['status']=='old_wait_only_supervisors_terminated_no_experiment_restarted','Handoff incomplete')
    out=ROOT/'data/derived/search_axi_dpi_capped_supervision_20261025_v5';out.mkdir(exist_ok=False)
    driver=ROOT/'scripts/replay_search_axi_dpi_v5.py';checker=ROOT/'scripts/check_search_axi_dpi_replay_v5.py'
    files={str(p):digest(p) for p in [handoff,driver,checker,Path(__file__).resolve()]}
    atomic(out/'plan.json',dict(files=files,minimum_raw_free_bytes=72*1024**3,per_process_address_space_limit_bytes=48*1024**3,core_dump_limit_bytes=0,full_four_state_model_backing_bytes=4190310144,
        policy='Keep original snapshot/compact experiments untouched; one capped original two-transaction replay, no automatic retry'))
    state=dict(owner_pid=os.getpid(),status='running',stage='waiting_lossless_core_archive_and_cgroup_admission');atomic(out/'state.json',state)
    try:
        archive=ROOT/'data/derived/capped_xelab_core_archive_20261025_v1'
        while True:
            a=json.loads((archive/'state.json').read_text())
            if a['status']!='running':break
            proc=Path('/proc')/str(a['owner_pid'])
            require(proc.exists() and b'archive_capped_xelab_core_v1.py' in (proc/'cmdline').read_bytes(),'Core archive owner missing; reconcile')
            time.sleep(30)
        require(a['status']=='complete','Core archive failed; no new replay')
        manifest=json.loads((archive/'manifest.json').read_text())
        require(manifest['source_removed'] and manifest['status']=='full_original_core_losslessly_preserved_independent_decompression_verified','Lossless archive verification missing')
        files[str(archive/'manifest.json')]=digest(archive/'manifest.json')
        cg=Path('/sys/fs/cgroup')
        while int((cg/'memory.max').read_text())-int((cg/'memory.current').read_text())<72*1024**3:time.sleep(30)
        bundle=Path('/tmp/A_graph_compression_recovery_20261025_v1/search_axi_dpi_replay_v5')
        result=ROOT/'results/search_axi_dpi_replay_audit_20261025_v3.json'
        require(not bundle.exists() and not result.exists(),'Existing attempt or accepted report; do not duplicate')
        for phase,command in [('full_capped_replay',[sys.executable,str(driver)]),('independent_audit',[sys.executable,str(checker),'--bundle',str(bundle),'--output',str(result)])]:
            for p,h in files.items():require(digest(p)==h,'Changed scheduled input')
            state['stage']=phase;atomic(out/'state.json',state);start=time.monotonic()
            with (out/(phase+'.log')).open('x') as log:
                child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
                state['child_pid']=child.pid;atomic(out/'state.json',state);code=child.wait()
            atomic(out/(phase+'.receipt.json'),dict(command=command,exit_code=code,elapsed_seconds=time.monotonic()-start,log_sha256=digest(out/(phase+'.log'))))
            require(code==0,'Capped replay/audit failed; preserve trial for diagnosis')
        state.update(status='complete',stage='search_core_full_depth_dpi_replay_independently_audited',report=str(result),report_sha256=digest(result));atomic(out/'state.json',state)
    except BaseException as e:state.update(status='failed',error=str(e));atomic(out/'state.json',state);raise
if __name__=='__main__':main()
