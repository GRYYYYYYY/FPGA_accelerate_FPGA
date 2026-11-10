#!/usr/bin/env python3
"""Record completed controlled HLS/physical trials without narrowing experiment scope."""
from pathlib import Path
from datetime import datetime,timezone
import json
from check_vitis_kernel import digest,require
from experiment_status_v4 import collect
from run_compact_native_stack_recovery_v1 import atomic
ROOT=Path(__file__).resolve().parents[1]
def main():
    previous=ROOT/'EXPERIMENT_STATUS_20261025_v5.json';out=ROOT/'EXPERIMENT_STATUS_20261025_v6.json';require(not out.exists(),'Refuse overwrite')
    result=json.loads(previous.read_text());original=json.loads((ROOT/'EXPERIMENT_STATUS.json').read_text());config=json.loads((ROOT/'configs/experiment.json').read_text())
    require([r['id'] for r in result['requirements']]==[r['id'] for r in original['requirements']] and len(result['requirements'])==9,'Original requirements changed')
    require([r['id'] for r in result['configured_variants']]==[r['id'] for r in config['variants']] and len(config['variants'])==8,'Original variants changed')
    for p,h in result['bindings'].items():require(digest(p)==h,'Previous snapshot binding changed: '+p)
    result['bindings'][str(previous)]=digest(previous)
    new={'full44_144gib_failure': 'full_rtl_stricter_cap_incident_20261025_v1.json', 'compact_recovery_v2_launch': 'compact_native_guard_recovery_launch_20261025_v2.json', 'compact_recovery_v2_contract': 'compact_native_recovery_v2_completion_contract_20261025_v1.json', 'fresh_xrt_visibility': 'xrt_board_recheck_20261025_v3.json', 'compact_global64_physical_inputs': 'compressed_compact_bus64_physical_preparation_20261025_v1.json', 'clock_public_surface': 'clock_public_model_surface_audit_20261025_v1.json', 'clock_official_documentation': 'clock_official_documentation_review_20261025_v1.json', 'stricter_scope_preserved': 'stricter_rtl_driver_scope_audit_20261025_v1.json'}
    current={}
    for key,name in new.items():
        p=ROOT/'results'/name;r=json.loads(p.read_text());current[key]=r;result['bindings'][str(p)]=digest(p)
        result['evidence'][key]=dict(path=str(p),sha256=digest(p),status=r['status'],scope='Recorded closed audit metadata; snapshot does not replace the artifact auditor')
    hardware=next(r for r in result['requirements'] if r['id']=='hardware');hardware['status']='full44_dpi_144gib_compile_failed_native_compact_recovery_v2_active_board_unavailable'
    hardware['evidence_keys']=list(dict.fromkeys(hardware['evidence_keys']+list(new)))
    hardware['remaining']='Original search full2tx replay remains independently verified. Full44 CSR global64 LLVM compilation failed under144GiB with exit134 and149429976KiB peak RSS; no integrated RTL ran. Native compact recoveryv1 was guard-aborted at0/4; v2 reuses the original compiled snapshot at unchanged96GiB AS/stack256MiB, active and unaccepted. Full30 snapshot and later compact-global64/staged-search chain terminated on upstream failure and were never executed. Read-control and compact-global64 physical artifacts are prepared only. Packet64 WNS-0.316ns still fails timing/DRC/methodology. Fresh local XRT sees0devices; platform, board bandwidth/power/end-to-end proof absent.'
    repro=next(r for r in result['requirements'] if r['id']=='reproducibility');repro['evidence_keys']=list(dict.fromkeys(repro['evidence_keys']+['full44_144gib_failure','compact_recovery_v2_contract','stricter_scope_preserved']))
    result['findings']['full44_compile_failure']=dict(exit_code=134,as_limit_gib=144,max_rss_kib=149429976,rtl_transactions_executed=0)
    result['findings']['fresh_xrt_visible_devices']=0
    semantic=next(r for r in result['requirements'] if r['id']=='semantics');semantic['evidence_keys']=list(dict.fromkeys(semantic['evidence_keys']+['clock_public_surface','clock_official_documentation']))
    memory=next(r for r in result['requirements'] if r['id']=='ddr_hbm');memory['evidence_keys']=list(dict.fromkeys(memory['evidence_keys']+['fresh_xrt_visibility']))
    result['active_process_observations']=collect()['tasks'];result['observed_utc']=datetime.now(timezone.utc).isoformat();result['completion_proven']=False;result['status']='active'
    result['scope']='Original9 requirements/8variants preserved; completed audits recorded. Live process status refreshed; fresh local XRT visibility rechecked; inherited CPU data remain historical. Failed and prepared evidence do not imply RTL acceptance.'
    for p in [Path(__file__).resolve(),ROOT/'scripts/experiment_status_v4.py']:result['bindings'][str(p)]=digest(p)
    require(all(not r['complete'] for r in result['requirements']),'No full requirement completion proven')
    atomic(out,result);print('Preserved original9 requirements/8variants; added8 failure/preparation/live-launch evidence sets; full completion remains false.')
if __name__=='__main__':main()
