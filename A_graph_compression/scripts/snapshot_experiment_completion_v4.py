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
    previous=ROOT/'EXPERIMENT_STATUS_20261025_v3.json';out=ROOT/'EXPERIMENT_STATUS_20261025_v4.json';require(not out.exists(),'Refuse overwrite')
    result=json.loads(previous.read_text());original=json.loads((ROOT/'EXPERIMENT_STATUS.json').read_text());config=json.loads((ROOT/'configs/experiment.json').read_text())
    require([r['id'] for r in result['requirements']]==[r['id'] for r in original['requirements']] and len(result['requirements'])==9,'Original requirements changed')
    require([r['id'] for r in result['configured_variants']]==[r['id'] for r in config['variants']] and len(config['variants'])==8,'Original variants changed')
    for p,h in result['bindings'].items():require(digest(p)==h,'Previous snapshot binding changed: '+p)
    result['bindings'][str(previous)]=digest(previous)
    new={'compact_global64_hls':'compressed_batch_compact_bus64_synthesis_review_20261025_v1.json','compact_global64_full44_csim':'compressed_batch_compact_bus64_full44_csim_20261025_v1.json','compact_global64_setup':'compressed_batch_compact_bus64_full_depth_cosim_setup_20261025_v1.json','compact_global64_guarded_copy':'compressed_batch_compact_bus64_guarded_setup_audit_20261025_v1.json','paired_global64_modes':'compressed_batch_csr_compact_global64_comparison_20261025_v1.json','packet64_postroute_optimization':'search_packet64_physopt_audit_20261025_v1.json','compact_global64_archive':'frozen_compact_global64_archive_audit_20261025_v1.json','updated_figures':'figures/csr_compact_and_physopt_20261025_v1/manifest.json'}
    current={}
    for key,name in new.items():
        p=ROOT/'results'/name;r=json.loads(p.read_text());current[key]=r;result['bindings'][str(p)]=digest(p)
        result['evidence'][key]=dict(path=str(p),sha256=digest(p),status=r['status'],scope='Recorded closed audit metadata; snapshot does not replace the artifact auditor')
    hardware=next(r for r in result['requirements'] if r['id']=='hardware');hardware['status']='paired_global64_hls_and_full_setup_closed_full_rtl_active_postroute_timing_still_negative'
    hardware['evidence_keys']=list(dict.fromkeys(hardware['evidence_keys']+list(new)[:6]))
    hardware['remaining']='Compact global64 HLS:447391LUT/328607FF,3.715ns versus3.65ns budget; full4tx/full44 Csim and setup independently audited, guarded execution copy not yet simulated. Packet64 OOC physopt legally routes all182762 nets at WNS-0.316ns, still fails timing/DRC/methodology. Original compact native simulation crashed; isolated stack256 recovery and full2tx search DPI v7 remain active and unaccepted. Full44 batch and full30 snapshot RTL plus board proof remain required.'
    repro=next(r for r in result['requirements'] if r['id']=='reproducibility');repro['evidence_keys']=list(dict.fromkeys(repro['evidence_keys']+['compact_global64_archive','updated_figures']))
    result['findings']['compact_global64_hls_resources']=current['compact_global64_hls']['resources'];result['findings']['packet64_optimized_setup_slack_ns']=current['packet64_postroute_optimization']['after']['setup']['slack_ns']
    result['active_process_observations']=collect()['tasks'];result['observed_utc']=datetime.now(timezone.utc).isoformat();result['completion_proven']=False;result['status']='active'
    result['scope']='Original9 requirements/8variants preserved; completed audits recorded. Live process status refreshed; inherited XRT/CPU observations remain historical, not new measurements.'
    for p in [Path(__file__).resolve(),ROOT/'scripts/experiment_status_v2.py']:result['bindings'][str(p)]=digest(p)
    require(all(not r['complete'] for r in result['requirements']),'No full requirement completion proven')
    atomic(out,result);print('Preserved original9 requirements/8variants; added8 closed evidence sets; full completion remains false.')
if __name__=='__main__':main()
