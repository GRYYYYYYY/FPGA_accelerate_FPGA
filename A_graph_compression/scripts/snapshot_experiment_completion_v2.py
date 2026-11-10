#!/usr/bin/env python3
"""Snapshot original experiment requirements and scoped evidence; never imply completion."""
import json,os,tempfile
from datetime import datetime,timezone
from pathlib import Path
from check_vitis_kernel import digest
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
def main():
    target=ROOT/'EXPERIMENT_STATUS_20261025_v2.json';assert not target.exists()
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
    bus=report('integrated_bus64_synthesis','results/compressed_batch_bus64_synthesis_review_20261025_v1.json')
    report('integrated_width_ablation','results/compressed_batch_bus_width_ablation_20261025_v1.json')
    packet_physical=report('search_packet64_postroute','results/search_packet_width64_physical_audit_20261025_v2.json')
    report('integrated_physical_resource_abort','results/compressed_bus64_physical_resource_abort_20261025_v1.json')
    report('dpi_four_page_protocol','results/axi_dpi_protocol_pages_oracle_20261025_v1.json')
    report('dpi_full_batch_model_preflight','results/compressed_bus64_dpi_storage_preflight_audit_20261025_v1.json')
    report('dpi_durable_archive','results/frozen_dpi_validation_archive_audit_20261025_v1.json')
    report('ablation_figures','results/figures/bus_width_ablation_20261025_v2/manifest.json')
    xrt=ROOT/'data/derived/xrt_environment_recheck_20261025_v2/receipt.json';xrtlog=xrt.parent/'examine.log';assert '0 devices found' in xrtlog.read_text();bindings[str(xrt)]=digest(xrt);bindings[str(xrtlog)]=digest(xrtlog)
    updates={
      'semantics':('regional_graph_equivalence_verified_full_special_resource_model_incomplete',['compressed_real_batches'],'Only 14 physically evidenced site instances; clock semantics and broader resource ownership/configuration remain incomplete.'),
      'coverage':('bounded_training_holdout_and_region_verified_full_device_coverage_unproven',[],'Existing bounded capture/holdout evidence cannot establish full-device or all-family coverage.'),
      'packed':('regional_binary_representations_and_full_workload_cpu_equivalence_verified',['compressed_real_batches'],'Graph image compression is separate from diagnostic trace encoding; platform transfer/capacity still unmeasured.'),
      'native':('completed_repeat_statistics_under_partial_site_model',['native_statistics','template_scope_statistics'],'Seven repeats per condition completed, but shared-host/cache and partial site-model limitations remain.'),
      'netlist':('regional_full_query_physical_pass_under_partial_model_full_semantics_incomplete',['compressed_real_batches'],'Prior physical readback is scoped to partial model; complete special-resource semantics and external IO remain.'),
      'hardware':('component_and_boundary_partial_full_batch_rtl_pending_physical_trial_resource_aborted',['search_boundary_rtl','integrated_bus64_synthesis','integrated_width_ablation','search_packet64_postroute','integrated_physical_resource_abort','dpi_four_page_protocol','dpi_full_batch_model_preflight'],'Global bus64 HLS LUT estimate433034 and clock3.715ns still misses3.65ns effective budget; full batch RTL pending, search-only routed WNS-0.382ns still fails, integrated physical attempt resource-aborted with no DCP. Small DPI units/preflight do not establish full-depth equivalence. Same-board implementation and timing/resources remain unproven.'),
      'ddr_hbm':('incomplete_no_visible_xrt_device_and_no_same_board_measurements',[],'Latest local XRT observation finds zero devices; actual platform, allocation, calibrated DDR/HBM and power measurements absent.'),
      'end_to_end':('captured_source_to_two_cpu_batches_repeat_statistics_complete_full_acquisition_training_board_chain_incomplete',['source_to_route_statistics','conversion_statistics'],'21 workers complete captured-TSV to two-batch CPU chain; Vivado acquisition, training, transfer, physical readback and board runtime remain outside that timer.'),
      'reproducibility':('immutable_stage_evidence_and_durable_backup_partial_complete_experiment_incomplete',['durable_backup','dpi_durable_archive','ablation_figures'],'New active artifacts not yet durably archived; final experiment commands, complete matrix and final research report remain.'),
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
    for name in ['compact_rtl_memory_serialization_20261025_v1','search_axi_dpi_serialized_supervision_20261025_v3','search_axi_dpi_final_audit_supervision_20261025_v3','compressed_bus64_dpi_supervision_20261025_v1']:
        p=ROOT/'data/derived'/name/'state.json';s=json.loads(p.read_text());proc=Path('/proc')/str(s['owner_pid']);require_live=proc.exists()
        observed.append(dict(bundle=name,state=s,owner_live=require_live,actual_command=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode() if require_live else None))
    for pid in [2516537,1509104]:
        proc=Path('/proc')/str(pid)
        if proc.exists():
            stat=(proc/'stat').read_text().rsplit(')',1)[1].split();observed.append(dict(actual_pid=pid,state=stat[0],start_ticks=stat[19],rss_bytes=int(stat[21])*os.sysconf('SC_PAGE_SIZE')))
    config=ROOT/'configs/experiment.json';cfg=json.loads(config.read_text());bindings[str(config)]=digest(config)
    variants=[dict(id=v['id'],configured_description=v['description'],status='synthetic_reference_available' if v['id']=='reference' else 'partial_site_model_cpu_comparison_available' if v['id'].startswith('cpu_') else 'incomplete_same_board_backend_measurement_absent') for v in cfg['variants']]
    for p in [ROOT/'EXPERIMENTS.md',ROOT/'INTERFACES.md',Path(__file__).resolve()]:bindings[str(p)]=digest(p)
    result=dict(goal=old['goal'],status='active',completion_proven=False,observed_utc=datetime.now(timezone.utc).isoformat(),scope='Requirements and evidence snapshot, not a replacement semantic audit or a completion claim',requirements=requirements,configured_variants=variants,evidence=evidence,active_process_observations=observed,findings=dict(native_workers=runtime['completed_workers'],source_to_route_workers=chain['completed_workers'],template_scope_workers=scope['completed_workers'],conversion_workers=conversion['completed_workers'],source_to_route_paired_ratios=chain['paired_comparisons'],csr_integrated_hls_resources=synth['resources'],csr_integrated_hls_estimated_clock_ns=synth['estimated_clock_ns'],board_visible_devices=0,integrated_bus64_hls_resources=bus['resources'],integrated_bus64_estimated_clock_ns=bus['estimated_clock_ns'],search_packet64_postroute_resources=packet_physical['stages']['routed']['resources'],search_packet64_setup_slack_ns=packet_physical['stages']['routed']['timing']['setup']['slack_ns']),bindings=bindings)
    fd,tmp=tempfile.mkstemp(dir=target.parent)
    with os.fdopen(fd,'w') as f:json.dump(result,f,indent=2,ensure_ascii=False);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,target);print('Recorded',len(requirements),'original requirements and',len(variants),'configured variants; goal remains active')
if __name__=='__main__':main()
