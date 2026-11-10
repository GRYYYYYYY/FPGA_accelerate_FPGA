#!/usr/bin/env python3
"""Wait for the existing execution owner and audit once, without rerunning RTL."""
import json,os,subprocess,time
from pathlib import Path
from check_vitis_kernel import digest,require
from supervise_compressed_batch_hls import identity
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
def main():
    out=BASE/'compressed_batch_guarded_final_audit_v1';out.mkdir(exist_ok=False)
    owner=BASE/'compressed_batch_rtl_guarded_execution_v1/state.json';current=json.loads(owner.read_text());pid=current['owner_pid'];original=identity(pid)
    require('supervise_compressed_batch_rtl_guarded.py' in original['command'],'Unexpected execution owner')
    checker=ROOT/'scripts/check_compressed_batch_guarded_rtl.py';checker_hash=digest(checker)
    state=dict(owner_pid=os.getpid(),observed_owner=pid,status='running',stage='wait_existing_execution')
    def save():
        p=out/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(out/'state.json')
    (out/'plan.json').write_text(json.dumps(dict(checker_sha256=checker_hash,original_identity=original,original_owner=pid,script_sha256=digest(__file__)),indent=2)+'\n');save()
    try:
        while True:
            current=json.loads(owner.read_text());require(current['owner_pid']==pid,'Owner changed')
            if current['status']!='running':break
            require(identity(pid)==original,'Owner missing or replaced; do not restart');time.sleep(30)
        require(current['status']=='complete','Original execution failed; preserve evidence')
        require(digest(checker)==checker_hash,'Checker changed while waiting')
        state['stage']='independent_audit';save()
        command=['python3',str(checker),'--output',str(ROOT/'results/compressed_batch_guarded_rtl_audit_20261025_v1.json')]
        with (out/'audit.log').open('x') as f:code=subprocess.run(command,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT).returncode
        (out/'receipt.json').write_text(json.dumps(dict(command=command,exit_code=code,log_sha256=digest(out/'audit.log')),indent=2)+'\n');require(code==0,'Independent audit failed')
        state.update(status='complete',stage='independently_audited');save()
    except BaseException as e:state.update(status='failed',error=str(e));save();raise
if __name__=='__main__':main()
