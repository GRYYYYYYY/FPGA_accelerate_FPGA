#!/usr/bin/env python3
"""Preserve the original matrix while recording native crash and live recovery."""
from datetime import datetime, timezone
import json
from pathlib import Path
from check_vitis_kernel import digest, require
from experiment_status import collect
from run_compact_native_stack_recovery_v1 import atomic

ROOT=Path(__file__).resolve().parents[1]

def main():
    previous=ROOT/'EXPERIMENT_STATUS_20261025_v2.json'
    output=ROOT/'EXPERIMENT_STATUS_20261025_v3.json'
    require(not output.exists(),'Refuse overwrite')
    result=json.loads(previous.read_text())
    original=json.loads((ROOT/'EXPERIMENT_STATUS.json').read_text())
    config=json.loads((ROOT/'configs/experiment.json').read_text())
    require([r['id'] for r in result['requirements']]==[r['id'] for r in original['requirements']], 'Requirement scope changed')
    require([v['id'] for v in result['configured_variants']]==[v['id'] for v in config['variants']], 'Variant scope changed')
    require(len(result['requirements'])==9 and len(result['configured_variants'])==8,'Incomplete original matrix')
    result['bindings'][str(previous)]=digest(previous)
    reports={
        'snapshot_native_resource_abort':'snapshot_compile_resource_abort_20261025_v1.json',
        'compact_native_simulator_crash':'compact_native_xsim_crash_incident_20261025_v1.json',
        'compact_core_location':'compact_xsim_core_location_20261025_v1.json',
        'snapshot_full30_preflight':'snapshot_dpi_storage_preflight_audit_20261025_v1.json',
        'snapshot_execution_preparation':'snapshot_dpi_execution_preparation_20261025_v1.json',
        'durable_failure_provenance':'frozen_dpi_incident_provenance_archive_audit_20261025_v1.json',
    }
    for key,name in reports.items():
        path=ROOT/'results'/name;report=json.loads(path.read_text())
        result['evidence'][key]=dict(path=str(path),sha256=digest(path),status=report['status'],
            scope='Report metadata and binding recorded; this snapshot does not replace the independent artifact auditor')
        result['bindings'][str(path)]=digest(path)
    hardware=next(r for r in result['requirements'] if r['id']=='hardware')
    hardware['status']='full_scope_rtl_trials_active_compact_native_crashed_stack_recovery_and_global64_hls_pending'
    hardware['evidence_keys']+=['snapshot_native_resource_abort','compact_native_simulator_crash','compact_core_location','snapshot_full30_preflight','snapshot_execution_preparation']
    hardware['remaining']+=' Original compact elaboration completed but XSim kernel SIGSEGV and C postcheck failed. Isolated stack256 runtime trial and search DPI v7 remain unaccepted; compact global64 HLS is running. Full30 snapshot must still execute. Preparations and live processes do not prove RTL acceptance.'
    reproducibility=next(r for r in result['requirements'] if r['id']=='reproducibility')
    reproducibility['evidence_keys'].append('durable_failure_provenance')
    result['active_process_observations']=collect()['tasks']
    result['observed_utc']=datetime.now(timezone.utc).isoformat()
    result['status']='active';result['completion_proven']=False
    result['scope']='Original requirements and variants retained. Live local process status refreshed; inherited physical/CPU/XRT results are historical observations, not new measurements.'
    for path in [Path(__file__).resolve(),ROOT/'scripts/experiment_status.py',ROOT/'scripts/run_compact_native_stack_recovery_v1.py']:
        result['bindings'][str(path)]=digest(path)
    require(all(not r['complete'] for r in result['requirements']),'No new complete requirement established')
    atomic(output,result)
    print('Preserved 9 requirements and 8 variants; recorded native failure and current live trials; completion remains unproven.')

if __name__=='__main__':main()
