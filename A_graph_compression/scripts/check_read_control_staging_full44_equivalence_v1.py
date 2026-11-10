#!/usr/bin/env python3
"""Compare every byte of all8 full44 candidate CPU snapshots with the frozen CPU oracle."""
import json,hashlib
from pathlib import Path
from check_vitis_kernel import digest,require
from run_compact_native_stack_recovery_v1 import atomic
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
def main():
    candidate=BASE/'read_control_staging_full44_cpu_v1';original=BASE/'compressed_batch_rtl_tb_cpu_v2';proof_path=ROOT/'results/compressed_batch_rtl_full_depth_cpu_20261025_v1.json';baseline=json.loads(proof_path.read_text());payload_path=candidate/'independent_payload_audit.json';payload=json.loads(payload_path.read_text())
    require(payload['ports']==baseline['ports']==44 and payload['transactions_per_mode']==baseline['transactions_per_mode']==4 and payload['modes']==2,'Incomplete scope')
    for p,h in payload['files'].items():require(digest(p)==h,'Changed candidate evidence')
    a={p.name:p for p in (candidate/'source').iterdir() if p.is_file()};b={p.name:p for p in (original/'source').iterdir() if p.is_file()};require(a.keys()==b.keys(),'Changed source set');require([n for n in a if digest(a[n])!=digest(b[n])]==['search_label_records.hpp'],'Changes beyond isolated header')
    files=dict(payload['files']);rows=[]
    for mode in [0,1]:
        for tx in range(4):
            actual=candidate/f'cpu_{mode}_{tx}.bin';reference=original/actual.name;require(actual.stat().st_size==reference.stat().st_size==946498280,'Reduced snapshot')
            h=hashlib.sha256()
            with actual.open('rb') as left,reference.open('rb') as right:
                while True:
                    x=left.read(8388608);y=right.read(8388608);require(x==y,'Complete full44 snapshot differs')
                    if not x:break
                    h.update(x)
            checksum=h.hexdigest();require(baseline['files'][str(reference)]==checksum,'Frozen oracle changed');files[str(actual)]=checksum;files[str(reference)]=checksum
            trace=candidate/f'trace_mode_{mode}_case_{tx}.bin';old_trace=original/trace.name;require(digest(trace)==digest(old_trace)==baseline['files'][str(old_trace)],'Trace changed');files[str(trace)]=digest(trace);files[str(old_trace)]=digest(old_trace)
            rows.append(dict(mode=mode,transaction=tx,bytes=actual.stat().st_size,sha256=checksum))
    for p in [proof_path,payload_path,Path(__file__).resolve(),ROOT/'scripts/check_compressed_batch_rtl_tb_cpu.py',ROOT/'scripts/check_vitis_kernel.py']:files[str(p)]=digest(p)
    output=ROOT/'results/read_control_staging_full44_cpu_equivalence_20261025_v1.json';require(not output.exists(),'Refuse overwrite');atomic(output,dict(status='control_staging_both_modes_all8_full44_cpu_snapshots_and_traces_identical_original_asan_ubsan_verified_hardware_pending',files=files,rows=rows,total_snapshot_bytes=sum(r['bytes'] for r in rows),rtl_verified=False,physical_timing_verified=False,limits=['Full declared pointer capacities but original logical4-node synthetic batch cases; not production traffic','Only CPU equivalence; new pipeline RTL and full physical timing remain unverified']))
    print('All8 full44 snapshots byte-identical; total bytes',sum(r['bytes'] for r in rows))
if __name__=='__main__':main()
