#!/usr/bin/env python3
"""Snapshot original experiment requirements and scoped evidence; never imply completion."""
import json,os,tempfile
from datetime import datetime,timezone
from pathlib import Path
from check_vitis_kernel import digest
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
def main():
    target=ROOT/'EXPERIMENT_STATUS_20261025_v1.json';assert not target.exists()
    old_path=ROOT/'EXPERIMENT_STATUS.json';old=json.loads(old_path.read_text())
    evidence={};bindings={str(old_path):digest(old_path)}
    def report(key,relative):
        p=ROOT/relative;r=json.loads(p.read_text());evidence[key]=dict(path=str(p),sha256=digest(p),status=r.get('status'),scope='Existing report metadata reviewed; this status snapshot does not re-execute its semantic auditor');bindings[str(p)]=digest(p);return r
    runtime=report('native_statistics','results/native_site_runtime_statistics_audit_20261023_v1.json')
    chain=report('source_to_route_statistics','results/source_to_route_statistics_audit_20261023_v1.json')
    scope=report('template_scope_statistics','results/template_scope_runtime_statistics_audit_20261023_v1.json')
    conversion=report('conversion_statistics','results/packed_conversion_statistics_audit_20261023_v1.json')
    batch=report('compressed_real_batches','results/compressed_batch_real_audit_20261025_v1.json')
    boundary=report('search_boundary_rtl','results/search_kernel_boundary_rtl_revalidation_20261025_v1.json')
    synth=report('compressed_csr_synthesis','results/compressed_batch_synthesis_review_20261025_v1.json')
    report('compact_full44_csim','results/compressed_batch_compact_full44_csim_20261025_v1.json')
    report('width64_full44_csim','results/compressed_batch_width64_full44_csim_20261025_v1.json')
    report('durable_backup','results/frozen_local_evidence_archive_audit_20261025_v1.json')
    xrt=ROOT/'data/derived/xrt_environment_recheck_20261025_v1/receipt.json';xrtlog=xrt.parent/'examine.log';assert '0 devices found' in xrtlog.read_text();bindings[str(xrt)]=digest(xrt);bindings[str(xrtlog)]=digest(xrtlog)
    updates={
      'semantics':('regional_graph_equivalence_verified_full_special_resource_model_incomplete',['compressed_real_batches'],'Only 14 physically evidenced site instances; clock semantics and broader resource ownership/configuration remain incomplete.'),
      'coverage':('bounded_training_holdout_and_region_verified_full_device_coverage_unproven',[],'Existing bounded capture/holdout evidence cannot establish full-device or all-family coverage.'),
      'packed':('regional_binary_representations_and_full_workload_cpu_equivalence_verified',['compressed_real_batches'],'Graph image compression is separate from diagnostic trace encoding; platform transfer/capacity still unmeasured.'),
      'native':('completed_repeat_statistics_under_partial_site_model',['native_statistics','template_scope_statistics'],'Seven repeats per condition completed, but shared-host/cache and partial site-model limitations remain.'),
      'netlist':('regional_full_query_physical_pass_under_partial_model_full_semantics_incomplete',['compressed_real_batches'],'Prior physical readback is scoped to partial model; complete special-resource semantics and external IO remain.'),
      'hardware':('component_rtl_and_boundary_evidence_partial_integrated_rtl_running_resource_budget_unmet',['search_boundary_rtl','compressed_csr_synthesis','compact_full44_csim','width64_full44_csim'],'Integrated CSR RTL not terminal; compact RTL missing; original integrated HLS LUT estimate exceeds whole-device reference, physical/platform fit unproven.'),
      'ddr_hbm':('incomplete_no_visible_xrt_device_and_no_same_board_measurements',[],'Latest local XRT observation finds zero devices; actual platform, allocation, calibrated DDR/HBM and power measurements absent.'),
      'end_to_end':('captured_source_to_two_cpu_batches_repeat_statistics_complete_full_acquisition_training_board_chain_incomplete',['source_to_route_statistics','conversion_statistics'],'21 workers complete captured-TSV to two-batch CPU chain; Vivado acquisition, training, transfer, physical readback and board runtime remain outside that timer.'),
      'reproducibility':('immutable_stage_evidence_and_durable_backup_partial_complete_experiment_incomplete',['durable_backup'],'New active artifacts not yet durably archived; final experiment commands, complete matrix and final research report remain.'),
    }
    requirements=[]
    for item in old['requirements']:
        status,keys,remaining=updates[item['id']]
        requirements.append(dict(id=item['id'],requirement=item['requirement'],status=status,evidence_keys=keys,remaining=remaining,complete=False))
    observed=[]
    for name in ['compressed_batch_rtl_guarded_v1','compressed_batch_rtl_guarded_execution_v1','compressed_batch_guarded_final_audit_v1','snapshot_rtl_local_recovery','compressed_batch_compact_hls','compressed_batch_width64_hls']:
        p=BASE/name/'state.json';s=json.loads(p.read_text());pid=s['owner_pid'];proc=Path('/proc',str(pid));live=proc.exists()
        command=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode() if live else None
        observed.append(dict(bundle=name,state=s,owner_live=live,actual_command=command))
    config=ROOT/'configs/experiment.json';cfg=json.loads(config.read_text());bindings[str(config)]=digest(config)
    variants=[dict(id=v['id'],configured_description=v['description'],status='synthetic_reference_available' if v['id']=='reference' else 'partial_site_model_cpu_comparison_available' if v['id'].startswith('cpu_') else 'incomplete_same_board_backend_measurement_absent') for v in cfg['variants']]
    for p in [ROOT/'EXPERIMENTS.md',ROOT/'INTERFACES.md',ROOT/'scripts/snapshot_experiment_completion.py']:bindings[str(p)]=digest(p)
    result=dict(goal=old['goal'],status='active',completion_proven=False,observed_utc=datetime.now(timezone.utc).isoformat(),scope='Requirements and evidence snapshot, not a replacement semantic audit or a completion claim',requirements=requirements,configured_variants=variants,evidence=evidence,active_process_observations=observed,findings=dict(native_workers=runtime['completed_workers'],source_to_route_workers=chain['completed_workers'],template_scope_workers=scope['completed_workers'],conversion_workers=conversion['completed_workers'],source_to_route_paired_ratios=chain['paired_comparisons'],csr_integrated_hls_resources=synth['resources'],csr_integrated_hls_estimated_clock_ns=synth['estimated_clock_ns'],board_visible_devices=0),bindings=bindings)
    fd,tmp=tempfile.mkstemp(dir=target.parent)
    with os.fdopen(fd,'w') as f:json.dump(result,f,indent=2,ensure_ascii=False);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,target);print('Recorded',len(requirements),'original requirements and',len(variants),'configured variants; goal remains active')
if __name__=='__main__':main()
