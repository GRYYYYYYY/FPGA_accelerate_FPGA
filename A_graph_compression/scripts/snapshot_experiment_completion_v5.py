#!/usr/bin/env python3
"""Record completed controlled HLS/physical trials without narrowing experiment scope."""
from pathlib import Path
from datetime import datetime,timezone
import json
from check_vitis_kernel import digest,require
from experiment_status_v2 import collect
from run_compact_native_stack_recovery_v1 import atomic
ROOT=Path(__file__).resolve().parents[1]
def main():
    previous=ROOT/'EXPERIMENT_STATUS_20261025_v4.json';out=ROOT/'EXPERIMENT_STATUS_20261025_v5.json';require(not out.exists(),'Refuse overwrite')
    result=json.loads(previous.read_text());original=json.loads((ROOT/'EXPERIMENT_STATUS.json').read_text());config=json.loads((ROOT/'configs/experiment.json').read_text())
    require([r['id'] for r in result['requirements']]==[r['id'] for r in original['requirements']] and len(result['requirements'])==9,'Original requirements changed')
    require([r['id'] for r in result['configured_variants']]==[r['id'] for r in config['variants']] and len(config['variants'])==8,'Original variants changed')
    for p,h in result['bindings'].items():require(digest(p)==h,'Previous snapshot binding changed: '+p)
    result['bindings'][str(previous)]=digest(previous)
    new={'search_full_dpi_replay': 'search_axi_dpi_replay_audit_20261025_v3.json', 'search_full_dpi_archive': 'frozen_search_dpi_final_archive_audit_20261025_v1.json', 'read_control_cpu': 'search_read_control_staging_cpu_20261025_v1.json', 'read_control_hls': 'search_read_control_staging_hls_audit_20261025_v1.json', 'read_control_full_setup': 'search_read_control_staging_full_depth_setup_audit_20261025_v1.json', 'read_control_full44_cpu': 'read_control_staging_full44_cpu_equivalence_20261025_v1.json', 'read_control_physical_prepared': 'search_read_control_staging_physical_preparation_20261025_v1.json', 'read_control_dpi_prepared': 'search_read_control_staging_dpi_entry_preparation_20261025_v1.json', 'compact_global64_dpi_storage': 'compressed_compact_bus64_dpi_storage_preflight_audit_20261025_v1.json', 'compact_global64_dpi_entry': 'compressed_compact_bus64_dpi_entry_preparation_20261025_v1.json'}
    current={}
    for key,name in new.items():
        p=ROOT/'results'/name;r=json.loads(p.read_text());current[key]=r;result['bindings'][str(p)]=digest(p)
        result['evidence'][key]=dict(path=str(p),sha256=digest(p),status=r['status'],scope='Recorded closed audit metadata; snapshot does not replace the artifact auditor')
    hardware=next(r for r in result['requirements'] if r['id']=='hardware');hardware['status']='search_full_dpi_replay_verified_integrated_modes_and_snapshot_pending_timing_negative'
    hardware['evidence_keys']=list(dict.fromkeys(hardware['evidence_keys']+list(new)))
    hardware['remaining']='Search original full-depth 2tx replay independently verified with exact cycles [2132461,12404], all5 output files and original C oracle. Integrated full44 CSR and full30 snapshot still pending admission/dependency; compact native stack recovery live, compact global64 model ledger and entry prepared only. Read-control staged candidate has HLS latency2/II1 and full44 two-mode CPU equivalence, but candidate RTL and physical remain unexecuted; LUT/FF overhead retained. Existing optimized packet64 route WNS -0.316ns still fails timing/DRC/methodology. Board/platform/bandwidth/power/end-to-end proof absent.'
    repro=next(r for r in result['requirements'] if r['id']=='reproducibility');repro['evidence_keys']=list(dict.fromkeys(repro['evidence_keys']+['search_full_dpi_archive']))
    result['findings']['search_full_dpi_cycles']=[2132461,12404]
    result['active_process_observations']=collect()['tasks'];result['observed_utc']=datetime.now(timezone.utc).isoformat();result['completion_proven']=False;result['status']='active'
    result['scope']='Original9 requirements/8variants preserved; completed audits recorded. Live process status refreshed; inherited XRT/CPU observations remain historical, not new measurements.'
    for p in [Path(__file__).resolve(),ROOT/'scripts/experiment_status_v2.py']:result['bindings'][str(p)]=digest(p)
    require(all(not r['complete'] for r in result['requirements']),'No full requirement completion proven')
    atomic(out,result);print('Preserved original9 requirements/8variants; added10 separately scoped evidence sets; full completion remains false.')
if __name__=='__main__':main()
