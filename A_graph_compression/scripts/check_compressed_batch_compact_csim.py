#!/usr/bin/env python3
"""Verify completed compact Csim snapshots while synthesis continues separately."""
import json,os,tempfile
from pathlib import Path
from check_vitis_kernel import digest,require
from read_batch_trace_v4 import decode_file
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
def audit():
    bundle=BASE/'compressed_batch_compact_hls';plan=json.loads((bundle/'plan.json').read_text())
    require(plan['graph_mode']==1 and plan['transactions']==4 and plan['full44_depth_tb'],'Wrong mode or full-depth gate')
    require(plan['max_single_output_file_bytes']==8589934592,'Missing output size limit')
    text=(bundle/'flow.log').read_text()
    require(text.splitlines().count('COMPRESSED_BATCH_TRACE_CSIM_COMPLETE')==1,'Csim has not completed')
    require('FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode=1 ports=44 transactions=4' in text and 'SEARCH_BATCH_PASS mode=1' in text,'Missing full-depth functional checks')
    proof_path=ROOT/'results/compressed_batch_rtl_full_depth_cpu_20261025_v1.json';proof=json.loads(proof_path.read_text())
    require(proof['ports']==44 and proof['transactions_per_mode']==4,'Missing reference proof')
    files={str(proof_path):digest(proof_path),str(bundle/'plan.json'):digest(bundle/'plan.json'),str(Path(__file__).resolve()):digest(__file__)}
    rows=[]
    for case in range(4):
        reference=BASE/f'compressed_batch_rtl_tb_cpu_v2/cpu_1_{case}.bin';actual=bundle/f'csim_1_{case}.bin'
        expected=proof['files'].get(str(reference));require(expected is not None and digest(reference)==expected,'Reference changed')
        require(actual.stat().st_size==reference.stat().st_size==946498280 and digest(actual)==expected,'Complete44 port snapshot differs')
        trace=Path(plan['project'])/f'solution/csim/build/trace_mode_1_case_{case}.bin'
        cpu=BASE/f'compressed_batch_rtl_tb_cpu_v2/trace_mode_1_case_{case}.bin'
        require(proof['files'].get(str(cpu))==digest(cpu),'Full-depth CPU trace changed')
        require(digest(trace)==digest(cpu),'Csim trace differs from CPU')
        if case<3:
            decoded=decode_file(trace,4);require(decoded['complete_batch']==(case!=1),'Wrong reset-state proof')
        else:
            try:decode_file(trace,4)
            except ValueError:pass
            else:raise ValueError('Error terminal wrongly accepted')
        for p in [reference,actual,trace,cpu]:files[str(p)]=digest(p)
        rows.append(dict(case=case,snapshot_bytes=actual.stat().st_size,full44_payload_sha256=expected,trace_sha256=digest(trace)))
    # Bind stable closed Csim log, not the still-growing synthesis log.
    log=Path(plan['project'])/'solution/csim/report/search_batch_trace_top_v2_csim.log'
    require(log.is_file(),'Missing closed Csim log');files[str(log)]=digest(log)
    return dict(status='compact_csim_four_full44_snapshots_and_exact_traces_independently_verified_synthesis_pending',files=files,transactions=rows,limits=['C simulation only; independent synthesis and RTL evidence still required','Logical four-node synthetic cases at declared pointer capacities; not production traffic'])
def main():
    target=ROOT/'results/compressed_batch_compact_full44_csim_20261025_v1.json';require(not target.exists(),'Refuse overwrite')
    report=audit();fd,tmp=tempfile.mkstemp(dir=target.parent)
    with os.fdopen(fd,'w') as f:json.dump(report,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,target);print(report['status'])
if __name__=='__main__':main()
